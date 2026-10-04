"""Spell and rune damage and healing measured in game against the 7.4 formulas (docs/reference-74/spell-formulas.md):
amount = base x magic power, magic power P = level x 2 + magic level x 3, at least 100. Each formula is checked at the
floor (P 100) and at P 380 (level 100, magic level 60). Damage is read from the numbers the client shows over the
target, halved player against player (combat.cpp); healing from the healed player's own health.

Helpers come from test_combat_formulas.py (HMM and SD were measured there).
"""
import time

import pytest

from test_combat_formulas import CREATURE, ENERGY, PHYSICAL, SD, _hits, _shoot
from tibia74 import BACKPACK, GameClient, Item

FIRE, POISON = 198, 30            # const.h TEXTCOLOR_ORANGE / TEXTCOLOR_LIGHTGREEN
BAG = 1988
FIREBALL, GFB, EXPLOSION, UH, ENVENOM = 2302, 2304, 2313, 2273, 2292
LOW, HIGH = (20, 10), (100, 60)   # (level, magic level): P 100 (the floor: 70) and P 380
EAST = 1
KNIGHT = 4

# Thais streets far from monster spawns, off the protection zone; every test has tiles of its own (a player who hit
# another stays logged in a while), and the area spells reach no other test's tiles while it runs.
RUNE_ROWS = {name: 32296 + i for i, name in enumerate(
    ["fireball-low", "fireball-high", "gfb-low", "gfb-high", "explosion-low", "explosion-high", "sd-low", "sd-high"])}
RUNE_X, RUNE_TARGET_X = 32326, 32329          # 3 tiles apart
SPELL_ROWS = {name: 32296 + i for i, name in enumerate(
    ["wave-low", "wave-high", "beam-low", "beam-high", "flame-low", "flame-high", "force-low", "force-high"])}
SPELL_X = 32334                               # the target stands in front (east): strikes reach only that tile


def power(level, maglevel):
    return max(100, level * 2 + maglevel * 3)


@pytest.fixture
def player(server, db, items):
    """new_player with more health and mana than its level gives (big enough to take or cast many spells):
    player(healthmax=..., manamax=..., **create_character kwargs)."""
    clients = []

    def make(healthmax=None, manamax=None, **kwargs) -> GameClient:
        char = db.create_character(storage={30001: 1}, **kwargs)
        con = db._connect()
        try:
            if healthmax:
                con.execute("UPDATE players SET healthmax = ?, health = ? WHERE id = ?",
                            (healthmax, kwargs.get("health") or healthmax, char.guid))
            if manamax:
                con.execute("UPDATE players SET manamax = ?, mana = ? WHERE id = ?", (manamax, manamax, char.guid))
            con.commit()
        finally:
            con.close()
        client = GameClient(items, port=server.port)
        client.login(char.account, char.password, char.name)
        client.character = char
        clients.append(client)
        assert client.pos == kwargs["pos"], f"placed at {client.pos}, not {kwargs['pos']}"
        return client

    yield make
    for c in clients:
        c.logout()


def _target(player, pos):
    return player(pos=pos, level=300, vocation=4, healthmax=20000)


def _check(name, hits, shots, lo, hi):
    print(f"\n{name}: expected {lo}-{hi}, hits {sorted(hits)}")
    assert len(hits) >= shots - 2, f"only {len(hits)} of {shots} shots seen: {hits}"
    assert all(lo - 1 <= h <= hi + 1 for h in hits), f"outside {lo}-{hi}: {sorted(hits)}"


def _halved(p, mina, maxa):
    """combat.cpp FORMULA_LEVELMAGIC: int(P x a) each end; then halved player against player."""
    return int(p * mina) // 2, int(p * maxa) // 2


# --- runes ---------------------------------------------------------------------------------------------------------
RUNES = [  # (row, rune, colour, 7.4 min and max share of P)
    ("fireball", FIREBALL, FIRE, 0.15, 0.25),
    ("gfb", GFB, FIRE, 0.35, 0.65),
    ("explosion", EXPLOSION, PHYSICAL, 0.20, 1.00),
    ("sd", SD, PHYSICAL, 1.30, 1.70),          # decided with the user 2026-10-04 (was 125 %P + 30 .. 170 %P)
]
# sudden death needs magic level 15: level 20 / ML 15 is P 85, so 100
RUNE_LOW = {"sd": (20, 15)}


@pytest.mark.parametrize("name, rune, color, mina, maxa", RUNES, ids=[r[0] for r in RUNES])
@pytest.mark.parametrize("which, stats", [("low", LOW), ("high", HIGH)], ids=["P 100", "P 380"])
def test_rune_damage_grows_with_magic_power(player, items, name, rune, color, mina, maxa, which, stats):
    """Fireball 15-25, great fireball 35-65, explosion 20-100, sudden death 130-170 % of magic power
    (tibiantis-notes Magic, OTHire, formulas.md §5); they were 16-33, 40 + 30 .. 70, 15-90 and 125 + 30 .. 170 %P
    (sudden death decided with the user 2026-10-04)."""
    y = RUNE_ROWS[f"{name}-{which}"]
    target = _target(player, (RUNE_TARGET_X, y, 7))
    level, maglevel = RUNE_LOW.get(name, stats) if which == "low" else stats
    caster = player(pos=(RUNE_X, y, 7), level=level, vocation=5, maglevel=maglevel, manamax=5000,
                    inventory={BACKPACK: Item(BAG, contents=[Item(rune, 3)] * 5)})
    caster.set_fight_modes(fight=1, chase=0, safe=0)
    shots = 12
    hits = _shoot(caster, items, rune, target, shots, color)
    lo, hi = _halved(power(level, maglevel), mina, maxa)
    _check(f"{name} level {level} ML {maglevel}", hits, shots, lo, hi)


# --- instant attack spells -----------------------------------------------------------------------------------------
SPELLS = [  # (row, words, colour, 7.4 min and max share of P, exhaustion)
    ("wave", "exevo mort hur", ENERGY, 1.00, 2.00, 2.1),
    ("beam", "exevo vis lux", ENERGY, 0.40, 0.80, 2.1),
    ("flame", "exori flam", FIRE, 0.35, 0.55, 1.1),
    ("force", "exori mort", PHYSICAL, 0.35, 0.55, 1.1),   # decided with the user 2026-10-04 (was 20-50 %P)
]
# the floor needs magic level 20 for energy wave: level 15 / ML 20 is P 90, so 100
SPELL_LOW = {"wave": (15, 20), "beam": LOW, "flame": LOW, "force": LOW}


@pytest.mark.parametrize("name, words, color, mina, maxa, exhaust", SPELLS, ids=[s[0] for s in SPELLS])
@pytest.mark.parametrize("which", ["low", "high"], ids=["P 100", "P 380"])
def test_spell_damage_grows_with_magic_power(player, name, words, color, mina, maxa, exhaust, which):
    """Energy wave 100-200, energy beam 40-80, flame strike and force strike 35-55 % of magic power
    (tibiantis-notes Magic, OTHire); energy wave was 115-190, flame strike 25-55 and force strike 20-50 %P (force
    strike decided with the user 2026-10-04). The target stands in front of the caster."""
    y = SPELL_ROWS[f"{name}-{which}"]
    target = _target(player, (SPELL_X + 1, y, 7))
    level, maglevel = SPELL_LOW[name] if which == "low" else HIGH
    caster = player(pos=(SPELL_X, y, 7), level=level, vocation=5, maglevel=maglevel, manamax=5000)
    caster.set_fight_modes(fight=1, chase=0, safe=0)
    caster.turn(EAST)
    time.sleep(0.5)
    shots = 12
    start = len(target.animated_texts)
    for _ in range(shots):
        caster.say(words)
        time.sleep(exhaust)
    time.sleep(0.5)
    hits = _hits(target, target.pos, start, color)
    lo, hi = _halved(power(level, maglevel), mina, maxa)
    _check(f"{words} level {level} ML {maglevel}", hits, shots, lo, hi)


# --- berserk: level only ------------------------------------------------------------------------------------------
@pytest.mark.parametrize("level, maglevel, y", [(30, 5, 32298), (100, 60, 32301)], ids=["level 30", "level 100"])
def test_berserk_hits_by_level_only(player, level, maglevel, y):
    """Berserk (exori): 2.4-4.0 x level, no magic level term (TI-Calc level/25 x 60..100, formulas.md §2; decided
    with the user 2026-10-04); halved against a player: level 30 72-120, halved 36-60, level 100 with
    magic level 60 240-400 halved 120-200. It was (2L + 3ML) x 1.4..1.65: 70-82 and 266-313 halved."""
    knight_pos = (32321, y, 7)                    # the 3x3 around it reaches only the target (west of the rune rows)
    target = _target(player, (knight_pos[0] + 1, y, 7))
    knight = player(pos=knight_pos, level=level, vocation=KNIGHT, maglevel=maglevel, manamax=5000)
    knight.set_fight_modes(fight=1, chase=0, safe=0)
    time.sleep(0.5)
    shots = 10
    start = len(target.animated_texts)
    for _ in range(shots):
        knight.say("exori")
        time.sleep(2.1)
    time.sleep(0.5)
    hits = _hits(target, target.pos, start, PHYSICAL)
    lo, hi = int(level * 2.4) // 2, int(level * 4.0) // 2
    _check(f"exori level {level} ML {maglevel}", hits, shots, lo, hi)


# --- healing -------------------------------------------------------------------------------------------------------
def _heals(healed, cast, times, pause):
    """Health gained by each of `times` casts (health read from the healed player's own stats)."""
    gained = []
    for _ in range(times):
        before = healed.stats.health
        cast()
        healed.wait_for(lambda: healed.stats.health != before, timeout=3)
        time.sleep(pause)
        gained.append(healed.stats.health - before)
    return gained


@pytest.mark.parametrize("which, stats, y", [("low", (20, 4), 32226), ("high", HIGH, 32228)],
                         ids=["P 100", "P 380"])
def test_ultimate_healing_rune_heals_250_percent_of_magic_power(player, items, which, stats, y):
    """UH rune: a fixed 250 % of magic power, not random (tibiantis-notes Magic, OTHire 250/0, TibiaWiki 2007 "not
    random on use"): 250 at the floor, 950 at P 380. Up to 2 more for a regeneration tick in between."""
    target = player(pos=(32313, y, 7), level=300, vocation=4, healthmax=20000, health=1)
    level, maglevel = stats
    caster = player(pos=(32312, y, 7), level=level, vocation=5, maglevel=maglevel, manamax=5000,
                    inventory={BACKPACK: Item(BAG, contents=[Item(UH, 1)] * 4)})
    caster.open_container(BACKPACK)
    cid = min(caster.containers)
    uh = items.by_server[UH].client_id

    def use():
        caster.use_item_with(caster.container_pos(cid, 0), uh, 0, target.pos, CREATURE, 1)

    gained = _heals(target, use, 4, 1.2)
    want = int(power(level, maglevel) * 2.5)
    print(f"\nUH level {level} ML {maglevel}: expected {want}, healed {gained}")
    assert all(want <= g <= want + 2 for g in gained), f"healed {gained}, 7.4 {want}"


@pytest.mark.parametrize("which, stats, y", [("low", (20, 8), 32226), ("high", HIGH, 32228)],
                         ids=["P 100", "P 380"])
def test_exura_vita_heals_200_to_300_percent_of_magic_power(player, which, stats, y):
    """exura vita: 200-300 % of magic power (tibiantis-notes Magic, OTHire 250/50, TI-Calc): 200-300 at the floor
    (magic level 8 is needed), 760-1140 at P 380."""
    level, maglevel = stats
    mage = player(pos=(32318, y, 7), level=level, vocation=5, maglevel=maglevel, manamax=5000,
                  healthmax=20000, health=1)
    gained = _heals(mage, lambda: mage.say("exura vita"), 8, 1.2)
    p = power(level, maglevel)
    lo, hi = int(p * 2.0), int(p * 3.0)
    print(f"\nexura vita level {level} ML {maglevel}: expected {lo}-{hi}, healed {sorted(gained)}")
    assert all(lo <= g <= hi + 2 for g in gained), f"healed {sorted(gained)}, 7.4 {lo}-{hi}"
    assert max(gained) - min(gained) >= (hi - lo) // 4, f"hardly random: {sorted(gained)}"


# --- poison: no hit, a poison of a share of magic power ------------------------------------------------------------
def _first_ticks(targets, wait):
    """The first poison number over each target (7.4: 5% of the total, rounded up, 4 s after the cast); no other
    number may show over it (the spells do not hit)."""
    time.sleep(wait)
    first = []
    for t, start, _ in targets:
        texts = [(p, c, x) for p, c, x in t.animated_texts[start:] if tuple(p) == tuple(t.pos)]
        nums = [int(x) for p, c, x in texts if c == POISON and x.strip().isdigit()]
        others = [x for p, c, x in texts if c != POISON]
        assert not others, f"not poison: {others}"
        first.append(nums[0] if nums else None)
    return first


def test_poison_storm_poisons_for_150_to_250_percent_of_magic_power(player):
    """No hit, every creature around is poisoned for 150-250 % of magic power (tibiantis-notes, TibiaWiki 2005-07
    "poisons the enemy with 200+/-50", OTHire 200/50): at the floor (level 8, ML 28 - the spell's level) the total
    is 150-250, so the first tick ceil(total / 20) is 8-13; not halved against players. It was a hit of
    150-250 %P plus a poison of 100."""
    caster_pos = (32334, 32216, 7)
    targets = [_target(player, (32331, 32215 + i, 7)) for i in range(3)]
    caster = player(pos=caster_pos, level=8, vocation=6, maglevel=28, manamax=5000)
    caster.set_fight_modes(fight=1, chase=0, safe=0)
    marks = [(t, len(t.animated_texts), time.time()) for t in targets]
    caster.say("exevo gran mas pox")
    time.sleep(2.5)
    for t, start, _ in marks:
        hit = [x for p, c, x in t.animated_texts[start:] if tuple(p) == tuple(t.pos)]
        assert not hit, f"poison storm hit at once: {hit}"
    first = _first_ticks(marks, wait=3.0)
    print(f"\npoison storm P 100: first ticks {first} (7.4: 8-13)")
    assert all(f is not None and 8 <= f <= 13 for f in first), first


def test_envenom_poisons_for_50_to_90_percent_of_magic_power(player, items):
    """Envenom: no hit, a poison of 50-90 % of magic power (tibiantis-notes Magic/poison, OTHire 70/20); at P 380 a
    total of 190-342, a first tick of 10-18. It was a fixed fire burn of about 80."""
    caster_pos = (32324, 32226, 7)
    targets = [_target(player, (32327, 32225 + i, 7)) for i in range(3)]
    level, maglevel = HIGH
    caster = player(pos=caster_pos, level=level, vocation=6, maglevel=maglevel, manamax=5000,
                    inventory={BACKPACK: Item(BAG, contents=[Item(ENVENOM, 3)])})
    caster.set_fight_modes(fight=1, chase=0, safe=0)
    caster.open_container(BACKPACK)
    cid = min(caster.containers)
    marks = []
    for t in targets:
        marks.append((t, len(t.animated_texts), time.time()))
        caster.use_item_with(caster.container_pos(cid, 0), items.by_server[ENVENOM].client_id, 0, t.pos, CREATURE, 1)
        time.sleep(2.6)                     # 2 s rune exhaustion; 2.1 s was sometimes "You are exhausted."
    first = _first_ticks(marks, wait=3.0)
    print(f"\nenvenom P 380: first ticks {first} (7.4: 10-18)")
    assert all(f is not None and 10 <= f <= 18 for f in first), first

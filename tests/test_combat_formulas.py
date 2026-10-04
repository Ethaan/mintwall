"""Combat measured in game against the 7.4 formulas (docs/reference-74/formulas.md §5-6), asked by the user 2026-10-03:
characters of different levels and magic levels hit a target many times; every hit is read from the damage number
the client shows over the target (animated text). Player against player, so each hit is halved (combat.cpp).

  - runes: damage = base x magic power, magic power = level x 2 + magic level x 3 (at least 100)
  - stone skin amulet: takes 80% of physical damage (a sudden death is physical in 7.4), 5 charges
  - armor: each melee hit loses about 50-100% of the armor value (7.4); the target takes much less
"""
import random
import statistics
import time

import pytest

from tibia74 import BACKPACK, Item, NECKLACE

HMM, SD, STONE_SKIN, BAG = 2311, 2268, 2197, 1988
MAGIC_SWORD = 2400
ARMOR_SET = {1: 2496, 4: 2472, 7: 2470, 8: 2645}   # horned helmet 11, magic plate armor 17, golden legs 9, steel boots 3
FIELD = (32320, 32214, 7)          # open street in Thais, no protection zone, 40+ tiles from any monster spawn: a
                                   # monster hitting the target would add its numbers (Rookgaard's premium side did)
ENERGY, PHYSICAL = 35, 180         # damage number colours (const.h TEXTCOLOR_LIGHTBLUE / TEXTCOLOR_RED)
CREATURE = 0x63


def _row(r):
    return (FIELD[0], FIELD[1] + r, FIELD[2]), (FIELD[0] + 3, FIELD[1] + r, FIELD[2])


def _target(new_player, pos, **kwargs):
    t = new_player(pos=pos, level=300, vocation=4, storage={30001: 1}, **kwargs)   # 4500 hp: survives the test
    assert t.pos == pos, f"target placed at {t.pos}, not {pos}"
    return t


def _caster(new_player, pos, level, maglevel, rune, runes):
    p = new_player(pos=pos, level=level, vocation=5, maglevel=maglevel, mana=5000, storage={30001: 1},
                   inventory={BACKPACK: Item(BAG, contents=[Item(rune, 5 if rune == HMM else 1)] * runes)})
    assert p.pos == pos, f"caster placed at {p.pos}, not {pos}"
    p.set_fight_modes(fight=1, chase=0, safe=0)          # secure mode off: an unmarked player can be hit
    return p


def _hits(observer, pos, since, color):
    """The damage numbers of one colour shown over `pos` since index `since` of the observer's animated texts."""
    return [int(t) for p, c, t in observer.animated_texts[since:]
            if tuple(p) == tuple(pos) and c == color and t.strip().isdigit()]


def _shoot(caster, items, rune, target, shots, color):
    if not caster.containers:                       # the second volley: the backpack is open already
        caster.open_container(BACKPACK)
    cid = min(caster.containers)
    start = len(target.animated_texts)
    for _ in range(shots):
        caster.use_item_with(caster.container_pos(cid, 0), items.by_server[rune].client_id, 0, target.pos, CREATURE, 1)
        time.sleep(2.1)                                    # rune exhaustion
    time.sleep(0.5)
    return _hits(target, target.pos, start, color)


def _range(power, mina, minb, maxa):
    """Our rune formula (combat.cpp FORMULA_LEVELMAGIC), halved player against player."""
    return int(power * mina + minb) // 2, int(power * maxa) // 2


@pytest.mark.parametrize("level, maglevel, row", [(20, 5, 0), (100, 60, 1)], ids=["power 100 (floor)", "power 380"])
def test_heavy_magic_missile_grows_with_magic_power(new_player, items, level, maglevel, row):
    """HMM 20-40% of magic power: level 20 / ML 5 is the floor 100 (20-40), level 100 / ML 60 is 380 (76-152);
    halved against a player."""
    at, to = _row(row)
    target = _target(new_player, to)
    caster = _caster(new_player, at, level, maglevel, HMM, 4)
    hits = _shoot(caster, items, HMM, target, 12, ENERGY)
    power = max(100, level * 2 + maglevel * 3)
    lo, hi = _range(power, 0.2, 0, 0.4)
    print(f"\nHMM level {level} ML {maglevel} (power {power}): expected {lo}-{hi}, hits {sorted(hits)}")
    assert len(hits) >= 10, f"only {len(hits)} of 12 shots seen: {hits}"
    assert all(lo - 1 <= h <= hi + 1 for h in hits), f"outside {lo}-{hi}: {sorted(hits)}"


def test_stone_skin_amulet_takes_80_percent_of_a_sudden_death(new_player, items, db):
    """SD (physical in 7.4) on the same target without and with a stone skin amulet: 1/5 of the damage, and the
    amulet is gone after its 5 charges."""
    at, to = _row(3)
    target = _target(new_player, to)
    caster = _caster(new_player, at, 100, 70, SD, 12)
    bare = _shoot(caster, items, SD, target, 5, PHYSICAL)
    beside = (to[0], to[1] + 1, to[2])          # the first target stays (in fight, it cannot log out)
    armed = new_player(pos=beside, level=300, vocation=4, storage={30001: 1},
                       inventory={NECKLACE: Item(STONE_SKIN, 5)})
    assert armed.pos == beside, armed.pos
    shielded = _shoot(caster, items, SD, armed, 5, PHYSICAL)
    power = 100 * 2 + 70 * 3
    lo, hi = _range(power, 1.25, 30, 1.7)
    print(f"\nSD power {power}: expected {lo}-{hi}; bare {sorted(bare)}; with the amulet {sorted(shielded)}")
    assert bare and all(lo - 1 <= h <= hi + 1 for h in bare), f"bare SD outside {lo}-{hi}: {bare}"
    assert len(shielded) == 5, shielded
    assert all(lo // 5 - 1 <= h <= hi // 5 + 1 for h in shielded), f"not 1/5 ({lo // 5}-{hi // 5}): {shielded}"
    assert armed.wait_for(lambda: NECKLACE not in armed.inventory, timeout=3), "the amulet survived 5 charges"


def _melee(new_player, attacker_pos, target_pos, armor, seconds=40):
    """A knight (sword skill 50, a sword: atk 14 - a hit of at most 41) hits the target for `seconds`;
    returns the damage numbers and the hp the target lost."""
    target = new_player(pos=target_pos, level=300, vocation=4, storage={30001: 1},
                        inventory=dict(armor) if armor else None)
    assert target.pos == target_pos, target.pos
    knight = new_player(pos=attacker_pos, level=60, vocation=4, skills={2: 50}, storage={30001: 1},
                        inventory={5: Item(2376)})          # sword, atk 14
    knight.set_fight_modes(fight=2, chase=1, safe=0)        # balanced
    start = len(target.animated_texts)
    knight.attack(target.player_id)
    time.sleep(seconds)
    knight.attack(0)
    time.sleep(1)
    hits = _hits(target, target.pos, start, PHYSICAL)          # the numbers, not the health bar: its first value
    return hits, sum(hits)                                     # can come in after the attack has begun


def _expected_melee(skill, atk, armor, turns=20000):
    """7.4 (formulas.md §6): max = (5 x skill + 50) x atk x 0.99 / 100, the hit rolled as the average of two
    0..max rolls; armor takes floor(A/2) + floor(A/2 x r/99) with r 0..98; halved player against player."""
    top = int((5 * skill + 50) * atk * 0.99 / 100)
    total = 0
    for _ in range(turns):
        hit = (random.randint(0, top) + random.randint(0, top)) // 2
        hit -= armor // 2 + int(armor // 2 * random.randint(0, 98) / 99)
        total += max(0, hit) // 2
    return total / turns


def test_armor_takes_off_melee_damage(new_player):
    """The same knight hits a bare target and one in heavy armor (horned helmet, magic plate armor, golden legs,
    steel boots): the armored one takes much less, as the 7.4 armor formula says."""
    a, b = _row(5)
    bare_hits, bare_lost = _melee(new_player, a, b, None)
    c, d = _row(7)
    armor = {slot: Item(item) for slot, item in ARMOR_SET.items()}
    armed_hits, armed_lost = _melee(new_player, c, d, armor)
    print(f"\nmelee sword 50 atk 14 for 40 s: bare lost {bare_lost} ({len(bare_hits)} hits, mean "
          f"{statistics.mean(bare_hits) if bare_hits else 0:.1f}), armored lost {armed_lost} ({len(armed_hits)} "
          f"hits, mean {statistics.mean(armed_hits) if armed_hits else 0:.1f})")
    assert bare_lost > 0, "the bare target was never hit"
    assert armed_lost < bare_lost * 0.6, f"armor saved too little: {armed_lost} vs {bare_lost}"


# --- distance and shield blocks ------------------------------------------------------------------------------------
FIELD2 = (32328, 32290, 7)         # another Thais street block, far from monsters
CROSSBOW, BOLT, DRAGON_SHIELD = 2455, 2543, 2516


def _row2(r):
    return (FIELD2[0], FIELD2[1] + r, FIELD2[2]), (FIELD2[0] + 3, FIELD2[1] + r, FIELD2[2])


def test_crossbow_bolts_hit_as_the_melee_formula_with_the_ammo_attack(new_player):
    """7.4: the bow's and ammunition's attack in the melee formula - distance 60, bolts (30): at most
    (5 x 60 + 50) x 30 x 0.99 / 100 = 103, halved against a player; adjacent... at 3 tiles about 9 shots in 10 hit."""
    at, to = _row2(0)
    target = _target(new_player, to)
    paladin = new_player(pos=at, level=60, vocation=3, skills={4: 60}, storage={30001: 1},
                         inventory={5: Item(CROSSBOW), 10: Item(BOLT, 100)})
    assert paladin.pos == at, paladin.pos
    paladin.set_fight_modes(fight=2, chase=0, safe=0)         # balanced, stand still
    start = len(target.animated_texts)
    paladin.attack(target.player_id)
    time.sleep(30)
    paladin.attack(0)
    time.sleep(1)
    hits = _hits(target, target.pos, start, PHYSICAL)
    top = int((5 * 60 + 50) * 30 * 0.99 / 100) // 2
    print(f"\ncrossbow + bolts, distance 60, 30 s: max {top}, {len(hits)} hits {sorted(hits)}")
    assert len(hits) >= 10, f"only {len(hits)} hits in 30 s (a shot every 2 s, ~90% hit): {hits}"
    assert all(1 <= h <= top + 1 for h in hits), f"outside 1-{top}: {sorted(hits)}"
    assert top * 0.3 <= statistics.mean(hits) <= top * 0.7, f"mean {statistics.mean(hits):.1f} of max {top}"


def _expected_blocked(skill, atk, shield_skill, shield_def, turns=20000):
    """7.4: the hit rolled as above, the block max (5 x shielding + 50) x def / 100 rolled the same way and taken
    off; halved player against player."""
    top = int((5 * skill + 50) * atk * 0.99 / 100)
    block = int((5 * shield_skill + 50) * shield_def / 100)
    total = 0
    for _ in range(turns):
        hit = (random.randint(0, top) + random.randint(0, top)) // 2
        hit -= (random.randint(0, block) + random.randint(0, block)) // 2 if block else 0
        total += max(0, hit) // 2
    return total / turns


def _hitter(new_player, attacker_pos, target, seconds=40):
    knight = new_player(pos=attacker_pos, level=100, vocation=4, skills={2: 80}, storage={30001: 1},
                        inventory={5: Item(MAGIC_SWORD)})
    knight.set_fight_modes(fight=2, chase=1, safe=0)
    start = len(target.animated_texts)
    knight.attack(target.player_id)
    time.sleep(seconds)
    knight.attack(0)
    time.sleep(1)
    return sum(_hits(target, target.pos, start, PHYSICAL))


def test_a_shield_blocks_melee_as_7_4(new_player):
    """A magic sword (atk 48) in sword 80 hands against a knight with shielding 80 and a dragon shield (def 31) and
    against the same knight with no shield: the shield takes off about what the 7.4 block formula says."""
    a, b = _row2(2)
    bare = new_player(pos=b, level=300, vocation=4, storage={30001: 1}, skills={5: 80})
    bare_lost = _hitter(new_player, a, bare)
    c, d = _row2(4)
    shielded = new_player(pos=d, level=300, vocation=4, storage={30001: 1}, skills={5: 80},
                          inventory={6: Item(DRAGON_SHIELD)})
    shielded_lost = _hitter(new_player, c, shielded)
    turns = 20
    want_bare, want_shielded = _expected_melee(80, 48, 0) * turns, _expected_blocked(80, 48, 80, 31) * turns
    print(f"\nmagic sword, sword 80, 40 s: bare lost {bare_lost} (7.4 ~{want_bare:.0f}), dragon shield / shielding 80 "
          f"lost {shielded_lost} (7.4 ~{want_shielded:.0f})")
    assert 0.6 * want_bare <= bare_lost <= 1.4 * want_bare
    assert shielded_lost <= 0.6 * bare_lost, "the shield blocked too little"
    assert 0.5 * want_shielded <= shielded_lost <= 1.6 * want_shielded

"""Death rules from docs/reference-74/death.md."""
import time

import pytest

from tibia74 import Item, RIGHT

ROAD = (32091, 32194, 7)           # open ground north-west of the Rookgaard temple, not a protection zone:
                                   # killers stay online in-fight after a kill, so not on the road test_walking uses
RED_SKULL = 4
KNIGHT, ELITE_KNIGHT = 4, 8
BAG = 1987


def _killer(new_player, pos):
    return new_player(pos=pos, level=100, vocation=KNIGHT, inventory={RIGHT: Item(2400)},   # magic sword
                      skills={2: 100})


def _kill(killer, victim, timeout=30):
    killer.set_fight_modes(fight=1, chase=1, safe=0)   # secure mode off, or no unmarked player can be attacked
    killer.attack(victim.player_id)
    assert killer.wait_for(lambda: victim.player_id in killer.removed_creatures or not victim.connected,
                           timeout=timeout),         f"{victim.name} did not die: victim at {victim.pos}, killer at {killer.pos}, "         f"killer saw {killer.text_messages[-3:]}"
    killer.attack(0)
    time.sleep(0.5)


def test_red_skull_after_3_unjustified_kills_in_a_day(new_player):
    """7.4: 3 unjustified kills a day (or 5 a week, 10 a month) give a red skull for 30 days."""
    killer = _killer(new_player, ROAD)
    me = killer.wait_for(lambda: killer.creatures.get(killer.player_id), timeout=5)
    for n in range(3):
        victim = new_player(pos=(ROAD[0], ROAD[1] + 1, ROAD[2]), vocation=KNIGHT, storage={30001: 1})   # a vocation: Rookgaard characters (none) cannot be attacked
        _kill(killer, victim)
        if n < 2:
            assert me.skull != RED_SKULL, f"red skull after {n + 1} kill(s)"
    assert killer.messages("was not justified"), killer.text_messages[-3:]
    assert killer.wait_for(lambda: me.skull == RED_SKULL, timeout=3), f"skull {me.skull} after 3 kills"


@pytest.mark.parametrize("premium_days, described_as", [(0, "a knight"), (30, "an elite knight")])
def test_promotion_only_works_with_premium(new_player, db, premium_days, described_as):
    """7.4: without premium a promoted character plays as its base vocation; the promotion is kept."""
    p = new_player(pos=ROAD, level=20, vocation=ELITE_KNIGHT, premium_days=premium_days)
    start = len(p.text_messages)
    p.look(p.pos, 0x63, 1)
    assert p.wait_for(lambda: any("You see yourself" in t for _, t in p.text_messages[start:]), timeout=3)
    seen = next(t for _, t in p.text_messages[start:] if "You see yourself" in t)
    assert f"You are {described_as}." in seen, seen
    p.logout()
    assert db.character(p.character.guid)["vocation"] == ELITE_KNIGHT, "the saved promotion was lost"


SORCERER, MASTER_SORCERER = 1, 5


def _described_as(c):
    start = len(c.text_messages)
    c.look(c.pos, 0x63, 1)
    assert c.wait_for(lambda: any("You see yourself" in t for _, t in c.text_messages[start:]), timeout=3)
    return next(t for _, t in c.text_messages[start:] if "You see yourself" in t)


def test_promotion_is_suspended_without_premium_and_back_with_it(new_player, db, server, items):
    """A master sorcerer whose premium ran out plays and shows as a sorcerer (TibiaWiki: promotions are
    "suspended when Premium Time expires [...] if you obtain another Premium Time, you will regain access"); the
    next login with premium is a master sorcerer again."""
    p = new_player(pos=ROAD, level=30, vocation=MASTER_SORCERER, premium_days=0, storage={30001: 1})
    assert "You are a sorcerer." in _described_as(p)
    character = p.character
    p.logout()
    assert db.character(character.guid)["vocation"] == MASTER_SORCERER, "the saved promotion was lost"
    con = db._connect()
    con.execute("UPDATE accounts SET premend = strftime('%s', 'now') + 30 * 86400 WHERE id = ?", (character.account,))
    con.commit()
    con.close()
    again = GameClient(items, port=server.port).login(character.account, character.password, character.name)
    try:
        assert "You are a master sorcerer." in _described_as(again)
    finally:
        again.logout()


def test_dying_back_to_rookgaard_keeps_the_new_bag(new_player, db):
    """Sent to Rookgaard by a death: the starter set used to land in the mainland corpse."""
    killer = _killer(new_player, ROAD)
    victim = new_player(pos=(ROAD[0], ROAD[1] + 1, ROAD[2]), level=6, vocation=KNIGHT, storage={30001: 1})
    guid = victim.character.guid
    _kill(killer, victim)
    deadline = time.time() + 5
    while time.time() < deadline and db.character(guid)["level"] != 1:
        time.sleep(0.2)
    row = db.character(guid)
    assert row["level"] == 1 and row["vocation"] == 0 and row["town_id"] == 1, \
        {k: row[k] for k in ("level", "vocation", "town_id")}
    assert any(r["pid"] == 3 and r["itemtype"] == BAG for r in db.items(guid)), \
        f"no bag in the backpack slot: {[(r['pid'], r['itemtype']) for r in db.items(guid)]}"


# ----------------------------------------------------------------------------- blessings

from tibia74 import BACKPACK, GameClient, SERVER_DIR   # noqa: E402
from tibia74.npcs import load_npcs                     # noqa: E402
from tibia74.server import TESTER_GROUP                # noqa: E402

BLESSING_STORAGE = 30010                               # + number, compat.lua / Player::BLESSING_STORAGE
ALL_BLESSINGS = {BLESSING_STORAGE + b: 1 for b in range(1, 6)}
NPCS = load_npcs(SERVER_DIR)
COINS = {2148: 1, 2152: 100, 2160: 10000}


def _money(db, guid):
    return sum(COINS.get(r["itemtype"], 0) * r["count"] for r in db.items(guid))


def _storage(db, guid, key):
    con = db._connect()
    try:
        row = con.execute("SELECT value FROM player_storage WHERE player_id = ? AND key = ?", (guid, key)).fetchone()
        return row[0] if row else None
    finally:
        con.close()


def _saved(p, db):
    guid = p.character.guid
    p.logout()
    deadline = time.time() + 5
    while time.time() < deadline and not db.character(guid)["lastlogout"]:
        time.sleep(0.2)
    return guid


def _login_at(server, items, db, character, pos):
    """Log a (logged out) character in at pos - how a test 'walks' to the next NPC or out of a temple."""
    con = db._connect()
    con.execute("UPDATE players SET posx = ?, posy = ?, posz = ? WHERE id = ?", (*pos, character.guid))
    con.commit()
    con.close()
    c = GameClient(items, port=server.port)
    c.login(character.account, character.password, character.name)
    c.character = character
    return c


def _near(new_player, spawn, **kwargs):
    """A new character standing next to an NPC's spawn (tries a few tiles: counters, walls, the NPC)."""
    for dx, dy in ((2, 0), (0, 2), (-2, 0), (0, -2), (1, 1), (-1, 1), (1, -1), (-1, -1),
                   (1, 0), (0, 1), (-1, 0), (0, -1)):
        p = new_player(pos=(spawn[0] + dx, spawn[1] + dy, spawn[2]), **kwargs)
        if p.pos[2] == spawn[2] and max(abs(p.pos[0] - spawn[0]), abs(p.pos[1] - spawn[1])) <= 3:
            return p
        p.logout()
    raise AssertionError(f"could not stand next to {spawn}")


def _buyer(new_player, npc, **kwargs):
    kwargs.setdefault("group_id", TESTER_GROUP)
    return _near(new_player, NPCS[npc].pos, level=50, premium_days=30, storage={30001: 1}, **kwargs,
                 inventory={BACKPACK: Item(1988, contents=[Item(2160, 2)])})     # 20000 gp


def _chat(p, npc, *lines):
    """Talk to an NPC while following it: Eremo walks every second and would leave talk range."""
    target = p.wait_for(lambda: next((c for c in p.creatures.values() if c.name == npc), None), timeout=3)
    assert target, f"{npc} is not in view"
    p.follow(target.id)
    p.wait_for(lambda: target.pos and p.pos and target.pos[2] == p.pos[2]
               and max(abs(target.pos[0] - p.pos[0]), abs(target.pos[1] - p.pos[1])) <= 1, timeout=5)
    try:
        return p.talk(*lines, npc=npc)
    finally:
        p.follow(0)


@pytest.mark.parametrize("npc, word, number", [
    ("Norf", "shielding", 2), ("Humphrey", "embrace", 1), ("Edala", "suns", 3), ("Eremo", "solitude", 4),
])
def test_npc_blesses_for_10000_on_one_word_of_the_name(new_player, db, npc, word, number):
    p = _buyer(new_player, npc)
    said = _chat(p, npc, "hi", word, "yes")
    assert any("You have been blessed" in r for r in said), said
    said = _chat(p, npc, word, "yes")
    assert any("already blessed" in r for r in said), f"blessed twice: {said}"
    guid = _saved(p, db)
    assert _money(db, guid) == 10000, f"paid {20000 - _money(db, guid)} gp"
    assert _storage(db, guid, BLESSING_STORAGE + number) == 1


def test_spark_of_the_phoenix_needs_kawill_then_pydar(new_player, server, items, db):
    """Kawill gives the first part (free), Pydar the second for 10000 - not the other way round."""
    p = _buyer(new_player, "Pydar")
    said = _chat(p, "Pydar", "hi", "phoenix", "yes")
    assert any("from Kawill first" in r for r in said), said
    character = p.character
    guid = _saved(p, db)
    assert _money(db, guid) == 20000, "Pydar took money without Kawill's part"

    kawill = NPCS["Kawill"].pos
    p = _login_at(server, items, db, character, (kawill[0], kawill[1] + 1, kawill[2]))
    said = _chat(p, "Kawill", "hi", "spark", "yes")
    assert any("first part" in r for r in said), said
    _saved(p, db)
    assert _money(db, guid) == 20000, "Kawill should not take money"

    pydar = NPCS["Pydar"].pos
    p = _login_at(server, items, db, character, (pydar[0], pydar[1] + 1, pydar[2]))
    said = _chat(p, "Pydar", "hi", "phoenix", "yes")
    assert any("You have been blessed" in r for r in said), said
    _saved(p, db)
    assert _money(db, guid) == 10000
    assert _storage(db, guid, BLESSING_STORAGE + 5) == 1


def test_a_bought_blessing_lowers_the_loss_and_is_lost_on_death(new_player, server, items, db):
    """Buy one blessing from Norf, then die: 9% instead of 10% experience, and the blessing is gone."""
    p = _buyer(new_player, "Norf", group_id=1, health=100, vocation=KNIGHT)   # testers cannot be attacked
    assert any("You have been blessed" in r for r in _chat(p, "Norf", "hi", "spiritual", "yes"))
    character = p.character
    guid = _saved(p, db)
    before = db.character(guid)["experience"]

    killer = _killer(new_player, ROAD)
    victim = _login_at(server, items, db, character, (ROAD[0], ROAD[1] + 1, ROAD[2]))   # out of the temple
    _kill(killer, victim)
    deadline = time.time() + 5
    while time.time() < deadline and db.character(guid)["experience"] == before:
        time.sleep(0.2)
    after = db.character(guid)["experience"]
    assert after == before - before * 9 // 100, f"lost {(before - after) / before:.2%}, expected 9%"
    assert _storage(db, guid, BLESSING_STORAGE + 2) in (None, 0), "the blessing survived the death"


@pytest.mark.parametrize("vocation, blessings, percent", [
    (KNIGHT, {}, 10), (KNIGHT, ALL_BLESSINGS, 5), (ELITE_KNIGHT, {}, 7), (ELITE_KNIGHT, ALL_BLESSINGS, 2),
])
def test_death_loss_is_10_percent_minus_blessings(new_player, db, vocation, blessings, percent):
    """10% of experience (7% promoted), 1 point less per blessing; all blessings are gone afterwards."""
    killer = _killer(new_player, ROAD)
    victim = new_player(pos=(ROAD[0], ROAD[1] + 1, ROAD[2]), level=50, vocation=vocation, premium_days=30,
                        health=100, storage={30001: 1, **blessings})   # a quick kill
    guid = victim.character.guid
    before = db.character(guid)["experience"]
    _kill(killer, victim)
    deadline = time.time() + 5
    while time.time() < deadline and db.character(guid)["experience"] == before:
        time.sleep(0.2)
    after = db.character(guid)["experience"]
    assert after == before - before * percent // 100, f"lost {(before - after) / before:.2%}, expected {percent}%"
    assert all(_storage(db, guid, key) in (None, 0) for key in ALL_BLESSINGS), "blessings survived the death"


# ----------------------------------------------------------------------------- levels, items, amulet of loss, respawn

from tibia74 import HEAD, NECKLACE, ARMOR, LEFT, LEGS, FEET, RING, AMMO   # noqa: E402
from tibia74.db import VOCATION_GAINS, capacity                          # noqa: E402

AMULET_OF_LOSS = 2173
ANKRAHMUN_TEMPLE, ANKRAHMUN_TOWN = (33194, 32853, 8), 9   # a home town far from where the victim dies
GOLD = 2148
ROPE, SHOVEL = 2120, 2554
WORN = {HEAD: 2457, NECKLACE: 2661, ARMOR: 2463, RIGHT: 2376, LEFT: 2525,   # steel helmet, scarf, plate armor,
        LEGS: 2647, FEET: 2643, RING: 2179, AMMO: 2544}                        # sword, dwarven shield, plate legs,
                                                                               # leather boots, gold ring, arrows


def _gear(necklace=None):
    """A backpack (rope, shovel, 50 gold) and something in every other slot."""
    gear = {slot: Item(item, 10 if slot == AMMO else 1) for slot, item in WORN.items()}
    gear[BACKPACK] = Item(1988, contents=[Item(ROPE), Item(SHOVEL), Item(GOLD, 50)])
    if necklace:
        gear[NECKLACE] = Item(necklace)
    return gear


def _after_death(db, guid, before):
    """Wait for the save that follows the death (the experience changes), then return the saved row."""
    deadline = time.time() + 5
    while time.time() < deadline and db.character(guid)["experience"] == before:
        time.sleep(0.2)
    row = db.character(guid)
    assert row["experience"] < before, "no save after the death"
    return row


def _kill_on(new_player, db, row, vocation=KNIGHT, **victim):
    """A knight (100 hp: a quick kill) killed on its own ROAD row; returns (guid, saved row after the death)."""
    killer = _killer(new_player, (ROAD[0], ROAD[1] + row, ROAD[2]))
    p = new_player(pos=(ROAD[0], ROAD[1] + row + 1, ROAD[2]), vocation=vocation, health=100,
                   storage={30001: 1}, **victim)
    guid = p.character.guid
    before = db.character(guid)["experience"]
    _kill(killer, p)
    return guid, _after_death(db, guid, before)


def _slots(db, guid):
    """{slot: item type} of what the saved character wears."""
    return {r["pid"]: r["itemtype"] for r in db.items(guid) if r["pid"] <= AMMO}


def test_lost_levels_take_their_hp_mana_and_cap_and_respawn_full(new_player, db):
    """Level 50 knight -10%: 1,662,570 exp is level 48, so two knight levels go: 2 x 15 hp, 5 mana, 25 cap.
    He comes back with full health and mana (killed at 100 hp and 0 mana)."""
    guid, row = _kill_on(new_player, db, 2, level=50, mana=0)
    assert row["experience"] == 1847300 - 184730 and row["level"] == 48, (row["experience"], row["level"])
    hp, mana, _ = VOCATION_GAINS[KNIGHT]
    assert (row["healthmax"], row["manamax"], row["cap"]) == (150 + 47 * hp, 47 * mana, capacity(KNIGHT, 48)), \
        {k: row[k] for k in ("healthmax", "manamax", "cap")}
    assert (row["health"], row["mana"]) == (row["healthmax"], row["manamax"]), \
        {k: row[k] for k in ("health", "healthmax", "mana", "manamax")}


def test_the_backpack_always_drops_other_items_10_percent_each(new_player, db):
    """The backpack goes into the corpse with its contents; each of the 9 other items drops at 10% - losing 6 or
    more of them would happen about once in 15,000 deaths."""
    guid, _ = _kill_on(new_player, db, 4, level=20, inventory=_gear())
    left = _slots(db, guid)
    assert BACKPACK not in left, f"the backpack stayed: {left}"
    assert not any(r["itemtype"] in (ROPE, SHOVEL, GOLD) for r in db.items(guid)), "the backpack's contents stayed"
    lost = [slot for slot in WORN if left.get(slot) != WORN[slot]]
    assert len(lost) <= 5, f"lost {len(lost)} of 9 equipped items (10% each): {lost}"


def test_amulet_of_loss_keeps_every_item_and_is_used_up(new_player, db):
    """Nothing drops, not even the backpack; the amulet is gone (not in the corpse either). The experience is
    still lost: the amulet protects items only."""
    guid, row = _kill_on(new_player, db, 6, level=20, inventory=_gear(necklace=AMULET_OF_LOSS))
    assert row["experience"] == 98800 - 9880, row["experience"]
    worn = {slot: item for slot, item in WORN.items() if slot != NECKLACE}
    left = _slots(db, guid)
    assert {slot: left.get(slot) for slot in worn} == worn and left.get(BACKPACK) == 1988, f"items dropped: {left}"
    assert sorted(r["itemtype"] for r in db.items(guid) if r["pid"] > AMMO) == sorted((ROPE, SHOVEL, GOLD)), \
        "the backpack lost its contents"
    assert NECKLACE not in left and not any(r["itemtype"] == AMULET_OF_LOSS for r in db.items(guid)), \
        "the amulet of loss was not used up"


def _red_skulled(db):
    """Mark the character just created as red skulled for 30 days (as Player::addUnjustifiedDead saves it)."""
    con = db._connect()
    con.execute("UPDATE players SET redskull = 1, redskulltime = strftime('%s', 'now') + 30 * 86400"
                " WHERE id = (SELECT MAX(id) FROM players)")
    con.commit()
    con.close()


@pytest.mark.parametrize("necklace, row", [(None, 8), (AMULET_OF_LOSS, 10)])
def test_a_red_skull_drops_everything_amulet_of_loss_or_not(new_player, db, server, items, necklace, row):
    """With a red skull all items go into the corpse; an amulet of loss does not help and is used up anyway."""
    character = db.create_character(level=20, vocation=KNIGHT, health=100, storage={30001: 1},
                                    pos=(ROAD[0], ROAD[1] + row + 1, ROAD[2]), inventory=_gear(necklace))
    _red_skulled(db)
    killer = _killer(new_player, (ROAD[0], ROAD[1] + row, ROAD[2]))
    p = GameClient(items, port=server.port).login(character.account, character.password, character.name)
    me = p.wait_for(lambda: p.creatures.get(p.player_id), timeout=5)
    time.sleep(2)   # a think or two: 30 days of red skull read back as ticks overflowed int32 and were dropped
    assert me and me.skull == RED_SKULL, f"the red skull is gone after logging in: {me}"
    before = db.character(character.guid)["experience"]
    _kill(killer, p)
    _after_death(db, character.guid, before)
    left = db.items(character.guid)
    assert not left, f"kept {[(r['pid'], r['itemtype']) for r in left]}"


def test_respawn_in_the_home_town_temple_with_full_health_and_mana(new_player, db, server, items):
    """Killed in Rookgaard, a character of Ankrahmun comes back in Ankrahmun's temple, at full health and mana."""
    guid, row = _kill_on(new_player, db, 12, level=30, mana=0, town_id=ANKRAHMUN_TOWN)
    assert (row["posx"], row["posy"], row["posz"]) == ANKRAHMUN_TEMPLE, (row["posx"], row["posy"], row["posz"])
    assert (row["health"], row["mana"]) == (row["healthmax"], row["manamax"]), \
        {k: row[k] for k in ("health", "healthmax", "mana", "manamax")}
    con = db._connect()
    account, name = con.execute("SELECT account_id, name FROM players WHERE id = ?", (guid,)).fetchone()
    con.close()
    again = GameClient(items, port=server.port).login(account, "test", name)
    try:
        assert again.wait_for(lambda: again.pos == ANKRAHMUN_TEMPLE, timeout=5), f"logged in at {again.pos}"
    finally:
        again.logout()


# ----------------------------------------------------------------------------- what a death takes: exp, ML, skills
#
# 7.4 (docs/reference-74/death.md §1-2; TibiaWiki Death 2005-05, oldid 6509/19247/23124; Blessings 2005-05, oldid
# 19249): 10% of the experience and of all skills, 7% for a promoted character (with premium), each blessing one
# point less. The loss is a share of everything gained (all the tries / mana spent since level 10 / ML 0), not of
# the current level's progress, so a death can take skill and magic levels away. The level-scaled formula is 8.41.

SWORD = 2


def _skill(db, guid, skill):
    con = db._connect()
    try:
        return tuple(con.execute("SELECT value, count FROM player_skills WHERE player_id = ? AND skillid = ?",
                                 (guid, skill)).fetchone())
    finally:
        con.close()


def _knight_sword_tries(level):
    """Tries from sword level-1 to level for a knight (50 x 1.1^(level-11), vocations.xml)."""
    return int(50 * 1.1 ** (level - 11))


def _sorcerer_mana(ml):
    """Mana spent from magic level ml-1 to ml for a sorcerer (1600 x 1.1^(ml-1), vocations.xml)."""
    return int(1600 * 1.1 ** (ml - 1))


def _after_loss(requirement, first, level, progress, percent):
    """(level, progress) left after losing percent of everything gained from level `first` (a skill starts at 10,
    the magic level at 0). The rounding of the loss is not in any source: ours rounds it up, either is accepted."""
    total = sum(requirement(n) for n in range(first + 1, level + 1)) + progress
    results = set()
    for lost in (total * percent // 100, -(-total * percent // 100)):
        left, lvl = total - lost, first
        while left >= requirement(lvl + 1):
            left -= requirement(lvl + 1)
            lvl += 1
        results.add((lvl, left))
    return results


@pytest.mark.parametrize("vocation, percent, line", [(KNIGHT, 10, 14), (ELITE_KNIGHT, 7, 16)])
def test_death_takes_10_percent_of_all_skill_tries_7_promoted(new_player, db, vocation, percent, line):
    """Sword 20 with no tries towards 21: 793 tries in all, 10% (80) is more than the level's progress, so the
    knight is back at sword 19 with 117 - 80 = 37 tries; promoted 7% (56) leaves 61. Level 50 so the 10% / 7% of
    experience is a few levels, nothing more."""
    guid, row = _kill_on(new_player, db, line, vocation=vocation, level=50, premium_days=30,
                          skills={SWORD: 20}, skill_tries={SWORD: 0})
    assert row["experience"] == 1847300 - 1847300 * percent // 100, row["experience"]
    assert row["vocation"] == vocation, f"the promotion was lost on death: vocation {row['vocation']}"
    expected = _after_loss(_knight_sword_tries, 10, 20, 0, percent)
    assert _skill(db, guid, SWORD) in expected, f"sword {_skill(db, guid, SWORD)}, expected one of {expected}"


@pytest.mark.parametrize("vocation, percent, line", [(SORCERER, 10, 18), (MASTER_SORCERER, 7, 20)])
def test_death_takes_10_percent_of_all_mana_spent_7_promoted(new_player, db, vocation, percent, line):
    """Magic level 10 with no mana towards 11: 25,495 mana spent in all; 10% (2,550) costs the magic level -
    back at 9 with 3,772 - 2,550 = 1,222 spent towards 10. Promoted: 7% (1,785) leaves 1,987."""
    guid, row = _kill_on(new_player, db, line, vocation=vocation, level=50, premium_days=30,
                          maglevel=10, manaspent=0)
    assert row["experience"] == 1847300 - 1847300 * percent // 100, row["experience"]
    expected = _after_loss(_sorcerer_mana, 0, 10, 0, percent)
    got = (row["maglevel"], row["manaspent"])
    assert got in expected, f"magic level {got}, expected one of {expected}"


def test_death_keeps_progress_when_the_loss_is_smaller(new_player, db):
    """Sword 20 and 100 tries towards 21: 893 in all, 10% is 89.3 - still sword 20 with 10 or 11 tries."""
    guid, _ = _kill_on(new_player, db, 22, level=50, skills={SWORD: 20}, skill_tries={SWORD: 100})
    expected = _after_loss(_knight_sword_tries, 10, 20, 100, 10)
    assert _skill(db, guid, SWORD) in expected, f"sword {_skill(db, guid, SWORD)}, expected one of {expected}"


def test_a_suspended_promotion_loses_10_percent_and_stays_promoted(new_player, db):
    """An elite knight without premium plays as a knight (the promotion is suspended), so he loses the full 10% -
    and the promotion is still saved after the death, back with premium."""
    guid, row = _kill_on(new_player, db, 24, vocation=ELITE_KNIGHT, level=50, premium_days=0)
    assert row["experience"] == 1847300 - 184730, f"lost {(1847300 - row['experience']) / 1847300:.2%}, expected 10%"
    assert row["vocation"] == ELITE_KNIGHT, f"the promotion was lost on death: vocation {row['vocation']}"

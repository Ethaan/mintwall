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
        victim = new_player(pos=(ROAD[0], ROAD[1] + 1, ROAD[2]), storage={30001: 1})
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
    p = _buyer(new_player, "Norf", group_id=1, health=100)                    # testers cannot be attacked
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

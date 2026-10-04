"""A new player's first days on Rookgaard, played like a player: out of the temple, down the sewer grate to the rats,
loot and sell, buy a weapon at Obi's, die once, and reach level 8 to see the Oracle.

The walking is real (tibia74/route.py: planned on the map, the grate and the ladder used like a player does), the
monsters are the map's own spawns, and the prices are the NPCs' own (test_npcs_rookgaard.py checks every one of
them; docs/reference-74/npc-shops.md). test_rookgaard.py has the single rules (beginner set, first kill, the Oracle's
choices, Tom); test_map_mechanics.py every ladder and grate; test_death.py the death rules of the mainland.
"""
import time

from tibia74 import BACKPACK, Item, RIGHT
from tibia74.db import VOCATION_GAINS, capacity, exp_for_level
from tibia74.quest import npc_pos, open_map_container, pick_up, take, talk_to, use_map_item
from tibia74.route import follow, walk_near, walk_next_to
from tibia74.server import TESTER_GROUP

ROOKGAARD_TEMPLE = (32097, 32219, 7)
SEWER_GRATE = (32097, 32205, 7)              # beside the temple (test_map_mechanics.py)
SEWER_LADDER = (32097, 32205, 8)             # right under it: the way back up
GRATE, LADDER = 430, 1386
DEAD_RAT = 2813                              # the corpse a rat leaves (rat.xml), what Seymour and Tom buy
GOLD = 2148
DAGGER, DAGGER_PRICE = 2379, 5               # Obi (rook_items.lua; npc-shops.md: no difference to TibiaWiki)
RAT_PRICE = 2                                # Seymour, Tom: a fresh dead rat
ROOK_FIELD = (32082, 32210, 7)               # open grass west of the village, not a protection zone
MALE_CORPSE = 3058                           # ITEM_MALE_CORPSE (const.h)
NONE = 0                                     # no vocation


def _gold(p):
    return sum(i.count for i in p.all_items() if i.name == "gold coin")


def _rats(p):
    return sum(1 for i in p.all_items() if i.name == "dead rat")


def _in_sewer(world):
    """A tile among the sewer rats below the temple."""
    return world.nearest_spawn("Rat", (ROOKGAARD_TEMPLE[0], ROOKGAARD_TEMPLE[1], 8))


# The room under the grate is cut off from the rats by water: a switch on each side lowers a drawbridge
# (test_rookgaard.py::test_sewer_switch_lowers_the_bridge_and_raises_it_again). Without it the only way into this
# sewer is the long way round from the west (stairs at 32046,32221).
WEST_SWITCH, EAST_SWITCH = (32098, 32204, 8), (32104, 32204, 8)
BRIDGE = [(32100, 32205, 8), (32101, 32205, 8)]
DRAWBRIDGE = 1284                            # client id of the lowered bridge
EAST_OF_BRIDGE = (32103, 32205, 8)


def _bridge_down(p):
    return all(p.tile_items(b) and p.tile_items(b)[0].client_id == DRAWBRIDGE for b in BRIDGE)


def _lower_the_bridge(p, switch):
    assert p.wait_for(lambda: p.tile_items(switch), timeout=5), f"switch {switch} not in view from {p.pos}"
    if not _bridge_down(p):
        top = p.tile_items(switch)[-1]
        p.use_item(switch, top.client_id, len(p.tile_items(switch)) - 1)
        assert p.wait_for(lambda: _bridge_down(p), timeout=5), \
            f"the switch at {switch} did not lower the bridge: {[p.tile_items(b) for b in BRIDGE]}"


def _down_to_the_rats(p, items, world_map):
    """Temple -> the grate -> the switch lowers the bridge -> across it, among the rats."""
    walk_next_to(p, items, world_map, SEWER_GRATE)
    use_map_item(p, items, SEWER_GRATE, GRATE)
    assert p.wait_for(lambda: p.pos == SEWER_LADDER, timeout=3), f"used the grate: at {p.pos}, not {SEWER_LADDER}"
    _lower_the_bridge(p, WEST_SWITCH)
    follow(p, items, world_map, EAST_OF_BRIDGE, open_tiles=BRIDGE)


def _up_to_the_temple(p, items, world_map):
    """Back over the bridge (lowered again from this side if it was raised) and up the ladder."""
    follow(p, items, world_map, EAST_OF_BRIDGE, open_tiles=BRIDGE)
    _lower_the_bridge(p, EAST_SWITCH)
    follow(p, items, world_map, ROOKGAARD_TEMPLE, open_tiles=BRIDGE)


def _corpse_near(p, items, server_id, radius=2):
    """The closest tile around the character with this corpse on it."""
    x, y, z = p.pos
    found = [(max(abs(dx), abs(dy)), (x + dx, y + dy, z))
             for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1)
             if any(items.by_client[i.client_id].server_id == server_id for i in p.tile_items((x + dx, y + dy, z)))]
    return min(found)[1] if found else None


def _close_rat(p, radius=5):
    """The nearest rat on our floor within radius (the sewer has rats behind walls and water too)."""
    rats = [r for r in p.creatures_named("Rat") if p.pos and r.pos[2] == p.pos[2]
            and max(abs(r.pos[0] - p.pos[0]), abs(r.pos[1] - p.pos[1])) <= radius]
    return min(rats, key=lambda r: max(abs(r.pos[0] - p.pos[0]), abs(r.pos[1] - p.pos[1])), default=None)


def _kill_a_rat(p, tries=5):
    """Attack the nearest close rat and chase it (rats run at 5 hp) until it dies; one we cannot get at in 40 s
    (behind water) is given up for the next. Returns the experience the kill gave."""
    p.set_fight_modes(fight=1, chase=1)
    for _ in range(tries):
        rat = p.wait_for(lambda: _close_rat(p), timeout=60)
        assert rat, f"no rat near {p.pos}"
        exp = p.stats.experience
        p.attack(rat.id)
        if p.wait_for(lambda: p.stats.experience > exp, timeout=40):
            p.attack(0)
            return p.stats.experience - exp
        p.attack(0)
    raise AssertionError(f"no rat killed in {tries} tries at {p.pos}, {p.stats.health} hp")


def _saved(p, db):
    """Log out and wait for the save; the saved row."""
    guid = p.character.guid
    p.logout()
    deadline = time.time() + 5
    while time.time() < deadline and not db.character(guid)["lastlogout"]:
        time.sleep(0.2)
    return db.character(guid)


# ----------------------------------------------------------------------------- hunt, sell, buy

def test_a_new_player_hunts_sewer_rats_sells_them_and_buys_a_dagger(new_player, items, world, world_map, db):
    """Fresh from the temple with the beginner set (club, jacket, bag): down the grate to the rats, kill them, take
    their gold and carry the corpses (2 gp each at Seymour) until there is enough for Obi's dagger (5 gp), up the
    ladder, sell, buy."""
    p = new_player()
    assert p.stats.level == 1 and p.pos[2] == 7, (p.stats.level, p.pos)
    assert p.wait_for(lambda: p.slot_of("bag"), timeout=5), f"no beginner bag: {p.inventory_names()}"
    bag = p.open_container(p.slot_of("bag"))
    assert bag, "the bag did not open"
    assert _gold(p) == 0, "a new player starts without money"

    _down_to_the_rats(p, items, world_map)
    walk_near(p, items, world_map, _in_sewer(world), open_tiles=BRIDGE)

    killed = 0
    while _gold(p) + RAT_PRICE * _rats(p) < DAGGER_PRICE:
        assert killed < 6, f"6 rats and still only {_gold(p)} gp and {_rats(p)} corpses"
        assert _kill_a_rat(p) == 5, "a rat gives 5 experience"
        killed += 1
        corpse = p.wait_for(lambda: _corpse_near(p, items, DEAD_RAT), timeout=3)
        assert corpse, f"no dead rat around {p.pos}"
        if max(abs(corpse[0] - p.pos[0]), abs(corpse[1] - p.pos[1])) > 1:
            walk_next_to(p, items, world_map, corpse)
        loot = open_map_container(p, items, corpse, DEAD_RAT)
        if any(i.name == "gold coin" for i in loot.items):
            take(p, items, loot, "gold coin")
        pick_up(p, items, corpse, "dead rat")
    gold, rats = _gold(p), _rats(p)

    _up_to_the_temple(p, items, world_map)
    seymour = npc_pos("Seymour")
    walk_near(p, items, world_map, seymour)
    assert p.pos[2] == seymour[2], f"not back up from the sewer: {p.pos}"
    replies = talk_to(p, "Seymour", "hi", *["sell dead rat", "yes"] * rats)
    assert p.wait_for(lambda: _rats(p) == 0, timeout=5), f"Seymour did not take the rats: {replies}"
    assert p.wait_for(lambda: _gold(p) == gold + RAT_PRICE * rats, timeout=5), \
        f"{rats} rats sold for {_gold(p) - gold} gp, not {RAT_PRICE * rats}: {replies}"

    money = _gold(p)
    walk_near(p, items, world_map, npc_pos("Obi"))
    replies = talk_to(p, "Obi", "hi", "buy dagger", "yes")
    assert p.wait_for(lambda: any(i.name == "dagger" for i in p.all_items()), timeout=5), \
        f"no dagger bought with {money} gp: {replies}"
    assert _gold(p) == money - DAGGER_PRICE, f"the dagger cost {money - _gold(p)} gp, not {DAGGER_PRICE}"

    guid = p.character.guid
    _saved(p, db)
    saved = db.items(guid)
    assert any(r["itemtype"] == DAGGER for r in saved), "the dagger was not saved"
    assert sum(r["count"] for r in saved if r["itemtype"] == GOLD) == money - DAGGER_PRICE


# ----------------------------------------------------------------------------- sewers

def test_down_the_sewer_grate_and_up_the_ladder(new_player, items, world_map):
    """Out of the temple to the grate, use it (one floor down, onto the ladder below), then the ladder from where
    one lands - the way every Rookgaard player first goes to the rats and back."""
    p = new_player(storage={30001: 1})
    walk_next_to(p, items, world_map, SEWER_GRATE)
    use_map_item(p, items, SEWER_GRATE, GRATE)
    assert p.wait_for(lambda: p.pos == SEWER_LADDER, timeout=3), f"used the grate: at {p.pos}, not {SEWER_LADDER}"
    use_map_item(p, items, SEWER_LADDER, LADDER)
    up = (SEWER_LADDER[0], SEWER_LADDER[1] + 1, SEWER_LADDER[2] - 1)
    assert p.wait_for(lambda: p.pos == up, timeout=3), f"used the ladder: at {p.pos}, not {up}"
    follow(p, items, world_map, ROOKGAARD_TEMPLE)          # and back to the temple, all on foot


def test_the_rats_below_the_grate_are_across_the_drawbridge(world, world_map):
    """On the map the room under the grate has no way to the rats but the drawbridge (the planner's own way in is
    the long one from the west); with the bridge lowered they are a short walk away."""
    from tibia74.quest import assert_way
    rats = _in_sewer(world)
    across = assert_way(world_map, SEWER_LADDER, rats, open_tiles=BRIDGE)
    without = assert_way(world_map, SEWER_LADDER, rats)
    assert any(s.arrive[2] != 8 for s in without), "a way to the rats without the bridge, staying in this sewer"
    assert len(across) < 50 and len(without) > 2 * len(across), (len(across), len(without))


def test_down_to_the_rats_over_the_drawbridge_and_back_up(new_player, items, world, world_map):
    """The way every Rookgaard player first goes to the rats and back: grate, west switch, bridge, rats - then back
    over the bridge (the east switch if someone raised it) and up the ladder to the temple."""
    p = new_player(storage={30001: 1}, group_id=TESTER_GROUP)     # rats leave testers alone: just the walk
    _down_to_the_rats(p, items, world_map)
    walk_near(p, items, world_map, _in_sewer(world), open_tiles=BRIDGE)
    assert p.pos[2] == 8, p.pos
    _up_to_the_temple(p, items, world_map)
    assert p.pos == ROOKGAARD_TEMPLE, p.pos


# ----------------------------------------------------------------------------- death

def test_death_in_rookgaard_costs_10_percent_and_the_bag_back_in_the_temple(new_player, items, server, db):
    """A level 6 rookgaarder (no vocation) killed by a wolf on the grass west of the village:
    - 10% of the experience (1600 -> 1440: level 5), with level 6's 5 hp, 5 mana and 10 cap (vocations.xml, 0)
    - no vocation, so he is not "rooked" (that is for a mainland character falling to level 5, player.cpp): he
      stays level 5, not 1, and keeps his skills' vocation
    - the bag always drops with what is in it, each other item at 10% (test_death.py)
    - back in the Rookgaard temple (town 1) with full health and mana."""
    exp = 1600
    victim = new_player(pos=ROOK_FIELD, level=6, experience=exp, health=20, mana=0, storage={30001: 1},
                        inventory={RIGHT: Item(2382),                                     # club
                                   BACKPACK: Item(1987, contents=[Item(GOLD, 7), Item(2050)])})   # bag: gold, torch
    guid = victim.character.guid
    assert victim.pos == ROOK_FIELD, victim.pos
    gm = new_player(pos=(ROOK_FIELD[0], ROOK_FIELD[1] - 3, ROOK_FIELD[2]), group_id=3)
    gm.say("/m Wolf")
    assert victim.wait_for(lambda: not victim.connected or victim.stats.health == 0, timeout=90), \
        f"the wolf did not kill him: {victim.stats.health} hp, {victim.pos}"
    deadline = time.time() + 5
    while time.time() < deadline and db.character(guid)["experience"] == exp:
        time.sleep(0.2)

    row = db.character(guid)
    lost = exp * 10 // 100
    assert row["experience"] == exp - lost, f"lost {exp - row['experience']} of {exp}, expected {lost} (10%)"
    assert (row["level"], row["vocation"]) == (5, NONE), (row["level"], row["vocation"])
    hp, mana, _ = VOCATION_GAINS[NONE]
    assert (row["healthmax"], row["manamax"], row["cap"]) == (150 + 4 * hp, 4 * mana, capacity(NONE, 5)), \
        {k: row[k] for k in ("healthmax", "manamax", "cap")}
    assert (row["health"], row["mana"]) == (row["healthmax"], row["manamax"]), "not back at full health"
    assert (row["posx"], row["posy"], row["posz"]) == ROOKGAARD_TEMPLE and row["town_id"] == 1, \
        (row["posx"], row["posy"], row["posz"], row["town_id"])
    kept = db.items(guid)
    assert not any(r["itemtype"] in (1987, GOLD, 2050) for r in kept), \
        f"the bag (always lost) or its contents were kept: {[(r['pid'], r['itemtype']) for r in kept]}"

    # the bag lies in his corpse where he died, and he logs in again in the temple
    corpse = gm.wait_for(lambda: next((pos for pos in gm.tiles if pos[2] == 7 and any(
        items.by_client[i.client_id].server_id == MALE_CORPSE for i in gm.tile_items(pos))), None), timeout=3)
    assert corpse, "no corpse where he died"
    gm.walk_to(corpse)
    inside = open_map_container(gm, items, corpse, MALE_CORPSE)
    assert any(i.name == "bag" for i in inside.items), f"the bag is not in the corpse: {inside.items}"

    from tibia74 import GameClient
    again = GameClient(items, port=server.port).login(victim.character.account, victim.character.password,
                                                      victim.character.name)
    try:
        assert again.wait_for(lambda: again.pos, timeout=5)
        assert max(abs(again.pos[0] - ROOKGAARD_TEMPLE[0]), abs(again.pos[1] - ROOKGAARD_TEMPLE[1])) <= 1 \
            and again.pos[2] == 7, f"logged in at {again.pos}, not in the temple"
        assert again.wait_for(lambda: again.stats.health == again.stats.max_health == 170, timeout=3), again.stats
    finally:
        again.logout()


# ----------------------------------------------------------------------------- level 8, the Oracle

def test_a_rat_takes_a_rookgaarder_to_level_8_and_he_walks_to_the_oracle(new_player, items, world, world_map):
    """Level 7, 3 experience short of level 8 (4200): from the temple down to the rats, one rat (5 exp), level 8 -
    "You advanced from Level 7 to Level 8." and level 8's gains for no vocation: 5 hp, 5 mana, 10 cap (185 hp,
    35 mana, 470 cap). Then on foot to the Oracle, who now talks to him (the choice itself:
    test_rookgaard.py::test_oracle_turns_a_level_8_into_a_knight_of_thais)."""
    p = new_player(level=7, experience=exp_for_level(8) - 3, storage={30001: 1}, skills={1: 25},
                   inventory={RIGHT: Item(2382), BACKPACK: Item(1987)})                   # club, bag
    hp, mana, _ = VOCATION_GAINS[NONE]
    assert p.wait_for(lambda: p.stats.max_health == 150 + 6 * hp, timeout=5), p.stats
    assert (p.stats.max_mana, p.stats.capacity) == (6 * mana, capacity(NONE, 7)), p.stats

    _down_to_the_rats(p, items, world_map)
    walk_near(p, items, world_map, _in_sewer(world), open_tiles=BRIDGE)
    _kill_a_rat(p)
    assert p.wait_for(lambda: p.stats.level == 8, timeout=3), f"level {p.stats.level}, exp {p.stats.experience}"
    assert p.messages("You advanced from Level 7 to Level 8"), p.text_messages[-3:]
    assert p.stats.experience == exp_for_level(8) + 2, p.stats.experience
    assert (p.stats.max_health, p.stats.max_mana, p.stats.capacity) == (185, 35, 470) == \
        (150 + 7 * hp, 7 * mana, capacity(NONE, 8)), p.stats

    _up_to_the_temple(p, items, world_map)
    oracle = npc_pos("The Oracle")
    walk_near(p, items, world_map, oracle)
    replies = talk_to(p, "The Oracle", "hi")
    assert replies and not any("COME BACK WHEN YOU HAVE GROWN UP" in r for r in replies), replies
    assert any("PREPARED" in r.upper() or "DESTINY" in r.upper() for r in replies), replies

"""The Desert Dungeon Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: four players, one of each vocation, level 20 or more (the gate), each with his sacrifice on the basin
# behind his switch (sorcerer a spellbook, druid an apple, paladin a crossbow, knight a sword) and standing on it; the
# paladin's lever teleports the four into the reward room: 100 platinum coins and a green bag (protection amulet, ring
# of healing, magic lightwand, ankh). Our map had nothing scripted and a forcefield in the middle of the room that took
# anyone into the reward room (removed; decided with the user).
SWITCHES = {   # vocation: (switch, where to start - the room side of it, basin, sacrifice)
    1: ((32677, 32089, 8), (32676, 32089, 8), (32679, 32089, 8), 2175),
    2: ((32669, 32089, 8), (32670, 32089, 8), (32667, 32089, 8), 2674),
    3: ((32673, 32085, 8), (32672, 32086, 8), (32673, 32083, 8), 2455),
    4: ((32673, 32093, 8), (32673, 32092, 8), (32673, 32094, 8), 2376),
}


def _press(p, items, switch, basin, sacrifice):
    """Onto the switch, the sacrifice on the basin behind it, off and on again: the switch goes down (it checks the
    basin when stepped on)."""
    start = p.pos
    step_onto(p, switch)
    drop_on(p, items, sacrifice, basin)
    step_onto(p, start)
    step_onto(p, switch)
LEVER, GATE, OUTSIDE_GATE = (32673, 32086, 8), (32673, 32100, 8), (32673, 32101, 8)
REWARD_ROOM = [(32671, 32069, 8), (32672, 32069, 8), (32671, 32070, 8), (32672, 32070, 8)]
CHESTS = [((32668, 32069, 8), ["100 platinum coins"]), ((32675, 32069, 8), ["a green bag"])]


def _four(new_player):
    from tibia74 import BACKPACK, Item
    players = {}
    for vocation, (switch, stand, basin, sacrifice) in SWITCHES.items():
        p = new_player(pos=stand, level=20, vocation=vocation, group_id=TESTER_GROUP, storage={30001: 1},
                       inventory={BACKPACK: Item(1988, contents=[Item(sacrifice)])})
        assert p.pos == stand, (vocation, p.pos)
        p.open_container(BACKPACK)
        players[vocation] = p
    return players


def test_desert_dungeon_quest(new_player, items, world_map):
    players = _four(new_player)
    for vocation, p in players.items():
        switch, _, basin, sacrifice = SWITCHES[vocation]
        _press(p, items, switch, basin, sacrifice)
        assert p.wait_for(lambda: any(getattr(t, "client_id", None) == items.by_server[425].client_id
                                      for t in p.tiles.get(switch, [])), timeout=3), ("switch not down", vocation)
    use_map_item(players[3], items, LEVER, "switch")
    for p in players.values():
        assert p.wait_for(lambda: p.pos in REWARD_ROOM, timeout=3), p.pos
    for vocation in SWITCHES:                                   # the sacrifices are gone
        _, _, basin, sacrifice = SWITCHES[vocation]
        assert not any(getattr(t, "client_id", None) == items.by_server[sacrifice].client_id
                       for t in players[3].tiles.get(basin, [])), basin
    knight = players[4]
    for vocation in (1, 2, 3):                                   # the room is small: the others leave first
        players[vocation].logout()
    for chest, found in CHESTS:
        collect(knight, items, world_map, chest, "chest", found, level=20)
    inside = bag_contents(knight, items)
    for name in ("protection amulet", "ring of healing", "magic lightwand", "ankh"):
        assert name in inside or carries(knight, name), (name, inside)


def test_desert_dungeon_wants_the_right_vocations(new_player, items):
    """A switch goes down only for its vocation with its sacrifice; the lever wants all four."""
    from tibia74 import BACKPACK, Item
    switch, stand, basin, _ = SWITCHES[1]
    knight = new_player(pos=stand, level=20, vocation=4, group_id=TESTER_GROUP, storage={30001: 1},
                        inventory={BACKPACK: Item(1988, contents=[Item(2175)])})
    knight.open_container(BACKPACK)
    _press(knight, items, switch, basin, 2175)
    knight.sleep(1)
    assert not any(getattr(t, "client_id", None) == items.by_server[425].client_id
                   for t in knight.tiles.get(switch, [])), "a knight pressed the sorcerer's switch"
    paladin = new_player(pos=SWITCHES[3][1], level=20, vocation=3, group_id=TESTER_GROUP, storage={30001: 1})
    before = len(paladin.text_messages)
    use_map_item(paladin, items, LEVER, "switch")
    assert paladin.wait_for(lambda: any("not possible" in t for _, t in paladin.text_messages[before:]), timeout=3)
    assert paladin.pos == SWITCHES[3][1]


def test_desert_dungeon_level_door(new_player, items):
    assert_level_door(new_player, items, GATE, OUTSIDE_GATE, 20)


def test_desert_dungeon_no_way_around_the_lever(world_map):
    """The middle forcefield is gone: the reward room is reached only through the lever."""
    assert_no_way(world_map, THAIS_TEMPLE, (32669, 32069, 8), level=100, rope=True, shovel=True, floors=9)

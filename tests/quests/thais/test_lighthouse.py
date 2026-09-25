"""Thais Lighthouse Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Thais Lighthouse Quest
# docs/reference-74/quests.md "Thais Lighthouse Quest"; TibiaWiki (2006): in the basement "a switch under some
# crates which will open a ladder down"; below, "a step switch that once a person stands on it will open stairs at
# the south end. The other person must go down the stairs and turn a lever. The lever turns on a teleporter in the
# right passage which leads to the quest room"; the chests (dark shield, battle hammer) are at its north end.
# No level, free, 2 players. The lever also makes the way out (the room has no other exit; turning it off traps
# whoever is inside, as the 2006 page warns). quests/thais_lighthouse.lua, movements thais_lighthouse_step.lua.

LIGHTHOUSE = dict(crate_switch=(32227, 32278, 8), trapdoor=(32225, 32276, 8), step_switch=(32225, 32268, 9),
                  stairs=(32225, 32282, 9), lever=(32225, 32285, 10), portal_in=(32233, 32276, 9),
                  room=(32225, 32271, 10), portal_out=(32225, 32276, 10), east_passage=(32232, 32276, 9),
                  chests={(32225, 32265, 10): "battle hammer", (32226, 32265, 10): "dark shield"})
TRAPDOOR, STAIRS_DOWN, FIELD = 369, 410, 1387


def test_thais_lighthouse_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    L = LIGHTHOUSE
    ability = dict(level=2000, vocation=4, rope=True)
    has = lambda p, pos, sid: any(i.client_id == sid for i in p.tile_items(pos))   # noqa: E731
    def player():
        p = strong(new_player, THAIS_TEMPLE)
        p.open_container(BACKPACK)
        p.set_fight_modes(fight=1, chase=0, safe=1)
        return p
    a = player()

    # the switch under the crates opens the trapdoor down to the ladder
    walk_next_to(a, items, world_map, L["crate_switch"], **ability)
    use_map_item(a, items, L["crate_switch"], "switch")             # the crates are moved off it first
    assert a.wait_for(lambda: has(a, L["trapdoor"], TRAPDOOR), timeout=3), (a.tiles.get(L["trapdoor"]),
                                                                           a.text_messages[-2:])
    b = player()                           # the second player, from the temple the first one has left
    for p in (a, b):
        walk_next_to(p, items, world_map, L["trapdoor"], **ability)
        step_onto(p, L["trapdoor"])
        assert p.wait_for(lambda: p.pos[2] == 9, timeout=3), p.pos

    # one stands on the step switch: the stairs at the south end open
    follow(a, items, world_map, L["step_switch"], **ability)
    assert b.wait_for(lambda: has(b, L["stairs"], STAIRS_DOWN), timeout=3), b.tiles.get(L["stairs"])
    walk_next_to(b, items, world_map, L["stairs"], **ability)
    step_onto(b, L["stairs"])
    assert b.wait_for(lambda: b.pos[2] == 10, timeout=3), b.pos

    # the other pulls the lever: the portal in the east passage (and the way out of the room) appear
    walk_next_to(b, items, world_map, L["lever"], **ability)
    use_map_item(b, items, L["lever"], "switch")

    # off the step switch the stairs close again; the portal is there (out of view from the switch)
    follow(a, items, world_map, L["east_passage"], **ability)
    assert a.wait_for(lambda: not has(a, L["stairs"], STAIRS_DOWN), timeout=3), a.tiles.get(L["stairs"])
    assert a.wait_for(lambda: has(a, L["portal_in"], FIELD), timeout=3), (a.tiles.get(L["portal_in"]),
                                                                         b.text_messages[-2:])
    step_onto(a, L["portal_in"])
    assert a.wait_for(lambda: a.pos == L["room"], timeout=3), a.pos

    for chest, reward in L["chests"].items():
        walk_next_to(a, items, world_map, chest, **ability)
        use_map_item(a, items, chest, "chest")
        assert a.wait_for(lambda: a.messages(f"You have found a {reward}."), timeout=3), a.text_messages[-3:]
        assert a.wait_for(lambda: carries(a, reward), timeout=3), a.inventory_names()
        a.sleep(1.1)
    use_map_item(a, items, next(iter(L["chests"])), "chest")
    assert a.wait_for(lambda: a.messages("The chest is empty."), timeout=3), a.text_messages[-2:]

    # out through the room's field, then the lever turns both fields off
    walk_next_to(a, items, world_map, L["portal_out"], **ability)
    step_onto(a, L["portal_out"])
    assert a.wait_for(lambda: a.pos == L["east_passage"], timeout=3), a.pos
    use_map_item(b, items, L["lever"], "switch")
    assert a.wait_for(lambda: not has(a, L["portal_in"], FIELD), timeout=3), a.tiles.get(L["portal_in"])


def test_lighthouse_rules(world_map):
    L = LIGHTHOUSE
    # the basement is open to anyone; the cyclops room is not, until the lever makes the portal - and it has no
    # way out of its own (the lever's second portal is the way out)
    assert_way(world_map, THAIS_TEMPLE, L["crate_switch"], level=1)
    assert_no_way(world_map, THAIS_TEMPLE, L["room"], level=2000, vocation=4, rope=True)
    assert_no_way(world_map, L["room"], THAIS_TEMPLE, level=2000, vocation=4, rope=True)

"""Triangle Tower Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (2005/2006): "If the tower is closed, pull the lever in the desert", climb past skeletons, ghouls, demon
# skeletons, stalkers to the top floor, open the box. Real-map table [4510]: garlic necklace, dwarven ring, 2 small
# sapphires - in the chest on our top floor (32565,32119,3). The lever had no script (quests/triangle_tower_lever.lua,
# the wall as tibiaot74). Free, no level, once.
TRIANGLE = dict(lever=(32573, 32121, 7), wall=(32566, 32119, 7), chest=(32565, 32119, 3), beside=(32564, 32119, 3))
BRICK_WALL = 1025


def test_triangle_tower_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    T = TRIANGLE
    p = strong(new_player, THAIS_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    wall = lambda: any(i.client_id == BRICK_WALL for i in p.tile_items(T["wall"]))   # noqa: E731
    walk_next_to(p, items, world_map, T["lever"], **ability)
    assert p.wait_for(wall, timeout=3), p.tiles.get(T["wall"])                             # closed
    use_map_item(p, items, T["lever"], "switch")
    assert p.wait_for(lambda: not wall(), timeout=3), (p.tiles.get(T["wall"]), p.text_messages[-2:])

    open_tower = dict(open_tiles={T["wall"]}, **ability)
    walk_next_to(p, items, world_map, T["chest"], **open_tower)
    before = len(p.text_messages)
    use_map_item(p, items, T["chest"], "chest")
    found = lambda: sorted(t for _, t in p.text_messages[before:] if t.startswith("You have found"))  # noqa: E731
    assert p.wait_for(lambda: found() == ["You have found 2 small sapphires.", "You have found a dwarven ring.",
                                          "You have found a garlic necklace."], timeout=3), found()
    p.sleep(1.1)
    use_map_item(p, items, T["chest"], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

    # out, and the lever closes the tower again
    walk_next_to(p, items, world_map, T["lever"], **open_tower)
    use_map_item(p, items, T["lever"], "switch")
    assert p.wait_for(wall, timeout=3), p.tiles.get(T["wall"])


def test_triangle_tower_rules(world_map):
    ability = dict(level=1, vocation=4, rope=True)
    assert_no_way(world_map, THAIS_TEMPLE, TRIANGLE["beside"], **ability)                      # the wall
    assert_way(world_map, THAIS_TEMPLE, TRIANGLE["beside"], open_tiles={TRIANGLE["wall"]}, **ability)
    assert_way(world_map, THAIS_TEMPLE, (32573, 32122, 7), **ability)                          # the lever

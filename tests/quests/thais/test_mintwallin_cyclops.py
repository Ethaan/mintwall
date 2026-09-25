"""Mintwallin Cyclops Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (2006): "Enter the NW corner and follow the passage to the switch. Pulling it moves the wall and traps you
# with the Cyclopes"; the reward behind it; out by the north hole. Current wiki: if the wall is already moved, "use
# Key 3667" (from a dead body under rubbish behind the Mad Mage room). Real-map table: [3667] key 3667, [3610] key
# 3610 (to the secret laboratory, Devil Helmet Quest), [3611] a small diamond next to it. The switch moves the wall
# both ways (decided with the user); quests/mintwallin_cyclops_wall.lua.
CYCLOPS = dict(switch=(32602, 32104, 14), at_switch=(32601, 32104, 14), north_walls=[(32593, 32103, 14), (32594, 32103, 14)],
               west_walls=[(32592, 32104, 14), (32592, 32105, 14)], door=(32592, 32102, 14),
               key_chest=(32589, 32097, 14), diamond_chest=(32590, 32097, 14), beside=(32589, 32098, 14),
               key_body=(32576, 32216, 15))
NORTH_WALL, WEST_WALL = 1026, 1025


def test_mintwallin_cyclops_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    C = CYCLOPS
    p = strong(new_player, THAIS_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    wall = lambda pos, wid: any(i.client_id == wid for i in p.tile_items(pos))   # noqa: E731

    # the switch: the wall to the reward opens, the way back closes (from its west side the walls are in view)
    follow(p, items, world_map, C["at_switch"], **ability)
    assert all(wall(w, NORTH_WALL) for w in C["north_walls"]), [p.tiles.get(w) for w in C["north_walls"]]
    use_map_item(p, items, C["switch"], "switch")
    assert p.wait_for(lambda: not any(wall(w, NORTH_WALL) for w in C["north_walls"]), timeout=3), \
        [p.tiles.get(w) for w in C["north_walls"]]

    # key 3610 and the diamond; from there the way back is in view: shut (the new walls are 9 tiles from the switch)
    moved = set(C["north_walls"])
    for chest, found in ((C["key_chest"], "a silver key"), (C["diamond_chest"], "a small diamond")):
        walk_next_to(p, items, world_map, chest, open_tiles=moved, **ability)
        assert p.wait_for(lambda: all(wall(w, WEST_WALL) for w in C["west_walls"]), timeout=3), \
            [p.tiles.get(w) for w in C["west_walls"]]
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    use_map_item(p, items, C["diamond_chest"], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

    # the switch again: the wall moves back (both ways); out by the north hole
    follow(p, items, world_map, C["at_switch"], open_tiles=moved, **ability)
    use_map_item(p, items, C["switch"], "switch")
    assert p.wait_for(lambda: all(wall(w, NORTH_WALL) for w in C["north_walls"]), timeout=3)
    follow(p, items, world_map, THAIS_TEMPLE, **ability)          # west, where the wall is gone again


def test_mintwallin_cyclops_key_3667(new_player, items, world_map):
    """Key 3667 lies in a dead body under rubbish behind the Mad Mage room; it opens the door to the reward."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    keys = [Item(2088, attributes=bytes([4]) + k.to_bytes(2, "little")) for k in (3620, 3666)]
    p = strong(new_player, THAIS_TEMPLE, items=keys, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    walk_next_to(p, items, world_map, CYCLOPS["key_body"], keys={3620, 3666}, **ability)
    use_map_item(p, items, CYCLOPS["key_body"], QUEST_BODY)          # the rubbish is moved off it first
    assert p.wait_for(lambda: p.messages("You have found a silver key."), timeout=3), p.text_messages[-3:]
    walk_next_to(p, items, world_map, CYCLOPS["key_chest"], keys={3620, 3666, 3667}, **ability)   # door 3667
    use_map_item(p, items, CYCLOPS["key_chest"], "chest")
    assert p.wait_for(lambda: p.messages("You have found a silver key."), timeout=3), p.text_messages[-3:]


def test_mintwallin_cyclops_rules(world_map):
    ability = dict(level=2000, vocation=4, rope=True)
    moved = set(CYCLOPS["north_walls"])
    assert_no_way(world_map, THAIS_TEMPLE, CYCLOPS["beside"], **ability)                     # the wall
    assert_way(world_map, THAIS_TEMPLE, CYCLOPS["beside"], open_tiles=moved, **ability)      # the switch
    assert_way(world_map, THAIS_TEMPLE, CYCLOPS["beside"], keys={3667}, **ability)           # or key 3667
    assert_way(world_map, CYCLOPS["beside"], THAIS_TEMPLE, **ability)                        # out: the north hole

"""Deeper Fibula Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Deeper Fibula Quest (Fibula dungeon)
# docs/reference-74/quests.md "Deeper Fibula Quest"; TibiaWiki 2006: key 3940 ("it can be bought on the island":
# Dermot, 2000 gold) opens the dungeon door below the well; past the level-50 gate "Key 3980 is found by useing on
# a hole to the west"; that key opens the door south to the dragon cave, where five bodies hold the rewards; the
# south-west portal leads back. Real-map table 10014-10019. We had to script the well down (action id 54545), give
# both doors their key numbers, and place four of the five bodies (where tibiaot74 has them). Free, level 50.
FIBULA_TEMPLE = (32176, 32437, 7)
FIBULA = dict(key_hole=(32219, 32401, 10), gate=(32212, 32435, 10), gate_outside=(32212, 32436, 10),
              portal=(32234, 32502, 10), portal_to=(32210, 32437, 10),
              bodies=[((32239, 32471, 10), "dead skeleton", "a tower shield", "tower shield"),
                      ((32239, 32478, 10), "dead skeleton", "a warrior helmet", "warrior helmet"),
                      ((32233, 32493, 10), "dead skeleton", "a dwarven ring", "dwarven ring"),
                      ((32245, 32492, 10), "dead dragon", "an elven amulet", "elven amulet"),
                      ((32256, 32500, 10), "dead human", "a knight axe", "knight axe")])
PLATINUM = 2152


def test_deeper_fibula_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import npc_pos, strong, talk_to
    from tibia74.route import walk_near, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(PLATINUM, 20)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)

    # key 3940 from Dermot on Fibula (the tunnel from Thais)
    walk_near(p, items, world_map, npc_pos("Dermot"), **ability)
    said = talk_to(p, "Dermot", "hi", "key", "yes")
    assert p.wait_for(lambda: carries(p, "copper key"), timeout=3), (said, p.inventory_names())

    # down the well, the key door, the level-50 gate; key 3980 in the small hole (a crate lies on it)
    walk_next_to(p, items, world_map, FIBULA["key_hole"], keys={3940}, **ability)
    use_map_item(p, items, FIBULA["key_hole"], "small hole")
    assert p.wait_for(lambda: p.messages("You have found a golden key."), timeout=3), p.text_messages[-3:]

    # the barrel pushed aside, door 3980, the dragon cave: five bodies
    keys = dict(keys={3940, 3980}, **ability)
    for body, what, found, name in FIBULA["bodies"]:
        walk_next_to(p, items, world_map, body, **keys)
        use_map_item(p, items, body, what)
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), (body, p.text_messages[-3:])
        assert p.wait_for(lambda: carries(p, name), timeout=3), p.inventory_names()
        p.sleep(1.1)
    body, what, _, _ = FIBULA["bodies"][-1]
    use_map_item(p, items, body, what)
    assert p.wait_for(lambda: p.messages(f"The {what} is empty."), timeout=3), p.text_messages[-2:]

    # out through the south-west portal
    walk_next_to(p, items, world_map, FIBULA["portal"], **keys)
    step_onto(p, FIBULA["portal"])
    assert p.wait_for(lambda: p.pos == FIBULA["portal_to"], timeout=3), p.pos


def test_deeper_fibula_level_door(new_player, items):
    """Level 49 is refused at the gate of expertise; level 50 passes."""
    assert_level_door(new_player, items, FIBULA["gate"], FIBULA["gate_outside"], 50)


def test_deeper_fibula_rules(world_map):
    ability = dict(vocation=4, rope=True)
    cave = FIBULA["bodies"][0][0]
    beside = (cave[0], cave[1] + 1, cave[2])
    # key 3940 opens the dungeon; the level-50 gate; key 3980 (from the hole) opens the dragon cave
    assert_no_way(world_map, FIBULA_TEMPLE, FIBULA["key_hole"], level=2000, **ability)
    assert_way(world_map, FIBULA_TEMPLE, (32220, 32401, 10), level=50, keys={3940}, **ability)
    assert_no_way(world_map, FIBULA_TEMPLE, (32220, 32401, 10), level=49, keys={3940}, **ability)
    assert_no_way(world_map, FIBULA_TEMPLE, beside, level=2000, keys={3940}, **ability)
    assert_way(world_map, FIBULA_TEMPLE, beside, level=50, keys={3940, 3980}, **ability)

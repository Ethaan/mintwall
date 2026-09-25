"""Fire Axe Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki pre-8.0: into the Edron dragon lair, down and up the rope holes (destroy field runes for the blocked ones),
# the level-60 gate, down to the 3 dragon lords: "The quest boxes are in the SW part of the room"; "For the Fire Axe,
# pick open a hole, go down and use the skeleton remains". Both containers were missing on our map: placed at
# tibiaot74's spots, real-map table uids 1019 (ring of healing, dragon necklace, 7 small diamonds) and 1018 (fire axe)
# - quests/system.lua.
FIRE_AXE = dict(gate=(33085, 31650, 10), chest=(33078, 31656, 11), pick_spot=(33081, 31651, 11),
                skeleton=(33084, 31650, 12), beside_chest=(33079, 31656, 11), beside_skeleton=(33083, 31650, 12))
DESTROY_FIELD = 2261


def test_fire_axe_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    F = FIRE_AXE
    p = strong(new_player, EDRON_TEMPLE, premium_days=30, items=[Item(PICK), Item(DESTROY_FIELD, 3)], maglevel=10,
               group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, pick=True)

    walk_next_to(p, items, world_map, F["chest"], **ability)
    use_map_item(p, items, F["chest"], "chest")
    for found in ("a ring of healing", "a dragon necklace", "7 small diamonds"):
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-4:]
    p.sleep(1.1)
    use_map_item(p, items, F["chest"], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

    # the pick hole down to the skeleton
    walk_next_to(p, items, world_map, F["skeleton"], **ability)
    use_map_item(p, items, F["skeleton"], "dead skeleton")
    assert p.wait_for(lambda: p.messages("You have found a fire axe."), timeout=3), p.text_messages[-3:]
    for name in ("ring of healing", "dragon necklace", "small diamond", "fire axe"):
        assert carries(p, name), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, F["skeleton"], "dead skeleton")
    assert p.wait_for(lambda: p.messages("The dead skeleton is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, EDRON_TEMPLE, **ability)


def test_fire_axe_level_door(new_player, items):
    assert_level_door(new_player, items, FIRE_AXE["gate"], (33086, 31650, 10), 60)


def test_fire_axe_rules(world_map):
    F = FIRE_AXE
    assert_way(world_map, EDRON_TEMPLE, F["beside_chest"], level=60, rope=True)
    assert_no_way(world_map, EDRON_TEMPLE, F["beside_chest"], level=59, rope=True, pick=True)       # the gate
    assert_no_way(world_map, EDRON_TEMPLE, F["beside_skeleton"], level=60, rope=True)               # the pick hole
    assert_way(world_map, EDRON_TEMPLE, F["beside_skeleton"], level=60, rope=True, pick=True)
    assert_way(world_map, F["beside_skeleton"], EDRON_TEMPLE, level=60, rope=True)                  # out
    assert_no_way(world_map, F["beside_chest"], EDRON_TEMPLE, level=60)                             # a rope

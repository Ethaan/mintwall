"""Orc Fortress Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: into the Orc Fortress hole, east, down the stairs, east and north "through the level 40 gate of
# expertise ... The quest boxes are located in the north end of this room" - knight armor, knight axe, fire sword
# (decided with the user 2026-09-26 over Tibiantis' list). Our map had the three chests without quest ids.
ORC_FORTRESS = dict(gate=(32981, 31760, 9), outside=(32981, 31761, 9), inside=(32981, 31728, 9),
                    chests=[((32980, 31727, 9), "a knight armor"), ((32981, 31727, 9), "a knight axe"),
                            ((32985, 31727, 9), "a fire sword")])


def test_orc_fortress_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    O = ORC_FORTRESS
    p = strong(new_player, ABDENDRIEL_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, rope=True)
    for chest, found in O["chests"]:
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    for name in ("knight armor", "knight axe", "fire sword"):
        assert carries(p, name), p.inventory_names()
    follow(p, items, world_map, ABDENDRIEL_TEMPLE, **ability)


def test_orc_fortress_level_door(new_player, items):
    O = ORC_FORTRESS
    assert_level_door(new_player, items, O["gate"], O["outside"], 40)


def test_orc_fortress_rules(world_map):
    O = ORC_FORTRESS
    assert_no_way(world_map, ABDENDRIEL_TEMPLE, O["inside"], level=39, rope=True)
    assert_way(world_map, ABDENDRIEL_TEMPLE, O["inside"], level=40, rope=True)

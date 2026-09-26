"""Circle Room Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: down through the Kazordoon dwarf mines "to the level 32 door, then go down the hole. [...] The quest
# boxes are at the far south end" - dwarven axe and war hammer (all sources). Our map (and the JS engine's) had the
# boxes' room shut by a locked door with no key number standing on lava; tibiaot74 has a plain door on dirt there.
CIRCLE_ROOM = dict(gate=(32510, 31956, 13), outside=(32510, 31957, 13), door=(32513, 31947, 14),
                   inside=(32513, 31945, 14),
                   boxes=[((32512, 31944, 14), "a dwarven axe"), ((32514, 31944, 14), "a war hammer")])


def test_circle_room_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    C = CIRCLE_ROOM
    p = strong(new_player, KAZORDOON_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, rope=True, floors=9)
    for box, found in C["boxes"]:
        walk_next_to(p, items, world_map, box, **ability)
        use_map_item(p, items, box, "box")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    for name in ("dwarven axe", "war hammer"):
        assert carries(p, name), p.inventory_names()
    before = len(p.text_messages)
    use_map_item(p, items, C["boxes"][0][0], "box")
    assert p.wait_for(lambda: any("empty" in t for _, t in p.text_messages[before:]), timeout=3), p.text_messages[-3:]
    follow(p, items, world_map, KAZORDOON_TEMPLE, **ability)


def test_circle_room_level_door(new_player, items):
    C = CIRCLE_ROOM
    assert_level_door(new_player, items, C["gate"], C["outside"], 32)


def test_circle_room_rules(world_map):
    C = CIRCLE_ROOM
    assert_no_way(world_map, KAZORDOON_TEMPLE, C["inside"], level=31, rope=True, floors=9)
    assert_way(world_map, KAZORDOON_TEMPLE, C["inside"], level=32, rope=True, floors=9)

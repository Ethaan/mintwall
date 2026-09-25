"""Power Ring Quest, Femor Hills (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: in Femor Hills "follow along the South side of the river that flows into the mountain [...] and rope
# up one level", east and down the ladder, north-east and down the hole, south-west and down one more level: "The Quest
# boxes are on the north end of this room, next to the Beer Casks" - a power ring and a bronze amulet. No level; a rope.
# Our map had both chests (32599/32601,31776,9) without quest ids: real-map table uids 4511 / 4512.
POWER_RING = dict(chests=[((32599, 31776, 9), "a power ring"), ((32601, 31776, 9), "a bronze amulet")],
                  beside=(32600, 31777, 9))


def test_power_ring_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, CARLIN_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=1, rope=True)
    for chest, found in POWER_RING["chests"]:
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    assert carries(p, "power ring") and carries(p, "bronze amulet"), p.inventory_names()
    for chest, _ in POWER_RING["chests"]:                                  # once each
        before = len(p.messages("The chest is empty."))
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: len(p.messages("The chest is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    follow(p, items, world_map, CARLIN_TEMPLE, **ability)


def test_power_ring_rules(world_map):
    B = POWER_RING["beside"]
    assert_way(world_map, CARLIN_TEMPLE, B, level=1, rope=True)                               # no level
    assert_no_way(world_map, CARLIN_TEMPLE, B, level=1)                                       # a rope
    assert_way(world_map, B, CARLIN_TEMPLE, level=1, rope=True)

"""Ring Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (current; no 7.x page, Tibiantis lists it): into the Edron Hero Cave with a rope, "Follow the route",
# "Use the chests to get your reward" - a time ring and a sword ring - "Follow the same way out". No level. Our map
# (and the JS engine's) lost both chests: placed in the two empty spots of the room at 33131/33134,31624,15, where
# tibiaot74 has them; uid = the item (2169 time ring, 2207 sword ring).
RING = dict(chests=[((33131, 31624, 15), "a time ring"), ((33134, 31624, 15), "a sword ring")],
            beside=(33131, 31625, 15))


def test_ring_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    p = edron_player(new_player)
    ability = dict(level=1, rope=True)
    for chest, found in RING["chests"]:
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    assert carries(p, "time ring") and carries(p, "sword ring"), p.inventory_names()
    for chest, _ in RING["chests"]:                                       # once each
        before = len(p.messages("The chest is empty."))
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: len(p.messages("The chest is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    follow(p, items, world_map, EDRON_TEMPLE, **ability)                 # "the same way out", up with the rope


def test_ring_rules(world_map):
    assert_way(world_map, EDRON_TEMPLE, RING["beside"], level=1)                     # no level
    assert_way(world_map, RING["beside"], EDRON_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, RING["beside"], EDRON_TEMPLE, level=1)                   # out needs the rope

"""Wedding Ring Quest, Edron Hero Cave (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (current; Tibiantis: "Wedding Ring Quest, Edron: Wedding Ring, Dragon Necklace"): into the Edron Hero
# Cave, "Follow the route", "In screen 8 you will face 3 Heroes and a Dark Apprentice. Use the chests to get a Wedding
# Ring and a Dragon Necklace. Follow the same way out." No level. Our map (and the JS engine's) lost both chests:
# placed in the kitchen's empty spots 33158,31621-31622,15, where tibiaot74 has them; uid = the item (2121 wedding
# ring, 2201 dragon necklace).
WEDDING = dict(chests=[((33158, 31621, 15), "a wedding ring"), ((33158, 31622, 15), "a dragon necklace")],
               beside=(33157, 31621, 15))


def test_wedding_ring_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    p = edron_player(new_player)
    ability = dict(level=1, rope=True)
    for chest, found in WEDDING["chests"]:
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    assert carries(p, "wedding ring") and carries(p, "dragon necklace"), p.inventory_names()
    for chest, _ in WEDDING["chests"]:                                    # once each
        before = len(p.messages("The chest is empty."))
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: len(p.messages("The chest is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    follow(p, items, world_map, EDRON_TEMPLE, **ability)                 # "the same way out"


def test_wedding_ring_rules(world_map):
    assert_way(world_map, EDRON_TEMPLE, WEDDING["beside"], level=1)                  # no level
    assert_way(world_map, WEDDING["beside"], EDRON_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, WEDDING["beside"], EDRON_TEMPLE, level=1)                # out needs a rope

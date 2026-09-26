"""Iron Hammer Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005/2006: dig the loose stone pile west of Kazordoon with a shovel, go north-west past the minotaurs to
# a room with beds - "The quest box is between the beds". Iron hammer (all sources). Our map had lost the box.
BOX = (32434, 31938, 8)
BESIDE = (32434, 31939, 8)


def test_iron_hammer_quest(new_player, items, world_map):
    from tibia74 import Item
    from tibia74.route import walk_next_to
    p = kazordoon_player(new_player, items=[Item(SHOVEL)])
    ability = dict(level=2000, rope=True, shovel=True)
    walk_next_to(p, items, world_map, BOX, **ability)
    use_map_item(p, items, BOX, "box")
    assert p.wait_for(lambda: p.messages("You have found an iron hammer."), timeout=3), p.text_messages[-3:]
    assert carries(p, "iron hammer"), p.inventory_names()


def test_iron_hammer_rules(world_map):
    # the way in is the loose stone pile: a shovel
    assert_no_way(world_map, KAZORDOON_TEMPLE, BESIDE, level=100, rope=True)
    assert_way(world_map, KAZORDOON_TEMPLE, BESIDE, level=100, rope=True, shovel=True)

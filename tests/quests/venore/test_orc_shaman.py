"""Orc Shaman Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: the shovel hole east of Venore's south gate, east and down - "The quest box is in the south-east corner
# of the room": a bag with a magic lightwand, an axe ring and a blank rune. Our map had lost the box.
BOX = (33089, 32030, 9)


def test_orc_shaman_quest(new_player, items, world_map):
    from tibia74 import Item
    p = venore_player(new_player, items=[Item(SHOVEL)])
    collect(p, items, world_map, BOX, "box", ["a bag"], level=2000, rope=True, shovel=True)
    inside = bag_contents(p, items)
    for name in ("magic lightwand", "axe ring", "blank rune"):
        assert name in inside, (name, inside)


def test_orc_shaman_rules(world_map):
    assert_no_way(world_map, VENORE_TEMPLE, (33088, 32030, 9), level=100, rope=True)
    assert_way(world_map, VENORE_TEMPLE, (33088, 32030, 9), level=100, rope=True, shovel=True)

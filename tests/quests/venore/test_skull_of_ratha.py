"""Skull of Ratha Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: on Witch Hill two boxes give two bags (white pearl + skull of Ratha; wolf tooth chain + dwarven ring);
# in the basement east of the hill a chest in the north-east corner a bag with 100 gp, a crystal necklace and 2 black
# pearls. Our map had the three containers without quest ids.
def test_skull_of_ratha_quest(new_player, items, world_map):
    p = venore_player(new_player)
    ability = dict(level=2000, rope=True)
    for spot, what in (((32847, 31917, 6), "box"), ((32845, 31917, 6), "box"), ((32867, 31909, 8), "chest")):
        collect(p, items, world_map, spot, what, ["a bag"], **ability)
    inside = bag_contents(p, items)
    for name in ("skull", "white pearl", "wolf tooth chain", "dwarven ring", "crystal necklace", "black pearl"):
        assert name in inside, (name, inside)

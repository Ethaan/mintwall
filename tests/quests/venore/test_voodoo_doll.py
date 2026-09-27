"""Voodoo Doll Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: down the hole on the north side of Greenclaw Swamp, west and down again, the boxes against the east
# wall of the large east room: a voodoo doll and a magic lightwand. Both boxes were lost on our map (placed at
# tibiaot74's spots).
def test_voodoo_doll_quest(new_player, items, world_map):
    p = venore_player(new_player)
    ability = dict(level=2000, rope=True)
    collect(p, items, world_map, (32757, 31957, 9), "box", ["a voodoo doll"], **ability)
    collect(p, items, world_map, (32758, 31952, 9), "box", ["a magic lightwand"], **ability)
    assert carries(p, "voodoo doll") and carries(p, "magic lightwand"), p.inventory_names()

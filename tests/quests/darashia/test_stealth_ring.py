"""Stealth Ring Quest (Minotaur Pyramid) (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: down the Minotaur Pyramid north-east of Darashia, past the mummy on the bottom floor - the south-east
# coffin holds the stealth ring, the north-east one the protection amulet. Our map had the coffins without quest ids.
def test_stealth_ring_quest(new_player, items, world_map):
    p = darashia_player(new_player)
    ability = dict(level=2000, rope=True, floors=9)
    collect(p, items, world_map, (33315, 32282, 11), "stone coffin", ["a stealth ring"], **ability)
    collect(p, items, world_map, (33315, 32277, 11), "stone coffin", ["a protection amulet"], **ability)
    assert carries(p, "stealth ring") and carries(p, "protection amulet"), p.inventory_names()

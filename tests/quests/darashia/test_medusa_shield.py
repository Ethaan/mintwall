"""Medusa Shield Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005/2006: down into Drefia, north to a hole, east through the level-60 gate, up the hole - "The rewards are
# located in a coffin in the east part of the room": medusa shield, skull staff, blue robe. Our map had no coffin
# there (placed at tibiaot74's spot; decided with the user).
COFFIN = (33049, 32399, 10)


def test_medusa_shield_quest(new_player, items, world_map):
    p = darashia_player(new_player)
    collect(p, items, world_map, COFFIN, "stone coffin", ["a medusa shield", "a skull staff", "a blue robe"],
            level=2000, rope=True, floors=9)
    for name in ("medusa shield", "skull staff", "blue robe"):
        assert carries(p, name), (name, p.inventory_names())


def test_medusa_shield_rules(world_map):
    beside = (COFFIN[0] - 1, COFFIN[1], COFFIN[2])
    assert_no_way(world_map, DARASHIA_TEMPLE, beside, level=59, rope=True, floors=9)
    assert_way(world_map, DARASHIA_TEMPLE, beside, level=60, rope=True, floors=9)

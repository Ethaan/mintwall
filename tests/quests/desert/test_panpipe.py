"""Panpipe Quest (Fire Devil Quest) (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: key 4055 in the hollow rock just south of the Desert Dungeon's entrance; down five floors, west, south,
# up past the library, rope up twice, south and up to the locked door - one fire devil - and the box: a bag with
# panpipes, 2 small amethysts and a power ring (all sources). Our map had the rock without a quest id, the door without
# its key number and no box.
ROCK, DOOR, BOX = (32652, 32107, 7), (32643, 32128, 8), (32644, 32131, 8)


def test_panpipe_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    p = strong(new_player, THAIS_TEMPLE, items=[Item(SHOVEL)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    keys = set()
    ability = lambda: dict(level=19, rope=True, shovel=True, keys=keys, floors=9)     # noqa: E731
    collect(p, items, world_map, ROCK, "stone", ["a silver key"], **ability())
    keys.add(4055)
    collect(p, items, world_map, BOX, "chest", ["a bag"], **ability())
    inside = bag_contents(p, items)
    for name in ("panpipes", "small amethyst", "power ring"):
        assert name in inside, (name, inside)


def test_panpipe_rules(world_map):
    beside = (BOX[0], BOX[1] - 1, BOX[2])
    assert_no_way(world_map, THAIS_TEMPLE, beside, level=19, rope=True, shovel=True, floors=9)
    assert_way(world_map, THAIS_TEMPLE, beside, level=19, rope=True, shovel=True, keys={4055}, floors=9)

"""Silver Brooch Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: shovel, rope and a pick into the mummies' tomb - "Use a coffin on the north end of this room": a bag
# with the silver brooch, 2 small rubies and 3 small diamonds. Our map had the coffin without a quest id.
COFFIN = (32775, 32006, 11)


def test_silver_brooch_quest(new_player, items, world_map):
    from tibia74 import Item
    p = venore_player(new_player, items=[Item(SHOVEL), Item(PICK), Item(2420)])
    collect(p, items, world_map, COFFIN, "wooden coffin", ["a bag"],
            level=2000, rope=True, shovel=True, pick=True, machete=True)
    inside = bag_contents(p, items)
    for name in ("silver brooch", "small ruby", "small diamond"):
        assert name in inside, (name, inside)


def test_silver_brooch_rules(world_map):
    # the tomb is under the pick spot
    beside = (COFFIN[0], COFFIN[1] + 1, COFFIN[2])
    assert_no_way(world_map, VENORE_TEMPLE, beside, level=100, rope=True, shovel=True, machete=True)
    assert_way(world_map, VENORE_TEMPLE, beside, level=100, rope=True, shovel=True, machete=True, pick=True)

"""Time Ring Quest (Shadowthorn Quest) (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: a machete into Shadowthorn, the hole, west and down the ramp - "three quest boxes in the north end of
# this room": time ring, elven amulet, crystal ball (all sources). Our map had the three chests without quest ids.
CHESTS = [((33038, 32171, 9), "a time ring"), ((33039, 32171, 9), "an elven amulet"),
          ((33040, 32171, 9), "a crystal ball")]
MACHETE = 2420


def test_time_ring_quest(new_player, items, world_map):
    from tibia74 import Item
    from tibia74.route import walk_next_to
    p = venore_player(new_player, items=[Item(MACHETE)])
    ability = dict(level=2000, rope=True, machete=True)
    for chest, found in CHESTS:
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    for name in ("time ring", "elven amulet", "crystal ball"):
        assert carries(p, name), p.inventory_names()


def test_time_ring_rules(world_map):
    # Shadowthorn's jungle: no way in without a machete
    assert_no_way(world_map, VENORE_TEMPLE, (33039, 32172, 9), level=100, rope=True)
    assert_way(world_map, VENORE_TEMPLE, (33039, 32172, 9), level=100, rope=True, machete=True)

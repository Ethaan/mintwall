"""Steel Helmet Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: rope up from the minotaur cave west of Kazordoon into the tower; "The rewards can be found in various
# dressers and chests" - steel helmet, 47 gp, 56 gp, a scroll. The current spoiler's four spots; our map had lost the
# steel helmet's box and had none of them scripted.
SPOTS = [((32460, 31951, 5), "drawers", "You have found 56 gold coins."),
         ((32462, 31947, 4), "box", "You have found a steel helmet."),
         ((32464, 31957, 5), "box", "You have found 47 gold coins."),
         ((32467, 31962, 4), "chest", "You have found a scroll.")]


def test_steel_helmet_quest(new_player, items, world_map):
    from tibia74 import Item
    from tibia74.route import walk_next_to
    p = kazordoon_player(new_player, items=[Item(SHOVEL)])
    ability = dict(level=2000, rope=True, shovel=True)
    for spot, what, found in SPOTS:
        walk_next_to(p, items, world_map, spot, **ability)
        use_map_item(p, items, spot, what)
        assert p.wait_for(lambda: p.messages(found), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    assert carries(p, "steel helmet") and carries(p, "scroll"), p.inventory_names()


def test_steel_helmet_rules(world_map):
    # the tower is reached from the cave below the loose stone pile: a shovel
    assert_no_way(world_map, KAZORDOON_TEMPLE, (32463, 31947, 4), level=100, rope=True)
    assert_way(world_map, KAZORDOON_TEMPLE, (32463, 31947, 4), level=100, rope=True, shovel=True)

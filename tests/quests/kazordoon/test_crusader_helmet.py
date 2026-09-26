"""Crusader Helmet Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: down the mines west of Kazordoon, "north through the level 35 door and down the hole [...] The
# reward is in a skeleton body at the far west end of the tunnel" - a crusader helmet (both wikis and the real-map
# table; Tibiantis alone says dwarven helmet). Our map had the skeleton without a quest id.
CRUSADER = dict(gate=(32475, 31946, 13), outside=(32475, 31947, 13), skeleton=(32427, 31943, 14),
                beside=(32428, 31942, 14))


def test_crusader_helmet_quest(new_player, items, world_map):
    from tibia74.route import walk_next_to
    C = CRUSADER
    p = kazordoon_player(new_player)
    ability = dict(level=2000, rope=True, floors=9)
    walk_next_to(p, items, world_map, C["skeleton"], **ability)
    use_map_item(p, items, C["skeleton"], "slain skeleton")
    assert p.wait_for(lambda: p.messages("You have found a crusader helmet."), timeout=3), p.text_messages[-3:]
    assert carries(p, "crusader helmet"), p.inventory_names()


def test_crusader_helmet_level_door(new_player, items):
    C = CRUSADER
    assert_level_door(new_player, items, C["gate"], C["outside"], 35)


def test_crusader_helmet_rules(world_map):
    C = CRUSADER
    assert_no_way(world_map, KAZORDOON_TEMPLE, C["beside"], level=34, rope=True, floors=9)
    assert_way(world_map, KAZORDOON_TEMPLE, C["beside"], level=35, rope=True, floors=9)

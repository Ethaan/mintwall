"""Double Hero Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki pre-8.0: down the Edron Hero Cave (holes, stairs, the dragons' hole), "Go south slowly" to the room of 2
# heroes; "Two chests at the south of the room: open both" - a club ring and a red gem. No level; a rope to get out.
# The boxes 33109/33110,31679,13 are on our map; real-map table uids 4522 / 4523 (quests/system.lua).
DOUBLE_HERO = dict(boxes=[((33109, 31679, 13), "a club ring"), ((33110, 31679, 13), "a red gem")],
                   beside=(33109, 31678, 13))


def test_double_hero_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    p = edron_player(new_player)
    ability = dict(level=1, rope=True)
    for box, found in DOUBLE_HERO["boxes"]:
        walk_next_to(p, items, world_map, box, **ability)
        use_map_item(p, items, box, "box")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    assert carries(p, "club ring") and carries(p, "red gem"), p.inventory_names()
    for box, _ in DOUBLE_HERO["boxes"]:                                   # once each
        before = len(p.messages("The box is empty."))
        use_map_item(p, items, box, "box")
        assert p.wait_for(lambda: len(p.messages("The box is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    follow(p, items, world_map, EDRON_TEMPLE, **ability)


def test_double_hero_rules(world_map):
    assert_way(world_map, EDRON_TEMPLE, DOUBLE_HERO["beside"], level=1)               # no level
    assert_way(world_map, DOUBLE_HERO["beside"], EDRON_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, DOUBLE_HERO["beside"], EDRON_TEMPLE, level=1)             # out needs a rope

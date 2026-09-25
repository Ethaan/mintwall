"""Troll Cave Quest, Edron (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki pre-8.0: down the castle drain to the grassy area, the troll cave's hole, "Follow this path to the north
# and east, and go down the hole", then down once more: "The reward is in two boxes on the East side of the room" -
# brass legs and a garlic necklace. No level; a rope. The boxes were missing on our map: placed at tibiaot74's spots,
# real-map table uids 1026 / 1027 (quests/system.lua).
TROLL_CAVE = dict(boxes=[((33143, 31719, 10), "brass legs"), ((33143, 31721, 10), "a garlic necklace")],
                  beside=(33142, 31719, 10))


def test_troll_cave_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    p = edron_player(new_player)
    ability = dict(level=1, rope=True)
    for box, found in TROLL_CAVE["boxes"]:
        walk_next_to(p, items, world_map, box, **ability)
        use_map_item(p, items, box, "box")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    assert carries(p, "brass legs") and carries(p, "garlic necklace"), p.inventory_names()
    for box, _ in TROLL_CAVE["boxes"]:                                    # once each
        before = len(p.messages("The box is empty."))
        walk_next_to(p, items, world_map, box, **ability)
        use_map_item(p, items, box, "box")
        assert p.wait_for(lambda: len(p.messages("The box is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    follow(p, items, world_map, EDRON_TEMPLE, **ability)                 # out by the grassy area's pitfall


def test_troll_cave_rules(world_map):
    B = TROLL_CAVE["beside"]
    assert_way(world_map, EDRON_TEMPLE, B, level=1, rope=True)                            # no level
    assert_no_way(world_map, EDRON_TEMPLE, B, level=1)                                    # a rope
    assert_way(world_map, B, EDRON_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, B, EDRON_TEMPLE, level=1)

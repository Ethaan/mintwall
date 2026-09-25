"""Life Ring Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Life Ring Quest (Thais Ancient Temple)
# docs/reference-74/quests.md "Life Ring Quest"; TibiaWiki: down the temple, east over the drawbridge, past the
# beholders to a dead end at water, "pick the hidden hole", the box in the NE corner below. Real-map table: "[3616] =
# {{2168},{2201,200}}, -- Ancient Temple Life ring Quest" (life ring, dragon necklace). Pick and rope. Free, once.
LIFE_RING = dict(box=(32443, 32238, 11), pick_spot=(32437, 32239, 10), beside=(32442, 32239, 11))


def test_life_ring_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(PICK)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, pick=True)
    walk_next_to(p, items, world_map, LIFE_RING["box"], **ability)
    before = len(p.text_messages)
    use_map_item(p, items, LIFE_RING["box"], "box")
    found = lambda: sorted(t for _, t in p.text_messages[before:] if t.startswith("You have found"))  # noqa: E731
    assert p.wait_for(lambda: found() == ["You have found a dragon necklace.", "You have found a life ring."],
                      timeout=3), found()
    p.sleep(1.1)
    use_map_item(p, items, LIFE_RING["box"], "box")
    assert p.wait_for(lambda: p.messages("The box is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)                    # out: a rope up the hole


def test_life_ring_rules(world_map):
    # a pick opens the way down, a rope is the way back up
    assert_no_way(world_map, THAIS_TEMPLE, LIFE_RING["beside"], level=1, rope=True)
    assert_way(world_map, THAIS_TEMPLE, LIFE_RING["beside"], level=1, rope=True, pick=True)
    assert_way(world_map, LIFE_RING["beside"], THAIS_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, LIFE_RING["beside"], THAIS_TEMPLE, level=1)

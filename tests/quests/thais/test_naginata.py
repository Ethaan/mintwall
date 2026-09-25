"""Naginata Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki: through the Thais dragon lair, "Pick the large rock over a hole", "The hole beyond the level 40 door
# leads down to 2 Dragon Lords. The chest is at the north end." The room had no container on our map: a chest placed
# at its north end (32346,32063,12). Real-map table [10065]: naginata. Pick and rope. Free, level 40, once.
NAGINATA = dict(chest=(32346, 32063, 12), beside=(32346, 32064, 12), gate=(32353, 32073, 11),
                gate_outside=(32354, 32073, 11))


def test_naginata_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    # destroy field: a fire field covers the rope spot on the way back (TibiaWiki recommends it)
    p = strong(new_player, THAIS_TEMPLE, items=[Item(PICK), Item(2261, 3)], maglevel=10, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, pick=True)
    walk_next_to(p, items, world_map, NAGINATA["chest"], **ability)
    use_map_item(p, items, NAGINATA["chest"], "chest")
    assert p.wait_for(lambda: p.messages("You have found a naginata."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "naginata"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, NAGINATA["chest"], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)


def test_naginata_level_door(new_player, items):
    assert_level_door(new_player, items, NAGINATA["gate"], NAGINATA["gate_outside"], 40)


def test_naginata_rules(world_map):
    ability = dict(vocation=4, rope=True)
    assert_no_way(world_map, THAIS_TEMPLE, NAGINATA["beside"], level=2000, **ability)            # the pick
    assert_no_way(world_map, THAIS_TEMPLE, NAGINATA["beside"], level=39, pick=True, **ability)   # the gate
    assert_way(world_map, THAIS_TEMPLE, NAGINATA["beside"], level=40, pick=True, **ability)
    assert_way(world_map, NAGINATA["beside"], THAIS_TEMPLE, level=40, **ability)

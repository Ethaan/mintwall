"""Spike Sword Quest / Fire Devil Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (2005/2006): shovel into the cave NE of the Triangle Tower, pick a hole, pick another, down to the fire
# devils' lava room: "The reward is in a body hidden behind a pillar". The body was missing on our map (placed at
# tibiaot74's spot, behind the pillar at 32569,32086,12). Real-map table [3620]: spike sword. Shovel, pick, rope.
SPIKE_SWORD = dict(body=(32568, 32085, 12), beside=(32567, 32085, 12))


def test_spike_sword_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(SHOVEL), Item(PICK)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, shovel=True, pick=True)
    walk_next_to(p, items, world_map, SPIKE_SWORD["body"], **ability)
    use_map_item(p, items, SPIKE_SWORD["body"], "dead human")
    assert p.wait_for(lambda: p.messages("You have found a spike sword."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "spike sword"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, SPIKE_SWORD["body"], "dead human")
    assert p.wait_for(lambda: p.messages("The dead human is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)


def test_spike_sword_rules(world_map):
    ability = dict(level=1, vocation=4, rope=True)
    assert_no_way(world_map, THAIS_TEMPLE, SPIKE_SWORD["beside"], shovel=True, **ability)          # the picks
    assert_no_way(world_map, THAIS_TEMPLE, SPIKE_SWORD["beside"], pick=True, **ability)            # the shovel
    assert_way(world_map, THAIS_TEMPLE, SPIKE_SWORD["beside"], shovel=True, pick=True, **ability)
    assert_way(world_map, SPIKE_SWORD["beside"], THAIS_TEMPLE, **ability)

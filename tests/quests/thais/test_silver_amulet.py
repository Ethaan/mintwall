"""Silver Amulet Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki: shovel into the Thais troll cave; "The amulet is hidden in a box in the southeast cellar" (its mapper
# link: 32507,32270,9 - there was no box on our map, placed; uid 2170 = the amulet - the real-map table's 1029 is the
# Edron Goblin Quest's). Free, once.
SILVER_AMULET = dict(box=(32507, 32270, 9), beside=(32507, 32269, 9))


def test_silver_amulet_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(SHOVEL)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, shovel=True)
    walk_next_to(p, items, world_map, SILVER_AMULET["box"], **ability)
    use_map_item(p, items, SILVER_AMULET["box"], "box")
    assert p.wait_for(lambda: p.messages("You have found a silver amulet."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "silver amulet"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, SILVER_AMULET["box"], "box")
    assert p.wait_for(lambda: p.messages("The box is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)


def test_silver_amulet_rules(world_map):
    assert_no_way(world_map, THAIS_TEMPLE, SILVER_AMULET["beside"], level=1)                    # a shovel opens it
    assert_way(world_map, THAIS_TEMPLE, SILVER_AMULET["beside"], level=1, shovel=True)
    assert_way(world_map, SILVER_AMULET["beside"], THAIS_TEMPLE, level=1)

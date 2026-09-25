"""Throwing Star Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Throwing Star Quest (Ancient Temple)
# docs/reference-74/quests.md "Throwing Star Quest"; TibiaWiki: through the Ancient Temple to the underground park,
# "Pick where the map indicates", the box "just SE of the ladder". Real-map table: "[3619] = {{2399,10}}, --
# throwing stars Mintwallin Quest". Pick and rope. Free, once.
THROWING_STAR = dict(box=(32522, 32111, 15), beside=(32521, 32110, 15))


def test_throwing_star_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(PICK)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, pick=True)
    walk_next_to(p, items, world_map, THROWING_STAR["box"], **ability)
    use_map_item(p, items, THROWING_STAR["box"], "box")
    assert p.wait_for(lambda: p.messages("You have found 10 throwing stars."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "throwing star"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, THROWING_STAR["box"], "box")
    assert p.wait_for(lambda: p.messages("The box is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)


def test_throwing_star_rules(world_map):
    assert_no_way(world_map, THAIS_TEMPLE, THROWING_STAR["beside"], level=1, rope=True)
    assert_way(world_map, THAIS_TEMPLE, THROWING_STAR["beside"], level=1, rope=True, pick=True)
    assert_way(world_map, THROWING_STAR["beside"], THAIS_TEMPLE, level=1, rope=True)

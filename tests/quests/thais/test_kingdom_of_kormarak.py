"""Kingdom of Kormarak Quest / Old Mintwallin Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (2006, "Old Mintwallin Quest"): past the ghouls and the teleporter, "the dead human by the wooden coffin";
# "It is a spawn, so you may find the body empty" - not once per character: whoever comes first takes it, and it is
# back after the server save (a map container; the map puts it back at every start). Real-map table [3618]: brass
# armor, brass helmet, hatchet, 4 throwing stars (the wiki since 2011 and Tibiantis say 13; no 7.x text names them).
# The body was missing on our map (placed where tibiaot74 has it).
KORMARAK = dict(body=(32552, 32200, 11), beside=(32551, 32200, 11))


def test_kingdom_of_kormarak_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import open_map_container, strong, take
    from tibia74.route import walk_next_to
    ability = dict(level=2000, vocation=4, rope=True)
    p = strong(new_player, THAIS_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, KORMARAK["body"], **ability)
    body = open_map_container(p, items, KORMARAK["body"], "dead human")
    assert sorted(i.name for i in body.items) == ["brass armor", "brass helmet", "hatchet", "throwing star"], body.items
    for name in ("brass armor", "brass helmet", "hatchet", "throwing star"):
        take(p, items, body, name)
    assert carries(p, "brass armor") and carries(p, "throwing star"), p.inventory_names()

    # a spawn, not a quest box: the next character finds it empty
    other = strong(new_player, KORMARAK["beside"][:2] + (11,), group_id=TESTER_GROUP)
    body = open_map_container(other, items, KORMARAK["body"], "dead human")
    assert other.wait_for(lambda: not body.items, timeout=2), body.items


def test_kingdom_of_kormarak_rules(world_map):
    assert_way(world_map, THAIS_TEMPLE, KORMARAK["beside"], level=1)
    assert_way(world_map, KORMARAK["beside"], THAIS_TEMPLE, level=1)

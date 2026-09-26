"""Dead Archer Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Dead Archer Quest (Thais troll cave)
# docs/reference-74/quests.md "Dead Archer Quest"; TibiaWiki (2006): shovel the troll cave hole open, down twice,
# south through the poison fields by the slimes, "Use the body at the north end of the room". The body was missing
# on our map: a dead human placed where tibiaot74 has it, with the real-map table's unique id 1662 (bow, 5 poison
# arrows, mana fluid, life fluid - also TibiaWiki pre-8.0 and Tibiantis). No level, free, 1 player, once.
DEAD_ARCHER = dict(body=(32513, 32302, 10), beside=(32514, 32303, 10), hole=(32493, 32259, 7))
SHOVEL_ID = 2554


def test_dead_archer_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(SHOVEL_ID)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, shovel=True)
    walk_next_to(p, items, world_map, DEAD_ARCHER["body"], **ability)
    before = len(p.text_messages)
    use_map_item(p, items, DEAD_ARCHER["body"], "dead human")
    found = lambda: [t for _, t in p.text_messages[before:] if t.startswith("You have found")]  # noqa: E731
    # a vial is named as its look text names it: "a vial of manafluid" (quests/system.lua describe(), items.xml 200xx)
    assert p.wait_for(lambda: sorted(found()) == sorted(["You have found a bow.", "You have found 5 poison arrows.",
                                                          "You have found a vial of manafluid.",
                                                          "You have found a vial of lifefluid."]),
                      timeout=3), found()
    assert p.wait_for(lambda: carries(p, "bow"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, DEAD_ARCHER["body"], "dead human")
    assert p.wait_for(lambda: p.messages("The dead human is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)                    # out: the ladders, nothing needed


def test_dead_archer_rules(world_map):
    # the troll cave is shovelled open; the way back up needs nothing
    assert_no_way(world_map, THAIS_TEMPLE, DEAD_ARCHER["beside"], level=1, rope=True)
    assert_way(world_map, THAIS_TEMPLE, DEAD_ARCHER["beside"], level=1, rope=True, shovel=True)
    assert_way(world_map, DEAD_ARCHER["beside"], THAIS_TEMPLE, level=1)

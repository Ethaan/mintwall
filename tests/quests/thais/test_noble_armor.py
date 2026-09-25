"""Noble Armor Quest / Skjaar Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (2005/2006): below Mount Sternum, Skjaar sells key 3142 for 1000 gold after a test - "redips" (Dago's
# pet), "7" (fingers), "black" (the demons) - then the level-35 gate, the crypt door, "open the chests": noble armor
# and crown helmet (real-map table 10043 / 10042). Skjaar gave tibiaot74's key number 2015 and took the gold without
# checking; the door had no key number; our map had one chest (the crown helmet box is added). Rope. Free, once.
NOBLE_ARMOR = dict(door=(32450, 32044, 8), gate=(32448, 32042, 8), gate_outside=(32448, 32041, 8),
                   chests={(32453, 32048, 8): ("chest", "a noble armor", "noble armor"),
                           (32455, 32048, 8): ("box", "a crown helmet", "crown helmet")},
                   beside=(32454, 32047, 8))


def test_noble_armor_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import npc_pos, strong, talk_to
    from tibia74.route import follow, walk_near, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(PLATINUM, 10)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    walk_near(p, items, world_map, npc_pos("Skjaar"), **ability)
    said = talk_to(p, "Skjaar", "hi", "key", "yes", "yes", "redips", "7", "black", "yes")
    assert any("physical strength" in r for r in said), said               # a knight: the warrior's greeting
    assert any("Here you go." in r for r in said), said
    assert p.wait_for(lambda: carries(p, "copper key"), timeout=3), p.inventory_names()
    assert not carries(p, "platinum coin"), "the 1000 gold were not paid"
    for chest, (what, found, name) in NOBLE_ARMOR["chests"].items():
        walk_next_to(p, items, world_map, chest, keys={3142}, **ability)
        use_map_item(p, items, chest, what)
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        assert p.wait_for(lambda: carries(p, name), timeout=3), p.inventory_names()
        p.sleep(1.1)
    use_map_item(p, items, next(iter(NOBLE_ARMOR["chests"])), "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, keys={3142}, **ability)


def test_skjaar_wants_the_gold(new_player, items, world_map):
    """No 1000 gold, no test and no key."""
    from tibia74 import BACKPACK
    from tibia74.quest import npc_pos, strong, talk_to
    from tibia74.route import walk_near
    p = strong(new_player, THAIS_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    walk_near(p, items, world_map, npc_pos("Skjaar"), level=2000, vocation=4, rope=True)
    said = talk_to(p, "Skjaar", "hi", "key", "yes", "yes", "redips")
    assert any("You don't have enough money." in r for r in said), said
    assert not any("how many fingers" in r for r in said), said


def test_noble_armor_level_door(new_player, items):
    assert_level_door(new_player, items, NOBLE_ARMOR["gate"], NOBLE_ARMOR["gate_outside"], 35)


def test_noble_armor_rules(world_map):
    ability = dict(vocation=4, rope=True)
    assert_no_way(world_map, THAIS_TEMPLE, NOBLE_ARMOR["beside"], level=2000, **ability)                # key 3142
    assert_no_way(world_map, THAIS_TEMPLE, NOBLE_ARMOR["beside"], level=34, keys={3142}, **ability)
    assert_way(world_map, THAIS_TEMPLE, NOBLE_ARMOR["beside"], level=35, keys={3142}, **ability)
    assert_way(world_map, NOBLE_ARMOR["beside"], THAIS_TEMPLE, level=35, keys={3142}, **ability)

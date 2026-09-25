"""Mad Mage Room Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Mad Mage Room Quest (Mintwallin)
# docs/reference-74/quests.md "Mad Mage Room Quest"; TibiaWiki: Key 3620 ("A Drawer in the Mintwallin barracks
# [...] used to lock and unlock all the doors in the Mintwallin prison") gets you to A Prisoner, who gives Key 3666
# for the answer to "The Riddle" (PD-D-KS-P-PD) and 7 apples (his transcript: "Hurray! [...] some apples.
# Interested?" ... "Really, really?" ... "Then take it and get happy - or die, hehe."); past the level-40 gate the
# key opens the reward room: Hat of the Mad (magician hat), stone skin amulet, star amulet (real-map table 10058-
# 10060). The prisoner's script gave the key to anyone; the doors had no key numbers; the containers no ids.
MAD_MAGE = dict(drawer=(32411, 32155, 15), at_prisoner=(32396, 32137, 13), gate=(32544, 32179, 14),
                gate_outside=(32544, 32180, 14), door=(32578, 32197, 15),
                rewards=[((32573, 32200, 14), "box", "a magician hat", "magician hat"),
                         ((32574, 32200, 14), "box", "a stone skin amulet", "stone skin amulet"),
                         ((32577, 32200, 14), "chest", "a star amulet", "star amulet")])
RED_APPLE = 2674


def test_mad_mage_room_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong, talk_to
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(RED_APPLE, 7)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)

    # the prison key from the barracks drawer
    walk_next_to(p, items, world_map, MAD_MAGE["drawer"], **ability)
    use_map_item(p, items, MAD_MAGE["drawer"], "drawers")
    assert p.wait_for(lambda: p.messages("You have found a silver key."), timeout=3), p.text_messages[-3:]

    # A Prisoner, through the bars: the riddle, 7 apples, key 3666
    follow(p, items, world_map, MAD_MAGE["at_prisoner"], keys={3620}, **ability)
    said = talk_to(p, "A Prisoner", "hi", "key", "pd-d-ks-p-pd", "yes", "yes", "yes", "yes")
    assert any("Then take it and get happy" in r for r in said), said
    assert not carries(p, "red apple"), "the apples were not taken"

    # the level-40 gate, door 3666, the three rewards
    keys = dict(keys={3620, 3666}, **ability)
    for container, what, found, name in MAD_MAGE["rewards"]:
        walk_next_to(p, items, world_map, container, **keys)
        use_map_item(p, items, container, what)
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), (container, p.text_messages[-3:])
        assert p.wait_for(lambda: carries(p, name), timeout=3), p.inventory_names()
        p.sleep(1.1)
    use_map_item(p, items, MAD_MAGE["rewards"][-1][0], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **keys)


def test_mad_mage_prisoner_wants_the_answer_and_the_apples(new_player, items, world_map):
    """The key is not for everyone: no answer, no key; the answer without 7 apples: "Get some more apples first!"."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong, talk_to
    from tibia74.route import follow
    prison_key = Item(2088, attributes=bytes([4]) + (3620).to_bytes(2, "little"))       # ATTR_ACTION_ID 3620
    p = strong(new_player, THAIS_TEMPLE, items=[Item(RED_APPLE, 6), prison_key], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    follow(p, items, world_map, MAD_MAGE["at_prisoner"], keys={3620}, **dict(level=2000, vocation=4, rope=True))
    said = talk_to(p, "A Prisoner", "hi", "key", "yes")
    assert any("IF you can solve my riddle" in r for r in said), said
    said = talk_to(p, "A Prisoner", "hi", "pd-d-ks-p-pd", "yes")
    assert any("Get some more apples first!" in r for r in said), said


def test_mad_mage_level_door(new_player, items):
    assert_level_door(new_player, items, MAD_MAGE["gate"], MAD_MAGE["gate_outside"], 40)


def test_mad_mage_rules(world_map):
    ability = dict(vocation=4, rope=True)
    beside = (32572, 32200, 14)
    assert_no_way(world_map, THAIS_TEMPLE, beside, level=2000, keys={3620}, **ability)        # needs key 3666
    assert_no_way(world_map, THAIS_TEMPLE, beside, level=39, keys={3620, 3666}, **ability)    # the level-40 gate
    assert_way(world_map, THAIS_TEMPLE, beside, level=40, keys={3620, 3666}, **ability)
    assert_no_way(world_map, MAD_MAGE["drawer"][:2] + (15,), MAD_MAGE["at_prisoner"], level=2000, **ability)
    assert_way(world_map, THAIS_TEMPLE, MAD_MAGE["at_prisoner"], level=2000, keys={3620}, **ability)

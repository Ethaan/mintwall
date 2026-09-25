"""Present Box Quest + Legion Helmet (Seymour) (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Present Box Quest (Rookgaard)
# docs/reference-74/quests.md "Present Box Quest"; TibiaWiki Present Quest (+ /Spoiler, 2006).
# Goal: the backpack in the chest next to the Bear Room stone switch; its present goes to Seymour for a
# legion helmet (hi, box, yes). Level: listed 2; Seymour mentions the box from level 6. 1 player, free, once.

PRESENT_CHEST = (32149, 32105, 11)            # unique id 52149, next to the stone switch


def test_present_box_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import open_carried, strong, talk_to
    from tibia74.route import walk_near, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)

    walk_next_to(p, items, world_map, PRESENT_CHEST, **ability)
    use_map_item(p, items, PRESENT_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found a backpack."), timeout=3), p.text_messages[-3:]
    found = open_carried(p, items, "backpack")
    assert sorted(i.name for i in found.items) == ["cup", "jug", "plate", "present"], found.items
    p.sleep(1.1)
    use_map_item(p, items, PRESENT_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

    walk_near(p, items, world_map, npc_pos("Seymour"), **ability)
    said = talk_to(p, "Seymour", "hi", "box", "yes")
    assert any("THANK YOU! Here is a helmet that will serve you well." in r for r in said), said
    assert p.wait_for(lambda: carries(p, "legion helmet"), timeout=3), p.inventory_names()
    said = talk_to(p, "Seymour", "hi", "box", "yes")
    if not any("You don't have one!" in r for r in said):
        raise AssertionError(" | ".join(["no HEY answer; speech:"] + [str(x) for x in p.speech[-14:]] + ["messages:"] + [str(x) for x in p.text_messages[-6:]]))


@pytest.mark.parametrize("level, speaks_of_the_box", [(5, False), (6, True)])
def test_seymour_speaks_of_the_box_from_level_6(new_player, level, speaks_of_the_box):
    from tibia74.quest import talk_to
    p = next_to(new_player, npc_pos("Seymour"), level=level, group_id=TESTER_GROUP, storage={30001: 1})
    said = talk_to(p, "Seymour", "hi", "mission")
    assert any("suitable box" in r for r in said) == speaks_of_the_box, said

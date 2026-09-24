"""Quests (docs/reference-74/quests.md, task.md "Quests"): each quest done end to end, the way a player would."""
import pytest

from tibia74.quest import carries, next_to, use_map_item
from tibia74.server import TESTER_GROUP   # monsters cannot attack: the rat sewer killed level 5s


# ----------------------------------------------------------------------------- quest chests (action id 2000)

RAPIER_BOX = (32099, 32198, 9)       # Rookgaard sewer: box, unique id 2384 = the rapier
AMBER_CHEST = (32171, 32197, 7)      # Rookgaard east dock: chest, unique id 20001 holding Amber's notebook


def test_a_quest_chest_gives_its_reward_once_per_player(new_player, items):
    p = next_to(new_player, RAPIER_BOX, level=5, group_id=TESTER_GROUP, storage={30001: 1})
    p.open_container(3)                              # the backpack, so the rapier shows up there
    use_map_item(p, items, RAPIER_BOX, "box")
    assert p.wait_for(lambda: p.messages("You have found a rapier."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "rapier"), timeout=3), p.inventory_names()
    p.sleep(1.1)                                     # the use delay
    use_map_item(p, items, RAPIER_BOX, "box")
    assert p.wait_for(lambda: p.messages("is empty"), timeout=3), p.text_messages[-3:]

    other = next_to(new_player, RAPIER_BOX, level=5, group_id=TESTER_GROUP, storage={30001: 1})
    use_map_item(other, items, RAPIER_BOX, "box")
    assert other.wait_for(lambda: other.messages("You have found a rapier."), timeout=3), \
        f"the second player got nothing: {other.text_messages[-3:]}"


def test_a_quest_chest_gives_what_lies_inside(new_player, items):
    """Unique id 20001 is no item id: the reward is the chest's contents (Amber's notebook)."""
    p = next_to(new_player, AMBER_CHEST, level=5, group_id=TESTER_GROUP, storage={30001: 1})
    use_map_item(p, items, AMBER_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found"), timeout=3), p.text_messages[-3:]
    found = p.messages("You have found")[0]
    assert "book" in found or "notebook" in found, found


# ----------------------------------------------------------------------------- Bear Room Quest (Rookgaard)
# docs/reference-74/quests.md "Bear Room Quest"; TibiaWiki Bear Room Quest/Spoiler and Key 4601.
# Goal: the three bear-room boxes. Level: none (no level door). Players: 1. Free. Once per character.
# Needs: a rope, and a pick (key 4601 lies below the mud south of the big table). Rewards: chain armor,
# brass helmet, 12 arrows + 40 gold coins (real-map chest table).

ROOKGAARD_TEMPLE = (32097, 32219, 7)
BEAR = {
    "mud": (32149, 32110, 11),                # south of the big table: a pick opens it (action id 100)
    "key_chest": (32150, 32111, 12),          # unique id 20003: copper key 4601
    "switch": (32148, 32105, 11),             # action id 52413: takes the stone away
    "stone": (32145, 32101, 11),
    "door": (32145, 32100, 11),               # locked, key 4601
    "inside": (32145, 32099, 11),
    "boxes": {(32141, 32097, 11): ["chain armor"], (32144, 32096, 11): ["brass helmet"],
              (32146, 32097, 11): ["12 arrows", "40 gold coins"]},
}
PICK = 2553


def test_bear_room_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.client import SOUTH  # noqa: F401
    from tibia74.quest import strong
    from tibia74.route import DIRECTIONS, follow, use_tool, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE, items=[Item(PICK)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)

    # the key: a pick on the mud south of the big table opens a hole; the chest below holds key 4601
    walk_next_to(p, items, world_map, BEAR["mud"], **ability)
    use_tool(p, items, "pick", BEAR["mud"])
    assert p.wait_for(lambda: items.by_client[p.tiles[BEAR["mud"]][0].client_id].server_id == 392, timeout=3), \
        f"no hole: {p.tiles.get(BEAR['mud'])} {p.text_messages[-2:]}"
    dx, dy = BEAR["mud"][0] - p.pos[0], BEAR["mud"][1] - p.pos[1]
    p.step(DIRECTIONS[(dx, dy)])
    assert p.wait_for(lambda: p.pos[2] == 12, timeout=3), f"did not drop through the hole: {p.pos}"
    walk_next_to(p, items, world_map, BEAR["key_chest"], **ability)
    use_map_item(p, items, BEAR["key_chest"], "chest")
    assert p.wait_for(lambda: p.messages("You have found a copper key."), timeout=3), p.text_messages[-3:]

    # back up the ladder; the switch north of the big table takes the stone away from the door
    walk_next_to(p, items, world_map, BEAR["switch"], **ability)
    use_map_item(p, items, BEAR["switch"], "switch")
    assert p.wait_for(lambda: len(p.tiles.get(BEAR["stone"], [])) == 1, timeout=3), \
        f"the stone is still there: {p.tiles.get(BEAR['stone'])}"

    # the door opens with key 4601; the bear is killed; the three boxes give their rewards
    follow(p, items, world_map, BEAR["inside"], keys={4601}, open_tiles={BEAR["stone"]}, **ability)
    bear = p.wait_for(lambda: p.nearest("Bear"), timeout=5)
    if bear:
        p.attack(bear.id)
        assert p.wait_for(lambda: bear.id in p.removed_creatures, timeout=30), "the bear is still alive"
        p.attack(0)
    for box, rewards in BEAR["boxes"].items():
        walk_next_to(p, items, world_map, box, keys={4601}, open_tiles={BEAR["stone"]}, **ability)
        before = len(p.text_messages)
        use_map_item(p, items, box, "chest")
        for reward in rewards:
            assert p.wait_for(lambda: any(f"You have found {'a ' if not reward[0].isdigit() else ''}{reward}."
                                          in t for _, t in p.text_messages[before:]), timeout=3), \
                (reward, [t for _, t in p.text_messages[before:]])
        p.sleep(1.1)
    for name in ("chain armor", "brass helmet"):
        assert carries(p, name), f"no {name}: {p.inventory_names()}"

    # once per character
    box = next(iter(BEAR["boxes"]))
    walk_next_to(p, items, world_map, box, keys={4601}, open_tiles={BEAR["stone"]}, **ability)
    use_map_item(p, items, box, "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]


# ----------------------------------------------------------------------------- Present Box Quest (Rookgaard)
# docs/reference-74/quests.md "Present Box Quest"; TibiaWiki Present Quest (+ /Spoiler, 2006).
# Goal: the backpack in the chest next to the Bear Room stone switch; its present goes to Seymour for a
# legion helmet (hi, box, yes). Level: listed 2; Seymour mentions the box from level 6. 1 player, free, once.

PRESENT_CHEST = (32149, 32105, 11)            # unique id 52149, next to the stone switch
SEYMOUR = (32103, 32195, 7)


def test_present_box_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import open_carried, strong, talk_to
    from tibia74.route import walk_next_to
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

    walk_next_to(p, items, world_map, SEYMOUR, **ability)
    said = talk_to(p, "Seymour", "hi", "box", "yes")
    assert any("THANK YOU! Here is a helmet that will serve you well." in r for r in said), said
    assert p.wait_for(lambda: carries(p, "legion helmet"), timeout=3), p.inventory_names()
    said = talk_to(p, "Seymour", "box", "yes")
    assert any("You don't have one!" in r for r in said), said


@pytest.mark.parametrize("level, speaks_of_the_box", [(5, False), (6, True)])
def test_seymour_speaks_of_the_box_from_level_6(new_player, level, speaks_of_the_box):
    from tibia74.quest import talk_to
    p = next_to(new_player, SEYMOUR, level=level, group_id=TESTER_GROUP, storage={30001: 1})
    said = talk_to(p, "Seymour", "hi", "mission")
    assert any("suitable box" in r for r in said) == speaks_of_the_box, said


# ----------------------------------------------------------------------------- Captain Iglues Treasure Quest
# docs/reference-74/quests.md "Captain Iglues Treasure Quest"; TibiaWiki spoiler (2006) + current page.
# Goal: the quest chest below the poison spider tower. Level: none. 1 player, free, once. Needs a rope.
# Reward: 2 salmon (the right chest; the left one refills daily with the letter and 12 salmon). Optional:
# a salmon for Amber (Academy basement) buys a word of orcish ("salmon", "yes").

IGLUE_CHEST = (32039, 32121, 13)              # unique id 52171
AMBER = (32103, 32182, 8)


def test_captain_iglues_treasure_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong, talk_to
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)

    walk_next_to(p, items, world_map, IGLUE_CHEST, **ability)
    use_map_item(p, items, IGLUE_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found 2 salmon."), timeout=3), p.text_messages[-3:]
    p.sleep(1.1)
    use_map_item(p, items, IGLUE_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

    walk_next_to(p, items, world_map, AMBER, **ability)
    said = talk_to(p, "Amber", "hi", "salmon", "yes")
    assert any("Orcs call arrows 'pixo'." in r for r in said), said

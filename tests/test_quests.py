"""Quests (docs/reference-74/quests.md, task.md "Quests"): each quest done end to end, the way a player would."""
import pytest

from tibia74.quest import carries, next_to, npc_pos, use_map_item
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


# ----------------------------------------------------------------------------- Captain Iglues Treasure Quest
# docs/reference-74/quests.md "Captain Iglues Treasure Quest"; TibiaWiki spoiler (2006) + current page.
# Goal: the quest chest below the poison spider tower. Level: none. 1 player, free, once. Needs a rope.
# Reward: 2 salmon (the right chest; the left one refills daily with the letter and 12 salmon). Optional:
# a salmon for Amber (Academy basement) buys a word of orcish ("salmon", "yes").

IGLUE_CHEST = (32039, 32121, 13)              # unique id 52171


def test_captain_iglues_treasure_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong, talk_to
    from tibia74.route import walk_near, walk_next_to
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

    walk_near(p, items, world_map, npc_pos("Amber"), **ability)
    said = talk_to(p, "Amber", "hi", "salmon", "yes")
    assert any("Orcs call arrows 'pixo'." in r for r in said), said


# ----------------------------------------------------------------------------- Combat Knife Quest (Rookgaard)
# docs/reference-74/quests.md: the box in the main sewer (drain in town), guarded by rats. No level, 1 player,
# free, once. Reward: a combat knife (the box's unique id 2404 is the knife).

COMBAT_KNIFE_BOX = (32102, 32235, 8)


def test_combat_knife_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, COMBAT_KNIFE_BOX, level=2000, vocation=4, rope=True)
    use_map_item(p, items, COMBAT_KNIFE_BOX, "chest")
    assert p.wait_for(lambda: p.messages("You have found a combat knife."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "combat knife"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, COMBAT_KNIFE_BOX, "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]


# ----------------------------------------------------------------------------- Doublet Quest (Rookgaard)
# docs/reference-74/quests.md "Doublet Quest"; TibiaWiki Doublet Quest/Spoiler: in the cellar under the stable
# north of Tom's shop, "use the ground (Loose Board) directly west of the sewer grate". 7.4 has no loose-board
# item: the board is the wooden flooring itself (tibiaot74's map: uid 7014 on it), with a barrel standing on it -
# push the barrel aside, then use the floor. No level, 1 player, free, once. Reward: a doublet (unique id 2485).

LOOSE_BOARD = (32084, 32181, 8)


def test_doublet_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, LOOSE_BOARD, level=2000, vocation=4, rope=True)
    use_map_item(p, items, LOOSE_BOARD, "wooden flooring")     # moves the barrel off first
    assert p.wait_for(lambda: p.messages("You have found a doublet."), timeout=3), (p.text_messages[-3:], p.pos, p.tiles.get(LOOSE_BOARD))
    assert p.wait_for(lambda: carries(p, "doublet"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, LOOSE_BOARD, "wooden flooring")
    assert p.wait_for(lambda: p.messages("The wooden flooring is empty."), timeout=3), p.text_messages[-2:]


# ----------------------------------------------------------------------------- Torch Quest (Rookgaard Academy)
# docs/reference-74/quests.md "Torch Quest"; TibiaWiki Torch Quest/Spoiler (removed in 2011, so in 7.4). Basement:
# north through two doors to a wall with a lever; the lever opens the wall; two more doors, a rat, the chest.
# No level, 1 player, free, once. Reward: a torch (the chest's unique id 2050).

ACADEMY_LEVER = (32093, 32174, 8)
ACADEMY_WALL = (32095, 32173, 8)
TORCH_CHEST = (32092, 32162, 8)


def test_torch_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)

    walk_next_to(p, items, world_map, ACADEMY_LEVER, **ability)
    use_map_item(p, items, ACADEMY_LEVER, "switch")
    assert p.wait_for(lambda: len(p.tiles.get(ACADEMY_WALL, [])) == 1, timeout=3), \
        f"the wall is still there: {p.tiles.get(ACADEMY_WALL)} {p.text_messages[-2:]}"
    walk_next_to(p, items, world_map, TORCH_CHEST, open_tiles={ACADEMY_WALL}, **ability)
    use_map_item(p, items, TORCH_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found a torch."), timeout=3), p.text_messages[-3:]
    p.sleep(1.1)
    use_map_item(p, items, TORCH_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]


# ----------------------------------------------------------------------------- Rookgaard Academy training arena
# Not a quest - an Academy feature on the same floors (task.md). Four levers under the blackboards bug / wolf /
# troll / spider; each opens its monster's cage gate one floor down, and the sign says "You have to close the door
# before you can open a new one." (quests/rook_academy_arena.lua; gates as in tibiaot74). The way in is the
# Academy's locked door 4600: Seymour sells that key (Key to Adventure, 5 gp).

ARENA_LEVERS = {"bug": (32088, 32148, 9), "wolf": (32090, 32148, 9), "troll": (32092, 32148, 9),
                "spider": (32094, 32148, 9)}
FRAMEWORK_GATE = 1037


def _gate(lever):
    return (lever[0], lever[1] + 1, 10)


def test_academy_training_arena(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_near, walk_next_to
    from tibia74 import Item
    from tibia74.quest import npc_pos, talk_to
    p = strong(new_player, ROOKGAARD_TEMPLE, items=[Item(2148, 5)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_near(p, items, world_map, npc_pos("Seymour"), level=2000, vocation=4, rope=True)
    said = talk_to(p, "Seymour", "hi", "key", "yes")
    assert p.wait_for(lambda: carries(p, "silver key"), timeout=3), (said, p.inventory_names())
    ability = dict(level=2000, vocation=4, rope=True, keys={4600})
    wolf_lever, bug_lever = ARENA_LEVERS["wolf"], ARENA_LEVERS["bug"]
    gate = _gate(wolf_lever)
    shut = lambda pos: any(i.client_id == FRAMEWORK_GATE for i in p.tile_items(pos))   # noqa: E731

    walk_next_to(p, items, world_map, wolf_lever, **ability)
    use_map_item(p, items, wolf_lever, "switch")
    assert p.wait_for(lambda: gate in p.tiles and not shut(gate), timeout=3), (p.tiles.get(gate), p.text_messages[-2:])

    walk_next_to(p, items, world_map, bug_lever, **ability)
    use_map_item(p, items, bug_lever, "switch")
    assert p.wait_for(lambda: p.messages("Sorry, not possible."), timeout=3), p.text_messages[-2:]
    assert shut(_gate(bug_lever)), "a second gate opened while the wolf's was open"

    # down into the arena and fight the wolf through the open gate
    walk_near(p, items, world_map, (gate[0], gate[1] + 1, 10), radius=1, **ability)
    wolf = p.wait_for(lambda: next((c for c in p.creatures.values() if c.name.lower() == "wolf"), None), timeout=5)
    assert wolf, f"no wolf in view from {p.pos}: {list(p.creatures.values())} gate {p.tiles.get(gate)}"
    p.set_fight_modes(fight=1, chase=1, safe=1)
    p.attack(wolf.id)
    assert p.wait_for(lambda: wolf.id not in p.creatures or p.creatures[wolf.id].health == 0, timeout=20), wolf
    p.set_fight_modes(fight=1, chase=0, safe=1)

    # back up: pull the wolf lever again to shut its gate, then another gate may open
    walk_next_to(p, items, world_map, wolf_lever, **ability)
    use_map_item(p, items, wolf_lever, "switch")
    assert p.wait_for(lambda: shut(gate), timeout=3), (p.tiles.get(gate), p.text_messages[-2:])
    p.sleep(1.1)
    walk_next_to(p, items, world_map, bug_lever, **ability)
    use_map_item(p, items, bug_lever, "switch")
    assert p.wait_for(lambda: not shut(_gate(bug_lever)), timeout=3), p.text_messages[-2:]
    use_map_item(p, items, bug_lever, "switch")               # leave the arena as it was
    assert p.wait_for(lambda: shut(_gate(bug_lever)), timeout=3)


# ----------------------------------------------------------------------------- Dragon Corpse Quest (Rookgaard)
# docs/reference-74/quests.md "Dragon Corpse Quest"; TibiaWiki spoiler. Bear cave east of town: a shovel opens
# the stone pile, a scythe cuts the wheat, run across the fire fields to the dead dragon. No level, 1 player,
# free, once. Reward: a bag with a copper shield and a legion helmet.

DEAD_DRAGON = (32179, 32224, 9)
SHOVEL, SCYTHE = 2554, 2550


def test_dragon_corpse_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import open_carried, strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE, items=[Item(SHOVEL), Item(SCYTHE)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, DEAD_DRAGON, level=2000, vocation=4, rope=True, scythe=True, shovel=True)
    use_map_item(p, items, DEAD_DRAGON, "dead dragon")
    assert p.wait_for(lambda: p.messages("You have found a bag."), timeout=3), p.text_messages[-3:]
    bag = open_carried(p, items, "bag")
    assert sorted(i.name for i in bag.items) == ["copper shield", "legion helmet"], bag.items
    p.sleep(1.1)
    use_map_item(p, items, DEAD_DRAGON, "dead dragon")
    assert p.wait_for(lambda: p.messages("The dead dragon is empty."), timeout=3), p.text_messages[-2:]


# ----------------------------------------------------------------------------- Katana Quest (Rookgaard)
# docs/reference-74/quests.md "Katana Quest"; TibiaWiki Katana Quest/Spoiler (2006 + current). Shovel the grave,
# down past spiders / skeletons, rope up, down again, past the poison fields: key 4603 lies in a body; the door
# 4603 leads down; the hidden lever behind the northern white pillar unlocks the room; the fresh corpses hold
# the katana and the viking helmet. No level, 1 player, free, once. Needs rope + shovel.

QUEST_BODY = 3058                          # the bodies with a reward; the room is full of others (3059 / 3060)
KATANA = {
    "key_body": (32176, 32132, 9),        # dead human, unique id 20002: silver key 4603
    "lever": (32182, 32145, 11),          # action id 52412
    "door": (32177, 32148, 11),           # locked (1209) until the lever
    "katana": (32174, 32149, 11),         # dead human, unique id 2412
    "helmet": (32175, 32145, 11),         # dead human, unique id 2473
}


def test_katana_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE, items=[Item(SHOVEL)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, shovel=True)

    walk_next_to(p, items, world_map, KATANA["key_body"], **ability)
    use_map_item(p, items, KATANA["key_body"], QUEST_BODY)       # under two other bodies: uncovered first
    assert p.wait_for(lambda: p.messages("You have found a silver key."), timeout=3), p.text_messages[-3:]

    walk_next_to(p, items, world_map, KATANA["lever"], keys={4603}, **ability)
    use_map_item(p, items, KATANA["lever"], "switch")
    walk_next_to(p, items, world_map, KATANA["door"], keys={4603}, **ability)
    use_map_item(p, items, KATANA["door"], "closed door")        # unlocked now: it opens
    assert p.wait_for(lambda: not any(getattr(t, "client_id", None) and items.name(items.by_client[t.client_id]
                      .server_id) == "closed door" for t in p.tiles.get(KATANA["door"], [])), timeout=3), \
        f"the door did not open: {p.tiles.get(KATANA['door'])} {p.text_messages[-2:]}"

    for spot, reward in ((KATANA["katana"], "katana"), (KATANA["helmet"], "viking helmet")):
        walk_next_to(p, items, world_map, spot, keys={4603}, open_tiles={KATANA["door"]}, **ability)
        use_map_item(p, items, spot, QUEST_BODY)
        assert p.wait_for(lambda: p.messages(f"You have found a {reward}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    use_map_item(p, items, KATANA["helmet"], QUEST_BODY)
    assert p.wait_for(lambda: p.messages("The dead human is empty."), timeout=3), p.text_messages[-2:]


# ----------------------------------------------------------------------------- Minotaur Hell Quest (Rookgaard)
# docs/reference-74/quests.md "Minotaur Hell Quest"; TibiaWiki spoiler. The main cave north of town, down to
# the minotaur room; three boxes just west of the stairs. No level, 1 player (group advised), free, once.
# Rewards: carlin sword, 4 poison arrows + 10 arrows, fishing rod.

MINOTAUR_HELL_BOXES = {(32124, 32064, 12): ["a carlin sword"], (32127, 32065, 12): ["4 poison arrows", "10 arrows"],
                       (32130, 32066, 12): ["a fishing rod"]}


def test_minotaur_hell_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    for box, rewards in MINOTAUR_HELL_BOXES.items():
        walk_next_to(p, items, world_map, box, level=2000, vocation=4, rope=True)
        before = len(p.text_messages)
        use_map_item(p, items, box, "box")
        for reward in rewards:
            assert p.wait_for(lambda: any(f"You have found {reward}." in t for _, t in p.text_messages[before:]),
                              timeout=3), (reward, [t for _, t in p.text_messages[before:]])
        p.sleep(1.1)
    use_map_item(p, items, next(iter(MINOTAUR_HELL_BOXES)), "box")
    assert p.wait_for(lambda: p.messages("The box is empty."), timeout=3), p.text_messages[-2:]


# ----------------------------------------------------------------------------- Rookgaard trade quests
# docs/reference-74/quests.md: find an item, trade it to an NPC. Chests / palm / flower are once per character.
# Amber's Notebook (free): chest on the east dock -> Amber (hi, book, yes) -> short sword.
# Honey Flower (premium: Lee'Delle is on the premium side): rope up the wasp tower -> flower -> Lee'Delle
#   (hi, honey flower) -> studded legs.
# Banana (free): the palm north-east of town -> Willie (hi, banana, yes) -> studded shield.

HONEY_FLOWER_SPOT = (32005, 32139, 3)
BANANA_PALM = (32172, 32169, 7)


def _trade(p, items, world_map, npc, lines, gives, ability):
    from tibia74.quest import talk_to
    from tibia74.route import walk_near
    from tibia74.quest import npc_pos
    walk_near(p, items, world_map, npc_pos(npc), **ability)          # shopkeepers stand behind a counter
    said = talk_to(p, npc, "hi", *lines)
    assert p.wait_for(lambda: carries(p, gives), timeout=3), (npc, said, p.inventory_names())


@pytest.mark.parametrize("quest", ["amber's notebook", "honey flower", "banana"])
def test_rookgaard_trade_quest(new_player, items, world_map, quest):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    premium = quest == "honey flower"
    p = strong(new_player, ROOKGAARD_TEMPLE, premium_days=30 if premium else 0)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    spot, what, found, npc, lines, gives = {
        "amber's notebook": (AMBER_CHEST, "chest", "You have found a book.", "Amber", ["book", "yes"], "short sword"),
        "honey flower": (HONEY_FLOWER_SPOT, "honey flower", "You have found a honey flower.", "Lee'Delle",
                         ["honey flower"], "studded legs"),
        "banana": (BANANA_PALM, "palm", "You have found a banana.", "Willie", ["banana", "yes"], "studded shield"),
    }[quest]
    walk_next_to(p, items, world_map, spot, **ability)
    use_map_item(p, items, spot, what)
    assert p.wait_for(lambda: p.messages(found), timeout=3), p.text_messages[-3:]
    p.sleep(1.1)
    use_map_item(p, items, spot, what)
    assert p.wait_for(lambda: p.messages("is empty."), timeout=3), f"not once only: {p.text_messages[-2:]}"
    _trade(p, items, world_map, npc, lines, gives, ability)


# The second banana palm, on top of the premium wolf hill (TibiaWiki Studded Shield Quest/Spoiler: "go to the
# premium side and up the wolf hill. Take the 3 boxes to the flat part and jump up to the Bananapalm there"). The
# flat part is floor 6; three boxes on a tile there and a step north lands on the palm's plateau (floor 5). It is
# the same quest as the north-east palm (Tibiantis.life): one banana per character between them.

WOLF_HILL_PALM = (31983, 32193, 5)
WOLF_HILL_STACK = (31983, 32195, 6)            # the flat part, south of the plateau
BOX = 1738


def test_banana_quest_wolf_hill_palm(new_player, items, world_map):
    from tibia74 import BACKPACK, NORTH, SOUTH, Item
    from tibia74.client import GameClient
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE, premium_days=30, items=[Item(BOX), Item(BOX), Item(BOX)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    follow(p, items, world_map, WOLF_HILL_STACK, **ability)
    for _ in range(3):                                            # the boxes onto our own tile
        cid, c = next((cid, c) for cid, c in p.containers.items() if any(i.client_id == BOX for i in c.items))
        slot = next(n for n, i in enumerate(c.items) if i.client_id == BOX)
        before = len(p.tile_items(WOLF_HILL_STACK))
        p.move_item(GameClient.container_pos(cid, slot), BOX, slot, WOLF_HILL_STACK)
        assert p.wait_for(lambda: len(p.tile_items(WOLF_HILL_STACK)) > before, timeout=3), p.text_messages[-2:]
    assert p.step(NORTH), f"could not climb: {p.pos} {p.text_messages[-2:]}"
    assert p.pos == (31983, 32194, 5), p.pos

    use_map_item(p, items, WOLF_HILL_PALM, "palm")
    assert p.wait_for(lambda: p.messages("You have found a banana."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "banana"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, WOLF_HILL_PALM, "palm")
    assert p.wait_for(lambda: p.messages("The palm is empty."), timeout=3), p.text_messages[-2:]

    # down onto the boxes again, and the north-east palm has nothing left for this character
    assert p.step(SOUTH), f"could not get down: {p.pos} {p.text_messages[-2:]}"
    assert p.pos == WOLF_HILL_STACK, p.pos
    before = len(p.messages("The palm is empty."))
    walk_next_to(p, items, world_map, BANANA_PALM, **ability)
    use_map_item(p, items, BANANA_PALM, "palm")
    assert p.wait_for(lambda: len(p.messages("The palm is empty.")) > before, timeout=3), p.text_messages[-2:]


# ----------------------------------------------------------------------------- Goblin Temple + Antidote Rune (Rookgaard)
# docs/reference-74/quests.md: premium side, through the troll cave (shovel the pile of rocks), down past the
# goblins, up the stairs: two chests (50 gp, 5 small stones, sandals / pan, 4 snowballs, milk). The pan goes
# to Billy (hi, pan, yes) for an antidote rune (Antidote Rune Quest). Premium, no level, 1 player, once.

GOBLIN_CHESTS = {(31973, 32209, 12): ["sandals", "5 small stones", "50 gold coins"],
                 (31977, 32209, 12): ["a pan", "4 snowballs", "a vial"]}


def test_goblin_temple_and_antidote_rune_quests(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import npc_pos, strong, talk_to
    from tibia74.route import walk_near, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE, premium_days=30, items=[Item(SHOVEL)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, shovel=True)
    for chest, rewards in GOBLIN_CHESTS.items():
        walk_next_to(p, items, world_map, chest, **ability)
        before = len(p.text_messages)
        use_map_item(p, items, chest, "chest")
        for reward in rewards:
            assert p.wait_for(lambda: any(f"You have found {reward}." in t for _, t in p.text_messages[before:]),
                              timeout=3), (reward, [t for _, t in p.text_messages[before:]])
        p.sleep(1.1)
    use_map_item(p, items, next(iter(GOBLIN_CHESTS)), "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

    walk_near(p, items, world_map, npc_pos("Billy"), **ability)
    said = talk_to(p, "Billy", "hi", "pan", "yes")
    assert p.wait_for(lambda: carries(p, "antidote rune"), timeout=3), (said, p.inventory_names())


# ----------------------------------------------------------------------------- Pick Quest (Rookgaard)
# docs/reference-74/quests.md "Small Axe Quest / Pick Quest": a small axe - once from the coffin in the premium
# skeleton cave (below), or from spots that respawn daily: the box in the orc cave (-2) and a body in the Katana
# cave - goes to Al Dee (hi, pick, yes) for a pick (needed for the Bear Room). Free, no level.

ORC_CAVE_BOX = (32080, 32121, 10)             # not a quest box: its small axe and arrow come back every day


def test_pick_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import open_map_container, strong, take, talk_to
    from tibia74.route import walk_near, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    walk_next_to(p, items, world_map, ORC_CAVE_BOX, **ability)
    box = open_map_container(p, items, ORC_CAVE_BOX, "box")
    take(p, items, box, "small axe")
    walk_near(p, items, world_map, npc_pos("Al Dee"), **ability)
    said = talk_to(p, "Al Dee", "hi", "pick", "yes")
    assert p.wait_for(lambda: carries(p, "pick"), timeout=3), (said, p.inventory_names())
    assert not carries(p, "small axe"), "Al Dee kept no small axe"


# ----------------------------------------------------------------------------- Small Axe Quest (Rookgaard premium)
# docs/reference-74/quests.md "Small Axe Quest": the right-hand coffin of the pair in the premium skeleton cave
# (TibiaWiki; tibiaot74's map: uid 7026 on the coffin at 31984,32246,10); the way down is dug open with a shovel.
# Premium, no level, once (Tibiantis quest id). Reward: a small axe (unique id 2559).

SMALL_AXE_COFFIN = (31984, 32246, 10)


def test_small_axe_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    from tibia74 import Item
    p = strong(new_player, ROOKGAARD_TEMPLE, premium_days=30, items=[Item(SHOVEL)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, SMALL_AXE_COFFIN, level=2000, vocation=4, rope=True, shovel=True)
    use_map_item(p, items, SMALL_AXE_COFFIN, "wooden coffin")
    assert p.wait_for(lambda: p.messages("You have found a small axe."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "small axe"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, SMALL_AXE_COFFIN, "wooden coffin")
    assert p.wait_for(lambda: p.messages("The wooden coffin is empty."), timeout=3), p.text_messages[-2:]

"""Bear Room Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


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

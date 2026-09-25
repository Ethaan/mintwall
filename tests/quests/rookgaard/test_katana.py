"""Katana Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


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
    from tibia74.route import walk_next_to
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

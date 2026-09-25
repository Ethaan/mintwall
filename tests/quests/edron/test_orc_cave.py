"""Edron Orc Cave quests: Shaman Treasure, Poison Daggers, Dark Armor, Barbarian Axe, Berserker Treasure
(docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki: "it is highly recommended that you get a team together and complete all of the quests in this cave at one
# time" - one trip here too. Shovel and rope; no level. The hole at the entrance drops into a pocket closed by a stone:
# the lever next to it (quests/edron_orc_cave_lever.lua) takes it away. The reward containers were missing on our
# map: placed where tibiaot74 has them, real-map table uids and contents (quests/system.lua).
ORC_CAVE = dict(lever=(33172, 31896, 8), stone=(33171, 31897, 8), pocket=(33173, 31898, 8),
                rewards=[((33127, 31885, 9), "dead skeleton", ["a blank rune"]),                  # Shaman Treasure: 3
                         ((33155, 31880, 11), "chest", ["a backpack"]),                          # Poison Daggers
                         ((33176, 31871, 12), "dead skeleton", ["a dark armor"]),                # Dark Armor
                         ((33185, 31945, 11), "box", ["a barbarian axe", "a scimitar"]),         # Barbarian Axe
                         ((33199, 31923, 11), "box", ["3 white pearls", "100 gold coins",        # Berserker Treasure
                                                     "75 gold coins"])])
STONE = 1285


def test_orc_cave_quests(new_player, items, world_map):
    from tibia74 import Item
    from tibia74.quest import open_carried, way
    from tibia74.route import follow, walk_next_to
    O = ORC_CAVE
    p = edron_player(new_player, items=[Item(SHOVEL)])
    ability = dict(level=1, rope=True, shovel=True)

    # into the pocket; the stone, the lever
    follow(p, items, world_map, O["pocket"], **ability)
    stone_on = lambda: any(i.client_id == STONE for i in p.tile_items(O["stone"]))   # noqa: E731
    assert p.wait_for(stone_on, timeout=3), p.tiles.get(O["stone"])
    assert way(world_map, O["pocket"], O["rewards"][0][0], **ability) is None     # the stone closes the cave
    use_map_item(p, items, O["lever"], "switch")
    assert p.wait_for(lambda: not stone_on(), timeout=3), p.tiles.get(O["stone"])
    opened = dict(ability, open_tiles={O["stone"]})

    # the five rewards, each once
    for pos, what, found in O["rewards"]:
        walk_next_to(p, items, world_map, pos, **opened)
        use_map_item(p, items, pos, what)
        for text in found:
            assert p.wait_for(lambda: p.messages(f"You have found {text}."), timeout=3), p.text_messages[-4:]
        p.sleep(1.1)
        before = len(p.messages("is empty."))
        use_map_item(p, items, pos, what)
        assert p.wait_for(lambda: len(p.messages("is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    assert len(p.messages("You have found a blank rune.")) == 3, p.text_messages
    assert sum(1 for i in p.all_items() if i.name == "blank rune") == 3, p.inventory_names()
    for name in ("dark armor", "barbarian axe", "scimitar", "white pearl"):
        assert carries(p, name), p.inventory_names()
    backpack = open_carried(p, items, "backpack")
    assert p.wait_for(lambda: sorted(i.name for i in backpack.items) ==
                      ["poison arrow", "poison dagger", "poison dagger"], timeout=3), backpack.items
    assert next(i for i in backpack.items if i.name == "poison arrow").count == 30, backpack.items

    follow(p, items, world_map, EDRON_TEMPLE, **opened)


def test_orc_cave_rules(world_map):
    O = ORC_CAVE
    opened = {O["stone"]}
    for pos, _, _ in O["rewards"]:
        beside = next((pos[0] + dx, pos[1] + dy, pos[2]) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                      if (dx or dy) and world_map.walkable((pos[0] + dx, pos[1] + dy, pos[2])))
        assert_no_way(world_map, EDRON_TEMPLE, beside, level=1, rope=True, shovel=True)              # the stone
        assert_way(world_map, EDRON_TEMPLE, beside, level=1, rope=True, open_tiles=opened)          # no level
        assert_way(world_map, beside, EDRON_TEMPLE, level=1, rope=True, shovel=True, open_tiles=opened)
        assert_no_way(world_map, beside, EDRON_TEMPLE, level=1, shovel=True, open_tiles=opened)     # a rope
    assert_way(world_map, EDRON_TEMPLE, O["pocket"], level=1, rope=True)                             # the lever

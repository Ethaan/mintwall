"""Rookgaard trade quests (Amber's notebook, honey flower, banana) (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


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

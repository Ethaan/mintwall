"""The White Raven Monastery Quest, part 1: the Family Brooch, Dalbrect, the Isle of the Kings (docs/reference-74/quests.md).
Part 2 (Costello, the Monk's Diary, the Blessed Ankh) comes with the Banshee Quest - it shares its switches."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006 spoiler: into the Ghostlands through the hole under the wall west of Carlin (a shovel; a rope back
# up), the abandoned house to the south and down, south and down the stairs, east, the south room and up: "Simply use
# the head of the top coffin to find the Family Brooch". Dalbrect (transcripts): "brooch", "yes", "yes" - he keeps it
# and is your friend; "passage", "yes": the Isle of the Kings for 10 gp. Captain Jack on the Isle sails back for 20 gp
# (Dalbrect's 2006 infobox). Our map: the coffin had no quest id (real-map table uid 4506 = the brooch).
WHITE_RAVEN = dict(coffin=(32248, 31866, 8), beside=(32250, 31866, 8),
                   isle_deck=(32188, 31958, 7), carlin_deck=(32205, 31756, 7))
BROOCH_FRIEND = "Thank you! I shall consider you my friend from now on!"
NOT_A_FRIEND = "I dare not anger the monks by bringing travellers there without their permission."


def _gold(p):
    return sum({"gold coin": 1, "platinum coin": 100}.get(i.name, 0) * max(i.count, 1) for i in p.all_items())


def test_white_raven_family_brooch_and_isle(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import npc_pos, strong, talk_to
    from tibia74.route import follow, walk_near, walk_next_to
    W = WHITE_RAVEN
    p = strong(new_player, CARLIN_TEMPLE, items=[Item(SHOVEL), Item(2148, 50)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=1, rope=True, shovel=True)

    walk_next_to(p, items, world_map, W["coffin"], **ability)         # the shovel hole, the house, the stairs
    use_map_item(p, items, W["coffin"], "wooden coffin")
    assert p.wait_for(lambda: p.messages("You have found a family brooch."), timeout=3), p.text_messages[-3:]
    assert carries(p, "family brooch"), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, W["coffin"], "wooden coffin")               # once per character
    assert p.wait_for(lambda: p.messages("The wooden coffin is empty."), timeout=3), p.text_messages[-2:]

    walk_near(p, items, world_map, npc_pos("Dalbrect"), **ability)     # back up the rope, to his hut
    said = talk_to(p, "Dalbrect", "hi", "passage")
    assert any(NOT_A_FRIEND in s for s in said), said
    said = talk_to(p, "Dalbrect", "hi", "brooch", "yes", "yes")
    assert any(BROOCH_FRIEND in s for s in said), said
    assert p.wait_for(lambda: not carries(p, "family brooch"), timeout=3), "Dalbrect did not keep the brooch"

    before = _gold(p)
    said = talk_to(p, "Dalbrect", "hi", "passage", "yes")
    assert p.wait_for(lambda: p.pos == W["isle_deck"], timeout=5), (p.pos, said)
    assert p.wait_for(lambda: _gold(p) == before - 10, timeout=3), (before, _gold(p))

    said = talk_to(p, "Captain Jack", "hi", "tibia", "yes")            # and back, 20 gp
    assert p.wait_for(lambda: p.pos == W["carlin_deck"], timeout=5), (p.pos, said)
    assert p.wait_for(lambda: _gold(p) == before - 30, timeout=3), (before, _gold(p))
    follow(p, items, world_map, CARLIN_TEMPLE, **ability)


def test_dalbrect_wants_the_brooch_first(new_player):
    """Without the brooch: no friendship, no passage."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import next_to, npc_pos, talk_to
    p = next_to(new_player, npc_pos("Dalbrect"), group_id=TESTER_GROUP, storage={30001: 1},
                inventory={BACKPACK: Item(1988, contents=[Item(2148, 50)])})
    said = talk_to(p, "Dalbrect", "hi", "brooch", "yes")
    assert any("I am too poor to be interested in jewelry." in s for s in said), said
    said = talk_to(p, "Dalbrect", "hi", "passage", "yes")
    assert any(NOT_A_FRIEND in s for s in said), said
    p.sleep(1)
    assert p.pos[2] == 7 and p.pos[1] < 31900, f"sailed to the Isle without being his friend: {p.pos}"


def test_dalbrect_friend_needs_the_fare(new_player):
    from tibia74.quest import next_to, npc_pos, talk_to
    p = next_to(new_player, npc_pos("Dalbrect"), group_id=TESTER_GROUP, storage={30001: 1, 99999: 1})
    said = talk_to(p, "Dalbrect", "hi", "passage", "yes")
    assert any("You don't have enough money." in s for s in said), said


def test_white_raven_rules(world_map):
    W = WHITE_RAVEN
    assert_way(world_map, CARLIN_TEMPLE, W["beside"], level=1, rope=True, shovel=True)        # no level
    assert_no_way(world_map, CARLIN_TEMPLE, W["beside"], level=1, rope=True)                   # the shovel hole
    assert_way(world_map, W["beside"], CARLIN_TEMPLE, level=1, rope=True, shovel=True)
    assert_no_way(world_map, W["beside"], CARLIN_TEMPLE, level=1, shovel=True)                 # a rope back up
    assert_no_way(world_map, CARLIN_TEMPLE, W["isle_deck"], level=1, rope=True, shovel=True)   # the Isle: by boat

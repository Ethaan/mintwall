"""Edron Goblin Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki pre-8.0: down the drain in the castle, "follow the only path" up to the grassy area, the goblin hill's
# hole, then the holes to the throne room: "The reward is in two chests in the throne room to the north" - a steel
# shield and a silver amulet. No level; a rope. The chests were missing on our map: placed at tibiaot74's spots next to
# the throne, real-map table uids 1028 / 1029 (quests/system.lua). Back: the pitfall in the grassy area drops onto the
# rope spots of the way in (movements/scripts/pitfall.lua).
GOBLIN = dict(chests=[((33095, 31800, 10), "a steel shield"), ((33095, 31801, 10), "a silver amulet")],
              beside=(33096, 31800, 10), pitfall=(33128, 31810, 7), next_to_pitfall=(33128, 31811, 7))


def test_edron_goblin_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    G = GOBLIN
    p = edron_player(new_player)
    ability = dict(level=1, rope=True)
    for chest, found in G["chests"]:
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    assert carries(p, "steel shield") and carries(p, "silver amulet"), p.inventory_names()
    for chest, _ in G["chests"]:                                          # once each
        before = len(p.messages("The chest is empty."))
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: len(p.messages("The chest is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)

    # back through the grassy area: the grass above the rope spot is a pitfall
    follow(p, items, world_map, G["next_to_pitfall"], **ability)
    step_onto(p, G["pitfall"])
    below = (G["pitfall"][0], G["pitfall"][1], G["pitfall"][2] + 1)
    assert p.wait_for(lambda: p.pos == below, timeout=3), p.pos
    follow(p, items, world_map, EDRON_TEMPLE, **ability)


def test_edron_goblin_rules(world_map):
    G = GOBLIN
    assert_way(world_map, EDRON_TEMPLE, G["beside"], level=1, rope=True)                  # no level
    assert_no_way(world_map, EDRON_TEMPLE, G["beside"], level=1)                          # a rope
    assert_way(world_map, G["beside"], EDRON_TEMPLE, level=1, rope=True)                  # out by the pitfall
    assert_no_way(world_map, G["beside"], EDRON_TEMPLE, level=1)

"""Vampire Shield Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki pre-8.0: down the Hero Cave holes, south and east, "Take the south path and down the stairs" to the
# warlock's room (the Temple of Xayepocax); "Enter the level 70 gate of expertise, and retrieve your reward of a
# Vampire Shield and a Dragon Lance from the chests. There is also a quest box outside of the level 70 door" (strange
# symbol, black pearl, mysterious fetish). Two gates lead into the one reward room. Rewards: quests/system.lua
# (real-map table uids 1016, 1017, 1032; the box was missing - placed at tibiaot74's spot).
VAMPIRE = dict(gates=[(33190, 31684, 14), (33195, 31684, 14)], gate_outside=(33190, 31683, 14),
               box=(33188, 31682, 14), inside=(33190, 31687, 14),
               chests=[((33189, 31688, 14), ["a dragon lance"]), ((33195, 31688, 14), ["a vampire shield"])])
BOX_FOUND = ["a strange symbol", "a black pearl", "a mysterious fetish"]


def test_vampire_shield_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    V = VAMPIRE
    p = edron_player(new_player)
    ability = dict(level=2000, vocation=4, rope=True)
    # the box outside the gate, then the two chests behind it; each once
    targets = [(V["box"], "box", BOX_FOUND)] + [(pos, "chest", found) for pos, found in V["chests"]]
    for pos, what, found in targets:
        walk_next_to(p, items, world_map, pos, **ability)
        use_map_item(p, items, pos, what)
        for text in found:
            assert p.wait_for(lambda: p.messages(f"You have found {text}."), timeout=3), p.text_messages[-4:]
        p.sleep(1.1)
    for name in ("strange symbol", "black pearl", "mysterious fetish", "dragon lance", "vampire shield"):
        assert carries(p, name), p.inventory_names()
    for pos, what, _ in targets:
        walk_next_to(p, items, world_map, pos, **ability)
        before = len(p.messages(f"The {what} is empty."))
        use_map_item(p, items, pos, what)
        assert p.wait_for(lambda: len(p.messages(f"The {what} is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    follow(p, items, world_map, EDRON_TEMPLE, **ability)                 # out: back up the holes with a rope


def test_vampire_shield_level_doors(new_player, items):
    assert_level_door(new_player, items, VAMPIRE["gates"][0], VAMPIRE["gate_outside"], 70)
    assert_level_door(new_player, items, VAMPIRE["gates"][1], (33195, 31683, 14), 70)


def test_vampire_shield_rules(world_map):
    V = VAMPIRE
    assert_way(world_map, EDRON_TEMPLE, V["inside"], level=70, rope=True)
    assert_no_way(world_map, EDRON_TEMPLE, V["inside"], level=69, rope=True)                  # the gates
    assert_way(world_map, EDRON_TEMPLE, (33189, 31682, 14), level=8, rope=True)             # the box: no level
    assert_way(world_map, V["inside"], EDRON_TEMPLE, level=70, rope=True)                    # out: a rope
    assert_no_way(world_map, V["inside"], EDRON_TEMPLE, level=70)

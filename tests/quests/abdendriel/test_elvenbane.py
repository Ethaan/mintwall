"""Elvenbane Quest, Ab'Dendriel (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: "Drop down the hole surrounded by four stones", north and west into the middle tower, up four floors:
# "The final floor contains 2 quest chests and 2 quest drawers" - morning star, dwarven shield, manafluid, blank rune,
# spellbook, 2 small diamonds, 100 gp. Our map: the hole was a closed stone pile (opened - decided with the user
# 2026-09-26: the wikis' open hole), the chests and drawers were missing (placed at tibiaot74's spots, real-map uids).
ELVENBANE = dict(hole=(32579, 31679, 7), top=(32590, 31645, 3),
                 things=[((32588, 31644, 3), "drawers", ["You have found a morning star."]),
                         ((32588, 31645, 3), "drawers", ["You have found a dwarven shield."]),
                         ((32590, 31647, 3), "chest", ["You have found a vial of manafluid.", "You have found a blank rune."]),
                         ((32591, 31647, 3), "chest", ["You have found a bag."])])


def test_elvenbane_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import open_carried, strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, ABDENDRIEL_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=1, rope=True)
    for pos, what, found in ELVENBANE["things"]:
        walk_next_to(p, items, world_map, pos, **ability)
        before = len(p.text_messages)
        use_map_item(p, items, pos, what)
        got = lambda: sorted(t for _, t in p.text_messages[before:] if t.startswith("You have found"))  # noqa: E731
        assert p.wait_for(lambda: got() == sorted(found), timeout=3), got()
        p.sleep(1.1)
        use_map_item(p, items, pos, what)
        assert p.wait_for(lambda: p.messages(f"The {what} is empty."), timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    bag = open_carried(p, items, "bag")
    assert p.wait_for(lambda: sorted(i.name for i in bag.items) == ["gold coin", "small diamond", "spellbook"],
                      timeout=3), bag.items
    follow(p, items, world_map, ABDENDRIEL_TEMPLE, **ability)            # rope back up the hole


def test_elvenbane_rules(world_map):
    E = ELVENBANE
    assert_way(world_map, ABDENDRIEL_TEMPLE, E["top"], level=1)                  # no level, no shovel: an open hole
    assert_no_way(world_map, E["top"], ABDENDRIEL_TEMPLE, level=1)               # a rope back up
    assert_way(world_map, E["top"], ABDENDRIEL_TEMPLE, level=1, rope=True)

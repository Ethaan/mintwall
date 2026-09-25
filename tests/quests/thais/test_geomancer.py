"""Geomancer Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (2006): down through Mount Sternum past the Graveyard of the Doomed and the dwarf soldiers, "The quest box
# is on the east side of the room, behind Dwarf Guards and a Dwarf Geomancer". The box was missing on our map (placed
# at tibiaot74's spot). Real-map table [3617]: small sapphire, small diamond, dwarven ring. Rope. Free, once.
GEOMANCER = dict(box=(32456, 32008, 13), beside=(32455, 32008, 13))


def test_geomancer_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    walk_next_to(p, items, world_map, GEOMANCER["box"], **ability)
    before = len(p.text_messages)
    use_map_item(p, items, GEOMANCER["box"], "box")
    found = lambda: sorted(t for _, t in p.text_messages[before:] if t.startswith("You have found"))  # noqa: E731
    assert p.wait_for(lambda: found() == ["You have found a dwarven ring.", "You have found a small diamond.",
                                          "You have found a small sapphire."], timeout=3), found()
    p.sleep(1.1)
    use_map_item(p, items, GEOMANCER["box"], "box")
    assert p.wait_for(lambda: p.messages("The box is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)


def test_geomancer_rules(world_map):
    assert_way(world_map, THAIS_TEMPLE, GEOMANCER["beside"], level=1)
    assert_way(world_map, GEOMANCER["beside"], THAIS_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, GEOMANCER["beside"], THAIS_TEMPLE, level=1)                      # a rope back up

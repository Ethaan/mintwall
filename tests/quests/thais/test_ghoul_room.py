"""Ghoul Room Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Ghoul Room Quest (Ancient Temple)
# docs/reference-74/quests.md "Ghoul Room Quest"; TibiaWiki (2006, current): in the skeleton room "Open a dead
# skeleton in the South-East of the room - you will get Key 3600"; "Use the well in that room to go down it. Kill 3
# Ghouls, unlock the door with Key 3600, get your reward". Real-map table [3601] key 3600, [3602] garlic necklace +
# club ring. The skeleton was missing (placed at tibiaot74's spot), the door had no key number, the well no script.
GHOUL_ROOM = dict(skeleton=(32509, 32181, 13), chest=(32500, 32176, 14), beside=(32501, 32176, 14))


def test_ghoul_room_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    walk_next_to(p, items, world_map, GHOUL_ROOM["skeleton"], **ability)
    use_map_item(p, items, GHOUL_ROOM["skeleton"], "dead skeleton")
    assert p.wait_for(lambda: p.messages("You have found a silver key."), timeout=3), p.text_messages[-3:]
    walk_next_to(p, items, world_map, GHOUL_ROOM["chest"], keys={3600}, **ability)   # the well, the ghouls, the door
    before = len(p.text_messages)
    use_map_item(p, items, GHOUL_ROOM["chest"], "chest")
    found = lambda: sorted(t for _, t in p.text_messages[before:] if t.startswith("You have found"))  # noqa: E731
    assert p.wait_for(lambda: found() == ["You have found a club ring.", "You have found a garlic necklace."],
                      timeout=3), found()
    p.sleep(1.1)
    use_map_item(p, items, GHOUL_ROOM["chest"], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, keys={3600}, **ability)


def test_ghoul_room_rules(world_map):
    assert_no_way(world_map, THAIS_TEMPLE, GHOUL_ROOM["beside"], level=1, rope=True)
    assert_way(world_map, THAIS_TEMPLE, GHOUL_ROOM["beside"], level=1, rope=True, keys={3600})
    assert_way(world_map, GHOUL_ROOM["beside"], THAIS_TEMPLE, level=1, rope=True, keys={3600})

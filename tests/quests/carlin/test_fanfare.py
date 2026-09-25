"""Fanfare Quest, Carlin (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: "get Key 3520 from the box in the north-east corner of the big room" of the building north-west of
# the boat; into the crypt at the south end of the cemetery, "Open the door to the west and look for a hole", down and
# north through the trolls, "Use the chest to receive the Fanfare". Current wiki: Key 3520 and a rope (the hole lands
# on a rope spot - the way back). Real-map table [3520] bone key 3520, [4507] fanfare. Our map: the box had no quest
# id, the crypt door no key number, the chest was missing (placed at tibiaot74's spot).
FANFARE = dict(box=(32376, 31802, 7), door=(32400, 31788, 8), chest=(32390, 31769, 9), beside=(32390, 31770, 9))


def test_fanfare_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    F = FANFARE
    p = strong(new_player, CARLIN_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=1, rope=True)
    walk_next_to(p, items, world_map, F["box"], **ability)
    use_map_item(p, items, F["box"], "box")
    assert p.wait_for(lambda: p.messages("You have found a bone key."), timeout=3), p.text_messages[-3:]
    p.sleep(1.1)
    use_map_item(p, items, F["box"], "box")                                 # one key per character
    assert p.wait_for(lambda: p.messages("The box is empty."), timeout=3), p.text_messages[-2:]

    walk_next_to(p, items, world_map, F["chest"], keys={3520}, **ability)  # the crypt door, the hole, the trolls
    use_map_item(p, items, F["chest"], "chest")
    assert p.wait_for(lambda: p.messages("You have found a fanfare."), timeout=3), p.text_messages[-3:]
    assert carries(p, "fanfare"), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, F["chest"], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, CARLIN_TEMPLE, keys={3520}, **ability)     # rope up the hole


def test_fanfare_rules(world_map):
    F = FANFARE
    assert_way(world_map, CARLIN_TEMPLE, F["beside"], level=1, keys={3520})                   # no level
    assert_no_way(world_map, CARLIN_TEMPLE, F["beside"], level=1, rope=True)                   # the key
    assert_way(world_map, F["beside"], CARLIN_TEMPLE, level=1, rope=True, keys={3520})        # out: a rope
    assert_no_way(world_map, F["beside"], CARLIN_TEMPLE, level=1, keys={3520})

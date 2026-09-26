"""Emperor's Cookies Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: key 3800 in a chest at the end of the secret passage north of Emperor Kruzak's room, then "open the
# door of the small room in the emperor's chamber with the key. In the chest [...] 7 and 20 Cookies and Key 3801", then
# "at the barracks you can open the door with Key 3801, in the chest will be the key, Key 3802". Our map had no key
# numbers on the doors, no quest chests, and the way into the chambers shut by three locked doors with no key number
# (tibiaot74 has plain doors there).
COOKIES = dict(
    chest_3800=(32605, 31908, 3), door_3800=(32645, 31906, 3), chest_3801=(32648, 31905, 3),
    door_3801=(32600, 31926, 6), chest_3802=(32599, 31923, 6),
)


def test_emperors_cookies_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import open_carried, strong
    from tibia74.route import walk_next_to
    C = COOKIES
    p = strong(new_player, KAZORDOON_TEMPLE, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    keys = set()
    ability = lambda: dict(level=2000, rope=True, keys=keys)       # noqa: E731

    walk_next_to(p, items, world_map, C["chest_3800"], **ability())
    use_map_item(p, items, C["chest_3800"], "chest")
    assert p.wait_for(lambda: p.messages("You have found a copper key."), timeout=3), p.text_messages[-3:]
    keys.add(3800)

    walk_next_to(p, items, world_map, C["chest_3801"], **ability())
    use_map_item(p, items, C["chest_3801"], "chest")
    assert p.wait_for(lambda: p.messages("You have found a bag."), timeout=3), p.text_messages[-3:]
    bag = open_carried(p, items, "bag")
    names = sorted((items.name(items.by_client[i.client_id].server_id), i.count) for i in bag.items)
    assert [n for n, _ in names] == ["cookie", "cookie", "copper key"], names
    assert sorted(c for n, c in names if n == "cookie") == [7, 20], names
    keys.add(3801)

    walk_next_to(p, items, world_map, C["chest_3802"], **ability())
    use_map_item(p, items, C["chest_3802"], "chest")
    assert p.wait_for(lambda: len(p.messages("You have found a copper key.")) >= 2, timeout=3), p.text_messages[-3:]
    before = len(p.text_messages)
    p.sleep(1.1)
    use_map_item(p, items, C["chest_3802"], "chest")
    assert p.wait_for(lambda: any("empty" in t for _, t in p.text_messages[before:]), timeout=3), p.text_messages[-3:]


def test_emperors_cookies_rules(world_map):
    C = COOKIES
    beside_3801, beside_3802 = (32647, 31905, 3), (32599, 31924, 6)
    assert_way(world_map, KAZORDOON_TEMPLE, (32605, 31907, 3), level=1, rope=True)
    assert_no_way(world_map, KAZORDOON_TEMPLE, beside_3801, level=1, rope=True)
    assert_way(world_map, KAZORDOON_TEMPLE, beside_3801, level=1, rope=True, keys={3800})
    assert_no_way(world_map, KAZORDOON_TEMPLE, beside_3802, level=1, rope=True, keys={3800})
    assert_way(world_map, KAZORDOON_TEMPLE, beside_3802, level=1, rope=True, keys={3801})


def test_key_3802_opens_the_dwacatra_prison(world_map):
    """Key 3802 "is needed to open Dwacatra Prison" (TibiaWiki 2006): the cell doors 32602-32603,31962/31966/31975,14
    (tibiaot74's key doors)."""
    cell = (32602, 31963, 14)
    assert_no_way(world_map, KAZORDOON_TEMPLE, cell, level=100, rope=True, floors=9)
    assert_way(world_map, KAZORDOON_TEMPLE, cell, level=100, rope=True, floors=9, keys={3802})

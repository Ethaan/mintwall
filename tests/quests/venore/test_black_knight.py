"""Black Knight Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: key 5010 in a dead tree west of Villa Scapula (the current wiki: two trees - one key per character
# between them), the basement door, down past the bonelords, the level-50 gate, the teleport up into the Black
# Knight's round room: the two southern trees give the crown shield and the crown armor (decided with the user over
# Tibiantis). Our map had the key door without a key number and nothing scripted.
BK = dict(key_trees=[(32813, 31964, 7), (32800, 31959, 7)], door=(32824, 31969, 8), gate=(32874, 31974, 12),
          outside=(32874, 31975, 12), shield=(32868, 31955, 11), armor=(32880, 31955, 11))


def test_black_knight_quest(new_player, items, world_map):
    p = venore_player(new_player)
    keys = set()
    ability = lambda: dict(level=2000, rope=True, keys=keys, floors=9)          # noqa: E731
    collect(p, items, world_map, BK["key_trees"][0], "dead tree", ["a silver key"], **ability())
    keys.add(5010)
    from tibia74.route import walk_next_to
    walk_next_to(p, items, world_map, BK["key_trees"][1], **ability())       # the other tree: one key per character
    before = len(p.text_messages)
    use_map_item(p, items, BK["key_trees"][1], "dead tree")
    assert p.wait_for(lambda: any("empty" in t for _, t in p.text_messages[before:]), timeout=3), p.text_messages[-3:]
    collect(p, items, world_map, BK["shield"], "dead tree", ["a crown shield"], **ability())
    collect(p, items, world_map, BK["armor"], "dead tree", ["a crown armor"], **ability())
    assert carries(p, "crown shield") and carries(p, "crown armor"), p.inventory_names()


def test_black_knight_level_door(new_player, items):
    assert_level_door(new_player, items, BK["gate"], BK["outside"], 50)


def test_black_knight_rules(world_map):
    beside = (BK["shield"][0] + 1, BK["shield"][1], BK["shield"][2])
    assert_no_way(world_map, VENORE_TEMPLE, beside, level=100, rope=True, floors=9)
    assert_no_way(world_map, VENORE_TEMPLE, beside, level=49, rope=True, keys={5010}, floors=9)
    assert_way(world_map, VENORE_TEMPLE, beside, level=50, rope=True, keys={5010}, floors=9)

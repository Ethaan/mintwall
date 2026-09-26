"""Longsword Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: into the troll cave east of the Dwarf Bridge ("The cave entrance is hidden behind a tree": the loose
# ground a shovel opens), down and north - "The quest boxes are on the north end of the large room". Longsword,
# mirror, 3 blank runes, wooden doll, wedding ring, 76 gp. Our map had the three containers without quest ids.
CONTAINERS = [((32643, 31969, 8), "chest", ["a longsword", "a mirror"]),
              ((32644, 31968, 8), "box", ["a blank rune", "a blank rune", "a blank rune", "a wooden doll"]),
              ((32648, 31970, 8), "box", ["a wedding ring", "76 gold coins"])]


def test_longsword_quest(new_player, items, world_map):
    from tibia74 import Item
    from tibia74.route import walk_next_to
    p = kazordoon_player(new_player, items=[Item(SHOVEL)])
    ability = dict(level=2000, rope=True, shovel=True)
    for spot, what, found in CONTAINERS:
        walk_next_to(p, items, world_map, spot, **ability)
        before = len(p.text_messages)
        use_map_item(p, items, spot, what)
        got = lambda: sorted(t[len("You have found "):-1] for _, t in p.text_messages[before:]  # noqa: E731
                             if t.startswith("You have found"))
        assert p.wait_for(lambda: got() == sorted(found), timeout=3), got()
        p.sleep(1.1)
    for name in ("longsword", "mirror", "wooden doll", "wedding ring"):
        assert carries(p, name), p.inventory_names()


def test_longsword_rules(world_map):
    # the cave's hidden entrance needs a shovel
    assert_no_way(world_map, KAZORDOON_TEMPLE, (32644, 31969, 8), level=100, rope=True)
    assert_way(world_map, KAZORDOON_TEMPLE, (32644, 31969, 8), level=100, rope=True, shovel=True)

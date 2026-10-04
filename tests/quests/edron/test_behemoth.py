"""Behemoth Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki pre-8.0: down Cyclopolis past the level-30 gate; "You'll have to move some stones in order to reach the
# quest room": in the small circular room lined with fire fields, "Use Destroy Field on one of these fields to discover
# a lever. Push the lever"; then north across the Behemoth floor, up the stairs, through the level door, "The quest
# boxes are at the north end of the room". The lever (quests/behemoth_lever.lua, the map's own at 33290,31715) takes
# the stones away and puts them back. Level 60 (TibiaWiki 2005, Tibiantis, tibiaot74's gate) and one of each chest per
# character - decided with the user. Rewards: quests/system.lua.
BEHEMOTH = dict(lever=(33290, 31715, 12), stones=[(x, 31677, 15) for x in range(33295, 33300)],
                south_of_stones=(33297, 31679, 15), north_of_stones=(33297, 31676, 15),
                gate=(33297, 31670, 14), gate_outside=(33297, 31671, 14),
                chests=[((33294, 31658, 13), "a demon shield"), ((33295, 31658, 13), "a golden armor"),
                        ((33297, 31658, 13), "a guardian halberd"), ((33298, 31658, 13), "a bag")])
DESTROY_FIELD, FIRE_FIELD, STONE, LEVER_LEFT, LEVER_RIGHT = 2261, 1487, 1304, 1945, 1946
BAG = ["platinum amulet", "life ring", "crystal ring", "small diamond", "small sapphire"]


def test_behemoth_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import open_carried, strong
    from tibia74.route import _destroy_fields, clear_items, follow, walk_next_to
    B = BEHEMOTH
    p = strong(new_player, EDRON_TEMPLE, premium_days=30, items=[Item(DESTROY_FIELD, 3)], maglevel=10,
               group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    has = lambda pos, sid: any(i.client_id == sid for i in p.tile_items(pos))   # noqa: E731
    stones = lambda: [s for s in B["stones"] if has(s, STONE)]                 # noqa: E731

    # the stones close the passage north on the Behemoth floor
    follow(p, items, world_map, B["south_of_stones"], **ability)
    assert p.wait_for(lambda: len(stones()) == 5, timeout=3), [p.tiles.get(s) for s in B["stones"]]

    # the lever lies under a fire field and a dead orc: "You may have to move corpses to find the lever" - move the
    # orc, destroy the field, pull the lever to the right
    walk_next_to(p, items, world_map, B["lever"], **ability)
    assert p.wait_for(lambda: has(B["lever"], FIRE_FIELD), timeout=3), p.tiles.get(B["lever"])
    clear_items(p, items, B["lever"])
    _destroy_fields(p, items, B["lever"])
    assert not has(B["lever"], FIRE_FIELD), p.tiles.get(B["lever"])
    use_map_item(p, items, B["lever"], "switch")
    assert p.wait_for(lambda: has(B["lever"], LEVER_RIGHT), timeout=3), p.tiles.get(B["lever"])

    # the stones are gone; north, up the stairs, the level door, the chests at the north end
    moved = set(B["stones"])
    follow(p, items, world_map, B["south_of_stones"], open_tiles=moved, **ability)
    assert p.wait_for(lambda: not stones(), timeout=3), [p.tiles.get(s) for s in B["stones"]]
    for chest, found in B["chests"]:
        walk_next_to(p, items, world_map, chest, open_tiles=moved, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    for name in ("demon shield", "golden armor", "guardian halberd"):
        assert carries(p, name), p.inventory_names()
    bag = open_carried(p, items, "bag")
    assert p.wait_for(lambda: sorted(i.name for i in bag.items) == sorted(BAG), timeout=3), bag.items
    counts = {i.name: i.count for i in bag.items}
    assert counts["small diamond"] == 3 and counts["small sapphire"] == 4, counts
    for chest, _ in B["chests"]:                                          # one of each per character
        walk_next_to(p, items, world_map, chest, open_tiles=moved, **ability)
        use_map_item(p, items, chest, "chest")
        before = len(p.messages("The chest is empty."))
        assert p.wait_for(lambda: len(p.messages("The chest is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)

    # out the way we came, while the stones are away
    follow(p, items, world_map, EDRON_TEMPLE, open_tiles=moved, **ability)


def test_behemoth_level_door(new_player, items):
    assert_level_door(new_player, items, BEHEMOTH["gate"], BEHEMOTH["gate_outside"], 60)


def test_behemoth_rules(world_map):
    ability = dict(level=2000, vocation=4, rope=True)
    moved = set(BEHEMOTH["stones"])
    chest = (33296, 31659, 13)
    assert_no_way(world_map, EDRON_TEMPLE, chest, **ability)                                   # the stones
    assert_way(world_map, EDRON_TEMPLE, (33293, 31717, 12), **ability)                         # the lever is free
    assert_way(world_map, EDRON_TEMPLE, chest, open_tiles=moved, **ability)                    # lever pulled
    assert_no_way(world_map, EDRON_TEMPLE, chest, open_tiles=moved, **dict(ability, level=59))  # the gate
    assert_way(world_map, chest, EDRON_TEMPLE, open_tiles=moved, **ability)                    # out
    # the stones back (the lever pulled again) close the only walking way out north of them
    assert_no_way(world_map, BEHEMOTH["north_of_stones"], EDRON_TEMPLE, **ability)

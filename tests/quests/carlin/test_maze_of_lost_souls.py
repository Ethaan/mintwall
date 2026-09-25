"""The Maze of Lost Souls and Demona, north of Carlin: Griffin Shield, Crystal Wand and Purple Tome quests
(docs/reference-74/quests.md). The Demona Ring Quest is not 7.4 (no chests on the map, first documented 2016 -
decided with the user 2026-09-25)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: from the Fields of Glory "Use the shovel to open a hole", on to the underground forest, "behind the
# trees, there is a hole and inside that hole there is a switch that you must turn right to open the entrance to the
# MoLS"; current wiki: the switch opens the hole 32483,31633,9 - it drops inside four level-30 gates ("You need to be
# level 30 to enter there"), a ladder under it leads back up. "In the first entrance room is the Griffin Shield Quest"
# (2 slain skeletons and a dead body), then the level-60 gate to Demona: the Crystal Wand room (two boxes by the
# thrones) and the library (the maps and the purple tome). Out: the teleport "to the surface" 32400,31656,15.
MOLS = dict(
    switch=(32528, 31724, 10), hole=(32483, 31633, 9), landing=(32483, 31633, 10),
    gate_30=(32486, 31633, 10), inside_30=(32485, 31633, 10),
    gate_60=(32483, 31722, 15), inside_60=(32484, 31722, 15),
    griffin=[((32498, 31721, 15), "slain skeleton", "a griffin shield"),
             ((32500, 31721, 15), "dead human", "a dwarven axe"),
             ((32503, 31724, 15), "slain skeleton", "an obsidian lance")],
    wand=[((32481, 31611, 15), "box", "a crystal wand"), ((32479, 31611, 15), "box", "a bag")],
    tome=[((32421, 31594, 15), "bookcase", "a purple tome"), ((32423, 31591, 15), "bookcase", "a map"),
          ((32428, 31591, 15), "bookcase", "a map")],
    exit=(32400, 31656, 15), surface=(32493, 31697, 7),
)
SWITCH_LEFT, SWITCH_RIGHT, HOLE = 1945, 1946, 383


def _into_the_maze(p, items, world_map, **ability):
    """From anywhere above: the switch to the right, then down the hole it opens."""
    from tibia74.route import follow, walk_next_to
    M = MOLS
    walk_next_to(p, items, world_map, M["switch"], **ability)
    if any(i.client_id == SWITCH_RIGHT for i in p.tile_items(M["switch"])):      # "turn it left and right again"
        use_map_item(p, items, M["switch"], "switch")
        p.sleep(1.1)
    use_map_item(p, items, M["switch"], "switch")
    assert p.wait_for(lambda: any(i.client_id == SWITCH_RIGHT for i in p.tile_items(M["switch"])), timeout=3), \
        p.tiles.get(M["switch"])
    follow(p, items, world_map, (M["hole"][0] - 1, M["hole"][1], M["hole"][2]), **ability)
    assert p.wait_for(lambda: any(i.client_id == HOLE for i in p.tile_items(M["hole"])), timeout=3), \
        p.tiles.get(M["hole"])
    step_onto(p, M["hole"])
    assert p.wait_for(lambda: p.pos == M["landing"], timeout=3), p.pos


def _take(p, items, world_map, things, **ability):
    from tibia74.route import walk_next_to
    for pos, what, found in things:
        walk_next_to(p, items, world_map, pos, **ability)
        use_map_item(p, items, pos, what)
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    for pos, what, _ in things:                                            # once each
        before = len(p.messages(f"The {what} is empty."))
        walk_next_to(p, items, world_map, pos, **ability)
        use_map_item(p, items, pos, what)
        assert p.wait_for(lambda: len(p.messages(f"The {what} is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)


def _explorer(new_player):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    p = strong(new_player, CARLIN_TEMPLE, items=[Item(SHOVEL)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def test_griffin_shield_quest(new_player, items, world_map):
    from tibia74.route import follow
    p = _explorer(new_player)
    ability = dict(level=30, rope=True, shovel=True)
    _into_the_maze(p, items, world_map, **ability)
    _take(p, items, world_map, MOLS["griffin"], **ability)
    for name in ("griffin shield", "dwarven axe", "obsidian lance"):
        assert carries(p, name), p.inventory_names()
    follow(p, items, world_map, CARLIN_TEMPLE, **ability)                 # back out through the maze and the ladder


def test_crystal_wand_and_purple_tome_quests(new_player, items, world_map):
    from tibia74.quest import open_carried
    from tibia74.route import follow
    M = MOLS
    p = _explorer(new_player)
    ability = dict(level=60, rope=True, shovel=True)
    _into_the_maze(p, items, world_map, **ability)
    _take(p, items, world_map, M["wand"], **ability)                      # Demona, past the level-60 gate
    assert carries(p, "crystal wand"), p.inventory_names()
    bag = open_carried(p, items, "bag")
    assert p.wait_for(lambda: sorted(i.name for i in bag.items) == ["sudden death rune", "written parchment"],
                      timeout=3), bag.items
    assert next(i for i in bag.items if i.name == "sudden death rune").count == 2, bag.items   # "Double SD"
    _take(p, items, world_map, M["tome"], **ability)                      # the library
    assert carries(p, "purple tome") and carries(p, "map"), p.inventory_names()
    follow(p, items, world_map, (M["exit"][0], M["exit"][1] + 1, M["exit"][2]), **ability)
    step_onto(p, M["exit"])
    assert p.wait_for(lambda: p.pos == M["surface"], timeout=3), p.pos   # the Fields of Glory


def test_mols_switch_opens_and_shuts_the_hole(new_player, items):
    """Right opens the hole, left shuts it (TibiaWiki: "if it is already turned right, turn it left and right again")."""
    from tibia74.quest import next_to
    M = MOLS
    watcher = next_to(new_player, M["hole"], group_id=TESTER_GROUP, storage={30001: 1})
    p = next_to(new_player, M["switch"], group_id=TESTER_GROUP, storage={30001: 1})
    ground = lambda: [i.client_id for i in watcher.tile_items(M["hole"])]   # noqa: E731
    if any(i.client_id == SWITCH_RIGHT for i in p.tile_items(M["switch"])):
        use_map_item(p, items, M["switch"], "switch")
        p.sleep(1.1)
    assert watcher.wait_for(lambda: HOLE not in ground(), timeout=3), ground()
    use_map_item(p, items, M["switch"], "switch")                           # to the right
    assert watcher.wait_for(lambda: HOLE in ground(), timeout=3), ground()
    p.sleep(1.1)
    use_map_item(p, items, M["switch"], "switch")                           # to the left
    assert watcher.wait_for(lambda: HOLE not in ground(), timeout=3), ground()


def test_mols_level_gates(new_player, items):
    M = MOLS
    assert_level_door(new_player, items, M["gate_30"], M["inside_30"], 30)   # out of the landing, into the maze
    assert_level_door(new_player, items, M["gate_60"], M["inside_60"], 60)   # Demona


def test_mols_rules(world_map):
    M = MOLS
    # without the switch there is no way down (the hole is not on the map)
    assert_no_way(world_map, CARLIN_TEMPLE, M["landing"], level=100, rope=True, shovel=True)
    # the switch: a shovel hole on the way (TibiaWiki: "Use the shovel to open a hole")
    beside_switch = (M["switch"][0] - 1, M["switch"][1], M["switch"][2])
    assert_way(world_map, CARLIN_TEMPLE, beside_switch, level=1, rope=True, shovel=True)
    assert_no_way(world_map, CARLIN_TEMPLE, beside_switch, level=1, rope=True)
    # from the landing: level 30 for the maze, 60 for Demona; the ladder back up for anyone
    assert_no_way(world_map, M["landing"], (32497, 31720, 15), level=29, rope=True, shovel=True)
    assert_way(world_map, M["landing"], (32497, 31720, 15), level=30, rope=True, shovel=True)
    assert_no_way(world_map, M["landing"], (32480, 31612, 15), level=59, rope=True, shovel=True)
    assert_way(world_map, M["landing"], (32480, 31612, 15), level=60, rope=True, shovel=True)
    assert_way(world_map, M["landing"], CARLIN_TEMPLE, level=1, rope=True, shovel=True)

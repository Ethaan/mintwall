"""The Queen of the Banshees Quest, under the Ghostlands (docs/reference-74/quests.md), and the White Raven Monastery
Quest part 2 (Costello, the monk's diary, the Blessed Ankh) that runs through the same dungeon."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki spoiler (Dec 2006 and current), tibiaot74's banshee scripts for positions. Decided with the user
# 2026-09-25: the 7.x wiki's rewards; the magic walls close by the hidden buttons and a minute after a switch opened
# them; the trespass fine on the Isle later. Our map had every piece but nothing ran: 11 portals without a destination,
# the flames, the switches, the doors; the round chamber had no floor over its stairs down (placed, as tibiaot74 did).
SEAL = dict(hidden=51101, plague=51102, demonrage=51103, sacrifice=51104, true_path=51105, logic=51106, kiss=51107)
BQ = dict(
    west_switch=(32212, 31888, 12), east_switch=(32315, 31910, 12),
    walls=[(32259, 31890, 10), (32259, 31891, 10)], outside_walls=(32259, 31892, 10), buttons=[(32258, 31889, 10)],
    hole=(32262, 31887, 10),
    trap_switch=(32266, 31861, 11), trapdoor=(32266, 31860, 11), monk=(32262, 31861, 11),
    hidden_flame=(32278, 31903, 13), hidden_chamber=(32266, 31849, 15), hidden_back=(32267, 31847, 15),
    hidden_seal_room=(32275, 31905, 13),
    logic_flame=(32311, 31978, 13), logic_right=[(32310, 31975, 13), (32312, 31975, 13), (32310, 31976, 13),
                                                 (32312, 31976, 13)],
    logic_chamber=(32261, 31856, 15), logic_back=(32259, 31858, 15),
    true_start=(32185, 31938, 14), true_path=[(32186, 31937, 14), (32187, 31937, 14), (32188, 31937, 14),
                                              (32188, 31938, 14), (32189, 31938, 14), (32189, 31939, 14),
                                              (32189, 31940, 14), (32190, 31940, 14), (32191, 31940, 14),
                                              (32191, 31939, 14), (32191, 31938, 14)],
    true_trap=(32187, 31936, 14),
    true_flame=(32192, 31938, 14), true_chamber=(32268, 31856, 15), true_back=(32267, 31858, 15),
    blood_spot=(32243, 31892, 14), sacrifice_flame=(32250, 31892, 14), sacrifice_chamber=(32261, 31849, 15),
    sacrifice_back=(32259, 31847, 15),
    warlock_tile=(32215, 31838, 15), levers=[(32220, y, 15) for y in (31843, 31845, 31844, 31842, 31846)],
    demon_flame=(32215, 31849, 15), demon_chamber=(32273, 31856, 15), demon_back=(32274, 31858, 15),
    white_table=(32173, 31871, 15), black_table=(32180, 31871, 15), pearl_portal=(32176, 31869, 15),
    behind_pearls=(32176, 31863, 15), plague_flame=(32171, 31853, 15), plague_chamber=(32273, 31849, 15),
    plague_back=(32274, 31847, 15),
    grave=(32202, 31812, 8), queen_hall=(32230, 31864, 14), before_doors=(32223, 31868, 14),
    doors=[(32223, y, 14) for y in (31872, 31875, 31878, 31881, 31884, 31887, 31890)],
    final_room=(32219, 31903, 15), exit=(32219, 31913, 15), ghostlands=(32199, 31834, 7),
    chests=[((32212, 31896, 15), "boots of haste"), ((32226, 31896, 15), "a giant sword"),
            ((32212, 31910, 15), "a tower shield"), ((32226, 31910, 15), "a bag")],
    warded_doors=[(32169, 31933, 7), (32171, 31936, 7)],
)
VIAL, BLOOD, WHITE_PEARL, BLACK_PEARL, HEAVY_MISSILE = 2006, 2, 2143, 2144, 2311
SWITCH_RIGHT, MAGIC_WALL = 1946, 1497
ALL_SEALS = {v: 1 for v in SEAL.values()}
POISON_FIELDS = [(32265, 31862, 11), (32265, 31863, 11)]   # under the east sacrificial stone: they reveal the switch


def _walk_over_the_poison_fields(p, items, world_map, **ability):
    """Onto one of the two poison fields (a monster may stand on the other)."""
    from tibia74.route import walk_next_to
    for _ in range(3):
        for field in POISON_FIELDS:
            walk_next_to(p, items, world_map, field, **ability)
            try:
                step_onto(p, field)
                return
            except AssertionError:
                p.sleep(1)
    raise AssertionError("could not step onto the poison fields")


def _has(p, pos, sid):
    return any(i.client_id == sid for i in p.tile_items(pos))


def _try_step(p, pos):
    """One step towards pos; the server may put you straight back (a flame whose task is not done)."""
    from tibia74.route import DIRECTIONS
    p.step(DIRECTIONS[(pos[0] - p.pos[0], pos[1] - p.pos[1])])
    p.sleep(1)


def _through_flame(p, items, world_map, flame, chamber, back_portal, back_to):
    """Into the seal's flame (from a tile next to it), then its chamber's portal back to the seal."""
    from tibia74.route import walk_next_to
    step_onto(p, flame)
    assert p.wait_for(lambda: p.pos == chamber, timeout=3), (flame, p.pos, p.text_messages[-2:])
    walk_next_to(p, items, world_map, back_portal, level=1)
    step_onto(p, back_portal)
    assert p.wait_for(lambda: p.pos == back_to, timeout=3), (back_portal, p.pos)


def test_banshee_quest(new_player, items, world_map, db):
    """Carlin temple -> the six seals -> the Queen's kiss, as one level-2000 tester; two friends pull the wall switches."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import next_to, npc_pos, strong, talk_to
    from tibia74.route import carried, follow, use_tool, walk_next_to
    B = BQ
    p = strong(new_player, CARLIN_TEMPLE, items=[Item(PICK), Item(SHOVEL), Item(VIAL, BLOOD), Item(WHITE_PEARL),
                                                 Item(BLACK_PEARL), Item(HEAVY_MISSILE, 50)],
               maglevel=30, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, rope=True, pick=True, shovel=True)
    # the dungeon's ghosts are immune to a sword: heavy magic missiles clear one from the way (tibia74/route.py _clear)

    # the magic walls: to their south side, then both switches at once, through, over the hidden buttons (they close)
    follow(p, items, world_map, B["outside_walls"], **ability)
    assert all(_has(p, w, MAGIC_WALL) for w in B["walls"]), [p.tiles.get(w) for w in B["walls"]]
    for switch in (B["west_switch"], B["east_switch"]):
        friend = next_to(new_player, switch, group_id=TESTER_GROUP, storage={30001: 1})
        use_map_item(friend, items, switch, "switch")
        friend.sleep(0.5)
        friend.logout()
    assert p.wait_for(lambda: not any(_has(p, w, MAGIC_WALL) for w in B["walls"]), timeout=3), \
        [p.tiles.get(w) for w in B["walls"]]
    follow(p, items, world_map, (B["hole"][0] - 1, B["hole"][1], 10), open_tiles=B["walls"], **ability)
    assert p.wait_for(lambda: all(_has(p, w, MAGIC_WALL) for w in B["walls"]), timeout=3), "the buttons did not close them"
    step_onto(p, B["hole"])
    assert p.wait_for(lambda: p.pos[2] == 11, timeout=3), p.pos

    # floor 11: the monk (White Raven: the diary), the switch that takes the wall off the trapdoor
    walk_next_to(p, items, world_map, B["monk"], **ability)
    use_map_item(p, items, B["monk"], "dead human")
    assert p.wait_for(lambda: p.messages("You have found a backpack."), timeout=3), p.text_messages[-3:]
    p.sleep(1.1)
    # "Walk over the poison fields and a switch will appear" (current wiki)
    _walk_over_the_poison_fields(p, items, world_map, **ability)
    assert p.wait_for(lambda: _has(p, B["trap_switch"], 1945), timeout=3), p.tiles.get(B["trap_switch"])
    walk_next_to(p, items, world_map, B["trap_switch"], **ability)
    use_map_item(p, items, B["trap_switch"], "switch")
    assert p.wait_for(lambda: not _has(p, B["trapdoor"], MAGIC_WALL), timeout=3), p.tiles.get(B["trapdoor"])

    # the Hidden Seal: the trapdoor, the portal into the long hall, the pick hole, the flame
    follow(p, items, world_map, (B["hidden_flame"][0] - 1, B["hidden_flame"][1], 13), open_tiles=[B["trapdoor"]],
           **ability)
    _through_flame(p, items, world_map, B["hidden_flame"], B["hidden_chamber"], B["hidden_back"], (32275, 31905, 13))

    # the Seal of Logic: the four western switches to the right
    for switch in B["logic_right"]:
        walk_next_to(p, items, world_map, switch, **ability)
        use_map_item(p, items, switch, "switch")
        assert p.wait_for(lambda: _has(p, switch, SWITCH_RIGHT), timeout=3), p.tiles.get(switch)
        p.sleep(1.1)
    follow(p, items, world_map, (B["logic_flame"][0] - 1, B["logic_flame"][1], 13), **ability)
    _through_flame(p, items, world_map, B["logic_flame"], B["logic_chamber"], B["logic_back"], (32312, 31974, 13))

    # the Seal of the True Path: only the drawn path
    follow(p, items, world_map, B["true_start"], **ability)
    for tile in B["true_path"]:
        step_onto(p, tile)
        assert p.wait_for(lambda: p.pos == tile, timeout=3), (tile, p.pos)
    _through_flame(p, items, world_map, B["true_flame"], B["true_chamber"], B["true_back"], (32186, 31938, 14))

    # the Seal of Sacrifice: blood between the stones
    walk_next_to(p, items, world_map, B["blood_spot"], **ability)
    use_tool(p, items, "vial", B["blood_spot"])
    assert p.wait_for(lambda: any(i.name == "pool" or i.client_id == items.by_server[2025].client_id
                                  for i in p.tile_items(B["blood_spot"])), timeout=3), p.tiles.get(B["blood_spot"])
    follow(p, items, world_map, (B["sacrifice_flame"][0] - 1, B["sacrifice_flame"][1], 14), **ability)
    _through_flame(p, items, world_map, B["sacrifice_flame"], B["sacrifice_chamber"], B["sacrifice_back"], (32245, 31891, 14))

    # the Seal of Demonrage: a warlock tile, the levers in the pictured order
    follow(p, items, world_map, (B["warlock_tile"][0], B["warlock_tile"][1] - 1, 15), **ability)
    step_onto(p, B["warlock_tile"])
    assert p.wait_for(lambda: len(p.creatures_named("Warlock")) >= 1, timeout=3), list(p.creatures.values())
    for lever in B["levers"]:
        walk_next_to(p, items, world_map, lever, **ability)
        use_map_item(p, items, lever, "switch")
        p.sleep(1.1)
    follow(p, items, world_map, (B["demon_flame"][0], B["demon_flame"][1] - 1, 15), **ability)
    _through_flame(p, items, world_map, B["demon_flame"], B["demon_chamber"], B["demon_back"], (32215, 31846, 15))

    # the Plague Seal: the pearls on the tables, the portal, the poison fields, the flame
    follow(p, items, world_map, (B["pearl_portal"][0], B["pearl_portal"][1] + 1, 15), **ability)
    for name, table in (("white pearl", B["white_table"]), ("black pearl", B["black_table"])):
        pos, cid, stackpos = carried(p, items, lambda n, name=name: n == name)
        p.move_item(pos, cid, stackpos, table)
        assert p.wait_for(lambda table=table: any(i.client_id == cid for i in p.tile_items(table)), timeout=3), \
            (name, p.tiles.get(table))
        p.sleep(0.5)
    step_onto(p, B["pearl_portal"])
    assert p.wait_for(lambda: p.pos == B["behind_pearls"], timeout=3), p.pos
    follow(p, items, world_map, (B["plague_flame"][0], B["plague_flame"][1] + 1, 15), **ability)
    _through_flame(p, items, world_map, B["plague_flame"], B["plague_chamber"], B["plague_back"], (32171, 31855, 15))

    # the seventh seal: the Queen's kiss, and the grave
    from tibia74.route import walk_near
    walk_near(p, items, world_map, npc_pos("The Queen of the Banshees"), **ability)
    said = talk_to(p, "The Queen of the Banshees", "hi", "seventh seal", *(["yes"] * 6), "kiss", "yes")
    assert any("You may ask me for my kiss now." in s for s in said), said
    assert p.wait_for(lambda: p.pos == B["grave"], timeout=5), (p.pos, said)
    p.logout()
    for name, key in SEAL.items():
        assert db.storage_after_logout(p.character.guid, key, 1) == 1, name


def test_banshee_final_room(new_player, items, world_map, db):
    """All seven seals: the seven doors open one by one, the four chests once, the way out - and not back in."""
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    B = BQ
    p = strong(new_player, B["queen_hall"], group_id=TESTER_GROUP, storage=dict(ALL_SEALS))
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, rope=True, storages=set(SEAL.values()))
    for chest, found in B["chests"]:
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    for name in ("boots of haste", "giant sword", "tower shield"):
        assert carries(p, name), p.inventory_names()
    follow(p, items, world_map, (B["exit"][0], B["exit"][1] - 1, 15), **ability)
    step_onto(p, B["exit"])
    assert p.wait_for(lambda: p.pos == B["ghostlands"], timeout=3), p.pos
    p.logout()
    assert db.storage_after_logout(p.character.guid, SEAL["kiss"], 2) == 2    # the seventh door is shut for them now
    bag = [r for r in db.items(p.character.guid) if r["itemtype"] in (2165, 2197, 2152)]
    assert sorted(r["itemtype"] for r in bag) == [2152, 2165, 2197], bag


def test_banshee_doors_need_every_seal(new_player, items, world_map):
    B = BQ
    for missing in SEAL:
        seals = {k: 1 for n, k in SEAL.items() if n != missing}
        assert_no_way(world_map, B["before_doors"], B["final_room"], level=100, storages=set(seals))
    assert_way(world_map, B["before_doors"], B["final_room"], level=100, storages=set(SEAL.values()))
    # "Once you went downstairs you can't go up again": the fences on the ramp back up (32218-32220,31894,15)
    assert_no_way(world_map, B["final_room"], B["before_doors"], level=100, storages=set(SEAL.values()))
    # in the game: the door of a missing seal
    from tibia74.quest import strong
    p = strong(new_player, (32223, 31873, 14), group_id=TESTER_GROUP,
               storage={k: 1 for n, k in SEAL.items() if n not in ("plague",)})
    use_map_item(p, items, B["doors"][1], "closed door")
    assert p.wait_for(lambda: p.messages("The door is sealed against unwanted intruders."), timeout=3), \
        p.text_messages[-2:]


def test_banshee_queen_rules(new_player):
    from tibia74.quest import next_to, npc_pos, talk_to
    queen = npc_pos("The Queen of the Banshees")
    young = next_to(new_player, queen, level=59, group_id=TESTER_GROUP, storage={30001: 1, **ALL_SEALS, SEAL["kiss"]: -1})
    said = talk_to(young, "The Queen of the Banshees", "hi", "seventh seal")
    assert any("You are not experienced enough" in s for s in said), said
    young.logout()
    missing = next_to(new_player, queen, level=60, group_id=TESTER_GROUP,
                      storage={30001: 1, SEAL["sacrifice"]: 1, SEAL["hidden"]: 1})
    said = talk_to(missing, "The Queen of the Banshees", "hi", "seventh seal", "yes", "yes", "yes")
    assert any("You have not faced the Plague Seal yet." in s for s in said), said
    said = talk_to(missing, "The Queen of the Banshees", "hi", "kiss")
    assert any("To receive my kiss you have to pass all other seals first." in s for s in said), said
    missing.logout()
    kissed = next_to(new_player, queen, level=100, group_id=TESTER_GROUP, storage={30001: 1, **ALL_SEALS})
    said = talk_to(kissed, "The Queen of the Banshees", "hi", "kiss")
    assert any("You've already received my kiss." in s for s in said), said


def test_banshee_seal_flames_want_their_task(new_player, items):
    """A flame whose task is not done puts you back where you came from."""
    from tibia74.quest import next_to, strong
    B = BQ
    # another test may have set the Seal of Logic's switches (one server): turn them back first
    fixer = next_to(new_player, B["logic_right"][0], group_id=TESTER_GROUP, storage={30001: 1})
    for switch in B["logic_right"]:
        if _has(fixer, switch, SWITCH_RIGHT):
            use_map_item(fixer, items, switch, "switch")
            fixer.sleep(1.1)
    fixer.logout()
    for flame, beside in ((B["logic_flame"], (32310, 31978, 13)),        # switches not set
                          (B["sacrifice_flame"], (32249, 31892, 14)),    # no blood
                          (B["demon_flame"], (32215, 31848, 15))):       # no tile, no levers
        p = strong(new_player, beside, group_id=TESTER_GROUP)
        _try_step(p, flame)
        assert p.wait_for(lambda: p.pos == beside, timeout=3), (flame, p.pos)
        p.logout()
    # the pearl portal without pearls on the tables
    p = strong(new_player, (32176, 31870, 15), group_id=TESTER_GROUP)
    _try_step(p, B["pearl_portal"])
    assert p.wait_for(lambda: p.pos == (32176, 31870, 15), timeout=3), p.pos
    p.logout()
    # a True Path tile off the path: back to the start of the room
    p = strong(new_player, (32186, 31936, 14), group_id=TESTER_GROUP)
    _try_step(p, B["true_trap"])
    assert p.wait_for(lambda: p.pos == B["true_start"], timeout=3), p.pos


def test_banshee_walls_close_after_a_minute(new_player, items):
    from tibia74.quest import next_to
    B = BQ
    watcher = next_to(new_player, B["outside_walls"], group_id=TESTER_GROUP, storage={30001: 1})
    friend = next_to(new_player, B["west_switch"], group_id=TESTER_GROUP, storage={30001: 1})
    use_map_item(friend, items, B["west_switch"], "switch")
    assert watcher.wait_for(lambda: not _has(watcher, B["walls"][0], MAGIC_WALL), timeout=3), watcher.tiles.get(B["walls"][0])
    watcher.sleep(50)
    assert not _has(watcher, B["walls"][0], MAGIC_WALL), "closed too early"
    assert watcher.wait_for(lambda: _has(watcher, B["walls"][0], MAGIC_WALL), timeout=15), "did not close after a minute"


def test_banshee_rules(world_map):
    B = BQ
    ability = dict(level=100, rope=True, pick=True, shovel=True)
    beside_hole = (B["hole"][0] - 1, B["hole"][1], 10)
    assert_no_way(world_map, CARLIN_TEMPLE, beside_hole, **ability)                          # the walls
    assert_way(world_map, CARLIN_TEMPLE, beside_hole, open_tiles=B["walls"], **ability)
    assert_way(world_map, beside_hole, CARLIN_TEMPLE, **ability)                             # the portal back out
    beside_flame = (B["hidden_flame"][0] - 1, B["hidden_flame"][1], 13)
    assert_no_way(world_map, CARLIN_TEMPLE, beside_flame, open_tiles=B["walls"], **ability)   # the trapdoor's wall
    no_pick = dict(ability, pick=False)
    assert_no_way(world_map, CARLIN_TEMPLE, beside_flame, open_tiles=B["walls"] + [B["trapdoor"]], **no_pick)
    assert_way(world_map, CARLIN_TEMPLE, beside_flame, open_tiles=B["walls"] + [B["trapdoor"]], **ability)
    assert_way(world_map, B["grave"], CARLIN_TEMPLE, **ability)                              # the kiss's way out


def test_white_raven_costello_and_the_diary(new_player, items):
    """Part 2: Costello's "fugio" opens the warded doors; the monk's diary buys the Blessed Ankh."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import next_to, npc_pos, talk_to
    B = BQ
    p = next_to(new_player, npc_pos("Costello"), group_id=TESTER_GROUP, storage={30001: 1},
                inventory={BACKPACK: Item(1988)})
    p.open_container(BACKPACK)
    said = talk_to(p, "Costello", "hi", "diary", "yes")
    assert any("You don't have any diary." in s for s in said), said
    said = talk_to(p, "Costello", "hi", "fugio", "yes")
    assert any("From now on you may open the warded doors to the catacombs." in s for s in said), said
    p.logout()
    diary = Item(1972)
    p = next_to(new_player, npc_pos("Costello"), group_id=TESTER_GROUP, storage={30001: 1},
                inventory={BACKPACK: Item(1988, contents=[diary])})
    p.open_container(BACKPACK)
    said = talk_to(p, "Costello", "hi", "diary", "yes")
    assert any("Take this blessed Ankh." in s for s in said), said
    assert p.wait_for(lambda: carries(p, "ankh") and not carries(p, "book"), timeout=3), p.inventory_names()


def test_white_raven_warded_doors(new_player, items):
    from tibia74.quest import strong
    B = BQ
    door = B["warded_doors"][1]
    outside = (door[0] + 1, door[1], 7)
    shut = strong(new_player, outside, group_id=TESTER_GROUP)
    use_map_item(shut, items, door, "closed door")
    assert shut.wait_for(lambda: shut.messages("The door is sealed against unwanted intruders."), timeout=3), \
        shut.text_messages[-2:]
    shut.logout()
    allowed = strong(new_player, outside, group_id=TESTER_GROUP, storage={51110: 1})
    use_map_item(allowed, items, door, "closed door")
    assert allowed.wait_for(lambda: allowed.pos == door, timeout=3), allowed.pos


def test_banshee_hidden_teleporter(new_player, world_map):
    """The long hall: "If you simply keep going south, you will be teleported back" - pick the hole before it."""
    p = new_player(pos=(32266, 31892, 12), group_id=TESTER_GROUP, storage={30001: 1})
    step_onto(p, (32266, 31893, 12))
    assert p.wait_for(lambda: p.pos == (32266, 31864, 12), timeout=3), p.pos
    # so the hall's south end (the round chamber, the Seal of Logic) is reached only through the first seal's rooms
    assert_no_way(world_map, (32266, 31880, 12), (32266, 31930, 12), level=100, rope=True)
    assert_way(world_map, (32266, 31880, 12), (32266, 31930, 12), level=100, rope=True, pick=True)


ISLE = dict(key_bookcase=(32180, 31934, 7), key_door=(32178, 31928, 6), library=(32178, 31929, 6),
            restricted=(32180, 31925, 5), captain_jack_deck=(32188, 31958, 7))
TRESPASSER = 99998


def _key_3350():
    from tibia74 import Item
    return Item(2088, attributes=bytes([4]) + (3350).to_bytes(2, "little"))      # silver key, ATTR_ACTION_ID 3350


def test_isle_key_3350_bookcase(new_player, items):
    """Key 3350 lies in the bookcase in Costello's room (TibiaWiki) - for every character, once."""
    from tibia74 import BACKPACK
    from tibia74.quest import next_to, open_carried
    I = ISLE
    from tibia74 import Item
    p = next_to(new_player, I["key_bookcase"], group_id=TESTER_GROUP, storage={30001: 1}, inventory={BACKPACK: Item(1988)})
    p.open_container(BACKPACK)
    use_map_item(p, items, I["key_bookcase"], "bookcase")
    assert p.wait_for(lambda: p.messages("You have found a bag."), timeout=3), p.text_messages[-3:]
    bag = open_carried(p, items, "bag")
    assert p.wait_for(lambda: sorted(i.name for i in bag.items) == ["scroll", "silver key"], timeout=3), bag.items
    p.sleep(1.1)
    use_map_item(p, items, I["key_bookcase"], "bookcase")
    assert p.wait_for(lambda: p.messages("The bookcase is empty."), timeout=3), p.text_messages[-2:]


def test_isle_trespass_and_absolution(new_player, items, world_map, db):
    """Up to the monks' floor: Captain Jack won't sail the trespasser, Costello takes 1,000 gp at level 30."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import next_to, npc_pos, talk_to
    from tibia74.route import follow, walk_near
    I = ISLE
    p = new_player(pos=I["library"], level=30, group_id=TESTER_GROUP, storage={30001: 1},
                   inventory={BACKPACK: Item(1988, contents=[_key_3350(), Item(2152, 10), Item(2148, 20)])})
    p.open_container(BACKPACK)
    follow(p, items, world_map, (I["restricted"][0], I["restricted"][1] + 2, 5), level=30, keys={3350})
    walk_near(p, items, world_map, npc_pos("Costello"), level=30, keys={3350})
    said = talk_to(p, "Costello", "hi", "crime", "yes")
    assert any("You have to be that trespasser" in s for s in said), said
    assert any("sacrifice of 1000 gold pieces" in s for s in said), said
    assert any("So receive your absolution!" in s for s in said), said
    p.logout()
    assert db.storage_after_logout(p.character.guid, TRESPASSER, -1) == -1
    money = sum({2148: 1, 2152: 100}.get(r["itemtype"], 0) * r["count"] for r in db.items(p.character.guid))
    assert money == 1020 - 1000, money

    # a trespasser who did not pay: the captains won't take them
    jack = next_to(new_player, npc_pos("Captain Jack"), group_id=TESTER_GROUP, storage={30001: 1, TRESPASSER: 1},
                   inventory={BACKPACK: Item(1988, contents=[Item(2148, 50)])})
    said = talk_to(jack, "Captain Jack", "hi")
    assert any("You must be that intruder the good brothers were talking about! Begone!" in s for s in said), said
    jack.logout()
    poor = next_to(new_player, npc_pos("Costello"), level=30, group_id=TESTER_GROUP, storage={30001: 1, TRESPASSER: 1})
    said = talk_to(poor, "Costello", "hi", "absolution", "yes")
    assert any("You don't have enough money." in s for s in said), said
    said = talk_to(poor, "Costello", "hi", "name")
    assert any(s == "Be gone!" for s in said), said


def test_banshee_switch_appears_on_the_poison_fields(new_player, items, world_map):
    """Floor 11: walking over the poison fields under the east sacrificial stone brings the switch (after a server start
    it is not there; the whole quest may have revealed it already in this session - then it stays)."""
    B = BQ
    p = next_to(new_player, POISON_FIELDS[1], level=100, group_id=TESTER_GROUP, storage={30001: 1})
    _walk_over_the_poison_fields(p, items, world_map, level=100)
    assert p.wait_for(lambda: _has(p, B["trap_switch"], 1945) or _has(p, B["trap_switch"], 1946), timeout=3),         p.tiles.get(B["trap_switch"])

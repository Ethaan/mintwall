"""The Ancient Tombs Quest: Dipthrah's tomb, the Mountain Tomb (docs/reference-74/quests.md)."""
from quests.ankrahmun.tombs import *  # noqa: F401,F403

# Current wiki: past the level-75 gate "Go through the doors listed below: endless, pale-faced, deceased, unholy,
# doomed, righteous, sharpened, mortal" (the poem in the Ancient Tombs book); the next teleporter leads to Dipthrah,
# who drops the ornamented ankh. Our map had lost the entrance's loose stone pile (33133,32568,7; tibiaot74's dig
# spot) and the gauntlet's exit teleport pointed into rock (now tibiaot74's 33095,32590,15). A wrong door sends you
# back to the first room (decided with the user 2026-09-28). The wiki's switches before the 7th floor are not on the
# 7.4 map.
T = DIPTHRAH
GATES = [(33083, 32620, 14), (33084, 32620, 14)]
FIRST_ROOM = (33072, 32640, 15)
ROWS = [32637, 32633, 32629, 32625, 32621, 32617, 32613, 32609]
DOOR_X = [33070, 33073, 33076]            # the sign naming each door stands east of it
# the poem: endless, pale-faced, deceased, unholy, doomed, righteous, sharpened, mortal (row by row, south first)
RIGHT = {32637: 33070, 32633: 33073, 32629: 33070, 32625: 33076, 32621: 33076, 32617: 33070, 32613: 33076,
         32609: 33070}
LAST_ROOM = (33073, 32605, 15)
GAUNTLET_EXIT = (33073, 32603, 15)
DIPTHRAH_ROOM = (33095, 32590, 15)


def _through(p, items, world_map, door):
    """Open a door from the chamber south of it (unless someone left it open) and step into the doorway."""
    from tibia74.quest import _find
    from tibia74.route import follow
    follow(p, items, world_map, (door[0], door[1] + 1, 15), level=2000)
    if _find(p, items, door, "closed door"):
        use_map_item(p, items, door, "closed door")
    step_onto(p, door)


def test_dipthrah_tomb(new_player, items, world_map):
    from tibia74.route import follow
    p = tomb_player(new_player)
    ability = dict(level=2000, shovel=True, rope=True, floors=12)
    follow(p, items, world_map, T.flame, **ability)
    sacrifice_coin(p, items, T)

    follow(p, items, world_map, FIRST_ROOM, **ability)
    for y in ROWS:                                   # the poem's doors, row by row
        _through(p, items, world_map, (RIGHT[y], y, 15))
        assert p.pos == (RIGHT[y], y, 15), (y, p.pos)
    follow(p, items, world_map, (GAUNTLET_EXIT[0], GAUNTLET_EXIT[1] + 1, 15), **ability)
    step_onto(p, GAUNTLET_EXIT)
    assert p.wait_for(lambda: p.pos == DIPTHRAH_ROOM, timeout=3), p.pos

    body = kill_pharaoh(p, items, world_map, T, **ability)
    loot(p, items, body, T.pass_item)
    follow(p, items, world_map, (T.portal[0] - 1, T.portal[1], T.portal[2]), **ability)
    step_onto(p, T.portal)
    assert p.wait_for(lambda: p.pos == T.room, timeout=3), p.pos
    assert not carries(p, T.pass_item), "the portal takes the ornamented ankh"
    collect(p, items, world_map, T.sarcophagus, "sarcophagus", [T.piece], level=2000)
    assert carries(p, "damaged helmet"), p.inventory_names()


def test_dipthrah_word_doors(new_player, items, world_map):
    """A wrong door sends you back to the first room."""
    from tibia74.quest import strong
    p = strong(new_player, FIRST_ROOM, premium_days=30, group_id=TESTER_GROUP)
    _through(p, items, world_map, (RIGHT[32637], 32637, 15))       # endless: right
    wrong = (33070, 32633, 15)                                      # ghost-faced
    _through(p, items, world_map, wrong)
    assert p.wait_for(lambda: p.pos == FIRST_ROOM, timeout=3), p.pos


def test_dipthrah_rules(new_player, items, world_map):
    assert_level_door(new_player, items, GATES[0], (GATES[0][0], GATES[0][1] - 1, 14), 75)
    assert_no_way(world_map, FIRST_ROOM, DIPTHRAH_ROOM, level=2000,
                  avoid=[(RIGHT[32609], 32609, 15)])           # only through the poem's last door
    assert_no_way(world_map, DIPTHRAH_ROOM, T.room, level=2000)
    assert_way(world_map, T.room, T.back, level=2000)

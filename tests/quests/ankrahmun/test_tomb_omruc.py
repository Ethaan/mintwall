"""The Ancient Tombs Quest: Omruc's tomb, the Peninsula Tomb (docs/reference-74/quests.md)."""
from quests.ankrahmun.tombs import *  # noqa: F401,F403

# Current wiki: "You are now faced with an invisible wall maze [...] Be aware that there are additional tiles you can
# step on, but this is the only route that will lead you through successfully. Lastly, enter the teleporter to the south
# to teleport to Omruc"; he drops the crystal arrow. Our map has the maze (invisible walls, item 1548) behind the
# level-75 gate; nothing else was needed beyond what all tombs share.
T = OMRUC
GATE = (33206, 32958, 14)
MAZE_EXIT = (33206, 32982, 14)            # the teleporter south of the maze
OMRUC_ROOM = (33207, 33002, 14)
INVISIBLE_WALL = 1548


def test_omruc_tomb(new_player, items, world_map):
    from tibia74.route import follow
    p = tomb_player(new_player)
    ability = dict(level=2000, shovel=True, rope=True, floors=12)
    follow(p, items, world_map, T.flame, **ability)
    sacrifice_coin(p, items, T)

    follow(p, items, world_map, (MAZE_EXIT[0], MAZE_EXIT[1] - 1, 14), **ability)     # through the maze
    step_onto(p, MAZE_EXIT)
    assert p.wait_for(lambda: p.pos == OMRUC_ROOM, timeout=3), p.pos
    body = kill_pharaoh(p, items, world_map, T, **ability)
    loot(p, items, body, T.pass_item)
    follow(p, items, world_map, (T.portal[0] + 1, T.portal[1], T.portal[2]), **ability)
    step_onto(p, T.portal)
    assert p.wait_for(lambda: p.pos == T.room, timeout=3), p.pos
    assert not carries(p, T.pass_item), "the portal takes the crystal arrow"
    collect(p, items, world_map, T.sarcophagus, "sarcophagus", [T.piece], level=2000)
    assert carries(p, "helmet adornment"), p.inventory_names()


def test_omruc_rules(new_player, items, world_map):
    assert_level_door(new_player, items, GATE, (GATE[0], GATE[1] - 1, 14), 75)
    # the maze's walls are there (invisible): the straight way south is shut
    assert_no_way(world_map, (33206, 32959, 14), (33206, 32977, 14), level=2000,
                  avoid=[(x, 32976, 14) for x in range(33198, 33214) if x != 33206])
    assert_no_way(world_map, OMRUC_ROOM, T.room, level=2000)
    assert_way(world_map, T.room, T.back, level=2000)

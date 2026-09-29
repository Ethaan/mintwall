"""The Ancient Tombs Quest: Morguthis's tomb, the Tarpit Tomb (docs/reference-74/quests.md)."""
from quests.ankrahmun.tombs import *  # noqa: F401,F403

# Current wiki: "follow the maps to the final hunting floor and another teleport. Enter the level 75 door to arrive at
# Morguthis' arena [...] To complete the puzzle you must step in each blue flame in the maze"; Morguthis drops the sword
# hilt. Our map had no way to the arena; decided with the user 2026-09-28: the paintings open the sealed room (tibiaot74),
# its teleport leads into the floor-14 labyrinth, whose centre teleport leads to the pocket before the arena's level
# doors; trapdoors drop you into the caves, the caves' teleports lead up beside a trapdoor (tibiaot74); the last
# teleport leads to Morguthis only after all seven blue flames.
T = MORGUTHIS
PAINTING, HIDDEN_WALL = (33212, 32693, 13), (33211, 32698, 13)
ROOM_TELEPORT = (33211, 32701, 13)
LABYRINTH = (33198, 32688, 14)
LABYRINTH_CENTRE = (33212, 32699, 14)
POCKET = (33260, 32707, 13)
GATES = [(33257, 32706, 13), (33262, 32706, 13)]
FLAMES = [(33263, 32681, 14), (33279, 32682, 14), (33275, 32685, 14), (33269, 32698, 14), (33270, 32667, 15),
          (33245, 32686, 15), (33252, 32703, 15)]
LAST_TELEPORT = (33263, 32668, 13)
MORGUTHIS_ROOM = (33164, 32694, 14)
TRAPDOOR = (33253, 32704, 13)


def _to_the_pocket(p, items, world_map, **ability):
    from tibia74.route import follow
    follow(p, items, world_map, (PAINTING[0], PAINTING[1] + 1, 13), **ability)
    use_map_item(p, items, PAINTING, "painting")
    assert p.wait_for(lambda: not any(getattr(t, "client_id", None) == items.by_server[1061].client_id
                                      for t in p.tiles.get(HIDDEN_WALL, [])), timeout=3), p.tiles.get(HIDDEN_WALL)
    follow(p, items, world_map, (ROOM_TELEPORT[0], ROOM_TELEPORT[1] - 1, 13), open_tiles={HIDDEN_WALL}, **ability)
    step_onto(p, ROOM_TELEPORT)
    assert p.wait_for(lambda: p.pos == LABYRINTH, timeout=3), p.pos
    follow(p, items, world_map, (LABYRINTH_CENTRE[0] - 1, LABYRINTH_CENTRE[1], 14), **ability)
    step_onto(p, LABYRINTH_CENTRE)
    assert p.wait_for(lambda: p.pos == POCKET, timeout=3), p.pos


def test_morguthis_tomb(new_player, items, world_map):
    from tibia74.route import follow
    p = tomb_player(new_player)
    ability = dict(level=2000, shovel=True, rope=True, floors=12)
    follow(p, items, world_map, T.flame, **ability)
    sacrifice_coin(p, items, T)
    _to_the_pocket(p, items, world_map, **ability)

    for flame in FLAMES:                                     # through the trapdoors, caves and rope holes
        follow(p, items, world_map, flame, **ability)
        assert p.pos == flame, (flame, p.pos)
    follow(p, items, world_map, (LAST_TELEPORT[0], LAST_TELEPORT[1] + 1, 13), **ability)
    step_onto(p, LAST_TELEPORT)
    assert p.wait_for(lambda: p.pos == MORGUTHIS_ROOM, timeout=3), p.pos

    body = kill_pharaoh(p, items, world_map, T, **ability)
    loot(p, items, body, T.pass_item)
    follow(p, items, world_map, (T.portal[0] - 1, T.portal[1], T.portal[2]), **ability)
    step_onto(p, T.portal)
    assert p.wait_for(lambda: p.pos == T.room, timeout=3), p.pos
    assert not carries(p, T.pass_item), "the portal takes the sword hilt"
    collect(p, items, world_map, T.sarcophagus, "sarcophagus", [T.piece], level=2000)
    assert carries(p, "right horn"), p.inventory_names()


def test_morguthis_arena_rules(new_player, items, world_map):
    """The last teleport without the flames: back to the pocket; a trapdoor drops you into the cave below."""
    from tibia74.quest import strong
    p = strong(new_player, (LAST_TELEPORT[0], LAST_TELEPORT[1] + 1, 13), premium_days=30, group_id=TESTER_GROUP)
    step_onto(p, LAST_TELEPORT)
    assert p.wait_for(lambda: p.pos == POCKET, timeout=3), p.pos
    p.logout()
    p = strong(new_player, (TRAPDOOR[0] + 1, TRAPDOOR[1], 13), premium_days=30, group_id=TESTER_GROUP)
    step_onto(p, TRAPDOOR)
    assert p.wait_for(lambda: p.pos == (TRAPDOOR[0], TRAPDOOR[1], 14), timeout=3), p.pos


def test_morguthis_rules(new_player, items, world_map):
    for gate in GATES:
        assert_level_door(new_player, items, gate, (gate[0], gate[1] + 1, 13), 75)
    assert_no_way(world_map, T.below, POCKET, level=2000, rope=True, floors=12)       # the wall is shut
    assert_way(world_map, T.below, POCKET, level=2000, rope=True, floors=12, open_tiles={HIDDEN_WALL})
    assert_no_way(world_map, MORGUTHIS_ROOM, T.room, level=2000)
    assert_way(world_map, T.room, T.back, level=2000)

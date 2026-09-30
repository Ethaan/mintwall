"""Serpentine Tower Quest / White Pearl Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: up the Sorcerer guild's pyramid, down below the library; "In the room to the North, you need to
# place a pot on an open fire (unless it is already there) - this will activate the portal on the East side of the
# room, so that it teleports you into the quest room. Go through the teleport and get the White Pearl from the chest."
# Our map had the fires, a pot on the floor and two forcefields without destinations, no chest (placed at
# tibiaot74's spot, real-map uid 3700). The pot stays on the fire until the restart; the way out is always open
# (decided with the user 2026-09-27).
FIRE = (33145, 32862, 7)                  # the open fire between two fires that carry a pot already
OPEN_FIRE, POT_ON_FIRE = 1424, 1428
POT, FLOOR_POT = 2562, (33147, 32867, 7)
BESIDE_FIRE = (33145, 32863, 7)
BEFORE_FIELD = (33147, 32864, 7)
FIELD_IN, FIELD_OUT = (33148, 32864, 7), (33150, 32864, 7)
PEARL_ROOM = (33151, 32864, 7)
CHEST = (33150, 32862, 7)

# The "continuation" (TibiaWiki 2005-current, no reward): the lamp above the barrel lets the fire elemental out of
# its cage below, the switch in its cage takes the magic walls away from the green djinn's hall on the floor below
# that. Both close again after 5 minutes (decided with the user).
BARREL, LAMP = (33151, 32862, 7), (33151, 32861, 7)
CAGE_WALL, CAGE_SWITCH = (33151, 32866, 8), (33152, 32866, 8)
MAGIC_WALLS = [(33148, 32867, 9), (33149, 32867, 9), (33148, 32868, 9), (33149, 32868, 9)]
STAIRS_ROOM = (33147, 32869, 9)
WALL_LAMP, CAGE_FRONT, MAGIC_WALL = 2039, 1100, 1497


def _on(p, items, pos, item_id):
    client_id = items.by_server[item_id].client_id
    return any(getattr(t, "client_id", None) == client_id for t in p.tiles.get(tuple(pos), []))


def _pot_on_the_fire(p, items, world_map):
    """Take the pot from the floor and put it on the open fire - as a player: pick it up, stand by the fire, drop."""
    from tibia74.quest import pick_up
    from tibia74.route import follow, walk_next_to
    walk_next_to(p, items, world_map, FLOOR_POT, level=2000)
    pick_up(p, items, FLOOR_POT, "pot")
    follow(p, items, world_map, BESIDE_FIRE, level=2000)
    client_id = items.by_server[POT].client_id
    cid, n = next((cid, n) for cid, c in p.containers.items() for n, i in enumerate(c.items) if i.client_id == client_id)
    p.move_item(p.container_pos(cid, n), client_id, n, FIRE, 1)
    assert p.wait_for(lambda: _on(p, items, FIRE, POT_ON_FIRE), timeout=3), (p.tiles.get(FIRE), p.text_messages[-2:])
    assert not _on(p, items, FIRE, POT), "the pot is still lying on the fire"


def test_serpentine_tower_quest(new_player, items, world_map):
    from tibia74.route import follow
    p = ankrahmun_player(new_player)
    follow(p, items, world_map, BEFORE_FIELD, level=2000)
    if _on(p, items, FIRE, OPEN_FIRE):                       # nobody has put the pot on yet: the field does nothing
        step_onto(p, FIELD_IN)
        p.sleep(1)
        assert p.pos == FIELD_IN, p.pos
        step_onto(p, BEFORE_FIELD)
        _pot_on_the_fire(p, items, world_map)
        follow(p, items, world_map, BEFORE_FIELD, level=2000)
    step_onto(p, FIELD_IN)
    assert p.wait_for(lambda: p.pos == PEARL_ROOM, timeout=3), p.pos

    collect(p, items, world_map, CHEST, "chest", ["a white pearl"], level=2000)
    assert carries(p, "white pearl"), p.inventory_names()
    before = len(p.text_messages)
    use_map_item(p, items, CHEST, "chest")
    assert p.wait_for(lambda: any("empty" in t for _, t in p.text_messages[before:]), timeout=3), p.text_messages[-2:]

    follow(p, items, world_map, (FIELD_OUT[0] + 1, FIELD_OUT[1], 7), level=2000)
    step_onto(p, FIELD_OUT)                                  # the way out, always open
    assert p.wait_for(lambda: p.pos == BEFORE_FIELD, timeout=3), p.pos


def test_serpentine_tower_continuation(new_player, items, world_map):
    """The lamp (behind the barrel) opens the fire elemental's cage; the switch in the cage takes the magic walls in
    front of the green djinn's hall away; both close again after 5 minutes."""
    import time
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, (33151, 32863, 7), premium_days=30, group_id=TESTER_GROUP)
    assert p.wait_for(lambda: _on(p, items, LAMP, WALL_LAMP), timeout=3), p.tiles.get(LAMP)
    # the barrel stands in front of the lamp: push it aside, stand under the lamp
    barrel = items.by_server[1774].client_id
    stackpos = next(n for n, t in enumerate(p.tiles.get(BARREL, [])) if getattr(t, "client_id", None) == barrel)
    p.move_item(BARREL, barrel, stackpos, (33150, 32863, 7), 1)
    assert p.wait_for(lambda: not _on(p, items, BARREL, 1774), timeout=3), p.text_messages[-2:]
    step_onto(p, BARREL)
    use_map_item(p, items, LAMP, "wall lamp")
    p.sleep(1)
    assert _on(p, items, LAMP, WALL_LAMP), "the lamp must not light"

    # the cage is open (the route kills the fire elemental if it stands in the way)
    walk_next_to(p, items, world_map, CAGE_SWITCH, level=2000, open_tiles={CAGE_WALL})
    assert not _on(p, items, CAGE_WALL, CAGE_FRONT), p.tiles.get(CAGE_WALL)
    use_map_item(p, items, CAGE_SWITCH, "switch")
    walls_opened = time.monotonic()
    assert p.wait_for(lambda: _on(p, items, CAGE_SWITCH, 1946), timeout=3), p.tiles.get(CAGE_SWITCH)

    follow(p, items, world_map, STAIRS_ROOM, level=2000)
    for pos in MAGIC_WALLS:
        assert not _on(p, items, pos, MAGIC_WALL), (pos, p.tiles.get(pos))

    # 5 minutes later (decided with the user 2026-09-27): not while a player is in the djinn's hall - the script
    # retries every 10 s - then the magic walls are back; the cage (nobody in it) closed on time
    follow(p, items, world_map, (33148, 32866, 9), level=2000, open_tiles=set(MAGIC_WALLS))
    p.sleep(max(0, walls_opened + 5 * 60 + 5 - time.monotonic()))
    for pos in MAGIC_WALLS:
        assert not _on(p, items, pos, MAGIC_WALL), (pos, p.tiles.get(pos))
    follow(p, items, world_map, STAIRS_ROOM, level=2000, open_tiles=set(MAGIC_WALLS))
    assert p.wait_for(lambda: all(_on(p, items, pos, MAGIC_WALL) for pos in MAGIC_WALLS), timeout=15),         [p.tiles.get(pos) for pos in MAGIC_WALLS]
    walk_next_to(p, items, world_map, CAGE_WALL, level=2000)
    assert p.wait_for(lambda: _on(p, items, CAGE_WALL, CAGE_FRONT), timeout=3), p.tiles.get(CAGE_WALL)


def test_serpentine_tower_rules(world_map):
    # no way into the pearl room but the forcefield (while the pot is on the fire); the way out leads to the temple
    assert_no_way(world_map, ANKRAHMUN_TEMPLE, (33151, 32863, 7), level=2000)
    assert_way(world_map, (33151, 32863, 7), ANKRAHMUN_TEMPLE, level=2000)
    # the fire elemental's cage and the green djinn's hall are closed on the map
    assert_no_way(world_map, ANKRAHMUN_TEMPLE, CAGE_SWITCH, level=2000)
    assert_no_way(world_map, ANKRAHMUN_TEMPLE, (33148, 32866, 9), level=2000)

"""The Ancient Tombs Quest: Rahemos's tomb, the Oasis Tomb (docs/reference-74/quests.md)."""
from quests.ankrahmun.tombs import *  # noqa: F401,F403

# TibiaWiki 2006: past the level-75 gate "You need to use levers to get a Carrot to be able to go through the next
# door. Each fault will cost you 200 hp"; "try to move against walls. Some of the walls let you go through"; "walk over
# the lava from the left side of the broken bridge"; Rahemos drops the ancient rune. Our map had lost the entrance's
# loose stone pile (33133,32640,7) and the door (33122,32765,14; tibiaot74's) and had the bridge whole: the pile, a
# quest door and lava in the bridge's middle as tibiaot74 (decided with the user 2026-09-28). The carrot is under a
# random hat on each pull. A counter stood on the only tile the switches can be pulled from (33119,32762,14; tibiaot74
# and the wiki's 2007 picture have the player standing there): removed.
T = RAHEMOS
ARRIVAL = (33124, 32760, 14)              # east of the gate, from the teleport
GATE = (33123, 32762, 14)
SWITCHES = [(33118, 32761, 14), (33118, 32762, 14), (33118, 32763, 14)]
HATS = [(33117, 32761, 14), (33117, 32762, 14), (33117, 32763, 14)]
DOOR = (33122, 32765, 14)
FOUND = 51125                             # storage: found the carrot (the door's action id)
BRIDGE_GAP = [(x, y, 14) for y in (32794, 32795) for x in (33119, 33120, 33121)]
BEFORE_LAVA, AFTER_LAVA = (33120, 32792, 14), (33120, 32797, 14)


def _find_the_carrot(p, items, world_map, hurts=False):
    """Pull hat switches until the carrot shows; every wrong one costs exactly 200 hp (not a tester's)."""
    from tibia74.route import walk_next_to
    carrot = items.by_server[2684].client_id
    walk_next_to(p, items, world_map, SWITCHES[1], level=2000)
    for pull in range(30):
        switch = SWITCHES[pull % 3]
        if max(abs(switch[0] - p.pos[0]), abs(switch[1] - p.pos[1])) > 1:
            walk_next_to(p, items, world_map, switch, level=2000)
        hp = p.stats.health
        use_map_item(p, items, switch, "switch")
        hat = HATS[pull % 3]
        if p.wait_for(lambda: any(getattr(t, "client_id", None) == carrot for t in p.tiles.get(hat, [])), timeout=1):
            return pull
        if hurts:
            assert p.wait_for(lambda: p.stats.health == hp - 200, timeout=2), (hp, p.stats.health)
        p.sleep(1.1)
    raise AssertionError("no carrot in 30 pulls")


def test_rahemos_tomb(new_player, items, world_map):
    from tibia74.route import follow
    p = tomb_player(new_player)
    ability = dict(level=2000, shovel=True, rope=True, floors=12)
    follow(p, items, world_map, T.flame, **ability)
    sacrifice_coin(p, items, T)

    follow(p, items, world_map, ARRIVAL, **ability)
    follow(p, items, world_map, (DOOR[0], DOOR[1] - 1, 14), **ability)
    use_map_item(p, items, DOOR, "closed door")                  # sealed until the carrot
    assert p.wait_for(lambda: p.messages("sealed"), timeout=3), p.text_messages[-2:]
    _find_the_carrot(p, items, world_map)

    # through the door, the maze's false walls and over the lava beside the broken bridge
    follow(p, items, world_map, BEFORE_LAVA, storages={FOUND}, **ability)
    follow(p, items, world_map, AFTER_LAVA, storages={FOUND}, avoid=BRIDGE_GAP, **ability)
    body = kill_pharaoh(p, items, world_map, T, storages={FOUND}, **ability)
    loot(p, items, body, T.pass_item)

    follow(p, items, world_map, (T.portal[0] + 1, T.portal[1], T.portal[2]), storages={FOUND}, **ability)
    step_onto(p, T.portal)
    assert p.wait_for(lambda: p.pos == T.room, timeout=3), p.pos
    assert not carries(p, T.pass_item), "the portal takes the ancient rune"
    collect(p, items, world_map, T.sarcophagus, "sarcophagus", [T.piece], level=2000)
    assert carries(p, "helmet piece"), p.inventory_names()


def test_rahemos_hats(new_player, items, world_map):
    """A wrong hat costs 200 hp; the carrot opens the door for this player."""
    from tibia74.quest import strong
    p = strong(new_player, (33119, 32762, 14), premium_days=30)
    _find_the_carrot(p, items, world_map, hurts=True)
    follow_door = (DOOR[0], DOOR[1] - 1, 14)
    from tibia74.route import follow
    follow(p, items, world_map, follow_door, level=2000)
    use_map_item(p, items, DOOR, "closed door")
    assert p.wait_for(lambda: p.pos == DOOR, timeout=3), (p.pos, p.text_messages[-2:])


def test_rahemos_rules(new_player, items, world_map):
    assert_level_door(new_player, items, GATE, (GATE[0] + 1, GATE[1], 14), 75)
    # the door is shut without the carrot; the lava only on the hidden path left of the broken bridge
    assert_no_way(world_map, ARRIVAL, BEFORE_LAVA, level=2000)
    assert_way(world_map, ARRIVAL, BEFORE_LAVA, level=2000, storages={FOUND})
    for tile in BRIDGE_GAP:
        assert not world_map.walkable(tile), tile
    assert_way(world_map, BEFORE_LAVA, AFTER_LAVA, level=2000)
    assert_no_way(world_map, T.lair, T.room, level=2000, storages={FOUND})
    assert_way(world_map, T.room, T.back, level=2000)

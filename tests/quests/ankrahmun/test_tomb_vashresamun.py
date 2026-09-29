"""The Ancient Tombs Quest: Vashresamun's tomb, the Ancient Ruins Tomb (docs/reference-74/quests.md)."""
from quests.ankrahmun.tombs import *  # noqa: F401,F403

# TibiaWiki 2006: down to the 7th floor, "Walk there, and put scarab coin to the coal basin"; through the teleport
# "you will see a gate of expertise for level 75. When you go trough it, there are many musical instruments. You have
# to play them in right order to get trough the next door" - drum, panpipes, lute, lyre, cornucopia (the wiki's
# picture, tibiaot74). Our map had the arrival on the door's side: swapped to the wiki's order (decided with the user
# 2026-09-28). Vashresamun drops the blue note; his portal takes it and leads to the sarcophagus with the left horn.
T = VASHRESAMUN
ARRIVAL = (33193, 32665, 15)              # behind the level-75 gate
GATE = (33192, 32665, 15)
DRUM, HORN_OF_SUNDERING, LUTE, FLUTE = (33188, 32660, 15), (33189, 32660, 15), (33190, 32660, 15), (33191, 32660, 15)
FANFARE, LYRE, PANPIPES, CORNUCOPIA = (33188, 32669, 15), (33189, 32669, 15), (33190, 32669, 15), (33191, 32669, 15)
TUNE = [(DRUM, "drum"), (PANPIPES, "panpipes"), (LUTE, "lute"), (LYRE, "lyre"), (CORNUCOPIA, "cornucopia")]
DOOR = (33184, 32665, 15)
TO_VASHRESAMUN = (33178, 32664, 15)
VASHRESAMUN_ROOM = (33130, 32656, 15)
BACK_OUT = (33194, 32664, 15)             # the teleport by the arrival leads back into the tomb


def _play(p, items, world_map, tune):
    from tibia74.route import walk_next_to
    for pos, name in tune:
        walk_next_to(p, items, world_map, pos, level=2000)
        use_map_item(p, items, pos, name)
        p.sleep(0.6)


def _door_opens(p, items, world_map):
    from tibia74.route import walk_next_to
    walk_next_to(p, items, world_map, DOOR, level=2000)
    before = len(p.text_messages)
    use_map_item(p, items, DOOR, "closed door")
    return p.wait_for(lambda: any(getattr(t, "client_id", None) == items.by_server[1233].client_id
                                  for t in p.tiles.get(DOOR, [])), timeout=2), p.text_messages[before:]


def test_vashresamun_tomb(new_player, items, world_map):
    from tibia74.route import follow
    p = tomb_player(new_player)
    ability = dict(level=2000, shovel=True, rope=True, floors=12)
    follow(p, items, world_map, T.flame, **ability)
    sacrifice_coin(p, items, T)

    follow(p, items, world_map, ARRIVAL, **ability)
    opened, said = _door_opens(p, items, world_map)            # the door needs the tune
    assert not opened and any("locked" in t for _, t in said), said
    _play(p, items, world_map, [(DRUM, "drum"), (LUTE, "lute")])   # wrong: starts over
    _play(p, items, world_map, TUNE)
    opened, said = _door_opens(p, items, world_map)
    assert opened, said
    cornucopia = items.by_server[2369].client_id               # played, not turned into grapes
    assert any(getattr(t, "client_id", None) == cornucopia for t in p.tiles.get(CORNUCOPIA, [])), \
        p.tiles.get(CORNUCOPIA)

    follow(p, items, world_map, (TO_VASHRESAMUN[0] + 1, TO_VASHRESAMUN[1], 15), open_tiles={DOOR}, **ability)
    step_onto(p, TO_VASHRESAMUN)
    assert p.wait_for(lambda: p.pos == VASHRESAMUN_ROOM, timeout=3), p.pos
    body = kill_pharaoh(p, items, world_map, T, **ability)
    loot(p, items, body, T.pass_item)

    follow(p, items, world_map, (T.portal[0] + 1, T.portal[1], T.portal[2]), **ability)
    step_onto(p, T.portal)
    assert p.wait_for(lambda: p.pos == T.room, timeout=3), p.pos
    assert not carries(p, T.pass_item), "the portal takes the blue note"
    collect(p, items, world_map, T.sarcophagus, "sarcophagus", [T.piece], level=2000)
    assert carries(p, T.piece.split(" ", 1)[1]), p.inventory_names()


def test_vashresamun_rules(new_player, items, world_map):
    from tibia74.quest import strong
    # the flame without a coin does nothing; the level-75 gate
    p = strong(new_player, (T.flame[0] + 1, T.flame[1], T.flame[2]), premium_days=30, group_id=TESTER_GROUP)
    step_onto(p, T.flame)
    p.sleep(1)
    assert p.pos == T.flame, p.pos
    p.logout()
    assert_level_door(new_player, items, GATE, ARRIVAL, 75)
    # the pharaoh's portal without the blue note: back to the start of the tomb
    p = strong(new_player, (T.portal[0] + 1, T.portal[1], T.portal[2]), premium_days=30, group_id=TESTER_GROUP)
    step_onto(p, T.portal)
    assert p.wait_for(lambda: p.pos == T.back, timeout=3), p.pos
    # no way to the pharaoh without the tune's door, none into the sarcophagus room but the portal
    assert_no_way(world_map, ARRIVAL, VASHRESAMUN_ROOM, level=2000)
    assert_no_way(world_map, VASHRESAMUN_ROOM, T.room, level=2000)
    assert_way(world_map, T.room, T.back, level=2000)

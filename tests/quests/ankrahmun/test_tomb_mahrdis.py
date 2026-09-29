"""The Ancient Tombs Quest: Mahrdis's tomb, the Shadow Tomb (docs/reference-74/quests.md)."""
from quests.ankrahmun.tombs import *  # noqa: F401,F403

# TibiaWiki 2005: up the spiral tower (level-75 gate), "you must pass room with Purple Fire on floor [...] If you step
# into Purple Fire you will lose 300 hp so move only on 'cold' squares. If Purple Fire will appear below you when you
# already on 'cold' square you will not lose any hp so don't hurry"; Mahrdis drops the burning heart. The purple fire is
# the searing fire (1506 -> 1507 -> ashes 1508 -> 1506, items.xml): our map has the room (33177-33189,32738-32754,15),
# but map items never started decaying - the fires stood still. They cycle now (iomapotbm.cpp: map items whose decay
# comes back round to themselves).
T = MAHRDIS
GATE = (33168, 32776, 15)
TO_MAHRDIS = (33157, 32771, 15)
MAHRDIS_ROOM = (33191, 32946, 15)
FIRE_ROOM = [(x, y, 15) for x in range(33177, 33190) for y in range(32738, 32755)]
FLAMES, ASHES = (1506, 1507), 1508


def test_mahrdis_tomb(new_player, items, world_map):
    from tibia74.route import follow
    p = tomb_player(new_player)
    ability = dict(level=2000, shovel=True, rope=True, floors=12)
    follow(p, items, world_map, T.flame, **ability)
    sacrifice_coin(p, items, T)

    follow(p, items, world_map, (TO_MAHRDIS[0], TO_MAHRDIS[1] + 1, 15), **ability)   # fire room, spiral, gate
    step_onto(p, TO_MAHRDIS)
    assert p.wait_for(lambda: p.pos == MAHRDIS_ROOM, timeout=3), p.pos
    body = kill_pharaoh(p, items, world_map, T, **ability)
    loot(p, items, body, T.pass_item)
    follow(p, items, world_map, (T.portal[0], T.portal[1] - 1, T.portal[2]), **ability)
    step_onto(p, T.portal)
    assert p.wait_for(lambda: p.pos == T.room, timeout=3), p.pos
    assert not carries(p, T.pass_item), "the portal takes the burning heart"
    collect(p, items, world_map, T.sarcophagus, "sarcophagus", [T.piece], level=2000)
    assert carries(p, "helmet ornament"), p.inventory_names()


def _fire_at(p, items, pos):
    ids = {items.by_client[t.client_id].server_id for t in p.tiles.get(pos, []) if getattr(t, "client_id", None)}
    return 1506 if 1506 in ids else 1507 if 1507 in ids else 1508 if ASHES in ids else None


def test_mahrdis_purple_fire(new_player, items):
    """The fires come and go (a burning tile turns to ashes and burns again); stepping into a flame costs 300 hp."""
    from tibia74.quest import strong
    p = strong(new_player, (33183, 32755, 15), premium_days=30)      # at the fire room's exit
    assert p.wait_for(lambda: any(_fire_at(p, items, t) for t in FIRE_ROOM), timeout=3)
    before = {t: _fire_at(p, items, t) for t in FIRE_ROOM if _fire_at(p, items, t)}
    p.sleep(11)
    after = {t: _fire_at(p, items, t) for t in before}
    assert any(after[t] != before[t] for t in before), "the fires stand still"
    # a flame next to us: step in
    for _ in range(40):
        near = [t for t in FIRE_ROOM if max(abs(t[0] - p.pos[0]), abs(t[1] - p.pos[1])) == 1
                and _fire_at(p, items, t) in FLAMES]
        if near:
            break
        p.sleep(0.5)
    assert near, "no flame beside the start"
    hp = p.stats.health
    step_onto(p, near[0])
    assert p.wait_for(lambda: p.stats.health <= hp - 300, timeout=3), (hp, p.stats.health)


def test_mahrdis_rules(new_player, items, world_map):
    assert_level_door(new_player, items, GATE, (GATE[0], GATE[1] + 1, 15), 75)
    assert_no_way(world_map, MAHRDIS_ROOM, T.room, level=2000)
    assert_way(world_map, T.room, T.back, level=2000)

"""The Paradox Tower Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki spoiler (Dec 2006) and first revision (2005): four missions of knowledge (Oldrak, Zoltan, Padreia, Lubo),
# Key 3899 in the booby-trapped dead tree north of the tower, four skulls on the sacrifice stones to reach it, jungle
# grass and a switch plate for the stairs, six levers, the ghoul's crate, the key-3899 door, six fruit, two chess
# knights, the Riddler's three seals with A Prisoner's personal answer to 1 + 1, and the treasure room whose plates
# destroy rewards - two of: 10k (100 platinum coins), wooden wand, 32 talons, phoenix egg (decided with the user). Our
# map had every piece; nothing was scripted, the Riddler let any digit through and knew one of the four answers.
MISSIONS = [   # NPC, the storages it needs, what to say, the storage it sets
    ("Oldrak", {}, ["hugo", "myth", "yenny the gentle"], 6664),
    ("Zoltan", {6664: 1}, ["yenny the gentle", "crunors caress"], 6665),
    ("Padreia", {6664: 1, 6665: 1}, ["crunor's caress", "footnote"], 6666),
    ("Lubo", {6664: 1, 6665: 1, 6666: 1}, ["crunor's cottage", "flower guys", "accident", "stable"], 6667),
]
TREE = (32497, 31887, 7)
KEY_3899 = 3899
SKULL, MACHETE = 2229, 2420
STONES = [(32563, 31957, 1), (32565, 31957, 1), (32567, 31957, 1), (32569, 31957, 1)]
CARVING = (32566, 31957, 1)
ARRIVAL = (32479, 31923, 7)
SUMS = [49, 94, 13, 1]                  # A Prisoner's answers, storage 6668 = which


def _key_3899():
    from tibia74 import Item
    return Item(2089, attributes=bytes([4]) + KEY_3899.to_bytes(2, "little"))       # ATTR_ACTION_ID


@pytest.mark.parametrize("npc, needs, words, sets", MISSIONS, ids=[m[0] for m in MISSIONS])
def test_paradox_tower_missions(new_player, db, npc, needs, words, sets):
    from tibia74.quest import next_to, talk_to
    # premium: Zoltan lives in Edron, a premium area - a free character logs in at Thais (decided with the user
    # 2026-10-04, the premium login rule)
    p = next_to(new_player, npc_pos(npc), storage={30001: 1, **needs}, group_id=TESTER_GROUP, premium_days=30)
    said = talk_to(p, npc, "hi", *words)
    assert len(said) >= len(words), said
    p.logout()
    assert db.storage_after_logout(p.character.guid, sets, 1) == 1, (npc, said)


def test_paradox_tower_missions_come_in_order(new_player, db):
    """Zoltan tells anyone about Yenny, but only who has heard Oldrak's part has learned something."""
    from tibia74.quest import next_to, talk_to
    p = next_to(new_player, npc_pos("Zoltan"), storage={30001: 1}, group_id=TESTER_GROUP,
                premium_days=30)       # Edron is premium: a free character would log in at Thais
    said = talk_to(p, "Zoltan", "hi", "yenny the gentle", "crunors caress")
    assert any("Crunors Caress" in s for s in said), said
    p.logout()
    assert db.storage_after_logout(p.character.guid, 6665, None) is None


def test_paradox_tower_key_tree(new_player, items, world_map):
    from tibia74 import Item
    from tibia74.route import walk_next_to
    p = kazordoon_player(new_player, items=[Item(SHOVEL)])
    ability = dict(level=2000, rope=True, shovel=True)
    walk_next_to(p, items, world_map, TREE, **ability)
    use_map_item(p, items, TREE, "dead tree")
    assert p.wait_for(lambda: p.messages("You have found a copper key."), timeout=3), p.text_messages[-3:]
    assert carries(p, "copper key"), p.inventory_names()
    before = len(p.text_messages)
    p.sleep(1.1)
    use_map_item(p, items, TREE, "dead tree")
    assert p.wait_for(lambda: any("empty" in t for _, t in p.text_messages[before:]), timeout=3), p.text_messages[-3:]


def test_paradox_tower_sacrifice(new_player, items, world_map):
    """A skull on each of the four sacrifice stones and the carving between them: to the tower. Without the four
    skulls the carving does nothing; the four carvings by the arrival lead back."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, (32566, 31958, 1), items=[Item(SKULL, 4)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    step_onto(p, CARVING)                                       # no skulls: nothing
    p.sleep(1)
    assert p.pos == CARVING, p.pos
    for stone in STONES:
        walk_next_to(p, items, world_map, stone, level=2000)
        _drop_on(p, items, SKULL, stone)
    walk_next_to(p, items, world_map, CARVING, level=2000)
    step_onto(p, CARVING)
    assert p.wait_for(lambda: p.pos == ARRIVAL, timeout=3), p.pos
    for stone in STONES:                                        # the skulls are gone, poison fields instead
        assert not any(getattr(t, "client_id", None) == items.by_server[SKULL].client_id
                       for t in p.tiles.get(stone, [])), stone
    carvings = [(32486, 31927, 7), (32487, 31927, 7), (32486, 31928, 7), (32487, 31928, 7)]
    walk_next_to(p, items, world_map, carvings[0], level=2000, avoid=carvings)
    step_onto(p, carvings[0])
    assert p.wait_for(lambda: p.pos == (32566, 31958, 1), timeout=3), p.pos


def _drop_on(p, items, item_id, pos):
    """Drop one of a carried stack on a map tile (a skull on a sacrifice stone, fruit on a counter)."""
    client_id = items.by_server[item_id].client_id
    for cid, c in p.containers.items():
        for n, i in enumerate(c.items):
            if i.client_id == client_id:
                before = sum(1 for t in p.tiles.get(tuple(pos), []) if getattr(t, "client_id", None) == client_id)
                p.move_item(p.container_pos(cid, n), client_id, n, tuple(pos), 1)
                assert p.wait_for(lambda: sum(1 for t in p.tiles.get(tuple(pos), [])
                                              if getattr(t, "client_id", None) == client_id) > before, timeout=3), \
                    (pos, p.tiles.get(tuple(pos)), p.text_messages[-2:])
                return
    raise AssertionError(f"no {item_id} carried")



LEVERS = [(32476 + i, 31900, 6) for i in range(6)]
LEVER_ORDER = [1946, 1946, 1945, 1945, 1946, 1945]          # Right, Right, Left, Left, Right, Left
FRUIT = [2682, 2676, 2679, 2674, 2681, 2678]                # melon, banana, cherry, apple, grapes, coconut
WHITE_KNIGHT, BLACK_KNIGHT = 2628, 2634
RIDDLES = ["test", "yes", "goshnar", "demonbunny", "tha'kull", "yes", "breath", "silence", "old", "yes", "green",
           "none"]
TREASURE = dict(landing=(32478, 31905, 1), plates=[(x, y, 1) for y in (31902, 31903) for x in range(32476, 32482)],
                egg=(32477, 31900, 1), ten_k=(32478, 31900, 1), talons=(32479, 31900, 1), wand=(32480, 31900, 1))


def _on(p, items, pos, item_id):
    client_id = items.by_server[item_id].client_id
    return any(getattr(t, "client_id", None) == client_id for t in p.tiles.get(tuple(pos), []))


def _climb(p, items, ladder, z):
    use_map_item(p, items, ladder, "ladder")
    assert p.wait_for(lambda: p.pos and p.pos[2] == z, timeout=3), (p.pos, ladder)


def _ladder_at(p, items, pos):
    return p.wait_for(lambda: _on(p, items, pos, 1386), timeout=3)


def _switch(p, items, world_map, pos, **ability):
    from tibia74.route import walk_next_to
    walk_next_to(p, items, world_map, pos, **ability)
    use_map_item(p, items, pos, "switch")


def test_paradox_tower_climb(new_player, items, world_map):
    """From the arrival by the tower to the treasure: grass and the stairs, the levers, the ghoul's crate, the
    key-3899 door and the fruit, the chess knights, the Riddler with this player's answer (94), and the plates -
    straight up the west side destroys the 10k and the egg: the wand and the talons are left."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong, talk_to
    from tibia74.route import follow, use_tool, walk_next_to
    p = strong(new_player, ARRIVAL, group_id=TESTER_GROUP, storage={6668: 2},
               items=[Item(MACHETE), _key_3899(), *[Item(f) for f in FRUIT], Item(WHITE_KNIGHT), Item(BLACK_KNIGHT)])
    p.open_container(BACKPACK)
    ability = dict(level=2000, machete=True, keys={KEY_3899})

    # the ground floor: cut the plate free and step on it - the stone turns into stairs
    stairs, plate = (32478, 31902, 7), (32481, 31905, 7)
    follow(p, items, world_map, (32482, 31905, 7), **ability)       # east of it: stones on the other sides
    if _on(p, items, plate, 2782):
        use_tool(p, items, "machete", plate, {2782})
        assert p.wait_for(lambda: not _on(p, items, plate, 2782), timeout=3), p.tiles.get(plate)
    step_onto(p, plate)
    assert p.wait_for(lambda: _on(p, items, stairs, 1385), timeout=3), p.tiles.get(stairs)
    walk_next_to(p, items, world_map, stairs, open_tiles=[stairs], **ability)
    step_onto(p, stairs)
    assert p.wait_for(lambda: p.pos[2] == 6, timeout=3), p.pos

    # the levers Right, Right, Left, Left, Right, Left, the switch: a ladder
    for lever, want in zip(LEVERS, LEVER_ORDER):
        walk_next_to(p, items, world_map, lever, **ability)
        if not _on(p, items, lever, want):
            use_map_item(p, items, lever, "switch")
            p.sleep(1.1)
    _switch(p, items, world_map, (32479, 31905, 6), **ability)
    assert _ladder_at(p, items, (32479, 31903, 6)), p.tiles.get((32479, 31903, 6))
    walk_next_to(p, items, world_map, (32479, 31903, 6), **ability)
    _climb(p, items, (32479, 31903, 6), 5)

    # the ghoul's room: the switch makes a crate; in the north-west corner it makes the ladder (a tester in the room
    # pushes it there - the ghoul does it at random, and it does not go after testers)
    _switch(p, items, world_map, (32481, 31904, 5), **ability)
    pusher = new_player(pos=(32478, 31900, 5), group_id=TESTER_GROUP, storage={30001: 1})
    crate = items.by_server[1739].client_id
    assert pusher.wait_for(lambda: _on(pusher, items, (32479, 31901, 5), 1739), timeout=3), pusher.pos
    for src, dst in (((32479, 31901, 5), (32477, 31901, 5)), ((32477, 31901, 5), (32476, 31900, 5))):
        n = next(n for n, t in enumerate(pusher.tiles[src]) if getattr(t, "client_id", None) == crate)
        pusher.move_item(src, crate, n, dst, 1)
        assert pusher.wait_for(lambda: _on(pusher, items, dst, 1739), timeout=3), (dst, pusher.text_messages[-2:])
    assert _ladder_at(p, items, (32478, 31904, 5)), p.tiles.get((32478, 31904, 5))
    walk_next_to(p, items, world_map, (32478, 31904, 5), **ability)
    _climb(p, items, (32478, 31904, 5), 4)
    # out of the corner, the ladder goes
    n = next(n for n, t in enumerate(pusher.tiles[(32476, 31900, 5)]) if getattr(t, "client_id", None) == crate)
    pusher.move_item((32476, 31900, 5), crate, n, (32477, 31901, 5), 1)
    assert pusher.wait_for(lambda: not _on(pusher, items, (32478, 31904, 5), 1386), timeout=3)
    pusher.logout()

    # through the key-3899 door, the six fruit on the counters, the switch: a ladder
    for i, fruit in enumerate(FRUIT):
        counter = (32476 + i, 31900, 4)
        walk_next_to(p, items, world_map, counter, **ability)
        _drop_on(p, items, fruit, counter)
    _switch(p, items, world_map, (32479, 31905, 4), **ability)
    assert _ladder_at(p, items, (32476, 31904, 4)), p.tiles.get((32476, 31904, 4))
    walk_next_to(p, items, world_map, (32476, 31904, 4), **ability)
    _climb(p, items, (32476, 31904, 4), 3)

    # the white knight by Cedric, the black by Tristan, the switch: a ladder
    for piece, square in ((WHITE_KNIGHT, (32478, 31903, 3)), (BLACK_KNIGHT, (32479, 31903, 3))):
        walk_next_to(p, items, world_map, square, **ability)
        _drop_on(p, items, piece, square)
    _switch(p, items, world_map, (32478, 31904, 3), **ability)
    assert _ladder_at(p, items, (32479, 31904, 3)), p.tiles.get((32479, 31904, 3))
    walk_next_to(p, items, world_map, (32479, 31904, 3), **ability)
    _climb(p, items, (32479, 31904, 3), 2)

    # the Riddler: the three seals, and this player's 1 + 1
    talk_to(p, "Riddler", "hi", *RIDDLES, "94")
    assert p.wait_for(lambda: p.pos == TREASURE["landing"], timeout=5), (p.pos, p.text_messages[-3:])

    # straight up the west side: the plates destroy the egg (row 2) and the 10k (row 1)
    others = [t for t in TREASURE["plates"] if t[0] != 32476]
    walk_next_to(p, items, world_map, (32476, 31903, 1), avoid=others, **ability)
    step_onto(p, (32476, 31903, 1))
    step_onto(p, (32476, 31902, 1))
    for chest, found in ((TREASURE["talons"], "You have found 32 talons."),
                         (TREASURE["wand"], "You have found a wooden wand.")):
        walk_next_to(p, items, world_map, chest, avoid=others, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(found), timeout=3), p.text_messages[-3:]
        p.sleep(1.1)
    for chest in (TREASURE["egg"], TREASURE["ten_k"]):
        walk_next_to(p, items, world_map, chest, avoid=others, **ability)
        before = len(p.text_messages)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: any("empty" in t for _, t in p.text_messages[before:]), timeout=3), \
            p.text_messages[-3:]
        p.sleep(1.1)


def test_paradox_tower_riddler_wants_your_own_answer(new_player, items):
    """Another player's number is WRONG: down into Hellgate."""
    from tibia74.quest import next_to, talk_to
    p = next_to(new_player, (32479, 31902, 2), storage={30001: 1, 6668: 1}, group_id=TESTER_GROUP)
    talk_to(p, "Riddler", "hi", *RIDDLES, "94")                # player 1's is 49
    assert p.wait_for(lambda: p.pos == (32725, 31589, 12), timeout=5), (p.pos, p.text_messages[-3:])


# The climb south of the Kazordoon entrance: four ledges, each levitated up facing north (a tile you stand on, the
# tile ahead one floor up); then the level-30 gate and two ropes to the sacrifice stones.
LEDGES = [(32570, 31976, 7), (32571, 31974, 6), (32571, 31972, 5), (32571, 31971, 4)]
ABOVE_THE_LEDGES = (32571, 31970, 3)


def _levitate_up(p):
    from tibia74 import NORTH
    p.turn(NORTH)
    p.sleep(2.2)                                  # a spell's exhaustion (2 s) after the last one
    z = p.pos[2]
    p.say('exani hur "up')
    return p.wait_for(lambda: p.pos[2] == z - 1, timeout=3)


def test_paradox_tower_levitate_climb(new_player, items, world_map):
    """Levitate (premium, level 12) up the four ledges, through the level-30 gate, up the ropes: at the stones."""
    from tibia74.quest import strong
    from tibia74.route import follow
    from tibia74 import BACKPACK
    p = strong(new_player, LEDGES[0], level=50, vocation=1, maglevel=20, premium_days=30, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)                                  # the rope
    for ledge in LEDGES:
        if p.pos != ledge:
            follow(p, items, world_map, ledge, level=50)
        assert _levitate_up(p), (ledge, p.pos, p.text_messages[-2:])
    assert p.pos == ABOVE_THE_LEDGES, p.pos
    follow(p, items, world_map, (32566, 31958, 1), level=50, rope=True)


def test_paradox_tower_levitate_is_premium(new_player):
    """A free account cannot levitate: "You need a premium account." - the tower is a premium quest (TibiaWiki 2006,
    Tibiantis), and Levitate one of the ways up."""
    from tibia74.quest import strong
    p = strong(new_player, LEDGES[0], level=50, vocation=1, maglevel=20, premium_days=0, group_id=TESTER_GROUP)
    assert not _levitate_up(p), p.pos
    assert p.messages("You need a premium account."), p.text_messages[-3:]
    assert p.pos == LEDGES[0], p.pos


def test_paradox_tower_the_ghoul_pushes_the_crate(new_player, items):
    """The ghoul itself: "Wait until the ghoul pushes the box into the north-west corner of his area, and a ladder will
    appear". A player it can see but not reach (not a tester - testers are left alone) makes it move, and moving it
    pushes the crate; sooner or later into the corner. Up to five minutes."""
    import time
    from tibia74.quest import strong
    p = strong(new_player, (32479, 31905, 5), level=100, storage={30001: 1})       # an ordinary player: the ghoul's target
    ghoul_room = [(x, y, 5) for x in range(32476, 32482) for y in (31900, 31901)]
    assert p.wait_for(lambda: any(c.name.lower() == "ghoul" for c in p.creatures.values()), timeout=5), \
        ("no ghoul", [(c.name, c.pos) for c in p.creatures.values()])
    if not any(_on(p, items, t, 1739) for t in ghoul_room):
        use_map_item(p, items, (32481, 31904, 5), "switch")
    assert p.wait_for(lambda: any(_on(p, items, t, 1739) for t in ghoul_room), timeout=3), "no crate"
    deadline = time.time() + 300
    while time.time() < deadline and not _on(p, items, (32478, 31904, 5), 1386):
        p.sleep(1)
    crate_at = [t for t in ghoul_room if _on(p, items, t, 1739)]
    assert _on(p, items, (32478, 31904, 5), 1386), f"no ladder after 5 minutes; the crate is at {crate_at}"


def test_paradox_tower_parcels_climb(new_player, items, world_map):
    """No levitate for a free account - but three parcels on the tile you stand on, one step towards the ledge, and you
    are up ("Levitate or use parcels to climb", TibiaWiki): the climb itself is free."""
    from tibia74 import BACKPACK, NORTH, Item
    from tibia74.quest import strong
    from tibia74.route import follow
    parcels = [Item(2595) for _ in range(12)]
    p = strong(new_player, LEDGES[0], level=50, premium_days=0, items=parcels, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    for ledge in LEDGES:
        if p.pos != ledge:
            follow(p, items, world_map, ledge, level=50)
        for _ in range(3):
            _drop_on(p, items, 2595, ledge)
        z = p.pos[2]
        p.step(NORTH)
        assert p.wait_for(lambda: p.pos[2] == z - 1, timeout=3), (ledge, p.pos, p.text_messages[-2:])
    assert p.pos == ABOVE_THE_LEDGES, p.pos

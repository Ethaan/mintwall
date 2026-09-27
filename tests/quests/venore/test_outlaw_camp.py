"""The Outlaw Camp Quest (Bright Sword Quest) (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: keys 3301-3303 in three dead trees of the Outlaw Camp, the switch behind the key-3303 door moves the
# oven in front of the chest with golden key 3304; a barrel in the notch of the wall past the level-45 gate, the power
# ring on the wooden surface and its switch (the ring goes behind the mill room's wall, the right passage opens), the
# mill's switch (the ring turns into a fire field, the wall moves as far as the barrel lets it); the key-3304 door and
# the chest: Bright Sword and Red Gem (decided with the user). Our map had no key numbers on the four key doors,
# nothing scripted, the oven missing, the ring lying behind the wall, and no stone nor mill switch (tibiaot74's
# spots, decided with the user: the full mechanism).
OC = dict(
    trees={3301: (32617, 32250, 7), 3302: (32609, 32244, 7), 3303: (32651, 32244, 7)},
    oven_switch=(32614, 32173, 9), oven=(32623, 32188, 9), key_box=(32623, 32187, 9),
    payment=(32594, 32214, 9), ring_switch=(32594, 32212, 9), passage=[(32603, 32216, 9), (32604, 32216, 9)],
    ring_behind_wall=(32613, 32220, 10), mill_switch=(32616, 32222, 10), notch=(32614, 32209, 10),
    stone=(32614, 32206, 10), gate=(32602, 32207, 10), outside_gate=(32602, 32208, 10),
    door=(32620, 32199, 10), chest=(32620, 32198, 10),
)
POWER_RING, BARREL, STONE = 2166, 1774, 1304


def _on(p, items, pos, item_id):
    client_id = items.by_server[item_id].client_id
    return any(getattr(t, "client_id", None) == client_id for t in p.tiles.get(tuple(pos), []))


def test_outlaw_camp_keys(new_player, items, world_map):
    """The three keys from the trees; the key-3303 door, the switch that moves the oven, key 3304 behind it."""
    from tibia74 import Item
    from tibia74.route import walk_next_to
    p = venore_player(new_player, items=[Item(SHOVEL)])
    keys = set()
    ability = lambda: dict(level=2000, rope=True, shovel=True, keys=keys, floors=9)   # noqa: E731
    for number, (tree, kind) in ((3301, (OC["trees"][3301], "a copper key")), (3302, (OC["trees"][3302], "a silver key")),
                                 (3303, (OC["trees"][3303], "a copper key"))):
        collect(p, items, world_map, tree, "dead tree", [kind], **ability())
        keys.add(number)
    walk_next_to(p, items, world_map, OC["oven_switch"], **ability())
    use_map_item(p, items, OC["oven_switch"], "switch")
    collect(p, items, world_map, OC["key_box"], "box", ["a golden key"], open_tiles=[OC["oven"]], **ability())
    keys.add(3304)
    assert carries(p, "golden key"), p.inventory_names()


def test_outlaw_camp_bright_sword(new_player, items, world_map):
    """The power ring paid on the wooden surface turns up behind the mill room's wall; the barrel in its notch; the
    mill's switch: the ring becomes a fire field, the stone past the level-45 gate moves - and key 3304 opens the way
    to the Bright Sword and the Red Gem. The mill works once a day: a second flip is refused."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    key_3304 = Item(2091, attributes=bytes([4]) + (3304).to_bytes(2, "little"))
    # the ring on the wooden surface, the switch
    payer = strong(new_player, (32594, 32213, 9), items=[Item(POWER_RING)], group_id=TESTER_GROUP)
    payer.open_container(BACKPACK)
    ring = items.by_server[POWER_RING].client_id
    cid, n = next((cid, n) for cid, c in payer.containers.items() for n, i in enumerate(c.items) if i.client_id == ring)
    payer.move_item(payer.container_pos(cid, n), ring, n, OC["payment"], 1)
    assert payer.wait_for(lambda: _on(payer, items, OC["payment"], POWER_RING), timeout=3), payer.text_messages[-2:]
    use_map_item(payer, items, OC["ring_switch"], "switch")
    assert payer.wait_for(lambda: not _on(payer, items, OC["payment"], POWER_RING), timeout=3)
    assert payer.wait_for(lambda: all(not _on(payer, items, w, 1026) for w in OC["passage"]), timeout=3), \
        "the right passage did not open"
    payer.logout()
    # a barrel in the notch (a GM puts it there: barrels are dragged from the Plains of Havoc)
    gm = new_player(pos=OC["notch"], group_id=3, storage={30001: 1})
    gm.say("/i 1774")
    assert gm.wait_for(lambda: _on(gm, items, OC["notch"], BARREL), timeout=3), gm.tiles.get(OC["notch"])
    gm.step(0)                                                  # north, out of the notch
    gm.logout()
    # the mill's switch: the ring into a fire field, the stone moves
    miller = new_player(pos=(32617, 32221, 10), group_id=TESTER_GROUP, storage={30001: 1})
    assert miller.wait_for(lambda: _on(miller, items, OC["ring_behind_wall"], POWER_RING), timeout=3)
    use_map_item(miller, items, OC["mill_switch"], "switch")
    assert miller.wait_for(lambda: not _on(miller, items, OC["ring_behind_wall"], POWER_RING), timeout=3)
    before = len(miller.text_messages)
    miller.sleep(1.1)
    use_map_item(miller, items, OC["mill_switch"], "switch")    # once a day
    assert miller.wait_for(lambda: any("not possible" in t for _, t in miller.text_messages[before:]), timeout=3)
    miller.logout()
    # through the gate, the moved wall, the key-3304 door: the chest
    p = strong(new_player, OC["outside_gate"], items=[key_3304], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    assert p.wait_for(lambda: not _on(p, items, OC["stone"], STONE), timeout=3), "the stone did not move"
    from tibia74.route import follow
    follow(p, items, world_map, OC["door"], level=2000, keys={3304}, open_tiles=[OC["stone"]])   # into the doorway
    before = len(p.text_messages)
    use_map_item(p, items, OC["chest"], "chest")
    assert p.wait_for(lambda: sorted(t for _, t in p.text_messages[before:] if t.startswith("You have found"))
                      == ["You have found a bright sword.", "You have found a red gem."], timeout=3), p.text_messages[-3:]
    assert carries(p, "bright sword") and carries(p, "red gem"), p.inventory_names()


def test_outlaw_camp_level_door(new_player, items):
    assert_level_door(new_player, items, OC["gate"], OC["outside_gate"], 45)


def test_outlaw_camp_rules(world_map):
    # the stone blocks the way to the chest's door until the mill moves it; then key 3304
    assert_no_way(world_map, OC["outside_gate"], OC["door"], level=100, keys={3304})
    assert_no_way(world_map, OC["outside_gate"], OC["door"], level=100, open_tiles=[OC["stone"]])
    assert_way(world_map, OC["outside_gate"], OC["door"], level=100, keys={3304}, open_tiles=[OC["stone"]])

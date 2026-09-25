"""Alawar's Vault Quest, Senja and Folda (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006 spoiler. Short path (Senja): in the castle cellar "Use a Destroy Field on that fire field and pull the
# switch under it", north into the portal to the quest boxes - "Entering the portal in the quest box-room will take
# you to the roof of the castle". Long path (Folda): the chest behind fire fields holds copper key 4503, it opens the
# door of the "Protected Area", "Pick under" the fire field at its end and drop two floors (no way back up), key 4501
# in the minotaurs' first room (it opens their storage room), key 4502 in the maze (with the Dark Helmet bag), up the
# stairs and through the vault doors. Real-map table: 4501-4505. Ferry: Nielson north of Carlin, 20 gp.
# Our map: the three keys lay loose where their chests had been (the containers were lost), the doors had no key
# numbers, the vault chests were missing, the switch had no script. Decided with the user 2026-09-25: the walls and
# the switch come back after 2 minutes; the vault portal goes to the castle roof (the map sent you back behind the walls).
ALAWAR = dict(
    folda=(32047, 31581, 7), senja=(32125, 31666, 7),
    key_4503=(32031, 31686, 8), key_4501=(32172, 31602, 10), key_4502=(32201, 31571, 10),
    protected_door=(32035, 31642, 8), pick_spot=(32040, 31636, 8), below=(32040, 31636, 10),
    vault_chests=[((32105, 31567, 9), "3 white pearls"), ((32109, 31567, 9), "a broad sword")],
    vault=(32107, 31567, 9), portal=(32107, 31566, 9), roof=(32189, 31625, 4),
    switch=(32180, 31633, 8), walls=[(x, 31626, 8) for x in range(32186, 32190)],
    cellar_portal=(32187, 31622, 8),
)
DESTROY_FIELD, SWITCH, MAGIC_WALL = 2261, 1945, 1497
MAZE_BAG = ["copper key", "dark helmet", "throwing knife", "blank rune", "gold coin"]


def _sail(p, items, world_map, where, arrival):
    from tibia74.quest import npc_pos, talk_to
    from tibia74.route import walk_near
    walk_near(p, items, world_map, npc_pos("Nielson"), level=1)
    said = talk_to(p, "Nielson", "hi", where, "yes")
    assert p.wait_for(lambda: p.pos == arrival, timeout=5), (p.pos, said)


def _open(p, items, world_map, pos, what, found, **ability):
    from tibia74.route import walk_next_to
    walk_next_to(p, items, world_map, pos, **ability)
    use_map_item(p, items, pos, what)
    assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), p.text_messages[-3:]
    p.sleep(1.1)


def test_alawars_vault_long_path(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import open_carried, strong
    from tibia74.route import follow
    A = ALAWAR
    p = strong(new_player, CARLIN_TEMPLE, items=[Item(PICK), Item(2148, 50)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    _sail(p, items, world_map, "folda", A["folda"])

    ability = dict(level=1, rope=True, pick=True)
    _open(p, items, world_map, A["key_4503"], "chest", "a copper key", **ability)       # through the fire fields
    use_map_item(p, items, A["key_4503"], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
    p.sleep(1.1)

    # the Protected Area, the pick under the fire field, two floors down
    follow(p, items, world_map, A["below"], keys={4503}, **ability)
    _open(p, items, world_map, A["key_4501"], "box", "a copper key", **ability)
    _open(p, items, world_map, A["key_4502"], "chest", "a bag", **ability)
    bag = open_carried(p, items, "bag")
    assert p.wait_for(lambda: sorted(i.name for i in bag.items) == sorted(MAZE_BAG), timeout=3), bag.items
    counts = {i.name: i.count for i in bag.items}
    assert counts["throwing knife"] == 4 and counts["gold coin"] == 33, counts

    keys = {4501, 4502, 4503}
    for chest, found in A["vault_chests"]:                                               # up, the vault doors
        _open(p, items, world_map, chest, "chest", found, keys=keys, **ability)
    assert carries(p, "white pearl") and carries(p, "broad sword"), p.inventory_names()

    follow(p, items, world_map, (A["portal"][0], A["portal"][1] + 1, A["portal"][2]), keys=keys, **ability)
    step_onto(p, A["portal"])
    assert p.wait_for(lambda: p.pos == A["roof"], timeout=3), p.pos                     # the castle roof
    follow(p, items, world_map, A["senja"], **ability)


def test_alawars_vault_short_path(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import _destroy_fields, follow, walk_next_to
    A = ALAWAR
    p = strong(new_player, CARLIN_TEMPLE, items=[Item(DESTROY_FIELD, 3), Item(2148, 50)], maglevel=10,
               group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    _sail(p, items, world_map, "senja", A["senja"])
    has = lambda pos, sid: any(i.client_id == sid for i in p.tile_items(pos))          # noqa: E731

    ability = dict(level=1)
    walk_next_to(p, items, world_map, A["switch"], **ability)
    _destroy_fields(p, items, A["switch"])
    use_map_item(p, items, A["switch"], "switch")
    assert p.wait_for(lambda: not has(A["switch"], SWITCH), timeout=3), p.tiles.get(A["switch"])   # it vanishes
    open_walls = set(A["walls"])
    follow(p, items, world_map, (A["cellar_portal"][0], A["cellar_portal"][1] + 1, 8), open_tiles=open_walls,
           **ability)
    assert not any(has(w, MAGIC_WALL) for w in A["walls"]), [p.tiles.get(w) for w in A["walls"]]
    step_onto(p, A["cellar_portal"])
    assert p.wait_for(lambda: p.pos == (32108, 31567, 9), timeout=3), p.pos
    for chest, found in A["vault_chests"]:
        _open(p, items, world_map, chest, "chest", found, **ability)
    for chest, _ in A["vault_chests"]:                                                   # once each
        before = len(p.messages("The chest is empty."))
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: len(p.messages("The chest is empty.")) > before, timeout=3), p.text_messages[-2:]
        p.sleep(1.1)
    follow(p, items, world_map, (A["portal"][0], A["portal"][1] + 1, A["portal"][2]), **ability)
    step_onto(p, A["portal"])
    assert p.wait_for(lambda: p.pos == A["roof"], timeout=3), p.pos


def test_senja_walls_come_back(new_player, items, world_map):
    """The switch opens the walls for 2 minutes (decided with the user); then walls and switch are back."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import _destroy_fields, follow, walk_next_to
    A = ALAWAR
    p = strong(new_player, (32181, 31634, 8), items=[Item(DESTROY_FIELD, 3)], maglevel=10, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    has = lambda pos, sid: any(i.client_id == sid for i in p.tile_items(pos))          # noqa: E731
    walk_next_to(p, items, world_map, A["switch"], level=1)
    # the short path test may have pulled it a moment ago (one server for all tests)
    assert p.wait_for(lambda: has(A["switch"], SWITCH), timeout=150), p.tiles.get(A["switch"])
    _destroy_fields(p, items, A["switch"])
    use_map_item(p, items, A["switch"], "switch")
    assert p.wait_for(lambda: not has(A["switch"], SWITCH), timeout=3), p.tiles.get(A["switch"])
    follow(p, items, world_map, (32184, 31629, 8), level=1)            # sees the switch and the walls (+-6 rows)
    assert p.wait_for(lambda: A["walls"][0] in p.tiles and not any(has(w, MAGIC_WALL) for w in A["walls"]),
                      timeout=3), [p.tiles.get(w) for w in A["walls"]]
    p.sleep(95)
    assert not any(has(w, MAGIC_WALL) for w in A["walls"]), "the walls came back too early"
    assert p.wait_for(lambda: all(has(w, MAGIC_WALL) for w in A["walls"]) and has(A["switch"], SWITCH), timeout=30), \
        (p.pos, [p.tiles.get(w) for w in A["walls"] + [A["switch"]]])


def test_alawars_vault_rules(world_map):
    A = ALAWAR
    pick_side = (A["pick_spot"][0] - 1, A["pick_spot"][1], 8)
    assert_no_way(world_map, A["folda"], pick_side, level=1, rope=True, pick=True)                   # key 4503
    assert_way(world_map, A["folda"], pick_side, level=1, rope=True, keys={4503})                    # no level
    assert_no_way(world_map, A["below"], A["vault"], level=1, rope=True, keys={4501, 4503})           # key 4502
    assert_way(world_map, A["below"], A["vault"], level=1, keys={4502})
    # no way back up from the minotaur level (TibiaWiki: "you cannot return here"): only through the vault
    assert_no_way(world_map, A["below"], A["folda"], level=1, rope=True, pick=True, keys={4501, 4503})
    assert_no_way(world_map, A["below"], A["senja"], level=1, rope=True, pick=True, keys={4501, 4503})
    assert_way(world_map, A["below"], A["senja"], level=1, keys={4502})                              # the portal
    # Senja: the walls keep you from the cellar portal until the switch is pulled
    inside = (A["cellar_portal"][0], A["cellar_portal"][1] + 1, 8)
    assert_no_way(world_map, A["senja"], inside, level=1)
    assert_way(world_map, A["senja"], inside, level=1, open_tiles=A["walls"])
    assert_way(world_map, A["vault"], A["senja"], level=1)                                           # the roof

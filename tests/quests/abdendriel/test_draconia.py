"""Draconia Quest, through Hellgate under Ab'Dendriel (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: key 3012 from Elathriel (5000 gp) opens Hellgate, the portal, the long way down and up to Draconia
# island, the pyramid: keys 3001-3008 - daily, lying where the wiki puts them (decided with the user 2026-09-26: first
# come after each server start) - the ground floor's two levers (a wall, a rock), the 3rd floor's floor switches for two
# players, the level-25 gate in front of the reward, the top floor's levers Left, Right, Left, Right and the portal to
# Ab'Dendriel. Reward: ice rapier + serpent sword, stone skin amulet + energy ring (two chests, decided with the user).
# Our map had the keys without numbers, the doors without key numbers, nothing scripted.
D = dict(
    elathriel_key=3012,
    skeleton=(32794, 31572, 7), coffin=(32802, 31576, 7),
    lever_wall=(32792, 31595, 7), lever_rock=(32792, 31579, 7), wall=(32792, 31581, 7), rock=(32790, 31594, 7),
    keys={3003: (32790, 31593, 7), 3004: (32807, 31576, 6), 3005: (32792, 31591, 6), 3006: (32801, 31579, 6),
          3007: (32813, 31576, 5)},
    south_plate=(32810, 31595, 5), sw_plate=(32794, 31595, 5), sw_wall=(32796, 31595, 5), nw_wall=(32795, 31578, 5),
    bookcase=(32800, 31582, 2), gate=(32804, 31583, 2), outside_gate=(32804, 31584, 2),
    chests=[((32803, 31582, 2), ["You have found an ice rapier.", "You have found a serpent sword."]),
            ((32804, 31582, 2), ["You have found a stone skin amulet.", "You have found an energy ring."])],
    top_levers=[(32802, 31584, 1), (32803, 31584, 1), (32804, 31584, 1), (32805, 31584, 1)],
    portal=(32805, 31587, 1), ab_dendriel_stone=(32701, 31639, 6), portal_back=(32803, 31587, 1),
)
LEFT, RIGHT, MAGIC_FIELDS = 1945, 1946, (1487, 1488, 1489, 1490, 1491, 1492, 1493, 1494, 1495, 1496)
DESTROY_FIELD = 2261


def _found(p, before):
    return sorted(t for _, t in p.text_messages[before:] if t.startswith("You have found"))


def test_draconia_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import npc_pos, open_map_container, pick_up, strong, take, talk_to
    from tibia74.route import _destroy_fields, follow, walk_near, walk_next_to
    p = strong(new_player, ABDENDRIEL_TEMPLE, items=[Item(2152, 50), Item(DESTROY_FIELD, 3)], maglevel=10,
               group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    keys = set()
    ability = lambda **kw: dict(level=2000, rope=True, keys=keys, floors=9, **kw)       # noqa: E731

    # Elathriel sells the Hellgate key
    walk_near(p, items, world_map, npc_pos("Elathriel"), **ability())
    said = talk_to(p, "Elathriel", "hi", "key", "yes")
    assert any("Here it is." in s for s in said), said
    keys.add(3012)

    # ground floor: key 3001 in the skeleton, 3002 in the coffin, the levers, 3003 behind the rock
    walk_next_to(p, items, world_map, D["skeleton"], **ability())
    skeleton = open_map_container(p, items, D["skeleton"], "dead skeleton")
    take(p, items, skeleton, "silver key")
    keys.add(3001)
    walk_next_to(p, items, world_map, D["coffin"], **ability())
    use_map_item(p, items, D["coffin"], "wooden coffin")
    assert p.wait_for(lambda: p.messages("You have found a silver key."), timeout=3), p.text_messages[-2:]
    keys.add(3002)
    walk_next_to(p, items, world_map, D["lever_wall"], **ability())
    use_map_item(p, items, D["lever_wall"], "switch")
    opened = [D["wall"]]
    walk_next_to(p, items, world_map, D["lever_rock"], **ability(open_tiles=opened))
    use_map_item(p, items, D["lever_rock"], "switch")
    opened.append(D["rock"])
    for number in (3003, 3004, 3005, 3006):                              # 2nd floor: 3004 under an energy field
        spot = D["keys"][number]
        walk_next_to(p, items, world_map, spot, **ability(open_tiles=opened))
        if any(i.client_id in {items.by_server[f].client_id for f in MAGIC_FIELDS} for i in p.tile_items(spot)):
            _destroy_fields(p, items, spot)
        pick_up(p, items, spot, "silver key")
        keys.add(number)
        p.sleep(0.5)

    # 3rd floor: a friend holds the SW room's switch, the hero the south one, then off to key 3007
    walk_next_to(p, items, world_map, D["south_plate"], **ability(open_tiles=opened))
    step_onto(p, D["south_plate"])
    friend = new_player(pos=(D["sw_plate"][0] + 1, D["sw_plate"][1], 5), group_id=TESTER_GROUP, storage={30001: 1})
    step_onto(friend, D["sw_plate"])
    assert p.wait_for(lambda: not any(i.client_id == items.by_server[1026].client_id
                                      for i in friend.tile_items(D["nw_wall"])), timeout=3), friend.tiles.get(D["nw_wall"])
    opened += [D["nw_wall"]]
    walk_next_to(p, items, world_map, D["keys"][3007], **ability(open_tiles=opened))
    pick_up(p, items, D["keys"][3007], "silver key")
    keys.add(3007)

    # the 6th floor: key 3008 in the western bookcase, the level-25 gate, the two chests
    walk_next_to(p, items, world_map, D["bookcase"], **ability(open_tiles=opened))
    bookcase = open_map_container(p, items, D["bookcase"], "bookcase")
    take(p, items, bookcase, "silver key")
    keys.add(3008)
    follow(p, items, world_map, D["gate"], **ability(open_tiles=opened))          # into the gate's doorway
    for chest, found in D["chests"]:
        before = len(p.text_messages)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: _found(p, before) == sorted(found), timeout=3), _found(p, before)
        p.sleep(1.1)

    # the top floor: Left, Right, Left, Right, and the portal to Ab'Dendriel
    for lever, want in zip(D["top_levers"], (LEFT, RIGHT, LEFT, RIGHT)):
        walk_next_to(p, items, world_map, lever, **ability(open_tiles=opened))
        if not any(i.client_id == items.by_server[want].client_id for i in p.tile_items(lever)):
            use_map_item(p, items, lever, "switch")
            p.sleep(1.1)
    walk_next_to(p, items, world_map, D["portal"], **ability(open_tiles=opened))
    step_onto(p, D["portal"])
    assert p.wait_for(lambda: p.pos == D["ab_dendriel_stone"], timeout=3), p.pos


def test_draconia_level_door(new_player, items):
    assert_level_door(new_player, items, D["gate"], D["outside_gate"], 25)


def test_draconia_rules(world_map):
    ability = dict(level=100, rope=True, floors=9)
    beside_skeleton = D["skeleton"]                                 # the dead skeleton lies on a walkable tile
    # the Hellgate key: no way in without it
    assert_no_way(world_map, ABDENDRIEL_TEMPLE, (32675, 31665, 10), **ability)
    assert_way(world_map, ABDENDRIEL_TEMPLE, (32675, 31665, 10), keys={3012}, **ability)
    # each key opens the next door: without 3001 no way to the coffin
    assert_no_way(world_map, ABDENDRIEL_TEMPLE, (32801, 31576, 7), keys={3012}, **ability)
    assert_way(world_map, ABDENDRIEL_TEMPLE, (32801, 31576, 7), keys={3012, 3001}, **ability)
    # the 3rd floor's NW wall keeps key 3007 away until the switches are held
    all_keys = {3012, 3001, 3002, 3003, 3004, 3005, 3006}
    walls = [(32792, 31581, 7), (32790, 31594, 7)]
    assert_no_way(world_map, beside_skeleton, (32812, 31577, 5), keys=all_keys, open_tiles=walls, **ability)
    assert_way(world_map, beside_skeleton, (32812, 31577, 5), keys=all_keys,
               open_tiles=walls + [(32796, 31595, 5), (32795, 31578, 5)], **ability)


def test_draconia_top_portal_wants_the_levers(new_player, items):
    """With the levers otherwise (all left, as the map starts), the portal puts you back."""
    # the whole quest may have set them right a moment ago (one server): turn one back first
    fixer = new_player(pos=D["top_levers"][2], group_id=TESTER_GROUP, storage={30001: 1})
    lever = D["top_levers"][1]
    if any(i.client_id == items.by_server[RIGHT].client_id for i in fixer.tile_items(lever)):
        use_map_item(fixer, items, lever, "switch")
        fixer.sleep(1.1)
    fixer.logout()
    p = new_player(pos=(32805, 31586, 1), group_id=TESTER_GROUP, storage={30001: 1})
    step_onto(p, D["portal"])
    assert p.wait_for(lambda: p.pos == D["portal_back"], timeout=3), p.pos

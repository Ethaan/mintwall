"""The Ancient Tombs Quest: Ashmunrah's tomb, the Ankrahmun Library Tomb, and the helmet (docs/reference-74/quests.md)."""
from quests.ankrahmun.tombs import *  # noqa: F401,F403

# Current wiki: "Kill Ashmunrah last [...] To enter the teleporter to the reward room, all the switches must be switched
# to the right [...] Put all 7 pieces of the Helmet of the Ancients on the small stone table to the north to get your
# reward"; TibiaWiki 2006: "place a Small Ruby on the helmet. Each ruby will only last [...] 30 minutes". Our map: the
# hall's rows of invisible walls leave one gap each (the wiki's path), the searing fires cycle (iomapotbm.cpp); the
# four switches were lost from their altar stones (placed at tibiaot74's spots), the table and the ruby had no script.
ENTRANCE = (33159, 32835, 7)
FLAME, BASIN, BELOW = (33162, 32831, 10), (33161, 32831, 10), (33148, 32870, 11)
TOMB = Tomb(entrance=ENTRANCE, flame=FLAME, basin=BASIN, below=BELOW, pharaoh="Ashmunrah", lair=(33179, 32884, 11),
            pass_item=None, portal=(33179, 32890, 11), room=(33198, 32886, 11), sarcophagus=None, piece=None,
            back=(33159, 32836, 7))
GATE = (33149, 32871, 11)
TO_ASHMUNRAH = (33193, 32908, 11)
ASHMUNRAH_ROOM = (33179, 32879, 11)
SWITCHES = [(33175, 32884, 11), (33176, 32880, 11), (33182, 32880, 11), (33183, 32884, 11)]
TABLE = (33198, 32876, 11)
PIECES = [2335, 2336, 2337, 2338, 2339, 2340, 2341]
HELMET, GLOWING, SMALL_RUBY = 2342, 2343, 2147
EXIT = (33198, 32887, 11)


def _switches_right(p, items, world_map):
    from tibia74.route import walk_next_to
    right = items.by_server[1946].client_id
    for switch in SWITCHES:
        if any(getattr(t, "client_id", None) == right for t in p.tiles.get(switch, [])):
            continue
        walk_next_to(p, items, world_map, switch, level=2000)
        use_map_item(p, items, switch, "switch")
        assert p.wait_for(lambda: any(getattr(t, "client_id", None) == right for t in p.tiles.get(switch, [])),
                          timeout=3), p.tiles.get(switch)
        p.sleep(1.1)


def test_ashmunrah_tomb_and_the_helmet(new_player, items, world_map):
    from tibia74 import Item
    from tibia74.route import follow
    p = tomb_player(new_player, items=[Item(i) for i in PIECES] + [Item(SMALL_RUBY)])
    ability = dict(level=2000, shovel=True, rope=True, floors=12)
    follow(p, items, world_map, TOMB.flame, **ability)
    sacrifice_coin(p, items, TOMB)

    follow(p, items, world_map, (TO_ASHMUNRAH[0] - 1, TO_ASHMUNRAH[1], 11), **ability)   # the hall, the fire
    step_onto(p, TO_ASHMUNRAH)
    assert p.wait_for(lambda: p.pos == ASHMUNRAH_ROOM, timeout=3), p.pos
    kill_pharaoh(p, items, world_map, TOMB, **ability)

    follow(p, items, world_map, (TOMB.portal[0], TOMB.portal[1] - 1, 11), **ability)
    step_onto(p, TOMB.portal)                                    # switches left: back into the room
    assert p.wait_for(lambda: p.pos == (33179, 32889, 11), timeout=3), p.pos
    _switches_right(p, items, world_map)
    follow(p, items, world_map, (TOMB.portal[0], TOMB.portal[1] - 1, 11), **ability)
    step_onto(p, TOMB.portal)
    assert p.wait_for(lambda: p.pos == TOMB.room, timeout=3), p.pos

    follow(p, items, world_map, (TABLE[0], TABLE[1] + 1, 11), **ability)
    for piece in PIECES:
        if piece != PIECES[-1]:
            drop_on(p, items, piece, TABLE)
        else:                                                    # the last one: the pieces become the helmet
            client_id = items.by_server[piece].client_id
            cid, n = next((cid, n) for cid, c in p.containers.items() for n, i in enumerate(c.items)
                          if i.client_id == client_id)
            p.move_item(p.container_pos(cid, n), client_id, n, TABLE, 1)
    helmet = items.by_server[HELMET].client_id
    assert p.wait_for(lambda: any(getattr(t, "client_id", None) == helmet for t in p.tiles.get(TABLE, [])),
                      timeout=3), p.tiles.get(TABLE)
    assert not any(getattr(t, "client_id", None) in {items.by_server[i].client_id for i in PIECES}
                   for t in p.tiles.get(TABLE, [])), p.tiles.get(TABLE)

    from tibia74.quest import pick_up
    pick_up(p, items, TABLE, "helmet of the ancients")
    from tibia74.route import carried
    helmet_at = carried(p, items, lambda n: n == "helmet of the ancients")
    ruby_at = carried(p, items, lambda n: n == "small ruby")
    p.use_item_with(*helmet_at, ruby_at[0], ruby_at[1], ruby_at[2])
    glowing = items.by_server[GLOWING].client_id
    assert p.wait_for(lambda: any(i.client_id == glowing for c in p.containers.values() for i in c.items), timeout=3), \
        p.text_messages[-2:]
    assert not carries(p, "small ruby")

    follow(p, items, world_map, (EXIT[0], EXIT[1] - 1, 11), **ability)
    step_onto(p, EXIT)
    assert p.wait_for(lambda: p.pos == TOMB.back, timeout=3), p.pos


def test_ashmunrah_rules(new_player, items, world_map):
    assert_level_door(new_player, items, GATE, (GATE[0], GATE[1] - 1, 11), 75)
    # the hall's invisible walls: one way across each row
    assert_way(world_map, BELOW, (33193, 32907, 11), level=2000)
    assert_no_way(world_map, ASHMUNRAH_ROOM, TOMB.room, level=2000)

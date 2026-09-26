"""The Ancient Temple's two drawbridges (Thais, floor 10; docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki: "If the bridge is up, pull the lever". The levers had no script; the bridges lie down on our map. A pull
# raises a lowered bridge (each tile back to its column's water) and lowers a raised one (quests/ancient_temple_drawbridges.lua).
BRIDGES = [dict(lever=(32413, 32230, 10), bank=(32413, 32231, 10), tiles=[(32410, 32231, 10), (32411, 32232, 10), (32412, 32231, 10)],
                water={(32410, 32231, 10): 508, (32411, 32232, 10): 493, (32412, 32231, 10): 493}),
           dict(lever=(32417, 32254, 10), bank=(32411, 32253, 10), tiles=[(32408, 32253, 10), (32409, 32253, 10), (32410, 32253, 10)],
                water={(32408, 32253, 10): 508, (32409, 32253, 10): 493, (32410, 32253, 10): 509})]
DRAWBRIDGE = 1284


def test_ancient_temple_drawbridges(new_player, items):
    from tibia74.quest import next_to
    for b in BRIDGES:
        p = next_to(new_player, b["lever"], group_id=TESTER_GROUP, storage={30001: 1})
        # the far end of the southern bridge is out of the puller's view (x +-8): someone on the bridge's bank watches
        watcher = new_player(pos=b["bank"], group_id=TESTER_GROUP, storage={30001: 1})
        ground = lambda pos: watcher.tile_items(pos)[0].client_id if watcher.tile_items(pos) else None   # noqa: E731
        bridge = items.by_server[DRAWBRIDGE].client_id
        assert watcher.wait_for(lambda: all(ground(t) == bridge for t in b["tiles"]), timeout=3), \
            [p.tiles.get(t) for t in b["tiles"]]
        use_map_item(p, items, b["lever"], "switch")                        # up
        assert watcher.wait_for(lambda: all(ground(t) == items.by_server[b["water"][t]].client_id for t in b["tiles"]),
                          timeout=3), [p.tiles.get(t) for t in b["tiles"]]
        p.sleep(1.1)
        use_map_item(p, items, b["lever"], "switch")                        # and down again
        assert watcher.wait_for(lambda: all(ground(t) == bridge for t in b["tiles"]), timeout=3), \
            [p.tiles.get(t) for t in b["tiles"]]
        p.logout()
        watcher.logout()

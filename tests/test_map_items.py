"""Items the map places."""
import time

from tibia74.quest import next_to
from tibia74.server import TESTER_GROUP


def test_map_bodies_do_not_decay(server, new_player, items):
    """7.4: the dead humans and skeletons lying in caves stay (quest bodies among them). A dead skeleton decays 10
    minutes after it is dropped; the map's ones never start (iomapotbm.cpp) - they were gone 10 minutes after each
    server start. Run alone this waits until the server has been up 11 minutes; in the full suite it is long past."""
    skeleton = (32305, 32254, 9)          # the Battle Axe Quest's dead skeleton (Thais sewers), item 3103
    wait = server.started_at + 11 * 60 - time.time()
    if wait > 0:
        time.sleep(wait)
    p = next_to(new_player, skeleton, group_id=TESTER_GROUP, storage={30001: 1})
    body = items.by_server[3103].client_id
    assert p.wait_for(lambda: any(i.client_id == body for i in p.tile_items(skeleton)), timeout=3), \
        p.tiles.get(skeleton)

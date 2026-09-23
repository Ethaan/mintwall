"""Timed save (docs/production-plan.md §3): players are saved while online, not only on logout.
The test server runs it every 15 s (tibia74/server.py sets SaveInterval); production uses 600 s."""
import re
import time

from tibia74 import EAST

ROAD = (32097, 32205, 7)             # Rookgaard, north of the temple: walkable, no other test stands here


def test_an_online_player_is_saved_without_logging_out(new_player, server, db):
    p = new_player(pos=ROAD, level=8, storage={30001: 1})
    guid = p.character.guid
    start_log = server.log_offset()
    assert p.step(EAST), f"could not step east from {p.pos}"
    moved = p.pos
    deadline = time.time() + 40
    while time.time() < deadline:
        row = db.character(guid)
        if (row["posx"], row["posy"], row["posz"]) == moved:
            break
        time.sleep(1)
    assert p.connected, "the player logged out - this must be saved while online"
    row = db.character(guid)
    assert (row["posx"], row["posy"], row["posz"]) == moved, \
        f"database still has {(row['posx'], row['posy'], row['posz'])}, the player stands at {moved}"
    saves = re.findall(r"> Server saved in (\d+) ms", server.log()[start_log:])
    assert saves, "no '> Server saved' line in the log"


def test_logging_back_in_right_away_keeps_the_newest_state(new_player, server, items):
    """The logout save is written in the background (dbwriter.h); an immediate login must wait for it."""
    from tibia74 import GameClient
    p = new_player(pos=(ROAD[0], ROAD[1] + 2, ROAD[2]), level=8, storage={30001: 1})
    character = p.character
    for _ in range(3):
        assert p.step(EAST), f"could not step east from {p.pos}"
        p.sleep(0.7)
    moved = p.pos
    p.logout()
    again = GameClient(items, port=server.port).login(character.account, character.password, character.name)
    try:
        assert again.pos == moved, f"logged back in at {again.pos}, logged out at {moved}"
    finally:
        again.logout()

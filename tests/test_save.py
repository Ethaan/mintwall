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


HOUSE_ID, HOUSE_TILE = 4, (32391, 32150, 7)       # a Thais house (Tibia74.otbm): clear marble floor
SAVE_LINE = re.compile(r"> Server saved in \d+ ms \(\d+ players, (\d+) (changed houses|houses \(all\))")


def _next_save(server, since, timeout=40):
    """(houses written, full?) of the first timed save logged after the log offset `since`."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        m = SAVE_LINE.search(server.log()[since:])
        if m:
            return int(m.group(1)), m.group(2) != "changed houses", since + m.end()
        time.sleep(0.5)
    raise AssertionError("no timed save logged")


def test_a_timed_save_writes_only_houses_that_changed(new_player, server, db, items):
    """The timed save used to rewrite every house (~22 ms of game thread each time); now only changed ones,
    with a full save every 6th time as a safety net."""
    from tibia74 import RIGHT, Item
    sword = 2376
    gm = new_player(pos=HOUSE_TILE, group_id=3, inventory={RIGHT: Item(sword)})   # a GM may drop items anywhere
    assert gm.pos == HOUSE_TILE, gm.pos
    gm.move_item(gm.inventory_pos(RIGHT), gm.inventory[RIGHT].client_id, 0, gm.pos, 1)
    assert gm.wait_for(lambda: RIGHT not in gm.inventory, timeout=3), gm.text_messages[-2:]
    since = server.log_offset()

    houses, full, since = _next_save(server, since)
    while full:                                      # the hourly full save: look at the next one
        houses, full, since = _next_save(server, since)
    assert houses >= 1, "the house with the dropped sword was not saved"

    houses, full, since = _next_save(server, since)
    if not full:
        assert houses == 0, f"{houses} houses written although nothing changed"

    con = db._connect()
    try:
        blob = con.execute("SELECT data FROM map_store WHERE house_id = ?", (HOUSE_ID,)).fetchone()[0]
    finally:
        con.close()
    assert sword.to_bytes(2, "little") in bytes(blob), "the sword is not in the house's saved items"


INFO_LINE = re.compile(r"> Server saved in \d+ ms \(\d+ players, \d+ (changed houses|houses \(all\)), (\d+) house infos")
OLD_LINE = re.compile(r"> Server saved in \d+ ms \((?:(?!house infos)[^\n])*\n")     # a whole line without the count


def _next_info_save(server, since, timeout=40):
    """(house infos written, full?) of the first timed save logged after the log offset `since`."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        log = server.log()[since:]
        m = INFO_LINE.search(log)
        if m:
            return int(m.group(2)), m.group(1) != "changed houses", since + m.end()
        assert not OLD_LINE.search(log), \
            "the save line has no 'N house infos' count - an old avesta74.exe? (server\\build.bat)"
        time.sleep(0.5)
    raise AssertionError("no timed save logged")


def test_a_timed_save_writes_only_the_house_infos_that_changed(new_player, server, db):
    """The houses table (owner, rent) and house_lists (guest, subowner and door lists) used to be rewritten for every
    house on each save; now only for houses whose info changed (House::isInfoChanged), all of them at a full save."""
    heir = db.create_character(storage={30001: 1})
    gm = new_player(pos=HOUSE_TILE, group_id=3, storage={30001: 1})    # God: may stand in any house
    assert gm.pos == HOUSE_TILE, gm.pos
    since = server.log_offset()
    gm.say(f"/owner {heir.name}")

    infos, full, since = _next_info_save(server, since)
    while full:                                      # the hourly full save: look at the next one
        infos, full, since = _next_info_save(server, since)
    assert infos >= 1, "the house with a new owner was not saved"
    con = db._connect()
    try:
        row = con.execute("SELECT owner FROM houses WHERE id = ?", (HOUSE_ID,)).fetchone()
    finally:
        con.close()
    assert row and row[0] == heir.guid, f"houses row of house {HOUSE_ID}: {row}, the owner is {heir.guid}"

    infos, full, since = _next_info_save(server, since)
    if full:
        infos, full, since = _next_info_save(server, since)
    assert not full and infos == 0, f"{infos} house infos written although none changed"

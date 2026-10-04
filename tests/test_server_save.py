"""The daily server save (task.md "Daily server save"; Q5 decided with the user 2026-10-04: like Tibiantis - every day
at one hour, about 10 minutes offline - at config.lua ServerSaveHour). globalevents/scripts/serversave.lua:
warnings 5, 3 and 1 minutes before, no logins from 5 minutes before, then everyone kicked, the houses of owners
without premium released (items to the depot of the house's town), everything saved with the house rent
(Houses::payHouses: the warning letter in the depot), and the server exits with code 10 for its supervisor.

This module runs a server of its own (the save shuts it down): on a free port the system picks, in
<MINTWALL_TEST_RUN>/server-save.
Its config: ServerSaveTestIn = 60 (the save 60 s after the start, not at the hour), ServerSaveTestMinute = 6 (a
warning "minute" lasts 6 s: warnings 30, 18 and 6 s before). One run, several tests reading what it left."""
import socket
import sqlite3
import time

import pytest

from tibia74 import GameClient, Item, RIGHT, SERVER_DIR, ServerProcess, TestDatabase
from tibia74.otbm import read_towns
from tibia74.server import RUN_DIR

TOWNS = {t.name: t for t in read_towns(SERVER_DIR / "data" / "world" / "Tibia74.otbm")}
THAIS, EDRON = TOWNS["Thais"], TOWNS["Edron"]
BEGINNER_SET = {30001: 1}
SAVE_IN, MINUTE = 60, 6
EXIT_CODE = 10                                   # serversave.lua EXIT_CODE
WARNING = 0x12                                   # MSG_STATUS_WARNING: red, in the middle of the screen
WARNINGS = ["Server is saving game in 5 minutes. Please come back in 10 minutes.",
            "Server is saving game in 3 minutes. Please come back in 10 minutes.",
            "Server is saving game in 1 minute. Please log out."]
GOING_DOWN = "The game is just going down."     # protocolgame.cpp, GAME_STATE_CLOSING

THAIS_ROAD = (32369, 32245, 7)                   # just south of the Thais temple
RENT_HOUSE = 53                                  # Upper Swamp Lane 2, Thais, rent 4740 (Tibia74-houses.xml)
PAID_HOUSE = 54                                  # Upper Swamp Lane 4, Thais, rent 4740
LOST_HOUSE, LOST_TILE = 474, (33208, 31798, 7)   # Castle Shop 2, Edron, rent 1890
SWORD = 2376
LETTER = 2598                                    # ITEM_LETTER_STAMPED: the rent warning


class Run:
    """What the save left: the characters, the clients' messages, the process' exit code."""
    chars: dict
    clients: dict
    refused: str
    exit_code: int
    log: str


def _setup(run):
    def setup(db_path):
        db = TestDatabase(db_path)
        c = run.chars = {
            "player": db.create_character(pos=THAIS_ROAD, storage=BEGINNER_SET),
            "late": db.create_character(pos=THAIS_ROAD, storage=BEGINNER_SET),
            "gm": db.create_character(pos=LOST_TILE, group_id=3, inventory={RIGHT: Item(SWORD)},
                                      storage=BEGINNER_SET),
            "renter": db.create_character(pos=THAIS_ROAD, premium_days=30, storage=BEGINNER_SET),  # no money
            "payer": db.create_character(pos=THAIS_ROAD, premium_days=30, storage=BEGINNER_SET),
            "expired": db.create_character(pos=THAIS_ROAD, premium_days=0, storage=BEGINNER_SET),
        }
        con = sqlite3.connect(db_path)
        far = int(time.time()) + 20 * 86400
        con.executemany("INSERT INTO houses (id, owner, paid, warnings, lastwarning) VALUES (?, ?, ?, 0, 0)",
                        [(RENT_HOUSE, c["renter"].guid, 0), (PAID_HOUSE, c["payer"].guid, far),
                         (LOST_HOUSE, c["expired"].guid, far)])
        con.commit()
        con.close()
    return setup


def _login(server, items, character):
    c = GameClient(items, port=server.port)
    c.login(character.account, character.password, character.name)
    return c


def _free_port():
    """Not MINTWALL_TEST_PORT: in a whole run conftest's server is there already."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def server():
    """This module's own server (overrides conftest's: the save ends it)."""
    run = Run()
    srv = ServerProcess(port=_free_port(), run_dir=RUN_DIR / "server-save", setup=_setup(run),
                        config={"ServerSaveEnabled": True, "ServerSaveTestIn": SAVE_IN,
                                "ServerSaveTestMinute": MINUTE})
    srv.start()
    srv.run = run
    yield srv
    srv.stop()


@pytest.fixture(scope="module")
def db(server):
    return TestDatabase(server.db_path)


@pytest.fixture(autouse=True)
def no_lua_errors(server):
    """conftest's, without its "the server died" check: here it exits on purpose."""
    start = server.log_offset()
    yield
    errors = server.lua_errors(since=start)
    if errors:
        pytest.fail("server logged Lua errors during the test:\n\n" + "\n\n".join(errors[:5]), pytrace=False)


@pytest.fixture(scope="module")
def save(server, items):
    """Log in, drop a sword in the expired owner's house, try a login after the first warning, wait for the exit."""
    run = server.run
    started = time.time()
    player = _login(server, items, run.chars["player"])
    gm = _login(server, items, run.chars["gm"])
    assert gm.pos == LOST_TILE, gm.pos
    gm.move_item(gm.inventory_pos(RIGHT), gm.inventory[RIGHT].client_id, 0, gm.pos, 1)   # a GM drops anywhere
    assert gm.wait_for(lambda: RIGHT not in gm.inventory, timeout=3), gm.text_messages[-2:]
    assert time.time() - started < SAVE_IN - 5 * MINUTE - 5, "too slow: the logins close before the setup is done"
    run.clients = {"player": player, "gm": gm}

    assert player.wait_for(lambda: player.messages("in 5 minutes"), timeout=SAVE_IN + 30), server.log_tail()
    try:
        _login(server, items, run.chars["late"]).logout()
        run.refused = None
    except Exception as e:                       # tibia74 ProtocolError: "login failed: <the server's text>"
        run.refused = str(e)

    try:
        run.exit_code = server.proc.wait(timeout=6 * MINUTE + 60)
    except Exception:
        pytest.fail("the server did not exit after the save:\n" + server.log_tail(20), pytrace=False)
    run.log = server.log()
    return run


# ---------------------------------------------------------------------------------------------- before

def test_everyone_gets_the_warnings_5_3_and_1_minutes_before(save):
    for who in ("player", "gm"):
        got = [t for cls, t in save.clients[who].text_messages if t.startswith("Server is saving game")]
        assert got == WARNINGS, (who, got)
        classes = {cls for cls, t in save.clients[who].text_messages if t.startswith("Server is saving game")}
        assert classes == {WARNING}, classes


def test_no_login_in_the_last_5_minutes(save):
    assert save.refused is not None, "a player logged in after the 5-minute warning"
    assert GOING_DOWN in save.refused, save.refused


# ---------------------------------------------------------------------------------------------- the save

def test_everyone_is_kicked(save):
    for who, client in save.clients.items():
        assert not client.connected, f"{who} is still connected"
    assert "> Server save: kicking everyone." in save.log


def test_the_characters_are_saved(save, db):
    """Kicked = saved: the GM's sword lies in the house (not in its hand any more)."""
    gm = save.chars["gm"]
    assert not [i for i in db.items(gm.guid) if i["itemtype"] == SWORD]
    assert db.character(gm.guid)["lastlogout"] > 0


def _depot_items(db, guid):
    """[(itemtype, depot id, attributes)] of everything in the character's depots (a depot chest's pid is its id)."""
    con = db._connect()
    try:
        rows = con.execute("SELECT pid, sid, itemtype, attributes FROM player_depotitems WHERE player_id = ?",
                           (guid,)).fetchall()
    finally:
        con.close()
    parent = {sid: pid for pid, sid, _, _ in rows}
    out = []
    for pid, sid, itemtype, attributes in rows:
        while pid in parent:
            pid = parent[pid]
        out.append((itemtype, pid, bytes(attributes or b"")))
    return out


def _house(db, house_id):
    con = db._connect()
    try:
        return con.execute("SELECT owner, paid, warnings FROM houses WHERE id = ?", (house_id,)).fetchone()
    finally:
        con.close()


def test_unpaid_rent_sends_the_warning_letter_to_the_depot_of_the_house_town(save, db):
    renter = save.chars["renter"]
    owner, paid, warnings = _house(db, RENT_HOUSE)
    assert owner == renter.guid, "the house was taken at the first missed rent"
    assert warnings == 1, warnings
    letters = [(depot, attrs) for itemtype, depot, attrs in _depot_items(db, renter.guid) if itemtype == LETTER]
    assert len(letters) == 1, _depot_items(db, renter.guid)
    depot, text = letters[0]
    assert depot == THAIS.id, depot
    assert b"is payable" in text and b"Upper Swamp Lane 2" in text, text


def test_a_paid_premium_house_is_kept(save, db):
    owner, paid, warnings = _house(db, PAID_HOUSE)
    assert owner == save.chars["payer"].guid
    assert warnings == 0
    assert not _depot_items(db, save.chars["payer"].guid)


def test_the_house_of_an_owner_without_premium_is_released_into_the_depot(save, db):
    """The owner never logged in: the save releases it (else only its login would), the sword goes to Edron."""
    expired = save.chars["expired"]
    owner, _, _ = _house(db, LOST_HOUSE)
    assert owner == 0, owner
    assert (SWORD, EDRON.id) in [(t, d) for t, d, _ in _depot_items(db, expired.guid)], _depot_items(db, expired.guid)
    assert f"{expired.name} has no premium, house Castle Shop 2 released" in save.log


# ---------------------------------------------------------------------------------------------- after

def test_the_server_exits_for_its_supervisor_to_restart_it(save):
    """Exit code 10 needs the build with doSetExitCode (otserv.cpp returns Game::exitCode)."""
    assert "> Server save: done, shutting down" in save.log
    assert save.exit_code == EXIT_CODE, f"exit code {save.exit_code}"

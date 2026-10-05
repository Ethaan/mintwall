"""Closing the server's console (or Ctrl+C / Ctrl+Break, logoff, system shutdown; SIGTERM / SIGINT / SIGHUP on Linux)
shuts it down cleanly: players kicked and saved, the map saved, the save writer flushed (otserv.cpp
installShutdownHandlers). Before, the process ended at once: what the writer held and everything since the last
timed save were lost.

The server here runs in a console of its own without a window (CREATE_NO_WINDOW), so a console event can be sent to
it alone: a helper process attaches to that console and calls GenerateConsoleCtrlEvent. Closing the window
(CTRL_CLOSE_EVENT) cannot be generated that way; the server handles it as these two, waiting at most 4.5 s for the
save before Windows ends the process. Its timed save is off (SaveInterval 3600): only the shutdown can have saved.
One server per event, on a free port, in <MINTWALL_TEST_RUN>/console-close."""
import os
import socket
import sqlite3
import subprocess
import sys
import time
from unittest import mock

import pytest

from tibia74 import EAST, GameClient, Item, RIGHT, ServerProcess, TestDatabase
from tibia74.server import RUN_DIR

pytestmark = pytest.mark.skipif(os.name != "nt", reason="Windows console events")

CREATE_NO_WINDOW = 0x08000000
CTRL_C_EVENT, CTRL_BREAK_EVENT = 0, 1
NAMES = {CTRL_C_EVENT: "Ctrl+C", CTRL_BREAK_EVENT: "Ctrl+Break"}      # otserv.cpp onConsoleEvent
ROAD = (32097, 32205, 7)                         # Rookgaard, north of the temple (test_save.py)
HOUSE_ID, HOUSE_TILE = 4, (32391, 32150, 7)      # a Thais house, clear marble floor (test_save.py)
SWORD = 2376
BEGINNER_SET = {30001: 1}

# attach to the server's console and send it the event (to every process on that console: this one ignores it)
SENDER = r"""
import ctypes, sys, time
from ctypes import wintypes
k = ctypes.WinDLL("kernel32", use_last_error=True)
ignore = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)(lambda event: True)
k.FreeConsole()
if not k.AttachConsole(int(sys.argv[1])):
    sys.exit(f"AttachConsole failed: {ctypes.get_last_error()}")
k.SetConsoleCtrlHandler(ignore, True)
if not k.GenerateConsoleCtrlEvent(int(sys.argv[2]), 0):
    sys.exit(f"GenerateConsoleCtrlEvent failed: {ctypes.get_last_error()}")
time.sleep(0.5)
"""


class ConsoleServer(ServerProcess):
    """A ServerProcess started in a console of its own with no window."""
    def start(self, timeout: float = 180.0):
        popen = subprocess.Popen

        def own_console(*args, **kwargs):
            return popen(*args, creationflags=CREATE_NO_WINDOW, **kwargs)
        with mock.patch.object(subprocess, "Popen", own_console):
            super().start(timeout)


def _free_port():
    """Not MINTWALL_TEST_PORT: in a whole run conftest's server is there already."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _setup(chars):
    def setup(db_path):
        db = TestDatabase(db_path)
        chars["player"] = db.create_character(pos=ROAD, storage=BEGINNER_SET)
        chars["gm"] = db.create_character(pos=HOUSE_TILE, group_id=3, inventory={RIGHT: Item(SWORD)},
                                          storage=BEGINNER_SET)
        chars["heir"] = db.create_character(storage=BEGINNER_SET)
    return setup


@pytest.fixture(scope="module", params=[CTRL_BREAK_EVENT, CTRL_C_EVENT], ids=["ctrl-break", "ctrl-c"])
def server(request):
    """This module's own server, one per event (overrides conftest's: the event ends it)."""
    chars = {}
    srv = ConsoleServer(port=_free_port(), run_dir=RUN_DIR / "console-close", setup=_setup(chars),
                        config={"SaveInterval": 3600})
    srv.start()
    srv.chars, srv.event = chars, request.param
    yield srv
    srv.stop()


@pytest.fixture(autouse=True)
def no_lua_errors(server):
    """conftest's, without its "the server died" check: here it exits on purpose."""
    start = server.log_offset()
    yield
    errors = server.lua_errors(since=start)
    if errors:
        pytest.fail("server logged Lua errors during the test:\n\n" + "\n\n".join(errors[:5]), pytrace=False)


def _login(server, items, character):
    c = GameClient(items, port=server.port)
    c.login(character.account, character.password, character.name)
    return c


def _query(server, sql, *args):
    con = sqlite3.connect(server.db_path)
    try:
        return con.execute(sql, args).fetchone()
    finally:
        con.close()


def test_a_console_event_saves_the_game_before_the_server_exits(server, items):
    chars, event = server.chars, server.event
    player = _login(server, items, chars["player"])
    assert player.step(EAST), f"could not step east from {player.pos}"
    moved = player.pos
    gm = _login(server, items, chars["gm"])
    assert gm.pos == HOUSE_TILE, gm.pos
    gm.say(f"/owner {chars['heir'].name}")
    gm.move_item(gm.inventory_pos(RIGHT), gm.inventory[RIGHT].client_id, 0, gm.pos, 1)   # a GM drops anywhere
    assert gm.wait_for(lambda: RIGHT not in gm.inventory, timeout=3), gm.text_messages[-2:]
    time.sleep(1)                                   # the /owner said before the drop is done too
    assert _query(server, "SELECT posx, posy, posz FROM players WHERE id = ?", chars["player"].guid) == ROAD, \
        "saved before the event: this test could not tell"

    since = server.log_offset()
    sent = subprocess.run([sys.executable, "-c", SENDER, str(server.proc.pid), str(event)],
                          creationflags=CREATE_NO_WINDOW, capture_output=True, text=True, timeout=15)
    assert sent.returncode == 0, sent.stderr or sent.stdout
    try:
        code = server.proc.wait(30)
    except subprocess.TimeoutExpired:
        raise AssertionError("the server did not exit within 30 s:\n" + server.log_tail())
    log = server.log()[since:]
    for c in (player, gm):
        try:
            c.close()
        except Exception:
            pass

    assert f"> {NAMES[event]}: saving and shutting down" in log, \
        f"exit code 0x{code & 0xFFFFFFFF:08X} and no shutdown save - an old avesta74.exe? (server\\build.bat)\n" \
        + server.log_tail(15)
    assert "> Server saved in" in log, server.log_tail(15)
    assert code == 0, f"exit code 0x{code & 0xFFFFFFFF:08X}\n" + server.log_tail(15)
    assert _query(server, "SELECT posx, posy, posz FROM players WHERE id = ?", chars["player"].guid) == moved, \
        "the player's step was not saved"
    assert _query(server, "SELECT owner FROM houses WHERE id = ?", HOUSE_ID) == (chars["heir"].guid,), \
        "the house's new owner was not saved"
    blob = _query(server, "SELECT data FROM map_store WHERE house_id = ?", HOUSE_ID)
    assert blob and SWORD.to_bytes(2, "little") in bytes(blob[0]), "the sword dropped in the house was not saved"

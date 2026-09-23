"""Salted PBKDF2 passwords (docs/production-plan.md §2): config PasswordType = "pbkdf2"."""
import base64
import hashlib
import hmac
import statistics
import threading
import time

import pytest

from tibia74 import EAST, WEST, GameClient
from tibia74.client import ProtocolError, character_list

PASSWORD = "test"                    # what tibia74/db.py create_character stores (as typed)
WALK = (32097, 32205, 7)             # Rookgaard, north of the temple (test_save.py stands here too, one step)


def _stored(db, account):
    con = db._connect()
    try:
        return con.execute("SELECT password FROM accounts WHERE id = ?", (account,)).fetchone()[0]
    finally:
        con.close()


def _verify(plain, stored):
    """The same check as passwords.cpp, with Python's standard library (tools/provision-accounts.py uses it)."""
    scheme, iterations, salt, expected = stored.split("$")
    assert scheme == "pbkdf2_sha256", stored
    actual = hashlib.pbkdf2_hmac("sha256", plain.encode("latin-1"), base64.b64decode(salt), int(iterations))
    return hmac.compare_digest(actual, base64.b64decode(expected))


def _offline_pbkdf2_account(new_player, db):
    """A character whose account already holds a PBKDF2 entry (first login rehashed it), logged out."""
    p = new_player(level=8)
    character = p.character
    p.logout()
    return character


def test_a_password_stored_as_typed_is_rehashed_on_first_login(new_player, db):
    p = new_player(level=8)
    account = p.character.account
    deadline = time.time() + 5
    while time.time() < deadline and not _stored(db, account).startswith("pbkdf2_sha256$"):
        time.sleep(0.2)
    stored = _stored(db, account)
    assert stored.startswith("pbkdf2_sha256$600000$"), f"still stored as {stored[:20]!r}"
    assert PASSWORD not in stored
    assert _verify(PASSWORD, stored), "the stored hash does not verify with hashlib"
    assert not _verify("wrong", stored)


def test_the_login_server_checks_pbkdf2_passwords(new_player, db, server):
    character = _offline_pbkdf2_account(new_player, db)
    ok = character_list(character.account, PASSWORD, port=server.port)
    assert character.name in [name for name, _ in ok.get("characters", [])], ok
    bad = character_list(character.account, "wrong", port=server.port)
    assert "valid account number and password" in bad.get("error", ""), bad


def test_the_game_server_checks_pbkdf2_passwords(new_player, db, server, items):
    character = _offline_pbkdf2_account(new_player, db)
    with pytest.raises(ProtocolError):
        GameClient(items, port=server.port).login(character.account, "wrong", character.name)
    time.sleep(1)                                    # LoginTimeout between attempts from one IP
    c = GameClient(items, port=server.port).login(character.account, PASSWORD, character.name)
    assert c.pos is not None
    c.logout()


def test_password_checks_do_not_stall_players_online(new_player, db, server):
    """Hashing runs on worker threads: a player online keeps getting answers while logins are checked.
    On the network thread every check (~90 ms here) would hold every connection."""
    accounts = [_offline_pbkdf2_account(new_player, db) for _ in range(3)]
    walker = new_player(pos=WALK, level=8)

    def step_latencies(n):
        out = []
        for _ in range(n):
            walker.sleep(1)                          # a fresh step each time, no queued walk
            start = time.time()
            assert walker.step(EAST if walker.pos[0] == WALK[0] else WEST), f"step refused at {walker.pos}"
            out.append(round(time.time() - start, 3))
        return out

    idle = step_latencies(4)
    stop = threading.Event()

    def logins():
        while not stop.is_set():
            for c in accounts:
                character_list(c.account, PASSWORD, port=server.port)

    threads = [threading.Thread(target=logins, daemon=True) for _ in range(6)]
    for t in threads:
        t.start()
    time.sleep(0.5)
    busy = step_latencies(8)
    stop.set()
    for t in threads:
        t.join(timeout=15)
    # measured: workers ~0.02 s either way; hashing on the network thread 0.11-0.19 s during logins
    assert statistics.mean(busy) < statistics.mean(idle) + 0.06, f"step answers idle {idle}, during logins {busy}"

"""tools/create-account.py and tools/accountlib.py: player accounts made while the server runs, logged in with the
7.4 protocol (the login proves the engine verifies the PBKDF2 hash); the password warning in MOTD and LoginMsg."""
import base64
import hashlib
import hmac
import importlib.util
import re
import sqlite3
import sys
import time

import pytest

from tibia74 import GameClient, SERVER_DIR
from tibia74.client import character_list

TOOLS = SERVER_DIR.parent / "tools"
sys.path.insert(0, str(TOOLS))
import accountlib  # noqa: E402

spec = importlib.util.spec_from_file_location("create_account", TOOLS / "create-account.py")
create_account_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(create_account_cli)

WARNING = "use a password you use nowhere else"


def _verify(plain, stored):
    scheme, iterations, salt, expected = stored.split("$")
    actual = hashlib.pbkdf2_hmac("sha256", plain.encode("latin-1"), base64.b64decode(salt), int(iterations))
    return scheme == "pbkdf2_sha256" and hmac.compare_digest(actual, base64.b64decode(expected))


def _create(server, **kwargs):
    con = accountlib.connect(server.db_path)
    try:
        return accountlib.create_account(con, **kwargs)
    finally:
        con.close()


def _rows(server, sql, *args):
    con = sqlite3.connect(server.db_path, timeout=10)
    try:
        return con.execute(sql, args).fetchall()
    finally:
        con.close()


def test_a_new_account_logs_in_while_the_server_runs(server, items):
    created = _create(server, character="Fresh Arrival", premium_days=3, email="player@example.com")
    number, password = created["account"], created["password"]
    assert 1_000_000 <= number <= 9_999_999
    assert len(password) == 12
    (stored, email, premend), = _rows(server, "SELECT password, email, premend FROM accounts WHERE id = ?", number)
    assert stored.startswith(f"pbkdf2_sha256${accountlib.ITERATIONS}$") and password not in stored
    assert email == "player@example.com"
    assert abs(premend - (time.time() + 3 * 86400)) < 60

    # the login server: character list, MOTD with the password warning, the premium days
    listing = character_list(number, password, port=server.port)
    assert [n for n, _ in listing.get("characters", [])] == ["Fresh Arrival"], listing
    assert listing["premium_days"] in (2, 3), listing
    motd_num, motd = listing["motd"].split("\n", 1)
    assert motd_num == re.search(r'MOTD_Num\s*=\s*"(\d+)"',
                                 (SERVER_DIR / "config.lua").read_text("latin-1")).group(1)
    assert motd.startswith("Welcome to Mintwall!") and WARNING in motd and "unencrypted" in motd, motd
    assert "valid account number and password" in character_list(number, "wrong!", port=server.port)["error"]

    # the game server: a level 1 Rookgaard character at the temple, LoginMsg with the warning
    time.sleep(1)                                   # LoginTimeout after the failed attempt from this IP
    c = GameClient(items, port=server.port).login(number, password, "Fresh Arrival")
    try:
        assert c.pos is not None and c.pos[2] == 7
        assert c.wait_for(lambda: c.messages("unencrypted"), 5), c.text_messages
        assert any(t.startswith("Welcome to Mintwall!") and "nowhere else" in t for t in c.messages("unencrypted"))
        (level, vocation, town), = _rows(server, "SELECT level, vocation, town_id FROM players WHERE name = ?",
                                         "Fresh Arrival")
        assert (level, vocation, town) == (1, 0, 1)
    finally:
        c.logout()


def test_duplicates_are_refused_and_change_nothing(server):
    first = _create(server)
    count = _rows(server, "SELECT COUNT(*) FROM accounts")[0][0]
    with pytest.raises(accountlib.AccountError, match="already exists"):
        _create(server, number=first["account"], password="another1")
    (stored,), = _rows(server, "SELECT password FROM accounts WHERE id = ?", first["account"])
    assert _verify(first["password"], stored), "the refused duplicate changed the existing password"

    _create(server, character="Taken Name")
    with pytest.raises(accountlib.AccountError, match="taken"):
        _create(server, character="Taken name")                                    # any case
    with pytest.raises(accountlib.AccountError, match="taken"):
        _create(server, character="Rook Tester")                                    # a seed character
    assert _rows(server, "SELECT COUNT(*) FROM accounts")[0][0] == count + 1, "a refused account was written"


@pytest.mark.parametrize("name", ["a", "lowercase", "Two  Spaces", "Trailing ", "Numb3r", "GM Mintwall",
                                  "God Of War", "A" * 26, "Ümlaut"])
def test_bad_character_names_are_refused(name):
    with pytest.raises(accountlib.AccountError):
        accountlib.check_name(name)


@pytest.mark.parametrize("name", ["Sir Galahad", "Lord of Ashes", "Bo"])
def test_good_character_names(name):
    accountlib.check_name(name)


@pytest.mark.parametrize("password", ["short", "has space", "x" * 30, "accént1"])
def test_bad_passwords_are_refused(password):
    with pytest.raises(accountlib.AccountError):
        accountlib.check_password(password)


def test_the_script_prints_the_password_once_and_the_warning(server, capsys):
    assert create_account_cli.main(["--db", str(server.db_path), "--character", "Script Made", "--female"]) == 0
    out = capsys.readouterr().out
    number = int(re.search(r"account:\s+(\d+)", out).group(1))
    password = re.search(r"password:\s+(\S+)", out).group(1)
    assert WARNING in out and "unencrypted" in out, out
    listing = character_list(number, password, port=server.port)
    assert [n for n, _ in listing.get("characters", [])] == ["Script Made"], listing
    assert _rows(server, "SELECT sex, looktype FROM players WHERE name = 'Script Made'") == [(0, 136)]

    # a given number and password: not printed back; the same number again is refused
    given = number + 1 if number < 9_999_999 else number - 1
    assert create_account_cli.main(["--db", str(server.db_path), "--account", str(given),
                                    "--password", "Given-pass1"]) == 0
    out = capsys.readouterr().out
    assert "Given-pass1" not in out and f"account:   {given}" in out
    with pytest.raises(SystemExit, match="already exists"):
        create_account_cli.main(["--db", str(server.db_path), "--account", str(given), "--password", "x" * 8])


def test_provision_accounts_uses_the_shared_hash(server):
    """tools/provision-accounts.py hashes with accountlib (no second copy of the format)."""
    spec_ = importlib.util.spec_from_file_location("provision", TOOLS / "provision-accounts.py")
    provision = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(provision)
    assert provision.pbkdf2 is accountlib.pbkdf2 and provision.ITERATIONS == accountlib.ITERATIONS

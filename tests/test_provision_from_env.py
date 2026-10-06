"""tools/provision-from-env.py against a throwaway database seeded like the live one.

Proves: the test accounts and all their dependent rows are deleted with no orphans, a house owned by a deleted
character is released (owner 0), the God password is reset and verifies, the main account and its character exist
and can be found, a --keep character is moved (not deleted), a whole --keep-account is moved then the empty account
deleted, --dry-run changes nothing, a second run is a no-op, and the run is refused while a socket holds the port.
"""
import importlib.util
import socket
import sqlite3

import pytest

from tibia74 import SERVER_DIR, Item, BACKPACK, ARMOR
from tibia74 import TestDatabase as Db   # aliased: pytest must not try to collect a class named Test*

spec = importlib.util.spec_from_file_location("provision_from_env",
                                              SERVER_DIR.parent / "tools" / "provision-from-env.py")
pfe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pfe)

FREE_PORT = 7998                      # nothing listens here: the "server running" guard lets it through
GOD_ACCOUNT = 9
OLD_GOD_PASSWORD = "old-god-secret"
MAIN_ACCOUNT = 1234567
MAIN_PASSWORD = "MainPlayerPass16"    # 16 chars
GOD_PASSWORD = "NewGodSecret16AB"
KEEP_ACCOUNT = 7000                   # source account whose characters all move to main

SNAP_TABLES = ("accounts", "players", "player_items", "player_skills", "player_storage",
               "player_deaths", "player_viplist", "houses", "house_requests")


def _snapshot(path):
    con = sqlite3.connect(path)
    try:
        return {t: sorted(map(tuple, con.execute(f"SELECT * FROM {t}"))) for t in SNAP_TABLES}
    finally:
        con.close()


@pytest.fixture
def world(tmp_path):
    """A throwaway DB seeded like the live one, plus the .env. Returns (db_path, env_path, ids)."""
    db = tmp_path / "db.db3"
    con = sqlite3.connect(db)
    con.executescript((SERVER_DIR / "sql" / "schema.sqlite").read_text(encoding="latin-1"))
    for gid, name in ((1, "player"), (3, "god")):
        con.execute("INSERT INTO groups (id, name, flags, access, maxdepotitems, maxviplist) "
                    "VALUES (?, ?, 0, 0, 1000, 100)", (gid, name))
    # God account (id 9) with an OLD password and a character - both must survive the run.
    con.execute("INSERT INTO accounts (id, password) VALUES (?, ?)",
                (GOD_ACCOUNT, pfe.pbkdf2(OLD_GOD_PASSWORD)))
    con.execute("INSERT INTO players (name, account_id, group_id, conditions, rank_id, town_id) "
                "VALUES ('Gamemaster', ?, 3, X'', 0, 1)", (GOD_ACCOUNT,))
    con.commit()
    con.close()

    db_api = Db(db)
    # Two doomed test characters with items, skills, storage; a viplist and a house tie them to extra tables.
    doomed = db_api.create_character("Doomed One",
                                     inventory={BACKPACK: Item(1988, contents=[Item(2160, 50)]), ARMOR: Item(2463)},
                                     skills={2: 55}, storage={1001: 7})
    doomed2 = db_api.create_character("Doomed Two", storage={1002: 3})
    # A character kept by NAME: its account stays, the character moves to main.
    kept = db_api.create_character("Kept Hero", inventory={ARMOR: Item(2465)}, skills={4: 44}, storage={2001: 9})
    # A whole account kept by --keep-account: three characters move to main, then the account is deleted.
    movers = [db_api.create_character(f"Mover {n}", inventory={BACKPACK: Item(1988)}, skills={2: 20 + n},
                                      storage={3000 + n: n}) for n in (1, 2, 3)]

    con = sqlite3.connect(db)
    # Extra dependent rows on Doomed One: a death (NOT covered by the ondelete trigger), a viplist, a house +
    # its list + a buy request.
    con.execute("INSERT INTO player_deaths (player_id, time, level) VALUES (?, 123, 5)", (doomed.guid,))
    con.execute("INSERT INTO player_viplist (player_id, vip_id) VALUES (?, ?)", (doomed.guid, doomed2.guid))
    con.execute("INSERT INTO houses (id, owner) VALUES (500, ?)", (doomed.guid,))
    con.execute("INSERT INTO house_lists (house_id, listid, list) VALUES (500, 1, 'Doomed One')")
    con.execute("INSERT INTO house_requests (house_id, player_id, account_id, created, state) "
                "VALUES (500, ?, ?, 123, 0)", (doomed.guid, doomed.account))
    # Collapse the three movers onto one real account (KEEP_ACCOUNT); their original accounts become empty.
    con.execute("INSERT INTO accounts (id, password) VALUES (?, ?)", (KEEP_ACCOUNT, pfe.pbkdf2("x")))
    for m in movers:
        con.execute("UPDATE players SET account_id = ? WHERE id = ?", (KEEP_ACCOUNT, m.guid))
    con.commit()
    con.close()

    env = tmp_path / ".env"
    env.write_text(f"GOD_ACCOUNT={GOD_ACCOUNT}\nGOD_PASSWORD={GOD_PASSWORD}\n"
                   f"MAIN_ACCOUNT={MAIN_ACCOUNT}\nMAIN_PASSWORD={MAIN_PASSWORD}\n"
                   f"MAIN_CHARACTER=Main Hero\nMAIN_EMAIL=player@example.com\n", encoding="utf-8")

    ids = {"doomed": doomed, "doomed2": doomed2, "kept": kept, "movers": movers}
    return db, env, ids


def _run(db, env, *extra):
    return pfe.main(["--db", str(db), "--env", str(env), "--port", str(FREE_PORT), "--yes", "--no-backup", *extra])


def test_test_accounts_and_rows_gone_with_no_orphans(world):
    db, env, ids = world
    con = sqlite3.connect(db)
    deleted = [r[0] for r in con.execute("SELECT id FROM players WHERE account_id NOT IN (?, ?, ?)",
                                         (GOD_ACCOUNT, MAIN_ACCOUNT, KEEP_ACCOUNT))]
    con.close()

    assert _run(db, env, "--keep", "Kept Hero", "--keep-account", str(KEEP_ACCOUNT)) == 0

    con = sqlite3.connect(db)
    # The two doomed accounts (and the movers' now-empty original accounts) are gone.
    assert ids["doomed"].account not in {r[0] for r in con.execute("SELECT id FROM accounts")}
    # No orphan rows anywhere: every player_id / vip_id points at a surviving player; houses released.
    alive = {r[0] for r in con.execute("SELECT id FROM players")}
    accts = {r[0] for r in con.execute("SELECT id FROM accounts")}
    tables = [t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    for table in tables:
        cols = {r[1] for r in con.execute(f'PRAGMA table_info("{table}")')}
        if "player_id" in cols:
            bad = [r[0] for r in con.execute(f"SELECT DISTINCT player_id FROM {table}") if r[0] not in alive]
            assert not bad, f"orphan player_id in {table}: {bad}"
        if "vip_id" in cols:
            bad = [r[0] for r in con.execute(f"SELECT DISTINCT vip_id FROM {table}") if r[0] not in alive]
            assert not bad, f"orphan vip_id in {table}: {bad}"
        if "account_id" in cols and table != "players":
            bad = [r[0] for r in con.execute(f"SELECT DISTINCT account_id FROM {table}") if r[0] not in accts]
            assert not bad, f"orphan account_id in {table}: {bad}"
    # Specifically the doomed character's dependent rows are all gone.
    for table in ("player_items", "player_skills", "player_storage", "player_deaths"):
        n = con.execute(f"SELECT COUNT(*) FROM {table} WHERE player_id = ?", (ids["doomed"].guid,)).fetchone()[0]
        assert n == 0, f"{table} still has rows for the deleted character"
    con.close()


def test_house_is_released(world):
    db, env, ids = world
    assert _run(db, env) == 0
    con = sqlite3.connect(db)
    assert con.execute("SELECT owner FROM houses WHERE id = 500").fetchone()[0] == 0
    con.close()


def test_god_password_updated_and_verifies(world):
    db, env, ids = world
    assert _run(db, env) == 0
    con = sqlite3.connect(db)
    stored = con.execute("SELECT password FROM accounts WHERE id = ?", (GOD_ACCOUNT,)).fetchone()[0]
    con.close()
    assert pfe.verify(GOD_PASSWORD, stored)
    assert not pfe.verify(OLD_GOD_PASSWORD, stored)


def test_main_account_and_character_exist(world):
    db, env, ids = world
    assert _run(db, env) == 0
    con = sqlite3.connect(db)
    stored = con.execute("SELECT password FROM accounts WHERE id = ?", (MAIN_ACCOUNT,)).fetchone()
    assert stored is not None and pfe.verify(MAIN_PASSWORD, stored[0])
    # Found the way the engine finds it (case-insensitive by name).
    found = con.execute("SELECT account_id FROM players WHERE LOWER(name) = LOWER('main hero')").fetchone()
    assert found is not None and found[0] == MAIN_ACCOUNT
    con.close()


def test_keep_character_moved_not_deleted(world):
    db, env, ids = world
    kept = ids["kept"]
    assert _run(db, env, "--keep", "Kept Hero") == 0
    con = sqlite3.connect(db)
    row = con.execute("SELECT account_id FROM players WHERE id = ?", (kept.guid,)).fetchone()
    assert row is not None and row[0] == MAIN_ACCOUNT, "kept character was not moved to the main account"
    # Its items/skills/storage rode along.
    assert con.execute("SELECT COUNT(*) FROM player_items WHERE player_id = ?", (kept.guid,)).fetchone()[0] > 0
    assert con.execute("SELECT value FROM player_storage WHERE player_id = ? AND key = 2001",
                       (kept.guid,)).fetchone()[0] == 9
    con.close()


def test_keep_account_moves_all_characters_then_deletes_source(world):
    db, env, ids = world
    movers = ids["movers"]
    assert _run(db, env, "--keep-account", str(KEEP_ACCOUNT)) == 0
    con = sqlite3.connect(db)
    # The source account is gone.
    assert con.execute("SELECT 1 FROM accounts WHERE id = ?", (KEEP_ACCOUNT,)).fetchone() is None
    for m in movers:
        row = con.execute("SELECT account_id FROM players WHERE id = ?", (m.guid,)).fetchone()
        assert row is not None and row[0] == MAIN_ACCOUNT, f"{m.name} not under main"
        # The dependent rows moved with the character (same player_id, now owned by main).
        assert con.execute("SELECT COUNT(*) FROM player_items WHERE player_id = ?", (m.guid,)).fetchone()[0] > 0
        assert con.execute("SELECT COUNT(*) FROM player_skills WHERE player_id = ?", (m.guid,)).fetchone()[0] == 7
        assert con.execute("SELECT COUNT(*) FROM player_storage WHERE player_id = ?", (m.guid,)).fetchone()[0] == 1
    con.close()


def test_main_valid_without_a_character(world):
    """MAIN_CHARACTER blank: the account is created, characters come only from the move."""
    db, env, ids = world
    env.write_text(f"GOD_ACCOUNT={GOD_ACCOUNT}\nGOD_PASSWORD={GOD_PASSWORD}\n"
                   f"MAIN_ACCOUNT={MAIN_ACCOUNT}\nMAIN_PASSWORD={MAIN_PASSWORD}\n", encoding="utf-8")
    assert _run(db, env, "--keep-account", str(KEEP_ACCOUNT)) == 0
    con = sqlite3.connect(db)
    assert con.execute("SELECT 1 FROM accounts WHERE id = ?", (MAIN_ACCOUNT,)).fetchone() is not None
    owned = con.execute("SELECT COUNT(*) FROM players WHERE account_id = ?", (MAIN_ACCOUNT,)).fetchone()[0]
    assert owned == 3, "the three moved characters should be the only ones on main"
    con.close()


def test_dry_run_changes_nothing(world):
    db, env, ids = world
    before = _snapshot(db)
    assert pfe.main(["--db", str(db), "--env", str(env), "--port", str(FREE_PORT),
                     "--keep-account", str(KEEP_ACCOUNT), "--dry-run"]) == 0
    assert _snapshot(db) == before


def test_second_run_is_a_no_op(world):
    db, env, ids = world
    assert _run(db, env, "--keep", "Kept Hero", "--keep-account", str(KEEP_ACCOUNT)) == 0
    after_first = _snapshot(db)
    assert _run(db, env, "--keep", "Kept Hero", "--keep-account", str(KEEP_ACCOUNT)) == 0
    assert _snapshot(db) == after_first, "a second run with the same .env changed the database"


def test_refuses_while_a_socket_listens(world):
    db, env, ids = world
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
        before = _snapshot(db)
        with pytest.raises(SystemExit, match="listening"):
            pfe.main(["--db", str(db), "--env", str(env), "--port", str(port), "--yes", "--no-backup"])
        assert _snapshot(db) == before, "the database was touched despite the port guard"


def test_missing_secrets_are_generated_and_written_back_without_printing(world, capsys):
    db, env, ids = world
    env.write_text("GOD_ACCOUNT=9\n", encoding="utf-8")   # everything else missing -> generated
    assert _run(db, env, "--keep-account", str(KEEP_ACCOUNT)) == 0
    out = capsys.readouterr().out
    assert "wrote credentials to .env" in out
    values = pfe.load_env(env)
    assert values["GOD_PASSWORD"] and values["MAIN_ACCOUNT"] and values["MAIN_PASSWORD"]
    assert len(values["GOD_PASSWORD"]) == pfe.GENERATED_PASSWORD_LENGTH
    assert 1_000_000 <= int(values["MAIN_ACCOUNT"]) <= 9_999_999
    # No password ever reaches stdout.
    assert values["GOD_PASSWORD"] not in out and values["MAIN_PASSWORD"] not in out
    # And the generated secrets actually work against the stored hashes.
    con = sqlite3.connect(db)
    g = con.execute("SELECT password FROM accounts WHERE id = 9").fetchone()[0]
    assert pfe.verify(values["GOD_PASSWORD"], g)
    con.close()

"""tools/provision-accounts.py (docs/production-plan.md §1) against a scratch copy of the seed database."""
import base64
import hashlib
import hmac
import importlib.util
import json
import re
import sqlite3

import pytest

from tibia74 import SERVER_DIR

spec = importlib.util.spec_from_file_location("provision", SERVER_DIR.parent / "tools" / "provision-accounts.py")
provision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision)

FREE_PORT = 7999                     # nothing listens here: the "server running" guard lets it through


def _seed_db(path):
    con = sqlite3.connect(path)
    con.executescript((SERVER_DIR / "sql" / "schema.sqlite").read_text(encoding="latin-1"))
    con.executescript((SERVER_DIR / "sql" / "seed.sql").read_text(encoding="latin-1"))
    con.commit()
    con.close()


def _verify(plain, stored):
    scheme, iterations, salt, expected = stored.split("$")
    actual = hashlib.pbkdf2_hmac("sha256", plain.encode("latin-1"), base64.b64decode(salt), int(iterations))
    return scheme == "pbkdf2_sha256" and hmac.compare_digest(actual, base64.b64decode(expected))


@pytest.fixture
def provisioned(tmp_path):
    db, creds = tmp_path / "db.db3", tmp_path / "secrets" / "accounts.json"
    _seed_db(db)
    assert provision.main(["--db", str(db), "--secrets", str(creds), "--generate", "--port", str(FREE_PORT),
                           "--no-backup"]) == 0
    return db, creds, json.loads(creds.read_text())


def test_accounts_characters_and_seed_cleanup(provisioned):
    db, _, creds = provisioned
    con = sqlite3.connect(db)
    accounts = {row[0]: row for row in con.execute("SELECT id, password, premend FROM accounts")}
    for role, spec_ in provision.ROLES.items():
        number, password = creds[role]["account"], creds[role]["password"]
        assert 1_000_000 <= number <= 9_999_999 and len(password) >= 16
        assert number in accounts, role
        assert _verify(password, accounts[number][1]), f"{role}: stored hash does not verify"
        assert (accounts[number][2] > 0) == spec_["premium"], f"{role}: premium {accounts[number][2]}"
        owned = {name for (name,) in con.execute("SELECT name FROM players WHERE account_id = ?", (number,))}
        assert owned == set(spec_["characters"]), f"{role}: {owned}"
    assert not set(provision.SEED_ACCOUNTS) & set(accounts), "a seed account (password in git) is left"
    assert not con.execute("SELECT 1 FROM players WHERE name = 'Mintwall'").fetchone(), "leftover character"
    gm_group = con.execute("SELECT group_id FROM players WHERE name = 'GM Mintwall'").fetchone()[0]
    assert gm_group == provision.GOD_GROUP
    con.close()


def test_running_again_keeps_everything(provisioned, tmp_path):
    db, creds_path, creds = provisioned
    assert provision.main(["--db", str(db), "--secrets", str(creds_path), "--port", str(FREE_PORT),
                           "--no-backup"]) == 0
    con = sqlite3.connect(db)
    assert con.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == len(provision.ROLES)
    stored = con.execute("SELECT password FROM accounts WHERE id = ?", (creds["god"]["account"],)).fetchone()[0]
    assert _verify(creds["god"]["password"], stored)
    con.close()


def test_credentials_never_go_inside_the_repository(tmp_path):
    db = tmp_path / "db.db3"
    _seed_db(db)
    with pytest.raises(SystemExit, match="inside the repository"):
        provision.main(["--db", str(db), "--secrets", str(SERVER_DIR / "accounts.json"), "--generate",
                        "--port", str(FREE_PORT)])
    assert not (SERVER_DIR / "accounts.json").exists()


def test_iterations_match_the_server_config():
    config = (SERVER_DIR / "config.lua").read_text(encoding="latin-1")
    assert int(re.search(r"PasswordIterations\s*=\s*(\d+)", config).group(1)) == provision.ITERATIONS
    assert re.search(r'PasswordType\s*=\s*"pbkdf2"', config)

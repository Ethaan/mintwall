"""Clean the database of test accounts and set up the real staff/player accounts from a .env file.

    tests\\.venv\\Scripts\\python.exe tools\\provision-from-env.py --db server\\db.db3 [--keep "Name1,Name2"] --yes

The secrets live only in a .env file that is never committed (see .env.example and .gitignore). Keys:

    GOD_ACCOUNT      the God account number (default 9)
    GOD_PASSWORD     its password - generated and written back if missing
    MAIN_ACCOUNT     the real player account number - generated (random 7 digits) if missing
    MAIN_PASSWORD    its password - generated (16 characters) if missing
    MAIN_CHARACTER   optional: a level 1 Rookgaard character created on the main account
    MAIN_EMAIL       optional: the main account's e-mail

A missing GOD_PASSWORD / MAIN_ACCOUNT / MAIN_PASSWORD is generated with accountlib and written back into .env;
the script never prints a password.

What it does (one transaction, rolled back on --dry-run):
  - keeps GOD_ACCOUNT and its characters; sets its password to GOD_PASSWORD (PBKDF2);
  - creates/keeps MAIN_ACCOUNT with MAIN_PASSWORD, MAIN_EMAIL and the optional MAIN_CHARACTER;
  - moves every --keep character (and every character of a --keep-account) onto the main account;
  - deletes every OTHER account (the test accounts) and all of their dependent rows, leaving no orphans and
    releasing any house they owned (owner -> 0). Only God and main are kept; a character survives a delete only
    by being moved to main, so naming it with --keep / --keep-account is the one way to preserve it.
It is idempotent: a password already matching is left as it is, so a second run with the same .env changes nothing.

The server rewrites the database on save, so the tool refuses to run while something listens on 127.0.0.1:7171
(use --force to override). On a real run the database is backed up first with the SQLite backup API.
"""
import argparse
import base64
import hashlib
import hmac
import os
import socket
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from accountlib import (ITERATIONS, LOOK, LOOKTYPE, NEW_CHARACTER, generate_password,  # noqa: E402
                        pbkdf2, random_account_number)

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO / "server" / "db.db3"
DEFAULT_ENV = REPO / ".env"
GENERATED_PASSWORD_LENGTH = 16


# --- .env ------------------------------------------------------------------------------------------------------

def load_env(path: Path) -> dict:
    """KEY=VALUE pairs; '#' comments and blank lines ignored, surrounding single/double quotes stripped."""
    data = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, value = s.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        data[key] = value
    return data


def write_env(path: Path, updates: dict):
    """Set/append the given keys in .env, keeping every other line (comments, blanks, other keys) as it is."""
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    written, out = set(), []
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and "=" in s and s.split("=", 1)[0].strip() in updates:
            key = s.split("=", 1)[0].strip()
            out.append(f"{key}={updates[key]}")
            written.add(key)
        else:
            out.append(line)
    for key, value in updates.items():
        if key not in written:
            out.append(f"{key}={value}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


# --- passwords -------------------------------------------------------------------------------------------------

def verify(plain: str, stored: str) -> bool:
    """True if the stored PBKDF2 hash (server/src/passwords.cpp format) is of this password - used to skip a
    rewrite when the password is already correct, so a second run changes nothing."""
    try:
        scheme, iterations, salt, expected = stored.split("$")
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    actual = hashlib.pbkdf2_hmac("sha256", plain.encode("latin-1"), base64.b64decode(salt), int(iterations))
    return hmac.compare_digest(actual, base64.b64decode(expected))


# --- configuration from the environment ------------------------------------------------------------------------

def _account_number(text, field):
    try:
        number = int(text)
    except (TypeError, ValueError):
        raise SystemExit(f"{field} must be a whole number, got {text!r}")
    if not 1 <= number <= 0xFFFFFFFF:
        raise SystemExit(f"{field} must be a positive account number")
    return number


def resolve_config(env_path: Path, con: sqlite3.Connection, keep: list, keep_accounts: list) -> dict:
    """Read the .env, generating and writing back any missing GOD_PASSWORD / MAIN_ACCOUNT / MAIN_PASSWORD."""
    env = load_env(env_path)
    generated = {}

    god_account = _account_number(env.get("GOD_ACCOUNT", "9"), "GOD_ACCOUNT")
    god_password = env.get("GOD_PASSWORD")
    if not god_password:
        god_password = generate_password(GENERATED_PASSWORD_LENGTH)
        generated["GOD_PASSWORD"] = god_password

    taken = {row[0] for row in con.execute("SELECT id FROM accounts")} | {god_account}
    main_account_text = env.get("MAIN_ACCOUNT")
    if main_account_text:
        main_account = _account_number(main_account_text, "MAIN_ACCOUNT")
    else:
        main_account = random_account_number(taken)
        generated["MAIN_ACCOUNT"] = str(main_account)
    main_password = env.get("MAIN_PASSWORD")
    if not main_password:
        main_password = generate_password(GENERATED_PASSWORD_LENGTH)
        generated["MAIN_PASSWORD"] = main_password

    if main_account == god_account:
        raise SystemExit("MAIN_ACCOUNT and GOD_ACCOUNT must be different")

    move_accounts = []
    for text in keep_accounts:
        text = str(text).strip()
        if not text:
            continue
        acc = _account_number(text, "--keep-account")
        if acc in (god_account, main_account):
            raise SystemExit("--keep-account cannot be the God or main account")
        move_accounts.append(acc)

    if generated:
        write_env(env_path, generated)
        print("wrote credentials to .env")

    return {
        "god_account": god_account, "god_password": god_password,
        "main_account": main_account, "main_password": main_password,
        "main_character": (env.get("MAIN_CHARACTER") or "").strip() or None,
        "main_email": (env.get("MAIN_EMAIL") or "").strip(),
        "keep": [k.strip() for k in keep if k.strip()],
        "move_accounts": move_accounts,
    }


# --- plan ------------------------------------------------------------------------------------------------------

def build_plan(con: sqlite3.Connection, cfg: dict) -> dict:
    accounts = sorted(row[0] for row in con.execute("SELECT id FROM accounts"))
    by_account = {}
    by_name = {}
    for pid, name, acc in con.execute("SELECT id, name, account_id FROM players"):
        by_account.setdefault(acc, []).append(name)
        by_name[name.lower()] = (pid, name, acc)

    # God and main are the only accounts kept; every other account is a test account and is deleted. The way to
    # preserve a character is to name it (--keep) or its whole account (--keep-account): it is MOVED onto main
    # first, so it survives while its old account is deleted. This keeps the tool idempotent - a second run finds
    # the character already on main and the old account already gone.
    keep_accounts = {cfg["god_account"], cfg["main_account"]}
    move, moved_pids, missing_keep, missing_accounts = [], set(), [], []

    # --keep-account: move EVERY character of the account onto main, then let the empty account be deleted.
    for acc in cfg.get("move_accounts", []):
        owned = [(pid, name) for pid, name, a in by_name.values() if a == acc]
        if not owned:
            missing_accounts.append(acc)
            continue
        for pid, name in owned:
            move.append((pid, name, acc))
            moved_pids.add(pid)

    # --keep "Name,Name": move the named character onto main (its old account is deleted like any other).
    for kept in cfg["keep"]:
        rec = by_name.get(kept.lower())
        if rec is None:
            missing_keep.append(kept)
            continue
        pid, name, acc = rec
        if acc != cfg["main_account"] and pid not in moved_pids:
            move.append((pid, name, acc))
            moved_pids.add(pid)

    delete_accounts = [a for a in accounts if a not in keep_accounts]
    return {
        "accounts": accounts, "by_account": by_account, "keep_accounts": keep_accounts,
        "delete_accounts": delete_accounts, "move": move, "moved_pids": moved_pids,
        "missing_keep": missing_keep, "missing_accounts": missing_accounts,
    }


def print_plan(cfg: dict, plan: dict):
    print("Plan:")
    print(f"  keep God account   {cfg['god_account']}  (password reset)")
    main_note = "create" if cfg["main_account"] not in plan["accounts"] else "keep"
    char = f", character {cfg['main_character']!r}" if cfg["main_character"] else ""
    print(f"  {main_note} main account {cfg['main_account']}{char}")
    if plan["move"]:
        for pid, name, acc in plan["move"]:
            print(f"  move character {name!r} (id {pid}) from account {acc} -> {cfg['main_account']}")
    if plan["missing_keep"]:
        print(f"  WARNING: no character named: {', '.join(plan['missing_keep'])}")
    if plan["missing_accounts"]:
        print(f"  WARNING: no such account(s) for --keep-account: "
              f"{', '.join(str(a) for a in plan['missing_accounts'])}")
    moved_names = {name for _pid, name, _acc in plan["move"]}
    print(f"  delete {len(plan['delete_accounts'])} test account(s):")
    for acc in plan["delete_accounts"]:
        names = [n for n in plan["by_account"].get(acc, []) if n not in moved_names]
        print(f"    account {acc}: {', '.join(names) if names else '(no characters left)'}")


# --- apply -----------------------------------------------------------------------------------------------------

def _player_fk_tables(con: sqlite3.Connection) -> list:
    """Every table except 'players' that has a player_id column (the dependent rows of a character)."""
    tables = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    out = []
    for table in tables:
        if table == "players":
            continue
        cols = {row[1] for row in con.execute(f'PRAGMA table_info("{table}")')}
        if "player_id" in cols:
            out.append(table)
    return out


def _account_fk_tables(con: sqlite3.Connection) -> list:
    """Every table except 'players'/'accounts' with an account_id column (e.g. house_requests)."""
    tables = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    out = []
    for table in tables:
        if table in ("players", "accounts"):
            continue
        cols = {row[1] for row in con.execute(f'PRAGMA table_info("{table}")')}
        if "account_id" in cols:
            out.append(table)
    return out


def _ids(con: sqlite3.Connection, accounts: list) -> list:
    if not accounts:
        return []
    marks = ",".join("?" * len(accounts))
    return [row[0] for row in con.execute(f"SELECT id FROM players WHERE account_id IN ({marks})", accounts)]


def apply(con: sqlite3.Connection, cfg: dict, plan: dict, dry_run: bool):
    """All changes in one transaction; committed on a real run, rolled back on --dry-run so nothing changes."""
    con.execute("BEGIN IMMEDIATE")
    try:
        # God account: keep it and its characters; set the password only if it is not already correct.
        row = con.execute("SELECT password FROM accounts WHERE id = ?", (cfg["god_account"],)).fetchone()
        if row is None:
            con.execute("INSERT INTO accounts (id, password) VALUES (?, ?)",
                        (cfg["god_account"], pbkdf2(cfg["god_password"])))
        elif not verify(cfg["god_password"], row[0]):
            con.execute("UPDATE accounts SET password = ? WHERE id = ?",
                        (pbkdf2(cfg["god_password"]), cfg["god_account"]))

        # Main account: create or keep; keep the password/e-mail in sync without needless rewrites.
        row = con.execute("SELECT password, email FROM accounts WHERE id = ?", (cfg["main_account"],)).fetchone()
        if row is None:
            con.execute("INSERT INTO accounts (id, password, email) VALUES (?, ?, ?)",
                        (cfg["main_account"], pbkdf2(cfg["main_password"]), cfg["main_email"]))
        else:
            if not verify(cfg["main_password"], row[0]):
                con.execute("UPDATE accounts SET password = ? WHERE id = ?",
                            (pbkdf2(cfg["main_password"]), cfg["main_account"]))
            if cfg["main_email"] and row[1] != cfg["main_email"]:
                con.execute("UPDATE accounts SET email = ? WHERE id = ?", (cfg["main_email"], cfg["main_account"]))

        # Main character (level 1 Rookgaard, like accountlib.create_account), created once if it is missing.
        if cfg["main_character"]:
            exists = con.execute("SELECT 1 FROM players WHERE LOWER(name) = LOWER(?)",
                                 (cfg["main_character"],)).fetchone()
            if not exists:
                c, sex = NEW_CHARACTER, 1
                con.execute(
                    "INSERT INTO players (name, account_id, group_id, sex, vocation, experience, level, health,"
                    " healthmax, mana, manamax, cap, looktype, lookhead, lookbody, looklegs, lookfeet, posx, posy,"
                    " posz, conditions, rank_id, town_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,"
                    " ?, ?, ?, ?, X'', ?, ?)",
                    (cfg["main_character"], cfg["main_account"], c["group_id"], sex, c["vocation"],
                     c["experience"], c["level"], c["health"], c["healthmax"], c["mana"], c["manamax"], c["cap"],
                     LOOKTYPE[sex], *LOOK, c["posx"], c["posy"], c["posz"], c["rank_id"], c["town_id"]))

        # Move the --keep characters onto the main account (they are spared from the delete below).
        for pid, name, _acc in plan["move"]:
            con.execute("UPDATE players SET account_id = ? WHERE id = ?", (cfg["main_account"], pid))

        # Delete the test accounts and all of their dependent rows, leaving no orphans.
        delete_accounts = plan["delete_accounts"]
        player_ids = _ids(con, delete_accounts)
        if player_ids:
            marks = ",".join("?" * len(player_ids))
            for table in _player_fk_tables(con):
                con.execute(f"DELETE FROM {table} WHERE player_id IN ({marks})", player_ids)
            con.execute(f"DELETE FROM player_viplist WHERE vip_id IN ({marks})", player_ids)
            con.execute(f"UPDATE houses SET owner = 0 WHERE owner IN ({marks})", player_ids)
            con.execute(f"DELETE FROM players WHERE id IN ({marks})", player_ids)
        if delete_accounts:
            marks = ",".join("?" * len(delete_accounts))
            for table in _account_fk_tables(con):
                con.execute(f"DELETE FROM {table} WHERE account_id IN ({marks})", delete_accounts)
            con.execute(f"DELETE FROM accounts WHERE id IN ({marks})", delete_accounts)

        if dry_run:
            con.execute("ROLLBACK")
        else:
            con.execute("COMMIT")
    except BaseException:
        con.execute("ROLLBACK")
        raise


# --- main ------------------------------------------------------------------------------------------------------

def server_running(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def confirm(assume_yes: bool) -> bool:
    if assume_yes:
        return True
    try:
        return input('Type "yes" to apply these changes: ').strip().lower() == "yes"
    except EOFError:
        return False


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB, help="the server database (default server/db.db3)")
    ap.add_argument("--env", type=Path, default=DEFAULT_ENV, help="the .env file (default .env in the repo root)")
    ap.add_argument("--keep", default="", help='character names to MOVE to the main account, e.g. "Name1,Name2"')
    ap.add_argument("--keep-account", default="", dest="keep_account",
                    help="account id(s), comma-separated: MOVE all their characters to main, then delete the "
                         "now-empty account(s)")
    ap.add_argument("--dry-run", action="store_true", help="show the plan and change nothing")
    ap.add_argument("--yes", action="store_true", help="apply without the interactive confirmation")
    ap.add_argument("--force", action="store_true", help="run even while a server listens on the port")
    ap.add_argument("--port", type=int, default=7171, help="refuse to run while a server listens here")
    ap.add_argument("--no-backup", action="store_true", help=argparse.SUPPRESS)   # tests only
    args = ap.parse_args(argv)

    if not args.db.exists():
        raise SystemExit(f"{args.db} not found")
    if server_running(args.port) and not args.force:
        raise SystemExit(f"a server is listening on 127.0.0.1:{args.port} - stop it first (or pass --force)")

    con = sqlite3.connect(args.db, timeout=10, isolation_level=None)
    try:
        cfg = resolve_config(args.env, con, args.keep.split(","), args.keep_account.split(","))
        plan = build_plan(con, cfg)
        print_plan(cfg, plan)

        if args.dry_run:
            apply(con, cfg, plan, dry_run=True)
            print("dry run: no changes made")
            return 0

        if not confirm(args.yes):
            print("aborted")
            return 1

        if not args.no_backup:
            backup = args.db.with_name(f"{args.db.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
            with sqlite3.connect(backup) as dst:
                con.backup(dst)
            print(f"backup: {backup}")

        apply(con, cfg, plan, dry_run=False)
    finally:
        con.close()
    print(f"done: kept God {cfg['god_account']} and main {cfg['main_account']}, "
          f"deleted {len(plan['delete_accounts'])} test account(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

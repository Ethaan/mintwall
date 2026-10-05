"""Provision the staff and test accounts (docs/production-plan.md §1).

    tests\\.venv\\Scripts\\python.exe tools\\provision-accounts.py --db server\\db.db3 --secrets PATH [--generate]

Four accounts replace the seed ones (1-6, 9, 111111, 222222 - their passwords are in git):

    god           GM Mintwall                                      (group God)
    testers       Centurion, Gandalf, Radagast, Legolas            premium (config InfiniteItemPlayers)
    rook_premium  Premium Tester, Oracle Tester                    premium
    rook_free     Free Tester, Rook Tester                         free

Premium is per account in 7.4, hence two Rookgaard accounts.

--secrets is a JSON file OUTSIDE the repository: {"god": {"account": 5470767, "password": "..."}, ...}.
With --generate it is created first: random 7-digit account numbers, random 24-character passwords. The script
never prints a password. Passwords are stored as salted PBKDF2 (server config PasswordType = "pbkdf2").

The server must be stopped (it rewrites players on logout and on every save). The database is backed up next
to itself first. Running it again is safe: accounts are updated, not duplicated.
"""
import argparse
import json
import os
import secrets
import socket
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from accountlib import ITERATIONS, pbkdf2, random_account_number  # noqa: E402,F401 - the shared code

REPO = Path(__file__).resolve().parent.parent
SEED_ACCOUNTS = [1, 2, 3, 4, 5, 6, 9, 111111, 222222]
PREMIUM_END = 2_000_000_000          # like seed.sql: premium until 2033
GOD_GROUP = 3

ROLES = {
    "god": {"premium": False, "characters": ["GM Mintwall"]},
    "testers": {"premium": True, "characters": ["Centurion", "Gandalf", "Radagast", "Legolas"]},
    "rook_premium": {"premium": True, "characters": ["Premium Tester", "Oracle Tester"]},
    "rook_free": {"premium": False, "characters": ["Free Tester", "Rook Tester"]},
}


def inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(REPO)
        return True
    except ValueError:
        return False


def generate(path: Path, con: sqlite3.Connection):
    taken = {row[0] for row in con.execute("SELECT id FROM accounts")}
    creds = {}
    for role in ROLES:
        number = random_account_number(taken)                      # 7 digits, never sequential
        taken.add(number)
        # 24 characters of [A-Za-z0-9_-]: typable in the 7.4 client (check the length once in the real client)
        creds[role] = {"account": number, "password": secrets.token_urlsafe(18)}
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8") as f:                  # "x": never overwrite existing credentials
        json.dump(creds, f, indent=2)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def load(path: Path) -> dict:
    creds = json.loads(path.read_text(encoding="utf-8"))
    for role in ROLES:
        entry = creds.get(role) or {}
        number, password = entry.get("account"), entry.get("password")
        if not (isinstance(number, int) and 1_000_000 <= number <= 9_999_999):
            raise SystemExit(f"{role}: account must be a 7-digit number")
        if not (isinstance(password, str) and len(password) >= 16):
            raise SystemExit(f"{role}: password must be at least 16 characters")
    if len({creds[r]["account"] for r in ROLES}) != len(ROLES):
        raise SystemExit("every role needs its own account number")
    return creds


def server_running(port: int = 7171) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def apply(con: sqlite3.Connection, creds: dict) -> list:
    """Accounts, character moves, seed cleanup - one transaction. Returns warnings."""
    warnings = []
    ids = {creds[r]["account"] for r in ROLES}
    with con:
        for role, spec in ROLES.items():
            number = creds[role]["account"]
            premend = PREMIUM_END if spec["premium"] else 0
            con.execute("INSERT INTO accounts (id, password, premend) VALUES (?, ?, ?) "
                        "ON CONFLICT(id) DO UPDATE SET password = excluded.password, premend = excluded.premend",
                        (number, pbkdf2(creds[role]["password"]), premend))
            for name in spec["characters"]:
                moved = con.execute("UPDATE players SET account_id = ? WHERE name = ?", (number, name)).rowcount
                if not moved:
                    warnings.append(f"{role}: no character named {name!r}")
        con.execute("UPDATE players SET group_id = ? WHERE name = ?", (GOD_GROUP, ROLES["god"]["characters"][0]))
        # the old seed accounts (passwords in git) go, with anything left on them (triggers delete characters)
        stale = [a for a in SEED_ACCOUNTS if a not in ids]
        con.execute(f"DELETE FROM accounts WHERE id IN ({','.join('?' * len(stale))})", stale)
    return warnings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", required=True, type=Path)
    ap.add_argument("--secrets", required=True, type=Path, help="JSON credentials file, outside the repository")
    ap.add_argument("--generate", action="store_true", help="create the credentials file first")
    ap.add_argument("--port", type=int, default=7171, help="refuse to run while a server listens here")
    ap.add_argument("--no-backup", action="store_true", help=argparse.SUPPRESS)   # tests only
    args = ap.parse_args(argv)

    if inside_repo(args.secrets):
        raise SystemExit(f"{args.secrets} is inside the repository - keep credentials out of git")
    if not args.db.exists():
        raise SystemExit(f"{args.db} not found")
    if server_running(args.port):
        raise SystemExit(f"a server is listening on port {args.port} - stop it first")

    con = sqlite3.connect(args.db)
    try:
        if args.generate:
            if args.secrets.exists():
                raise SystemExit(f"{args.secrets} already exists - drop --generate to apply it")
            generate(args.secrets, con)
        creds = load(args.secrets)
        if not args.no_backup:
            backup = args.db.with_name(f"{args.db.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
            with sqlite3.connect(backup) as dst:
                con.backup(dst)
            print(f"backup: {backup}")
        warnings = apply(con, creds)
    finally:
        con.close()
    for w in warnings:
        print(f"warning: {w}")
    print(f"{len(ROLES)} accounts provisioned; credentials in {args.secrets}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

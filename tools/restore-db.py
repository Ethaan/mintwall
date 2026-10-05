"""Restore a backup made by tools/backup-db.py into the server's database (docs/production-plan.md "3b").

The server must be stopped: it refuses while anything answers on the server's port (config.lua Port / IP, or
--port), and on Windows the rename below also fails while a process holds the database open.
Steps:
  1. unpacks the backup (.db3.gz or .db3) to a temporary file next to the database and runs
     PRAGMA integrity_check on it - a bad backup never replaces anything;
  2. moves the current database aside, with its -wal / -shm files if any (they may hold the last committed
     writes), as <db>.pre-restore-<UTC time> (+ -wal / -shm, so SQLite can still open it there);
  3. moves the restored copy into place.

Usage:
  python tools/restore-db.py backups/db-hourly-20261005T130000Z.db3.gz
  python tools/restore-db.py --latest                  newest backup in backups/ (or --dest / MINTWALL_BACKUP_DIR)
  python tools/restore-db.py --latest --db scratch.db3 --yes   restore drill into a scratch file
Exit codes: 0 restored, 1 error, 2 refused (server running / not confirmed).
"""
import argparse
import datetime as dt
import gzip
import os
import re
import shutil
import socket
import sqlite3
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO / "server" / "db.db3"
DEFAULT_CONFIG = REPO / "server" / "config.lua"
DEFAULT_DEST = REPO / "backups"
NAME_RE = re.compile(r"^db-(hourly|daily)-(\d{8}T\d{6}Z)(?:-(\d+))?\.db3(\.gz)?$")


def config_value(config: Path, key: str):
    """The first `Key = "value"` / `Key = 123` in config.lua, or None."""
    try:
        text = config.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r'^\s*' + re.escape(key) + r'\s*=\s*"?([^"\s,]+)"?', text, re.M)
    return m.group(1) if m else None


def listening(port: int, hosts) -> str:
    """The first host:port that accepts a TCP connection, or ''."""
    for host in hosts:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return f"{host}:{port}"
        except OSError:
            continue
    return ""


def newest_backup(dest: Path) -> Path:
    found = []
    for p in dest.iterdir() if dest.is_dir() else []:
        m = NAME_RE.match(p.name)
        if m and p.is_file():
            found.append(((m.group(2), int(m.group(3) or 1)), p))
    if not found:
        raise SystemExit(f"error: no backups in {dest}")
    return max(found)[1]


def unpack(backup: Path, out: Path) -> None:
    opener = gzip.open if backup.name.endswith(".gz") else open
    with opener(backup, "rb") as f, open(out, "wb") as g:
        shutil.copyfileobj(f, g, 1024 * 1024)
        g.flush()
        os.fsync(g.fileno())


def check(path: Path) -> list:
    con = sqlite3.connect(str(path))
    try:
        return [r[0] for r in con.execute("PRAGMA integrity_check")]
    except sqlite3.DatabaseError as e:                           # "file is not a database"...
        return [str(e)]
    finally:
        con.close()


def restore(backup: Path, db: Path, now: dt.datetime = None) -> Path:
    """Restores backup into db; returns where the previous database went (or None if there was none)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    if not backup.is_file():
        raise SystemExit(f"error: no backup at {backup}")
    db.parent.mkdir(parents=True, exist_ok=True)
    tmp = db.with_name(f".restore-{os.getpid()}-{db.name}")
    try:
        unpack(backup, tmp)
        result = check(tmp)
        if result != ["ok"]:
            raise SystemExit(f"error: {backup.name} fails integrity_check: {result[:5]} - nothing changed")
        for side in ("-wal", "-shm", "-journal"):                # check() may leave none, but be sure
            Path(str(tmp) + side).unlink(missing_ok=True)

        aside = None
        if db.exists():
            aside = db.with_name(f"{db.name}.pre-restore-{now.strftime('%Y%m%dT%H%M%SZ')}")
            try:
                os.replace(db, aside)                            # fails on Windows while the server has it open
            except PermissionError:
                raise SystemExit(f"error: cannot move {db} aside - is the server (or another program) using it?")
            for side in ("-wal", "-shm"):
                p = Path(str(db) + side)
                if p.exists():
                    os.replace(p, Path(str(aside) + side))
        os.replace(tmp, db)
        return aside
    finally:
        tmp.unlink(missing_ok=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("backup", nargs="?", type=Path, help="backup file (.db3.gz or .db3)")
    ap.add_argument("--latest", action="store_true", help="the newest backup in --dest")
    ap.add_argument("--dest", type=Path, default=Path(os.environ.get("MINTWALL_BACKUP_DIR", DEFAULT_DEST)),
                    help="backup directory for --latest (default backups/, or MINTWALL_BACKUP_DIR)")
    ap.add_argument("--db", type=Path, default=DEFAULT_DB, help="database to replace (default server/db.db3)")
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="config.lua for the port check")
    ap.add_argument("--port", type=int, help="port the server listens on (default: config.lua Port, 7171)")
    ap.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    a = ap.parse_args(argv)

    if bool(a.backup) == a.latest:
        ap.error("give a backup file or --latest")
    backup = newest_backup(a.dest.resolve()) if a.latest else a.backup.resolve()
    db = a.db.resolve()

    port = a.port or int(config_value(a.config, "Port") or 7171)
    hosts = ["127.0.0.1"]
    ip = config_value(a.config, "IP")
    if a.port is None and ip and ip not in hosts:
        hosts.append(ip)
    busy = listening(port, hosts)
    if busy:
        print(f"refused: something is listening on {busy} - stop the server first", file=sys.stderr)
        return 2

    print(f"restore {backup}\n   into {db}")
    if not a.yes:
        try:                                                     # (NUL counts as a tty on Windows)
            answer = input("Type 'restore' to go on: ") if sys.stdin.isatty() else ""
        except EOFError:
            answer = ""
        if answer.strip() != "restore":
            print("refused: not confirmed", file=sys.stderr)
            return 2

    aside = restore(backup, db)
    if aside:
        print(f"previous database kept as {aside}")
    print("restored; integrity_check ok. Start the server and check a character logs in.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

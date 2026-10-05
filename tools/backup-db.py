"""Online backup of the server's SQLite database (docs/production-plan.md "3b. Backups").

Safe while the server runs: it uses SQLite's online backup API in one step, which reads one consistent
snapshot (a single read transaction; in WAL mode the server's writes go on meanwhile and are not in the copy).
Each run:
  1. copies the database to a temporary file, switches the copy to a self-contained rollback-journal file
     (the server puts it back in WAL mode when it opens it) and runs PRAGMA integrity_check on it;
  2. gzips it to <dest>/db-<kind>-<UTC time>.db3.gz (atomic rename, so a half-written backup never has the
     final name);
  3. kind "auto" (the default, meant for an hourly schedule): an hourly backup, plus a daily one when there is
     none yet for today (UTC);
  4. optional upload: --upload-cmd (or MINTWALL_BACKUP_UPLOAD) is a shell command run once per new file, with
     {path}, {name} and {kind} filled in, e.g. (production, S3 per the plan):
       --upload-cmd "aws s3 cp \"{path}\" \"s3://BUCKET/mintwall/{kind}/{name}\" --sse aws:kms --only-show-errors"
     A failed upload exits with code 3 (the local backup stays);
  5. rotation: keeps the newest --keep-hourly hourly and --keep-daily daily backups in <dest>; only files named
     like its own backups are ever deleted (the S3 copies age out by the bucket's lifecycle rules instead).

Usage:
  python tools/backup-db.py                         server/db.db3 -> backups/ (repo root)
  python tools/backup-db.py --dest D:\\mintwall-backups --keep-hourly 48 --keep-daily 14
  python tools/backup-db.py --kind daily            a daily backup now, regardless of today's
Exit codes: 0 ok, 1 error (no database, failed integrity check...), 3 upload failed.
Standard library only (Python 3.9+), so it also runs on the plan's Linux host.
"""
import argparse
import datetime as dt
import gzip
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO / "server" / "db.db3"
DEFAULT_DEST = REPO / "backups"
KINDS = ("hourly", "daily")
# db-hourly-20261005T130000Z.db3.gz (a -2, -3... suffix when two backups land in the same second)
NAME_RE = re.compile(r"^db-(hourly|daily)-(\d{8}T\d{6}Z)(?:-(\d+))?\.db3(\.gz)?$")
STAMP = "%Y%m%dT%H%M%SZ"


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def list_backups(dest: Path, kind: str = None):
    """[(path, kind, time, seq)] of the backups in dest, newest first."""
    found = []
    if not dest.is_dir():
        return found
    for p in dest.iterdir():
        m = NAME_RE.match(p.name)
        if not m or not p.is_file():
            continue
        if kind is not None and m.group(1) != kind:
            continue
        when = dt.datetime.strptime(m.group(2), STAMP).replace(tzinfo=dt.timezone.utc)
        found.append((p, m.group(1), when, int(m.group(3) or 1)))
    found.sort(key=lambda b: (b[2], b[3]), reverse=True)
    return found


def snapshot(db: Path, out: Path) -> None:
    """Consistent copy of db into out (a new file), checked with integrity_check."""
    if not db.is_file():
        raise SystemExit(f"error: no database at {db}")
    # a normal connection (a mode=ro one cannot always open a WAL database whose -shm is missing), made read-only
    src = sqlite3.connect(str(db), timeout=30)
    try:
        src.execute("PRAGMA query_only=ON")
        dst = sqlite3.connect(str(out))
        try:
            src.backup(dst)                                  # pages=-1: one step, one read transaction
            dst.execute("PRAGMA journal_mode=DELETE")        # one self-contained file, no -wal next to it
            result = [r[0] for r in dst.execute("PRAGMA integrity_check")]
        finally:
            dst.close()
    finally:
        src.close()
    if result != ["ok"]:
        out.unlink(missing_ok=True)
        raise SystemExit(f"error: integrity_check of the copy failed: {result[:5]}")


def unique_name(dest: Path, kind: str, when: dt.datetime, compress: bool) -> Path:
    ext = ".db3.gz" if compress else ".db3"
    base = f"db-{kind}-{when.strftime(STAMP)}"
    path, n = dest / (base + ext), 1
    while path.exists():
        n += 1
        path = dest / f"{base}-{n}{ext}"
    return path


def store(snap: Path, final: Path, compress: bool) -> None:
    tmp = final.with_name(".tmp-" + final.name)
    if compress:
        with open(snap, "rb") as f, gzip.open(tmp, "wb", compresslevel=6) as g:
            shutil.copyfileobj(f, g, 1024 * 1024)
    else:
        shutil.copyfile(snap, tmp)
    with open(tmp, "rb+") as f:
        os.fsync(f.fileno())
    os.replace(tmp, final)


def rotate(dest: Path, keep: dict) -> list:
    """Deletes the backups beyond the newest keep[kind] of each kind; returns the deleted paths."""
    deleted = []
    for kind in KINDS:
        for path, *_ in list_backups(dest, kind)[max(keep[kind], 0):]:
            path.unlink()
            deleted.append(path)
    return deleted


def upload(cmd: str, path: Path, kind: str) -> bool:
    line = cmd.format(path=str(path), name=path.name, kind=kind)
    print(f"upload: {path.name}")
    try:
        done = subprocess.run(line, shell=True, timeout=15 * 60)
    except subprocess.TimeoutExpired:
        print(f"error: upload of {path.name} timed out", file=sys.stderr)
        return False
    if done.returncode != 0:
        print(f"error: upload of {path.name} failed (exit code {done.returncode})", file=sys.stderr)
        return False
    return True


def run(db: Path, dest: Path, kind: str = "auto", keep_hourly: int = 48, keep_daily: int = 14,
        compress: bool = True, upload_cmd: str = None, now: dt.datetime = None) -> int:
    now = now or utcnow()
    dest.mkdir(parents=True, exist_ok=True)
    kinds = [kind] if kind != "auto" else ["hourly"]
    if kind == "auto":
        newest_daily = list_backups(dest, "daily")
        if not newest_daily or newest_daily[0][2].date() < now.date():
            kinds.append("daily")

    snap = dest / f".tmp-snapshot-{os.getpid()}.db3"
    written = []
    try:
        snapshot(db, snap)
        for k in kinds:
            final = unique_name(dest, k, now, compress)
            store(snap, final, compress)
            written.append((final, k))
            print(f"backup: {final} ({final.stat().st_size} bytes)")
    finally:
        snap.unlink(missing_ok=True)

    ok = True
    if upload_cmd:
        for path, k in written:
            ok = upload(upload_cmd, path, k) and ok

    for path in rotate(dest, {"hourly": keep_hourly, "daily": keep_daily}):
        print(f"rotated out: {path.name}")
    return 0 if ok else 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB, help="database to back up (default server/db.db3)")
    ap.add_argument("--dest", type=Path, default=Path(os.environ.get("MINTWALL_BACKUP_DIR", DEFAULT_DEST)),
                    help="backup directory (default backups/ in the repo, or MINTWALL_BACKUP_DIR)")
    ap.add_argument("--kind", choices=("auto",) + KINDS, default="auto",
                    help="auto: hourly + the day's first daily (default)")
    ap.add_argument("--keep-hourly", type=int, default=48)
    ap.add_argument("--keep-daily", type=int, default=14)
    ap.add_argument("--no-compress", action="store_true", help="plain .db3 files instead of .db3.gz")
    ap.add_argument("--upload-cmd", default=os.environ.get("MINTWALL_BACKUP_UPLOAD"),
                    help="shell command per new file; {path} {name} {kind} are filled in")
    a = ap.parse_args(argv)
    return run(a.db.resolve(), a.dest.resolve(), a.kind, a.keep_hourly, a.keep_daily,
               not a.no_compress, a.upload_cmd)


if __name__ == "__main__":
    sys.exit(main())

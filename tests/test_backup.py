"""Backups and restart supervision (docs/production-plan.md "3b"): tools/backup-db.py, tools/restore-db.py,
tools/install-service.ps1 (dry run), tools/service-run.ps1 and deploy/mintwall.service.

No game server: every database is a throwaway one in a temp dir (server/db.db3 is never opened), no service or
scheduled task is installed, and the port check runs against a dummy listening socket.
"""
import datetime as dt
import gzip
import importlib.util
import re
import shutil
import socket
import sqlite3
import subprocess
import sys
import threading
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "tools"
REAL_DB = REPO / "server" / "db.db3"
UTC = dt.timezone.utc


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), TOOLS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


backup = load("backup-db")
restore = load("restore-db")


# ---------------------------------------------------------------- helpers

def make_db(path: Path, rows: int = 20000) -> None:
    """A WAL database like the server's: a ledger whose total never changes, and a log counted in meta."""
    con = sqlite3.connect(str(path))
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript("""
        CREATE TABLE ledger (id INTEGER PRIMARY KEY, balance INTEGER NOT NULL);
        CREATE TABLE log (id INTEGER PRIMARY KEY, payload BLOB NOT NULL);
        CREATE TABLE meta (k TEXT PRIMARY KEY, v INTEGER NOT NULL);
        INSERT INTO meta VALUES ('log_rows', 0);
    """)
    con.executemany("INSERT INTO ledger (id, balance) VALUES (?, 1000)", [(i,) for i in range(100)])
    con.executemany("INSERT INTO log (payload) VALUES (?)", [(b"x" * 200,) for _ in range(rows)])
    con.execute("UPDATE meta SET v = ? WHERE k = 'log_rows'", (rows,))
    con.commit()
    con.close()


def consistent(path: Path) -> None:
    con = sqlite3.connect(str(path))
    try:
        assert [r[0] for r in con.execute("PRAGMA integrity_check")] == ["ok"]
        assert con.execute("SELECT SUM(balance) FROM ledger").fetchone()[0] == 100 * 1000
        logged = con.execute("SELECT v FROM meta WHERE k = 'log_rows'").fetchone()[0]
        assert con.execute("SELECT COUNT(*) FROM log").fetchone()[0] == logged
    finally:
        con.close()


def unpack(gz: Path, out: Path) -> Path:
    with gzip.open(gz, "rb") as f, open(out, "wb") as g:
        shutil.copyfileobj(f, g)
    return out


def names(dest: Path):
    return sorted(p.name for p in dest.iterdir())


@pytest.fixture(autouse=True)
def real_db_untouched():
    """The dev database is never touched: same size and mtime after each test."""
    before = REAL_DB.stat() if REAL_DB.exists() else None
    yield
    after = REAL_DB.stat() if REAL_DB.exists() else None
    if before is not None:
        assert (after.st_size, after.st_mtime_ns) == (before.st_size, before.st_mtime_ns)


# ---------------------------------------------------------------- backup

def test_backup_while_a_writer_changes_the_db_is_consistent(tmp_path):
    db, dest = tmp_path / "live.db3", tmp_path / "backups"
    make_db(db)
    stop, commits, errors = threading.Event(), [0], []

    def writer():
        con = sqlite3.connect(str(db), timeout=30)
        con.execute("PRAGMA journal_mode=WAL")
        n = 0
        try:
            while not stop.is_set():
                n += 1
                a, b = n % 100, (n * 7 + 3) % 100
                with con:                                    # one transaction: the invariants hold at commit
                    con.execute("UPDATE ledger SET balance = balance - 5 WHERE id = ?", (a,))
                    con.execute("UPDATE ledger SET balance = balance + 5 WHERE id = ?", (b,))
                    con.executemany("INSERT INTO log (payload) VALUES (?)", [(b"y" * 300,)] * 20)
                    con.execute("UPDATE meta SET v = v + 20 WHERE k = 'log_rows'")
                commits[0] += 1
        except Exception as e:                               # pragma: no cover - reported below
            errors.append(e)
        finally:
            con.close()

    t = threading.Thread(target=writer, daemon=True)
    t.start()
    try:
        made = []
        for i in range(8):
            start = commits[0]
            now = dt.datetime(2026, 10, 5, 10, 0, 0, tzinfo=UTC) + dt.timedelta(hours=i)
            assert backup.run(db, dest, kind="hourly", keep_hourly=100, now=now) == 0
            made.append(commits[0] - start)
    finally:
        stop.set()
        t.join(10)
    assert not errors, errors
    assert commits[0] > 0 and sum(made) > 0, "the writer never committed while backups ran"

    files = backup.list_backups(dest, "hourly")
    assert len(files) == 8
    rows = set()
    for i, (path, kind, *_rest) in enumerate(files):
        assert path.name.endswith(".db3.gz")
        copy = unpack(path, tmp_path / f"check{i}.db3")
        consistent(copy)
        con = sqlite3.connect(str(copy))
        assert con.execute("PRAGMA journal_mode").fetchone()[0] == "delete"   # self-contained file
        rows.add(con.execute("SELECT v FROM meta").fetchone()[0])
        con.close()
    assert len(rows) > 1, "every backup saw the same state: the writer did not run between them"
    assert not [p for p in dest.iterdir() if p.name.startswith(".tmp-")]


def test_backup_cli(tmp_path):
    db, dest = tmp_path / "live.db3", tmp_path / "out"
    make_db(db, rows=100)
    done = subprocess.run([sys.executable, str(TOOLS / "backup-db.py"), "--db", str(db), "--dest", str(dest)],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    got = names(dest)
    assert len(got) == 2 and got[0].startswith("db-daily-") and got[1].startswith("db-hourly-"), got
    consistent(unpack(dest / got[1], tmp_path / "c.db3"))


def test_backup_without_a_database_fails(tmp_path):
    with pytest.raises(SystemExit):
        backup.run(tmp_path / "missing.db3", tmp_path / "out")
    assert not [p for p in (tmp_path / "out").iterdir() if backup.NAME_RE.match(p.name)]


# ---------------------------------------------------------------- rotation

def test_rotation_keeps_the_newest_of_each_kind(tmp_path):
    dest = tmp_path / "b"
    dest.mkdir()
    t0 = dt.datetime(2026, 10, 1, tzinfo=UTC)
    for h in range(10):
        (dest / f"db-hourly-{(t0 + dt.timedelta(hours=h)).strftime(backup.STAMP)}.db3.gz").write_bytes(b"h")
    for d in range(5):
        (dest / f"db-daily-{(t0 + dt.timedelta(days=d)).strftime(backup.STAMP)}.db3.gz").write_bytes(b"d")
    (dest / "db-hourly-20261001T090000Z-2.db3.gz").write_bytes(b"h")   # same second as hour 9, newer
    for other in ("notes.txt", "db-weekly-20261001T000000Z.db3.gz", "db.db3", "db-hourly-junk.db3.gz"):
        (dest / other).write_bytes(b"keep me")

    deleted = backup.rotate(dest, {"hourly": 3, "daily": 2})
    assert len(deleted) == 8 + 3
    assert names(dest) == sorted([
        "db-hourly-20261001T090000Z-2.db3.gz", "db-hourly-20261001T090000Z.db3.gz",
        "db-hourly-20261001T080000Z.db3.gz",
        "db-daily-20261005T000000Z.db3.gz", "db-daily-20261004T000000Z.db3.gz",
        "notes.txt", "db-weekly-20261001T000000Z.db3.gz", "db.db3", "db-hourly-junk.db3.gz",
    ])


def test_auto_takes_one_daily_per_day_and_rotates(tmp_path):
    db, dest = tmp_path / "live.db3", tmp_path / "b"
    make_db(db, rows=10)
    day1 = dt.datetime(2026, 10, 5, 0, 30, tzinfo=UTC)
    for h in range(5):                                      # 5 hours on day 1
        backup.run(db, dest, keep_hourly=3, keep_daily=2, now=day1 + dt.timedelta(hours=h))
    assert [b[1] for b in backup.list_backups(dest)] == ["hourly"] * 3 + ["daily"]
    for d in (1, 2):                                        # the first run of each new day adds a daily
        backup.run(db, dest, keep_hourly=3, keep_daily=2, now=day1 + dt.timedelta(days=d))
    daily = backup.list_backups(dest, "daily")
    assert [b[2].date() for b in daily] == [dt.date(2026, 10, 7), dt.date(2026, 10, 6)]
    assert len(backup.list_backups(dest, "hourly")) == 3
    backup.run(db, dest, kind="daily", keep_daily=2, now=day1 + dt.timedelta(days=2, hours=1))   # forced
    assert len(backup.list_backups(dest, "daily")) == 2


def test_two_backups_in_the_same_second_both_kept(tmp_path):
    db, dest = tmp_path / "live.db3", tmp_path / "b"
    make_db(db, rows=10)
    now = dt.datetime(2026, 10, 5, 12, tzinfo=UTC)
    backup.run(db, dest, kind="hourly", now=now)
    backup.run(db, dest, kind="hourly", now=now)
    assert names(dest) == ["db-hourly-20261005T120000Z-2.db3.gz", "db-hourly-20261005T120000Z.db3.gz"]
    assert backup.list_backups(dest)[0][0].name.endswith("-2.db3.gz")


# ---------------------------------------------------------------- upload hook

def test_upload_command_gets_each_new_file(tmp_path):
    db, dest, bucket = tmp_path / "live.db3", tmp_path / "b", tmp_path / "bucket"
    make_db(db, rows=10)
    bucket.mkdir()
    cmd = (f'"{sys.executable}" -c "import shutil, sys; shutil.copy(sys.argv[1], sys.argv[2])" '
           f'"{{path}}" "{bucket}/{{kind}}-{{name}}"')
    assert backup.run(db, dest, upload_cmd=cmd, now=dt.datetime(2026, 10, 5, 3, tzinfo=UTC)) == 0
    assert names(bucket) == ["daily-db-daily-20261005T030000Z.db3.gz", "hourly-db-hourly-20261005T030000Z.db3.gz"]


def test_failed_upload_exits_3_and_keeps_the_backup(tmp_path):
    db, dest = tmp_path / "live.db3", tmp_path / "b"
    make_db(db, rows=10)
    cmd = f'"{sys.executable}" -c "import sys; sys.exit(7)"'
    assert backup.run(db, dest, kind="hourly", upload_cmd=cmd) == 3
    assert len(backup.list_backups(dest)) == 1


# ---------------------------------------------------------------- restore

@pytest.fixture
def restore_setup(tmp_path):
    """A 'current' database with a pending WAL, and a backup of an older state."""
    old, dest, target = tmp_path / "old.db3", tmp_path / "b", tmp_path / "server" / "db.db3"
    make_db(old, rows=10)
    backup.run(old, dest, kind="hourly", now=dt.datetime(2026, 10, 5, 1, tzinfo=UTC))
    backup.run(old, dest, kind="hourly", now=dt.datetime(2026, 10, 5, 2, tzinfo=UTC))
    target.parent.mkdir()
    make_db(target, rows=50)
    return dest, target


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def log_rows(db: Path) -> int:
    con = sqlite3.connect(str(db))
    try:
        return con.execute("SELECT COUNT(*) FROM log").fetchone()[0]
    finally:
        con.close()


def test_restore_refuses_while_the_server_port_listens(restore_setup, tmp_path):
    dest, target = restore_setup
    before = target.read_bytes()
    with socket.socket() as srv:                            # a stand-in game server
        srv.bind(("127.0.0.1", 0))
        srv.listen()
        port = srv.getsockname()[1]
        code = restore.main(["--latest", "--dest", str(dest), "--db", str(target), "--port", str(port), "--yes"])
    assert code == 2
    assert target.read_bytes() == before
    assert sorted(p.name for p in target.parent.iterdir()) == ["db.db3"]


def test_restore_reads_the_port_from_config(restore_setup, tmp_path):
    dest, target = restore_setup
    with socket.socket() as srv:
        srv.bind(("127.0.0.1", 0))
        srv.listen()
        config = tmp_path / "config.lua"
        config.write_text(f'    IP = "127.0.0.1"\n    Port = "{srv.getsockname()[1]}"\n')
        code = restore.main(["--latest", "--dest", str(dest), "--db", str(target), "--config", str(config), "--yes"])
    assert code == 2


def test_restore_when_stopped_moves_the_current_db_aside(restore_setup, tmp_path):
    dest, target = restore_setup
    # leave committed writes in the -wal, as a crashed server would
    keep = sqlite3.connect(str(target))
    keep.execute("PRAGMA wal_autocheckpoint=0")
    with keep:
        keep.execute("INSERT INTO log (payload) VALUES (x'00')")
        keep.execute("UPDATE meta SET v = v + 1")
    wal = Path(str(target) + "-wal")
    assert wal.exists() and wal.stat().st_size > 0
    snapshot = tmp_path / "wal-copy"
    snapshot.mkdir()
    for p in (target, wal):
        shutil.copy(p, snapshot / p.name)
    keep.close()                                            # the last connection checkpoints and removes the WAL:
    for p in snapshot.iterdir():                            # put the crash state (db + WAL) back
        shutil.copy(p, target.parent / p.name)
    assert wal.stat().st_size > 0

    code = restore.main(["--latest", "--dest", str(dest), "--db", str(target), "--port", str(free_port()), "--yes"])
    assert code == 0
    assert log_rows(target) == 10                           # the backup's state
    consistent(target)
    aside = [p for p in target.parent.iterdir() if p.name.startswith("db.db3.pre-restore-")]
    main = [p for p in aside if re.fullmatch(r"db\.db3\.pre-restore-\d{8}T\d{6}Z", p.name)]
    assert len(main) == 1 and Path(str(main[0]) + "-wal") in aside
    assert log_rows(main[0]) == 51                          # the previous database, its WAL included
    assert not Path(str(target) + "-wal").exists() or Path(str(target) + "-wal").stat().st_size == 0


def test_restore_picks_the_newest_backup(restore_setup):
    dest, _ = restore_setup
    assert restore.newest_backup(dest).name == "db-hourly-20261005T020000Z.db3.gz"


def test_restore_refuses_a_corrupt_backup(restore_setup, tmp_path):
    _, target = restore_setup
    bad = tmp_path / "db-hourly-20261005T050000Z.db3"
    bad.write_bytes(b"SQLite format 3\x00" + b"\xff" * 4096)
    before = log_rows(target)
    with pytest.raises(SystemExit):
        restore.restore(bad, target)
    assert log_rows(target) == before
    assert not [p for p in target.parent.iterdir() if "pre-restore" in p.name or p.name.startswith(".restore-")]


def test_restore_cli_without_yes_and_no_tty_refuses(restore_setup):
    dest, target = restore_setup
    done = subprocess.run([sys.executable, str(TOOLS / "restore-db.py"), "--latest", "--dest", str(dest),
                           "--db", str(target), "--port", str(free_port())],
                          stdin=subprocess.DEVNULL, capture_output=True, text=True)
    assert done.returncode == 2 and "not confirmed" in done.stderr
    assert log_rows(target) == 50


# ---------------------------------------------------------------- Windows service (NSSM), dry run only

def powershell(*args, timeout=60):
    return subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", *args],
                          capture_output=True, text=True, timeout=timeout)


windows = pytest.mark.skipif(sys.platform != "win32", reason="Windows PowerShell")


@windows
def test_install_service_dry_run_prints_the_nssm_commands(tmp_path):
    logs = tmp_path / "logs"
    done = powershell("-File", str(TOOLS / "install-service.ps1"), "-DryRun", "-LogDir", str(logs),
                      "-NssmPath", r"C:\nowhere\nssm.exe", "-ServiceAccount", r".\mintwall",
                      "-ServicePassword", "hunter2 secret", "-Start")
    assert done.returncode == 0, done.stderr
    out = done.stdout
    assert out.startswith("DRY RUN")
    assert not logs.exists()                                 # nothing created
    lines = [l for l in out.splitlines() if l.startswith("nssm ")]
    assert lines[0].startswith("nssm install mintwall ") and lines[0].endswith("powershell.exe")
    server = str(REPO / "server")
    expected = [
        f"nssm set mintwall AppDirectory {server}",
        "nssm set mintwall Start SERVICE_AUTO_START",
        "nssm set mintwall AppExit Default Restart",
        "nssm set mintwall AppKillProcessTree 1",
        "nssm set mintwall AppStdin NUL",
        f"nssm set mintwall AppStdout {logs}\\server-stdout.log",
        f"nssm set mintwall AppStderr {logs}\\server-stderr.log",
        "nssm set mintwall AppRotateFiles 1",
        "nssm set mintwall AppRotateOnline 1",
        "nssm set mintwall AppRotateBytes 10485760",
        r"nssm set mintwall ObjectName .\mintwall ********",
        "nssm start mintwall",
    ]
    for line in expected:
        assert line in lines, line
    assert "hunter2" not in out
    params = next(l for l in lines if " AppParameters " in l)
    assert "service-run.ps1" in params and f'-ServerDir \\"{server}\\"' in params
    assert any(re.fullmatch(r"nssm set mintwall AppStopMethodConsole \d+", l) for l in lines)


@windows
def test_install_service_whatif_and_uninstall_dry_run():
    done = powershell("-File", str(TOOLS / "install-service.ps1"), "-WhatIf", "-Uninstall",
                      "-ServiceName", "mintwall-test-never-installed")
    assert done.returncode == 0, done.stderr
    lines = [l for l in done.stdout.splitlines() if l.startswith("nssm ")]
    assert lines == ["nssm stop mintwall-test-never-installed", "nssm remove mintwall-test-never-installed confirm"]


@windows
def test_service_run_logs_planned_exits_and_backs_off_after_crashes(tmp_path):
    logs = tmp_path / "logs"
    script = TOOLS / "service-run.ps1"

    def run(exit_code):
        cmd = (f"& '{script}' -ServerDir '{tmp_path}' -LogDir '{logs}' -Exe cmd.exe -ExeArgs '/c','exit {exit_code}'"
               f" -BaseDelay 1 -MaxDelay 2; exit $LASTEXITCODE")
        return powershell("-Command", cmd)

    assert run(10).returncode == 10
    assert run(0).returncode == 0
    assert run(3).returncode == 3
    assert run(3).returncode == 3
    assert run(3).returncode == 3
    log = (logs / "supervisor.log").read_text(encoding="utf-8-sig").splitlines()
    notes = [l.split(" ", 2)[2] for l in log if not l.split(" ", 2)[2].startswith("start ")]
    assert notes[0].startswith("exit 10 after ") and notes[0].endswith("planned restart (daily server save)")
    assert notes[1].startswith("exit 0 after ") and "clean shutdown" in notes[1]
    assert re.match(r"CRASH exit 3 \(0x00000003\) after \d+s; 1 crash\(es\) in the last 15 min; restart in 1s", notes[2])
    assert notes[3].endswith("2 crash(es) in the last 15 min; restart in 2s")
    assert notes[4].endswith("3 crash(es) in the last 15 min; restart in 2s")   # capped at MaxDelay
    assert len((logs / "crashes.txt").read_text(encoding="utf-8-sig").split()) == 3


@windows
def test_service_run_passes_the_server_output_through(tmp_path):
    """NSSM captures the wrapper's stdout/stderr: the server's must reach them."""
    cmd = (f"& '{TOOLS / 'service-run.ps1'}' -ServerDir '{tmp_path}' -LogDir '{tmp_path / 'logs'}' -Exe cmd.exe "
           f"-ExeArgs '/c','echo to-stdout & echo to-stderr 1>&2 & exit 10'; exit $LASTEXITCODE")
    done = powershell("-Command", cmd)
    assert done.returncode == 10
    assert "to-stdout" in done.stdout and "to-stderr" in done.stderr


@windows
def test_service_run_prunes_old_rotated_logs(tmp_path):
    logs = tmp_path / "logs"
    logs.mkdir()
    import os
    import time
    for i in range(5):
        p = logs / f"server-stdout-2026100{i}T000000.000.log"
        p.write_text("x")
        os.utime(p, (time.time() - 1000 + i, time.time() - 1000 + i))
    (logs / "server-stdout.log").write_text("live")
    cmd = (f"& '{TOOLS / 'service-run.ps1'}' -ServerDir '{tmp_path}' -LogDir '{logs}' -Exe cmd.exe "
           f"-ExeArgs '/c','exit 10' -KeepRotated 2; exit $LASTEXITCODE")
    assert powershell("-Command", cmd).returncode == 10
    assert sorted(p.name for p in logs.glob("server-stdout*")) == [
        "server-stdout-20261003T000000.000.log", "server-stdout-20261004T000000.000.log", "server-stdout.log"]


# ---------------------------------------------------------------- systemd unit, static checks

def parse_unit(path: Path) -> dict:
    sections, current = {}, None
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        m = re.fullmatch(r"\[(\w+)\]", line)
        if m:
            current = sections.setdefault(m.group(1), {})
            continue
        assert current is not None, f"line {n} outside a section"
        assert not raw.endswith("\\"), f"line {n}: no continuation lines"
        key, sep, value = line.partition("=")
        assert sep and re.fullmatch(r"[A-Za-z]+", key), f"line {n} is not Key=value: {raw}"
        current.setdefault(key, []).append(value)
    return sections


def test_systemd_unit_static_checks():
    unit = parse_unit(REPO / "deploy" / "mintwall.service")
    assert set(unit) == {"Unit", "Service", "Install"}
    svc = unit["Service"]
    one = {k: v[-1] for k, v in svc.items()}
    assert one["Restart"] == "always"
    assert int(one["RestartSec"]) > 0
    assert "10" in one["SuccessExitStatus"].split()
    assert one["StandardInput"] == "null"
    assert one["User"] not in ("root", "0")                  # otserv.cpp refuses to run as root
    assert one["ExecStart"].startswith("/") and one["WorkingDirectory"].startswith("/")
    assert one["ExecStart"].startswith(one["WorkingDirectory"] + "/")
    assert int(one["TimeoutStopSec"]) >= 30
    assert one["ReadWritePaths"] == one["WorkingDirectory"]
    assert one["StandardOutput"] == "journal" and one["StandardError"] == "journal"
    # $ is systemd's; the shell's variables need $$
    post = one["ExecStopPost"]
    assert "$$EXIT_STATUS" in post and "$$SERVICE_RESULT" in post
    assert not re.search(r"(?<!\$)\$(?!\$)", post.replace("$$", ""))
    assert "planned restart" in post and "CRASH" in post
    assert int(unit["Unit"]["StartLimitBurst"][-1]) >= 3
    assert int(unit["Unit"]["StartLimitIntervalSec"][-1]) > 0
    assert unit["Install"]["WantedBy"] == ["multi-user.target"]
    assert "\r" not in (REPO / "deploy" / "mintwall.service").read_bytes().decode()   # LF only for Linux

"""Starts an isolated test server: own config, own SQLite database, own port."""
import os
import re
import socket
import sqlite3
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = ROOT / "server"
# MINTWALL_TEST_RUN / MINTWALL_TEST_PORT: a folder and a port of its own for each pytest session running at the same
# time (several agents at once); the default is the one session tests/.run on 7181.
#
# Under pytest-xdist each worker runs its own session in its own process, so every worker needs its OWN server on its
# OWN port and run folder or they collide. xdist sets PYTEST_XDIST_WORKER ("gw0", "gw1", ...) in each worker; from it
# we derive port = base (7300, or MINTWALL_TEST_PORT) + worker index and run dir tests/.run-gwN (or a per-worker
# subfolder of MINTWALL_TEST_RUN when that is set). Base 7300 keeps workers clear of the dev server on 7171. Without
# xdist (PYTEST_XDIST_WORKER unset) behaviour is exactly as before: MINTWALL_TEST_PORT / .run, default 7181 / tests/.run.
_WORKER = os.environ.get("PYTEST_XDIST_WORKER")   # "gw0", "gw1", ... when running under pytest-xdist, else None


def _worker_index(worker: str) -> int:
    m = re.search(r"\d+", worker)
    return int(m.group()) if m else 0


if _WORKER:
    TEST_PORT = int(os.environ.get("MINTWALL_TEST_PORT", "7300")) + _worker_index(_WORKER)
    RUN_DIR = (Path(os.environ["MINTWALL_TEST_RUN"]) / _WORKER if os.environ.get("MINTWALL_TEST_RUN")
               else ROOT / "tests" / f".run-{_WORKER}")
else:
    RUN_DIR = Path(os.environ["MINTWALL_TEST_RUN"]) if os.environ.get("MINTWALL_TEST_RUN") else ROOT / "tests" / ".run"
    TEST_PORT = int(os.environ.get("MINTWALL_TEST_PORT", "7181"))   # 7171: watch in your client (tibia74/watch.py)
TESTER_GROUP = 2   # see prepare()
SPAWN_RATE = 20    # RateSpawn of the test server, see prepare()


class ServerProcess:
    def __init__(self, port: int = TEST_PORT, run_dir: Path = RUN_DIR, config: dict = None, setup=None):
        """config: extra config.lua values (appended, so they win); setup(db_path): called on the fresh database
        before the server starts (test_server_save.py puts its houses there)."""
        self.port = port
        self.run_dir = Path(run_dir)
        self.db_path = self.run_dir / "test.db3"
        self.config_path = self.run_dir / "config.lua"
        self.log_path = self.run_dir / "server.log"
        self.config = config or {}
        self.setup = setup
        self.proc = None
        self._job = None
        self.started_at = None
        self._log_file = None

    # --- setup -------------------------------------------------------------
    def prepare(self):
        self.run_dir.mkdir(parents=True, exist_ok=True)
        if self.db_path.exists():
            self.db_path.unlink()
        con = sqlite3.connect(self.db_path)
        con.executescript((SERVER_DIR / "sql" / "schema.sqlite").read_text(encoding="latin-1"))
        con.executescript((SERVER_DIR / "sql" / "seed.sql").read_text(encoding="latin-1"))
        # Test-only group for scripted NPC visits: talks fast without being muted, and roaming monsters
        # cannot attack it (a fight blocks the logout that saves the character the test then checks)
        flags = 1 << 36 | 1 << 3   # PlayerFlag_CannotBeMuted, PlayerFlag_CannotBeAttacked
        con.execute('INSERT INTO groups (id, name, flags, access, maxdepotitems, maxviplist)'
                    ' VALUES (?, ?, ?, 0, 1000, 50)', (TESTER_GROUP, "Tester", flags))
        con.commit()
        con.close()

        cfg = (SERVER_DIR / "config.lua").read_text(encoding="latin-1")
        db = self.db_path.as_posix()
        cfg = re.sub(r'(\bSQL_DB\s*=\s*)"[^"]*"', lambda m: f'{m.group(1)}"{db}"', cfg)
        cfg = re.sub(r'(\bPort\s*=\s*)"[^"]*"', lambda m: f'{m.group(1)}"{self.port}"', cfg)
        cfg = re.sub(r'(\bSaveInterval\s*=\s*)\d+', lambda m: f'{m.group(1)}15', cfg)   # test_save.py waits for it
        cfg = re.sub(r'(\bMaxPlayers\s*=\s*)"\d+"', lambda m: f'{m.group(1)}"500"', cfg)  # test_save_load.py: 100+
        # every test character logs in from 127.0.0.1, many within seconds (next_to tries up to eight tiles): the
        # brute-force guard (LoginTries logins less than RetryTimeout apart disable the IP) would lock the tests out
        cfg = re.sub(r'(\bLoginTries\s*=\s*)\d+', lambda m: f'{m.group(1)}0', cfg)
        # respawn 20x faster than CipSoft's times (src/spawn.cpp divides every spot's delay by it): 600 s spots come
        # back after 15-30 s, close to the old 60 s test world; test_spawns.py measures with it
        cfg = re.sub(r'(\bRateSpawn\s*=\s*)\d+', lambda m: f'{m.group(1)}{SPAWN_RATE}', cfg)
        # the daily server save (globalevents/scripts/serversave.lua) would shut a test server down at its hour;
        # test_server_save.py turns it on for its own server
        cfg = re.sub(r'(\bServerSaveEnabled\s*=\s*)\w+', lambda m: f'{m.group(1)}false', cfg)
        for key, value in self.config.items():
            cfg += f"\n{key} = {_lua(value)}\n"
        self.config_path.write_text(cfg, encoding="latin-1")
        if self.setup:
            self.setup(self.db_path)

    # --- lifecycle ---------------------------------------------------------
    def start(self, timeout: float = 120.0):
        if _port_open(self.port):
            raise RuntimeError(f"port {self.port} is already in use - is another test server running?")
        exe = SERVER_DIR / "avesta74.exe"
        if not exe.exists():
            raise RuntimeError(f"{exe} not found - run server\\build.bat first")
        self.prepare()
        self._log_file = open(self.log_path, "wb")
        self.proc = subprocess.Popen(
            [str(exe), "-c", str(self.config_path)],
            cwd=SERVER_DIR, stdout=self._log_file, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
        )
        self._job = _dies_with_us(self.proc)
        # a failed start stops the server it started: a fixture whose setup raised gets no teardown, and the job
        # object only ends the server with pytest - until then it would run on, holding its port and run folder
        try:
            deadline = time.time() + timeout
            while time.time() < deadline:
                if self.proc.poll() is not None:
                    raise RuntimeError(f"server exited during startup:\n{self.log_tail()}")
                if "Server Running" in self.log() and _port_open(self.port):
                    self.started_at = time.time()      # the map is loaded: its items' timers start from here
                    return
                time.sleep(0.5)
            raise RuntimeError(f"server did not start within {timeout}s:\n{self.log_tail()}")
        except BaseException:      # also a Ctrl+C while the map loads
            self.stop()
            raise

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(10)
        if self._log_file:
            self._log_file.close()
            self._log_file = None

    # --- log inspection ----------------------------------------------------
    def log(self) -> str:
        try:
            return self.log_path.read_bytes().decode("latin-1")
        except FileNotFoundError:
            return ""

    def log_tail(self, n: int = 40) -> str:
        return "\n".join(self.log().splitlines()[-n:])

    def log_offset(self) -> int:
        return len(self.log())

    def lua_errors(self, since: int = 0) -> list[str]:
        """Lua errors logged after `since` (a log_offset()), each with its following lines."""
        lines = self.log()[since:].splitlines()
        errors = []
        for i, line in enumerate(lines):
            if "Lua Script Error" in line:
                errors.append("\n".join(lines[i:i + 5]))
        return errors


def _dies_with_us(proc):
    """Windows: put the server into a job object that kills it when this process ends, however it ends - a pytest
    stopped by a timeout (or killed) takes its server along instead of leaving it running on the port. Returns the
    job handle (kept open as long as we live), or None where that is not possible."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class Basic(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class Extended(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", Basic), ("IoInfo", ctypes.c_uint64 * 6),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateJobObjectW.restype = wintypes.HANDLE
        k32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        k32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
        k32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        job = k32.CreateJobObjectW(None, None)
        info = Extended()
        info.BasicLimitInformation.LimitFlags = 0x2000          # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not job or not k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))                 or not k32.AssignProcessToJobObject(job, int(proc._handle)):
            return None
        return job
    except (OSError, AttributeError):
        return None


def _lua(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return str(value)


def _port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0

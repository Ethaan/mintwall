"""Starts an isolated test server: own config, own SQLite database, own port."""
import re
import socket
import sqlite3
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SERVER_DIR = ROOT / "server"
RUN_DIR = ROOT / "tests" / ".run"
TEST_PORT = 7181
TESTER_GROUP = 2   # see prepare()


class ServerProcess:
    def __init__(self, port: int = TEST_PORT):
        self.port = port
        self.run_dir = RUN_DIR
        self.db_path = RUN_DIR / "test.db3"
        self.config_path = RUN_DIR / "config.lua"
        self.log_path = RUN_DIR / "server.log"
        self.proc = None
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
        self.config_path.write_text(cfg, encoding="latin-1")

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
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise RuntimeError(f"server exited during startup:\n{self.log_tail()}")
            if "Server Running" in self.log() and _port_open(self.port):
                return
            time.sleep(0.5)
        raise RuntimeError(f"server did not start within {timeout}s:\n{self.log_tail()}")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
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


def _port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", port)) == 0

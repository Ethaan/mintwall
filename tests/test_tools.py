"""The developer tools in tools/: walk-trace.py's run folder and ports (parallel runs must not overwrite each other),
talk-test.ps1's NPC visits (GM /goto or a database move) and its refusal of the dev server."""
import importlib.util
import socket
import subprocess
import sys

import pytest

from tibia74.server import ROOT, SERVER_DIR

TALK_TEST = ROOT / "tools" / "talk-test.ps1"


@pytest.fixture(scope="module")
def walk_trace():
    spec = importlib.util.spec_from_file_location("walk_trace", ROOT / "tools" / "walk-trace.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_walk_trace_defaults_are_the_old_ones(walk_trace):
    opts = walk_trace.parse_args([], env={})
    assert (opts.port, opts.server_port) == (7171, 7172)
    assert opts.run_dir == (ROOT / "tools" / ".run").resolve()
    assert opts.db == (SERVER_DIR / "db.db3").resolve()


def test_walk_trace_options_from_environment_and_command_line(walk_trace, tmp_path):
    env = {"WALKTRACE_RUN": str(tmp_path / "a"), "WALKTRACE_PORT": "7301", "WALKTRACE_SERVER_PORT": "7302",
           "WALKTRACE_DB": str(tmp_path / "x.db3")}
    opts = walk_trace.parse_args([], env=env)
    assert (opts.run_dir, opts.port, opts.server_port, opts.db) == (tmp_path / "a", 7301, 7302, tmp_path / "x.db3")
    opts = walk_trace.parse_args(["--run-dir", str(tmp_path / "b"), "--port", "7311", "--server-port", "7312"], env=env)
    assert (opts.run_dir, opts.port, opts.server_port) == (tmp_path / "b", 7311, 7312)   # the options win
    opts = walk_trace.parse_args(["7321", "7322"], env=env)                              # the old form
    assert (opts.port, opts.server_port) == (7321, 7322)


@pytest.mark.parametrize("argv", [["7321"], ["--port", "7400", "--server-port", "7400"], ["--port", "70000"]])
def test_walk_trace_rejects_bad_ports(walk_trace, argv):
    with pytest.raises(SystemExit):
        walk_trace.parse_args(argv, env={})


def test_walk_trace_run_folder_is_locked(walk_trace, tmp_path):
    first = walk_trace.lock_run_dir(tmp_path)
    assert first is not None
    assert walk_trace.lock_run_dir(tmp_path) is None      # a second run in the same folder
    first.close()                                         # the first run ended
    again = walk_trace.lock_run_dir(tmp_path)
    assert again is not None
    again.close()


def test_walk_trace_refuses_a_taken_port_without_writing(tmp_path):
    with socket.socket() as taken:
        taken.bind(("127.0.0.1", 0))
        taken.listen(1)
        port = taken.getsockname()[1]
        run = subprocess.run([sys.executable, str(ROOT / "tools" / "walk-trace.py"), "--run-dir", str(tmp_path / "r"),
                              "--port", str(port + 1 if port < 65535 else port - 1), "--server-port", str(port)],
                             capture_output=True, text=True, timeout=60)
    assert run.returncode != 0
    assert "already in use" in run.stderr
    assert not (tmp_path / "r").exists()                  # no config, no log: the other run's files are safe


def _talk_test(*args, timeout=90):
    return subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(TALK_TEST), *args],
                          capture_output=True, text=True, timeout=timeout)


def test_talk_test_refuses_the_dev_server():
    run = _talk_test("-Port", "7171", "-Words", "hi")
    assert run.returncode != 0 and "7171" in run.stderr


def test_talk_test_refuses_the_dev_database():
    run = _talk_test("-Npc", "Sam", "-Via", "db", "-Db", str(SERVER_DIR / "db.db3"), "-Port", "1")
    assert run.returncode != 0
    assert "dev server's database" in run.stderr or "no database" in run.stderr


def test_talk_test_unknown_npc():
    run = _talk_test("-Npc", "Nobody At All", "-Port", "1")
    assert run.returncode != 0 and "no NPC" in run.stderr


def test_talk_test_goto_any_npc(server):
    """A GM /goto to Ishina in Darashia, far from every temple the God character could start at."""
    run = _talk_test("-Port", str(server.port), "-Npc", "Ishina", "-Words", "hi,job,bye")
    assert run.returncode == 0, run.stdout + run.stderr
    assert "I am a jeweller." in run.stdout, run.stdout


def test_talk_test_database_move(server):
    """Mintwall (a normal character) moved in the test database next to Bezil, underground in Kazordoon."""
    run = _talk_test("-Port", str(server.port), "-Db", str(server.db_path), "-Npc", "Bezil", "-Via", "db",
                     "-Words", "hi,job,bye")
    assert run.returncode == 0, run.stdout + run.stderr
    assert "We sell equipment of all kind." in run.stdout, run.stdout

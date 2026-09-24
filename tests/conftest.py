"""Shared fixtures: one isolated server per test session, fresh characters per test."""
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from tibia74 import GameClient, Items, ServerProcess, SERVER_DIR, TestDatabase  # noqa: E402

DATA_DIR = SERVER_DIR / "data"


@pytest.fixture(scope="session")
def server():
    srv = ServerProcess()
    srv.start()
    yield srv
    srv.stop()


@pytest.fixture(scope="session")
def items():
    return Items(DATA_DIR)


@pytest.fixture(scope="session")
def db(server):
    return TestDatabase(server.db_path)


@pytest.fixture(scope="session")
def world_map():
    """Walkability and floor changes of the whole map, for route planning (tibia74/worldmap.py; cached)."""
    from tibia74.worldmap import WorldMap
    return WorldMap.load(SERVER_DIR, Path(__file__).parent / ".run")


@pytest.fixture(scope="session")
def world():
    """Map facts parsed from the spawn file: spawns by name, npc positions."""
    return World(DATA_DIR / "world" / "Tibia74-spawns.xml")


@pytest.fixture
def new_player(server, db, items):
    """Factory: new_player(level=8, pos=(x, y, z), inventory={...}) -> logged-in GameClient."""
    clients = []

    def make(**kwargs) -> GameClient:
        char = db.create_character(**kwargs)
        client = GameClient(items, port=server.port)
        client.login(char.account, char.password, char.name)
        client.character = char
        clients.append(client)
        return client

    yield make
    for c in clients:
        c.logout()


@pytest.fixture(autouse=True)
def no_lua_errors(request, server):
    """Every test fails if the server logged a Lua error while it ran."""
    start = server.log_offset()
    yield
    code = server.proc.poll() if server.proc else None
    if code is not None:   # a crash: name the test it happened in (exit code 0xC0000005 = access violation)
        pytest.fail(f"the server died during this test, exit code 0x{code & 0xFFFFFFFF:08X}\n"
                    + server.log_tail(15), pytrace=False)
    errors = server.lua_errors(since=start)
    if errors:
        pytest.fail("server logged Lua errors during the test:\n\n" + "\n\n".join(errors[:5]), pytrace=False)


class World:
    def __init__(self, spawns_file: Path):
        text = spawns_file.read_text(encoding="latin-1")
        self.monsters: dict[str, list[tuple]] = {}
        self.npcs: dict[str, tuple] = {}
        for m in re.finditer(r'<spawn centerx="(\d+)" centery="(\d+)" centerz="(\d+)"[^>]*>(.*?)</spawn>',
                             text, re.S):
            cx, cy, cz = int(m.group(1)), int(m.group(2)), int(m.group(3))
            for kind, name, x, y in re.findall(
                    r'<(monster|npc) name="([^"]+)" x="(-?\d+)" y="(-?\d+)"', m.group(4)):
                pos = (cx + int(x), cy + int(y), cz)
                if kind == "npc":
                    self.npcs[name] = pos
                else:
                    self.monsters.setdefault(name, []).append(pos)

    def nearest_spawn(self, monster: str, to: tuple, same_floor: bool = True) -> tuple:
        cands = [p for p in self.monsters.get(monster, []) if not same_floor or p[2] == to[2]]
        if not cands:
            raise LookupError(f"no {monster} spawn found")
        return min(cands, key=lambda p: max(abs(p[0] - to[0]), abs(p[1] - to[1])))

"""Respawn as in CipSoft's world (decided with the user 2026-10-04, docs/reference-74/spawns.md option (c)).

Data (no server needed): every monster's spawntime in server/data/world/Tibia74-spawns.xml is the one
tools/apply-cip-spawntimes.py gives it - its twin's in Nostalrius' CipSoft-derived spawn file
(docs/reference-74/nostalrius-spawns.csv), 600 s without a twin, and the decided values (8 tomb pharaohs 600 s,
the Black Knight 720 s). No boss is in the spawn file.

In game (src/spawn.cpp; Nostalrius src/spawn.cpp and tibiantis.info's trivia):
  - each slot has its own timer from its monster's death: a spawntime t over 500 s comes back after a random time
    between t/2 and t (fewer than 200 players online), shorter ones after exactly t; the test server divides it by
    RateSpawn (tests/tibia74/server.py SPAWN_RATE);
  - a player near the spot when it is due blocks it (the slot waits a new delay): on the same floor, and
    underground also from 2 floors above or below.

The spot: the lone rotworm at 32065,31578,10 (Cip 800 s: 20-40 s on the test server) - the only single-monster
underground spawn of a weak monster with no other spawn within 14 squares and 2 floors, and a floor above it.
"""
import importlib.util
import time
import xml.etree.ElementTree as ET

import pytest

from tibia74 import RIGHT, SERVER_DIR, Item
from tibia74.server import SPAWN_RATE

ROOT = SERVER_DIR.parent
SPAWN_FILE = SERVER_DIR / "data" / "world" / "Tibia74-spawns.xml"

_spec = importlib.util.spec_from_file_location("apply_cip_spawntimes", ROOT / "tools" / "apply-cip-spawntimes.py")
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)


def _monsters():
    out = []
    for sp in ET.parse(SPAWN_FILE).getroot().iter("spawn"):
        cx, cy, cz = (int(sp.get(k)) for k in ("centerx", "centery", "centerz"))
        for m in sp.iter("monster"):
            out.append((m.get("name"), (cx + int(m.get("x")), cy + int(m.get("y")), cz), int(m.get("spawntime"))))
    return out


MONSTERS = _monsters()


# ----------------------------------------------------------------------------- data

def test_every_spawntime_is_the_cip_one():
    nost = tool.load_nostalrius()
    wrong = [(name, pos, t, tool.wanted(nost, name, pos)) for name, pos, t in MONSTERS
             if t != tool.wanted(nost, name, pos)[0]]
    assert not wrong, f"{len(wrong)} entries differ - run tools/apply-cip-spawntimes.py: {wrong[:10]}"


def test_no_editor_default_left():
    """60 s (the map editor's default every entry had) only where Cip's own spot says 60 (the tomb traps)."""
    nost = tool.load_nostalrius()
    sixty = [(name, pos) for name, pos, t in MONSTERS if t == 60]
    assert sixty, "Cip has 60 s spots (the tomb traps)"
    for name, pos in sixty:
        assert tool.wanted(nost, name, pos) == (60, "twin"), (name, pos)


def test_almost_every_entry_has_a_cip_twin():
    nost = tool.load_nostalrius()
    rules = [tool.wanted(nost, name, pos)[1] for name, pos, _ in MONSTERS]
    assert len(MONSTERS) == 18666
    assert rules.count("default") <= 25, rules.count("default")     # 21: 9 "demongoblin", sheep, spiders, ...
    assert all(t == tool.DEFAULT for name, pos, t in MONSTERS if tool.wanted(nost, name, pos)[1] == "default")


def test_the_decided_values():
    pharaohs = {name: t for name, pos, t in MONSTERS if name.lower() in tool.PHARAOHS}
    assert len(pharaohs) == 8 and set(pharaohs.values()) == {600}, pharaohs
    assert [t for name, pos, t in MONSTERS if name == "Black Knight" and pos == (32874, 31948, 11)] == [720]


def test_no_boss_in_the_spawn_file():
    """Bosses "do not spawn like normal creatures" (TibiaWiki "Bosses" 2007)."""
    bosses = {"orshabaal", "ferumbras", "demodras", "the horned fox", "dharalion", "general murius", "grorlam",
              "necropharus", "the old widow", "the evil eye", "yeti"}
    assert not [m for m in MONSTERS if m[0].lower() in bosses]


def test_the_test_spot_is_alone():
    """The live tests' rotworm: alone in its block, its Cip time 800 s, nothing else spawns near it."""
    near = [m for m in MONSTERS if abs(m[1][2] - SPOT[2]) <= 2
            and max(abs(m[1][0] - SPOT[0]), abs(m[1][1] - SPOT[1])) <= 14]
    assert near == [("Rotworm", SPOT, 800)], near


# ----------------------------------------------------------------------------- in game

SPOT = (32065, 31578, 10)
NEXT_TO = (32064, 31578, 10)          # the killer stands here
WATCH = (32061, 31576, 10)            # an observer, 4 squares away (in view)
ABOVE = (32062, 31580, 9)             # one floor up, 3 squares off
MIN_DELAY = 800 / 2 / SPAWN_RATE      # 20 s
MAX_DELAY = 800 / SPAWN_RATE          # 40 s
KNIGHT, MAGIC_SWORD = 4, 2400
SPAWN_TESTER = 74                     # a player group that gets no in-fight lock (PlayerFlag_NotGainInFight) and
NOT_GAIN_IN_FIGHT, CANNOT_BE_ATTACKED = 1 << 9, 1 << 3   # cannot be hit: it logs out right after its kill


@pytest.fixture
def spawn_player(db, new_player):
    con = db._connect()
    con.execute('INSERT OR REPLACE INTO groups (id, name, flags, access, maxdepotitems, maxviplist)'
                ' VALUES (?, ?, ?, 0, 1000, 50)', (SPAWN_TESTER, "SpawnTester", NOT_GAIN_IN_FIGHT | CANNOT_BE_ATTACKED))
    con.commit()
    con.close()

    def make(pos, **kw):
        return new_player(pos=pos, group_id=SPAWN_TESTER, premium_days=30, storage={30001: 1}, **kw)
    return make


def _near(pos, at, dist=1):
    """Logged in on `at` or next to it (the server moves a login off a tile someone stands on)."""
    return pos[2] == at[2] and max(abs(pos[0] - at[0]), abs(pos[1] - at[1])) <= dist


def _rotworms(p):
    return [c for c in p.creatures_named("Rotworm") if c.pos and c.pos[2] == SPOT[2]
            and max(abs(c.pos[0] - SPOT[0]), abs(c.pos[1] - SPOT[1])) <= 3]


def _look(spawn_player, at=WATCH, wait=1.5):
    """Logs a character in at `at`, returns (client, rotworms it sees near the spot)."""
    p = spawn_player(at)
    assert _near(p.pos, at), p.pos
    p.sleep(wait)
    return p, _rotworms(p)


def _rotworm_present(spawn_player):
    """Makes sure the rotworm stands on its spot (waits one whole delay with nobody near if not)."""
    p, seen = _look(spawn_player)
    p.logout()
    if not seen:
        time.sleep(MAX_DELAY + 2)
        p, seen = _look(spawn_player)
        p.logout()
    assert seen, "the rotworm did not come back"


def _kill(spawn_player):
    """A level 60 knight kills the rotworm; returns the client (still logged in) and the time of the kill."""
    _rotworm_present(spawn_player)
    k = spawn_player(NEXT_TO, level=60, vocation=KNIGHT, skills={2: 70}, inventory={RIGHT: Item(MAGIC_SWORD)})
    assert _near(k.pos, NEXT_TO), k.pos
    assert k.wait_for(lambda: _rotworms(k), timeout=5), "no rotworm"
    worm = _rotworms(k)[0]
    k.set_fight_modes(fight=1, chase=1)
    k.attack(worm.id)
    assert k.wait_for(lambda: worm.id in k.removed_creatures, timeout=30), f"rotworm not killed: {worm}"
    return k, time.time()


def _sleep_until(t):
    time.sleep(max(0.0, t - time.time()))


def test_a_killed_monster_respawns_after_its_own_time(spawn_player):
    """Nobody near: not back before t/2 (20 s), back by t (40 s) after its death."""
    k, killed = _kill(spawn_player)
    k.logout()
    _sleep_until(killed + MIN_DELAY - 5)
    p, seen = _look(spawn_player, wait=1.0)          # 16 s: before t/2, and gone again before the slot is due
    p.logout()
    assert not seen, f"back {time.time() - killed:.0f} s after its death, Cip: {MIN_DELAY:.0f}-{MAX_DELAY:.0f} s"
    assert time.time() < killed + MIN_DELAY, "the observer stayed too long, it may have blocked the respawn"
    _sleep_until(killed + MAX_DELAY + 2)
    p, seen = _look(spawn_player, wait=1.0)
    assert seen, f"not back {time.time() - killed:.0f} s after its death (Cip: {MIN_DELAY:.0f}-{MAX_DELAY:.0f} s)"


def test_a_player_next_to_the_spot_blocks_the_respawn(spawn_player):
    """The killer stays next to the spot past the longest delay: nothing comes. Once he left, it comes back within
    one more delay."""
    k, killed = _kill(spawn_player)
    appeared = k.wait_for(lambda: _rotworms(k), timeout=MAX_DELAY + 5)
    assert not appeared, f"respawned next to a player {time.time() - killed:.0f} s after its death"
    k.logout()
    left = time.time()
    # blocked at its first due time (at most MAX_DELAY after the kill): the slot waits a new delay from then
    _sleep_until(killed + 2 * MAX_DELAY + 2)
    p, seen = _look(spawn_player, wait=1.0)
    assert seen, f"not back {time.time() - left:.0f} s after the player left"


def test_a_player_one_floor_up_blocks_the_respawn_underground(spawn_player):
    """Underground a player 2 floors up or down blocks a respawn (tibiantis.info trivia; Nostalrius checks the
    spectators of every floor in view). Someone one floor above the spot from right after the kill until past the
    longest delay: the rotworm is still not back."""
    k, killed = _kill(spawn_player)
    up = spawn_player(ABOVE)
    assert _near(up.pos, ABOVE), up.pos
    k.logout()
    _sleep_until(killed + MAX_DELAY + 3)
    p, seen = _look(spawn_player, wait=1.0)          # the player upstairs is still there
    assert not seen, f"respawned under a player one floor up, {time.time() - killed:.0f} s after its death"
    up.logout()
    p.logout()

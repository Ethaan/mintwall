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

  - overspawn: a monster more than 10 squares from its spot, or on another floor, frees its slot (Monster::
    onCreatureMove -> Spawn::onMonsterMove); the slot respawns after its time while the first one still lives;
  - wandering is held by the despawn radius (config.lua DespawnRadius 50), not by the block's radius (1);
  - the players-online scaling (above 200 players) is Nostalrius' Spawn::getInterval: checked against the source
    below (no live test - it needs over 200 players online to change anything).

The spots: the lone rotworm at 32065,31578,10 (Cip 800 s: 20-40 s on the test server) - the only single-monster
underground spawn of a weak monster with no other spawn within 14 squares and 2 floors, and a floor above it; the
lone scorpion in the open desert at 33303,32420,7 (nothing within 22 squares, 600 s: 15-30 s) for luring; the lone
rat in a cellar at 32450,32110,8 (nothing within 22 squares, 600 s), two squares from a ladder under a trapdoor.
"""
import importlib.util
import re
import time
import xml.etree.ElementTree as ET

import pytest

from tibia74 import RIGHT, SERVER_DIR, WEST, Item
from tibia74.route import use_tool
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


@pytest.mark.parametrize("name, spot, alone", [("Scorpion", (33303, 32420, 7), 22), ("Rat", (32450, 32110, 8), 14)])
def test_the_overspawn_spots_are_alone(name, spot, alone):
    """The overspawn tests' monsters, Cip 600 s: the scorpion (led 12 squares off) alone within 22 squares and 2
    floors, the rat (in a closed cellar room) within 14."""
    near = [m for m in MONSTERS if abs(m[1][2] - spot[2]) <= 2
            and max(abs(m[1][0] - spot[0]), abs(m[1][1] - spot[1])) <= alone]
    assert near == [(name, spot, 600)], near


# ----------------------------------------------------------------------------- players online (no server)

SPAWN_CPP = SERVER_DIR / "src" / "spawn.cpp"


def _nostalrius_interval(interval, players):
    """Nostalrius src/spawn.cpp (github.com/Ezzz-dev/Nostalrius, master), Spawn::getInterval - (low, high) of
    normal_random(newInterval / 2, newInterval):
        uint32_t newInterval = interval;
        if (newInterval > 500000) {
            size_t playersOnline = g_game.getPlayersOnline();
            if (playersOnline <= 800) {
                if (playersOnline > 200) {
                    newInterval = 200 * interval / (playersOnline / 2 + 100);
                }
            } else {
                newInterval = 2 * interval / 5;
            }
            return normal_random(newInterval / 2, newInterval);
        }
        return newInterval;"""
    if interval > 500000:
        if players <= 800:
            n = 200 * interval // (players // 2 + 100) if players > 200 else interval
        else:
            n = 2 * interval // 5
        return n // 2, n
    return interval, interval


def _ours_interval(interval, players):
    """(low, high) of Spawn::getRespawnDelay at RateSpawn 1, from server/src/spawn.cpp's own text: its two
    expressions are taken from the source and evaluated with C integer division."""
    src = SPAWN_CPP.read_text(encoding="latin-1")
    body = re.search(r"uint32_t Spawn::getRespawnDelay\(uint32_t interval\)\n\{(.*?)\n\}\n", src, re.S).group(1)
    code = re.sub(r"//[^\n]*", "", body)
    big = re.search(r"if\(delay > (\d+)\)\{", code)
    branches = re.search(r"if\(playersOnline > (\d+)\)\{\s*delay = ([^;]+);\s*\}\s*"
                         r"else if\(playersOnline > (\d+)\)\{\s*delay = ([^;]+);\s*\}", code)
    assert big and branches, "getRespawnDelay changed shape - update this check"
    assert re.search(r"delay = normalRandom\(\(int32_t\)\(delay / 2\), \(int32_t\)delay\);", code)
    high_n, high_expr, low_n, low_expr = int(branches[1]), branches[2], int(branches[3]), branches[4]

    def ev(expr, delay):
        return eval(expr.replace("/", "//"), {}, {"delay": delay, "playersOnline": players})

    delay = interval
    if delay > int(big[1]):
        if players > high_n:
            delay = ev(high_expr, delay)
        elif players > low_n:
            delay = ev(low_expr, delay)
        return delay // 2, delay
    return delay, delay


def test_players_online_scaling_is_nostalrius():
    """Above 200 players a spawntime over 500 s is shortened as in Nostalrius (CipSoft's): 200*t/(players/2+100) up
    to 800 players, 0.4*t above, then random between half and all of it. Checked against spawn.cpp's own expressions
    for every players count up to 1200 - a live test would need over 200 players online to see any change."""
    for interval in (60000, 300000, 500000, 500001, 600000, 800000, 2000000, 20000000):
        for players in list(range(0, 1201, 3)) + [199, 200, 201, 202, 799, 800, 801]:
            assert _ours_interval(interval, players) == _nostalrius_interval(interval, players), (interval, players)
    # a few by hand: no change up to 200 (or 201: 201/2 + 100 = 200), 600 s at 400 players: 200-400 s
    assert _ours_interval(600000, 0) == _ours_interval(600000, 201) == (300000, 600000)
    assert _ours_interval(600000, 400) == (200000, 400000)
    assert _ours_interval(600000, 1000) == (120000, 240000)
    assert _ours_interval(500000, 1000) == (500000, 500000)          # 500 s or less: exact, whatever is online


def _nostalrius_normal_random(min_number, max_number, v):
    """Nostalrius src/tools.cpp normal_random with the normal draw v (std::normal_distribution(0.5, 0.25)):
        if (minNumber == maxNumber) return minNumber;
        else if (minNumber > maxNumber) std::swap(minNumber, maxNumber);
        const int32_t diff = maxNumber - minNumber;
        if (v < 0.0) increment = diff / 2;
        else if (v > 1.0) increment = (diff + 1) / 2;
        else increment = round(v * diff);
        return minNumber + increment;"""
    if min_number == max_number:
        return min_number
    if min_number > max_number:
        min_number, max_number = max_number, min_number
    diff = max_number - min_number
    if v < 0.0:
        inc = diff // 2
    elif v > 1.0:
        inc = (diff + 1) // 2
    else:
        inc = int(v * diff + 0.5)                    # C round() for v * diff >= 0
    return min_number + inc


def _ours_normal_random(min_number, max_number, v):
    """spawn.cpp's normalRandom with the draw v: its body read from the source, each branch's expression taken out
    and evaluated with C integer division."""
    src = SPAWN_CPP.read_text(encoding="latin-1")
    body = re.search(r"static int32_t normalRandom\(int32_t minNumber, int32_t maxNumber\)\n\{(.*?)\n\}\n", src, re.S)
    assert body, "no normalRandom in spawn.cpp"
    code = re.sub(r"//[^\n]*", "", body.group(1))
    shape = re.search(
        r"if\(minNumber == maxNumber\)\{\s*return minNumber;\s*\}\s*"
        r"else if\(minNumber > maxNumber\)\{\s*std::swap\(minNumber, maxNumber\);\s*\}\s*"
        r"int32_t increment;\s*const int32_t diff = maxNumber - minNumber;\s*"
        r"const float v = box_muller\(0\.5f, 0\.25f\);\s*"
        r"if\(v < 0\.0f\)\{\s*increment = ([^;]+);\s*\}\s*"
        r"else if\(v > 1\.0f\)\{\s*increment = ([^;]+);\s*\}\s*"
        r"else\{\s*increment = \(int32_t\)std::floor\(v \* diff \+ 0\.5f\);\s*\}\s*"
        r"return minNumber \+ increment;", code)
    assert shape, "normalRandom changed shape - update this check"
    if min_number == max_number:
        return min_number
    if min_number > max_number:
        min_number, max_number = max_number, min_number
    diff = max_number - min_number
    if v < 0.0:
        inc = eval(shape[1].replace("/", "//"), {}, {"diff": diff})
    elif v > 1.0:
        inc = eval(shape[2].replace("/", "//"), {}, {"diff": diff})
    else:
        inc = int(v * diff + 0.5)
    return min_number + inc


def test_the_random_part_is_nostalrius():
    """The delay is random between half and all of it as Nostalrius' normal_random draws it: a normal draw (mean 0.5,
    deviation 0.25) over the range, and a draw outside [0, 1] (about 2.3 % each side) goes to the MIDDLE, not to the
    ends (tools.cpp random_range DISTRO_NORMAL would put it on t/2 or t). Checked from spawn.cpp's normalRandom."""
    for lo, hi in ((300000, 600000), (15000, 30000), (7, 8), (0, 1), (5, 5), (600000, 300000)):
        for v in (-1.3, -0.01, 0.0, 0.1, 0.25, 0.5, 0.75, 0.999, 1.0, 1.01, 2.4):
            assert _ours_normal_random(lo, hi, v) == _nostalrius_normal_random(lo, hi, v), (lo, hi, v)
    assert _ours_normal_random(300000, 600000, -0.2) == 450000         # below the range: the middle, not t/2
    assert _ours_normal_random(300000, 600001, 1.2) == 450001          # above: the middle (rounded up), not t


def test_rate_spawn_divides_the_delay():
    """RateSpawn (config.lua; the test server's 20) divides every delay, after the scaling and the randomness."""
    body = SPAWN_CPP.read_text(encoding="latin-1").split("uint32_t Spawn::getRespawnDelay", 1)[1].split("\n}\n", 1)[0]
    assert re.search(r"getNumber\(ConfigManager::RATE_SPAWN\);\s*if\(rate > 1\)\{\s*delay /= rate;", body)
    assert body.index("normalRandom") < body.index("delay /= rate")


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


# ----------------------------------------------------------------------------- overspawn (in game)

GM_GROUP = 3                          # server/sql/seed.sql God: IgnoredByMonsters - it neither draws a monster nor
                                      # blocks a respawn (Spawn::findPlayer), so it can watch a spot all along
LURER = 75                            # an ordinary player monsters go for, but no in-fight lock: it logs out at once
SCORPION = (33303, 32420, 7)          # alone in the open desert (Cip 600 s: 15-30 s on the test server)
RAT = (32450, 32110, 8)               # alone in a cellar room (Cip 600 s)
MIN_600, MAX_600 = 600 / 2 / SPAWN_RATE, 600 / SPAWN_RATE
RAT_LADDER = (32452, 32110, 8)        # two squares east: a ladder under the trapdoor (32452, 32110, 7)
RAT_TRAPDOOR = (32452, 32110, 7)
RAT_ROOM = [(32450, 32110, 8), (32451, 32110, 8), (32451, 32109, 8), (32452, 32109, 8), RAT_LADDER,
            (32452, 32111, 8)]
ROPE = 2120


def _cheb(a, b):
    """Squares between two positions (-1: not on one floor, or not seen)."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) if a and b and a[2] == b[2] else -1


@pytest.fixture
def lure_player(db, new_player):
    con = db._connect()
    con.execute('INSERT OR REPLACE INTO groups (id, name, flags, access, maxdepotitems, maxviplist)'
                ' VALUES (?, ?, ?, 0, 1000, 50)', (LURER, "LureTester", NOT_GAIN_IN_FIGHT))
    con.commit()
    con.close()

    def make(pos, **kw):
        return new_player(pos=pos, group_id=LURER, level=80, vocation=KNIGHT, skills={2: 70},
                          inventory={RIGHT: Item(MAGIC_SWORD)}, storage={30001: 1}, premium_days=30, **kw)
    return make


def _monsters_near(p, name, spot, dist):
    return [c for c in p.creatures_named(name) if 0 <= _cheb(c.pos, spot) <= dist]


def _kill_it(k, mid):
    k.set_fight_modes(fight=1, chase=1)
    k.attack(mid)
    assert k.wait_for(lambda: mid in k.removed_creatures, timeout=30), f"not killed: {k.creatures.get(mid)}"


def test_a_lured_monster_frees_its_slot_past_10_squares(new_player, lure_player):
    """Overspawn by distance (TI-trivia: "lured more than 10 squares away"). A player leads the scorpion west to 10
    squares from its spot and logs out: in more than its longest delay nothing new comes (the slot is still its).
    Another leads it one square further: its slot is free, and a new scorpion stands on the spot after the slot's
    time (15-30 s) while the first one still lives. A God watches all along (it blocks nothing)."""
    look_from = (SCORPION[0] - 5, SCORPION[1] - 3, 7)
    gm = new_player(pos=look_from, group_id=GM_GROUP, storage={30001: 1})
    assert 0 <= _cheb(gm.pos, look_from) <= 1, gm.pos
    if not gm.wait_for(lambda: _monsters_near(gm, "Scorpion", SCORPION, 6), timeout=3):
        assert gm.wait_for(lambda: _monsters_near(gm, "Scorpion", SCORPION, 6), timeout=MAX_600 + 3), \
            "no scorpion by its spot"
    first = _monsters_near(gm, "Scorpion", SCORPION, 6)[0]
    sid = first.id

    def lured():
        return gm.creatures[sid].pos

    # 1) to exactly 10 squares
    lurer = lure_player((first.pos[0] - 2, first.pos[1], 7))
    assert lurer.wait_for(lambda: _cheb(lured(), lurer.pos) == 1, timeout=10), (lured(), lurer.pos)
    while _cheb(lured(), SCORPION) < 10:
        assert lurer.step(WEST), f"blocked at {lurer.pos}"
        assert lurer.wait_for(lambda: _cheb(lured(), lurer.pos) == 1, timeout=6), (lured(), lurer.pos)
    lurer.logout()
    gm.sleep(1.0)
    assert _cheb(lured(), SCORPION) == 10, f"led to {lured()}, wanted 10 squares from {SCORPION}"
    came = gm.wait_for(lambda: _monsters_near(gm, "Scorpion", SCORPION, 3), timeout=MAX_600 + 3)
    assert not came, f"a second scorpion with the first 10 squares off: {came}, the first at {lured()}"

    # 2) one square further: 11
    at = lured()
    lurer = lure_player((at[0] - 2, at[1], 7))
    # Spawn::findPlayer looks 11 squares around the spot (Map::maxViewportX/Y): 12 blocks nothing
    assert _cheb(lurer.pos, SCORPION) >= 12, f"{lurer.pos}: in range of the spot, it would block the respawn"
    assert gm.wait_for(lambda: _cheb(lured(), SCORPION) > 10, timeout=10), lured()
    freed = time.time()
    came = gm.wait_for(lambda: [c for c in _monsters_near(gm, "Scorpion", SCORPION, 3) if c.id != sid],
                       timeout=MAX_600 + 5)
    after = time.time() - freed
    assert came, (f"no new scorpion {after:.0f} s after the first went 11 squares off (Cip: "
                  f"{MIN_600:.0f}-{MAX_600:.0f} s); the first at {lured()}")
    assert after >= MIN_600 - 1.5, f"a new one after {after:.1f} s, the slot's time is {MIN_600:.0f}-{MAX_600:.0f} s"
    assert came[0].pos == SCORPION, came
    assert sid not in gm.removed_creatures and _cheb(lured(), SCORPION) == 11, \
        f"the first scorpion is not there any more: {gm.creatures.get(sid)}"

    # the lured one is put down: the spot is as it was (one scorpion)
    _kill_it(lurer, sid)
    lurer.logout()


def _push(gm, mid, to):
    """The God pushes the monster onto `to` (a square next to it), like a player moving a creature."""
    for _ in range(4):
        m = gm.creatures[mid]
        if tuple(m.pos) == to:
            return
        stack = gm.tiles.get(tuple(m.pos), [])
        at = next(n for n, t in enumerate(stack) if (t if isinstance(t, int) else getattr(t, "id", None)) == mid)
        gm.move_item(tuple(m.pos), 0x63, at, to)
        if gm.wait_for(lambda: tuple(gm.creatures[mid].pos) == to, timeout=3):
            return
    raise AssertionError(f"could not push {gm.creatures.get(mid)} to {to} (the God at {gm.pos})")


def test_a_monster_roped_up_a_floor_frees_its_slot(new_player, spawn_player, items):
    """Overspawn by floor change (TI-trivia, Mino Hell: "a monster respawns after being roped up 1 floor"). Monsters
    never step onto stairs, holes or ladders themselves (Tile::__queryAdd), and nobody can push one there: in the game
    a monster changes floor when a player ropes it up (rope.lua pulls up whatever stands under the hole). A God pushes
    the cellar rat onto the ladder under the trapdoor, another ropes it up: a new rat stands on the spot after the
    slot's time (15-30 s), the roped one still lives upstairs. Gods block nothing; the roped rat is killed after."""
    gm = None
    for at in ((32451, 32109, 8), (32452, 32109, 8), (32451, 32110, 8)):
        gm = new_player(pos=at, group_id=GM_GROUP, storage={30001: 1})
        if gm.pos in RAT_ROOM:
            break
        gm.logout()
    assert gm.pos in RAT_ROOM, gm.pos

    def rats():
        return [c for c in gm.creatures_named("Rat") if c.pos in RAT_ROOM]

    if not gm.wait_for(rats, timeout=3):
        assert gm.wait_for(rats, timeout=MAX_600 + 3), "no rat in the cellar"
    rid = rats()[0].id
    # onto the ladder, one square at a time (a push moves a creature one square)
    if gm.creatures[rid].pos == RAT:
        _push(gm, rid, (32451, 32110, 8) if gm.pos != (32451, 32110, 8) else (32451, 32109, 8))
    _push(gm, rid, RAT_LADDER)

    up = new_player(pos=(RAT_TRAPDOOR[0] + 1, RAT_TRAPDOOR[1], 7), group_id=GM_GROUP, storage={30001: 1},
                    inventory={RIGHT: Item(ROPE)})
    assert _cheb(up.pos, RAT_TRAPDOOR) == 1, up.pos
    use_tool(up, items, "rope", RAT_TRAPDOOR)
    pulled_to = (RAT_TRAPDOOR[0], RAT_TRAPDOOR[1] + 1, 7)
    assert gm.wait_for(lambda: gm.creatures[rid].pos == pulled_to, timeout=5), \
        f"the rope did not pull the rat up: {gm.creatures.get(rid)}"
    roped = time.time()
    came = gm.wait_for(lambda: [c for c in rats() if c.id != rid], timeout=MAX_600 + 5)
    after = time.time() - roped
    assert came, f"no new rat {after:.0f} s after the first was roped up (Cip: {MIN_600:.0f}-{MAX_600:.0f} s)"
    assert after >= MIN_600 - 1.5, f"a new rat after {after:.1f} s, the slot's time is {MIN_600:.0f}-{MAX_600:.0f} s"
    assert came[0].pos == RAT, came
    assert rid not in up.removed_creatures and getattr(up.creatures.get(rid), "pos", None) == pulled_to, \
        f"the roped rat is not upstairs any more: {up.creatures.get(rid)}"

    up.logout()
    k = spawn_player((pulled_to[0] + 1, pulled_to[1], 7), level=60, vocation=KNIGHT, skills={2: 70},
                     inventory={RIGHT: Item(MAGIC_SWORD)})
    assert k.wait_for(lambda: rid in k.creatures and k.creatures[rid].pos, timeout=5), "the roped rat is gone"
    _kill_it(k, rid)


def test_wandering_is_not_held_by_the_spawn_radius(spawn_player):
    """A monster that sees a player it may not attack walks about at random (Monster::getRandomStep): only the
    despawn radius (50) holds it, not its block's radius 1 (Monster::isInSpawnRange). The scorpion in the open desert
    goes 3 squares and more from its spot. (The Paradox Tower ghoul test covers a monster in a room.)"""
    watch_from = (SCORPION[0] - 4, SCORPION[1] + 4, 7)
    p = spawn_player(watch_from)
    assert 0 <= _cheb(p.pos, watch_from) <= 1, p.pos
    if not p.wait_for(lambda: _monsters_near(p, "Scorpion", SCORPION, 8), timeout=3):
        assert p.wait_for(lambda: _monsters_near(p, "Scorpion", SCORPION, 8), timeout=2 * MAX_600 + 3), "no scorpion"
    sid = _monsters_near(p, "Scorpion", SCORPION, 8)[0].id
    start = p.creatures[sid].pos
    seen = {start}

    def away():
        pos = p.creatures[sid].pos
        seen.add(pos)
        return pos is not None and pos != start and _cheb(pos, SCORPION) >= 3

    assert p.wait_for(away, timeout=90), f"the scorpion kept within 2 squares of its spot: {sorted(seen)}"
    p.logout()

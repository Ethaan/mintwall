"""Which parts of the map are premium areas, worked out from the map itself.

Neither the engine nor the map has a premium tile flag (tile.h: protection zone, no-pvp, no-logout, pvp, refresh).
What the map marks is the way in: every ship and carpet takes premium accounts only (npc/lib/captain.lua,
docs/reference-74/travel.md), and King's Bridge on Rookgaard is premium ground (action id 50003,
movements/scripts/premium_tile.lua). So a premium area is a place you cannot walk to from a free town:

- the mainland: everything reachable on foot from the Thais temple (doors, keys, levels, ropes, shovels all allowed:
  a free account can do all of that) is free; the Isle of the Kings (Dalbrect, no premium check), the Isle of the
  Mists (a druids' portal), Senja/Folda/Vega (free ferries), the Isle of Solitude and the Venore dragon lair (reached
  by teleports) are free too;
- premium: what you walk to from the Edron, Darashia and Ankrahmun temples (Edron, Cormaya, Stonehome; Darashia,
  Ankrahmun, Drefia, the djinn fortresses), Eremo's island and the Ghost Ship;
- Rookgaard: what you walk to from the Gatekeeper's hall without stepping on King's Bridge is the premium side, what
  you walk to from the temple is the free side.

cover() turns the premium tiles into boxes that hold no free tile (water in between does not matter: nobody stands
there); tools/premium-areas.py writes them to server/data/creaturescripts/lib/premium_areas.lua for the login script.
"""
import collections
import re
from pathlib import Path

from . import route
from .otbm import read_towns, read_tiles

KINGS_BRIDGE_AID = 50003
GATEKEEPER_HALL = (32035, 32183, 6)
# the free places a temple fill from Thais does not reach (one-way teleports or free boats lead there)
FREE_STARTS = ["Thais", "Rookgaard", "Isle of Solitude", "Senja", "Folda", "Vega", "Mists", "VenoreDragons",
               "KingsIsle"]
PREMIUM_STARTS = {"mainland": ["Edron", "Darashia", "Ankrahmun", "Eremo", "Ghostship"]}


class _Any(set):
    def __contains__(self, item):
        return True


def _fill(world, start, avoid=frozenset(), keys=_Any()):
    seen, queue = {start}, collections.deque([start])
    while queue:
        p = queue.popleft()
        for _, step in route._neighbours(world, p, 1000, 0, keys, keys, True, avoid=avoid, scythe=True,
                                         shovel=True, pick=True, machete=True):
            a = step.arrive
            if a not in seen and a not in avoid:
                seen.add(a)
                queue.append(a)
    return seen


def areas(world, server_dir: Path):
    """-> (free tiles, {"mainland": premium tiles, "rookgaard": premium tiles})"""
    otbm = server_dir / "data" / "world" / "Tibia74.otbm"
    temples = {t.name: t.temple for t in read_towns(otbm)}
    bridge = frozenset(t.pos for t in read_tiles(otbm, area=((31900, 32100, 7), (32200, 32300, 7)))
                       if any(i.attrs.get("action_id") == KINGS_BRIDGE_AID for i in t.items))
    assert bridge, "King's Bridge (action id 50003) is not on the map any more"
    rook_premium = _fill(world, GATEKEEPER_HALL, bridge)
    free = set()
    for name in FREE_STARTS:
        if temples[name] not in free:
            # Rookgaard: the free side ends at the bridge (with every key the two sides meet behind locked doors)
            free |= _fill(world, temples[name], bridge | frozenset(rook_premium) if name == "Rookgaard" else
                          frozenset())
    mainland = set()
    for name in PREMIUM_STARTS["mainland"]:
        if temples[name] not in mainland:
            mainland |= _fill(world, temples[name])
    mainland -= free                     # the Ghost Ship sails on to Darashia, Mists/KingsIsle teleport out
    return free, {"mainland": mainland, "rookgaard": rook_premium - free}


def _bbox(points):
    return (tuple(min(p[i] for p in points) for i in range(3)), tuple(max(p[i] for p in points) for i in range(3)))


def _inside(p, lo, hi):
    return lo[0] <= p[0] <= hi[0] and lo[1] <= p[1] <= hi[1] and lo[2] <= p[2] <= hi[2]


def cover(premium, free):
    """Boxes ((x1, y1, z1), (x2, y2, z2)) holding every premium tile and no free one."""
    def split(points, frees):
        lo, hi = _bbox(points)
        frees = [f for f in frees if _inside(f, lo, hi)]
        if not frees:
            return [(lo, hi)]
        best = None
        for axis in range(3):
            for frac in (0.25, 0.5, 0.75):
                cut = min(lo[axis] + int((hi[axis] - lo[axis]) * frac), hi[axis] - 1)
                a = [p for p in points if p[axis] <= cut]
                b = [p for p in points if p[axis] > cut]
                if not a or not b:
                    continue
                score = sum(1 for part in (a, b) for f in frees if _inside(f, *_bbox(part)))
                if best is None or score < best[0]:
                    best = (score, a, b)
        return split(best[1], frees) + split(best[2], frees)

    boxes = []
    free = list(free)
    for lo, hi in split(list(premium), free):
        # all floors when no free tile is in the way: underground and towers of the same place
        whole = ((lo[0], lo[1], 0), (hi[0], hi[1], 15))
        boxes.append(whole if not any(_inside(f, *whole) for f in free) else (lo, hi))
    return boxes


LUA_BOX = re.compile(r"\{(\d+), (\d+), (\d+), (\d+), (\d+), (\d+), \"(\w+)\"\}")


def read_lua_boxes(path: Path):
    """The boxes premium_areas.lua holds: [((x1, y1, z1), (x2, y2, z2), area)]"""
    return [((int(m[0]), int(m[1]), int(m[2])), (int(m[3]), int(m[4]), int(m[5])), m[6])
            for m in LUA_BOX.findall(path.read_text(encoding="utf-8"))]

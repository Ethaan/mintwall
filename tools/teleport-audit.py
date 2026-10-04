r"""Every teleport (magic forcefield with a destination, or one a movement script moves you from) on our map, where it
sends you, and what is odd about it:

    BLOCKED       the destination is a wall / solid item (the engine puts you there anyway: stuck, or standing on it)
    VOID          no tile at the destination at all
    ONTO-TP       the destination is another teleport (the engine sends you on - or back)
    ONTO-FLOOR    the destination is a hole / stairs (you go on down or up)
    ROOK<->MAIN   it crosses between Rookgaard and the mainland
    CLOSED n      from the destination the route planner reaches only n tiles: no walking, ladder, rope, door (any
                  key), shovel or pick way out. Often fine - a quest room left by a script (a lever, a pharaoh's
                  portal), an island left by boat, Hellgate (levitate / parcels) - see NOTES
    DIFF <map>    a compared map sends it elsewhere (or has no teleport there)

Forcefields without a destination are listed as "inert" (they do nothing) or "script <file>" (action id handled in
movements.xml). Compare with the original map (server\data\world\Tibia74.otbm.bak - the 21 Sep import, or a copy of
it) and other maps with --compare; reading a map takes ~20 s.

    python tools\teleport-audit.py [--compare MAP ...] [--flagged] [--no-regions]
"""
import argparse
import re
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from tibia74 import SERVER_DIR  # noqa: E402
from tibia74.otbm import read_tiles  # noqa: E402
from tibia74.route import _neighbours  # noqa: E402
from tibia74.worldmap import SCRIPTED_TELEPORTS, VOID, WorldMap  # noqa: E402

MAP = SERVER_DIR / "data" / "world" / "Tibia74.otbm"
ROOKGAARD = ((31900, 32000), (32250, 32300))     # the island's box: x 31900-32250, y 32000-32300 (Thais starts ~32300)
REGION_CAP = 30000

# what this audit found out about teleports it flags (2026-10-03), so the table explains itself
NOTES = {
    (32107, 31566, 9): "Senja vault portal -> castle roof (decided with the user); the island is left by boat",
    (32187, 31622, 8): "Senja: into the vault; the island is left by boat",
    (32675, 31646, 10): "Hellgate: the way out needs levitate / parcels and a bridge switch (TibiaWiki Route:Hellgate 2006)",
    (32794, 31576, 5): "Draconia: the key-3007 portal rooms (switches)",
    (32812, 31576, 5): "Draconia: the key-3007 portal rooms (switches)",
    (33238, 32644, 14): "Morguthis's floor 14: went into the wall south of the altar room (33162,32654,14) - now the "
                        "room (33161,32652,14); tibiaot74 sends it to the pocket before the level-75 doors (question)",
    (33073, 32603, 15): "Dipthrah's lair; left by the pharaoh's portal (aid 51121)",
    (33120, 32811, 15): "Rahemos's lair; left by the pharaoh's portal (aid 51121)",
    (33157, 32771, 15): "Mahrdis's lair; left by the pharaoh's portal (aid 51121)",
    (33178, 32664, 15): "Vashresamun's lair; left by the pharaoh's portal (aid 51121)",
    (33193, 32908, 11): "Ashmunrah's lair; left by his portal (aid 51121) / the forcefield (aid 51161)",
    (33206, 32982, 14): "Omruc's lair; left by the pharaoh's portal (aid 51121)",
    (33368, 32805, 14): "Thalas's lair; left by the pharaoh's portal (aid 51121)",
    (33278, 31592, 11): "Demon Helmet Quest: behind the Gate of the Lost Souls (two players hold it open)",
    (33286, 31589, 12): "Demon Helmet Quest: behind the Gate of the Lost Souls (two players hold it open)",
    (33324, 31592, 14): "Demon Helmet Quest: into the demons' room; out by the switch's portal",
    (32476, 31904, 3): "Paradox Tower: the climb - switches make the ladders up",
    (32476, 31904, 5): "Paradox Tower: the climb - switches make the ladders up",
    (32479, 31904, 2): "Paradox Tower: the climb - switches make the ladders up",
    (32481, 31904, 4): "Paradox Tower: the climb - switches make the ladders up",
    (32481, 31905, 1): "Paradox Tower: the treasure room - its carvings lead back",
    (33328, 32181, 6): "Ghost Ship forcefield -> the Darashia boat landing, which is a wooden pillar (the boats land "
                       "there too, npc/lib/captain.lua; question)",
}


def is_rookgaard(pos):
    (x1, y1), (x2, y2) = ROOKGAARD
    return x1 <= pos[0] <= x2 and y1 <= pos[1] <= y2


def movement_scripts():
    """movements.xml: action id -> script."""
    xml = (SERVER_DIR / "data" / "movements" / "movements.xml").read_text(encoding="latin-1")
    return {int(m.group(1)): m.group(2) for m in re.finditer(r'actionid="(\d+)"\s+script="([^"]+)"', xml)}


def map_teleports(path):
    """{pos: (item id, destination, action id)} of every item with a teleport attribute."""
    out = {}
    for tile in read_tiles(path):
        for m in tile.items:
            if "teleport" in m.attrs:
                out[tile.pos] = (m.id, tuple(m.attrs["teleport"]), m.attrs.get("action_id"))
    return out


def closed_region(world, start, keys):
    """How many tiles the planner reaches from start (with every key, rope, shovel, pick), or None when that is more
    than REGION_CAP (= the open world)."""
    seen, queue = {start}, deque([start])
    while queue:
        pos = queue.popleft()
        for _, step in _neighbours(world, pos, 1000, 0, keys, keys, True, shovel=True, pick=True, scythe=True,
                                   machete=True):
            nxt = step.arrive if step.kind != "door" else step.target
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
                if len(seen) >= REGION_CAP:
                    return None
    return len(seen)


def flags_for(world, src, dst, keys, regions=True):
    flags = []
    info = world.info(dst)
    if world.kind(dst) == VOID:
        flags.append("VOID")
    elif not world.walkable(dst):
        flags.append("BLOCKED")
    if "teleport" in info:
        flags.append(f"ONTO-TP {info['teleport']}")
    elif info.get("down") or info.get("up"):
        flags.append("ONTO-FLOOR")
    if is_rookgaard(src) != is_rookgaard(dst):
        flags.append("ROOK<->MAIN")
    if regions and world.kind(dst) != VOID:
        n = closed_region(world, world.arrival(dst) or dst, keys)
        if n is not None:
            flags.append(f"CLOSED {n}")
    return flags


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--compare", nargs="*", type=Path, default=[], help="other maps to compare destinations with")
    ap.add_argument("--flagged", action="store_true", help="only teleports with a flag")
    ap.add_argument("--no-regions", action="store_true", help="skip the CLOSED check (faster)")
    args = ap.parse_args()

    world = WorldMap.load(SERVER_DIR, Path(__file__).resolve().parents[1] / "tests" / ".run")
    keys = {i["aid"] for i in world.special.values() if i.get("aid")}
    scripts = movement_scripts()
    ours = map_teleports(MAP)
    others = {path.name if path.name != MAP.name else str(path): map_teleports(path) for path in args.compare}

    rows = []
    for src, (item, dst, aid) in ours.items():
        if dst == (0, 0, 0):
            dst = SCRIPTED_TELEPORTS.get(aid)
        if dst is None:
            what = f"script {scripts[aid]} (aid {aid})" if aid in scripts else \
                f"aid {aid}, no script" if aid else "inert"
            rows.append((src, None, what, ["NO-SCRIPT"] if aid and aid not in scripts else []))
            continue
        rows.append((src, dst, f"aid {aid}" if aid else "", flags_for(world, src, dst, keys, not args.no_regions)))
    for aid, dst in SCRIPTED_TELEPORTS.items():     # tiles / doors a script moves you from (no forcefield)
        for pos, info in world.special.items():
            if info.get("aid") == aid and pos not in ours:
                rows.append((pos, dst, f"script aid {aid}", flags_for(world, pos, dst, keys, not args.no_regions)))
    for src, dst, what, flags in rows:
        if what.startswith("script aid"):
            continue                                # a door / tile, not a forcefield: nothing to compare
        for name, theirs in others.items():
            t = theirs.get(src)
            if t is None:
                flags.append(f"DIFF {name}: none")
            elif dst is not None and t[1] != dst and t[1] != (0, 0, 0):
                flags.append(f"DIFF {name}: {t[1]}")
    for name, theirs in others.items():
        for src in sorted(set(theirs) - set(ours)):
            rows.append((src, None, f"only on {name} -> {theirs[src][1]}", [f"DIFF {name}: missing here"]))

    shown = 0
    for src, dst, what, flags in sorted(rows):
        if args.flagged and not flags:
            continue
        shown += 1
        target = "%d,%d,%d" % dst if dst else "-"
        print(f"{'%d,%d,%d' % src:<18} -> {target:<18} {what:<40} {'; '.join(flags)}")
        if src in NOTES:
            print(f"{'':<22}note: {NOTES[src]}")
    with_dest = sum(1 for r in rows if r[1])
    print(f"\n{len(ours)} forcefields with a teleport attribute on {MAP.name}; {with_dest} rows with a destination; "
          f"{shown} shown")
    return 0


if __name__ == "__main__":
    sys.exit(main())

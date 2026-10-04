"""Gives every door of a house a door number of its own, in place in an OTBM map file.

On Tibia74.otbm 92 houses had two or more doors with the same door number (ATTR_HOUSEDOORID; Spiritkeep's door 17 three
times). The engine keeps one access list per door number (House::getDoorByNumber finds the first door with it), so
"aleta grav" on the second door edited the first one's list. The first door with a number keeps it (map order), the
others get the lowest numbers the house does not use yet. A door number of 0 is no house door to the engine
(IOMapOTBM: only doors with a number join the house) and is left alone.

    python tools\\renumber-house-doors.py server\\data\\world\\Tibia74.otbm --backup <folder> [--dry-run]

Only the door number bytes change (one byte each, the file keeps its size). --backup copies the map into that folder
first (never over an existing file); the map's own .bak is not touched.
"""
import argparse
import shutil
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from tibia74.otbm import (ATTR_ACTION_ID, ATTR_COUNT, ATTR_DECAYING_STATE, ATTR_DEPOT_ID, ATTR_DESC,  # noqa: E402
                          ATTR_DURATION, ATTR_HOUSEDOORID, ATTR_RUNE_CHARGES, ATTR_SLEEPERGUID, ATTR_SLEEPSTART,
                          ATTR_TELE_DEST, ATTR_TEXT, ATTR_UNIQUE_ID, ATTR_WRITTENBY, ATTR_WRITTENDATE, OTBM_HOUSETILE,
                          OTBM_ITEM, OTBM_TILE, OTBM_TILE_AREA)

NODE_START, NODE_END, ESCAPE = 0xFE, 0xFF, 0xFD


def door_number_index(props: bytes):
    """Index in an item node's (unescaped) props of its door number byte, or None. Walks the attributes the way
    tests/tibia74/otbm.py reads them (an unknown attribute ends the walk)."""
    p = 2                                                    # after the item id
    while p < len(props):
        a = props[p]
        p += 1
        if a == ATTR_HOUSEDOORID:
            return p if p < len(props) else None
        if a == ATTR_TELE_DEST:
            p += 5
        elif a in (ATTR_ACTION_ID, ATTR_UNIQUE_ID, ATTR_DEPOT_ID):
            p += 2
        elif a in (ATTR_COUNT, ATTR_RUNE_CHARGES, ATTR_DECAYING_STATE):
            p += 1
        elif a in (ATTR_TEXT, ATTR_DESC, ATTR_WRITTENBY):
            p += 2 + struct.unpack_from("<H", props, p)[0]
        elif a in (ATTR_DURATION, ATTR_WRITTENDATE, ATTR_SLEEPERGUID, ATTR_SLEEPSTART):
            p += 4
        else:
            return None
    return None


def house_doors(raw: bytes):
    """[(house id, (x, y, z), item id, door number, offset of the door number byte in raw)], in map order: the items
    lying directly on a house tile that have a door number."""
    doors = []
    i, n = 4, len(raw)
    base = (0, 0, 0)
    stack = []                 # [type, props bytearray, raw offsets of the props bytes (item nodes only) or None]
    tile = None                # (house id, pos) of the house tile being read
    while i < n:
        b = raw[i]
        if b == NODE_START:
            ntype = raw[i + 1]
            # only the items lying directly on a house tile need their byte offsets
            track = ntype == OTBM_ITEM and len(stack) >= 1 and stack[-1][0] == OTBM_HOUSETILE
            stack.append([ntype, bytearray(), [] if track else None])
            i += 2
        elif b == NODE_END:
            ntype, props, offsets = stack.pop()
            if ntype == OTBM_HOUSETILE:
                tile = None
            elif offsets is not None and tile is not None:
                k = door_number_index(bytes(props))
                if k is not None:
                    doors.append((tile[0], tile[1], struct.unpack_from("<H", props, 0)[0], props[k], offsets[k]))
            i += 1
        else:
            if b == ESCAPE:
                i += 1
            node = stack[-1]
            if node[0] == OTBM_ITEM and node[2] is None:      # an item we do not need: skip its bytes quickly
                node[1].append(raw[i])
                i += 1
                continue
            node[1].append(raw[i])
            if node[2] is not None:
                node[2].append(i)
            i += 1
            if node[0] == OTBM_TILE_AREA and len(node[1]) == 5:
                base = struct.unpack_from("<HHB", node[1], 0)
            elif node[0] == OTBM_HOUSETILE and len(node[1]) == 6:
                props = node[1]
                tile = (struct.unpack_from("<I", props, 2)[0], (base[0] + props[0], base[1] + props[1], base[2]))
    return doors


def renumbering(doors):
    """[(house id, pos, old number, new number, offset)] for the doors whose number another door of the house had
    first."""
    by_house = {}
    for hid, pos, _, number, offset in doors:
        if number:
            by_house.setdefault(hid, []).append((pos, number, offset))
    changes = []
    for hid, ds in by_house.items():
        used = {number for _, number, _ in ds}
        seen = set()
        for pos, number, offset in ds:
            if number not in seen:
                seen.add(number)
                continue
            new = next(k for k in range(1, 256) if k not in used)
            if new >= ESCAPE:
                raise SystemExit(f"house {hid}: no door number left below {ESCAPE} for the door at {pos}")
            used.add(new)
            changes.append((hid, pos, number, new, offset))
    return changes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map", type=Path)
    ap.add_argument("--backup", type=Path, help="a folder to copy the map into before writing it")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    raw = bytearray(args.map.read_bytes())
    doors = house_doors(raw)
    changes = renumbering(doors)
    houses = sorted({c[0] for c in changes})
    print(f"{len(doors)} house doors, {sum(1 for d in doors if not d[3])} with door number 0 (left alone); "
          f"{len(changes)} doors of {len(houses)} houses renumbered")
    for hid, pos, old, new, _ in changes:
        print(f"  house {hid} door at {pos}: {old} -> {new}")
    if args.dry_run or not changes:
        return 0
    if args.backup is None:
        raise SystemExit("give --backup <folder> (or --dry-run)")
    args.backup.mkdir(parents=True, exist_ok=True)
    backup = args.backup / f"{args.map.stem}.before-door-renumbering-{time.strftime('%Y%m%d-%H%M%S')}{args.map.suffix}"
    if backup.exists():
        raise SystemExit(f"{backup} exists already")
    shutil.copy2(args.map, backup)
    print(f"backup: {backup}")
    for _, _, old, new, offset in changes:
        assert raw[offset] == old and old < ESCAPE and raw[offset - 1] != ESCAPE, (offset, raw[offset], old)
        raw[offset] = new
    args.map.write_bytes(bytes(raw))
    print(f"wrote {args.map}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

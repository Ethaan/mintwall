"""Copies the tiles of an area from another OTBM map into ours, in place (keeps a .bak the first time) - for a place our
7.4 map export lost and another map rebuilt (the Ornamented Shield Quest's cave under the pick hole: tibiaot74's).

    python tools\\map-copy-tiles.py server\\data\\world\\Tibia74.otbm SOURCE.otbm x1,y1,z x2,y2,z [--skip-ground 100,101]
        [--skip-ids-from 3000] [--skip 3128]

Each source tile in the box whose ground is not in --skip-ground (earth / void: the rock around) replaces ours, or is
added where we have none. Items with an id >= --skip-ids-from (not in our 7.4 item list) and --skip ids are left out;
item attributes kept: action id, unique id, count, teleport destination. Only those tiles' bytes change.
"""
import argparse
import importlib.util
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from tibia74.otbm import (ATTR_ACTION_ID, ATTR_COUNT, ATTR_ITEM, ATTR_TELE_DEST, ATTR_UNIQUE_ID, OTBM_ITEM,  # noqa: E402
                          OTBM_TILE, read_tiles)

_spec = importlib.util.spec_from_file_location("map_set_attrs", Path(__file__).with_name("map-set-attrs.py"))
msa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(msa)
NODE_START, NODE_END = msa.NODE_START, msa.NODE_END


def item_props(m) -> bytes:
    props = struct.pack("<H", m.id)
    if m.attrs.get("count") is not None:
        props += bytes([ATTR_COUNT, m.attrs["count"]])
    if m.attrs.get("action_id") is not None:
        props += bytes([ATTR_ACTION_ID]) + struct.pack("<H", m.attrs["action_id"])
    if m.attrs.get("unique_id") is not None:
        props += bytes([ATTR_UNIQUE_ID]) + struct.pack("<H", m.attrs["unique_id"])
    if m.attrs.get("teleport") is not None:
        props += bytes([ATTR_TELE_DEST]) + struct.pack("<HHB", *m.attrs["teleport"])
    return props


def tile_node(pos, items) -> bytes:
    ground, rest = items[0], items[1:]
    props = bytes([pos[0] & 0xFF, pos[1] & 0xFF, ATTR_ITEM]) + struct.pack("<H", ground.id)
    children = b"".join(bytes([NODE_START, OTBM_ITEM]) + msa.escape(item_props(m)) + bytes([NODE_END]) for m in rest)
    return bytes([NODE_START, OTBM_TILE]) + msa.escape(props) + children + bytes([NODE_END])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map", type=Path)
    ap.add_argument("source", type=Path)
    ap.add_argument("start", help="x1,y1,z")
    ap.add_argument("end", help="x2,y2,z (same floor)")
    ap.add_argument("--skip-ground", default="100,101", help="source tiles with this ground are the rock around: left")
    ap.add_argument("--skip-ids-from", type=int, default=3000)
    ap.add_argument("--skip", default="", help="item ids to leave out (e.g. the source's own quest body)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    a = tuple(int(v) for v in args.start.split(","))
    b = tuple(int(v) for v in args.end.split(","))
    skip_ground = {int(v) for v in args.skip_ground.split(",") if v}
    skip = {int(v) for v in args.skip.split(",") if v}

    source = [t for t in read_tiles(args.source, area=(a, b)) if t.items and t.items[0].id not in skip_ground]
    raw = args.map.read_bytes()
    for t in sorted(source, key=lambda t: t.pos):
        items = [t.items[0]] + [m for m in t.items[1:] if m.id < args.skip_ids_from and m.id not in skip]
        new = tile_node(t.pos, items)
        ours = msa.find_tile(raw, t.pos)
        if ours is not None:
            start, end = ours["start"], ours["end"] + 1
            what = "replaced"
        else:
            start = end = msa.find_area_end(raw, (t.pos[0] & 0xFF00, t.pos[1] & 0xFF00, t.pos[2]))
            what = "added"
        dropped = [m.id for m in t.items[1:] if m not in items]
        print(f"{t.pos}: {what}, {[m.id for m in items]}" + (f" (left out {dropped})" if dropped else ""))
        raw = raw[:start] + new + raw[end:]
    if args.dry_run:
        return 0
    backup = args.map.with_suffix(args.map.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(args.map, backup)
    args.map.write_bytes(raw)
    print(f"wrote {args.map}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

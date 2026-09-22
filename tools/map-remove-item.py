"""Removes an item from a tile in an OTBM map file, in place (keeps a .bak the first time).

    python tools\\map-remove-item.py server\\data\\world\\Tibia74.otbm 32095,32219,7 --id 1387

Deletes whole item nodes, so the rest of the file is untouched. Prints what it removed.
"""
import argparse
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from tibia74.otbm import OTBM_HOUSETILE, OTBM_ITEM, OTBM_TILE, OTBM_TILE_AREA  # noqa: E402

NODE_START, NODE_END, ESCAPE = 0xFE, 0xFF, 0xFD


def find_item_nodes(raw: bytes, target: tuple, item_id: int = None):
    """Yield (start_offset, end_offset_exclusive, id, props) for item nodes on the target tile."""
    i, n = 4, len(raw)
    base = (0, 0, 0)
    tile_pos = None
    stack = []            # (type, props bytearray, start offset)
    while i < n:
        b = raw[i]
        if b == NODE_START:
            stack.append([raw[i + 1], bytearray(), i])
            i += 2
        elif b == NODE_END:
            ntype, props, start = stack.pop()
            if ntype == OTBM_TILE_AREA:
                pass
            elif ntype == OTBM_ITEM and tile_pos == target:
                iid = struct.unpack_from("<H", props, 0)[0]
                if item_id is None or iid == item_id:
                    yield start, i + 1, iid, bytes(props)
            i += 1
        else:
            if b == ESCAPE:
                i += 1
            node = stack[-1]
            node[1].append(raw[i])
            i += 1
            # A tile/area node's position is known once its fixed header bytes have been read
            if node[0] == OTBM_TILE_AREA and len(node[1]) == 5:
                base = struct.unpack_from("<HHB", node[1], 0)
            elif node[0] in (OTBM_TILE, OTBM_HOUSETILE) and len(node[1]) == 2:
                tile_pos = (base[0] + node[1][0], base[1] + node[1][1], base[2])
    return


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map", type=Path)
    ap.add_argument("pos", help="x,y,z of the tile")
    ap.add_argument("--id", type=int, default=None, help="only remove items with this id")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    target = tuple(int(v) for v in args.pos.split(","))
    raw = args.map.read_bytes()
    found = list(find_item_nodes(raw, target, args.id))
    if not found:
        print(f"no matching item on {target}")
        return 1

    for start, end, iid, props in found:
        print(f"removing item {iid} at {target} ({end - start} bytes at offset {start})")
    if args.dry_run:
        return 0

    backup = args.map.with_suffix(args.map.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(args.map, backup)
        print(f"backup: {backup}")

    out = bytearray(raw)
    for start, end, _, _ in sorted(found, reverse=True):
        del out[start:end]
    args.map.write_bytes(bytes(out))
    print(f"wrote {args.map} ({len(raw)} -> {len(out)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

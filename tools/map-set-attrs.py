"""Gives an item on a tile of an OTBM map file an action id and/or unique id, or a teleport a new destination
(--teleport x,y,z), or puts a new item on a tile (--add), or makes a tile where the map has none (--new-tile, the item
is its ground), in place (keeps a .bak the first time).

    python tools\\map-set-attrs.py server\\data\\world\\Tibia74.otbm 32084,32181,8 --id 405 --aid 2000 --uid 2485

The item may be a full item node or the tile's inline ground (then it becomes an item node, the way RME saves a
ground with attributes). Only that tile's bytes change. Refuses a unique id already used elsewhere on the map.
"""
import argparse
import shutil
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from tibia74.otbm import (ATTR_ACTION_ID, ATTR_COUNT, ATTR_ITEM, ATTR_TELE_DEST, ATTR_TILE_FLAGS, ATTR_UNIQUE_ID,  # noqa: E402
                          OTBM_HOUSETILE, OTBM_ITEM, OTBM_TILE, OTBM_TILE_AREA, _item_attrs_strict, read_tiles)

NODE_START, NODE_END, ESCAPE = 0xFE, 0xFF, 0xFD


def escape(data: bytes) -> bytes:
    out = bytearray()
    for b in data:
        if b in (NODE_START, NODE_END, ESCAPE):
            out.append(ESCAPE)
        out.append(b)
    return bytes(out)


def find_tile(raw: bytes, target: tuple):
    """The target tile: {"start", "props_end", "type", "props", "items": [{"start", "props_end", "props"}]}
    (offsets into raw; props_end = where the node's own props stop: its first child or its end)."""
    i, n = 4, len(raw)
    base = (0, 0, 0)
    stack = []            # [type, props, start, props_end]
    tile = None
    while i < n:
        b = raw[i]
        if b == NODE_START:
            if stack and stack[-1][3] is None:
                stack[-1][3] = i
            stack.append([raw[i + 1], bytearray(), i, None])
            i += 2
        elif b == NODE_END:
            ntype, props, start, props_end = stack.pop()
            props_end = i if props_end is None else props_end
            if ntype == OTBM_TILE_AREA:
                base = struct.unpack_from("<HHB", props, 0)
            elif ntype in (OTBM_TILE, OTBM_HOUSETILE):
                pos = (base[0] + props[0], base[1] + props[1], base[2])
                if pos == target:
                    tile["start"], tile["props_end"], tile["type"], tile["props"] = start, props_end, ntype, bytes(props)
                    tile["end"] = i                  # its NODE_END: a new item goes right before it (on top)
                    return tile
                tile = None
            elif ntype == OTBM_ITEM and len(stack) >= 1 and stack[-1][0] in (OTBM_TILE, OTBM_HOUSETILE):
                if tile is None:
                    tile = {"items": []}
                tile["items"].append({"start": start, "props_end": props_end, "props": bytes(props)})
            i += 1
        else:
            if b == ESCAPE:
                i += 1
            stack[-1][1].append(raw[i])
            i += 1
            node = stack[-1]
            if node[0] == OTBM_TILE_AREA and len(node[1]) == 5:
                base = struct.unpack_from("<HHB", node[1], 0)
            elif node[0] in (OTBM_TILE, OTBM_HOUSETILE) and len(node[1]) == 1:
                tile = {"items": []}     # a new tile starts: forget the previous tile's items
    return None


def find_area_end(raw: bytes, base: tuple):
    """Offset of the NODE_END of the tile area (x & 0xFF00, y & 0xFF00, z) - a new tile goes right before it."""
    i, n = 4, len(raw)
    stack = []            # [type, props]
    while i < n:
        b = raw[i]
        if b == NODE_START:
            stack.append([raw[i + 1], bytearray()])
            i += 2
        elif b == NODE_END:
            ntype, props = stack.pop()
            if ntype == OTBM_TILE_AREA and tuple(struct.unpack_from("<HHB", props, 0)) == base:
                return i
            i += 1
        else:
            if b == ESCAPE:
                i += 1
            if stack and len(stack[-1][1]) < 16:
                stack[-1][1].append(raw[i])
            i += 1
    return None


def inline_ground(tile: dict):
    """(offset in tile props of the ATTR_ITEM attribute, ground id) or None."""
    props = tile["props"]
    p = 2 + (4 if tile["type"] == OTBM_HOUSETILE else 0)
    while p < len(props):
        a = props[p]
        if a == ATTR_TILE_FLAGS:
            p += 5
        elif a == ATTR_ITEM:
            return p, struct.unpack_from("<H", props, p + 1)[0]
        else:
            break
    return None


def with_ids(props: bytes, aid, uid) -> bytes:
    extra = b""
    if aid is not None:
        extra += bytes([ATTR_ACTION_ID]) + struct.pack("<H", aid)
    if uid is not None:
        extra += bytes([ATTR_UNIQUE_ID]) + struct.pack("<H", uid)
    return props + extra


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map", type=Path)
    ap.add_argument("pos", help="x,y,z of the tile")
    ap.add_argument("--id", type=int, required=True, help="the item's id")
    ap.add_argument("--aid", type=int)
    ap.add_argument("--uid", type=int)
    ap.add_argument("--teleport", help="x,y,z: the new destination of the teleport")
    ap.add_argument("--contents", default="",
                    help='with --add: items inside the new container, e.g. "2465,2460,2388,2399x4" (id or idxcount)')
    ap.add_argument("--add", action="store_true",
                    help="put a new item --id (with --aid/--uid) on top of the tile instead of editing one there")
    ap.add_argument("--bottom", action="store_true",
                    help="with --add: put the new item right above the ground, under what lies there (a lever under a "
                         "fire field and a corpse)")
    ap.add_argument("--top", action="store_true",
                    help="two or more of the item on the tile (stacked boxes): take the top one - the one a use opens")
    ap.add_argument("--replace", action="store_true",
                    help="the item already has an action / unique id (and nothing else): replace them")
    ap.add_argument("--new-tile", action="store_true",
                    help="the map has no tile there: make one whose ground is --id (e.g. stairs down over stairs up "
                         "whose floor the map left out)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.aid is None and args.uid is None and args.teleport is None and not args.add and not args.new_tile:
        ap.error("give --aid and/or --uid, or --teleport")

    target = tuple(int(v) for v in args.pos.split(","))
    if args.uid is not None:
        for t in read_tiles(args.map):
            for m in t.items:
                if m.attrs.get("unique_id") == args.uid:
                    raise SystemExit(f"unique id {args.uid} is already on {t.pos} (item {m.id})")

    raw = args.map.read_bytes()
    tile = find_tile(raw, target)
    if args.new_tile:
        if tile is not None:
            raise SystemExit(f"{target} already has a tile")
        area = (target[0] & 0xFF00, target[1] & 0xFF00, target[2])
        start = end = find_area_end(raw, area)
        if start is None:
            raise SystemExit(f"no tile area {area} in the map - add the tile with a map editor")
        props = bytes([target[0] & 0xFF, target[1] & 0xFF, ATTR_ITEM]) + struct.pack("<H", args.id)
        new = bytes([NODE_START, OTBM_TILE]) + escape(props) + bytes([NODE_END])
        print(f"{target}: new tile, ground {args.id}")
        return _write(args, raw, start, end, new)
    if tile is None:
        raise SystemExit(f"no tile at {target}")

    matching = [it for it in tile["items"] if struct.unpack_from("<H", it["props"], 0)[0] == args.id]
    item = (matching[-1] if args.top else matching[0]) if matching else None
    if args.add:
        start = end = tile["end"]
        if args.bottom:
            if inline_ground(tile) is not None:
                start = end = tile["props_end"]              # the ground is in the tile's props: first child
            else:
                ground = tile["items"][0]                    # the ground's node (no children): right after it
                if raw[ground["props_end"]] != NODE_END:
                    raise SystemExit(f"the ground on {target} has children - edit it by hand")
                start = end = ground["props_end"] + 1
        children = b""
        for part in filter(None, args.contents.split(",")):
            cid, _, count = part.partition("x")
            props = struct.pack("<H", int(cid)) + (bytes([ATTR_COUNT, int(count)]) if count else b"")
            children += bytes([NODE_START, OTBM_ITEM]) + escape(props) + bytes([NODE_END])
        new = bytes([NODE_START, OTBM_ITEM]) + escape(with_ids(struct.pack("<H", args.id), args.aid, args.uid))             + children + bytes([NODE_END])
        what = "new item above the ground" if args.bottom else "new item on top"
    elif args.teleport is not None:
        props = item["props"] if item is not None else b""
        if len(props) != 8 or props[2] != ATTR_TELE_DEST:
            raise SystemExit(f"no teleport {args.id} (with only a destination) on {target}")
        dest = tuple(int(v) for v in args.teleport.split(","))
        start, end = item["start"] + 2, item["props_end"]
        new = escape(props[:3] + struct.pack("<HHB", *dest))
        what = f"teleport {struct.unpack_from('<HHB', props, 3)} -> {dest}"
    elif item is not None:
        if len(item["props"]) > 2:
            # other attributes (a text, a count): the ids go after them, unless it already has one
            attrs = _item_attrs_strict(item["props"], 2)
            if "unknown" in attrs or (("action_id" in attrs or "unique_id" in attrs) and
                                      not (args.replace and set(attrs) <= {"action_id", "unique_id"})):
                raise SystemExit(f"item {args.id} on {target} already has {attrs} - edit it by hand (or --replace)")
            if args.replace:                     # only ids on it: write them anew
                item["props"] = item["props"][:2]
        start, end = item["start"] + 2, item["props_end"]
        new = escape(with_ids(item["props"], args.aid, args.uid))
        what = "item node"
    else:
        ground = inline_ground(tile)
        if ground is None or ground[1] != args.id:
            raise SystemExit(f"no item {args.id} on {target}")
        p, _ = ground
        props = tile["props"]
        tile_props = props[:p] + props[p + 3:]
        node = bytes([NODE_START, OTBM_ITEM]) + escape(with_ids(struct.pack("<H", args.id), args.aid, args.uid)) \
            + bytes([NODE_END])
        # the ground node goes first among the tile's children (ground is the bottom of the stack)
        start, end = tile["start"] + 2, tile["props_end"]
        new = escape(tile_props) + node
        what = "inline ground -> item node"

    print(f"{target}: item {args.id} ({what})" + ("" if args.teleport else f" gets aid={args.aid} uid={args.uid}"))
    return _write(args, raw, start, end, new)


def _write(args, raw, start, end, new):
    if args.dry_run:
        return 0
    backup = args.map.with_suffix(args.map.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(args.map, backup)
        print(f"backup: {backup}")
    out = raw[:start] + new + raw[end:]
    args.map.write_bytes(out)
    print(f"wrote {args.map} ({len(raw)} -> {len(out)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

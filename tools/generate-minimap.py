"""Write the 7.4 client's minimap files (*.map) for the whole world: every floor shows as explored.

    tests\\.venv\\Scripts\\python.exe tools\\generate-minimap.py [--client-dir client\\Tibia740]

Close the client first: it rewrites its .map files when it exits.

File format (checked against files the client wrote itself: 5890 of 5891 explored tiles identical):
  name     XXXYYYZZ.map = x // 256, y // 256 (3 digits each), floor (2 digits); one file per 256x256 block
  0..65535       minimap colour per tile, column by column (index = dx * 256 + dy); 0 = unexplored
  65536..131071  walk speed per tile (the ground's speed, 255 = cannot walk), same order
  131072..       u32 number of map marks + the marks - kept from the existing file, so your flags stay

Colour = the last minimap colour among the tile's ground / bottom (walls) / top items, like the client.
Colours and speeds come from the client's Tibia.dat (7.40 layout, parsed exactly to its last byte).
"""
import argparse
import struct
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))
from tibia74 import SERVER_DIR, Items           # noqa: E402
from tibia74.otbm import read_tiles              # noqa: E402

# 7.40 Tibia.dat item flags that carry data (bytes): ground speed, writable, writable once, light,
# elevation, minimap colour (OTClient's 7.40 attribute table)
DAT_DATA = {0: 2, 7: 2, 8: 2, 16: 4, 19: 2, 22: 2}
GROUND, ON_BOTTOM, ON_TOP, NOT_WALKABLE, MINIMAP_COLOUR = 0, 1, 2, 11, 22
BLOCK = 256 * 256


def read_dat(path: Path) -> list:
    """Flags of every thing in Tibia.dat, index = client id - 100 (items first)."""
    b = path.read_bytes()
    _, items, creatures, effects, missiles = struct.unpack_from("<IHHHH", b, 0)
    pos, things = 12, []
    for _ in range((items - 99) + creatures + effects + missiles):
        flags = {}
        while True:
            f = b[pos]
            pos += 1
            if f == 0xFF:
                break
            size = DAT_DATA.get(f, 0)
            flags[f] = b[pos:pos + size]
            pos += size
        w, h = b[pos], b[pos + 1]
        pos += 2 + (1 if w > 1 or h > 1 else 0)
        layers, px, py, phases = b[pos:pos + 4]
        pos += 4 + 2 * w * h * layers * px * py * phases
        things.append(flags)
    if pos != len(b):
        raise SystemExit(f"{path}: parsed {pos} of {len(b)} bytes - not the 7.40 layout")
    return things


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--client-dir", type=Path, default=REPO / "client" / "Tibia740")
    args = ap.parse_args(argv)

    started = time.time()
    things = read_dat(args.client_dir / "Tibia.dat")
    items = Items(SERVER_DIR / "data")
    cache = {}

    def tile_info(server_id):
        """(colour or 0 if none / not a ground-wall-top item, ground speed or 0, blocks walking)"""
        if server_id not in cache:
            t = items.by_server.get(server_id)
            f = things[t.client_id - 100] if t and 100 <= t.client_id < 100 + len(things) else {}
            colour = 0
            if MINIMAP_COLOUR in f and (GROUND in f or ON_BOTTOM in f or ON_TOP in f):
                colour = struct.unpack("<H", f[MINIMAP_COLOUR])[0] & 0xFF
            speed = struct.unpack("<H", f[GROUND])[0] if GROUND in f else 0
            cache[server_id] = (colour, speed, NOT_WALKABLE in f)
        return cache[server_id]

    blocks = {}                                    # (bx, by, z) -> bytearray(2 * BLOCK)
    tiles = 0
    for tile in read_tiles(SERVER_DIR / "data" / "world" / "Tibia74.otbm"):
        x, y, z = tile.pos
        colour, speed, walkable = 0, 0, True
        for item in tile.items:
            c, s, blocks_walk = tile_info(item.id)
            if c:
                colour = c
            if s:
                speed = s
            if blocks_walk:
                walkable = False
        if not colour:
            continue
        key = (x // 256, y // 256, z)
        data = blocks.get(key)
        if data is None:
            data = blocks[key] = bytearray(BLOCK) + bytearray(b"\xff" * BLOCK)
        i = (x % 256) * 256 + (y % 256)
        data[i] = colour
        data[BLOCK + i] = min(speed, 254) if walkable and speed else 255
        tiles += 1

    kept = 0
    for (bx, by, z), data in blocks.items():
        path = args.client_dir / f"{bx:03d}{by:03d}{z:02d}.map"
        marks = struct.pack("<I", 0)
        if path.exists():
            old = path.read_bytes()
            if len(old) >= 2 * BLOCK + 4:
                marks = old[2 * BLOCK:]            # the player's map marks
                kept += struct.unpack_from("<I", marks, 0)[0]
        path.write_bytes(bytes(data) + marks)
    print(f"{len(blocks)} minimap files, {tiles} tiles, {kept} map marks kept "
          f"({time.time() - started:.0f} s) in {args.client_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

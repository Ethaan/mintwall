r"""Why can't the route planner get somewhere? Prints the walkable region around each point (same floor, the
planner's own walkability) and every way in or out of it: floor changes next to it, teleports into it, doors on
its edge. Trace backwards from a quest room until a region shows no way in - that is the missing piece (a switch,
a key door, a pick spot, a grate).

    python tools\map-regions.py 33324,31592,15 33287,31592,13
"""
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from tibia74 import SERVER_DIR  # noqa: E402
from tibia74.worldmap import WorldMap  # noqa: E402


def region(world, start, cap=40000):
    seen, queue = {start}, deque([start])
    while queue:
        x, y, z = queue.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                n = (x + dx, y + dy, z)
                if n not in seen and world.walkable(n) and len(seen) < cap:
                    seen.add(n)
                    queue.append(n)
    return seen


def main():
    world = WorldMap.load(SERVER_DIR, Path(__file__).resolve().parents[1] / "tests" / ".run")
    for arg in sys.argv[1:]:
        start = tuple(int(v) for v in arg.split(","))
        tiles = region(world, start)
        xs, ys = [p[0] for p in tiles], [p[1] for p in tiles]
        print(f"{start}: {len(tiles)} tiles, x {min(xs)}-{max(xs)}, y {min(ys)}-{max(ys)}")
        for pos, info in sorted(world.special.items()):
            near = any((pos[0] + dx, pos[1] + dy, pos[2] + dz) in tiles
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1) for dz in (-1, 0, 1))
            if pos in tiles and info.keys() - {"stand"}:
                print("   in       ", pos, info, "->", world.arrival(pos))
            elif "teleport" in info and tuple(info["teleport"]) in tiles:
                print("   tp into  ", pos, info)
            elif near and pos not in tiles:
                print("   next to  ", pos, info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

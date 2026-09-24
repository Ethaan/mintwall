"""The world map as the route planner needs it: which tiles you can walk on, and how you change floors.

Built from server/data/world/Tibia74.otbm and cached under tests/.run (rebuilt when the map, items.otb or
actions.xml change). Every rule comes from the server, not from guesses:
- walkable: a ground with a speed, and no item with the items.otb "block solid" flag (closed doors are
  blocking, but listed as doors: they open);
- floor changes (items.otb flags, as in Tile::__queryDestination, tile.cpp):
    down  (hole, stairs down): (x, y, z) -> (x, y, z+1), moved off a ramp below: N y+1, S y-1, E x-1, W x+1
    up    (ramp N/S/E/W):      (x, y, z) -> (x, y, z-1) moved N y-1, S y+1, E x+1, W x-1
- ladder (item 1386, actions/scripts/teleport.lua): use it -> (x, y+1, z-1)
- rope spot (ground 384 / 418, actions/scripts/rope.lua): use a rope on it (nobody on it) -> (x, y+1, z-1)
- doors, by the script actions.xml gives the item: increment.lua = closed (use opens it), door_locked.lua =
  a key with the door's action id opens it (key.lua), questdoor_closed.lua = storage (action id) must be 1,
  gateofexp_closed.lua = level (action id - 1000) or vocation (2001-2008)
- teleports: items with a destination (OTBM teleport attribute)
- tools: grown wheat (2739) is passable after a scythe cuts it; a stone pile (closed hole) becomes a way
  down after a shovel opens it (hole: down, like any hole)
"""
import pickle
import re
from pathlib import Path

from .items import Items
from .otbm import read_tiles

VOID, WALK, BLOCKED, SPECIAL = 0, 1, 2, 3
BLOCK_SOLID = 1
FLOOR_DOWN, FLOOR_N, FLOOR_E, FLOOR_S, FLOOR_W = 256, 512, 1024, 2048, 4096
LADDER = 1386
ROPE_SPOTS = {384, 418}
UP_SHIFT = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
DOWN_SHIFT = {"N": (0, 1), "S": (0, -1), "E": (-1, 0), "W": (1, 0)}   # moved off a ramp you arrive on
DOOR_SCRIPTS = {"increment.lua": "closed", "doors/door_locked.lua": "locked",
                "doors/questdoor_closed.lua": "quest", "doors/gateofexp_closed.lua": "level"}
CACHE_VERSION = 3
GROWN_WHEAT = 2739                   # solid; a scythe cuts it (actions/scripts/scythe.lua)
STONE_PILES = {468, 481, 483}        # closed holes (CLOSED_HOLE, actions/lib/actions.lua): a shovel opens them


def _xml_floor_changes(server_dir: Path) -> dict:
    """item id -> "down" / "N" / "S" / "E" / "W" from items.xml <attribute key="floorchange">. The engine
    takes floor changes from items.otb flags AND from these (items.cpp); this items.otb has none."""
    xml = (server_dir / "data" / "items" / "items.xml").read_text(encoding="latin-1")
    out = {}
    for m in re.finditer(r"<item\s+([^>]*?)/?>(.*?)(?=<item\s|</items>)", xml, re.S):
        change = re.search(r'key="floorchange"\s+value="(\w+)"', m.group(2))
        if not change:
            continue
        value = {"down": "down", "north": "N", "south": "S", "east": "E", "west": "W"}[change.group(1).lower()]
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        if "id" in attrs:
            ids = [int(attrs["id"])]
        else:
            ids = range(int(attrs["fromid"]), int(attrs["toid"]) + 1)
        for i in ids:
            out[i] = value
    return out


def _door_kinds(server_dir: Path) -> dict:
    """item id -> door kind, from the scripts actions.xml gives the closed doors."""
    xml = (server_dir / "data" / "actions" / "actions.xml").read_text(encoding="latin-1")
    kinds = {}
    for item_id, script in re.findall(r'itemid="(\d+)"\s+script="([^"]+)"', xml):
        if script in DOOR_SCRIPTS:
            kinds[int(item_id)] = DOOR_SCRIPTS[script]
    return kinds


class WorldMap:
    def __init__(self, walk: dict, special: dict):
        self.walk = walk          # (x // 256, y // 256, z) -> bytearray(65536), index (x % 256) * 256 + (y % 256)
        self.special = special    # (x, y, z) -> dict describing the tile (see _classify)

    # ------------------------------------------------------------------ queries
    def kind(self, pos) -> int:
        x, y, z = pos
        block = self.walk.get((x // 256, y // 256, z))
        return block[(x % 256) * 256 + (y % 256)] if block else VOID

    def walkable(self, pos) -> bool:
        k = self.kind(pos)
        return k == WALK or (k == SPECIAL and self.special.get(tuple(pos), {}).get("stand", False))

    def info(self, pos) -> dict:
        return self.special.get(tuple(pos), {})

    def arrival(self, pos):
        """Where stepping onto pos takes you (floor change / teleport), or None for a normal tile."""
        s = self.info(pos)
        x, y, z = pos
        if "teleport" in s:
            return tuple(s["teleport"])
        if s.get("down"):
            below = self.info((x, y, z + 1)).get("up")
            dx, dy = DOWN_SHIFT.get(below, (0, 0))
            return (x + dx, y + dy, z + 1)
        if s.get("up"):
            dx, dy = UP_SHIFT[s["up"]]
            return (x + dx, y + dy, z - 1)
        return None

    # ------------------------------------------------------------------ building
    @classmethod
    def load(cls, server_dir: Path, cache_dir: Path) -> "WorldMap":
        sources = [server_dir / "data" / "world" / "Tibia74.otbm", server_dir / "data" / "items" / "items.otb",
                   server_dir / "data" / "actions" / "actions.xml", server_dir / "data" / "items" / "items.xml"]
        stamp = (CACHE_VERSION,) + tuple(int(p.stat().st_mtime) for p in sources)
        cache = cache_dir / "worldmap.pickle"
        if cache.exists():
            try:
                with open(cache, "rb") as f:
                    saved_stamp, walk, special = pickle.load(f)
                if saved_stamp == stamp:
                    return cls(walk, special)
            except Exception:
                pass
        world = cls.build(server_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        with open(cache, "wb") as f:
            pickle.dump((stamp, world.walk, world.special), f, protocol=pickle.HIGHEST_PROTOCOL)
        return world

    @classmethod
    def build(cls, server_dir: Path) -> "WorldMap":
        items = Items(server_dir / "data")
        doors = _door_kinds(server_dir)
        changes = _xml_floor_changes(server_dir)
        walk, special = {}, {}
        for tile in read_tiles(server_dir / "data" / "world" / "Tibia74.otbm"):
            kind, info = cls._classify(tile, items, doors, changes)
            if kind == VOID:
                continue
            x, y, z = tile.pos
            block = walk.get((x // 256, y // 256, z))
            if block is None:
                block = walk[(x // 256, y // 256, z)] = bytearray(256 * 256)
            block[(x % 256) * 256 + (y % 256)] = kind
            if info:
                special[tile.pos] = info
        return cls(walk, special)

    @staticmethod
    def _classify(tile, items, doors, changes):
        if not tile.items:
            return VOID, None
        ground = items.by_server.get(tile.items[0].id)
        if ground is None or not ground.speed:
            return VOID, None
        info, blocked = {}, False
        for m in tile.items:
            t = items.by_server.get(m.id)
            if t is None:
                continue
            if m.id in doors:
                info["door"] = doors[m.id]
                info["door_id"] = m.id
                info["aid"] = m.attrs.get("action_id", 0)
                continue
            if t.flags & FLOOR_DOWN or changes.get(m.id) == "down":
                info["down"] = True
            if changes.get(m.id) in UP_SHIFT:
                info["up"] = changes[m.id]
            for flag, d in ((FLOOR_N, "N"), (FLOOR_S, "S"), (FLOOR_E, "E"), (FLOOR_W, "W")):
                if t.flags & flag:
                    info["up"] = d
            if m.id == LADDER:
                info["ladder"] = True
            if m.id in ROPE_SPOTS:
                info["rope"] = True
            if m.id == GROWN_WHEAT:
                info["wheat"] = True
                continue                  # blocking only until cut
            if m.id in STONE_PILES:
                info["dig"] = True        # a shovel opens a hole: a way down
            if m.attrs.get("teleport"):
                info["teleport"] = tuple(m.attrs["teleport"])
            if t.flags & BLOCK_SOLID:
                blocked = True
        if info.get("down") or info.get("up") or "teleport" in info:
            info["stand"] = True          # you walk onto it (and are moved)
            return SPECIAL, info
        if "door" in info or info.get("wheat") or info.get("dig"):
            return SPECIAL, info          # blocking / a way down only with the right tool
        if info:                          # ladder / rope spot: used from next to it
            info["stand"] = not blocked
            return SPECIAL, info
        return (BLOCKED if blocked else WALK), None

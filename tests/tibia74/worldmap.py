"""The world map as the route planner needs it: which tiles you can walk on, and how you change floors.

Built from server/data/world/Tibia74.otbm and cached under tests/.run (rebuilt when the map, items.otb or
actions.xml change). Every rule comes from the server, not from guesses:
- walkable: a ground with a speed, and no item with the items.otb "block solid" flag (closed doors are
  blocking, but listed as doors: they open);
- floor changes (items.otb flags, as in Tile::__queryDestination, tile.cpp):
    down  (hole, stairs down): (x, y, z) -> (x, y, z+1), moved off a ramp below: N y+1, S y-1, E x-1, W x+1
    up    (ramp N/S/E/W):      (x, y, z) -> (x, y, z-1) moved N y-1, S y+1, E x+1, W x-1
- ladder (item 1386, actions/scripts/teleport.lua): use it -> (x, y+1, z-1)
- sewer grate (item 430, the same script): use it -> (x, y, z+1)
- rope spot (ground 384 / 418, actions/scripts/rope.lua): use a rope on it (nobody on it) -> (x, y+1, z-1)
- doors, by the script actions.xml gives the item: increment.lua = closed (use opens it), door_locked.lua =
  a key with the door's action id opens it (key.lua), questdoor_closed.lua = storage (action id) must be 1,
  gateofexp_closed.lua = level (action id - 1000) or vocation (2001-2008)
- teleports: items with a destination (OTBM teleport attribute)
- tools: grown wheat (2739) is passable after a scythe cuts it; a stone pile (closed hole) becomes a way
  down after a shovel opens it (hole: down, like any hole)
- a tile blocked only by movable things (a barrel, a crate) is passable after pushing them aside ("push")
"""
import pickle
import re
from pathlib import Path

from .items import Items
from .otbm import read_tiles

VOID, WALK, BLOCKED, SPECIAL = 0, 1, 2, 3
BLOCK_SOLID = 1
MOVEABLE = 64                         # items.otb: a player can push it aside (a barrel, a crate)
HAS_HEIGHT = 8                        # items.otb: two of these on a tile are too high to step on (game.cpp)
FLOOR_DOWN, FLOOR_N, FLOOR_E, FLOOR_S, FLOOR_W = 256, 512, 1024, 2048, 4096
LADDER = 1386
SEWER_GRATE = 430                     # actions/scripts/teleport.lua: use it -> (x, y, z+1)
WELL_DOWN = 54545                     # action id of wells you climb down (actions/scripts/draw_well_down.lua)
ROPE_SPOTS = {384, 418}
UP_SHIFT = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
DOWN_SHIFT = {"N": (0, 1), "S": (0, -1), "E": (-1, 0), "W": (1, 0)}   # moved off a ramp you arrive on
DOOR_SCRIPTS = {"increment.lua": "closed", "doors/door_locked.lua": "locked",
                "doors/questdoor_closed.lua": "quest", "doors/gateofexp_closed.lua": "level"}
CACHE_VERSION = 15
GROWN_WHEAT = 2739                   # solid; a scythe cuts it (actions/scripts/scythe.lua)
JUNGLE_GRASS = 2782                  # solid; a machete cuts it (actions/scripts/machete.lua) - the Paradox Tower
STONE_PILES = {468, 481, 483}        # closed holes (CLOSED_HOLE, actions/lib/actions.lua): a shovel opens them
MUD = {103, 351, 352, 353, 354, 355}  # actions/lib/actions.lua: with action id 100 a pick opens a hole (pick.lua)
PICK_SPOT = 100
PITFALL_GRASS = 293                  # movements/scripts/pitfall.lua: opens under a player, who falls one floor down
# tiles a movement script teleports you from (no teleport item): action id -> destination
SCRIPTED_TELEPORTS = {51056: (32266, 31864, 12),   # the Banshee Quest's secret teleporter (movements/banshee_seals.lua)
                      51082: (32566, 31958, 1)}    # the Paradox Tower's carvings back (movements/paradox_tower.lua)


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
    """item id -> door kind, from the scripts actions.xml gives the closed doors. Only items named a door or a
    gate: increment.lua also lights ovens and lamps and flips switches - none of them a way through."""
    xml = (server_dir / "data" / "actions" / "actions.xml").read_text(encoding="latin-1")
    items = (server_dir / "data" / "items" / "items.xml").read_text(encoding="latin-1")
    names = {int(m.group(1)): m.group(2) for m in re.finditer(r'<item id="(\d+)"[^>]*name="([^"]*)"', items)}
    kinds = {}
    for item_id, script in re.findall(r'itemid="(\d+)"\s+script="([^"]+)"', xml):
        name = names.get(int(item_id), "")
        if script in DOOR_SCRIPTS and ("door" in name or "gate" in name):
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
        """Where stepping onto pos takes you (floor change / teleport), or None for a normal tile. Chained: the
        server moves you on from where you land if that is a floor change too (a hole onto a hole drops two
        floors - the Demon Helmet Quest's "hole [...] will bring you down 2 floors")."""
        where = self._arrival_once(pos)
        for _ in range(8):
            nxt = self._arrival_once(where) if where is not None else None
            if nxt is None:
                return where
            where = nxt
        return where

    def _arrival_once(self, pos):
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
        info, blocked, fixed = {}, False, False
        pushable, high = [], []
        for m in tile.items:
            t = items.by_server.get(m.id)
            if t is None:
                continue
            if m.id in doors and m.attrs.get("house_door"):
                blocked = fixed = True    # a house door opens for its owner and guests only ("You are not invited.")
                continue
            if m.id in doors:
                info["door"] = doors[m.id]
                info["door_id"] = m.id
                info["aid"] = m.attrs.get("action_id", 0)
                continue
            if t.flags & FLOOR_DOWN or changes.get(m.id) == "down" or m.id == PITFALL_GRASS:
                info["down"] = True
            if changes.get(m.id) in UP_SHIFT:
                info["up"] = changes[m.id]
            for flag, d in ((FLOOR_N, "N"), (FLOOR_S, "S"), (FLOOR_E, "E"), (FLOOR_W, "W")):
                if t.flags & flag:
                    info["up"] = d
            if m.id == LADDER:
                info["ladder"] = True
            # a sewer grate with an action id of its own is up to its script (the Mintwallin grate is shut)
            if (m.id == SEWER_GRATE and not m.attrs.get("action_id")) or m.attrs.get("action_id") == WELL_DOWN:
                info["grate"] = True      # used from next to it: one floor down
                info["grate_id"] = m.id
            if m.id in ROPE_SPOTS:
                info["rope"] = True
            if m.id == GROWN_WHEAT:
                info["wheat"] = True
                continue                  # blocking only until cut
            if m.id == JUNGLE_GRASS:
                info["grass"] = True
                continue                  # blocking only until cut
            if m.id in STONE_PILES:
                info["dig"] = True        # a shovel opens a hole: a way down
            if m.id in MUD and m.attrs.get("action_id") == PICK_SPOT:
                info["pick"] = True       # a pick opens a hole in it: a way down (and a floor to walk until then)
            if m.attrs.get("teleport"):
                info["teleport"] = tuple(m.attrs["teleport"])
            if m.attrs.get("action_id") in SCRIPTED_TELEPORTS:
                info["teleport"] = SCRIPTED_TELEPORTS[m.attrs["action_id"]]
            if t.flags & HAS_HEIGHT and m is not tile.items[0]:
                high.append(m)
            if t.flags & BLOCK_SOLID:
                blocked = True
                if t.flags & MOVEABLE and m is not tile.items[0] and not m.attrs:
                    pushable.append(m.id)     # a barrel in the way: push it aside and walk on
                else:
                    fixed = True
        if len(high) >= 2 and not info:
            # Game::internalMoveCreature: a step up by 2 or more (two chairs, stacked boxes) is refused; if they
            # can all be moved, pushing them aside clears the way
            movable = [m.id for m in high if items.by_server[m.id].flags & MOVEABLE and not m.attrs]
            if len(movable) == len(high) and not fixed:
                return SPECIAL, {"push": sorted(set(movable + pushable))}
            return BLOCKED, None
        if blocked and not fixed and pushable and not info:
            return SPECIAL, {"push": pushable}
        if info.get("down") or info.get("up") or "teleport" in info:
            # you walk onto it (and are moved) - unless something fixed blocks it: a magic wall on a trapdoor (the
            # Banshee Quest's, until its switch) is a wall
            info["stand"] = not (blocked and fixed)
            return SPECIAL, info
        if (info.get("wheat") or info.get("grass")) and blocked and fixed:
            return BLOCKED, None          # a stone under the grass: cutting it opens nothing
        if "door" in info or info.get("wheat") or info.get("grass") or info.get("dig"):
            return SPECIAL, info          # blocking / a way down only with the right tool
        if info:                          # ladder / rope spot / pick spot: used from next to it
            info["stand"] = not blocked
            return SPECIAL, info
        return (BLOCKED if blocked else WALK), None

"""Reader for OTBM map files (the format Remere's Map Editor saves), enough to inspect tiles and items.

    for tile in read_tiles(path, area=((x1, y1, z1), (x2, y2, z2))):
        tile.pos, tile.items -> [MapItem(id, attrs)]
"""
import struct
from dataclasses import dataclass, field
from pathlib import Path

NODE_START, NODE_END, ESCAPE = 0xFE, 0xFF, 0xFD

OTBM_MAP_DATA = 2
OTBM_TILE_AREA = 4
OTBM_TILE = 5
OTBM_ITEM = 6
OTBM_TOWNS = 12
OTBM_TOWN = 13
OTBM_HOUSETILE = 14

ATTR_TILE_FLAGS = 3
ATTR_ACTION_ID = 4
ATTR_UNIQUE_ID = 5
ATTR_TEXT = 6
ATTR_DESC = 7
ATTR_TELE_DEST = 8
ATTR_ITEM = 9
ATTR_DEPOT_ID = 10
ATTR_RUNE_CHARGES = 12
ATTR_HOUSEDOORID = 14
ATTR_COUNT = 15
ATTR_DURATION = 16
ATTR_DECAYING_STATE = 17
ATTR_WRITTENDATE = 18
ATTR_WRITTENBY = 19
ATTR_SLEEPERGUID = 20
ATTR_SLEEPSTART = 21


@dataclass
class MapItem:
    id: int
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)   # container contents

    @property
    def teleport_to(self):
        return self.attrs.get("teleport")


@dataclass
class Tile:
    pos: tuple
    items: list
    house_id: int = 0
    flags: int = 0


@dataclass
class Town:
    id: int
    name: str
    temple: tuple


def _parse_nodes(raw: bytes):
    """Yield ('start', type, props_bytes) / ('end',) events; props are unescaped."""
    i, n = 4, len(raw)
    stack = []
    while i < n:
        b = raw[i]
        if b == NODE_START:
            if stack and stack[-1][1] is not None:
                yield ("start", stack[-1][0], bytes(stack[-1][1]))
                stack[-1][1] = None
            stack.append([raw[i + 1], bytearray()])
            i += 2
        elif b == NODE_END:
            node = stack.pop()
            if node[1] is not None:
                yield ("start", node[0], bytes(node[1]))
            yield ("end",)
            i += 1
        else:
            if b == ESCAPE:
                i += 1
            stack[-1][1].append(raw[i])
            i += 1


def _item_attrs(props: bytes, p: int) -> dict:
    attrs = {}
    while p < len(props):
        a = props[p]
        p += 1
        if a == ATTR_TELE_DEST:
            attrs["teleport"] = struct.unpack_from("<HHB", props, p)
            p += 5
        elif a in (ATTR_ACTION_ID, ATTR_UNIQUE_ID, ATTR_DEPOT_ID):
            attrs[{ATTR_ACTION_ID: "action_id", ATTR_UNIQUE_ID: "unique_id", ATTR_DEPOT_ID: "depot_id"}[a]] = \
                struct.unpack_from("<H", props, p)[0]
            p += 2
        elif a in (ATTR_COUNT, ATTR_RUNE_CHARGES, ATTR_HOUSEDOORID, ATTR_DECAYING_STATE):
            attrs[{ATTR_COUNT: "count", ATTR_RUNE_CHARGES: "charges", ATTR_HOUSEDOORID: "house_door",
                   ATTR_DECAYING_STATE: "decaying"}[a]] = props[p]
            p += 1
        elif a in (ATTR_TEXT, ATTR_DESC, ATTR_WRITTENBY):
            ln = struct.unpack_from("<H", props, p)[0]
            attrs[{ATTR_TEXT: "text", ATTR_DESC: "description", ATTR_WRITTENBY: "written_by"}[a]] = \
                props[p + 2:p + 2 + ln].decode("latin-1")
            p += 2 + ln
        elif a in (ATTR_DURATION, ATTR_WRITTENDATE, ATTR_SLEEPERGUID, ATTR_SLEEPSTART):
            p += 4
        else:
            attrs.setdefault("unknown", []).append(a)
            break
    return attrs


def _in_area(pos, area):
    if area is None:
        return True
    (x1, y1, z1), (x2, y2, z2) = area
    return x1 <= pos[0] <= x2 and y1 <= pos[1] <= y2 and z1 <= pos[2] <= z2


def read_tiles(path: Path, area=None):
    """Yield every Tile (optionally only those inside area = ((x1,y1,z1),(x2,y2,z2)))."""
    base = (0, 0, 0)
    tile = None
    item_stack = []            # items being built (for nested container items)
    for ev in _parse_nodes(Path(path).read_bytes()):
        if ev[0] == "end":
            if item_stack:
                item = item_stack.pop()
                (item_stack[-1].children if item_stack else tile.items).append(item) if tile else None
            elif tile is not None:
                if _in_area(tile.pos, area):
                    yield tile
                tile = None
            continue
        _, ntype, props = ev
        if ntype == OTBM_TILE_AREA:
            base = struct.unpack_from("<HHB", props, 0)
        elif ntype in (OTBM_TILE, OTBM_HOUSETILE):
            pos = (base[0] + props[0], base[1] + props[1], base[2])
            tile = Tile(pos, [])
            p = 2
            if ntype == OTBM_HOUSETILE:
                tile.house_id = struct.unpack_from("<I", props, p)[0]
                p += 4
            while p < len(props):
                a = props[p]
                p += 1
                if a == ATTR_TILE_FLAGS:
                    tile.flags = struct.unpack_from("<I", props, p)[0]
                    p += 4
                elif a == ATTR_ITEM:
                    tile.items.append(MapItem(struct.unpack_from("<H", props, p)[0]))
                    p += 2
                else:
                    break
        elif ntype == OTBM_ITEM and tile is not None:
            item_stack.append(MapItem(struct.unpack_from("<H", props, 0)[0], _item_attrs(props, 2)))


def read_towns(path: Path) -> list[Town]:
    towns = []
    for ev in _parse_nodes(Path(path).read_bytes()):
        if ev[0] == "start" and ev[1] == OTBM_TOWN:
            props = ev[2]
            tid = struct.unpack_from("<I", props, 0)[0]
            ln = struct.unpack_from("<H", props, 4)[0]
            name = props[6:6 + ln].decode("latin-1")
            temple = struct.unpack_from("<HHB", props, 6 + ln)
            towns.append(Town(tid, name, temple))
    return towns

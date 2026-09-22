"""Item metadata from the server's items.otb / items.xml.

The client needs to know, per client item id:
  - whether the id is followed by a count byte on the wire (stackable, fluid container, splash)
  - where it goes in a tile's stack (ground / always-on-top with its top order / normal)
"""
import re
import struct
from dataclasses import dataclass
from pathlib import Path

GROUP_GROUND = 1
GROUP_CONTAINER = 2
GROUP_SPLASH = 11
GROUP_FLUID = 12

FLAG_STACKABLE = 128
FLAG_ALWAYSONTOP = 8192

ATTR_SERVERID = 0x10
ATTR_CLIENTID = 0x11
ATTR_SPEED = 0x14
ATTR_TOPORDER = 0x2B


@dataclass
class ItemType:
    server_id: int
    client_id: int
    group: int
    flags: int
    top_order: int = 0
    name: str = ""
    speed: int = 0          # ground speed: step duration = 1000 * speed / creature speed

    @property
    def has_count(self) -> bool:
        return bool(self.flags & FLAG_STACKABLE) or self.group in (GROUP_SPLASH, GROUP_FLUID)

    @property
    def is_ground(self) -> bool:
        return self.group == GROUP_GROUND

    @property
    def always_on_top(self) -> bool:
        return bool(self.flags & FLAG_ALWAYSONTOP)

    @property
    def is_container(self) -> bool:
        return self.group == GROUP_CONTAINER


def _read_nodes(raw: bytes):
    """Yield (depth, payload) for each node of an OTB node tree (0xFE start, 0xFF end, 0xFD escape)."""
    depth = 0
    cur = None
    i = 4  # 4-byte file identifier
    while i < len(raw):
        b = raw[i]
        if b == 0xFD:
            i += 1
            cur.append(raw[i])
        elif b == 0xFE:
            if cur is not None:
                yield depth, bytes(cur)
            depth += 1
            cur = bytearray()
        elif b == 0xFF:
            if cur is not None:
                yield depth, bytes(cur)
                cur = None
            depth -= 1
        else:
            cur.append(b)
        i += 1


class Items:
    def __init__(self, data_dir: Path):
        self.by_client: dict[int, ItemType] = {}
        self.by_server: dict[int, ItemType] = {}
        self._load_otb(Path(data_dir) / "items" / "items.otb")
        self._load_names(Path(data_dir) / "items" / "items.xml")

    def _load_otb(self, path: Path):
        for depth, node in _read_nodes(path.read_bytes()):
            if depth != 2 or len(node) < 5:
                continue
            group = node[0]
            flags = struct.unpack_from("<I", node, 1)[0]
            p = 5
            sid = cid = None
            top_order = speed = 0
            while p + 3 <= len(node):
                attr = node[p]
                length = struct.unpack_from("<H", node, p + 1)[0]
                p += 3
                if attr == ATTR_SERVERID:
                    sid = struct.unpack_from("<H", node, p)[0]
                elif attr == ATTR_CLIENTID:
                    cid = struct.unpack_from("<H", node, p)[0]
                elif attr == ATTR_TOPORDER:
                    top_order = node[p]
                elif attr == ATTR_SPEED:
                    speed = struct.unpack_from("<H", node, p)[0]
                p += length
            if sid is None or cid is None:
                continue
            it = ItemType(sid, cid, group, flags, top_order, speed=speed)
            self.by_server[sid] = it
            self.by_client.setdefault(cid, it)

    def _load_names(self, path: Path):
        text = path.read_text(encoding="latin-1")
        for m in re.finditer(r'<item\s+id="(\d+)"[^>]*?name="([^"]*)"', text):
            it = self.by_server.get(int(m.group(1)))
            if it:
                it.name = m.group(2)
        for m in re.finditer(r'<item\s+fromid="(\d+)"\s+toid="(\d+)"[^>]*?name="([^"]*)"', text):
            for sid in range(int(m.group(1)), int(m.group(2)) + 1):
                it = self.by_server.get(sid)
                if it and not it.name:
                    it.name = m.group(3)

    def client(self, client_id: int) -> ItemType:
        it = self.by_client.get(client_id)
        if it is None:
            # Unknown ids are treated as plain items; better than desyncing silently
            it = ItemType(client_id, client_id, 0, 0)
        return it

    def name(self, server_id: int) -> str:
        it = self.by_server.get(server_id)
        return it.name if it else f"item#{server_id}"

    def id_by_name(self, name: str) -> int:
        name = name.lower()
        for sid, it in self.by_server.items():
            if it.name.lower() == name:
                return sid
        raise KeyError(f"no item named {name!r}")

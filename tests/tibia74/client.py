"""Headless Tibia 7.4 game client for automated tests.

Mirrors Avesta's ProtocolGame writers (server/src/protocolgame.cpp) byte for byte. A background
thread parses every server packet and keeps a model of what a real client would know: our position,
stats, skills, inventory, open containers, visible tiles and creatures, and all messages.
Tests act through methods (walk, say, attack, use...) and assert with wait_for(...).
"""
import socket
import threading
import time
from dataclasses import dataclass, field

from .items import Items
from .net import Reader, Writer

NORTH, EAST, SOUTH, WEST = 0, 1, 2, 3
NORTHEAST, SOUTHEAST, SOUTHWEST, NORTHWEST = 4, 5, 6, 7
_DIR_DELTA = {NORTH: (0, -1), EAST: (1, 0), SOUTH: (0, 1), WEST: (-1, 0),
              NORTHEAST: (1, -1), SOUTHEAST: (1, 1), SOUTHWEST: (-1, 1), NORTHWEST: (-1, -1)}
_WALK_OPCODE = {NORTH: 0x65, EAST: 0x66, SOUTH: 0x67, WEST: 0x68,
                NORTHEAST: 0x6A, SOUTHEAST: 0x6B, SOUTHWEST: 0x6C, NORTHWEST: 0x6D}

SPEAK_SAY = 1

SLOT_NAMES = {1: "head", 2: "necklace", 3: "backpack", 4: "armor", 5: "right", 6: "left",
              7: "legs", 8: "feet", 9: "ring", 10: "ammo"}

MAX_Z = 15


class ProtocolError(Exception):
    pass


@dataclass
class Item:
    client_id: int
    count: int = 1
    name: str = ""

    def __repr__(self):
        c = f" x{self.count}" if self.count != 1 else ""
        return f"<{self.name or 'item'} #{self.client_id}{c}>"


@dataclass
class Creature:
    id: int
    name: str
    health: int = 100          # percent
    direction: int = 0
    pos: tuple = None           # None when not on any known tile
    speed: int = 0
    outfit: tuple = ()
    skull: int = 0              # 0 none, 1 yellow, 2 green, 3 white, 4 red

    def __repr__(self):
        return f"<{self.name} #{self.id} {self.health}% at {self.pos}>"


@dataclass
class Container:
    cid: int
    item_id: int
    name: str
    capacity: int
    items: list = field(default_factory=list)


@dataclass
class Stats:
    health: int = 0
    max_health: int = 0
    capacity: int = 0
    experience: int = 0
    level: int = 0
    level_percent: int = 0
    mana: int = 0
    max_mana: int = 0
    magic_level: int = 0
    magic_level_percent: int = 0


class GameClient:
    def __init__(self, items: Items, host: str = "127.0.0.1", port: int = 7171):
        self.items = items
        self.host, self.port = host, port
        self.sock = None
        self.player_id = None
        self.pos = None
        self.stats = Stats()
        self.icons = 0                                 # condition icons (0xA2): 1 = poisoned
        self.skills = {}
        self.inventory: dict[int, Item] = {}
        self.containers: dict[int, Container] = {}
        self.creatures: dict[int, Creature] = {}
        self.tiles: dict[tuple, list] = {}      # pos -> stack of Item | Creature(id reference)
        self.text_messages: list[tuple] = []    # (class, text)
        self.speech: list[tuple] = []           # (name, type, text)
        self.animated_texts: list[tuple] = []   # (pos, color, text)
        self.effects: list[tuple] = []          # (pos, type)
        self.removed_creatures: list[int] = []  # ids removed from view, in order
        self.cancel_walks = 0
        self.disconnect_reason = None
        self.errors: list[str] = []
        self.connected = False
        self._lock = threading.Condition()
        self._thread = None
        self.center = None                      # camera centre, moved by map slices like the real client

    # ================================================================ connection
    def login(self, account: int, password: str, character: str, timeout: float = 10.0):
        self.sock = socket.create_connection((self.host, self.port), timeout=timeout)
        self.sock.settimeout(None)
        w = Writer().u8(0x0A).u16(2).u16(740).u8(0).u32(account).string(character).string(password)
        self.sock.sendall(w.packet())
        self.connected = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True, name=f"client-{character}")
        self._thread.start()
        if not self.wait_for(lambda: self.pos is not None or not self.connected, timeout):
            raise TimeoutError("no map received after login")
        if self.pos is None:
            raise ProtocolError(f"login failed: {self.disconnect_reason}")
        return self

    def logout(self):
        if self.connected:
            try:
                self._send(Writer().u8(0x14))
                self.wait_for(lambda: not self.connected, 3)
            except OSError:
                pass
        self.close()

    def close(self):
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

    def _send(self, w: Writer):
        self.sock.sendall(w.packet())

    def _recv_exact(self, n: int) -> bytes:
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError("connection closed")
            buf += chunk
        return buf

    def _read_loop(self):
        try:
            while self.connected:
                size = int.from_bytes(self._recv_exact(2), "little")
                data = self._recv_exact(size)
                with self._lock:
                    try:
                        self._parse_packet(Reader(data))
                    except Exception as e:  # keep going; record for the test to see
                        self.errors.append(f"{type(e).__name__}: {e} (packet {data[:24].hex()}...)")
                    self._lock.notify_all()
        except (ConnectionError, OSError):
            pass
        finally:
            with self._lock:
                self.connected = False
                self._lock.notify_all()

    # ================================================================ waiting
    def wait_for(self, predicate, timeout: float = 5.0) -> bool:
        """Block until predicate() is truthy (checked after each packet) or timeout. Returns the result."""
        deadline = time.time() + timeout
        with self._lock:
            while True:
                result = predicate()
                if result:
                    return result
                remaining = deadline - time.time()
                if remaining <= 0:
                    return result
                self._lock.wait(min(remaining, 0.25))

    def sleep(self, seconds: float):
        time.sleep(seconds)

    # ================================================================ actions
    def say(self, text: str):
        self._send(Writer().u8(0x96).u8(SPEAK_SAY).string(text))

    def talk(self, *lines: str, npc: str = None, wait: float = 2.5) -> list[str]:
        """Say each line and return everything NPCs (or `npc`) said in reply, in order."""
        replies = []
        for line in lines:
            start = len(self.speech)
            self.say(line)
            self.wait_for(lambda: any(n != self.name for n, _, _ in self.speech[start:]
                                      if npc is None or n == npc), wait)
            time.sleep(0.3)
            with self._lock:
                replies += [t for n, _, t in self.speech[start:]
                            if n != self.name and (npc is None or n == npc)]
        return replies

    def step(self, direction: int, timeout: float = 3.0) -> bool:
        """One step. True if we moved, False if the server cancelled it."""
        before, cancels = self.pos, self.cancel_walks
        self._send(Writer().u8(_WALK_OPCODE[direction]))
        return bool(self.wait_for(lambda: self.pos != before or self.cancel_walks != cancels, timeout)
                    and self.pos != before)

    def walk_to(self, target: tuple, max_steps: int = 200) -> bool:
        """Greedy walk (same floor) with simple sidestepping. Good enough for short test paths."""
        tx, ty, tz = target
        for _ in range(max_steps):
            x, y, z = self.pos
            if (x, y) == (tx, ty):
                return True
            dx, dy = (tx > x) - (tx < x), (ty > y) - (ty < y)
            options = [d for d, delta in _DIR_DELTA.items() if delta == (dx, dy)]
            options += [d for d, delta in _DIR_DELTA.items()
                        if delta in ((dx, 0), (0, dy)) and delta != (0, 0)]
            options += [d for d, delta in _DIR_DELTA.items()
                        if (delta[0] == dx and dx) or (delta[1] == dy and dy)]
            if not any(self.step(d) for d in dict.fromkeys(options)):
                return False
        return self.pos[:2] == (tx, ty)

    def auto_walk(self, directions: list):
        """Walk a whole path in one request (0x64), like clicking on the map in the real client: the server steps
        it at the character's speed. The 7.4 client numbers directions 1 E, 2 NE, 3 N, 4 NW, 5 W, 6 SW, 7 S, 8 SE."""
        raw = {EAST: 1, NORTHEAST: 2, NORTH: 3, NORTHWEST: 4, WEST: 5, SOUTHWEST: 6, SOUTH: 7, SOUTHEAST: 8}
        w = Writer().u8(0x64).u8(len(directions))
        for d in directions:
            w.u8(raw[d])
        self._send(w)

    def stop_auto_walk(self):
        self._send(Writer().u8(0x69))

    def turn(self, direction: int):
        """Turn without stepping (0x6F-0x72, like ctrl + arrow): direction spells go the way you face."""
        self._send(Writer().u8(0x6F + direction))

    def set_fight_modes(self, fight: int = 1, chase: int = 1, safe: int = 1):
        """fight 1=offensive 2=balanced 3=defensive; chase 1 = follow the target."""
        self._send(Writer().u8(0xA0).u8(fight).u8(chase).u8(safe))

    def attack(self, creature_id: int):
        self._send(Writer().u8(0xA1).u32(creature_id))

    def follow(self, creature_id: int):
        self._send(Writer().u8(0xA2).u32(creature_id))

    def look(self, pos: tuple, client_id: int, stackpos: int):
        self._send(Writer().u8(0x8C).position(pos).u16(client_id).u8(stackpos))

    def use_item(self, pos: tuple, client_id: int, stackpos: int, index: int = 0):
        self._send(Writer().u8(0x82).position(pos).u16(client_id).u8(stackpos).u8(index))

    def use_item_with(self, pos: tuple, client_id: int, stackpos: int,
                      to_pos: tuple, to_client_id: int, to_stackpos: int):
        """'Use with' (0x83): a rune on a target, a fluid on yourself (to_client_id 0x63 = a creature)."""
        self._send(Writer().u8(0x83).position(pos).u16(client_id).u8(stackpos)
                   .position(to_pos).u16(to_client_id).u8(to_stackpos))

    def move_item(self, from_pos: tuple, client_id: int, stackpos: int, to_pos: tuple, count: int = 1):
        self._send(Writer().u8(0x78).position(from_pos).u16(client_id).u8(stackpos)
                   .position(to_pos).u8(count))

    def open_container(self, slot: int, timeout: float = 3.0):
        """Open the container worn in `slot` (like right-clicking it) and return it once known."""
        item = self.inventory.get(slot)
        if item is None:
            return None
        known = set(self.containers)
        self.use_item(self.inventory_pos(slot), item.client_id, 0)
        return self.wait_for(lambda: next((self.containers[c] for c in self.containers if c not in known), None),
                             timeout)

    def slot_of(self, item_name: str):
        """Inventory slot holding an item with this name, or None."""
        return next((s for s, i in self.inventory.items() if i.name == item_name), None)

    @staticmethod
    def inventory_pos(slot: int) -> tuple:
        return (0xFFFF, slot, 0)

    @staticmethod
    def container_pos(cid: int, slot: int) -> tuple:
        return (0xFFFF, 0x40 | cid, slot)

    # ================================================================ queries
    @property
    def name(self):
        me = self.creatures.get(self.player_id)
        return me.name if me else None

    def creatures_named(self, name: str) -> list[Creature]:
        name = name.lower()
        return [c for c in self.creatures.values() if c.name.lower() == name and c.pos is not None]

    def nearest(self, name: str):
        cands = self.creatures_named(name)
        if not cands or not self.pos:
            return None
        return min(cands, key=lambda c: max(abs(c.pos[0] - self.pos[0]), abs(c.pos[1] - self.pos[1]))
                   + (100 if c.pos[2] != self.pos[2] else 0))

    def inventory_names(self) -> dict[str, str]:
        return {SLOT_NAMES[s]: i.name for s, i in self.inventory.items()}

    def all_items(self) -> list[Item]:
        """Everything worn plus everything in open containers."""
        out = list(self.inventory.values())
        for c in self.containers.values():
            out += c.items
        return out

    def tile_items(self, pos: tuple) -> list[Item]:
        return [t for t in self.tiles.get(tuple(pos), []) if isinstance(t, Item)]

    def messages(self, contains: str = "") -> list[str]:
        return [t for _, t in self.text_messages if contains.lower() in t.lower()]

    # ================================================================ parsing
    def _parse_packet(self, r: Reader):
        while r.remaining() > 0:
            op = r.u8()
            handler = _HANDLERS.get(op)
            if handler is None:
                raise ProtocolError(f"unknown opcode 0x{op:02X} at {r.pos - 1}")
            handler(self, r)

    # --- things -----------------------------------------------------------
    def _read_item(self, r: Reader) -> Item:
        cid = r.u16()
        it = self.items.client(cid)
        count = r.u8() if it.has_count else 1
        return Item(cid, count, it.name)

    def _read_outfit(self, r: Reader) -> tuple:
        look = r.u8()
        if look != 0:
            return (look, r.u8(), r.u8(), r.u8(), r.u8())
        return (0, r.u16())

    def _read_creature(self, r: Reader, kind: int) -> Creature:
        if kind == 0x62:
            cid = r.u32()
            c = self.creatures.get(cid) or Creature(cid, "?")
        elif kind == 0x61:
            removed = r.u32()
            if removed:
                self.creatures.pop(removed, None)
            cid = r.u32()
            c = Creature(cid, r.string())
        else:
            raise ProtocolError(f"bad creature marker 0x{kind:04X}")
        c.health = r.u8()
        c.direction = r.u8()
        c.outfit = self._read_outfit(r)
        r.u8(); r.u8()          # light level, color
        c.speed = r.u16()
        c.skull = r.u8()
        r.u8()                  # party shield
        self.creatures[cid] = c
        return c

    def _read_thing(self, r: Reader):
        marker = r.peek_u16()
        if marker in (0x61, 0x62):
            r.u16()
            return self._read_creature(r, marker)
        return self._read_item(r)

    # --- tiles ------------------------------------------------------------
    def _set_tile(self, pos: tuple, things: list):
        old = self.tiles.get(pos)
        if old:
            for t in old:
                if isinstance(t, Creature) and t.pos == pos:
                    t.pos = None
        stack = []
        for t in things:
            if isinstance(t, Creature):
                t.pos = pos
                if t.id == self.player_id:
                    self.pos = pos
            stack.append(t)
        self.tiles[pos] = stack

    def _read_tile_things(self, r: Reader) -> tuple[list, int]:
        things = []
        while True:
            if r.peek_u16() >= 0xFF00:
                return things, r.u16() & 0xFF
            things.append(self._read_thing(r))

    def _read_floors(self, r: Reader, floors: list, x: int, y: int, w: int, h: int):
        """floors = [(z, offset)]; tiles are at (x + nx + offset, y + ny + offset, z)."""
        skip = 0
        for z, offset in floors:
            for nx in range(w):
                for ny in range(h):
                    pos = (x + nx + offset, y + ny + offset, z)
                    if skip == 0:
                        things, skip = self._read_tile_things(r)
                        self._set_tile(pos, things)
                    else:
                        skip -= 1
                        self.tiles.pop(pos, None)

    def _map_floors(self, z: int) -> list:
        if z > 7:
            return [(nz, z - nz) for nz in range(z - 2, min(MAX_Z, z + 2) + 1)]
        return [(nz, z - nz) for nz in range(7, -1, -1)]

    def _read_map_area(self, r: Reader, x: int, y: int, z: int, w: int, h: int):
        self._read_floors(r, self._map_floors(z), x, y, w, h)

    def _insert_thing(self, pos: tuple, thing):
        stack = self.tiles.setdefault(pos, [])
        if isinstance(thing, Creature):
            thing.pos = pos
            if thing.id == self.player_id:
                self.pos = pos
            i = 0
            while i < len(stack) and isinstance(stack[i], Item) and (
                    self.items.client(stack[i].client_id).is_ground
                    or self.items.client(stack[i].client_id).always_on_top):
                i += 1
            stack.insert(i, thing)
            return
        it = self.items.client(thing.client_id)
        if it.is_ground:
            stack.insert(0, thing)
        elif it.always_on_top:
            i = 0
            while i < len(stack) and isinstance(stack[i], Item):
                other = self.items.client(stack[i].client_id)
                if not (other.is_ground or (other.always_on_top and other.top_order <= it.top_order)):
                    break
                i += 1
            stack.insert(i, thing)
        else:
            i = 0
            while i < len(stack) and (isinstance(stack[i], Creature)
                                      or self.items.client(stack[i].client_id).is_ground
                                      or self.items.client(stack[i].client_id).always_on_top):
                i += 1
            stack.insert(i, thing)

    def _remove_at(self, pos: tuple, stackpos: int):
        stack = self.tiles.get(pos)
        if not stack or stackpos >= len(stack):
            return None
        thing = stack.pop(stackpos)
        if isinstance(thing, Creature) and thing.pos == pos:
            thing.pos = None
        return thing


# ==================================================================== handlers
def _h_login(c: GameClient, r: Reader):
    c.player_id = r.u32()
    r.u16()  # beat
    r.u8()   # can report bugs


def _h_gm_actions(c, r):
    r.skip(32)


def _h_disconnect(c, r):
    c.disconnect_reason = r.string()
    c.connected = False


def _h_waitlist(c, r):
    c.disconnect_reason = r.string()
    r.u8()
    c.connected = False


def _h_ping(c, r):
    try:
        c._send(Writer().u8(0x1E))
    except OSError:
        pass


def _h_map(c, r):
    c.pos = r.position()
    c.center = c.pos
    x, y, z = c.pos
    c._read_map_area(r, x - 8, y - 6, z, 18, 14)


def _h_slice(c: GameClient, r: Reader, op: int):
    # Same as the real client: shift the camera one step, then read the newly visible row/column
    x, y, z = c.center
    if op == 0x65:
        y -= 1
        c._read_map_area(r, x - 8, y - 6, z, 18, 1)
    elif op == 0x66:
        x += 1
        c._read_map_area(r, x + 9, y - 6, z, 1, 14)
    elif op == 0x67:
        y += 1
        c._read_map_area(r, x - 8, y + 7, z, 18, 1)
    else:
        x -= 1
        c._read_map_area(r, x - 8, y - 6, z, 1, 14)
    c.center = (x, y, z)


def _h_update_tile(c, r):
    pos = r.position()
    if r.peek_u16() == 0xFF01:
        r.u16()
        c._set_tile(pos, [])
        return
    things, _ = c._read_tile_things(r)
    c._set_tile(pos, things)


def _h_add_thing(c, r):
    pos = r.position()
    c._insert_thing(pos, c._read_thing(r))


def _h_transform_thing(c, r):
    pos = r.position()
    stackpos = r.u8()
    if r.peek_u16() == 0x63:
        r.u16()
        cid = r.u32()
        d = r.u8()
        if cid in c.creatures:
            c.creatures[cid].direction = d
        return
    item = c._read_item(r)
    stack = c.tiles.get(pos)
    if stack and stackpos < len(stack):
        stack[stackpos] = item


def _h_remove_thing(c, r):
    pos = r.position()
    thing = c._remove_at(pos, r.u8())
    if isinstance(thing, Creature):
        c.removed_creatures.append(thing.id)


def _h_move_creature(c, r):
    old = r.position()
    stackpos = r.u8()
    new = r.position()
    thing = c._remove_at(old, stackpos)
    if not isinstance(thing, Creature):
        # We didn't track that tile precisely; find the creature by position as a fallback
        thing = next((cr for cr in c.creatures.values() if cr.pos == old), None)
    if thing is None:
        return
    c._insert_thing(new, thing)


def _h_floor_up(c, r):
    x, y, z = c.center
    z -= 1
    if z == 7:
        c._read_floors(r, [(nz, 8 - nz) for nz in range(5, -1, -1)], x - 8, y - 6, 18, 14)
    elif z > 7:
        c._read_floors(r, [(z - 2, 3)], x - 8, y - 6, 18, 14)
    c.center = (x + 1, y + 1, z)


def _h_floor_down(c, r):
    x, y, z = c.center
    z += 1
    if z == 8:
        c._read_floors(r, [(z, -1), (z + 1, -2), (z + 2, -3)], x - 8, y - 6, 18, 14)
    elif 8 < z < 14:
        c._read_floors(r, [(z + 2, -3)], x - 8, y - 6, 18, 14)
    c.center = (x - 1, y - 1, z)


def _h_open_container(c, r):
    cid = r.u8()
    item_id = r.u16()
    name = r.string()
    cap = r.u8()
    r.u8()  # has parent
    n = r.u8()
    c.containers[cid] = Container(cid, item_id, name, cap, [c._read_item(r) for _ in range(n)])


def _h_close_container(c, r):
    c.containers.pop(r.u8(), None)


def _h_container_add(c, r):
    cid = r.u8()
    item = c._read_item(r)
    if cid in c.containers:
        c.containers[cid].items.insert(0, item)


def _h_container_update(c, r):
    cid, slot = r.u8(), r.u8()
    item = c._read_item(r)
    cont = c.containers.get(cid)
    if cont and slot < len(cont.items):
        cont.items[slot] = item


def _h_container_remove(c, r):
    cid, slot = r.u8(), r.u8()
    cont = c.containers.get(cid)
    if cont and slot < len(cont.items):
        cont.items.pop(slot)


def _h_inventory_set(c, r):
    slot = r.u8()
    c.inventory[slot] = c._read_item(r)


def _h_inventory_clear(c, r):
    c.inventory.pop(r.u8(), None)


def _h_trade(c, r):
    r.string()
    for _ in range(r.u8()):
        c._read_item(r)


def _h_world_light(c, r):
    r.u8(); r.u8()


def _h_magic_effect(c, r):
    c.effects.append((r.position(), r.u8()))


def _h_animated_text(c, r):
    c.animated_texts.append((r.position(), r.u8(), r.string()))


def _h_distance_shot(c, r):
    r.position(); r.position(); r.u8()


def _h_creature_square(c, r):
    r.u32(); r.u8()


def _h_creature_health(c, r):
    cid, hp = r.u32(), r.u8()
    if cid in c.creatures:
        c.creatures[cid].health = hp


def _h_creature_light(c, r):
    r.u32(); r.u8(); r.u8()


def _h_creature_outfit(c, r):
    cid = r.u32()
    outfit = c._read_outfit(r)
    if cid in c.creatures:
        c.creatures[cid].outfit = outfit


def _h_creature_speed(c, r):
    cid, speed = r.u32(), r.u16()
    if cid in c.creatures:
        c.creatures[cid].speed = speed


def _h_creature_skull(c, r):
    cid, skull = r.u32(), r.u8()
    if cid in c.creatures:
        c.creatures[cid].skull = skull


def _h_creature_u32_u8(c, r):
    r.u32(); r.u8()


def _h_text_window(c, r):
    r.u32(); r.u16(); r.u16(); c.text_messages.append((0x96, r.string()))


def _h_house_window(c, r):
    r.u8(); r.u32(); r.string()


def _h_stats(c, r):
    s = c.stats
    s.health, s.max_health, s.capacity = r.u16(), r.u16(), r.u16()
    s.experience = r.u32()
    s.level, s.level_percent = r.u8(), r.u8()
    s.mana, s.max_mana = r.u16(), r.u16()
    s.magic_level, s.magic_level_percent = r.u8(), r.u8()


def _h_skills(c, r):
    for name in ("fist", "club", "sword", "axe", "distance", "shielding", "fishing"):
        c.skills[name] = (r.u8(), r.u8())


def _h_icons(c, r):
    c.icons = r.u8()             # 1 poisoned, 2 burning, 4 electrified, 8 drunk, 16 mana shield, 32 paralysed, 64 haste


def _h_nothing(c, r):
    pass


def _h_speak(c, r):
    name = r.string()
    kind = r.u8()
    if kind in (1, 2, 3, 0x10, 0x11):
        r.position()
    elif kind in (5, 0x0A, 0x0E, 0x0C):
        r.u16()
    elif kind == 6:
        r.u32()
    c.speech.append((name, kind, r.string()))


def _h_channels(c, r):
    for _ in range(r.u8()):
        r.u16(); r.string()


def _h_u16_string(c, r):
    r.u16(); r.string()


def _h_string(c, r):
    r.string()


def _h_u16(c, r):
    r.u16()


def _h_text_message(c, r):
    c.text_messages.append((r.u8(), r.string()))


def _h_cancel_walk(c, r):
    r.u8()
    c.cancel_walks += 1


def _h_outfit_window(c, r):
    c._read_outfit(r); r.u8(); r.u8()


def _h_vip(c, r):
    r.u32(); r.string(); r.u8()


def _h_u32(c, r):
    r.u32()


_HANDLERS = {
    0x0A: _h_login, 0x0B: _h_gm_actions, 0x14: _h_disconnect, 0x16: _h_waitlist, 0x1E: _h_ping,
    0x28: _h_nothing,
    0x64: _h_map,
    0x65: lambda c, r: _h_slice(c, r, 0x65), 0x66: lambda c, r: _h_slice(c, r, 0x66),
    0x67: lambda c, r: _h_slice(c, r, 0x67), 0x68: lambda c, r: _h_slice(c, r, 0x68),
    0x69: _h_update_tile, 0x6A: _h_add_thing, 0x6B: _h_transform_thing, 0x6C: _h_remove_thing,
    0x6D: _h_move_creature,
    0x6E: _h_open_container, 0x6F: _h_close_container, 0x70: _h_container_add,
    0x71: _h_container_update, 0x72: _h_container_remove,
    0x78: _h_inventory_set, 0x79: _h_inventory_clear,
    0x7D: _h_trade, 0x7E: _h_trade, 0x7F: _h_nothing,
    0x82: _h_world_light, 0x83: _h_magic_effect, 0x84: _h_animated_text, 0x85: _h_distance_shot,
    0x86: _h_creature_square, 0x8C: _h_creature_health, 0x8D: _h_creature_light,
    0x8E: _h_creature_outfit, 0x8F: _h_creature_speed, 0x90: _h_creature_skull,
    0x91: _h_creature_u32_u8,
    0x96: _h_text_window, 0x97: _h_house_window,
    0xA0: _h_stats, 0xA1: _h_skills, 0xA2: _h_icons, 0xA3: _h_nothing,
    0xAA: _h_speak, 0xAB: _h_channels, 0xAC: _h_u16_string, 0xAD: _h_string, 0xAE: _h_u16,
    0xAF: _h_string, 0xB0: _h_string, 0xB1: _h_nothing, 0xB2: _h_u16_string, 0xB3: _h_u16,
    0xB4: _h_text_message, 0xB5: _h_cancel_walk,
    0xBE: _h_floor_up, 0xBF: _h_floor_down,
    0xC8: _h_outfit_window, 0xD2: _h_vip, 0xD3: _h_u32, 0xD4: _h_u32,
}


def character_list(account: int, password: str, host: str = "127.0.0.1", port: int = 7171,
                   timeout: float = 10.0) -> dict:
    """The 7.4 login-server exchange (protocol 0x01): what the client shows before choosing a character.
    Returns {"error": text} or {"motd": text, "characters": [(name, world)], "premium_days": n}."""
    w = Writer().u8(0x01).u16(2).u16(740)
    w.buf += bytes(12)                                  # dat / spr / pic signatures, not checked
    w.u32(account).string(password)
    with socket.create_connection((host, port), timeout=timeout) as s:
        s.settimeout(timeout)
        s.sendall(w.packet())
        data = b""
        while True:                                     # the server closes the connection after replying
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
    if len(data) < 2:
        return {"error": "no reply"}
    r = Reader(data[2:2 + int.from_bytes(data[:2], "little")])
    out = {}
    while r.remaining() > 0:
        op = r.u8()
        if op == 0x0A:
            return {"error": r.string()}
        if op == 0x14:
            out["motd"] = r.string()
        elif op == 0x64:
            out["characters"] = []
            for _ in range(r.u8()):
                name, world = r.string(), r.string()
                r.u32(), r.u16()                        # world ip, port
                out["characters"].append((name, world))
            out["premium_days"] = r.u16()
        else:
            break
    return out

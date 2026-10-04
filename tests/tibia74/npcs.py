"""What each NPC says it does, read from server/data/npc - the spec the NPC tests check the server against.

NPCs come in three flavours and all three are read:
  - XML parameters for default.lua (Jiddo): keywords + keyword_replyN, shop_buyable, shop_sellable
  - Lua scripts: shopModule:addBuyableItem/addSellableItem(...) and keywordHandler:addKeyword(..., text = ...)
  - old OTServ <interaction> XML (no script): read only for its name; covered by hand-written tests
"""
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ShopItem:
    names: list            # what the player says after "buy"/"sell"; first one is used by the tests
    item_id: int
    price: int
    subtype: int = 0       # fluid type / charges for buyables, 0 = none
    real_name: str = ""    # the name the NPC uses in its replies


@dataclass
class Npc:
    name: str
    xml: Path
    script: str = ""       # "" for <interaction> NPCs
    positions: list = field(default_factory=list)  # every spawn of this NPC in the world's spawns file
    radii: list = field(default_factory=list)      # how far it may wander from each of them (the spawn's radius)
    keywords: dict = field(default_factory=dict)   # "job" -> reply
    buyable: list = field(default_factory=list)    # the player can buy these
    sellable: list = field(default_factory=list)   # the player can sell these

    @property
    def pos(self):
        return self.positions[0] if self.positions else None

    @property
    def radius(self):
        return self.radii[0] if self.radii else 0

    @property
    def is_interaction(self) -> bool:
        return not self.script


def _parse_shop_param(value: str, buy: bool) -> list:
    out = []
    for entry in filter(None, (e.strip() for e in value.split(";"))):
        parts = [p.strip() for p in entry.split(",")]
        name, item_id, price = parts[0], int(parts[1]), int(parts[2])
        subtype = int(parts[3]) if buy and len(parts) > 3 and parts[3] else 0
        out.append(ShopItem([name], item_id, price, subtype, name))
    return out


_LUA_STR = r"""(?:'((?:[^'\\]|\\.)*)'|"((?:[^"\\]|\\.)*)")"""
_LUA_SHOP = re.compile(r"add(Buyable|Sellable)Item\(\s*(\{[^}]*\}|nil)\s*,\s*(\d+)\s*,\s*(\d+)\s*"
                       r"(?:,\s*(\d+)\s*)?(?:,\s*" + _LUA_STR + r"\s*)?\)")
_LUA_KEYWORD = re.compile(r"addKeyword\(\s*\{([^}]*)\}\s*,\s*StdModule\.say\s*,\s*\{[^}]*?\btext\s*=\s*" + _LUA_STR)


def _lua_strings(text: str) -> list:
    return [a or b for a, b in re.findall(_LUA_STR, text)]


def _read_script(npc: Npc, script: Path):
    code = script.read_text(encoding="latin-1")
    code = re.sub(r"--\[\[.*?\]\]", "", code, flags=re.S)          # block comments
    code = re.sub(r"--[^\n]*", "", code)                             # line comments
    for kind, names, item_id, price, extra, s1, s2 in _LUA_SHOP.findall(code):
        real = s1 or s2
        names = _lua_strings(names) if names != "nil" else [real]
        item = ShopItem(names or [real], int(item_id), int(price), int(extra or 0) if kind == "Buyable" else 0,
                        real or (names[0] if names else ""))
        (npc.buyable if kind == "Buyable" else npc.sellable).append(item)
    for words, t1, t2 in _LUA_KEYWORD.findall(code):
        npc.keywords[" ".join(_lua_strings(words))] = t1 or t2


def load_npcs(server_dir: Path) -> dict:
    """name -> Npc for every NPC XML in server/data/npc, with spawn positions from the map's spawns file."""
    npc_dir = server_dir / "data" / "npc"
    npcs = {}
    for xml in sorted(npc_dir.glob("*.xml")):
        root = ET.fromstring(xml.read_text(encoding="latin-1"))
        if root.tag != "npc":
            continue
        npc = Npc(root.get("name"), xml, root.get("script") or "")
        params = {p.get("key"): p.get("value") or "" for p in root.iter("parameter")}
        if params.get("keywords"):
            words = [w for w in params["keywords"].split(";") if w]
            for i, word in enumerate(words, 1):
                reply = params.get(f"keyword_reply{i}")
                if reply is not None:
                    npc.keywords[word] = reply
        npc.buyable += _parse_shop_param(params.get("shop_buyable", ""), buy=True)
        npc.sellable += _parse_shop_param(params.get("shop_sellable", ""), buy=False)
        if npc.script and (npc_dir / "scripts" / npc.script).exists():
            _read_script(npc, npc_dir / "scripts" / npc.script)
        npcs[npc.name] = npc

    spawns = next((server_dir / "data" / "world").glob("*-spawns.xml"), None)
    if spawns:
        # a spawn names the NPC's file ("Baa'Leal" -> Baa'Leal.xml, the name the XML gives is "Baa'leal"); the server
        # finds the file case-insensitively (Windows)
        by_lower = {name.lower(): npc for name, npc in npcs.items()}
        for spawn in ET.fromstring(spawns.read_text(encoding="latin-1")).iter("spawn"):
            cx, cy = int(spawn.get("centerx")), int(spawn.get("centery"))
            for n in spawn.iter("npc"):
                if n.get("name").lower() in by_lower:
                    npc = by_lower[n.get("name").lower()]
                    npc.positions.append((cx + int(n.get("x")), cy + int(n.get("y")), int(n.get("z"))))
                    npc.radii.append(int(spawn.get("radius") or 0))
    return npcs


ROOKGAARD_X, ROOKGAARD_Y = (31900, 32200), (32120, 32300)


def rookgaard_pos(npc: Npc):
    """The NPC's spawn on Rookgaard, or None."""
    return next((p for p in npc.positions if ROOKGAARD_X[0] <= p[0] <= ROOKGAARD_X[1]
                 and ROOKGAARD_Y[0] <= p[1] <= ROOKGAARD_Y[1]), None)

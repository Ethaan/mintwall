"""NPC data checks that need no server: shop items exist, are what the NPC calls them, and can be obtained."""
import re

import pytest

from tibia74 import SERVER_DIR, Items
from tibia74.items import GROUP_FLUID

FLAG_PICKUPABLE = 1 << 5        # items.otb
from tibia74.npcs import load_npcs, rookgaard_pos

NPCS = load_npcs(SERVER_DIR)
ROOKGAARD_NPCS = sorted(n for n, npc in NPCS.items() if rookgaard_pos(npc))
SPAWNED = sorted(n for n, npc in NPCS.items() if npc.positions)
# NPCs whose shops still wait for a decision (task.md); test_shops.py skips them too
PENDING = set()
ITEMS = Items(SERVER_DIR / "data")


def _obtainable_ids() -> set:
    """Items a player can come by: monster corpses and loot, and anything an NPC sells."""
    ids = set()
    for xml in (SERVER_DIR / "data" / "monster").glob("*.xml"):
        text = xml.read_text(encoding="latin-1")
        ids |= {int(i) for i in re.findall(r'corpse="(\d+)"', text)}
        loot = re.search(r"<loot>(.*)</loot>", text, re.S)
        if loot:
            ids |= {int(i) for i in re.findall(r'<item id="(\d+)"', loot.group(1))}
    for npc in NPCS.values():
        ids |= {i.item_id for i in npc.buyable}
    return ids


OBTAINABLE = _obtainable_ids()


def _shop(npc):
    return [("buy", i) for i in npc.buyable] + [("sell", i) for i in npc.sellable]


def _said(item) -> str:
    return item.real_name or item.names[0]


def _name_ok(item, it) -> bool:
    # a fluid container sold filled ("mug of beer", "life fluid") is named after its contents; "apple" is a red apple,
    # "small book" a book, "pitchfork" a pitch fork
    said, name = (re.sub(r"[^a-z]", "", n.lower()) for n in (_said(item), it.name))
    return said in name or name in said or bool(item.subtype and it.group == GROUP_FLUID)


@pytest.mark.parametrize("name", [n for n in SPAWNED if n not in PENDING])
def test_shop_items_exist_and_match_their_names(name):
    bad = []
    for kind, item in _shop(NPCS[name]):
        it = ITEMS.by_server.get(item.item_id)
        if it is None:
            bad.append(f"{kind} {item.names[0]!r}: item {item.item_id} does not exist")
        elif not _name_ok(item, it):
            bad.append(f"{kind} {item.names[0]!r}: called {_said(item)!r}, but item {item.item_id} is a {it.name!r}")
    assert not bad, "\n".join(bad)


@pytest.mark.parametrize("name", [n for n in SPAWNED if n not in PENDING])
def test_everything_the_npc_sells_can_be_carried(name):
    """The shop hands the item to the player: a dresser or a statue (not pickupable in 7.4) cannot be sold."""
    bad = [f"{_said(item)!r} ({item.item_id})" for item in NPCS[name].buyable
           if item.item_id in ITEMS.by_server and not ITEMS.by_server[item.item_id].flags & FLAG_PICKUPABLE]
    assert not bad, "cannot be carried: " + ", ".join(bad)


@pytest.mark.parametrize("name", ROOKGAARD_NPCS)
def test_everything_the_npc_buys_can_be_obtained(name):
    bad = [f"{item.names[0]!r} ({item.item_id})" for item in NPCS[name].sellable
           if item.item_id not in OBTAINABLE]
    assert not bad, "no monster drops these and no NPC sells them: " + ", ".join(bad)



def test_no_npc_script_changes_the_shared_npc_library():
    """All NPCs share one Lua state (context.md "Script compatibility layer"): a script that redefines a library
    function - `function FocusModule:init` - changes it for every NPC set up after it. A Lost Soul made the greeting
    words gibberish that way and A Prisoner (and others, by load order) could no longer be greeted with "hi".
    Customise an instance instead: `local focus = FocusModule:new(); function focus:init(handler) ... end`."""
    offenders = []
    lib = SERVER_DIR / "data" / "npc" / "lib"
    # anything an NPC script loads counts (data/global/greeting.lua redefined FocusModule:init for 19 NPCs' sake)
    for path in (p for p in (SERVER_DIR / "data").rglob("*.lua") if lib not in p.parents):
        text = path.read_text(encoding="latin-1")
        for m in re.finditer(r"^\s*function\s+(FocusModule|NpcHandler|KeywordHandler|ShopModule|StdModule|"
                             r"TravelModule|NpcSystem)[.:]\w+", text, re.M):
            offenders.append(f"{path.name}: {m.group(0).strip()}")
    assert not offenders, "\n".join(offenders)


def test_every_npc_callback_is_its_own():
    """All NPCs share one Lua state: a script that registers a callback it never defines - or defines it as a global -
    runs another NPC's. Edowir registered "creatureSayCallback" without one and ran some other NPC's (with that NPC's
    handler); after "hi" to him no one could log in. Every callback a script registers is a local of that script."""
    offenders = []
    for path in (SERVER_DIR / "data" / "npc" / "scripts").glob("*.lua"):
        text = re.sub(r"--[^\n]*", "", path.read_text(encoding="latin-1"))
        for name in set(re.findall(r"setCallback\(\s*CALLBACK_\w+\s*,\s*([A-Za-z_]\w*)\s*\)", text)):
            if not re.search(r"local\s+function\s+" + name + r"\s*\(|local\s+" + name + r"\s*=", text):
                offenders.append(f"{path.name}: {name}")
    assert not offenders, "\n".join(sorted(offenders))


def test_no_npc_has_an_empty_keyword():
    """An empty keyword matched every message forever (Lua 5.1's string.find clamps the start): Edowir had one, and
    everything said to him froze the server. containsWord refuses them now; none should be written either."""
    offenders = []
    for path in (SERVER_DIR / "data" / "npc" / "scripts").glob("*.lua"):
        text = path.read_text(encoding="latin-1")
        if re.search(r"addKeyword\(\{\s*(''|\"\")\s*[,}]", text):
            offenders.append(path.name)
    for path in (SERVER_DIR / "data" / "npc").glob("*.xml"):
        m = re.search(r'key="keywords" value="([^"]*)"', path.read_text(encoding="latin-1"))
        if m and any(not word.strip() for word in m.group(1).rstrip(";").split(";")):
            offenders.append(path.name)
    assert not offenders, offenders

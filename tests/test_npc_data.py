"""NPC data checks that need no server: shop items exist, are what the NPC calls them, and can be obtained."""
import re

import pytest

from tibia74 import SERVER_DIR, Items
from tibia74.items import GROUP_FLUID
from tibia74.npcs import load_npcs, rookgaard_pos

NPCS = load_npcs(SERVER_DIR)
ROOKGAARD_NPCS = sorted(n for n, npc in NPCS.items() if rookgaard_pos(npc))
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
    # a fluid container sold filled ("mug of beer", "life fluid") is named after its contents
    return _said(item).lower() == it.name.lower() or bool(item.subtype and it.group == GROUP_FLUID)


@pytest.mark.parametrize("name", ROOKGAARD_NPCS)
def test_shop_items_exist_and_match_their_names(name):
    bad = []
    for kind, item in _shop(NPCS[name]):
        it = ITEMS.by_server.get(item.item_id)
        if it is None:
            bad.append(f"{kind} {item.names[0]!r}: item {item.item_id} does not exist")
        elif not _name_ok(item, it):
            bad.append(f"{kind} {item.names[0]!r}: called {_said(item)!r}, but item {item.item_id} is a {it.name!r}")
    assert not bad, "\n".join(bad)


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
    for path in (SERVER_DIR / "data" / "npc" / "scripts").glob("*.lua"):
        text = path.read_text(encoding="latin-1")
        for m in re.finditer(r"^\s*function\s+(FocusModule|NpcHandler|KeywordHandler|ShopModule|StdModule|"
                             r"TravelModule|NpcSystem)[.:]\w+", text, re.M):
            offenders.append(f"{path.name}: {m.group(0).strip()}")
    assert not offenders, "\n".join(offenders)

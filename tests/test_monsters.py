"""Every spawned monster Tibiantis (a 7.4 server) has is as Tibiantis has it - decided with the user 2026-10-02:
hit points, experience, speed, flee point, summon/convince cost and the loot (docs/reference-74/tibiantis/
creatures.json, set by tools/apply-tibiantis-monsters.py; docs/reference-74/monsters.md compares). No server needed."""
import importlib.util
import json
import re
import xml.etree.ElementTree as ET

import pytest

from tibia74 import SERVER_DIR, Items

ROOT = SERVER_DIR.parent
spec = importlib.util.spec_from_file_location("apply", ROOT / "tools" / "apply-tibiantis-monsters.py")
apply = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apply)

REF = {c["name"].lower(): c for c in json.loads(apply.REF.read_text(encoding="utf-8"))["CREATURES"]
       if not c.get("custom")}
FILES = {}
for f in (SERVER_DIR / "data" / "monster").glob("*.xml"):
    root = ET.parse(f).getroot()
    if root.tag == "monster" and root.get("name").lower() in apply.spawned() and root.get("name").lower() in REF:
        FILES[root.get("name").lower()] = root
IDS, ITEMS = apply.item_ids(), Items(SERVER_DIR / "data")


@pytest.mark.parametrize("name", sorted(FILES))
def test_monster_is_the_74_one(name):
    root, t = FILES[name], REF[name]
    flags = {k: v for fl in root.iter("flag") for k, v in fl.attrib.items()}
    got = {"hp": int(root.find("health").get("max")), "exp": int(root.get("experience")),
           "speed": int(root.get("speed")), "flee": int(flags.get("runonhealth", 0)),
           "cost": int(root.get("manacost") or 0)}
    want = {"hp": t["hp"], "exp": t["exp"], "speed": 2 * t["speed"] + 80, "flee": t.get("flee", 0),
            "cost": t.get("summon") or t.get("convince") or 0}
    assert got == want


@pytest.mark.parametrize("name", sorted(FILES))
def test_monster_drops_the_74_loot(name):
    root, t = FILES[name], REF[name]
    got = sorted((int(i.get("id")), int(i.get("chance") or i.get("chance1")), int(i.get("countmax") or 1))
                 for i in root.find("loot").iter("item"))
    skipped = []
    xml = apply.loot_xml(t.get("drops", []), IDS, ITEMS, skipped, name)
    want = sorted((int(i), int(c), int(n or 1)) for i, n, c in
                  re.findall(r'<item id="(\d+)"(?: countmax="(\d+)")? chance="(\d+)"', xml))
    assert got == want


def test_monster_attacks_agree_with_74_or_are_reviewed():
    """Every spawned monster's attacks against TibiaWiki pre-8.0 and tibiantis-notes (the spell spike,
    tools/compare-monster-spells.py): a difference is fixed or written down in its REVIEWED list."""
    spec = importlib.util.spec_from_file_location("spells", ROOT / "tools" / "compare-monster-spells.py")
    spells = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(spells)
    spells.main()
    assert ", 0 flagged and not reviewed." in spells.OUT.read_text(encoding="utf-8")

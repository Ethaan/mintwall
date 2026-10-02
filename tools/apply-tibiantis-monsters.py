"""Monsters as Tibiantis (a 7.4 server) has them - decided with the user 2026-10-02: for every spawned monster in
docs/reference-74/tibiantis/creatures.json (not its custom ones), server/data/monster/<name>.xml gets
  - the loot: Tibiantis' drop list - an item drops with its percent chance, a stackable one with 1..amount (our
    loot rule, monsters.cpp); a non-stackable item that drops "amount" times is listed that many times
  - hit points, experience, speed (ours = 2 x Tibiantis' + 80: a rotworm 18 -> 116), the flee point
    (runonhealth), the summon/convince mana cost and whether it can be summoned / convinced
Monsters Tibiantis does not have (the tomb bosses, the traps) are left alone. compare-monsters.py shows the result.

    python tools/apply-tibiantis-monsters.py
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from tibia74 import SERVER_DIR, Items              # noqa: E402

REF = ROOT / "docs" / "reference-74" / "tibiantis" / "creatures.json"
MONSTERS = SERVER_DIR / "data" / "monster"
NAMES = {"magic light wand": "magic lightwand", "brown bread": "bread", "broadsword": "broad sword",
         "pitchfork": "pitch fork", "bottle": "blue bottle"}


def item_ids():
    ids = {}
    for item in ET.parse(SERVER_DIR / "data" / "items" / "items.xml").getroot():
        name = item.get("name")
        if name:
            ids.setdefault(name.lower(), int(item.get("id") or item.get("fromid")))
    return ids


def spawned():
    text = (SERVER_DIR / "data" / "world" / "Tibia74-spawns.xml").read_text(encoding="latin-1")
    return {n.lower() for n in re.findall(r'<monster name="([^"]+)"', text)}


def loot_xml(drops, ids, items, skipped, monster):
    lines = ["  <loot>"]
    for d in drops:
        name = NAMES.get(d["name"].lower(), d["name"].lower())
        iid = ids.get(name)
        if iid is None:
            skipped.append(f"{monster}: {d['name']}")
            continue
        chance = max(1, round(d["pct"] * 1000))
        stackable = iid in items.by_server and items.by_server[iid].has_count
        if stackable and d["amount"] > 1:
            lines.append(f'    <item id="{iid}" countmax="{d["amount"]}" chance="{chance}"/>   <!-- {name} -->')
        else:
            for _ in range(d["amount"] if not stackable else 1):
                lines.append(f'    <item id="{iid}" chance="{chance}"/>   <!-- {name} -->')
    lines.append("  </loot>")
    return "\n".join(lines)


def set_flag(text, name, value):
    if re.search(r'<flag ' + name + r'="', text):
        return re.sub(r'(<flag ' + name + r'=")[^"]*(")', lambda m: f"{m.group(1)}{value}{m.group(2)}", text)
    return text.replace("</flags>", f'  <flag {name}="{value}"/>\n  </flags>')


def main():
    ids, items = item_ids(), Items(SERVER_DIR / "data")
    ref = {c["name"].lower(): c for c in json.loads(REF.read_text(encoding="utf-8"))["CREATURES"] if not c.get("custom")}
    alive = spawned()
    skipped, done = [], []
    for f in sorted(MONSTERS.glob("*.xml")):
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'<monster name="([^"]+)"', text)
        if not m or m.group(1).lower() not in alive or m.group(1).lower() not in ref:
            continue
        name, t = m.group(1).lower(), ref[m.group(1).lower()]
        loot = loot_xml(t.get("drops", []), ids, items, skipped, name)
        if re.search(r"\s*<loot>.*?</loot>", text, re.S):
            text = re.sub(r" *<loot>.*?</loot>", lambda _: loot, text, count=1, flags=re.S)
        elif "<loot/>" in text:
            text = text.replace("<loot/>", loot.strip())
        else:
            text = text.replace("</monster>", loot + "\n</monster>")
        text = re.sub(r'(<health now=")\d+(" max=")\d+', lambda mm: f'{mm.group(1)}{t["hp"]}{mm.group(2)}{t["hp"]}',
                      text, count=1)
        text = re.sub(r'(<monster [^>]*\bexperience=")\d+', lambda mm: f'{mm.group(1)}{t["exp"]}', text, count=1)
        if t.get("speed") is not None:
            text = re.sub(r'(<monster [^>]*\bspeed=")\d+', lambda mm: f'{mm.group(1)}{2 * t["speed"] + 80}', text,
                          count=1)
        cost = t.get("summon") or t.get("convince") or 0
        text = re.sub(r'(<monster [^>]*\bmanacost=")\d+', lambda mm: f'{mm.group(1)}{cost}', text, count=1)
        text = set_flag(text, "summonable", 1 if t.get("summon") else 0)
        text = set_flag(text, "convinceable", 1 if t.get("convince") else 0)
        if t.get("flee") is not None:
            text = set_flag(text, "runonhealth", t["flee"])
        f.write_text(text, encoding="utf-8")
        done.append(name)
    print(f"{len(done)} monsters set as Tibiantis; drops without an item of ours: {skipped}")


if __name__ == "__main__":
    main()

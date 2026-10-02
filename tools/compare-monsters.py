"""Compares our monsters (server/data/monster/*.xml) with Tibiantis' 7.4 creatures (docs/reference-74/tibiantis/
creatures.json, tools/fetch-tibiantis.py) and writes docs/reference-74/monsters.md: hit points, experience, speed,
flee point, summon/convince cost, and the loot - expected gold and item value per kill, items missing or extra, chances
off by more than half - ranked by how much a monster changes the economy (value per kill x how many spawn).

Our loot rule (monsters.cpp): an item drops with chance/100000, a stackable one with 1..countmax, so on average
(countmax + 1) / 2. Tibiantis gives the chance in percent and the most that drops ("amount").
Item value: what an NPC pays for it (Tibiantis EQSELL, else the best our NPCs pay); gold is 1.

    python tools/compare-monsters.py
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from tibia74 import SERVER_DIR                      # noqa: E402
from tibia74.npcs import load_npcs                  # noqa: E402

REF = ROOT / "docs" / "reference-74" / "tibiantis"
OUT = ROOT / "docs" / "reference-74" / "monsters.md"
GOLD = 2148
ALIAS = {"magic light wand": "magic lightwand", "brown bread": "bread", "broadsword": "broad sword",
         "pitchfork": "pitch fork", "bottle": "blue bottle"}      # as tools/apply-tibiantis-monsters.py


def item_names():
    ids, names = {}, {}
    for item in ET.parse(SERVER_DIR / "data" / "items" / "items.xml").getroot():
        name = item.get("name")
        if not name:
            continue
        rng = [int(item.get("id"))] if item.get("id") else range(int(item.get("fromid")), int(item.get("toid")) + 1)
        for i in rng:
            names[i] = name.lower()
            ids.setdefault(name.lower(), i)
    return ids, names


def values(names):
    """What an item fetches from an NPC: Tibiantis' best price, else the best our NPCs pay."""
    eq = json.loads((REF / "eqsell.json").read_text(encoding="utf-8"))["EQSELL"]
    value = {}
    for npc in load_npcs(SERVER_DIR).values():
        for w in npc.sellable:
            value[w.item_id] = max(value.get(w.item_id, 0), w.price)
    by_name = {}
    for i, n in names.items():
        by_name.setdefault(n, []).append(i)
    for name, e in eq.items():
        for i in by_name.get(name, []):
            value[i] = e["best"]
    value[GOLD] = 1
    value[2152] = 100
    return value


def our_loot(root):
    """[(item id, chance 0..1, average count)], container contents included."""
    out = []

    def walk(node, factor):
        for it in node.findall("item"):
            iid = int(it.get("id"))
            chance = int(it.get("chance") or it.get("chance1") or 0) / 100000 * factor
            countmax = int(it.get("countmax") or 1)
            out.append((iid, chance, (countmax + 1) / 2 if countmax > 1 else 1))
            inside = it.find("inside")
            if inside is not None:
                walk(inside, chance)
    loot = root.find("loot")
    if loot is not None:
        walk(loot, 1)
    return out


def spawn_counts():
    text = (SERVER_DIR / "data" / "world" / "Tibia74-spawns.xml").read_text(encoding="latin-1")
    return Counter(n.lower() for n in re.findall(r'<monster name="([^"]+)"', text))


def main():
    ids, names = item_names()
    value = values(names)
    spawns = spawn_counts()
    ref = {c["name"].lower(): c for c in json.loads((REF / "creatures.json").read_text(encoding="utf-8"))["CREATURES"]
           if not c.get("custom")}
    rows, unmatched = [], []
    for f in sorted((SERVER_DIR / "data" / "monster").glob("*.xml")):
        root = ET.parse(f).getroot()
        if root.tag != "monster":            # monsters.xml: the list of files
            continue
        name = root.get("name").lower()
        if name not in spawns:
            continue
        t = ref.get(name)
        if t is None:
            unmatched.append(name)
            continue
        flags = {k: v for fl in root.iter("flag") for k, v in fl.attrib.items()}
        health = root.find("health")
        stats = []
        hp = int(health.get("max"))
        if hp != t["hp"]:
            stats.append(f"hp {hp} (7.4 {t['hp']})")
        exp = int(root.get("experience"))
        if exp != t["exp"]:
            stats.append(f"exp {exp} (7.4 {t['exp']})")
        speed = int(root.get("speed"))
        if t.get("speed") is not None and speed != 2 * t["speed"] + 80:
            stats.append(f"speed {speed} (7.4 {2 * t['speed'] + 80})")
        flee = int(flags.get("runonhealth", 0))
        if t.get("flee") is not None and flee != t["flee"]:
            stats.append(f"flees at {flee} hp (7.4 {t['flee']})")
        mana = int(root.get("manacost") or 0)
        cost = t.get("summon") or t.get("convince") or 0
        if mana != cost:
            stats.append(f"summon/convince {mana} (7.4 {cost})")

        mine = our_loot(root)
        ours_gold = sum(c * n for i, c, n in mine if i == GOLD)
        ours_value = sum(c * n * value.get(i, 0) for i, c, n in mine)
        theirs, missing = [], []
        for d in t.get("drops", []):
            dn = ALIAS.get(d["name"].lower(), d["name"].lower())
            iid = ids.get(dn)
            if iid is None:
                missing.append(d["name"])
                continue
            n = (d["amount"] + 1) / 2 if d["amount"] > 1 else 1
            theirs.append((iid, d["pct"] / 100, n))
        t_gold = sum(c * n for i, c, n in theirs if i == GOLD)
        t_value = sum(c * n * value.get(i, 0) for i, c, n in theirs)

        loot = []
        mine_by, theirs_by = {}, {}
        for i, c, n in mine:
            mine_by[i] = mine_by.get(i, 0) + c * n
        for i, c, n in theirs:
            theirs_by[i] = theirs_by.get(i, 0) + c * n
        extra = [names.get(i, str(i)) for i in mine_by if i not in theirs_by and i != GOLD]
        lacks = [names.get(i, str(i)) for i in theirs_by if i not in mine_by and i != GOLD]
        off = [f"{names.get(i, i)} {mine_by[i]:.2f} (7.4 {theirs_by[i]:.2f})" for i in mine_by
               if i in theirs_by and i != GOLD and not (0.5 <= mine_by[i] / theirs_by[i] <= 2)]
        if extra:
            loot.append("drops, not in 7.4: " + ", ".join(sorted(extra)))
        if lacks:
            loot.append("7.4 drops, ours not: " + ", ".join(sorted(lacks)))
        if off:
            loot.append("per kill off by more than x2: " + ", ".join(off))
        if missing:
            loot.append("Tibiantis names without an item of ours: " + ", ".join(missing))
        weight = (ours_value - t_value) * spawns[name]
        rows.append((weight, name, spawns[name], ours_gold, t_gold, ours_value, t_value, stats, loot))

    rows.sort(key=lambda r: -abs(r[0]))
    lines = ["# Monsters against Tibiantis (7.4)", "",
             "Generated by `tools/compare-monsters.py`. Value = gold plus what NPCs pay for the items, per kill, on",
             "average. Ranked by (our value - 7.4 value) x spawns: the economy's biggest differences first.", "",
             "| monster | spawns | gold/kill ours | 7.4 | value/kill ours | 7.4 | economy x spawns |",
             "|---|---|---|---|---|---|---|"]
    for w, name, n, og, tg, ov, tv, stats, loot in rows:
        lines.append(f"| {name} | {n} | {og:.0f} | {tg:.0f} | {ov:.0f} | {tv:.0f} | {w:+.0f} |")
    lines += ["", "## Details", ""]
    for w, name, n, og, tg, ov, tv, stats, loot in rows:
        if not stats and not loot:
            continue
        lines += [f"### {name}", ""] + [f"- {s}" for s in stats + loot] + [""]
    lines += ["## Spawned, not in Tibiantis' list", "", ", ".join(unmatched) or "-", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{OUT}: {len(rows)} monsters compared, {len(unmatched)} without 7.4 data")


if __name__ == "__main__":
    main()

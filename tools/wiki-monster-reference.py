"""Builds docs/reference-74/monster-abilities.json: what every spawned monster attacks with, as TibiaWiki described it
before 8.0 - the Infobox_Creature "abilities" (each attack with its damage range: "Melee (0-120), Fire Wave
(100-170)"), "maxdmg", immunities and "behavior". The latest pre-8.0 revision with abilities is taken (the early ones
are often empty); each entry keeps its revision id and date. Spell chances, intervals and areas are not on the wiki.

    python tools/wiki-monster-reference.py [monster name ...]   (no names: every spawned monster)
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wikiref", ROOT / "tools" / "wiki-npc-reference.py")
wikiref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wikiref)

OUT = ROOT / "docs" / "reference-74" / "monster-abilities.json"
SPAWNS = ROOT / "server" / "data" / "world" / "Tibia74-spawns.xml"
FIELDS = ["abilities", "maxdmg", "hp", "exp", "behavior", "physicalimmune", "fireimmune", "energyimmune",
          "poisonimmune", "lifedrainimmune", "paralyzeimmune", "invisibleimmune", "senseinvis", "pushable",
          "pushobjects"]


def field(text, name):
    m = re.search(r"\|\s*" + name + r"\s*=(.*?)(?=\n\s*\|\s*\w+\s*=|\n\s*\}\}|\Z)", text, re.S)
    if not m:
        return ""
    value = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", m.group(1))
    return re.sub(r"<[^>]*>|\s+", " ", value).strip()


def reference(name):
    best = None
    for title in (name.title(), name.capitalize(), name):
        revs = wikiref.revisions(title)
        for rev in revs:
            text = rev.get("*", "")
            if "Infobox" in text and field(text, "abilities"):
                best = rev                                   # the latest one with abilities wins
        if revs:
            break
    if best is None:
        return None
    entry = {k: field(best["*"], k) for k in FIELDS}
    entry.update(rev=best["revid"], date=best["timestamp"][:10])
    return entry


def main(names):
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    if not names:
        text = SPAWNS.read_text(encoding="latin-1")
        names = sorted({n.lower() for n in re.findall(r'<monster name="([^"]+)"', text)})
    for i, name in enumerate(names, 1):
        try:
            data[name] = reference(name)
        except Exception as e:                       # noqa: BLE001
            print(f"{name}: {e}", flush=True)
            continue
        e = data[name]
        print(f"[{i}/{len(names)}] {name}: " + (f"rev {e['rev']} {e['date']} {e['abilities'][:90]}" if e else "none"),
              flush=True)
        OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])

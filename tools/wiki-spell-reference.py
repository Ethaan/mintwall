"""Builds docs/reference-74/spells.json: every spell of spells.xml as TibiaWiki first described it with an
Infobox_Spell or Infobox_Rune (before 8.0): words, level, magic level, mana, price, vocations, who teaches it. Most
infoboxes are from May 2005 (7.4); each entry keeps its revision id and date. A field the wiki leaves out stays "".

    python tools/wiki-spell-reference.py [spell name ...]   (no names: every spell of spells.xml)
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

SPELLS_XML = ROOT / "server" / "data" / "spells" / "spells.xml"
OUT = ROOT / "docs" / "reference-74" / "spells.json"
WIKI_NAME = {"Desintegrate": "Disintegrate", "Food": "Food (Spell)", "Invisibility": "Invisible",   # ours -> the wiki's
             "Fire Bomb": "Firebomb", "Energy Bomb": "Energybomb"}
FIELDS = {"words": ["words"], "level": ["expLvl", "level", "lvl"], "maglevel": ["MagLvl", "maglevel", "mlvl", "makeML"],
          "mana": ["mana", "makemana"], "usemaglevel": ["useML"], "charges": ["charges"], "soul": ["soul"],
          "price": ["spellcost", "price", "cost"], "voc": ["voc"], "premium": ["premium"],
          "learnfrom": ["learnfrom", "npc"]}


def clean(value):
    value = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", value)
    return re.sub(r"<[^>]*>|\s+", " ", value).strip()


def infobox(text, name):
    for key in FIELDS[name]:
        m = re.search(r"\|\s*" + key + r"\s*=([^\n|]*)", text, re.I)
        if m and m.group(1).strip():
            return clean(m.group(1))
    return ""


def reference(name):
    """The first infobox; a field it leaves out (the runes' level) from the first later revision that has it, with
    that revision in "<field>_rev"."""
    title = WIKI_NAME.get(name, name)
    revs = wikiref.revisions(title, follow=False)
    if not any(re.search(r"Infobox[ _](Spell|Rune)", r.get("*", "")) for r in revs):
        revs = wikiref.revisions(title)
    entry = None
    for rev in revs:
        text = rev.get("*", "")
        if not re.search(r"Infobox[ _](Spell|Rune)", text):
            continue
        if entry is None:
            entry = {k: infobox(text, k) for k in FIELDS}
            entry.update(rev=rev["revid"], date=rev["timestamp"][:10])
            continue
        for key in ("level", "maglevel", "mana", "price"):
            if not entry[key] and infobox(text, key):
                entry[key] = infobox(text, key)
                entry[key + "_rev"] = f"{rev['revid']} {rev['timestamp'][:10]}"
    return entry


def main(names):
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    if not names:
        xml = SPELLS_XML.read_text(encoding="latin-1")
        names = [n for n in re.findall(r'<(?:instant|conjure) name="([^"]+)"', xml) if not n.startswith("House")]
    for i, name in enumerate(names, 1):
        try:
            data[name] = reference(name)
        except Exception as e:                       # noqa: BLE001
            print(f"{name}: {e}", flush=True)
            continue
        e = data[name]
        print(f"[{i}/{len(names)}] {name}: " + (f"rev {e['rev']} {e['date']} level {e['level']} ml {e['maglevel']}"
                                                f" mana {e['mana']} price {e['price']}" if e else "no infobox"),
              flush=True)
        OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])

"""Compare item weights in server/data/items/items.xml with the Tibiantis (7.4) data.

Sources: docs/reference-74/tibiantis/weights.json (helmets, armors, legs, boots, weapons...) and shields.json.
items.xml keeps weights in hundredths of an oz (weight 12000 = 120.00 oz).

    python tools/compare-item-weights.py            # the differences only
    python tools/compare-item-weights.py --all      # also the matches and the items we do not have

A weight of 0 in the Tibiantis data means "unknown" there and is skipped. Some differences are known and kept
on purpose (KEPT below, with the evidence); they are listed but marked.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS_XML = ROOT / "server" / "data" / "items" / "items.xml"
TIBIANTIS = ROOT / "docs" / "reference-74" / "tibiantis"

# Tibiantis name -> our name
ALIASES = {
    "broadsword": "broad sword",
    "bunnyslippers": "bunny slippers",
    "daramian axe": "daramanian axe",
    "dwarfen helmet": "dwarven helmet",
    "pharao sword": "pharaoh sword",
}
# items of ours sharing a name with a Tibiantis one but a different object
NOT_THE_SAME = {2566}   # knife: the kitchen knife (the weapon is 2403)

# differences we keep, with the reason (oz)
# (TibiaWiki revisions of the item page; weights changed between 2005 and 2008, so these are open questions)
KEPT = {
    "dragon scale helmet": "TibiaWiki 2006-09..2007 say 60.00 oz; 32.50 only appears later",
    "ornamented shield": "TibiaWiki 2005-06..2007 say 67 oz; never 72",
    "golden legs": "decided 2026-10-04 (closest wiki to 7.4): TibiaWiki 2005-06 says 54, 2005-12 on says 56 (as Tibiantis)",
    "pharao sword": "decided 2026-10-04 (closest wiki to 7.4): TibiaWiki 2005-06 says 190, 2006-11 says 150 (as Tibiantis), 2008 on 52",
}


def norm(name: str) -> str:
    return re.sub(r"[\s\-]+", " ", name.lower().replace("'", "")).strip()


def our_items() -> dict:
    """normalized name -> [(id, weight in oz or None)]"""
    out = {}
    for it in ET.parse(ITEMS_XML).getroot():
        name = it.get("name")
        if not name:
            continue
        ids = [int(it.get("id"))] if it.get("id") else list(range(int(it.get("fromid")), int(it.get("toid")) + 1))
        weight = next((int(a.get("value")) / 100 for a in it.findall("attribute") if a.get("key") == "weight"), None)
        for i in ids:
            if i not in NOT_THE_SAME:
                out.setdefault(norm(name), []).append((i, weight))
    return out


def tibiantis_weights() -> dict:
    """name -> weight in oz"""
    weights = dict(json.loads((TIBIANTIS / "weights.json").read_text("utf-8"))["WEIGHTS"])
    for shield in json.loads((TIBIANTIS / "shields.json").read_text("utf-8"))["SHIELDS"]:
        if "weight" in shield:
            weights.setdefault(shield["name"], shield["weight"])
    return weights


def main(show_all: bool = False) -> int:
    ours = our_items()
    diffs = 0
    for name, theirs in sorted(tibiantis_weights().items()):
        ours_for = ours.get(norm(ALIASES.get(name, name)))
        if not ours_for:
            if show_all:
                print(f"  {name:26} not in items.xml (Tibiantis {theirs} oz)")
            continue
        if not theirs:
            if show_all:
                print(f"  {name:26} unknown in Tibiantis, ours {ours_for[0][1]} oz")
            continue
        for item_id, weight in ours_for:
            if weight is not None and abs(weight - theirs) < 0.005:
                if show_all:
                    print(f"  {name:26} {item_id:5}  {weight:8.2f} oz  ok")
                continue
            mark = f"  KEPT: {KEPT[name]}" if name in KEPT else ""
            ours_txt = "none" if weight is None else f"{weight:.2f}"
            print(f"! {name:26} {item_id:5}  ours {ours_txt:>8} oz  Tibiantis {theirs:8.2f} oz{mark}")
            diffs += name not in KEPT
    print(f"{diffs} difference(s) to look at")
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main("--all" in sys.argv))

"""Saves the 7.4 reference data tibiantis.life embeds in its pages (Tibiantis is a 7.4 server; its data won over
TibiaWiki's where they disagree - decided with the user 2026-10-01) to docs/reference-74/tibiantis/<name>.json:

  EQSELL       what NPCs pay for an item: the best price and, per city, the NPCs who pay it
  MARKET_COST  what an item costs to buy (an NPC's price; a [low, high] range for what only players sell)
  CREATURES    hit points, experience, loot
  WEAPONS, SHIELDS, ARMOR, WEIGHTS   item stats
  SPELLS       the spells (tools/apply-tibiantis-spells.py reads its own copy, spells-tibiantis.json)
  QUESTS, LSR_ITEMS

    python tools/fetch-tibiantis.py
"""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "reference-74" / "tibiantis"
URL = "https://tibiantis.life/"
NAMES = ["EQSELL", "MARKET_COST", "CREATURES", "WEAPONS", "SHIELDS", "ARMOR", "WEIGHTS", "SPELLS", "QUESTS",
         "LSR_ITEMS"]


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (mintwall 7.4 reference)"})
    page = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    OUT.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        m = re.search(r"const " + name + r"\s*=\s*", page)
        if not m:
            print(f"{name}: not on the page")
            continue
        data, _ = json.JSONDecoder().raw_decode(page[m.end():])
        (OUT / f"{name.lower()}.json").write_text(
            json.dumps({"source": URL, name: data}, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        print(f"{name}: {len(data)} entries")


if __name__ == "__main__":
    main()

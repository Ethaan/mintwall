"""Sets the monthly rent of every house in Tibia74-houses.xml from Tibiantis' house list (decided with the user
2026-10-04: rents like Tibiantis, a 7.4 server with the CipSoft house list; its houses page says the winner of an
auction pays "the bid plus the first rent [...] to their depot of the corresponding town").

    python tools/apply-tibiantis-rents.py --fetch      # download the list again into docs/reference-74/tibiantis/houses.json
    python tools/apply-tibiantis-rents.py [--dry-run]  # set rent="" in server/data/world/Tibia74-houses.xml

The list: https://tibiantis.online/?page=houses, world Ancestra, one page per town and type (house / guildhouse);
Tibiantis has no Ankrahmun houses. A house matches by its town and its name (case, apostrophes and spaces evened out,
plus the spellings in ALIASES - none needed so far). A house without a match gets the median gold per house tile of
the matched houses of its town (all matched houses for a town without any), times its house tiles on the map, rounded
to 10 gold.
No house is left with rent 0.
"""
import argparse
import json
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from tibia74.otbm import read_tiles, read_towns  # noqa: E402

WORLD = ROOT / "server" / "data" / "world"
HOUSES_XML = WORLD / "Tibia74-houses.xml"
JSON = ROOT / "docs" / "reference-74" / "tibiantis" / "houses.json"
URL = "https://tibiantis.online/?page=houses"
TOWNS = ["Ab'Dendriel", "Carlin", "Darashia", "Edron", "Kazordoon", "Thais", "Venore"]

# our name -> Tibiantis' name, for houses whose names differ by more than case, apostrophes and spaces (same town);
# none so far: all 691 houses of the 7 towns Tibiantis has match as they are (2026-10-04)
ALIASES = {
}

ROW = re.compile(r"<tr class='hover' id=(\d+)[^>]*>\s*<td>\d+</td>\s*<td><a [^>]*>(.*?)</a></td>\s*<td>(.*?)</td>"
                 r"\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td>(.*?)</td></tr>", re.S)


def fetch():
    houses = []
    for town in TOWNS:
        for gh in (0, 1):
            url = URL + "&" + urllib.parse.urlencode({"world": 1, "town": town, "gh": gh, "status": 0})
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            page = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
            rows = ROW.findall(page)
            listed = page.count("page=HouseAuction&id=")          # each house's link (the page has other links)
            if listed != len(rows):
                raise SystemExit(f"{town} gh={gh}: {listed} houses on the page, {len(rows)} parsed")
            for hid, name, desc, rent, sqm, status in rows:
                houses.append({"id": int(hid), "town": town, "guildhouse": bool(gh), "name": _html(name),
                               "description": _html(desc), "rent": int(rent), "sqm": int(sqm),
                               "status": _html(re.sub(r"<br\s*/?>", " ", status))})
            time.sleep(0.5)
    JSON.parent.mkdir(parents=True, exist_ok=True)
    JSON.write_text(json.dumps({"source": URL, "world": "Ancestra", "fetched": time.strftime("%Y-%m-%d"),
                                "houses": houses}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(houses)} houses -> {JSON.relative_to(ROOT)}")


def _html(s):
    s = re.sub(r"<[^>]+>", "", s)
    for a, b in (("&amp;", "&"), ("&#39;", "'"), ("&#039;", "'"), ("&quot;", '"'), ("&nbsp;", " ")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def key(name):
    name = name.replace("’", "'").replace("`", "'").lower()
    return re.sub(r"\s+", " ", name).strip()


def our_houses():
    xml = HOUSES_XML.read_bytes().decode("latin-1")           # bytes: the line endings stay as they are
    houses = {}
    for m in re.finditer(r"<house\s([^>]*?)/>", xml):
        a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        houses[int(a["houseid"])] = a
    return xml, houses


def house_tiles():
    tiles = Counter()
    for t in read_tiles(WORLD / "Tibia74.otbm"):
        if t.house_id:
            tiles[t.house_id] += 1
    return tiles


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download the list again (and stop)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true", help="list the unmatched houses")
    args = ap.parse_args()
    if args.fetch:
        fetch()
        return

    theirs = json.loads(JSON.read_text(encoding="utf-8"))["houses"]
    by_key = {}
    for h in theirs:
        by_key.setdefault((h["town"], key(h["name"])), []).append(h)
    dupes = {k: v for k, v in by_key.items() if len(v) > 1}
    if dupes:
        print(f"warning: {len(dupes)} Tibiantis names twice in a town: {list(dupes)[:5]}")

    xml, ours = our_houses()
    towns = {t.id: t.name for t in read_towns(WORLD / "Tibia74.otbm")}
    tiles = house_tiles()

    rents, matched, used = {}, {}, set()
    for hid, h in ours.items():
        town = towns[int(h["townid"])]
        name = ALIASES.get(h["name"], h["name"])
        found = by_key.get((town, key(name)))
        if found:
            rents[hid] = found[0]["rent"]
            matched[hid] = found[0]
            used.add(found[0]["id"])

    per_tile = {}
    for hid in matched:
        per_tile.setdefault(int(ours[hid]["townid"]), []).append(rents[hid] / tiles[hid])
    everywhere = statistics.median(v for vs in per_tile.values() for v in vs)
    fitted = {}
    for hid, h in ours.items():
        if hid in rents:
            continue
        town = int(h["townid"])
        gold = statistics.median(per_tile[town]) if town in per_tile else everywhere
        rents[hid] = fitted[hid] = max(10, int(round(gold * tiles[hid] / 10.0)) * 10)

    size_diff = [(hid, ours[hid]["name"], tiles[hid], m["sqm"]) for hid, m in matched.items() if tiles[hid] != m["sqm"]]
    print(f"{len(ours)} houses: {len(matched)} matched by town + name, {len(fitted)} rent per tile")
    print(f"Tibiantis: {len(theirs)} houses, {len(theirs) - len(used)} not matched by one of ours")
    for town_id in sorted({int(h["townid"]) for h in ours.values()}):
        n = sum(1 for h in ours.values() if int(h["townid"]) == town_id)
        m = sum(1 for hid in matched if int(ours[hid]["townid"]) == town_id)
        rule = (f"median {statistics.median(per_tile[town_id]):.1f} gp/tile" if town_id in per_tile
                else f"no match - all towns' median {everywhere:.1f} gp/tile")
        print(f"  {towns[town_id]:12s} {m:4d}/{n:<4d} matched; the others: {rule}")
    print(f"matched houses whose house tiles differ from Tibiantis' SQM: {len(size_diff)}")
    if args.verbose:
        for hid in sorted(fitted):
            print(f"  ours  {hid:4d} {towns[int(ours[hid]['townid'])]:12s} {ours[hid]['name']!r} -> {fitted[hid]}")
        for h in theirs:
            if h["id"] not in used:
                print(f"  their {h['town']:12s} {h['name']!r} rent {h['rent']} sqm {h['sqm']}")
        for d in size_diff:
            print(f"  size  {d}")

    assert all(r > 0 for r in rents.values())
    if args.dry_run:
        return

    def repl(m):
        hid = int(re.search(r'houseid="(\d+)"', m.group(0)).group(1))
        return re.sub(r'rent="\d*"', f'rent="{rents[hid]}"', m.group(0))
    new = re.sub(r"<house\s[^>]*?/>", repl, xml)
    HOUSES_XML.write_bytes(new.encode("latin-1"))
    print(f"rents written to {HOUSES_XML.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

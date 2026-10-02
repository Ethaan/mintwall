"""Builds docs/reference-74/npc-shops.json: what every spawned NPC bought and sold, from TibiaWiki as close to 7.4 as
the wiki has it.

For each NPC the earliest revision of its page that lists wares (an Infobox_NPC "buys" or "sells" with prices) is
taken, up to CUTOFF (8.0 changed many prices). 7.4 left on 2005-08-09; the wiki's lists only began in late 2005, so
most entries are from 7.5-7.9 - the "rev"/"date" of each entry say which. Prose prices ("a rat corpse for 2 Gold")
are not read; "text" keeps the revision's notes for a reader.

    python tools/wiki-npc-reference.py [NPC name ...]     (no names: every NPC in the spawns file)
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from tibia74 import SERVER_DIR                      # noqa: E402
from tibia74.npcs import load_npcs                  # noqa: E402

OUT = ROOT / "docs" / "reference-74" / "npc-shops.json"
API = "https://tibia.fandom.com/api.php"
CUTOFF = "2007-06-26T00:00:00Z"                     # Tibia 8.0
ITEM = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]\s*(?:\(([^)]*)\)\s*)?:?\s*(\d+(?:[,.]\d{3})*)\s*(k\b)?")


def api(**params):
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (mintwall 7.4 reference)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:                       # noqa: BLE001 - network: retry
            time.sleep(2 + attempt * 3)
            last = e
    raise last


def revisions(title, follow=True):
    """Every revision of the page up to CUTOFF, oldest first (content included). follow: the page a redirect leads
    to now (an old page renamed since) - the 2005 history may be under the old title itself."""
    out, cont = [], {}
    extra = {"redirects": 1} if follow else {}
    while True:
        d = api(action="query", prop="revisions", titles=title, rvlimit=50, rvdir="newer", rvend=CUTOFF,
                rvprop="ids|timestamp|content", **extra, **cont)
        for page in d["query"]["pages"].values():
            out += page.get("revisions", [])
        if "continue" not in d:
            return out
        cont = {"rvcontinue": d["continue"]["rvcontinue"]}


def field(text, name):
    m = re.search(r"\|\s*" + name + r"\s*=(.*?)(?=\n\s*\|\s*\w+\s*=|\n\s*\}\}|\Z)", text, re.S)
    return m.group(1).strip() if m else ""


def wares(value):
    """{"Spear": 10, ...} from "[[Spear]] 10, <br>[[Rapier]] 15 [[gp]]..." """
    value = re.sub(r"\[\[gp\]\]s?|\[\[GP\]\]s?|gps?\b", "", value)
    return {m.group(1).strip(): int(re.sub("[,.]", "", m.group(3))) * (1000 if m.group(4) else 1)
            for m in ITEM.finditer(value)
            if m.group(1).lower() not in ("gold", "gp", "image")}


def reference(name):
    revs = revisions(name)
    for rev in revs:
        text = rev.get("*", "")
        raw_sells, raw_buys = field(text, "sells"), field(text, "buys")
        sells, buys = wares(raw_sells), wares(raw_buys)
        if sells or buys:
            return {"rev": rev["revid"], "date": rev["timestamp"][:10], "sells": sells, "buys": buys,
                    "raw_sells": re.sub(r"\s+", " ", raw_sells), "raw_buys": re.sub(r"\s+", " ", raw_buys),
                    "notes": re.sub(r"\s+", " ", field(text, "notes"))[:400]}
    if revs:
        first = revs[0]
        return {"rev": first["revid"], "date": first["timestamp"][:10], "sells": {}, "buys": {},
                "text": re.sub(r"\s+", " ", first.get("*", ""))[:600]}
    return None


def main(names):
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    if not names:
        names = sorted(n for n, npc in load_npcs(SERVER_DIR).items() if npc.positions)
    for i, name in enumerate(names, 1):
        try:
            data[name] = reference(name)
        except Exception as e:                       # noqa: BLE001
            print(f"{name}: {e}", flush=True)
            continue
        entry = data[name]
        print(f"[{i}/{len(names)}] {name}: " + (f"rev {entry['rev']} {entry['date']} sells {len(entry['sells'])}"
                                                f" buys {len(entry['buys'])}" if entry else "no page"), flush=True)
        OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])

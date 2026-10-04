"""Sets every monster's spawntime in server/data/world/Tibia74-spawns.xml from CipSoft-derived data (decided with
the user 2026-10-04, docs/reference-74/spawns.md option (c)).

Source: Nostalrius (github Ezzz-dev/Nostalrius, data/world/spawns.xml), a 7.7 server whose world files come from
CipSoft's. Its monster entries are kept, compact, in docs/reference-74/nostalrius-spawns.csv (name, x, y, z,
spawntime in seconds; positions absolute). `--fetch` downloads the file again and rewrites the CSV.

Rules, per <monster> entry of ours (its position is the block centre + x/y, on the block's floor):
  1. kept, decided values: the 8 tomb pharaohs 600 s; the Black Knight at 32874,31948,11 720 s (TibiaWiki 2006:
     "around a constant 12 minutes")
  2. its twin: the Nostalrius monster of the same name on the same floor nearest to it (largest of |dx|, |dy|), at
     most MAX_DIST tiles away; it gets the twin's spawntime
  3. no twin: DEFAULT seconds (Cip's value for 78% of all spots)
NPC entries are left alone (the engine never respawns an NPC). Bosses are not in our spawn file and none is added.

    python tools/apply-cip-spawntimes.py            # rewrite the spawn file, print a summary
    python tools/apply-cip-spawntimes.py --check    # only report how many entries differ
    python tools/apply-cip-spawntimes.py --fetch    # re-download Nostalrius' spawns.xml into the CSV first
"""
import argparse
import collections
import csv
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPAWNS = ROOT / "server" / "data" / "world" / "Tibia74-spawns.xml"
NOST_CSV = ROOT / "docs" / "reference-74" / "nostalrius-spawns.csv"
NOST_URL = "https://raw.githubusercontent.com/Ezzz-dev/Nostalrius/master/data/world/spawns.xml"

MAX_DIST = 8
DEFAULT = 600
PHARAOHS = {"rahemos", "dipthrah", "vashresamun", "morguthis", "mahrdis", "omruc", "thalas", "ashmunrah"}
KEPT_AT = {("black knight", (32874, 31948, 11)): 720}
KEPT_NAME = {name: 600 for name in PHARAOHS}
ALIAS = {"bone beast": "bonebeast"}      # our name -> Nostalrius' name

SPAWN_RE = re.compile(r'<spawn\b([^>]*?)(/?)>(.*?)(?:</spawn>|(?=<spawn\b)|(?=</spawns>))', re.S)
MONSTER_RE = re.compile(r'<monster\b[^>]*?/>')
ATTR_RE = re.compile(r'(\w+)="([^"]*)"')


def _attrs(tag: str) -> dict:
    return dict(ATTR_RE.findall(tag))


def fetch():
    req = urllib.request.Request(NOST_URL, headers={"User-Agent": "mintwall spawn reference"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=120).read())
    rows = []
    for sp in root.iter("spawn"):
        cx, cy, cz = (int(sp.get(k)) for k in ("centerx", "centery", "centerz"))
        for m in sp.iter("monster"):
            rows.append((m.get("name").lower(), cx + int(m.get("x")), cy + int(m.get("y")), cz,
                         int(m.get("spawntime"))))
    NOST_CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(NOST_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "x", "y", "z", "spawntime"])
        w.writerows(rows)
    print(f"{len(rows)} Nostalrius monster entries -> {NOST_CSV.relative_to(ROOT)}")


def load_nostalrius() -> dict:
    """{(name, z): [(x, y, spawntime), ...]}"""
    out = collections.defaultdict(list)
    with open(NOST_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[(row["name"], int(row["z"]))].append((int(row["x"]), int(row["y"]), int(row["spawntime"])))
    return out


def twin(nost: dict, name: str, pos: tuple):
    """(distance, spawntime) of the nearest same-name Nostalrius monster on the floor, or None."""
    x, y, z = pos
    best = None
    for nx, ny, t in nost.get((ALIAS.get(name, name), z), ()):
        d = max(abs(nx - x), abs(ny - y))
        if d <= MAX_DIST:
            key = (d, (nx - x) ** 2 + (ny - y) ** 2)
            if best is None or key < best[0]:
                best = (key, t)
    return None if best is None else (best[0][0], best[1])


def wanted(nost: dict, name: str, pos: tuple) -> tuple:
    """(spawntime, rule) for one of our monster entries."""
    name = name.lower()
    if (name, pos) in KEPT_AT:
        return KEPT_AT[(name, pos)], "kept"
    if name in KEPT_NAME:
        return KEPT_NAME[name], "kept"
    t = twin(nost, name, pos)
    if t is not None:
        return t[1], "twin"
    return DEFAULT, "default"


def our_monsters(text: str):
    """Yields (match of the monster tag in `text`, name, absolute position, spawntime)."""
    for sp in SPAWN_RE.finditer(text):
        a = _attrs(sp.group(1))
        cx, cy, cz = int(a["centerx"]), int(a["centery"]), int(a["centerz"])
        start = sp.start(3)
        for m in MONSTER_RE.finditer(sp.group(3)):
            ma = _attrs(m.group(0))
            yield (start + m.start(), start + m.end()), m.group(0), ma["name"], \
                (cx + int(ma["x"]), cy + int(ma["y"]), cz), int(ma.get("spawntime", 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download Nostalrius' spawns.xml into the CSV first")
    ap.add_argument("--check", action="store_true", help="do not write, exit 1 if anything would change")
    args = ap.parse_args()
    if args.fetch:
        fetch()
    nost = load_nostalrius()
    text = SPAWNS.read_text(encoding="latin-1")
    parts, last = [], 0
    rules, changed, times = collections.Counter(), 0, collections.Counter()
    defaults = collections.Counter()
    for (s, e), tag, name, pos, old in our_monsters(text):
        t, rule = wanted(nost, name, pos)
        rules[rule] += 1
        times[t] += 1
        if rule == "default":
            defaults[name] += 1
        if t != old:
            changed += 1
            new = re.sub(r'spawntime="\d*"', f'spawntime="{t}"', tag) if 'spawntime="' in tag \
                else tag.replace("/>", f' spawntime="{t}"/>')
            parts += [text[last:s], new]
            last = e
    parts.append(text[last:])
    print(f"{sum(rules.values())} monsters: {dict(rules)}; {changed} spawntimes to change")
    print("unmatched (default %d s): %s" % (DEFAULT, dict(defaults)))
    print("spawntimes:", ", ".join(f"{t}s x{n}" for t, n in sorted(times.items())))
    if args.check:
        sys.exit(1 if changed else 0)
    if changed:
        SPAWNS.write_text("".join(parts), encoding="latin-1", newline="")
        print(f"written {SPAWNS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

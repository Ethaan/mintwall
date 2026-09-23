"""Import 7.4 creature combat values (attack, defence, armor, fighting skill) into our monster XMLs.

    tests\\.venv\\Scripts\\python.exe tools\\import-74-creatures.py [--dry-run]

Source: tibiantis-notes (https://tibiantis-notes.github.io/Creature, data in js/creature.js), whose
creature values follow the 7.4 data. The extracted numbers are kept in docs/reference-74/creatures.csv
(re-downloaded when missing). In 7.4 a creature's melee max and block max follow the player formula
(5 x skill + 50) x attack|defence x 0.99 / 100 - the engine does that when the monster file gives
  <attack name="melee" ... skill="S" attack="A"/>   and   <defenses armor="R" defense="D" skill="S">
This script writes exactly those attributes; everything else in the file is left as it is.
"""
import csv
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MONSTER_DIR = ROOT / "server" / "data" / "monster"
CSV = ROOT / "docs" / "reference-74" / "creatures.csv"
SOURCE = "https://tibiantis-notes.github.io/js/creature.js"
FIELDS = ["name", "Attack", "Defence", "Armor", "FistFighting", "HitPoints"]
ALIASES = {"bone beast": "bonebeast"}   # our name -> the source's


def download() -> list:
    js = urllib.request.urlopen(SOURCE, timeout=30).read().decode("utf-8", "replace")
    rows = []
    for body in re.findall(r"=\s*\{(name:\s*\".*?)\}\s*;", js, re.S):
        row = {"name": re.search(r'name:\s*"([^"]+)"', body).group(1)}
        for f in FIELDS[1:]:
            m = re.search(rf"\b{f}:\s*(-?\d+)", body)
            row[f] = int(m.group(1)) if m else 0
        rows.append(row)
    CSV.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV, "w", newline="", encoding="utf-8") as f:
        f.write(f"# 7.4 creature combat values, extracted from {SOURCE}\n")
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return rows


def load() -> dict:
    if not CSV.exists():
        download()
    with open(CSV, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    return {r["name"].lower(): {k: (int(v) if k != "name" else v) for k, v in r.items()}
            for r in csv.DictReader(lines)}


def set_attr(tag: str, name: str, value) -> str:
    if re.search(rf'\b{name}="[^"]*"', tag):
        return re.sub(rf'\b{name}="[^"]*"', f'{name}="{value}"', tag)
    return re.sub(r"\s*(/?>)$", f' {name}="{value}"\\1', tag)


def drop_attr(tag: str, name: str) -> str:
    return re.sub(rf'\s+\b{name}="[^"]*"', "", tag)


def old_melee_max(tag: str):
    m = re.search(r'\bmax="(-?\d+)"', tag)
    return abs(int(m.group(1))) if m else None


def main(dry_run: bool):
    data = load()
    changed, unmatched = [], []
    for xml in sorted(MONSTER_DIR.glob("*.xml")):
        text = xml.read_text(encoding="latin-1")
        m = re.search(r'<monster name="([^"]+)"', text)
        if not m:
            continue
        name = m.group(1)
        c = data.get(ALIASES.get(name.lower(), name.lower()))
        if not c:
            unmatched.append(name)
            continue
        new = text
        melee = re.search(r'<attack name="melee"[^>]*?/?>', new)
        before = old_melee_max(melee.group(0)) if melee else None
        if melee and c["Attack"] > 0:
            tag = drop_attr(drop_attr(melee.group(0), "min"), "max")
            tag = set_attr(set_attr(tag, "skill", c["FistFighting"]), "attack", c["Attack"])
            new = new.replace(melee.group(0), tag, 1)
        defenses = re.search(r"<defenses\b[^>]*>", new)
        if defenses:
            tag = set_attr(set_attr(set_attr(defenses.group(0), "armor", c["Armor"]),
                                    "defense", c["Defence"]), "skill", c["FistFighting"])
            new = new.replace(defenses.group(0), tag, 1)
        if new != text:
            after = int((5 * c["FistFighting"] + 50) * c["Attack"] * 0.99 / 100) if melee and c["Attack"] else None
            changed.append((name, before, after))
            if not dry_run:
                xml.write_text(new, encoding="latin-1")
    print(f"{len(changed)} monsters updated{' (dry run)' if dry_run else ''}, {len(unmatched)} without 7.4 data")
    for name, before, after in changed:
        print(f"  {name:24} melee max {before!s:>5} -> {after!s:>5}")
    if unmatched:
        print("no 7.4 data (left as they are):", ", ".join(unmatched))


if __name__ == "__main__":
    main("--dry-run" in sys.argv)

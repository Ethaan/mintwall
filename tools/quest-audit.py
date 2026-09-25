r"""Which quest containers does our map lack? Compares every quest object on tibiaot74's map (action id 8000 + a
unique id, their quest system) with the same tile on ours:

    done        our tile has a quest object (action id 2000)
    unscripted  the same item stands there, without a quest id - give it one (tools\map-set-attrs.py)
    missing     no such item on our tile - the map lost it, or tibiaot74 added it: check the sources first

tibiaot74 is one source, not the truth (it adds things; its items are 7.7 ids, "?<id>" = unknown to us). Use the
list to find what to look at, then settle each object with the quest-testing skill.

    python tools\quest-audit.py [x1,y1,x2,y2]      (optional area filter, any floor)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from tibia74 import SERVER_DIR, Items  # noqa: E402
from tibia74.otbm import read_tiles  # noqa: E402

TIBIAOT74_MAP = Path(r"C:\Users\cuent\AppData\Local\Temp\claude\C--mintwall\cb76e97f-21a8-4aea-9f82-8ac28d35d828"
                     r"\scratchpad\otserver\server\data\world\world.otbm")


TIBIAOT74_QUESTS = TIBIAOT74_MAP.parents[1] / "actions" / "scripts" / "main" / "quest.lua"


def their_notes():
    """tibiaot74's quest.lua: unique id -> (the comment above it, the "You have found ..." text) - which quest an
    object belongs to, by their reading."""
    import re
    if not TIBIAOT74_QUESTS.exists():
        return {}
    lines = TIBIAOT74_QUESTS.read_text(encoding="latin-1").splitlines()
    notes = {}
    for n, line in enumerate(lines):
        m = re.search(r"item\.uid\s*==\s*(\d+)", line)
        if not m:
            continue
        comment = next((lines[k].strip("- 	") for k in range(n - 1, max(n - 6, 0), -1)
                        if lines[k].strip().startswith("--") and lines[k].strip("- 	")), "")
        found = next((re.search(r'"([^"]*found[^"]*)"', lines[k]).group(1) for k in range(n, min(n + 20, len(lines)))
                      if re.search(r'"[^"]*found[^"]*"', lines[k])), "")
        notes.setdefault(int(m.group(1)), (comment, found))
    return notes


def main():
    area = tuple(int(v) for v in sys.argv[1].split(",")) if len(sys.argv) > 1 else None
    items = Items(SERVER_DIR / "data")
    name = lambda i: items.name(i) if i in items.by_server else f"?{i}"  # noqa: E731
    inside = lambda p: area is None or (area[0] <= p[0] <= area[2] and area[1] <= p[1] <= area[3])  # noqa: E731
    if not TIBIAOT74_MAP.exists():
        print(f"tibiaot74's map is not at {TIBIAOT74_MAP} (git clone tibiaot74/otserver into the scratchpad)")
        return 1
    theirs = {}
    for t in read_tiles(TIBIAOT74_MAP):
        for m in t.items:
            if m.attrs.get("action_id") == 8000 and m.attrs.get("unique_id") and inside(t.pos):
                theirs[t.pos] = (m.id, m.attrs["unique_id"])
    ours = {}
    for t in read_tiles(SERVER_DIR / "data" / "world" / "Tibia74.otbm"):
        if t.pos in theirs:
            ours[t.pos] = [(m.id, m.attrs.get("action_id"), m.attrs.get("unique_id")) for m in t.items[1:]]
    notes = their_notes()
    rows = {"done": [], "unscripted": [], "missing": []}
    for pos, (item_id, uid) in sorted(theirs.items()):
        here = ours.get(pos, [])
        if any(aid == 2000 for _, aid, _ in here):
            kind = "done"
        elif any(i == item_id or name(i) == name(item_id) for i, _, _ in here):
            kind = "unscripted"
        else:
            kind = "missing"
        comment, found = notes.get(uid, ("", ""))
        rows[kind].append(f"{pos}  {name(item_id)}  (their uid {uid}: {comment or '-'} | {found or '-'})  "
                          f"ours: {[name(i) for i, _, _ in here]}")
    print(f"{len(theirs)} quest objects on tibiaot74's map: " + ", ".join(f"{len(v)} {k}" for k, v in rows.items()))
    for kind in ("unscripted", "missing"):
        print(f"\n{kind.upper()}:")
        for row in rows[kind]:
            print("  ", row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

r"""Which quest objects does our map lack? Compares every scripted object on tibiaot74's map (action id 8000 + a
unique id - their quest system - or any unique / action id their actions.xml scripts, e.g. a lever) with the same
tile on ours:

    done        our tile has a quest object (action id 2000), or the same item there has an action / unique id
    unscripted  the same item stands there, without a quest id - give it one (tools\map-set-attrs.py)
    missing     no such item on our tile - the map lost it, or tibiaot74 added it: check the sources first

Under each object it lists the look-alikes on our map within 6 tiles on the same floor ("near:"): the same item id,
or the same kind (switch/lever, chest/box/crate/coffin, dead body/skeleton, key). The map often has the object
itself a few tiles from where tibiaot74 put it - before adding one at their spot, use the map's own:

    near: switch 33290,31715,12 (3 tiles)                  unscripted - probably that one
    near: switch 33290,31715,12 (3 tiles, aid 51021)       scripted already - probably done there

Look-alikes on the object's own tile are listed only for "missing", look-alikes that are tibiaot74 objects
themselves (a row of reward chests) not at all. "done" objects are printed only when they have an
unscripted look-alike nearby: we may have added a second one beside the map's own. Run it with --map on the original
map (server\data\world\Tibia74.otbm.bak) to see what the map had before we changed it.

tibiaot74 is one source, not the truth (it adds things; its items are 7.7 ids, "?<id>" = unknown to us). Use the
list to find what to look at, then settle each object with the quest-testing skill.

    python tools\quest-audit.py [x1,y1,x2,y2] [--map server\data\world\Tibia74.otbm.bak]
        x1,y1,x2,y2   optional area filter, any floor
        --map         our map to compare with (default: server\data\world\Tibia74.otbm)
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))

from tibia74 import SERVER_DIR, Items  # noqa: E402
from tibia74.otbm import read_tiles  # noqa: E402

TIBIAOT74_MAP = Path(r"C:\Users\cuent\AppData\Local\Temp\claude\C--mintwall\cb76e97f-21a8-4aea-9f82-8ac28d35d828"
                     r"\scratchpad\otserver\server\data\world\world.otbm")


TIBIAOT74_QUESTS = TIBIAOT74_MAP.parents[1] / "actions" / "scripts" / "main" / "quest.lua"
TIBIAOT74_ACTIONS = TIBIAOT74_MAP.parents[1] / "actions" / "actions.xml"

NEAR = 6                                    # look-alikes this many tiles away (same floor) count
LEVERS = {1945, 1946}                       # two-state switches
BOXES = set(range(1738, 1750))              # boxes, crates, chests, coffins
BODIES = {3103, 3102, 3104, 3128, 3081, 3088, 3132, 3098}
KEYS = set(range(2086, 2093))


def their_notes():
    """tibiaot74's quest.lua: unique id -> (the comment above it, the "You have found ..." text) - which quest an
    object belongs to, by their reading."""
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


def their_actions():
    """tibiaot74's actions.xml: ({unique id: script}, {action id: script}) - the ids their scripts react to."""
    uids, aids = {}, {}
    if not TIBIAOT74_ACTIONS.exists():
        return uids, aids
    for line in TIBIAOT74_ACTIONS.read_text(encoding="latin-1").splitlines():
        script = re.search(r'(?:script|value)="([^"]*)"', line)
        script = script.group(1) if script else "?"
        if m := re.search(r'<action\s+uniqueid="(\d+)"', line):
            uids[int(m.group(1))] = script
        elif m := re.search(r'<action\s+actionid="(\d+)"', line):
            aids[int(m.group(1))] = script
        elif m := re.search(r'<action\s+fromaid="(\d+)"\s+toaid="(\d+)"', line):
            aids.update({a: script for a in range(int(m.group(1)), int(m.group(2)) + 1)})
    return uids, aids


def main():
    ap = argparse.ArgumentParser(description="tibiaot74's quest objects against our map")
    ap.add_argument("area", nargs="?", help="x1,y1,x2,y2 (any floor)")
    ap.add_argument("--map", type=Path, default=SERVER_DIR / "data" / "world" / "Tibia74.otbm",
                    help="our map (e.g. server\\data\\world\\Tibia74.otbm.bak, the original)")
    args = ap.parse_args()
    area = tuple(int(v) for v in args.area.split(",")) if args.area else None
    items = Items(SERVER_DIR / "data")
    name = lambda i: items.name(i) if i in items.by_server else f"?{i}"  # noqa: E731
    inside = lambda p: area is None or (area[0] <= p[0] <= area[2] and area[1] <= p[1] <= area[3])  # noqa: E731

    def kind(i):
        n = name(i).lower()
        if i in LEVERS or n in ("switch", "lever"):
            return "lever"
        if i in BOXES or n.endswith(("chest", "box", "crate", "coffin")):
            return "box"
        if i in BODIES or n.startswith(("dead ", "slain ")) or "skeleton" in n:
            return "body"
        if i in KEYS or n.endswith(" key"):
            return "key"
        return None

    def alike(a, b):
        return a == b or name(a) == name(b) or (kind(a) is not None and kind(a) == kind(b))

    if not TIBIAOT74_MAP.exists():
        print(f"tibiaot74's map is not at {TIBIAOT74_MAP} (git clone tibiaot74/otserver into the scratchpad)")
        return 1
    if not args.map.exists():
        print(f"no map at {args.map}")
        return 1
    uids, aids = their_actions()
    theirs = {}                             # pos -> (item id, action id, unique id)
    for t in read_tiles(TIBIAOT74_MAP):
        for m in t.items:
            aid, uid = m.attrs.get("action_id"), m.attrs.get("unique_id")
            if ((aid == 8000 and uid) or uid in uids or aid in aids) and inside(t.pos):
                theirs[t.pos] = (m.id, aid, uid)
    near = {}                               # our tile -> the positions of theirs within NEAR tiles
    for x, y, z in theirs:
        for dx in range(-NEAR, NEAR + 1):
            for dy in range(-NEAR, NEAR + 1):
                near.setdefault((x + dx, y + dy, z), []).append((x, y, z))
    ours, lookalikes = {}, {pos: [] for pos in theirs}
    for t in read_tiles(args.map):
        if t.pos not in near:
            continue
        here = [(m.id, m.attrs.get("action_id"), m.attrs.get("unique_id")) for m in t.items[1:]]
        if t.pos in theirs:
            ours[t.pos] = here
        for pos in near[t.pos]:
            lookalikes[pos] += [(t.pos, i, aid, uid) for i, aid, uid in here if alike(i, theirs[pos][0])]
    notes = their_notes()
    rows = {"done": [], "unscripted": [], "missing": []}
    count = dict.fromkeys(rows, 0)
    for pos, (item_id, their_aid, uid) in sorted(theirs.items()):
        here = ours.get(pos, [])
        same = [(i, aid, u) for i, aid, u in here if i == item_id or name(i) == name(item_id)]
        if any(aid == 2000 for _, aid, _ in here) or any(aid or u for _, aid, u in same):
            kind_ = "done"
        elif same:
            kind_ = "unscripted"
        else:
            kind_ = "missing"
        count[kind_] += 1
        if their_aid == 8000:
            comment, found = notes.get(uid, ("", ""))
            theirs_note = f"their uid {uid}: {comment or '-'} | {found or '-'}"
        else:
            theirs_note = f"their uid {uid}: {uids[uid]}" if uid in uids else f"their aid {their_aid}: {aids[their_aid]}"
        lines = [f"{pos}  {name(item_id)}  ({theirs_note})  ours: {[name(i) for i, _, _ in here]}"]
        unscripted_near = False
        for p, i, aid, u in sorted(lookalikes[pos], key=lambda e: (max(abs(e[0][0] - pos[0]),
                                                                       abs(e[0][1] - pos[1])), e[0])):
            dist = max(abs(p[0] - pos[0]), abs(p[1] - pos[1]))
            if (p == pos and kind_ != "missing") or (p != pos and p in theirs):
                continue                    # tibiaot74's other objects have rows of their own
            ids = ", ".join(s for s in (aid and f"aid {aid}", u and f"uid {u}") if s)
            where = f"{name(i)} {p[0]},{p[1]},{p[2]} ({dist} tile{'s' if dist != 1 else ''}{', ' + ids if ids else ''})"
            if ids:
                lines.append(f"    near: {where:<52} scripted already - probably done there")
            else:
                unscripted_near = True
                lines.append(f"    near: {where:<52} unscripted - probably that one")
        if kind_ != "done" or unscripted_near:
            rows[kind_].append("\n".join(lines))
    print(f"{len(theirs)} quest objects on tibiaot74's map: " + ", ".join(f"{n} {k}" for k, n in count.items())
          + f"  (ours: {args.map.name})")
    for kind_, title in (("unscripted", "UNSCRIPTED"), ("missing", "MISSING"),
                         ("done", "DONE, BUT AN UNSCRIPTED LOOK-ALIKE IS NEAR (a second one?)")):
        if rows[kind_] or kind_ != "done":
            print(f"\n{title}:")
        for row in rows[kind_]:
            print("  ", row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

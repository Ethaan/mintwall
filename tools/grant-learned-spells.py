"""Grant every character the spells its vocation could learn from the NPC teachers (task.md: spell buying is new).

    tests\\.venv\\Scripts\\python.exe tools\\grant-learned-spells.py [--db server\\db.db3] --dry-run
    tests\\.venv\\Scripts\\python.exe tools\\grant-learned-spells.py [--db server\\db.db3] --backup

The rules are the teachers' (npc/lib/spellteacher.lua) and the data theirs (npc/lib/spells74.lua, read here, not
copied): a spell some teacher teaches to the character's base vocation, its magic level reached, and for the
"promoted" spells (Eremo's) a promoted vocation. There is no character level or premium check in the teachers -
premium only decides who can reach a teacher - so none here. Rookgaard characters (no vocation) get nothing.

Spells already known (any case - the engine compares them case-insensitively) are kept and not added twice, so a
second run adds nothing. Names are written as spells.xml spells them.

The server must be stopped: it rewrites player_spells on every save and logout. A real run needs --backup (the
database is copied next to itself first, with the sqlite backup API so a WAL file is included).
"""
import argparse
import re
import socket
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPELLS74 = ROOT / "server" / "data" / "npc" / "lib" / "spells74.lua"


def load_spells(path: Path = SPELLS74) -> dict:
    """{spell: (maglevel, promoted, {base vocations taught to})} from spells74.lua."""
    text = path.read_text(encoding="utf-8")
    spells_block, teachers_block = text.split("TEACHERS74 = {", 1)
    spells = {}
    for name, body in re.findall(r'^\t\["([^"]+)"\] = \{(.*)\},$', spells_block, re.M):
        maglevel = int(re.search(r"maglevel = (\d+)", body).group(1))
        spells[name] = (maglevel, "promoted = true" in body, set())
    if not spells:
        raise SystemExit(f"no spells found in {path}")
    for teaches in re.findall(r'^\t\["[^"]+"\] = \{(\[.*)\},$', teachers_block, re.M):
        for name, vocations in re.findall(r'\["([^"]+)"\] = \{([\d, ]+)\}', teaches):
            spells[name][2].update(int(v) for v in vocations.split(","))
    return spells


def learnable(spells: dict, vocation: int, maglevel: int) -> list:
    """The spells a character of this vocation and magic level could buy from the teachers, by name."""
    if vocation <= 0:
        return []
    base, promoted = (vocation - 4, True) if vocation > 4 else (vocation, False)
    return sorted(name for name, (mlvl, needs_promotion, vocations) in spells.items()
                  if base in vocations and maglevel >= mlvl and (promoted or not needs_promotion))


def plan(con: sqlite3.Connection, spells: dict) -> list:
    """[(player id, name, vocation, level, maglevel, [spells to add])] for every character."""
    known = {}
    for pid, name in con.execute("SELECT player_id, name FROM player_spells"):
        known.setdefault(pid, set()).add(name.lower())
    result = []
    for pid, name, vocation, level, maglevel in con.execute(
            "SELECT id, name, vocation, level, maglevel FROM players ORDER BY id"):
        add = [s for s in learnable(spells, vocation, maglevel) if s.lower() not in known.get(pid, set())]
        result.append((pid, name, vocation, level, maglevel, add))
    return result


def server_running(port: int = 7171) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", type=Path, default=ROOT / "server" / "db.db3")
    ap.add_argument("--dry-run", action="store_true", help="print what would be added, change nothing")
    ap.add_argument("--backup", action="store_true", help="copy the database first (required for a real run)")
    ap.add_argument("--force", action="store_true", help="run even though a server listens on --port")
    ap.add_argument("--port", type=int, default=7171, help="refuse to run while a server listens here")
    args = ap.parse_args(argv)

    if not args.db.exists():
        raise SystemExit(f"{args.db} not found")
    if not args.dry_run and not args.backup:
        raise SystemExit("a real run needs --backup (or use --dry-run)")
    if not args.dry_run and not args.force and server_running(args.port):
        raise SystemExit(f"a server is listening on port {args.port} - stop it first (it overwrites the "
                         "database on save), or pass --force")

    spells = load_spells()
    con = sqlite3.connect(args.db, timeout=10)
    try:
        todo = plan(con, spells)
        if not args.dry_run:
            backup = args.db.with_name(f"{args.db.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
            with sqlite3.connect(backup) as dst:
                con.backup(dst)
            dst.close()
            print(f"backup: {backup}")
            with con:
                con.executemany("INSERT INTO player_spells (player_id, name) VALUES (?, ?)",
                                [(pid, s) for pid, *_, add in todo for s in add])
    finally:
        con.close()

    verb = "would add" if args.dry_run else "added"
    for pid, name, vocation, level, maglevel, add in todo:
        print(f"{name} (id {pid}, vocation {vocation}, level {level}, magic level {maglevel}): "
              f"{verb} {len(add)}" + (f" - {', '.join(add)}" if add else ""))
    total = sum(len(t[-1]) for t in todo)
    print(f"{verb} {total} spells to {sum(1 for t in todo if t[-1])} of {len(todo)} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())

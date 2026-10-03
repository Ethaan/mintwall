"""Spike (2026-10-02): what 7.4 monsters attacked with, against ours. Writes docs/reference-74/monster-spells.md, per
spawned monster:
  - TibiaWiki pre-8.0 "abilities" (docs/reference-74/monster-abilities.json, tools/wiki-monster-reference.py): each
    attack with its damage range - no chances, intervals or areas
  - tibiantis-notes (docs/reference-74/tibiantis/notes-creatures.json, from "data files post 7.4"): haste and
    paralyze spells (strength, duration, chance), the poison its melee gives, strategy, how often it changes target
  - ours (server/data/monster/*.xml): every attack and defense - element, damage, shape, chance
and flags an element whose damage range differs from the wiki's by more than a third, or that one side lacks.

    python tools/compare-monster-spells.py
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "docs" / "reference-74"
OUT = REF / "monster-spells.md"
MONSTERS = ROOT / "server" / "data" / "monster"
SPAWNS = ROOT / "server" / "data" / "world" / "Tibia74-spawns.xml"

# wiki words -> our attack names
ELEMENT = [(r"summon", "summon"), (r"drunk", "drunk"), (r"appearance|outfit|transform|illusion", "outfit"),
           (r"melee|physical|hit", "melee"), (r"life ?drain|drain life", "lifedrain"), (r"mana ?drain", "manadrain"),
           (r"poison|earth", "poison"), (r"fire|flam|burn", "fire"), (r"energy|electr|lightning", "energy"),
           (r"heal", "healing"), (r"paraly", "speed"), (r"haste|speed", "speed"), (r"invisib", "invisible"),
           (r"distance|spear|arrow|bolt|stone|throw|bone|star", "physical")]
# our attack names that are an element's: a condition or a field of it
SAME = {"poisoncondition": "poison", "poisonfield": "poison", "energycondition": "energy", "energyfield": "energy",
        "firecondition": "fire", "firefield": "fire"}


# looked at by hand (2026-10-02): the flags left are kept on purpose
REVIEWED = {
    "ashmunrah": "tomb pharaoh: the wiki lists only melee and summons but 'max damage 1600+' - its page is incomplete",
    "dipthrah": "tomb pharaoh: 'Hot Water Explosion (0-600)' is our life drain area; page incomplete",
    "mahrdis": "tomb pharaoh: page incomplete (its distance attacks are listed without an element)",
    "morguthis": "tomb pharaoh: page incomplete ('Sudden Death Berserk', 'Berserk (~400)')",
    "omruc": "tomb pharaoh: his arrows are our physical/fire distance attacks; page incomplete",
    "rahemos": "tomb pharaoh: 'Energy Attack (200-600), Sudden Death (0-500)' are ours; page incomplete",
    "thalas": "tomb pharaoh: 'Poison Bomb' is a poison area, read as a missing physical attack",
    "vashresamun": "tomb pharaoh: page incomplete",
    "beholder": "its HMM is our energy, its SDs our physical (SD did physical damage in 7.4)",
    "elf arcanist": "its Heavy Magic Missile is our energy attack",
    "orc shaman": "Energy Missile (20-30) and Fire Missiles (9-41) are ours",
    "elf scout": "'Arrows (0-2 per turn) (0-120)': two arrows a turn of up to 60, as ours",
    "hunter": "'Arrows (0-2 per turn) (0-200)': two arrows a turn of up to 100, as ours",
    "magicthrower": "TibiaWiki Dec 2006: 'Magicthrowers shoot poison' - the June 2007 'energy' kept out",
    "vampire": "turns into a bat (its own outfit), not on the wiki - kept",
    "witch": "the frog: no frog creature or item in 7.4 to take the look from - not done",
    "blue djinn": "Cancel Invisibility: no monster attack for it in the engine - not done",
    "green djinn": "Cancel Invisibility: no monster attack for it in the engine - not done",
    "deathslicer": "Invisible Energy Beam added; the area 'exori' is 200-400",
    "elder beholder": "Soulfire and Sudden Death are its fire and physical distance attacks",
    "efreet": "its paralyze (tibiantis-notes) kept; energy berserk is our energy area",
    "marid": "Electrifies you: our energy area; paralyze from tibiantis-notes",
    "warlock": "its Energy Missile did physical damage (TibiaWiki); burst arrow is our fire area",
    "banshee": "Great Musical Bomb added as a physical area",
    "fire devil": "'Fireballs 0-2 (0-100)': 0-2 is how many - the fireball is 0-100, as ours",
    "priestess": "her SDs are our physical attack; melee poison 250 as tibiantis-notes",
}


def wiki_attacks(text):
    """[(our attack name, min, max, the wiki's words)] from "Melee (0-120), Fire Wave (100-160), Self-Healing"."""
    out = []
    for part in re.split(r",|;|\band\b", text):
        part = part.strip()
        if not part:
            continue
        name = next((ours for pat, ours in ELEMENT if re.search(pat, part, re.I)), "?")
        m = re.search(r"(\d+)\s*-\s*(\d+)", part)
        lo, hi = (int(m.group(1)), int(m.group(2))) if m else (None, None)
        out.append((name, lo, hi, part))
    return out


def our_attacks(root):
    out = []
    for kind in ("attacks", "defenses"):
        node = root.find(kind)
        if node is None:
            continue
        for a in node.findall("attack" if kind == "attacks" else "defense"):
            name = a.get("name")
            lo, hi = a.get("min"), a.get("max")
            shape = ", ".join(f"{k} {a.get(k)}" for k in ("radius", "length", "spread", "range", "target")
                              if a.get(k))
            if name == "melee":
                desc = f"melee attack {a.get('attack')} skill {a.get('skill')}" + (
                    f", poison {a.get('poison')}" if a.get("poison") else "")
                out.append(("melee", None, None, desc))
                if a.get("poison"):
                    out.append(("poison", None, None, f"melee poisons {a.get('poison')}"))
                continue
            name = SAME.get(name, name)
            dmg = (abs(int(lo)), abs(int(hi))) if lo and hi else (None, None)
            desc = (f"{name} {dmg[0]}-{dmg[1]}" if dmg[0] is not None else name) + (
                f" ({shape})" if shape else "") + f", chance {a.get('chance', '?')}% every {a.get('interval', '?')} ms"
            if a.get("speedchange"):
                desc += f", speed {a.get('speedchange')} for {a.get('duration')} ms"
            out.append((name, min(dmg) if dmg[0] is not None else None, max(dmg) if dmg[0] is not None else None,
                        desc))
    summons = root.find("summons")
    if summons is not None:
        for sm in summons.findall("summon"):
            out.append(("summon", None, None, f"summons {sm.get('name')} (max {summons.get('maxSummons')})"))
    return out


def main():
    wiki = json.loads((REF / "monster-abilities.json").read_text(encoding="utf-8"))
    notes = {k.lower(): v for k, v in
             json.loads((REF / "tibiantis" / "notes-creatures.json").read_text(encoding="utf-8"))["creatures"].items()}
    spawned = {n.lower() for n in re.findall(r'<monster name="([^"]+)"', SPAWNS.read_text(encoding="latin-1"))}
    files = {}
    for f in MONSTERS.glob("*.xml"):
        root = ET.parse(f).getroot()
        if root.tag == "monster" and root.get("name").lower() in spawned:
            files[root.get("name").lower()] = root

    lines = ["# Monster attacks and spells: 7.4 sources against ours (spike, 2026-10-02)", "",
             "Generated by `tools/compare-monster-spells.py`. Sources: TibiaWiki pre-8.0 creature pages (damage per",
             "attack, no chances/areas) and tibiantis-notes (haste/paralyze spells, melee poison, strategy - from data",
             "files after 7.4). \"!\" marks an element whose damage differs from the wiki's by more than a third, or that",
             "only one side has.", ""]
    flagged = 0
    for name in sorted(files):
        root, w, n = files[name], wiki.get(name), notes.get(name, {})
        mine = our_attacks(root)
        theirs = wiki_attacks(w["abilities"]) if w else []
        flags = []
        for el, lo, hi, words in theirs:
            if el in ("melee", "?"):
                continue
            ours = [x for x in mine if x[0] == el or (el == "physical" and x[0] == "physical")]
            if not ours:
                flags.append(f"! 7.4 has {words!r}, ours has no {el} attack")
            elif lo is not None and hi is not None:
                match = [x for x in ours if x[2] is None or abs(x[2] - hi) <= max(10, hi / 3)]
                if not match:
                    flags.append(f"! {words!r}: ours {', '.join(x[3].split(' (')[0] for x in ours)}")
        for el in {x[0] for x in mine} - {t[0] for t in theirs} - {"melee", "healing", "speed", "invisible"}:
            if theirs:
                flags.append(f"! ours has {el}, the 7.4 list does not")
        if flags and name in REVIEWED:
            flags = [f.replace("! ", "(reviewed) ", 1) for f in flags] + [f"reviewed: {REVIEWED[name]}"]
        flagged += any(f.startswith("!") for f in flags)
        lines += [f"## {name}", ""]
        if w:
            lines.append(f"- **TibiaWiki** (rev {w['rev']}, {w['date']}): {w['abilities']}"
                         + (f" - max damage {w['maxdmg']}" if w.get("maxdmg") else ""))
        else:
            lines.append("- **TibiaWiki**: no pre-8.0 abilities")
        extra = [n[k] for k in ("Haste_spell", "Paralyze_spell") if n.get(k)]
        if n:
            extra.append(f"melee poison {int(n['Poison'])}" if n.get("Poison") else "no melee poison")
            extra.append(f"strategy {n.get('Strategy')}, changes target {int(n.get('LoseTarget', 0))}")
        if extra:
            lines.append("- **tibiantis-notes**: " + "; ".join(extra))
        lines.append("- **ours**: " + ("; ".join(x[3] for x in mine) or "-"))
        lines += [f"  - {f}" for f in flags] + [""]
    lines.insert(6, "Looked at by hand 2026-10-02: \"reviewed\" lines are kept on purpose (REVIEWED in the tool).\n")
    lines.insert(6, f"{len(files)} spawned monsters, {flagged} flagged and not reviewed.\n")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{OUT}: {len(files)} monsters, {flagged} flagged")


if __name__ == "__main__":
    main()

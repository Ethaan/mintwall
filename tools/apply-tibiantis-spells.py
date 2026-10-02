"""Spells as Tibiantis (a 7.4 server) has them - decided with the user 2026-10-01.

  1. --fetch: reads the spell table tibiantis.life/spells embeds (words, magic level, mana, price, charges, the magic
     level to use a rune, and per vocation the NPCs who teach it, with their positions) into
     docs/reference-74/spells-tibiantis.json.
  2. Patches server/data/spells/spells.xml: every spell must be learned from an NPC (needlearn); magic level, mana,
     rune charges and vocations from Tibiantis; no character level (Tibiantis has none). A premium flag stays. A
     rune itself is used by any vocation that has its use magic level ("mluse": Magic Wall 9, Sudden Death 15).
  3. Writes server/data/npc/lib/spells74.lua: the spells for the teachers (npc/lib/spellteacher.lua) and who teaches
     what to which vocation.

    python tools/apply-tibiantis-spells.py [--fetch]
"""
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "docs" / "reference-74" / "spells-tibiantis.json"
SPELLS_XML = ROOT / "server" / "data" / "spells" / "spells.xml"
LUA = ROOT / "server" / "data" / "npc" / "lib" / "spells74.lua"
URL = "https://tibiantis.life/spells"

# Tibiantis' name -> spells.xml's (playerLearnInstantSpell takes the spells.xml name)
OURS = {"Invisible": "Invisibility", "Poisoned Arrow": "Conjure Poisoned Arrow",
        "Explosive Arrow": "Conjure Explosive Arrow", "Power Bolt": "Conjure Power Bolt", "Firebomb": "Fire Bomb",
        "Poisonbomb": "Poison Bomb", "Energybomb": "Energy Bomb"}
# Tibiantis spells we leave out (decided with the user: no price on the page)
SKIP = {"Discharge", "Extinguish", "Desintegrate Spell"}
# Eremo's spells are for the promoted only (spells.xml had them so, and TibiaWiki 2005: Challenge "Elite Knight",
# Power Bolt "Royal Paladins", Wild Growth "Elder Druids"); Tibiantis' table names the base vocation
PROMOTED_ONLY = {"Challenge", "Conjure Power Bolt", "Wild Growth", "Enchant Staff"}
PROMOTED = {"Sorcerer": "Master Sorcerer", "Druid": "Elder Druid", "Paladin": "Royal Paladin", "Knight": "Elite Knight"}
VOCATION_ID = {"Sorcerer": 1, "Druid": 2, "Paladin": 3, "Knight": 4}
# what a player may also say for a spell (the old scripts' names, the spellbook's)
ALIASES = {"Food": ["create food"], "Invisibility": ["invisible"], "Fire Bomb": ["firebomb"],
           "Poison Bomb": ["poisonbomb", "poison bomb"], "Energy Bomb": ["energybomb"],
           "Conjure Poisoned Arrow": ["poisoned arrow"], "Conjure Explosive Arrow": ["explosive arrow"],
           "Conjure Power Bolt": ["power bolt"], "Conjure Arrow": ["arrow"], "Conjure Bolt": ["bolt"]}


def fetch():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (mintwall 7.4 reference)"})
    page = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    at = page.find('"words": "adori vita vis"')
    start = [m for m in re.finditer(r'(?:=|:)\s*\[\s*\{"(?:id|name)"', page[:at])][-1]
    spells, _ = json.JSONDecoder().raw_decode(page[page.index("[", start.start()):])
    REF.write_text(json.dumps({"source": URL, "spells": spells}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{REF}: {len(spells)} spells")


def load():
    spells = {}
    for s in json.loads(REF.read_text(encoding="utf-8"))["spells"]:
        if s["name"] not in SKIP:
            spells[OURS.get(s["name"], s["name"])] = s
    return spells


def vocation_tags(vocs, promoted_only=False, indent="            "):
    if promoted_only:
        return "\n".join(indent + f'<vocation name="{PROMOTED[v]}"/>' for v in vocs)
    lines, row = [], []
    for v in vocs:
        row += [f'<vocation name="{v}"/>', f'<vocation name="{PROMOTED[v]}"/>']
    for i in range(0, len(row), 2):
        lines.append(indent + f"{row[i]:<28}{row[i + 1]}".rstrip())
    return "\n".join(lines)


def set_attr(tag, name, value):
    if value is None:
        return re.sub(r'\s+' + name + r'="[^"]*"', "", tag)
    if re.search(r'\s' + name + r'="', tag):
        return re.sub(r'(\s' + name + r'=")[^"]*"', lambda m: m.group(1) + str(value) + '"', tag)
    return re.sub(r'(\s+words="[^"]*"|\s+id="[^"]*")', lambda m: m.group(1) + f' {name}="{value}"', tag, count=1)


def patch_xml(spells):
    xml = SPELLS_XML.read_text(encoding="latin-1")
    runes = {s["words"]: s for s in spells.values() if s["kind"] == "rune"}
    done = set()

    def spell(m):
        kind, tag, body, close = m.group(1), m.group(2), m.group(3), m.group(4)
        name = re.search(r'name="([^"]*)"', tag).group(1)
        s = spells.get(name)
        if s is None:
            return m.group(0)
        done.add(name)
        tag = set_attr(tag, "maglv", s["ml"])
        if isinstance(s["mana"], int) and s["mana"] > 0:
            tag = set_attr(tag, "mana", s["mana"])
        if kind == "conjure" and s.get("charges"):
            tag = set_attr(tag, "conjureCount", s["charges"])
        tag = set_attr(tag, "lvl", None)        # a premium flag stays (Levitate: TibiaWiki 2005 and 2006)
        tag = set_attr(tag, "needlearn", 1)
        tag = tag.rstrip()
        vocs = [v for v in ("Sorcerer", "Druid", "Paladin", "Knight") if v in s["voc"]]
        inner = "" if len(vocs) == 4 else "\n" + vocation_tags(vocs, name in PROMOTED_ONLY) + "\n        "
        return f"<{kind}{tag}>{inner}</{kind}>" if inner else f"<{kind}{tag} />"

    xml = re.sub(r"<(instant|conjure)(\s[^>]*?)(?:/>()()|>(.*?)(</\1>))", spell, xml, flags=re.S)

    def rune(m):
        tag = m.group(1)
        words = re.search(r'name="([^"]*)"', tag).group(1)
        s = runes.get(words)
        if s is None or s.get("mluse") is None:
            return m.group(0)
        tag = set_attr(tag, "maglv", s["mluse"])
        return f"<rune{tag.rstrip()} />"            # any vocation may use a rune (no <vocation> list)

    xml = re.sub(r"<rune(\s[^>]*?)(?:/>|>.*?</rune>)", rune, xml, flags=re.S)
    xml = re.sub(r'(<instant name="Levitate"[^>]*/>)(\s*<!--[^>]*-->)?',
                 r"\1   <!-- premium: TibiaWiki 2005 and 2006 -->", xml)
    SPELLS_XML.write_text(xml, encoding="latin-1")
    missing = sorted(set(spells) - done)
    print(f"{SPELLS_XML}: {len(done)} spells patched" + (f"; not in spells.xml: {missing}" if missing else ""))


def lua_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_lua(spells):
    teachers = {}
    for name, s in spells.items():
        for voc, npcs in (s.get("buy") or {}).items():
            for npc in npcs:
                teachers.setdefault(npc["npc"], {}).setdefault(name, set()).add(VOCATION_ID[voc])
    out = ["-- Generated by tools/apply-tibiantis-spells.py from docs/reference-74/spells-tibiantis.json - do not edit.",
           "-- SPELLS74[name]: the spell as Tibiantis teaches it (name = spells.xml's); TEACHERS74[npc][name]: the",
           "-- vocations (1 sorcerer, 2 druid, 3 paladin, 4 knight) that NPC teaches it to.", "SPELLS74 = {"]
    for name in sorted(spells):
        s = spells[name]
        words = re.sub(r'\s*"name"|\s*up / down', "", s["words"]).strip()
        keys = sorted({name.lower(), s["name"].lower(), *ALIASES.get(name, [])}, key=lambda k: (-len(k), k))
        out.append(f"\t[{lua_str(name)}] = {{words = {lua_str(words)}, maglevel = {s['ml']}, price = {s['price']}, "
                   f"keywords = {{{', '.join(lua_str(k) for k in keys)}}}"
                   + (", promoted = true" if name in PROMOTED_ONLY else "") + "},")
    out += ["}", "", "TEACHERS74 = {"]
    for npc in sorted(teachers):
        rows = ", ".join(f"[{lua_str(n)}] = {{{', '.join(str(v) for v in sorted(vs))}}}"
                         for n, vs in sorted(teachers[npc].items()))
        out.append(f"\t[{lua_str(npc)}] = {{{rows}}},")
    out.append("}")
    LUA.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{LUA}: {len(spells)} spells, {len(teachers)} teachers")


if __name__ == "__main__":
    if "--fetch" in sys.argv or not REF.exists():
        fetch()
    spells = load()
    patch_xml(spells)
    write_lua(spells)

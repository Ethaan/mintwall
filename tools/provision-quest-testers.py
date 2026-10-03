"""The quest-testing account (asked by the user 2026-10-02): account 8, password 8, premium, with promoted characters
of the levels quests need - each with a good set for its level, every spell of its vocation learned, never-ending
runes and fluids (action id 64000; their names go into InfiniteItemPlayers through server/config.local.lua, which is
not committed), the usual tools and money.

    tests\\.venv\\Scripts\\python.exe tools\\provision-quest-testers.py [--db server\\db.db3]

LOCAL TESTING ONLY - a one-digit password. Never run it on the production database (task.md, pre-launch: remove
account 8; config.local.lua is never deployed). The server must be stopped: it rewrites characters on logout and
on every save. The database is backed up next to itself first. Running it again rebuilds the characters as listed.

Hit points, mana and capacity are 7.4's for a character that left Rookgaard at level 8 (tibiantis-notes "Classes"):
knight 15 x L + 65 hp / 5 x L - 5 mana / 25 x L + 270 cap, paladin 10 x L + 105 / 15 x L - 85 / 20 x L + 310, mage
5 x L + 145 / 30 x L - 205 / 10 x L + 390. Skills and magic level: typical for the level (tibiantis-notes tables).
"""
import argparse
import importlib.util
import re
import socket
import sqlite3
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tests"))
from tibia74.db import learnable_spells            # noqa: E402

spec = importlib.util.spec_from_file_location("provision", REPO / "tools" / "provision-accounts.py")
provision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(provision)

ACCOUNT, PASSWORD = 8, "8"
PREMIUM_END = 2_000_000_000
LOCAL_CONFIG = REPO / "server" / "config.local.lua"
INFINITE = bytes([4]) + (64000).to_bytes(2, "little")      # attribute: action id 64000 - never runs out

TOWNS = {"thais": (2, (32369, 32241, 7)), "venore": (8, (32957, 32076, 7))}
EK, RP, MS, ED = 8, 7, 5, 6

# name, vocation, level, sex (1 male), town, what it is for
ROSTER = [
    ("Draknor Stoneheart", EK, 69, 1, "venore", "Orc Fortress"),
    ("Lyria Swiftarrow", RP, 69, 0, "venore", "Orc Fortress"),
    ("Valerius Dawnbringer", RP, 177, 1, "thais", "Demon Helmet"),
    ("Grumbar Ironhide", EK, 97, 1, "thais", "Behemoth Quest"),
    ("Eldrin Moonshadow", ED, 100, 1, "thais", "level 100"),
    ("Zarathos the Grey", MS, 120, 1, "thais", "level 120"),
    ("Brannoc Wolfsbane", EK, 80, 1, "thais", "level 80"),
    ("Kaelith Ravenwood", RP, 60, 0, "thais", "level 60"),
    ("Morwen Ashgrove", MS, 75, 0, "thais", "level 75"),
    ("Thorgrim Axebeard", EK, 120, 1, "thais", "level 120"),
    ("Sylvan Thornweaver", ED, 60, 1, "thais", "level 60"),
]

# slots (player_items.pid): 1 head, 2 necklace, 3 backpack, 4 armor, 5 right hand, 6 left hand, 7 legs, 8 feet,
# 9 ring, 10 ammo
CROWN_HELMET, ROYAL_HELMET, MYSTIC_TURBAN = 2491, 2498, 2663
KNIGHT_ARMOR, GOLDEN_ARMOR, BLUE_ROBE = 2476, 2466, 2656
KNIGHT_LEGS, CROWN_LEGS, GOLDEN_LEGS = 2477, 2488, 2470
BOOTS_OF_HASTE, DRAGON_SHIELD, MASTERMIND = 2195, 2516, 2514
FIRE_SWORD, MAGIC_SWORD, GIANT_SWORD, CROSSBOW, POWER_BOLT = 2392, 2400, 2393, 2455, 2547
STONE_SKIN, SPELLBOOK = 2197, 2175
SD, UH, HMM, GFB, EXPLOSION, MAGIC_WALL, PARALYZE, ENERGY_BOMB = 2268, 2273, 2311, 2304, 2313, 2293, 2278, 2262
VIAL, MANA, LIFE = 2006, 7, 10
ROPE, SHOVEL, PICK, MACHETE, SCYTHE, CROWBAR = 2120, 2554, 2553, 2420, 2550, 2416
CRYSTAL, DRAGON_HAM, BACKPACK, LIGHT = 2160, 2672, 1988, 2162

STATS = {   # per level: hp, mana, cap and the base at "level 0"
    "knight": (15, 65, 5, -5, 25, 270),
    "paladin": (10, 105, 15, -85, 20, 310),
    "mage": (5, 145, 30, -205, 10, 390),
}
LOOK = {"knight": (131, 139), "paladin": (129, 137), "mage": (130, 138)}   # male, female


def kind(vocation):
    return {EK: "knight", RP: "paladin", MS: "mage", ED: "mage"}[vocation]


# typical magic level by level (tibiantis-notes "Classes": class magic power progression)
MAGIC = {"knight": [(10, 1), (20, 3), (30, 4), (40, 5), (60, 6), (100, 7), (150, 8), (200, 9)],
         "paladin": [(10, 3), (20, 9), (30, 12), (40, 15), (50, 16), (60, 17), (80, 18), (90, 19), (110, 20),
                     (120, 21), (140, 22), (160, 23), (190, 24), (240, 25)],
         "mage": [(10, 5), (20, 20), (30, 32), (40, 44), (50, 55), (60, 59), (70, 62), (80, 63), (90, 64),
                  (100, 67), (110, 70), (120, 71), (150, 74), (200, 79), (250, 84)]}


def magic_level(k, level):
    table = MAGIC[k]
    for (l1, m1), (l2, m2) in zip(table, table[1:]):
        if l1 <= level <= l2:
            return round(m1 + (m2 - m1) * (level - l1) / (l2 - l1))
    return table[-1][1] if level > table[-1][0] else table[0][1]


def skills(vocation, level):
    """(fist, club, sword, axe, distance, shielding, fishing), magic level - typical old-school values."""
    ml = magic_level(kind(vocation), level)
    if vocation == EK:
        melee = min(95, 60 + level // 4)
        return (20, 20, melee, 20, 30, melee - 2, 20), ml
    if vocation == RP:
        dist = min(110, 70 + level // 4)
        return (20, 25, 25, 25, dist, min(95, 55 + level // 4), 20), ml
    return (15, 15, 15, 15, 20, min(40, 20 + level // 6), 20), ml


def gear(vocation, level):
    """{slot: (item, count, attributes, [contents])}"""
    infinite = lambda item, count: (item, count, INFINITE, [])          # noqa: E731
    tools = [(ROPE, 1, b"", []), (SHOVEL, 1, b"", []), (PICK, 1, b"", []), (MACHETE, 1, b"", []),
             (SCYTHE, 1, b"", []), (CROWBAR, 1, b"", []), (LIGHT, 1, b"", []), (DRAGON_HAM, 20, b"", []),
             (CRYSTAL, 10, b"", [])]
    fluids = [infinite(VIAL, MANA), infinite(VIAL, LIFE)]
    if vocation == EK:
        runes = [infinite(UH, 1), infinite(HMM, 5), infinite(GFB, 2), infinite(EXPLOSION, 3)]
        top = level >= 100
        slots = {1: (CROWN_HELMET, 1, b"", []), 4: (KNIGHT_ARMOR, 1, b"", []),
                 7: ((GOLDEN_LEGS if top else KNIGHT_LEGS), 1, b"", []), 8: (BOOTS_OF_HASTE, 1, b"", []),
                 5: ((MAGIC_SWORD if top else FIRE_SWORD), 1, b"", []),
                 6: ((MASTERMIND if top else DRAGON_SHIELD), 1, b"", [])}
        extra = [(GIANT_SWORD, 1, b"", [])]
    elif vocation == RP:
        runes = [infinite(SD, 1), infinite(UH, 1), infinite(HMM, 5), infinite(GFB, 2), infinite(EXPLOSION, 3),
                 infinite(MAGIC_WALL, 4)]
        top = level >= 150
        slots = {1: ((ROYAL_HELMET if top else CROWN_HELMET), 1, b"", []),
                 4: ((GOLDEN_ARMOR if top else KNIGHT_ARMOR), 1, b"", []),
                 7: ((GOLDEN_LEGS if top else KNIGHT_LEGS), 1, b"", []), 8: (BOOTS_OF_HASTE, 1, b"", []),
                 5: (CROSSBOW, 1, b"", []), 10: (POWER_BOLT, 100, b"", [])}
        extra = [(POWER_BOLT, 100, b"", [])] * 4
    else:
        runes = [infinite(SD, 1), infinite(UH, 1), infinite(HMM, 5), infinite(GFB, 2), infinite(EXPLOSION, 3),
                 infinite(MAGIC_WALL, 4)] + ([infinite(PARALYZE, 1)] if vocation == ED else
                                             [infinite(ENERGY_BOMB, 2)])
        slots = {1: (MYSTIC_TURBAN, 1, b"", []), 4: (BLUE_ROBE, 1, b"", []), 7: (CROWN_LEGS, 1, b"", []),
                 8: (BOOTS_OF_HASTE, 1, b"", []), 5: (SPELLBOOK, 1, b"", []), 6: (MASTERMIND, 1, b"", [])}
        extra = []
    slots[2] = infinite(STONE_SKIN, 5)
    # a backpack of tools and supplies, and in it a backpack of runes and fluids
    slots[3] = (BACKPACK, 1, b"", tools + extra + [(BACKPACK, 1, b"", runes + fluids)])
    return slots


def insert_items(con, guid, slots):
    sid = iter(range(101, 10_000))

    def add(pid, item):
        item_id, count, attrs, contents = item
        my = next(sid)
        con.execute("INSERT INTO player_items (player_id, pid, sid, itemtype, count, attributes) VALUES (?,?,?,?,?,?)",
                    (guid, pid, my, item_id, count, attrs))
        for child in contents:
            add(my, child)

    for slot, item in sorted(slots.items()):
        add(slot, item)


def exp_for_level(level):
    return (50 * (level - 1) ** 3 - 150 * (level - 1) ** 2 + 400 * (level - 1)) // 3


def provision_characters(con):
    with con:
        con.execute("INSERT INTO accounts (id, password, premend) VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET "
                    "password = excluded.password, premend = excluded.premend",
                    (ACCOUNT, provision.pbkdf2(PASSWORD), PREMIUM_END))
        for name, vocation, level, sex, town, _ in ROSTER:
            con.execute("DELETE FROM players WHERE name = ?", (name,))    # triggers remove items, skills...
            k = kind(vocation)
            hp_l, hp_0, mana_l, mana_0, cap_l, cap_0 = STATS[k]
            hp, mana, cap = hp_l * level + hp_0, mana_l * level + mana_0, cap_l * level + cap_0
            town_id, (x, y, z) = TOWNS[town]
            looktype = LOOK[k][0 if sex else 1]
            skill, ml = skills(vocation, level)
            cur = con.execute(
                "INSERT INTO players (name, account_id, group_id, sex, vocation, experience, level, maglevel,"
                " health, healthmax, mana, manamax, cap, looktype, lookhead, lookbody, looklegs, lookfeet,"
                " posx, posy, posz, conditions, rank_id, town_id)"
                " VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 78, 69, 58, 114, ?, ?, ?, ?, 0, ?)",
                (name, ACCOUNT, sex, vocation, exp_for_level(level), level, ml, hp, hp, mana, mana, cap, looktype,
                 x, y, z, b"", town_id))
            guid = cur.lastrowid
            for skill_id, value in enumerate(skill):
                con.execute("UPDATE player_skills SET value = ? WHERE player_id = ? AND skillid = ?",
                            (value, guid, skill_id))
            for spell in learnable_spells(vocation):
                con.execute("INSERT INTO player_spells (player_id, name) VALUES (?, ?)", (guid, spell))
            con.execute("INSERT INTO player_storage (player_id, key, value) VALUES (?, 30001, 1)", (guid,))
            insert_items(con, guid, gear(vocation, level))


def allow_infinite_items():
    """The roster's never-ending runes and fluids: server/config.local.lua (not committed - .gitignore) adds their
    names to config.lua's InfiniteItemPlayers; the server reads it right after config.lua."""
    names = ", ".join(name for name, *_ in ROSTER)
    LOCAL_CONFIG.write_text(
        "-- Local settings over config.lua, never committed (.gitignore) - written by tools/provision-quest-testers.py.\n"
        "-- The quest-testing characters (account 8) may use the never-ending test items. Not for production.\n"
        f'InfiniteItemPlayers = InfiniteItemPlayers .. ", {names}"\n', encoding="latin-1")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", type=Path, default=REPO / "server" / "db.db3")
    ap.add_argument("--port", type=int, default=7171)
    args = ap.parse_args(argv)
    with socket.socket() as s:
        s.settimeout(0.5)
        if s.connect_ex(("127.0.0.1", args.port)) == 0:
            raise SystemExit(f"a server is listening on port {args.port} - stop it first")
    con = sqlite3.connect(args.db)
    try:
        backup = args.db.with_name(f"{args.db.name}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
        with sqlite3.connect(backup) as dst:
            con.backup(dst)
        print(f"backup: {backup}")
        provision_characters(con)
    finally:
        con.close()
    allow_infinite_items()
    print(f"account {ACCOUNT} / password {PASSWORD} (premium):")
    for name, vocation, level, sex, town, purpose in ROSTER:
        print(f"  {name:22} level {level:3} {kind(vocation):7} ({purpose}, starts in {town.title()})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

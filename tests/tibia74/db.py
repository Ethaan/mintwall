"""Creates test characters directly in the test database (the 7.4 client has no character creation)."""
import functools
import itertools
import re
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path

# Inventory slots as stored in player_items.pid
HEAD, NECKLACE, BACKPACK, ARMOR, RIGHT, LEFT, LEGS, FEET, RING, AMMO = range(1, 11)

# From data/vocations.xml: (hp, mana, cap) gained per level
VOCATION_GAINS = {
    0: (5, 5, 10),    # none (Rookgaard): 10 cap a level - 470 at level 8 for every vocation (tibiantis-notes)
    1: (5, 30, 10),   # sorcerer
    2: (5, 30, 10),   # druid
    3: (10, 15, 20),  # paladin
    4: (15, 5, 25),   # knight
}
VOCATION_GAINS.update({v + 4: g for v, g in list(VOCATION_GAINS.items()) if v})

TEST_ACCOUNT_BASE = 500000
_counter = itertools.count(1)


VOCATION_NAMES = {1: "Sorcerer", 2: "Druid", 3: "Paladin", 4: "Knight",
                  5: "Master Sorcerer", 6: "Elder Druid", 7: "Royal Paladin", 8: "Elite Knight"}


@functools.lru_cache(maxsize=None)
def learnable_spells(vocation: int = None) -> tuple:
    """The spells a player must learn from an NPC (needlearn in spells.xml) - those of a vocation, or all of them.
    A learned spell is cast whatever the vocation, so a test character only knows its own vocation's."""
    xml = (Path(__file__).resolve().parents[2] / "server" / "data" / "spells" / "spells.xml").read_text("latin-1")
    spells = []
    for m in re.finditer(r'<(instant|conjure) name="([^"]+)"([^>]*?)(/>|>(.*?)</\1>)', xml, re.S):
        if 'needlearn="1"' not in m.group(3):
            continue
        vocations = re.findall(r'vocation name="([^"]+)"', m.group(5) or "")
        if vocation is None or not vocations or VOCATION_NAMES.get(vocation) in vocations:
            spells.append(m.group(2))
    return tuple(spells)


def exp_for_level(level: int) -> int:
    lv = level - 1
    return (50 * lv ** 3 - 150 * lv ** 2 + 400 * lv) // 3


@dataclass
class Item:
    item_id: int
    count: int = 1
    contents: list = field(default_factory=list)  # items inside, if this is a container
    attributes: bytes = b""                        # serialized item attributes (e.g. text())

    @staticmethod
    def text(value: str) -> bytes:
        """Attributes for an item with writing on it (a label, a letter): ATTR_TEXT, u16 length, text."""
        raw = value.encode("latin-1")
        return bytes([6]) + len(raw).to_bytes(2, "little") + raw   # 6 = ATTR_TEXT


@dataclass
class Character:
    guid: int
    name: str
    account: int
    password: str


BEGINNER_SET_GIVEN = 30001   # storage login.lua sets once it handed out the beginner set


class TestDatabase:
    def __init__(self, path: Path):
        self.path = Path(path)

    def _connect(self):
        con = sqlite3.connect(self.path, timeout=10)
        con.execute("PRAGMA foreign_keys = OFF")
        return con

    def create_character(self, name: str = None, *, level: int = 1, vocation: int = 0,
                         town_id: int = 1, pos: tuple = None, sex: int = 1,
                         inventory: dict = None, group_id: int = 1,
                         health: int = None, mana: int = None, storage: dict = None,
                         premium_days: int = 0, maglevel: int = 0, skills: dict = None,
                         experience: int = None, spells: list = None, manaspent: int = 0,
                         skill_tries: dict = None) -> Character:
        """New character on its own account. pos=None means 'spawn at the town temple'.
        storage: {key: value} player storage, e.g. {BEGINNER_SET_GIVEN: 1} to skip the first-login set.
        skills: {skill id: level}, 0 fist 1 club 2 sword 3 axe 4 distance 5 shielding 6 fishing.
        spells: the spells it has learned (spells.xml names); None: every spell of its vocation (spells must be
        learned from an NPC - npc/lib/spellteacher.lua - and most tests just cast them)."""
        n = next(_counter)
        name = name or f"Test{n:04d}"
        account = TEST_ACCOUNT_BASE + n
        password = "test"
        hp_gain, mana_gain, cap_gain = VOCATION_GAINS[vocation]
        healthmax = 150 + hp_gain * (level - 1)
        manamax = 0 + mana_gain * (level - 1)
        cap = 400 + cap_gain * (level - 1)
        x, y, z = pos or (0, 0, 0)

        con = self._connect()
        try:
            premend = int(time.time()) + premium_days * 86400 if premium_days else 0
            con.execute('INSERT OR REPLACE INTO accounts (id, password, premend) VALUES (?, ?, ?)',
                        (account, password, premend))
            cur = con.execute(
                'INSERT INTO players (name, account_id, group_id, sex, vocation, experience, level,'
                ' health, healthmax, mana, manamax, cap, posx, posy, posz, conditions, rank_id, town_id)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?)',
                (name, account, group_id, sex, vocation,
                 exp_for_level(level) if experience is None else experience, level,
                 health if health is not None else healthmax, healthmax,
                 mana if mana is not None else manamax, manamax, cap, x, y, z, b"", town_id))
            guid = cur.lastrowid
            if inventory:
                self._insert_items(con, guid, inventory)
            if maglevel:
                con.execute('UPDATE players SET maglevel = ? WHERE id = ?', (maglevel, guid))
            for skill, value in (skills or {}).items():
                con.execute('UPDATE player_skills SET value = ? WHERE player_id = ? AND skillid = ?', (value, guid, skill))
            for skill, count in (skill_tries or {}).items():     # tries already made towards the next skill level
                con.execute('UPDATE player_skills SET count = ? WHERE player_id = ? AND skillid = ?', (count, guid, skill))
            if manaspent:                                         # mana already spent towards the next magic level
                con.execute('UPDATE players SET manaspent = ? WHERE id = ?', (manaspent, guid))
            if spells is None:
                spells = learnable_spells(vocation) if vocation else []
            for spell in spells:
                con.execute('INSERT INTO player_spells (player_id, name) VALUES (?, ?)', (guid, spell))
            for key, value in (storage or {}).items():
                con.execute('INSERT INTO player_storage (player_id, key, value) VALUES (?, ?, ?)', (guid, key, value))
            con.commit()
        finally:
            con.close()
        return Character(guid, name, account, password)

    def spells(self, guid: int) -> list:
        """The spells a character has learned (saved at logout)."""
        con = self._connect()
        try:
            return [r[0] for r in con.execute('SELECT name FROM player_spells WHERE player_id = ?', (guid,))]
        finally:
            con.close()

    def _insert_items(self, con, guid: int, inventory: dict):
        sid = itertools.count(101)

        def add(pid: int, item: Item):
            my_sid = next(sid)
            con.execute('INSERT INTO player_items (player_id, pid, sid, itemtype, count, attributes)'
                        ' VALUES (?, ?, ?, ?, ?, ?)', (guid, pid, my_sid, item.item_id, item.count, item.attributes))
            for child in item.contents:
                add(my_sid, child)

        for slot, item in inventory.items():
            add(slot, item if isinstance(item, Item) else Item(item))

    def character(self, guid: int) -> dict:
        con = self._connect()
        con.row_factory = sqlite3.Row
        try:
            return dict(con.execute('SELECT * FROM players WHERE id = ?', (guid,)).fetchone())
        finally:
            con.close()

    def items(self, guid: int) -> list[dict]:
        con = self._connect()
        con.row_factory = sqlite3.Row
        try:
            return [dict(r) for r in con.execute('SELECT * FROM player_items WHERE player_id = ?', (guid,))]
        finally:
            con.close()

    def storage(self, guid: int, key: int):
        """A player storage value as saved (None if the character has none)."""
        con = self._connect()
        try:
            row = con.execute('SELECT value FROM player_storage WHERE player_id = ? AND key = ?', (guid, key)).fetchone()
            return None if row is None else row[0]
        finally:
            con.close()

    def town_after_logout(self, guid: int, expected, timeout: float = 30.0):
        """The character's home town (town_id) once the server has saved it after logout."""
        import time
        deadline = time.time() + timeout
        value = self.character(guid)["town_id"]
        while value != expected and time.time() < deadline:
            time.sleep(0.2)
            value = self.character(guid)["town_id"]
        return value

    def storage_after_logout(self, guid: int, key: int, expected, timeout: float = 90.0):
        """The storage once the server has written the character: logout returns at the disconnect, the save follows -
        and a character that fought (the router kills monsters in its way) stays in the game until its fight
        condition ends (about a minute), and is saved only then."""
        import time
        deadline = time.time() + timeout
        value = self.storage(guid, key)
        while value != expected and time.time() < deadline:
            time.sleep(0.2)
            value = self.storage(guid, key)
        return value

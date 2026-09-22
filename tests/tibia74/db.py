"""Creates test characters directly in the test database (the 7.4 client has no character creation)."""
import itertools
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path

# Inventory slots as stored in player_items.pid
HEAD, NECKLACE, BACKPACK, ARMOR, RIGHT, LEFT, LEGS, FEET, RING, AMMO = range(1, 11)

# From data/vocations.xml: (hp, mana, cap) gained per level
VOCATION_GAINS = {
    0: (5, 5, 5),     # none (Rookgaard)
    1: (5, 30, 10),   # sorcerer
    2: (5, 30, 10),   # druid
    3: (10, 15, 20),  # paladin
    4: (15, 5, 25),   # knight
}
VOCATION_GAINS.update({v + 4: g for v, g in list(VOCATION_GAINS.items()) if v})

TEST_ACCOUNT_BASE = 500000
_counter = itertools.count(1)


def exp_for_level(level: int) -> int:
    lv = level - 1
    return (50 * lv ** 3 - 150 * lv ** 2 + 400 * lv) // 3


@dataclass
class Item:
    item_id: int
    count: int = 1
    contents: list = field(default_factory=list)  # items inside, if this is a container


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
                         premium_days: int = 0) -> Character:
        """New character on its own account. pos=None means 'spawn at the town temple'.
        storage: {key: value} player storage, e.g. {BEGINNER_SET_GIVEN: 1} to skip the first-login set."""
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
                (name, account, group_id, sex, vocation, exp_for_level(level), level,
                 health if health is not None else healthmax, healthmax,
                 mana if mana is not None else manamax, manamax, cap, x, y, z, b"", town_id))
            guid = cur.lastrowid
            if inventory:
                self._insert_items(con, guid, inventory)
            for key, value in (storage or {}).items():
                con.execute('INSERT INTO player_storage (player_id, key, value) VALUES (?, ?, ?)', (guid, key, value))
            con.commit()
        finally:
            con.close()
        return Character(guid, name, account, password)

    def _insert_items(self, con, guid: int, inventory: dict):
        sid = itertools.count(101)

        def add(pid: int, item: Item):
            my_sid = next(sid)
            con.execute('INSERT INTO player_items (player_id, pid, sid, itemtype, count, attributes)'
                        ' VALUES (?, ?, ?, ?, ?, ?)', (guid, pid, my_sid, item.item_id, item.count, b""))
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

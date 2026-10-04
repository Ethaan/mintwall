"""Skulls, logout block and protection zone block on a regular PvP world, as the tibia.com manual described them during
7.4 (section 4.3, archived 2005-03-08: web.archive.org/web/20050308021836/http://www.tibia.com/guide/?subtopic=manual&section=combat):

- secure mode refuses an attack on an unmarked character;
- attacking an unmarked character gives a white skull, which "will stay as long as the logout block is active", and a
  protection zone block that lasts as long as the logout block: 60 s after the last violence (PZLock = 60000);
- the attacked character is free to flee into a protection zone;
- "Player killers may not log out or enter protection zones for a full 15 minutes!" (WhiteSkullTime = 15).

The red skull (3 a day / 5 a week / 10 a month, 30 days) is in test_death.py, Rookgaard's no-PvP rule in
test_rookgaard.py (test_rookgaard_is_non_pvp).

The automatic banishment at 6 unjustified kills a day (10 a week, 20 a month) lasts 7 days the first time, 30 days the
second and 30 more each time after (60, 90, ...), like Tibiantis (decided 2026-10-04; Player::addUnjustifiedDead)."""
import sqlite3
import time

import pytest

from tibia74 import Item, NORTH, RIGHT, SOUTH

WHITE_SKULL, NO_SKULL = 3, 0
BANISHMENT = 3                     # bans.type (server/src/ban.h BANTYPE_BANISHMENT)
AUTOMATIC = "Automatic Banishment."
DAY = 86400
KNIGHT = 4
PZ_REFUSED = "can not enter a protection zone"

# Outside the north door of the Thais temple: one step south is protection zone (x 32367-32371).
THAIS_DOOR, INTO_THAIS = (32369, 32230, 7), SOUTH
# Outside the south door of the Carlin temple: one step north is protection zone (x 32360-32361).
CARLIN_DOOR, INTO_CARLIN = (32360, 31788, 7), NORTH


def _me(c):
    return c.wait_for(lambda: c.creatures.get(c.player_id), timeout=5)


def _skull_of(viewer, c):
    creature = viewer.creatures.get(c.player_id)
    return creature.skull if creature else None


def _victim(new_player, pos, level=50):
    return new_player(pos=pos, level=level, vocation=KNIGHT, storage={30001: 1})   # a vocation: Rookgaard (none) is no-PvP


def _refused_pz(c, direction):
    """Try to step into the protection zone: True if refused with the PZ block message (and not moved)."""
    start = len(c.text_messages)
    before = c.pos
    moved = c.step(direction)
    if moved:
        return False
    return bool(c.wait_for(lambda: any(PZ_REFUSED in t for _, t in c.text_messages[start:]), timeout=3)) \
        and c.pos == before


def test_secure_mode_refuses_attacking_an_unmarked_player(new_player):
    attacker = new_player(pos=(THAIS_DOOR[0] - 1, THAIS_DOOR[1] - 2, 7), level=20, vocation=KNIGHT, storage={30001: 1})
    victim = _victim(new_player, (attacker.pos[0] + 1, attacker.pos[1], 7))
    health = victim.wait_for(lambda: victim.stats.health, timeout=3)
    attacker.set_fight_modes(fight=1, chase=0, safe=1)
    attacker.attack(victim.player_id)
    assert attacker.wait_for(lambda: attacker.messages("Turn secure mode off"), timeout=3), attacker.text_messages[-3:]
    attacker.sleep(3)
    assert _me(attacker).skull == NO_SKULL
    assert victim.stats.health == health


def test_pz_block_lasts_60_s_after_an_attack_and_15_min_after_a_kill(new_player):
    """Two fights at once, to wait the 60 s only one time: an attack at the Thais temple door, a kill at Carlin's."""
    # --- the kill (Carlin): the killer stays blocked for 15 minutes
    killer = new_player(pos=CARLIN_DOOR, level=100, vocation=KNIGHT, inventory={RIGHT: Item(2400)},   # magic sword
                        skills={2: 100}, storage={30001: 1})
    dead = _victim(new_player, (CARLIN_DOOR[0] + 1, CARLIN_DOOR[1] + 1, 7), level=8)
    assert killer.pos == CARLIN_DOOR, f"the killer logged in at {killer.pos}"
    killer.set_fight_modes(fight=1, chase=0, safe=0)
    killer.attack(dead.player_id)
    assert killer.wait_for(lambda: dead.player_id in killer.removed_creatures or not dead.connected, timeout=30), \
        f"the victim did not die: {killer.text_messages[-3:]}"
    killer.attack(0)
    assert killer.wait_for(lambda: killer.messages("was not justified"), timeout=3), killer.text_messages[-3:]
    killer_attacked_at = time.time()

    # --- the attack (Thais): an unarmed level 8 against a level 50 knight, one or two blows and no more
    attacker = new_player(pos=THAIS_DOOR, level=8, vocation=KNIGHT, storage={30001: 1})
    victim = _victim(new_player, (THAIS_DOOR[0] + 1, THAIS_DOOR[1], 7))
    assert attacker.pos == THAIS_DOOR and victim.pos == (THAIS_DOOR[0] + 1, THAIS_DOOR[1], 7), (attacker.pos, victim.pos)
    me = _me(attacker)
    assert me.skull == NO_SKULL
    attacker.set_fight_modes(fight=1, chase=0, safe=0)
    attacker.attack(victim.player_id)
    assert attacker.wait_for(lambda: me.skull == WHITE_SKULL, timeout=5), f"no white skull after attacking: {me.skull}"
    attacker.attack(0)
    attacked_at = time.time()
    assert victim.wait_for(lambda: _skull_of(victim, attacker) == WHITE_SKULL, timeout=3), "others must see the skull"
    assert _skull_of(victim, victim) == NO_SKULL, "the attacked character got a skull"

    assert _refused_pz(attacker, INTO_THAIS), f"the attacker could enter the protection zone: {attacker.pos}"
    assert victim.step(INTO_THAIS), "the attacked character must be free to flee into the protection zone"

    # --- 60 s after the last violence: the attacker's skull and PZ block are gone, the killer's are not
    assert attacker.wait_for(lambda: me.skull == NO_SKULL, timeout=75), f"the white skull is still on: {me.skull}"
    gone_after = time.time() - attacked_at
    assert 55 <= gone_after <= 70, f"the white skull lasted {gone_after:.0f} s, not the 60 s logout block"
    assert attacker.step(INTO_THAIS), "60 s after the attack the attacker still may not enter the protection zone"

    assert time.time() - killer_attacked_at > 60
    assert _me(killer).skull == WHITE_SKULL, "the killer's white skull ended with the 60 s logout block, not 15 min"
    assert _refused_pz(killer, INTO_CARLIN), "the killer may enter a protection zone before the 15 minutes are over"


def _ban_rows(db, account):
    con = sqlite3.connect(db.path, timeout=10)
    try:
        return con.execute('SELECT expires, added, comment FROM bans WHERE type = ? AND value = ? ORDER BY id',
                           (BANISHMENT, account)).fetchall()
    finally:
        con.close()


def _seed(db, guid, account, kills_today, earlier_bans):
    """Unjustified kills already made today (player_kills, IOPlayer::addUnjustifiedKill) and earlier, expired
    automatic banishments of the account."""
    now = int(time.time())
    con = sqlite3.connect(db.path, timeout=10)
    try:
        con.execute('CREATE TABLE IF NOT EXISTS player_kills (player_id INTEGER NOT NULL, time INTEGER NOT NULL)')
        for n in range(kills_today):
            con.execute('INSERT INTO player_kills (player_id, time) VALUES (?, ?)', (guid, now - 3600 + n))
        for n in range(earlier_bans):
            added = now - (400 - 100 * n) * DAY
            con.execute('INSERT INTO bans (type, value, active, expires, added, admin_id, reason, comment)'
                        ' VALUES (?, ?, 1, ?, ?, 0, ?, ?)',
                        (BANISHMENT, account, added + 7 * DAY, added, "Unjustified player killing.", AUTOMATIC))
        con.commit()
    finally:
        con.close()


@pytest.mark.parametrize("earlier_bans, days", [(0, 7), (1, 30), (2, 60)])
def test_sixth_unjustified_kill_in_a_day_bans_7_days_then_30_then_60(new_player, db, earlier_bans, days):
    """The 6th unjustified kill of the day bans the account: 7 days the first time, 30 the second, 60 the third.
    5 kills are seeded in the database, the 6th is a real one."""
    killer = new_player(pos=CARLIN_DOOR, level=100, vocation=KNIGHT, inventory={RIGHT: Item(2400)},   # magic sword
                        skills={2: 100}, storage={30001: 1})
    if killer.pos != CARLIN_DOOR:            # the door tile was taken at login: pushed aside, maybe into the temple
        killer.wait_for(lambda: killer.walk_to(CARLIN_DOOR, max_steps=3), timeout=15)
    assert killer.pos == CARLIN_DOOR, f"the killer is at {killer.pos}, not at the door {CARLIN_DOOR}"
    account = killer.character.account
    _seed(db, killer.character.guid, account, kills_today=5, earlier_bans=earlier_bans)
    victim = _victim(new_player, (CARLIN_DOOR[0] + 1, CARLIN_DOOR[1] + 1, 7), level=8)
    killer.set_fight_modes(fight=1, chase=0, safe=0)
    killer.attack(victim.player_id)
    assert killer.wait_for(lambda: victim.player_id in killer.removed_creatures or not victim.connected, timeout=30),         f"the victim did not die: {killer.text_messages[-3:]}"
    assert killer.wait_for(lambda: not killer.connected, timeout=10), "the banished killer was not kicked"

    deadline = time.time() + 10
    while len(_ban_rows(db, account)) <= earlier_bans and time.time() < deadline:
        time.sleep(0.5)
    rows = _ban_rows(db, account)
    assert len(rows) == earlier_bans + 1, f"banishments of the account: {rows}"
    expires, added, comment = rows[-1]
    assert comment == AUTOMATIC
    assert abs((expires - added) - days * DAY) <= 5, f"banished for {(expires - added) / DAY:.2f} days, not {days}"


def _seed_gm(db, account, warnings, gm_bans):
    """The account's gamemaster warnings (accounts.warnings) and earlier, expired bans by a gamemaster (an admin_id,
    the gamemaster's own comment: Game::violationWindow)."""
    now = int(time.time())
    con = sqlite3.connect(db.path, timeout=10)
    try:
        con.execute('UPDATE accounts SET warnings = ? WHERE id = ?', (warnings, account))
        for n in range(gm_bans):
            added = now - (300 - 50 * n) * DAY
            con.execute('INSERT INTO bans (type, value, active, expires, added, admin_id, reason, comment)'
                        ' VALUES (?, ?, 1, ?, ?, 1, ?, ?)',
                        (BANISHMENT, account, added + DAY, added, "offensive name", "insulting the gamemaster"))
        con.commit()
    finally:
        con.close()


@pytest.mark.parametrize("earlier_bans, days", [(1, 30), (2, 60)])
def test_a_final_ban_for_unjustified_kills_is_never_shorter_than_the_automatic_one(new_player, db, earlier_bans,
                                                                                   days):
    """An account with the gamemaster warnings for the final ban (WarningsToFinalBan 4) gets the longer of the final
    ban (FinalBanLength, 7 days) and the automatic ban it would get otherwise (7 / 30 / 60 ... days) - decided with
    the user 2026-10-04. Two earlier bans by a gamemaster are seeded too: they do not count as automatic ones (the
    count is of admin_id 0 "Automatic Banishment." rows, BanManager::getAutomaticBanishmentsCount)."""
    killer = new_player(pos=CARLIN_DOOR, level=100, vocation=KNIGHT, inventory={RIGHT: Item(2400)},   # magic sword
                        skills={2: 100}, storage={30001: 1})
    if killer.pos != CARLIN_DOOR:
        killer.wait_for(lambda: killer.walk_to(CARLIN_DOOR, max_steps=3), timeout=15)
    assert killer.pos == CARLIN_DOOR, f"the killer is at {killer.pos}, not at the door {CARLIN_DOOR}"
    account = killer.character.account
    _seed(db, killer.character.guid, account, kills_today=5, earlier_bans=earlier_bans)
    _seed_gm(db, account, warnings=4, gm_bans=2)
    victim = _victim(new_player, (CARLIN_DOOR[0] + 1, CARLIN_DOOR[1] + 1, 7), level=8)
    killer.set_fight_modes(fight=1, chase=0, safe=0)
    killer.attack(victim.player_id)
    assert killer.wait_for(lambda: victim.player_id in killer.removed_creatures or not victim.connected, timeout=30), \
        f"the victim did not die: {killer.text_messages[-3:]}"
    assert killer.wait_for(lambda: not killer.connected, timeout=10), "the banished killer was not kicked"

    seeded = earlier_bans + 2
    deadline = time.time() + 10
    while len(_ban_rows(db, account)) <= seeded and time.time() < deadline:
        time.sleep(0.5)
    rows = _ban_rows(db, account)
    assert len(rows) == seeded + 1, f"banishments of the account: {rows}"
    expires, added, comment = rows[-1]
    assert comment == AUTOMATIC
    assert abs((expires - added) - days * DAY) <= 5, f"banished for {(expires - added) / DAY:.2f} days, not {days}"

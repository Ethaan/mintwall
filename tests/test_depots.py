"""Depots and mail (7.4): every town's depot lockers open that town's depot, what lies in it stays after a relog,
and each town's depot is its own. Parcels and letters reach the receiver's depot of the town on the label.

Sources: TibiaWiki Updates/4.0 (May 1998): "Implementation of ... Depots and the Mail System" - mailboxes, parcels,
letters and labels are all "implemented = 4.0", so they belong in 7.4. TibiaWiki Depot (2011 revision 407993 and
now): "Every hometown, except Rookgaard ..., has a depot", "Each city depot is unique", "Venore is currently the only
town with 2 depot buildings, and you can access the same items from either of the two"; lockers per town: Ab'Dendriel
24, Ankrahmun 22, Carlin 38, Darashia 18, Edron 36, Kazordoon 18, Venore 20 + 14, Thais 46 (ours 50: no 7.4 count
known - the map's).
"""
import functools
import time

import pytest

from tibia74 import BACKPACK, GameClient, Item, SERVER_DIR
from tibia74.otbm import read_tiles, read_towns
from tibia74.quest import next_to, use_map_item
from tibia74.server import TESTER_GROUP

MAP = SERVER_DIR / "data" / "world" / "Tibia74.otbm"
LOCKERS = range(2589, 2593)
MAILBOX = 2593
DEPOT_CHEST = 2594
PARCEL, STAMPED_PARCEL, LETTER, STAMPED_LETTER, LABEL = 2595, 2596, 2597, 2598, 2599
CARLIN_SWORD = 2395
PROTECTION_ZONE = 1                     # OTBM tile flag (tile.h TILESTATE_PROTECTIONZONE)
ROOKGAARD = ((31900, 32050, 0), (32200, 32300, 15))

THAIS, CARLIN, KAZORDOON, ABDENDRIEL, EDRON, DARASHIA, VENORE, ANKRAHMUN = 2, 3, 4, 5, 6, 7, 8, 9
# the map's lockers per depot town (TibiaWiki Depot: the same, but Thais 46)
LOCKER_COUNT = {THAIS: 50, CARLIN: 38, KAZORDOON: 18, ABDENDRIEL: 24, EDRON: 36, DARASHIA: 18, VENORE: 34,
                ANKRAHMUN: 22}
# one locker of each depot house: (town, locker)
DEPOTS = [
    (THAIS, (32352, 32225, 7)),
    (CARLIN, (32332, 31785, 8)),
    (KAZORDOON, (32663, 31918, 8)),
    (ABDENDRIEL, (32678, 31683, 7)),
    (EDRON, (33161, 31804, 8)),
    (DARASHIA, (33205, 32455, 8)),
    (VENORE, (32913, 32071, 7)),          # the depot west of the temple (the map had no depot id on its 20 lockers)
    (VENORE, (33013, 32046, 7)),          # the depot north-east of the temple
    (ANKRAHMUN, (33130, 32849, 7)),
]
THAIS_MAILBOX, NEXT_TO_THAIS_MAILBOX = (32365, 32213, 7), (32366, 32213, 7)    # next to the Thais temple (test_mail.py)


# ----------------------------------------------------------------------------- the map

@functools.lru_cache(maxsize=None)
def _map():
    """(lockers [(pos, depot id)], mailboxes [(pos, action id)], tile flags {pos: flags})."""
    lockers, mailboxes, flags = [], [], {}
    for t in read_tiles(MAP):
        flags[t.pos] = t.flags
        for it in t.items:
            if it.id in LOCKERS:
                lockers.append((t.pos, it.attrs.get("depot_id")))
            elif it.id == MAILBOX:
                mailboxes.append((t.pos, it.attrs.get("action_id")))
    return lockers, mailboxes, flags


def _inside(pos, area):
    (x1, y1, z1), (x2, y2, z2) = area
    return x1 <= pos[0] <= x2 and y1 <= pos[1] <= y2 and z1 <= pos[2] <= z2


def test_every_locker_opens_a_depot_town():
    """A locker without a depot id opened depot 0 - a depot of no town, not even Venore's other depot house."""
    lockers, _, _ = _map()
    towns = {t.id: t.name for t in read_towns(MAP)}
    wrong = [(pos, depot) for pos, depot in lockers if depot not in LOCKER_COUNT]
    assert not wrong, f"{len(wrong)} lockers open no depot town: {wrong[:10]} (towns: {towns})"


def test_lockers_per_town_are_the_maps():
    lockers, _, _ = _map()
    count = {}
    for _, depot in lockers:
        count[depot] = count.get(depot, 0) + 1
    assert count == LOCKER_COUNT


def test_rookgaard_has_no_depot_and_no_mailbox():
    """TibiaWiki Depot / Rook Depot: there is no depot on the island (players keep a second character instead)."""
    lockers, mailboxes, _ = _map()
    assert not [p for p, _ in lockers if _inside(p, ROOKGAARD)]
    assert not [p for p, _ in mailboxes if _inside(p, ROOKGAARD)]


def test_every_locker_is_in_a_protection_zone():
    """The locker's tile and a tile beside it, where its owner stands, are protection zone (as the map has them)."""
    lockers, _, flags = _map()
    bad = []
    for pos, _ in lockers:
        beside = [(pos[0] + dx, pos[1] + dy, pos[2]) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if not flags.get(pos, 0) & PROTECTION_ZONE or not any(flags.get(b, 0) & PROTECTION_ZONE for b in beside):
            bad.append(pos)
    assert not bad, bad


def test_every_depot_has_a_mailbox():
    """A free mailbox (no quest action id) within a few steps of each depot house's lockers."""
    lockers, mailboxes, _ = _map()
    free = [p for p, aid in mailboxes if not aid]
    far = []
    for _, locker in DEPOTS:
        same = [pos for pos, _ in lockers if max(abs(pos[0] - locker[0]), abs(pos[1] - locker[1])) <= 25]
        near = min(max(abs(m[0] - p[0]), abs(m[1] - p[1])) + 5 * abs(m[2] - p[2]) for m in free for p in same)
        if near > 10:
            far.append((locker, near))
    assert not far, far


# ----------------------------------------------------------------------------- live

def _depot_rows(db, guid):
    """(depot id, item id) of everything in the character's depots, at any depth: player_depotitems keeps the locker
    under pid = its depot id and every item under its parent's sid."""
    con = db._connect()
    try:
        rows = con.execute("SELECT pid, sid, itemtype FROM player_depotitems WHERE player_id = ?", (guid,)).fetchall()
    finally:
        con.close()
    parent = {sid: pid for pid, sid, _ in rows}
    sids = set(parent)

    def depot(sid):
        while parent[sid] in sids:
            sid = parent[sid]
        return parent[sid]
    return [(depot(sid), itemtype) for _, sid, itemtype in rows]


def _wait_rows(db, guid, check, timeout=30.0):
    """The depot rows once the logout save wrote them (it follows the disconnect)."""
    deadline = time.time() + timeout
    rows = _depot_rows(db, guid)
    while not check(rows) and time.time() < deadline:
        time.sleep(0.2)
        rows = _depot_rows(db, guid)
    return rows


def _logout(p, db):
    """Log out and wait for the logout save (it follows the disconnect): lastlogout is 0 until then (_move_to)."""
    p.logout()
    con = db._connect()
    try:
        deadline = time.time() + 30
        while time.time() < deadline:
            if con.execute("SELECT lastlogout FROM players WHERE id = ?", (p.character.guid,)).fetchone()[0]:
                return
            time.sleep(0.2)
    finally:
        con.close()
    raise AssertionError(f"{p.character.name} was not saved after the logout")


def _move_to(db, guid, pos):
    """Where the (saved, logged out) character logs in next."""
    con = db._connect()
    try:
        con.execute("UPDATE players SET posx = ?, posy = ?, posz = ?, lastlogout = 0 WHERE id = ?", (*pos, guid))
        con.commit()
    finally:
        con.close()


def _login_next_to(server, items, db, character, locker):
    """Log the character back in on a tile beside the locker (the 8 neighbours, as next_to does)."""
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
        _move_to(db, character.guid, (locker[0] + dx, locker[1] + dy, locker[2]))
        p = GameClient(items, port=server.port)
        p.login(character.account, character.password, character.name)
        p.character = character
        if p.pos[2] == locker[2] and max(abs(p.pos[0] - locker[0]), abs(p.pos[1] - locker[1])) <= 1:
            return p
        _logout(p, db)
    raise AssertionError(f"could not stand next to {locker}")


def _open_depot(p, items, locker):
    """Use the locker, then the depot chest in it: the chest's window."""
    window = max(p.containers, default=-1) + 1
    use_map_item(p, items, locker, "locker", window=window)
    assert p.wait_for(lambda: window in p.containers, timeout=3), f"the locker {locker} did not open: " \
                                                                    f"{p.text_messages[-2:]}"
    content = p.containers[window].items
    at = next(n for n, i in enumerate(content) if items.by_client[i.client_id].server_id == DEPOT_CHEST)
    p.use_item(p.container_pos(window, at), content[at].client_id, at, window + 1)
    assert p.wait_for(lambda: window + 1 in p.containers, timeout=3), "the depot chest did not open"
    return p.containers[window], p.containers[window + 1]


def _names(items, container):
    return [items.name(items.by_client[i.client_id].server_id) for i in container.items]


def _deposit(p, items, locker):
    """Open the backpack and the depot and put the backpack's carlin sword into the depot chest."""
    bag = p.open_container(BACKPACK)
    bag_window = next(k for k, v in p.containers.items() if v is bag)
    _, chest = _open_depot(p, items, locker)
    chest_window = next(k for k, v in p.containers.items() if v is chest)
    sword = bag.items[0]
    p.move_item(p.container_pos(bag_window, 0), sword.client_id, 0, p.container_pos(chest_window, 0), 1)
    assert p.wait_for(lambda: "carlin sword" in _names(items, chest), timeout=3), p.text_messages[-2:]


@pytest.mark.parametrize("town, locker", DEPOTS, ids=[f"{t}-{l[0]},{l[1]},{l[2]}" for t, l in DEPOTS])
def test_a_locker_opens_its_towns_depot(new_player, db, items, town, locker):
    p = next_to(new_player, locker, group_id=TESTER_GROUP, storage={30001: 1}, premium_days=30,
                inventory={BACKPACK: Item(1988, contents=[Item(CARLIN_SWORD)])})
    _deposit(p, items, locker)
    guid = p.character.guid
    _logout(p, db)
    rows = _wait_rows(db, guid, lambda r: (town, CARLIN_SWORD) in r)
    assert (town, CARLIN_SWORD) in rows, f"saved in depot(s) {sorted(set(pid for pid, _ in rows))}, not {town}"


def test_the_depot_keeps_its_items_after_a_relog_and_only_in_its_town(new_player, server, db, items):
    """Into the Thais depot, log out; in Carlin the depot chest is empty; back in Thais the sword is there."""
    thais, carlin = DEPOTS[0][1], DEPOTS[1][1]
    p = next_to(new_player, thais, group_id=TESTER_GROUP, storage={30001: 1}, premium_days=30,
                inventory={BACKPACK: Item(1988, contents=[Item(CARLIN_SWORD)])})
    character = p.character
    _deposit(p, items, thais)
    _logout(p, db)
    assert (THAIS, CARLIN_SWORD) in _wait_rows(db, character.guid, lambda r: (THAIS, CARLIN_SWORD) in r)

    p = _login_next_to(server, items, db, character, carlin)
    try:
        _, chest = _open_depot(p, items, carlin)
        p.sleep(0.5)
        assert "carlin sword" not in _names(items, chest), _names(items, chest)
    finally:
        _logout(p, db)
    assert CARLIN in {pid for pid, _ in _depot_rows(db, character.guid)}     # the Carlin depot was saved too

    p = _login_next_to(server, items, db, character, thais)
    try:
        _, chest = _open_depot(p, items, thais)
        assert p.wait_for(lambda: "carlin sword" in _names(items, chest), timeout=3), _names(items, chest)
    finally:
        p.logout()


def _mail(new_player, thing):
    """A sender beside the Thais mailbox drops `thing` (from its backpack) into it; returns (sender, backpack)."""
    p = new_player(pos=NEXT_TO_THAIS_MAILBOX, group_id=TESTER_GROUP, storage={30001: 1}, premium_days=30,
                   inventory={BACKPACK: Item(1988, contents=[thing])})
    bag = p.open_container(BACKPACK)
    cid = next(k for k, v in p.containers.items() if v is bag)
    p.move_item(p.container_pos(cid, 0), bag.items[0].client_id, 0, THAIS_MAILBOX, 1)
    p.wait_for(lambda: not bag.items or p.messages("not possible"), timeout=3)
    return p, bag


def test_a_parcel_from_thais_arrives_in_the_receivers_carlin_depot(new_player, server, db, items):
    receiver = db.create_character(storage={30001: 1}, group_id=TESTER_GROUP)
    parcel = Item(PARCEL, contents=[Item(LABEL, attributes=Item.text(f"{receiver.name}\nCarlin")), Item(CARLIN_SWORD)])
    p, bag = _mail(new_player, parcel)
    assert not bag.items, f"the mailbox did not take the parcel: {p.text_messages[-2:]}"
    rows = _depot_rows(db, receiver.guid)
    assert (CARLIN, STAMPED_PARCEL) in rows and (CARLIN, CARLIN_SWORD) in rows, rows

    carlin = DEPOTS[1][1]
    r = _login_next_to(server, items, db, receiver, carlin)
    try:
        locker, _ = _open_depot(r, items, carlin)
        assert "stamped parcel" in _names(items, locker), _names(items, locker)
    finally:
        r.logout()


def test_a_letter_to_venore_shows_in_both_venore_depots(new_player, server, db, items):
    """Mail goes to the town's depot (8); the west depot house's lockers had no depot id and opened another one."""
    receiver = db.create_character(storage={30001: 1}, group_id=TESTER_GROUP)
    p, bag = _mail(new_player, Item(LETTER, attributes=Item.text(f"{receiver.name}\nVenore\nhello")))
    assert not bag.items, f"the mailbox did not take the letter: {p.text_messages[-2:]}"
    assert (VENORE, STAMPED_LETTER) in _depot_rows(db, receiver.guid)
    for _, locker in [d for d in DEPOTS if d[0] == VENORE]:
        r = _login_next_to(server, items, db, receiver, locker)
        try:
            opened, _ = _open_depot(r, items, locker)
            assert "stamped letter" in _names(items, opened), (locker, _names(items, opened))
        finally:
            _logout(r, db)


@pytest.mark.parametrize("town", ["Rookgaard", "Fibula"])
def test_mail_to_a_town_without_a_depot_is_refused(new_player, db, town):
    """Needs the mailbox.cpp / depot.cpp change (rebuild): the map's 47 towns include villages with no locker (Fibula,
    Senja, ...); a parcel to one of them was taken and put into a depot nobody can open. Rookgaard was refused already."""
    receiver = db.create_character()
    parcel = Item(PARCEL, contents=[Item(LABEL, attributes=Item.text(f"{receiver.name}\n{town}")), Item(CARLIN_SWORD)])
    p, bag = _mail(new_player, parcel)
    assert [i.name for i in bag.items] == ["parcel"], f"the mailbox took mail to {town}"
    assert p.messages("not possible"), p.text_messages[-2:]
    assert not _depot_rows(db, receiver.guid)

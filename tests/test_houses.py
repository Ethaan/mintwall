"""Houses (task.md "Houses: confirm Tibia74-houses.xml loads, rent, doors, ownership commands" and "House doors: test
that owners/invited players can open them and others cannot").

7.4 rules (TibiaWiki, see task.md): only premium characters own houses; the owner keeps lists with house spells said
inside the house - "aleta sio" guests (may enter the house), "aleta som" subowners (open every door, edit the guest
list), "aleta grav" facing a door: who may open that door - and "alana sio <name>" puts a player out at the entrance.
Everyone else can neither open a house door nor step into the house.

The engine: house.cpp (Door::canUse, House::getHouseAccessLevel, kickPlayer, setAccessList), housetile.cpp
(__queryAdd: "You are not invited."), spells.cpp (the House* spells), commands.cpp (/owner, /gethouse, /buyhouse).
The houses used are the Sunset Homes flats in Thais (one door each; no other test uses them)."""
import functools
import re
import subprocess
import time

import pytest

from tibia74 import BACKPACK, EAST, WEST, SOUTHWEST, GameClient, Item, RIGHT, SERVER_DIR
from tibia74.otbm import read_tiles, read_towns

WORLD = SERVER_DIR / "data" / "world"
BEGINNER_SET = {30001: 1}
THAIS = 2
CLOSED_DOOR, OPEN_DOOR = 1219, 1220                 # the flats' doors (actions.xml: increment.lua opens them)
NOT_USABLE = "You can not use this object."          # RET_CANNOTUSETHISOBJECT: a house door you may not open
NOT_INVITED = "You are not invited."                # RET_PLAYERISNOTINVITED: a house tile you may not enter
NOT_POSSIBLE = "Sorry, not possible."
SWORD, GOLD = 2376, 2148
TILE_PRICE = 100                                    # config.lua HousePrice: /buyhouse costs this per house tile


class Flat:
    """A Sunset Homes flat: the corridor tile in front of its door (the house entry), the door west of it, the room
    behind the door, and a corridor tile north of the entry (diagonal to the door)."""
    def __init__(self, house_id, name, entry, tiles):
        self.id, self.name, self.entry, self.tiles = house_id, name, entry, tiles
        x, y, z = entry
        self.door = (x - 1, y, z)
        self.inside = (x - 2, y, z)
        self.further = (x - 3, y, z)
        self.beside = (x, y - 1, z)


FLAT_01 = Flat(6, "Sunset Homes, Flat 01", (32333, 32232, 7), 13)
FLAT_02 = Flat(7, "Sunset Homes, Flat 02", (32333, 32237, 7), 13)
FLAT_03 = Flat(8, "Sunset Homes, Flat 03", (32334, 32244, 7), 13)
FLAT_11 = Flat(9, "Sunset Homes, Flat 11", (32333, 32232, 6), 13)
FLAT_12 = Flat(10, "Sunset Homes, Flat 12", (32333, 32237, 6), 13)
FLAT_13 = Flat(11, "Sunset Homes, Flat 13", (32334, 32244, 6), 19)
FLAT_14 = Flat(12, "Sunset Homes, Flat 14", (32334, 32249, 6), 13)
FLAT_21 = Flat(13, "Sunset Homes, Flat 21", (32333, 32232, 5), 13)
FLAT_22 = Flat(14, "Sunset Homes, Flat 22", (32333, 32237, 5), 13)
FLAT_23 = Flat(15, "Sunset Homes, Flat 23", (32334, 32244, 5), 19)
FLAT_24 = Flat(16, "Sunset Homes, Flat 24", (32334, 32249, 5), 13)
FLATS = (FLAT_01, FLAT_02, FLAT_03, FLAT_11, FLAT_12, FLAT_13, FLAT_14, FLAT_21, FLAT_22, FLAT_23, FLAT_24)


# ---------------------------------------------------------------------------------------------- the file and the map

def _houses_xml():
    xml = (WORLD / "Tibia74-houses.xml").read_text("latin-1")
    houses = {}
    for m in re.finditer(r"<house\s([^>]*?)/>", xml):
        a = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        houses[int(a["houseid"])] = a
    return houses


@functools.lru_cache(maxsize=None)
def _map_houses():
    """({house id: [house tiles]}, {house id: [(door pos, item id, door id)]}, {pos: item ids}) - the whole map (~30 s)."""
    tiles, doors, stacks = {}, {}, {}
    for t in read_tiles(WORLD / "Tibia74.otbm"):
        stacks[t.pos] = [m.id for m in t.items]
        if t.house_id:
            tiles.setdefault(t.house_id, []).append(t.pos)
            for m in t.items:
                if "house_door" in m.attrs:
                    doors.setdefault(t.house_id, []).append((t.pos, m.id, m.attrs["house_door"]))
    return tiles, doors, stacks


def _entry(house):
    return int(house["entryx"]), int(house["entryy"]), int(house["entryz"])


def test_houses_xml_matches_the_map():
    """Every house of Tibia74-houses.xml is on the map and the other way round (Houses::loadHousesXML gives up at the
    first unknown id; a house missing from the file has no entry, town or rent); each has a door of its own, its entry
    is a tile outside the house in front of one, and its town is a mainland town."""
    houses = _houses_xml()
    tiles, doors, stacks = _map_houses()
    towns = {t.id: t.name for t in read_towns(WORLD / "Tibia74.otbm")}
    assert len(houses) == 816, len(houses)
    assert set(houses) == set(tiles), (sorted(set(houses) - set(tiles))[:10], sorted(set(tiles) - set(houses))[:10])
    names = [h["name"] for h in houses.values()]
    assert len(names) == len(set(names)), "two houses share a name"

    house_of = {p: hid for hid, ps in tiles.items() for p in ps}
    problems = []
    for hid, h in houses.items():
        if towns.get(int(h["townid"]), "Rookgaard") == "Rookgaard":
            problems.append(f"{hid} {h['name']}: town {h['townid']}")
        if not doors.get(hid):
            problems.append(f"{hid} {h['name']}: no house door")
            continue
        e = _entry(h)
        if e in house_of:
            problems.append(f"{hid} {h['name']}: entry {e} is a house tile (house {house_of[e]})")
        if not stacks.get(e):
            problems.append(f"{hid} {h['name']}: entry {e} has no ground")
        if not any(p[2] == e[2] and max(abs(p[0] - e[0]), abs(p[1] - e[1])) == 1 for p, _, _ in doors[hid]):
            problems.append(f"{hid} {h['name']}: entry {e} is not in front of one of its doors")
    assert not problems, f"{len(problems)} problems:\n" + "\n".join(problems[:20])

    for flat in FLATS:                              # what the tests below rely on
        h = houses[flat.id]
        assert h["name"] == flat.name and _entry(h) == flat.entry and h["townid"] == str(THAIS), h
        assert [(p, i) for p, i, _ in doors[flat.id]] == [(flat.door, CLOSED_DOOR)], doors[flat.id]
        assert len(tiles[flat.id]) == flat.tiles
        assert {flat.inside, flat.further} <= set(tiles[flat.id]) and flat.beside not in house_of
        assert len(stacks[flat.entry]) == 1 and len(stacks[flat.beside]) == 1, "the corridor tiles are not bare floor"
        assert stacks[flat.inside] == [405] and stacks[flat.further] == [405], "the room tiles are not bare floor"


def test_no_house_has_two_doors_with_one_door_number():
    """The engine keeps one access list per door number (House::getDoorByNumber takes the first door with it), so
    "aleta grav" on a second door with the same number edited the first one's list. 92 houses had such doors (e.g.
    Spiritkeep's door 17 three times); tools/renumber-house-doors.py numbered them apart (2026-10-04)."""
    _, doors, _ = _map_houses()
    shared = {}
    for hid, ds in doors.items():
        numbers = [number for _, _, number in ds if number]
        twice = sorted({n for n in numbers if numbers.count(n) > 1})
        if twice:
            shared[hid] = twice
    assert not shared, f"{len(shared)} houses with door numbers used twice: {dict(list(shared.items())[:10])}"


def test_the_houses_load_without_warnings(server):
    log = server.log()
    assert "Server Running" in log
    house_lines = [line for line in log.splitlines()
                   if re.search(r"house", line, re.I) and re.search(r"warn|error|fail|unknown|not set", line, re.I)]
    assert not house_lines, "\n".join(house_lines[:10])


def test_the_rent_is_monthly():
    cfg = (SERVER_DIR / "config.lua").read_text("latin-1")
    assert re.search(r'^\s*HouseRentPeriod\s*=\s*"monthly"', cfg, re.M)


# ---------------------------------------------------------------------------------------------- helpers

@pytest.fixture
def login(server, items):
    """login(character) -> a GameClient for an existing character, logged out after the test."""
    clients = []

    def make(character):
        c = GameClient(items, port=server.port)
        c.login(character.account, character.password, character.name)
        c.character = character
        clients.append(c)
        return c

    yield make
    for c in clients:
        c.logout()


def _say_and_read(c, text, contains, timeout=3):
    start = len(c.text_messages)
    c.say(text)
    c.wait_for(lambda: any(contains in t for _, t in c.text_messages[start:]), timeout=timeout)
    return [t for _, t in c.text_messages[start:]]


def _house_of(gm, name):
    lines = [t for t in _say_and_read(gm, f"/gethouse {name}", name) if name in t]
    assert lines, f"no answer to /gethouse {name}"
    return lines[0]


def _owner(new_player, db, login, flat, pos=None, **kwargs):
    """A premium Thais character that owns `flat` (given by a GM's /owner, said in the house), logged in at `pos`."""
    character = db.create_character(pos=pos or flat.entry, premium_days=30, town_id=THAIS, storage=BEGINNER_SET,
                                    **kwargs)
    gm = new_player(pos=flat.further, group_id=3, storage=BEGINNER_SET)   # God: CanEditHouses, may stand in any house
    assert gm.pos == flat.further, gm.pos
    gm.say(f"/owner {character.name}")
    assert gm.wait_for(lambda: flat.name in _house_of(gm, character.name), timeout=5), _house_of(gm, character.name)
    gm.logout()
    time.sleep(0.5)
    return login(character)


def _stack(c, pos):
    """(client id, stack position) of the top item on a tile as `c` sees it."""
    stack = c.tiles.get(tuple(pos), [])
    for i in range(len(stack) - 1, -1, -1):
        if hasattr(stack[i], "client_id"):
            return stack[i].client_id, i
    return None, None


def _door_is(c, flat, items, server_id, timeout=3):
    cid = items.by_server[server_id].client_id
    return c.wait_for(lambda: _stack(c, flat.door)[0] == cid, timeout=timeout)


def _use_door(c, flat):
    cid, stackpos = _stack(c, flat.door)
    c.use_item(flat.door, cid, stackpos)


def _got(c, text, since, timeout=3):
    return c.wait_for(lambda: any(text in t for _, t in c.text_messages[since:]), timeout=timeout)


def _cast(c, words):
    """Say a house spell: they are spells, with the 1 s exhaustion of a non-aggressive one (HealExhausted)."""
    time.sleep(1.1)
    c.say(words)


def _house_list(c, words):
    """Say a house spell (aleta sio / som / grav) -> (window id, the list) of the window it opens, or None."""
    start = len(c.house_windows)
    _cast(c, words)
    if not c.wait_for(lambda: len(c.house_windows) > start, timeout=3):
        return None
    _, window_id, text = c.house_windows[-1]
    return window_id, text


def _set_house_list(c, words, names):
    opened = _house_list(c, words)
    assert opened, f"no list window for '{words}': {c.text_messages[-2:]}"
    c.edit_house_list(opened[0], "\n".join(names))
    time.sleep(0.5)


# ---------------------------------------------------------------------------------------------- doors

def test_the_owner_opens_the_door_and_a_stranger_cannot(new_player, db, login, items):
    flat = FLAT_01
    owner = _owner(new_player, db, login, flat)
    stranger = new_player(pos=flat.beside, storage=BEGINNER_SET)
    assert _door_is(stranger, flat, items, CLOSED_DOOR), stranger.tiles.get(flat.door)

    since = len(stranger.text_messages)
    _use_door(stranger, flat)
    assert _got(stranger, NOT_USABLE, since), stranger.text_messages[-3:]
    assert not _door_is(stranger, flat, items, OPEN_DOOR, timeout=1), "a stranger opened the house door"

    _use_door(owner, flat)
    assert _door_is(owner, flat, items, OPEN_DOOR), owner.text_messages[-3:]
    assert owner.step(WEST) and owner.pos == flat.door
    assert owner.step(WEST) and owner.pos == flat.inside

    # the door stands open, but the stranger may still neither step in nor close it
    since = len(stranger.text_messages)
    assert not stranger.step(SOUTHWEST), "a stranger walked into the house"
    assert _got(stranger, NOT_INVITED, since), stranger.text_messages[-3:]
    since = len(stranger.text_messages)
    _use_door(stranger, flat)
    assert _got(stranger, NOT_USABLE, since), stranger.text_messages[-3:]
    assert not _door_is(stranger, flat, items, CLOSED_DOOR, timeout=1), "a stranger closed the house door"

    _use_door(owner, flat)                          # the owner closes it from inside
    assert _door_is(owner, flat, items, CLOSED_DOOR)


def test_a_guest_enters_through_the_open_door_but_does_not_open_it(new_player, db, login, items):
    """aleta sio: the guest may be in the house, opening a door takes its door list (aleta grav) or a subowner."""
    flat = FLAT_02
    owner = _owner(new_player, db, login, flat, pos=flat.inside)
    guest = new_player(pos=flat.beside, storage=BEGINNER_SET)
    _set_house_list(owner, "aleta sio", [guest.character.name])
    assert guest.character.name.lower() in _house_list(owner, "aleta sio")[1].lower()

    since = len(guest.text_messages)
    _use_door(guest, flat)
    assert _got(guest, NOT_USABLE, since), guest.text_messages[-3:]
    assert not _door_is(guest, flat, items, OPEN_DOOR, timeout=1)

    _use_door(owner, flat)
    assert _door_is(owner, flat, items, OPEN_DOOR)
    assert owner.step(WEST)                         # make room
    assert guest.step(SOUTHWEST) and guest.pos == flat.door, guest.text_messages[-2:]
    assert guest.step(WEST) and guest.pos == flat.inside, guest.pos


def test_the_door_list_opens_the_door(new_player, db, login, items):
    """aleta grav, said facing the door from inside: the players on that door's list may open it (and nobody else).
    Being on a door list alone does not let you into the house (house tiles need the guest list)."""
    flat = FLAT_03
    owner = _owner(new_player, db, login, flat, pos=flat.inside)
    friend = new_player(pos=flat.beside, storage=BEGINNER_SET)
    owner.turn(EAST)
    time.sleep(0.3)
    _set_house_list(owner, "aleta grav", [friend.character.name])
    assert friend.character.name.lower() in _house_list(owner, "aleta grav")[1].lower()

    _use_door(friend, flat)
    assert _door_is(friend, flat, items, OPEN_DOOR), friend.text_messages[-3:]
    since = len(friend.text_messages)
    assert not friend.step(SOUTHWEST)
    assert _got(friend, NOT_INVITED, since), friend.text_messages[-3:]
    _use_door(friend, flat)
    assert _door_is(friend, flat, items, CLOSED_DOOR)


def test_a_subowner_opens_the_door_and_edits_only_the_guest_list(new_player, db, login, items):
    flat = FLAT_11
    owner = _owner(new_player, db, login, flat, pos=flat.further)
    sub = new_player(pos=flat.beside, storage=BEGINNER_SET)
    stranger = new_player(pos=flat.entry, storage=BEGINNER_SET)
    _set_house_list(owner, "aleta som", [sub.character.name])

    _use_door(sub, flat)
    assert _door_is(sub, flat, items, OPEN_DOOR), sub.text_messages[-3:]
    assert sub.step(SOUTHWEST) and sub.step(WEST) and sub.pos == flat.inside, sub.pos
    sub.turn(EAST)
    time.sleep(0.3)
    assert _house_list(sub, "aleta sio") is not None, "a subowner may edit the guest list"
    since = len(sub.text_messages)
    assert _house_list(sub, "aleta som") is None, "a subowner edited the subowner list"
    assert _got(sub, NOT_POSSIBLE, since)
    since = len(sub.text_messages)
    assert _house_list(sub, "aleta grav") is None, "a subowner edited a door list"
    assert _got(sub, NOT_POSSIBLE, since)

    since = len(stranger.text_messages)
    assert not stranger.step(WEST)
    assert _got(stranger, NOT_INVITED, since)


def test_house_spells_outside_a_house_do_nothing(new_player, items):
    p = new_player(pos=FLAT_01.beside, storage=BEGINNER_SET)
    assert _house_list(p, "aleta sio") is None


# ---------------------------------------------------------------------------------------------- putting players out

def test_alana_sio_puts_a_guest_out_at_the_entrance(new_player, db, login, items):
    flat = FLAT_12
    owner = _owner(new_player, db, login, flat, pos=flat.further)
    guest = db.create_character(pos=flat.inside, town_id=THAIS, storage=BEGINNER_SET)
    _set_house_list(owner, "aleta sio", [guest.name])
    g = login(guest)
    assert g.pos == flat.inside, g.pos

    _cast(g, f'alana sio "{owner.character.name}')        # a guest cannot put the owner out
    time.sleep(1)
    assert owner.pos == flat.further, owner.pos

    _cast(owner, f'alana sio "{guest.name}')
    assert g.wait_for(lambda: g.pos == flat.entry, timeout=3), f"the guest is still at {g.pos}"
    assert owner.pos == flat.further


def test_a_guest_puts_himself_out_but_not_another_guest(new_player, db, login, items):
    """tibia.com manual (2004): "Owners and subowners can kick guests [...] guests can also kick themselves." Needs
    the house.cpp kickPlayer change (rebuild): any guest could put any other guest out."""
    flat = FLAT_14
    owner = _owner(new_player, db, login, flat, pos=flat.further)
    first = db.create_character(pos=flat.inside, town_id=THAIS, storage=BEGINNER_SET)
    second = db.create_character(pos=(flat.inside[0], flat.inside[1] - 1, flat.inside[2]), town_id=THAIS,
                                 storage=BEGINNER_SET)
    _set_house_list(owner, "aleta sio", [first.name, second.name])
    a, b = login(first), login(second)
    b_pos = b.pos
    _cast(a, f'alana sio "{second.name}')
    time.sleep(1)
    assert b.pos == b_pos, "a guest put another guest out"
    _cast(a, f'alana sio "{first.name}')
    assert a.wait_for(lambda: a.pos == flat.entry, timeout=3), f"the guest could not leave: {a.pos}"


def test_taking_a_guest_off_the_list_puts_him_out(new_player, db, login, items):
    """House::setAccessList puts out everyone the new list no longer invites (tibia.com manual, 2004). Needs the
    game.cpp internalTeleport fix (rebuild): it checked the tile the player stood on - in the house he was no longer
    invited to - instead of the destination, so the move out was refused and he stayed inside."""
    flat = FLAT_13
    owner = _owner(new_player, db, login, flat, pos=flat.further)
    guest = db.create_character(pos=flat.inside, town_id=THAIS, storage=BEGINNER_SET)
    _set_house_list(owner, "aleta sio", [guest.name])
    g = login(guest)
    assert g.pos == flat.inside, g.pos
    _set_house_list(owner, "aleta sio", [])
    assert g.wait_for(lambda: g.pos == flat.entry, timeout=3), f"the former guest is still at {g.pos}"


def test_an_uninvited_player_logging_in_in_the_house_appears_at_the_entrance(new_player, db, login, items):
    """tibia.com manual (2004): uninvited players in the house, "or logging in there later, are moved outside
    automatically" (HouseTile::__queryDestination sends him to the house entry)."""
    flat = FLAT_21
    _owner(new_player, db, login, flat).logout()
    stranger = new_player(pos=flat.inside, storage=BEGINNER_SET)
    assert stranger.pos == flat.entry, f"logged in at {stranger.pos}, inside a house he is not invited to"


# ---------------------------------------------------------------------------------------------- owning

def test_buyhouse_needs_premium_and_the_price(new_player, db, login, items):
    """/buyhouse (commands.xml, access 0), said in front of the door facing it, is how a player gets a house today:
    an OT command - in 7.4 houses were auctioned on tibia.com. Premium only; config.lua HousePrice gold a house tile,
    taken from what the player carries."""
    flat = FLAT_22
    price = flat.tiles * TILE_PRICE
    assert price == 1300

    free = new_player(pos=flat.entry, premium_days=0, storage=BEGINNER_SET, inventory={RIGHT: Item(GOLD, 100)})
    free.turn(WEST)
    time.sleep(0.3)
    assert "You need a premium account." in _say_and_read(free, "/buyhouse", "premium")
    free.logout()

    poor = new_player(pos=flat.entry, premium_days=30, storage=BEGINNER_SET, inventory={RIGHT: Item(GOLD, 10)})
    poor.turn(WEST)
    time.sleep(0.3)
    assert "You do not have enough money." in _say_and_read(poor, "/buyhouse", "money")
    poor.logout()

    bag = Item(1988, contents=[Item(GOLD, 100)] * 12)            # 1200 + 100 in the hand
    buyer = new_player(pos=flat.entry, premium_days=30, storage=BEGINNER_SET,
                       inventory={RIGHT: Item(GOLD, 100), BACKPACK: bag})
    buyer.turn(WEST)
    time.sleep(0.3)
    replies = _say_and_read(buyer, "/buyhouse", "bought")
    assert any("successfully bought" in t for t in replies), replies
    _use_door(buyer, flat)
    assert _door_is(buyer, flat, items, OPEN_DOOR), "the new owner cannot open the door"
    assert any("already the owner" in t for t in _say_and_read(buyer, "/buyhouse", "owner"))


def _saved_house_items(db, house_id):
    con = db._connect()
    try:
        row = con.execute("SELECT data FROM map_store WHERE house_id = ?", (house_id,)).fetchone()
        return bytes(row[0]) if row else b""
    finally:
        con.close()


def _wait_saved(db, house_id, server_id, timeout=40):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if server_id.to_bytes(2, "little") in _saved_house_items(db, house_id):
            return True
        time.sleep(1)
    return False


def _drop_sword(owner, flat, items):
    owner.move_item(owner.inventory_pos(RIGHT), owner.inventory[RIGHT].client_id, 0, flat.further, 1)
    sword = items.by_server[SWORD].client_id
    assert owner.wait_for(lambda: _stack(owner, flat.further)[0] == sword, timeout=3), owner.text_messages[-2:]


def test_items_left_in_the_house_stay_after_relog(new_player, db, login, items):
    flat = FLAT_23
    owner = _owner(new_player, db, login, flat, pos=flat.inside, inventory={RIGHT: Item(SWORD)})
    character = owner.character
    _drop_sword(owner, flat, items)
    owner.logout()
    time.sleep(1)
    again = login(character)
    assert again.pos == flat.inside, again.pos
    assert _stack(again, flat.further)[0] == items.by_server[SWORD].client_id, again.tiles.get(flat.further)
    assert _wait_saved(db, flat.id, SWORD), "the sword is not in the house's saved items (map_store)"


def _restart(server):
    """Stop the test server and start it again on the same database (ServerProcess.start would wipe it). The stop is
    a terminate - no shutdown save - so this shows what the timed saves kept."""
    server.stop()
    since = server.log_offset()
    server._log_file = open(server.log_path, "ab")
    server.proc = subprocess.Popen([str(SERVER_DIR / "avesta74.exe"), "-c", str(server.config_path)],
                                   cwd=SERVER_DIR, stdout=server._log_file, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL)
    deadline = time.time() + 180
    while time.time() < deadline:
        if server.proc.poll() is not None:
            raise RuntimeError("the server exited while restarting:\n" + server.log_tail())
        if "Server Running" in server.log()[since:]:
            time.sleep(1)
            server.started_at = time.time()
            return
        time.sleep(0.5)
    raise RuntimeError("the server did not come back:\n" + server.log_tail())


def test_the_house_its_lists_and_items_survive_a_restart(new_player, db, login, items, server):
    """Owner, guest list and the items in the house come back after a restart (tables houses, house_lists,
    map_store). Last in the file: it restarts the session's server."""
    flat = FLAT_24
    owner = _owner(new_player, db, login, flat, pos=flat.inside, inventory={RIGHT: Item(SWORD)})
    guest = db.create_character(pos=flat.beside, town_id=THAIS, storage=BEGINNER_SET)
    _set_house_list(owner, "aleta sio", [guest.name])
    _drop_sword(owner, flat, items)
    assert _wait_saved(db, flat.id, SWORD), "the sword was not saved"
    time.sleep(16)                                  # one more timed save (every 15 s here): owner and lists
    character = owner.character
    owner.logout()
    time.sleep(1)

    _restart(server)
    o = login(character)
    assert o.pos == flat.inside, o.pos
    assert _stack(o, flat.further)[0] == items.by_server[SWORD].client_id, o.tiles.get(flat.further)
    assert guest.name.lower() in _house_list(o, "aleta sio")[1].lower()
    g = login(guest)
    _use_door(o, flat)
    assert _door_is(o, flat, items, OPEN_DOOR)
    assert g.step(SOUTHWEST) and g.pos == flat.door, "the guest list was lost"



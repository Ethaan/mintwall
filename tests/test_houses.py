"""Houses (task.md "Houses: confirm Tibia74-houses.xml loads, rent, doors, ownership commands" and "House doors: test
that owners/invited players can open them and others cannot").

7.4 rules (TibiaWiki, see task.md): only premium characters own houses; the owner keeps lists with house spells said
inside the house - "aleta sio" guests (may enter the house), "aleta som" subowners (open every door, edit the guest
list), "aleta grav" facing a door: who may open that door - and "alana sio <name>" puts a player out at the entrance.
Everyone else can neither open a house door nor step into the house.

The engine: house.cpp (Door::canUse, House::getHouseAccessLevel, kickPlayer, setAccessList), housetile.cpp
(__queryAdd: "You are not invited."), spells.cpp (the House* spells), commands.cpp (/owner, /gethouse). Getting a
house: /buyhouse (talkactions/scripts/buyhouse.lua, data/lib/houses.lua), handed over at the next server save.
The houses used are the Sunset Homes flats in Thais (one door each; no other test uses them)."""
import functools
import json
import re
import socket
import sqlite3
import subprocess
import time

import pytest

from tibia74 import (BACKPACK, EAST, NORTH, NORTHWEST, SOUTHWEST, WEST, GameClient, Item, RIGHT, SERVER_DIR,
                     ServerProcess)
from tibia74.db import Character, TestDatabase as _Database      # (not Test*: pytest would try to collect it)
from tibia74.net import Writer
from tibia74.server import ROOT, RUN_DIR
from tibia74.otbm import read_tiles, read_towns

WORLD = SERVER_DIR / "data" / "world"
BEGINNER_SET = {30001: 1}
THAIS = 2
CLOSED_DOOR, OPEN_DOOR = 1219, 1220                 # the flats' doors (actions.xml: increment.lua opens them)
NOT_USABLE = "You can not use this object."          # RET_CANNOTUSETHISOBJECT: a house door you may not open
NOT_INVITED = "You are not invited."                # RET_PLAYERISNOTINVITED: a house tile you may not enter
NOT_POSSIBLE = "Sorry, not possible."
SWORD, GOLD = 2376, 2148


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


def test_alana_sio_alone_puts_the_caster_out(new_player, db, login, items):
    """"alana sio" with no name puts the one who says it out, as later servers do (House::kickPlayer; decided with the
    user 2026-10-04). Needs the rebuild."""
    flat = FLAT_24
    owner = _owner(new_player, db, login, flat, pos=flat.inside)
    assert owner.pos == flat.inside, owner.pos
    _cast(owner, "alana sio")
    assert owner.wait_for(lambda: owner.pos == flat.entry, timeout=3), f"the owner is still at {owner.pos}"


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

def test_every_house_has_a_rent():
    """Rents from Tibiantis' house list (tools/apply-tibiantis-rents.py, docs/reference-74/tibiantis/houses.json);
    the houses it does not have (Ankrahmun) at its median gold per house tile. A rent of 0 would never be charged
    (Houses::payHouses skips it) and /buyhouse would hand the house over for nothing."""
    houses = _houses_xml()
    free = [f"{hid} {h['name']}" for hid, h in houses.items() if int(h.get("rent") or 0) <= 0]
    assert not free, f"{len(free)} houses without a rent: {free[:10]}"
    tibiantis = {(h["town"], h["name"]): h["rent"]
                 for h in json.loads((ROOT / "docs" / "reference-74" / "tibiantis" / "houses.json")
                                     .read_text(encoding="utf-8"))["houses"]}
    assert tibiantis[("Thais", "Sunset Homes, Flat 22")] == int(houses[FLAT_22.id]["rent"]) == FLAT_22_RENT
    assert tibiantis[("Thais", "Sunset Homes, Flat 23")] == int(houses[FLAT_23.id]["rent"]) == FLAT_23_RENT
    assert tibiantis[("Thais", "Spiritkeep")] == int(houses[SPIRITKEEP]["rent"]) == SPIRITKEEP_RENT
    assert houses[SPIRITKEEP].get("guildhall") == "true" and not houses[FLAT_22.id].get("guildhall")


def test_the_engine_reads_the_guildhalls_of_the_houses_file(server):
    """Houses::loadHousesXML reads guildhall="true" (isHouseGuildHall, House::isGuildHall: one house and one guildhall
    per account) and logs the ids it read. Needs the rebuild (older builds ignored the attribute)."""
    line = re.search(r"^> Guildhalls:(.*)$", server.log(), re.M)
    assert line, "no '> Guildhalls:' line in the log: an older build"
    assert {int(i) for i in line.group(1).split()} == \
        {hid for hid, h in _houses_xml().items() if h.get("guildhall") == "true"}


def test_the_old_build_guildhall_list_of_the_scripts_matches_the_houses_file():
    """data/lib/houses.lua keeps the guildhall ids for builds whose isHouseGuildHall was a stub (OLD_BUILD_GUILDHALLS;
    remove both once no server runs such a build)."""
    lua = (SERVER_DIR / "data" / "lib" / "houses.lua").read_text("latin-1")
    listed = {int(i) for i in re.findall(r"\d+", re.search(r"OLD_BUILD_GUILDHALLS = \{(.*?)\}", lua, re.S).group(1))}
    assert listed == {hid for hid, h in _houses_xml().items() if h.get("guildhall") == "true"}


def test_buyhouse_away_from_a_door_explains_itself(new_player):
    p = new_player(pos=FLAT_01.beside, premium_days=30, storage=BEGINNER_SET)
    assert any("Stand in front of the door" in t for t in _say_and_read(p, "/buyhouse", "door"))
    assert any("has not asked for a house" in t for t in _say_and_read(p, "/cancelhouse", "house"))


def test_a_new_owner_puts_everyone_out(new_player, db, login, items):
    """House::setHouseOwner puts out everyone in the house (the old owner and his guests) when the owner changes."""
    flat = FLAT_22
    owner = _owner(new_player, db, login, flat, pos=flat.inside)
    guest = db.create_character(pos=FLAT_22_ROOM, town_id=THAIS, storage=BEGINNER_SET)
    _set_house_list(owner, "aleta sio", [guest.name])
    g = login(guest)
    assert g.pos == FLAT_22_ROOM, g.pos
    heir = db.create_character(pos=THAIS_ROAD, premium_days=30, town_id=THAIS, storage=BEGINNER_SET)
    gm = new_player(pos=flat.further, group_id=3, storage=BEGINNER_SET)
    gm.say(f"/owner {heir.name}")
    assert owner.wait_for(lambda: owner.pos == flat.entry, timeout=5), f"the old owner is still at {owner.pos}"
    assert g.wait_for(lambda: g.pos == flat.entry, timeout=5), f"his guest is still at {g.pos}"
    assert gm.wait_for(lambda: flat.name in _house_of(gm, heir.name), timeout=5), _house_of(gm, heir.name)


def _give_house(new_player, house_id, character):
    """A GM standing on a bare tile of the house makes `character` its owner (/owner)."""
    tiles, _, stacks = _map_houses()
    spot = next(p for p in sorted(tiles[house_id]) if len(stacks[p]) == 1)
    gm = new_player(pos=spot, group_id=3, storage=BEGINNER_SET)
    assert gm.pos == spot, gm.pos
    gm.say(f"/owner {character.name}")
    house = _houses_xml()[house_id]["name"]
    assert gm.wait_for(lambda: house in _house_of(gm, character.name), timeout=5), _house_of(gm, character.name)
    gm.logout()


def test_sellhouse_keeps_one_house_per_account(new_player, db, login):
    """/sellhouse <name> offers the house in a trade (Commands::sellHouse); talkactions/scripts/sellhouse.lua refuses
    a receiver first by the rules of /buyhouse (data/lib/houses.lua houseTransferProblem): his account may not have
    another house, he needs premium."""
    seller_char = db.create_character(pos=THAIS_ROAD, premium_days=30, town_id=THAIS, storage=BEGINNER_SET)
    _give_house(new_player, UPPER_SWAMP_LANE_4, seller_char)
    landlord = db.create_character(pos=THAIS_ROAD, premium_days=30, town_id=THAIS, storage=BEGINNER_SET)
    _give_house(new_player, UPPER_SWAMP_LANE_2, landlord)
    # another character on the landlord's account (premium is the account's)
    other = db.create_character(pos=(THAIS_ROAD[0] + 1, THAIS_ROAD[1], 7), town_id=THAIS, storage=BEGINNER_SET)
    _sql(db.path, "UPDATE players SET account_id = ? WHERE id = ?", landlord.account, other.guid)
    other = Character(other.guid, other.name, landlord.account, landlord.password)
    seller = login(seller_char)
    login(other)
    replies = _say_and_read(seller, f"/sellhouse {other.name}", "house")
    assert any(f"{other.name}'s account already has a house" in t for t in replies), replies

    free = new_player(pos=(THAIS_ROAD[0], THAIS_ROAD[1] + 1, 7), premium_days=0, storage=BEGINNER_SET)
    assert any("has no premium account" in t for t in _say_and_read(seller, f"/sellhouse {free.character.name}",
                                                                      "premium"))

    buyer = new_player(pos=(THAIS_ROAD[0] - 1, THAIS_ROAD[1], 7), premium_days=30, storage=BEGINNER_SET)
    mark = len(seller.text_messages)
    seller.say(f"/sellhouse {buyer.character.name}")              # allowed: the engine offers the trade
    time.sleep(1.5)
    said = [t for _, t in seller.text_messages[mark:]]
    assert not any("account" in t or "premium" in t or "guild" in t for t in said), said


def test_a_house_owner_who_leads_a_guild_may_also_ask_for_a_guildhall(new_player, db, login):
    """One house and one guildhall per account, like Tibiantis (data/lib/houses.lua, decided with the user
    2026-10-04): a guild leader who owns a house may ask for a guildhall, but his account may not ask for a second
    house. The request is withdrawn at the end (/cancelhouse)."""
    leader_char = db.create_character(pos=SPIRITKEEP_ENTRY, premium_days=30, town_id=THAIS, storage=BEGINNER_SET)
    _give_house(new_player, LOWER_SWAMP_LANE_1, leader_char)
    _put_in_depot(db.path, leader_char.guid, THAIS, [(CRYSTAL, 2)])                   # 20000: Spiritkeep's rent
    con = sqlite3.connect(db.path)
    try:
        guild = con.execute("INSERT INTO guilds (name, ownerid, creationdata) VALUES (?, ?, 0)",
                            (f"Keepers {leader_char.guid}", leader_char.guid)).lastrowid
        rank = dict(con.execute("SELECT level, id FROM guild_ranks WHERE guild_id = ?", (guild,)))
        con.execute("UPDATE players SET rank_id = ? WHERE id = ?", (rank[3], leader_char.guid))   # Leader
        con.commit()
    finally:
        con.close()
    alt_char = db.create_character(pos=FLAT_23.entry, town_id=THAIS, storage=BEGINNER_SET)   # the same account
    _sql(db.path, "UPDATE players SET account_id = ? WHERE id = ?", leader_char.account, alt_char.guid)
    alt_char = Character(alt_char.guid, alt_char.name, leader_char.account, leader_char.password)

    leader = login(leader_char)
    assert leader.pos == SPIRITKEEP_ENTRY, leader.pos
    replies = _buy(leader, NORTH, "house")
    assert any(WILL_BE_YOURS in t and "Spiritkeep" in t for t in replies), replies
    leader.logout()
    time.sleep(0.5)

    alt = login(alt_char)
    assert alt.pos == FLAT_23.entry, alt.pos
    replies = _buy(alt, WEST, "house")
    assert any("Your account already has a house: Lower Swamp Lane 1" in t for t in replies), replies
    assert any("Spiritkeep" in t for t in _buy(alt, NORTH, "house")), "the pending guildhall request is not shown"
    said = _say_and_read(alt, "/cancelhouse", "withdrawn")
    assert any("withdrawn the request for the house Spiritkeep" in t for t in said), said


def _make_guild_leader(db_path, guid, name):
    con = sqlite3.connect(db_path)
    try:
        guild = con.execute("INSERT INTO guilds (name, ownerid, creationdata) VALUES (?, ?, 0)",
                            (name, guid)).lastrowid
        rank = dict(con.execute("SELECT level, id FROM guild_ranks WHERE guild_id = ?", (guild,)))
        con.execute("UPDATE players SET rank_id = ? WHERE id = ?", (rank[3], guid))      # Leader
        con.commit()
    finally:
        con.close()


def _trade_house(seller, buyer):
    """After /sellhouse: the buyer offers his right-hand item for the house document, both accept."""
    buyer._send(Writer().u8(0x7D).position(buyer.inventory_pos(RIGHT)).u16(buyer.inventory[RIGHT].client_id).u8(0)
                .u32(seller.player_id))
    time.sleep(0.5)
    seller._send(Writer().u8(0x7F))
    time.sleep(0.3)
    buyer._send(Writer().u8(0x7F))
    time.sleep(1)


def test_a_house_owner_gets_a_guildhall_through_sellhouse(new_player, db, login):
    """One house and one guildhall per account: Commands::sellHouse refused every receiver who owned a house ("Trade
    player already owns a house."), now only one whose account has one of the same kind (House::canTransferTo). The
    seller owns a house and a guildhall: /sellhouse sells the house he stands in or faces, else the one named after a
    comma (with neither it asks which). Needs the rebuild."""
    seller_char = db.create_character(pos=THAIS_ROAD, premium_days=30, town_id=THAIS, storage=BEGINNER_SET)
    _give_house(new_player, SORCERERS_AVENUE_1A, seller_char)       # (/gethouse names the lowest id: this one first)
    _give_house(new_player, HALLS_OF_THE_ADVENTURERS, seller_char)
    buyer_char = db.create_character(pos=(THAIS_ROAD[0] + 1, THAIS_ROAD[1], 7), premium_days=30, town_id=THAIS,
                                     storage=BEGINNER_SET, inventory={RIGHT: Item(SWORD)})
    _give_house(new_player, LOWER_SWAMP_LANE_3, buyer_char)
    _make_guild_leader(db.path, buyer_char.guid, f"Adventurers {buyer_char.guid}")
    seller, buyer = login(seller_char), login(buyer_char)

    replies = _say_and_read(seller, f"/sellhouse {buyer_char.name}", "house")
    assert any("You own a house and a guildhall" in t for t in replies), replies

    mark = len(seller.text_messages)
    seller.say(f"/sellhouse {buyer_char.name}, Halls of the Adventurers")
    time.sleep(1)
    said = [t for _, t in seller.text_messages[mark:]]
    assert not any("own" in t or "account" in t or "guild" in t or "For now" in t for t in said), said
    _trade_house(seller, buyer)

    gm = new_player(pos=(THAIS_ROAD[0], THAIS_ROAD[1] + 1, 7), group_id=3, storage=BEGINNER_SET)
    assert gm.wait_for(lambda: "Halls of the Adventurers" in _house_of(gm, buyer_char.name), timeout=5), \
        (_house_of(gm, buyer_char.name), buyer.text_messages[-3:])          # /gethouse: the lowest id he owns
    assert "Sorcerer's Avenue 1a" in _house_of(gm, seller_char.name)


def test_a_house_request_made_during_the_trade_stops_the_sale(new_player, db, login, items):
    """/sellhouse checks the receiver when the trade is offered; his account may ask for a house (/buyhouse, or a
    website row in house_requests) while the trade window is open. The engine checks again when the trade is accepted
    (Game::playerAcceptTrade, House::canTransferTo; House::executeTransfer once more): refused, nobody's items move.
    Needs the rebuild."""
    seller_char = db.create_character(pos=THAIS_ROAD, premium_days=30, town_id=THAIS, storage=BEGINNER_SET)
    _give_house(new_player, UPPER_SWAMP_LANE_8, seller_char)
    buyer_char = db.create_character(pos=(THAIS_ROAD[0] - 1, THAIS_ROAD[1], 7), premium_days=30, town_id=THAIS,
                                     storage=BEGINNER_SET, inventory={RIGHT: Item(SWORD)})
    seller, buyer = login(seller_char), login(buyer_char)

    mark = len(seller.text_messages)
    seller.say(f"/sellhouse {buyer_char.name}")
    time.sleep(1)
    said = [t for _, t in seller.text_messages[mark:]]
    assert not any("account" in t or "premium" in t or "own" in t for t in said), said

    _sql(db.path, "INSERT INTO house_requests (house_id, player_id, account_id, created, state) VALUES (?, ?, ?, ?, 0)",
         UPPER_SWAMP_LANE_10, buyer_char.guid, buyer_char.account, int(time.time()))
    try:
        mark = len(buyer.text_messages)
        _trade_house(seller, buyer)
        assert _got(buyer, f"{buyer_char.name}'s account has asked for a house already", mark), \
            buyer.text_messages[-3:]
        sword = items.by_server[SWORD].client_id
        assert buyer.inventory.get(RIGHT) and buyer.inventory[RIGHT].client_id == sword, buyer.inventory
        assert not any(i.client_id == sword for i in seller.inventory.values()), seller.inventory
        gm = new_player(pos=(THAIS_ROAD[0], THAIS_ROAD[1] + 1, 7), group_id=3, storage=BEGINNER_SET)
        assert "Upper Swamp Lane 8" in _house_of(gm, seller_char.name)
        assert "does not own any house" in _house_of(gm, buyer_char.name)
    finally:
        _sql(db.path, "DELETE FROM house_requests WHERE account_id = ?", buyer_char.account)


# ---------------------------------------------------------------------------------------------- buying a house

UPPER_SWAMP_LANE_2, UPPER_SWAMP_LANE_4 = 53, 54     # Thais houses no other test here uses
LOWER_SWAMP_LANE_1, LOWER_SWAMP_LANE_3 = 55, 56
UPPER_SWAMP_LANE_8, UPPER_SWAMP_LANE_10 = 57, 59
SORCERERS_AVENUE_1A = 61
HALLS_OF_THE_ADVENTURERS = 3                        # a Thais guildhall

THAIS_ROAD = (32369, 32245, 7)                      # just south of the Thais temple
FLAT_22_RENT, FLAT_23_RENT = 520, 860               # Tibiantis' rents
SPIRITKEEP, SPIRITKEEP_RENT = 1, 19210              # a Thais guildhall
SPIRITKEEP_ENTRY = (32265, 32316, 7)                # its front door is north of it
FLAT_22_ROOM = (32330, 32238, 5)                    # a free tile of Flat 22's room (south-west of `inside`)
OWNER_SPOT = (32330, 32236, 5)                      # and another one (north-west of `inside`)
GOLD, PLATINUM, CRYSTAL = 2148, 2152, 2160
LOCKER, DEPOT_CHEST = 2589, 2594                    # Player::getDepot: a locker with the depot chest in it
CARLIN = 3
SAVE_IN, MINUTE = 150, 6                            # serversave.lua's test hooks (see test_server_save.py)
WILL_BE_YOURS = "It will be yours after the next server save"


def _put_in_depot(db_path, guid, depot, coins):
    """Coins [(item id, count)] in the depot chest of the character's depot `depot` (= town id), saved the way the
    engine saves a depot (player_depotitems: the locker's pid is the depot id)."""
    con = sqlite3.connect(db_path)
    try:
        sid = (con.execute("SELECT MAX(sid) FROM player_depotitems WHERE player_id = ?", (guid,)).fetchone()[0]
               or 1000) + 1
        rows = [(guid, depot, sid, LOCKER, 1), (guid, sid, sid + 1, DEPOT_CHEST, 1)]
        rows += [(guid, sid + 1, sid + 2 + i, item, count) for i, (item, count) in enumerate(coins)]
        con.executemany("INSERT INTO player_depotitems (player_id, pid, sid, itemtype, count, attributes)"
                        " VALUES (?, ?, ?, ?, ?, x'')", rows)
        con.commit()
    finally:
        con.close()


def _depot_money(db, guid, depot):
    value = {GOLD: 1, PLATINUM: 100, CRYSTAL: 10000}
    con = db._connect()
    try:
        rows = con.execute("SELECT pid, sid, itemtype, count FROM player_depotitems WHERE player_id = ?",
                           (guid,)).fetchall()
    finally:
        con.close()
    parent = {sid: pid for pid, sid, _, _ in rows}
    money = 0
    for pid, sid, itemtype, count in rows:
        while pid in parent:
            pid = parent[pid]
        if pid == depot and itemtype in value:
            money += value[itemtype] * max(1, count)
    return money


def _house_row(db, house_id):
    con = db._connect()
    try:
        return con.execute("SELECT owner, paid FROM houses WHERE id = ?", (house_id,)).fetchone()
    finally:
        con.close()


def _requests(db):
    con = db._connect()
    try:
        return con.execute("SELECT house_id, player_id, state FROM house_requests ORDER BY id").fetchall()
    finally:
        con.close()


def _sql(db_path, query, *args):
    con = sqlite3.connect(db_path)
    try:
        con.execute(query, args)
        con.commit()
    finally:
        con.close()


def _buy(c, facing, expect):
    """/buyhouse facing `facing` -> the answers (the reply comes once the character's save is written)."""
    c.turn(facing)
    time.sleep(0.3)
    return _say_and_read(c, "/buyhouse", expect, timeout=8)


class Cast:
    """The characters of the end-to-end test, made in its server's fresh database."""


def _cast_setup(cast):
    def setup(db_path):
        db = _Database(db_path)
        mk = functools.partial(db.create_character, premium_days=30, town_id=THAIS, storage=BEGINNER_SET)
        cast.buyer = mk(pos=FLAT_22.entry)
        _put_in_depot(db_path, cast.buyer.guid, THAIS, [(PLATINUM, 5), (GOLD, 20), (GOLD, 100)])   # 620 gold
        alt = mk(pos=FLAT_23.entry)                     # a second character on the buyer's account
        _sql(db_path, "UPDATE players SET account_id = ? WHERE id = ?", cast.buyer.account, alt.guid)
        cast.alt = Character(alt.guid, alt.name, cast.buyer.account, cast.buyer.password)
        cast.rival = mk(pos=FLAT_22.entry)
        _put_in_depot(db_path, cast.rival.guid, THAIS, [(CRYSTAL, 1)])
        cast.landlord = mk(pos=THAIS_ROAD)
        cast.taker = mk(pos=FLAT_21.entry)
        _put_in_depot(db_path, cast.taker.guid, THAIS, [(CRYSTAL, 1)])
        # the rent in another town's depot and in the backpack: neither counts
        cast.poor = mk(pos=FLAT_23.entry, inventory={BACKPACK: Item(1988, contents=[Item(GOLD, 100)] * 10)})
        _put_in_depot(db_path, cast.poor.guid, THAIS, [(GOLD, 100)])
        _put_in_depot(db_path, cast.poor.guid, CARLIN, [(CRYSTAL, 1)])
        cast.free = mk(pos=FLAT_23.entry, premium_days=0)
        _put_in_depot(db_path, cast.free.guid, THAIS, [(CRYSTAL, 1)])
        cast.member = mk(pos=SPIRITKEEP_ENTRY)
        _put_in_depot(db_path, cast.member.guid, THAIS, [(CRYSTAL, 3)])
        cast.leader = mk(pos=SPIRITKEEP_ENTRY)
        _put_in_depot(db_path, cast.leader.guid, THAIS, [(CRYSTAL, 2)])                         # 20000 gold
        cast.quitter = mk(pos=FLAT_24.entry)
        _put_in_depot(db_path, cast.quitter.guid, THAIS, [(CRYSTAL, 1)])
        cast.lapsed = mk(pos=FLAT_24.entry)
        _put_in_depot(db_path, cast.lapsed.guid, THAIS, [(CRYSTAL, 1)])
        con = sqlite3.connect(db_path)
        con.execute("INSERT INTO houses (id, owner, paid, warnings, lastwarning) VALUES (?, ?, ?, 0, 0)",
                    (FLAT_21.id, cast.landlord.guid, int(time.time()) + 20 * 86400))
        con.execute("INSERT INTO guilds (id, name, ownerid, creationdata) VALUES (1, 'Spirits', ?, 0)",
                    (cast.leader.guid,))
        rank = dict(con.execute("SELECT level, id FROM guild_ranks WHERE guild_id = 1"))   # the schema's trigger:
        con.execute("UPDATE players SET rank_id = ? WHERE id = ?", (rank[3], cast.leader.guid))  # Leader 3,
        con.execute("UPDATE players SET rank_id = ? WHERE id = ?", (rank[1], cast.member.guid))  # Member 1
        con.commit()
        con.close()
    return setup


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_buying_a_house_end_to_end(items):
    """The stand-in for the 7.4 auction (task.md Q17, data/lib/houses.lua): /buyhouse in front of the door asks for
    the house, the next server save hands it over and Houses::payHouses takes the first month's rent from the depot of
    the house's town. Then the house with its new owner: guests, a stranger, a kick, off the list, a mass kick.
    Runs a server of its own (the save shuts it down; it comes back on the same database without the save)."""
    cast = Cast()
    srv = ServerProcess(port=_free_port(), run_dir=RUN_DIR / "house-save", setup=_cast_setup(cast),
                        config={"ServerSaveEnabled": True, "ServerSaveTestIn": SAVE_IN,
                                "ServerSaveTestMinute": MINUTE})
    srv.start()
    started = time.time()
    db = _Database(srv.db_path)
    clients = []

    def login(character):
        c = GameClient(items, port=srv.port)
        c.login(character.account, character.password, character.name)
        clients.append(c)
        return c

    def logout(c):
        c.logout()
        time.sleep(0.5)

    try:
        # --- before the save: the request and the refusals
        buyer = login(cast.buyer)
        assert buyer.pos == FLAT_22.entry, buyer.pos
        replies = _buy(buyer, WEST, "house")
        assert any(WILL_BE_YOURS in t and "Sunset Homes, Flat 22" in t for t in replies), replies
        assert any("already asked for a house" in t for t in _buy(buyer, WEST, "house"))
        replies = _buy(buyer, NORTH, "house")                  # not facing a door: the pending request
        assert any("has asked for the house Sunset Homes, Flat 22" in t for t in replies), replies
        logout(buyer)

        alt = login(cast.alt)                                   # the same account, another house
        assert any("Your account has already asked for a house: Sunset Homes, Flat 22" in t
                   for t in _buy(alt, WEST, "house")), alt.text_messages[-3:]
        logout(alt)

        rival = login(cast.rival)                               # first come, first served
        assert rival.pos == FLAT_22.entry, rival.pos
        assert any("Someone has already asked for this house" in t for t in _buy(rival, WEST, "house"))
        logout(rival)

        taker = login(cast.taker)
        assert any("This house already has an owner." in t for t in _buy(taker, WEST, "owner"))
        logout(taker)

        poor = login(cast.poor)
        replies = _buy(poor, WEST, "gold")
        assert any(f"You need the first month's rent of {FLAT_23_RENT} gold in your depot in Thais. You have 100"
                   " gold there." in t for t in replies), replies
        logout(poor)

        free = login(cast.free)
        assert any("You need a premium account." in t for t in _buy(free, WEST, "premium"))
        logout(free)

        member = login(cast.member)
        assert member.pos == SPIRITKEEP_ENTRY, member.pos
        assert any("Only the leader of a guild can rent a guildhall." in t for t in _buy(member, NORTH, "guild"))
        logout(member)

        leader = login(cast.leader)
        assert any(WILL_BE_YOURS in t for t in _buy(leader, NORTH, "house")), leader.text_messages[-3:]
        logout(leader)

        quitter = login(cast.quitter)
        assert any(WILL_BE_YOURS in t for t in _buy(quitter, WEST, "house"))
        assert any("withdrawn the request for the house Sunset Homes, Flat 24" in t
                   for t in _say_and_read(quitter, "/cancelhouse", "house"))
        logout(quitter)

        lapsed = login(cast.lapsed)                             # the house is free again
        assert any(WILL_BE_YOURS in t for t in _buy(lapsed, WEST, "house"))
        logout(lapsed)
        _sql(srv.db_path, "UPDATE accounts SET premend = 0 WHERE id = ?", cast.lapsed.account)   # premium runs out

        assert sorted(_requests(db)) == sorted([(FLAT_22.id, cast.buyer.guid, 0), (SPIRITKEEP, cast.leader.guid, 0),
                                                (FLAT_24.id, cast.lapsed.guid, 0)]), _requests(db)
        assert time.time() - started < SAVE_IN - 5 * MINUTE - 5, "too slow: the logins close before the save"

        # --- the save
        try:
            code = srv.proc.wait(timeout=SAVE_IN + 120)
        except subprocess.TimeoutExpired:
            pytest.fail("the server did not exit after the save:\n" + srv.log_tail(20), pytrace=False)
        assert code == 10, (code, srv.log_tail(20))
        log = srv.log()
        assert f"house Sunset Homes, Flat 22 handed over to {cast.buyer.name}" in log, srv.log_tail(30)
        assert f"house Spiritkeep handed over to {cast.leader.name}" in log
        assert f"request of {cast.lapsed.name} for house Sunset Homes, Flat 24 cancelled" in log
        assert _house_row(db, FLAT_22.id)[0] == cast.buyer.guid
        assert _house_row(db, FLAT_22.id)[1] > time.time() + 29 * 86400, "the first month is not paid"
        assert _depot_money(db, cast.buyer.guid, THAIS) == 620 - FLAT_22_RENT
        assert _house_row(db, SPIRITKEEP)[0] == cast.leader.guid
        assert _depot_money(db, cast.leader.guid, THAIS) == 20000 - SPIRITKEEP_RENT
        assert (_house_row(db, FLAT_24.id) or (0,))[0] == 0
        assert _depot_money(db, cast.lapsed.guid, THAIS) == 10000

        # --- after the save: the same database, no save this time
        with open(srv.config_path, "a", encoding="latin-1") as f:
            f.write("\nServerSaveEnabled = false\n")
        _restart(srv)
        since = srv.log_offset()

        lapsed = login(cast.lapsed)
        assert lapsed.wait_for(lambda: any("was cancelled at the server save: You need a premium account." in t
                                           for _, t in lapsed.text_messages), timeout=5), lapsed.text_messages
        logout(lapsed)

        owner = login(cast.buyer)
        assert owner.wait_for(lambda: any(f"The house Sunset Homes, Flat 22 is yours now. The first month's rent of"
                                          f" {FLAT_22_RENT} gold was taken from your depot in Thais." in t
                                          for _, t in owner.text_messages), timeout=5), owner.text_messages
        assert _requests(db) == [(SPIRITKEEP, cast.leader.guid, 1)], _requests(db)   # shown once, then deleted

        flat = FLAT_22
        owner.turn(WEST)
        time.sleep(0.3)
        _use_door(owner, flat)
        assert _door_is(owner, flat, items, OPEN_DOOR), owner.text_messages[-3:]
        assert owner.step(WEST) and owner.step(WEST) and owner.pos == flat.inside, owner.pos
        assert owner.step(NORTHWEST) and owner.pos == OWNER_SPOT, owner.pos     # out of the way

        friend_char = db.create_character(pos=flat.beside, town_id=THAIS, storage=BEGINNER_SET)
        guest_char = db.create_character(pos=FLAT_22_ROOM, town_id=THAIS, storage=BEGINNER_SET)
        stranger_char = db.create_character(pos=flat.beside, town_id=THAIS, storage=BEGINNER_SET)
        _set_house_list(owner, "aleta sio", [friend_char.name, guest_char.name])

        friend = login(friend_char)                             # in through the open door
        assert friend.pos == flat.beside, friend.pos
        assert friend.step(SOUTHWEST) and friend.step(WEST) and friend.pos == flat.inside, friend.pos
        guest = login(guest_char)                               # invited: may log in inside
        assert guest.pos == FLAT_22_ROOM, guest.pos

        stranger = login(stranger_char)
        assert stranger.pos == flat.beside, stranger.pos
        mark = len(stranger.text_messages)
        assert not stranger.step(SOUTHWEST), "a stranger walked into the house"
        assert _got(stranger, NOT_INVITED, mark)
        logout(stranger)

        _cast(owner, f'alana sio "{friend_char.name}')          # kick one
        assert friend.wait_for(lambda: friend.pos == flat.entry, timeout=3), f"the friend is still at {friend.pos}"
        assert guest.pos == FLAT_22_ROOM
        assert friend.step(WEST) and friend.step(WEST) and friend.pos == flat.inside, friend.pos   # still invited

        _set_house_list(owner, "aleta sio", [guest_char.name])   # off the list: out
        assert friend.wait_for(lambda: friend.pos == flat.entry, timeout=3), f"the friend is still at {friend.pos}"
        time.sleep(0.5)
        assert guest.pos == FLAT_22_ROOM, "the guest still on the list was put out"

        _set_house_list(owner, "aleta sio", [])                   # the mass kick: an empty guest list
        assert guest.wait_for(lambda: guest.pos == flat.entry, timeout=3), f"the guest is still at {guest.pos}"
        assert owner.pos == OWNER_SPOT, "the owner was put out"

        errors = srv.lua_errors(since=since)
        assert not errors, errors[:3]
    finally:
        for c in clients:
            try:
                c.logout()
            except Exception:
                pass
        srv.stop()
    errors = srv.lua_errors()
    assert not errors, "server logged Lua errors:\n\n" + "\n\n".join(errors[:5])


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



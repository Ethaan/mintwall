"""What a premium account unlocks in 7.4, and that a free account is refused each of it (docs/reference-74/premium.md).

tibia.com "Features of Premium Accounts" (last modified 30 Nov 2004, two weeks before 7.4): the premium areas (Edron,
Darama, the Rookgaard premium side - reached by ship, carpet or King's Bridge), login when the world is full, the
spells of the magic guild of Edron, promotion, houses, guild leadership, Premia, private chat channels and a VIP list
of 50 (20 without, tibia.com manual "Communication" 2004), account personalisation. Tibiantis FAQ adds beds and three
more outfits per sex.

Covered elsewhere: the promotion (test_promotion.py: a free account is refused), houses (test_houses.py
test_buying_a_house_end_to_end: "You need a premium account."), King's Bridge and the Rookgaard premium shops
(test_rookgaard.py), ships to Carlin (test_travel.py), premium running out (test_premium_expiry.py: premium areas
from the map, moved to Thais, the kept outfit).

Some tests here need the engine rebuilt (server/build.bat) - their docstrings say so: player.cpp addVIP (20 / 50)
and chat.cpp createChannel (no private channel for a free account)."""
import re
import time

import pytest

import tibia74.client as client_module
from tibia74 import BACKPACK, Item, SERVER_DIR
from tibia74.db import BEGINNER_SET_GIVEN
from tibia74.net import Writer
from tibia74.npcs import load_npcs
from tibia74.premium import read_lua_boxes
from tibia74.quest import next_to, talk_to
from tibia74.server import TESTER_GROUP

NPCS = load_npcs(SERVER_DIR)
NPC_DIR = SERVER_DIR / "data" / "npc"
BOXES = read_lua_boxes(SERVER_DIR / "data" / "creaturescripts" / "lib" / "premium_areas.lua")
BEGINNER_SET = {BEGINNER_SET_GIVEN: 1}
NEED_PREMIUM = "You need a premium account."             # RET_YOUNEEDPREMIUMACCOUNT
NOT_USABLE = "You can not use this object."              # RET_CANNOTUSETHISOBJECT
SORCERER, DRUID, PALADIN, KNIGHT = 1, 2, 3, 4


def premium_area(pos):
    """"mainland" / "rookgaard" for a premium tile (creaturescripts/lib/premium_areas.lua), None for free ground."""
    return next((name for lo, hi, name in BOXES if all(lo[i] <= pos[i] <= hi[i] for i in range(3))), None)


@pytest.fixture
def recorded(monkeypatch):
    """recorded(opcode, read) -> list: what every client parses for that server packet from now on, read(c, r) each."""
    def record(opcode, read):
        seen = []

        def handler(c, r):
            seen.append((c, read(c, r)))
        monkeypatch.setitem(client_module._HANDLERS, opcode, handler)
        return seen
    return record


def _of(seen, c):
    return [what for who, what in seen if who is c]


# ---------------------------------------------------------------------------------------------- premium areas

# Every ship, carpet and the Kazordoon-Cormaya boat that leaves from free ground for a premium area. tibia.com 2004:
# "The only way for a traveller to reach them is by boat, so only premium players can go there" (manual "World"),
# the captains "will take you to almost any place for a hefty fee, provided you are a premium player".
FROM_FREE_GROUND = [
    ("Captain Bluebear", ["hi", "edron", "yes"]),       # Thais
    ("Captain Bluebear", ["bring me to edron"]),        # the one-line shortcut, without greeting
    ("Captain Greyhound", ["hi", "edron", "yes"]),      # Carlin
    ("Captain Seagull", ["hi", "edron", "yes"]),        # Ab'Dendriel
    ("Captain Fearless", ["hi", "darashia", "yes"]),    # Venore
    ("Captain Fearless", ["hi", "ankrahmun", "yes"]),
    ("Uzon", ["hi", "darashia", "yes"]),                # the carpet on Femor Hills
    ("Uzon", ["hi", "edron", "yes"]),
    ("Brodrosch", ["hi", "cormaya", "yes"]),            # Kazordoon
]


@pytest.mark.parametrize("npc, lines", FROM_FREE_GROUND,
                         ids=[f"{n}-{' '.join(lines)}" for n, lines in FROM_FREE_GROUND])
def test_a_free_account_is_refused_every_trip_into_a_premium_area(new_player, npc, lines):
    pos = NPCS[npc].pos
    assert premium_area(pos) is None, f"{npc} stands in a premium area - a free account cannot get there"
    p = next_to(new_player, pos, level=50, premium_days=0, group_id=TESTER_GROUP, storage=BEGINNER_SET,
                inventory={BACKPACK: Item(1988, contents=[Item(2160, 1)])})        # 10,000 gp
    start = p.pos
    said = talk_to(p, npc, *lines)
    p.sleep(1.5)
    assert premium_area(p.pos) is None and max(abs(p.pos[0] - start[0]), abs(p.pos[1] - start[1])) <= 3, \
        f"a free account travelled to {p.pos}; {npc} said {said}"
    assert any("premium account" in s for s in said), said


def test_a_premium_account_flies_from_femor_hills_to_darashia(new_player):
    """The other side of the refusal above: the same trip with premium (Uzon: 60 gp, scripts/uzon.lua)."""
    p = next_to(new_player, NPCS["Uzon"].pos, level=50, premium_days=30, group_id=TESTER_GROUP,
                storage=BEGINNER_SET, inventory={BACKPACK: Item(1988, contents=[Item(2152, 1)])})   # 100 gp
    said = talk_to(p, "Uzon", "hi", "darashia", "yes")
    assert p.wait_for(lambda: premium_area(p.pos) == "mainland", timeout=5), f"still at {p.pos}: {said}"


TRAVEL = re.compile(r"StdModule\.travel,\s*\{([^}]*destination\s*=\s*\{[^}]*\}[^}]*)\}")
NUMBER = r"\s*=\s*(-?\d+)"


def test_every_npc_trip_into_a_premium_area_takes_premium_accounts_only():
    """Every StdModule.travel destination in a premium area is premium = true, and the captains (npc/lib/captain.lua,
    every harbour) ask for premium before anything else. The map has no other free way in:
    test_premium_expiry.py::test_premium_areas_match_the_map (no free tile reachable on foot in a premium box)."""
    wrong, checked = [], 0
    for script in sorted((NPC_DIR / "scripts").glob("*.lua")):
        for m in TRAVEL.finditer(script.read_text(encoding="latin-1")):
            body = m.group(1)
            dest = tuple(int(re.search(axis + NUMBER, body).group(1)) for axis in ("x", "y", "z"))
            if premium_area(dest):
                checked += 1
                if not re.search(r"premium\s*=\s*true", body):
                    wrong.append(f"{script.name}: {dest}")
    assert checked >= 5, f"only {checked} trips into a premium area found - did the scripts change?"
    assert not wrong, f"free trips into a premium area: {wrong}"

    captain = (NPC_DIR / "lib" / "captain.lua").read_text(encoding="latin-1")
    travel = captain[captain.index("local function travel("):]
    first = travel.split("\n")[1].strip()
    assert first == "if not isPremium(cid) then", f"captain.lua travel() no longer starts with the premium check: {first}"


# ---------------------------------------------------------------------------------------------- spells

TEACHERS = re.compile(r'\["([^"]+)"\] = \{((?:\["[^"]+"\] = \{[\d, ]+\},? ?)+)\}')
TEACHES = re.compile(r'\["([^"]+)"\] = \{([\d, ]+)\}')
# the spells only the Edron teachers (Puffels, Ursula, Gundralph, Zoltan; Eremo on his isle) teach, by vocation -
# Tibiantis' teacher table (docs/reference-74/spells-tibiantis.json, every seller in Edron) without its own spells
EDRON_ONLY = {
    SORCERER: {"Animate Dead", "Desintegrate", "Energy Bomb", "Energy Strike", "Enchant Staff", "Flame Strike",
               "Force Strike", "Haste", "Levitate", "Magic Rope", "Magic Wall", "Soulfire", "Strong Haste",
               "Ultimate Explosion", "Ultimate Light"},
    DRUID: {"Animate Dead", "Cancel Invisibility", "Desintegrate", "Energy Strike", "Envenom", "Flame Strike",
            "Force Strike", "Haste", "Heal Friend", "Levitate", "Magic Rope", "Mass Healing", "Paralyze",
            "Poison Bomb", "Poison Storm", "Soulfire", "Strong Haste", "Ultimate Light", "Undead Legion",
            "Wild Growth"},
    PALADIN: {"Conjure Bolt", "Conjure Power Bolt", "Desintegrate", "Haste", "Levitate", "Magic Rope"},
    KNIGHT: {"Berserk", "Challenge", "Haste", "Levitate", "Magic Rope"},
}


def _teachers():
    """{(spell, vocation): [teacher names]} from npc/lib/spells74.lua TEACHERS74."""
    src = (NPC_DIR / "lib" / "spells74.lua").read_text(encoding="latin-1")
    out = {}
    for npc, spells in TEACHERS.findall(src[src.index("TEACHERS74"):]):
        for spell, vocations in TEACHES.findall(spells):
            for vocation in map(int, vocations.split(",")):
                out.setdefault((spell, vocation), []).append(npc)
    return out


def test_the_spells_of_the_edron_magic_guild_are_taught_in_premium_areas_only():
    """tibia.com 2004 "Cool New Spells": "The mighty wizards from the magic guild of Edron have developed new spells.
    Cast haste [...] Fry your opponents with the mighty Ultimate Explosion!" - premium spells are the ones only
    taught where only premium accounts go (no teacher checks premium: a free account never meets them)."""
    teachers = _teachers()
    for (spell, vocation), npcs in teachers.items():
        for npc in npcs:
            assert npc in NPCS and NPCS[npc].pos, f"{npc} (teaches {spell}) is not on the map"
    premium_only = {}
    for (spell, vocation), npcs in teachers.items():
        if all(premium_area(NPCS[n].pos) for n in npcs):
            premium_only.setdefault(vocation, set()).add(spell)
    assert premium_only == EDRON_ONLY
    assert "Haste" in premium_only[KNIGHT] and "Ultimate Explosion" in premium_only[SORCERER]


SPELL_NEEDS_PREMIUM = "You need a premium account to use this spell."     # 7.4; spells.cpp playerSpellCheck
PREM = re.compile(r'<(instant|conjure|rune)\b[^>]*\bname="([^"]+)"[^>]*>')


def _premium_spells_xml():
    """{spells.xml name: tag} of every spell with prem="1"."""
    xml = (SERVER_DIR / "data" / "spells" / "spells.xml").read_text(encoding="latin-1")
    return {m.group(2): m.group(1) for m in PREM.finditer(xml) if 'prem="1"' in m.group(0)}


def test_the_premium_spells_are_the_ones_taught_in_premium_areas_only():
    """Decided with the user 2026-10-04: a spell no teacher on free ground teaches to any vocation needs premium to
    cast (spells.xml prem="1"), so a character whose premium ran out loses it until renewed. prem is per spell, not
    per vocation: a spell free for one vocation and premium-only for another would need the engine changed - there is
    none today, and this fails if one appears. Runes keep no prem (a premium conjure's rune is anyone's)."""
    free_for, premium_for = {}, {}             # spell -> the vocations that learn it on free ground / only in premium
    for (spell, vocation), npcs in _teachers().items():
        on_free_ground = any(premium_area(NPCS[n].pos) is None for n in npcs)
        (free_for if on_free_ground else premium_for).setdefault(spell, set()).add(vocation)
    mixed = {spell: (sorted(free_for[spell]), sorted(vocations)) for spell, vocations in premium_for.items()
             if spell in free_for}
    assert not mixed, f"free for some vocations, premium-only for others (prem is per spell): {mixed}"
    premium_only = set(premium_for)
    assert premium_only == set().union(*EDRON_ONLY.values())
    marked = _premium_spells_xml()
    assert set(marked) == premium_only, \
        f"prem=\"1\" missing: {sorted(premium_only - set(marked))}, extra: {sorted(set(marked) - premium_only)}"
    assert set(marked.values()) <= {"instant", "conjure"}, marked
    assert len(premium_only) == 28, sorted(premium_only)


# One spell per vocation that only Edron / Eremo teach it, non-aggressive (cast anywhere): words, mana.
PREMIUM_SPELL = {
    SORCERER: ("Ultimate Light", "utevo vis lux", 140),
    DRUID: ("Mass Healing", "exura gran mas res", 120),
    PALADIN: ("Conjure Bolt", "exevo con mort", 70),
    KNIGHT: ("Haste", "utani hur", 60),
}
SPELL_SPOT = (32369, 32241, 7)         # Thais temple (test_spells.py conjures there too)


def _caster(new_player, vocation, spell, premium):
    p = new_player(pos=SPELL_SPOT, vocation=vocation, level=100, maglevel=30, mana=1000,
                   premium_days=30 if premium else 0,
                   spells=[spell], group_id=TESTER_GROUP, storage=BEGINNER_SET)
    p.wait_for(lambda: p.stats.mana, timeout=3)
    return p


@pytest.mark.parametrize("vocation", list(PREMIUM_SPELL), ids=["sorcerer", "druid", "paladin", "knight"])
def test_a_free_account_cannot_cast_a_premium_spell_it_knows(new_player, vocation):
    """A character who learned it with premium and whose premium ran out: refused with the 7.4 text, no mana spent.
    Waits on the rebuild (spells.cpp: the text was "You need a premium account.")."""
    spell, words, _ = PREMIUM_SPELL[vocation]
    p = _caster(new_player, vocation, spell, premium=False)
    before = p.stats.mana
    p.say(words)
    assert p.wait_for(lambda: p.messages(SPELL_NEEDS_PREMIUM), timeout=3), p.text_messages[-3:]
    assert p.stats.mana == before


@pytest.mark.parametrize("vocation", list(PREMIUM_SPELL), ids=["sorcerer", "druid", "paladin", "knight"])
def test_a_premium_account_casts_the_premium_spell(new_player, vocation):
    spell, words, mana = PREMIUM_SPELL[vocation]
    p = _caster(new_player, vocation, spell, premium=True)
    before = p.stats.mana
    p.say(words)
    assert p.wait_for(lambda: p.stats.mana == before - mana, timeout=3), (p.stats.mana, p.text_messages[-3:])
    assert not p.messages("premium account")


@pytest.mark.parametrize("vocation", list(PREMIUM_SPELL), ids=["sorcerer", "druid", "paladin", "knight"])
def test_a_free_account_casts_a_spell_taught_on_free_ground(new_player, vocation):
    """Great Light: every vocation learns it in a free town (Gregor, Faluae, Etzel, ...)."""
    teachers = _teachers()[("Great Light", vocation)]
    assert any(premium_area(NPCS[n].pos) is None for n in teachers), teachers
    p = _caster(new_player, vocation, "Great Light", premium=False)
    before = p.stats.mana
    p.say("utevo gran lux")
    assert p.wait_for(lambda: p.stats.mana == before - 60, timeout=3), (p.stats.mana, p.text_messages[-3:])
    assert not p.messages("premium account")


# Paradox Tower's first ledge (test_paradox_tower.py): levitate up facing north, back down facing south.
LEDGE, ON_THE_LEDGE = (32570, 31976, 7), (32570, 31975, 6)


@pytest.mark.parametrize("up, down", [("exani hur up", "exani hur down"),
                                      ('exani hur "up', 'exani hur "down'),
                                      ('exani hur "up"', 'exani hur "down"')],
                         ids=["7.4 words", "quote", "quotes"])
def test_levitate_up_and_down(new_player, up, down):
    """TibiaWiki Levitate 2005: "exani hur up / exani hur down". The unquoted form waits on the rebuild
    (spells.cpp Spells::getInstantSpell took text after the words only behind a quote)."""
    from tibia74 import NORTH, SOUTH
    p = new_player(pos=LEDGE, vocation=SORCERER, level=50, maglevel=20, mana=500, premium_days=30,
                   spells=["Levitate"], group_id=TESTER_GROUP, storage=BEGINNER_SET)
    assert p.pos == LEDGE, p.pos
    p.turn(NORTH)
    p.sleep(0.5)
    p.say(up)
    assert p.wait_for(lambda: p.pos == ON_THE_LEDGE, timeout=3), (p.pos, p.text_messages[-2:])
    p.turn(SOUTH)
    p.sleep(2.2)                                  # a spell's exhaustion
    p.say(down)
    assert p.wait_for(lambda: p.pos == LEDGE, timeout=3), (p.pos, p.text_messages[-2:])


def test_levitate_needs_premium_to_cast(new_player):
    """spells.xml Levitate prem="1" (TibiaWiki Levitate 2005: "Only premium account players can use this spell"):
    a free account that knows it is refused. The 7.4 text waits on the rebuild. Also
    test_paradox_tower.py::test_paradox_tower_levitate_is_premium."""
    free = new_player(pos=LEDGE, vocation=DRUID, level=20, maglevel=3, premium_days=0, spells=["Levitate"],
                      group_id=TESTER_GROUP, storage=BEGINNER_SET)
    from tibia74 import NORTH
    free.turn(NORTH)
    free.say('exani hur "up')
    assert free.wait_for(lambda: free.messages(SPELL_NEEDS_PREMIUM), timeout=3), free.text_messages[-3:]
    assert free.pos == LEDGE


# ---------------------------------------------------------------------------------------------- outfits

MALE, FEMALE = 1, 0
# 7.4: citizen, hunter, mage, knight for everyone; nobleman/noblewoman, summoner, warrior with premium
OUTFIT_RANGE = {(MALE, False): (128, 131), (MALE, True): (128, 134),
                (FEMALE, False): (136, 139), (FEMALE, True): (136, 142)}


@pytest.mark.parametrize("sex, premium", list(OUTFIT_RANGE), ids=["male-free", "male-premium", "female-free",
                                                                   "female-premium"])
def test_the_outfit_dialog_offers_the_premium_outfits_to_premium_accounts_only(new_player, recorded, sex, premium):
    windows = recorded(0xC8, lambda c, r: (c._read_outfit(r), r.u8(), r.u8()))
    p = new_player(sex=sex, premium_days=30 if premium else 0, storage=BEGINNER_SET)
    p._send(Writer().u8(0xD2))                                # "Set Outfit" in the client
    assert p.wait_for(lambda: _of(windows, p), timeout=3), "no outfit dialog"
    _, first, last = _of(windows, p)[0]
    assert (first, last) == OUTFIT_RANGE[(sex, premium)]


def _outfit(c):
    return c.wait_for(lambda: c.creatures.get(c.player_id), timeout=5).outfit


def _set_outfit(c, looktype):
    c._send(Writer().u8(0xD3).u8(looktype).u8(10).u8(20).u8(30).u8(40))
    time.sleep(1)


def test_a_free_account_cannot_wear_a_premium_outfit(new_player):
    p = new_player(sex=MALE, premium_days=0, storage=BEGINNER_SET)
    for premium_outfit in (132, 133, 134):                    # nobleman, summoner, warrior
        _set_outfit(p, premium_outfit)
        assert _outfit(p)[0] != premium_outfit, f"a free account wears outfit {premium_outfit}"
    _set_outfit(p, 130)                                       # mage: free
    assert _outfit(p) == (130, 10, 20, 30, 40)


def test_a_premium_account_wears_a_premium_outfit(new_player):
    p = new_player(sex=FEMALE, premium_days=30, storage=BEGINNER_SET)
    _set_outfit(p, 142)                                       # warrior
    assert _outfit(p) == (142, 10, 20, 30, 40)


# ---------------------------------------------------------------------------------------------- chat

PRIVATE = 0xFFFF                                              # CHANNEL_PRIVATE (chat.h): "Private Chat Channel"


def _channels(c, lists):
    before = len(_of(lists, c))
    c._send(Writer().u8(0x97))                                # the client's "open channel" dialog
    assert c.wait_for(lambda: len(_of(lists, c)) > before, timeout=3), "no channel list"
    return _of(lists, c)[-1]


def _read_channels(c, r):
    return [(r.u16(), r.string()) for _ in range(r.u8())]


@pytest.mark.parametrize("premium", [False, True], ids=["free", "premium"])
def test_the_private_chat_channel_is_offered_to_premium_accounts_only(new_player, recorded, premium):
    """tibia.com 2004: "Premium players are allowed to open up private chat channels to which they can invite their
    friends" (anyone can be invited)."""
    lists = recorded(0xAB, _read_channels)
    p = new_player(premium_days=30 if premium else 0, storage=BEGINNER_SET)
    offered = PRIVATE in [cid for cid, _ in _channels(p, lists)]
    assert offered == premium


@pytest.mark.parametrize("premium", [False, True], ids=["free", "premium"])
def test_only_a_premium_account_opens_a_private_chat_channel(new_player, recorded, premium):
    """The packet itself (0xAA), not only the dialog: a free account gets no channel. Needs the chat.cpp change
    (rebuild) for the free case."""
    opened = recorded(0xB2, lambda c, r: (r.u16(), r.string()))
    p = new_player(premium_days=30 if premium else 0, storage=BEGINNER_SET)
    p._send(Writer().u8(0xAA))
    got = p.wait_for(lambda: _of(opened, p), timeout=2)
    if premium:
        assert got and _of(opened, p)[0][1] == f"{p.character.name}'s Channel", _of(opened, p)
    else:
        assert not got, f"a free account opened {_of(opened, p)}"


def _add_vips(db, p, added, count):
    """Ask to add `count` new characters to p's VIP list -> how many the server added."""
    before = len(_of(added, p))
    for _ in range(count):
        p._send(Writer().u8(0xDC).string(db.create_character(storage=BEGINNER_SET).name))
    p.sleep(1.5)
    return len(_of(added, p)) - before


@pytest.mark.parametrize("premium, limit", [(False, 20), (True, 50)], ids=["free-20", "premium-50"])
def test_the_vip_list_holds_20_names_or_50_with_premium(new_player, db, recorded, premium, limit):
    """tibia.com manual "Communication" 2004: "VIP lists can contain up to 20 names. Note, however, premium players
    have their VIP lists extended to a total of 50 names." Needs the player.cpp change (rebuild): it was 51 for all."""
    added = recorded(0xD2, lambda c, r: (r.u32(), r.string(), r.u8()))
    p = new_player(premium_days=30 if premium else 0, storage=BEGINNER_SET)
    assert _add_vips(db, p, added, limit) == limit
    since = len(p.text_messages)
    assert _add_vips(db, p, added, 1) == 0, f"name {limit + 1} was added"
    assert any("You cannot add more buddies." in t for _, t in p.text_messages[since:]), p.text_messages[-3:]


# ---------------------------------------------------------------------------------------------- blessings

@pytest.mark.parametrize("npc, word", [("Norf", "shielding"), ("Humphrey", "embrace"), ("Edala", "suns")])
def test_a_free_account_is_blessed_on_free_ground(new_player, npc, word):
    """TibiaWiki Blessings 2005-2006: "Blessings can be obtained by any player", "One blessing [Eremo's, on his premium
    isle] and the promotion require premium accounts". Humphrey's Embrace of Tibia was premium-only."""
    assert premium_area(NPCS[npc].pos) is None
    p = next_to(new_player, NPCS[npc].pos, level=50, premium_days=0, group_id=TESTER_GROUP, storage=BEGINNER_SET,
                inventory={BACKPACK: Item(1988, contents=[Item(2160, 1)])})        # 10,000 gp
    said = talk_to(p, npc, "hi", word, "yes")
    assert any("You have been blessed" in s for s in said), said


# ---------------------------------------------------------------------------------------------- beds

# The City Wall 5c and 5e, Thais (houses 88 and 90; no other test uses them): the head of the bed, the tile beside it
# and a tile for the GM, all in the house.
BEDS = {"free": ((32411, 32222, 7), (32412, 32222, 7), (32413, 32223, 7)),
        "premium": ((32411, 32226, 7), (32412, 32226, 7), (32413, 32227, 7))}


def _owner_beside_the_bed(new_player, db, items, server, premium):
    from tibia74 import GameClient
    bed, beside, gm_pos = BEDS["premium" if premium else "free"]
    owner = db.create_character(pos=beside, premium_days=30 if premium else 0, town_id=2, storage=BEGINNER_SET)
    gm = new_player(pos=gm_pos, group_id=3, storage=BEGINNER_SET)     # God: may stand in any house, /owner
    assert gm.pos == gm_pos, gm.pos
    gm.say(f"/owner {owner.name}")
    gm.sleep(1)
    gm.logout()
    c = GameClient(items, port=server.port)
    c.login(owner.account, owner.password, owner.name)
    c.character = owner
    assert c.pos == beside, f"the owner logged in at {c.pos}"
    return c, bed


def _use_bed(c, bed, items):
    stack = c.tiles.get(bed, [])
    head = next(i for i, t in enumerate(stack) if getattr(t, "client_id", None) == items.by_server[1754].client_id)
    c.use_item(bed, stack[head].client_id, head)


def test_a_free_account_cannot_sleep_in_a_bed(new_player, db, items, server):
    """config.lua PremOnlyBeds (BedItem::canUse); Tibiantis FAQ: premium players "sleep in bed". Even in its own
    house (a house whose owner's premium ran out until the server save takes it)."""
    c, bed = _owner_beside_the_bed(new_player, db, items, server, premium=False)
    try:
        since = len(c.text_messages)
        _use_bed(c, bed, items)
        assert c.wait_for(lambda: any(NOT_USABLE in t for _, t in c.text_messages[since:]), timeout=3), \
            c.text_messages[-3:]
        assert c.connected, "the free account went to bed (logged out)"
    finally:
        c.logout()


def test_a_premium_account_sleeps_in_its_bed(new_player, db, items, server):
    c, bed = _owner_beside_the_bed(new_player, db, items, server, premium=True)
    _use_bed(c, bed, items)
    assert c.wait_for(lambda: not c.connected, timeout=5), f"still awake: {c.text_messages[-3:]}"
    c.close()

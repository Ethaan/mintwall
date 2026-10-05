"""Rookgaard NPCs in game, checked against what their own XML/script says (see tibia74/npcs.py):
every keyword gets its reply, every item they sell can be bought and every item they buy can be sold
for the listed price. Trades are checked in the saved character (money and items) after logout."""
import math

import pytest

from tibia74 import BACKPACK, Item, Items, SERVER_DIR
from tibia74.db import BEGINNER_SET_GIVEN
from tibia74.items import GROUP_FLUID
from tibia74.npcs import load_npcs, rookgaard_pos
from tibia74.quest import near_npc, say_to, seen_npc
from tibia74.server import TESTER_GROUP

NPCS = {name: npc for name, npc in load_npcs(SERVER_DIR).items() if rookgaard_pos(npc) and not npc.is_interaction}
ITEMS = Items(SERVER_DIR / "data")

BACKPACK_ID = 1988
COINS = {2148: 1, 2152: 100, 2160: 10000}          # gold, platinum, crystal coin
CHUNK = 12                                         # trades per character: fits one backpack with the change
GREETINGS = {"hi", "hello", "bye", "farewell"}
from tibia74.premium import in_premium_area   # Loui, Zerbrus, Billy: the premium side of Rookgaard

PREMIUM_TRADERS = {"Lee'Delle", "Norma"}            # trade with premium accounts only (npc/lib/premiumshop.lua)


def _chunks(kind):
    return [pytest.param(name, i, id=f"{name}-{i + 1}")
            for name, npc in sorted(NPCS.items())
            for i in range(math.ceil(len(getattr(npc, kind)) / CHUNK))]


def _visit(new_player, npc, inventory=None):
    """A strong character (for capacity) next to the NPC, greeted and in talk range. It talks faster
    than a player may (the server mutes after a few quick lines), so it is in the unmutable test group.
    Found where the NPC has walked to by now, past whoever an earlier test left beside it."""
    p = near_npc(new_player, npc, spawn=rookgaard_pos(npc), level=100, inventory=inventory,
                 storage={BEGINNER_SET_GIVEN: 1}, group_id=TESTER_GROUP,
                 premium_days=30 if npc.name in PREMIUM_TRADERS or in_premium_area(rookgaard_pos(npc)) else 0)
    p.greeting = say_to(p, npc.name, f"hi {npc.name.lower()}")    # by name: a neighbour would take a plain "hi"
    me = seen_npc(p, npc.name)
    assert p.greeting, f"{npc.name} does not answer hi: it is at {me and me.pos}, we are at {p.pos}"
    return p


def _saved(p, db):
    """Items of the character as saved on logout: {(itemtype, count): rows}."""
    db.logout_and_saved(p)
    return db.items(p.character.guid)


def _money(rows):
    return sum(COINS[r["itemtype"]] * r["count"] for r in rows if r["itemtype"] in COINS)


def _count(rows, item):
    it = ITEMS.by_server[item.item_id]
    if it.group == GROUP_FLUID:
        return sum(1 for r in rows if r["itemtype"] == item.item_id and r["count"] == item.subtype)
    if it.has_count:
        return sum(r["count"] for r in rows if r["itemtype"] == item.item_id)
    return sum(1 for r in rows if r["itemtype"] == item.item_id)


def _coins(amount):
    """Enough coins for amount, as backpack contents."""
    crystals = math.ceil(amount / 10000)
    return [Item(2160, min(100, crystals - i)) for i in range(0, crystals, 100)]


@pytest.mark.parametrize("name", sorted(n for n, npc in NPCS.items() if npc.keywords))
def test_npc_answers_its_keywords(new_player, name):
    npc = NPCS[name]
    p = _visit(new_player, npc)
    wrong = []
    for keyword, reply in npc.keywords.items():
        if keyword.lower() in GREETINGS:
            continue
        expected = reply.replace("|PLAYERNAME|", p.name).replace("{", "").replace("}", "")
        got = p.talk(keyword, npc=name)
        if expected not in got:
            wrong.append(f"{keyword!r}: expected {expected!r}\n{'':{len(keyword) + 4}}got      {got}")
    assert not wrong, f"{len(wrong)} of {len(npc.keywords)} keywords answered wrong:\n" + "\n".join(wrong)


@pytest.mark.parametrize("name, chunk", _chunks("buyable"))
def test_npc_sells_each_item_for_its_price(new_player, db, name, chunk):
    npc = NPCS[name]
    items = npc.buyable[chunk * CHUNK:(chunk + 1) * CHUNK]
    cost = sum(i.price for i in items)
    coins = _coins(cost)
    p = _visit(new_player, npc, inventory={BACKPACK: Item(BACKPACK_ID, contents=coins)})
    said = {}
    for item in items:
        said[item.names[0]] = p.talk(f"buy {item.names[0]}", "yes", npc=name)
    # what cannot be carried (a football) is put at the buyer's feet
    at_feet = [{"itemtype": ITEMS.client(i.client_id).server_id, "count": i.count} for i in p.tile_items(p.pos)]

    rows = _saved(p, db) + at_feet
    wanted = {}
    for item in items:
        wanted[(item.item_id, item.subtype)] = wanted.get((item.item_id, item.subtype), 0) + 1
    missing = [f"{i.names[0]!r} ({i.item_id}): NPC said {said[i.names[0]]}" for i in items
               if _count(rows, i) < wanted[(i.item_id, i.subtype)]]
    paid = _money([{"itemtype": c.item_id, "count": c.count} for c in coins]) - _money(rows)
    assert not missing, f"greeted with {p.greeting}; not received:\n" + "\n".join(missing)
    assert paid == cost, f"paid {paid} gp for items listed at {cost} gp in total"


@pytest.mark.parametrize("name, chunk", _chunks("sellable"))
def test_npc_buys_each_item_for_its_price(new_player, db, name, chunk):
    npc = NPCS[name]
    items = npc.sellable[chunk * CHUNK:(chunk + 1) * CHUNK]
    goods = [Item(i.item_id, 0 if ITEMS.by_server[i.item_id].group == GROUP_FLUID else 1) for i in items]
    p = _visit(new_player, npc, inventory={BACKPACK: Item(BACKPACK_ID, contents=goods)})
    said = {}
    for item in items:
        said[item.names[0]] = p.talk(f"sell {item.names[0]}", "yes", npc=name)

    rows = _saved(p, db)
    kept = [f"{i.names[0]!r} ({i.item_id}): NPC said {said[i.names[0]]}" for i in items
            if any(r["itemtype"] == i.item_id for r in rows)]
    earned, expected = _money(rows), sum(i.price for i in items)
    assert not kept, f"greeted with {p.greeting}; not taken:\n" + "\n".join(kept)
    assert earned == expected, f"got {earned} gp for items listed at {expected} gp in total"


# ----------------------------------------------------------------------------- special NPCs (hand-written)

ALL_NPCS = load_npcs(SERVER_DIR)
SMALL_AXE, PICK, PAN, ANTIDOTE_RUNE, BOOK, SHORT_SWORD = 2559, 2553, 2563, 2266, 1955, 2406
HONEY_FLOWER, STUDDED_LEGS, PRESENT, LEGION_HELMET, SILVER_KEY, SABRE = 2103, 2468, 1990, 2480, 2088, 2385


@pytest.mark.parametrize("name, lines, gives, gets", [
    ("Al Dee", ["pick", "yes"], SMALL_AXE, PICK),
    ("Billy", ["pan", "yes"], PAN, ANTIDOTE_RUNE),
    ("Amber", ["book", "yes"], BOOK, SHORT_SWORD),
    ("Lee'Delle", ["honey flower"], HONEY_FLOWER, STUDDED_LEGS),
    ("Seymour", ["box", "yes"], PRESENT, LEGION_HELMET),
])
def test_npc_trades_a_quest_item_for_its_reward(new_player, db, name, lines, gives, gets):
    p = _visit(new_player, ALL_NPCS[name], inventory={BACKPACK: Item(BACKPACK_ID, contents=[Item(gives)])})
    said = p.talk(*lines, npc=name)
    rows = _saved(p, db)
    assert not any(r["itemtype"] == gives for r in rows), f"{name} did not take item {gives}; said {said}"
    assert any(r["itemtype"] == gets for r in rows), f"{name} gave no item {gets}; said {said}"


def test_seymour_sells_the_key_to_adventure(new_player, db):
    p = _visit(new_player, ALL_NPCS["Seymour"], inventory={BACKPACK: Item(BACKPACK_ID, contents=[Item(2148, 10)])})
    said = p.talk("key", "yes", npc="Seymour")
    rows = _saved(p, db)
    keys = [r for r in rows if r["itemtype"] == SILVER_KEY]
    assert keys, f"no key; Seymour said {said}"
    assert b"\x04" + (4600).to_bytes(2, "little") in bytes(keys[0]["attributes"] or b""), \
        "the key does not have action id 4600 (the door it opens)"
    assert _money(rows) == 5, f"paid {10 - _money(rows)} gp instead of 5"


def test_blind_orc_sells_a_sabre_in_orcish(new_player, db):
    """<interaction> NPC: 'charach' greets, 'goshak charcha' asks for a sabre, 'mok' is yes."""
    orc = ALL_NPCS["Blind Orc"]
    p = new_player(pos=orc.pos, level=20, storage={BEGINNER_SET_GIVEN: 1}, group_id=TESTER_GROUP,
                   inventory={BACKPACK: Item(BACKPACK_ID, contents=[Item(2148, 25)])})
    said = p.talk("charach", "goshak charcha", "mok", npc="Blind Orc")
    rows = _saved(p, db)
    assert any(r["itemtype"] == SABRE for r in rows), f"no sabre; the orc said {said}"
    assert _money(rows) == 0, f"paid {25 - _money(rows)} gp instead of 25"


@pytest.mark.parametrize("name", ["Cipfried", "Dallheim", "Zerbrus"])
def test_healer_heals_a_badly_wounded_player_to_65(new_player, name):
    npc = ALL_NPCS[name]
    p = new_player(pos=rookgaard_pos(npc), health=30, group_id=TESTER_GROUP)
    said = p.talk("hi", "heal", npc=name)
    assert p.wait_for(lambda: p.stats.health >= 65, timeout=5), f"health {p.stats.health}; {name} said {said}"

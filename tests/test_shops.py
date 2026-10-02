"""Every shop off Rookgaard, in game: each item an NPC sells can be bought and each item it buys can be sold, for the
listed price (test_npcs_rookgaard.py does Rookgaard). The prices themselves were audited against Tibiantis and
TibiaWiki 2005-06 (task.md, shop audit 2026-10-01; docs/reference-74/npc-shops.md)."""
import math

import pytest

import test_npcs_rookgaard as rook
from test_npc_data import PENDING
from test_npc_talk import GREETING
from tibia74 import BACKPACK, Item, SERVER_DIR
from tibia74.db import BEGINNER_SET_GIVEN
from tibia74.items import GROUP_FLUID
from tibia74.npcs import load_npcs, rookgaard_pos
from tibia74.server import TESTER_GROUP

# greeted with another word (the djinn) or not trading with everyone: their own tests
SKIP = set(GREETING) | PENDING
NPCS = {name: npc for name, npc in load_npcs(SERVER_DIR).items()
        if npc.positions and not rookgaard_pos(npc) and not npc.is_interaction and name not in SKIP}
CHUNK = rook.CHUNK


def _chunks(kind):
    return [pytest.param(name, i, id=f"{name}-{i + 1}")
            for name, npc in sorted(NPCS.items())
            for i in range(math.ceil(len(getattr(npc, kind)) / CHUNK))]


def _visit(new_player, npc, inventory=None):
    """A strong premium character (some shops are premium) in talk range of the NPC, greeted."""
    spawn = npc.pos
    for dx, dy in ((2, 0), (0, 2), (-2, 0), (0, -2), (2, 1), (2, -1), (1, 2), (-1, 2),
                   (0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)):
        p = new_player(pos=(spawn[0] + dx, spawn[1] + dy, spawn[2]), level=100, inventory=inventory,
                       premium_days=30, storage={BEGINNER_SET_GIVEN: 1, 30001: 1}, group_id=TESTER_GROUP)
        if p.pos[2] == spawn[2] and max(abs(p.pos[0] - spawn[0]), abs(p.pos[1] - spawn[1])) <= 3:
            break
        p.logout()
    me = p.wait_for(lambda: p.nearest(npc.name), timeout=60)      # wanderers (Hardek: 20 tiles) come back
    assert me, f"{npc.name} is not near its spawn {spawn} (we are at {p.pos})"
    if max(abs(me.pos[0] - p.pos[0]), abs(me.pos[1] - p.pos[1])) > 3:
        p.walk_to(me.pos)
    p.greeting = p.talk("hi", npc=npc.name)
    assert p.greeting, f"{npc.name} does not answer hi"
    return p


@pytest.mark.parametrize("name, chunk", _chunks("buyable"))
def test_npc_sells_each_item_for_its_price(new_player, db, name, chunk):
    npc = NPCS[name]
    items = npc.buyable[chunk * CHUNK:(chunk + 1) * CHUNK]
    cost = sum(i.price for i in items)
    coins = rook._coins(cost)
    p = _visit(new_player, npc, inventory={BACKPACK: Item(rook.BACKPACK_ID, contents=coins)})
    said = {i.names[0]: p.talk(f"buy {i.names[0]}", "yes", npc=name) for i in items}
    # what does not fit (both hands full, the backpack full) is put at the buyer's feet
    at_feet = [{"itemtype": rook.ITEMS.client(i.client_id).server_id, "count": i.count} for i in p.tile_items(p.pos)]
    rows = rook._saved(p, db) + at_feet
    wanted = {}
    for item in items:
        wanted[(item.item_id, item.subtype)] = wanted.get((item.item_id, item.subtype), 0) + 1
    missing = [f"{i.names[0]!r} ({i.item_id}): NPC said {said[i.names[0]]}" for i in items
               if rook._count(rows, i) < wanted[(i.item_id, i.subtype)]]
    paid = rook._money([{"itemtype": c.item_id, "count": c.count} for c in coins]) - rook._money(rows)
    assert not missing, f"greeted with {p.greeting}; not received:\n" + "\n".join(missing)
    assert paid == cost, f"paid {paid} gp for items listed at {cost} gp in total"


@pytest.mark.parametrize("name, chunk", _chunks("sellable"))
def test_npc_buys_each_item_for_its_price(new_player, db, name, chunk):
    npc = NPCS[name]
    items = npc.sellable[chunk * CHUNK:(chunk + 1) * CHUNK]
    goods = [Item(i.item_id, 0 if rook.ITEMS.by_server[i.item_id].group == GROUP_FLUID else 1) for i in items]
    p = _visit(new_player, npc, inventory={BACKPACK: Item(rook.BACKPACK_ID, contents=goods)})
    said = {i.names[0]: p.talk(f"sell {i.names[0]}", "yes", npc=name) for i in items}
    rows = rook._saved(p, db)
    kept = [f"{i.names[0]!r} ({i.item_id}): NPC said {said[i.names[0]]}" for i in items
            if any(r["itemtype"] == i.item_id for r in rows)]
    earned, expected = rook._money(rows), sum(i.price for i in items)
    assert not kept, f"greeted with {p.greeting}; not taken:\n" + "\n".join(kept)
    assert earned == expected, f"got {earned} gp for items listed at {expected} gp in total"


def test_a_bought_ring_is_not_put_on(new_player, db):
    """With both hands full, a bought life ring went into the free ring slot and became a worn one (2205),
    wearing off; a crystal ball went into the ammo slot. Given items go to a hand or a bag, else at the feet."""
    npc = NPCS["Alexander"]
    p = _visit(new_player, npc, inventory={BACKPACK: Item(rook.BACKPACK_ID, contents=rook._coins(2000))})
    for ware in ("crystal ball", "life ring"):
        p.talk(f"buy {ware}", "yes", npc="Alexander")
    rows = rook._saved(p, db)
    worn = [(r["pid"], r["itemtype"]) for r in rows if r["pid"] in (1, 2, 4, 7, 8, 9, 10)]
    assert not worn, f"bought items put on (slot, item): {worn}"
    assert any(r["itemtype"] == 2168 for r in rows), "the life ring is gone"


def test_only_one_trader_of_a_shared_shop_answers(new_player, db):
    """Bezil and Nezil share a shop: "hi" greeted both and both sold on "yes" - the buyer paid twice. A player
    talks to one NPC at a time now (npc/lib/npcsystem/npchandler.lua, decided with the user 2026-10-02)."""
    npc = NPCS["Bezil"]
    p = _visit(new_player, npc, inventory={BACKPACK: Item(rook.BACKPACK_ID, contents=rook._coins(8))})
    assert p.wait_for(lambda: p.nearest("Nezil"), timeout=60), "Nezil is not in the shop"
    said = p.talk("buy candelabrum", "yes")                  # every NPC's words, not just Bezil's
    assert not any(n == "Nezil" for n, _, _ in p.speech), [s for s in p.speech if s[0] in ("Bezil", "Nezil")]
    rows = rook._saved(p, db)
    assert rook._money(rows) == 0 and any(r["itemtype"] == 2041 for r in rows), (said, rows)

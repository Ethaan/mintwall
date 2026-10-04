"""Capacity in 7.4: what a character can carry, by vocation and level, and what is refused above it.

Formula (TibiaWiki "Formula" 2007-11, oldid 128170; tibiantis-notes "Classes"): 470 + (level - 8) x gain for a
character that left Rookgaard at level 8 - knight 25, paladin 20, sorcerer/druid 10 - and 400 + (level - 1) x 10 in
Rookgaard (no vocation). The client shows the free capacity (cap minus everything carried, whole oz).
Item weights: server/data/items/items.xml, checked against the Tibiantis data by tools/compare-item-weights.py.
"""
import functools
import xml.etree.ElementTree as ET

import pytest

from tibia74 import ARMOR, BACKPACK, RIGHT, SERVER_DIR, Item
from tibia74.db import capacity, exp_for_level
from tibia74.net import Writer

SKIP_SET = {30001: 1}              # no beginner set: start with exactly what the test gives
ROAD = (32091, 32194, 7)           # open ground north-west of the Rookgaard temple (test_death.py walks here too)

MACE, PLATE_ARMOR, BACKPACK_ID, SWORD = 2398, 2463, 1988, 2376
NONE, SORCERER, DRUID, PALADIN, KNIGHT, ELITE_KNIGHT = 0, 1, 2, 3, 4, 8
TOO_HEAVY = "This object is too heavy."        # player.cpp RET_NOTENOUGHCAPACITY


@functools.lru_cache(maxsize=None)
def weight(item_id: int) -> float:
    """Weight in oz from items.xml (stored in hundredths)."""
    for it in ET.parse(SERVER_DIR / "data" / "items" / "items.xml").getroot():
        if it.get("id") == str(item_id):
            return next(int(a.get("value")) / 100 for a in it.findall("attribute") if a.get("key") == "weight")
    raise KeyError(item_id)


def _free_cap(p, expected, timeout=3):
    """Wait until the client shows `expected` free capacity; return what it shows."""
    p.wait_for(lambda: p.stats.capacity == expected, timeout=timeout)
    return p.stats.capacity


def _stackpos(p, pos, client_id):
    return next((n for n, t in enumerate(p.tiles.get(tuple(pos), [])) if getattr(t, "client_id", None) == client_id),
                None)


def _drop(p, from_pos, client_id, from_stackpos=0, to=None):
    """Put a carried item on our own tile (or on `to`)."""
    to = tuple(to or p.pos)
    p.move_item(from_pos, client_id, from_stackpos, to)
    assert p.wait_for(lambda: _stackpos(p, to, client_id) is not None, timeout=3), \
        f"#{client_id} not on {to}: {p.tiles.get(to)} {p.text_messages[-2:]}"


def _pick_up(p, client_id, slot=RIGHT):
    p.move_item(p.pos, client_id, _stackpos(p, p.pos, client_id), p.inventory_pos(slot))


# ----------------------------------------------------------------------------- the formula

def test_formula_matches_the_tibiantis_base_capacity():
    """tibiantis-notes "Classes": base capacity knight 270, paladin 310, mage 390 (cap = level x gain + base)."""
    for vocation, gain, base in ((KNIGHT, 25, 270), (PALADIN, 20, 310), (SORCERER, 10, 390), (DRUID, 10, 390)):
        for level in (8, 20, 100):
            assert capacity(vocation, level) == gain * level + base, (vocation, level)
    assert capacity(NONE, 1) == 400 and capacity(NONE, 8) == 470


@pytest.mark.parametrize("vocation, level, cap", [
    (NONE, 1, 400), (NONE, 8, 470), (NONE, 12, 510),
    (KNIGHT, 8, 470), (KNIGHT, 20, 770), (ELITE_KNIGHT, 100, 2770),
    (PALADIN, 20, 710), (SORCERER, 20, 590), (DRUID, 45, 840),
])
def test_capacity_shown_is_the_7_4_formula(new_player, vocation, level, cap):
    p = new_player(pos=ROAD, level=level, vocation=vocation, storage=SKIP_SET)
    assert _free_cap(p, cap) == cap, f"shows {p.stats.capacity}, 7.4: {cap}"


def test_carried_items_take_their_weight_off_the_capacity_shown(new_player):
    """Plate armor 120 + backpack 18 holding another plate armor 120 + mace 38 = 296 oz off 470."""
    inventory = {ARMOR: Item(PLATE_ARMOR), BACKPACK: Item(BACKPACK_ID, contents=[Item(PLATE_ARMOR)]),
                 RIGHT: Item(MACE)}
    p = new_player(pos=(ROAD[0], ROAD[1] + 1, ROAD[2]), level=8, vocation=KNIGHT, storage=SKIP_SET,
                   inventory=inventory)
    carried = 2 * weight(PLATE_ARMOR) + weight(BACKPACK_ID) + weight(MACE)
    assert carried == 296
    assert _free_cap(p, 470 - 296) == 470 - 296


@pytest.mark.parametrize("vocation, level", [(NONE, 1), (KNIGHT, 8)], ids=["rookgaard", "knight"])
def test_a_level_up_adds_the_vocation_capacity(new_player, vocation, level):
    """One experience point short of the next level, a rat (5 exp) makes it: +10 in Rookgaard, +25 for a knight."""
    spot = (32107, 32224, 7)                                   # the dirt road east of the temple (test_rookgaard)
    p = new_player(pos=spot, level=level, vocation=vocation, experience=exp_for_level(level + 1) - 1,
                   inventory={RIGHT: Item(SWORD)}, skills={2: 50}, storage=SKIP_SET)
    gm = new_player(pos=(spot[0], spot[1] - 3, spot[2]), group_id=3)
    before = capacity(vocation, level) - weight(SWORD)
    assert _free_cap(p, before) == before
    gm.say("/m Rat")
    rat = p.wait_for(lambda: p.nearest("Rat"), timeout=5)
    assert rat, "no rat"
    p.set_fight_modes(fight=1, chase=1)
    p.attack(rat.id)
    assert p.wait_for(lambda: p.stats.level == level + 1, timeout=60), f"level {p.stats.level}, rat {rat}"
    after = capacity(vocation, level + 1) - weight(SWORD)
    assert _free_cap(p, after) == after, f"free cap {before} -> {p.stats.capacity}, 7.4: {after}"


# ----------------------------------------------------------------------------- picking up

def test_picking_up_an_item_takes_its_weight(new_player):
    """A level 1 (400 oz) with a mace (38 oz): 362 free; the mace on the ground: 400; picked up again: 362."""
    p = new_player(pos=(ROAD[0], ROAD[1] + 2, ROAD[2]), storage=SKIP_SET, inventory={RIGHT: Item(MACE)})
    assert _free_cap(p, 362) == 362
    mace = p.inventory[RIGHT].client_id
    _drop(p, p.inventory_pos(RIGHT), mace)
    assert _free_cap(p, 400) == 400
    _pick_up(p, mace)
    assert p.wait_for(lambda: RIGHT in p.inventory, timeout=3), p.text_messages[-2:]
    assert _free_cap(p, 362) == 362


def test_an_item_heavier_than_the_free_capacity_is_refused(new_player):
    """400 oz carried 378 (2 plate armors in a backpack, one worn): the 38 oz mace does not fit in the 22 left -
    "This object is too heavy." and it stays on the ground. With one plate armor put down it fits."""
    inventory = {ARMOR: Item(PLATE_ARMOR), BACKPACK: Item(BACKPACK_ID, contents=[Item(PLATE_ARMOR), Item(PLATE_ARMOR)]),
                 RIGHT: Item(MACE)}                    # 416 oz: loaded from the database over the limit
    p = new_player(pos=(ROAD[0], ROAD[1] + 3, ROAD[2]), storage=SKIP_SET, inventory=inventory)
    assert _free_cap(p, 0) == 0, "over the limit shows 0"
    mace = p.inventory[RIGHT].client_id
    _drop(p, p.inventory_pos(RIGHT), mace)
    assert _free_cap(p, 22) == 22

    start = len(p.text_messages)
    _pick_up(p, mace)
    assert p.wait_for(lambda: any(TOO_HEAVY in t for _, t in p.text_messages[start:]), timeout=3), \
        p.text_messages[start:]
    assert RIGHT not in p.inventory and _stackpos(p, p.pos, mace) is not None, "the mace was picked up"
    assert p.stats.capacity == 22

    bag = p.open_container(BACKPACK)
    assert bag and len(bag.items) == 2, bag
    east = (p.pos[0] + 1, p.pos[1], p.pos[2])       # not onto the mace: only the top item of a pile can be moved
    _drop(p, p.container_pos(bag.cid, 0), bag.items[0].client_id, 0, to=east)
    assert _free_cap(p, 142) == 142
    _pick_up(p, mace)
    assert p.wait_for(lambda: RIGHT in p.inventory, timeout=3), p.text_messages[-2:]
    assert _free_cap(p, 104) == 104


def test_a_heavy_item_does_not_fit_into_a_carried_backpack_either(new_player):
    """The capacity counts what is in containers too: a full-up character cannot drop the mace into its backpack."""
    inventory = {ARMOR: Item(PLATE_ARMOR), BACKPACK: Item(BACKPACK_ID, contents=[Item(PLATE_ARMOR), Item(PLATE_ARMOR)]),
                 RIGHT: Item(MACE)}
    p = new_player(pos=(ROAD[0], ROAD[1] + 4, ROAD[2]), storage=SKIP_SET, inventory=inventory)
    mace = p.inventory[RIGHT].client_id
    _drop(p, p.inventory_pos(RIGHT), mace)
    bag = p.open_container(BACKPACK)
    assert bag, "backpack did not open"
    start = len(p.text_messages)
    p.move_item(p.pos, mace, _stackpos(p, p.pos, mace), p.container_pos(bag.cid, 0))
    assert p.wait_for(lambda: any(TOO_HEAVY in t for _, t in p.text_messages[start:]), timeout=3), \
        p.text_messages[start:]
    assert len(p.containers[bag.cid].items) == 2 and _free_cap(p, 22) == 22


# ----------------------------------------------------------------------------- receiving

def _offer(p, slot, partner_id):
    """Trade request (0x7D) with the item in an inventory slot."""
    p._send(Writer().u8(0x7D).position(p.inventory_pos(slot)).u16(p.inventory[slot].client_id).u8(0)
            .u32(partner_id))


def test_a_traded_item_over_the_free_capacity_is_refused(new_player):
    """A trade fails when an item does not fit the receiver's capacity: both keep their items, and the receiver is
    told "You do not have enough capacity to carry this object." with the weight (game.cpp)."""
    giver = new_player(pos=(ROAD[0], ROAD[1] + 5, ROAD[2]), level=50, vocation=KNIGHT, storage=SKIP_SET,
                       inventory={RIGHT: Item(PLATE_ARMOR)})
    taker = new_player(pos=(ROAD[0], ROAD[1] + 6, ROAD[2]), storage=SKIP_SET,       # 400 oz, 104 free
                       inventory={RIGHT: Item(MACE), BACKPACK: Item(BACKPACK_ID, contents=[Item(PLATE_ARMOR)] * 2)})
    assert _free_cap(taker, 400 - 38 - 18 - 240) == 104
    mace, plate = taker.inventory[RIGHT].client_id, giver.inventory[RIGHT].client_id
    for p, other in ((giver, taker), (taker, giver)):
        _offer(p, RIGHT, other.player_id)
        p.sleep(0.3)
    taker_start = len(taker.text_messages)
    giver._send(Writer().u8(0x7F))
    giver.sleep(0.2)
    taker._send(Writer().u8(0x7F))
    assert taker.wait_for(lambda: any("You do not have enough capacity to carry this object." in t
                                      for _, t in taker.text_messages[taker_start:]), timeout=3), \
        taker.text_messages[taker_start:]
    assert any("It weighs 120.00 oz." in t for _, t in taker.text_messages[taker_start:]), taker.text_messages[-2:]
    taker.sleep(0.5)
    assert taker.inventory[RIGHT].client_id == mace and giver.inventory[RIGHT].client_id == plate, \
        ("the items were swapped", taker.inventory, giver.inventory)
    assert taker.stats.capacity == 104


def test_a_traded_item_within_the_free_capacity_takes_its_weight(new_player):
    """The same trade with room: the plate armor (120) for the mace (38) leaves 224 + 38 - 120 = 142 free."""
    giver = new_player(pos=(ROAD[0], ROAD[1] + 7, ROAD[2]), level=50, vocation=KNIGHT, storage=SKIP_SET,
                       inventory={RIGHT: Item(PLATE_ARMOR)})
    taker = new_player(pos=(ROAD[0], ROAD[1] + 8, ROAD[2]), storage=SKIP_SET,
                       inventory={RIGHT: Item(MACE), BACKPACK: Item(BACKPACK_ID, contents=[Item(PLATE_ARMOR)])})
    assert _free_cap(taker, 400 - 38 - 18 - 120) == 224
    mace = taker.inventory[RIGHT].client_id
    for p, other in ((giver, taker), (taker, giver)):
        _offer(p, RIGHT, other.player_id)
        p.sleep(0.3)
    giver._send(Writer().u8(0x7F))
    giver.sleep(0.2)
    taker._send(Writer().u8(0x7F))
    assert _free_cap(taker, 224 + 38 - 120) == 142, (taker.inventory, taker.text_messages[-2:])
    assert giver.wait_for(lambda: any(i.client_id == mace for i in giver.inventory.values()), timeout=3), \
        giver.inventory

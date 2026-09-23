"""7.4 exhaustion (docs/reference-74/formulas.md, "Exhaustion"): one magic exhaustion for spells and runes -
attack 2 s, strikes and paralyze 1 s, everything else 1 s, UH / IH none; fluids drinkable while exhausted."""
import time

import pytest

from tibia74 import BACKPACK, Item
from tibia74.server import TESTER_GROUP

SPOT = (32139, 32136, 7)             # open ground, no protection zone, 12+ tiles from any spawn and other test
                                     # fields (it was 2 tiles from the bolt test: GFBs and in-fight casters)
CREATURE = 0x63
GFB, UH, PARALYZE, MANA_FLUID = 2304, 2273, 2278, 7


def _mage(new_player, items=(), **kwargs):
    kwargs.setdefault("pos", SPOT)
    return new_player(level=100, vocation=2, maglevel=60, mana=2000, health=100, group_id=TESTER_GROUP,
                      inventory={BACKPACK: Item(1988, contents=list(items))}, **kwargs)


def _bag(p):
    bag = p.open_container(BACKPACK)
    return bag, next(k for k, v in p.containers.items() if v is bag)


def _use_on_self(p, bag, cid, slot):
    p.use_item_with(p.container_pos(cid, slot), bag.items[slot].client_id, slot, p.pos, CREATURE, 1)


def _use_on_ground(p, bag, cid, slot, pos, ground_client_id):
    p.use_item_with(p.container_pos(cid, slot), bag.items[slot].client_id, slot, pos, ground_client_id, 0)


def _exura_works_after(p, since, limit=4.0):
    """Seconds from `since` until "exura" is accepted, trying every 150 ms (None if never within limit).
    Starts 0.3 s after `since`: the action's own mana change must arrive first, or it looks like a cast."""
    time.sleep(max(0.0, since + 0.3 - time.time()))
    while time.time() - since < limit:
        before = p.stats.mana
        p.say("exura")
        if p.wait_for(lambda: p.stats.mana < before, timeout=0.15):
            return time.time() - since
    return None


def _gfb(p, bag, cid, slot):
    _use_on_ground(p, bag, cid, slot, (p.pos[0] + 2, p.pos[1], p.pos[2]), 0)


@pytest.mark.parametrize("action, low, high", [
    ("exura", 0.9, 1.5),              # healing spell: 1 s
    ("exori vis", 0.9, 1.5),          # strike: 1 s
    ("gfb", 1.9, 2.5),                # attack rune: 2 s
    ("uh", 0.0, 0.6),                 # UH rune: no exhaustion (was 1 s)
    ("mana fluid", 0.9, 1.5),         # a fluid exhausts for 1 s afterwards
])
def test_exhaustion_after(new_player, action, low, high):
    p = _mage(new_player, items=[Item(GFB, 50), Item(UH, 50), Item(2006, MANA_FLUID)])
    bag, cid = _bag(p)
    p.set_fight_modes(fight=1, chase=0, safe=0)
    p.wait_for(lambda: p.stats.mana, timeout=3)
    start = time.time()
    {"exura": lambda: p.say("exura"), "exori vis": lambda: p.say("exori vis"), "gfb": lambda: _gfb(p, bag, cid, 0),
     "uh": lambda: _use_on_self(p, bag, cid, 1), "mana fluid": lambda: _use_on_self(p, bag, cid, 2)}[action]()
    waited = _exura_works_after(p, start)
    assert waited is not None and low <= waited <= high, f"exura worked after {waited} s, expected {low}-{high}"


def test_paralyze_rune_exhausts_1_second(new_player):
    p = _mage(new_player, items=[Item(PARALYZE, 5)])
    target = new_player(pos=(SPOT[0] + 3, SPOT[1], SPOT[2]), level=50, vocation=4, storage={30001: 1})
    bag, cid = _bag(p)
    p.set_fight_modes(fight=1, chase=0, safe=0)
    p.wait_for(lambda: p.stats.mana, timeout=3)
    seen = p.wait_for(lambda: p.creatures.get(target.player_id), timeout=3)
    speed = seen.speed
    start = time.time()
    p.use_item_with(p.container_pos(cid, 0), bag.items[0].client_id, 0, target.pos, CREATURE, 1)
    waited = _exura_works_after(p, start)
    assert seen.speed < speed, f"the rune did not paralyze: speed {speed} -> {seen.speed}"
    assert waited is not None and 0.9 <= waited <= 1.5, f"exura worked after {waited} s, expected 1 s (was 2 s)"


def test_fluids_can_be_drunk_while_exhausted(new_player):
    """7.4: a fluid works while magic-exhausted (after the 1 s use delay) - an attack rune's 2 s blocked it."""
    p = _mage(new_player, items=[Item(GFB, 50), Item(2006, MANA_FLUID)])
    bag, cid = _bag(p)
    p.set_fight_modes(fight=1, chase=0, safe=0)
    p.wait_for(lambda: p.stats.mana, timeout=3)
    _gfb(p, bag, cid, 0)
    p.sleep(1.2)                                       # past the use delay, inside the 2 s exhaustion
    before, n = p.stats.mana, len(p.text_messages)
    _use_on_self(p, bag, cid, 1)
    assert p.wait_for(lambda: p.stats.mana > before, timeout=1.5), f"not drunk: {p.text_messages[n:]}"

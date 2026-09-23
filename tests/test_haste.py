"""Haste and wild growth - 7.4 per Tibiantis-notes (speed page) and the tibiantis.info spell list."""
import time

import pytest

from tibia74 import EAST, RIGHT, Item
from tibia74.server import TESTER_GROUP

FIELD = (32150, 32153, 7)            # open grass x-1..x+4, y-1..y+4, 12+ tiles from any spawn and other test fields
RUSH_WOOD, MACHETE = 1499, 2420


def _druid(new_player, level=100, **kwargs):
    kwargs.setdefault("pos", FIELD)
    return new_player(level=level, vocation=2, maglevel=30, mana=1000, group_id=TESTER_GROUP, **kwargs)


def _own_speed(p):
    me = p.wait_for(lambda: p.creatures.get(p.player_id), timeout=3)
    return me


@pytest.mark.parametrize("words, level, expected", [
    ("utani hur", 11, 288),           # base 240: 1.3 x 240 - 24 = 288
    ("utani hur", 100, 518),          # base 418: 519.4, down to even 518 (ours gave 520)
    ("utani gran hur", 11, 352),      # 1.7 x 240 - 56 = 352
    ("utani gran hur", 100, 654),     # 654.6, down to even 654
])
def test_haste_speed_is_the_7_4_formula_rounded_down_to_even(new_player, words, level, expected):
    p = _druid(new_player, level=level)
    me = _own_speed(p)
    normal = me.speed
    assert normal == 218 + 2 * level, f"base speed {normal}"
    p.say(words)
    assert p.wait_for(lambda: me.speed != normal, timeout=3), p.text_messages[-2:]
    assert me.speed == expected, f"{words} at level {level}: speed {me.speed}, expected {expected}"


def test_haste_lasts_66_and_strong_haste_44_seconds(new_player):
    """Both in one test (run side by side): haste was 40 s, strong haste 45 s."""
    fast = _druid(new_player)
    faster = _druid(new_player, pos=(FIELD[0] + 2, FIELD[1] + 2, FIELD[2]))
    fast_me, faster_me = _own_speed(fast), _own_speed(faster)
    normal = fast_me.speed
    fast.say("utani hur")
    faster.say("utani gran hur")
    start = time.time()
    assert fast.wait_for(lambda: fast_me.speed > normal, timeout=3) and faster.wait_for(
        lambda: faster_me.speed > normal, timeout=3)
    assert faster.wait_for(lambda: faster_me.speed == normal, timeout=50), "strong haste still on after 50 s"
    strong = time.time() - start
    assert fast.wait_for(lambda: fast_me.speed == normal, timeout=75 - strong), "haste still on after 75 s"
    haste = time.time() - start
    assert 42 <= strong <= 47, f"strong haste lasted {strong:.1f} s, expected 44"
    assert 64 <= haste <= 69, f"haste lasted {haste:.1f} s, expected 66"


def _wild_growth(new_player, vocation=2):
    p = new_player(pos=FIELD, level=100, vocation=vocation, maglevel=30, mana=1000, group_id=TESTER_GROUP,
                   inventory={RIGHT: Item(MACHETE)})
    target = (p.pos[0] + 1, p.pos[1], p.pos[2])
    p.turn(EAST)
    p.sleep(0.3)
    return p, target


def _rush_wood(p, items, pos):
    return [i for i in p.tile_items(pos) if items.by_client[i.client_id].server_id == RUSH_WOOD]


def test_wild_growth_is_druid_only(new_player, items):
    p, target = _wild_growth(new_player, vocation=1)
    p.say("exevo grav vita")
    assert p.wait_for(lambda: p.messages("vocation"), timeout=3), p.text_messages[-2:]
    assert not _rush_wood(p, items, target)


def test_wild_growth_does_not_stack_and_a_machete_cuts_it(new_player, items):
    p, target = _wild_growth(new_player)
    p.say("exevo grav vita")
    assert p.wait_for(lambda: _rush_wood(p, items, target), timeout=3), f"no rush wood: {p.text_messages[-2:]}"
    p.sleep(1.2)                                       # past the 1 s exhaustion
    n = len(p.text_messages)
    p.say("exevo grav vita")
    assert p.wait_for(lambda: len(p.text_messages) > n, timeout=3), "a second one was not refused"
    assert len(_rush_wood(p, items, target)) == 1, "two rush woods on one tile"
    wood = _rush_wood(p, items, target)[0]
    stackpos = p.tile_items(target).index(wood)
    p.use_item_with(p.inventory_pos(RIGHT), p.inventory[RIGHT].client_id, 0, target, wood.client_id, stackpos)
    assert p.wait_for(lambda: not _rush_wood(p, items, target), timeout=3), f"not cut: {p.text_messages[-2:]}"

"""Spears in 7.4 (task.md "Spears: range, breaking/dropping on the ground, stacking, damage vs 7.4"):

  - stackable: the 7.4 client's Tibia.dat marks the spear (2389) stackable, as items.otb does
  - thrown spears are not used up: they land under the target (a hit) or on a tile of the 3x3 around it (a miss)
    and can be picked up again; they did not break in 7.4 (TibiaWiki rev 6579 / 10893, May-June 2005: "these do
    not disappear when thrown, and can be picked up again"; breaking came with the 2005 updates)
  - range 6 (TibiaWiki rev 131557 / 151060: the Christmas 2007 update cut it from 6 to 3)

Player against player on an open street of Thais, no monsters near (rows 32288-32303, x 32300-32314).
"""
import time

import pytest

from tibia74 import BACKPACK, RIGHT, Item

SPEAR, BAG = 2389, 1988


def _paladin(new_player, pos, inventory):
    p = new_player(pos=pos, level=30, vocation=3, skills={4: 60}, storage={30001: 1}, inventory=inventory)
    assert p.pos == pos, f"paladin placed at {p.pos}, not {pos}"
    p.set_fight_modes(fight=2, chase=0, safe=0)          # balanced, stand still, secure mode off
    return p


def _target(new_player, pos):
    t = new_player(pos=pos, level=300, vocation=4, storage={30001: 1})   # 4500 hp: survives the test
    assert t.pos == pos, f"target placed at {t.pos}, not {pos}"
    return t


def _spears_in_hand(p):
    item = p.inventory.get(RIGHT)
    return item.count if item and item.client_id == SPEAR else 0


def _spears_on(p, pos):
    return sum(i.count for i in p.tile_items(pos) if i.client_id == SPEAR)


def test_spears_stack_in_the_hand(new_player):
    """7 spears in the hand and 3 in the backpack: moving the 3 onto the hand makes one stack of 10."""
    p = _paladin(new_player, (32302, 32288, 7), {RIGHT: Item(SPEAR, 7), BACKPACK: Item(BAG, contents=[Item(SPEAR, 3)])})
    assert _spears_in_hand(p) == 7, p.inventory
    p.open_container(BACKPACK)
    cid = min(p.containers)
    p.move_item(p.container_pos(cid, 0), SPEAR, 0, p.inventory_pos(RIGHT), 3)
    assert p.wait_for(lambda: _spears_in_hand(p) == 10), f"hand: {p.inventory.get(RIGHT)}"
    assert not p.containers[cid].items, f"backpack still holds {p.containers[cid].items}"


def test_thrown_spears_land_on_and_around_the_target_and_do_not_break(new_player):
    """10 spears thrown from 3 tiles: every one ends on the target's tile (hits) or the 3x3 around it (misses),
    none is lost - 7.4 spears did not break."""
    to = (32313, 32300, 7)
    target = _target(new_player, to)
    paladin = _paladin(new_player, (32310, 32300, 7), {RIGHT: Item(SPEAR, 10)})
    around = [(to[0] + dx, to[1] + dy, to[2]) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    before = sum(_spears_on(paladin, pos) for pos in around)
    paladin.attack(target.player_id)
    assert paladin.wait_for(lambda: _spears_in_hand(paladin) == 0, timeout=40), \
        f"{_spears_in_hand(paladin)} spears still in the hand after 40 s"
    paladin.attack(0)
    time.sleep(1)
    landed = {pos: _spears_on(paladin, pos) - (before if pos == to else 0) for pos in around}
    print(f"\n10 spears from 3 tiles landed: {landed}")
    assert sum(_spears_on(paladin, pos) for pos in around) - before == 10, f"spears lost (broken?): {landed}"
    assert landed[to] > 0, f"no spear under the target (about 3 in 4 hit at skill 60): {landed}"


@pytest.mark.parametrize("distance, row, throws", [(6, 32297, True), (7, 32303, False)], ids=["6 tiles", "7 tiles"])
def test_spear_range_is_6(new_player, distance, row, throws):
    """A spear reaches a target 6 tiles away; at 7 tiles the paladin does not throw at all."""
    at = (32300, row, 7)
    target = _target(new_player, (at[0] + distance, row, 7))
    paladin = _paladin(new_player, at, {RIGHT: Item(SPEAR, 5)})
    paladin.attack(target.player_id)
    thrown = paladin.wait_for(lambda: _spears_in_hand(paladin) < 5, timeout=8)
    paladin.attack(0)
    assert bool(thrown) == throws, f"at {distance} tiles: {5 - _spears_in_hand(paladin)} spears thrown in 8 s"

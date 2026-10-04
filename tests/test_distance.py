"""Bows, crossbows and their ammunition in 7.4 (task.md "Royal paladin: bolts / crossbow and arrows / bow distance").

7.4 values (sources in docs/reference-74/formulas.md §6.1 and the task notes):
  - range: bow 6, crossbow 5 (TibiaWiki Bow rev 121686, Crossbow revs 100735-133112, 2007, before 8.0)
  - bows and crossbows have no attack of their own (TibiaWiki "attack = 0" 2006-2007): the ammunition's attack
    goes into the melee formula, max = (5 x skill + 50) x atk x 0.99 / 100. Arrow 25, bolt 30, poison arrow 20,
    power bolt 40 (TibiaWiki revs 55068 / 55062 / 93103 / 78528)
  - hit chance = 91% x min(skill / (15 x d - 1), 1), an adjacent target counting as d = 5 (tibiantis-notes
    distance_calculator); a miss lands on a tile of the 3x3 around the target
  - arrows and bolts are used up, a hit or a miss: nothing lands on the floor (only thrown weapons do,
    test_spears.py; tibiantis-notes counts "bolts used per hour")
  - burst arrow: 0-60% of magic power (level x 2 + magic level x 3, at least 100) on the 3x3 around where it lands
    (tibiantis-notes Magic, distance_calculator)
  - poison arrow: an arrow hit that also poisons (power 50, tibiantis-notes poison)

Player against player (every hit halved, combat.cpp) on a street in north-east Thais with no monster spawn within
16 tiles and no protection zone (x 32390-32398, y 32188-32200). Each test has rows of its own: a target that was
hit stays in fight after the test and cannot log out at once.
"""
import statistics
import time

import pytest

from test_combat_formulas import PHYSICAL, _hits, _target
from tibia74 import AMMO, RIGHT, Item

BOW, CROSSBOW = 2456, 2455
ARROW, BOLT, POISON_ARROW, BURST_ARROW, POWER_BOLT = 2544, 2543, 2545, 2546, 2547
POISON = 30                        # the poison damage colour (const.h TEXTCOLOR_LIGHTGREEN)
X = 32390


def _shooter(new_player, pos, weapon, ammo, count, skill=60, **kwargs):
    kwargs.setdefault("level", 60)
    kwargs.setdefault("vocation", 3)
    p = new_player(pos=pos, skills={4: skill}, storage={30001: 1},
                   inventory={RIGHT: Item(weapon), AMMO: Item(ammo, count)}, **kwargs)
    assert p.pos == pos, f"shooter placed at {p.pos}, not {pos}"
    p.set_fight_modes(fight=2, chase=0, safe=0)          # balanced, stand still, secure mode off
    return p


def _ammo(p):
    item = p.inventory.get(AMMO)
    return item.count if item else 0


def _top(skill, atk):
    """7.4 max hit, halved player against player."""
    return int((5 * skill + 50) * atk * 0.99 / 100) // 2


def _on_floor(p, around, name):
    return sum(i.count for pos in around for i in p.tile_items(pos) if getattr(i, "name", "") == name)


def _around(pos):
    return [(pos[0] + dx, pos[1] + dy, pos[2]) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]


@pytest.mark.parametrize("weapon, ammo, distance, row, shoots", [
    (CROSSBOW, BOLT, 5, 32188, True), (CROSSBOW, BOLT, 6, 32189, False),
    (BOW, ARROW, 6, 32190, True), (BOW, ARROW, 7, 32191, False),
], ids=["crossbow 5", "crossbow 6", "bow 6", "bow 7"])
def test_range_bow_6_crossbow_5(new_player, weapon, ammo, distance, row, shoots):
    """A crossbow reaches 5 tiles and a bow 6; one tile further the paladin does not shoot at all."""
    at = (X, row, 7)
    target = _target(new_player, (X + distance, row, 7))
    paladin = _shooter(new_player, at, weapon, ammo, 10)
    paladin.attack(target.player_id)
    shot = paladin.wait_for(lambda: _ammo(paladin) < 10, timeout=8)
    paladin.attack(0)
    assert bool(shot) == shoots, f"at {distance} tiles: {10 - _ammo(paladin)} shots in 8 s"


def test_hit_chance_follows_skill_and_distance_and_ammo_is_used_up(new_player):
    """Distance skill 30, 60 s each, three paladins at once: a crossbow at 5 tiles and one adjacent to its target
    both hit about 37% (7.4: 91% x 30 / 74 - adjacent counts as 5 tiles), a bow at 2 tiles about 91% (30 / 29 is
    over 1). The old fixed 80% for bolts would fail the first two. Every shot uses its bolt or arrow and none is
    left on the floor around the targets."""
    rows = {"crossbow 5 tiles": (CROSSBOW, BOLT, 5, 32193), "crossbow adjacent": (CROSSBOW, BOLT, 1, 32194),
            "bow 2 tiles": (BOW, ARROW, 2, 32195)}
    runs = {}
    for name, (weapon, ammo, distance, row) in rows.items():
        target = _target(new_player, (X + distance, row, 7))
        paladin = _shooter(new_player, (X, row, 7), weapon, ammo, 100, skill=30)
        runs[name] = (paladin, target, ammo, len(target.animated_texts))
    for paladin, target, _, _ in runs.values():
        paladin.attack(target.player_id)
    time.sleep(60)
    for paladin, _, _, _ in runs.values():
        paladin.attack(0)
    time.sleep(1)
    result = {}
    for name, (paladin, target, ammo, start) in runs.items():
        shots = 100 - _ammo(paladin)
        hits = len(_hits(target, target.pos, start, PHYSICAL))
        floor = _on_floor(paladin, _around(target.pos), "bolt" if ammo == BOLT else "arrow")
        result[name] = (shots, hits, floor)
    print("\nskill 30, 60 s: " + "; ".join(f"{n}: {h} hits of {s} shots ({h / max(s, 1):.0%}), {f} on the floor"
                                         for n, (s, h, f) in result.items()))
    for name, (shots, hits, floor) in result.items():
        assert shots >= 25, f"{name}: only {shots} shots in 60 s (one every 2 s)"
        assert floor == 0, f"{name}: {floor} pieces of ammunition left on the floor - 7.4 uses them up"
    far_shots = result["crossbow 5 tiles"][0] + result["crossbow adjacent"][0]
    far_hits = result["crossbow 5 tiles"][1] + result["crossbow adjacent"][1]
    assert 0.2 * far_shots <= far_hits <= 0.55 * far_shots, \
        f"5 tiles and adjacent: {far_hits} of {far_shots} hit (7.4: 37%)"
    shots, hits, _ = result["bow 2 tiles"]
    assert hits >= 0.75 * shots, f"bow at 2 tiles: {hits} of {shots} hit (7.4: 91%)"


def test_power_bolts_hit_with_attack_40(new_player):
    """Power bolts are attack 40 in 7.4 (ours was 50): distance 60 at 2 tiles, at most
    (5 x 60 + 50) x 40 x 0.99 / 100 = 138, halved 69 (attack 50 would reach 86)."""
    to = (X + 2, 32196, 7)
    target = _target(new_player, to)
    paladin = _shooter(new_player, (X, 32196, 7), CROSSBOW, POWER_BOLT, 100)
    start = len(target.animated_texts)
    paladin.attack(target.player_id)
    time.sleep(60)
    paladin.attack(0)
    time.sleep(1)
    hits = _hits(target, to, start, PHYSICAL)
    top = _top(60, 40)
    print(f"\npower bolts, distance 60, 60 s: max {top}, {100 - _ammo(paladin)} shots, {len(hits)} hits, "
          f"mean {statistics.mean(hits) if hits else 0:.1f}: {sorted(hits)}")
    assert len(hits) >= 18, f"only {len(hits)} hits in 60 s at 2 tiles"
    assert all(1 <= h <= top + 1 for h in hits), f"outside 1-{top}: {sorted(hits)}"
    assert top * 0.35 <= statistics.mean(hits) <= top * 0.65, f"mean {statistics.mean(hits):.1f} of max {top}"


def test_poison_arrows_hit_as_arrows_and_poison(new_player):
    """A poison arrow is an arrow hit by distance skill (attack 20: at most 69, halved 34) and poisons the target:
    small green numbers afterwards (power 50, at most 3 a tick), not the old magic-level poison hits."""
    to = (X + 2, 32197, 7)
    target = _target(new_player, to)
    paladin = _shooter(new_player, (X, 32197, 7), BOW, POISON_ARROW, 10)
    start = len(target.animated_texts)
    paladin.attack(target.player_id)
    assert paladin.wait_for(lambda: _ammo(paladin) == 0, timeout=40), f"{_ammo(paladin)} arrows left after 40 s"
    paladin.attack(0)
    poisoned = target.wait_for(lambda: target.icons & 1, timeout=3)
    time.sleep(9)                                      # two poison ticks
    hits = _hits(target, to, start, PHYSICAL)
    ticks = _hits(target, to, start, POISON)
    top = _top(60, 20)
    print(f"\npoison arrows, distance 60: hits {sorted(hits)} (max {top}), poison {ticks}, poisoned {bool(poisoned)}")
    assert hits and all(1 <= h <= top + 1 for h in hits), f"arrow hits outside 1-{top}: {sorted(hits)}"
    assert poisoned, "the target was never poisoned"
    assert ticks and all(1 <= t <= 3 for t in ticks), f"poison ticks {ticks} (power 50: 3, then 2, then 1)"


def test_burst_arrow_hits_the_3x3_by_magic_power(new_player):
    """A sorcerer (level 50, magic level 40: power 220) shoots 10 burst arrows at a target 4 tiles away: up to
    60% of 220 = 132, halved 66. Its neighbour takes damage as well, a player 3 tiles past the target never does
    (a miss lands at most 1 tile off and bursts 1 tile around). No arrow is left on the floor."""
    row = 32200
    to = (X + 4, row, 7)
    target = _target(new_player, to)
    neighbour = _target(new_player, (X + 5, row, 7))
    far = _target(new_player, (X + 7, row, 7))
    mage = _shooter(new_player, (X, row, 7), BOW, BURST_ARROW, 10, skill=10, level=50, vocation=1, maglevel=40)
    starts = [len(p.animated_texts) for p in (target, neighbour, far)]
    mage.attack(target.player_id)
    assert mage.wait_for(lambda: _ammo(mage) == 0, timeout=40), f"{_ammo(mage)} burst arrows left after 40 s"
    mage.attack(0)
    time.sleep(1)
    got = [_hits(p, p.pos, s, PHYSICAL) for p, s in zip((target, neighbour, far), starts)]
    top = int(220 * 0.6) // 2
    floor = _on_floor(mage, _around(to), "burst arrow")
    print(f"\nburst arrows, power 220 (max {top}): target {sorted(got[0])}, neighbour {sorted(got[1])}, "
          f"3 tiles past {got[2]}, {floor} on the floor")
    assert got[0] and got[1], f"the target ({got[0]}) and its neighbour ({got[1]}) should both be hit"
    assert not got[2], f"a player 3 tiles past the target was hit: {got[2]}"
    assert all(1 <= h <= top + 1 for h in got[0] + got[1]), f"outside 1-{top}: {got[0] + got[1]}"
    assert floor == 0, f"{floor} burst arrows on the floor"

"""Field damage measured in game: a character steps on a field a rune made, steps off at once, and the test reads
every damage number its client shows (animated text) with the time it came. Values from items.xml (`field` attributes,
items.cpp: a `damage` before any `ticks` is the hit on entering, the rest come every `ticks` ms; poison `start` 5
spreads 100 over hits of 5, 4, 3, 2, 1, ConditionDamage::generateDamageList) checked against 7.4 in
docs/reference-74/spell-formulas.md "Fields and bombs":

  - fire field (1492): 20 on entering, then 10 every 10 s, 7 times (TibiaWiki Fire Field rev 72254, 2006-12: "20 fire
    damage ... then 10 fire damage for 7 times"; rev 85637, 2007-02: "each 9 seconds")
  - medium fire field (1493, what the big one decays to): 20 on entering, then 10 every 10 s, 5 times - 70 in all
    (TibiaWiki Fire rev 23177, 2005-11: "Medium Fire Fields: 5 turns, 70 damage", "20 HP as an initial hit ... then
    10 HP each 2 turns"; decided with the user 2026-10-04, it was 7 x 10 with no hit on entering)
  - energy field (1495): 30 on entering, then 25 twice, 10 s apart - 80 in all (TibiaWiki Energy rev 23178, 2005-11:
    "30 HP of initial damage, and then two additional hits for 25 HP each"; decided with the user 2026-10-04, it was
    one 25 as the 2007 pages say)
  - poison field (1496): poison of 100 starting at 5, a hit every 4 s (tibiantis-notes poison.txt: "Poison fields do
    100 periodic poison damage. Damage cycles start at 5"; "Damage starts after 4 seconds and at 4 second intervals")

The conditions tick on the creature's think (1 s); the gaps seen are the item's +0.0 .. +0.1 s. The first one runs
longer: the condition does not count down while the character still stands on the field (Creature::onTickCondition),
so it adds the step off (seen 4.6 s, 10.7-11.7 s)."""
import time

from tibia74 import BACKPACK, EAST, WEST, Item
from tibia74.server import TESTER_GROUP

GOD_GROUP = 3                 # server/sql/seed.sql: access 3, may say /i (create an item on its own tile)
MEDIUM_FIRE_FIELD = 1493

FIRE_FIELD_RUNE, ENERGY_FIELD_RUNE, POISON_FIELD_RUNE = 2301, 2277, 2285
FIRE, ENERGY, POISON = 198, 35, 30   # damage number colours (const.h TEXTCOLOR_ORANGE / LIGHTBLUE / LIGHTGREEN)
INFINITE = bytes([4]) + (64000).to_bytes(2, "little")     # action id 64000: a test character's never-ending rune
STREET = (32326, 32214, 7)    # open Thais street, no protection zone, far from monsters (test_combat_formulas.py)


def _row(r):
    """Target, field tile, caster on row r of the street: the target steps east onto the field and back."""
    y = STREET[1] + 2 * r
    return (STREET[0], y, 7), (STREET[0] + 1, y, 7), (STREET[0] + 4, y, 7)


def _field(new_player, items, rune, row):
    """A caster throws `rune` on the field tile; returns (target, field tile)."""
    at, tile, cast_from = _row(row)
    target = new_player(pos=at, level=300, vocation=4, storage={30001: 1})      # 4500 hp
    assert target.pos == at, f"target placed at {target.pos}, not {at}"
    caster = new_player(pos=cast_from, level=100, vocation=5, maglevel=40, mana=3000, group_id=TESTER_GROUP,
                        storage={30001: 1},
                        inventory={BACKPACK: Item(1988, contents=[Item(rune, 1, attributes=INFINITE)])})
    assert caster.pos == cast_from, f"caster placed at {caster.pos}, not {cast_from}"
    caster.set_fight_modes(fight=1, chase=0, safe=0)
    bag = caster.open_container(BACKPACK)
    cid = next(k for k, v in caster.containers.items() if v is bag)
    stack = caster.tile_items(tile)
    caster.use_item_with(caster.container_pos(cid, 0), items.by_server[rune].client_id, 0,
                         tile, stack[-1].client_id, len(stack) - 1)
    field = items.by_server[{FIRE_FIELD_RUNE: 1492, ENERGY_FIELD_RUNE: 1495, POISON_FIELD_RUNE: 1496}[rune]].client_id
    assert target.wait_for(lambda: any(t.client_id == field for t in target.tile_items(tile)), timeout=3), \
        f"no field on {tile}: {target.tile_items(tile)} {caster.text_messages[-2:]}"
    return target, tile


def _step_through(target, tile, color, seconds):
    """Step onto the field and straight back; every damage number of `color` over the target (on the field or back
    home) for `seconds`, as (seconds since the step, damage)."""
    home = target.pos
    seen, hits = len(target.animated_texts), []
    t0 = time.time()
    assert target.step(EAST), f"could not step onto the field at {tile}"
    assert target.step(WEST, timeout=5), "could not step off the field"
    assert target.pos == home
    while time.time() - t0 < seconds:
        target.wait_for(lambda: len(target.animated_texts) > seen, timeout=max(0.0, seconds - (time.time() - t0)))
        now = time.time() - t0
        with target._lock:
            new, seen = target.animated_texts[seen:], len(target.animated_texts)
        hits += [(round(now, 1), int(t)) for p, c, t in new
                 if c == color and t.strip().isdigit() and tuple(p) in (tuple(home), tuple(tile))]
    return hits


def _intervals(hits):
    return [round(b[0] - a[0], 1) for a, b in zip(hits, hits[1:])]


def _every(hits, tick):
    """The first gap is the tick plus the time on the field (up to 2.5 s), the others the tick +-0.6 s (so a 5 s
    poison tick fails)."""
    gaps = _intervals(hits)
    return bool(gaps) and tick - 1 <= gaps[0] <= tick + 2.5 and all(tick - 0.6 <= g <= tick + 0.6 for g in gaps[1:])


def test_fire_field_burns_20_then_10_every_10_seconds(new_player, items):
    target, tile = _field(new_player, items, FIRE_FIELD_RUNE, 0)
    hits = _step_through(target, tile, FIRE, 33)
    print(f"\nfire field: {hits}, intervals {_intervals(hits)}")
    assert hits and hits[0][1] == 20 and hits[0][0] < 1.5, f"no 20 on entering: {hits}"
    burns = hits[1:]
    assert [d for _, d in burns] == [10, 10, 10], f"not 10 every 10 s: {hits}"
    assert _every(hits, 10), f"not every 10 s: {_intervals(hits)}"


def test_medium_fire_field_burns_20_then_10_five_times(new_player, items):
    """A god makes a medium fire field on its own tile (/i 1493) and steps off; the target steps on it and back."""
    at, tile = (32326, 32213, 7), (32327, 32213, 7)        # the row above the fire field's (row 0)
    target = new_player(pos=at, level=300, vocation=4, storage={30001: 1})
    assert target.pos == at, f"target placed at {target.pos}, not {at}"
    god = new_player(pos=tile, group_id=GOD_GROUP, storage={30001: 1})
    assert god.pos == tile, f"god placed at {god.pos}, not {tile}"
    god.say(f"/i {MEDIUM_FIRE_FIELD}")
    field = items.by_server[MEDIUM_FIRE_FIELD].client_id
    assert target.wait_for(lambda: any(t.client_id == field for t in target.tile_items(tile)), timeout=3), \
        f"no medium fire field on {tile}: {target.tile_items(tile)}"
    assert god.step(EAST), "the god could not step off the field"       # it may burn as well: not over the target
    hits = _step_through(target, tile, FIRE, 60)
    print(f"\nmedium fire field: {hits}, intervals {_intervals(hits)}")
    assert hits and hits[0][1] == 20 and hits[0][0] < 1.5, f"no 20 on entering: {hits}"
    assert [d for _, d in hits[1:]] == [10] * 5, f"not 10 five times: {hits}"
    assert _every(hits, 10), f"not every 10 s: {_intervals(hits)}"


def test_energy_field_hits_30_then_25_twice(new_player, items):
    target, tile = _field(new_player, items, ENERGY_FIELD_RUNE, 1)
    hits = _step_through(target, tile, ENERGY, 26)
    print(f"\nenergy field: {hits}, intervals {_intervals(hits)}")
    assert [d for _, d in hits] == [30, 25, 25], f"not 30 then 25 twice: {hits}"
    assert hits[0][0] < 1.5, f"the 30 did not come on entering: {hits}"
    assert _every(hits, 10), f"the 25s not 10 s apart: {hits}"


def test_poison_field_poisons_from_5_every_4_seconds(new_player, items):
    target, tile = _field(new_player, items, POISON_FIELD_RUNE, 2)
    hits = _step_through(target, tile, POISON, 23)
    print(f"\npoison field: {hits}, intervals {_intervals(hits)}")
    assert len(hits) >= 5, f"too few poison hits in 23 s: {hits}"
    assert [d for _, d in hits[:5]] == [5, 5, 5, 5, 4], f"not 5, 5, 5, 5, 4 (100 starting at 5): {hits}"
    assert _every(hits, 4), f"not every 4 s: {_intervals(hits)}"

"""Magic level and skill training as 7.4 (docs/reference-74/formulas.md §8), asked by the user 2026-10-03: every
spell or rune counts the mana it costs; the next magic level takes 1600 x b^ML mana (b: mage 1.1, paladin 1.4,
knight 3.0 - so a knight's ML 9 takes 10.5 million, a paladin's ML 25 7.2 million, a mage's ML 71 1.26 million);
the next skill level takes base x b^(skill - 10) tries (base 50 melee/fist, 30 distance, 100 shielding; b knight
melee 1.1, ...). A character starts one cast or one hit short of the next level and must reach it exactly there."""
import re
import time

import pytest

from tibia74 import SERVER_DIR, Item

FIELD = (32320, 32222, 7)          # Thais street, no protection zone, far from monsters (test_combat_formulas.py
                                   # uses the rows above)
SORCERER, DRUID, PALADIN, KNIGHT = 1, 2, 3, 4
B = {SORCERER: 1.1, DRUID: 1.1, PALADIN: 1.4, KNIGHT: 3.0}


def mana_for_next(vocation, maglevel):
    return int(1600 * B[vocation] ** maglevel)


@pytest.mark.parametrize("vocation, maglevel", [(SORCERER, 0), (KNIGHT, 5), (KNIGHT, 8), (PALADIN, 15),
                                                (PALADIN, 25), (SORCERER, 70)],
                         ids=["ML 0 (any)", "knight ML 5", "knight ML 8", "paladin ML 15", "paladin ML 25",
                              "sorcerer ML 70"])
def test_the_next_magic_level_takes_1600_times_b_to_the_ml_mana(new_player, vocation, maglevel):
    """Two light spells of 20 mana each: the first leaves the character 1 mana short, the second levels it."""
    need = mana_for_next(vocation, maglevel)
    slack = need // 1_000_000           # the engine works it out in single precision: 7 mana off at 7.2 million
    p = new_player(pos=FIELD, level=100, vocation=vocation, maglevel=maglevel, mana=500, storage={30001: 1},
                   manaspent=need - 21 - slack)
    assert p.wait_for(lambda: p.stats.magic_level == maglevel, timeout=3), p.stats
    p.say("utevo lux")                                              # 20 mana
    time.sleep(1.2)
    assert p.stats.magic_level == maglevel, f"advanced {need - 1} of {need} mana in"
    p.say("utevo lux")
    assert p.wait_for(lambda: p.stats.magic_level == maglevel + 1, timeout=3), \
        f"ML {maglevel} -> {maglevel + 1} should take {need} mana: still {p.stats.magic_level}, {p.text_messages[-2:]}"
    assert p.messages(f"You advanced to magic level {maglevel + 1}"), p.text_messages[-3:]


@pytest.mark.parametrize("skill, b, base, value", [(2, 1.1, 50, 99), (2, 1.1, 50, 103)],
                         ids=["knight sword 99", "knight sword 103"])
def test_the_next_skill_level_takes_base_times_b_tries(new_player, skill, b, base, value):
    """A knight one try short of the next sword level hits a target once and advances."""
    need = int(base * b ** (value - 10))
    target = new_player(pos=(FIELD[0] + 1, FIELD[1] + 2, FIELD[2]), level=300, vocation=KNIGHT, storage={30001: 1})
    p = new_player(pos=(FIELD[0], FIELD[1] + 2, FIELD[2]), level=100, vocation=KNIGHT, storage={30001: 1},
                   skills={skill: value}, skill_tries={skill: need - 1}, inventory={5: Item(2376)})   # a sword
    assert p.wait_for(lambda: p.skills.get("sword", (0,))[0] == value, timeout=3), p.skills
    p.set_fight_modes(fight=2, chase=1, safe=0)
    p.attack(target.player_id)
    advanced = p.wait_for(lambda: p.skills["sword"][0] == value + 1, timeout=6)
    p.attack(0)
    assert advanced, f"sword {value} -> {value + 1} should take {need} tries: {p.skills['sword']}"


# --- which actions train which skill (task.md "Which actions train which skill", "Fist fighting ... skills start at
# 10"). 7.4: a melee or distance swing is a try, a shot that draws blood counts double for distance; a try counts
# only while you drew blood on your target within the last 30 tries (attacks made or received); every attack your
# shield faces (two a turn at most) is a shielding try, blood, spark or puff, and only with a shield - never a
# weapon; every cast on water that still has a fish is a fishing try, a catch counts double (TibiaWiki "Training"
# 2006-02 rev 28743 and 2008-05 rev 158855, "Shielding" 2007-03 rev 88636, "Fishing" 2006-01 rev 25585;
# docs/reference-74/tibiantis-notes/training.txt). Every skill starts at 10, magic level at 0 ("Skills" 2007-01
# rev 77912).
FIST, CLUB, SWORD_SKILL, AXE, DISTANCE, SHIELDING, FISHING = range(7)
SKILL_NAMES = ("fist", "club", "sword", "axe", "distance", "shielding", "fishing")
SWORD, MAGIC_SWORD, CROSSBOW, BOLT, DRAGON_SHIELD, FISHING_ROD = 2376, 2400, 2455, 2543, 2516, 2580
FISH_WATER = 490                   # 491 no fish, 492 fished out (back to 490 after 120 s)
SHORE = (32320, 32226, 7)          # FIELD's street runs along the water at x 32319
SKILL_BASE = {FIST: 50, DISTANCE: 30, SHIELDING: 100, FISHING: 20}   # tries for skill 10 -> 11, any vocation


def _at(dx, dy):
    return (FIELD[0] + dx, FIELD[1] + dy, FIELD[2])


def _skill(p, name):
    return p.skills.get(name, (0, 0))[0]


def _one_try_short(new_player, pos, vocation, skill, **kwargs):
    """A level 100 character with `skill` at 10, one try short of 11 (the client shows 99%)."""
    p = new_player(pos=pos, level=100, vocation=vocation, storage={30001: 1},
                   skill_tries={skill: SKILL_BASE[skill] - 1}, **kwargs)
    name = SKILL_NAMES[skill]
    assert p.wait_for(lambda: p.skills.get(name, (0, 0))[0] == 10 and p.skills[name][1] >= 90, timeout=3), p.skills
    return p, name


def _draw_blood(fighter, target, timeout=15):
    """`fighter` hits `target` until it bleeds: a try only counts within 30 tries of drawing blood."""
    fighter.set_fight_modes(fight=1, chase=0, safe=0)
    fighter.attack(target.player_id)
    bled = target.wait_for(lambda: target.stats.max_health and target.stats.health < target.stats.max_health,
                           timeout=timeout)
    assert bled, f"{fighter.name} drew no blood on {target.name} in {timeout} s"


def test_a_new_character_has_every_skill_at_10_and_magic_level_0(new_player):
    p = new_player(pos=_at(2, 0), storage={30001: 1})
    assert p.wait_for(lambda: len(p.skills) == 7, timeout=3), p.skills
    assert {name: value[0] for name, value in p.skills.items()} == {name: 10 for name in SKILL_NAMES}
    assert p.stats.magic_level == 0, p.stats


def test_rate_skill_and_rate_mag_are_1():
    """Real 7.4 speed: config.lua RateSkill and RateMag multiply every try and every mana point."""
    config = (SERVER_DIR / "config.lua").read_text(encoding="latin-1")
    assert re.search(r"^\s*RateSkill\s*=\s*1\s*$", config, re.M), "RateSkill should be 1"
    assert re.search(r"^\s*RateMag\s*=\s*1\s*$", config, re.M), "RateMag should be 1"


def test_a_fist_hit_with_no_weapon_trains_fist_fighting(new_player):
    """Nothing in either hand: the character fights with its fists (atk 7) and fist fighting trains."""
    target = new_player(pos=_at(3, 4), level=300, vocation=KNIGHT, storage={30001: 1})
    p, name = _one_try_short(new_player, _at(2, 4), KNIGHT, FIST)
    assert 5 not in p.inventory and 6 not in p.inventory, p.inventory
    p.set_fight_modes(fight=1, chase=0, safe=0)
    p.attack(target.player_id)
    advanced = p.wait_for(lambda: _skill(p, name) == 11, timeout=15)
    p.attack(0)
    assert advanced, f"fists: still {p.skills[name]}, the target lost {target.stats.max_health - target.stats.health}"
    assert [_skill(p, s) for s in ("club", "sword", "axe")] == [10, 10, 10], p.skills


def test_a_crossbow_shot_trains_distance_fighting(new_player):
    target = new_player(pos=_at(4, 6), level=300, vocation=KNIGHT, storage={30001: 1})
    p, name = _one_try_short(new_player, _at(2, 6), PALADIN, DISTANCE,
                             inventory={5: Item(CROSSBOW), 10: Item(BOLT, 100)})
    p.set_fight_modes(fight=1, chase=0, safe=0)
    p.attack(target.player_id)
    advanced = p.wait_for(lambda: _skill(p, name) == 11, timeout=20)
    p.attack(0)
    assert advanced, f"crossbow: still {p.skills[name]}, the target lost {target.stats.max_health - target.stats.health}"


def test_a_blocked_attack_trains_shielding(new_player):
    """A knight with a dragon shield bleeds a weak attacker, whose fists (max 7) its shield then blocks: the next
    attack the shield faces is the missing try."""
    p, name = _one_try_short(new_player, _at(2, 8), KNIGHT, SHIELDING, inventory={6: Item(DRAGON_SHIELD)})
    attacker = new_player(pos=_at(3, 8), level=100, vocation=KNIGHT, storage={30001: 1})
    _draw_blood(p, attacker)
    attacker.set_fight_modes(fight=1, chase=0, safe=0)
    attacker.attack(p.player_id)
    advanced = p.wait_for(lambda: _skill(p, name) == 11, timeout=10)
    attacker.attack(0)
    p.attack(0)
    assert advanced, f"shielding: still {p.skills[name]}"


def test_an_attack_that_draws_blood_through_the_shield_still_trains_shielding(new_player):
    """7.4 counts every attack the shield faces - blood, spark or puff. A magic sword (sword 80) gets through a
    dragon shield at shielding 10 nearly every time: by the first hit that draws blood the try is in."""
    p, name = _one_try_short(new_player, _at(2, 10), KNIGHT, SHIELDING, inventory={6: Item(DRAGON_SHIELD)})
    attacker = new_player(pos=_at(3, 10), level=100, vocation=KNIGHT, storage={30001: 1}, skills={SWORD_SKILL: 80},
                          inventory={5: Item(MAGIC_SWORD)})
    _draw_blood(p, attacker)
    full = p.stats.health
    attacker.set_fight_modes(fight=1, chase=0, safe=0)
    attacker.attack(p.player_id)
    bled = p.wait_for(lambda: p.stats.health < full, timeout=10)
    advanced = p.wait_for(lambda: _skill(p, name) == 11, timeout=1)   # the try comes before the damage
    attacker.attack(0)
    p.attack(0)
    assert bled, "the magic sword drew no blood in 10 s"
    assert advanced, f"the first blooded hit trained no shielding: {p.skills[name]}, lost {full - p.stats.health}"


def test_blocking_with_a_weapon_trains_no_shielding(new_player):
    """No shield: the sword blocks, but only a shield trains shielding."""
    p, name = _one_try_short(new_player, _at(2, 12), KNIGHT, SHIELDING, inventory={5: Item(SWORD)})
    attacker = new_player(pos=_at(3, 12), level=100, vocation=KNIGHT, storage={30001: 1})
    _draw_blood(p, attacker)
    attacker.set_fight_modes(fight=1, chase=0, safe=0)
    attacker.attack(p.player_id)
    time.sleep(8)                                                    # four attacks
    attacker.attack(0)
    p.attack(0)
    assert p.skills[name][0] == 10, f"a sword trained shielding: {p.skills[name]}"


def test_fishing_on_water_with_fish_trains_fishing(new_player, items):
    """One cast on water that still has a fish is a try (a catch two)."""
    water = (SHORE[0] - 1, SHORE[1], SHORE[2])
    p, name = _one_try_short(new_player, SHORE, KNIGHT, FISHING, inventory={5: Item(FISHING_ROD)})
    assert p.wait_for(lambda: p.tile_items(water), timeout=3), "the water tile is not in view"
    ground = p.tile_items(water)[0]
    assert ground.client_id == items.by_server[FISH_WATER].client_id, f"{water} is {ground}, not water with fish"
    p.use_item_with(p.inventory_pos(5), items.by_server[FISHING_ROD].client_id, 0, water, ground.client_id, 0)
    assert p.wait_for(lambda: _skill(p, name) == 11, timeout=3), f"fishing: still {p.skills[name]}"

"""Magic level and skill training as 7.4 (docs/reference-74/formulas.md §8), asked by the user 2026-10-03: every
spell or rune counts the mana it costs; the next magic level takes 1600 x b^ML mana (b: mage 1.1, paladin 1.4,
knight 3.0 - so a knight's ML 9 takes 10.5 million, a paladin's ML 25 7.2 million, a mage's ML 71 1.26 million);
the next skill level takes base x b^(skill - 10) tries (base 50 melee/fist, 30 distance, 100 shielding; b knight
melee 1.1, ...). A character starts one cast or one hit short of the next level and must reach it exactly there."""
import time

import pytest

from tibia74 import Item

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

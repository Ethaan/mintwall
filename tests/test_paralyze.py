"""Paralyze rune (adana ani) - 7.4 per Tibiantis-notes (speed page): speed set to 40 whatever the level, for
about 10 s; speed items still add; haste is cancelled; healing spells/runes and haste remove it."""
import time

import pytest

from tibia74 import BACKPACK, FEET, Item
from tibia74.server import TESTER_GROUP

SPOT = (32061, 32191, 7)             # open ground, no protection zone, 12+ tiles from any spawn
CREATURE = 0x63
PARALYZE, BOOTS_OF_HASTE = 2278, 2195


def _paralyze(new_player, target_level=100, caster_group=TESTER_GROUP, **target_kwargs):
    target_kwargs.setdefault("vocation", 4)   # a vocation: Rookgaard characters (none) cannot be attacked
    caster = new_player(pos=SPOT, level=100, vocation=2, maglevel=60, mana=2000, group_id=caster_group,
                        inventory={BACKPACK: Item(1988, contents=[Item(PARALYZE, 5)])})
    target = new_player(pos=(caster.pos[0] + 2, caster.pos[1], caster.pos[2]), level=target_level,
                        storage={30001: 1}, **target_kwargs)
    bag = caster.open_container(BACKPACK)
    cid = next(k for k, v in caster.containers.items() if v is bag)
    caster.set_fight_modes(fight=1, chase=0, safe=0)
    seen = caster.wait_for(lambda: caster.creatures.get(target.player_id), timeout=3)
    normal = seen.speed
    caster.use_item_with(caster.container_pos(cid, 0), bag.items[0].client_id, 0, target.pos, CREATURE, 1)
    assert caster.wait_for(lambda: seen.speed != normal, timeout=3), f"not paralyzed: {caster.text_messages[-2:]}"
    return caster, target, seen, normal


@pytest.mark.parametrize("level", [20, 150])
def test_paralyze_sets_speed_40_whatever_the_level(new_player, level):
    """It was base speed x -1, i.e. speed 0: the target could not walk at all, for 60 s."""
    caster, target, seen, normal = _paralyze(new_player, target_level=level)
    assert seen.speed == 40, f"paralyzed speed {seen.speed} (normal {normal}), expected 40"


def test_paralyze_lasts_about_10_seconds(new_player):
    caster, target, seen, normal = _paralyze(new_player)
    start = time.time()
    assert caster.wait_for(lambda: seen.speed == normal, timeout=15), f"still at speed {seen.speed} after 15 s"
    assert 8.5 <= time.time() - start <= 12, f"paralyzed for {time.time() - start:.1f} s, expected about 10"


def test_speed_items_still_count_while_paralyzed(new_player):
    caster, target, seen, normal = _paralyze(new_player, inventory={FEET: Item(BOOTS_OF_HASTE)})
    assert seen.speed == 40 + 40, f"paralyzed speed with boots of haste {seen.speed}, expected 80"


@pytest.mark.parametrize("words", ["exura", "utani hur"])
def test_healing_or_haste_removes_paralyze(new_player, words):
    caster, target, seen, normal = _paralyze(new_player, vocation=2, maglevel=20, mana=500)
    target.say(words)
    assert caster.wait_for(lambda: seen.speed >= normal, timeout=3), f"'{words}' left speed at {seen.speed}"


def test_paralyzing_a_player_gives_no_skull(new_player):
    """Tibiantis-notes: casting paralyze gives no skull (it does block entering a protection zone)."""
    caster, target, seen, normal = _paralyze(new_player, caster_group=1)
    me = target.wait_for(lambda: target.creatures.get(caster.player_id), timeout=3)
    caster.sleep(1.5)
    assert me.skull == 0, f"the caster got skull {me.skull}"


def test_using_the_rune_costs_600_mana(new_player):
    """Tibiantis: 600 mana to use (it was free)."""
    caster = new_player(pos=SPOT, level=100, vocation=2, maglevel=60, mana=2000, group_id=TESTER_GROUP,
                        inventory={BACKPACK: Item(1988, contents=[Item(PARALYZE, 5)])})
    target = new_player(pos=(caster.pos[0] + 2, caster.pos[1], caster.pos[2]), level=50, vocation=4, storage={30001: 1})
    bag = caster.open_container(BACKPACK)
    cid = next(k for k, v in caster.containers.items() if v is bag)
    caster.set_fight_modes(fight=1, chase=0, safe=0)
    caster.wait_for(lambda: caster.stats.mana and caster.creatures.get(target.player_id), timeout=3)
    before = caster.stats.mana
    caster.use_item_with(caster.container_pos(cid, 0), bag.items[0].client_id, 0, target.pos, CREATURE, 1)
    assert caster.wait_for(lambda: caster.stats.mana != before, timeout=3), caster.text_messages[-2:]
    caster.sleep(0.3)
    assert before - caster.stats.mana == 600, f"paid {before - caster.stats.mana} mana"


def test_the_rune_needs_600_mana(new_player):
    caster = new_player(pos=SPOT, level=100, vocation=2, maglevel=60, mana=599, group_id=TESTER_GROUP,
                        inventory={BACKPACK: Item(1988, contents=[Item(PARALYZE, 5)])})
    target = new_player(pos=(caster.pos[0] + 2, caster.pos[1], caster.pos[2]), level=50, vocation=4, storage={30001: 1})
    bag = caster.open_container(BACKPACK)
    cid = next(k for k, v in caster.containers.items() if v is bag)
    caster.set_fight_modes(fight=1, chase=0, safe=0)
    seen = caster.wait_for(lambda: caster.creatures.get(target.player_id), timeout=3)
    normal = seen.speed
    caster.use_item_with(caster.container_pos(cid, 0), bag.items[0].client_id, 0, target.pos, CREATURE, 1)
    assert caster.wait_for(lambda: caster.messages("not have enough mana"), timeout=3), caster.text_messages[-2:]
    assert seen.speed == normal

"""Spells are learned from NPC teachers before they can be cast, as in 7.4 (decided with the user 2026-10-01). What each
teacher teaches to which vocation, the prices and magic levels are Tibiantis' (npc/lib/spells74.lua, made by
tools/apply-tibiantis-spells.py from docs/reference-74/spells-tibiantis.json); npc/lib/spellteacher.lua says it."""
import re

import pytest

from tibia74 import BACKPACK, SERVER_DIR, Item
from tibia74.quest import next_to, npc_pos, talk_to
from tibia74.server import TESTER_GROUP

GOLD, BAG = 2148, 1988
SPELLS74 = (SERVER_DIR / "data" / "npc" / "lib" / "spells74.lua").read_text(encoding="utf-8")
TEACHERS = dict(re.findall(r'^\t\["([^"]+)"\] = \{(\[.*)\},$', SPELLS74, re.M))


def _teaches(npc):
    """{spell: [vocations]} of a teacher, from spells74.lua."""
    return {name: [int(v) for v in vocs.split(", ")]
            for name, vocs in re.findall(r'\["([^"]+)"\] = \{([\d, ]+)\}', TEACHERS[npc])}


def _coins(gold):
    """Gold in stacks of up to 100, as it lies in a backpack."""
    return [Item(GOLD, min(100, gold - n)) for n in range(0, gold, 100)]


def _student(new_player, npc, vocation, gold=0, **kwargs):
    kwargs.setdefault("spells", [])
    p = next_to(new_player, npc_pos(npc), level=20, vocation=vocation, group_id=TESTER_GROUP,
                storage={30001: 1}, inventory={BACKPACK: Item(BAG, contents=_coins(gold))}, **kwargs)
    assert p.open_container(BACKPACK), "no backpack"
    return p


def _gold(p):
    return sum(i.count for i in p.all_items() if i.name == "gold coin")


def test_a_spell_must_be_learned_before_it_is_cast(new_player):
    p = new_player(level=20, vocation=2, maglevel=5, mana=100, spells=[], storage={30001: 1})
    p.say("exura")
    assert p.wait_for(lambda: p.messages("learn this spell first"), timeout=3), p.text_messages[-3:]


def test_marvik_teaches_a_druid_light_healing_for_170_gold(new_player, db):
    p = _student(new_player, "Marvik", vocation=2, gold=200, maglevel=1, mana=100)
    said = talk_to(p, "Marvik", "hi", "light healing", "yes")
    assert any("Do you want to learn the spell 'Light Healing' for 170 gold?" in s for s in said), said
    assert any("Here you are" in s for s in said), said
    assert p.wait_for(lambda: _gold(p) == 30, timeout=3), f"{_gold(p)} gold left, not 30"

    said = talk_to(p, "Marvik", "hi", "light healing", "yes")
    assert any("You already know how to cast this spell." in s for s in said), said
    p.say("exura")
    p.wait_for(lambda: p.messages("learn this spell first"), timeout=2)
    assert not p.messages("learn this spell first"), p.text_messages[-3:]
    p.logout()
    assert "Light Healing" in [s.title() for s in db.spells(p.character.guid)]


def test_a_teacher_turns_away_another_vocation(new_player):
    p = _student(new_player, "Marvik", vocation=4, gold=200)
    said = talk_to(p, "Marvik", "hi", "light healing")
    assert any("this spell is only for druids" in s for s in said), said


def test_a_teacher_wants_the_magic_level(new_player):
    p = _student(new_player, "Marvik", vocation=2, gold=2000, maglevel=7)
    said = talk_to(p, "Marvik", "hi", "ultimate healing", "yes")
    assert any("You must have magic level 8 or better to learn this spell!" in s for s in said), said
    assert p.wait_for(lambda: _gold(p) == 2000, timeout=2)


def test_a_teacher_wants_the_money(new_player):
    p = _student(new_player, "Marvik", vocation=2, gold=100, maglevel=1)
    said = talk_to(p, "Marvik", "hi", "light healing", "yes")
    assert any("You do not have enough money" in s for s in said), said


@pytest.mark.parametrize("vocation, learns", [(4, False), (8, True)], ids=["knight", "elite knight"])
def test_eremo_teaches_challenge_to_elite_knights_only(new_player, vocation, learns):
    p = _student(new_player, "Eremo", vocation=vocation, gold=2000, maglevel=4, premium_days=30)
    said = talk_to(p, "Eremo", "hi", "challenge", "yes")
    if learns:
        assert any("Here you are" in s for s in said), said
    else:
        assert any("only for promoted knights" in s for s in said), said


@pytest.mark.parametrize("npc", sorted(TEACHERS))
def test_every_teacher_lists_his_spells(new_player, npc):
    """Tibiantis' 24 teachers, each with what he teaches the first vocation he teaches."""
    teaches = _teaches(npc)
    vocation = min(v for vocs in teaches.values() for v in vocs)
    p = _student(new_player, npc, vocation=vocation, premium_days=30)
    said = talk_to(p, npc, "hi", "spells", stay=True)
    assert any("I teach" in s for s in said), said
    mine = [name for name, vocs in teaches.items() if vocation in vocs]

    def missing():                     # a long list comes line by line, seconds apart
        text = " ".join(t for n, _, t in p.speech if n == npc)
        return [name for name in mine if f"'{name}'" not in text]
    p.wait_for(lambda: not missing(), timeout=20)
    assert not missing(), f"{npc} does not list {missing()}: {[t for n, _, t in p.speech if n == npc]}"

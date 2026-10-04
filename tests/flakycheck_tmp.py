"""TEMPORARY (flaky-NPC verification, delete me): the same NPC visits over and over in one long session."""
import time

import pytest

import test_npc_talk as talk
import test_shops as shops
from tibia74.quest import talk_to

NAMES = ["Hardek", "Wyda", "Frodo", "Gorn", "Jimbin", "A Wrinkled Beholder", "Nezil", "Bezil"]


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("round_", range(10))
def test_talk_again(new_player, name, round_):
    talk.test_npc_answers(new_player, name)


@pytest.mark.parametrize("name", ["Hardek", "Frodo", "Gorn", "Nezil"])
@pytest.mark.parametrize("round_", range(10))
def test_visit_again(new_player, name, round_):
    p = shops._visit(new_player, shops.NPCS[name])
    talk_to(p, name, "bye")

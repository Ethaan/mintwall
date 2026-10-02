"""The Thais gate guards (npc/lib/guard.lua; TibiaWiki 2006: each "protects the city from creatures"; decided with the
user 2026-09-30): a wild monster near a guard dies, the rat bounty pays 1 gold for a dead rat, insults burn."""
import pytest

from tibia74 import BACKPACK, Item
from tibia74.quest import talk_to
from tibia74.server import TESTER_GROUP
from test_npc_talk import NPCS, near

GUARDS = ["Grof, the guard", "Tim, The Guard", "Kulag, the guard", "Walter, The Guard"]
DEAD_RAT = 2813


@pytest.mark.parametrize("guard", GUARDS)
def test_guard_kills_a_monster_at_the_gate(new_player, guard):
    """A GM puts a troll beside the guard: within a few seconds it is dead."""
    pos = NPCS[guard].positions[0]
    gm = near(new_player, pos, group_id=3, storage={30001: 1})
    gm.say("/m Troll")
    troll = gm.wait_for(lambda: next((c for c in gm.creatures.values() if c.name.lower() == "troll"), None), timeout=3)
    assert troll, [c.name for c in gm.creatures.values()]
    assert gm.wait_for(lambda: troll.id in gm.removed_creatures or gm.creatures.get(troll.id) is None
                       or gm.creatures[troll.id].health == 0, timeout=8), troll
    assert gm.wait_for(lambda: any("Get lost, you beast!" in t for n, _, t in gm.speech if n == guard), timeout=3),         gm.speech[-3:]


def test_guard_pays_the_rat_bounty(new_player):
    guard = "Kulag, the guard"
    p = near(new_player, NPCS[guard].positions[0], level=10, group_id=TESTER_GROUP, storage={30001: 1},
             inventory={BACKPACK: Item(1988, contents=[Item(DEAD_RAT)])})
    p.open_container(BACKPACK)
    replies = talk_to(p, guard, "hi", "rat", "yes")
    assert any("Do you bring a freshly killed rat for a bounty of 1 gold?" in r for r in replies), replies
    assert any("Here is your reward." in r for r in replies), replies
    assert p.wait_for(lambda: any(i.name == "gold coin" for i in p.all_items()), timeout=3), p.all_items()
    assert not any(i.name == "dead rat" for i in p.all_items())
    replies = talk_to(p, guard, "hi", "rat", "yes")                     # none left
    assert any("it's gone" in r for r in replies), replies


def test_guard_burns_an_insult(new_player):
    guard = "Walter, The Guard"
    p = near(new_player, NPCS[guard].positions[0], level=10, storage={30001: 1})
    before = p.stats.health
    replies = talk_to(p, guard, "hi", "you idiot")
    assert any("Take this!" in r for r in replies), replies
    assert p.wait_for(lambda: p.stats.health < before, timeout=6), (before, p.stats.health)

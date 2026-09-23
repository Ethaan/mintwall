"""Boat travel: the captain takes the fare and the ship brings you there."""
import pytest

from tibia74 import BACKPACK, NORTH, Item, SERVER_DIR
from tibia74.db import BEGINNER_SET_GIVEN
from tibia74.npcs import load_npcs
from tibia74.server import TESTER_GROUP

BLUEBEAR = load_npcs(SERVER_DIR)["Captain Bluebear"].pos    # Thais harbour
EDRON_HARBOUR = (33176, 31764, 7)                             # barco_thais.lua EdronPosition
FARE = 110


@pytest.mark.parametrize("lines", [
    ["hi", "edron", "yes"],              # the usual conversation (StdModule.travel)
    ["bring me to edron"],               # the one-line shortcut, without greeting
], ids=["conversation", "bring-me-to"])
def test_captain_bluebear_sails_from_thais_to_edron(new_player, db, lines):
    p = new_player(pos=(BLUEBEAR[0], BLUEBEAR[1] + 1, BLUEBEAR[2]), level=50, premium_days=30,
                   group_id=TESTER_GROUP, storage={BEGINNER_SET_GIVEN: 1},
                   inventory={BACKPACK: Item(1988, contents=[Item(2152, 2)])})   # 200 gp
    said = p.talk(*lines, npc="Captain Bluebear")
    assert p.wait_for(lambda: p.pos == EDRON_HARBOUR, timeout=5), f"still at {p.pos}; the captain said {said}"

    p.logout()
    money = sum({2148: 1, 2152: 100, 2160: 10000}.get(r["itemtype"], 0) * r["count"]
                for r in db.items(p.character.guid))
    assert money == 200 - FARE, f"paid {200 - money} gp for a {FARE} gp trip"


def test_no_teleport_from_thais_back_to_rookgaard(new_player):
    """A magic forcefield next to the Thais temple sent players to the Rookgaard temple (removed)."""
    spot = (32366, 32235, 7)
    p = new_player(pos=(spot[0], spot[1] + 1, spot[2]), level=8, town_id=2)
    p.step(NORTH)                      # onto the spot
    assert p.wait_for(lambda: p.pos == spot, timeout=3), f"could not step onto {spot}: {p.pos}"
    p.sleep(1)
    assert p.pos == spot, f"teleported to {p.pos}"

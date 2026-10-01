"""Boat travel: the captain takes the fare and the ship brings you there."""
import pytest

from tibia74 import BACKPACK, NORTH, Item, SERVER_DIR
from tibia74.db import BEGINNER_SET_GIVEN
from tibia74.npcs import load_npcs
from tibia74.server import TESTER_GROUP

BLUEBEAR = load_npcs(SERVER_DIR)["Captain Bluebear"].pos    # Thais harbour
EDRON_HARBOUR = (33176, 31764, 7)                             # barco_thais.lua EdronPosition
FARE = 150                                                    # TibiaWiki 2005: Thais-Edron 150


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


@pytest.mark.parametrize("lines", [["hi", "carlin", "yes"], ["bring me to carlin"]], ids=["conversation", "bring-me-to"])
def test_ships_take_premium_players_only(new_player, lines):
    """TibiaWiki 2006: "Captain Bluebear will transport any premium players by ship" - a free account stays."""
    p = new_player(pos=(BLUEBEAR[0], BLUEBEAR[1] + 1, BLUEBEAR[2]), level=50, premium_days=0,
                   group_id=TESTER_GROUP, storage={BEGINNER_SET_GIVEN: 1},
                   inventory={BACKPACK: Item(1988, contents=[Item(2152, 2)])})
    start = p.pos
    said = p.talk(*lines, npc="Captain Bluebear")
    p.sleep(1.5)
    assert p.pos == start, f"a free account sailed to {p.pos}"
    assert any("premium account" in s for s in said) or p.messages("premium account"), said


def test_the_captain_is_heard_before_the_ship_sails(new_player):
    """"Set the sails!" is spoken through the scheduler; the trip used to start first and the passenger never saw it."""
    p = new_player(pos=(BLUEBEAR[0], BLUEBEAR[1] + 1, BLUEBEAR[2]), level=50, premium_days=30,
                   group_id=TESTER_GROUP, storage={BEGINNER_SET_GIVEN: 1},
                   inventory={BACKPACK: Item(1988, contents=[Item(2152, 2)])})
    said = p.talk("hi", "edron", "yes", npc="Captain Bluebear")
    assert "Set the sails!" in said, said
    assert p.wait_for(lambda: p.pos == EDRON_HARBOUR, timeout=5), p.pos


# docs/reference-74/travel.md: every captain's 7.4 routes and prices, and none of the later destinations
ROUTES = {
    "Captain Bluebear": {"ab'dendriel": 130, "carlin": 110, "edron": 150, "venore": 170},
    "Captain Greyhound": {"ab'dendriel": 80, "edron": 110, "thais": 110, "venore": 130},
    "Captain Seagull": {"carlin": 80, "edron": 70, "thais": 130, "venore": 90},
    "Captain Fearless": {"ab'dendriel": 90, "ankrahmun": 150, "carlin": 130, "darashia": 60, "edron": 40, "thais": 170},
    "Captain Seahorse": {"ab'dendriel": 70, "ankrahmun": 160, "carlin": 110, "cormaya": 20, "thais": 160, "venore": 40},
    "Captain Sinbeard": {"darashia": 100, "edron": 160, "venore": 150},
    "Petros": {"ankrahmun": 100, "venore": 60},
}
LATER = ["port hope", "liberty bay", "svargrond", "yalahar"]


@pytest.mark.parametrize("captain", list(ROUTES))
def test_captains_sail_the_74_routes(new_player, captain):
    from tibia74.quest import next_to, talk_to
    p = next_to(new_player, load_npcs(SERVER_DIR)[captain].pos, level=50, premium_days=30, group_id=TESTER_GROUP,
                storage={BEGINNER_SET_GIVEN: 1})
    for town, price in ROUTES[captain].items():
        said = talk_to(p, captain, "hi", town, "no")
        assert any(f"for {price} gold coins" in s for s in said), (town, said)
    for town in LATER:
        said = talk_to(p, captain, "hi", town)
        assert not any("gold coins" in s for s in said), (town, said)

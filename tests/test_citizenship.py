"""The portals of citizenship (TibiaWiki 2005, Portal of Citizenship: "a portal that you enter to become citizen of a
city ... in Carlin the portal is right under the temple"): each town's portal (action id 1001-1008) makes you its
citizen - you respawn there - and brings you into its temple. movements/scripts/citizenship.lua."""
import pytest

from tibia74.quest import next_to, step_onto
from tibia74.server import TESTER_GROUP

PORTALS = {"Thais": ((32369, 32246, 6), 2, (32369, 32241, 7)),
           "Carlin": ((32360, 31784, 8), 3, (32360, 31782, 7)),
           "Kazordoon": ((32642, 31925, 12), 4, (32649, 31925, 11)),
           "Ab'Dendriel": ((32607, 31682, 7), 5, (32732, 31634, 7)),
           "Edron": ((33210, 31804, 8), 6, (33217, 31814, 8)),
           "Darashia": ((33216, 32455, 2), 7, (33213, 32454, 1)),
           "Venore": ((32951, 32035, 7), 8, (32957, 32076, 7)),
           "Ankrahmun": ((33195, 32849, 6), 9, (33194, 32853, 8))}


@pytest.mark.parametrize("town", list(PORTALS))
def test_portal_of_citizenship(new_player, db, town):
    portal, town_id, temple = PORTALS[town]
    p = next_to(new_player, portal, level=20, premium_days=30, town_id=1, group_id=TESTER_GROUP,
                storage={30001: 1})
    step_onto(p, portal)
    assert p.wait_for(lambda: p.pos == temple, timeout=3), p.pos
    assert p.wait_for(lambda: p.messages(f"You are now a citizen of {town}."), timeout=3), p.text_messages[-2:]
    p.logout()
    assert db.town_after_logout(p.character.guid, town_id) == town_id

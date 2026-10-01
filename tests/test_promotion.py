"""Promotion (TibiaWiki 2005, Vocation Promotion): "It can be purchased from King Tibianus III of Thais, Queen Eloise of
Carlin, Emperor Kruzak of Kazordoon or the Grand Vizier Ishebad of Ankrahmun. The requirements for a promotion are:
20,000 gold pieces, Level 20 or higher, A premium account." The NPC module called a function that did not exist
(getPlayerPromotionLevel): nobody could be promoted; the four charged 10,000."""
import time

import pytest

from tibia74 import BACKPACK, Item
from tibia74.quest import talk_to
from test_npc_talk import NPCS, near
from tibia74.server import TESTER_GROUP

PROMOTERS = {"King Tibianus": "hail king", "Queen Eloise": "hail queen eloise",
             "Emperor Kruzak": "hail emperor", "Ishebad": "hail ishebad"}
KNIGHT, ELITE_KNIGHT = 4, 8
CRYSTAL = 2160


def promotee(new_player, npc, level=20, vocation=KNIGHT, premium_days=30, gold=20000):
    contents = [Item(CRYSTAL, gold // 10000)] if gold >= 10000 else [Item(2148, gold)] if gold else []
    return near(new_player, NPCS[npc].positions[0], level=level, vocation=vocation, premium_days=premium_days,
                group_id=TESTER_GROUP, storage={30001: 1}, inventory={BACKPACK: Item(1988, contents=contents)})


def saved_vocation(db, p, expected, timeout=30):
    p.logout()
    deadline = time.time() + timeout
    while db.character(p.character.guid)["vocation"] != expected and time.time() < deadline:
        time.sleep(0.2)
    return db.character(p.character.guid)["vocation"]


@pytest.mark.parametrize("npc", list(PROMOTERS))
def test_promotion(new_player, db, npc):
    p = promotee(new_player, npc)
    replies = talk_to(p, npc, PROMOTERS[npc], "promotion", "yes")
    assert any("for 20000 gold coins" in r for r in replies), replies
    assert any("Congratulations! You are now promoted." in r for r in replies), replies
    assert saved_vocation(db, p, ELITE_KNIGHT) == ELITE_KNIGHT


@pytest.mark.parametrize("case, kwargs, answer", [
    ("level 19", dict(level=19), "once you have reached level 20"),
    ("free account", dict(premium_days=0), "You need a premium account"),
    ("19999 gold", dict(gold=19999), "You do not have enough money!"),
    ("already promoted", dict(vocation=ELITE_KNIGHT), "You are already promoted!"),
])
def test_promotion_rules(new_player, db, case, kwargs, answer):
    p = promotee(new_player, "King Tibianus", **kwargs)
    replies = talk_to(p, "King Tibianus", "hail king", "promotion", "yes")
    assert any(answer in r for r in replies), (case, replies)
    vocation = kwargs.get("vocation", KNIGHT)
    assert saved_vocation(db, p, vocation) == vocation

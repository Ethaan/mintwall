"""Vocations against 7.4 (tibiantis-notes "Classes" and "Skills", docs/reference-74/tibiantis-notes/): what a level
gives, regeneration per hour, skill and magic level multipliers. No server needed."""
import xml.etree.ElementTree as ET

import pytest

from tibia74 import SERVER_DIR

VOCATIONS = {int(v.get("id")): v for v in ET.parse(SERVER_DIR / "data" / "vocations.xml").getroot()}

# per level: hp, mana, cap; per hour: hp, mana regeneration (promoted where it differs)
CLASSES = {
    4: (15, 5, 25, 600, 300), 8: (15, 5, 25, 900, 300),        # knight, elite knight
    3: (10, 15, 20, 450, 450), 7: (10, 15, 20, 600, 600),      # paladin, royal paladin
    1: (5, 30, 10, 300, 600), 5: (5, 30, 10, 300, 900),        # sorcerer, master sorcerer
    2: (5, 30, 10, 300, 600), 6: (5, 30, 10, 300, 900),        # druid, elder druid
}
# skill id -> multiplier: 0 fist, 1 club, 2 sword, 3 axe, 4 distance, 5 shielding; and magic level
SKILLS = {
    4: ({0: 1.1, 1: 1.1, 2: 1.1, 3: 1.1, 4: 1.4, 5: 1.1}, 3.0),
    3: ({0: 1.2, 1: 1.2, 2: 1.2, 3: 1.2, 4: 1.1, 5: 1.1}, 1.4),
    1: ({0: 1.5, 1: 2.0, 2: 2.0, 3: 2.0, 4: 2.0, 5: 1.5}, 1.1),
    2: ({0: 1.5, 1: 1.8, 2: 1.8, 3: 1.8, 4: 1.8, 5: 1.5}, 1.1),
}


@pytest.mark.parametrize("vid", sorted(CLASSES))
def test_level_gains_and_regeneration(vid):
    v = VOCATIONS[vid]
    hp, mana, cap, hp_hour, mana_hour = CLASSES[vid]
    assert (int(v.get("gainhp")), int(v.get("gainmana")), int(v.get("gaincap"))) == (hp, mana, cap)
    per_hour = lambda ticks, amount: 3600 // int(ticks) * int(amount)          # noqa: E731
    assert per_hour(v.get("gainhpticks"), v.get("gainhpamount")) == hp_hour
    assert per_hour(v.get("gainmanaticks"), v.get("gainmanaamount")) == mana_hour


@pytest.mark.parametrize("vid", sorted(SKILLS))
def test_skill_and_magic_multipliers(vid):
    skills, magic = SKILLS[vid]
    for v in (VOCATIONS[vid], VOCATIONS[vid + 4]):
        got = {int(s.get("id")): float(s.get("multiplier")) for s in v.findall("skill") if int(s.get("id")) <= 5}
        assert got == skills
        assert float(v.get("manamultiplier")) == magic


def test_every_vocation_carries_470_at_level_8():
    """Base capacity (tibiantis-notes): knight 25 x level + 270, paladin 20 x level + 310, mage 10 x level + 390 -
    470 at level 8 for all, so Rookgaard (no vocation) gives 10 a level from 400 at level 1."""
    assert 400 + 7 * int(VOCATIONS[0].get("gaincap")) == 470


def _item(item_id):
    for it in ET.parse(SERVER_DIR / "data" / "items" / "items.xml").getroot():
        if it.get("id") == str(item_id):
            return {a.get("key"): a.get("value") for a in it.findall("attribute")}
    raise KeyError(item_id)


@pytest.mark.parametrize("item_id, seconds, every_ms, total", [(2205, 1200, 3000, 400), (2216, 450, 1000, 450)],
                         ids=["life ring", "ring of healing"])
def test_regeneration_ring(item_id, seconds, every_ms, total):
    """tibiantis-notes: a life ring gives 1 hp and mana every 3 s for 20 min (400), a ring of healing every second
    for 7.5 min (450). Ours gave 4 mana a tick (1600 / 1920)."""
    a = _item(item_id)
    assert int(a["duration"]) == seconds
    for stat in ("health", "mana"):
        assert int(a[stat + "Ticks"]) == every_ms
        assert int(a[stat + "Gain"]) * seconds * 1000 // every_ms == total


def test_rookie_magic_multiplier_is_3():
    """No vocation: 3.0 (TibiaWiki formulae page, the only source; ours was 4.0 - decided with the user 2026-10-03)."""
    assert float(VOCATIONS[0].get("manamultiplier")) == 3.0

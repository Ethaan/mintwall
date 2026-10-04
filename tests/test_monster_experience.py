"""Monster experience as in 7.4 (task.md "Monster experience"), checked 2026-10-03.

Data (no server needed): every monster's experience in server/data/monster/*.xml is Tibiantis' (a 7.4 server,
docs/reference-74/tibiantis/creatures.json); the monsters Tibiantis lacks are TibiaWiki's from the 7.4 era (first
revisions, May-June 2005, before 7.5 on 2005-08-09) or are kept as they are, listed below with why.

The 7.4 rule, in game (creature.cpp Creature::getGainedExperience):
  - each player that hit the monster gets its experience times his share of all the damage it took, rounded down -
    there was no shared party experience before 8.10 (Christmas 2007; TibiaWiki "Party" pre-8.0 revisions only know
    green skulls and shared loot), and a player killing alone gets exactly the monster's experience;
  - damage without an attacker (traps, ownerless fields) is not counted (tibiantis-notes trap.txt: "To gain full
    experience from the monster killed with traps you will need to deal 1 or more damage from another source");
  - a summon's share goes half to its master (TibiaWiki "Summon Creature" 2005-11: "if your summon causes all of
    the damage to kill a Rotworm, you will receive only 20 exp (half)").
"""
import json
import time
import xml.etree.ElementTree as ET

import pytest

from tibia74 import BACKPACK, RIGHT, SERVER_DIR, Item

ROOT = SERVER_DIR.parent
TIBIANTIS = {c["name"].lower(): c for c in
             json.loads((ROOT / "docs" / "reference-74" / "tibiantis" / "creatures.json").read_text(encoding="utf-8"))
             ["CREATURES"] if not c.get("custom")}
ALIAS = {"bone beast": "bonebeast"}

# Not in Tibiantis: TibiaWiki's experience in its first revision of the page (all from 7.4 time, before 2005-08-09).
WIKI_74 = {
    "ashmunrah": (3100, 13395, "2005-06-16"),     # ours had 5000 - its hit points swapped in; 3100 on every revision
    "mahrdis": (3050, 7900, "2005-05-21"),        # ours had 2800, 3050 on every revision
    "dipthrah": (2900, 7897, "2005-05-21"),
    "morguthis": (3000, 7899, "2005-05-21"),
    "omruc": (2950, 7898, "2005-05-21"),
    "rahemos": (3100, 13368, "2005-06-16"),
    "thalas": (2950, 10295, "2005-06-16"),
    "vashresamun": (2950, 7901, "2005-05-21"),
}
# No 7.4 source: kept as they are. Not in 7.4 (TibiaWiki pages begin with 7.5, 2005-08-09 or later), traps, or
# our own. Their experience is pinned so a change is a decision.
KEPT = {
    "assassin": 105, "bandit": 65, "dark monk": 145, "smuggler": 48,             # 7.5 (pages from 2005-08-09/10)
    "demodras": 3100, "dharalion": 1200, "general murius": 1300, "grorlam": 290,  # 7.5+ bosses; wiki numbers
    "necropharus": 1100, "orshabaal": 9999, "the evil eye": 1500,                 # differ but are not 7.4 either
    "the horned fox": 200, "the old widow": 1900,
    "chicken": 0,                                                                 # wiki 2005-09: 0
    "demongoblin": 25,                                                            # wiki "Demon (Goblin)" 2007: 25
    "flamethrower": 1200, "magicthrower": 1200, "plaguethrower": 1300,            # traps, attackable="0": nobody
    "shredderthrower": 18,                                                        # can ever kill them
    "poisonthrower": 1200,                                                        # not spawned
    "deathslicer": 0,         # a trap (decided with the user 2026-10-04): not attackable, immune, 0 exp
}


def _monsters():
    out = {}
    for f in sorted((SERVER_DIR / "data" / "monster").glob("*.xml")):
        root = ET.parse(f).getroot()
        if root.tag == "monster":
            out[root.get("name").lower()] = root
    return out


MONSTERS = _monsters()


def experience(name: str) -> int:
    return int(MONSTERS[name.lower()].get("experience"))


@pytest.mark.parametrize("name", sorted(MONSTERS))
def test_monster_experience_is_the_74_one(name):
    exp = experience(name)
    ref = TIBIANTIS.get(ALIAS.get(name, name))
    if ref is not None:
        assert exp == ref["exp"], f"{name}: {exp}, Tibiantis {ref['exp']}"
    elif name in WIKI_74:
        want, rev, date = WIKI_74[name]
        assert exp == want, f"{name}: {exp}, TibiaWiki {want} (oldid {rev}, {date})"
    else:
        assert name in KEPT, f"{name}: no 7.4 experience known - find one or add it to KEPT"
        assert exp == KEPT[name], f"{name}: {exp}, kept at {KEPT[name]} - a change should be decided"


def test_every_tibiantis_monster_is_one_of_ours():
    ours = {ALIAS.get(n, n) for n in MONSTERS}
    assert not set(TIBIANTIS) - ours, sorted(set(TIBIANTIS) - ours)


# ----------------------------------------------------------------------------- in game

FIELD = (32330, 32218, 7)         # Thais, the open square east of test_combat_formulas' field; no spawn near
KNIGHT, SORCERER = 4, 1
MAGIC_SWORD, HMM, BAG = 2400, 2311, 1988
ENERGY, EXP_TEXT = 35, 215        # const.h TEXTCOLOR_LIGHTBLUE (energy damage), TEXTCOLOR_WHITE_EXP
CREATURE = 0x63


def _gm_summons(new_player, at, monster, watcher):
    gm = new_player(pos=at, group_id=3)
    gm.say(f"/m {monster}")
    m = watcher.wait_for(lambda: watcher.nearest(monster), timeout=5) and watcher.nearest(monster)
    assert m, f"no {monster} appeared"
    return m


def _gains(p, since):
    """The white experience numbers shown over the player since index `since` (others' show up too)."""
    return [int(t) for pos, c, t in p.animated_texts[since:]
            if c == EXP_TEXT and t.strip().isdigit() and tuple(pos) == tuple(p.pos)]


@pytest.mark.parametrize("monster", ["Rat", "Rotworm", "Minotaur", "Cyclops"])
def test_killing_a_monster_alone_gives_its_experience(new_player, monster):
    """A level 60 knight with a magic sword kills it alone: his experience grows by exactly the monster's."""
    spot = (FIELD[0], FIELD[1], FIELD[2])
    p = new_player(pos=spot, level=60, vocation=KNIGHT, storage={30001: 1}, skills={2: 70},
                   inventory={RIGHT: Item(MAGIC_SWORD)})
    assert p.pos == spot, p.pos
    before = p.wait_for(lambda: p.stats.experience, timeout=5) and p.stats.experience
    texts = len(p.animated_texts)
    m = _gm_summons(new_player, (spot[0], spot[1] - 3, spot[2]), monster, p)
    p.set_fight_modes(fight=1, chase=1)
    p.attack(m.id)
    want = experience(monster)
    assert p.wait_for(lambda: m.id in p.removed_creatures, timeout=60), f"{monster} not killed: {m}"
    assert p.wait_for(lambda: p.stats.experience - before >= want, timeout=3) or want == 0, p.stats.experience
    p.sleep(0.5)
    assert p.stats.experience - before == want
    assert _gains(p, texts) == [want]


def test_two_players_share_the_experience_by_damage(new_player, items):
    """A level 100 sorcerer (645 hp: the cyclops hits him all along, a dead player gains nothing) hits a cyclops
    (260 hp, 150 exp) with two heavy magic missiles, then a knight kills it with his magic sword. Each gets
    150 x his damage / 260, rounded down: the sorcerer's damage is the energy numbers shown over the cyclops, the
    knight's the rest of its 260 hit points."""
    mage_at = (FIELD[0] - 8, FIELD[1] - 2, FIELD[2])
    knight_at = (FIELD[0] - 8, FIELD[1], FIELD[2])
    mage = new_player(pos=mage_at, level=100, vocation=SORCERER, maglevel=3, mana=2000, storage={30001: 1},
                      inventory={BACKPACK: Item(BAG, contents=[Item(HMM, 5)])})
    knight = new_player(pos=knight_at, level=60, vocation=KNIGHT, storage={30001: 1}, skills={2: 70},
                        inventory={RIGHT: Item(MAGIC_SWORD)})
    assert mage.pos == mage_at and knight.pos == knight_at, (mage.pos, knight.pos)
    m_before = mage.wait_for(lambda: mage.stats.experience, timeout=5) and mage.stats.experience
    k_before = knight.wait_for(lambda: knight.stats.experience, timeout=5) and knight.stats.experience
    m_texts, k_texts = len(mage.animated_texts), len(knight.animated_texts)
    cyclops = _gm_summons(new_player, (mage_at[0] + 4, mage_at[1] + 1, mage_at[2]), "Cyclops", mage)
    hp, exp = int(MONSTERS["cyclops"].find("health").get("max")), experience("Cyclops")
    assert (hp, exp) == (260, 150)

    mage.set_fight_modes(fight=1, chase=0, safe=1)
    mage.open_container(BACKPACK)
    cid = min(mage.containers)
    for _ in range(2):                         # power 209 (level 100, ML 3): 42-84 a missile, at most 168
        c = mage.creatures[cyclops.id]
        assert c.pos and c.health > 0, c
        mage.use_item_with(mage.container_pos(cid, 0), items.by_server[HMM].client_id, 0, c.pos, CREATURE, 1)
        time.sleep(2.1)                                                              # rune exhaustion
    time.sleep(0.5)
    mage_damage = sum(int(t) for pos, c, t in mage.animated_texts[m_texts:]
                      if c == ENERGY and t.strip().isdigit() and tuple(pos) not in (mage.pos, knight.pos))
    assert 0 < mage_damage < hp, mage_damage
    assert mage.stats.health > 0

    knight.set_fight_modes(fight=1, chase=1)
    knight.attack(cyclops.id)
    assert knight.wait_for(lambda: cyclops.id in knight.removed_creatures, timeout=90), cyclops
    mage_exp, knight_exp = mage_damage * exp // hp, (hp - mage_damage) * exp // hp
    knight.wait_for(lambda: knight.stats.experience - k_before >= knight_exp, timeout=3)
    mage.wait_for(lambda: mage.stats.experience - m_before >= mage_exp, timeout=3)
    time.sleep(0.5)
    assert mage.stats.health > 0 and knight.stats.health > 0, "a dead player gains nothing"
    got = (mage.stats.experience - m_before, knight.stats.experience - k_before)
    assert got == (mage_exp, knight_exp), (
        f"mage dealt {mage_damage} of {hp}: got {got}, 7.4 {(mage_exp, knight_exp)}; texts seen by the mage "
        f"{[(p, c, t) for p, c, t in mage.animated_texts[m_texts:] if t.strip().isdigit()]}")
    assert _gains(mage, m_texts) == [mage_exp] and _gains(knight, k_texts) == [knight_exp]

"""7.4 formulas, pinned: see docs/reference-74/formulas.md for the sources of every number."""
import pytest

from tibia74 import BACKPACK, Item
from tibia74.server import TESTER_GROUP

CREATURE = 0x63
MANA_FLUID, LIFE_FLUID = 7, 10


@pytest.mark.parametrize("fluid, stat", [(MANA_FLUID, "mana"), (LIFE_FLUID, "health")])
def test_fluids_give_25_to_75(new_player, fluid, stat):
    p = new_player(level=50, vocation=1, mana=0, health=100, group_id=TESTER_GROUP,
                   pos=(32369, 32241, 7), inventory={BACKPACK: Item(1988, contents=[Item(2006, fluid)] * 6)})
    bag = p.open_container(BACKPACK)
    cid = next(k for k, v in p.containers.items() if v is bag)
    gains = []
    for _ in range(6):
        before = getattr(p.stats, stat)
        slot = next(n for n, i in enumerate(bag.items) if i.count == fluid)
        p.use_item_with(p.container_pos(cid, slot), bag.items[slot].client_id, slot, p.pos, CREATURE, 1)
        assert p.wait_for(lambda: getattr(p.stats, stat) != before, timeout=3), f"no {stat} from the fluid"
        gains.append(getattr(p.stats, stat) - before)
        p.sleep(1.1)
    assert all(25 <= g <= 75 for g in gains), gains


IH_RUNE = 2265


def test_runes_use_a_magic_power_of_at_least_100(new_player):
    """P = level*2 + mlvl*3, at least 100: a level 8 IH rune heals 40-100 (it healed 7-14 at P=19)."""
    p = new_player(level=8, vocation=1, maglevel=1, health=40, group_id=TESTER_GROUP, pos=(32369, 32241, 7),
                   inventory={BACKPACK: Item(1988, contents=[Item(IH_RUNE, 1)])})
    bag = p.open_container(BACKPACK)
    cid = next(k for k, v in p.containers.items() if v is bag)
    before = p.stats.health
    p.use_item_with(p.container_pos(cid, 0), bag.items[0].client_id, 0, p.pos, CREATURE, 1)
    assert p.wait_for(lambda: p.stats.health != before, timeout=3), f"no heal: {p.text_messages[-2:]}"
    assert 40 <= p.stats.health - before <= 100, f"healed {p.stats.health - before}"


def test_regeneration_per_vocation_is_7_4():
    """1 hp / 1 mana every N seconds (docs/reference-74/formulas.md §7)."""
    import re
    from tibia74 import SERVER_DIR
    xml = (SERVER_DIR / "data" / "vocations.xml").read_text(encoding="latin-1")
    ticks = {m.group(2): (int(m.group(3)), int(m.group(4))) for m in re.finditer(
        r'<vocation id="(\d)" name="([^"]+)"[^>]*gainhpticks="(\d+)"[^>]*gainmanaticks="(\d+)"', xml)}
    assert {k: v for k, v in ticks.items() if k != "Gamemaster"} == {
        "None": (12, 12), "Sorcerer": (12, 6), "Druid": (12, 6), "Paladin": (8, 8), "Knight": (6, 12),
        "Master Sorcerer": (12, 4), "Elder Druid": (12, 4), "Royal Paladin": (6, 6), "Elite Knight": (4, 12)}


def test_monster_melee_follows_the_7_4_formula(new_player):
    """A dwarf guard (7.4: attack 39, skill 55) hits at most (5*55+50)*39*0.99/100 = 125 - it was 200.
    The target wears nothing and holds no shield, so every hit shows its full rolled damage."""
    import time
    spot = (32060, 32200, 7)   # an open field, not the road the walking tests use (the guard stays)
    victim = new_player(pos=spot, level=100, storage={30001: 1})
    gm = new_player(pos=(spot[0], spot[1] - 3, spot[2]), group_id=3)
    gm.say("/m Dwarf Guard")
    guard = victim.wait_for(lambda: victim.nearest("Dwarf Guard"), timeout=5)
    assert guard, "no dwarf guard"
    hits, deadline = [], time.time() + 40
    while time.time() < deadline and len(hits) < 15:
        n = len(victim.animated_texts)
        victim.sleep(0.2)
        hits += [int(t) for pos, _, t in victim.animated_texts[n:] if pos == victim.pos and t.isdigit()]
    assert len(hits) >= 5, f"too few hits to judge: {hits}"
    assert max(hits) <= 125, f"hits {sorted(hits)} - above the 7.4 max of 125"


def test_bolts_hit_by_skill_and_distance_not_a_fixed_chance(new_player):
    """7.4: hit chance = 91% x min(skill / (15d - 1), 1) - distance skill 20 at 5 tiles hits ~25%.
    Bolts and arrows had a fixed hitChance in items.xml (80 / 90) that ignored skill and distance."""
    import time
    from tibia74 import AMMO, RIGHT
    spot = (32031, 32138, 7)          # open grass, 12+ tiles from any spawn
    shooter = new_player(pos=spot, level=100, vocation=3, skills={4: 20},
                         inventory={RIGHT: Item(2455), AMMO: Item(2543, 100)})          # crossbow, bolts
    target = new_player(pos=(spot[0] + 5, spot[1], spot[2]), level=100, storage={30001: 1})
    assert shooter.pos == spot and target.pos == (spot[0] + 5, spot[1], spot[2]), (shooter.pos, target.pos)
    shooter.set_fight_modes(fight=1, chase=0, safe=0)
    start = len(target.animated_texts)
    shooter.attack(target.player_id)
    deadline = time.time() + 60
    while time.time() < deadline and 100 - shooter.inventory[AMMO].count < 20:
        shooter.sleep(0.5)
    shooter.attack(0)
    shots = 100 - shooter.inventory[AMMO].count
    hits = sum(1 for pos, _, t in target.animated_texts[start:] if pos == target.pos and t.isdigit())
    assert shots >= 15, f"only {shots} shots"
    assert hits / shots < 0.55, f"{hits} of {shots} bolts hit - skill 20 at 5 tiles should hit ~25%, not a fixed 80%"

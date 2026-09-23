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

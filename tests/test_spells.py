"""Spells that do more than damage or heal."""
import re

import pytest

from tibia74 import SERVER_DIR
from tibia74.server import TESTER_GROUP

ROPE_SPOT = (32077, 32151, 8)        # Rookgaard, ground 384; the way up comes out at (x, y+1, z-1)


def test_magic_rope_pulls_you_up_a_rope_spot(new_player):
    p = new_player(pos=ROPE_SPOT, level=20, vocation=1, mana=100, maglevel=5)
    assert p.pos == ROPE_SPOT, p.pos
    p.say("exani tera")
    assert p.wait_for(lambda: p.pos == (ROPE_SPOT[0], ROPE_SPOT[1] + 1, ROPE_SPOT[2] - 1), timeout=3), p.pos


def test_magic_rope_does_nothing_off_a_rope_spot(new_player):
    start = (ROPE_SPOT[0], ROPE_SPOT[1] + 1, ROPE_SPOT[2] - 1)
    p = new_player(pos=start, level=20, vocation=1, mana=100, maglevel=5)
    start = p.pos                    # the rope test above may still be standing there
    p.say("exani tera")
    assert p.wait_for(lambda: p.messages("not possible"), timeout=3), p.text_messages[-3:]
    assert p.pos == start


def test_no_script_compares_a_function_result_with_TRUE_or_FALSE():
    """Engine functions (isPlayer, isCreature, hasCondition...) and isInArray return true/false, and TRUE is 1:
    `isPlayer(cid) == TRUE` is never true. That broke exani tera, destroy field, animate dead, traps, house
    checks and the healers' fire/poison cure."""
    bad = []
    for script in (SERVER_DIR / "data").rglob("*.lua"):
        for n, line in enumerate(script.read_text(encoding="latin-1").splitlines(), 1):
            if re.search(r"(\)|\bret)\s*[=~]=\s*(TRUE|FALSE)\b", line):
                bad.append(f"{script.relative_to(SERVER_DIR)}:{n}: {line.strip()}")
    assert not bad, "\n".join(bad)


def test_spell_scripts_return_a_boolean():
    """onCastSpell returning LUA_NO_ERROR (undefined here, so nil) logged "Expected boolean type parameter"."""
    bad = [str(f.relative_to(SERVER_DIR)) for f in (SERVER_DIR / "data" / "spells").rglob("*.lua")
           if re.search(r"return LUA_(NO_)?ERROR", f.read_text(encoding="latin-1"))]
    assert not bad, bad


SD_RUNE = 2268
FIELD = (32094, 32165, 7)            # open ground x..x+9, y..y+6 north of Rookgaard town, no protection zone,
                                     # 12+ tiles from any spawn (the first field was a deer spawn)


INFINITE = bytes([4]) + (64000).to_bytes(2, "little")     # action id 64000: a test character's never-ending rune


def _sd_caster(new_player, row, marked=False):
    """Each test its own row: a caster stays online (in fight) after the test, on the tile it stood on."""
    from tibia74 import BACKPACK, Item
    pos = (FIELD[0], FIELD[1] + row, FIELD[2])
    p = new_player(pos=pos, level=100, vocation=5, maglevel=70, mana=1000,
                   inventory={BACKPACK: Item(1988, contents=[Item(SD_RUNE, 5, attributes=INFINITE if marked else b"")])})
    assert p.pos == pos, f"caster placed at {p.pos}, not {pos}"
    p.set_fight_modes(fight=1, chase=0, safe=0)    # secure mode off, or runes on unmarked players are refused
    return p


def _throw_sd(p, items, target):
    bag = p.open_container(3)
    cid = next(k for k, v in p.containers.items() if v is bag)
    p.use_item_with(p.container_pos(cid, 0), items.by_server[SD_RUNE].client_id, 0, target.pos, 0x63, 1)


@pytest.mark.parametrize("marked, row", [(False, 0), (True, 2)], ids=["normal", "infinite"])
def test_sudden_death_reaches_7_tiles_the_edge_of_the_screen(new_player, items, marked, row):
    """The 7.4 screen shows 7 tiles each side (15 x 11): a rune reaches what you can see. The infinite
    runes (action id 64000) got infinite_fluid.lua's adjacent-only range: "Too far away." past 1 tile."""
    p = _sd_caster(new_player, row, marked)
    target = new_player(pos=(p.pos[0] + 7, p.pos[1], p.pos[2]), level=100, storage={30001: 1})
    assert target.pos == (p.pos[0] + 7, p.pos[1], p.pos[2]), target.pos
    before = target.wait_for(lambda: target.stats.health, timeout=3)
    _throw_sd(p, items, target)
    assert target.wait_for(lambda: target.stats.health < before, timeout=3), p.text_messages[-2:]


@pytest.mark.parametrize("marked, row", [(False, 4), (True, 6)], ids=["normal", "infinite"])
def test_sudden_death_does_not_reach_off_screen(new_player, items, marked, row):
    p = _sd_caster(new_player, row, marked)
    target = new_player(pos=(p.pos[0] + 8, p.pos[1], p.pos[2]), level=100, storage={30001: 1})
    assert target.pos[0] - p.pos[0] >= 8, f"target placed at {target.pos}"    # a busy tile moves it further out
    before = target.wait_for(lambda: target.stats.health, timeout=3)
    _throw_sd(p, items, target)
    hit = target.wait_for(lambda: target.stats.health < before, timeout=3)
    assert not hit, f"an SD hit 8 tiles away ({before} -> {target.stats.health} hp)"
    assert p.messages("too far"), p.text_messages[-3:]


def _spells_xml():
    return (SERVER_DIR / "data" / "spells" / "spells.xml").read_text(encoding="latin-1")


def test_every_rune_conjure_makes_the_rune_its_spell_uses():
    """adori vita vis made 2263 and adura vita 2274: items with the right name but no rune spell behind them."""
    xml = _spells_xml()
    runes = {re.search(r'name="([^"]+)"', t).group(1).lower(): int(re.search(r'\bid="(\d+)"', t).group(1))
             for t in re.findall(r"<rune\b[^>]*>", xml)}
    bad = []
    for tag in re.findall(r"<conjure\b[^>]*>", xml):
        if 'function="conjureRune"' not in tag:
            continue
        words = re.search(r'words="([^"]+)"', tag).group(1).lower()
        made = int(re.search(r'conjureId="(\d+)"', tag).group(1))
        if runes.get(words) != made:
            bad.append(f"{words}: makes {made}, the rune spell is {runes.get(words)}")
    assert not bad, bad


BLANK_RUNE = 2260


@pytest.mark.parametrize("vocation, words, rune", [(1, "adori vita vis", SD_RUNE), (2, "adura vita", 2273)],
                         ids=["sudden death", "ultimate healing"])
def test_conjuring_makes_a_usable_rune(new_player, items, vocation, words, rune):
    from tibia74 import Item, RIGHT
    p = new_player(pos=(32369, 32241, 7), level=60, vocation=vocation, maglevel=30, mana=500,
                   group_id=TESTER_GROUP, inventory={RIGHT: Item(BLANK_RUNE)})
    p.say(words)
    made = lambda: items.by_client[p.inventory[RIGHT].client_id].server_id if p.inventory.get(RIGHT) else None
    assert p.wait_for(lambda: made() == rune, timeout=3), \
        f"right hand holds {made()} ({items.name(made()) if made() else '-'}), expected {rune}; {p.text_messages[-2:]}"

"""Spells that do more than damage or heal."""
import re

import pytest

from tibia74 import SERVER_DIR

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
FIELD = (32034, 32150, 7)            # open walkable ground x..x+9, y..y+6 (Rookgaard, north-west), no protection zone


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
    assert target.pos == (p.pos[0] + 8, p.pos[1], p.pos[2]), target.pos
    before = target.wait_for(lambda: target.stats.health, timeout=3)
    _throw_sd(p, items, target)
    hit = target.wait_for(lambda: target.stats.health < before, timeout=3)
    assert not hit, f"an SD hit 8 tiles away ({before} -> {target.stats.health} hp)"
    assert p.messages("too far"), p.text_messages[-3:]

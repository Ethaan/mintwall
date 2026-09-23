"""Spells that do more than damage or heal."""
import re

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

"""Every NPC on the map answers its greeting and a question, without a Lua error (task.md: "Talk-test every NPC once;
log the ones that error or don't answer"). A character next to each spawned NPC says the greeting, "job" and "bye";
the no_lua_errors fixture fails the NPC whose script errs."""
import pytest

from tibia74 import SERVER_DIR
from tibia74.npcs import load_npcs
from tibia74.quest import talk_to
from tibia74.server import TESTER_GROUP

NPCS = load_npcs(SERVER_DIR)
SPAWNED = sorted(name for name, npc in NPCS.items() if npc.positions)

# greeted with something else than "hi" (the word, and storages the NPC wants first)
DJINN = {"djanni'hah": ["Alesar", "Baa'leal", "Bo'ques", "Fa'hradin", "Gabel", "Haroun", "Malor", "Nah'bob", "Ubaid",
                        "Umar", "Yaman"]}
GREETING = {name: ("djanni'hah", {70102: 1}) for name in DJINN["djanni'hah"]}
GREETING.update({
    "Rata'mari": ("piedpiper", {70101: 4}),
    "Maryza": ("hi maryza", {}),
    "King Tibianus": ("hail king", {}),
    "Queen Eloise": ("hail queen eloise", {}),
    "Emperor Kruzak": ("hail emperor", {}),
    "Ishebad": ("hail ishebad", {}),
    "Blind Orc": ("charach", {}),          # he speaks orcish ("Ikem Charach maruk.")
})


def near(new_player, pos, **kwargs):
    """A character on a free tile as close to pos as can be, up to 3 tiles (NPCs hear within 4: across a counter)."""
    for r in (1, 2, 3):
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if max(abs(dx), abs(dy)) != r:
                    continue
                p = new_player(pos=(pos[0] + dx, pos[1] + dy, pos[2]), **kwargs)
                if p.pos[2] == pos[2] and max(abs(p.pos[0] - pos[0]), abs(p.pos[1] - pos[1])) <= 3:
                    return p
                p.logout()
    raise AssertionError(f"no free tile within 3 of {pos}")


# 7.4 NPCs that never talk: TibiaWiki 2006, "This npc is an un-reachable illusion. When you aproach it, it will
# disappear" (the Ghostlands apparitions); Arkhothep's page is a creature's
SILENT = {"A Ghostly Woman", "A Lost Soul", "A Tainted Soul", "A Tortured Soul", "Arkhothep"}


@pytest.mark.parametrize("name", SPAWNED)
def test_npc_answers(new_player, name):
    word, storage = GREETING.get(name, ("hi", {}))
    p = near(new_player, NPCS[name].positions[0], level=100, premium_days=30, group_id=TESTER_GROUP,
                storage={30001: 1, **storage})
    # follow the NPC (they wander, some ten tiles from their spawn) and talk
    replies = talk_to(p, name, word, "job", "bye", find=60)
    if name in SILENT:
        assert not replies, f"{name} is silent in 7.4: {replies}"
    else:
        assert replies, f"{name} does not answer {word!r}"

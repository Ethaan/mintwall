"""Walking pace: the server lets the next step start exactly when the previous one is over.

A held key sends the next step as soon as the last one is confirmed, so the time until the next
confirmation is how long the server made us wait: the previous step's duration,
1000 * ground speed / player speed, twice that after a diagonal step. Too long a wait is the
character stopping for a moment; that is what these tests catch."""
import time

from tibia74 import NORTH, SOUTH, NORTHEAST, NORTHWEST, SOUTHEAST, SOUTHWEST
from tibia74.server import TESTER_GROUP

DIAGONAL = {NORTHEAST, NORTHWEST, SOUTHEAST, SOUTHWEST}
TOLERANCE_MS = 150                # delivery jitter of one packet is up to ~100 ms; the bugs this
                                  # catches cost a whole extra step (+400 ms)
ROAD = (32107, 32217, 7)          # dirt road east of the Rookgaard temple, 2 tiles wide, all ground 103
STAIRS_FOOT = (32110, 32209, 7)   # stairs at 32110,32207 lead up to 32110,32206,6


def _base_ms(p, items):
    """A straight step from where we stand: the server times it by the ground we are on."""
    ground = p.tile_items(p.pos)[0]
    return 1000 * items.client(ground.client_id).speed / p.creatures[p.player_id].speed


def _check_pace(p, items, first, directions):
    """Walk first, then directions as a held key would; list the steps that waited longer or shorter
    than the previous step takes."""
    assert p.step(first), f"first step {first} from {p.pos} was refused"
    wrong, previous = [], first
    for d in directions:
        expected = _base_ms(p, items) * (2 if previous in DIAGONAL else 1)
        where, start = p.pos, time.perf_counter()
        assert p.step(d), f"step {d} from {p.pos} was refused"
        waited = (time.perf_counter() - start) * 1000
        if abs(waited - expected) > TOLERANCE_MS:
            wrong.append(f"{previous}->{d} at {where}: waited {waited:.0f} ms, previous step takes {expected:.0f} ms")
        previous = d
    return wrong


def test_steps_wait_only_for_the_previous_step(new_player, items):
    p = new_player(pos=ROAD, level=20, group_id=TESTER_GROUP)
    wrong = _check_pace(p, items, SOUTH, [SOUTH, SOUTHEAST, SOUTHWEST, SOUTHEAST, SOUTH, SOUTH])
    assert not wrong, "\n".join(wrong)


def test_stairs_cost_a_normal_step(new_player, items):
    """Up and down the stairs holding the key: no extra wait after a floor change."""
    p = new_player(pos=STAIRS_FOOT, level=20, group_id=TESTER_GROUP)
    wrong = _check_pace(p, items, NORTH, [NORTH, SOUTH, NORTH, SOUTH, SOUTH])
    assert p.pos[2] == 7, f"ended on the wrong floor: {p.pos}"
    assert not wrong, "\n".join(wrong)

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


def test_fluid_used_while_walking_works_without_stopping(new_player, items):
    """7.4 lets you use runes and fluids on the move. It used to wait for the step to end, and the
    next step cancelled it, so nothing happened until the player stopped."""
    from tibia74 import BACKPACK, Item
    p = new_player(pos=ROAD, level=20, vocation=4, mana=0, group_id=TESTER_GROUP,
                   inventory={BACKPACK: Item(1988, contents=[Item(2006, 7)])})   # mana fluid
    bag = p.open_container(BACKPACK)
    cid = next(k for k, v in p.containers.items() if v is bag)
    assert p.step(SOUTH)
    p.use_item_with(p.container_pos(cid, 0), bag.items[0].client_id, 0, p.pos, 0x63, 1)   # drink, keep walking
    drank_at = None
    for n in range(1, 6):
        assert p.step(SOUTH), f"step {n} refused"
        if drank_at is None and any(t == "Aaaah..." for _, _, t in p.speech):
            drank_at = n
    assert drank_at is not None, f"never drank while walking; mana {p.stats.mana}, {p.text_messages[-2:]}"
    assert drank_at <= 2, f"drank only after {drank_at} more steps"


DH_TELEPORT_WEST = (33285, 31589, 12)  # west of the teleport 33286,31589,12 on the Demon Helmet route
DH_LANDING = (33277, 31592, 11)        # where it lands, just west of the portal 33278,31592,11
DH_ROOM = (33279, 31592, 12)           # where that portal sends you (back to the room)


def test_step_sent_with_the_one_onto_a_teleport_does_not_run_after_landing(new_player):
    """Two east steps back to back, the first onto a teleport: the second one used to run after the
    teleport, from the landing spot, and walked straight into the portal next to it (Demon Helmet route,
    found in game). A teleport ends the walk: the step waiting for its turn is dropped."""
    from tibia74 import EAST
    from tibia74.client import _WALK_OPCODE
    from tibia74.net import Writer
    p = new_player(pos=DH_TELEPORT_WEST, level=30, premium_days=30)   # premium area
    assert p.pos == DH_TELEPORT_WEST, f"logged in at {p.pos}"
    p._send(Writer().u8(_WALK_OPCODE[EAST]))
    p._send(Writer().u8(_WALK_OPCODE[EAST]))
    assert p.wait_for(lambda: p.pos != DH_TELEPORT_WEST, 3), "the first step was refused"
    time.sleep(1.5)                                   # time for a second step to run, if it would
    assert p.pos == DH_LANDING, f"ended on {p.pos}, expected to stay where the teleport lands {DH_LANDING}"

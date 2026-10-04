"""The ways between floors and places a player uses all over the map: ladders, sewer grates, stairs and ramps, holes
and trapdoors, rope spots, stone piles a shovel opens, and teleports (magic forcefields with a destination).

Each one the way a player uses it - standing beside it, a step onto it or a "use" - with a few real examples from
different towns (picked from Tibia74.otbm with tibia74/worldmap.py). The rules, as the server has them:
- ladder (1386, actions/scripts/teleport.lua): use it -> (x, y+1, z-1)
- sewer grate (430, the same script): use it -> (x, y, z+1)
- stairs / ramps (items.xml floorchange north/south/east/west): step on -> one floor up, past the ramp's top
- stairs down, holes, trapdoors (floorchange down): step on -> one floor down (moved off a ramp you land on)
- rope spot (ground 384 / 418, actions/scripts/rope.lua): use a rope on it -> (x, y+1, z-1)
- stone pile (468 / 481, actions/scripts/shovel.lua): a shovel opens a hole (469 / 482) that closes again by
  itself (items.xml decayTo: 60 s / 300 s)
- teleport (1387 with a destination): step in -> the destination
Characters are testers: monsters leave them alone, so a cave full of them does not get in the way.
"""
import pytest

from tibia74 import Item, LEFT, RIGHT
from tibia74.quest import step_onto, use_map_item
from tibia74.route import _rope, use_tool
from tibia74.server import TESTER_GROUP

ROPE, SHOVEL, LADDER, SEWER_GRATE = 2120, 2554, 1386, 430
STONE_PILE, STONE_PILE_HOLE = 468, 469
LOOSE_STONE_PILE, LOOSE_STONE_PILE_HOLE = 481, 482


def _beside(world_map, target):
    """A plain floor tile next to target (straight before diagonal): no floor change, no door."""
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)):
        n = (target[0] + dx, target[1] + dy, target[2])
        if world_map.walkable(n) and not world_map.arrival(n) and "door" not in world_map.info(n):
            return n
    raise AssertionError(f"no floor tile next to {target}")


def _player_beside(new_player, world_map, target, **kwargs):
    start = _beside(world_map, target)
    kwargs.setdefault("premium_days", 30)      # a free character in Edron, Darashia... is sent to Thais at login
    p = new_player(pos=start, level=20, group_id=TESTER_GROUP, storage={30001: 1}, **kwargs)
    assert p.pos == start, f"logged in at {p.pos}, not at {start} (next to {target})"
    return p


def _has(p, items, pos, server_id):
    return any(getattr(t, "client_id", None) and items.by_client[t.client_id].server_id == server_id
               for t in p.tiles.get(tuple(pos), []))


# ------------------------------------------------------------------------------------------------ ladders

LADDERS = {
    "Rookgaard sewers, under the temple's grate": (32097, 32205, 8),
    "Thais": (32382, 32230, 7),
    "Carlin": (32347, 31780, 7),
    "Kazordoon": (32628, 31937, 11),
    "Venore sewers": (32917, 32076, 9),
    "Edron": (33215, 31825, 7),
}


@pytest.mark.parametrize("ladder", LADDERS.values(), ids=LADDERS.keys())
def test_using_a_ladder_climbs_one_floor(new_player, items, world_map, ladder):
    p = _player_beside(new_player, world_map, ladder)
    use_map_item(p, items, ladder, LADDER)
    up = (ladder[0], ladder[1] + 1, ladder[2] - 1)
    assert p.wait_for(lambda: p.pos == up, timeout=3), f"used the ladder at {ladder}: at {p.pos}, not {up}"


SEWER_GRATES = {
    "Rookgaard, beside the temple": (32097, 32205, 7),
    "Thais": (32366, 32252, 7),
    "Carlin": (32374, 31774, 7),
}


@pytest.mark.parametrize("grate", SEWER_GRATES.values(), ids=SEWER_GRATES.keys())
def test_using_a_sewer_grate_climbs_down(new_player, items, world_map, grate):
    p = _player_beside(new_player, world_map, grate)
    use_map_item(p, items, grate, SEWER_GRATE)
    down = (grate[0], grate[1], grate[2] + 1)
    assert p.wait_for(lambda: p.pos == down, timeout=3), f"used the grate at {grate}: at {p.pos}, not {down}"


# ------------------------------------------------------------------------- stairs, holes, trapdoors, teleports
# (where you step onto, where you arrive)

STAIRS = {
    "Rookgaard, up to the shop north-east of the temple": ((32110, 32207, 7), (32110, 32206, 6)),
    "Thais, up beside the temple": ((32360, 32241, 7), (32360, 32240, 6)),
    "Carlin, up": ((32365, 31783, 7), (32365, 31782, 6)),
    "Kazordoon, up": ((32661, 31922, 12), (32661, 31921, 11)),
    "Venore, up": ((32953, 32077, 7), (32953, 32076, 6)),
    "Edron, up": ((33211, 31814, 8), (33211, 31813, 7)),
    "Carlin, down": ((32360, 31778, 7), (32360, 31779, 8)),
    "Thais, down": ((32360, 32241, 6), (32360, 32242, 7)),
    "Kazordoon, down": ((32661, 31922, 11), (32661, 31923, 12)),
    "Edron, down": ((33211, 31818, 6), (33211, 31819, 7)),
    "Venore dragon lair, down onto a west ramp": ((32804, 32148, 7), (32805, 32148, 8)),
}

HOLES = {
    "Rookgaard sewers, hole": ((32058, 32180, 8), (32058, 32180, 9)),
    "Rookgaard, hole onto a ramp": ((32146, 32207, 7), (32145, 32207, 8)),
    "Thais, hole": ((32371, 32242, 9), (32371, 32242, 10)),
    "Carlin, hole": ((32392, 31787, 8), (32392, 31787, 9)),
    "Kazordoon, hole": ((32667, 31939, 10), (32667, 31939, 11)),
    "Kazordoon, hole east": ((32683, 31918, 8), (32683, 31918, 9)),
    "Rookgaard, trapdoor": ((32080, 32181, 7), (32080, 32181, 8)),
    "Rookgaard, trapdoor onto stairs": ((32110, 32207, 6), (32110, 32208, 7)),
    "Thais, trapdoor": ((32319, 32275, 7), (32319, 32275, 8)),
    "Carlin, trapdoor": ((32292, 31779, 6), (32292, 31779, 7)),
    "Edron, the goblins' pitfall": ((33128, 31810, 7), (33128, 31810, 8)),
}

TELEPORTS = {
    "Rookgaard academy arena, in": ((32082, 32171, 9), (32088, 32171, 9)),
    "Rookgaard academy arena, out": ((32089, 32171, 9), (32081, 32172, 9)),
    "Hellgate, below Ab'Dendriel": ((32675, 31646, 10), (32725, 31589, 12)),
    "north-east of Ab'Dendriel": ((32794, 31576, 5), (32812, 31577, 5)),
    "north of Carlin, back to the surface": ((32400, 31656, 15), (32493, 31697, 7)),
    "Ankrahmun": ((33150, 32864, 7), (33147, 32864, 7)),
    "Darashia": ((33083, 32569, 13), (33083, 32570, 14)),
    "north of Venore": ((32874, 31955, 11), (32874, 31955, 12)),
}


@pytest.mark.parametrize("target, arrive", [*STAIRS.values(), *HOLES.values(), *TELEPORTS.values()],
                         ids=[*(f"stairs: {k}" for k in STAIRS), *(f"hole: {k}" for k in HOLES),
                              *(f"teleport: {k}" for k in TELEPORTS)])
def test_stepping_on_it_takes_you_there(new_player, world_map, target, arrive):
    p = _player_beside(new_player, world_map, target)
    step_onto(p, target)
    assert p.wait_for(lambda: p.pos == arrive, timeout=3), f"stepped onto {target}: at {p.pos}, not {arrive}"


# ------------------------------------------------------------------------------------------------ rope spots

ROPE_SPOTS = {
    "Rookgaard sewers": (32058, 32180, 9),
    "Thais": (32371, 32242, 10),
    "Carlin": (32392, 31787, 9),
    "Kazordoon": (32667, 31939, 11),
    "Edron": (33234, 31843, 10),
    "Venore": (33008, 32076, 9),
}


@pytest.mark.parametrize("spot", ROPE_SPOTS.values(), ids=ROPE_SPOTS.keys())
def test_a_rope_on_a_rope_spot_pulls_you_up(new_player, items, world_map, spot):
    p = _player_beside(new_player, world_map, spot, inventory={RIGHT: Item(ROPE)})
    up = (spot[0], spot[1] + 1, spot[2] - 1)
    assert _rope(p, items, spot, up), f"used a rope on {spot}: at {p.pos}, not {up}, {p.text_messages[-2:]}"


# ------------------------------------------------------------------------------------------ shovel spots

def test_a_shovel_opens_a_stone_pile_you_fall_through_and_a_rope_gets_you_back(new_player, items, world_map):
    """Rookgaard, north of the village: a stone pile above a rope spot. Dig, fall, rope up again."""
    pile = (32077, 32151, 7)
    p = _player_beside(new_player, world_map, pile, inventory={RIGHT: Item(SHOVEL), LEFT: Item(ROPE)})
    use_tool(p, items, "shovel", pile, {STONE_PILE})
    assert p.wait_for(lambda: _has(p, items, pile, STONE_PILE_HOLE), timeout=3), \
        f"the shovel did not open the stone pile at {pile}: {p.tiles.get(pile)}, {p.text_messages[-2:]}"
    step_onto(p, pile)
    below = (pile[0], pile[1], pile[2] + 1)
    assert p.wait_for(lambda: p.pos == below, timeout=3), f"stepped into the hole at {pile}: at {p.pos}"
    # the way back: the spot under the hole is a rope spot (the hole is still open: 60 s). Off it first: rope.lua
    # refuses a spot anyone stands on, its user too ("You can not use this object.")
    step_onto(p, _beside(world_map, below))
    up = (below[0], below[1] + 1, pile[2])
    assert _rope(p, items, below, up), f"used a rope on {below}: at {p.pos}, not {up}, {p.text_messages[-2:]}"


def test_a_dug_hole_closes_again_after_a_minute(new_player, items, world_map):
    """Kazordoon, the hills above the city: items.xml lets a dug hole (469) decay back to the stone pile after
    60 s - nobody has to close it. One who stays beside it sees the pile come back."""
    pile = (32651, 31937, 7)
    p = _player_beside(new_player, world_map, pile, inventory={RIGHT: Item(SHOVEL)})
    use_tool(p, items, "shovel", pile, {STONE_PILE})
    assert p.wait_for(lambda: _has(p, items, pile, STONE_PILE_HOLE), timeout=3), \
        f"the shovel did not open the stone pile at {pile}: {p.tiles.get(pile)}, {p.text_messages[-2:]}"
    p.sleep(50)
    assert _has(p, items, pile, STONE_PILE_HOLE), "the hole closed well before its minute"
    assert p.wait_for(lambda: _has(p, items, pile, STONE_PILE), timeout=20), \
        f"the hole at {pile} is still open after 70 s: {p.tiles.get(pile)}"


def test_a_shovel_opens_a_loose_stone_pile(new_player, items, world_map):
    """Ankrahmun, east of the city: a loose stone pile (481) opens into a hole (482, closes after 300 s) above a
    ladder - the way into a tomb."""
    pile = (33255, 32833, 7)
    p = _player_beside(new_player, world_map, pile, inventory={RIGHT: Item(SHOVEL)})
    use_tool(p, items, "shovel", pile, {LOOSE_STONE_PILE})
    assert p.wait_for(lambda: _has(p, items, pile, LOOSE_STONE_PILE_HOLE), timeout=3), \
        f"the shovel did not open the loose stone pile at {pile}: {p.tiles.get(pile)}, {p.text_messages[-2:]}"
    step_onto(p, pile)
    below = (pile[0], pile[1], pile[2] + 1)
    assert p.wait_for(lambda: p.pos == below, timeout=3), f"stepped into the hole at {pile}: at {p.pos}"

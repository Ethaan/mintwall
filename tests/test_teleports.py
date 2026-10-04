"""Every teleport on the map lands somewhere a player can stand (no server needed: the map's own data, as the route
planner reads it - tibia74/worldmap.py). The full table, with the original map and other maps compared:
tools/teleport-audit.py.

Found by the audit (2026-10-03): Morguthis's floor-14 forcefield 33238,32644,14 sent players into the rock south of
the altar room (33162,32654,14) - stuck for good; it now lands in the room (33161,32652,14). The Ghost Ship's
forcefield (33328,32181,6) and the boats landed on a wooden pillar in Darashia (33290,32481,7); now on the deck next to
it (33290,32480,7)."""
from tibia74.worldmap import VOID

ROOKGAARD = ((31900, 32000), (32250, 32300))      # x 31900-32250, y 32000-32300 (tools/teleport-audit.py)

def _teleports(world_map):
    return {pos: tuple(info["teleport"]) for pos, info in world_map.special.items() if "teleport" in info}


def _rookgaard(pos):
    (x1, y1), (x2, y2) = ROOKGAARD
    return x1 <= pos[0] <= x2 and y1 <= pos[1] <= y2


def test_the_map_has_its_teleports(world_map):
    assert len(_teleports(world_map)) > 120


def test_every_teleport_lands_on_a_tile_you_can_stand_on(world_map):
    bad = {src: (dst, "no tile" if world_map.kind(dst) == VOID else "blocked")
           for src, dst in _teleports(world_map).items()
           if not world_map.walkable(dst)}
    assert not bad, bad


def test_no_teleport_lands_on_another_teleport_or_a_floor_change(world_map):
    """The engine moves you on from where you land: onto a teleport it sends you on (or straight back), onto a hole
    down."""
    teleports = _teleports(world_map)
    onto = {src: (dst, world_map.info(dst)) for src, dst in teleports.items()
            if dst in teleports or world_map.info(dst).get("down") or world_map.info(dst).get("up")}
    assert not onto, onto


def test_no_teleport_between_rookgaard_and_the_mainland(world_map):
    """Two did (the Rookgaard temple's to Thais, one beside the Thais temple to Rookgaard - removed); only the
    Oracle (and death) takes a player off the island."""
    crossing = {src: dst for src, dst in _teleports(world_map).items() if _rookgaard(src) != _rookgaard(dst)}
    assert not crossing, crossing

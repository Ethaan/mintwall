"""Every town's temple (the 47 towns of Tibia74.otbm, read from the map): a character logs in right on it - not pushed to a
free tile next to it, which the engine does when the spot is blocked - and can step off and back. A character whose
position is 0,0,0 starts at its town's temple (IOPlayer::loadPlayer; death sends it there too: Player::onDie), and the
nine real towns' temples are protection zone.

Most of the 47 "towns" are not towns but spawn/utility points of the old map (Havoc, Orc, Minocity, DragonIsle, ...);
nothing sends a player to them, but a /town command or a wrong town_id could, so they get the same check."""
import pytest

from tibia74 import NORTH, EAST, SOUTH, WEST, NORTHEAST, SOUTHEAST, SOUTHWEST, NORTHWEST, SERVER_DIR
from tibia74.client import _DIR_DELTA
from tibia74.db import BEGINNER_SET_GIVEN
from tibia74.otbm import read_tiles, read_towns
from tibia74.server import TESTER_GROUP

MAP = SERVER_DIR / "data" / "world" / "Tibia74.otbm"
TOWNS = {t.name: t for t in read_towns(MAP)}
REAL_TOWNS = ["Rookgaard", "Thais", "Carlin", "Kazordoon", "Ab'Dendriel", "Edron", "Darashia", "Venore", "Ankrahmun"]
TILESTATE_PROTECTIONZONE = 1      # OTBM tile flag, read by the engine as the tile's protection zone
OPPOSITE = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST,
            NORTHEAST: SOUTHWEST, SOUTHWEST: NORTHEAST, NORTHWEST: SOUTHEAST, SOUTHEAST: NORTHWEST}

# A vocation-less character: a premium-expired vocation character is sent to the TEMPLE_TP_ID town instead
PLAYER = dict(level=8, vocation=0, group_id=TESTER_GROUP, storage={BEGINNER_SET_GIVEN: 1})


def _step_off_and_back(p, temple):
    """Step to any neighbour on the same floor and back onto the temple; the neighbour taken, or None."""
    for d in (NORTH, EAST, SOUTH, WEST, NORTHEAST, SOUTHEAST, SOUTHWEST, NORTHWEST):
        if not p.step(d):
            continue
        dx, dy = _DIR_DELTA[d]
        assert p.pos == (temple[0] + dx, temple[1] + dy, temple[2]), \
            f"stepping {d} from the temple {temple} led to {p.pos} (floor change?)"
        neighbour = p.pos
        assert p.step(OPPOSITE[d]) and p.pos == temple, f"could not step back from {neighbour}: at {p.pos}"
        return neighbour
    return None


@pytest.mark.parametrize("name", list(TOWNS))
def test_temple_is_walkable(new_player, name):
    town = TOWNS[name]
    p = new_player(pos=town.temple, town_id=town.id, **PLAYER)
    assert p.pos == town.temple, f"{name}: logged in at {p.pos}, not on the temple {town.temple} (blocked?)"
    assert _step_off_and_back(p, town.temple), f"{name}: no walkable tile around the temple {town.temple}"


@pytest.mark.parametrize("name", list(TOWNS))
def test_character_of_the_town_starts_at_its_temple(new_player, db, name):
    """Position 0,0,0 = the town's temple: where a citizen of the town starts and respawns."""
    town = TOWNS[name]
    p = new_player(pos=None, town_id=town.id, **PLAYER)
    assert p.pos == town.temple, f"{name}: a citizen logged in at {p.pos}, not at the temple {town.temple}"
    p.logout()
    assert db.town_after_logout(p.character.guid, town.id) == town.id


@pytest.fixture(scope="module")
def temple_tiles():
    temples = {TOWNS[n].temple for n in REAL_TOWNS}
    return {t.pos: t for t in read_tiles(MAP) if t.pos in temples}


@pytest.mark.parametrize("name", REAL_TOWNS[1:])
def test_real_town_temple_is_protection_zone(temple_tiles, name):
    temple = TOWNS[name].temple
    assert temple in temple_tiles, f"{name}: no tile at the temple {temple}"
    assert temple_tiles[temple].flags & TILESTATE_PROTECTIONZONE, f"{name}: the temple {temple} is not protection zone"


def test_rookgaard_temple_is_no_protection_zone(temple_tiles):
    """7.4 Rookgaard had none (the user's memory, 2026-10-03): no tile on the island is protection zone on the source
    map, ours or the JS engine's copy, while the Thais temple has 176 - so it is the map's, not lost in our edits."""
    temple = TOWNS["Rookgaard"].temple
    assert not temple_tiles[temple].flags & TILESTATE_PROTECTIONZONE

"""What the Ancient Tombs tests share (docs/reference-74/quests.md, The Ancient Tombs Quest): each tomb's mystic flame
and coal basin, the pharaohs' pass items and sarcophagus rooms, and the moves a player makes there - a scarab coin on
the basin, killing a pharaoh and taking his pass item from the body."""
from quests.common import *  # noqa: F401,F403

SCARAB_COIN = 2159
HMM = 2311                                # heavy magic missile rune: energy, what hurts every pharaoh
GROUP_CONTAINER = 2


class Tomb:
    def __init__(self, entrance, flame, basin, below, pharaoh, lair, pass_item, portal, room, sarcophagus, piece, back):
        self.entrance = entrance          # the loose stone pile to dig open
        self.flame, self.basin = flame, basin
        self.below = below                # where the flame takes you once the coin is on the basin
        self.pharaoh, self.pass_item = pharaoh, pass_item
        self.lair = lair                  # where the pharaoh spawns (the spawns file)
        self.portal = portal              # the forcefield in the pharaoh's room
        self.room = room                  # the sarcophagus room (with the pass item)
        self.sarcophagus, self.piece = sarcophagus, piece
        self.back = back                  # the start of the tomb (without it) - where the room's exit leads too


# positions: our map (the flames' and portals' former destinations), tibiaot74's sarcophagi; pieces: current wiki
VASHRESAMUN = Tomb(entrance=(33208, 32591, 7), flame=(33276, 32553, 14), basin=(33276, 32552, 14),
                   below=(33271, 32553, 14), pharaoh="Vashresamun", lair=(33121, 32656, 15), pass_item="blue note",
                   portal=(33116, 32656, 15), room=(33145, 32667, 15), sarcophagus=(33145, 32663, 15),
                   piece="a left horn", back=(33208, 32589, 7))
RAHEMOS = Tomb(entrance=(33133, 32640, 7), flame=(33135, 32683, 12), basin=(33135, 32682, 12),
               below=(33130, 32683, 12), pharaoh="Rahemos", lair=(33076, 32781, 14), pass_item="ancient rune",
               portal=(33073, 32781, 14), room=(33052, 32778, 14), sarcophagus=(33051, 32774, 14),
               piece="a helmet piece", back=(33133, 32642, 7))
DIPTHRAH = Tomb(entrance=(33133, 32568, 7), flame=(33073, 32590, 13), basin=(33073, 32589, 13),
                below=(33080, 32588, 13), pharaoh="Dipthrah", lair=(33092, 32590, 15), pass_item="ornamented ankh",
                portal=(33103, 32590, 15), room=(33127, 32593, 15), sarcophagus=(33126, 32589, 15),
                piece="a damaged helmet", back=(33132, 32570, 7))
OMRUC = Tomb(entrance=(33027, 32869, 7), flame=(33097, 32816, 13), basin=(33098, 32816, 13),
             below=(33093, 32824, 13), pharaoh="Omruc", lair=(33202, 32998, 14), pass_item="crystal arrow",
             portal=(33195, 33002, 14), room=(33179, 33017, 14), sarcophagus=(33178, 33013, 14),
             piece="a helmet adornment", back=(33028, 32869, 7))
THALAS = Tomb(entrance=(33282, 32743, 7), flame=(33293, 32742, 13), basin=(33293, 32741, 13),
              below=(33300, 32742, 13), pharaoh="Thalas", lair=(33396, 32839, 14), pass_item="cobrafang dagger",
              portal=(33396, 32852, 14), room=(33349, 32830, 14), sarcophagus=(33349, 32825, 14),
              piece="a gem holder", back=(33282, 32742, 7))
MAHRDIS = Tomb(entrance=(33255, 32833, 7), flame=(33240, 32856, 13), basin=(33240, 32855, 13),
               below=(33246, 32850, 13), pharaoh="Mahrdis", lair=(33191, 32954, 15), pass_item="burning heart",
               portal=(33191, 32959, 15), room=(33175, 32936, 15), sarcophagus=(33174, 32932, 15),
               piece="a helmet ornament", back=(33254, 32833, 7))
MORGUTHIS = Tomb(entrance=(33233, 32704, 7), flame=(33234, 32692, 13), basin=(33233, 32692, 13),
                 below=(33234, 32687, 13), pharaoh="Morguthis", lair=(33169, 32694, 14), pass_item="sword hilt",
                 portal=(33174, 32694, 14), room=(33183, 32716, 14), sarcophagus=(33182, 32712, 14),
                 piece="a right horn", back=(33232, 32704, 7))


def tomb_player(new_player, items=(), coins=1, **kwargs):
    """A strong premium tester at the Ankrahmun temple with a shovel, scarab coins and heavy magic missile runes (a
    pharaoh heals faster than a sword hurts him)."""
    from tibia74 import Item
    kwargs.setdefault("maglevel", 100)
    return ankrahmun_player(new_player, items=[Item(SHOVEL), Item(SCARAB_COIN, coins), *[Item(HMM, 100)] * 3, *items],
                            **kwargs)


def sacrifice_coin(p, items, tomb):
    """Standing on the mystic flame, put one scarab coin on the empty coal basin: down to the deeper tomb."""
    assert p.pos == tomb.flame, (p.pos, tomb.flame)
    client_id = items.by_server[SCARAB_COIN].client_id
    cid, n, item = next((cid, n, i) for cid, c in p.containers.items() for n, i in enumerate(c.items)
                        if i.client_id == client_id)
    p.move_item(p.container_pos(cid, n), client_id, n, tomb.basin, 1)
    assert p.wait_for(lambda: p.pos == tomb.below, timeout=3), (p.pos, p.text_messages[-2:])


def kill_pharaoh(p, items, world_map, tomb, **ability):
    """Go to the pharaoh's lair and kill him; returns where his body lies."""
    from tibia74.route import walk_near
    walk_near(p, items, world_map, tomb.lair, radius=3, **ability)
    return kill(p, items, tomb.pharaoh, lair=tomb.lair, world_map=world_map, ability=ability)


def kill(p, items, name, timeout=120, lair=None, world_map=None, ability=None):
    """Fight the creature named `name` in view - sword and heavy magic missiles, like a player - until its body
    lies there; returns where. Some pharaohs turn invisible now and then (Omruc, Morguthis, Ashmunrah): the client
    loses them - wait until they show again (the fight goes on) or their body appears."""
    from tibia74.route import carried
    creature = p.wait_for(lambda: next((c for c in p.creatures.values() if c.name == name), None), timeout=5)
    assert creature, f"no {name} in view from {p.pos}: {list(p.creatures.values())}"
    bodies_before = set(_bodies(p, items))
    last = [creature.pos]

    def body():
        new = [pos for pos in _bodies(p, items) if pos not in bodies_before]
        near = last[0] or p.pos
        return min(new, key=lambda pos: abs(pos[0] - near[0]) + abs(pos[1] - near[1])) if new else None

    def seen():
        c = p.creatures.get(creature.id)          # a creature out of view stays known, without a position
        if c is not None and c.pos:
            last[0] = c.pos
            return c
        return None

    p.set_fight_modes(fight=1, chase=1, safe=1)
    for _ in range(int(timeout / 2.1)):
        if body():
            break
        c = seen()
        if c is None:
            p.wait_for(lambda: body() or seen(), 2.1)
            continue
        p.attack(creature.id)
        rune = carried(p, p.items, lambda n: n == "heavy magic missile rune")
        stack = p.tiles.get(tuple(c.pos), [])
        at = next((n for n, t in enumerate(stack)
                   if (t if isinstance(t, int) else getattr(t, "id", None)) == creature.id), None)
        if rune is not None and at is not None:
            p.use_item_with(*rune, tuple(c.pos), 0x63, at)
        p.wait_for(body, 2.1)                    # rune exhaustion
    found = p.wait_for(body, 5)
    if not found and lair and (creature.id in p.removed_creatures or creature.health == 0):
        # he died where the client no longer saw him (Thalas slips out of view): look where he lived
        from tibia74.route import walk_near
        last[0] = last[0] or lair
        walk_near(p, items, world_map, lair, radius=3, **(ability or {}))
        found = p.wait_for(body, 5)
    assert found, (creature, last[0], p.pos)
    p.attack(0)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return found


def _bodies(p, items):
    return [pos for pos, stack in list(p.tiles.items())
            for t in stack if getattr(t, "client_id", None) and
            items.name(items.by_client[t.client_id].server_id) == "dead pharaoh"]


def loot(p, items, pos, name):
    """Open the body lying at pos and take `name` out of it into the backpack."""
    from tibia74.quest import open_map_container, take
    assert p.wait_for(lambda: _body(items, p, pos), timeout=3), (pos, p.tiles.get(pos))
    body = open_map_container(p, items, pos, _body(items, p, pos))
    assert any(i.name == name for i in body.items), (name, body.items)
    take(p, items, body, name)


def _body(items, p, pos):
    for thing in reversed(p.tiles.get(tuple(pos), [])):
        cid = getattr(thing, "client_id", None)
        if cid and items.by_client[cid].group == GROUP_CONTAINER:
            return items.by_client[cid].server_id
    return None

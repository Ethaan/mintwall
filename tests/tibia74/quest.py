"""Helpers for quest tests (docs/reference-74/quests.md): a character that can do any route, and the actions a
player takes on the way - use things on the map, open quest containers, check what they carry.

Walking itself is tibia74/route.py (plan on the real map + follow it, re-planning on surprises).
"""
from . import BACKPACK, RIGHT, Item

ROPE = 2120


def strong(new_player, pos, *, level=2000, vocation=4, items=(), **kwargs):
    """A character that walks fast and survives anything on the way. Level 2000 is not a quest's rule: the
    tests that check a quest's level door use a character of exactly that level."""
    kwargs.setdefault("storage", {})
    kwargs["storage"] = {30001: 1, **kwargs["storage"]}           # no beginner-set chat on login
    return new_player(pos=pos, level=level, vocation=vocation, skills={1: 150, 2: 150, 3: 150, 5: 150},
                      inventory={RIGHT: Item(2400),                               # magic sword
                                 BACKPACK: Item(1988, contents=[Item(ROPE), *items])}, **kwargs)


def next_to(new_player, target, **kwargs):
    """A new character standing within one tile of target (tries the 8 neighbours: walls, counters)."""
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
        p = new_player(pos=(target[0] + dx, target[1] + dy, target[2]), **kwargs)
        if p.pos[2] == target[2] and max(abs(p.pos[0] - target[0]), abs(p.pos[1] - target[1])) <= 1:
            return p
        p.logout()
    raise AssertionError(f"could not stand next to {target}")


def _find(p, items, pos, what):
    for stackpos, thing in enumerate(p.tiles.get(pos, [])):
        cid = getattr(thing, "client_id", None)
        if cid:
            sid = items.by_client[cid].server_id
            if sid == what or items.name(sid) == what:
                return stackpos, thing, sid
    return None


def _above(p, items, pos, target_stackpos):
    """Movable items lying on top of the target (the server uses the topmost item: Game::internalGetThing,
    STACKPOS_USE -> getTopDownItem), highest first. Ground, always-on-top items and creatures don't count."""
    out = []
    for stackpos, thing in enumerate(p.tiles.get(pos, [])[:target_stackpos]):
        cid = getattr(thing, "client_id", None)
        if stackpos == 0 or not cid:
            continue
        if not items.by_client[cid].always_on_top:
            out.append((stackpos, thing))
    return out


def use_map_item(p, items, pos, what):
    """Use (right-click) an item lying at pos. `what` is its server id or its name ("box", "chest"), never "any
    container". The server uses the topmost item on the tile, whatever the client points at - so, like a
    player would, first move whatever lies on top of it (a corpse left by a fight, say) onto our own tile."""
    pos = tuple(pos)
    assert p.wait_for(lambda: pos in p.tiles, timeout=3), f"{pos} not in view"
    for _ in range(10):
        found = _find(p, items, pos, what)
        if found is None:
            raise AssertionError(f"no {what!r} at {pos}: {p.tiles.get(pos)}")
        stackpos, thing, sid = found
        above = _above(p, items, pos, stackpos)
        if not above:
            p.use_item(pos, thing.client_id, stackpos)
            return sid
        top_pos, top = above[0]
        before = len(p.tiles.get(pos, []))
        # onto our own tile, else any tile around the target the server accepts ("There is not enough room")
        spots = [p.pos] + [(pos[0] + dx, pos[1] + dy, pos[2]) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                           if (dx or dy) and (pos[0] + dx, pos[1] + dy, pos[2]) != p.pos]
        for spot in spots:
            p.move_item(pos, top.client_id, top_pos, spot, max(top.count, 1))
            if p.wait_for(lambda: len(p.tiles.get(pos, [])) < before, timeout=1.5):
                break
        else:
            raise AssertionError(f"could not move {top} off the {what} at {pos}: {p.text_messages[-2:]}")
    raise AssertionError(f"too many things on the {what} at {pos}: {p.tiles.get(pos)}")


def carries(p, name):
    """The character wears it or has it in an open container."""
    return any(i.name == name for i in p.all_items())


def talk_to(p, npc, *lines):
    """Say lines to an NPC while following it (NPCs wander and leave talk range); returns its replies."""
    target = p.wait_for(lambda: next((c for c in p.creatures.values() if c.name == npc), None), timeout=5)
    assert target, f"{npc} is not in view from {p.pos}"
    p.follow(target.id)
    p.wait_for(lambda: target.pos and p.pos and target.pos[2] == p.pos[2]
               and max(abs(target.pos[0] - p.pos[0]), abs(target.pos[1] - p.pos[1])) <= 1, timeout=8)
    try:
        return p.talk(*lines, npc=npc)
    finally:
        p.follow(0)


def open_carried(p, items, name):
    """Open a container the character carries - worn (a reward can land in a free hand) or in an open
    container - in a new container window, and return it once the client shows it. The 7.4 "use" packet
    names the window to open into: 0 would replace the main backpack's window."""
    window = max(p.containers, default=-1) + 1
    sources = [(p.inventory_pos(slot), item.client_id, 0) for slot, item in p.inventory.items() if slot != 3]
    sources += [(p.container_pos(cid, n), item.client_id, n)
                for cid, c in p.containers.items() for n, item in enumerate(c.items)]
    for pos, client_id, stackpos in sources:
        if items.name(items.by_client[client_id].server_id) == name:
            p.use_item(pos, client_id, stackpos, window)
            assert p.wait_for(lambda: window in p.containers, timeout=3), f"{name} did not open"
            return p.containers[window]
    raise AssertionError(f"no {name} carried: {p.inventory_names()}, {[c.items for c in p.containers.values()]}")

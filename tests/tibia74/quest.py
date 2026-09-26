"""Helpers for quest tests (docs/reference-74/quests.md): a character that can do any route, and the actions a
player takes on the way - use things on the map, open quest containers, check what they carry.

Walking itself is tibia74/route.py (plan on the real map + follow it, re-planning on surprises).
"""
import re

from . import BACKPACK, RIGHT, Item, watch

ROPE = 2120


def strong(new_player, pos, *, level=2000, vocation=4, items=(), **kwargs):
    """A character that walks fast and survives anything on the way. Level 2000 is not a quest's rule: the
    tests that check a quest's level door use a character of exactly that level."""
    kwargs.setdefault("storage", {})
    kwargs["storage"] = {30001: 1, **kwargs["storage"]}           # no beginner-set chat on login
    p = new_player(pos=pos, level=level, vocation=vocation, skills={1: 150, 2: 150, 3: 150, 5: 150},
                   inventory={RIGHT: Item(2400),                                  # magic sword
                              BACKPACK: Item(1988, contents=[Item(ROPE), *items])}, **kwargs)
    watch.wait_for_viewer(p)
    return p


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
    STACKPOS_USE -> getTopDownItem), highest first. Ground, always-on-top items and creatures don't count.
    The target itself may be the ground (a loose board): then every item lying on the tile is on top of it."""
    out = []
    things = p.tiles.get(pos, [])
    for stackpos, thing in enumerate(things if target_stackpos == 0 else things[:target_stackpos]):
        cid = getattr(thing, "client_id", None)
        if stackpos == 0 or not cid:
            continue
        if not items.by_client[cid].always_on_top:
            out.append((stackpos, thing))
    return out


def use_map_item(p, items, pos, what, window=0):
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
            p.use_item(pos, thing.client_id, stackpos, window)   # window: where a container opens
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
        replies = []
        for line in lines:
            replies += _say_unmuted(p, line, npc)
        return replies
    finally:
        p.follow(0)
        if lines and lines[-1] != "bye":
            # like a player: an NPC talks to one player at a time and would keep us. Wait for its goodbye,
            # or it arrives late and is taken for the answer to the next conversation's first line
            _say_unmuted(p, "bye", npc)


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


def _say_unmuted(p, line, npc):
    """Say one line to an NPC like a player: a moment between lines (the anti-spam mute counts fast talk), and
    if the mute swallowed it ("You are muted for N seconds." and no answer) wait that long and say it again.
    A line the NPC answered counts as heard, mute message or not."""
    replies = []
    for _ in range(4):
        before = len(p.text_messages)
        replies += p.talk(line, npc=npc)
        if replies:
            p.sleep(0.7)
            return replies
        muted = [t for _, t in p.text_messages[before:] if "muted for" in t]
        if not muted:
            return replies
        found = re.search(r"(\d+) second", muted[-1])
        p.sleep((int(found.group(1)) if found else 5) + 0.5)
    raise AssertionError(f"still muted after 4 tries saying {line!r}: {p.text_messages[-3:]}")


_NPC_POSITIONS = None


def npc_pos(name):
    """Where an NPC spawns (the map's spawns file) - never a position copied from a guide."""
    global _NPC_POSITIONS
    if _NPC_POSITIONS is None:
        from . import SERVER_DIR
        from .npcs import load_npcs
        _NPC_POSITIONS = {n: npc.pos for n, npc in load_npcs(SERVER_DIR).items()}
    assert _NPC_POSITIONS.get(name), f"no spawn for NPC {name!r}"
    return _NPC_POSITIONS[name]


def open_map_container(p, items, pos, what):
    """Open a container lying on the map (a box, a body) in a new window, like right-clicking it."""
    window = max(p.containers, default=-1) + 1
    before = set(p.containers)
    use_map_item(p, items, pos, what, window)
    assert p.wait_for(lambda: set(p.containers) - before, timeout=3), f"the {what} at {pos} did not open"
    return p.containers[(set(p.containers) - before).pop()]


def take(p, items, container, name, into=3):
    """Move an item out of an open container into the backpack worn in slot `into` (dropped on the worn backpack, like
    a player; its window must be open to see it arrive)."""
    source = next(cid for cid, c in p.containers.items() if c is container)
    target = next(cid for cid, c in p.containers.items() if c is not container and c.item_id == p.inventory[into].client_id)
    n, item = next((n, i) for n, i in enumerate(container.items) if i.name == name)
    bag = p.containers[target]
    before = sum(1 for i in bag.items if i.name == name)
    p.move_item(p.container_pos(source, n), item.client_id, n, p.inventory_pos(into), max(item.count, 1))
    assert p.wait_for(lambda: sum(1 for i in bag.items if i.name == name) > before, timeout=3), \
        f"{name} not taken: {p.text_messages[-2:]}"


def pick_up(p, items, pos, name, into=3):
    """Pick an item lying on the map up into the backpack worn in slot `into` (it must be open), like dragging it -
    from under a field too (Draconia's keys)."""
    target = next(cid for cid, c in p.containers.items() if c.item_id == p.inventory[into].client_id)
    stack = p.tiles.get(tuple(pos), [])
    n, thing = next((n, t) for n, t in enumerate(stack) if getattr(t, "client_id", None)
                    and items.name(items.by_client[t.client_id].server_id) == name)
    before = sum(1 for i in p.containers[target].items if i.name == name)
    p.move_item(tuple(pos), thing.client_id, n, p.inventory_pos(into), max(getattr(thing, "count", 1), 1))
    bag = p.containers[target]
    assert p.wait_for(lambda: sum(1 for i in bag.items if i.name == name) > before, timeout=3), \
        f"{name} not picked up at {pos}: {stack}, {p.text_messages[-2:]}"


# ------------------------------------------------------------------------------------------ quest rules
# The questions every quest answers (see .claude/skills/quest-testing): can you get in, what level / vocation /
# key / storage lets you, can you get out again. These check one rule each, the way a player meets it.

def step_onto(p, pos):
    """One step from a neighbouring tile onto pos - for a floor change the route planner cannot know (a trapdoor,
    stairs or a portal a switch has just made)."""
    from .route import DIRECTIONS
    d = DIRECTIONS[(pos[0] - p.pos[0], pos[1] - p.pos[1])]
    before = p.pos
    p.step(d)
    assert p.wait_for(lambda: p.pos != before, timeout=3), f"could not step from {before} onto {pos}"


def assert_level_door(new_player, items, door, outside, level, *, vocation=4, gate="gate of expertise"):
    """A level door (gate of expertise, action id 1000 + level): a character of level - 1 standing at `outside`
    is refused ("Only the worthy may pass.") and stays; one of exactly `level` passes into the doorway.
    Testers (monsters leave them alone) with no GM access - access skips the check (gateofexp_closed.lua)."""
    from .server import TESTER_GROUP
    below = new_player(pos=outside, level=level - 1, vocation=vocation, group_id=TESTER_GROUP, storage={30001: 1})
    assert below.pos == tuple(outside), f"level {level - 1} did not start at {outside}: {below.pos}"
    use_map_item(below, items, door, gate)
    assert below.wait_for(lambda: below.messages("Only the worthy may pass."), timeout=3), \
        f"level {level - 1} was not refused at {door}: {below.text_messages[-2:]}"
    below.sleep(0.5)
    assert below.pos == tuple(outside), f"level {level - 1} got through {door}: {below.pos}"
    below.logout()

    worthy = new_player(pos=outside, level=level, vocation=vocation, group_id=TESTER_GROUP, storage={30001: 1})
    use_map_item(worthy, items, door, gate)
    assert worthy.wait_for(lambda: worthy.pos == tuple(door), timeout=3), \
        f"level {level} did not pass {door}: at {worthy.pos}, {worthy.text_messages[-2:]}"
    worthy.logout()


def way(world, start, goal, **ability):
    """The planned route from start to goal (list of steps), or None if the map has no way for this character.
    A static check on the map as it is at server start (switches and portals a script makes are not in it)."""
    from .route import RouteError, plan
    try:
        return plan(world, start, goal, **ability)
    except RouteError:
        return None


def assert_way(world, start, goal, **ability):
    steps = way(world, start, goal, **ability)
    assert steps is not None, f"no way from {start} to {goal} with {ability}"
    return steps


def assert_no_way(world, start, goal, **ability):
    """E.g. no way into a quest without its key, or no way out of a room whose exit a switch has to open."""
    steps = way(world, start, goal, **ability)
    assert steps is None, f"a way from {start} to {goal} with {ability}: " \
                          f"{[(s.kind, s.target) for s in steps if s.kind != 'walk']}"

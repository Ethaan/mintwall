"""Plan and walk routes across the real map, the way a player would (quest tests start in a temple).

    steps = plan(world, start, goal, level=..., keys={4601}, storages={...}, rope=True)
    follow(client, world, goal, level=..., ...)      # plans, walks, re-plans on surprises

A step is one move: walking to a neighbour tile (which may take you to another floor or through a
teleport), opening a door, using a ladder, or roping up. Costs follow 7.4: a diagonal step takes three
times as long as a straight one (docs/reference-74 speed notes), doors cost one extra use.
Doors are only planned through when the character may pass them (world.info: door kinds):
closed = anyone, locked = holds the key (action id), quest = storage set, level = level / vocation.
"""
import heapq
import time
from dataclasses import dataclass

from .client import EAST, NORTH, NORTHEAST, NORTHWEST, SOUTH, SOUTHEAST, SOUTHWEST, WEST, Creature
from . import watch
from .worldmap import WorldMap

DIRECTIONS = {(0, -1): NORTH, (1, 0): EAST, (0, 1): SOUTH, (-1, 0): WEST,
              (1, -1): NORTHEAST, (1, 1): SOUTHEAST, (-1, 1): SOUTHWEST, (-1, -1): NORTHWEST}
ROPE = 2120


@dataclass(frozen=True)
class Step:
    kind: str          # "walk" | "door" | "ladder" | "rope"
    target: tuple      # the tile stepped on / the door / ladder / rope spot
    arrive: tuple      # where the character stands afterwards


def may_pass(info: dict, level: int, vocation: int, keys: set, storages: set) -> bool:
    kind, aid = info.get("door"), info.get("aid", 0)
    if kind == "closed":
        return True
    if kind == "locked":
        return aid in keys
    if kind == "quest":
        return aid == 0 or aid in storages
    if kind == "level":
        if 1001 <= aid <= 1999:
            return level >= aid - 1000
        if 2001 <= aid <= 2008:
            return vocation == aid - 2000
        return True                       # no action id: an ordinary gate (gateofexp_closed opens it)
    return False


def _neighbours(world: WorldMap, pos, level, vocation, keys, storages, rope, open_tiles=frozenset(),
                avoid=frozenset(), scythe=False, shovel=False, pick=False):
    x, y, z = pos
    for (dx, dy), _ in DIRECTIONS.items():
        m = (x + dx, y + dy, z)
        if m in avoid:
            continue
        cost = 3 if dx and dy else 1
        info = world.info(m)
        if "door" in info and m not in open_tiles:
            if may_pass(info, level, vocation, keys, storages) and not (dx and dy):
                yield cost + 1, Step("door", m, m)
            continue
        if world.walkable(m) or m in open_tiles:
            yield cost, Step("walk", m, world.arrival(m) or m)
        elif scythe and info.get("wheat") and not (dx and dy):
            yield cost + 1, Step("wheat", m, m)
        elif shovel and info.get("dig") and not (dx and dy):
            yield cost + 1, Step("dig", m, (m[0], m[1], m[2] + 1))
        elif info.get("push") and not (dx and dy):
            yield cost + 4, Step("push", m, m)
        if pick and info.get("pick") and not (dx and dy):
            yield cost + 2, Step("pick", m, (m[0], m[1], m[2] + 1))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            t = (x + dx, y + dy, z)
            info = world.info(t)
            up = (t[0], t[1] + 1, z - 1)
            if info.get("ladder") and world.walkable(up):
                yield 2, Step("ladder", t, world.arrival(up) or up)
            below = (t[0], t[1], z + 1)
            if info.get("grate") and world.walkable(below):
                yield 2, Step("grate", t, world.arrival(below) or below)
            if rope and info.get("rope") and t != pos and world.walkable(up):
                yield 2, Step("rope", t, world.arrival(up) or up)


def plan(world: WorldMap, start, goal, *, margins=(60, 150, 400), **kwargs):
    """Cheapest list of Steps from start to goal (both tuples). The search stays in a box around start and
    goal, widened when there is no route inside it (the way down to a dungeon can leave a small box)."""
    error = None
    for margin in margins:
        try:
            return _plan(world, start, goal, margin=margin, **kwargs)
        except RouteError as e:
            error = e
    raise error


def _plan(world: WorldMap, start, goal, *, level=1, vocation=0, keys=(), storages=(), rope=False,
          open_tiles=(), avoid=(), scythe=False, shovel=False, pick=False, margin=60, floors=4,
          max_nodes=2_000_000):
    start, goal = tuple(start), tuple(goal)
    keys, storages, open_tiles = set(keys), set(storages), frozenset(tuple(t) for t in open_tiles)
    avoid = frozenset(tuple(t) for t in avoid)
    lo = (min(start[0], goal[0]) - margin, min(start[1], goal[1]) - margin, min(start[2], goal[2]) - floors)
    hi = (max(start[0], goal[0]) + margin, max(start[1], goal[1]) + margin, max(start[2], goal[2]) + floors)

    def h(p):
        return max(abs(p[0] - goal[0]), abs(p[1] - goal[1])) + 3 * abs(p[2] - goal[2])

    frontier = [(h(start), 0, start)]
    came = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        _, cost, pos = heapq.heappop(frontier)
        if pos == goal:
            steps = []
            while came[pos] is not None:
                prev, step = came[pos]
                steps.append(step)
                pos = prev
            return steps[::-1]
        if cost > cost_so_far.get(pos, 1 << 30):
            continue
        for c, step in _neighbours(world, pos, level, vocation, keys, storages, rope, open_tiles, avoid,
                                   scythe, shovel, pick):
            nxt = step.arrive if step.kind != "door" else step.target
            if not (lo[0] <= nxt[0] <= hi[0] and lo[1] <= nxt[1] <= hi[1] and lo[2] <= nxt[2] <= hi[2]):
                continue
            new = cost + c
            if new < cost_so_far.get(nxt, 1 << 30):
                cost_so_far[nxt] = new
                came[nxt] = (pos, step)
                heapq.heappush(frontier, (new + h(nxt), new, nxt))
        if len(cost_so_far) > max_nodes:
            break
    raise RouteError(f"no route from {start} to {goal} (searched {len(cost_so_far)} tiles, box {lo}..{hi})")


class RouteError(AssertionError):
    pass


# ---------------------------------------------------------------------------------------------- walking

def _stack_item(client, items, pos, server_ids):
    """(client id, stackpos) of the first item at pos with one of these server ids."""
    for stackpos, thing in enumerate(client.tiles.get(tuple(pos), [])):
        cid = getattr(thing, "client_id", None)
        if cid and items.by_client[cid].server_id in server_ids:
            return cid, stackpos
    return None, None


def _blocker(client, pos):
    for thing in client.tiles.get(tuple(pos), []):
        if isinstance(thing, int):
            c = client.creatures.get(thing)
            if c:
                return c
        if isinstance(thing, Creature):
            return thing
    return None


def _clear(client, pos, timeout=30):
    """Kill the monster standing on pos (the character is strong; players / NPCs are waited for)."""
    c = _blocker(client, pos)
    if c is None or c.id == client.player_id:
        return
    if 0x40000000 <= c.id < 0x80000000:              # monsters (Creature::idRange: players 0x10000000, NPCs 0x80000000)
        client.attack(c.id)
        client.wait_for(lambda: c.id in client.removed_creatures or _blocker(client, pos) is not c, timeout)
        client.attack(0)
    else:
        client.sleep(1)


def _walk_to(client, target, arrive, timeout=5.0):
    dx, dy = target[0] - client.pos[0], target[1] - client.pos[1]
    direction = DIRECTIONS[(dx, dy)]
    for _ in range(4):
        before = client.pos
        client.step(direction, timeout=timeout)
        if client.wait_for(lambda: client.pos == arrive, timeout=1.5):
            watch.pace()
            return True
        if client.pos != before:                     # moved, but not where the rules say: re-plan
            return False
        _clear(client, target)
    return False


AUTO_WALK_MAX = 100                                  # directions per request (the client sends at most 255)


def _plain_run(client, steps, start):
    """How many steps from `start` on are plain walking on the current floor - no floor change, no teleport,
    no door - and can go in one auto-walk. Watch mode walks tile by tile, at the pace a viewer can follow."""
    if watch.STEP_DELAY:
        return 0
    n, z = 0, client.pos[2]
    for step in steps[start:start + AUTO_WALK_MAX]:
        if step.kind != "walk" or step.arrive != step.target or step.target[2] != z:
            break
        n += 1
    return n


def _auto_walk(client, steps, per_step=0.25):
    """Send the run as one auto-walk and wait until the character stands on its last tile. Returns (True, None),
    or (False, tile): stopped short - something in the way (a monster on `tile` is killed), or off the path (a
    floor change the map does not know on `tile`: the walk is stopped at once, the caller avoids that tile)."""
    directions, at = [], client.pos
    for step in steps:
        directions.append(DIRECTIONS[(step.target[0] - at[0], step.target[1] - at[1])])
        at = step.target
    targets = [s.target for s in steps]
    start, end = client.pos, targets[-1]
    cancels = client.cancel_walks
    client.auto_walk(directions)
    last_move, last_pos, done = time.time(), client.pos, -1       # done: index of the last tile reached
    deadline = time.time() + 3 + per_step * len(steps)
    while time.time() < deadline:
        pos = client.pos
        if pos == end:
            return True, None
        if client.cancel_walks != cancels:                       # a step refused (something in the way): stop
            client.stop_auto_walk()                              # before the server skips it and walks on
            break
        if pos != last_pos:
            if pos not in targets and pos != start:              # off the path: stop right away
                client.stop_auto_walk()
                client.wait_for(lambda: client.pos == pos, timeout=0.3)
                jumped = pos[2] != last_pos[2] or max(abs(pos[0] - last_pos[0]), abs(pos[1] - last_pos[1])) > 1
                # another floor / a jump: a floor change the map does not know on the next tile; one tile aside:
                # the server skipped a step it refused (a creature in the way) and walked on - just re-plan
                return False, (targets[done + 1] if jumped else None)
            done = targets.index(pos) if pos in targets else done
            last_move, last_pos = time.time(), pos
        elif time.time() - last_move > 1.5:                      # stalled: blocked, or the walk was cancelled
            break
        time.sleep(0.02)
    return False, None


def _push_aside(client, items, world, pos, next_step=None):
    """Move the movable things blocking pos (a barrel, a crate) onto a free tile next to it - not where we stand,
    not the tile the route takes next - like a player pushing a barrel out of the doorway."""
    ids = set(world.info(pos).get("push", ()))
    avoid = {client.pos, tuple(pos)} | {s.target for s in (next_step or [])}     # the route ahead
    for _ in range(4):
        cid, stackpos = _stack_item(client, items, pos, ids)
        if cid is None:
            return True                                    # nothing (left) in the way
        # next to it first; in a one-tile passage there is no room beside it: throw it further (up to 3 tiles,
        # the server checks the throw), like a player clears a doorway
        spots = sorted(((pos[0] + dx, pos[1] + dy, pos[2]) for dx in range(-3, 4) for dy in range(-3, 4)),
                       key=lambda q: max(abs(q[0] - pos[0]), abs(q[1] - pos[1])))
        spots = [q for q in spots if q not in avoid and q != tuple(pos) and world.walkable(q)
                 and not _blocker(client, q)]
        before = len(client.tiles.get(tuple(pos), []))
        for spot in spots:
            client.move_item(tuple(pos), cid, stackpos, spot)
            if client.wait_for(lambda: len(client.tiles.get(tuple(pos), [])) < before, timeout=1.5):
                break
        else:
            return False
    return _stack_item(client, items, pos, ids)[0] is None


def _use(client, items, pos, server_ids, arrive=None, timeout=5.0):
    cid, stackpos = _stack_item(client, items, pos, server_ids)
    if cid is None:
        raise RouteError(f"nothing to use at {pos}: {client.tiles.get(tuple(pos))}")
    client.use_item(tuple(pos), cid, stackpos)
    if arrive:
        return client.wait_for(lambda: client.pos == arrive, timeout=timeout)
    return True


def _destroy_fields(client, items, pos):
    """Burn away the magic fields on pos with a carried destroy field rune (adito grav), like a player clearing a
    rope spot: rope.lua refuses a spot with a field on it ("You can not use this object.")."""
    for _ in range(3):
        field = next(((n, t) for n, t in enumerate(client.tiles.get(tuple(pos), [])) if getattr(t, "client_id", None)
                      and items.name(items.by_client[t.client_id].server_id).endswith(" field")), None)
        if field is None:
            return
        rune = carried(client, items, lambda n: n == "destroy field rune")
        if rune is None:
            raise RouteError(f"a field lies on {pos}, and the character has no destroy field rune to clear it")
        stackpos, thing = field
        client.use_item_with(*rune, tuple(pos), thing.client_id, stackpos)
        client.wait_for(lambda: len(client.tiles.get(tuple(pos), [])) <= stackpos
                        or client.tiles[tuple(pos)][stackpos] is not thing, timeout=2)
        client.sleep(1.1)                         # rune exhaustion


def _rope(client, items, spot, arrive, timeout=5.0):
    slot = next((s for s, i in client.inventory.items() if items.by_client[i.client_id].server_id == ROPE), None)
    if slot is not None:
        src, src_cid, src_stack = client.inventory_pos(slot), client.inventory[slot].client_id, 0
    else:
        found = next(((cid, n, i) for cid, c in client.containers.items() for n, i in enumerate(c.items)
                      if items.by_client[i.client_id].server_id == ROPE), None)
        if found is None:
            raise RouteError("the route needs a rope, and the character has none (worn or in an open container)")
        cid, n, i = found
        src, src_cid, src_stack = client.container_pos(cid, n), i.client_id, n
    if _blocker(client, spot):              # the rope only works on an empty spot (rope.lua): clear it first
        _clear(client, spot)
    clear_items(client, items, spot)          # corpses of what was just killed there, say
    _destroy_fields(client, items, spot)      # a field on the spot blocks the rope (rope.lua)
    ground = client.tiles.get(tuple(spot), [None])[0]
    client.use_item_with(src, src_cid, src_stack, tuple(spot), ground.client_id, 0)
    return client.wait_for(lambda: client.pos == arrive, timeout=timeout)


def follow(client, items, world: WorldMap, goal, *, replans=6, **ability):
    """Walk the character from where it stands to goal. `ability`: level, vocation, keys, storages, rope,
    open_tiles (became walkable), avoid (tiles not to step on). The map changes during quests - a hole
    opened with a pick, say: a step that lands somewhere the plan did not expect adds that tile to avoid."""
    goal = tuple(goal)
    ability = dict(ability)
    avoid = {tuple(t) for t in ability.pop("avoid", ())}
    last = None
    slow_start = 0
    interruptions = 60                                # auto-walks cut short by monsters: not a failed plan
    attempt = 0
    while attempt <= replans:
        attempt += 1
        interrupted = False
        steps = plan(world, client.pos, goal, avoid=avoid, **ability)
        i, slow = 0, slow_start
        slow_start = 3                               # after any re-plan: the first tiles one by one
        while i < len(steps):
            step = last = steps[i]
            i += 1
            run = _plain_run(client, steps, i - 1) if slow <= 0 else 0
            slow -= 1
            if run > 1:                              # several plain tiles on this floor: one auto-walk request
                ok, off_path = _auto_walk(client, steps[i - 1:i - 1 + run])
                i += run - 1
                last = steps[i - 1]
                if not ok:
                    if off_path is not None:
                        avoid.add(off_path)          # it took us to another floor: a hole the map does not know
                    elif interruptions > 0:
                        interruptions -= 1
                        interrupted = True
                    break                            # blocked or off the path: re-plan from here, and walk the
                continue                             # next tiles step by step (next attempt: slow)
            if step.kind == "walk":
                before = client.pos
                ok = _walk_to(client, step.target, step.arrive)
                if not ok and client.pos != step.target and client.pos[2] != step.target[2]:
                    avoid.add(step.target)           # it took us to another floor: a hole the map does not know
                elif not ok and client.pos == before and not _blocker(client, step.target):
                    avoid.add(step.target)           # refused with nobody on it: the map is wrong about this tile
            elif step.kind == "door":
                info = world.info(step.target)
                if _stack_item(client, items, step.target, {info["door_id"]})[0] is None:
                    pass                             # someone left it open (another player, an earlier test)
                elif info["door"] == "locked":
                    _unlock(client, items, step.target, info["door_id"])
                else:
                    _use(client, items, step.target, {info["door_id"]})
                client.sleep(0.3)                    # the door opens (becomes a different, open item)
                # a gate of expertise puts whoever opens it into the doorway itself
                ok = client.pos == step.target or _walk_to(client, step.target, step.target)
            elif step.kind == "ladder":
                ok = _use(client, items, step.target, {1386}, arrive=step.arrive)
            elif step.kind == "grate":
                ok = _use(client, items, step.target, {world.info(step.target).get("grate_id", 430)},
                          arrive=step.arrive)
            elif step.kind == "wheat":               # cut it with the scythe, then walk through
                use_tool(client, items, "scythe", step.target, {2739})
                client.sleep(0.4)
                ok = _walk_to(client, step.target, step.target)
            elif step.kind == "dig":                 # open the stone pile with the shovel, then step in
                use_tool(client, items, "shovel", step.target)
                client.sleep(0.4)
                ok = _walk_to(client, step.target, step.arrive)
            elif step.kind == "push":                # push the barrel aside, then walk on
                ok = (_push_aside(client, items, world, step.target, steps[i:i + 6])
                      and _walk_to(client, step.target, step.arrive))
            elif step.kind == "pick":                # break a hole into the mud with the pick, then step in
                use_tool(client, items, "pick", step.target)
                client.sleep(0.4)
                ok = _walk_to(client, step.target, step.arrive)
            else:
                ok = _rope(client, items, step.target, step.arrive)
            if not ok:
                break                                # re-plan from where we actually stand
        else:
            if client.pos == goal:
                return
        if client.pos == goal:
            return
        if interrupted:
            attempt -= 1                             # a monster in the way is no reason to give up
        time.sleep(0.2)
    tile = client.tiles.get(tuple(last.target), []) if last else []
    raise RouteError(f"could not reach {goal}: standing at {client.pos} after {replans} re-plans; last step "
                     f"{last}, the client sees there {tile}; messages {[t for _, t in client.text_messages[-4:]]}")


def _all_carried(client, items, matches):
    """Every carried item whose name matches: (position, client id, stackpos)."""
    out = [(client.inventory_pos(slot), item.client_id, 0) for slot, item in client.inventory.items()
           if matches(items.name(items.by_client[item.client_id].server_id))]
    for cid, container in client.containers.items():
        out += [(client.container_pos(cid, n), item.client_id, n) for n, item in enumerate(container.items)
                if matches(items.name(items.by_client[item.client_id].server_id))]
    return out


def _unlock(client, items, door, door_id):
    """Open a locked door with the right key: the client cannot see a key's number, so, like a player with a
    key ring, try each carried key until the door opens."""
    keys = _all_carried(client, items, lambda n: n.endswith(" key"))
    if not keys:
        raise RouteError(f"no key carried for the door at {door}")
    for source in keys:
        if _stack_item(client, items, door, {door_id})[0] is None:
            return
        cid, stackpos = _stack_item(client, items, door, {door_id})
        client.use_item_with(*source, tuple(door), cid, stackpos)
        client.wait_for(lambda: _stack_item(client, items, door, {door_id})[0] is None, timeout=1.2)
        client.sleep(0.2)


def carried(client, items, matches):
    """(position, client id, stackpos) of the first carried item whose name matches (worn, or in an open
    container) - the source of a "use with"."""
    for slot, item in client.inventory.items():
        if matches(items.name(items.by_client[item.client_id].server_id)):
            return client.inventory_pos(slot), item.client_id, 0
    for cid, container in client.containers.items():
        for n, item in enumerate(container.items):
            if matches(items.name(items.by_client[item.client_id].server_id)):
                return client.container_pos(cid, n), item.client_id, n
    return None


def use_tool(client, items, matches, pos, target_ids=None):
    """Use a carried item (pick, shovel, rope, key) on a map position, like "use with" in the client: on the
    item there with one of target_ids, or on the ground."""
    source = carried(client, items, matches if callable(matches) else (lambda n: n == matches))
    if source is None:
        raise RouteError(f"the character carries no {matches} (worn, or in an open container)")
    stack = client.tiles.get(tuple(pos), [])
    target_cid, target_stack = stack[0].client_id, 0
    if target_ids:
        for n, thing in enumerate(stack):
            cid = getattr(thing, "client_id", None)
            if cid and items.by_client[cid].server_id in target_ids:
                target_cid, target_stack = cid, n
    client.use_item_with(*source, tuple(pos), target_cid, target_stack)


def walk_next_to(client, items, world: WorldMap, target, **ability):
    """Walk to the closest walkable tile next to target (a chest, a switch, a door). A tile the server refuses
    (something on it the map does not show - a corpse, a creature) is given up for the next closest one."""
    target = tuple(target)
    open_tiles = {tuple(t) for t in ability.get("open_tiles", ())}
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            n = (target[0] + dx, target[1] + dy, target[2])
            if (dx or dy) and (world.walkable(n) or n in open_tiles) and not world.arrival(n):
                if client.pos == n:
                    return
                try:
                    candidates.append((len(plan(world, client.pos, n, **ability)), n))
                except RouteError:
                    continue
    if not candidates:
        raise RouteError(f"no reachable tile next to {target}")
    error = None
    for _, n in sorted(candidates):
        try:
            follow(client, items, world, n, **ability)
            return
        except RouteError as e:
            error = e
            if client.pos[2] == target[2] and max(abs(client.pos[0] - target[0]),
                                                  abs(client.pos[1] - target[1])) == 1:
                return                               # stopped on another tile next to it: good enough
    raise error


def clear_items(client, items, pos, tries=12):
    """Move the movable items (corpses, loot) off a tile, like a player dragging them aside: onto our own tile,
    else any tile around. Ground, always-on-top items (walls, ladders, pools) and creatures stay."""
    pos = tuple(pos)
    for _ in range(tries):
        stack = client.tiles.get(pos, [])
        movable = [(n, t) for n, t in enumerate(stack) if n > 0 and getattr(t, "client_id", None)
                   and not items.by_client[t.client_id].always_on_top
                   and items.by_client[t.client_id].flags & 64]            # items.otb FLAG_MOVEABLE
        if not movable:
            return
        n, thing = movable[0]
        before = len(stack)
        spots = [client.pos] + [(pos[0] + dx, pos[1] + dy, pos[2]) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                                if (dx or dy) and (pos[0] + dx, pos[1] + dy, pos[2]) != client.pos]
        for spot in spots:
            client.move_item(pos, thing.client_id, n, spot, max(getattr(thing, "count", 1), 1))
            if client.wait_for(lambda: len(client.tiles.get(pos, [])) < before, timeout=1.0):
                break


def walk_near(client, items, world: WorldMap, target, radius=2, **ability):
    """Walk to a reachable tile within `radius` of target, closest first - for NPCs, who are often talked to
    across a counter (the tiles next to them are the counter or their side of it)."""
    target = tuple(target)
    candidates = sorted(((max(abs(dx), abs(dy)), (target[0] + dx, target[1] + dy, target[2]))
                         for dx in range(-radius, radius + 1) for dy in range(-radius, radius + 1) if dx or dy))
    for _, n in candidates:
        if world.walkable(n) and not world.arrival(n):
            if client.pos == n:
                return
            try:
                plan(world, client.pos, n, **ability)
            except RouteError:
                continue
            follow(client, items, world, n, **ability)
            return
    raise RouteError(f"no reachable tile within {radius} of {target}")

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
                avoid=frozenset()):
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
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            t = (x + dx, y + dy, z)
            info = world.info(t)
            up = (t[0], t[1] + 1, z - 1)
            if info.get("ladder") and world.walkable(up):
                yield 2, Step("ladder", t, world.arrival(up) or up)
            if rope and info.get("rope") and t != pos and world.walkable(up):
                yield 2, Step("rope", t, world.arrival(up) or up)


def plan(world: WorldMap, start, goal, *, level=1, vocation=0, keys=(), storages=(), rope=False,
         open_tiles=(), avoid=(), margin=60, floors=4, max_nodes=2_000_000):
    """Cheapest list of Steps from start to goal (both tuples). Raises if there is none in the search box."""
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
        for c, step in _neighbours(world, pos, level, vocation, keys, storages, rope, open_tiles, avoid):
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
            return True
        if client.pos != before:                     # moved, but not where the rules say: re-plan
            return False
        _clear(client, target)
    return False


def _use(client, items, pos, server_ids, arrive=None, timeout=5.0):
    cid, stackpos = _stack_item(client, items, pos, server_ids)
    if cid is None:
        raise RouteError(f"nothing to use at {pos}: {client.tiles.get(tuple(pos))}")
    client.use_item(tuple(pos), cid, stackpos)
    if arrive:
        return client.wait_for(lambda: client.pos == arrive, timeout=timeout)
    return True


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
    for attempt in range(replans + 1):
        steps = plan(world, client.pos, goal, avoid=avoid, **ability)
        for step in steps:
            last = step
            if step.kind == "walk":
                ok = _walk_to(client, step.target, step.arrive)
                if not ok and client.pos != step.target and client.pos[2] != step.target[2]:
                    avoid.add(step.target)           # it took us to another floor: a hole the map does not know
            elif step.kind == "door":
                info = world.info(step.target)
                if info["door"] == "locked":
                    use_tool(client, items, lambda n: n.endswith(" key"), step.target, {info["door_id"]})
                else:
                    _use(client, items, step.target, {info["door_id"]})
                client.sleep(0.3)                    # the door opens (becomes a different, open item)
                ok = _walk_to(client, step.target, step.target)
            elif step.kind == "ladder":
                ok = _use(client, items, step.target, {1386}, arrive=step.arrive)
            else:
                ok = _rope(client, items, step.target, step.arrive)
            if not ok:
                break                                # re-plan from where we actually stand
        else:
            if client.pos == goal:
                return
        time.sleep(0.2)
    tile = client.tiles.get(tuple(last.target), []) if last else []
    raise RouteError(f"could not reach {goal}: standing at {client.pos} after {replans} re-plans; last step "
                     f"{last}, the client sees there {tile}; messages {[t for _, t in client.text_messages[-4:]]}")


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
    """Walk to the closest walkable tile next to target (a chest, a switch, a door)."""
    target = tuple(target)
    open_tiles = {tuple(t) for t in ability.get("open_tiles", ())}
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            n = (target[0] + dx, target[1] + dy, target[2])
            if (dx or dy) and (world.walkable(n) or n in open_tiles) and not world.arrival(n):
                if client.pos == n:
                    return
                try:
                    cost = len(plan(world, client.pos, n, **ability))
                except RouteError:
                    continue
                if best is None or cost < best[0]:
                    best = (cost, n)
    if best is None:
        raise RouteError(f"no reachable tile next to {target}")
    follow(client, items, world, best[1], **ability)

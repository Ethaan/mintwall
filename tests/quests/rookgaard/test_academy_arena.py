"""Rookgaard Academy training arena (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Rookgaard Academy training arena
# Not a quest - an Academy feature on the same floors (task.md). Four levers under the blackboards bug / wolf /
# troll / spider; each opens its monster's cage gate one floor down, and the sign says "You have to close the door
# before you can open a new one." (quests/rook_academy_arena.lua; gates as in tibiaot74). The way in is the
# Academy's locked door 4600: Seymour sells that key (Key to Adventure, 5 gp).

ARENA_LEVERS = {"bug": (32088, 32148, 9), "wolf": (32090, 32148, 9), "troll": (32092, 32148, 9),
                "spider": (32094, 32148, 9)}
FRAMEWORK_GATE = 1037


def _gate(lever):
    return (lever[0], lever[1] + 1, 10)


def test_academy_training_arena(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_near, walk_next_to
    from tibia74 import Item
    from tibia74.quest import npc_pos, talk_to
    p = strong(new_player, ROOKGAARD_TEMPLE, items=[Item(2148, 5)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_near(p, items, world_map, npc_pos("Seymour"), level=2000, vocation=4, rope=True)
    said = talk_to(p, "Seymour", "hi", "key", "yes")
    assert p.wait_for(lambda: carries(p, "silver key"), timeout=3), (said, p.inventory_names())
    ability = dict(level=2000, vocation=4, rope=True, keys={4600})
    wolf_lever, bug_lever = ARENA_LEVERS["wolf"], ARENA_LEVERS["bug"]
    gate = _gate(wolf_lever)
    shut = lambda pos: any(i.client_id == FRAMEWORK_GATE for i in p.tile_items(pos))   # noqa: E731

    walk_next_to(p, items, world_map, wolf_lever, **ability)
    use_map_item(p, items, wolf_lever, "switch")
    assert p.wait_for(lambda: gate in p.tiles and not shut(gate), timeout=3), (p.tiles.get(gate), p.text_messages[-2:])

    walk_next_to(p, items, world_map, bug_lever, **ability)
    use_map_item(p, items, bug_lever, "switch")
    assert p.wait_for(lambda: p.messages("Sorry, not possible."), timeout=3), p.text_messages[-2:]
    assert shut(_gate(bug_lever)), "a second gate opened while the wolf's was open"

    # down into the arena and fight the wolf through the open gate
    walk_near(p, items, world_map, (gate[0], gate[1] + 1, 10), radius=1, **ability)
    wolf = p.wait_for(lambda: next((c for c in p.creatures.values() if c.name.lower() == "wolf"), None), timeout=5)
    assert wolf, f"no wolf in view from {p.pos}: {list(p.creatures.values())} gate {p.tiles.get(gate)}"
    p.set_fight_modes(fight=1, chase=1, safe=1)
    p.attack(wolf.id)
    assert p.wait_for(lambda: wolf.id not in p.creatures or p.creatures[wolf.id].health == 0, timeout=20), wolf
    p.set_fight_modes(fight=1, chase=0, safe=1)

    # back up: pull the wolf lever again to shut its gate, then another gate may open
    walk_next_to(p, items, world_map, wolf_lever, **ability)
    use_map_item(p, items, wolf_lever, "switch")
    assert p.wait_for(lambda: shut(gate), timeout=3), (p.tiles.get(gate), p.text_messages[-2:])
    p.sleep(1.1)
    walk_next_to(p, items, world_map, bug_lever, **ability)
    use_map_item(p, items, bug_lever, "switch")
    assert p.wait_for(lambda: not shut(_gate(bug_lever)), timeout=3), p.text_messages[-2:]
    use_map_item(p, items, bug_lever, "switch")               # leave the arena as it was
    assert p.wait_for(lambda: shut(_gate(bug_lever)), timeout=3)

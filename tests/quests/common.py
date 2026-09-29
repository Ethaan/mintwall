"""Shared by the quest tests (tests/quests/<city>/test_<quest>.py): temples, item ids, helpers. Each quest file does
`from quests.common import *`. The playbook for a new quest is .claude/skills/quest-testing."""
import pytest  # noqa: F401

from tibia74.quest import (assert_level_door, assert_no_way, assert_way, carries, next_to, npc_pos,  # noqa: F401
                           step_onto, use_map_item)
from tibia74.server import TESTER_GROUP  # noqa: F401  monsters cannot attack testers

ROOKGAARD_TEMPLE = (32097, 32219, 7)
THAIS_TEMPLE = (32369, 32241, 7)
FIBULA_TEMPLE = (32176, 32437, 7)
EDRON_TEMPLE = (33217, 31814, 8)
CARLIN_TEMPLE = (32360, 31782, 7)
HAVOC_TEMPLE = (32783, 32243, 6)
ABDENDRIEL_TEMPLE = (32732, 31634, 7)
KAZORDOON_TEMPLE = (32649, 31925, 11)
VENORE_TEMPLE = (32957, 32076, 7)
DARASHIA_TEMPLE = (33213, 32454, 1)
ANKRAHMUN_TEMPLE = (33194, 32853, 8)

PICK = 2553
SHOVEL = SHOVEL_ID = 2554
SCYTHE = 2550
PLATINUM = 2152
RED_APPLE = 2674
MASTER_SORCERER_ID = 5
QUEST_BODY = 3058                  # the Rookgaard quest bodies with a reward (the rooms are full of others)

# Rookgaard spots more than one test uses
RAPIER_BOX = (32099, 32198, 9)       # Rookgaard sewer: box, unique id 2384 = the rapier
AMBER_CHEST = (32171, 32197, 7)      # Rookgaard east dock: chest, unique id 20001 holding Amber's notebook
BANANA_PALM = (32172, 32169, 7)


def edron_player(new_player, items=()):
    """A premium tester at the Edron temple with a pick, backpack open (Edron Hero Cave quests)."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    # a tester: monsters do not attack it (the parchment's demons would kill it while the test waits)
    p = strong(new_player, EDRON_TEMPLE, premium_days=30, items=[Item(PICK), *items], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def kazordoon_player(new_player, items=(), **kwargs):
    """A strong tester at the Kazordoon temple, backpack open (the Kazordoon quests)."""
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    p = strong(new_player, KAZORDOON_TEMPLE, items=list(items), group_id=TESTER_GROUP, **kwargs)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def venore_player(new_player, items=(), **kwargs):
    """A strong tester at the Venore temple, backpack open (the Venore quests)."""
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    p = strong(new_player, VENORE_TEMPLE, items=list(items), group_id=TESTER_GROUP, **kwargs)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def collect(p, items, world_map, spot, what, found, **ability):
    """Walk next to a quest container, use it and check its "You have found ..." messages (found: the texts after
    "You have found ", in any order); a second use says it is empty."""
    from tibia74.route import walk_next_to
    walk_next_to(p, items, world_map, spot, **ability)
    before = len(p.text_messages)
    use_map_item(p, items, spot, what)
    got = lambda: sorted(t[len("You have found "):].rstrip(".") for _, t in p.text_messages[before:]  # noqa: E731
                         if t.startswith("You have found"))
    assert p.wait_for(lambda: got() == sorted(f.rstrip(".") for f in found), timeout=3), (spot, got())
    p.sleep(1.1)


def bag_contents(p, items):
    """The names of what lies in the bags the character carries in its hands, ammo slot or open containers (quest
    rewards that come in a bag land wherever there is room): opens each one."""
    names = []
    sources = [(p.inventory_pos(slot), item.client_id, 0) for slot, item in p.inventory.items() if slot != 3]
    sources += [(p.container_pos(cid, n), item.client_id, n)
                for cid, c in list(p.containers.items()) for n, item in enumerate(c.items)]
    for pos, client_id, stackpos in sources:
        if not items.name(items.by_client[client_id].server_id).endswith("bag"):
            continue
        window = max(p.containers, default=-1) + 1
        p.use_item(pos, client_id, stackpos, window)
        assert p.wait_for(lambda: window in p.containers, timeout=3), f"the bag at {pos} did not open"
        names += [items.name(items.by_client[i.client_id].server_id) for i in p.containers[window].items]
    return names


def darashia_player(new_player, items=(), **kwargs):
    """A strong premium tester at the Darashia temple, backpack open (the Darashia quests; Darashia is premium)."""
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    kwargs.setdefault("premium_days", 30)
    p = strong(new_player, DARASHIA_TEMPLE, items=list(items), group_id=TESTER_GROUP, **kwargs)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def drop_on(p, items, item_id, pos):
    """Drop one of a carried item (from an open container) on a map tile within reach - a sacrifice on a basin, a
    skull on a stone, fruit on a counter."""
    client_id = items.by_server[item_id].client_id
    count = lambda: sum(1 for t in p.tiles.get(tuple(pos), []) if getattr(t, "client_id", None) == client_id)  # noqa: E731
    for cid, c in p.containers.items():
        for n, i in enumerate(c.items):
            if i.client_id == client_id:
                before = count()
                p.move_item(p.container_pos(cid, n), client_id, n, tuple(pos), 1)
                assert p.wait_for(lambda: count() > before, timeout=3), (pos, p.text_messages[-2:])
                return
    raise AssertionError(f"no {item_id} carried")


def ankrahmun_player(new_player, items=(), **kwargs):
    """A strong premium tester at the Ankrahmun temple, backpack open (the Ankrahmun quests; Ankrahmun is premium)."""
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    kwargs.setdefault("premium_days", 30)
    kwargs.setdefault("group_id", TESTER_GROUP)
    p = strong(new_player, ANKRAHMUN_TEMPLE, items=list(items), **kwargs)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p

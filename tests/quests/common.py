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

"""Goblin Temple Quest + Antidote Rune Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Goblin Temple + Antidote Rune (Rookgaard)
# docs/reference-74/quests.md: premium side, through the troll cave (shovel the pile of rocks), down past the
# goblins, up the stairs: two chests (50 gp, 5 small stones, sandals / pan, 4 snowballs, milk). The pan goes
# to Billy (hi, pan, yes) for an antidote rune (Antidote Rune Quest). Premium, no level, 1 player, once.

GOBLIN_CHESTS = {(31973, 32209, 12): ["sandals", "5 small stones", "50 gold coins"],
                 (31977, 32209, 12): ["a pan", "4 snowballs", "a vial of milk"]}


def test_goblin_temple_and_antidote_rune_quests(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import npc_pos, strong, talk_to
    from tibia74.route import walk_near, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE, premium_days=30, items=[Item(SHOVEL)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, shovel=True)
    for chest, rewards in GOBLIN_CHESTS.items():
        walk_next_to(p, items, world_map, chest, **ability)
        before = len(p.text_messages)
        use_map_item(p, items, chest, "chest")
        for reward in rewards:
            assert p.wait_for(lambda: any(f"You have found {reward}." in t for _, t in p.text_messages[before:]),
                              timeout=3), (reward, [t for _, t in p.text_messages[before:]])
        p.sleep(1.1)
    use_map_item(p, items, next(iter(GOBLIN_CHESTS)), "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

    walk_near(p, items, world_map, npc_pos("Billy"), **ability)
    said = talk_to(p, "Billy", "hi", "pan", "yes")
    assert p.wait_for(lambda: carries(p, "antidote rune"), timeout=3), (said, p.inventory_names())

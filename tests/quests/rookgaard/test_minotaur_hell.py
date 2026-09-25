"""Minotaur Hell Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Minotaur Hell Quest (Rookgaard)
# docs/reference-74/quests.md "Minotaur Hell Quest"; TibiaWiki spoiler. The main cave north of town, down to
# the minotaur room; three boxes just west of the stairs. No level, 1 player (group advised), free, once.
# Rewards: carlin sword, 4 poison arrows + 10 arrows, fishing rod.

MINOTAUR_HELL_BOXES = {(32124, 32064, 12): ["a carlin sword"], (32127, 32065, 12): ["4 poison arrows", "10 arrows"],
                       (32130, 32066, 12): ["a fishing rod"]}


def test_minotaur_hell_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    for box, rewards in MINOTAUR_HELL_BOXES.items():
        walk_next_to(p, items, world_map, box, level=2000, vocation=4, rope=True)
        before = len(p.text_messages)
        use_map_item(p, items, box, "box")
        for reward in rewards:
            assert p.wait_for(lambda: any(f"You have found {reward}." in t for _, t in p.text_messages[before:]),
                              timeout=3), (reward, [t for _, t in p.text_messages[before:]])
        p.sleep(1.1)
    use_map_item(p, items, next(iter(MINOTAUR_HELL_BOXES)), "box")
    assert p.wait_for(lambda: p.messages("The box is empty."), timeout=3), p.text_messages[-2:]

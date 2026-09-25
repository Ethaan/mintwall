"""Captain Iglues Treasure Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Captain Iglues Treasure Quest
# docs/reference-74/quests.md "Captain Iglues Treasure Quest"; TibiaWiki spoiler (2006) + current page.
# Goal: the quest chest below the poison spider tower. Level: none. 1 player, free, once. Needs a rope.
# Reward: 2 salmon (the right chest; the left one refills daily with the letter and 12 salmon). Optional:
# a salmon for Amber (Academy basement) buys a word of orcish ("salmon", "yes").

IGLUE_CHEST = (32039, 32121, 13)              # unique id 52171


def test_captain_iglues_treasure_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong, talk_to
    from tibia74.route import walk_near, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)

    walk_next_to(p, items, world_map, IGLUE_CHEST, **ability)
    use_map_item(p, items, IGLUE_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found 2 salmon."), timeout=3), p.text_messages[-3:]
    p.sleep(1.1)
    use_map_item(p, items, IGLUE_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

    walk_near(p, items, world_map, npc_pos("Amber"), **ability)
    said = talk_to(p, "Amber", "hi", "salmon", "yes")
    assert any("Orcs call arrows 'pixo'." in r for r in said), said

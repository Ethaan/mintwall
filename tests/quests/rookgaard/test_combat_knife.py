"""Combat Knife Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Combat Knife Quest (Rookgaard)
# docs/reference-74/quests.md: the box in the main sewer (drain in town), guarded by rats. No level, 1 player,
# free, once. Reward: a combat knife (the box's unique id 2404 is the knife).

COMBAT_KNIFE_BOX = (32102, 32235, 8)


def test_combat_knife_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, COMBAT_KNIFE_BOX, level=2000, vocation=4, rope=True)
    use_map_item(p, items, COMBAT_KNIFE_BOX, "chest")
    assert p.wait_for(lambda: p.messages("You have found a combat knife."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "combat knife"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, COMBAT_KNIFE_BOX, "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

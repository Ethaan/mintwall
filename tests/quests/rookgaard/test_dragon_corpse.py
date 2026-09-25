"""Dragon Corpse Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Dragon Corpse Quest (Rookgaard)
# docs/reference-74/quests.md "Dragon Corpse Quest"; TibiaWiki spoiler. Bear cave east of town: a shovel opens
# the stone pile, a scythe cuts the wheat, run across the fire fields to the dead dragon. No level, 1 player,
# free, once. Reward: a bag with a copper shield and a legion helmet.

DEAD_DRAGON = (32179, 32224, 9)
SHOVEL, SCYTHE = 2554, 2550


def test_dragon_corpse_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import open_carried, strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE, items=[Item(SHOVEL), Item(SCYTHE)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, DEAD_DRAGON, level=2000, vocation=4, rope=True, scythe=True, shovel=True)
    use_map_item(p, items, DEAD_DRAGON, "dead dragon")
    assert p.wait_for(lambda: p.messages("You have found a bag."), timeout=3), p.text_messages[-3:]
    bag = open_carried(p, items, "bag")
    assert sorted(i.name for i in bag.items) == ["copper shield", "legion helmet"], bag.items
    p.sleep(1.1)
    use_map_item(p, items, DEAD_DRAGON, "dead dragon")
    assert p.wait_for(lambda: p.messages("The dead dragon is empty."), timeout=3), p.text_messages[-2:]

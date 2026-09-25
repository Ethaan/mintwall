"""Small Axe Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Small Axe Quest (Rookgaard premium)
# docs/reference-74/quests.md "Small Axe Quest": the right-hand coffin of the pair in the premium skeleton cave
# (TibiaWiki; tibiaot74's map: uid 7026 on the coffin at 31984,32246,10); the way down is dug open with a shovel.
# Premium, no level, once (Tibiantis quest id). Reward: a small axe (unique id 2559).

SMALL_AXE_COFFIN = (31984, 32246, 10)


def test_small_axe_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    from tibia74 import Item
    p = strong(new_player, ROOKGAARD_TEMPLE, premium_days=30, items=[Item(SHOVEL)])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, SMALL_AXE_COFFIN, level=2000, vocation=4, rope=True, shovel=True)
    use_map_item(p, items, SMALL_AXE_COFFIN, "wooden coffin")
    assert p.wait_for(lambda: p.messages("You have found a small axe."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "small axe"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, SMALL_AXE_COFFIN, "wooden coffin")
    assert p.wait_for(lambda: p.messages("The wooden coffin is empty."), timeout=3), p.text_messages[-2:]

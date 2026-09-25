"""Pick Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Pick Quest (Rookgaard)
# docs/reference-74/quests.md "Small Axe Quest / Pick Quest": a small axe - once from the coffin in the premium
# skeleton cave (below), or from spots that respawn daily: the box in the orc cave (-2) and a body in the Katana
# cave - goes to Al Dee (hi, pick, yes) for a pick (needed for the Bear Room). Free, no level.

ORC_CAVE_BOX = (32080, 32121, 10)             # not a quest box: its small axe and arrow come back every day


def test_pick_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import open_map_container, strong, take, talk_to
    from tibia74.route import walk_near, walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    walk_next_to(p, items, world_map, ORC_CAVE_BOX, **ability)
    box = open_map_container(p, items, ORC_CAVE_BOX, "box")
    take(p, items, box, "small axe")
    walk_near(p, items, world_map, npc_pos("Al Dee"), **ability)
    said = talk_to(p, "Al Dee", "hi", "pick", "yes")
    assert p.wait_for(lambda: carries(p, "pick"), timeout=3), (said, p.inventory_names())
    assert not carries(p, "small axe"), "Al Dee kept no small axe"

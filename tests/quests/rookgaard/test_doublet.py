"""Doublet Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Doublet Quest (Rookgaard)
# docs/reference-74/quests.md "Doublet Quest"; TibiaWiki Doublet Quest/Spoiler: in the cellar under the stable
# north of Tom's shop, "use the ground (Loose Board) directly west of the sewer grate". 7.4 has no loose-board
# item: the board is the wooden flooring itself (tibiaot74's map: uid 7014 on it), with a barrel standing on it -
# push the barrel aside, then use the floor. No level, 1 player, free, once. Reward: a doublet (unique id 2485).

LOOSE_BOARD = (32084, 32181, 8)


def test_doublet_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, LOOSE_BOARD, level=2000, vocation=4, rope=True)
    use_map_item(p, items, LOOSE_BOARD, "wooden flooring")     # moves the barrel off first
    assert p.wait_for(lambda: p.messages("You have found a doublet."), timeout=3), (p.text_messages[-3:], p.pos, p.tiles.get(LOOSE_BOARD))
    assert p.wait_for(lambda: carries(p, "doublet"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, LOOSE_BOARD, "wooden flooring")
    assert p.wait_for(lambda: p.messages("The wooden flooring is empty."), timeout=3), p.text_messages[-2:]

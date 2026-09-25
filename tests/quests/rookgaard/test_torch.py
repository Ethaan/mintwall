"""Torch Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Torch Quest (Rookgaard Academy)
# docs/reference-74/quests.md "Torch Quest"; TibiaWiki Torch Quest/Spoiler (removed in 2011, so in 7.4). Basement:
# north through two doors to a wall with a lever; the lever opens the wall; two more doors, a rat, the chest.
# No level, 1 player, free, once. Reward: a torch (the chest's unique id 2050).

ACADEMY_LEVER = (32093, 32174, 8)
ACADEMY_WALL = (32095, 32173, 8)
TORCH_CHEST = (32092, 32162, 8)


def test_torch_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)

    walk_next_to(p, items, world_map, ACADEMY_LEVER, **ability)
    use_map_item(p, items, ACADEMY_LEVER, "switch")
    assert p.wait_for(lambda: len(p.tiles.get(ACADEMY_WALL, [])) == 1, timeout=3), \
        f"the wall is still there: {p.tiles.get(ACADEMY_WALL)} {p.text_messages[-2:]}"
    walk_next_to(p, items, world_map, TORCH_CHEST, open_tiles={ACADEMY_WALL}, **ability)
    use_map_item(p, items, TORCH_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found a torch."), timeout=3), p.text_messages[-3:]
    p.sleep(1.1)
    use_map_item(p, items, TORCH_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]

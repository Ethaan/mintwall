"""Triple UH Rune Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki pre-8.0: down the Edron Hero Cave (holes, stairs, the dragons' hole, two more stairs) to "the last floor"
# (current wiki: 5 monks), "Rewards are in the box". Rope. No level. The box was missing on our map: placed at
# 33136,31601,15; real-map table uid 1015 = 5 mana fluids and an ultimate healing rune with 3 charges (TibiaWiki 2006
# too) - quests/system.lua.
TRIPLE_UH = dict(box=(33136, 31601, 15), beside=(33137, 31601, 15))


def test_triple_uh_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    p = edron_player(new_player)
    ability = dict(level=1, rope=True)
    walk_next_to(p, items, world_map, TRIPLE_UH["box"], **ability)
    use_map_item(p, items, TRIPLE_UH["box"], "box")
    assert p.wait_for(lambda: p.messages("You have found an ultimate healing rune."), timeout=3), p.text_messages[-7:]
    assert len(p.messages("You have found a vial of manafluid.")) == 5, p.text_messages[-7:]
    # 7.4 sends no charges for a rune (it is not stackable): the look text tells them
    cid, n = next((cid, n) for cid, c in p.containers.items() for n, i in enumerate(c.items)
                  if i.name == "ultimate healing rune")
    p.look(p.container_pos(cid, n), p.containers[cid].items[n].client_id, n)
    assert p.wait_for(lambda: p.messages('"adura vita"-spell (3x)'), timeout=3), p.text_messages[-2:]
    assert sum(1 for i in p.all_items() if i.name == "vial") == 5, p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, TRIPLE_UH["box"], "box")
    assert p.wait_for(lambda: p.messages("The box is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, EDRON_TEMPLE, **ability)


def test_triple_uh_rules(world_map):
    assert_way(world_map, EDRON_TEMPLE, TRIPLE_UH["beside"], level=1)                 # no level
    assert_way(world_map, TRIPLE_UH["beside"], EDRON_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, TRIPLE_UH["beside"], EDRON_TEMPLE, level=1)               # out needs a rope

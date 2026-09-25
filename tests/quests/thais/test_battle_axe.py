"""Battle Axe Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Battle Axe Quest (Thais sewers)
# docs/reference-74/quests.md "Battle Axe Quest"; TibiaWiki 2006: rope + pick; in the south-west of the sewers
# "use the pick where indicated, and go down the hole [...] You will find the Battle Axe in a dead Skeleton";
# current wiki: 4 cave rats. The dead skeleton was missing on our map: placed where tibiaot74 has it, with the
# real-map table's unique id 1658 (= battle axe). No level, free, 1 player, once. The rope spot below is the way out.
BATTLE_AXE = dict(pick_spot=(32302, 32257, 8), skeleton=(32305, 32254, 9), below=(32303, 32257, 9))


def test_battle_axe_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(PICK)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, pick=True)
    walk_next_to(p, items, world_map, BATTLE_AXE["skeleton"], **ability)     # down the sewer grate, pick, hole
    use_map_item(p, items, BATTLE_AXE["skeleton"], "dead skeleton")
    assert p.wait_for(lambda: p.messages("You have found a battle axe."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "battle axe"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, BATTLE_AXE["skeleton"], "dead skeleton")
    assert p.wait_for(lambda: p.messages("The dead skeleton is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)                    # out: rope up, the sewer ladder


def test_battle_axe_rules(world_map):
    # a pick is needed to get in, a rope to get out
    assert_no_way(world_map, THAIS_TEMPLE, BATTLE_AXE["below"], level=1, rope=True)
    assert_way(world_map, THAIS_TEMPLE, BATTLE_AXE["below"], level=1, rope=True, pick=True)
    assert_way(world_map, BATTLE_AXE["below"], THAIS_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, BATTLE_AXE["below"], THAIS_TEMPLE, level=1)

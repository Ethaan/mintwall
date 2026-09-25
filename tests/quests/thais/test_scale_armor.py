"""Scale Armor Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Scale Armor Quest (near the Ancient Temple)
# docs/reference-74/quests.md "Scale Armor Quest"; TibiaWiki (2005/2006): shovel the hole west of the Ancient Temple
# entrance, north and east to a room with a well, "use the lower-right corner of the well to go down", open the
# chests. Real-map table: "[10061] = {{2483,1}}, -- scale armor -- near AT"; our map already had the scale armor in
# the chest - now a quest chest (once per character); the well had no script (action id 54545 now). The chest next
# to it (piece of iron, a book - pre-8.0 lists them too) stays an ordinary chest: no real-map table entry. Free.
SCALE_ARMOR = dict(chest=(32357, 32130, 9), well=(32354, 32131, 8), beside=(32356, 32130, 9))


def test_scale_armor_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    p = strong(new_player, THAIS_TEMPLE, items=[Item(SHOVEL_ID)], group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True, shovel=True)
    walk_next_to(p, items, world_map, SCALE_ARMOR["chest"], **ability)     # the hole, the well down
    use_map_item(p, items, SCALE_ARMOR["chest"], "chest")
    assert p.wait_for(lambda: p.messages("You have found a scale armor."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "scale armor"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, SCALE_ARMOR["chest"], "chest")
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)                    # out: the ladder, a rope up


def test_scale_armor_rules(world_map):
    # the chest room is below the well: in by the well; out by the ladder under it, and on up the cave's other
    # ladder (32347,32123,8) - no rope needed
    assert_way(world_map, THAIS_TEMPLE, SCALE_ARMOR["beside"], level=1, rope=True, shovel=True)
    assert_way(world_map, SCALE_ARMOR["beside"], THAIS_TEMPLE, level=1)

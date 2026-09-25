"""Six Rubies Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (2006): through the Ancient Temple to the dragons' fire island, "Destroy Field the fire covering a hole
# [...] Use the hole; you do not go down it. It gives the reward." The small hole under a fire field is on our map
# (32370,32265,12). 6 small rubies (TibiaWiki, Tibiantis; the real-map table's 2 is outvoted). Rope. Free, once.
SIX_RUBIES = dict(hole=(32370, 32265, 12), beside=(32370, 32264, 12))
DESTROY_FIELD, FIRE_FIELD = 2261, 1487


def test_six_rubies_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import carried, follow, walk_next_to
    S = SIX_RUBIES
    p = strong(new_player, THAIS_TEMPLE, items=[Item(DESTROY_FIELD, 3)], maglevel=10, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    ability = dict(level=2000, vocation=4, rope=True)
    walk_next_to(p, items, world_map, S["hole"], **ability)
    fire = lambda: next(((n, t) for n, t in enumerate(p.tiles.get(S["hole"], []))           # noqa: E731
                         if getattr(t, "client_id", None) == FIRE_FIELD), None)
    assert p.wait_for(fire, timeout=3), p.tiles.get(S["hole"])
    stackpos, field = fire()
    p.use_item_with(*carried(p, items, lambda n: n == "destroy field rune"), S["hole"], field.client_id, stackpos)
    assert p.wait_for(lambda: not fire(), timeout=3), (p.tiles.get(S["hole"]), p.text_messages[-2:])
    p.sleep(1.1)
    use_map_item(p, items, S["hole"], "small hole")
    assert p.wait_for(lambda: p.messages("You have found 6 small rubies."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "small ruby"), timeout=3), p.inventory_names()
    p.sleep(1.1)
    use_map_item(p, items, S["hole"], "small hole")
    assert p.wait_for(lambda: p.messages("The small hole is empty."), timeout=3), p.text_messages[-2:]
    follow(p, items, world_map, THAIS_TEMPLE, **ability)


def test_six_rubies_rules(world_map):
    assert_way(world_map, THAIS_TEMPLE, SIX_RUBIES["beside"], level=1)
    assert_way(world_map, SIX_RUBIES["beside"], THAIS_TEMPLE, level=1, rope=True)
    assert_no_way(world_map, SIX_RUBIES["beside"], THAIS_TEMPLE, level=1)                     # a rope out

"""Small Ruby Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (current; no 7.x page): up to the Mintwallin throne room, into the pit, down the hole (dragons), "Destroy
# Field or browse the fire field at the north of the room": 1 small ruby, a daily respawn - not a quest box. Our map
# has it: the small ruby under a fire field at 32437,32174,15 (a map item, back at every server start). Free.
SMALL_RUBY = dict(ruby=(32437, 32174, 15))
DESTROY_FIELD, FIRE_FIELD, RUBY = 2261, 1487, 2147


def test_small_ruby_quest(new_player, items, world_map):
    from tibia74 import BACKPACK, Item
    from tibia74.quest import strong
    from tibia74.route import carried, walk_next_to
    pos = SMALL_RUBY["ruby"]
    p = strong(new_player, THAIS_TEMPLE, items=[Item(DESTROY_FIELD, 3), Item(SHOVEL)], maglevel=10,
               group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    walk_next_to(p, items, world_map, pos, level=2000, vocation=4, rope=True, shovel=True)
    on_tile = lambda cid: next(((n, t) for n, t in enumerate(p.tiles.get(pos, []))       # noqa: E731
                                if getattr(t, "client_id", None) == cid), None)
    assert p.wait_for(lambda: on_tile(FIRE_FIELD) and on_tile(RUBY), timeout=3), p.tiles.get(pos)
    stackpos, field = on_tile(FIRE_FIELD)
    p.use_item_with(*carried(p, items, lambda n: n == "destroy field rune"), pos, field.client_id, stackpos)
    assert p.wait_for(lambda: not on_tile(FIRE_FIELD), timeout=3), (p.tiles.get(pos), p.text_messages[-2:])
    stackpos, ruby = on_tile(RUBY)
    backpack = next(cid for cid, c in p.containers.items() if c.item_id == p.inventory[BACKPACK].client_id)
    p.move_item(pos, ruby.client_id, stackpos, p.container_pos(backpack, 0), 1)
    assert p.wait_for(lambda: carries(p, "small ruby"), timeout=3), (p.inventory_names(), p.text_messages[-2:])
    assert not on_tile(RUBY), "the ruby is still there"


def test_small_ruby_rules(world_map):
    beside = (SMALL_RUBY["ruby"][0], SMALL_RUBY["ruby"][1] + 1, 15)
    assert_way(world_map, THAIS_TEMPLE, beside, level=1, rope=True, shovel=True)
    assert_way(world_map, beside, THAIS_TEMPLE, level=1, rope=True, shovel=True)

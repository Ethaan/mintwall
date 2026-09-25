"""Demon Helmet Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403
from quests.edron.test_parchment_room import parchment_room


LOST_SOULS_SWITCHES = [(33190, 31629, 13), (33191, 31629, 13)]
LOST_SOULS_GATE = {(33210, 31630, 13), (33211, 31630, 13), (33212, 31630, 13)}
DEMON_HELMET = dict(switch=(33330, 31591, 15), stone=(33314, 31592, 15), portal_out=(33316, 31591, 15),
                    out=(33328, 31592, 14),
                    boxes={(33313, 31591, 15): "demon helmet", (33313, 31592, 15): "demon shield",
                           (33313, 31593, 15): "steel boots"})
STONE_WALL = 1050


def test_demon_helmet_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    D = DEMON_HELMET
    hero = edron_player(new_player)
    ability = dict(level=2000, vocation=4, rope=True, pick=True)
    parchment_room(hero, items, world_map, ability)          # key 6010, now in the open bag

    # through the level-100 gate and the key door, to the Gate of the Lost Souls
    gate_ability = dict(ability, keys={6010})
    walk_next_to(hero, items, world_map, (33211, 31631, 13), **gate_ability)
    wall = lambda p, pos: any(i.client_id == STONE_WALL for i in p.tile_items(pos))  # noqa: E731
    assert all(wall(hero, g) for g in LOST_SOULS_GATE), [hero.tiles.get(g) for g in LOST_SOULS_GATE]

    # two friends hold the switches: the gate opens only while both stand there
    helpers = []
    for switch in LOST_SOULS_SWITCHES:
        h = edron_player(new_player)
        follow(h, items, world_map, switch, level=2000, vocation=4, rope=True)
        helpers.append(h)
    assert hero.wait_for(lambda: not any(wall(hero, g) for g in LOST_SOULS_GATE), timeout=3), \
        [hero.tiles.get(g) for g in LOST_SOULS_GATE]
    follow(hero, items, world_map, (33211, 31629, 13), open_tiles=LOST_SOULS_GATE, **gate_ability)
    # one friend steps off his switch (onto a free tile beside it): the gate closes behind the hero
    from tibia74.route import DIRECTIONS
    sx, sy, sz = LOST_SOULS_SWITCHES[0]
    sides = [d for (dx, dy), d in DIRECTIONS.items() if world_map.walkable((sx + dx, sy + dy, sz))
             and (sx + dx, sy + dy, sz) not in LOST_SOULS_SWITCHES]
    assert any(helpers[0].step(d) for d in sides), f"the helper could not step off {helpers[0].pos}"
    assert hero.wait_for(lambda: all(wall(hero, g) for g in LOST_SOULS_GATE), timeout=3), \
        [hero.tiles.get(g) for g in LOST_SOULS_GATE]

    # down to the quest room; the east switch opens the boxes and the way out
    follow(hero, items, world_map, (33324, 31592, 15), **gate_ability)
    walk_next_to(hero, items, world_map, D["switch"], **gate_ability)
    use_map_item(hero, items, D["switch"], "switch")
    # the boxes are at the other end of the room, out of view from the switch: go over, then look
    walk_next_to(hero, items, world_map, D["portal_out"], **gate_ability)
    assert hero.wait_for(lambda: not any(i.client_id == 1355 for i in hero.tile_items(D["stone"])), timeout=3), \
        (hero.tiles.get(D["stone"]), hero.pos, hero.text_messages[-3:])
    assert hero.wait_for(lambda: any(i.client_id == 1387 for i in hero.tile_items(D["portal_out"])), timeout=3)
    for box, reward in D["boxes"].items():
        walk_next_to(hero, items, world_map, box, open_tiles={D["stone"]}, **gate_ability)
        use_map_item(hero, items, box, "chest")
        found = f"You have found {'' if reward.endswith('s') else 'a '}{reward}."   # "steel boots": no article
        assert hero.wait_for(lambda: hero.messages(found), timeout=3), hero.text_messages[-3:]
        hero.sleep(1.1)
    use_map_item(hero, items, next(iter(D["boxes"])), "chest")
    assert hero.wait_for(lambda: hero.messages("The chest is empty."), timeout=3), hero.text_messages[-2:]
    for reward in D["boxes"].values():
        assert carries(hero, reward), (reward, hero.inventory_names())

    # out through the portal the switch opened
    walk_next_to(hero, items, world_map, D["portal_out"], open_tiles={D["stone"]}, **gate_ability)
    step_onto(hero, D["portal_out"])
    assert hero.wait_for(lambda: hero.pos == D["out"], timeout=3), hero.pos


DEMON_HELMET_GATE = (33211, 31638, 13)          # gate of expertise, level 100 (action id 1100)
DEMON_HELMET_GATE_OUTSIDE = (33211, 31639, 13)


def test_demon_helmet_level_door(new_player, items):
    """Level 99 is refused at the gate of expertise; level 100 passes."""
    assert_level_door(new_player, items, DEMON_HELMET_GATE, DEMON_HELMET_GATE_OUTSIDE, 100)


def test_demon_helmet_rules(world_map):
    ability = dict(level=2000, vocation=4, rope=True, pick=True)
    past_key_door = (33211, 31633, 13)
    # without key 6010 (Parchment Room) no way past the door after the gate; with it, as far as the Lost Souls
    assert_no_way(world_map, EDRON_TEMPLE, past_key_door, **ability)
    assert_way(world_map, EDRON_TEMPLE, past_key_door, keys={6010}, **ability)
    # level 99: not even with the key
    assert_no_way(world_map, EDRON_TEMPLE, past_key_door, **dict(ability, level=99), keys={6010})
    # the Gate of the Lost Souls is a wall until two players hold its switches
    assert_no_way(world_map, EDRON_TEMPLE, DEMON_HELMET["out"], keys={6010}, **ability)
    assert_way(world_map, EDRON_TEMPLE, DEMON_HELMET["out"], keys={6010}, open_tiles=LOST_SOULS_GATE, **ability)
    # the quest room has no way out until its switch opens the portal
    assert_no_way(world_map, (33324, 31592, 15), EDRON_TEMPLE, keys={6010}, open_tiles=LOST_SOULS_GATE, **ability)

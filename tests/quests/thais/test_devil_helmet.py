"""Devil Helmet Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki (2006): at least 2 players - one "goes down the ladder, a bit west, up a hole, and south to a blocked
# passage. Standing on the open square opens a grate"; the others "go down the grate", through the level-30 gate, and
# Key 3610 (Mintwallin Cyclops Quest) opens the laboratory: Devil Helmet, Halberd, 4 Small Sapphires (real-map table
# [3613], one container). The switch tile (32468,32119,14) was on our map; the grate opened for anyone (now only while
# the switch is held, movements/mintwallin_grate_switch.lua), the lab doors had no key number, the lab no container.
DEVIL_HELMET = dict(switch=(32468, 32119, 14), grate=(32482, 32170, 14), by_grate=(32482, 32169, 14),
                    gate=(32479, 32174, 15), gate_outside=(32480, 32174, 15), box=(32459, 32144, 15),
                    lab=(32460, 32145, 15))
HOLE, DIRT = 383, 351


def _key_3610():
    from tibia74 import Item
    return Item(2088, attributes=bytes([4]) + (3610).to_bytes(2, "little"))      # silver key, ATTR_ACTION_ID 3610


def test_devil_helmet_quest(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import follow, walk_next_to
    D = DEVIL_HELMET
    ability = dict(level=2000, vocation=4, rope=True)
    hero = strong(new_player, THAIS_TEMPLE, items=[_key_3610()], group_id=TESTER_GROUP)
    hero.open_container(BACKPACK)
    hero.set_fight_modes(fight=1, chase=0, safe=1)
    follow(hero, items, world_map, D["by_grate"], **ability)
    ground = lambda: hero.tiles.get(D["grate"], [None])[0]                                 # noqa: E731
    assert getattr(ground(), "client_id", None) == DIRT, hero.tiles.get(D["grate"])
    use_map_item(hero, items, D["grate"], "sewer grate")                                    # shut
    assert hero.wait_for(lambda: hero.messages("Sorry, not possible."), timeout=3), hero.text_messages[-2:]

    # the friend holds the open square far away: the grate opens
    friend = strong(new_player, THAIS_TEMPLE, group_id=TESTER_GROUP)
    friend.open_container(BACKPACK)
    follow(friend, items, world_map, D["switch"], **ability)
    assert hero.wait_for(lambda: getattr(ground(), "client_id", None) == HOLE, timeout=3), hero.tiles.get(D["grate"])
    step_onto(hero, D["grate"])
    assert hero.wait_for(lambda: hero.pos[2] == 15, timeout=3), hero.pos

    # the level-30 gate, key 3610, the laboratory
    walk_next_to(hero, items, world_map, D["box"], keys={3610}, **ability)
    before = len(hero.text_messages)
    use_map_item(hero, items, D["box"], "box")
    found = lambda: sorted(t for _, t in hero.text_messages[before:] if t.startswith("You have found"))  # noqa: E731
    assert hero.wait_for(lambda: found() == ["You have found 4 small sapphires.", "You have found a devil helmet.",
                                             "You have found a halberd."], timeout=3), found()
    hero.sleep(1.1)
    use_map_item(hero, items, D["box"], "box")
    assert hero.wait_for(lambda: hero.messages("The box is empty."), timeout=3), hero.text_messages[-2:]

    friend.step(2)                                              # off the switch: the grate shuts again
    follow(hero, items, world_map, THAIS_TEMPLE, keys={3610}, **ability)


def test_devil_helmet_level_door(new_player, items):
    assert_level_door(new_player, items, DEVIL_HELMET["gate"], DEVIL_HELMET["gate_outside"], 30)


def test_devil_helmet_rules(world_map):
    ability = dict(level=2000, vocation=4, rope=True)
    below = (DEVIL_HELMET["grate"][0], DEVIL_HELMET["grate"][1] + 1, 15)
    # alone there is no way down: the grate opens only for a friend on the switch
    assert_no_way(world_map, THAIS_TEMPLE, DEVIL_HELMET["lab"], keys={3610}, **ability)
    assert_way(world_map, THAIS_TEMPLE, DEVIL_HELMET["switch"], **ability)
    assert_way(world_map, below, DEVIL_HELMET["lab"], keys={3610}, **ability)
    assert_no_way(world_map, below, DEVIL_HELMET["lab"], **ability)                          # key 3610
    assert_no_way(world_map, below, DEVIL_HELMET["lab"], keys={3610}, **dict(ability, level=29))
    assert_way(world_map, DEVIL_HELMET["lab"], THAIS_TEMPLE, keys={3610}, **ability)

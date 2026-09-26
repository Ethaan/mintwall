"""Plains of Havoc quests (docs/reference-74/quests.md): Giant Smithhammer, Iron Helmet, Power Bolts, Isle of the Mists,
Ornamented Shield. Decided with the user 2026-09-25: the Smithhammer's west chest gives it all; the Iron Helmet body the
union of the 7.x sources; the Isle of the Mists 3 emeralds, druids only; the Ornamented Shield both parts."""
from quests.common import *  # noqa: F401,F403

DESTROY_FIELD = 2261
DRUID = 2


def _hero(new_player, items=(), **kwargs):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    p = strong(new_player, HAVOC_TEMPLE, items=list(items), group_id=TESTER_GROUP, **kwargs)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def _found(p, before):
    return sorted(t for _, t in p.text_messages[before:] if t.startswith("You have found"))


def _open(p, items, world_map, pos, what, expected, **ability):
    from tibia74.route import walk_next_to
    walk_next_to(p, items, world_map, pos, **ability)
    before = len(p.text_messages)
    use_map_item(p, items, pos, what)
    assert p.wait_for(lambda: _found(p, before) == sorted(expected), timeout=3), _found(p, before)
    p.sleep(1.1)
    use_map_item(p, items, pos, what)                                     # once per character
    assert p.wait_for(lambda: p.messages(f"The {what} is empty."), timeout=3), p.text_messages[-2:]
    p.sleep(1.1)


# "Go down the stairs in the north structure ... The quest box is located in the room directly to the south" (2006)
def test_giant_smithhammer_quest(new_player, items, world_map):
    from tibia74.route import follow
    p = _hero(new_player)
    _open(p, items, world_map, (32775, 32253, 8), "chest",
          ["You have found a giant smithhammer.", "You have found a talon.", "You have found 100 gold coins."], level=1)
    follow(p, items, world_map, HAVOC_TEMPLE, level=1)


# "a dead body partially obscured by a tree" just west of the camp (2006)
def test_iron_helmet_quest(new_player, items, world_map):
    from tibia74.quest import open_carried
    p = _hero(new_player)
    _open(p, items, world_map, (32769, 32225, 7), "dead human", ["You have found a backpack."], level=1)
    bag = open_carried(p, items, "backpack")
    want = ["iron helmet", "sudden death rune", "leather armor", "stamped letter", "worn leather boots", "longsword"]
    assert p.wait_for(lambda: sorted(i.name for i in bag.items) == sorted(want), timeout=3), bag.items


# "Go into the hole just south of the Plains of Havoc Temple ... The reward is in a dead body" (2006)
def test_power_bolts_quest(new_player, items, world_map):
    from tibia74.route import follow
    p = _hero(new_player)
    ability = dict(level=1, rope=True, shovel=True)
    _open(p, items, world_map, (32818, 32284, 8), "dead human",
          ["You have found a bag.", "You have found a two handed sword."], **ability)
    follow(p, items, world_map, HAVOC_TEMPLE, **ability)


# the portal near the orcs, the box on the ground floor of the isle's building; druids only
def test_isle_of_the_mists_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    portal, isle = (32831, 32294, 7), (32851, 32339, 6)
    knight = _hero(new_player)
    walk_next_to(knight, items, world_map, portal, level=1)
    before = knight.pos
    from tibia74.route import DIRECTIONS
    knight.step(DIRECTIONS[(portal[0] - knight.pos[0], portal[1] - knight.pos[1])])
    knight.sleep(1)
    assert knight.pos == before, f"a knight got through to {knight.pos}"
    knight.logout()
    druid = _hero(new_player, vocation=DRUID)
    walk_next_to(druid, items, world_map, portal, level=1)
    step_onto(druid, portal)
    assert druid.wait_for(lambda: druid.pos == isle, timeout=3), druid.pos
    _open(druid, items, world_map, (32852, 32332, 7), "box", ["You have found 3 small emeralds."], level=1)
    follow(druid, items, world_map, HAVOC_TEMPLE, level=1)                   # the isle's portal back


def test_ornamented_shield_quest(new_player, items, world_map):
    """Part 1: down the lair, the pick hole, Krendorak's body under the fire; part 2: a partner holds the stalagmites
    away, the red bag, and up the rope near the Necromant House."""
    from tibia74 import Item
    from tibia74.quest import next_to, open_carried
    from tibia74.route import _destroy_fields, follow, walk_next_to
    p = _hero(new_player, items=[Item(PICK), Item(SHOVEL), Item(DESTROY_FIELD, 3)], maglevel=10)
    ability = dict(level=2000, rope=True, pick=True, shovel=True)
    body = (32778, 32282, 11)
    walk_next_to(p, items, world_map, body, **ability)                    # the hidden hole, the lair, the pick hole
    _destroy_fields(p, items, body)
    before = len(p.text_messages)
    use_map_item(p, items, body, "dead human")
    want = ["You have found a bag.", "You have found an ornamented shield.", "You have found a steel helmet."]
    assert p.wait_for(lambda: _found(p, before) == sorted(want), timeout=3), _found(p, before)
    bag = open_carried(p, items, "bag")
    assert p.wait_for(lambda: sorted(i.name for i in bag.items) ==
                      sorted(["crystal key", "spike sword", "dragon necklace", "might ring", "book"]), timeout=3), bag.items

    # part 2
    stalagmites, plate = (32771, 32297, 10), (32770, 32282, 10)
    follow(p, items, world_map, (32771, 32295, 10), **ability)            # rope back up, south to the stalagmites
    assert any(i.client_id == items.by_server[387].client_id for i in p.tile_items(stalagmites)), p.tiles.get(stalagmites)
    partner = next_to(new_player, plate, group_id=TESTER_GROUP, storage={30001: 1})
    step_onto(partner, plate)
    assert p.wait_for(lambda: not any(i.client_id == items.by_server[387].client_id for i in p.tile_items(stalagmites)),
                      timeout=3), p.tiles.get(stalagmites)
    before = len(p.text_messages)
    chest = (32771, 32299, 10)
    walk_next_to(p, items, world_map, chest, open_tiles=[stalagmites], **ability)
    use_map_item(p, items, chest, "chest")
    assert p.wait_for(lambda: _found(p, before) == ["You have found a red bag."], timeout=3), _found(p, before)
    p.sleep(1.1)
    follow(p, items, world_map, HAVOC_TEMPLE, open_tiles=[stalagmites], **ability)   # the rope hole near the chest


def test_havoc_rules(world_map):
    ability = dict(level=100, rope=True, pick=True, shovel=True)
    body_side = (32777, 32283, 11)
    assert_way(world_map, HAVOC_TEMPLE, body_side, **ability)
    assert_no_way(world_map, HAVOC_TEMPLE, body_side, **dict(ability, pick=False))       # the pick hole
    assert_way(world_map, body_side, HAVOC_TEMPLE, **ability)                              # rope back up
    chest_side = (32771, 32298, 10)
    assert_no_way(world_map, HAVOC_TEMPLE, chest_side, **ability)                          # the stalagmites
    assert_way(world_map, HAVOC_TEMPLE, chest_side, open_tiles=[(32771, 32297, 10)], **ability)

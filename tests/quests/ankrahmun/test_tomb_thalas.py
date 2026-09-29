"""The Ancient Tombs Quest: Thalas's tomb, the Stone Tomb (docs/reference-74/quests.md)."""
from tibia74 import BACKPACK
from quests.ankrahmun.tombs import *  # noqa: F401,F403

# Current wiki: "Everyone must step on the switch to get poisoned, after getting poisoned say hi to the Cobra NPC to the
# south (he will respond with 'Begone! Hissssss! You bear not the mark of the cobra!' if you are not fast enough) to get
# teleported to a room with Thalas"; Thalas drops the cobrafang dagger. Our map: the floor-14 corridor ends in a
# forcefield that pointed one tile back, the Cobra's corridor behind it had no way in, the Cobra was spawned as a
# monster, no switches. Now (decided with the user 2026-09-28): poisoned, the forcefield leads into the Cobra's
# corridor, and the Cobra (an NPC again) sends a poisoned player to Thalas; the corridor's north end still has the
# level-75 gate and the forcefield to Thalas.
T = THALAS
STUB = (33399, 32802, 14)
BEFORE_STUB = (33399, 32801, 14)
CORRIDOR = (33367, 32853, 14)
COBRA = (33366, 32855, 14)
GATE = (33368, 32807, 14)
THALAS_ROOM = (33397, 32835, 14)
POISON_FIELD_RUNE = 2285
POISONED = 1                              # the client's condition icons


def _poison_yourself(p, items):
    """A poison field rune on your own tile: poisoned."""
    from tibia74.route import use_tool
    use_tool(p, items, "poison field rune", p.pos)
    assert p.wait_for(lambda: p.icons & POISONED, timeout=3), ("not poisoned", p.text_messages[-2:])


def _tester_at(new_player, pos):
    from tibia74 import Item
    from tibia74.quest import strong
    p = strong(new_player, pos, premium_days=30, maglevel=100, group_id=TESTER_GROUP, items=[*[Item(HMM, 100)] * 3])
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def test_thalas_tomb(new_player, items, world_map):
    """From the temple to the corridor's forcefield as a tester (monsters leave it alone); testers cannot be poisoned,
    so a normal character takes it through the forcefield and to the Cobra; in Thalas's room a tester again."""
    from tibia74 import Item
    from tibia74.quest import strong, talk_to
    from tibia74.route import follow
    p = tomb_player(new_player)
    ability = dict(level=2000, shovel=True, rope=True, floors=12)
    follow(p, items, world_map, T.flame, **ability)
    sacrifice_coin(p, items, T)
    follow(p, items, world_map, (BEFORE_STUB[0] + 2, BEFORE_STUB[1] - 1, 14), **ability)   # aside: the next one
    p.logout()                                                                        # walks up to the forcefield

    p = strong(new_player, BEFORE_STUB, premium_days=30, maglevel=100,
               items=[Item(POISON_FIELD_RUNE, 3), *[Item(HMM, 100)] * 3])
    p.open_container(BACKPACK)
    follow(p, items, world_map, BEFORE_STUB, **ability)
    _poison_yourself(p, items)
    step_onto(p, STUB)
    assert p.wait_for(lambda: p.pos == CORRIDOR, timeout=3), p.pos
    said = talk_to(p, "Cobra", "hi")
    assert p.wait_for(lambda: p.pos == THALAS_ROOM, timeout=3), (p.pos, said)
    assert any("Venture the path of decay" in s for s in said), said
    p.logout()

    # the fight, the pass and the sarcophagus as a tester again (Thalas's throwers would stall a normal character)
    p = _tester_at(new_player, THALAS_ROOM)

    body = kill_pharaoh(p, items, world_map, T, **ability)
    loot(p, items, body, T.pass_item)
    follow(p, items, world_map, (T.portal[0], T.portal[1] - 1, T.portal[2]), **ability)
    step_onto(p, T.portal)
    assert p.wait_for(lambda: p.pos == T.room, timeout=3), p.pos
    assert not carries(p, T.pass_item), "the portal takes the cobrafang dagger"
    collect(p, items, world_map, T.sarcophagus, "sarcophagus", [T.piece], level=2000)
    assert carries(p, "gem holder"), p.inventory_names()


def test_thalas_cobra_turns_away_the_unpoisoned(new_player):
    from tibia74.quest import strong, talk_to
    p = strong(new_player, CORRIDOR, premium_days=30, group_id=TESTER_GROUP)
    said = talk_to(p, "Cobra", "hi")
    assert any("You bear not the mark of the cobra" in s for s in said), said
    p.sleep(1)
    assert p.pos != THALAS_ROOM, p.pos


def test_thalas_forcefield_needs_poison(new_player, items):
    from tibia74 import Item
    from tibia74.quest import strong
    p = strong(new_player, BEFORE_STUB, premium_days=30, maglevel=100, items=[Item(POISON_FIELD_RUNE, 3)])
    p.open_container(BACKPACK)
    from tibia74.route import DIRECTIONS
    p.step(DIRECTIONS[(0, 1)])                                   # not poisoned: straight back
    p.sleep(1)
    assert p.pos == BEFORE_STUB, p.pos
    _poison_yourself(p, items)
    step_onto(p, STUB)
    assert p.wait_for(lambda: p.pos == CORRIDOR, timeout=3), p.pos


def test_thalas_rules(new_player, items, world_map):
    assert_level_door(new_player, items, GATE, (GATE[0], GATE[1] + 1, 14), 75)
    # the Cobra's corridor has no way in but the forcefield (poisoned); from it, the gate's way to Thalas
    assert_no_way(world_map, T.below, CORRIDOR, level=2000, rope=True, floors=12)
    assert_way(world_map, CORRIDOR, THALAS_ROOM, level=2000)
    assert_no_way(world_map, THALAS_ROOM, T.room, level=2000)
    assert_way(world_map, T.room, T.back, level=2000)

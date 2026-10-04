"""Plate Armor Quest (the Ghost Ship) (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005: Captain Fearless's passengers from Venore to Darashia are "randomly hijacked" by the Ghost Ship (one
# trip in ten here; decided with the user); below deck "Use the head of the coffin against the far wall": a plate armor;
# the ship's forcefield takes you on to Darashia (decided with the user; our map sent you back to Venore). Nothing sent
# players to the ship, the coffin had no quest id.
ARRIVAL, COFFIN, EXIT = (33319, 32172, 6), (33327, 32180, 8), (33328, 32181, 6)
DARASHIA_DOCK = (33290, 32480, 7)   # where the boats land (npc/lib/captain.lua); 33290,32481 has a wooden pillar


def test_ghost_ship_plate_armor(new_player, items, world_map):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    from tibia74.route import walk_next_to
    p = strong(new_player, ARRIVAL, premium_days=30, group_id=TESTER_GROUP)
    p.open_container(BACKPACK)
    collect(p, items, world_map, COFFIN, "wooden coffin", ["a plate armor"], level=2000, rope=True)
    assert carries(p, "plate armor"), p.inventory_names()
    walk_next_to(p, items, world_map, EXIT, level=2000, rope=True)
    step_onto(p, EXIT)
    assert p.wait_for(lambda: p.pos == DARASHIA_DOCK, timeout=3), p.pos


def test_captain_fearless_sometimes_sails_into_the_ghost_ship(new_player):
    """Venore to Darashia, again and again: one trip in ten ends on the Ghost Ship's deck (a GM calls the passenger
    back to Venore after each ordinary trip). Sixty trips miss it only once in ~500 runs."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import next_to, npc_pos
    captain = npc_pos("Captain Fearless")
    p = next_to(new_player, captain, level=50, premium_days=30, group_id=TESTER_GROUP, storage={30001: 1},
                inventory={BACKPACK: Item(1988, contents=[Item(2160, 1)])})             # 10k: many fares
    home = p.pos
    gm = next_to(new_player, home, group_id=3, storage={30001: 1})
    for trip in range(60):
        p.say("bye")                                            # the shortcut only works when he is not talking to us
        p.sleep(0.6)
        p.say("bring me to darashia")
        assert p.wait_for(lambda: p.pos[2] != home[2] or max(abs(p.pos[0] - home[0]), abs(p.pos[1] - home[1])) > 5,
                          timeout=3), (trip, p.pos, p.text_messages[-2:])
        if p.pos == ARRIVAL:
            return
        assert p.pos == DARASHIA_DOCK, p.pos
        gm.say("/c " + p.name)
        assert p.wait_for(lambda: p.pos[2] == gm.pos[2] and max(abs(p.pos[0] - gm.pos[0]), abs(p.pos[1] - gm.pos[1])) <= 1,
                          timeout=3), p.pos
        p.sleep(0.3)
    raise AssertionError("sixty trips to Darashia and never the Ghost Ship")

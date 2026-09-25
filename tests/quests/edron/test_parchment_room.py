"""Parchment Room Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# Parchment Room Quest: docs/reference-74/quests.md. In the Hero Cave a pick opens a hole in the mud (33094,31626,13)
# down to the gravestone and the teleporter into the Parchment Room; the coffin lies under the seal "Buried forever
# [...] Don't remove this seal or bad things may happen." - moving it calls 4 demons. The coffin (uid 10057, real-map
# table): a bag with the golden key 6010, a bone, a stealth ring, 2 talons and a skull. No level, premium, once.
PARCHMENT_COFFIN = (33063, 31624, 15)
PARCHMENT_SEAL = 1953
PARCHMENT_DEMONS = [(33060, 31623, 15), (33066, 31623, 15), (33060, 31627, 15), (33066, 31627, 15)]


def parchment_room(p, items, world_map, ability):
    from tibia74.quest import open_carried
    from tibia74.route import walk_next_to
    walk_next_to(p, items, world_map, PARCHMENT_COFFIN, **ability)
    seal_on = lambda: any(i.client_id == PARCHMENT_SEAL for i in p.tile_items(PARCHMENT_COFFIN))  # noqa: E731
    sealed = seal_on()
    if sealed:
        use_map_item(p, items, PARCHMENT_COFFIN, "wooden coffin")  # sealed: it does not open
        assert p.wait_for(lambda: p.messages("Sorry, not possible."), timeout=3), p.text_messages[-2:]
        stackpos = next(n for n, t in enumerate(p.tiles[PARCHMENT_COFFIN])
                        if getattr(t, "client_id", None) == PARCHMENT_SEAL)
        p.move_item(PARCHMENT_COFFIN, PARCHMENT_SEAL, stackpos, p.pos)   # take the seal off, onto our own tile
        assert p.wait_for(lambda: not seal_on(), timeout=3), p.tiles.get(PARCHMENT_COFFIN)
        p.sleep(1.1)
    use_map_item(p, items, PARCHMENT_COFFIN, "wooden coffin")
    assert p.wait_for(lambda: p.messages("You have found a bag."), timeout=3), p.text_messages[-3:]
    bag = open_carried(p, items, "bag")
    assert p.wait_for(lambda: sorted(i.name for i in bag.items) ==
                      sorted(["golden key", "bone", "stealth ring", "talon", "skull"]), timeout=3), bag.items
    return sealed


def test_parchment_room_quest(new_player, items, world_map):
    p = edron_player(new_player)
    ability = dict(level=2000, vocation=4, rope=True, pick=True)
    assert parchment_room(p, items, world_map, ability), "the seal was not on the coffin"
    # the 4 called demons (they walk off their spots at once; the room has a demon of its own too)
    demons = lambda: [c for c in p.creatures.values() if c.name.lower() == "demon" and c.pos  # noqa: E731
                      and c.pos[2] == 15 and 33055 <= c.pos[0] <= 33071 and 31618 <= c.pos[1] <= 31632]
    assert p.wait_for(lambda: len(demons()) >= 4, timeout=3), [c for c in p.creatures.values() if c.pos and c.pos[2] >= 14]
    p.sleep(1.1)
    use_map_item(p, items, PARCHMENT_COFFIN, "wooden coffin")
    assert p.wait_for(lambda: p.messages("The wooden coffin is empty."), timeout=3), p.text_messages[-2:]
    # a minute later a new seal lies on the coffin for the next group
    assert p.wait_for(lambda: any(i.client_id == PARCHMENT_SEAL for i in p.tile_items(PARCHMENT_COFFIN)),
                      timeout=70), p.tiles.get(PARCHMENT_COFFIN)


# Demon Helmet Quest: docs/reference-74/quests.md. Level 100 gate, then the door that key 6010 (Parchment Room)
# opens, then the Gate of the Lost Souls, open only while two players stand on its switches (33190/33191,31629,13);
# past fire, a portal, a hole two floors down, and the portal into the quest room. There the east switch takes the
# stone away from the boxes (demon helmet, demon shield, steel boots) and opens the portal out. Premium, level 100.
def test_parchment_room_rules(world_map):
    ability = dict(level=1, vocation=0, rope=True)
    # the way in needs a pick (the mud hole) - and there is a way back out (grate, rope up the pick hole)
    assert_no_way(world_map, EDRON_TEMPLE, PARCHMENT_COFFIN, **ability)
    inside = (33064, 31624, 15)
    assert_way(world_map, EDRON_TEMPLE, inside, pick=True, **ability)
    assert_way(world_map, inside, EDRON_TEMPLE, **ability)

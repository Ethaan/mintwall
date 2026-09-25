"""Annihilator Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- Annihilator Quest (Edron Hero Cave)
# docs/reference-74/quests.md "Annihilator Quest"; TibiaWiki 2005: four level-100 players line up on the squares,
# the front one pulls the lever, all four land in a room with six demons ("two north, two south and two dead ahead
# blocking the door"); past the door "You can only enter this door once, so choose your reward wisely": demon
# armor, magic sword, stonecutter axe, a present (the annihilation bear, 2006). Out through the portal.
# quests/annihilator_lever.lua (once per server save, "Sorry, not possible." for a wrong team - decided with the
# user), the chests share storage 51012 (quests/system.lua). This run: four master sorcerers and Ultimate Explosion.
ANNI = dict(lever=(33226, 31671, 13), squares=[(33225, 31671, 13), (33224, 31671, 13), (33223, 31671, 13),
                                                (33222, 31671, 13)],
            gate=(33214, 31671, 13), gate_outside=(33213, 31671, 13),
            arrival=[(33222, 31659, 13), (33221, 31659, 13), (33220, 31659, 13), (33219, 31659, 13)],
            room=(33218, 33225, 31655, 31662), portal=(33236, 31659, 13), out=(33210, 31673, 13),
            chests=[((33227, 31656, 13), "a demon armor", "demon armor"),
                    ((33229, 31656, 13), "a magic sword", "magic sword"),
                    ((33231, 31656, 13), "a stonecutter axe", "stonecutter axe"),
                    ((33233, 31656, 13), "a present", "present")])
MASTER_SORCERER_ID = 5


def _anni_player(new_player, **kwargs):
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    p = strong(new_player, EDRON_TEMPLE, vocation=MASTER_SORCERER_ID, maglevel=100, premium_days=30,
               group_id=TESTER_GROUP, **kwargs)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def test_annihilator_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    ability = dict(level=2000, vocation=MASTER_SORCERER_ID, rope=True)
    pulled = lambda p: any(i.client_id == 1945 for i in p.tile_items(ANNI["lever"]))   # noqa: E731

    # the team gathers; the lever refuses a team of three and a team with someone who already has a reward
    team = []
    for square in ANNI["squares"][:3]:
        p = _anni_player(new_player)
        follow(p, items, world_map, square, **ability)
        team.append(p)
    front = team[0]
    use_map_item(front, items, ANNI["lever"], "switch")
    assert front.wait_for(lambda: front.messages("Sorry, not possible."), timeout=3), front.text_messages[-2:]
    veteran = _anni_player(new_player, storage={51012: 1})
    follow(veteran, items, world_map, ANNI["squares"][3], **ability)
    front.sleep(1.1)
    before = len(front.messages("Sorry, not possible."))
    use_map_item(front, items, ANNI["lever"], "switch")
    assert front.wait_for(lambda: len(front.messages("Sorry, not possible.")) > before, timeout=3), \
        front.text_messages[-2:]
    veteran.logout()
    fourth = _anni_player(new_player)
    follow(fourth, items, world_map, ANNI["squares"][3], **ability)
    team.append(fourth)

    # the pull: all four in the demon room, six demons
    front.sleep(1.1)
    use_map_item(front, items, ANNI["lever"], "switch")
    for p, arrival in zip(team, ANNI["arrival"]):
        assert p.wait_for(lambda: p.pos == arrival, timeout=3), f"{p.name} is at {p.pos}, not {arrival}"
    x1, x2, y1, y2 = ANNI["room"]
    demons = lambda: [c for c in front.creatures.values() if c.name.lower() == "demon" and c.pos  # noqa: E731
                      and c.id not in front.removed_creatures and x1 <= c.pos[0] <= x2 and y1 <= c.pos[1] <= y2
                      and c.pos[2] == 13]
    assert front.wait_for(lambda: len(demons()) == 6, timeout=3), demons()

    # four master sorcerers, Ultimate Explosion until no demon is left
    for _ in range(30):
        if not demons():
            break
        for p in team:
            p.say("exevo gran mas vis")
        front.sleep(2.1)                                      # the spell exhaustion
    assert not demons(), f"demons left: {demons()}"

    # through the door, one at a time (the row in front of the chests is one tile wide): each takes one reward -
    # the first also tries a second chest: empty - and leaves through the portal
    for n, (p, (chest, found, name)) in enumerate(zip(team, ANNI["chests"])):
        walk_next_to(p, items, world_map, chest, **ability)
        use_map_item(p, items, chest, "chest")
        assert p.wait_for(lambda: p.messages(f"You have found {found}."), timeout=3), (p.name, p.text_messages[-3:])
        assert p.wait_for(lambda: carries(p, name), timeout=3), p.inventory_names()
        if n == 0:
            p.sleep(1.1)
            walk_next_to(p, items, world_map, ANNI["chests"][1][0], **ability)
            use_map_item(p, items, ANNI["chests"][1][0], "chest")
            assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
        walk_next_to(p, items, world_map, ANNI["portal"], **ability)
        step_onto(p, ANNI["portal"])
        assert p.wait_for(lambda: p.pos == ANNI["out"], timeout=3), f"{p.name} is at {p.pos}"
        p.logout()

    # once per server save: the pulled lever refuses the next team
    late = _anni_player(new_player)
    walk_next_to(late, items, world_map, ANNI["lever"], **ability)
    assert late.wait_for(lambda: pulled(late), timeout=3), late.tiles.get(ANNI["lever"])
    use_map_item(late, items, ANNI["lever"], "switch")
    assert late.wait_for(lambda: late.messages("Sorry, not possible."), timeout=3), late.text_messages[-2:]


def test_annihilator_level_door(new_player, items):
    """The level-100 gate in front of the lever: level 99 is refused, level 100 passes."""
    assert_level_door(new_player, items, ANNI["gate"], ANNI["gate_outside"], 100)


def test_annihilator_rules(world_map):
    ability = dict(vocation=MASTER_SORCERER_ID, rope=True)
    assert_no_way(world_map, EDRON_TEMPLE, ANNI["squares"][0], level=99, **ability)
    assert_way(world_map, EDRON_TEMPLE, ANNI["squares"][0], level=100, **ability)
    # the demon room is reached only by the lever; from there the door, the chests and the portal lead out
    assert_no_way(world_map, EDRON_TEMPLE, ANNI["arrival"][0], level=2000, **ability)
    assert_way(world_map, ANNI["arrival"][0], EDRON_TEMPLE, level=100, **ability)

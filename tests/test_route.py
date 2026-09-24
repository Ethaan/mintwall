"""The route framework quests use (tibia74/worldmap.py, tibia74/route.py): plan on the real map, then walk it."""
from tibia74 import BACKPACK
from tibia74.quest import carries, strong, use_map_item
from tibia74.route import follow, plan

ROOKGAARD_TEMPLE = (32097, 32219, 7)
RAPIER_BOX = (32099, 32198, 9)
NEXT_TO_BOX = (32099, 32199, 9)


def test_a_route_goes_down_into_the_rookgaard_sewers(world_map):
    steps = plan(world_map, ROOKGAARD_TEMPLE, NEXT_TO_BOX, level=2000)
    floors = [s.arrive[2] for s in steps]
    assert floors[-1] == 9 and 8 in floors, floors


def test_walking_from_the_temple_to_a_quest_box_and_back(new_player, items, world_map):
    p = strong(new_player, ROOKGAARD_TEMPLE)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    follow(p, items, world_map, NEXT_TO_BOX, level=2000, vocation=4, rope=True)
    assert p.pos == NEXT_TO_BOX
    use_map_item(p, items, RAPIER_BOX, "box")
    assert p.wait_for(lambda: carries(p, "rapier"), timeout=3),         (p.pos, [t for _, t in p.text_messages if "rat" not in t][-10:], p.inventory_names(),
         p.tiles.get(RAPIER_BOX))
    follow(p, items, world_map, ROOKGAARD_TEMPLE, level=2000, vocation=4, rope=True)
    assert p.pos == ROOKGAARD_TEMPLE


def test_no_teleport_lands_on_another_teleport(world_map):
    """The engine teleports again on arrival, so a field whose destination is another field sends you on (or back).
    The Rookgaard Academy's arena field (32089,32171,9) went to the field beside it and bounced every player back
    out; its destination is now past that field, as on tibiaot74's map (tools/map-set-attrs.py --teleport)."""
    teleports = {pos: tuple(info["teleport"]) for pos, info in world_map.special.items() if "teleport" in info}
    assert len(teleports) > 100
    onto = {src: dst for src, dst in teleports.items() if dst in teleports}
    assert not onto, onto

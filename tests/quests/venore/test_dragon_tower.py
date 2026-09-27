"""Dragon Tower Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2005/2006: up Shadowthorn's dragon tower, "two boxes near the top of the tower" - the real-map table's split
# (decided with the user): 2 small sapphires, 30 burst arrows, 60 poison arrows, 100 gp; a bow, a mana fluid and a life
# fluid. Our map had the two boxes without quest ids.
def test_dragon_tower_quest(new_player, items, world_map):
    from tibia74 import Item
    p = venore_player(new_player, items=[Item(2420)])
    ability = dict(level=2000, rope=True, machete=True)
    collect(p, items, world_map, (33072, 32169, 2), "box",
            ["2 small sapphires", "30 burst arrows", "60 poison arrows", "100 gold coins"], **ability)
    collect(p, items, world_map, (33079, 32169, 2), "box",
            ["a bow", "a vial of manafluid", "a vial of lifefluid"], **ability)
    assert carries(p, "bow") and carries(p, "burst arrow"), p.inventory_names()

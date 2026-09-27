"""Blood Herb Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki 2006: in Greenclaw Swamp "the dead tree by the water" gives the blood herb (Wyda's trade for her
# witchesbroom is not scripted yet). Our map had the tree without a quest id.
def test_blood_herb_quest(new_player, items, world_map):
    from tibia74 import Item
    p = venore_player(new_player, items=[Item(SHOVEL), Item(2420)])
    collect(p, items, world_map, (32769, 31968, 7), "dead tree", ["a blood herb"],
            level=2000, rope=True, shovel=True, machete=True)
    assert carries(p, "blood herb"), p.inventory_names()


def test_wyda_trades_the_blood_herb_for_her_witchesbroom(new_player):
    """TibiaWiki 2006: "She needs a Blood Herb for her potions and is willing to offer her Witchesbroom for it"."""
    from tibia74 import BACKPACK, Item
    from tibia74.quest import next_to, talk_to
    p = next_to(new_player, npc_pos("Wyda"), storage={30001: 1}, group_id=TESTER_GROUP,
                inventory={BACKPACK: Item(1988, contents=[Item(2798)])})
    p.open_container(BACKPACK)
    said = talk_to(p, "Wyda", "hi", "blood herb", "yes")
    assert any("witchesbroom" in s for s in said), said
    assert p.wait_for(lambda: carries(p, "witchesbroom"), timeout=3), p.inventory_names()
    assert not carries(p, "blood herb"), p.inventory_names()

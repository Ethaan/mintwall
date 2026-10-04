"""Quest chests in general (action id 2000, quests/system.lua) (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# ----------------------------------------------------------------------------- quest chests (action id 2000)

RAPIER_BOX = (32099, 32198, 9)       # Rookgaard sewer: box, unique id 2384 = the rapier
AMBER_CHEST = (32171, 32197, 7)      # Rookgaard east dock: chest, unique id 20001 holding Amber's notebook


def test_a_quest_chest_gives_its_reward_once_per_player(new_player, items):
    p = next_to(new_player, RAPIER_BOX, level=5, group_id=TESTER_GROUP, storage={30001: 1})
    p.open_container(3)                              # the backpack, so the rapier shows up there
    use_map_item(p, items, RAPIER_BOX, "box")
    assert p.wait_for(lambda: p.messages("You have found a rapier."), timeout=3), p.text_messages[-3:]
    assert p.wait_for(lambda: carries(p, "rapier"), timeout=3), p.inventory_names()
    p.sleep(1.1)                                     # the use delay
    use_map_item(p, items, RAPIER_BOX, "box")
    assert p.wait_for(lambda: p.messages("is empty"), timeout=3), p.text_messages[-3:]

    other = next_to(new_player, RAPIER_BOX, level=5, group_id=TESTER_GROUP, storage={30001: 1})
    use_map_item(other, items, RAPIER_BOX, "box")
    assert other.wait_for(lambda: other.messages("You have found a rapier."), timeout=3), \
        f"the second player got nothing: {other.text_messages[-3:]}"


def test_a_quest_chest_gives_what_lies_inside(new_player, items):
    """Unique id 20001 is no item id: the reward is the chest's contents (Amber's notebook)."""
    p = next_to(new_player, AMBER_CHEST, level=5, group_id=TESTER_GROUP, storage={30001: 1})
    use_map_item(p, items, AMBER_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found"), timeout=3), p.text_messages[-3:]
    found = p.messages("You have found")[0]
    assert "book" in found or "notebook" in found, found


# ----------------------------------------------------------------------------- a reward too heavy to carry
# Cip's words (Nostalrius, the 7.7 server rebuilt from Cip's files, data/actions/scripts/misc/chests.lua):
# "You have found %s. Weighing %d.%02d oz %s too heavy." The reward stays: the chest can be opened again.

DEAD_DRAGON = (32179, 32224, 9)      # Dragon Corpse Quest: a bag (8 oz) with a copper shield (63) and a legion helmet (31)


def _loaded(new_player, target):
    """A level 1 character (400 oz) carrying 416 oz: two plate armors in a backpack, one worn, a mace - no cap left."""
    from tibia74 import ARMOR, BACKPACK, RIGHT, Item
    inventory = {ARMOR: Item(2463), BACKPACK: Item(1988, contents=[Item(2463), Item(2463)]), RIGHT: Item(2398)}
    return next_to(new_player, target, level=1, group_id=TESTER_GROUP, storage={30001: 1}, inventory=inventory)


def test_a_reward_too_heavy_says_its_weight_and_stays(new_player, items):
    p = _loaded(new_player, RAPIER_BOX)
    use_map_item(p, items, RAPIER_BOX, "box")
    assert p.wait_for(lambda: p.messages("You have found a rapier. Weighing 15.00 oz it is too heavy."), timeout=3), \
        p.text_messages[-3:]
    assert not carries(p, "rapier")
    p.sleep(1.1)
    use_map_item(p, items, RAPIER_BOX, "box")       # not marked as taken: it says the same again, not "empty"
    assert p.wait_for(lambda: len(p.messages("Weighing 15.00 oz it is too heavy.")) == 2, timeout=3), \
        p.text_messages[-3:]


def test_a_bag_too_heavy_weighs_with_its_contents(new_player, items):
    """The bag (quests/system.lua REWARDS) does not exist before it is given: 8 + 63 + 31 = 102 oz."""
    p = _loaded(new_player, DEAD_DRAGON)
    use_map_item(p, items, DEAD_DRAGON, "dead dragon")
    assert p.wait_for(lambda: p.messages("You have found a bag. Weighing 102.00 oz it is too heavy."), timeout=3), \
        p.text_messages[-3:]
    assert not carries(p, "bag")

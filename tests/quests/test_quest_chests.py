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

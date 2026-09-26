"""Explorer Brooch Quest (docs/reference-74/quests.md)."""
from quests.common import *  # noqa: F401,F403


# TibiaWiki: "In upper side of room you will see 4 sewer gates. Go down, kill rat and take Explorer Brooch from body."
# The explorer brooch is a 7.6 item: the body gives the elven brooch it looks like (decided with the user 2026-09-26).
# Our map had the corridor under the grates but not the body.
BODY = (32636, 31873, 10)


def test_explorer_brooch_quest(new_player, items, world_map):
    from tibia74.route import follow, walk_next_to
    p = kazordoon_player(new_player)
    ability = dict(level=2000, rope=True)
    walk_next_to(p, items, world_map, BODY, **ability)
    use_map_item(p, items, BODY, "dead human")
    assert p.wait_for(lambda: p.messages("You have found an elven brooch."), timeout=3), p.text_messages[-3:]
    assert carries(p, "elven brooch"), p.inventory_names()
    before = len(p.text_messages)
    p.sleep(1.1)
    use_map_item(p, items, BODY, "dead human")
    assert p.wait_for(lambda: any("empty" in t for _, t in p.text_messages[before:]), timeout=3), p.text_messages[-3:]
    follow(p, items, world_map, KAZORDOON_TEMPLE, **ability)                 # back up the grate's ladder

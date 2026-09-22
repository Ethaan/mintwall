"""The new-player journey: Rookgaard temple -> first kills -> level 8 -> the Oracle."""
import pytest

from tibia74 import Item, RIGHT

ROOKGAARD_TEMPLE = (32097, 32219, 7)
THAIS_TEMPLE = (32369, 32241, 7)
TOWN_IDS = {"rookgaard": 1, "thais": 2, "carlin": 3, "venore": 8}   # from Tibia74.otbm

CLUB = 2382


def distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) if a[2] == b[2] else 99


# ----------------------------------------------------------------------------- arrival

def test_new_player_spawns_on_rookgaard_temple(new_player):
    p = new_player()
    assert p.pos == ROOKGAARD_TEMPLE
    assert p.stats.level == 1
    assert p.stats.health == p.stats.max_health == 150


def test_new_player_is_greeted_by_cipfried(new_player):
    p = new_player()
    replies = p.talk("hi", npc="Cipfried")
    assert any("Feel free to ask me for help" in r for r in replies), replies


def test_new_player_gets_the_beginner_set(new_player):
    """7.4 beginner set: club, torch, bag with a red apple, jacket (male) / coat (female)."""
    p = new_player(sex=1)
    assert p.wait_for(lambda: len(p.inventory) >= 3, timeout=5), p.inventory_names()
    worn = p.inventory_names()
    assert worn.get("armor") == "jacket", worn
    assert "club" in worn.values(), worn

    bag = p.open_container(p.slot_of("bag"))
    assert bag, f"no bag in the inventory: {worn}"
    inside = sorted(i.name for i in bag.items)
    assert inside == ["red apple", "torch"], inside


def test_new_player_has_the_noob_outfit(new_player):
    p = new_player(sex=1)
    me = p.wait_for(lambda: p.creatures.get(p.player_id), timeout=5)
    # looktype, then golden hair, blue shirt, brown legs, dark shoes
    assert me.outfit == (128, 78, 69, 58, 114), me.outfit


# ----------------------------------------------------------------------------- first kills

def test_level_1_player_can_kill_a_rat(new_player, world):
    spawn = world.nearest_spawn("Rat", ROOKGAARD_TEMPLE)
    p = new_player(pos=spawn, inventory={RIGHT: Item(CLUB)})
    rat = p.wait_for(lambda: p.nearest("Rat"), timeout=30)
    assert rat, f"no rat visible near spawn {spawn}"

    exp_before = p.stats.experience
    p.set_fight_modes(fight=1, chase=1)
    p.attack(rat.id)
    assert p.wait_for(lambda: rat.id in p.removed_creatures and p.stats.experience > exp_before,
                      timeout=90), f"rat not killed: {rat}, exp {p.stats.experience}"
    assert p.stats.health > 0


# ----------------------------------------------------------------------------- the Oracle

def _near_oracle(new_player, world, level):
    oracle = world.npcs["The Oracle"]
    p = new_player(level=level, pos=(oracle[0], oracle[1] + 2, oracle[2]))
    assert distance(p.pos, oracle) <= 3, f"could not place the player near the Oracle: {p.pos}"
    return p


def test_oracle_sends_away_players_below_level_8(new_player, world):
    p = _near_oracle(new_player, world, level=7)
    assert any("COME BACK WHEN YOU HAVE GROWN UP" in r for r in p.talk("hi", npc="The Oracle"))


def test_oracle_turns_a_level_8_into_a_knight_of_thais(new_player, world, db):
    p = _near_oracle(new_player, world, level=8)
    replies = p.talk("hi", "yes", "thais", "knight", npc="The Oracle")
    assert any("ARE YOU SURE" in r for r in replies), replies
    p.say("yes")   # the Oracle teleports us at once, so its "SO BE IT" is said after we're gone
    assert p.wait_for(lambda: p.pos == THAIS_TEMPLE, timeout=5), f"not teleported to Thais: {p.pos}"

    p.logout()
    row = db.character(p.character.guid)
    assert row["vocation"] == 4
    assert row["town_id"] == TOWN_IDS["thais"], "Oracle set the wrong home town (respawn temple)"

"""The new-player journey: Rookgaard temple -> first kills -> level 8 -> the Oracle."""
import pytest

from tibia74 import Item, RIGHT
from tibia74.server import TESTER_GROUP

ROOKGAARD_TEMPLE = (32097, 32219, 7)
THAIS_TEMPLE = (32369, 32241, 7)
TOWN_IDS = {"rookgaard": 1, "thais": 2, "carlin": 3, "venore": 8}   # from Tibia74.otbm

CLUB = 2382


def distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) if a[2] == b[2] else 99


# ----------------------------------------------------------------------------- arrival

def test_new_player_spawns_on_rookgaard_temple(new_player):
    p = new_player()
    # on the temple spot, or next to it when another character already stands there (the engine's placement)
    assert p.pos[2] == ROOKGAARD_TEMPLE[2] and max(abs(p.pos[0] - ROOKGAARD_TEMPLE[0]),
                                                    abs(p.pos[1] - ROOKGAARD_TEMPLE[1])) <= 1, p.pos
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


def test_killing_a_rat_gives_experience_and_a_level_up(new_player):
    """A level 1 one experience point short of level 2 (100) kills a rat (5 exp): level 2 and more hp."""
    spot = (32107, 32224, 7)                                   # the dirt road east of the temple
    p = new_player(pos=spot, experience=99, inventory={RIGHT: Item(2376)}, skills={2: 50})   # sword
    gm = new_player(pos=(spot[0], spot[1] - 3, spot[2]), group_id=3)
    max_hp = p.wait_for(lambda: p.stats.max_health, timeout=5)
    gm.say("/m Rat")
    rat = p.wait_for(lambda: p.nearest("Rat"), timeout=5)
    assert rat, "no rat"
    p.set_fight_modes(fight=1, chase=1)
    p.attack(rat.id)
    assert p.wait_for(lambda: rat.id in p.removed_creatures, timeout=60), f"rat not killed: {rat}"
    assert p.wait_for(lambda: p.stats.experience >= 104, timeout=3), f"experience {p.stats.experience}"
    assert p.wait_for(lambda: p.stats.level == 2, timeout=3), f"level {p.stats.level}"
    assert p.messages("You advanced from Level 1 to Level 2"), p.text_messages[-3:]
    assert p.stats.max_health > max_hp, f"max hp {max_hp} -> {p.stats.max_health}"


def test_killed_monster_dies_at_once(new_player, world):
    """It used to stand at 0 hp until its once-a-second check came round (plus 100-200 ms)."""
    import time
    # the sewer rats below the temple: not the spawn test_level_1_player_can_kill_a_rat empties
    spawn = world.nearest_spawn("Rat", (ROOKGAARD_TEMPLE[0], ROOKGAARD_TEMPLE[1], 8))
    p = new_player(pos=spawn, level=50, vocation=4, inventory={RIGHT: Item(2400)})   # magic sword
    rat = p.wait_for(lambda: p.nearest("Rat"), timeout=30)
    assert rat, f"no rat visible near spawn {spawn}"
    p.set_fight_modes(fight=1, chase=1)
    p.attack(rat.id)
    assert p.wait_for(lambda: rat.health == 0 or rat.id in p.removed_creatures, timeout=60), f"rat not killed: {rat}"
    at_zero = time.perf_counter()
    assert p.wait_for(lambda: rat.id in p.removed_creatures, timeout=3), "the dead rat never went away"
    stood = (time.perf_counter() - at_zero) * 1000
    assert stood < 100, f"the rat stood at 0 hp for {stood:.0f} ms"   # old build: 106-1199 ms


# ----------------------------------------------------------------------------- the Oracle

def _near_oracle(new_player, world, level):
    oracle = world.npcs["The Oracle"]
    p = new_player(level=level, pos=(oracle[0], oracle[1] + 2, oracle[2]))
    assert distance(p.pos, oracle) <= 3, f"could not place the player near the Oracle: {p.pos}"
    return p


def test_oracle_sends_away_players_below_level_8(new_player, world):
    p = _near_oracle(new_player, world, level=7)
    assert any("COME BACK WHEN YOU HAVE GROWN UP" in r for r in p.talk("hi", npc="The Oracle"))


@pytest.mark.parametrize("premium_days", [0, 30])
def test_oracle_offers_carlin_thais_and_venore(new_player, world, premium_days):
    """The 2005 Oracle: the three free towns, premium or not (decided with the user 2026-10-01)."""
    p = _near_oracle(new_player, world, level=8)
    replies = p.talk("hi", "yes", "edron", npc="The Oracle")
    assert any("CARLIN, THAIS, OR VENORE?" in r for r in replies), replies
    assert not any("IN EDRON" in r for r in replies), replies


def test_oracle_turns_a_level_8_into_a_knight_of_thais(new_player, world, db):
    p = _near_oracle(new_player, world, level=8)
    replies = p.talk("hi", "yes", "thais", "knight", npc="The Oracle")
    assert any("ARE YOU SURE" in r for r in replies), replies
    assert any("IN WHICH TOWN" in r for r in replies), replies
    assert not any("{" in r or "}" in r for r in replies), f"8.x {{keyword}} braces in 7.4 text: {replies}"
    items = len(p.all_items())
    # he teleports us a moment after "SO BE IT!", so we hear it
    assert "SO BE IT!" in p.talk("yes", npc="The Oracle", wait=1)
    assert p.wait_for(lambda: p.pos == THAIS_TEMPLE, timeout=5), f"not teleported to Thais: {p.pos}"
    assert len(p.all_items()) == items, "the Oracle gave a starter kit (7.4 had none)"

    p.logout()
    row = db.character(p.character.guid)
    assert row["vocation"] == 4
    assert row["town_id"] == TOWN_IDS["thais"], "Oracle set the wrong home town (respawn temple)"


# ----------------------------------------------------------------------------- rat sewer bridge

WEST_SWITCH, EAST_SWITCH = (32098, 32204, 8), (32104, 32204, 8)
BRIDGE = [(32100, 32205, 8), (32101, 32205, 8)]
DRAWBRIDGE = 1284


def _use_switch(p, pos):
    switch = p.tile_items(pos)[-1]
    p.use_item(pos, switch.client_id, len(p.tile_items(pos)) - 1)


def test_sewer_switch_lowers_the_bridge_and_raises_it_again(new_player):
    p = new_player(pos=(32099, 32205, 8))
    assert p.wait_for(lambda: p.tile_items(WEST_SWITCH), timeout=5)

    _use_switch(p, WEST_SWITCH)
    assert p.wait_for(lambda: all(p.tile_items(b)[0].client_id == DRAWBRIDGE for b in BRIDGE), timeout=5), \
        [p.tile_items(b) for b in BRIDGE]
    assert p.walk_to((32103, 32205, 8)), f"could not cross the bridge, stuck at {p.pos}"

    walker = new_player(pos=(32101, 32205, 8))   # standing on the bridge when it is raised
    assert p.wait_for(lambda: walker.pos == (32101, 32205, 8), timeout=5)
    _use_switch(p, EAST_SWITCH)
    assert p.wait_for(lambda: all(p.tile_items(b)[0].client_id != DRAWBRIDGE for b in BRIDGE), timeout=5)
    assert walker.wait_for(lambda: walker.pos == (32102, 32205, 8), timeout=5), f"left on the water at {walker.pos}"


# ----------------------------------------------------------------------------- Tom the tanner

TOM = (32085, 32199, 7)
BAG = 1988
DEAD_RAT, DEAD_RABBIT = 2813, 3119   # the corpses rats and rabbits really leave


def _gold(p):
    return sum(i.count for i in p.all_items() if i.name == "gold coin")


@pytest.mark.parametrize("corpse, name", [(DEAD_RAT, "dead rat"), (DEAD_RABBIT, "dead rabbit")])
def test_tom_buys_fresh_corpses_for_2_gold(new_player, corpse, name):
    from tibia74 import BACKPACK
    p = new_player(pos=(TOM[0] + 1, TOM[1] + 1, TOM[2]), inventory={BACKPACK: Item(BAG, contents=[Item(corpse)])})
    assert p.open_container(BACKPACK), "no backpack"

    replies = p.talk("hi", f"sell {name}", "yes", npc="Tom")
    assert p.wait_for(lambda: _gold(p) == 2, timeout=5), f"no gold; Tom said {replies}"
    assert not any(i.name == name for i in p.all_items()), "corpse still in the backpack"


# ----------------------------------------------------------------------------- King's Bridge

KINGS_BRIDGE_EAST, KINGS_BRIDGE_WEST = (32059, 32192, 7), (32055, 32192, 7)   # premium planks at x 32057


def test_kings_bridge_turns_back_free_accounts(new_player):
    p = new_player(pos=KINGS_BRIDGE_EAST)
    p.walk_to(KINGS_BRIDGE_WEST, max_steps=6)
    assert p.pos[0] > 32057, f"a free account crossed King's Bridge: {p.pos}"
    assert p.messages("Only premium citizens may pass"), p.text_messages


def test_kings_bridge_lets_premium_accounts_cross(new_player):
    p = new_player(pos=KINGS_BRIDGE_EAST, premium_days=30)
    assert p.walk_to(KINGS_BRIDGE_WEST, max_steps=6), f"premium account stopped at {p.pos}"


# ----------------------------------------------------------------------------- the Gatekeeper (premium side)

ANKRAHMUN_TEMPLE, ANKRAHMUN_TOWN = (33194, 32853, 8), 9   # from Tibia74.otbm


def test_gatekeeper_sends_a_premium_level_8_to_ankrahmun(new_player, world, db):
    """The premium side's Oracle (west of King's Bridge): Ab'Dendriel, Ankrahmun, Darashia or Kazordoon."""
    keeper = world.npcs["The Gatekeeper"]
    # snakes roam the (unprotected) room; an attacked player cannot log out, so use the unattackable group
    p = new_player(level=8, premium_days=30, pos=(keeper[0], keeper[1] + 1, keeper[2]),   # +2 is a trapdoor
                   group_id=TESTER_GROUP)
    assert distance(p.pos, keeper) <= 3, f"could not place the player near the Gatekeeper: {p.pos}"
    replies = p.talk("hi", "yes", "edron", "ankrahmun", "knight", npc="The Gatekeeper")
    assert any("Ab'Dendriel, Ankrahmun, Darashia or Kazordoon?" in r for r in replies), replies
    assert not any("Edron will be" in r for r in replies), replies
    assert any("Are you sure" in r for r in replies), replies
    items = len(p.all_items())
    p.say("yes")
    assert p.wait_for(lambda: p.pos == ANKRAHMUN_TEMPLE, timeout=5), f"not teleported to Ankrahmun: {p.pos}"
    assert len(p.all_items()) == items, "the Gatekeeper gave a starter kit (7.4 had none)"

    p.logout()
    row = db.character(p.character.guid)
    assert row["vocation"] == 4
    assert row["town_id"] == ANKRAHMUN_TOWN, f"home town {row['town_id']} is not Ankrahmun (respawn temple)"


# ----------------------------------------------------------------------------- premium side, locked door

PREMIUM_SIDE_DOOR = (32042, 32205, 6)   # locked door (1209, no key) from the house south of King's Bridge
LOCKED_DOOR = 1209


@pytest.mark.parametrize("premium_days", [0, 30])
def test_keyless_locked_door_stays_locked(new_player, premium_days):
    """It used to open for anyone ("impossible to happen") - a way around King's Bridge."""
    p = new_player(pos=(PREMIUM_SIDE_DOOR[0] + 1, PREMIUM_SIDE_DOOR[1], PREMIUM_SIDE_DOOR[2]),
                   premium_days=premium_days)
    assert p.wait_for(lambda: p.tile_items(PREMIUM_SIDE_DOOR), timeout=5)
    door = p.tile_items(PREMIUM_SIDE_DOOR)[-1]
    assert door.client_id == LOCKED_DOOR, p.tile_items(PREMIUM_SIDE_DOOR)
    p.use_item(PREMIUM_SIDE_DOOR, door.client_id, len(p.tile_items(PREMIUM_SIDE_DOOR)) - 1)
    assert p.wait_for(lambda: p.messages("It is locked"), timeout=3), p.text_messages
    assert p.tile_items(PREMIUM_SIDE_DOOR)[-1].client_id == LOCKED_DOOR, "the locked door opened"


# the village street north of the temple, two walkable tiles without the protection zone flag (checked below): a
# player placed on a tile he cannot stand on lands on the temple, a protection zone, where no attack works anyway
ROOK_FIELD = (32085, 32191, 7)
ROOK_FIELD_EAST = (32086, 32191, 7)
PROTECTION_ZONE = 1                  # OTBM tile flag (tile.h TILESTATE_PROTECTIONZONE)


def test_rook_field_is_walkable_and_no_protection_zone(world_map):
    from tibia74 import SERVER_DIR
    from tibia74.otbm import read_tiles
    tiles = {t.pos: t for t in read_tiles(SERVER_DIR / "data" / "world" / "Tibia74.otbm",
                                          area=(ROOK_FIELD, ROOK_FIELD_EAST))}
    for pos in (ROOK_FIELD, ROOK_FIELD_EAST):
        assert world_map.walkable(pos), f"{pos} is not walkable"
        assert pos in tiles and not tiles[pos].flags & PROTECTION_ZONE, f"{pos} is protection zone"
        assert not tiles[pos].house_id, f"{pos} is a house tile"


@pytest.mark.parametrize("attacker_vocation, target_vocation", [(0, 0), (4, 0), (0, 4)],
                         ids=["rook vs rook", "knight vs rook", "rook vs knight"])
def test_rookgaard_is_non_pvp(new_player, attacker_vocation, target_vocation):
    """No player hurts a player without a vocation, and none of them hurts anyone (Combat::rookgaardForbids)."""
    from tibia74 import RIGHT, Item
    attacker = new_player(pos=ROOK_FIELD, level=50, vocation=attacker_vocation, skills={1: 80, 2: 80},
                          inventory={RIGHT: Item(2382)})                       # club
    target = new_player(pos=ROOK_FIELD_EAST, level=50, vocation=target_vocation, storage={30001: 1})
    # both stand where they were put, off the protection zone (test above): the attack fails for the Rookgaard rule
    assert attacker.pos == ROOK_FIELD and target.pos == ROOK_FIELD_EAST, (attacker.pos, target.pos)
    health = target.wait_for(lambda: target.stats.health, timeout=3)
    attacker.set_fight_modes(fight=1, chase=1, safe=0)
    attacker.attack(target.player_id)
    assert attacker.wait_for(lambda: attacker.messages("may not attack this player"), timeout=3), \
        attacker.text_messages[-3:]
    attacker.sleep(4)                                                          # two attack turns
    assert target.stats.health == health, f"the target lost {health - target.stats.health} hp"


# ----------------------------------------------------------------------------- shopkeepers (TibiaWiki 2005)

GOLD = 2148


def _shop_customer(new_player, npc, premium_days=0, items=()):
    from tibia74 import BACKPACK
    from tibia74.quest import next_to, npc_pos
    p = next_to(new_player, npc_pos(npc), premium_days=premium_days, group_id=TESTER_GROUP,
                inventory={BACKPACK: Item(BAG, contents=list(items))})
    assert p.open_container(BACKPACK), "no backpack"
    return p


def test_seymour_pays_2_gold_for_a_dead_rat(new_player):
    """TibiaWiki 2005: "At earlier levels you can give him a rat corpse for 2 Gold"."""
    from tibia74.quest import talk_to
    p = _shop_customer(new_player, "Seymour", items=[Item(DEAD_RAT)])
    replies = talk_to(p, "Seymour", "hi", "sell dead rat", "yes")
    assert p.wait_for(lambda: _gold(p) == 2, timeout=5), f"no gold; Seymour said {replies}"
    assert not any(i.name == "dead rat" for i in p.all_items()), "the rat is still in the backpack"


def test_lee_delle_sells_at_the_2005_prices_and_no_football(new_player):
    """TibiaWiki 2005-11: spear 10 gp; no football on her list (ours sold one for 111)."""
    from tibia74.quest import talk_to
    p = _shop_customer(new_player, "Lee'Delle", premium_days=30, items=[Item(GOLD, count=10)])
    replies = talk_to(p, "Lee'Delle", "hi", "buy football", "buy spear", "yes")
    assert not any("football" in r.lower() for r in replies), replies
    assert p.wait_for(lambda: any(i.name == "spear" for i in p.all_items()), timeout=5), replies
    assert _gold(p) == 0, f"a spear cost {10 - _gold(p)} gp, not 10"


@pytest.mark.parametrize("premium_days", [0, 30])
def test_norma_sells_equipment_to_premium_players_only(new_player, premium_days):
    """TibiaWiki 2005: "Norma is a premium npc ... she sells and buys equipments for adventurers"."""
    from tibia74.quest import talk_to
    p = _shop_customer(new_player, "Norma", premium_days=premium_days, items=[Item(GOLD, count=10)])
    replies = talk_to(p, "Norma", "hi", "buy spear", "yes")
    bought = p.wait_for(lambda: any(i.name == "spear" for i in p.all_items()), timeout=3)
    if premium_days:
        assert bought, replies
        assert _gold(p) == 0
    else:
        assert not bought and _gold(p) == 10, replies
        assert any("only trade with premium" in r for r in replies), replies

"""The quick manual-testing accounts in sql/seed.sql log in and have what the docs say."""
import pytest

from tibia74 import GameClient, BACKPACK, RING

CREATURE = 0x63    # client id meaning "the creature on that tile" in a use-with


@pytest.mark.parametrize("account, password, name", [
    (1, "1", "Free Tester"),
    (2, "2", "Premium Tester"),
    (3, "3", "Centurion"),
    (9, "9", "GM Mintwall"),
])
def test_seeded_account_logs_in(server, items, account, password, name):
    c = GameClient(items, port=server.port)
    try:
        c.login(account, password, name)
        assert c.name == name
    finally:
        c.logout()


def test_centurion_is_fully_equipped_and_his_mana_fluid_refills(server, items):
    c = GameClient(items, port=server.port)
    try:
        c.login(3, "3", "Centurion")
        assert c.wait_for(lambda: len(c.inventory) >= 9, timeout=5), c.inventory_names()
        assert c.inventory_names() == {
            "head": "royal helmet", "necklace": "amulet of loss", "backpack": "backpack", "armor": "blue robe",
            "right": "magic sword", "left": "demon shield", "legs": "golden legs", "feet": "boots of haste",
            "ring": "time ring"}, c.inventory_names()

        bag = c.open_container(BACKPACK)
        assert bag, "backpack does not open"
        names = sorted(i.name for i in bag.items)
        assert names == sorted(["vial", "sudden death rune", "magic wall rune", "ultimate healing rune",
                                "rope", "shovel", "pick", "ring of the sky", "crystal coin",
                                "ultimate healing rune", "explosion rune", "stone skin amulet"]), names
        assert next(i for i in bag.items if i.name == "crystal coin").count == 100

        slot = next(n for n, i in enumerate(bag.items) if i.name == "vial")
        cid = next(k for k, v in c.containers.items() if v is bag)
        for sip in range(2):
            start = len(c.speech)
            vial = bag.items[slot]
            c.use_item_with(c.container_pos(cid, slot), vial.client_id, slot, c.pos, CREATURE, 1)
            assert c.wait_for(lambda: any(t == "Aaaah..." for _, _, t in c.speech[start:]), timeout=3), \
                f"drink {sip + 1}: no 'Aaaah...'; {c.text_messages[-3:]}"
            assert c.wait_for(lambda: bag.items[slot].count == 7, timeout=3), \
                f"drink {sip + 1}: the vial holds fluid {bag.items[slot].count}, not mana (7)"
            c.sleep(1.1)    # drinking exhausts for a second
    finally:
        c.logout()


def test_centurion_time_ring_speeds_him_up(server, items):
    """The worn time ring gives +speed from login on, and again after taking it off and on."""
    c = GameClient(items, port=server.port)
    try:
        c.login(3, "3", "Centurion")
        assert c.wait_for(lambda: c.inventory.get(RING) and c.creatures.get(c.player_id), timeout=5)
        bag = c.open_container(BACKPACK)
        cid = next(k for k, v in c.containers.items() if v is bag)
        me = c.creatures[c.player_id]
        slow = me.speed

        ring = c.inventory[RING]
        c.move_item(c.inventory_pos(RING), ring.client_id, 0, c.container_pos(cid, 0))
        assert c.wait_for(lambda: RING not in c.inventory, timeout=3), "could not take the ring off"
        worn_before = me.speed
        at = next(n for n, i in enumerate(bag.items) if i.name == "time ring")
        c.move_item(c.container_pos(cid, at), bag.items[at].client_id, at, c.inventory_pos(RING))
        assert c.wait_for(lambda: me.speed > worn_before, timeout=3), \
            f"time ring on: speed {me.speed}, off: {worn_before} (at login {slow})"
        assert slow == me.speed, f"the ring was not already working at login: {slow} vs {me.speed}"
    finally:
        c.logout()


def _rune_charges(db, guid, itemtype):
    """Charges of the marked runes, as saved on logout (the 7.4 protocol does not send rune charges)."""
    marked = bytes([4]) + (64000).to_bytes(2, "little")
    return [r["count"] for r in db.items(guid) if r["itemtype"] == itemtype and marked in bytes(r["attributes"] or b"")]


def _use_rune_on_self(c, bag, cid, slot, times):
    for _ in range(times):
        start = len(c.effects)
        c.use_item_with(c.container_pos(cid, slot), bag.items[slot].client_id, slot, c.pos, CREATURE, 1)
        assert c.wait_for(lambda: len(c.effects) > start, timeout=3), f"rune not used: {c.text_messages[-2:]}"
        c.sleep(1.1)


def test_centurion_supply_runes_never_run_out(server, items, db):
    """The UH rune with action id 64000 keeps its charges - Centurion is in config InfiniteItemPlayers."""
    c = GameClient(items, port=server.port)
    try:
        c.login(3, "3", "Centurion")
        bag = c.open_container(BACKPACK)
        assert bag, "backpack does not open"
        cid = next(k for k, v in c.containers.items() if v is bag)
        slot = [n for n, i in enumerate(bag.items) if i.name == "ultimate healing rune"][-1]   # the supply one
        _use_rune_on_self(c, bag, cid, slot, 2)
    finally:
        c.logout()
    con = db._connect()
    guid = con.execute("SELECT id FROM players WHERE name = 'Centurion'").fetchone()[0]
    con.close()
    assert _rune_charges(db, guid, 2273) == [100], _rune_charges(db, guid, 2273)


def test_infinite_items_are_ordinary_for_everyone_else(new_player, db):
    """Marked items only never run out for config InfiniteItemPlayers (Player::isAllowedToUseInfinite)."""
    from tibia74 import Item
    marked = bytes([4]) + (64000).to_bytes(2, "little")          # action id 64000
    p = new_player(level=50, vocation=1, maglevel=4, health=100, pos=(32369, 32241, 7),
                   inventory={BACKPACK: Item(1988, contents=[Item(2273, 5, attributes=marked),     # UH rune
                                                             Item(2006, 7, attributes=marked)])})  # mana fluid
    bag = p.open_container(BACKPACK)
    cid = next(k for k, v in p.containers.items() if v is bag)
    _use_rune_on_self(p, bag, cid, next(n for n, i in enumerate(bag.items) if i.name == "ultimate healing rune"), 1)
    vial = next(n for n, i in enumerate(bag.items) if i.name == "vial")
    p.use_item_with(p.container_pos(cid, vial), bag.items[vial].client_id, vial, p.pos, CREATURE, 1)
    assert p.wait_for(lambda: bag.items[vial].count == 0, timeout=3), f"vial still holds {bag.items[vial].count}"
    guid = p.character.guid
    p.logout()
    assert _rune_charges(db, guid, 2273) == [4], f"rune charges {_rune_charges(db, guid, 2273)}, expected 5 -> 4"

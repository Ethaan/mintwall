"""Magic wall and wild growth on fields. 7.4: "Magic Wall or wild growth will not remove fields"
(docs/reference-74/tibiantis-notes/poison.txt): the wall goes on top, the field stays under it and burns again
once the wall is gone. A field rune thrown at a wall does not remove it either ("Makes an indestructible wall",
TibiaWiki Magic Wall, 2008-05 revision 156918), and destroy field cannot reach through it ("from any distance as
long theres nothing blocking the path", TibiaWiki Destroy Field, 2008-02 revision 146472).

Found in game: in the Demon Helmet fire corridor (Edron, 33210-33212,31620-31629,13) a magic wall thrown on the
map's fire fields (1487/1488, not replaceable) did nothing - the engine refused to put a field on a field it
could not replace, and threw the wall away."""
from tibia74 import BACKPACK, WEST, NORTHWEST, Item
from tibia74.server import TESTER_GROUP

MAGIC_WALL_RUNE, FIRE_BOMB_RUNE, FIRE_FIELD_RUNE, DESTROY_FIELD_RUNE = 2293, 2305, 2301, 2261
MAGIC_WALL, WILD_GROWTH = 1498, 1499
MAP_FIRE_FIELDS = {1487, 1488}
FIRE_FIELDS = {1487, 1488, 1492, 1493, 1494}
INFINITE = bytes([4]) + (64000).to_bytes(2, "little")     # action id 64000: a test character's never-ending rune

# the Demon Helmet fire corridor, ground 407 (tests/tibia74/otbm.py read_tiles); no protection zone
CORRIDOR_FIRE = (33211, 31627, 13)          # map fire field 1487 (20 damage on entering)
CORRIDOR_FIRE_EAST = (33212, 31628, 13)     # free, south-east of it
GROWTH_SPOT, GROWTH_FIRE = (33211, 31629, 13), (33210, 31629, 13)   # free; map fire field 1488 west of it
BOMB_SPOT, BOMB_WALL, BOMB_TARGET = (33212, 31631, 13), (33211, 31631, 13), (33211, 31632, 13)   # all free
FIELD_SPOT, FIELD_TILE = (33212, 31618, 13), (33211, 31618, 13)    # free, north of the fires


def _caster(new_player, pos, runes, vocation=5, group_id=TESTER_GROUP, **kwargs):
    p = new_player(pos=pos, level=100, vocation=vocation, maglevel=40, mana=3000, premium_days=30,
                   group_id=group_id, storage={30001: 1},
                   inventory={BACKPACK: Item(1988, contents=[Item(r, 1, attributes=INFINITE) for r in runes])},
                   **kwargs)
    assert p.pos == pos, f"placed at {p.pos}, not {pos}"
    p.set_fight_modes(fight=1, chase=0, safe=0)
    bag = p.open_container(BACKPACK)
    p.rune_bag = next(k for k, v in p.containers.items() if v is bag)
    return p


def _ids(p, items, pos):
    return {items.client(t.client_id).server_id for t in p.tile_items(pos)}


def _use_rune(p, items, rune, pos):
    bag = p.containers[p.rune_bag]
    slot = next(n for n, it in enumerate(bag.items) if items.client(it.client_id).server_id == rune)
    stack = p.tile_items(pos)
    top = stack[-1]
    p.use_item_with(p.container_pos(p.rune_bag, slot), items.by_server[rune].client_id, slot,
                    pos, top.client_id, len(stack) - 1)


def test_a_magic_wall_goes_on_a_map_fire_field_which_burns_again_after_it(new_player, items):
    p = _caster(new_player, CORRIDOR_FIRE_EAST, [MAGIC_WALL_RUNE])
    assert _ids(p, items, CORRIDOR_FIRE) & MAP_FIRE_FIELDS, p.tile_items(CORRIDOR_FIRE)
    _use_rune(p, items, MAGIC_WALL_RUNE, CORRIDOR_FIRE)
    assert p.wait_for(lambda: MAGIC_WALL in _ids(p, items, CORRIDOR_FIRE), timeout=3), \
        f"no magic wall on the fire field: {_ids(p, items, CORRIDOR_FIRE)} {p.text_messages[-2:]}"
    assert _ids(p, items, CORRIDOR_FIRE) & MAP_FIRE_FIELDS, "the fire field went away under the wall"
    assert not p.step(NORTHWEST, timeout=1.5), "walked into the magic wall"

    # the wall lasts 20 s; the fire field is still there after it
    assert p.wait_for(lambda: MAGIC_WALL not in _ids(p, items, CORRIDOR_FIRE), timeout=25), "the wall never went"
    assert _ids(p, items, CORRIDOR_FIRE) & MAP_FIRE_FIELDS, f"no fire field after the wall: {_ids(p, items, CORRIDOR_FIRE)}"
    p.logout()

    # and it burns: a normal character steps on it
    b = new_player(pos=CORRIDOR_FIRE_EAST, level=100, vocation=4, premium_days=30, storage={30001: 1})
    assert b.pos == CORRIDOR_FIRE_EAST, b.pos
    before = b.wait_for(lambda: b.stats.health, timeout=3) and b.stats.health
    assert b.step(NORTHWEST), f"could not step onto the fire field from {b.pos}"
    assert b.wait_for(lambda: b.stats.health < before, timeout=3), "the fire field did not burn"


def test_wild_growth_goes_on_a_map_fire_field(new_player, items):
    p = _caster(new_player, GROWTH_SPOT, [], vocation=6)     # elder druid
    assert _ids(p, items, GROWTH_FIRE) & MAP_FIRE_FIELDS, p.tile_items(GROWTH_FIRE)
    p.turn(WEST)
    p.wait_for(lambda: p.creatures[p.player_id].direction == WEST, timeout=2)
    p.say("exevo grav vita")
    assert p.wait_for(lambda: WILD_GROWTH in _ids(p, items, GROWTH_FIRE), timeout=3), \
        f"no wild growth on the fire field: {_ids(p, items, GROWTH_FIRE)} {p.text_messages[-2:]}"
    assert _ids(p, items, GROWTH_FIRE) & MAP_FIRE_FIELDS, "the fire field went away under the wild growth"


def test_a_fire_bomb_does_not_remove_a_magic_wall(new_player, items):
    p = _caster(new_player, BOMB_SPOT, [MAGIC_WALL_RUNE, FIRE_BOMB_RUNE])
    _use_rune(p, items, MAGIC_WALL_RUNE, BOMB_WALL)
    assert p.wait_for(lambda: MAGIC_WALL in _ids(p, items, BOMB_WALL), timeout=3), p.text_messages[-2:]
    p.sleep(2.2)                                                      # rune exhaustion
    _use_rune(p, items, FIRE_BOMB_RUNE, BOMB_TARGET)                  # its 3x3 covers the wall
    assert p.wait_for(lambda: _ids(p, items, BOMB_TARGET) & FIRE_FIELDS, timeout=3), \
        f"the fire bomb made no fire: {p.text_messages[-2:]}"
    ids = _ids(p, items, BOMB_WALL)
    assert MAGIC_WALL in ids, f"the fire bomb removed the magic wall: {ids}"
    assert not ids & FIRE_FIELDS, f"a fire field went on the magic wall's tile: {ids}"


def test_a_field_under_a_magic_wall_outlives_it_and_destroy_field_reaches_it_only_then(new_player, items):
    """The tile keeps knowing it has a field when the wall on top of it goes (destroy field finds the field the
    same way monsters avoid it and stepping burns: Tile::getFieldItem)."""
    p = _caster(new_player, FIELD_SPOT, [FIRE_FIELD_RUNE, MAGIC_WALL_RUNE, DESTROY_FIELD_RUNE])
    _use_rune(p, items, FIRE_FIELD_RUNE, FIELD_TILE)
    assert p.wait_for(lambda: _ids(p, items, FIELD_TILE) & FIRE_FIELDS, timeout=3), p.text_messages[-2:]
    p.sleep(2.2)
    _use_rune(p, items, MAGIC_WALL_RUNE, FIELD_TILE)
    assert p.wait_for(lambda: MAGIC_WALL in _ids(p, items, FIELD_TILE), timeout=3), p.text_messages[-2:]
    assert _ids(p, items, FIELD_TILE) & FIRE_FIELDS, f"the magic wall replaced the fire field: {_ids(p, items, FIELD_TILE)}"

    p.sleep(2.2)
    _use_rune(p, items, DESTROY_FIELD_RUNE, FIELD_TILE)               # the wall is in the way
    p.sleep(1)
    ids = _ids(p, items, FIELD_TILE)
    assert MAGIC_WALL in ids and ids & FIRE_FIELDS, f"destroy field reached through the magic wall: {ids}"

    assert p.wait_for(lambda: MAGIC_WALL not in _ids(p, items, FIELD_TILE), timeout=25), "the wall never went"
    assert _ids(p, items, FIELD_TILE) & FIRE_FIELDS, f"no fire field after the wall: {_ids(p, items, FIELD_TILE)}"
    _use_rune(p, items, DESTROY_FIELD_RUNE, FIELD_TILE)
    assert p.wait_for(lambda: not _ids(p, items, FIELD_TILE) & FIRE_FIELDS, timeout=3), \
        f"destroy field did not find the fire field once the wall was gone: {p.text_messages[-2:]}"

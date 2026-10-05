# Server memory

Task: "Reduce server memory (~2.5 GB with full map)". Measured on 2026-10-05 with a test server
(`tests/tibia74/server.py` `ServerProcess`, run dir `tests/.run-mem`, port 7228), read with PowerShell
`Get-Process` 10 s after "Server Running".

## Measurements (exe built Oct 4 2026, before the change below)

| Setup | Working set | Private bytes | Peak WS | Startup |
|---|---|---|---|---|
| Full map `Tibia74.otbm` + spawns + houses | **2472 MB** | **2557 MB** | 2786 MB | 5.5 s |
| Full map, empty spawn file | 2426 MB | 2480 MB | 2786 MB | 5.1 s |
| Small map `Fibula.otbm` (no spawns/houses) | 58 MB | 50 MB | 63 MB | 1.0 s |

So the server itself (items.otb/xml, Lua states, scripts, vocations, monster types) is ~60 MB, the 18,666 monsters
and 303 NPCs of `Tibia74-spawns.xml` are ~50-80 MB, and **the map is ~2.37 GB**.

The map (counted with `tests/tibia74/otbm.py`):

- 7,296,177 tiles, 7,659,403 items (+645 inside containers), 5,968 items with attributes, 40,260 house tiles
- 6,950,375 tiles (95%) hold exactly one item (their ground) - 4,339,950 of them are item 101 "earth"
- 28,443 quadtree leaves (8x8 columns), 122,455 `Floor`s (8x8x1, 512 bytes each)

## Where the 2.37 GB goes (x64 MSVC layout, Windows heap: +8 byte header, 16 byte buckets)

| Structure | Per unit | Count | Total |
|---|---|---|---|
| `Tile` (Cylinder vptr/vbptr, ground, 3 `std::vector`s = 72 bytes, qt_node, pos, flags, vtordisp, virtual base `Thing` 24) | ~152 B -> 160 B block | 7.30 M | ~1.11 GB |
| `Item` (ItemAttributes vptr+attrs 24, vbptr, id/count/loadedOnMap, vtordisp, `Thing` 24) | ~72 B -> 80 B block | 7.66 M | ~0.58 GB |
| **`Map::refreshTileMap`**: a `std::map<Tile*, {ItemVector clones, uint64}>` node for **every** tile (`if(hasFlag(TILESTATE_REFRESH))` was commented out in `Map::setTile`) | 72 B -> 80 B block | 7.30 M | **~0.56 GB** |
| ... plus a `clone()` of every down item of every tile kept in it (never read: the restore code in `Game::refreshMap` is commented out) | ~80-100 B | ~0.35 M | ~0.03 GB |
| `Floor` arrays | 512 B | 122 k | 0.06 GB |
| Quadtree nodes/leaves | small | ~40 k | < 0.01 GB |

Sum ~2.35 GB, matching the measured 2.37 GB. The OTBM loader's node tree (`FileLoader`, one 32-byte `NodeStruct`
per tile/item node, ~0.35 GB) exists only during the load: it is the 2786 - 2426 = 360 MB between peak and final
working set, and is freed when `IOMapOTBM::loadMap` returns.

## Change made (not yet built - see below)

**Refresh map: one `Tile*` per tile instead of a `std::map` node + clones.**

- `src/map.h`: `std::map<Tile*, RefreshBlock_t> refreshTileMap` -> `std::vector<Tile*> refreshTiles`.
- `src/map.cpp` `Map::setTile`: push the tile (only when it was actually placed - before, a duplicate tile that was
  rejected still got an entry); no more clones of the down items. `Map::loadMap`: `shrink_to_fit()` after the load.
- `src/game.h/.cpp` `refreshMap`/`proceduralRefresh`: walk the vector by **index**, not iterator - combat/spells
  create tiles at runtime (`Game::setTile` for a field cast on a position without a tile), and a `push_back` during
  a running `/refreshmap` would invalidate an iterator. The commented-out "restore to original state" block that
  read the clones is removed (it was dead code).

Behaviour is unchanged: `/refreshmap` and `doRefreshMap()` still visit every tile and remove its cleanable items
(`Item::isCleanable`: not loaded with the map, no action/unique id, pickupable). Only the visiting order changes
(load order instead of pointer order). Nothing in `data/` or `tests/` calls either (serversave.lua does not refresh).

| Change | Saves (estimate) | Risk |
|---|---|---|
| Refresh map -> `std::vector<Tile*>` (58 MB for 7.3 M pointers), no clones | **~0.53 GB** (0.56 + 0.03 - 0.06) -> expected ~1.9 GB working set | Low: 4 files, only `/refreshmap` / `doRefreshMap` use it, neither tested nor scripted |

**Not built / not measured yet**: an `avesta74.exe` from `C:\mintwall\server` was running (another agent's test
server) for the whole session, so `server\build.bat` was not run. To verify once it is free:

```
server\build.bat
python -c "import sys,time;sys.path.insert(0,'tests');from pathlib import Path;from tibia74.server import ServerProcess as S;s=S(port=7228,run_dir=Path(r'C:\mintwall\tests\.run-mem'));s.start(600);time.sleep(10);print(s.proc.pid);input('measure with Get-Process -Id <pid>, then Enter');s.stop()"
```

Expected: working set ~1.9-2.0 GB (from 2.47 GB). Also check `/refreshmap` as a GM still removes a dropped item.
Note (unchanged, pre-existing): `proceduralRefresh` does 250 tiles every 100 ms, so a full `/refreshmap` over 7.3 M
tiles takes ~49 minutes.

## Further reductions (proposals, not implemented - larger/riskier)

| Proposal | Saves (estimate) | Risk / cost |
|---|---|---|
| **Lazy tile item lists**: replace `topItems`, `downItems`, `creatures` (3 x 24 B) by one pointer to a struct allocated on the first top/down item or creature (TFS's StaticTile/DynamicTile idea). 95% of tiles hold only their ground and never get a creature. Tile 152 -> ~88 B (96 B block) | **~0.45 GB** | Medium: ~100 direct uses of the three vectors in tile.cpp, game.cpp, map.cpp, monster.cpp, protocolgame.cpp and others; mechanical but needs the full test run |
| Free the lists again when a tile's last creature/item leaves | small, keeps the saving over time | Low once the above exists |
| Shared ground items for plain ground tiles (e.g. 4.3 M "earth") | up to ~0.5 GB | High: every `Item` has its own `Thing::parent` (getPosition, getTile, decay, use/move code paths assume it); not recommended |
| Pool/arena allocation for `Tile` and `Item` (no 8 B header / 16 B rounding) | ~0.05-0.1 GB | Medium (the old `__OTSERV_ALLOCATOR__` pool is per-size boost pools with a global lock; a dedicated arena for map-load objects would be better) |
| Drop `ItemAttributes`' virtual destructor (8 B/item) | 0 today (72 -> 64 B still lands in the 80 B bucket) | - |
| Streaming OTBM loader (no full node tree) | only the 0.36 GB load-time peak | Medium, no steady-state gain |
| Spawns / NPC Lua / items tables | together < 0.15 GB | Not worth it |

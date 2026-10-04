# mintwall - project context

Read this first in every new session. Keep it current: when a decision changes or something
non-obvious is learned, update this file. Work items live in `task.md`.

## Goal

A classic **Tibia 7.4** server that players connect to with the **original CipSoft 7.4 client**,
kept as close to real 7.4 as possible. We deliberately moved away from heavily customized
OTClient-based clients (Olders, Miracle) - no custom client, no added features.

## Stack and why

| Piece | Choice | Why |
|---|---|---|
| Client | Original `Tibia740.zip` (ots.me archive), IP-patched copy `Tibia-mintwall.exe` | Genuine 7.4 files (Dec 2004), no customization |
| Server | **Avesta74** (peonso/avesta74, source rev102), C++ | Speaks the real 7.4 protocol natively, SQLite, small codebase |
| Map | `Tibia74.otbm` from Inconcessus/Tibia74-JS-Engine | 7.4 real map (222222's "Authentic 7.4 Real Map", OTLand), 47 towns, spawns, houses |
| NPCs | 306 NPCs from tibiaot74/otserver | 7.4 dialogue; written for OTX/TFS 0.3 + Jiddo NpcSystem, run via a compat layer |
| Build | CMake + vcpkg (`C:\vcpkg`) + VS 2022 Build Tools, static x64 | Only toolchain on this machine; no WSL/Docker |

Rejected: tfs1041_oldschool (10.41 protocol), fschuindt TFS-7.4 (needs a modded 7.72 client),
tibiaot74's own engine/map (7.72 items), bradleyworkman 7.1 map (wrong era).

## Layout

```
C:\mintwall                 (outside OneDrive on purpose: no syncing of build/db files)
  context.md, task.md, README.md
  server\
    src\                    Avesta C++ source (modified, see "Engine changes")
    data\                   game data: items, monster, npc, spells, actions, world\ (maps)
    config.lua              IP 127.0.0.1, port 7171, SQLite db.db3, Map = data/world/Tibia74.otbm
    sql\schema.sqlite, sql\seed.sql
    build.bat, init-db.bat, start-server.bat
    build\                  (ignored) cmake/vcpkg output
  client\Tibia740\          (ignored, proprietary) original client + Tibia-mintwall.exe
  client-mod\
    mintwall.cpp, build.bat mintwall.dll: WH_GETMESSAGE hook on the client's UI thread that drops
                            Windows' key repeats for movement keys and posts its own (33 ms, no initial
                            delay; last held key wins). Loaded via an extra import in Tibia-mintwall.exe
  tools\
    patch-client.ps1        writes Tibia-mintwall.exe: IP patch + new ".mintw" section with an import
                            table that adds mintwall.dll!MintwallInit; copies mintwall.dll next to it
    walk-trace.py           proxy on 7171 -> own server on 7172; logs step requests/moves/cancels
                            with expected step times (mise run walk-trace)
    talk-test.ps1           scripted 7.4 login + chat, prints server text (NPC testing)
    otb-ids.ps1             dumps server->client id pairs from an items.otb
```

## Everyday commands

```
server\build.bat                      rebuild (first run compiles all deps via vcpkg, slow)
server\init-db.bat                    fresh db.db3 from sql\ (delete db.db3 first)
server\start-server.bat               run the server
mise run build|seed|reseed|start-server|stop-server|restart-server|test   same via mise.toml
                                      (stop/restart touch only the dev server: tools/dev-server.ps1)
powershell -ExecutionPolicy Bypass -File tools\talk-test.ps1 -Words "hi,job,bye"
powershell -ExecutionPolicy Bypass -File tools\patch-client.ps1 -Ip <address>
```
SQLite shell: `server\build\vcpkg_installed\x64-windows-static\tools\sqlite3.exe server\db.db3`

## Accounts (local, from sql/seed.sql)

- 111111 / tibia - "Mintwall", player, Rookgaard (town 1)
- 1 / 1 - "Free Tester", free account, level 1, Rookgaard
- 2 / 2 - "Premium Tester", premium account (premend 2000000000 = May 2033; premend is read as
  32-bit, so no later date), level 8, Rookgaard - for King's Bridge and the Gatekeeper
- Noob outfit (new characters): looktype 128 male / 136 female, head 78, body 69, legs 58, feet 114
  (picked in the client's own outfit dialog; set in data/creaturescripts/scripts/login.lua)
- 222222 / test - "Rook Tester" (level 1, Rookgaard temple) and "Oracle Tester" (level 8, next to
  The Oracle) for manually playing the new-player journey
- 3 / 3 - "Centurion", premium level 171 elite knight, Thais: royal helmet, blue robe, golden legs,
  boots of haste, magic sword, demon shield, amulet of loss, time ring (~24.8 days of wear), backpack
  with a self-refilling mana fluid (action id 64000), SD/MW/UH runes (100 charges), rope, shovel,
  pick, ring of the sky, 100 crystal coins, UH / explosion runes and a stone skin amulet that never run
  out. Magic level 9, sword/shield 90. For exploring the mainland. "Never run out" = action id 64000
  on the item AND the name in config.lua InfiniteItemPlayers (Player::isAllowedToUseInfinite); for
  anyone else those items are ordinary
- 4 / 4 - "Gandalf", premium level 500 master sorcerer, Thais: magic level 100, shielding 100, mystic turban,
  blue robe, golden legs, boots of haste, mastermind shield, stone skin amulet, time ring; backpack with
  SD / GFB / UH / explosion / MW runes and a mana fluid that never run out (in InfiniteItemPlayers)
- 5 / 5 - "Radagast", premium level 500 elder druid (as Gandalf, plus infinite paralyze runes)
- 6 / 6 - "Legolas", premium level 500 royal paladin: distance 100, shielding 100, ML 25, crossbow + bolts,
  bow + arrows, 100 spears, infinite SD / GFB / UH / explosion / paralyze runes
- 9 / 9 - "GM Mintwall", group God (access 3), Thais (town 2)
- Items: `/i <id> [count]`, `/n "<name>" [count]` (max 100). Broadcast `/B text`.

## Engine changes vs upstream Avesta (keep this list complete)

- Modern MSVC/Boost 1.92: `io_service`->`io_context`, `to_ulong`->`to_uint`, missing
  `<sstream>`/`<string>`, `round()` clash renamed `roundToInt`, `_WIN32_WINNT 0x0601`,
  `_HAS_AUTO_PTR_ETC=1` for `std::binary_function`
- Map loader: OTBM v1+ store stack counts as `ATTR_COUNT`, not inline (`Item::otbmInlineCount`)
- NPCs: `<parameters>` parsed from NPC XML (`Npc::loadParams`), Lua `getNpcParameter(key)`
- NPC events call Lua without expecting a boolean return (was an error per NPC per tick)
- New Lua `isPlayer(cid)`; `getSpectators` 4th arg (multifloor) optional
- Login creature events are now actually executed (upstream had `playerLogIn()` but never called it),
  which is what runs `data/creaturescripts/scripts/login.lua` (beginner set + classic outfit)
- Data: `TRUE`/`FALSE` defined in global.lua; antidote rune constant typo; `Demongoblin` monster;
  spawns: Bonebeast->Bone Beast, Cobra/Demon Skeleton were tagged as NPCs
- Premium (docs/reference-74/premium.md): VIP list 20 free / maxviplist with premium (`Player::addVIP`, was 51
  for all); a free account cannot open a private chat channel (`Chat::createChannel`)

## Script compatibility layer

TFS-era scripts run on Avesta through shims, not rewrites:
- `data/compat.lua` (loaded at the END of global.lua - it aliases constants defined there): renamed functions
  (getPlayerName, isPzLocked, getThingPosition...), pure helpers (isInArray...), no-op stubs for
  post-7.4 features (blessings, outfits), 7.4 promotion (voc 1-4 -> 5-8)
- `data/npc/lib/compat.lua` (NPC state): selfSay drops extra args (TFS passes cid, Avesta
  treats arg 2 as a delay!), getNpcDistanceTo, talk-only shop stubs, item constants (`Cf*`)
- `data/npc/lib/` = Jiddo NpcSystem from tibiaot74; `_npcsystem.lua` loads files explicitly
- Avesta shares ONE Lua state for all NPCs; events are captured right after each script loads

Prefer adding a shim over editing hundreds of scripts. Prefer engine fixes over script hacks
when the engine is wrong.

## Gotchas learned

- Many source/data files are **CRLF**; perl/sed edits must allow `\r?\n` (edits silently no-op otherwise)
- In perl replacements `$/` is a variable - don't write `"..."$/` in a pattern
- Git Bash rewrites `/B` style args into paths: prefix `MSYS_NO_PATHCONV=1`
- Port 7171 is also used by another local server `C:\ot\server\tfs.exe` (separate 7.6 project);
  Windows lets both bind and routes connections unpredictably - keep it stopped
- The 7.4 client has no RSA/XTEA; login hosts are 4 fixed strings in Tibia.exe (max 16 chars)
- Items: our items.otb (Avesta, v1.2) and the map's (v1.3) have identical server->client ids
- Full map server uses ~2.5 GB RAM
- Edit a character in db.db3 only while it is logged out: the server keeps an online character in
  memory and its logout save overwrites the DB (lost Centurion's rings once). lastlogin/lastlogout in
  the DB do NOT tell whether a character is online right now - ask the player to log out first
- The `server.log` of a running server is locked; the exe is locked while running (stop before rebuild)
- Premium is checked at login only, **by design** (as real Tibia): premium that runs out while you play lasts
  until you log out (or the daily server save kicks everyone) - e.g. it ends Monday 4 AM, the save is 3 AM:
  up to ~23 hours more. A lost connection counts as a logout. Promotion suspension follows the same rule
  (IOPlayer::loadPlayer). Do not "fix" this with an online check

## Testing (tests/)

Gameplay is verified by an automated suite, not by hand:
- `tests
- `tests\run-tests.bat` (or `-k oracle` for a subset). Starts its **own** server
  (`-c tests/.run/config.lua`, port **7181**, fresh `tests/.run/test.db3` from sql/), so the dev
  server on 7171 and db.db3 are never touched. Needs `server\avesta74.exe` built.
- `tests/tibia74/` is a headless 7.4 client (Python) that mirrors Avesta's `protocolgame.cpp`
  byte for byte and models position, stats, skills, inventory, containers, tiles, creatures, messages.
  Camera centre is moved by map slices/floor changes exactly like the real client.
- Each test creates fresh characters in the DB (`new_player(level=, pos=, inventory=, vocation=)`),
  logs in, acts (`talk`, `walk_to`, `attack`, `use_item`, `move_item`...) and asserts with `wait_for`.
- Every test also fails if the server logged any Lua error while it ran.
- Quests: one file per quest, `tests/quests/<city>/test_<quest>.py`, shared bits in `tests/quests/common.py`;
  how to do a quest: `.claude/skills/quest-testing`. `pytest quests/thais` runs one city.
- Lua errors in the server log now include the called function and the script line.
- Spec not implemented yet -> write the test anyway and mark `xfail(strict=True)`; it turns
  into a failure the moment the feature works, reminding us to remove the marker.
- Python 3.12 is installed per-user; the venv lives in `tests/.venv` (ignored).

## Working agreement

- One task at a time from `task.md`; mark it done with a one-line note of what changed
- Tests are for behaviour that matters (the player journey, formulas, quests, shops) - not for
  every small fix. A one-off map or data fix is just fixed; run the suite before committing
- Commit after each finished task

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
  tools\
    patch-client.ps1        writes Tibia-mintwall.exe pointing at an IP
    talk-test.ps1           scripted 7.4 login + chat, prints server text (NPC testing)
    otb-ids.ps1             dumps server->client id pairs from an items.otb
```

## Everyday commands

```
server\build.bat                      rebuild (first run compiles all deps via vcpkg, slow)
server\init-db.bat                    fresh db.db3 from sql\ (delete db.db3 first)
server\start-server.bat               run the server
powershell -ExecutionPolicy Bypass -File tools\talk-test.ps1 -Words "hi,job,bye"
powershell -ExecutionPolicy Bypass -File tools\patch-client.ps1 -Ip <address>
```
SQLite shell: `server\build\vcpkg_installed\x64-windows-static\tools\sqlite3.exe server\db.db3`

## Accounts (local, from sql/seed.sql)

- 111111 / tibia - "Mintwall", player, Rookgaard (town 1)
- 999999 / (see seed.sql) - "GM Mintwall", group God (access 3), Thais (town 2)
- Items: `/i <id> [count]`, `/n "<name>" [count]` (max 100). Broadcast `/B text`.

## Engine changes vs upstream Avesta (keep this list complete)

- Modern MSVC/Boost 1.92: `io_service`->`io_context`, `to_ulong`->`to_uint`, missing
  `<sstream>`/`<string>`, `round()` clash renamed `roundToInt`, `_WIN32_WINNT 0x0601`,
  `_HAS_AUTO_PTR_ETC=1` for `std::binary_function`
- Map loader: OTBM v1+ store stack counts as `ATTR_COUNT`, not inline (`Item::otbmInlineCount`)
- NPCs: `<parameters>` parsed from NPC XML (`Npc::loadParams`), Lua `getNpcParameter(key)`
- NPC events call Lua without expecting a boolean return (was an error per NPC per tick)
- New Lua `isPlayer(cid)`; `getSpectators` 4th arg (multifloor) optional
- Data: `TRUE`/`FALSE` defined in global.lua; antidote rune constant typo; `Demongoblin` monster;
  spawns: Bonebeast->Bone Beast, Cobra/Demon Skeleton were tagged as NPCs

## Script compatibility layer

TFS-era scripts run on Avesta through shims, not rewrites:
- `data/compat.lua` (loaded by global.lua, every interface): renamed functions
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
- The `server.log` of a running server is locked; the exe is locked while running (stop before rebuild)

## Working agreement

- One task at a time from `task.md`; mark it done with a one-line note of what changed
- Verify with the server log (zero Lua errors) and, for NPCs, `tools\talk-test.ps1`
- Commit after each finished task

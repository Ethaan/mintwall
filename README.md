# mintwall

Tibia 7.4 server (Avesta74) + the original CipSoft 7.4 client.

## Layout
- `server/` - Avesta74 otserv, protocol 7.4, from https://github.com/peonso/avesta74 (source rev102)
  - `src/` C++ source, `data/` game data, `config.lua` server config, `sql/` schema + seed data
  - `data/world/Tibia74.otbm` (+ `-spawns.xml`, `-houses.xml`) - 7.4 real map, 47 towns, 18,665 monster spawns, 816 houses,
    from https://github.com/Inconcessus/Tibia74-JS-Engine (originally 222222's "Authentic 7.4 Real Map", OTLand)
  - `data/world/Fibula.otbm` - small test map from https://github.com/dhustkoder/OTServ74
  - `data/npc/` - 306 NPCs (XML dialogue + scripts) from https://github.com/tibiaot74/otserver, running on
    Jiddo's NpcSystem (`data/npc/lib/`) through a compatibility layer (`data/compat.lua`, `data/npc/lib/compat.lua`)
- `client/Tibia740/` - original 7.4 client (`Tibia740.zip` from https://downloads.ots.me/?dir=data/tibia-clients/windows/zip). Not committed.
- `tools/patch-client.ps1` - writes `client/Tibia740/Tibia-mintwall.exe`, a copy of the client pointing at a given IP
  that also loads `mintwall.dll`
- `client-mod/` - `mintwall.dll`, our client improvements: smooth keyboard walking (no Windows key-repeat
  delay after pressing or changing a direction). Players get `Tibia-mintwall.exe` + `mintwall.dll`.

## Requirements
- Visual Studio 2022 Build Tools (C++), CMake, vcpkg at `C:\vcpkg`

## Setup
```
server\build.bat          :: first run builds all dependencies via vcpkg (slow)
server\init-db.bat        :: creates server\db.db3 (account 111111 / password tibia)
client-mod\build.bat      :: builds mintwall.dll (32-bit)
powershell -ExecutionPolicy Bypass -File tools\patch-client.ps1   :: -Ip <addr> for a non-local server
server\start-server.bat
```
Then run `client\Tibia740\Tibia-mintwall.exe` and log in with 111111 / tibia.

With [mise](https://mise.jdx.dev/) (`winget install jdx.mise`) the same steps are tasks: `mise run build`,
`mise run seed`, `mise run start-server`, plus `restart-server`, `stop-server`, `reseed` (wipes the DB) and `test`.
`mise tasks` lists them.

Port 7171 must be free (the 7.4 client always uses it).

## Changes to upstream Avesta
- Builds with CMake + vcpkg on modern MSVC/Boost: `io_service` -> `io_context`, `to_ulong` -> `to_uint`,
  missing `<sstream>`/`<string>` includes, `round()` clash renamed, `_WIN32_WINNT` 0x0601
- `data/global.lua`: define `TRUE`/`FALSE` (were missing, broke 9 spells)
- `antidote_rune.lua`: fixed misspelled `COMBAT_PARAM_TARGETCASTERORTOPMOST`
- `data/npc/lib/compat.lua` + `data/compat.lua`: TFS-era function names mapped onto Avesta's API
- NPC engine: `<parameters>` in NPC XML + `getNpcParameter(key)`; NPC events no longer expect a boolean return
  (every NPC logged an error per tick); new `isPlayer(cid)`; `getSpectators` multifloor argument optional
- Map loader: reads OTBM v1+ maps (stack counts as attributes); `Demongoblin` monster added; spawn fixes

## Accounts (local testing, from sql/seed.sql)
| Account | Password | Character | Notes |
|---|---|---|---|
| 111111 | tibia | Mintwall | player, starts in Rookgaard |
| 999999 | see sql/seed.sql | GM Mintwall | God group (access 3): /B, /goto, /i, /n, /reload, ... |

## Testing NPCs without the client
```
powershell -ExecutionPolicy Bypass -File tools\talk-test.ps1 -Words "hi,job,bye"
```

## Known gaps
- The Queen of the Banshees and Donald McRonald are greeting-only placeholders
- Bank / marriage / blessing NPC scripts come from a newer server and aren't 7.4 features; parts won't work
- Full map uses ~2.5 GB RAM

# mintwall - tasks

Status: `[ ]` todo, `[~]` in progress, `[x]` done. Add new tasks to the right section as they come up.
When finishing one, tick it and add a short note (what changed / how verified).

## Done

- [x] Pick client: original CipSoft 7.4 client + IP patch (`tools/patch-client.ps1`)
- [x] Pick and build server: Avesta74 on MSVC + vcpkg, static exe
- [x] SQLite database + seed accounts (`init-db.bat`)
- [x] Load 7.4 real map (loader fix for OTBM v1 stack counts)
- [x] Fix monster names in spawns (Bone Beast, Demongoblin)
- [x] Port 306 NPCs with Jiddo NpcSystem + compat layer; verified Cipfried (dialogue) and Al Dee (shop)
- [x] God account (999999, group God, access 3)
- [x] context.md / task.md
- [x] Automated gameplay test suite (tests/): headless 7.4 client, isolated test server, fresh characters
- [x] Oracle: fixed undefined CONST_ME_TELEPORT (compat.lua loaded too early) and wrong town ids
      (now looked up by name); covered by test_rookgaard.py

## New player journey (tests/test_rookgaard.py)

- [ ] Decide the starter kit (items + slots) and give it on first login; then drop the xfail
- [ ] Oracle gives a vocation bag (TFS-era, not 7.4) - keep or remove?
- [ ] Oracle's "SO BE IT" is never seen (player is teleported first) - delay the teleport slightly?
- [ ] More journey tests: rookgaard shops buy/sell with money, sewers/ladders, death in Rookgaard, reaching level 8 via exp

## NPCs

- [ ] Write real dialogue for The Queen of the Banshees (placeholder greets only)
- [ ] Replace Donald McRonald placeholder with his real 7.4 NPC
- [ ] Talk-test every NPC once; log the ones that error or don't answer
- [ ] Boat captains: verify travel destinations/prices are 7.4 (no Liberty Bay/Port Hope etc. if not in 7.4)
- [ ] Guards (Grof, Tim, Kulag, Walter): scripts use `getMonstersfromArea` - implement or rewrite
- [ ] Remove or neutralize non-7.4 NPC features: banks (bank.lua, evabank.lua, Lokur), marriage, blessings, addon outfits
- [ ] Promotion NPCs: verify 7.4 rules (level 20, 20k gp, premium) and that `doPlayerSetPromotionLevel` shim is right
- [ ] Bone-collector NPCs use `doPlayerRemoveBones`/`getPlayerBones` - implement or rewrite
- [ ] Spell-teaching NPCs: check spell lists/prices/levels against 7.4
- [ ] Shop prices: audit buy/sell lists against 7.4 (tibiaot74 data may include 7.72 items)

## Map / world

- [ ] Quests: chests, quest doors, levers (actions/unique ids on the map vs `data/actions`)
- [ ] Houses: confirm `Tibia74-houses.xml` loads, rent, doors, ownership commands
- [ ] Temples: log in to each of the 47 towns' temple positions, confirm walkable
- [ ] Depots and mailboxes (mailboxes weren't in 7.4 - check the map)
- [ ] Teleports, ladders, holes, rope spots, shovel spots work
- [ ] Reduce server memory (~2.5 GB with full map)
- [x] Removed the teleport in Rookgaard temple that sent new players to Thais
      (tools/map-remove-item.py)
- [ ] Audit every teleport on the map against 7.4 (only the Rookgaard one was wrong so far)

## Monsters

- [ ] Audit the 102 spawned monster types: stats, loot, spells vs 7.4
- [ ] Check spawn times/radius are sane for 7.4

## Game rules and formulas

Decide the target for each (real 7.4 or our own choice), write it down here, then add a test.
Current config: RateExp/RateSkill/RateMag/RateLoot/RateSpawn = 1 (real Tibia speed); the
experience stages script (`creaturescripts/scripts/stages.lua`) exists but is not registered.

### Experience and levels
- [ ] Experience per level: confirm `(50*(L-1)^3 - 150*(L-1)^2 + 400*(L-1)) / 3` (Player::getExpForLevel)
- [ ] Experience rate: keep 1x, pick a multiplier, or enable stages (7.4 had no stages)
- [ ] Monster experience: exp from each monster matches 7.4, including exp split when several players attack
- [ ] Level-up gains per vocation: HP / mana / capacity (data/vocations.xml: none 5/5/5, knight 15/5/25...)
- [ ] Level-down on death: losing enough exp removes levels and their HP/mana/cap

### Magic level
- [ ] Mana needed per magic level: `1600 * multiplier^mlvl` with vocation multipliers
      (vocations.xml manamultiplier: sorcerer/druid 1.1, paladin 1.4, knight 3.0, none 4.0)
- [ ] Mana spent counts toward magic level (spells and runes), RateMag applies
- [ ] Magic level shown correctly in the client (stats packet mlvl + percent)

### Skills
- [ ] Skill tries per level: `50 * multiplier^(skill-10)`-style formula per skill and vocation (vocations.xml)
- [ ] Which actions train which skill: melee hits, shield blocks, distance, fishing; RateSkill applies
- [ ] Fist fighting when no weapon; skills start at 10

### Combat formulas
- [ ] Melee damage: attack, skill, level, fight mode (offensive/balanced/defensive)
- [ ] Defense and armor reduction (the Avesta "revbattlesys" formula - compare with 7.4)
- [ ] Distance: hit chance, ammo, range
- [ ] Spell and rune damage formulas (level + magic level) per spell
- [ ] Attack speed (vocations.xml attackspeed 2000 ms) and exhaustion

### Regeneration, food, soul
- [ ] HP/mana regeneration per vocation (gainhpticks/gainmanaticks) and food duration
- [ ] Soul points: did 7.4 have them? (soul came in 7.5 - probably disable)
- [ ] Capacity: item weights and cap limit

### Death and PvP
- [ ] Death penalty: exp / mana / skill / item loss percentages (loss_* columns, default 10)
- [ ] Respawn at home town temple (town_id), bag/items drop rules, blessings do not exist in 7.4
- [ ] Skulls and PZ: PZLock 60 s, KillsToRedSkull 5, KillsToBan 7 - confirm 7.4 values
- [ ] Rookgaard: no PvP on the island (non-pvp zone or protection level)

### Idle and session
- [ ] Idle timeout far too short, warning reads "idle for 0 minutes": IdleTimeWarning 30 s /
      IdleTimeKick 60 s in config.lua and player.cpp prints whole minutes only.
      Real Tibia warned at ~14 min and kicked at ~15 min
- [ ] Idle message wording: "idle for X minutes , you will be" has a stray space

### Premium
- [ ] What premium unlocks in 7.4 (towns, promotion, spells, houses) and how players get it

### Spells, runes, items
- [ ] Verify 7.4 spell list, words, mana, level, vocation, premium (remove post-7.4 spells)
- [ ] Runes: charges, magic level required, soul (7.4 had none)
- [ ] Remove leftover warnings: "Unknown command /invisible, /serverdiag", items.otb minor-version warning

## Branding and client texts

Server-side (config.lua) - editable, current values are Avesta defaults:
- [ ] MOTD shown after entering the account (`MOTD`, bump `MOTD_Num` so clients show it again)
- [ ] Pick the one server/world name and use it everywhere (character list shows "<char> (OpenTibia)",
      MOTD, login message, website, patched client): `WorldName`, `ServerName`, `OwnerName` in config.lua
- [ ] In-game login message (`LoginMsg`, mentions otserv.org) and `ServerName` / `OwnerName`
- [ ] First-login "Welcome to <ServerName>. Please choose an outfit." (protocolgame.cpp sendAddCreature)

Client-side (Tibia.exe) - only by patching strings in the copy we hand out, never longer than the original:
- [ ] Decide if we patch client texts at all (it is the only client change besides the IP patch)
- [ ] Info button text ("Copyright (C) 2002-2004 CipSoft GmbH" - keep CipSoft's copyright)
- [ ] "Check www.tibia.com" references (login servers offline message, hints) -> our website
- [ ] If yes: extend tools/patch-client.ps1 with a text table, plus a test that the patched exe still has the original size

## Accounts / security / ops

- [ ] Change the God account password before anyone else can connect
- [ ] Switch `PasswordType` from plain to sha1 (and seed accordingly)
- [ ] Account creation for players (7.4 had no in-client creation - website or script)
- [ ] Run as a service / auto-restart; backups of db.db3
- [ ] Hosting: public IP, patched client for players (`patch-client.ps1 -Ip ...`)

## Tooling

- [ ] `talk-test.ps1`: support walking/teleporting (GM) so any NPC can be tested without editing the DB
- [x] Smoke test runner: tests\run-tests.bat
un-tests.bat
- [ ] Test every NPC answers "hi" (generated test per NPC)

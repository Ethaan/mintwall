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

## Monsters

- [ ] Audit the 102 spawned monster types: stats, loot, spells vs 7.4
- [ ] Check spawn times/radius are sane for 7.4

## Game rules / spells / items

- [ ] Verify 7.4 spell list, mana, levels, runes (and remove post-7.4 spells)
- [ ] Verify vocations, skill rates, exp stages (7.4 had no stages)
- [ ] Remove leftover warnings: "Unknown command /invisible, /serverdiag", items.otb minor-version warning
- [ ] Death / temple / loss percentages behave like 7.4

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

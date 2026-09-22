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

- [x] 7.4 beginner set on first login (club, torch, bag with a red apple, jacket/coat) and the
      "noob outfit" (head 78, body 69, legs 58, feet 114 - picked in the real client); login creature events
      were never called by the engine - fixed
- [ ] Oracle gives a vocation bag (TFS-era, not 7.4) - keep or remove?
- [ ] Oracle's "SO BE IT" is never seen (player is teleported first) - delay the teleport slightly?
- [ ] More journey tests: rookgaard shops buy/sell with money, sewers/ladders, death in Rookgaard, reaching level 8 via exp

## NPCs

- [x] Tom: selling lost the item and paid nothing on every NPC (broken shop helpers in global.lua);
      dead rabbit id 2992 -> 3119 (the corpse rabbits leave). test_rookgaard.py
- [x] Rookgaard NPC tests - all 19 NPCs, 107 tests pass (full suite ~6 min)
  - [x] 1. tests/test_npcs_rookgaard.py, generated from each NPC's XML/script (tibia74/npcs.py): every
        keyword gets its reply, every item can be bought / sold for its listed price (checked in the
        saved character). Test characters are in a test-only unmutable group (fast talk gets muted)
  - [x] 2. tests/test_npc_data.py: shop item ids exist and match their names; what an NPC buys can be
        obtained (monster corpse/loot or a shop)
  - [x] 3. hand-written: quest trades (Al Dee pick, Billy pan, Amber book, Lee'Delle honey flower,
        Seymour present), Seymour's Key to Adventure (action id 4600), Blind Orc, healers (heal to 65)
  - Bugs found and fixed on the way:
    - default.lua (121 NPCs) bought and sold a sample axe
    - keyword matching (all NPCs): capitalised keywords never matched; substrings matched ("sell" in
      "counsellor"); random order let "axe" answer "buy hand axe" -> whole words, most specific first
    - NPC texts: 8.x {keyword} braces stripped in selfSay (Oracle: "{CARLIN}")
    - Norma: buy/sell dialogue keywords hijacked her shop; egg was a phoenix egg (2328 -> 2695)
    - Al Dee/Dixi/Obi: sold "axe" paid for a hand axe (2380 -> 2386); "sttuded shield"; Dixi/Obi sold
      worms (item 3976 does not exist in 7.4)
    - Blind Orc: <interaction> XML is not supported by Avesta - he never spoke; ported to blind_orc.lua
- [x] The Gatekeeper (Rookgaard premium side, 32035,32183,6 - the map's blackboards describe him): the
      premium Oracle (Ankrahmun, Darashia, Edron). Ankrahmun and Edron had swapped town ids (respawn in
      the wrong city) - now looked up by name, destination = the town's temple. test_rookgaard.py
- [ ] Gatekeeper and Oracle hand out vocation starter kits (TFS-era) - 7.4 had none? (reference task)
- [ ] Questions for the 7.4 reference: did Lee'Delle sell footballs (111 gp)? Seymour buys dead rats?
      Norma's lines are 8.x ("ask me for a trade"); NPC muting when talking fast to NPCs
- [ ] After the Rookgaard NPC tests: gather a 7.4-era reference (prices, NPC dialogue, spell lists)
      from a source like TibiaWiki's history/archived pages, store it in the repo and compare our NPCs
      against it (then the same for the other towns)
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
- [x] King's Bridge (Rookgaard, 32057,32192-32193,7): action id 50003 = premium-only ground, nothing
      handled it; movements/scripts/premium_tile.lua sends free accounts back. test_rookgaard.py
- [x] Locked doors without a key (action id 0) opened for anyone (door_locked.lua: "impossible to
      happen") - e.g. 32042,32205,6, the way onto Rookgaard's premium side around King's Bridge. Now
      only house doors open that way (the engine checks house access first). Item 1210 (the unlocked
      closed door) was described as "It is locked." test_rookgaard.py
- [ ] House doors: test that owners/invited players can open them and others cannot (Houses task)
- [x] Rookgaard sewer bridge levers (action id 50001, 32098/32104,32204,8): ported upstream's
      rat bridge as `rook_rat_bridge.lua`; covered by test_rookgaard.py
- [ ] Other map action ids with no script behind them (50001 had none) - list and port them

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
- [x] Idle timeout: warned at 30 s and kicked at 60 s, so the warning read "idle for 0 minutes"
      (whole minutes only) -> config.lua IdleTimeWarning 14 min, IdleTimeKick 15 min, like real Tibia
- [x] Idle message wording: "...idle for 14 minutes. You will be disconnected in 1 minute if you are
      still idle." (was "minutes , you will be"; player.cpp, needs a rebuild)

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
- [ ] Decide if we patch client texts at all (besides the IP patch and loading mintwall.dll)
- [ ] Info button text ("Copyright (C) 2002-2004 CipSoft GmbH" - keep CipSoft's copyright)
- [ ] "Check www.tibia.com" references (login servers offline message, hints) -> our website
- [ ] If yes: extend tools/patch-client.ps1 with a text table, plus a test that the patched exe still has the original size

## Walking smoothness

- [x] Measure it: `tools/walk-trace.py` (mise run walk-trace) - logging proxy with the real client.
      Found: after every new direction the client waited Windows' key-repeat delay (~500 ms)
- [x] Client fix: `client-mod/mintwall.dll` repeats movement keys itself (no initial delay, last held
      key wins), loaded by Tibia-mintwall.exe through an added import. Confirmed in game
- [x] Server: TCP_NODELAY on game sockets (Nagle could hold a step confirmation back) - server.cpp
- [x] Stairs: every floor change doubled the next step (lastStepCost 2): ~900 ms instead of ~450 off
      each stair while the real client asks after the normal time (walk-trace) - creature.cpp
- [x] Diagonals: the wait before a step also counted the *next* step's direction, so straight->diagonal
      waited 2x and diagonal->diagonal 4x (1.7 s) - Creature::getWalkDelay / getStepDuration(dir)
- [x] 1 ms timer resolution (timeBeginPeriod): steps landed up to ~100 ms early/late - otserv.cpp
- [x] tests/test_walking.py: pace on a road (straight + diagonals) and up/down stairs
- [ ] A step pressed while another is queued replaces it (Player::setNextWalkTask) - dropped steps when
      tapping back and forth (seen in the stairs trace); queue one step instead?
- [ ] Re-trace with the real client on the new server (walk-trace summary: steps more than 50 ms late)

## Accounts / security / ops

- [ ] Change the God account password before anyone else can connect
- [ ] Switch `PasswordType` from plain to sha1 (and seed accordingly)
- [ ] Account creation for players (7.4 had no in-client creation - website or script)
- [ ] Run as a service / auto-restart; backups of db.db3
- [ ] Hosting: public IP, patched client for players (`patch-client.ps1 -Ip ...`)

## Tooling

- [ ] `talk-test.ps1`: support walking/teleporting (GM) so any NPC can be tested without editing the DB
- [x] Smoke test runner: tests\run-tests.bat
- [x] mise tasks (`mise.toml`): build, seed, reseed, start/stop/restart-server, test
- [x] God group sees ID / action id / Position on look (flag bit 42; enable "Show Info Messages
      in Console" in the client to copy them)
un-tests.bat
- [ ] Test every NPC answers "hi" (generated test per NPC)

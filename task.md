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
- [x] God account (9 / 9, group God, access 3)
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
- [ ] Remove or neutralize non-7.4 NPC features: banks (bank.lua, evabank.lua, Lokur), marriage, addon outfits
- [ ] Promotion NPCs: verify 7.4 rules (level 20, 20k gp, premium) and that `doPlayerSetPromotionLevel` shim is right
- [ ] Bone-collector NPCs use `doPlayerRemoveBones`/`getPlayerBones` - implement or rewrite
- [ ] Spell-teaching NPCs: check spell lists/prices/levels against 7.4
- [ ] Shop prices: audit buy/sell lists against 7.4 (tibiaot74 data may include 7.72 items)

## Map / world

- [ ] Quests: chests, quest doors, levers (actions/unique ids on the map vs `data/actions`)

## Quests (each one needs an end-to-end test)

The test for a quest starts a strong character (e.g. level 2000: fast, survives) in a temple and does the whole
quest the way a player would: walk / travel there, level doors, levers, keys, talk to NPCs, open the reward
chest, and check the reward is in the backpack (and that the chest cannot be opened twice). Needs test-client
helpers: route walking across floors (stairs, ladders, holes, rope spots), pulling levers, opening doors.

- [x] Research: 97 quests of 7.4 with rules, steps, rewards and sources - docs/reference-74/quests.md
      (top: what our map already has - chests use action id 2000 + unique id, none are scripted yet)
- [x] Quest chest system: data/actions/scripts/quests/system.lua for action id 2000 (unique id = storage; reward =
      the unique id when it is an item id, else a copy of the chest contents incl. key action ids; once per
      player; a reward you cannot carry stays). tests/test_quests.py (rapier box, Amber's chest)
- [x] Quest test framework: tibia74/worldmap.py (walkability + floor changes + doors from the engine's own
      rules, cached), tibia74/route.py (A* across floors: stairs, holes, ramps, ladders, rope, doors a character
      may pass; walks it, kills blockers, re-plans), tibia74/quest.py (strong character, use map items like a
      player - the server uses the TOP item, so things lying on top are moved off first). tests/test_route.py
  - [ ] Parallel runs later (pytest-xdist, one server per worker)
- [x] Rookgaard Academy training arena: four levers (aid 50005-50008, 32088-32094,32148,9) under the sign "Pull a
      lever to fight a monster of your choice" had no script. Done 2026-09-23: quests/rook_academy_arena.lua opens
      the cage gate (1037 at x,32149,10; tibiaot74's train monster1-4.lua) and, as the sign says, only one gate at
      a time ("Sorry, not possible." - no source for the message). test_quests.py::test_academy_training_arena
      (buys Seymour's key 4600 for the Academy door). Map fix: the field into the arena (32089,32171,9) sent you
      onto the field beside it, which sent you straight back out - nobody could get in (the JS engine's map has the
      same data). Destination now (32081,32172,9) as on tibiaot74's map; test_route.py checks no teleport lands on
      another (the only such case of 168)
- [ ] Quest log: the 7.4 client has none (TibiaWiki: added in 7.9) - revisit later (e.g. a !quests command or the website)
- [ ] Settle reward / level conflicts per quest (Tibiantis vs TibiaWiki, see quests.md) as each one is done

One per quest (rules from quests.md; each: research check -> map/script work -> end-to-end test):
- [x] Bear Room Quest - Rookgaard, orc/minotaur cave north of town (level none known (listed as 2); 1 player)
      Done 2026-09-23: rewards table (52148 arrows + gold, 20003 key 4601) in quests/system.lua, stone switch
      52413 (quests/rook_bear_room.lua); test_quests.py::test_bear_room_quest does it from the temple. Map quirk:
      a (daily-loot) chest lies ON the switch tile, so clicking the switch opens the chest - move it off first.
      Decided 2026-09-23: keep it (part of the map; players can move it)
- [x] Present Box Quest + Legion Helmet Quest - chest by stone switch on Bear Room level; NPC Seymour (Acad… (level none known (listed as 2); 1 player)
      Done 2026-09-23: chest 52149 reward (backpack: present, jug, plate, cup) in quests/system.lua; Seymour:
      per-player conversation state (was global), box talk from level 6 (TibiaWiki 2006; was 4), mission/quest
      precedence fixed. test_quests.py::test_present_box_quest (+ level 5/6 test). Found: seymour.lua did not
      load after an edit and Seymour vanished silently - test_spells.py now fails on any script load error
- [x] Captain Iglues Treasure Quest - Rookgaard, under the poison spider tower (N) (level none known (listed as 2); 1 player)
      Done 2026-09-23: quest chest 52171 = 2 salmon (reward table; the left chest on our map is the daily one with
      the stamped letter + 12 salmon, as the current wiki says); Amber takes a salmon for 'pixo'.
      test_quests.py::test_captain_iglues_treasure_quest. Framework: planner widens its search box (the way
      down left the old 60-tile box); talk_to says bye and waits out the anti-spam mute like a player
- [x] Combat Knife Quest - Rookgaard town sewer (no level; 1 player)
      Done 2026-09-23: box uid 2404 (= the knife). test_quests.py::test_combat_knife_quest
- [x] Doublet Quest - cellar under stable north of Tom's shop (no level; 1 player)
      Done 2026-09-23: 7.4 has no loose-board item - the board is the wooden flooring west of the sewer grate
      (32084,32181,8) under a barrel, as on tibiaot74's map (uid 7014 there). New tools/map-set-attrs.py gave it
      aid 2000 uid 2485 (= the doublet). test_quests.py::test_doublet_quest pushes the barrel off and uses the floor
      Engine fix: using a tile with nothing on it now uses its ground (game.cpp internalGetThing STACKPOS_USEITEM
      fell through to "Sorry, not possible.")
- [x] Dragon Corpse Quest - bear cave east of town (level none known (listed as 2); 1 player)
      Done 2026-09-23: dead dragon uid 54322 = bag (copper shield, legion helmet) in the reward table; the router now
      digs stone piles (shovel) and cuts wheat (scythe). test_quests.py::test_dragon_corpse_quest
- [x] Goblin Temple Quest - premium side: troll cave to goblin temple (no level; 1 player; premium)
      Done 2026-09-23: chests 52169 (sandals, 5 small stones, 50 gp) / 52170 (pan, 4 snowballs, milk) in the reward
      table - wiki 2005/2006/current + Tibiantis say 50 gp, the real-map table 100 (4 against 1).
      test_quests.py::test_goblin_temple_and_antidote_rune_quests (premium, shovel)
- [x] Antidote Rune Quest (modern: Small Health Potion Quest) - NPC Billy, premium side (no level; 1 player; premium)
      Done 2026-09-23: the goblin temple pan -> Billy (hi, pan, yes) -> antidote rune, in the same test
- [x] Katana Quest - graves then rotworm/skeleton cave (level none known (listed as 2); 1 player)
      Done 2026-09-23: body uid 20002 = silver key 4603 (reward table); hidden lever aid 52412 unlocks the room door
      (1209 <-> 1210) and puts an escape teleport inside while locked (quests/rook_katana_lever.lua, positions from
      tibiaot74); corpses 2412 katana / 2473 viking helmet. The key body lies under two others: uncover it first.
      test_quests.py::test_katana_quest
- [x] Minotaur Hell Quest - main cave north of town, bottom floor (level none known (listed as 2); 1 (group advised) player(s))
      Done 2026-09-23: boxes 2395 carlin sword, 52159 = 4 poison arrows + 10 arrows (reward table), 2580 fishing rod.
      test_quests.py::test_minotaur_hell_quest
- [x] Small Axe Quest + Pick Quest - skeleton cave (premium) or respawn spots; Al Dee (level none (Pick listed as 2); 1 player)
      Pick trade: test_quests.py::test_pick_quest (small axe from the daily orc-cave box -> Al Dee).
      Done 2026-09-23: the once-only coffin is 1742 at 31984,32246,10 (tibiaot74's map: uid 7026 on it); now aid
      2000 uid 2559 (= the small axe). test_quests.py::test_small_axe_quest (premium)
- [x] Rapier Quest - town sewer, west, one floor down (no level; 1 player)
      Done 2026-09-23: box uid 2384 (= the rapier). test_route.py walks from the temple and opens it
- [x] Amber's Notebook Quest + Short Sword Quest - chest on east dock; Amber (Academy) (level none (trade listed as 2); 1 player)
      Done 2026-09-23: dock chest 20001 holds black book 1972 (our map) - Amber accepts it and tibiaot74's 1955 (same
      sprite; the real-map table's 1950 is a brown book). test_rookgaard_trade_quest[amber's notebook]
- [x] Honey Flower Quest + Studded Legs Quest - wasp tower NW; Lee'Delle (premium side) (level none (trade listed as 2); 1 player)
      Done 2026-09-23: flower uid 2103 on the wasp tower (rope; the router drags corpses off the rope spot),
      Lee'Delle across her counter (premium). test_rookgaard_trade_quest[honey flower]
- [x] Banana Quest + Studded Shield Quest - banana palm NE (free) or premium wolf hill; Willie (level none (trade listed as 2); 1 player)
      Done 2026-09-23: palm uid 2676 = banana, Willie (free account). test_rookgaard_trade_quest[banana]
      Wolf hill palm: it IS on our map, on the plateau at 31983,32193,5 (floor 6 is the "flat part"); now aid 2000
      uid 52414, which quests/system.lua (SAME_QUEST) maps to the first palm's storage 2676.
      test_quests.py::test_banana_quest_wolf_hill_palm stacks 3 boxes, climbs, and the NE palm is then empty.
      QUESTION for the user: no movable boxes lie anywhere near the hill on our map - where do players get the 3
      boxes? (the test brings its own)
- [x] Torch Quest - Rookgaard Academy basement (no level; 1 player)
      Done 2026-09-23: academy lever aid 50004 opens the brick wall at 32095,32173,8 (quests/rook_academy_lever.lua;
      wall position from tibiaot74's academy switch); chest uid 2050 = torch. test_quests.py::test_torch_quest
- [ ] Battle Axe Quest - Thais sewers (SW) (no level; 1 player)
- [ ] Dead Archer Quest - Thais Troll Cave (E of Thais) (no level; 1 player)
- [ ] Deeper Fibula Quest - Fibula dungeon (level 50 (door); 1 player)
- [ ] Devil Helmet Quest - Thais Ancient Temple to Mintwallin (level 30 (door); 2+ (one player holds a floor … player(s))
- [ ] Geomancer Quest - Mount Sternum undead cave (N of Thais) (no level; 1 player)
- [ ] Ghoul Room Quest - Thais Ancient Temple (no level; 1 player)
- [ ] Kingdom of Kormarak Quest (Old Mintwallin) - Thais Ancient Temple (no level; 1 player)
- [ ] Life Ring Quest - Thais Ancient Temple (S branch) (no level; 1 player)
- [ ] Mad Mage Room Quest - Thais Ancient Temple, toward Mintwallin (level 40 (door); 1 player)
- [ ] Mintwallin Cyclops Quest - Thais Ancient Temple, cyclops room (no level; 1 player)
- [ ] Naginata Quest - Thais Dragon Lair (N of Alatar Lake) (level 40 (door); 1 player)
- [ ] Noble Armor Quest (Skjaar/DTD) - below Mount Sternum (level 35 (door); 1 player)
- [ ] Scale Armor Quest - cave W of Ancient Temple entrance (no level; 1 player)
- [ ] Silver Amulet Quest - Thais Troll Cave cellar (no level; 1 player)
- [ ] Six Rubies Quest (Double Dragon) - Thais Ancient Temple (no level; 1 player)
- [ ] Small Ruby Quest - Mintwallin throne room pit (no level; 1 player)
- [ ] Spike Sword Quest (Fire Devil) - cave E of Mount Sternum / NE of Triangle Tower (no level; 1 player)
- [ ] Thais Lighthouse Quest (Dark Shield) - Thais lighthouse, SW of Thais (no level; 2 (step switch + lever) player(s))
- [ ] Throwing Star Quest - Thais Ancient Temple, underground park (no level; 1 player)
- [ ] Triangle Tower Quest - Triangle Tower (E of Thais, desert edge) (no level; 1 player)
- [ ] Giant Smithhammer Quest - Plains of Havoc cyclops/minotaur camp (no level; 1 player)
- [ ] Ornamented Shield Quest - Plains of Havoc Dragon Lair (no level; 1 (part 1); 2 (part 2) player(s))
- [ ] Alawar's Vault Quest - Senja / Folda (ice islands N of Carlin) (no level; 1 player)
- [ ] Crystal Wand Quest (Double SD Quest) - Demona, via Maze of Lost Souls (N of Carlin) (level 60 (door); 1 player)
- [ ] Demona Ring Quest - Demona (level 60 (Demona gate); 1 player)
- [ ] Fanfare Quest - Carlin graveyard crypt (no level; 1 player)
- [ ] Griffin Shield Quest (MoLS Quest) - Gates of Demona, Maze of Lost Souls (level 30 (not a door, see notes); 1 player)
- [ ] Power Ring Quest (Bronze Amulet / Femor Hills Goblin) - Femor Hills goblin cave (no level; 1 player)
- [ ] Purple Tome Quest (Map Quest) - Demona library (level 60 (Demona gate); 1 player)
- [ ] The Queen of the Banshees Quest (Banshee Quest) - Under Ghostlands and Isle of the Kings (level 60 (Queen refuses <60); 1+ (easier with a team; seal … player(s))
- [ ] The White Raven Monastery Quest (Family Brooch Quest / Island of King… - Ghostlands W of Carlin, Isle of the Kings (no level; 1 player)
- [ ] Draconia Quest - Draconia, via Hellgate under Ab'Dendriel (level 25 (door); 2 minimum (floor switches) player(s))
- [ ] Elvenbane Quest (Elf Castle Quest) - Elvenbane castle, SW of Ab'Dendriel (no level; 1 player)
- [ ] Orc Fortress Quest - Orc Fortress, W of Ab'Dendriel (level 40 (door); 1 player)
- [ ] Circle Room Quest (Dwarven Quest / Dwarf Hell Quest) - Dwarf mines W of Kazordoon (level 32 (door); 1 player)
- [ ] Crusader Helmet Quest - Deep Dwarf Mines W of Kazordoon (level 35 (door); 1 player)
- [ ] Emperor's Cookies Quest - Emperor Kruzak's chambers, Kazordoon (no level; 1 player)
- [ ] Explorer Brooch Quest - Jolly Axeman tavern sewer, Kazordoon (no level; 1 player)
- [ ] Iron Hammer Quest - Minotaur cave W of Kazordoon (no level; 1 player)
- [ ] Longsword Quest - Troll cave E of Dwarf Bridge (no level; 1 player)
- [ ] Steel Helmet Quest (Minotaur Tower Quest) - Minotaur tower W of Kazordoon (no level; 1 player)
- [ ] The Paradox Tower Quest - Paradox Tower, near Kazordoon (+ PoH, Edron, Carlin, Thais,… (level 30; 1 player; premium)
- [ ] Black Knight Quest (Crown Set) - Villa Scapula swamp, north of Venore (~32827,31959,7) (level 50 (door); 1+ player(s))
- [ ] Blood Herb Quest (Witchesbroom) - Greenclaw Swamp, west of Venore (no level; 1 player)
- [ ] The Desert Dungeon Quest (Desert / Vocation / 10k Quest) - Below Jakundaf Desert (entrance ~32649,32093,7) (level 20 (door); 4, one of each vocation player(s); Knight + Paladin + Druid + Sorcerer)
- [ ] Dragon Tower Quest - Shadowthorn, south-east of Venore (no level; 1 player)
- [ ] Heaven Blossom Quest - Shadowthorn underground (no level; 1 player)
- [ ] Iron Helmet Quest (Muriel's Letter) - Plains of Havoc, west of the cyclops/orc/minotaur camp (~32… (no level; 1 player)
- [ ] Isle of the Mists Quest (Druid Quest) - Isle of the Mists; teleport in PoH (~32831,32295,7) (no level; 1 player; druid, per the quest legend (the wiki d…)
- [ ] Orc Shaman Quest - Swamp/orc cave east of Venore (~33055,32030,7) (no level; 1 player)
- [ ] The Outlaw Camp Quest (Bright Sword Quest) - Outlaw Camp, west of Thais/Venore road (~32615,32253,7) (level 45 (door); 1 (2 recommended) player(s))
- [ ] Panpipe Quest (Fire Devil Quest) - Desert Dungeon, Jakundaf Desert (no level; 1 player)
- [ ] Power Bolts Quest - Hole south of the PoH temple (~32815,32280,7) (no level; 1 player)
- [ ] Silver Brooch Quest (Mummy Quest) - Greenclaw Swamp caves (~32700,31992,7) (no level; 1 player)
- [ ] Skull of Ratha Quest (incl. Wolf Tooth Chain and Crystal Necklace) - Amazon Camp, north of Venore (~32846,31920,7) (no level; 1 player)
- [ ] Time Ring Quest (Shadowthorn Quest) - Shadowthorn underground (~33060,32182,7) (no level; 1 player)
- [ ] Voodoo Doll Quest - Greenclaw Swamp, north side (~32737,31953,7) (no level; 1 player)
- [ ] Medusa Shield Quest (Star Room / Necromancer Quest) - Drefia, west of Darashia (~32996,32413,7) (level 60 (door); 1+ (team advised) player(s); premium)
- [ ] Plate Armor Quest (Ghost Ship) - Ghost Ship, random on the Venore to Darashia boat (no level; 1 player; premium)
- [ ] Stealth Ring Quest (Minotaur Pyramid) - Minotaur (Dark) Pyramid, north-east of Darashia (~33312,322… (no level; 1 player; premium)
- [ ] The Ancient Tombs Quest (Helmet of the Ancients) - 8 Ankrahmun tombs (level 75 (doors); team advised player(s); premium)
- [ ] The Djinn War - Efreet Faction (Green Djinn Quest) - Mal'ouquah + Ankrahmun, Carlin, Thais, Ulderek's Rock, Asht… (level 30 (fortress door) / 40 (Orc King door); 1 player; premium)
- [ ] The Djinn War - Marid Faction (Blue Djinn Quest) - Ashta'daramai + Kazordoon, Mal'ouquah, Ulderek's Rock (level 30 / 40; 1 player; premium)
- [ ] Serpentine Tower Quest / White Pearl Quest (one quest) - Serpentine Tower (Sorcerer guild), Ankrahmun (~33147,32866,… (no level; 1 player; premium)
- [ ] Annihilator Quest - Edron, Hero Cave (deepest floors) (level 100 (lever/tiles; level-100 door at que…; exactly 4 player(s); premium)
- [ ] Behemoth Quest - Edron, Cyclopolis (deep) (level 60 in 2004 (level door; raised to 80 in…; 1+ (team advised) player(s); premium)
- [ ] Vampire Shield Quest - Edron, Hero Cave (Warlock room / Temple of Xayepocax) (level 70 (level door); 1+ player(s); premium)
- [ ] Demon Helmet Quest - Edron, Hero Cave → Demon Hell (level 100 (level door); team (4 demons + banshees in … player(s); premium)
- [ ] Parchment Room Quest - Edron, Hero Cave (no level; 1+ (5 demons) player(s); premium)
- [ ] Ring Quest - Edron, Hero Cave (no level; 1+ player(s); premium)
- [ ] Wedding Ring Quest (Hero Cave) - Edron, Hero Cave (no level; 1+ player(s); premium)
- [ ] Double Hero Quest - Edron, Hero Cave (no level; 1+ player(s); premium)
- [ ] Triple UH Rune Quest (now "Adorned UH Rune Quest") - Edron, Hero Cave (no level; 1+ player(s); premium)
- [ ] Barbarian Axe Quest - Edron Orc Cave (bottom) (no level; 1+ player(s); premium)
- [ ] Berserker Treasure Quest - Edron Orc Cave (no level; 1+ player(s); premium)
- [ ] Dark Armor Quest - Edron Orc Cave (giant spider pit) (no level; 1+ player(s); premium)
- [ ] Poison Daggers Quest - Edron Orc Cave (shaman level) (no level; 1+ player(s); premium)
- [ ] Shaman Treasure Quest - Edron Orc Cave (room with a Sacrificial Stone) (no level; 1+ player(s); premium)
- [ ] Edron Goblin Quest - Edron Goblin Cave, west of town (no level; 1 player; premium)
- [ ] Troll Cave Quest - Edron Troll Cave, west of town (no level; 1 player; premium)
- [ ] Fire Axe Quest - Edron Dragon Lair (level 60 (level door); 1+ player(s); premium)
- [ ] Postman Missions Quest - starts at Kevin (post office between Thais and Kazordoon), … (no level; 1 player; premium)
- [ ] Iron Ore Quest - Dwarf Mines near Kazordoon (no level; — player(s); —)
- [ ] Minotaur Leather Quest - raft south of Thais (no level; — player(s); —)

- [ ] Dalbrect (boat to the Isle of the Kings, west of Carlin, 32206,31756): he only sails for players who
      brought his family brooch (item 2318), but there is no way to get it - in the Ghostlands there is a spot
      you click (use) to find it. Make that work + test: brooch -> Dalbrect -> 10 gp -> Isle of the Kings
  - [ ] dalbrect.lua: the "blood stains" check never blocks (hasCondition(...) ~= 1: the engine returns
        true/false); talk_state is a global shared by every player talking to him
  - [ ] Widen tests/test_spells.py's script scan: also `== 1` / `~= 1` / `== 0` on functions that return
        true/false (the same bug class as isInArray(...) == TRUE)
- [ ] Houses: confirm `Tibia74-houses.xml` loads, rent, doors, ownership commands
- [ ] Temples: log in to each of the 47 towns' temple positions, confirm walkable
- [ ] Depots and mailboxes (mailboxes weren't in 7.4 - check the map)
- [ ] Teleports, ladders, holes, rope spots, shovel spots work
- [ ] Reduce server memory (~2.5 GB with full map)
- [x] Removed the teleport in Rookgaard temple that sent new players to Thais
      (tools/map-remove-item.py)
- [x] Removed the teleport next to the Thais temple (32366,32235,7) that sent players to the
      Rookgaard temple; a full-map scan found no other mainland teleport into Rookgaard. test_travel.py
- [ ] Audit every teleport on the map against 7.4 (two wrong ones so far, both to/from Rookgaard)
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
- [x] Experience works (the 2026-09-22 report was a false alarm). Pinned by
      test_rookgaard.py::test_killing_a_rat_gives_experience_and_a_level_up: 99 exp + a rat (5) ->
      level 2, "You advanced from Level 1 to Level 2.", more max hp
- [ ] Experience per level: confirm `(50*(L-1)^3 - 150*(L-1)^2 + 400*(L-1)) / 3` (Player::getExpForLevel)
- [ ] Experience rate: keep 1x, pick a multiplier, or enable stages (7.4 had no stages)
- [ ] Monster experience: exp from each monster matches 7.4, including exp split when several players attack
- [ ] Level-up gains per vocation: HP / mana / capacity (data/vocations.xml: none 5/5/5, knight 15/5/25...)
- [ ] Level-down on death: losing enough exp removes levels and their HP/mana/cap

### Magic level
- [ ] Rookie (no vocation) magic level multiplier is 4.0; 7.4 used 3.0 (TW-Formulae, one source)
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
- [x] Attack speed (vocations.xml attackspeed 2000 ms) and exhaustion (exhaustion done 2026-09-23, §9)

### Regeneration, food, soul
- [ ] HP/mana regeneration per vocation (gainhpticks/gainmanaticks) and food duration
- [ ] Soul points: did 7.4 have them? (soul came in 7.5 - probably disable)
- [ ] Capacity: item weights and cap limit

### Death and PvP
- [ ] Revisit the death rules (not a bug - make sure every 7.4 rule is applied), research first like
      the formulas (docs/reference-74), then pin each rule with a test:
  - [ ] Experience / magic level / skills: 10%, promoted characters 7% (Player::getDeathLossFactor)
  - [ ] Levels lost with their HP / mana / capacity
  - [ ] Items: which slots can drop and how likely; the backpack/containers; what stays in the corpse
  - [ ] Amulet of loss: keeps all items, is used up; does it also apply to exp/skills? (7.4: items only?)
  - [ ] Skulls: red skull (and white?) - does the amulet of loss still work, are all items lost?
  - [ ] Promotion kept or lost on death; premium ending while promoted
  - [ ] Where you respawn (home town temple), with what health/mana
  - Research done: docs/reference-74/death.md. Already right: 10% / 7% promoted, level loss, containers
    100%, other items 10%, amulet of loss (items only, used up, fails under red skull), respawn full hp/mana.
    To fix, ranked:
  - [x] 1. Red skull: 7.4 = 3 kills a day / 5 a week / 10 a month, lasts 30 days, ban at 6/10/20
        (ours: 5 kills ~a day, fades with the kills, ban at 7 - config.lua, player.cpp:3779-3834)
  - [x] 2. Promotion is suspended while premium is off (7% loss, regeneration) - ioplayer.cpp:183-187
        checks an empty Account and never runs
  - [x] 3. Sent to Rookgaard: sendToRook() gives the starter set before the corpse drops the loot, so the
        new backpack lands in the mainland corpse
        Done 2026-09-22: player_kills table + day/week/month counts (Player::addUnjustifiedDead, !frags);
        IOPlayer::loadPlayer plays a promoted free account as its base vocation and saves the promotion;
        Player::dropLoot skips the drop on a death that sends to Rookgaard. tests/test_death.py
  - [x] 4. Blessings existed in 7.4 (since 7.2): 5 x 10k gp, each -1% exp/skill loss (to 5%, promoted 2%),
        no item protection, all lost on death. Done 2026-09-22: storage 30011-30015, Player::getDeathLossPercent;
        one word of the name is enough (lib/npc.lua addBlessingKeywords). Norf (Thais) spiritual shielding,
        Humphrey (Carlin) embrace of tibia, Edala (Ab'Dendriel) fire of the suns, Eremo (via Cormaya)
        wisdom of solitude, Kazordoon spark of the phoenix in two parts: Kawill (free) then Pydar (10k).
        Tests: each NPC takes 10000 and blesses once, Pydar refuses without Kawill, bought blessing -> 9%
        and gone after death, 10/5/7/2% loss
  - [x] 5. White skull 15 min instead of 3 (WhiteSkullTime = 15)
  - [x] 6. Per-character loss_* columns are no longer read (IOPlayer::loadPlayer)
- [ ] Respawn at home town temple (town_id), bag/items drop rules
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

## Spells and runes (found while making the Centurion test character)

- [x] rope, shovel, pick, keys (key.lua), bread, instruments, decaying items called isIntegerInArray, which did not
      exist - every use failed. Defined in compat.lua. tests/test_spells.py now fails on any call to a function
      nothing defines (tibia74/luascan.py), with the known ones listed below (the list may only shrink)
- [ ] Undefined functions still called (KNOWN_UNDEFINED in tests/test_spells.py):
  - [ ] getPlayerPromotionLevel - the NPC promotion module: promotion probably fails (see Promotion NPCs)
  - [ ] broadcastMessage - raid announcements, death/kill broadcast scripts
  - [ ] GM ban manager: addAccountBan, addPlayerBan, removeAccountBan, removePlayerBan, getAccountBanList,
        getPlayersByAccountNumber
  - [ ] doNpcSellItem, getPlayerPVPBlessing, getPlayerLookDir (NPC system / functions.lua leftovers)
  - [ ] marriage + banks (not 7.4): remove with the "non-7.4 NPC features" task

- [x] Exhaustion vs 7.4 (docs/reference-74/formulas.md §9): attack 2 s, strikes 1 s, healing/support 1 s and
      the 1 s use delay were right. Fixed: UH / IH runes gave 1 s (7.4: none), paralyze rune 2 s (7.4: 1 s),
      fluids were blocked while exhausted (7.4: drinkable). tests/test_exhaustion.py measures each one

- [x] exani tera never worked, and neither did destroy field, animate dead, traps, house isPlayer checks or
      the healers' fire/poison cure: scripts compared engine booleans with TRUE (= 1), and spell scripts
      returned the undefined LUA_NO_ERROR ("Expected boolean type parameter"). Fixed in 20 scripts;
      tests/test_spells.py pins exani tera and both patterns

- [x] Sudden death rune could be thrown too far away (reported 2026-09-22): the rune range check was right
      (+-7 / +-5 = the 7.4 screen, line of sight - Actions::canUseFar), but Game::playerUseItemEx walked the
      caster towards an out-of-range target and threw from there, so an SD hit 8+ tiles away. Runes now
      fail with "Too far away." tests/test_spells.py: hits at 7, refused at 8
      The report was really about "Too far away." on screen: the infinite test runes (action id 64000) got
      infinite_fluid.lua's adjacent-only range. Actions::getAction skips that action id on runes (it only
      keeps the charges). Tested with normal and infinite SDs. Battle list on players is refused on purpose
      (7.4: "You are not allowed to shoot directly on players"), on monsters it works
- [x] Paralyze rune (adana ani, 2278) vs 7.4 (Tibiantis-notes speed page, tibiantis.info spell list):
      speed set to 40 whatever the level for ~10 s - ours was speed 0 (could not walk) for 60 s. Fixed in
      paralyze_rune.lua. Already right: haste cancelled, healing spells/runes and haste remove it (mass
      healing now too), speed items still add, no skull for the caster, druids use it at ml 18, make at
      ml 35. Exhaustion 1 s (§9). tests/test_paralyze.py
  - [x] Mana to use: 600 (Tibiantis; was 0), making stays 900 (Tibiantis-notes: real 7.4). Chosen 2026-09-23
  - [x] Monsters immune to paralyze vs 7.4 (Tibiantis-notes creature data, NoParalyze): all match except
        Dwarf Geomancer, which was immune - fixed. The 30 monsters without 7.4 data are not checked
- [x] Haste (Tibiantis-notes speed): utani hur base x 1.3 - 24 for 66 s, utani gran hur base x 1.7 - 56 for
      44 s, rounded DOWN to an even number. Ours was 40 s / 45 s and rounded up (level 100: 520 vs 518).
      Fixed: haste.lua / strong_haste.lua ticks, ConditionSpeed::formulaSpeedDelta. tests/test_haste.py
- [x] Wild growth: 7.4 has the instant spell exevo grav vita, not a rune (the rune came later). Druids only
      and one per tile were already right; the machete could not cut anything (machete.lua called an
      undefined isIntegerInArray with undefined tables) - rewritten: cuts rush wood and jungle grass.
      Mana: kept at 220 (Tibiantis charges 150) - decided 2026-09-23
- [ ] Royal paladin: bolts / crossbow and arrows / bow distance (range, hit chance - see 5b in the
      formulas list), damage with the 7.4 formula; test with Legolas (6 / 6)
- [ ] Spears: range, breaking/dropping on the ground, stacking, damage vs 7.4

- [ ] Spell values the research lists as higher than 7.4 but did not rank: fireball (16-33 vs 15-25 %P),
      great fireball (40+30..70 vs 35-65), force strike (20-50 vs 18..33, one source), exura sio
      (100+30..135 vs 80-160, one source). docs/reference-74/formulas.md §5
- [ ] Life ring / ring of healing regeneration not checked against 7.4 (1 per 3 s for 20 min / 1 per 1 s
      for 7.5 min)

- [x] Conjuring makes the wrong items: "adori vita vis" -> 2263 (done 2026-09-23), "adura vita" -> 2274 ("spell rune"),
      but the usable runes are 2268 (sudden death) and 2273 (ultimate healing) - spells.xml conjureId
- [x] Drinking any fluid failed ("You can not use this object.", Lua error): fluids.lua calls
      doPlayerSay, a TFS function Avesta lacks -> shim in data/compat.lua. tests/test_accounts.py

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
- [~] Overshoot: holding a key for 2 squares walked 3. The client remembers a key-down that arrives
      mid-step and walks it when the step ends; our 33 ms repeats always filled that memory.
      mintwall.dll now hooks the client's send(), learns step times from its walk packets and gives
      exactly one repeat per step, ~60 ms before the step ends (built; waiting for a try in game)
- [~] Using runes/fluids while walking never happened until you stopped: every step set the next
      action to the step's end and cancelled a pending one (Player::onWalk, Game::playerMove).
      Removed; actions keep their own delays. test_walking.py (fails on the old build; rebuild pending)
- [ ] Target box: clicking a monster mid-step misses (the client picks by tile, the monster is
      already on its new tile while drawn sliding from the old one). Plan: measure misses with
      walk-trace, then a click assist in mintwall.dll (move a right-click onto the creature drawn
      under the cursor; needs the game view rect and the client's creature list in memory)
- [ ] A step pressed while another is queued replaces it (Player::setNextWalkTask) - dropped steps when
      tapping back and forth (seen in the stairs trace); queue one step instead?
- [ ] Re-trace with the real client on the new server (walk-trace summary: steps more than 50 ms late)

## Travel and combat feel

- [x] Boats took the fare but never sailed: StdModule.travel called doTeleportThing(cid, pos, false);
      Avesta takes (uid, pos) and read the 'false' as the position -> shim in both compat layers.
      "bring me to <town>" compared doPlayerRemoveMoney(...) == TRUE, but Avesta returns booleans:
      money taken, "you don't have enough money", no trip. 64 such comparisons in 20 scripts rewritten
      (also: house purchase ignored needPremium; premium-only choices never offered). test_travel.py
- [x] A killed monster stood at 0 hp for 0.1-1.2 s: deaths waited for the creature's once-a-second
      check plus 100-200 ms. Now handled right after the killing blow (Creature::changeHealth ->
      Game::checkCreatureDeath). test_rookgaard.py (needs the rebuild)
- [x] Mail: a parcel the mailbox could not deliver was left lying on the mailbox tile (lost at the
      next restart). Receiver names were matched case-sensitively and label lines were not trimmed,
      so "centurion" or a trailing space was enough. Now: names case-insensitive (IOPlayer, LOWER()),
      lines trimmed, undeliverable mail refused on the tile ("Sorry, not possible."). test_mail.py
- [~] 7.4 formulas, step by step from docs/reference-74/formulas.md ("Mismatches, ranked"):
  - [x] 1. Monster spells every 2 s next to the target, 1 s at a distance (Monster::getSpellInterval,
        attack and defense spells; the melee attack keeps its own interval). Measured with a test
        dragon lord healing on every roll: 9 heals in 11 s before, 5-6 in 12 s after. Dwarf
        geomancer heal 75-325 -> 75-125, hero 200-350 -> 200-250
  - [x] 2. Mana / life fluids 40-80 -> 25-75; life fluids were broken (doPlayerAddHealth missing ->
        compat alias). test_formulas.py
  - [x] 3. Player melee/distance max (5*skill+50)*atk*stance*0.99/100, stances atk x1.2/1.0/0.6 and
        def x0.6/1.0/1.8, shield block max (5*shield+50)*def*stance/100 rolled 0..max like an attack
        (weapons.cpp, player.cpp, creature.cpp). Source C1 (tibiantis-notes calculators) - not pinned
        by a test yet (needs a damage-measuring setup)
  - [x] 3b. Monster melee and blocking from 7.4 attack/defense/armor/skill per creature:
        tools/import-74-creatures.py (source tibiantis-notes js/creature.js, numbers kept in
        docs/reference-74/creatures.csv) set <attack name="melee" skill= attack=> and
        <defenses armor= defense= skill=> on 92 monsters (e.g. dragon lord 250 -> 204, dwarf guard
        200 -> 125, demon 400 -> 514). Engine: exact 7.4 melee max (Weapons::getMaxMeleeDamage) and a
        skill-based block rolled 0..max for monsters with <defenses skill=> (Monster::getDefense).
        test_formulas.py (dwarf guard never above 125)
  - [ ] 3c. 30 monsters have no 7.4 data in the source (bosses, traps, assassin, bandit, dark monk,
        smuggler, chicken, yeti) - keep their values or find another 7.4 source
  - [x] 4. Magic power floor P >= 100 (combat.cpp FORMULA_LEVELMAGIC + magicPower() in compat.lua for
        the Lua heal formulas). 7.4 values: energy beam 40-80, fire wave 20-40, poison storm 150-250,
        great energy beam 40-200, mass healing 160-240, exura 10-30, IH rune 40-100, exura vita 200-300,
        UH rune fixed 250 (%P). test_formulas.py (IH rune at level 8)
  - [x] 5. Regeneration: Elite Knight 4/12, Paladin 8/8, Royal Paladin 6/6, MS/ED hp 12 (vocations.xml,
        test_formulas.py); promoted characters lose 7% instead of 10% on death (Player::getDeathLossFactor)
  - [x] 5b. Distance hit chance min(skill/(15d-1), 1) - only one source, sources conflict on the minimum
        Spike 2026-09-23 (paladin attacks): 7.4 hit chance = projectile x min(skill/(15d-1), 1), adjacent = d 5,
        projectile 91% arrows/bolts, 76% thrown (TN distance_calculator source). Spears / stars / knives: our
        TFS table (weapons.cpp:877) is the same model at 75%: within 1% everywhere, adjacent included - OK.
        Bolts / arrows: items.xml hitChance 80 (bolt, poison/burst arrow) / 90 (arrow) is a FIXED chance
        that skips skill and distance: skill 30 at 7 tiles hits 80% (7.4: 26%), skill 100 hits 80% (7.4:
        91%). Fixed: hitChance removed from 2543-2546, they use the ammo table (maxHitChance 90, = 7.4 model).
        test_formulas.py: skill 20 at 5 tiles hits under 55% of 20 bolts (old: 17 of 20)
        Melee with sword/club/axe: same formula as knights (vocations.xml multipliers all 1.0) - OK.
        Open: spear range (ours 5), spears stackable and breaking in 7.4?
  - [ ] Tests for step 3 (melee, distance, stances, shield block): measure damage and blocks in game
        against the 7.4 formulas - the formulas are built but not pinned by any test yet
- [x] 7.4 formulas research (docs/reference-74/formulas.md): Berserk = level x 4 mana
      is the real 7.4 cost (TibiaWiki: until the 2007 summer update); monster healing rates; mana
      fluid 25-75 in 7.4 (ours 40-80); magic formula base x (mlv*3 + lv*2)/100 (tibiantis-notes).
      No hydras exist on our server (post-7.4 creature?)
- [ ] Travel questions for the 7.4 reference: Edron premium-only? which captains went where, prices
- [ ] Oracle: premium players are now offered Darashia/Ankrahmun/Edron too (the script's intent; it
      never worked before) - overlaps with the Gatekeeper, check against 7.4

## Stability

- [x] "Test server crashed silently" (twice, 2026-09-22) was not a crash: exit code 1 = killed from
      outside. mise stop-server/restart-server ran `taskkill /IM avesta74.exe /F`, which also killed the
      test suite's server (7181) - the second time at 18:51:25, exactly when the dev server was
      restarted. Now tools/dev-server.ps1 stops only the dev server (the one without -c) and
      start-server checks port 7171. conftest names the test during which the server died, with its
      exit code (0xC0000005 would be a real crash)

## Accounts / security / ops

- [ ] Production plan: docs/production-plan.md (accounts, PBKDF2, saves/backups, restart, observability, Terraform)
  - [x] 1. Accounts A-D (God / balance testers / Rook premium / Rook free), random 7-digit numbers, 24-char
        passwords: tools/provision-accounts.py (credentials file outside the repo, backup first, refuses while
        the server runs, idempotent); seed.sql stays dev/test only. tests/test_provision.py
        - [ ] Run it on the local db.db3 (you) and check a 24-character password can be typed in the real client
  - [x] 2. Salted PBKDF2 (PasswordType = "pbkdf2", 600000 iterations, OpenSSL via vcpkg - passwords.cpp):
        checked on 2 worker threads (authpool.cpp), not the network thread; legacy rows rehash on first login;
        the existing LoginTries / RetryTimeout throttle per IP stays. tests/test_passwords.py (the stall test
        fails when the check runs inline: 0.15 s vs 0.02 s per step answer)
  - [x] 3a. Timed save: every SaveInterval s (config, 600) via data/globalevents/scripts/save.lua; every save
        logs "> Server saved in N ms" (Game::saveServer). tests/test_save.py (test server: 15 s)
  - [x] 3c. Async save (must have). 100 players online (tests/test_save_load.py, ~29 items each):
        before: the game froze ~570 ms per save (per-player transactions, a disk sync each)
        + SQLite WAL / synchronous NORMAL / busy timeout (databasesqlite.cpp): ~145 ms
        + capture on the game thread, write on a background thread with its own connection, one transaction
          (DBBatch capture in executeQuery, dbwriter.cpp): game thread 34 ms (players ~12, map ~22), written
          in ~65 ms off-thread; slowest step answer 54-75 ms (normal median ~23). Budget in the test: 150 ms
        Logout saves go through the same writer; a login waits for that player's pending write
        (dbwriter::waitFor); shutdown flushes the writer. players.save is read at login, not per save.
        Log: "> Server saved in N ms (P players, map M ms; written in W ms)"
    - [x] Map part (~22 ms, constant): the timed save writes only houses whose items changed (HouseTile marks
          the House on any item change, container contents included; text writes too); every 6th timed save,
          GM saves and shutdown write all. Now 2-7 ms. A clean shutdown did not save houses at all - fixed.
          tests/test_save.py (1 changed house after a drop, 0 when nothing changed, the item in map_store)
    - [ ] House info (owner, rent, access lists) is still rewritten for every house each save (the 2-7 ms)
    - [ ] A hard kill (closing the console) skips the shutdown flush: loses what is queued (ms) plus
          progress since the last timed save - by design (SaveInterval)
  - [ ] 3b. Backups (hourly SQLite snapshot to S3, daily EBS, restore drill) and restart supervision - at deploy
  - [ ] 4. Observability (CloudWatch agent, status-protocol health check, alarms to Slack) - at deploy
- [ ] Passwords travel unencrypted (7.4 protocol, encryption came in 7.7):
  - [ ] Tell players: MOTD / login message / website - use a password you use nowhere else
  - [ ] TLS through mintwall.dll (hook connect/send/recv, SChannel) + TLS terminator in front of the server
        (stunnel locally, AWS NLB TLS listener in production); spike first: does hooking the 7.4 client's
        Winsock calls from the DLL work, and what latency does it add

- [ ] Change the God account password before anyone else can connect
- [ ] Switch `PasswordType` from plain to sha1 (and seed accordingly)
- [ ] Account creation for players (7.4 had no in-client creation - website or script)
- [ ] Run as a service / auto-restart; backups of db.db3
- [ ] Hosting: public IP, patched client for players (`patch-client.ps1 -Ip ...`)

## Tooling

- [ ] Commit today's work (nothing from 2026-09-22 is committed yet): client walking DLL, server walking /
      stairs / diagonals / runes-while-walking, NPC fixes and tests, King's Bridge, doors, Gatekeeper,
      travel, mail, monster death, formulas, test accounts, idle, mise/dev-server
- [ ] walk-trace and the test suite both write tools/.run/walk-trace.config.lua / tests/.run - two
      parallel walk-trace runs overwrite each other's config

- [ ] `talk-test.ps1`: support walking/teleporting (GM) so any NPC can be tested without editing the DB
- [x] Smoke test runner: tests\run-tests.bat
- [x] mise tasks (`mise.toml`): build, seed, reseed, start/stop/restart-server, test
- [x] God group sees ID / action id / Position on look (flag bit 42; enable "Show Info Messages
      in Console" in the client to copy them)
un-tests.bat
- [ ] Test every NPC answers "hi" (generated test per NPC)

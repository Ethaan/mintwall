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


## Questions for the user

Gathered while working (the work goes on meanwhile); each with the evidence and a recommendation. Asked in batches.

- [x] Q1 Server/world name (branding tasks wait on it): the character list shows "<char> (OpenTibia)", the login - answered 2026-10-03 -> "Mintwall"
      message mentions otserv.org. What name - "Mintwall"? Then WorldName/ServerName/OwnerName, MOTD, LoginMsg,
      the first-login text all use it (see "Branding and client texts").
- [x] Q2 Experience rate: 7.4 was 1x with no stages (ours: RateExp 1, stages script unused). Keep 1x? (recommended: - answered 2026-10-03 -> keep 1x
      yes - the formulas and loot are now 7.4's, a multiplier changes the whole economy)
- [x] Q3 Rookgaard (no vocation) magic level multiplier: ours 4.0, TibiaWiki's formulae page 3.0 (one source). - answered 2026-10-03 -> 3.0
      Change to 3.0? (recommended: yes - it only affects rookies; 3.0 is the only source)
- [x] Q4 Premium running out (see "Premium runs out -> free"): the outfit - back to the free one at once, or kept - answered 2026-10-03: Tibiantis rules (outfit kept until changed, moved to the Thais temple, house items to the depot of the house's town) - implement under "Premium runs out -> free"
      until changed (Tibiantis)? moved to the Thais temple or the nearest free town? house items to the depot of
      the house's town or Thais? (recommended: Tibiantis' rules - outfit kept until changed, moved to the Thais
      temple, house items to the house town's depot)
- [x] Q5 Daily server save (see "Daily server save"): the hour, warnings before it, kick + restart, what resets. - answered 2026-10-04: daily save like Tibiantis but at another hour (hour still to pick - configurable); warnings, kick, save, release houses, restart
      (recommended: 9:00 CET like Tibiantis... or a quiet hour for your players; broadcast at 5/3/1 minutes; kick +
      restart; nothing else resets until "refresh" squares are chosen)
- [x] Q6 Shop runes from NPCs (Shiriel, Fenech sold runes in the 2006 wiki - possibly 7.6): add rune sales or not? - answered 2026-10-04: not yet - no pre-7.6 source
      (recommended: not yet - no pre-7.6 source)
- [x] Q7 The 30 monsters with no 7.4 combat data (tomb bosses, traps, assassin, bandit, dark monk, smuggler, - answered 2026-10-04: keep the current values
      chicken, yeti): keep their current values? (recommended: keep - no 7.4 source; the pharaohs were reviewed)
- [x] Q8 Respawn (docs/reference-74/spawns.md): every spot is 60 s; with the engine's 60 s check a kill is back in - answered 2026-10-04: (c) Cip data per spot + randomisation + players-online scaling + a timer per slot + multi-floor blocking
      60-120 s, 5-10x faster than 7.x (Cip data: 600 s for 78% of spots, rare spots 1,800-20,000 s). (a) keep 60 s,
      (b) Nostalrius' value per spot, (c) (b) + Cip's randomisation, players-online scaling and a timer per slot,
      (d) one value. Also: block respawn from other floors (one-line Spawn::findPlayer change), Cip values for the 77
      rare / quest-guardian spots anyway, overspawn at ~10 squares or a floor change instead of radius 1.
      (recommended: (c), multi-floor yes, rare spots yes, ~10 squares)
- [x] Q9 Using a rope on the rope spot you stand on is refused ("You can not use this object.", rope.lua refuses any - answered 2026-10-04: keep it refused (step off first)
      creature on the spot, the user too); players step off first. 7.4 let a creature or a field block a rope spot
      (tibiantis notes, poison bomb). Keep, or let the user through when alone on it? (recommended: keep, unless you
      remember 7.4 allowing it)
- [x] Q10 Automatic ban length (6/10/20 unjustified kills a day/week/month): ours BanLength 1 day. The 7.4 manual only - answered 2026-10-04: like Tibiantis: 7 days, then 30, then +30 each time - Done 2026-10-04: player.cpp addUnjustifiedDead + ban.cpp (counts earlier automatic bans; isBanished now sees a running ban behind an expired one) - NEEDS REBUILD; test_skulls.py::test_sixth_unjustified_kill_in_a_day_bans_7_days_then_30_then_60
      says "banished automatically"; Tibiantis: 7 days the first time, 30 the second, +30 each after. (recommended:
      Tibiantis - the only source with numbers; needs a small change to count earlier bans)
- [x] Q11 Thrown weapons: (a) spear attack - 7.4-era wiki (revs 6760/19275, May-June 2005) says 30, 25 from Nov 2005 - answered 2026-10-04: spear attack stays 25; throwing star/knife/small stone range 6 (done, items.xml)
      (rev 23930, no update note); ours 25; knife 30->25 and stone 20->10 same pattern. (b) throwing star / knife / small
      stone range: ours 5; rev 131557 says all hand-thrown weapons were 6 before 8.1 (later revisions name only spears).
      (recommended: (a) keep 25 - no second 7.4 source; (b) 6 for all, consistent with the one source)
- [x] Q12 Fished-out water comes back after 120 s here; TibiaWiki Training rev 158855 (May 2008, post-7.4) says about - answered 2026-10-04: keep 120 s
      30 minutes; no 7.4 source. (recommended: keep 120 s until a 7.4 source turns up)
- [x] Q13 Item weights that changed in the 2005-06 wiki (7.4 = Dec 2004): tower shield ours 82 (2005-06: 88, Tibiantis - answered 2026-10-04: 2005-06 wiki: tower shield 88, black shield 41.5 (done), the rest kept
      88), black shield 42 (2005-06: 41.5, Tibiantis 41.5), golden legs 54 (2005-06: 54, Tibiantis 56), pharaoh sword 190
      (2005-06: 190, Tibiantis 150), dragon scale helmet 60 (Tibiantis 32.5, later only), ornamented shield 67 (wiki
      always 67, Tibiantis 72), golden mace 50 (no page before 2009, today 41). Take the 2005-06 values or Tibiantis?
      (recommended: 2005-06 wiki - closest to 7.4 - i.e. tower 88, black 41.5, the rest as they are)
- [x] Q14 Capacity edge cases: (a) an item weighing exactly the free cap is refused (hasCapacity uses <); allow it - answered 2026-10-04: (a) allow an item that fits the free cap exactly; (b) an NPC sale over the cap is refused with "You do not have enough capacity." and the money kept - Done 2026-10-04: Player::hasCapacity compares in hundredths (exact fit allowed, NEEDS REBUILD); ShopModule.onConfirm checks the weight before the money (test_shops.py::test_an_item_over_the_free_capacity_is_not_sold)
      (<=, rebuild)? (b) an NPC sale over the cap drops the item on the floor with no message; 7.4? (recommended: (a)
      allow; (b) refuse with "You do not have enough capacity." - no 7.4 source for either, ask what you remember)
- [x] Q15 Deathslicer (5 on floor 13): ours 320 exp, 2000 hp, attackable. Current TibiaWiki: exp 0, hp 8200, immune to - answered 2026-10-04: a trap: not attackable, immune to everything, 0 exp (done, deathslicer.xml)
      all damage (a trap, in since 7.4); no 7.4-era number. Make it a trap like the throwers - not attackable, 0 exp?
      (recommended: yes)
- [x] Q16 GM ban command: talkactions/scripts/banmanager.lua (TFS-style, unregistered) calls 6 functions our engine - answered 2026-10-04: delete banmanager.lua (GMs use the engine's player/IP bans) - Done 2026-10-04: banmanager.lua deleted, 6 names off KNOWN_UNDEFINED
      lacks. The engine has player-name and IP bans for Lua (addBan, addIPBan...), account bans only checked; /b is
      commented out in commands.cpp. Delete banmanager.lua and ban via the engine's player/IP bans (or restore /b), or
      wire it up (new C++ for account bans)? (recommended: delete it; restore /b if GMs need a command)
- [x] Q17 Houses (7.4: website auction only, 7 days, bid + first month's rent from the house town's depot; one house per - answered 2026-10-04: stand-in /buyhouse: a request handed over at the next server save, one house per account, checks premium + the rent in the depot + the house free; Tibiantis rents; full end-to-end tests incl. house spells and a mass kick. The website can take this over later (the user: "if it make sense to do this on the website only thats okay") - in progress - Done 2026-10-04: lib/houses.lua + table house_requests (a website can insert requests); /buyhouse at the door records a request, /buyhouse elsewhere shows it, /cancelhouse withdraws; checks free / premium / one per account / guildhall = guild leader / first rent in the house town's depot (carried gold does not count), again at the save, which hands over and payHouses takes the first rent; the result is told at the next login. Rents: Tibiantis (691 of 816 matched; Ankrahmun 45 gp/tile), no rent 0 left (tools/apply-tibiantis-rents.py). No kick-all spell in 7.4 (TibiaWiki House rev 78243): emptying the guest list puts everyone out. test_houses.py::test_buying_a_house_end_to_end (+19).
      account; rent monthly from that depot; tibia.com manual 2004-06). Ours: /buyhouse (premium, 100 gp per tile) and
      /sellhouse - not 7.4. (a) keep /buyhouse as a stand-in until a website, but one house per account, guildhalls for
      guild leaders, charging the first month's rent? keep /sellhouse? (b) rents: 416 houses have rent 0, the rest look
      made up - take Tibiantis' house list (tibiantis.online/?page=houses) or a per-tile rent? (c) "alana sio" with no
      name: kick yourself (later servers) or nothing (ours)? (recommended: (a) yes / keep; (b) Tibiantis; (c) yourself)
- [x] Q18 Server save hour (Q5): which hour (server time)? and the warnings at 5/3/1 minutes ok? - answered 2026-10-04: early morning - ServerSaveHour = 6 (config.lua)
- [x] Q19 Bans: (a) with enough GM warnings (WarningsToFinalBan) the "final" ban (FinalBanLength 7 days) or deletion - answered 2026-10-04: (a) the final ban is never shorter than the automatic one; (b) GM bans stay out of the count - Done 2026-10-04: the final ban takes the longer of FinalBanLength and the automatic length (NEEDS REBUILD); GM bans confirmed out of the count
      applies instead, and can be shorter than a repeat automatic ban (30/60...) - keep? (b) GM bans do not count toward
      the automatic ban length - intended? (recommended: (a) make the final ban at least the automatic length; (b) yes)
- [x] Q20 Houses: (a) Tibiantis allows one house AND one guildhall per account; ours one in total (as asked) - keep? - answered 2026-10-04: one house AND one guildhall per account (like Tibiantis); "alana sio" with no name puts the caster out - Done 2026-10-04: lib/houses.lua per kind (house / guildhall), /cancelhouse withdraws all; house.cpp kickPlayer: alana sio alone puts the caster out (NEEDS REBUILD). Engine /sellhouse still refuses a buyer who owns any house (C++).
      (b) "alana sio" with no name: put the caster out (later servers) or nothing (ours)? (c) is emptying the guest list
      enough as the "kick everyone", or a command too? (recommended: (a) keep one; (b) put the caster out; (c) enough)
- [x] Q21 Distance details: (a) poison arrow attack - TibiaWiki 2006-07 says 20 ("less than an arrow"), tibiantis- - answered 2026-10-04: poison arrow attack 20; remove the minimum damage (distance and melee) (C++) - Done 2026-10-04: weapons.cpp distance rolls from 0 (melee never had a minimum) - NEEDS REBUILD
      notes 10; ours 20. (b) its poison - tibiantis-notes power 50 (3 a tick first), TibiaWiki "2 HP per turn" (2006) / 1
      (2005); ours 50 (a 25-50 roll fits both). (c) minimum damage: ours ceil(level x 0.2) vs monsters, x 0.1 vs players;
      the 7.4 calculator has none. (recommended: (a) 20, (b) the 25-50 roll, (c) remove the minimum vs players and
      monsters - no 7.4 source has one)
- [x] Q22 Spells (docs/reference-74/spell-formulas.md): (a) sudden death - tibiantis-notes and OTHire 130-170 %P, ours - answered 2026-10-04: SD 130-170 %P, force strike 35-55, berserk level only - Done 2026-10-04: sudden_death -1.3..-1.7, force_strike -0.35..-0.55, berserk 2.4-4.0 x level; test_spell_damage.py
      125 %P + 30 .. 170 %P (155-170 at the floor) - change? (b) force strike - OTHire 35-55, OTL-Mech 18-33, ours 20-50.
      (c) berserk - level only (TI-Calc 2.4-4.0 x level) or also magic level (ours)? (d) burn tick 10 s (ours, like
      fire fields) vs "9 s" / "2 turns" on the wiki. (e) damage roll: clipped normal (ours) - no source on 7.4's shape.
      (recommended: (a) 130-170, (b) 35-55 like the other strikes, (c) level only, (d) keep 10 s, (e) keep)
- [x] Q23 Fields (spell-formulas.md Q8-Q12): (a) medium fire field: ours 7 x 10 with no hit on stepping in; TibiaWiki - answered 2026-10-04: follow the 2005 text: medium fire 20 + 5 x 10, energy field 30 + 2 x 25 - Done 2026-10-04 in items.xml (1493/1488/1501, 1495/1491/1504); the last hit or two of a long damage chain is lost - see the condition bug below
      2005-11 "20 initial, then 10 each 2 turns", 70 total - make it 20 + 5 x 10? (b) energy field: ours 30 + 25 (55);
      TibiaWiki 2005-11/2006-10 30 + 2 x 25 (80), 2007 55 - count 2? (c) non-PvP fields last 10 s here; wiki 8 s fire
      (2005), 3 s poison bomb (2006) - only matters on no-PvP tiles. (recommended: (a) yes, (b) yes - the only 7.4-era
      text, (c) fire 8 s, poison/energy 3-8 s)
- [x] Q24 Premium (docs/reference-74/premium.md): (a) how players get premium - 7.4: bought on tibia.com; ours: only by - answered 2026-10-04: (a) website only (no GM command); (b) every spell taught only in Edron / on Eremo's isle needs premium to cast (a player whose premium ran out loses them until renewed); (c) keep the waiting-list priority; (d) keep the VIP list whole - Done 2026-10-04: 28 spells prem="1" (derived from the teachers on premium ground; drift test in test_premium.py); "You need a premium account to use this spell." (spells.cpp, NEEDS REBUILD)
      hand in the DB. A GM command /premium <name>, <days> now, the website later? (b) every Edron spell premium to cast, or
      only Levitate (ours, TibiaWiki 2005)? (c) premium logs in past MaxPlayers (7.4 text) or keep the waiting-list
      priority? (d) premium runs out: cut the VIP list to 20 or keep it (no new names)? (recommended: (a) GM command
      now, (b) only Levitate, (c) keep, (d) keep)
- [x] Engine: a long damage condition (fields, poison) loses its last hit(s): executeConditions counts 1000 ms per
      think but thinks run 1.02-1.09 s apart, and the condition ends on a wall-clock endTime. Measured: medium fire 20 + 4
      x 10 (not 5), energy 30 + 25 (not 2). Proposed fix in condition.cpp ConditionDamage::executeCondition: keep the
      condition alive while damageList is not empty. test_fields.py (2) wait on it. Done 2026-10-04 (approved by the user): condition.cpp - NEEDS REBUILD
  - [x] /sellhouse can give a house to an account that already has one - add the one-per-account and guild-leader checks
        Done 2026-10-04: talkactions/scripts/sellhouse.lua + houses.lua houseTransferProblem (checked when the trade is
        offered; a request made while the trade window is open slips through - closing it needs House::executeTransfer, C++)
        - test_houses.py::test_sellhouse_keeps_one_house_per_account
  - [ ] tests/tibia74/server.py: ServerProcess.start leaves the server running when its startup times out
  - [ ] Engine clean-up (rebuild): remove Commands::buyHouse and HousePrice; read guildhall in loadHousesXML and fix
        luaIsHouseGuildHall (then drop the id list in lib/houses.lua); depot money binding (drop the 1.5 s wait)

## New player journey (tests/test_rookgaard.py)

- [x] 7.4 beginner set on first login (club, torch, bag with a red apple, jacket/coat) and the
      "noob outfit" (head 78, body 69, legs 58, feet 114 - picked in the real client); login creature events
      were never called by the engine - fixed
- [x] Oracle gives a vocation bag (TFS-era, not 7.4) - keep or remove?
      Done 2026-10-01: removed (decided with the user: 7.4 had no starter kit). npc/lib/oracle.lua
- [x] Oracle's "SO BE IT" is never seen (player is teleported first) - delay the teleport slightly?
      Done 2026-10-01: the player is teleported 1 s after it. test_oracle_turns_a_level_8_into_a_knight_of_thais
- [x] More journey tests: rookgaard shops buy/sell with money, sewers/ladders, death in Rookgaard, reaching level 8 via exp - 2026-10-04: tests/test_rookgaard_journey.py written (hunt/sell/buy, sewers, death, level 8 + Oracle), not passing yet: test 1 hangs (likely the sewer rat spawn 32097,32211,8 is unreachable for walk_near) - debug - Done 2026-10-04: all 6 pass twice (the sewer rats are behind a drawbridge: the test pulls its switch); test_rookgaard_journey.py
  - [ ] test_rookgaard.py ROOK_FIELD (32082,32210,7) is not walkable: test_rookgaard_is_non_pvp logs in at the temple (PZ) and may pass for the wrong reason - use (32085,32191,7)
  - [ ] _saved helpers in test_npcs_rookgaard.py / test_death.py wait for lastlogout only - a periodic save can set it first; wait for lastlogout >= the logout time (as test_rookgaard_journey.py does)

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
- [x] Gatekeeper and Oracle hand out vocation starter kits (TFS-era) - 7.4 had none? (reference task)
      Done 2026-10-01 (decided with the user): no kit, and the 2005 TibiaWiki town lists - the Oracle Carlin,
      Thais, Venore (premium or not), the Gatekeeper Ab'Dendriel, Ankrahmun, Darashia, Kazordoon (no Edron, no
      Port Hope; the Island of Destiny branch is gone). Both are oracleNpc{} (npc/lib/oracle.lua).
      test_rookgaard.py: test_oracle_offers_carlin_thais_and_venore, test_gatekeeper_sends_a_premium_level_8_...
- [x] Questions for the 7.4 reference: did Lee'Delle sell footballs (111 gp)? Seymour buys dead rats?
      Norma's lines are 8.x ("ask me for a trade"); NPC muting when talking fast to NPCs
      Done 2026-10-01 (TibiaWiki 2005 revisions): Lee'Delle sold no football - removed; her prices were the
      2005 list (spear 10, rope 50, ...; ours were ~10% under). Seymour paid 2 gold for a rat corpse - kept
      (it works). Norma was a premium equipment shopkeeper at the same spot (food seller only from 2008):
      now Lee'Delle's wares and prices; both trade with premium accounts only (npc/lib/premiumshop.lua; the
      refusal line is ours). Muting: kept - the engine's message buffer mutes NPC talk like any talk in the
      default channel, as 7.x did. test_rookgaard.py: test_seymour_pays_2_gold_for_a_dead_rat,
      test_lee_delle_sells_at_the_2005_prices_and_no_football, test_norma_sells_equipment_to_premium_...
- [x] After the Rookgaard NPC tests: gather a 7.4-era reference (prices, NPC dialogue, spell lists)
      from a source like TibiaWiki's history/archived pages, store it in the repo and compare our NPCs
      against it (then the same for the other towns)
      Done 2026-10-01: docs/reference-74/npc-shops.json (tools/wiki-npc-reference.py: each spawned NPC's
      earliest TibiaWiki revision with a ware list before 8.0 - mostly late 2005/2006; raw text kept) and
      npc-shops.md (tools/compare-npc-shops.py: 124 shops differ, 16 match, 10 have no list - a guide: the
      early lists were partly copied between NPCs and have typos). docs/reference-74/spells.json
      (tools/wiki-spell-reference.py: 60 of 66 spells from May 2005 infoboxes - level, magic level, mana,
      price, where taught). Dialogue: not collected (the 2005 pages have almost none).
- [x] Write real dialogue for The Queen of the Banshees (placeholder greets only)
      Done 2026-09-25 with the Banshee Quest (npc/scripts/banshee_queen.lua, the TibiaWiki transcripts; test_banshee.py)
- [x] Replace Donald McRonald placeholder with his real 7.4 NPC
      Done 2026-09-30: his TibiaWiki 2006 trade (wheat 1, cheese 5, carrots 3 gp; dead spiders bought at 2 gp) and a
      few lines (ours - no transcript). Sherry McRonald could not be greeted (her shop and greeting were set up inside a
      callback that never ran) and was spelled "Mcronald".
- [x] Talk-test every NPC once; log the ones that error or don't answer
      Done 2026-09-30: tests/test_npc_talk.py - all 307 spawned NPCs, each greeted its own way (djinns DJANNI'HAH,
      kings "hail", the Blind Orc "charach", ...), then "job" and "bye"; the no_lua_errors fixture fails a script that
      errs. Found and fixed: Edowir had an empty keyword - every word said to him looped forever and froze the server
      (containsWord now refuses empty keywords; test_no_npc_has_an_empty_keyword); 22 scripts registered a
      creatureSayCallback they never defined and ran another NPC's (all NPCs share one Lua state) and 74 callbacks
      were globals (now locals; test_every_npc_callback_is_its_own); data/global/greeting.lua redefined FocusModule:init
      for every NPC after 19 of them (deleted; the shared-library test scans all of data/ now). Silent by design: the
      four Ghostlands apparitions ("an un-reachable illusion", TibiaWiki 2006) and Arkhothep (a creature's page). The
      test server's login guard (LoginTries) is off - every test logs in from 127.0.0.1.
- [x] Boat captains: verify travel destinations/prices are 7.4 (no Liberty Bay/Port Hope etc. if not in 7.4)
      Done 2026-09-30: docs/reference-74/travel.md (each travel NPC's wiki page before 7.5). The seven sea captains
      rewritten on npc/lib/captain.lua (one route table each; "bring me to" kept; Fearless keeps the Ghost Ship):
      Port Hope (Bluebear, Seahorse, Sinbeard, Petros, Fearless's shortcut) and Svargrond (Bluebear) removed,
      Bluebear-Edron 110 -> 150, Seahorse-Carlin was free -> 110. Uzon-Darashia 40 -> 60, Pemaret-Edron free -> 10,
      the ice ferrymen no longer offer their own island. Spawns: Captain Greyhound's npc z 6 -> 7 and Christoph's
      7 -> 6 (the engine uses the spawn centre's floor; the tests read the npc's). test_travel.py
      test_captains_sail_the_74_routes
- [x] Guards (Grof, Tim, Kulag, Walter): scripts use `getMonstersfromArea` - implement or rewrite
      Done 2026-09-30: npc/lib/guard.lua. TibiaWiki 2006: each "protects the city from creatures" at a Thais gate;
      decided with the user: a guard kills a wild monster within 4 tiles on his floor ("Get lost, you beast!"; a
      player's summon is left alone), the rat bounty pays 1 gold for a dead rat (taken), insults burn. Before: Kulag
      and Walter erased 401+ HP monsters through a global getMonstersfromArea in the shared Lua state, Grof never
      answered anything (npcHandler.focus), the bounty paid nothing and the fire was no condition.
      tests/test_guards.py
- [x] Remove or neutralize non-7.4 NPC features: banks (bank.lua, evabank.lua, Lokur), marriage, addon outfits
      Done 2026-10-01 (decided with the user): the bankers Ebenizer, Eva, Muzir, Rokyn and Suzy (TibiaWiki pages start
      January 2007 - the bank update) are no longer spawned (files kept). Tesha and Tezila stay jewellers (their NPC-file
      shops; no bank, no money changing - Tezila's "weddind ring" fixed). Lokur is the postman only (his 470-line
      script was a bank around one Postman line; his greeting named a player "Andrewsorcerer", his city list had Port
      Hope). Lynda is a Thais priestess again (marriage system removed; marriagesystem.lua and changegold.lua deleted).
      No NPC offered addon outfits.
- [x] Promotion NPCs: verify 7.4 rules (level 20, 20k gp, premium) and that `doPlayerSetPromotionLevel` shim is right
      Done 2026-09-30: nobody could be promoted - StdModule.promotePlayer called getPlayerPromotionLevel (it did not
      exist; now in compat.lua: vocation 5-8 = promoted) and read a config key that does not exist. TibiaWiki 2005
      (Vocation Promotion): King Tibianus, Queen Eloise, Emperor Kruzak, Ishebad; 20,000 gp (they charged 10,000 -
      Ishebad quoted 20,000), level 20, premium; a character without a vocation is refused before paying. Their
      keyword 'promot' (a CipSoft word start) never matched "promotion" since keywords match whole words: a keyword
      ending in "*" now matches the start of a word (containsWord) - promot*, dwarv*, enem*, necroman*, rumo*, undea*
      in 12 NPCs. tests/test_promotion.py (each promoter; level 19, free account, 19,999 gp, already promoted).
- [x] Bone-collector NPCs use `doPlayerRemoveBones`/`getPlayerBones` - implement or rewrite
      Done 2026-09-30: no NPC uses them any more - they were dead local copies in Hugo, Talphion and Noodles (rewritten
      for the Postman Missions; Kevin counts the 20 bones himself). test_spells.py: getPlayerPromotionLevel is
      defined now (compat.lua) and left KNOWN_UNDEFINED.
- [x] Spell-teaching NPCs: check spell lists/prices/levels against 7.4
      Found 2026-10-01: every spell teacher (17 scripts) is broken - StdModule.learnSpell calls
      parameters.vocation(cid) but they pass a number (a Lua error on every purchase), and all pass level 1.
      No spell has needlearn, so nobody needs to buy a spell anyway; spells.xml gates by magic level only.
      Done 2026-10-01, decided with the user: spells as Tibiantis (a 7.4 server) has them - its spell table
      (docs/reference-74/spells-tibiantis.json, tools/apply-tibiantis-spells.py --fetch) won over TibiaWiki,
      whose 2005 spell pages and 2007 teacher pages disagree on ~30 spells (spells.json keeps them).
      - Every spell must be learned (needlearn="1"); magic level only, no character level (Levitate keeps its
        premium flag, loses its level 12); mana, rune charges, vocations from Tibiantis. Eremo's spells
        (Challenge, Power Bolt, Wild Growth, Enchant Staff) stay promoted-only (Tibiantis' table names the base
        vocation; the 2005 wiki and our old data say promoted).
      - Runes: any vocation uses any rune with its use magic level (Magic Wall 9, Sudden Death 15, Paralyze 18).
      - Teachers: Tibiantis' 24 (npc/lib/spellteacher.lua + spells74.lua; the 7.x lines "Do you want to learn
        the spell '...' for ... gold?"): Elane, Faluae, Irea, Shanar, Eroth, Etzel, Maealil, Elathriel,
        Padreia, Marvik, Zoltan (he still taught in 7.4), Eremo added; Chatterbone, Smiley, Tothdral, Rahkem,
        Ormuhn no longer teach (none in Tibiantis; Ankrahmun has no teacher). Force Strike and Envenom kept
        (Tibiantis teaches them); its Discharge/Extinguish/exito tera left out (no price).
      - Test characters know their vocation's spells unless spells=[] (tests/tibia74/db.py).
      tests: test_spell_teachers.py (learning rules, all 24 teachers list their spells), test_spells.py
      test_a_knight_shoots_sudden_death_from_magic_level_15.
- [x] Existing characters on the live database know no spell now (spell buying is new) - grant them their
      vocation's spells once, or let them buy (decided: they buy - "Must buy, as 7.4"); tell the players
      Done 2026-10-04: nothing to grant - a dry run on a copy of the live DB shows the 11 player characters already know exactly their spells (players buy them, as decided); only 4 GM/test characters (Centurion, Gandalf, Radagast, Legolas) would get spells. tools/grant-learned-spells.py (--dry-run, --backup, refuses while 7171 listens) + tests/test_grant_spells.py, if ever needed.
- [x] Shop prices: audit buy/sell lists against 7.4 (tibiaot74 data may include 7.72 items)
      Done 2026-10-01 (decided with the user): Tibiantis first (docs/reference-74/tibiantis/, tools/fetch-tibiantis.py:
      EQSELL = what NPCs pay, MARKET_COST = the cheapest buy anywhere), then each NPC's own TibiaWiki page, then the
      wiki consensus (docs/reference-74/npc-shops.md, tools/compare-npc-shops.py). Pages after 7.6 (2005-12-12) kept
      except for fluids: life fluid 100 again (60 is 7.6's), mana fluid 100. Djinn keep their 2006 wiki prices.
      - Tibiantis: Shanar buys 10 more weapons, Willard axe/club/sword, Turvy/Romella club, Kroox devil helmet,
        Beatrice sickle 3 / scythe 12; studded legs 60 (was 50), leather legs bought for 1, Rookgaard studded
        helmet 63; Romella's double axe was called "battle axe".
      - Wiki: apple 3, bag 4, beer 2, bottle 3, bucket 4, cup 2, oil 20, dresser 25, trough 7, green tunic 10,
        brass shield 16 (Hardek), Chemar letter 8 / parcel 15; 41 NPCs got the wares their pages list (Ahmet's
        general store, food and drink sellers, weapon shops...).
      - Wrong items: Timur's torch was a lit torch, the trough a pendulum clock, "ranger's cloak" a hidden turbant
        (no 7.4 item - removed), box a crate, parchment a written one; typos (chesse, dager, throwing knight,
        weddind ring...); Velvet's pillows renamed to their 7.4 names; worms and Venorean spice (not 7.4) removed.
      tests: test_npc_data.py (every shop item exists, is called what it is, and what is sold can be carried - all
      spawned NPCs), test_shops.py (every mainland ware bought and sold in game).
- [x] Shop questions (decided with the user 2026-10-01): furniture shops sell only what can be carried in 7.4
      (kits - ids 3901+ - are not 7.4 items; dressers, statues... cannot be carried): pillows, flowers, vases,
      amphoras, crates, tapestries; Allen and Yulas have nothing left to sell. Coloured bags/backpacks keep their
      colour under their own name ("golden backpack"). Yaman's rods removed (7.6). Also fixed while testing: empty
      fluid containers were sold filled (Chephan's bottle with beer, buckets with slime), Chephan's second pot for
      0 gp, Frodo's two price lists (Food.lua deleted), three wares all called "book" (Gorn, Thomas).
      Jimbin's whole script sat inside his message callback (keywords and shop added again on every message; he
      stopped answering "hi").
- [x] Engine: an item given to a player (a purchase, a quest reward) went into any free slot that took it - a
      bought life ring into the ring slot, worn and wearing off (2205), a crystal ball into the ammo slot. Now never
      the ring or the ammo slot (Player::__queryDestination; armor still goes on, as the beginner set). 2026-10-01,
      test_shops.py test_a_bought_ring_is_not_put_on
- [x] Two traders in one shop (Bezil and Nezil, Kazordoon): "hi" greeted both and both sold on "yes" - the buyer
      paid twice. Fixed 2026-10-02 (asked by the user): a player talks to one NPC at a time - the other stays
      silent until that conversation ends (TALKING_TO in npc/lib/npcsystem/npchandler.lua); "hi <name>" reaches
      that NPC anyway and the first one lets the player go (the name check compared the lower-case message with
      capitalised names - it never worked; and "hi" counted only when no "hi" + letter appeared anywhere in the message,
      so "hi bashira", "hi shiriel", "hi phillip" were refused - now a whole-word match). Orc King's guards are
      summoned beside a blocked tile. test_shops.py test_only_one_trader_of_a_shared_shop_answers,
      test_greeting_the_other_trader_by_name_hands_the_player_over; test_npc_talk greets each NPC by name
- [x] NPC rune sales (Shiriel, Fenech: TibiaWiki 2006) and Maryza's cookbook not added - runes from NPCs may be - decided 2026-10-04: not yet (no pre-7.6 source)
      7.6; ask when the magic shops are looked at

## Map / world

- [x] Quests: chests, quest doors, levers (actions/unique ids on the map vs `data/actions`)
      Done 2026-09-30: every quest is scripted and tested; the full-map id scan found only the citizenship portals
      (see "Other map action ids" below) - and the quest-object audit is settled

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
- [x] Quest tests split (2026-09-24): tests/test_quests.py became tests/quests/<city>/test_<quest>.py (27 files, the
      same 50 tests) + quests/common.py (temples, item ids, edron_player). "test_quests.py::test_x" below = the test
      of that name in its quest's file
- [x] Quest testing skill (.claude/skills/quest-testing): research -> questions -> map -> scripts -> tests -> record.
      Framework: tibia74/quest.py assert_level_door (level - 1 refused, level passes), way / assert_way /
      assert_no_way (way in, way out, key needed), step_onto; tools/map-regions.py (why the planner cannot get
      somewhere), tools/map-set-attrs.py. Rule tests: test_quests.py *_rules, test_demon_helmet_level_door
- [x] Vocation doors (gateofexp_closed.lua): a promoted character was kept out of its base vocation's door. Fixed
      2026-09-24: a base door (action id 2001-2004) lets in the vocation promoted or not (a master sorcerer is a
      sorcerer); a promoted door (2005-2008) only the promoted one. Our map has NO vocation door (no action id
      2001-2008 anywhere) - so no in-game test yet:
  - [-] Test the vocation door rules with the first quest that has one - checked 2026-09-26 through Darashia: no quest
        on our map has a vocation door (the Desert Dungeon checks vocations on its switches and lever)
- [x] Promotion without premium (checked 2026-09-24): suspended - plays and shows as the base vocation, the saved
      vocation stays promoted, back with premium (current TibiaWiki; the 2005 page only says buying needs premium).
      test_death.py::test_promotion_only_works_with_premium, test_promotion_is_suspended_without_premium_and_back_with_it
      (master sorcerer). Premium is checked at login only - by design, as real Tibia (context.md "Gotchas")
- [x] Premium runs out -> free (today: only the promotion is suspended; nothing else happens). What the user wants
      (2026-09-24), to check against sources before building:
      - at the next login a character standing in a premium area goes to the Thais temple (and Thais becomes its
        home town?)
      - the outfit goes back to the free (noob) one
      - the house is lost; its items go to the Thais depot - but items in the depots of premium cities (Edron,
        Ankrahmun...) stay there
      Tibiantis FAQ (scratchpad to_faq.html.txt): "Houses are lost during the next server save, character is moved
      out of premium area upon the next login, promotion is deactivated [...] The selected premium outfit can still
      be used until it is changed." Open questions: outfit (noob at once vs kept until changed, as Tibiantis)?
      moved where exactly (Thais temple, or the nearest free town)? house items: to the depot of the house's town
      or always Thais (7.4 rule)? which areas count as premium (map premium tiles / towns)? Tests for each rule
      Done 2026-10-03 (decided with the user: Tibiantis rules). At login, a character without premium
      (creaturescripts/scripts/login.lua premiumExpired): [2026-10-04: the house is now lost at the next server save,
      serversave.lua, as Tibiantis - not at login]; a citizen of Edron/Darashia/Ankrahmun becomes a Thais citizen; standing in a premium area -> Thais temple
      (Rookgaard premium side -> Rookgaard temple). Premium areas: flood-filled from the map (ships, carpets and King's
      Bridge are premium-only), tools/premium-areas.py -> creaturescripts/lib/premium_areas.lua (4 mainland boxes, 56
      Rookgaard). Outfit: the worn premium outfit stays (new colours ok) until changed - protocolgame.cpp parseSetOutfit
      (was: a refused outfit became look type 0 = invisible) - NEEDS REBUILD. tests/test_premium_expiry.py (16; 3 outfit
      tests wait on the rebuild). test_temples/test_map_mechanics testers now premium.
      Open: houses of players who never log in again are never released (needs the daily server save, Q5); Femor Hills
      and the Paradox Tower count as free (walkable from Kazordoon on our map).
- [x] Daily server save. Today only the 10-minute background save exists (nobody kicked) - so premium never ends
      for someone who never logs out (idle kick aside), and "respawns at server save" never happens.
      Tibiantis (7.4 server, FAQ): every day 9:00 CET, ~10 minutes offline, no login in the last 5 minutes before;
      never reset the world. Its trivia: only map squares with the "refresh" flag are reset (daily respawns); other
      squares keep what lies there even across the save (people hide loot bags for days).
      Our map has NO refresh-flag squares (checked 2026-09-24: 47,244 protection-zone tiles, 81 no-logout, 0
      refresh) - a refresh-style reset first needs the squares chosen (quest spots, daily chests) and marked.
      To decide with the user: the hour (3 AM?); warnings before (real Tibia broadcast minutes ahead); kick +
      restart vs kick + in-place reset; what resets (refresh-flag tiles only, like Tibiantis? quest spots: Small
      Axe box, Katana cave body, Captain Iglue's daily chest; houses of expired premium); some servers also clean
      the whole map every 1-2 weeks - wanted?
      Safety: scheduled by the server itself (config: hour), NOT a GM command (too risky, per the user); if a
      manual trigger is ever needed, console / admin-only with a confirmation. Tests: kicked at the hour, refresh
      tiles reset, other tiles untouched, expired premium applied, no login in the last minutes
      Done 2026-10-04 (decided with the user: like Tibiantis, hour to pick - Q18): globalevents/scripts/serversave.lua,
      config ServerSaveEnabled / ServerSaveHour (local time; 9 for now). Warnings at 5/3/1 min ("Server is saving game in
      5 minutes. Please come back in 10 minutes." - TibiaWiki Server Save), logins closed for the last 5 min (Tibiantis),
      then kick all, release houses of owners without premium (DB, so also owners who never log in), save with rent
      (payHouses), shut down with exit code 10 (game.cpp/otserv.cpp/luascript doSetExitCode - NEEDS REBUILD). A restart,
      not a reopen: quest states (Annihilator lever, Draconia keys, Paradox ladders...) reset on map load. No "refresh"
      reset: the map has no refresh tiles. Test servers run with ServerSaveEnabled = false. tests/test_server_save.py (8;
      the exit code waits on the rebuild).
  - [ ] Restart supervisor (NSSM / systemd, restart on exit) - without it the server stays down after the save; until
        then ServerSaveEnabled = false on an unwatched machine (production-plan §3)
- [x] Quest objects audit (tools/quest-audit.py, 2026-09-24): of tibiaot74's 166 quest objects our map has 8 scripted,
      62 standing there without a quest id (e.g. the 4 Annihilator chests 33227-33233,31656,13), 96 missing (the
      Battle Axe skeleton and the Dead Archer body were two of them). Our map (= the JS engine's) lost many quest
      containers. Work through them quest by quest with the quest-testing skill - each "missing" one needs sources
      (tibiaot74 also adds its own things)
      Done 2026-09-30: re-run - 130 done, 36 left, all settled. 32 belong to quests finished at our map's own positions
      (tibiaot74's spots differ: Draconia's keys lie loose, Sam's Old Backpack is not 7.4, the Tear basin has an action
      id, etc.). The Holy Tible (32828,32340,7) is a loose book with Banor's prayer on the original map - nothing to
      do. The six small rubies (their 32371,32262,12) are the Six Rubies Quest, done at our map's hole 32370,32265,12.
      Key 4009's chest (32690,32129,10) and the copper key in the dead tree (32657,32250,7) are tibiaot74's: no door
      on our map takes keys 4009/4022/2041 and the real-map chest table has neither (key 4009 / the Desert Dungeon
      library is the current wiki's "long path").
- [x] Map items decay (found 2026-09-24; built 2026-09-25, tests/test_map_items.py): the OTBM loader started decay on every map item, so the decorative dead
      humans (15 min) and dead skeletons (10 min, then gone) in caves vanished after each start. Fixed in
      iomapotbm.cpp (map items don't decay; moved later, they do) - NEEDS A REBUILD (the dev server was running);
      then a test (a map skeleton is still there after its 10 minutes)
- [ ] Quest log: the 7.4 client has none (TibiaWiki: added in 7.9) - revisit later (e.g. a !quests command or the website)
- [x] Settle reward / level conflicts per quest (Tibiantis vs TibiaWiki, see quests.md) as each one is done
      Done 2026-09-30: every quest is done; each entry above records what was settled and what was decided with the user

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
- [x] Battle Axe Quest - Thais sewers (SW) (no level; 1 player)
      Done 2026-09-24: the reward container was missing from our map (and the JS engine's): dead skeleton 3103
      ("You will find the Battle Axe in a dead Skeleton", TibiaWiki 2006) placed at 32305,32254,9 (tibiaot74's spot)
      with aid 2000 uid 1658 (real-map table: battle axe, sewers); REWARDS[1658]. Pick spot 32302,32257,8 and the 4
      cave rats were already there. tools/map-set-attrs.py --add puts new items on a tile.
      test_quests.py::test_battle_axe_quest (Thais temple, sewer grate, pick, loot, rope out), test_battle_axe_rules
- [x] Dead Archer Quest - Thais Troll Cave (E of Thais) (no level; 1 player)
      Done 2026-09-24: the body was missing from our map (and the JS engine's): dead human 3129 at 32513,32302,10 (north
      end of the slime room; tibiaot74's spot) with aid 2000 uid 1662 (real-map table); REWARDS[1662] = bow, 5 poison
      arrows, mana fluid, life fluid (TibiaWiki pre-8.0, Tibiantis, real-map table). Shovel hole 32493,32259,7.
      test_quests.py::test_dead_archer_quest, test_dead_archer_rules
  - [x] Quest messages said "You have found a vial." for any fluid. Done 2026-09-25: named as the look text names it -
        "a vial of manafluid" (quests/system.lua describe()). items.xml had no fluid names at all (ids 20001-20028 name
        the fluid types, items.cpp), so the look text itself read "a vial of ." - added the 7.4 fluids with the 7.x
        spellings (TibiaWiki 2006 titled the page "Manafluid"): water, blood, beer, slime, lemonade, milk, manafluid,
        lifefluid, oil, urine, wine, mud, lava, swamp
- [x] Deeper Fibula Quest - Fibula dungeon (level 50 (door); 1 player)
      Done 2026-09-24. Nothing worked before: the Fibula well (action id 54545) had no script (now
      draw_well_down.lua: down to the ladder below; also the Ancient Temple's well at 32508,32176,13); the dungeon
      door 32190,32432,8 and the dragon-cave door 32277,32420,10 had no key numbers (now 3940 - Dermot sells it,
      2000 gp - and 3980); key 3980 lies in the small hole 32219,32401,10 under a crate ("found by useing on a
      hole", TibiaWiki 2006); four of the five reward bodies were missing (placed where tibiaot74 has them).
      Real-map table ids 10014-10019 (REWARDS). test_quests.py::test_deeper_fibula_quest (from the Thais temple),
      test_deeper_fibula_level_door (49 refused, 50 passes), test_deeper_fibula_rules.
      Router: auto-walk (the client's map click, packet 0x64), wells, pushing barrels/crates aside (thrown up
      to 3 tiles in a one-tile passage), trying each carried key on a locked door, only doors/gates count as doors
      (ovens and lamps use the same script)
- [x] Devil Helmet Quest - Thais Ancient Temple to Mintwallin (level 30 (door); 2+ (one player holds a floor … player(s))
      Done 2026-09-24: the switch tile 32468,32119,14 (aid 51018, movements/mintwallin_grate_switch.lua) turns the
      grate's ground 32482,32170,14 into a hole while someone stands on it (as tibiaot74); the grate (aid 51019) is
      shut otherwise - it used to open for anyone, so one player could do it alone (TibiaWiki: at least 2). Lab doors
      32462,32153,14 and 32462,32151,15 = key 3610; the lab had no container: box 32459,32144,15 uid 3613 (real-map
      table: devil helmet, halberd, 4 small sapphires). quests/thais/test_devil_helmet.py (hero + friend on the switch,
      level-30 door, rules). Router: a sewer grate with its own action id is left to its script
- [x] Geomancer Quest - Mount Sternum undead cave (N of Thais) (no level; 1 player)
      Done 2026-09-24: the box was missing ("The quest box is on the east side of the room", TibiaWiki 2006): box
      32456,32008,13 (tibiaot74's spot), uid 3617 = small sapphire, small diamond, dwarven ring (real-map table, one
      container). quests/thais/test_geomancer.py
- [x] Ghoul Room Quest - Thais Ancient Temple (no level; 1 player)
      Done 2026-09-24: key skeleton missing (dead skeleton 32509,32181,13 added at tibiaot74's spot, uid 3601 = key
      3600), the door 32506,32175,14 had no key number (now 3600), the well 32508,32176,13 is the 54545 one; reward
      [3602] garlic necklace + club ring in the middle one of the room's three chests (32500,32176,14 - no source says
      which). test_quests.py::test_ghoul_room_quest, test_ghoul_room_rules
- [x] Kingdom of Kormarak Quest (Old Mintwallin) - Thais Ancient Temple (no level; 1 player)
      Done 2026-09-24: "It is a spawn, so you may find the body empty" (TibiaWiki 2006) - not a quest box: a plain dead
      human by the wooden coffin (32552,32200,11; missing, placed at tibiaot74's spot) holding brass armor, brass
      helmet, hatchet, 4 throwing stars (real-map table [3618]; the 2011+ wiki / Tibiantis say 13). First come takes
      it; back at every start (needs the map-decay rebuild, or the body decays 15 min after start).
      quests/thais/test_kingdom_of_kormarak.py (a second character finds it empty)
- [x] Life Ring Quest - Thais Ancient Temple (S branch) (no level; 1 player)
      Done 2026-09-24: the box 32443,32238,11 is now a quest box, uid 3616 (real-map table: life ring + dragon
      necklace 200); pick spot 32437,32239,10 and the rope spot below were already there.
      test_quests.py::test_life_ring_quest, test_life_ring_rules
  - [x] Drawbridge levers (Ancient Temple 32413,32230,10 and 32417,32254,10). Done 2026-09-25: aid 51058,
        quests/ancient_temple_drawbridges.lua - a pull raises a lowered bridge (each tile back to its column's water on
        the map: 508 / 493 / 509) and lowers a raised one, like Rookgaard's sewer bridge; things on it go to the lever's
        bank. The bridges start down. tests/quests/thais/test_ancient_temple_drawbridges.py
- [x] Mad Mage Room Quest - Thais Ancient Temple, toward Mintwallin (level 40 (door); 1 player)
      Done 2026-09-24. A Prisoner's script gave key 3666 to anyone ("key", "yes"), took 1000 gold in the lesson and
      shared one conversation state: rewritten from his TibiaWiki transcripts (riddle answer, 7 apples, "Really,
      really?", per-player state, sell rune, mathemagics). Nobody could greet him at all: A Lost Soul.lua (and
      Wyat.lua) replaced FocusModule:init for every NPC loaded after them (one shared Lua state) - now instance-only;
      test_npc_data.py::test_no_npc_script_changes_the_shared_npc_library. Map: prison doors 32395,32117,15 and
      32393,32136,14 = key 3620 (TibiaWiki: all prison doors); the barracks drawer 32411,32155,15 is a quest drawer
      (uid 13620 = key 3620, one per character; the real-map table's 3620 is the Spike Sword body); door 32578,32197,15 = key 3666; the three rewards (real-map table
      10058 magician hat, 10059 stone skin amulet 5, 10060 star amulet) in the room's box / top box / chest (west to
      east; no source says which is which). quests/thais/test_mad_mage_room.py (full run from the Thais temple, the
      prisoner refuses without the answer / apples, level-40 door, rules). Router: two height items on a tile (two
      chairs) can't be stepped on; a tile the server keeps refusing is avoided
- [x] Mintwallin Cyclops Quest - Thais Ancient Temple, cyclops room (no level; 1 player)
      Done 2026-09-24: the switch 32602,32104,14 (aid 51016, quests/mintwallin_cyclops_wall.lua) moves the wall as
      tibiaot74 does - north walls 32593-32594,32103,14 go, walls close the way back at 32592,32104-32105,14 - and
      moves it back when pulled again (decided with the user: both ways). Key 3667: the dead human under rubbish
      32576,32216,15 (uid 3667); its door 32592,32102,14. Chests: key 3610 (uid 3610, it lay there already) and the
      small diamond next to it (uid 3611) - real-map table. quests/thais/test_mintwallin_cyclops.py (switch route,
      key-3667 route, rules)
- [x] Naginata Quest - Thais Dragon Lair (N of Alatar Lake) (level 40 (door); 1 player)
      Done 2026-09-24: "The chest is at the north end" (TibiaWiki) - the room below the level-40 gate had no container:
      a chest at 32346,32063,12, uid 10065 = naginata (real-map table). quests/thais/test_naginata.py (pick, level-40
      door, rules). Router: house doors are closed to the planner ("You are not invited."); a field on a rope spot is
      burnt away with a carried destroy field rune (rope.lua refuses a spot with a field)
- [x] Noble Armor Quest (Skjaar/DTD) - below Mount Sternum (level 35 (door); 1 player)
      Done 2026-09-24: Skjaar gave tibiaot74's key number 2015 and took the 1000 gold without checking; now key 3142
      (TibiaWiki), the gold checked, both greetings (warriors / mages, from his transcript) and his small talk. The crypt
      door 32450,32044,8 had no key number (3142); the chest 32453,32048,8 = noble armor (10043), a box added at
      32455,32048,8 = crown helmet (10042) - real-map table, two containers. quests/thais/test_noble_armor.py (quiz,
      no gold no test, level-35 door, rules)
- [x] Scale Armor Quest - cave W of Ancient Temple entrance (no level; 1 player)
      Done 2026-09-24: the chest 32357,32130,9 (holding the scale armor on our map) is now a quest chest, uid 10061
      (real-map table "scale armor -- near AT"); the well 32354,32131,8 ("use the lower-right corner of the well",
      TibiaWiki) got action id 54545 (down to the ladder below). The next chest (piece of iron, book) stays an
      ordinary chest. test_quests.py::test_scale_armor_quest, test_scale_armor_rules
- [x] Silver Amulet Quest - Thais Troll Cave cellar (no level; 1 player)
      Done 2026-09-24: "a box in the southeast cellar" - TibiaWiki's mapper link 32507,32270,9, no box on our map:
      placed, uid 2170 (the amulet; the real-map table's 1029 is the Edron Goblin Quest's). quests/thais/test_silver_amulet.py
- [x] Six Rubies Quest (Double Dragon) - Thais Ancient Temple (no level; 1 player)
      Done 2026-09-24: the small hole under a fire field 32370,32265,12 (our map) is the quest hole, uid 3614 = 6 small
      rubies (TibiaWiki 2006 + current + Tibiantis against the real-map table's 2). The test clears the fire with a
      destroy field rune, as the wiki says. quests/thais/test_six_rubies.py
- [x] Small Ruby Quest - Mintwallin throne room pit (no level; 1 player)
      Done 2026-09-24: nothing to change - our map has the small ruby under a fire field at 32437,32174,15 (a daily
      respawn, as the wiki says: a map item). quests/thais/test_small_ruby.py (destroy field, pick it up)
- [x] Spike Sword Quest (Fire Devil) - cave E of Mount Sternum / NE of Triangle Tower (no level; 1 player)
      Done 2026-09-24: "The reward is in a body hidden behind a pillar" - missing on our map: dead human at 32568,32085,12
      (tibiaot74's spot), uid 3620 = spike sword (real-map table; the Mintwallin prison drawer moved to uid 13620).
      Shovel + 2 picks + rope. quests/thais/test_spike_sword.py
- [x] Thais Lighthouse Quest (Dark Shield) - Thais lighthouse, SW of Thais (no level; 2 (step switch + lever) player(s))
      Done 2026-09-24: none of it was scripted. Action ids 51001 (switch under the crates -> trapdoor 369 above the
      ladder), 51002 (step switch -> stairs 410 at the south end while someone stands on it; movements), 51003
      (lever -> portals on/off). The cyclops room has no exit on any map (ours, tibiaot74, JS engine): decided with
      the user, the lever makes both the way in (32233,32276,9 -> 32225,32271,10) and out (32225,32276,10 ->
      32232,32276,9), so turning it off traps whoever is inside (TibiaWiki 2006). Chests 2417/2521 as on the map.
      test_quests.py::test_thais_lighthouse_quest (two players from the Thais temple)
- [x] Throwing Star Quest - Thais Ancient Temple, underground park (no level; 1 player)
      Done 2026-09-24: the box 32522,32111,15 is now a quest box, uid 3619 (real-map table: 10 throwing stars);
      pick spot 32517,32107,14 with the ladder below. test_quests.py::test_throwing_star_quest, _rules
- [x] Triangle Tower Quest - Triangle Tower (E of Thais, desert edge) (no level; 1 player)
      Done 2026-09-24: the desert lever 32573,32121,7 had no script (quests/triangle_tower_lever.lua, aid 51020: the
      wall 32566,32119,7 goes / comes back, as tibiaot74); the top-floor chest 32565,32119,3 = uid 4510 (real-map
      table: garlic necklace, dwarven ring, 2 small sapphires). quests/thais/test_triangle_tower.py
- [x] Giant Smithhammer Quest - Plains of Havoc cyclops/minotaur camp (no level; 1 player)
      Done 2026-09-25: our map has two chests in the room below the temple; the west one (32775,32253,8) is the quest box,
      uid 4520 (giant smithhammer, talon, 100 gp - real-map table; decided with the user: one box). tests/quests/havoc/
- [x] Ornamented Shield Quest - Plains of Havoc Dragon Lair (no level; 1 (part 1); 2 (part 2) player(s))
      Done 2026-09-25 (both parts, decided with the user). The cave under the treasure room's pick spot (32774,32289,10) was
      missing from our map (and the JS engine's: solid earth) - copied from tibiaot74's map (tools/map-copy-tiles.py, new:
      32771-32779,32281-32291,11, its 7.7 lava borders left out). Krendorak's body under the fire field in its NE corner
      (32778,32282,11) uid 51068: bag (crystal key 3702, spike sword, dragon necklace, might ring, Krendorak's journal) +
      ornamented shield + steel helmet. Part 2: the partner's tile 32770,32282,10 (aid 51059, movements/plains_of_havoc.lua)
      holds the stalagmites 32771,32297,10 away; the chest behind them 32771,32299,10 uid 4516 (red bag: time ring, 5
      platinum, garlic necklace, spellbook, lyre - real-map table); the rope hole there leads out.
- [x] Alawar's Vault Quest - Senja / Folda (ice islands N of Carlin) (no level; 1 player)
      Done 2026-09-25: the three keys lay loose on the floor where their containers had been (our map and the JS engine's):
      chest 32031,31686,8 uid 4503 (key 4503), box 32172,31602,10 uid 4501 (key 4501), chest on the counter 32201,31571,10
      uid 4502 (bag: key 4502, dark helmet, 4 throwing knives, blank rune, 33 gp); the vault chests 32105/32109,31567,9 were
      missing: uid 4504 (3 white pearls), 4505 (broad sword). Doors got their key numbers (4503 Protected Area
      32035,31642,8; 4501 storage room 32039,31603,10; 4502 vault 32107-32108,31568,9). Senja cellar switch
      32180,31633,8 (aid 51025, quests/senja_vault_lever.lua): the walls 32186-32189,31626,8 and the switch vanish, back
      after 2 minutes (decided with the user). The vault portal goes to the castle roof 32189,31625,4 (decided with the
      user; 2006 wiki, tibiaot74 - the map sent you back behind the walls). pick.lua works through a field on the spot
      ("use pick on the fire field"); the router follows a pick / shovel hole onto a second hole ("fall two levels").
      tests/quests/carlin/test_alawars_vault.py (long path from Folda, short path from Senja, walls back, rules)
- [x] Crystal Wand Quest (Double SD Quest) - Demona, via Maze of Lost Souls (N of Carlin) (level 60 (door); 1 player)
      Done 2026-09-25: the two boxes by the thrones 32479/32481,31611,15 are on our map, the left one holds Ferumbras'
      twinkiller letter: left = uid 51028 (bag: SD rune with 2 charges + the letter), right = uid 51027 (crystal wand); no
      source says which box - tibiaot74 puts the wand left. quests/system.lua can now give an item's text (a letter, a map).
      The Maze of Lost Souls (done 2026-09-25): the entrance switch 32528,31724,10 (aid 51026, quests/mols_entrance_switch.lua)
      turned right opens the hole 32483,31633,9 (current wiki's coordinates) into the ring of level-30 gates, left shuts it;
      a ladder under it leads back up. tests/quests/carlin/test_maze_of_lost_souls.py
- [x] Demona Ring Quest - NOT 7.4 (decided with the user 2026-09-25): no chests on our map (nor tibiaot74's), first wiki page 2016;
      only Tibiantis lists it. Nothing to do
- [x] Fanfare Quest - Carlin graveyard crypt (no level; 1 player)
      Done 2026-09-25: the key box 32376,31802,7 = uid 3520 (bone key 3520, real-map table), the crypt's west double
      door 32400,31788-31789,8 now needs key 3520 (it had no key number), the chest 32390,31769,9 was missing - placed at
      tibiaot74's spot, uid 4507 (fanfare). Way out: rope up the hole. tests/quests/carlin/test_fanfare.py
- [x] Griffin Shield Quest (MoLS Quest) - Gates of Demona, Maze of Lost Souls (level 30 (the maze's gates); 1 player)
      Done 2026-09-25: the "level 30" is the four level-30 gates around the maze's landing (our map, aid 1030). The two slain
      skeletons and the dead body were missing: placed at tibiaot74's spots, uids 10062 griffin shield / 10063 dwarven axe /
      10064 obsidian lance (real-map table).
- [x] Power Ring Quest (Bronze Amulet / Femor Hills Goblin) - Femor Hills goblin cave (no level; 1 player)
      Done 2026-09-25: the two chests 32599/32601,31776,9 got the real-map table's uids 4511 (power ring, 2166 - the
      unworn one; the table says 2203, the worn one) / 4512 (bronze amulet). tests/quests/carlin/test_power_ring.py
- [x] Purple Tome Quest (Map Quest) - Demona library (level 60 (Demona gate); 1 player)
      Done 2026-09-25: the library's two maps lay in their bookcases as loot for the first comer (32423/32428,31591,15): now
      quest bookcases uid 51030 / 51031 (the maps with their texts); the purple tome was missing: bookcase 32421,31594,15 uid
      51029 (tibiaot74's spot). Out: the teleport "to the surface" 32400,31656,15.
- [x] The Queen of the Banshees Quest (Banshee Quest) - Under Ghostlands and Isle of the Kings (level 60 (Queen refuses <60); 1+ (easier with a team; seal … player(s))
      Done 2026-09-25. Our map had every piece and nothing ran. Seals = player storages 51101-51107 (Hidden, Plague,
      Demonrage, Sacrifice, True Path, Logic, the kiss); the seven doors 32223,31872-31890,14 (after the level-60 gate) carry
      them as action ids (quest doors). movements/scripts/banshee_seals.lua: the six blue flames (aids 51040-51045) mark
      their seal when their task is done and send you to its chamber on floor 15, whose portal now leads back (tibiaot74's
      pairs, confirmed by the chambers' monuments). Hidden: 2 ghosts + a demon skeleton per pass. Logic: the six switches
      32310-32314,31975-31976,13 as the wiki picture (western four right). True Path: the 15 floor tiles off the drawn path
      send you back (aid 51046). Sacrifice: a blood pool on 32243,31892,14 (spilled per player). Demonrage: a warlock tile
      (2 warlocks per player, once) and the levers 32220,31842-31846,15 in the order the wiki's coins show (2nd, 4th, 3rd,
      1st, 5th). Plague: white pearl on 32173,31871, black on 32180,31871, then the portals 32176/32177,31869. Way in:
      the two switches (aid 51050) each open one magic wall 32259,31890-31891,10; the hidden buttons behind them and a
      one-minute timer close them (decided with the user); the portal beside them leads back out. Floor 11: the switch
      32266,31861 (aid 51051) takes the magic wall off the trapdoor. The round chamber had no floor over its stairs down to
      the Seal of Logic: stairs 410 at 32252-32254,31942,12 (tibiaot74 has stairs there too; tools/map-set-attrs.py
      --new-tile). The Queen (npc/scripts/banshee_queen.lua, the transcripts): level 60, the six seals, the kiss ->
      the grave room 32202,31812,8. Final room: chests uid 51061-51064 (boots of haste, giant sword, tower shield, bag with
      stealth ring, stone skin amulet, 100 platinum - the 7.x wiki's set, decided with the user); the way out 32219,31913,15
      (to the Ghostlands) shuts the seventh door for good (kiss storage 2). tests/quests/carlin/test_banshee.py (the whole
      quest from the Carlin temple, the final room, the doors, the Queen, the flames, the walls, the planner rules)
  - [x] "Once you went downstairs you can't go up again": the ramp back up (32218-32220,31894,15) has fences (1547,
        block solid) - the map already does it; the route planner wrongly let a floor change with a fixed blocker on it
        be walked (fixed 2026-09-25). test_banshee_doors_need_every_seal
  - [x] The long hall's secret teleporter (done 2026-09-25, asked by the user): the row right south of the pick spot,
        32265-32267,31893,12 (aid 51056), sends you back to the hall's start 32266,31864,12 - between the pick spot and
        where the first seal's rope comes back up (the wiki's picture), so the hall's south end is reached only through
        the Hidden Seal. The route planner knows it (worldmap.SCRIPTED_TELEPORTS). test_banshee_hidden_teleporter
  - [x] "walk over the poison fields and a switch will appear" (floor 11; current wiki) - done 2026-09-26: the switch
        32266,31861,11 is off the map; the ground under the poison fields 32265,31862-31863,11 (aid 51112,
        movements/banshee_seals.lua) brings it back (aid 51051) until the next server start.
        test_banshee_switch_appears_on_the_poison_fields and the whole quest
  - [-] Explorer Society's Spectral Dress behind a quest door on the way (7.6) - not 7.4
- [x] Engine: a portal with both a map destination and a movement script crashed the server (0xC0000005: the engine
      moved the player and the script moved them again). The Banshee exit portal is scripted only; no other such portal
      on the map (checked 2026-09-25)
- [x] movements/scripts/onadd_questdoor.lua returned nothing for a numbered quest door (a Lua error each time one
      closed) - fixed 2026-09-25
- [x] The White Raven Monastery Quest (Family Brooch Quest / Island of King… - Ghostlands W of Carlin, Isle of the Kings (no level; 1 player)
  - [x] Part 1 done 2026-09-25: the brooch coffin 32248,31866,8 = uid 4506 (family brooch; real-map table), Dalbrect
        rewritten from the wiki transcripts (brooch/yes/yes = friend, storage 99999; passage/yes = 10 gp to the Isle deck
        32188,31958,7; per-player state; pz-lock check that works), Captain Jack (7.2, already on the Isle boat) sails back for
        20 gp - decided with the user: a way back by boat (the 7.x wiki's "20gp to return"; I first asked about a second
        Dalbrect, then found Jack). tests/quests/carlin/test_white_raven.py
  - [x] Part 2 done 2026-09-25 (with the Banshee Quest): the dead monk 32262,31861,11 = uid 51065 (backpack with the diary
        and its text, and the junk our map has in him - once per character). Costello (npc/scripts/costello.lua, transcripts):
        "fugio", "yes" -> storage 51110 opens the warded doors 32169,31933,7 / 32171,31936,7 (quest doors); "diary", "yes"
        takes the diary (item 1972) -> Blessed Ankh (2327, the "ankh" among the 7.2-7.24 quest items). test_banshee.py
  - [x] The Isle's restricted floor (done 2026-09-25, asked by the user): the stairs behind the key-3350 door put you
        on 32180,31925,5 (aid 51057, movements/scripts/isle_restricted.lua) = trespasser (storage 99998). Costello greets
        them "WHAT? ...", "crime"/"absolution": 500 / 1,000 / 5,000 / 10,000 gp by level (TibiaWiki), "Be gone!"
        otherwise; Captain Jack: "By the gods! You must be that intruder ... Begone!"; Dalbrect won't sail them either.
        Key 3350's bookcase in Costello's room (32180,31934,7) was plain loot: now uid 51066, once per character (the
        bag with the abbot's scroll and the key). test_isle_key_3350_bookcase, test_isle_trespass_and_absolution
- [x] NPC keyword handler (2026-09-25): every NPC shared one per-player "last conversation node" table
      (KeywordHandler.lastNode on the class), so a player a captain teleported mid-conversation got the old NPC's
      conversation from the next NPC (Captain Jack greeted with Dalbrect's words and ignored "tibia"). Each handler has its
      own now (npc/lib/npcsystem/keywordhandler.lua). Covered by test_white_raven.py (Dalbrect, then Jack)
- [x] NPC travel lines are never seen: selfSay is scheduled (Npc::doSay, SCHEDULER_MINTICKS) and the captain teleports
      Done 2026-09-26: the travel modules teleport 300 ms after the words (teleportAfterWords, npc/scripts/lib/npc.lua).
      test_travel.py test_the_captain_is_heard_before_the_ship_sails
      the player in the same call, so "Have a nice trip!" / "Set the sails!" is said after the player left. Teleport a
      moment later (addEvent) or say it at the destination - check what 7.4 showed
- [x] Draconia Quest - Draconia, via Hellgate under Ab'Dendriel (level 25 (door); 2 minimum (floor switches) player(s))
      Done 2026-09-26. Hellgate: both doors (32675,31671,10 / 32675,31649,10) now need key 3012; Elathriel sold a key with
      tibiaot74's number 2017 - now 3012. Pyramid: the doors got key numbers 3001-3008 (tibiaot74's pairs); the keys stay
      daily, first come (decided with the user: the 7.x "daily respawn") - the loose ones got their numbers, key 3001 lies
      in a dead skeleton at 32794,31572,7 (placed), key 3002 comes from the coffin 32802,31576,7 once per server start (a
      coffin is no container in 7.4; quests/draconia.lua), key 3005 moved off the statue tile it lay on (the server refuses items under a statue) to 32792,31591,6
      (tibiaot74's spot, "by a pillar or statue"), key 3008 is in the western bookcase. Ground floor levers
      (aid 51070): wall 32792,31581,7 / rock 32790,31594,7. 3rd floor: floor switches 32810,31595,5 and 32794,31595,5
      (aid 51071, movements/draconia.lua) hold the walls 32796,31595,5 / 32795,31578,5 open; the portals to key 3007's
      room got their destinations. Level-25 gate 32804,31583,2; chests 32803/32804,31582,2 uid 51075 (ice rapier, serpent
      sword) / 51076 (stone skin amulet, energy ring) - decided with the user. Top floor: levers 32802-32805,31584,1 Left,
      Right, Left, Right and the portal 32805,31587,1 (aid 51074) -> Ab'Dendriel 32701,31639,6, otherwise back.
      tests/quests/abdendriel/test_draconia.py (the route planner needed floors=9: Hellgate goes down to floor 15); 4 tests pass. take() and pick_up() in tibia74/quest.py now check the carried count goes up (a failed move used to pass when an earlier key of the same name was already in the backpack)
- [x] Elvenbane Quest (Elf Castle Quest) - Elvenbane castle, SW of Ab'Dendriel (no level; 1 player)
      Done 2026-09-26: the hole "surrounded by four stones" (32579,31679,7) was a closed stone pile - opened (decided with
      the user: both wikis' open hole; tools/map-set-attrs.py --set-ground). The tower top's 2 chests and 2 drawers were
      missing: placed at tibiaot74's spots, real-map uids 10053 (bag: spellbook, 2 small diamonds, 100 gp), 10054
      (manafluid, blank rune), 10055 (morning star), 10056 (dwarven shield). tests/quests/abdendriel/test_elvenbane.py
- [x] Orc Fortress Quest - Orc Fortress, W of Ab'Dendriel (level 40 (door); 1 player)
      Done 2026-09-26: the three chests 32980/32981/32985,31727,9 past the level-40 gate got uids 10031 knight armor /
      10030 knight axe / 10029 fire sword (decided with the user over Tibiantis' list; west to east as tibiaot74).
      tests/quests/abdendriel/test_orc_fortress.py
- [x] Circle Room Quest (Dwarven Quest / Dwarf Hell Quest) - Dwarf mines W of Kazordoon (level 32 (door); 1 player)
      Done 2026-09-26: the boxes' room 32511-32514,31944-31946,14 was shut by a locked door with no key number standing on
      lava (ours and the JS engine's map) - now a plain door 1213 on dirt at 32513,31947,14 (tibiaot74). Boxes 32512 /
      32514,31944,14 uid 3812 dwarven axe / 3813 war hammer (real-map table). Level-32 gate 32510,31956,13.
      tests/quests/kazordoon/test_circle_room.py
- [x] Crusader Helmet Quest - Deep Dwarf Mines W of Kazordoon (level 35 (door); 1 player)
      Done 2026-09-26: the slain skeleton 32427,31943,14 uid 10034 gives the crusader helmet (both wikis and the real-map
      table; Tibiantis alone says dwarven helmet). Level-35 gate 32475,31946,13, the hole behind it.
      tests/quests/kazordoon/test_crusader_helmet.py
- [x] Emperor's Cookies Quest - Emperor Kruzak's chambers, Kazordoon (no level; 1 player)
      Done 2026-09-26: the way into the chambers had three locked doors with no key number (32625,31917,3, 32636,31911,3,
      32639,31906,3) - plain doors now (tibiaot74). Chest 32605,31908,3 uid 3808 key 3800; door 32645,31906,3 key 3800;
      chest 32648,31905,3 uid 3809 bag with 20+7 cookies and key 3801; barracks door 32600,31926,6 key 3801; chest
      32599,31923,6 uid 3810 key 3802 (the 7.x wiki names each chest's contents; the real-map table's ids).
      Key 3802 opens the Dwacatra prison cells 32602-32603,31962/31966/31975,14 (tibiaot74's doors); the Mine Hub room's
      door is not found yet. tests/quests/kazordoon/test_emperors_cookies.py
- [x] Explorer Brooch Quest - Jolly Axeman tavern sewer, Kazordoon (no level; 1 player)
      Done 2026-09-26: the dead human 32636,31873,10 below the four grates (our map had lost it) uid 51078 gives an elven
      brooch - the explorer brooch is a 7.6 item that looks the same (decided with the user).
      tests/quests/kazordoon/test_explorer_brooch.py
- [x] Iron Hammer Quest - Minotaur cave W of Kazordoon (no level; 1 player)
      Done 2026-09-26: the box between the beds 32434,31938,8 (lost on our map; tibiaot74's) uid 3807 iron hammer. Way in:
      the loose stone pile (shovel). tests/quests/kazordoon/test_iron_hammer.py
- [x] Longsword Quest - Troll cave E of Dwarf Bridge (no level; 1 player)
      Done 2026-09-26: the chest and two boxes at the large room's north end 32643,31969 / 32644,31968 / 32648,31970,8 uid
      3804 longsword + mirror / 3805 3 blank runes + wooden doll / 3806 wedding ring + 76 gp (real-map table; which
      container holds which is written nowhere: west to east). Way in: the hidden hole 32663,31962,7 (shovel).
      tests/quests/kazordoon/test_longsword.py
- [x] Steel Helmet Quest (Minotaur Tower Quest) - Minotaur tower W of Kazordoon (no level; 1 player)
      Done 2026-09-26: the current spoiler's four spots - drawers 32460,31951,5 uid 3800 56 gp, box 32462,31947,4 (lost on
      our map) uid 3802 steel helmet, box 32464,31957,5 uid 3801 47 gp, chest 32467,31962,4 uid 3803 the Horned Fox's
      scroll (real-map table's ids and text). tests/quests/kazordoon/test_steel_helmet.py
- [x] The Paradox Tower Quest - Paradox Tower, near Kazordoon (+ PoH, Edron, Carlin, Thais,… (level 30; 1 player; premium)
      Done 2026-09-26. NPCs (npc/scripts/lib/npc.lua knowledgeChain): Oldrak 6664, Zoltan 6665, Padreia 6666, Lubo 6667 -
      each answers "hi" now (Zoltan, Padreia, Lubo only knew "hello"), per-player state (one talk_state was shared by every
      NPC and player), the storage only after the NPC before; Oldrak lost the 8.x hallowed axe, Padreia and Zoltan got
      their transcript lines back, Lubo keeps his shop. The Riddler (rewritten): the three seals word for word, a wrong
      answer or another player's number -> Hellgate 32725,31589,12, the player's own number (A Prisoner's SUMS[6668]) ->
      the treasure room; the old one let any digit through and knew one answer of four. Map + scripts
      (actions/quests/paradox_tower.lua, movements/paradox_tower.lua): dead tree 32497,31887,7 key 3899 once per
      character, the trap half the time (up to 200 hp, never the last one; poison fields); the carving 32566,31957,1 takes
      a skull from each of the four stones (poison fields instead) -> 32479,31923,7, the carvings back
      32486-32487,31927-31928,7; the plate 32481,31905,7 (under grass) turns the stone 32478,31902,7 into stairs, the
      doorway 32478-32479,31907,7 back; levers R R L L R L + switch 32479,31905,6 -> ladder 32479,31903,6; the ghoul
      room's switch 32481,31904,5 makes a crate, a crate in the corner 32476,31900,5 makes the ladder 32478,31904,5 and
      taking it away removes it (our map had the crate and ladder saved in the solved state - removed); door
      32479,31903,4 key 3899; fruit on the counters + switch 32479,31905,4 -> ladder 32476,31904,4; knights + switch
      32478,31904,3 -> ladder 32479,31904,3; the five forcefields got their destinations; treasure chests
      32477-32480,31900,1 uids 51091 phoenix egg / 51092 100 platinum coins / 51093 32 talons / 51094 wooden wand (both
      decided with the user), the plates x 32476-32481, y 31902/31903 destroy them (K W T T T K / E E E K W W).
      Tests: tests/quests/kazordoon/test_paradox_tower.py (the missions and their order, the tree, the sacrifice, the whole
      climb to two rewards, another player's number). Planner: machete + jungle grass.
      Also tested 2026-09-26: the climb to the stones with Levitate (premium) and with parcels (free: three parcels on
      the ledge, a step north); a free account's Levitate is refused. The ghoul could never spawn nor move - its room
      was protection zone (tools/map-set-attrs.py --tile-flags 0 on 32476-32481,31900-31901,5; the room stays walled
      in) - now it pushes the crate into the corner by itself (test_paradox_tower_the_ghoul_pushes_the_crate, ~4 min).
      Premium: the quest is premium (TibiaWiki 2006, Tibiantis); on our server only Zoltan (Edron) could make it so,
      and the boats take free accounts (see "Boats: premium only?"). A Prisoner always asks the colour.
- [x] Black Knight Quest (Crown Set) - Villa Scapula swamp, north of Venore (~32827,31959,7) (level 50 (door); 1+ player(s))
      Done 2026-09-26: key 5010 in the dead trees 32813,31964,7 (uid 51033) and 32800,31959,7 (uid 51034, SAME_QUEST: one
      key per character); the basement door 32824,31969,8 got key number 5010; past the level-50 gate 32874,31974,12 the
      southern trees give uid 2519 crown shield (32868,31955,11) and 2487 crown armor (32880,31955,11) - decided with the
      user over Tibiantis. tests/quests/venore/test_black_knight.py
- [x] Blood Herb Quest (Witchesbroom) - Greenclaw Swamp, west of Venore (no level; 1 player)
      Done 2026-09-26: the dead tree 32769,31968,7 uid 10032 gives the blood herb (real-map table). Wyda (npc/scripts/wyda.lua, her transcript lines)
      trades the herb for her witchesbroom (item 2324, "broom" before - the wiki's weight 11.00 and flavor text); the
      trade's own lines are not written down anywhere (ours). tests/quests/venore/test_blood_herb.py
- [x] The Desert Dungeon Quest (Desert / Vocation / 10k Quest) - Below Jakundaf Desert (entrance ~32649,32093,7) (level 20 (door); 4, one of each vocation player(s); Knight + Paladin + Druid + Sorcerer)
      Done 2026-09-26: the forcefield in the middle of the vocation room (32673,32089,8) took anyone into the reward
      room - removed (decided with the user); the four switches (aid 51095, movements/desert_dungeon.lua) go down only for
      their vocation with the sacrifice on the basin behind (sorcerer spellbook E, druid red apple W, paladin crossbow N,
      knight sword S); the paladin's lever 32673,32086,8 (aid 51096) wants all four at level 20+, takes the sacrifices and
      teleports them into the reward room; chests 32668,32069,8 uid 51097 100 platinum coins and 32675,32069,8 uid 51098
      green bag (protection amulet, ring of healing, magic lightwand, ankh). tests/quests/desert/test_desert_dungeon.py
- [x] Dragon Tower Quest - Shadowthorn, south-east of Venore (no level; 1 player)
      Done 2026-09-26: the two boxes 33072,32169,2 (uid 3505: 2 small sapphires, 30 burst arrows, 60 poison arrows,
      100 gp) and 33079,32169,2 (uid 3506: bow, mana fluid, life fluid) - the real-map table's split, decided with the
      user. Needs a machete (Shadowthorn). tests/quests/venore/test_dragon_tower.py
- [-] Heaven Blossom Quest - Shadowthorn underground (no level; 1 player)
      Not 7.4 (decided with the user 2026-09-26): the wiki page is from 2014 and the pickupable heaven blossom came
      with 7.8; our 7.4 one is an immovable plant. Nothing scripted.
- [x] Iron Helmet Quest (Muriel's Letter) - Plains of Havoc, west of the cyclops/orc/minotaur camp (~32… (no level; 1 player)
      Done 2026-09-25: the body was missing - dead human at 32769,32225,7 by the sycamore (tibiaot74's spot), uid 4518:
      backpack with iron helmet, SD rune, leather armor, Muriel's letter (real-map table's text), worn leather boots,
      longsword (decided with the user: the 2006 wiki's list + the longsword of the other sources).
- [x] Isle of the Mists Quest (Druid Quest) - Isle of the Mists; teleport in PoH (~32831,32295,7) (no level; 1 player; druid, per the quest legend (the wiki d…)
      Done 2026-09-25: druids only (decided with the user): the portal 32831,32294,7 is scripted (aid 51060) and puts others
      back; the box 32852,32332,7 uid 51067 = 3 small emeralds (the 2006 wiki; decided with the user); the book is in the
      bookcase beside it on our map.
- [x] Orc Shaman Quest - Swamp/orc cave east of Venore (~33055,32030,7) (no level; 1 player)
      Done 2026-09-26: the box in the south-east corner (lost on our map) placed at tibiaot74's 33089,32030,9, uid 3504:
      a bag with a magic lightwand, an axe ring, a blank rune. tests/quests/venore/test_orc_shaman.py
- [x] The Outlaw Camp Quest (Bright Sword Quest) - Outlaw Camp, west of Thais/Venore road (~32615,32253,7) (level 45 (door); 1 (2 recommended) player(s))
      Done 2026-09-26 (the full mechanism, decided with the user): keys 3301/3302/3303 in the trees 32617,32250 /
      32609,32244 / 32651,32244,7; key doors 32614,32175,9 (3303), 32619,32241,8 (3301), 32619,32240,8 (3302),
      32620,32199,10 (3304) got their numbers; actions/quests/outlaw_camp.lua: the switch 32614,32173,9 moves the oven
      32623,32188,9 (lost on our map) in front of the key-3304 box 32623,32187,9; the power ring on the counter
      32594,32214,9 + switch 32594,32212,9 opens the right passage (32603-32604,32216,9) and puts the ring behind the mill
      room's wall (32613,32220,10 - it lay there already, removed); the mill switch 32616,32222,10 (placed) once per server
      start: the ring into a fire field, and with a barrel in the notch 32614,32209,10 the stone 32614,32206,10 (placed)
      goes for 5 minutes. Chest 32620,32198,10 uid 2407: bright sword + red gem (decided with the user).
      tests/quests/venore/test_outlaw_camp.py
- [x] Panpipe Quest (Fire Devil Quest) - Desert Dungeon, Jakundaf Desert (no level; 1 player)
      Done 2026-09-26: the hollow rock 32652,32107,7 uid 3621 gives key 4055; its door 32643,32128,8 got the number;
      the box behind the fire devil (lost on our map) placed at 32644,32131,8 uid 3622: a bag with panpipes, 2 small
      amethysts, a power ring. tests/quests/desert/test_panpipe.py
- [x] Power Bolts Quest - Hole south of the PoH temple (~32815,32280,7) (no level; 1 player)
      Done 2026-09-25: the dead human 32818,32284,8 uid 4514: bag (5 power bolts, 12 burst arrows) + two handed sword (the
      real-map table's 4514 + 4513); the Dreammaster book lies beside it on our map.
- [x] Silver Brooch Quest (Mummy Quest) - Greenclaw Swamp caves (~32700,31992,7) (no level; 1 player)
      Done 2026-09-26: the north coffin 32775,32006,11 uid 3503: a bag with the silver brooch, 2 small rubies, 3 small
      diamonds. tests/quests/venore/test_silver_brooch.py
- [x] Skull of Ratha Quest (incl. Wolf Tooth Chain and Crystal Necklace) - Amazon Camp, north of Venore (~32846,31920,7) (no level; 1 player)
      Done 2026-09-26: Witch Hill boxes 32847,31917,6 (uid 3501: bag, white pearl + skull of Ratha) and
      32845,31917,6 (uid 51032: bag, wolf tooth chain + dwarven ring); basement chest 32867,31909,8 (uid 3502: bag, 100 gp,
      crystal necklace, 2 black pearls). tests/quests/venore/test_skull_of_ratha.py
- [x] Time Ring Quest (Shadowthorn Quest) - Shadowthorn underground (~33060,32182,7) (no level; 1 player)
      Done 2026-09-26: the chests 33038-33040,32171,9 uid 10039 time ring / 10040 elven amulet (50 charges) / 10041 crystal
      ball (real-map table; west to east as tibiaot74). Shadowthorn needs a machete (jungle grass at 33020-33021,32145,7).
      tests/quests/venore/test_time_ring.py
- [x] Voodoo Doll Quest - Greenclaw Swamp, north side (~32737,31953,7) (no level; 1 player)
      Done 2026-09-26: the two boxes against the east wall (lost on our map) placed at tibiaot74's 32757,31957,9 (uid
      3500 voodoo doll) and 32758,31952,9 (uid 2162 magic lightwand). tests/quests/venore/test_voodoo_doll.py
- [x] Medusa Shield Quest (Star Room / Necromancer Quest) - Drefia, west of Darashia (~32996,32413,7) (level 60 (door); 1+ (team advised) player(s); premium)
      Done 2026-09-26: our map had no reward coffin - a stone coffin at 33049,32399-32400,10 (tibiaot74's spot; decided
      with the user), uid 10033: medusa shield, skull staff, blue robe (real-map table). Level-60 gates 33032/33037,32398,11.
      tests/quests/darashia/test_medusa_shield.py
- [x] Plate Armor Quest (Ghost Ship) - Ghost Ship, random on the Venore to Darashia boat (no level; 1 player; premium)
      Done 2026-09-26: nothing sent players to the Ghost Ship - Captain Fearless (barco_venore.lua) now hijacks one
      Venore-Darashia trip in ten onto its deck 33319,32172,6 (conversation and "bring me to"; decided with the user);
      the coffin 33327,32180,8 uid 10066 gives the plate armor; the ship's forcefield 33328,32181,6 goes on to Darashia
      33290,32481,7 (it went to Venore; decided with the user). tests/quests/darashia/test_ghost_ship.py
- [x] Stealth Ring Quest (Minotaur Pyramid) - Minotaur (Dark) Pyramid, north-east of Darashia (~33312,322… (no level; 1 player; premium)
      Done 2026-09-26: the Minotaur Pyramid's bottom-floor coffins 33315,32282,11 uid 3900 stealth ring (SE) and
      33315,32277,11 uid 3901 protection amulet (NE). tests/quests/darashia/test_stealth_ring.py
- [x] The Ancient Tombs Quest (Helmet of the Ancients) - 8 Ankrahmun tombs (level 75 (doors); team advised player(s); premium)
      In progress (2026-09-28). Shared (movements/ancient_tombs.lua, decided with the user): level-75 gates (aid 1075,
      10 gates); the mystic flames lost their free map destinations - a scarab coin on the basin beside (aid 51120)
      takes whoever stands on the flame down, the coin is used up; the pharaohs' portals (aid 51121) lead to the
      sarcophagus room only with the pass item, which they take, else to the start of the tomb; every pharaoh drops his
      pass item every kill (loot 100%, names fixed to "Omruc" etc.); sarcophagi uid 8206-8212 (tibiaot74's) with the
      current wiki's pieces. Tests: tests/quests/ankrahmun/tombs.py + test_tomb_<pharaoh>.py.
      Vashresamun: done - instruments (aid 51122, uids 51130-51137) drum, panpipes, lute, lyre, cornucopia (wiki picture
      + tibiaot74), per player (storage 51122), open the door 33184,32665,15 (aid 51123); our map's arrival was on the
      door's side: teleports swapped to the wiki's order (decided with the user).
      Rahemos: done - entrance pile 33133,32640,7 restored (tibiaot74); hat switches (aid 51124, hats uid 51140-51142):
      random carrot, 200 hp a wrong one, per player storage 51125 = the quest door placed at 33122,32765,14 (decided with
      the user); a counter on the switches' only reachable tile 33119,32762,14 removed (tibiaot74 + wiki picture); the
      bridge's middle rows turned to lava (tibiaot74 + "broken bridge"; decided with the user).
      Dipthrah: done - entrance pile 33133,32568,7 restored; the 16 wrong word doors (aid 51126) send you back to the
      first room 33072,32640,15 (decided with the user); the gauntlet's exit teleport pointed into rock: now tibiaot74's
      33095,32590,15. The current wiki's switches before the 7th floor are not on the 7.4 map.
      Done 2026-09-29: all eight tombs and the stone table (the seven pieces become the helmet; a small ruby makes it
      glow 30 minutes) pass - test_tomb_<pharaoh>.py. Test fixes: the Thalas forcefield rule starts beside the tile
      the full run leaves its poison field on; Ashmunrah's portal is stepped on from beside the tile it sends you
      back to; the router goes around Ashmunrah's throwers (in their wall slots) and pushes Morguthis's deathslicers
      (nothing hurts them; TibiaWiki: "You can push it") - step_onto clears a monster standing on a portal.
- [x] The Djinn War - Efreet Faction (Green Djinn Quest) - Mal'ouquah + Ankrahmun, Carlin, Thais, Ulderek's Rock, Asht… (level 30 (fortress door) / 40 (Orc King door); 1 player; premium)
- [x] The Djinn War - Marid Faction (Blue Djinn Quest) - Ashta'daramai + Kazordoon, Mal'ouquah, Ulderek's Rock (level 30 / 40; 1 player; premium)
      Done 2026-09-29 (both sides): the NPC ports could not be finished (no Tear, no lamp exchange, trade open to
      all, "passage" not understood, missing functions, storages shared with quest chests). Rewritten on
      npc/lib/djinn.lua (storages 70100 Efreet / 70101 Marid progress, 70102 Melchior's word, 70103 Orc King's
      guards); ShopModule.mayTrade gates the traders. Map: fortress gates aid 1030; Tear basin's northern tiles aid
      51170; the gemmed lamps by Gabel's / Malor's beds aid 51171 (actions/scripts/quests/djinn_war.lua). Decided with
      the user: DJANNI'HAH only (7.4), traders only after the side is done, the basin's northern half, Maryza's
      cookbook repeatable. tests/quests/ankrahmun/test_djinn_war.py (13 tests). Router: a creature that blocks a tile
      twice is gone around; one nothing hurts is pushed (deathslicers); walk_near accepts standing next to an NPC
      on the tile it aimed for.
- [x] Serpentine Tower Quest / White Pearl Quest (one quest) - Serpentine Tower (Sorcerer guild), Ankrahmun (~33147,32866,… (no level; 1 player; premium)
      Done 2026-09-27: the open fire 33145,32862,7 (aid 51180, movements/serpentine_tower.lua): a pot put on it becomes
      the campfire with a pot (1428) until the restart (decided with the user); the forcefield 33148,32864,7 (aid 51181)
      then goes into the pearl room 33151,32864,7; the way out 33150,32864,7 -> 33147,32864,7 always (tibiaot74; decided
      with the user). Chest 33150,32862,7 (lost on our map) uid 3700: white pearl (real-map table). The continuation
      (scripted on the user's wish): the wall lamp above the barrel 33151,32861,7 (placed, aid 51182) opens the fire
      elemental's cage 33151,32866,8; its switch 33152,32866,8 (aid 51183) takes the magic walls 33148-33149,32867-32868,9
      from the green djinn's hall; both close after 5 minutes once no player is inside (decided with the user). The
      djinn's and vampire's switches do nothing. tests/quests/ankrahmun/test_serpentine_tower.py
- [x] Serpentine Tower: the 5-minute close of the fire elemental's cage and the djinn hall's magic walls is untested
      Done 2026-09-29: test_serpentine_tower_continuation waits them out (open while a player is in the hall).
- [x] Action id clash: the Serpentine Tower took 51100-51103, the Banshee seal doors' ids (their doors ran the tower's
      scripts; the Banshee final room was unreachable). Fixed 2026-09-29: the tower uses 51180-51183.
- [x] Annihilator Quest - Edron, Hero Cave (deepest floors) (level 100 (lever/tiles; level-100 door at que…; exactly 4 player(s); premium)
      Done 2026-09-24: nothing was scripted (lever, squares, chests without ids). quests/annihilator_lever.lua (aid
      51011 on the lever 33226,31671,13): four players on 33222-33225,31671,13, each level 100+ and without a reward
      -> 6 demons + teleport (tibiaot74's positions); decided with the user: once per server save (the lever stays
      down until the restart), "Sorry, not possible." for a wrong team. Chests 51012-51015 (demon armor, magic sword,
      stonecutter axe, present + annihilation bear) share storage 51012 (system.lua SAME_QUEST; rewards now looked
      up per object first). test_quests.py::test_annihilator_quest (4 master sorcerers, Ultimate Explosion; team of
      3 and a veteran refused; the pulled lever refuses the next team), test_annihilator_level_door, _rules
- [x] Behemoth Quest - Edron, Cyclopolis (deep) (level 60 in 2004 (level door; raised to 80 in…; 1+ (team advised) player(s); premium)
      Done 2026-09-24: level 60 (decided with the user: TibiaWiki 2005, Tibiantis and tibiaot74's gate; our map's gate
      said 80 - now aid 1060 at 33297,31670,14). The lever that moves the stones (33295-33299,31677,15) had no script:
      2026-10-03 the user found two levers - ours, placed at tibiaot74's 33293,31718,12, and the map's own (unscripted,
      the one players find) at 33290,31715,12 under a fire field and a dead orc. The map's own got aid 51021
      (quests/behemoth_lever.lua, both ways), ours was removed. The four chests had no ids: 51023 demon shield (2520 is the Demon
      Helmet's), 2466 golden armor, 2427 guardian halberd, 51022 bag (platinum amulet, life ring, crystal ring,
      3 small diamonds, 4 small sapphires) - TibiaWiki 2005 / tibiaot74; one of each per character (decided with the
      user). The lever lies under the dead wolf and the fire field ("move corpses"). tests/quests/edron/test_behemoth.py.
      tools/map-set-attrs.py --bottom (an item under what lies there)
- [x] Vampire Shield Quest - Edron, Hero Cave (Warlock room / Temple of Xayepocax) (level 70 (level door); 1+ player(s); premium)
      Done 2026-09-25: chests 33189/33195,31688,14 got the real-map table's uids 1017 dragon lance / 1016 vampire shield
      (which is which: tibiaot74); the box outside the level-70 gate was missing - placed at 33188,31682,14, uid 1032
      (strange symbol, black pearl, mysterious fetish). tests/quests/edron/test_vampire_shield.py
- [x] Demon Helmet Quest - Edron, Hero Cave → Demon Hell (level 100 (level door); team (4 demons + banshees in … player(s); premium)
      Done 2026-09-24. Scripted what the 7.4 map had but nothing ran: the Gate of the Lost Souls (step tiles aid 50665
      at 33190/33191,31629,13 open the wall 33210-33212,31630,13 only while both are held - decided with the user;
      current wiki), the quest-room switch aid 50666 (takes the immovable stone 1355 from the boxes and opens the
      portal out 33316,31591,15 -> 33328,31592,14; tibiaot74's positions). The locked door after the level-100
      gate (33211,31634,13) had no key number: now key 6010 from the Parchment Room (decided with the user; current
      wiki + 2006 "Demon key"). Boxes 2493/2520/2645 as on the map.
      test_quests.py::test_demon_helmet_quest (the hero does the Parchment Room for the key, two friends hold the
      gate). Router: chained floor changes (the hole onto a hole = "down 2 floors"), gates of expertise put you
      in the doorway
- [x] Parchment Room Quest - Edron, Hero Cave (no level; 1+ (5 demons) player(s); premium)
      Done 2026-09-24: coffin 33063,31624,15 = uid 10057 (real-map table): bag with golden key 6010, bone, stealth
      ring, 2 talons, skull (system.lua REWARDS; bag contents may now carry a key number). The seal (parchment, aid
      51010) calls 4 demons when taken off the coffin (movements RemoveItem; tibiaot74's spots) and comes back after
      60 s (tibiaot74's time, no source); the coffin does not open while sealed (it is always-on-top, so it was
      usable through the seal). test_quests.py::test_parchment_room_quest. Router: pick holes (mud aid 100) and
      sewer grates (use -> one floor down: the only way out of the room, then rope up through the pick hole)
- [x] Ring Quest - Edron, Hero Cave (no level; 1+ player(s); premium)
      Done 2026-09-25: both chests were missing - placed at 33131/33134,31624,15 (tibiaot74), uid 2169 time ring / 2207
      sword ring. tests/quests/edron/test_ring.py
- [x] Wedding Ring Quest (Hero Cave) - Edron, Hero Cave (no level; 1+ player(s); premium)
      Done 2026-09-25: both chests were missing - placed at 33158,31621-31622,15 (tibiaot74), uid 2121 wedding ring /
      2201 dragon necklace. tests/quests/edron/test_wedding_ring.py
- [x] Double Hero Quest - Edron, Hero Cave (no level; 1+ player(s); premium)
      Done 2026-09-25: boxes 33109/33110,31679,13 got uid 4522 club ring / 4523 red gem (real-map table).
      tests/quests/edron/test_double_hero.py
- [x] Triple UH Rune Quest (now "Adorned UH Rune Quest") - Edron, Hero Cave (no level; 1+ player(s); premium)
      Done 2026-09-25: the box was missing - placed at 33136,31601,15 (5-monk floor), uid 1015: 5 mana fluids + UH rune
      with 3 charges (real-map table, TibiaWiki 2006). tests/quests/edron/test_triple_uh.py
- [x] Barbarian Axe Quest - Edron Orc Cave (bottom) (no level; 1+ player(s); premium)
      Done 2026-09-25 with the other four Orc Cave quests: box 33185,31945,11 uid 1030 (barbarian axe + scimitar in one box -
      the real-map table's single uid; tibiaot74 and the current wiki's Berserker page have two). The entrance stone
      (33171,31897,8) had an unscripted lever on the original map: quests/edron_orc_cave_lever.lua (aid 51024).
      tests/quests/edron/test_orc_cave.py
- [x] Berserker Treasure Quest - Edron Orc Cave (no level; 1+ player(s); premium)
      Done 2026-09-25: box 33199,31923,11 uid 1031 (3 white pearls, 175 gp). test_orc_cave.py
- [x] Dark Armor Quest - Edron Orc Cave (giant spider pit) (no level; 1+ player(s); premium)
      Done 2026-09-25: dead skeleton 33176,31871,12 uid 4521 (dark armor; the 7.x text says "a dead body", tibiaot74 a
      skeleton). test_orc_cave.py
- [x] Poison Daggers Quest - Edron Orc Cave (shaman level) (no level; 1+ player(s); premium)
      Done 2026-09-25: chest 33155,31880,11 uid 1034 (backpack: 2 poison daggers, 30 poison arrows). test_orc_cave.py
- [x] Shaman Treasure Quest - Edron Orc Cave (room with a Sacrificial Stone) (no level; 1+ player(s); premium)
      Done 2026-09-25: dead skeleton 33127,31885,9 uid 1033 (3 blank runes). test_orc_cave.py
- [x] Edron Goblin Quest - Edron Goblin Cave, west of town (no level; 1 player; premium)
      Done 2026-09-25: the chests were missing - placed at 33095,31800-31801,10 by the throne, uid 1028 steel shield / 1029
      silver amulet (real-map table's Edron entries; the Thais Silver Amulet box moved to uid 2170). The way back is the
      grassy area's pitfall: pitfall.lua now drops the player (it left them standing on the open hole) and the router
      knows grass 293 as a way down. tests/quests/edron/test_goblin.py
- [x] Troll Cave Quest - Edron Troll Cave, west of town (no level; 1 player; premium)
      Done 2026-09-25: the boxes were missing - placed at 33143,31719/31721,10, uid 1026 brass legs / 1027 garlic necklace.
      tests/quests/edron/test_troll_cave.py
- [x] Fire Axe Quest - Edron Dragon Lair (level 60 (level door); 1+ player(s); premium)
      Done 2026-09-25: chest 33078,31656,11 uid 1019 (ring of healing, dragon necklace, 7 small diamonds) and dead skeleton
      below the pick hole 33084,31650,12 uid 1018 (fire axe) were missing - placed (tibiaot74, real-map table).
      tests/quests/edron/test_fire_axe.py
- [x] Postman Missions Quest - starts at Kevin (post office between Thais and Kazordoon), … (no level; 1 player; premium)
      Done 2026-09-30: blocked at mission 1 (nothing counted the passages), no map object was scripted, the NPCs kept
      their topic in a global every NPC shares (Kevin's "yes" chain could reset the quest), several had no greeting.
      npc/lib/postman.lua (progress storage 70200 1-31, 70201 passages, 70202 bones, 70203 sniffs, 70204 measurements,
      70205 Markwin, 70206 present taken); npc/lib/questnpc.lua (the NPC builder, shared with the djinns). Kevin,
      A Strange Fellow, Talphion, Noodles, Hugo, Markwin, Benjamin, Liane, Olrik, Dove, Chrystal rewritten (the 2006
      transcripts), Eloise/Dermot/Lokur/Kroox patched. StdModule.travel and the captains' "bring me to" count the
      passages and give Grand Postmen 10 gp off; ShopModule.price: parcels 10 / letters 5 gp for Assistant Postmen.
      Map (actions/scripts/quests/postman.lua): Folda mailbox 32013,31562,4 aid 51190 (crowbar); Kevin's doors
      32569/32567,32023,6 aid 51191/51192 and chests placed on the closets' counters 32569/32567,32024,6 aid
      51194/51195 (present once; letter bag needs 500 oz); Waldo's door 32515,32248,8 aid 51193, body 32514,32248,8
      aid 51196; Santa's mailbox 31948,31711,6 aid 51197 (the bag becomes a red bag). Royal mailboxes aid 51199 (Minotaur
      Pyramid 33307,32292,7; Mine Hub 32448/32454/32459,31964-31975,10; Drefia 32995,32446,7; Mintwallin
      32423,32095,15; Cyclopolis 33271,31656,8; Shadowthorn 33083,32184,8; Orc Fort 32970,31778,7) - the engine
      (Game::playerMoveItem) refuses non-Arch Postmen. Letters at Benjamin/Chrystal 10 -> 8 gp (TibiaWiki 2006).
      Decided with the user: 10 gp off a passage, royal mailboxes locked, Markwin wants his guards dead, Noodles any
      order / keeps nothing. tests/quests/postman/test_postman.py.
- [ ] Postman: the "surface" royal mailbox near the Kazordoon mines (2006 wiki, no usable coordinate) is not locked
      (the captains' quoted price: done 2026-09-30 - StdModule.say quotes the travel node's travelCost)
- [-] Iron Ore Quest - Dwarf Mines near Kazordoon (no level; — player(s); —)
      Probably not 7.4 (wiki page from 2011, no version, not on Tibiantis) - left out unless a 7.4 source turns up
- [x] Minotaur Leather Quest - raft south of Thais - NOT 7.4 (checked 2026-09-24): the item "minotaur leather" is not
      in our 7.4 item list at all; the wiki page is from 2011 with no version; not on Tibiantis. Nothing to do

- [x] Dalbrect (boat to the Isle of the Kings, west of Carlin, 32206,31756): he only sails for players who
      brought his family brooch (item 2318), but there is no way to get it - in the Ghostlands there is a spot
      you click (use) to find it. Make that work + test: brooch -> Dalbrect -> 10 gp -> Isle of the Kings
  - [x] dalbrect.lua: the "blood stains" check never blocks (hasCondition(...) ~= 1: the engine returns
        true/false); talk_state is a global shared by every player talking to him
        Done 2026-09-25 with the White Raven Monastery Quest part 1 (see there); Captain Jack had the same two bugs
  - [x] Widen tests/test_spells.py's script scan: also `== 1` / `~= 1` / `== 0` on functions that return
        true/false (the same bug class as isInArray(...) == TRUE)
        Done 2026-10-03: luascan.boolean_functions (143) + test_no_script_compares_a_boolean_function_with_1_or_0 - none found
- [x] Houses: confirm `Tibia74-houses.xml` loads, rent, doors, ownership commands
      Done 2026-10-04: 816 houses in file and map, no warnings; doors, aleta sio/som/grav, alana sio, items kept over
      relog and restart - tests/test_houses.py (15). Fixed (NEEDS REBUILD): game.cpp internalTeleport checked the source
      tile for the house rule (a removed guest stayed inside); house.cpp kickPlayer let a guest kick other guests.
      Rent is never charged (payHouses only on /closeserver serversave) - with the daily save (Q5). Open: Q17.
  - [x] 92 houses share a door number between two doors (aleta grav on the second edits the first) - renumber (map tool)
        Done 2026-10-04: tools/renumber-house-doors.py - 352 doors in 92 houses renumbered (backup in the scratchpad);
        test_houses.py::test_no_house_has_two_doors_with_one_door_number
- [x] Temples: log in to each of the 47 towns' temple positions, confirm walkable
      Done 2026-10-03: test_temples.py - all 47 temples (towns read from the map): a character logs in right on
      the temple and steps off and back; a town_id character at 0,0,0 starts there; the 8 mainland temples are
      protection zone. Isle of Solitude and Home (towns 10/21) share 32316,31942,7
- [x] Rookgaard has no protection zone tile at all in the map (temple 32097,32219,7, depot included) - confirm
      the 7.4 state. 2026-10-03: kept - the user remembers none, and the source map has none on the whole island
      (ours and the JS engine's copy: 0 of 121,586 tiles; the Thais temple 176). test_temples.py
      test_rookgaard_temple_is_no_protection_zone
- [x] Depots and mailboxes (mailboxes weren't in 7.4 - check the map)
      Done 2026-10-04: mail is from 4.0 (TibiaWiki Updates/4.0), so mailboxes belong; Rookgaard has no depot (right).
      Lockers per town match the wiki (Thais 50 vs 46 in 2011 - kept). Fixed: Venore's main depot house (20 lockers) had
      no depot id (opened depot 0) - now 8 (tools/map-set-attrs.py --depot-id). Mail to a town without a locker (Fibula,
      Senja...) was lost - now refused (town.h/depot.cpp/mailbox.cpp, NEEDS REBUILD). tests/test_depots.py (19).
      Quest chests: Cip's "You have found a rapier. Weighing 15.00 oz it is too heavy." (Nostalrius chests.lua) in
      system.lua, postman.lua, paradox_tower.lua; getItemWeightById (luascript, rebuild; a Lua fallback works now).
  - [x] Live DB: items saved in depot 0 from Venore's main depot are now out of sight - move them to depot 8 - answered 2026-10-04: no, leave them (test characters only)
        (player_depotitems) when the server is stopped? (ask the user)
- [x] Teleports, ladders, holes, rope spots, shovel spots work
      Done 2026-10-03: tests/test_map_mechanics.py (48 cases: Rookgaard, Thais, Carlin, Kazordoon, Venore, Edron,
      Ab'Dendriel/Hellgate, Ankrahmun, Darashia): ladders, sewer grates, stairs up/down (incl. landing shifted off a ramp),
      holes, trapdoors, pitfall, rope spots, teleports, shovel on stone piles and loose stone piles (the dug hole closes
      after 60 s). No bugs. Always-open holes left alone: Elvenbane 32579,31679,7 (decided), pitfall 32371,32149,7,
      unreachable loose ice 32491,32245,11. Open: Q9 (rope on the spot you stand on).
- [ ] Reduce server memory (~2.5 GB with full map)
- [x] Removed the teleport in Rookgaard temple that sent new players to Thais
      (tools/map-remove-item.py)
- [x] Removed the teleport next to the Thais temple (32366,32235,7) that sent players to the
      Rookgaard temple; a full-map scan found no other mainland teleport into Rookgaard. test_travel.py
- [x] Audit every teleport on the map against 7.4 (two wrong ones so far, both to/from Rookgaard)
      Done 2026-10-04: tools/teleport-audit.py, tests/test_teleports.py. 165 forcefields; none crosses Rookgaard/mainland,
      lands in rock, on a teleport or a hole; 21 lead into closed areas, each checked (pharaoh portals, Paradox switches,
      Senja boat...). Fixed: Morguthis floor-14 forcefield 33238,32644,14 sent players into rock (original map too) - now
      the altar room 33161,32652,14 (tibiaot74 sends it to the level-75 doors instead: a second way in, not taken).
  - [x] Darashia boat landing 33290,32481,7 (all captains + the Ghost Ship forcefield) is a wooden pillar - move it to a
        free deck tile (e.g. 33290,32480,7) and drop test_teleports.py's exception
        Done 2026-10-04: captain.lua HARBOURS Darashia and the Ghost Ship forcefield -> 33290,32480,7; exception dropped
- [x] King's Bridge (Rookgaard, 32057,32192-32193,7): action id 50003 = premium-only ground, nothing
      handled it; movements/scripts/premium_tile.lua sends free accounts back. test_rookgaard.py
- [x] Locked doors without a key (action id 0) opened for anyone (door_locked.lua: "impossible to
      happen") - e.g. 32042,32205,6, the way onto Rookgaard's premium side around King's Bridge. Now
      only house doors open that way (the engine checks house access first). Item 1210 (the unlocked
      closed door) was described as "It is locked." test_rookgaard.py
- [x] House doors: test that owners/invited players can open them and others cannot (Houses task) - Done 2026-10-04: test_houses.py
- [x] Rookgaard sewer bridge levers (action id 50001, 32098/32104,32204,8): ported upstream's
      rat bridge as `rook_rat_bridge.lua`; covered by test_rookgaard.py
- [x] Other map action ids with no script behind them (50001 had none) - list and port them
      Done 2026-09-30: a full-map scan (every action / unique id vs actions.xml, movements.xml, the quest chest
      system, doors and keys, and the numbers the scripts use) left two groups. The portals of citizenship (TibiaWiki
      2005) 1001-1008 in each town (Thais..Ankrahmun = town 2-9) only teleported: movements/scripts/citizenship.lua
      makes you a citizen (town id) and takes you into the temple; their map destinations cleared (map-set-attrs.py
      --teleport now edits a destination beside an action id). test_citizenship.py. Left: aid 50002 on two floor
      tiles of the bridge beside the Rookgaard Academy (32091-32092,32175,6) - no source or script says what it did.

## Monsters

- [x] Loot spike (asked 2026-09-26): is every monster's loot the 7.4 loot - items, counts, chances - and is the gold
      and item value per kill balanced like 7.4? Compare monster/*.xml with a 7.4-era source (TibiaWiki pre-8.0
      creature pages, Tibiantis creature data), list the differences ranked by how much they change the economy.

- [x] Audit the 102 spawned monster types: stats, loot, spells vs 7.4
      Done 2026-10-02 (decided with the user): the 87 spawned monsters Tibiantis has are as Tibiantis has them
      (tools/apply-tibiantis-monsters.py from docs/reference-74/tibiantis/creatures.json): the loot - our most
      spawned monsters dropped several times 7.4's value per kill (rotworm 44 gold vs 8, dwarf guard 193 vs 40
      gold+items, ghoul 48 vs 12, mummy 99 vs 30; the demon less, 592 vs 930) - and hit points (gargoyle 450 ->
      250, elder beholder 1100 -> 500, pig 150 -> 25), experience (lich 1400 -> 900, valkyrie 185 -> 85, swamp
      troll 65 -> 25, slime 260 -> 160...), speed (56; ours = 2 x Tibiantis + 80: mummy 220 -> 150, lich 320 ->
      210), flee point, summon/convince cost. docs/reference-74/monsters.md (tools/compare-monsters.py) compares;
      test_monsters.py pins them. Elder beholder's "beholder helmet" is no 7.4 item - left out.
      Left: the 15 without 7.4 data (tomb bosses, traps) keep theirs; spells/attacks not compared (Tibiantis'
      list has no attack spells) - see 3c below
- [x] Monster attacks and spells vs 7.4 - spike 2026-10-02, docs/reference-74/monster-spells.md
      (tools/compare-monster-spells.py). Sources found: TibiaWiki pre-8.0 creature pages give each attack with its
      damage range (docs/reference-74/monster-abilities.json, tools/wiki-monster-reference.py; 101 of 102 spawned
      monsters, the June 2007 revisions - the earlier ones mostly lack abilities); tibiantis-notes gives haste and
      paralyze spells (strength, duration, chance), melee poison, strategy, target changing
      (docs/reference-74/tibiantis/notes-creatures.json). Not found anywhere: spell chances, intervals and areas.
      Of 102 monsters 72 agree with the wiki; 30 are flagged, e.g. the dragon's fireball 45-65 (7.4 60-110), the
      deathslicer's exori 150-250 (200-400), the elder beholder's energy beam 45-75 (130-300?), the marid's energy
      65-115 (100-250), elf scout/hunter arrows half the 7.4 damage; attacks 7.4 did not list (life drains on the
      djinn and tomb pharaohs, the witch's frog spell missing, the djinn's cancel invisibility missing).
      Fixed 2026-10-02 by hand (the user: "fix all 30"): damage to the wiki's (dragon fireball 60-110 / wave
      100-160, deathslicer 0-500 melee, 200-400 area + an energy beam, marid energy 100-250, warlock, priestess,
      orc warlord, elf arcanist, geomancer, fire devil, banshee life drain + its Great Musical Bomb, elder
      beholder energy beam), attacks 7.4 does not list removed (djinn and marid life drain, marid fire and rabbit,
      efreet drunk/rat, geomancer fire, gargoyle stones, warlock mana drain), melee poison as tibiantis-notes
      (banshee 65, scorpion 350, swamp troll 10, wasp 25, giant spider 150, lich 400); beholders' doubled
      summons. Kept on purpose, with reasons, in the tool's REVIEWED list: the tomb pharaohs (their wiki pages
      are incomplete), the witch's frog and djinn's cancel invisibility (nothing in 7.4 / the engine to do them
      with). test_monsters.py test_monster_attacks_agree_with_74_or_are_reviewed
- [ ] Duplicate quest objects (found 2026-10-03 through the Behemoth lever): the quest audit placed missing objects at
      tibiaot74's spot without looking for the map's own unscripted one nearby - the Behemoth room had the map's
      lever (fixed: it is the quest lever now, ours removed). An audit of everything scripted we added against
      look-alikes (lever/chest/box/body ids) within 6 tiles in the original map (Tibia74.otbm.bak) flags, to look at:
      - Deeper Fibula: the original map has ONE body at 32239,32476,10; we put tibiaot74's two reward bodies at
        32239,32471 (tower shield) and 32478 (warrior helmet) - three bodies now
        Reviewed 2026-10-03, kept (decided with the user): ours are where TibiaWiki puts them - the tower shield "in a
        skeleton under a fire field" (the map had the field, not the body), the helmet "in a skeleton behind a rock"
        (rocks at 32238-32241,32478-32479); the map's own body at 32476 is in the open - decoration
      - Alawar's Vault: chest 32031,31686,8 (key 4503) beside three plain chests of the map
      - boxes among crates (probably storerooms): 32172,31602,10 (key 4501), 32455,32048,8 (uid 10042),
        32507,32270,9 (uid 2170); chest 33078,31656,11 (uid 1019) near the map's chest 33081,31658
      Then: make tools/quest-audit.py report an unscripted look-alike near a "missing" object - done 2026-10-03:
      it lists under each object the map's look-alikes within 6 tiles, same floor ("near:", same id or same kind:
      switch, chest/box/crate/coffin, body/skeleton, key; unscripted = "probably that one", scripted = "probably
      done there"), prints "done" objects that have an unscripted look-alike near (a second one?), also checks
      objects with a uid/aid their actions.xml scripts (the Behemoth lever had no aid 8000), and takes
      --map server\data\world\Tibia74.otbm.bak to compare with the original map
- [ ] Flaky in the full run, pass alone (2026-10-03): test_npc_talk for Hardek (wanders 20 tiles), A Wrinkled
      Beholder, Jimbin - probably a character an earlier test left standing or talking there
- [ ] Flaky quest tests (seen 2026-10-02; Rahemos failed the same way before the monster change, the deathslicer
      in Morguthis's tomb was not changed):
      test_tomb_rahemos (Rahemos heals 200-500 on 20% of his turns and summons a demon; the test's sword + heavy
      magic missiles sometimes do not outpace it in 120 s), test_tomb_morguthis (a deathslicer - unkillable,
      walks, pushable one square, as TibiaWiki 2006 - stands in the corridor at 33263,32679,13 and the router's
      push loses to it). Make the fights/route more robust (stronger runes for the pharaoh, push the deathslicer
      off the path before walking)
- [x] Check spawn times/radius are sane for 7.4
      Done 2026-10-03: docs/reference-74/spawns.md. Our 18,666 monster positions match CipSoft-derived data (Nostalrius
      7.7) almost 1:1, but every spawntime is the map editor's 60 s (7.x: 600 s for most spots, randomised and scaled by
      players online; Black Knight about 12 min per the 2006 wiki). Fixed: the 8 tomb pharaohs 60 -> 600 s, the Black
      Knight 60 -> 720 s. Open: Q8 in the questions at the top (global respawn speed, multi-floor blocking, rare spots, overspawn, timers).
      Done 2026-10-04 (Q8, decided with the user: (c)): tools/apply-cip-spawntimes.py gives each entry its Nostalrius twin's
      time (18,636 twins + 9 decided; 21 without a twin -> 600 s; data in docs/reference-74/nostalrius-spawns.csv).
      spawn.cpp/h + monster.cpp (NEEDS REBUILD): a timer per slot from the monster's death, t/2..t random above 500 s and
      shortened only above 200 players (Nostalrius getInterval), a player in view blocks it (underground +-2 floors, on the
      surface its floor and all above), overspawn beyond 10 squares or a floor change. RateSpawn now divides the delays
      (1 live; the test server uses 20). tests/test_spawns.py (6 data tests pass; 2 live tests wait on the rebuild).
  - [ ] Live tests for overspawn (10 squares / floor change) and the players-online scaling; after the rebuild check the
        hunting and quest tests still behave with RateSpawn 20

## Game rules and formulas

Decide the target for each (real 7.4 or our own choice), write it down here, then add a test.
Current config: RateExp/RateSkill/RateMag/RateLoot/RateSpawn = 1 (real Tibia speed); the
experience stages script (`creaturescripts/scripts/stages.lua`) exists but is not registered.

### Experience and levels
- [x] Experience works (the 2026-09-22 report was a false alarm). Pinned by
      test_rookgaard.py::test_killing_a_rat_gives_experience_and_a_level_up: 99 exp + a rat (5) ->
      level 2, "You advanced from Level 1 to Level 2.", more max hp
- [x] Experience per level: confirm `(50*(L-1)^3 - 150*(L-1)^2 + 400*(L-1)) / 3` (Player::getExpForLevel)
      2026-10-02: the same as Tibiantis' experience table (tibiantis.online ?page=exptable: 8 = 4,200, 50 = 1,847,300)
- [x] Experience rate: keep 1x, pick a multiplier, or enable stages (7.4 had no stages) - Done 2026-10-03: decided with the user - stays 1x, no stages (RateExp 1)
- [x] Monster experience: exp from each monster matches 7.4, including exp split when several players attack
      Done 2026-10-03: all 91 Tibiantis monsters match; fixed Ashmunrah 5000 -> 3100 and Mahrdis 2800 -> 3050 (every
      wiki revision from May-June 2005). Split by damage share, no shared party exp (came in 8.10); trap damage does not
      count; a summon's share is halved for its master; players give no exp (WorldType pvp, 7.4 only on PvP-enforced).
      creature.cpp getGainedExperience: integer maths (lost 1 exp on exact shares) - NEEDS REBUILD.
      tests/test_monster_experience.py (static per monster + solo kills + a two-player split). Open: Q15.
- [x] Level-up gains per vocation: HP / mana / capacity (data/vocations.xml: none 5/5/5, knight 15/5/25...)
      2026-10-02, tibiantis-notes "Classes": knight 15/5/25, paladin 10/15/20, mage 5/30/10 and their base hp/mana
      as ours; capacity is 470 at level 8 for all - Rookgaard (no vocation) gives 10 cap a level, not 5 (fixed).
      test_vocations.py
- [x] Level-down on death: losing enough exp removes levels and their HP/mana/cap
      2026-10-03: test_death.py test_lost_levels_take_their_hp_mana_and_cap_and_respawn_full

### Magic level
- [x] Rookie (no vocation) magic level multiplier is 4.0; 7.4 used 3.0 (TW-Formulae, one source) - Done 2026-10-03: decided with the user - now 3.0 (vocations.xml); test_vocations.py test_rookie_magic_multiplier_is_3
- [x] Mana needed per magic level: `1600 * multiplier^mlvl` with vocation multipliers
      2026-10-03 test_training.py: one cast short of the next level, the next cast levels it - ML 0->1 (1600, 80
      utevo lux), knight ML 5 and 8 (8->9: 10.5 million), paladin ML 15 and 25 (25->26: 7.2 million), sorcerer ML 70
      (1.26 million). The engine works in single precision (7 mana off at 7.2 million)
      (vocations.xml manamultiplier: sorcerer/druid 1.1, paladin 1.4, knight 3.0, none 4.0)
- [x] Mana spent counts toward magic level (spells and runes), RateMag applies (test_training.py: utevo lux)
- [x] Magic level shown correctly in the client (stats packet mlvl + percent)
      2026-10-03: test_training.py reads the magic level from the client's stats packet as it advances

### Skills
- [x] Skill tries per level: `50 * multiplier^(skill-10)`-style formula per skill and vocation (vocations.xml)
      2026-10-03 test_training.py: a knight one try short of sword 100 (241,501 tries) and of 104 (353,582) levels
      on the next hit
      2026-10-02: the multipliers are tibiantis-notes' "Skills" table (test_vocations.py); the formula not checked
- [x] Which actions train which skill: melee hits, shield blocks, distance, fishing; RateSkill applies
      Done 2026-10-03 (TibiaWiki Training revs 28743/158855, Shielding rev 88636, tibiantis-notes training.txt):
      one try per swing/shot while you drew blood within the last 30 tries (attacks made and attacks the shield faces
      share the 30), a bleeding distance shot counts 2, a miss 1; shielding trains on every attack the shield faces
      (2 a turn, blood or not; not PvP ranged, not weapon blocks); fishing: every cast on water with fish, no worms
      (worms came in 7.5, Updates/7.5). RateSkill/RateMag 1. C++ (creature.cpp blockHit, player.cpp/h onBlockHit,
      onAttackMissed, getDefense; weapons.cpp miss branch) - NEEDS REBUILD; 5 tests in test_training.py wait on it.
      Open: Q12 (fished-out water).
- [x] Fist fighting when no weapon; skills start at 10 - Done 2026-10-03: fist atk 7, def 5 with no weapon and no shield (training.txt; def needs the rebuild); new characters have every skill 10, ML 0 - test_training.py

### Combat formulas
- [x] Melee damage: attack, skill, level, fight mode (offensive/balanced/defensive)
      2026-10-03 test_combat_formulas.py test_armor_takes_off_melee_damage, test_a_shield_blocks_melee_as_7_4:
      balanced-stance hits as (5 x skill + 50) x atk x 0.99 / 100 (sword 50 atk 14, sword 80 atk 48); other stances
      not measured
- [x] Defense and armor reduction (the Avesta "revbattlesys" formula - compare with 7.4)
      2026-10-03 test_armor_takes_off_melee_damage (40 armor: ~95% off a 41-max sword) and
      test_a_shield_blocks_melee_as_7_4 (shielding 80 + dragon shield, balanced: ~22 a swing, 7.4 ~22).
      Open: 7.4 blocks in defensive stance with no target; ours keeps the player's stance (default offensive)
- [x] Distance: hit chance, ammo, range
      2026-10-03 test_combat_formulas.py test_crossbow_bolts_hit_as_the_melee_formula_with_the_ammo_attack: bolts
      at 3 tiles 82-93% hit (7.4 90%), a bolt used per shot, damage the melee formula with the bolt's atk 30;
      test_formulas.py: hit chance at 5 tiles. Range (out of range) not tested
- [x] Spell and rune damage formulas (level + magic level) per spell
      Done 2026-10-04: docs/reference-74/spell-formulas.md (every 7.4 attack/healing spell and rune, ours vs 7.4, sources).
      P = max(100, 2 x level + 3 x ML). Fixed: fireball 15-25 %P, GFB 35-65, explosion 20-100, energy/flame strike 35-55,
      energy wave 100-200, ultimate explosion 200-300, heal friend 80-160; poison storm = poison only (150-250 %P total),
      envenom = poison 50-90 %P (was a fixed fire burn 79), soulfire = burn 100-140 %P (was fixed 80). Conjure counts and
      all 32 rune charges already match pre-7.5. tests/test_spell_damage.py (18). global.lua condition params renumbered
      to match enums.h (MINVALUE and later were 2 too low). Open: Q22. (OTHire's "leaked files" formulas used only as
      corroboration - they agree with tibiantis-notes where both exist.)
  - [x] formulas.md §4-5 (spells) and §6.1 (distance) are out of date - point them to spell-formulas.md / refresh - Done 2026-10-04 (checked against the code)
  - [x] Fields: poison field ticks every 5 s here, 4 s in 7.4; medium fire field does 70 here, 60 per TibiaWiki - check and fix - Done 2026-10-04: poison field ticks every 4 s (1490/1496/1503) and lasts 248 s (tibiantis-notes poison.txt); medium fire is 70 in the 7.4-era wiki (60 only in 2007) - kept; fire 20 + 7 x 10 and energy 30 + 25 measured. tests/test_fields.py (3). Open: Q23
- [x] Attack speed (vocations.xml attackspeed 2000 ms) and exhaustion (exhaustion done 2026-09-23, §9)

### Regeneration, food, soul
- [x] HP/mana regeneration per vocation (gainhpticks/gainmanaticks) and food duration
      2026-10-02: per hour as tibiantis-notes (knight 600/900 promoted hp, 300 mana; paladin 450, RP 600; mage
      300 hp, 600/900 mana) - test_vocations.py. Life ring gave 4 mana a tick (1600 instead of 400) and ring of
      healing 4 a second for 480 s (7.5 min, 450 total) - fixed. Food: regeneration = nutrition x 12 s, at most
      1200 s (tibiantis-notes) - not checked yet
- [x] Soul points: did 7.4 have them? (soul came in 7.5 - probably disable)
      2026-10-03: no (TibiaWiki 7.5 update); ours: soul is compiled only under __PROTOCOL_76__, off (formulas.md §7)
- [x] Capacity: item weights and cap limit
      Done 2026-10-03: cap = 470 + (level-8) x gain (knight 25, paladin 20, mage 10), Rookgaard 400 + (level-1) x 10
      (TibiaWiki Formula oldid 128170, tibiantis-notes Classes) - the engine was right; the test helper db.py was not
      (now capacity()). "This object is too heavy." on pick-up; trades "You do not have enough capacity to carry this
      object. It weighs X oz.". 16 weights fixed in items.xml where Tibiantis and every pre-8.0 wiki revision agree
      (tools/compare-item-weights.py: 0 open). tests/test_capacity.py (18). Open: Q13, Q14.
  - [ ] tests/tibia74/db.py creates characters with HP/mana 150 + gain x (level-1), not 7.4 (knight 15L+65...) - many
        combat tests depend on it; fix with care
  - [x] Quest chests say "You have found X, but you cannot carry it." (quests/system.lua); use the Postman chest's - Done 2026-10-04 (see Depots and mailboxes)
        7.4-style "It weighs X oz. It is too heavy." everywhere

### Death and PvP
- [ ] Revisit the death rules (not a bug - make sure every 7.4 rule is applied), research first like
      the formulas (docs/reference-74), then pin each rule with a test:
  - [x] Experience / magic level / skills: 10%, promoted characters 7% (Player::getDeathLossFactor)
        Done 2026-10-03: already 7.4 (Player::getDeathLossPercent: 10%, promoted 7%, -1 per blessing - blessings existed
        in 7.4, TibiaWiki Blessings oldid 6510 of 2005-05). Loss is a share of everything gained (exp, all tries, all mana
        spent), so it can cost a level. test_death.py: ..._10_percent_of_all_skill_tries_7_promoted, ..._of_all_mana_spent_
        7_promoted, test_death_keeps_progress_when_the_loss_is_smaller. Unknown: 7.4 rounding (ours: skills up, exp down).
    - [x] death.md §1/2/7/8 and formulas.md §8 still describe the old getDeathLossFactor and say no blessings - refresh - Done 2026-10-03 (§3-6, 9 still cite some stale line numbers)
  - [x] Levels lost with their HP / mana / capacity
        2026-10-03: test_death.py test_lost_levels_take_their_hp_mana_and_cap_and_respawn_full (level 50 knight
        -> 48: 2 x 15 hp / 5 mana / 25 cap gone, back at full health and mana)
  - [x] Items: which slots can drop and how likely; the backpack/containers; what stays in the corpse
        2026-10-03: test_death.py test_the_backpack_always_drops_other_items_10_percent_each (the backpack and
        its contents always go, at most 5 of the 9 other items)
  - [x] Amulet of loss: keeps all items, is used up; does it also apply to exp/skills? (7.4: items only?)
        2026-10-03: test_death.py test_amulet_of_loss_keeps_every_item_and_is_used_up (backpack and contents
        kept, the amulet gone, 10% experience still lost)
  - [x] Skulls: red skull (and white?) - does the amulet of loss still work, are all items lost?
        2026-10-03: test_death.py test_a_red_skull_drops_everything_amulet_of_loss_or_not (white skull: no
        change, death.md). Found: a red skull with more than ~24.8 days left was lost at login (redskulltime
        read back as int32 milliseconds overflowed, IOPlayer::loadPlayer) - fixed, needs the rebuild
  - [x] Promotion kept or lost on death; premium ending while promoted - Done 2026-10-03: kept on death; suspended (plays as base vocation, loses 10%) while not premium, the DB keeps the promotion - test_a_suspended_promotion_loses_10_percent_and_stays_promoted
  - [x] Where you respawn (home town temple), with what health/mana
        2026-10-03: test_death.py test_respawn_in_the_home_town_temple_with_full_health_and_mana (an Ankrahmun
        character killed in Rookgaard logs in at Ankrahmun's temple)
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
- [x] Respawn at home town temple (town_id), bag/items drop rules
      2026-10-03: test_death.py test_respawn_in_the_home_town_temple_with_full_health_and_mana,
      test_the_backpack_always_drops_other_items_10_percent_each, test_amulet_of_loss_keeps_every_item_and_is_used_up
- [x] Skulls and PZ: PZLock 60 s, KillsToRedSkull 5, KillsToBan 7 - confirm 7.4 values
      Done 2026-10-03: already 7.4 (tibia.com manual 4.3, archived 2005-03-08; TibiaWiki Skull_System oldid 11103):
      PZ/logout block 60 s, 15 min after a kill, white skull while blocked, red skull at 3/5/10 unjustified kills per
      day/week/month for 30 days (resets), ban at 6/10/20 (addUnjustifiedDead - KillsToRedSkull/KillsToBan in config.lua
      are no longer read), kill credit last hit + most damage in 60 s. No protection level in 7.4.
      tests/test_skulls.py (secure mode, PZ block 60 s after an attack / 15 min after a kill). Not 7.4, left out: no
      attacking for 10 s after login (2007 manual). Kept: a defender who fights back is PZ-blocked too (2005 wording).
      Open: Q10 (ban length).
- [x] Rookgaard: no PvP on the island (non-pvp zone or protection level) - Done 2026-10-03: 7.4 manual "free to attack each other once they have left Rookgaard"; ours by vocation 0 (combat.cpp rookgaardForbids) - same in practice; test_rookgaard.py::test_rookgaard_is_non_pvp

### Idle and session
- [x] Idle timeout: warned at 30 s and kicked at 60 s, so the warning read "idle for 0 minutes"
      (whole minutes only) -> config.lua IdleTimeWarning 14 min, IdleTimeKick 15 min, like real Tibia
- [x] Idle message wording: "...idle for 14 minutes. You will be disconnected in 1 minute if you are
      still idle." (was "minutes , you will be"; player.cpp, needs a rebuild)

### Premium
- [x] What premium unlocks in 7.4 (towns, promotion, spells, houses) and how players get it
      Done 2026-10-04: docs/reference-74/premium.md (tibia.com "Features of Premium Accounts", 30 Nov 2004). Already enforced: premium areas (ships, carpets, King's Bridge), Edron/Eremo spells taught only there, promotion, houses, beds, 3 outfits. Fixed: VIP list 20 free / 50 premium (was 51), a free account can no longer open a private channel by packet (player.cpp, chat.cpp - NEEDS REBUILD); Humphrey's blessing is free (blessings were for anyone). tests/test_premium.py (30; 3 wait on the rebuild). Open: Q24.
  - [x] Levitate: spells.cpp getInstantSpell rejects `exani hur up` (the 7.4 words), only `exani hur "up` works - fix (rebuild) - Done 2026-10-04: a spell with a parameter takes the rest of the text, quoted or not (exani hur up, exiva Name, exura sio Name, utevo res rat) - NEEDS REBUILD

### Spells, runes, items
- [x] Verify 7.4 spell list, words, mana, level, vocation, premium (remove post-7.4 spells)
      2026-10-01: as Tibiantis (spells-tibiantis.json, tools/apply-tibiantis-spells.py) - see Spell-teaching NPCs
- [x] Runes: charges, magic level required, soul (7.4 had none)
      2026-10-01: charges and the use magic level as Tibiantis; any vocation uses a rune; no soul (see above)
- [x] Remove leftover warnings: "Unknown command /invisible, /serverdiag", items.otb minor-version warning
      Done 2026-10-03: removed /invisible (never in the engine) and /serverdiag (only built with
      __ENABLE_SERVER_DIAGNOSTIC__) from commands.xml. Left: "[OTBM loader] This map needs an updated items
      OTB file" - harmless, Tibia74.otbm's header says items minor 3 (RME), items.otb is minor 2 (iomapotbm.cpp
      only warns); byte 20 of Tibia74.otbm set from 03 to 02 (the user agreed, 2026-10-03) - the map loads, no
      warning. Saving the map again in RME with a minor-3 items.otb brings it back.

## Branding and client texts

Server-side (config.lua) - editable, current values are Avesta defaults:
- [x] MOTD shown after entering the account (`MOTD`, bump `MOTD_Num` so clients show it again) - Done 2026-10-03: MOTD "Welcome to Mintwall!", MOTD_Num 2
- [x] Pick the one server/world name and use it everywhere (character list shows "<char> (OpenTibia)", - Done 2026-10-03: decided with the user - "Mintwall": WorldName, ServerName, OwnerName (config.lua)
      MOTD, login message, website, patched client): `WorldName`, `ServerName`, `OwnerName` in config.lua
- [x] In-game login message (`LoginMsg`, mentions otserv.org) and `ServerName` / `OwnerName` - Done 2026-10-03: LoginMsg "Welcome to Mintwall.", ServerName "Mintwall"
- [x] First-login "Welcome to <ServerName>. Please choose an outfit." (protocolgame.cpp sendAddCreature) - Done 2026-10-03: uses ServerName - now "Welcome to Mintwall. Please choose an outfit."

Client-side (Tibia.exe) - only by patching strings in the copy we hand out, never longer than the original:
- [ ] Decide if we patch client texts at all (besides the IP patch and loading mintwall.dll)
- [ ] Info button text ("Copyright (C) 2002-2004 CipSoft GmbH" - keep CipSoft's copyright)
- [ ] "Check www.tibia.com" references (login servers offline message, hints) -> our website
- [ ] If yes: extend tools/patch-client.ps1 with a text table, plus a test that the patched exe still has the original size

## Spells and runes (found while making the Centurion test character)

- [x] Levitate (exani hur): premium and level 12 (TibiaWiki 2005 and 2006) - it had neither (2026-10-01: the level
      went with Tibiantis' magic-level-only spells; premium stays). 2026-09-26,
      test_paradox_tower_levitate_is_premium. The other premium spells still carry no prem="1" (see the premium task).

- [x] rope, shovel, pick, keys (key.lua), bread, instruments, decaying items called isIntegerInArray, which did not
      exist - every use failed. Defined in compat.lua. tests/test_spells.py now fails on any call to a function
      nothing defines (tibia74/luascan.py), with the known ones listed below (the list may only shrink)
- [ ] Undefined functions still called (KNOWN_UNDEFINED in tests/test_spells.py):
  - [x] getPlayerPromotionLevel - the NPC promotion module: promotion probably fails (see Promotion NPCs)
        Done 2026-09-30 (compat.lua)
  - [x] broadcastMessage - raid announcements, death/kill broadcast scripts
        Done 2026-10-03: only in unregistered samples (die2.lua, kill.lua, raidevent.lua + testraid.xml) - deleted;
        a raid XML's <announce> covers raids
  - [ ] (Q16) GM ban manager: addAccountBan, addPlayerBan, removeAccountBan, removePlayerBan, getAccountBanList,
        getPlayersByAccountNumber
  - [x] doNpcSellItem, getPlayerPVPBlessing, getPlayerLookDir (NPC system / functions.lua leftovers)
        Done 2026-10-03: trade-window callbacks removed (no trade window in 7.4), the 8.x PvP-blessing branch removed,
        dead modules1.lua deleted, getPlayerLookPos uses getCreatureLookDir; global.lua no longer overrides the engine's
        getPlayerByAccountNumber
  - [x] marriage + banks (not 7.4): remove with the "non-7.4 NPC features" task
        Done 2026-10-01

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
- [x] Royal paladin: bolts / crossbow and arrows / bow distance (range, hit chance - see 5b in the
      formulas list), damage with the 7.4 formula; test with Legolas (6 / 6)
      Done 2026-10-04: bow range 6, crossbow 5, no attack of their own (TibiaWiki 2006-07); ammo arrow 25, bolt 30,
      poison arrow 20, power bolt 40 (was 50); used up per shot, never dropped; hit chance 91% x min(skill/(15d-1),1)
      (tibiantis-notes) - our table within 2%. Burst arrow 0-60% of magic power on the 3x3 (was 55%), no shield block;
      poison arrow now a skill-based arrow hit + 7.4 poison (power 50). tests/test_distance.py (8). formulas.md §6.1
      still describes the old distance code - refresh. Open: Q21.
- [x] Spears: range, breaking/dropping on the ground, stacking, damage vs 7.4
      Done 2026-10-03: 7.4 (TibiaWiki Spear revs 6579/10893, 2005; tibiantis-notes "spears never break"): spears drop
      under/around the target and can be picked up, no breaking (3% came Christmas 2005); stackable (7.4 Tibia.dat flag,
      items.otb agree). Range 6 until 8.1 (revs 131557/151060): items.xml 5 -> 6. A miss lands on any tile of the 3x3
      around the target, centre included (TN distance_calculator): weapons.cpp - NEEDS REBUILD. tests/test_spears.py
      (stack, land/no break, range 6 vs 7). Open: Q11.

- [x] Spell values the research lists as higher than 7.4 but did not rank: fireball (16-33 vs 15-25 %P),
      great fireball (40+30..70 vs 35-65), force strike (20-50 vs 18..33, one source), exura sio
      (100+30..135 vs 80-160, one source). docs/reference-74/formulas.md §5
      Done 2026-10-04 with the spell formulas (spell-formulas.md)
- [x] Life ring / ring of healing regeneration not checked against 7.4 (1 per 3 s for 20 min / 1 per 1 s
      for 7.5 min) - 2026-10-02: they gave 4 mana a tick; fixed, test_vocations.py test_regeneration_ring

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
- [x] A step queued before a teleport runs after it (found by the user 2026-10-04, Demon Helmet: the teleport
      33286,31589,12 lands west of the portal 33278,31592,11, a queued east step walks into it -> back in the room).
      Creature::onCreatureMove stops the auto-walk on teleport but not Player::nextStepEvent.
      Done 2026-10-04 (NEEDS REBUILD): a teleport drops the queued step, and a step that arrives within the landing's
      step time after a teleport-on-step is dropped with a walk cancel (game.cpp playerMove, player.cpp/h); stairs,
      ramps and holes unchanged. test_walking.py::test_step_sent_with_the_one_onto_a_teleport_does_not_run_after_landing
- [x] Magic wall / wild growth on a map field (1487/1488/1491, replaceable=0) does nothing (found by the user
      2026-10-04). 7.4 (tibiantis-notes poison.txt): "Magic Wall or wild growth will not remove fields" - the wall
      goes on top, the field stays; a fire bomb must not remove a wall
      Done 2026-10-04 (NEEDS REBUILD): tile.cpp - a wall goes on top of any field, no damage field under a wall, the
      field flag stays when the wall goes (getFieldItem prefers the damage field); destroy field reaches the fire only
      after the wall decays. tests/test_magic_wall.py (4)
- [ ] A step pressed while another is queued replaces it (Player::setNextWalkTask) - dropped steps when
      tapping back and forth (seen in the stairs trace); queue one step instead?
- [ ] Re-trace with the real client on the new server (walk-trace summary: steps more than 50 ms late)

## Travel and combat feel

- [x] Boats premium only (2026-09-26): TibiaWiki 2006 "Captain Bluebear will transport any premium players by ship",
      "Only characters on a Premium Account can go to Edron / Darashia, using the boat or the magic carpet". Premium on
      for every destination of the captains (barco_*.lua), the Edron and Cormaya boats, Eremo and the carpets (Chemar,
      Pino, Uzon); the "bring me to" shortcuts skipped the check - a guard now refuses free accounts ("I'm sorry, but
      you need a premium account in order to travel onboard our ships."). The ice-island boats (Nielson and the
      islands' ferrymen) stay free: no source calls them premium. test_travel.py test_ships_take_premium_players_only.
      Open: the captains' fares are the 8.x ones of the scripts - check them against 7.4.

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
  - [x] 3c. 30 monsters have no 7.4 data in the source (bosses, traps, assassin, bandit, dark monk, - decided 2026-10-04: keep their values
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
  - [x] Tests for step 3 (melee, distance, stances, shield block): measure damage and blocks in game
        against the 7.4 formulas - the formulas are built but not pinned by any test yet
        2026-10-03 (asked by the user): test_combat_formulas.py reads every hit from the damage numbers over the
        target (Thais street, no monsters near): HMM at magic power 100 hits 13-19 (7.4: 10-20 halved PvP) and at
        380 38-75 (38-76); SD at power 410 284-304 (271-348), with a stone skin amulet 55-64 (1/5); a sword hitting
        for at most 41 took 152-185 hp in 40 s off a bare target, 2-12 off one in 40 armor (7.4 armor formula
        predicts ~198 and ~10). 2026-10-03, 3 runs: the same sword (40 s) took 190-241 off a bare target and 8-25
        off the armored one (7.4 ~197 / ~10); crossbow + bolts at distance 60, 3 tiles, 60 s: 28-30 shots (bolts
        used), 82-93% hit (76 of 88, 7.4: 90%), hits 3-51 mean 25-28 (7.4 max 51 halved, mean ~26); magic sword,
        sword 80, 60 s, 28-30 swings: bare mean 53-59 a hit (7.4 ~53), a balanced knight with shielding 80 and a
        dragon shield 19-23 a swing, 7-10 swings blocked to 0 (7.4 block max 139: ~22, a quarter blocked) - the
        shield takes ~60% off. Found: the engine starts every player in offensive stance (Player fightMode =
        FIGHTMODE_ATTACK, block x0.6: an unset target took 696 instead of ~440 in 20 swings); 7.4 blocks in
        defensive stance when the player has no target - not done (test sets the target balanced)
- [x] 7.4 formulas research (docs/reference-74/formulas.md): Berserk = level x 4 mana
      is the real 7.4 cost (TibiaWiki: until the 2007 summer update); monster healing rates; mana
      fluid 25-75 in 7.4 (ours 40-80); magic formula base x (mlv*3 + lv*2)/100 (tibiantis-notes).
      No hydras exist on our server (post-7.4 creature?)
- [x] Travel questions for the 7.4 reference: Edron premium-only? which captains went where, prices
      Done 2026-09-30: docs/reference-74/travel.md
- [x] Oracle: premium players are now offered Darashia/Ankrahmun/Edron too (the script's intent; it
      never worked before) - overlaps with the Gatekeeper, check against 7.4
      Done 2026-10-01: the Oracle offers Carlin, Thais and Venore to everyone; the premium towns are the
      Gatekeeper's

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
- [x] Test every NPC answers "hi" (generated test per NPC)
      Done 2026-09-30: tests/test_npc_talk.py (see "Talk-test every NPC once")

## Pre-launch

- [ ] Before launch: remove the quest-testing account 8 (password "8") and its characters from the production
      database, and never deploy server/config.local.lua (their InfiniteItemPlayers names; .gitignore keeps it out of
      git - the server reads it after config.lua when it is there; tools/provision-quest-testers.py, local only)

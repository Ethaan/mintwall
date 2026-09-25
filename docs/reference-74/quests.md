# 7.4 quests: list, rules, and what our map already has

One row per quest in the master table below (research, 2026-09-23). Each quest is tracked in task.md
(section "Quests") and gets an end-to-end test: a strong character starts in a temple, does the quest the way
a player would, and checks the reward and the once-per-player rule.

## What our map (Tibia74.otbm) already contains

How the map encodes quests (the usual OT "quest system" convention):
- **Quest chest:** action id 2000; unique id = the player storage that marks it as looted. When the unique id
  is an item id (< 10000) that item is the reward, otherwise the chest's contents are. **No script handles
  action id 2000 today** (data/actions/scripts/quest_reward.lua is an unregistered example), so none of these
  chests give anything yet. One generic script would switch all of them on.
- **Level doors** ("gate of expertise"): action id 1001-1999, level = action id - 1000 (gateofexp_closed.lua, works).
- **Quest doors:** action id = the storage that must be 1 (questdoor_closed.lua, works).
- **Keys:** action id = the door they open (copper keys 4501-4503, wooden key 3700).

Found on the map (tools: the OTBM scan in tests/tibia74/otbm.py):

| Where | What | Quest |
|---|---|---|
| 32099,32198,9 | box uid 2384 (rapier) | Rapier Quest |
| 32124-32130,32064-32066,12 | boxes uid 2395 (carlin sword), 2580 (fishing rod), 52159 | Minotaur Hell Quest |
| 32092,32162,8 | chest uid 2050 (torch) | Torch Quest |
| 32102,32235,8 | chest uid 2404 (combat knife) | Combat Knife Quest |
| 32141-32149,32096-32105,11 | chests uid 2464 (chain armor), 2460 (brass helmet), 52148, 52149; door 4601 | Bear Room Quest |
| 32150,32111,12 | chest uid 20003 | Present Box Quest (probably) |
| 31973-31977,32209,12 / 32039,32121,13 | chests uid 52169, 52170, 52171 | Rookgaard (Captain Iglues / Goblin Temple?) - to check |
| 32171,32197,7 | chest uid 20001 with a book | Amber's Notebook Quest |
| 32174-32176,32132-32149,9-11 | dead humans uid 2412 (katana), 2473 (viking helmet), 20002; doors 4600, 4603 | Katana Quest |
| 32179,32224,9 | dead dragon uid 54322 | Dragon Corpse Quest |
| 32172,32169,7 | palm uid 2676 (banana) | Banana Quest |
| 32005,32139,3 | honey flower uid 2103 | Honey Flower Quest |
| 32225-32226,32265,10 | chests uid 2417 (battle hammer), 2521 (dark shield), with the items inside | Thais Lighthouse Quest |
| 33313,31591-31593,15 | chests uid 2493 (demon helmet), 2520 (demon shield), 2645 (steel boots); switch 50666 at 33330,31591,15 | Demon Helmet Quest |
| 32031,31686,8 / 32172,31602,10 / 32201,31571,10 | copper keys 4503, 4501, 4502 | Alawar's Vault Quest |
| 32818,32230,9 | wooden key 3700 | Plains of Havoc (Ornamented Shield uses key 3702 - check) |
| 32178,31928,6 | quest door 3350 | Ghostlands / White Raven (check) |
| 32 gates of expertise | levels 20, 25, 30, 32, 35, 40, 45, 50, 60, 70, 80, 100 | e.g. level 100 at 33211,31638,13 and 33214,31671,13 (Annihilator area), 80 at 33297,31670,14 (before the Demon Helmet chests) |

Everything else (Banshee, Behemoth, Annihilator's reward room, Black Knight, Vampire Shield, Desert Quest, most
mainland quests) has **no reward placed** on our map: the route and doors may exist, the chests / rewards / NPC
steps have to be added per quest from the research below.


## How this was built and which sources were reachable

| Source | Reachable? | What it gave |
|---|---|---|
| https://tibiantis.info/library/quests | yes (the quest table is embedded in the page JS) | 100 quests with level, premium, location and rewards. Each row links to TibiaWiki spoilers. Only the Aruthang Quest (a Tibiantis custom quest, excluded here) has its own page. |
| https://tibiantis.life/ (Tibiantis completionist tracker) | yes (JSON embedded in the page) | Same list, plus descriptions, creatures, requirements and chest/trade type. Adds Rookgaard items missing from tibiantis.info: Amber's Notebook, Antidote Rune, Banana, Honey Flower, Legion Helmet, Present Box, Small Axe, Torch. Has **no entry** for Black Knight, Ancient Tombs, Serpentine Tower or White Pearl. |
| https://tibiantis-notes.github.io/ | yes, but it has no quest or location pages (only skills, calculators and creatures) | nothing for quests |
| https://tibiantis.online | yes (forum). Only a group-quest scheduling thread (?id=82): Banshee lvl 60+, Behemoth lvl 60+, Orc Fortress | Confirms Tibiantis runs Banshee and Behemoth at level 60 |
| tibia.fandom.com (TibiaWiki) HTML | **403 (Cloudflare)** | |
| tibia.fandom.com **api.php** | **yes**. Used for all TibiaWiki data, including page history | Current pages, the first (mostly 2005) revision and the last revision before 2007 (the "pre8" 7.x snapshot) for about 110 quest pages and their /Spoiler pages. Also the `Quests/Version` table and the `Updates/*` dates. |
| TibiaWiki `Quests` page, revision 13618 of **2005-08-06** (3 days before 7.5) | yes | **The best contemporary 7.4 quest list**: https://tibia.fandom.com/index.php?oldid=13618 (see below) |
| tibia-wiki.net (Polish mirror) | 404 for the spoiler URLs | |
| tibiawiki.com.br | 403 | |
| OTLand "Quest System for 7.4 Realots" https://otland.net/threads/quest-system-for-7-4-realots.254941/ | yes | A Lua table of every 7.4/7.72 real-map quest chest, with its **uniqueid** and the items inside. The author says it covers "100% 7.4 and 7.72 chestboxes" except some Tiquanda/Jakundaf. Useful for checking the chest contents on your map. |
| OTLand "all 7.6 quests" thread https://otland.net/threads/hello-im-looking-for-a-place-to-find-all-7-6-quests-listed.237169/ | yes | Only advice: use TibiaWiki revisions from 2005 to 2006 (which is what this document does) |
| OTLand "7.4 quests list" thread | 404 | |

Key version dates (TibiaWiki `Updates/*`): 7.1 = 2003, 7.2 = 16 Dec 2003, **7.24 = 15 Mar 2004** (Annihilator, Postman, White Raven, Mad Mage Room, Skull of Ratha, Voodoo Doll, Giant Smithhammer), 7.3 = 11 Aug 2004 (Medusa Shield, Serpentine Tower), **7.4 = 14 Dec 2004** (Ankrahmun, Djinn War, Ancient Tombs), **7.5 = 9 Aug 2005** (Port Hope, Sam's Old Backpack, Elephant Tusk: NOT 7.4), 7.9 = 2006 (Pits of Inferno: NOT 7.4), 8.0 = Jan 2007.

### Important caveats
1. **Tibiantis is built on the leaked CipSoft 7.7 map**; its map page is "7.7 Cipsoft/Tibiantis". It removes post-7.4 areas: its quest list has no Port Hope and no Pits of Inferno. It also adds custom content (Aruthang, custom creatures). A quest that appears on Tibiantis is strong evidence that it existed in 7.4. **Tibiantis's reward column is mixed.** For some quests it shows its own real-server rewards, which differ from TibiaWiki: Behemoth, Vampire Shield, Fire Axe, Medusa Shield, Outlaw Camp, Orc Fortress, Banshee, Deeper Fibula. For others it copies modern TibiaWiki text (for example "Health Potion", "Mana Potion", "Annihilation Bear"). Potions, wands of the 7.8+ type, achievements, outfits/addons and the "Golden Bag" are all post-7.4. Where the two sources conflict, the table shows both. The chest contents on your own 7.4 map are the final authority, and the OTLand uniqueid table helps check them.
2. **Coordinates** come from TibiaWiki `{{Mapper Coords|A.B|C.D|z}}`, converted as x = A*256+B and y = C*256+D. They are real-map positions of an entrance, NPC or chest on the *current* map. Old areas should match the 7.4 map, but none has been checked against a 7.4 map.
3. **"Once per player"**: the 7.x wiki rarely says so explicitly. On CipSoft servers quest chests and corpses were one-per-character quest containers. Rows marked "assumed" follow that convention.
4. "Min level 2" on Rookgaard is a listed or recommended value. No source shows a level door on Rookgaard.

### The contemporary 7.4 list (TibiaWiki `Quests`, 2005-08-06, oldid 13618), with the old names mapped to today's names
- Rookgaard free: Amber's Lost Notebook, Bear Room, Captain Iglues Treasure, Combat Knife, Dragon Corpse, Katana, Minotaur Hell (a.k.a. Carlin Sword Quest), Present Box, Small Axe, Studded Shield, Torch. Rookgaard premium: Goblin Temple, Honey Flower, The Pan Quest (= Antidote Rune Quest), Small Axe.
- Mainland free: Alawars Vault, Banshee, Battle Axe, Black Knight, Blood Herb, Bright Sword (= Outlaw Camp), Crusader Helmet, Dark Helmet (redirects to Alawar's Vault), Dead Archer, Deeper Fibula, Desert Dungeon (a.k.a. Vocation Quest / 10k Quest), Devil Helmet, Double SD (= Crystal Wand), Dracona (= Draconia), Dragon Tower, DTD Quest (= Noble Armor), Dwarf Hell (= Circle Room), Elvenbane, Emperors Cookies, Family Brooch (= White Raven Monastery), Fanfare, Geomancer, Ghoul Room, Giant Smithing Hammer, Griffin Shield, Iron Hammer, Iron Helmet, Life Ring, Light House (= Thais Lighthouse), Longsword, Mad Mage Room, Mintwalin Cyclops, Naginata, Old Mintwalin (= Kingdom of Kormarak), Orc Fort, Orc Shaman, Ornamented Shield, Panpipe, Power Bolts, Power Ring, Scale Armor, Silver Brooch, Skull of Ratha, Spikesword, Time Ring, Triangle Tower, Voodoo Doll.
- Mainland premium: Annihilator, Barbarian Axe, Behemoth, Berserker Treasure, Blue Djinn, Dark Armor, Demon Quest (= Demon Helmet), Double Hero, Edron Goblin, Fire Axe, Green Djinn, Helmet of the Ancients (= Ancient Tombs), Medusa Shield, Paradox Quest, Parchment Room, Plate Armor, Poison Daggers, Postman, Shaman Treasure, Stealth Ring, Triple UH Rune, Troll Cave, Vampire Shield. (The page ends "more coming soon".)
- On Tibiantis but **not** on that 2005 list (so their 7.4 status rests on Tibiantis or weaker evidence): Doublet, Rapier, Pick and Short Sword trades, Silver Amulet, Six Rubies, Small Ruby, Throwing Star, Isle of the Mists, Heaven Blossom, Purple Tome, Demona Ring, Ring Quest, Wedding Ring, Serpentine Tower / White Pearl.

### Requested items with no separate quest
- **Dragon Scale Mail quest**: no source (2005 list, Tibiantis, TibiaWiki, OTLand chest table) has a DSM quest. Dragon-lair quests are Fire Axe (Edron Dragon Lair), Ornamented Shield (Plains of Havoc Dragon Lair) and Naginata (Thais Dragon Lair).
- **Crown Armor / Hero Cave**: crown armor comes from the **Black Knight Quest** (Crown Armor + Crown Shield). The Hero Cave hosts Annihilator, Demon Helmet, Vampire Shield, Parchment Room, Ring, Wedding Ring, Double Hero and Triple UH (see the Hero Cave note in the Edron section).
- **Wolf Tooth Chain**: part of the **Skull of Ratha Quest** (Amazon Camp, Venore).
- **Stealth Ring**: Stealth Ring Quest (Minotaur Pyramid, Darashia). Also found in Parchment Room, Banshee and Demona Ring.
- **Minotaur**: Minotaur Hell (Rookgaard), Iron Hammer, Steel Helmet / Minotaur Tower (Kazordoon), Stealth Ring (Minotaur Pyramid). Minotaur Leather Quest is probably post-7.4.
- **Pits of Inferno** (7.9) and **Sam's Old Backpack** (7.5) are **not 7.4**.
- **Postman**: 7.24, so it is 7.4. The 2005 wiki describes only 3 ranks, so the full 10-mission chain may have been extended later.

## Master table

| Quest | Location | Min level | Players | Vocation | Premium | Rewards | Once | In 7.4? | Confidence |
|---|---|---|---|---|---|---|---|---|---|
| Bear Room Quest | Rookgaard, orc/minotaur cave north of town | none known (listed as 2) | 1 | any | no | Chain Armor, Brass Helmet, 12 Arrows, 40 gp (3 boxes); Key 4601 chest | yes | yes (wiki 5.2; Tibiantis) | high |
| Present Box Quest + Legion Helmet Quest | chest by stone switch on Bear Room level; NPC Seymour (Academy) | none known (listed as 2) | 1 | any | no | Backpack with Present Box, Jug, Plate, Cup; Present Box traded for Legion Helmet | yes | yes (wiki 5.2; Tibiantis) | high |
| Captain Iglues Treasure Quest | Rookgaard, under the poison spider tower (N) | none known (listed as 2) | 1 | any | no | 2 Salmon (+ Letter per 2005-06 wiki) | yes (quest chest) | yes (Tibiantis; wiki 2005) | medium |
| Combat Knife Quest | Rookgaard town sewer | none | 1 | any | no | Combat Knife | yes | yes (wiki 5.2) | high |
| Doublet Quest | cellar under stable north of Tom's shop | none | 1 | any | no | Doublet (loose board) | yes | yes (Tibiantis; wiki 2005) | medium |
| Dragon Corpse Quest | bear cave east of town | none known (listed as 2) | 1 | any | no | Bag with Copper Shield + Legion Helmet | yes | yes (wiki 5.2) | high |
| Goblin Temple Quest | premium side: troll cave to goblin temple | none known | 1 | any | yes | 50 gp, 4 Snowballs, 5 Small Stones, Sandals, Pan, Milk | yes | yes (Tibiantis; wiki 2005) | medium |
| Antidote Rune Quest (modern: Small Health Potion Quest) | NPC Billy, premium side | none | 1 | any | yes | Pan traded for Antidote Rune | yes (tied to once-only Pan) | yes (Antidote Rune version; potion version is 8.20) | medium |
| Katana Quest | graves then rotworm/skeleton cave | none known (listed as 2) | 1 | any | no | Katana, Viking Helmet (in corpses); Key 4603 | yes | yes (wiki 5.2) | high |
| Minotaur Hell Quest | main cave north of town, bottom floor | none known (listed as 2) | 1 (group advised) | any | no | Carlin Sword, 4 Poison Arrows, 10 Arrows, Fishing Rod | yes | yes (wiki 5.2) | high |
| Small Axe Quest + Pick Quest | skeleton cave (premium) or respawn spots; Al Dee | none (Pick listed as 2) | 1 | any | Small Axe chest: yes (premium); trade: no | Small Axe traded for Pick (Al Dee) | Small Axe coffin once (Tibiantis quest id); other spots respawn | yes (Tibiantis; wiki 2006) | medium |
| Rapier Quest | town sewer, west, one floor down | none | 1 | any | no | Rapier | yes | yes (wiki 5.2) | high |
| Amber's Notebook Quest + Short Sword Quest | chest on east dock; Amber (Academy) | none (trade listed as 2) | 1 | any | no | Notebook traded for Short Sword | chest yes; any such book can be traded | yes (wiki 5.2) | high |
| Honey Flower Quest + Studded Legs Quest | wasp tower NW; Lee'Delle (premium side) | none (trade listed as 2) | 1 | any | trade: yes; flower: no | Honey Flower traded for Studded Legs | flower chest once (Tibiantis id); any Honey Flower tradable | yes (wiki "7.11 (2)") | high |
| Banana Quest + Studded Shield Quest | banana palm NE (free) or premium wolf hill; Willie | none (trade listed as 2) | 1 | any | no | Banana traded for Studded Shield | yes, both palms share one quest id (Tibiantis.life) | yes (wiki 6.0) | high |
| Torch Quest | Rookgaard Academy basement | none | 1 | any | no | Torch | yes | probably (on Tibiantis.life; not on tibiantis.info list; wiki: no version, removed 9.2) | medium |
| Battle Axe Quest | Thais sewers (SW) | 0 | 1 | any | no | Battle Axe | unknown (current wiki: quest Pile of Bones) | yes | medium |
| Dead Archer Quest | Thais Troll Cave (E of Thais) | 0 | 1 | any | no | Bow, 5 Poison Arrows, Mana Fluid, Life Fluid (7.x) | unknown | yes | medium |
| Deeper Fibula Quest | Fibula dungeon | 50 (door) | 1 | any | no | Knight Axe, Warrior Helmet, Elven Amulet, Tower Shield, Dwarven Ring (in corpses; wiki). Tibiantis lists different items | unknown | yes (wiki: 5.0) | medium (reward conflict) |
| Devil Helmet Quest | Thais Ancient Temple to Mintwallin | 30 (door) | 2+ (one player holds a floor tile to open the grate) | any | no | Devil Helmet, Halberd, 4 Small Sapphires | unknown | yes (wiki: 5.01) | high |
| Geomancer Quest | Mount Sternum undead cave (N of Thais) | 0 | 1 | any | no | Small Sapphire, Small Diamond, Dwarven Ring | unknown | yes | medium |
| Ghoul Room Quest | Thais Ancient Temple | 0 | 1 | any | no | Garlic Necklace, Club Ring | unknown | yes (wiki: 5.01) | high |
| Kingdom of Kormarak Quest (Old Mintwallin) | Thais Ancient Temple | 0 | 1 | any | no | Brass Armor, Brass Helmet, Hatchet, 13 Throwing Stars (wiki from 2011 on) | no (daily respawn corpse) | likely | medium-low |
| Life Ring Quest | Thais Ancient Temple (S branch) | 0 | 1 | any | no | Life Ring, Dragon Necklace | unknown | yes | medium |
| Mad Mage Room Quest | Thais Ancient Temple, toward Mintwallin | 40 (door) | 1 | any | no | Hat of the Mad, Stone Skin Amulet, Star Amulet (quest boxes) + daily chest | quest boxes yes; one chest is daily | yes (wiki: 7.24) | high |
| Mintwallin Cyclops Quest | Thais Ancient Temple, cyclops room | 0 | 1 | any | no | Small Diamond (7.x); current wiki adds more items | unknown | yes | medium |
| Naginata Quest | Thais Dragon Lair (N of Alatar Lake) | 40 (door) | 1 | any | no | Naginata | unknown | yes | medium |
| Noble Armor Quest (Skjaar/DTD) | below Mount Sternum | 35 (door) | 1 | any | no | Noble Armor, Crown Helmet (wiki); Tibiantis: Noble Armor | unknown | yes | medium |
| Scale Armor Quest | cave W of Ancient Temple entrance | 0 | 1 | any | no | Scale Armor (+ Piece of Iron, Book per pre8) | unknown | yes | medium |
| Silver Amulet Quest | Thais Troll Cave cellar | 0 | 1 | any | no | Silver Amulet | unknown | yes (wiki: 5.2) | medium |
| Six Rubies Quest (Double Dragon) | Thais Ancient Temple | 0 | 1 | any | no | 6 Small Rubies | unknown | likely | medium |
| Small Ruby Quest | Mintwallin throne room pit | 0 | 1 | any | no | 1 Small Ruby | no (daily respawn) | likely | low |
| Spike Sword Quest (Fire Devil) | cave E of Mount Sternum / NE of Triangle Tower | 0 | 1 | any | no | Spike Sword | unknown | yes | medium |
| Thais Lighthouse Quest (Dark Shield) | Thais lighthouse, SW of Thais | 0 | 2 (step switch + lever) | any | no | Dark Shield, Battle Hammer | unknown | yes (wiki: 3.0) | high |
| Throwing Star Quest | Thais Ancient Temple, underground park | 0 | 1 | any | no | 10 Throwing Stars | unknown | yes | medium |
| Triangle Tower Quest | Triangle Tower (E of Thais, desert edge) | 0 | 1 | any | no | Garlic Necklace, Dwarven Ring, 2 Small Sapphires | unknown | yes | medium |
| Giant Smithhammer Quest | Plains of Havoc cyclops/minotaur camp | 0 | 1 | any | no | Talon, Giant Smithhammer, 100 gp | unknown | yes (wiki: 7.24) | high |
| Ornamented Shield Quest | Plains of Havoc Dragon Lair | 0 | 1 (part 1); 2 (part 2) | any | no | Brown bag: Key 3702, Might Ring, Dragon Necklace, Spike Sword, book, Ornamented Shield, Steel Helmet (+ Red Bag part 2, current wiki only) | unknown | yes (wiki: 5.1) | medium (part 2 unconfirmed for 7.4) |
| Alawar's Vault Quest | Senja / Folda (ice islands N of Carlin) | 0 | 1 | any | no | 3 White Pearls, Broadsword (short path); + Dark Helmet, 4 Throwing Knives, Blank Rune, 33gp, Keys 4501/4502/4503 (long path) | yes (chests) | yes (6.5) | high |
| Crystal Wand Quest (Double SD Quest) | Demona, via Maze of Lost Souls (N of Carlin) | 60 (door) | 1 | any | no | Crystal Wand, 2-charge Sudden Death rune, Twinkiller Rune (Book) | yes | likely (no dated version; in Tibiantis) | medium |
| Demona Ring Quest | Demona | 60 (Demona gate) | 1 | any | no | Energy Ring, Stealth Ring (2 chests; unclear whether both can be taken) | yes | uncertain (no wiki page before 2016; in Tibiantis) | low-medium |
| Fanfare Quest | Carlin graveyard crypt | 0 | 1 | any | no | Fanfare | yes | likely (in Tibiantis; wiki 2005 page) | medium-high |
| Griffin Shield Quest (MoLS Quest) | Gates of Demona, Maze of Lost Souls | 30 (not a door, see notes) | 1 | any | no | Griffin Shield, Dwarven Axe, Obsidian Lance (in corpses) | yes | likely (in Tibiantis; wiki 2006) | medium |
| Power Ring Quest (Bronze Amulet / Femor Hills Goblin) | Femor Hills goblin cave | 0 | 1 | any | no | Power Ring, Bronze Amulet | yes | likely (in Tibiantis) | medium-high |
| Purple Tome Quest (Map Quest) | Demona library | 60 (Demona gate) | 1 | any | no | Tibia Map (Book), Fields of Glory Map (Book), Purple Tome (bookcases) | unknown | uncertain (no wiki page before 2020; in Tibiantis) | low-medium |
| The Queen of the Banshees Quest (Banshee Quest) | Under Ghostlands and Isle of the Kings | 60 (Queen refuses <60) | 1+ (easier with a team; seal 3 spawns 2 warlocks per member) | any | no | Boots of Haste, Giant Sword, Tower Shield, Stealth Ring, Stone Skin Amulet, 10k gp (all). Tibiantis lists Boots of Haste, Amulet of Loss, Stealth Ring, Stone Skin Amulet | yes | yes (7.2) | high (rewards conflict) |
| The White Raven Monastery Quest (Family Brooch Quest / Island of Kings Quest) | Ghostlands W of Carlin, Isle of the Kings | 0 | 1 | any | no | Family Brooch (gives Dalbrect passage), Blessed Ankh (from Costello for the Monk's Diary) | yes | yes (7.24 = Mar 2004) | high (brooch), medium (diary/ankh part) |
| Draconia Quest | Draconia, via Hellgate under Ab'Dendriel | 25 (door) | 2 minimum (floor switches) | any | no | Ice Rapier, Serpent Sword, Stone Skin Amulet, Energy Ring | yes | yes (6.2) | high |
| Elvenbane Quest (Elf Castle Quest) | Elvenbane castle, SW of Ab'Dendriel | 0 | 1 | any | no | Morning Star, Dwarven Shield, Mana Fluid (7.x; now Strong Mana Potion), Blank Rune, Spellbook, 2 Small Diamonds, 100gp | yes | likely (in Tibiantis) | medium-high |
| Orc Fortress Quest | Orc Fortress, W of Ab'Dendriel | 40 (door) | 1 | any | no | Wiki: Knight Armor, Knight Axe, Fire Sword. Tibiantis: 10k, Stone Skin Amulet, 8 Small Emeralds | yes | yes (6.1) | medium (rewards conflict) |
| Circle Room Quest (Dwarven Quest / Dwarf Hell Quest) | Dwarf mines W of Kazordoon | 32 (door) | 1 | any | no | Dwarven Axe, War Hammer | yes | likely (in Tibiantis) | high |
| Crusader Helmet Quest | Deep Dwarf Mines W of Kazordoon | 35 (door) | 1 | any | no | Wiki: Crusader Helmet. Tibiantis: "Dwarfen Helmet" | yes | likely (in Tibiantis; wiki 2005) | medium (reward conflict) |
| Emperor's Cookies Quest | Emperor Kruzak's chambers, Kazordoon | 0 | 1 | any | no | Key 3800, bag with 20+7 cookies and Key 3801, Key 3802 | keys (see notes) | yes (6.1) | high |
| Explorer Brooch Quest | Jolly Axeman tavern sewer, Kazordoon | 0 | 1 | any | no | Explorer Brooch | yes (corpse) | yes (6.1) | high |
| Iron Hammer Quest | Minotaur cave W of Kazordoon | 0 | 1 | any | no | Iron Hammer | yes | yes (6.61-6.97) | high |
| Longsword Quest | Troll cave E of Dwarf Bridge | 0 | 1 | any | no | Longsword, Mirror, 3 Blank Runes, Wooden Doll, Wedding Ring, 76gp | yes | likely (in Tibiantis) | medium-high |
| Steel Helmet Quest (Minotaur Tower Quest) | Minotaur tower W of Kazordoon | 0 | 1 | any | no | Steel Helmet, 47gp, 56gp, The Fox Is Out (Book) (7.x page: "Scroll") | yes | yes (6.61-6.97) | high |
| The Paradox Tower Quest | Paradox Tower, near Kazordoon (+ PoH, Edron, Carlin, Thais, Mintwallin, Hellgate) | 30 | 1 | any | yes | 2 of 4: 10k gp, Wooden Wand (2005 wiki and Tibiantis; later Wand of Cosmic Energy), 32 Talons, Phoenix Egg | yes | yes (6.61-6.97) | high |
| Black Knight Quest (Crown Set) | Villa Scapula swamp, north of Venore (~32827,31959,7) | 50 (door) | 1+ | any | no | Crown Armor, Crown Shield (2 dead trees; you take both) | trees are quest containers; once per player assumed, source does not say | yes (7.1) | high for the route. Conflict: TI lists level 0 and reward "nothing" |
| Blood Herb Quest (Witchesbroom) | Greenclaw Swamp, west of Venore | 0 | 1 | any | no | Blood Herb (Wyda will trade it for Witchesbroom) | yes (quest tree) | yes (6.1) | high |
| The Desert Dungeon Quest (Desert / Vocation / 10k Quest) | Below Jakundaf Desert (entrance ~32649,32093,7) | 20 (door) | 4, one of each vocation | Knight + Paladin + Druid + Sorcerer | no | chest 1: 100 platinum coins; chest 2: green bag with Protection Amulet, Ring of Healing, Magic Light Wand, Ankh (both chests) | rewards once; the quest can be repeated to help others | yes (6.1) | high |
| Dragon Tower Quest | Shadowthorn, south-east of Venore | 0 | 1 | any | no | 7.x: 2 Small Sapphires, 30 Burst Arrows, 60 Poison Arrows, Bow (TW-old: 100 gp instead of Bow). The potions on TW-cur are post-7.4 | assumed | yes (7.1) | medium on the reward list |
| Heaven Blossom Quest | Shadowthorn underground | 0 | 1 | any | no | Heaven Blossom (barrel) | unknown | uncertain. No wiki page before 2014, but TI/TL list it | low |
| Iron Helmet Quest (Muriel's Letter) | Plains of Havoc, west of the cyclops/orc/minotaur camp (~32787,32232,7) | 0 | 1 | any | no | Iron Helmet, Sudden Death rune, plus loose Leather Armor / Letter / Worn Leather Boots (TW-cur adds a book and a Longsword) | assumed (body is a quest container) | yes (on TW-old 2005) | medium |
| Isle of the Mists Quest (Druid Quest) | Isle of the Mists; teleport in PoH (~32831,32295,7) | 0 | 1 | druid, per the quest legend (the wiki does not confirm a vocation check) | no | 7.x: 3 Small Emeralds + book; TW-cur: 2 Small Emeralds + book | assumed | likely (wiki from 2006 on; TI lists it) | medium |
| Orc Shaman Quest | Swamp/orc cave east of Venore (~33055,32030,7) | 0 | 1 | any | no | Magic Light Wand, Axe Ring, Blank Rune | assumed | yes (TW-old Aug 2005) | high |
| The Outlaw Camp Quest (Bright Sword Quest) | Outlaw Camp, west of Thais/Venore road (~32615,32253,7) | 45 (door) | 1 (2 recommended) | any | no | Bright Sword, Red Gem | yes | yes (6.4) | high for the route. TI reward conflict: "8k, 50 Power Bolts, Red Gem" |
| Panpipe Quest (Fire Devil Quest) | Desert Dungeon, Jakundaf Desert | 0 | 1 | any | no | Panpipes, 2 Small Amethysts, Power Ring (in a bag) | assumed | yes (6.1) | high |
| Power Bolts Quest | Hole south of the PoH temple (~32815,32280,7) | 0 | 1 | any | no | 5 Power Bolts, 12 Burst Arrows, Two Handed Sword, book (TW-cur also lists respawning Throwing Stars and a Talon) | assumed (corpses) | yes (wiki 2006; TI) | medium |
| Silver Brooch Quest (Mummy Quest) | Greenclaw Swamp caves (~32700,31992,7) | 0 | 1 | any | no | Silver Brooch, 2 Small Rubies, 3 Small Diamonds (coffin) | assumed | yes (wiki 2006; TI) | high |
| Skull of Ratha Quest (incl. Wolf Tooth Chain and Crystal Necklace) | Amazon Camp, north of Venore (~32846,31920,7) | 0 | 1 | any | no | box 1: White Pearl + Skull of Ratha; box 2: Wolf Tooth Chain + Dwarven Ring; basement chest: 100 gp, Crystal Necklace, 2 Black Pearls | assumed | yes (7.24) | high |
| Time Ring Quest (Shadowthorn Quest) | Shadowthorn underground (~33060,32182,7) | 0 | 1 | any | no | Time Ring, Elven Amulet, Crystal Ball (3 boxes; you take all) | assumed | yes (7.1) | high |
| Voodoo Doll Quest | Greenclaw Swamp, north side (~32737,31953,7) | 0 | 1 | any | no | Voodoo Doll, Magic Light Wand (2 boxes) | assumed | yes (7.24) | high |
| Medusa Shield Quest (Star Room / Necromancer Quest) | Drefia, west of Darashia (~32996,32413,7) | 60 (door) | 1+ (team advised) | any | yes | Medusa Shield, Skull Staff, Blue Robe (one coffin) | assumed | yes (7.3) | high for the route. TI reward conflict: "5k, Blue Spell Wand, 2x BP UH, 2x BP HMM, BP Explosion" |
| Plate Armor Quest (Ghost Ship) | Ghost Ship, random on the Venore to Darashia boat | 0 | 1 | any | yes | Plate Armor (coffin) | assumed | yes (6.61-6.97) | high |
| Stealth Ring Quest (Minotaur Pyramid) | Minotaur (Dark) Pyramid, north-east of Darashia (~33312,32282,7) | 0 | 1 | any | yes | Stealth Ring (SE coffin), Protection Amulet (NE coffin) | assumed | yes (6.61-6.97) | high |
| The Ancient Tombs Quest (Helmet of the Ancients) | 8 Ankrahmun tombs | 75 (doors) | team advised | any | yes | 7 helmet pieces, combined into Helmet of the Ancients (ruby socket) | each piece once per character | yes (7.4) | medium. TI reward "to be discovered"; TL has no entry |
| The Djinn War - Efreet Faction (Green Djinn Quest) | Mal'ouquah + Ankrahmun, Carlin, Thais, Ulderek's Rock, Ashta'daramai | 30 (fortress door) / 40 (Orc King door) | 1 | any | yes | 600 gp, trade rights with the Efreet (TW-cur adds a Gemmed Lamp) | yes; locks out the Marid side | yes (7.4) | high |
| The Djinn War - Marid Faction (Blue Djinn Quest) | Ashta'daramai + Kazordoon, Mal'ouquah, Ulderek's Rock | 30 / 40 | 1 | any | yes | 3 Small Sapphires, trade rights with the Marid (TW-cur adds a Gemmed Lamp) | yes; locks out the Efreet side | yes (7.4) | high |
| Serpentine Tower Quest / White Pearl Quest (one quest) | Serpentine Tower (Sorcerer guild), Ankrahmun (~33147,32866,7) | 0 | 1 | any | yes | White Pearl. The Fire Elemental / Green Djinn cage "continuation" gives no known reward | assumed | yes (7.3; on wiki since Feb 2006) | medium. TI lists both names separately |
| Annihilator Quest | Edron, Hero Cave (deepest floors) | 100 (lever/tiles; level-100 door at quest entrance per current wiki) | exactly 4 | any | yes | choose ONE: Demon Armor / Magic Sword / Stonecutter Axe / Present Box with teddy ("Annihilation") bear | yes (reward room door enterable once) | yes (7.24, Mar 2004) | high |
| Behemoth Quest | Edron, Cyclopolis (deep) | 60 in 2004 (level door; raised to 80 in late 2004/early 2005); Tibiantis: 60 | 1+ (team advised) | any | yes | wiki: Demon Shield, Golden Armor, Guardian Halberd, Platinum Amulet, Life Ring, Crystal Ring, 3 Small Diamonds, 4 Small Sapphires. Tibiantis: 30k, Life Ring, 5 Small Diamonds, 5 Small Sapphires, 5 Small Rubies, 100 Power Bolts | yes (quest chests) | yes (7.2, flagged "confirmation needed") | medium (level and rewards conflict) |
| Vampire Shield Quest | Edron, Hero Cave (Warlock room / Temple of Xayepocax) | 70 (level door) | 1+ | any | yes | wiki: Vampire Shield, Dragon Lance (behind lvl-70 door) + box outside the door: Strange Symbol, Black Pearl, Mysterious Fetish. Tibiantis: Ice Rapier, 2x BP SD | yes (chests) | yes (6.4) | medium (rewards conflict) |
| Demon Helmet Quest | Edron, Hero Cave → Demon Hell | 100 (level door) | team (4 demons + banshees in room, 5 demons on the way) | any | yes | Demon Helmet, Demon Shield, Steel Boots (all three, separate boxes). Tibiantis: "to be discovered" | yes (chests) | yes (6.4) | medium-high (Key 6010 need is only confirmed by the current wiki) |
| Parchment Room Quest | Edron, Hero Cave | none | 1+ (5 demons) | any | yes | Brown bag: Key 6010 (golden "Demon key"), Bone, Stealth Ring, 2 Talons, Skull | yes (coffin) | yes (7.2) | high |
| Ring Quest | Edron, Hero Cave | none | 1+ | any | yes | Time Ring, Sword Ring | yes (chests) | yes (7.1 per wiki; listed on Tibiantis) | medium (not documented on the wiki before 2008) |
| Wedding Ring Quest (Hero Cave) | Edron, Hero Cave | none | 1+ | any | yes | Wedding Ring, Dragon Necklace | yes (chests) | likely (6.4 per wiki; listed on Tibiantis) | medium-low (page only exists from 2010) |
| Double Hero Quest | Edron, Hero Cave | none | 1+ | any | yes | Club Ring, Red Gem (two chests, both taken) | yes | yes (6.4) | high |
| Triple UH Rune Quest (now "Adorned UH Rune Quest") | Edron, Hero Cave | none | 1+ | any | yes | 7.x: UH rune with 3 charges (+5 Mana Fluids per the 2006 infobox). Current: Silver Rune Emblem (UH) | yes | yes (6.4) | medium (5 mana fluids only in the 2006 infobox) |
| Barbarian Axe Quest | Edron Orc Cave (bottom) | none | 1+ | any | yes | Barbarian Axe, Scimitar | yes | yes (6.4) | high |
| Berserker Treasure Quest | Edron Orc Cave | none | 1+ | any | yes | 3 White Pearls + gold (181 gp per 2006 wiki; 175 gp per current wiki and Tibiantis) | yes | yes (6.4) | high |
| Dark Armor Quest | Edron Orc Cave (giant spider pit) | none | 1+ | any | yes | Dark Armor (in a dead body) | yes | yes (6.4) | high |
| Poison Daggers Quest | Edron Orc Cave (shaman level) | none | 1+ | any | yes | 2 Poison Daggers, 30 Poison Arrows (in a backpack) | yes | yes (6.4) | high |
| Shaman Treasure Quest | Edron Orc Cave (room with a Sacrificial Stone) | none | 1+ | any | yes | 3 Blank Runes (in a skeleton) | yes | yes (6.4) | high |
| Edron Goblin Quest | Edron Goblin Cave, west of town | none | 1 | any | yes | Steel Shield, Silver Amulet | yes | yes (6.4) | high |
| Troll Cave Quest | Edron Troll Cave, west of town | none | 1 | any | yes | Brass Legs, Garlic Necklace | yes | yes (6.4) | high |
| Fire Axe Quest | Edron Dragon Lair | 60 (level door) | 1+ | any | yes | wiki: Ring of Healing, Dragon Necklace, 7 Small Diamonds (boxes) + Fire Axe (use skeleton in a hole you open with a pick). Tibiantis: Red Spellwand, Life Ring, BP GFB, BP UH, Paralyze Rune, 2x Soulfire, 4x Fire Bomb, 2x Energy Bomb | yes | yes (6.4) | medium (rewards conflict) |
| Postman Missions Quest | starts at Kevin (post office between Thais and Kazordoon), spans the whole map | none | 1 | any | yes | discounts on parcels/letters/boats, Post Officer's Hat, Post Horn, use of locked mailboxes | yes (NPC-state progression) | yes (7.24) | high |
| Pits of Inferno Quest | under Plains of Havoc | 80 | — | — | yes | — | — | NO (7.9, 2006) | high |
| Sam's Old Backpack Quest | Ulderek's Rock / Dwarf Mines | 35 | — | — | no | Dwarven Armor | — | NO (7.5, Aug 2005) | high |
| Elephant Tusk Quest | east of Port Hope | none | — | — | yes | 2 Elephant Tusks | — | NO (7.5) | high |
| Magic Sword Quest (Sword of Valor, Mintwallin) | Mintwallin | — | — | — | no | Magic Sword, Yellow Spell Wand, 2x Demon Armor, 2x Demon Legs | repeatable | NO (removed before 7.4; deprecated) | medium |
| Iron Ore Quest | Dwarf Mines near Kazordoon | none | — | — | no | Iron Ore | — | uncertain / probably not (no version on the wiki, not on Tibiantis) | low |
| Minotaur Leather Quest | raft south of Thais | none | — | — | no | Minotaur Leather | — | uncertain / probably not (no version on the wiki, not on Tibiantis) | low |

## Rookgaard

### Bear Room Quest
- **Status on our server (2026-09-23): works, tested end to end** (tests/test_quests.py::test_bear_room_quest).
  Map: boxes uid 2464 (chain armor), 2460 (brass helmet), 52148 (12 arrows + 40 gp - reward table), key chest 20003
  (copper key 4601 - reward table) at 32150,32111,12 below the mud (aid 100) at 32149,32110,11; stone switch aid
  52413 at 32148,32105,11 toggles the stone 1304 at 32145,32101,11; door 1212 aid 4601 at 32145,32100,11.
  Quirk: a loot chest (scrolls, bucket, blue bottle) lies on the switch tile, on top of the switch - the server
  uses the top item, so the chest must be moved away before the switch can be used.
- Alt names: Chain Armor Quest.
- Location: Rookgaard, abandoned building a little north of town, down through troll/orc cave floors. Coordinates: unknown (no Mapper Coords on the page).
- Version: implemented 5.2 per TibiaWiki; in 7.4: yes. On Tibiantis (level 2, free).
- Requirements: no level door known. "Level 2" on the 2006 wiki and Tibiantis is a listed/recommended value. Free account; 1 player. Items: Rope; Key 4601 or a Pick.
- Steps:
  1. Go to the abandoned building north of Rookgaard and go down the hole.
  2. Go east and down (trolls).
  3. Go down again (a few orcs), then down again (2-4 orcs; 2005 text says minotaurs).
  4. Final level: 1-2 minotaurs and orcs. If you have no Key 4601, use a Pick on the mud floor square directly south of the big table and go down. The chest there holds Key 4601. Climb back up.
  5. Use the switch north of the big table to remove the stone blocking the bear-room door. Open the door with Key 4601 and kill the Bear.
  6. Open all three boxes. You can leave through the sewer grate (spider room) back to the minotaur room.
- Rewards: Chain Armor, Brass Helmet, 12 Arrows, 40 gp. You take all three boxes; there is no choice. Tibiantis.life also counts Key 4601 as a reward. The pre-2007 wiki, the current wiki and Tibiantis agree.
- Once per player: yes (quest boxes). The Present Box chest is next to the stone switch.
- Sources: https://tibia.fandom.com/wiki/Bear_Room_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=64348 ; infobox https://tibia.fandom.com/index.php?oldid=30071 ; https://tibiantis.info/library/quests ; https://tibiantis.life/
- Confidence: high.

### Present Box Quest / Legion Helmet Quest
- **Status on our server (2026-09-23): works, tested end to end** (tests/test_quests.py::test_present_box_quest).
  Chest uid 52149 at 32149,32105,11 (reward table: backpack with present 1990, jug, plate, cup); Seymour (32103,32195,7)
  trades the present for a legion helmet (hi, box, yes) and mentions the box from level 6.
- Alt names: Present Quest, Legion Helmet Quest. Tibiantis.life has two entries: Present Box Quest (chest) and Legion Helmet Quest (trade).
- Location: chest next to the stone switch on the last Bear Room level. NPC Seymour (Academy) is at about (32102, 32196, 7).
- Version: 5.2; in 7.4: yes.
- Requirements: listed level 2. The 7.x legend says Seymour mentions the box only at level 6 or higher; whether the trade itself needs level 6 is unknown. Free; 1 player.
- Steps:
  1. Follow the Bear Room route to the final level and open the chest near the switch.
  2. Talk to Seymour: hi, box (or "present box"), yes.
- Rewards: backpack with Present Box, Jug, Plate, Cup. The Present Box is traded for a Legion Helmet.
- Once: yes.
- Sources: https://tibia.fandom.com/wiki/Present_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=30884 and https://tibia.fandom.com/index.php?oldid=51824 ; https://tibiantis.life/
- Confidence: high.

### Captain Iglues Treasure Quest
- **Status on our server (2026-09-23): works, tested end to end.** Quest chest uid 52171 at 32039,32121,13 = 2 salmon
  (reward table); the chest beside it (32038) is the daily one (stamped letter "Treasure of captain Iglue" + 12 salmon).
- Alt names: Orc Language Quest, Salmon Quest.
- Location: under the poison spider tower in northern Rookgaard. Entrance at about (32058, 32091, 7).
- Version: the wiki gives no version; the page dates from Aug 2005. On Tibiantis (level 2, free). In 7.4: yes.
- Requirements: no level door known; free; 1 player. Items: Rope. Food is recommended, and an antidote rune is optional (Tibiantis.life).
- Steps:
  1. Enter the poison spider tower and go down one level.
  2. Go south(-east) and down the first hole.
  3. Follow the path north-west and go down (many poison spiders, 2 poison fields).
  4. Go down another level. Follow the passage west and south, then go down (no creatures).
  5. In the stone-walled area with Skeletons, go down the stairs to two chests guarded by 2 Skeletons.
  6. Optional: bring the Salmon to Amber (Rookgaard Academy) for information about the orc language.
- Rewards: Tibiantis.life gives 2 Salmon. The 2005-06 wiki gives a Letter and two Salmon. The current wiki puts 2 Salmon in the right (quest) chest and 12 Salmon plus a Stamped Letter in the left chest as a daily respawn. The tibiantis.info list says "Treasure of Captain Iglue (Book) and some Salmon". There is no choice.
- Once: yes for the quest chest; the other chest respawns.
- Sources: https://tibia.fandom.com/wiki/Captain_Iglues_Treasure_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=42633 ; https://tibiantis.info/library/quests ; https://tibiantis.life/
- Confidence: medium (which item sits in which chest in 7.4 is unclear).

### Combat Knife Quest
- Location: Rookgaard main sewer (enter by the drain in town). Entrance at about (32117, 32221, 7).
- Version: 5.2; in 7.4: yes.
- Requirements: none; free; 1 player.
- Steps:
  1. Use the drain to enter the sewer.
  2. Follow the path. The 2005 text says east then south; the current text says north, then west twice. 3-4 rats guard the box.
  3. The box is partly hidden behind debris; use it.
- Rewards: Combat Knife.
- Once: yes.
- Sources: https://tibia.fandom.com/wiki/Combat_Knife_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=23964 ; https://tibiantis.life/
- Confidence: high (the directions differ between revisions, so check the map).

### Doublet Quest
- Location: cellar of the stable north of Tom's shop. Ladder at about (32081, 32183, 7).
- Version: the wiki gives no version; the page dates from Sep 2005. On Tibiantis. In 7.4: yes.
- Requirements: none; free; 1 player; a torch or other light helps.
- Steps:
  1. Tom mentions an adventurer who left a doublet before leaving for the mainland. The legend says he kept his loot under a loose board next to a strange note on the wall.
  2. Go down the ladder in the stable and kill the rat.
  3. Use the ground (Loose Board) directly west of the sewer grate.
- Rewards: Doublet.
- Once: yes (it is a Tibiantis.life "chest" quest).
- Sources: https://tibia.fandom.com/wiki/Doublet_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=58445 and https://tibia.fandom.com/index.php?oldid=61509 ; https://tibiantis.life/
- Confidence: medium.

### Dragon Corpse Quest
- Alt names: Copper Shield Quest, Dead Dragon Quest.
- Location: bear cave east of town. Entrance at about (32146, 32208, 7).
- Version: 5.2; in 7.4: yes.
- Requirements: no level door known; free; 1 player. Items: Rope, Shovel, Scythe, life fluids and food; 102 oz of free capacity.
- Steps:
  1. Go down the hole into the bear cave (many bears) and take the southern branch.
  2. At the end (pool of water), use the Shovel on the hole and go down.
  3. Use the Scythe on the wheat.
  4. Run across 4 large fire fields and 1 medium fire field to the Dragon corpse. The 2005 text says "like 10 fire fields".
  5. Open the dead dragon to get a bag with a Copper Shield and a Legion Helmet, then run back.
- Rewards: bag with Copper Shield and Legion Helmet. All sources agree.
- Once: yes.
- Sources: https://tibia.fandom.com/wiki/Dragon_Corpse_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=63733 ; https://tibiantis.life/
- Confidence: high.

### Goblin Temple Quest
- Alt names: Rookgaard Goblin Quest, Temple of Cheese Quest.
- Location: Rookgaard premium area, through the premium troll cave (pile of rocks). Entrance at about (32001, 32213, 7).
- Version: the wiki gives no version; the page dates from Sep 2005. On Tibiantis (premium). In 7.4: yes.
- Requirements: premium; no level door known; 1 player. Items: Shovel, Rope.
- Steps:
  1. Shovel the pile of rocks and go down (troll). Go down the hole near the north-east corner (trolls), follow the passage and go down, then go down again (orcs, trolls). Follow the passage south; the side rooms hold monsters up to minotaurs.
  2. Cross the bridge (goblins throw stones) and go down. Go through the round room, east at the crossroads, past the sign praising Cheese the god, and down.
  3. Run through the goblin room and go up the stairs (3 goblins, 1 minotaur, 1 orc spearman, 1 wasp). Open the chests.
- Rewards: 50 gp, 4 Snowballs, 5 Small Stones, Sandals, Pan, Milk. All versions agree. The Pan goes to Billy (Antidote Rune Quest). Small Axes from goblins can be traded to Al Dee for a Pick.
- Once: yes.
- Sources: https://tibia.fandom.com/wiki/Goblin_Temple_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=57028 ; https://tibiantis.life/
- Confidence: medium (the route text is vague, so use the map).

### Antidote Rune Quest
- Alt names: Pan Quest. The current wiki calls it "Small Health Potion Quest".
- Location: NPC Billy, Rookgaard premium side, at about (32051, 32205, 7).
- Version: in 7.x Billy gives an Antidote Rune. The Small Health Potion version came with 8.20 (Winter Update 2007). Tibiantis.life has it as "Antidote Rune Quest" (trade, premium). In 7.4: yes, as the Antidote Rune version.
- Requirements: premium; the Pan from the Goblin Temple Quest.
- Steps:
  1. Do the Goblin Temple Quest to get the Pan.
  2. Give the Pan to Billy. The exact keywords are unknown.
- Rewards: Antidote Rune in 7.4 (Small Health Potion in modern Tibia).
- Once: effectively yes, because the Pan is a once-only reward.
- Sources: https://tibia.fandom.com/wiki/Small_Health_Potion_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=21044 and https://tibia.fandom.com/index.php?oldid=53359 ; https://tibiantis.life/
- Confidence: medium.

### Katana Quest
- Alt names: Katana Room Quest, Viking Helmet Quest.
- Location: graves in Rookgaard, with a rotworm dungeon under them. The 2006 text places the graves north-west of the free area; the current text says north-east of the island. The grave is at about (32151, 32151, 7).
- Version: 5.2; in 7.4: yes.
- Requirements: no level door known; free; 1 player. Items: Rope, Shovel; Key 4603 (can be found inside); antidote runes or life fluids recommended.
- Steps:
  1. Shovel the middle grave and go down (spiders, poison spiders). Go to the hole and jump in.
  2. In the skeleton area, kill the skeletons (use the narrow passage to the south). Go east to a rope spot, rope up into the rotworm room, run to the other hole and go down.
  3. Pass the 4 poison fields.
  4. If you have no Key 4603, face north: the key is in one of the bodies (you may need to uncover it).
  5. East of the poison fields, go down the hole (1 skeleton). Open the door with Key 4603 and go downstairs.
  6. Use the hidden lever behind the northern white pillar to unlock the door. The room may hold 2 skeletons and a rotworm. Enter and close the door.
  7. Loot the fresh human corpses for the Katana and the Viking Helmet. A teleport lets you out if you get locked in.
- Rewards: Katana, Viking Helmet. Tibiantis also lists Key 4603.
- Once: yes.
- Sources: https://tibia.fandom.com/wiki/Katana_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=48802 and https://tibia.fandom.com/index.php?oldid=53356 ; https://tibiantis.life/
- Confidence: high.

### Minotaur Hell Quest
- Alt names: Carlin Sword Quest.
- Location: Rookgaard main cave north of town (reached from the level 2 bridge). Entrance at about (32095, 32138, 7).
- Version: 5.2; in 7.4: yes.
- Requirements: no level door known; free; 1 player, though a group is advised. Items: life fluids; boxes are useful.
- Steps:
  1. Floor -1: a rat, trolls, spiders. Go east to the ladder down.
  2. Floor -2: orcs. Go north, then north-east, then north-west to the ladder down into the Wolf Maze (-3).
  3. Go north through the wolves and orcs to the ladder into Minotaur Hell (about 2 minotaurs, 8 orcs, wolves).
  4. Take the stairs down to the final room (about 5 minotaurs, 3 wolves). The three quest boxes are just west of the stairs on the south wall.
- Rewards: Carlin Sword, 4 Poison Arrows, 10 Arrows, Fishing Rod. All sources agree.
- Once: yes.
- Sources: https://tibia.fandom.com/wiki/Minotaur_Hell_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=66981 ; https://tibiantis.life/
- Confidence: high.

### Small Axe Quest / Pick Quest
- Alt names: Pick Quest, Small Axe Quest. Tibiantis.life has two entries: Small Axe Quest (chest, premium) and Pick Quest (trade).
- Location: several spots in Rookgaard. Al Dee's shop is at about (32063, 32182, 7).
- Version: the wiki gives no version; the page dates from 2006. On Tibiantis. In 7.4: yes.
- Requirements: none. The skeleton-cave coffin (Small Axe chest) and goblin drops are on the premium side; the Katana cave and orc cave spots are free.
- Steps:
  1. Get a Small Axe from one of these places:
     - the skeleton cave in the far south-west premium area (Shovel; right-hand coffin);
     - goblin drops (premium);
     - a dead body in the Katana Quest cave, north of the rope spot before the poison fields (respawns at server save);
     - a box in the orc cave on floor -2 of the main cave (respawns at server save).
  2. Give the axe to Al Dee and ask for a Pick.
- Rewards: Small Axe, traded for a Pick. The Pick is needed for the Bear Room Quest.
- Once: the Small Axe quest chest is once only (Tibiantis quest id). The other spots respawn, and the Al Dee trade is repeatable (unknown whether it has a limit).
- Sources: https://tibia.fandom.com/wiki/Pick_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=39940 ; https://tibiantis.life/
- Confidence: medium (Al Dee's keywords are unknown).

### Rapier Quest
- Location: Rookgaard main rat sewer. Entrance at about (32094, 32204, 7).
- Version: 5.2; in 7.4: yes.
- Requirements: none; free; 1 player.
- Steps:
  1. Enter the sewer, go west and down the hole or ladder (3-7 rats).
  2. The quest box is in the north-east part of the room.
- Rewards: Rapier.
- Once: yes.
- Sources: https://tibia.fandom.com/wiki/Rapier_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=24209 ; https://tibiantis.life/
- Confidence: high.

### Amber's Notebook Quest / Short Sword Quest
- Alt names: Amber's Lost Notebook Quest. Tibiantis.life has two entries: Amber's Notebook Quest (chest) and Short Sword Quest (trade).
- Location: dock east of town at about (32172, 32197, 7). Amber is in the Academy resting room at about (32103, 32183, 8).
- Version: 5.2; in 7.4: yes.
- Requirements: none; free; 1 player.
- Steps:
  1. Use the chest on the east dock (wolves, bugs, spiders, poison spiders nearby) to get a black book (Amber's notebook).
  2. Talk to Amber: hi, book, yes. She gives a Short Sword.
- Rewards: Notebook, traded for a Short Sword.
- Once: the chest is once only. Amber accepts any such notebook.
- Sources: https://tibia.fandom.com/wiki/Short_Sword_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=29268 ; https://tibiantis.life/
- Confidence: high.

### Honey Flower Quest / Studded Legs Quest
- Alt names: Wasp Quest. Tibiantis.life has two entries: Honey Flower Quest (chest, free) and Studded Legs Quest (trade, premium).
- Location: wasp tower in north-west Rookgaard at about (31999, 32140, 7). Lee'Delle's shop is on the premium side at about (32024, 32196, 7).
- Version: "7.11 (2)"; in 7.4: yes.
- Requirements: Rope. Premium is needed to reach Lee'Delle. Life fluids and an antidote rune are recommended.
- Steps:
  1. Rope up the wasp tower.
  2. Use the flower on the right to get a Honey Flower.
  3. Talk to Lee'Delle: hi, honey flower. She gives Studded Legs.
- Rewards: Honey Flower, traded for Studded Legs.
- Once: the flower spot is once only (Tibiantis quest id). Lee'Delle accepts any Honey Flower.
- Sources: https://tibia.fandom.com/wiki/Studded_Legs_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=24204 ; https://tibiantis.life/
- Confidence: high.

### Banana Quest / Studded Shield Quest
- Tibiantis.life has two entries: Banana Quest (chest) and Studded Shield Quest (trade).
- Location: banana palm in north-east Rookgaard at about (32172, 32169, 7). A second palm stands on the premium wolf hill: the hill is at about (31988, 32199, 7), the palm on its plateau at (31983, 32193, 5), reached from the flat part (floor 6) by stacking 3 boxes and stepping up (our map; uid 52414 shares storage 2676). Willie is in town at about (32067, 32205, 7).
- Version: 6.0; in 7.4: yes.
- Requirements: none; free; 1 player.
- Steps:
  1. Use the banana palm to get a Banana.
  2. Talk to Willie: hi, banana, yes. He gives a Studded Shield.
- Rewards: Banana, traded for a Studded Shield.
- Once: yes. Tibiantis.life notes that both palms share one quest id, so a player gets only one banana.
- Sources: https://tibia.fandom.com/wiki/Studded_Shield_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=30400 ; https://tibiantis.life/
- Confidence: high.

### Torch Quest
- Location: Rookgaard Academy basement. Coordinates unknown.
- Version: the wiki gives no version; the page dates from Sep 2005, and the quest was removed in the Summer Update 2011 (9.2). It is on Tibiantis.life but not on the tibiantis.info list. In 7.4: probably yes.
- Requirements: none; free.
- Steps:
  1. The 2005 text: go to the Academy basement and head north, opening doors; the box at the end holds a torch.
  2. The current wiki adds: a lever opens a wall halfway, then there are two more doors and a rat, then the chest (5 oz).
- Rewards: Torch.
- Once: yes.
- Sources: https://tibia.fandom.com/wiki/Torch_Quest/Spoiler ; pre8 https://tibia.fandom.com/index.php?oldid=20870 ; https://tibiantis.life/
- Confidence: medium.

### Other Rookgaard chests
- The respawning Small Axe spots (orc cave box, Katana cave body) and Captain Iglue's second chest (a daily respawn, per the current wiki) are not quests. No other Rookgaard quest pages turned up in the fetched set or on the Tibiantis lists.

## Thais, Fibula, Mintwallin, Plains of Havoc

### Battle Axe Quest
- **Other names:** Cave Rat Quest.
- **Location:** Thais sewers, south-west end. Pick spot around x 32302, y 32257, z 8.
- **Added / in 7.4:** The wiki gives no "implemented" version. The TibiaWiki page existed in July 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, any vocation, free account. Bring a Rope and a Pick.
- **Steps:**
  1. Enter the sewers next to the Thais depot. You will meet Rats.
  2. Go south and west to the SW dead end.
  3. Use the Pick on the tile 2 sqm north of the dead end, on the east side (current wiki). Go down the hole.
  4. Kill the Cave Rats (4, per current wiki). Open the skeleton (current wiki: "Pile of Bones (Quest)") to get the Battle Axe.
- **Rewards:** Battle Axe. It is not a choice. The pre8 wiki, current wiki and Tibiantis agree.
- **Once / rules:** unknown for 7.4. The current wiki calls the container a quest container, which suggests once per character.
- **Sources:** https://tibia.fandom.com/index.php?oldid=70616 (pre8 spoiler) ; https://tibia.fandom.com/index.php?oldid=29946 ; https://tibia.fandom.com/wiki/Battle_Axe_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Our server (2026-09-24):** pick spot 32302,32257,8 (rope spot below), 4 cave rats, dead skeleton 3103 at 32305,32254,9 (added; tibiaot74's position) aid 2000 uid 1658 = battle axe, once per character.
- **Confidence:** medium.

### Dead Archer Quest
- **Other names:** Thais Slimes Quest. The pre8 spoiler is titled "Dead Demon Quest".
- **Location:** Thais Troll Cave, east of Thais. The hole entrance is around x 32491, y 32260, z 7.
- **Added / in 7.4:** version unknown. The page existed in June 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. Bring a Shovel and a Rope. Antidote or Destroy Field is recommended for the poison fields.
- **Steps:**
  1. Shovel open the troll cave hole and go down.
  2. Go east and down a hole.
  3. Go east and down again. Expect Orcs and Orc Warriors, and possibly lured Scorpions.
  4. Go south through the poison fields on both sides of the Slime spawn.
  5. Use the body at the north end of the room.
- **Rewards:**
  - 7.x (pre8): Bow, 5 Poison Arrows, Mana Fluid, Life Fluid.
  - Current wiki: Mana Potion and Health Potion instead of the fluids. This is a post-7.4 change.
  - Tibiantis: fluids, which matches 7.x.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=73645 ; https://tibia.fandom.com/index.php?oldid=29954 ; https://tibia.fandom.com/wiki/Dead_Archer_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Our server (2026-09-24):** shovel hole 32493,32259,7; dead human 3129 at 32513,32302,10 (added; tibiaot74's position) aid 2000 uid 1662 = bow, 5 poison arrows, mana fluid, life fluid (real-map table), once per character.
- **Confidence:** medium.

### Deeper Fibula Quest
- **Other names:** none known.
- **Location:** Fibula (island south of Thais), in the dungeon entered through the well. No coordinates given.
- **Added / in 7.4:** the wiki says 5.0. Yes.
- **Requirements:**
  - Level 50 gate of expertise.
  - 1 player, free account.
  - Key 3940 (bought on Fibula) for the locked dungeon door.
  - Key 3980, found during the quest.
  - Destroy Field runes.
- **Steps:**
  1. Go down the Fibula well and follow the dungeon, using Key 3940 on the locked door.
  2. Go east through a teleporter.
  3. Of the two teleporters, take the right one, behind the level 50 gate.
  4. You reach a minotaur room (current wiki: 2 Minotaur Guards and 4 Minotaur Archers).
  5. Go west through fire and energy fields, past the Minotaur Mages. "Use" a hole to the west to get **Key 3980**.
  6. Go back and south, and unlock the door with Key 3980. More minotaurs follow.
  7. Next is the dragon cave. The current wiki counts about 16 Dragons and 4 Dragon Lords.
  8. Loot the corpses at the end of the cave:
     - Tower Shield: NW corner, in a skeleton under a fire field.
     - Warrior Helmet: south of that, in a skeleton behind a rock.
     - Dwarven Ring: north of the exit portal, in a skeleton.
     - Elven Amulet: directly east of that, in a fresh dragon corpse.
     - Knight Axe: south-east of that, in a dead human.
  9. The SW portal returns you to the entrance.
- **Rewards:**
  - pre8 and current wiki: Knight Axe, Warrior Helmet, Elven Amulet, Tower Shield, Dwarven Ring. All are taken, from separate corpses.
  - **Conflict:** Tibiantis lists "Elven Amulet, Dwarven Ring, Serpent Sword, 6 Small Diamonds, Time Ring" with level 0. This may reflect Tibiantis's own map data.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=55209 ; https://tibia.fandom.com/index.php?oldid=29955 ; https://tibia.fandom.com/wiki/Deeper_Fibula_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Our server (2026-09-24):** well 32172,32439,7 (aid 54545) down; door 32190,32432,8 = key 3940 (Dermot, 2000 gp); level-50 gate 32212,32435,10 then teleport 32212,32433 -> 32281,32388,10; key 3980 in the small hole 32219,32401,10 (uid 10014, a crate on it); barrels at 32253/32268,32401,10 to push aside; door 32277,32420,10 = key 3980; bodies (uid 10015-10019): tower shield 32239,32471,10, warrior helmet 32239,32478,10, dwarven ring 32233,32493,10, elven amulet 32245,32492,10, knight axe 32256,32500,10; portal 32234,32502,10 -> 32210,32437,10.
- **Confidence:** medium. The route is solid, but the rewards and level door conflict with Tibiantis.

### Devil Helmet Quest
- **Other names:** Mintwallin Lab Quest, Markwin's Secret.
- **Location:** Thais Ancient Temple (entrance around x 32356, y 32171, z 7), deep toward Mintwallin. The grate is around x 32482, y 32171, z 14.
- **Added / in 7.4:** the wiki says 5.01. Yes.
- **Requirements:**
  - Level 30 door.
  - **At least 2 players**: one stands on a tile to open a grate and cannot finish the quest.
  - Free account.
  - Rope and Destroy Field. A Pick is optional, for one exit.
  - Silver **Key 3610**, obtained during the quest.
- **Steps:**
  1. In the Ancient Temple, go down 2 levels and north, then down to the Rotworms.
  2. Go east and south, down a ladder, through the poison-field level, and down again.
  3. Go east and north (Minotaurs), then down the circled hole (Cyclopes).
  4. **Key:** go north and down into the Minotaur room (Minotaurs, Archers, Mages). Go south and up.
  5. Pull the switch. The wall moves and traps you with the Cyclopes. Kill them, use Destroy Field on the fire, then "use" the hole to get **Key 3610**. Exit through the north hole.
  6. Go back and take the leftmost passage south. Go up twice, along, and down twice.
  7. Head south, first left, past the side way to the Mad Mage room, then left to the ladders down toward Mintwallin.
  8. **Split up:** one player goes down the ladder, a bit west, up a hole, and south to a blocked passage. Standing on the open square opens a grate.
  9. The others go south past spiders and poison fields and down the grate. Go through the level 30 door, then up the hole.
  10. Kill the Dragon guarding the last room. The holes in the floor drop you to a Giant Spider and cannot be climbed back.
  11. Open the door with Key 3610 and go down. Face 3 Minotaur Guards, 2 Minotaur Archers and Minotaur Mages. The chests are there.
  12. There are 3 ways out:
      - back the way you came;
      - the Key 3610 door, then a hole to the labyrinth (2 Beholders; "Bonelords" in the current wiki);
      - Pick a hole to the west, which leads into Markwin's throne room in Mintwallin.
- **Rewards:** Devil Helmet, Halberd, 4 Small Sapphires. The pre8 wiki, current wiki and Tibiantis agree.
- **Once / rules:** unknown. The switch wall resets on floor reset or server save.
- **Sources:** https://tibia.fandom.com/index.php?oldid=60158 ; https://tibia.fandom.com/index.php?oldid=29957 ; https://tibia.fandom.com/wiki/Devil_Helmet_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** high.

### Geomancer Quest
- **Other names:** Undead Cave Quest.
- **Location:** Mount Sternum, north of Thais.
  - Current wiki marker: around x 32441, y 32008, z 13.
  - pre8 photo link of the quest room: x 32364, y 31948, z 13 (tibia.pl link, as given).
- **Added / in 7.4:** version unknown. The page existed in Oct 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. Bring a Rope.
- **Steps (pre8):**
  1. Take the hole and staircase in the centre of Mt Sternum.
  2. Go north and down.
  3. Go south and up.
  4. Go west and north past the Graveyard of the Doomed, then down.
  5. Go directly west and down a hole.
  6. Go SE past the Dwarf Soldiers and down.
  7. Go to the north end and down.
  8. Go north and down.
  9. The quest box is on the east side of the room, behind Dwarf Guards and a Dwarf Geomancer.
- **Rewards:** Small Sapphire, Small Diamond, Dwarven Ring. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=65209 ; https://tibia.fandom.com/index.php?oldid=29967 ; https://tibia.fandom.com/wiki/Geomancer_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium.

### Ghoul Room Quest
- **Other names:** none known.
- **Location:** Thais Ancient Temple (entrance around x 32356, y 32171, z 7).
- **Added / in 7.4:** the wiki says 5.01. Yes.
- **Requirements:** level 0, 1 player, free account. Antidote or Destroy Field is recommended. **Key 3600** is found in the quest.
- **Steps:**
  1. Go down 2 levels in the Ancient Temple and north to the end of the large room.
  2. Go down to the Rotworms, then east, south and east, and down a ladder.
  3. Cross the poison-field room and go down the ladder.
  4. Take the small tunnel east, then north, to a room with Skeletons and Rotworms.
  5. Open the dead skeleton in the SE of that room to get Key 3600.
  6. Use the well in that room to go down.
  7. Kill 3 Ghouls, unlock the door with Key 3600, and take the reward.
- **Rewards:** Garlic Necklace, Club Ring. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=24026 ; https://tibia.fandom.com/index.php?oldid=29968 ; https://tibia.fandom.com/wiki/Ghoul_Room_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Our server (2026-09-24):** dead skeleton 32509,32181,13 uid 3601 = key 3600; well 32508,32176,13 (aid 54545) down; door 32506,32175,14 = key 3600; chest 32500,32176,14 uid 3602 = garlic necklace (150) + club ring, once per character.
- **Confidence:** high.

### Kingdom of Kormarak Quest
- **Other names:** Old Mintwallin Quest.
- **Location:** Thais Ancient Temple (entrance around x 32356, y 32171, z 7). A sign reads "Home of the dead Kingdom of Kormarak – Enter and die!"
- **Added / in 7.4:** version unknown (the infobox field is blank). A pre8 spoiler exists (Oct 2006, "Old Mintwallin Quest"), and the quest is on Tibiantis. Likely yes.
- **Requirements:** level 0, 1 player, free account. Rope. Antidote is recommended.
- **Steps:**
  1. Take the Ancient Temple route down past the poison-gas room. The next ladder has 3 Minotaurs and Poison Spiders.
  2. Go north. The Ghoul Room is on this route.
  3. Go up the stairs by the sign. There are 3 Ghouls and a teleporter (a "Magic Forcefield").
  4. The teleporter leads to a room with about 10–15 Ghouls (11 in the current wiki) and a Demon Skeleton.
  5. Open the dead human by the wooden coffin.
- **Rewards:** Brass Armor, Brass Helmet, Hatchet, 13 Throwing Stars. This comes from the wiki since 2011 and Tibiantis; the pre8 spoiler does not name items.
- **Once / rules:** **daily respawn, not once per player.** The pre8 wiki says "It is a spawn, so you may find the body empty". The current wiki says one character per floor reset.
- **Sources:** https://tibia.fandom.com/index.php?oldid=62130 ; https://tibia.fandom.com/wiki/Kingdom_of_Kormarak_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium-low for the 7.4 item list.

### Life Ring Quest
- **Other names:** none known.
- **Location:** Thais Ancient Temple, south branch (entrance around x 32356, y 32171, z 7).
- **Added / in 7.4:** version unknown. The page existed in June 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. Pick and Rope.
- **Steps:**
  1. Go down the temple steps, then south and down a level.
  2. Go east through Orcs to water and a drawbridge. If the bridge is up, pull the lever south of it through a narrow passage.
  3. Cross, then go east past 2 Beholders and south past 2 more, to a dead end at water.
  4. Pick the hidden hole on the west wall.
  5. Go down. There are 3 Beholders; roping them up one by one is suggested.
  6. The quest box is in the NE corner.
- **Rewards:** Life Ring, Dragon Necklace. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=58720 ; https://tibia.fandom.com/index.php?oldid=35324 ; https://tibia.fandom.com/wiki/Life_Ring_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Our server (2026-09-24):** drawbridges 32410-32412,32231-32232,10 and 32408-32410,32253,10 down (levers unscripted); pick spot 32437,32239,10; box 32443,32238,11 uid 3616 = life ring + dragon necklace (200), once per character; rope up.
- **Confidence:** medium.

### Mad Mage Room Quest
- **Other names:** Mad Mage Quest, Hat of the Mad Quest, Skull Room Quest.
- **Location:** Thais Ancient Temple, on the route to Mintwallin. Entrance around x 32356, y 32171, z 7.
- **Added / in 7.4:** the wiki says 7.24 (15 Mar 2004). Yes.
- **Requirements:**
  - Level 40 door.
  - 1 player, free account.
  - 7 Red Apples.
  - **Key 3620** to reach A Prisoner (current wiki; it is found in the barracks south of Markwin in Mintwallin).
  - **Key 3666**, which you get from A Prisoner.
  - Rope and Shovel.
- **Steps:**
  1. Go to the Mintwallin prison and talk to **A Prisoner**. Say hi → riddle → "PD-D-KS-P-PD".
  2. Give the 7 apples and answer yes to his repeated "really?" prompts. You receive silver **Key 3666**.
  3. Route: Ancient Temple → down 2 levels, north → Rotworms → east/south, down ladder → poison fields → down → east/north (Minotaurs) → down the circled hole (Cyclopes).
  4. Take the leftmost passage south, go up twice and down twice, then south, west, north and right to the **level 40 door**.
  5. Go down the stairs. Expect a Dragon, Giant Spider, Beholder/Bonelord, Demon Skeletons, Ghoul, Scorpion and Skeleton.
  6. Open the SE locked door with Key 3666 and go up the ladder. Fight 2–3 Demon Skeletons.
  7. The rewards are in the chests.
  8. A book in the NE bookcase ("The Riddle") holds the riddle's answer.
- **Rewards:**
  - Quest boxes: Hat of the Mad, Stone Skin Amulet, Star Amulet. All three are taken; there is no choice.
  - A separate daily chest (pre8): Silver Dagger, Mana Fluids, and per the pre8 wiki also Energy Ring, Blank Runes, Throwing Stars and food.
  - The current wiki and Tibiantis say "Mana Potions", which is a modern replacement.
- **Once / rules:** quest boxes are presumably once per character. The side chest is a daily respawn.
- **Sources:** https://tibia.fandom.com/index.php?oldid=64426 ; https://tibia.fandom.com/index.php?oldid=41066 ; https://tibia.fandom.com/wiki/Mad_Mage_Room_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Our server (2026-09-24):** barracks drawer 32411,32155,15 (uid 13620 = key 3620); prison doors 32395,32117,15 and 32393,32136,14 (key 3620); A Prisoner 32393,32137,13, talked to through the bars from 32396,32137,13 (answer + 7 red apples -> key 3666); level-40 gate 32544,32179,14; door 32578,32197,15 (key 3666), ladder up; box 32573,32200,14 = magician hat (10058), top box 32574,32200,14 = stone skin amulet 5 (10059), chest 32577,32200,14 = star amulet (10060).
- **Confidence:** high. Key 3620 comes only from the current wiki.

### Mintwallin Cyclops Quest
- **Other names:** none known.
- **Location:** Thais Ancient Temple depths (entrance around x 32356, y 32171, z 7).
- **Added / in 7.4:** version unknown. The page existed in Oct 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. Rope. Antidote or Destroy Field.
- **Steps:**
  1. Follow the Ancient Temple route to the cyclops hole, as in the Devil Helmet Quest.
  2. Go north and down into the Minotaur room.
  3. Go south in the room and up a level.
  4. Enter the NW corner and follow the passage to the switch. Pulling it moves the wall and traps you with the Cyclopes.
  5. Take the reward. Exit by the north hole back to the Minotaur room.
  6. The current wiki adds that if the wall is already moved, you must wait for a reset or use Key 3667.
- **Rewards:**
  - pre8: Small Diamond.
  - Current wiki: Small Diamond, 2 Strong Health Potions, Hatchet, Chain Helmet, Chain Armor. The potions are modern.
  - Tibiantis: Small Diamond, 2 Health Potions, Hatchet, Chain Helmet, Chain Armor.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=24200 ; https://tibia.fandom.com/index.php?oldid=29977 ; https://tibia.fandom.com/wiki/Mintwallin_Cyclops_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium. The exact 7.4 item list is uncertain.
- **Our server (2026-09-24):** switch 32602,32104,14 (aid 51016) moves the wall both ways (north 32593-32594,32103,14 open / west 32592,32104-32105,14 shut); key 3667 in the dead human 32576,32216,15 (under rubbish) opens door 32592,32102,14; chests 32589,32097,14 = key 3610 (uid 3610), 32590,32097,14 = small diamond (uid 3611); out by the north hole 32587,32089,14.

### Naginata Quest
- **Other names:** none known.
- **Location:** Thais Dragon Lair. The cave north of Alatar Lake is around x 32357, y 32085, z 7.
- **Added / in 7.4:** version unknown. The page existed in Oct 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 40 door, 1 player, free account. Rope and Pick. Destroy Field is recommended.
- **Steps:**
  1. Enter the cave north of Alatar Lake, go SE and down.
  2. Go south, then east, and up the ladder.
  3. Go SW and down **two** levels.
  4. Go around south and up.
  5. Go west and down.
  6. Go north and down.
  7. Go up into the Dragon Lair (Dragons, 1–2 Dragon Lords in the north).
  8. In the small north room, Pick the large rock over a hole (the current wiki warns this costs HP), then go down.
  9. The hole beyond the level 40 door leads down to 2 Dragon Lords.
  10. The chest is at the north end.
- **Rewards:** Naginata. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=55796 ; https://tibia.fandom.com/index.php?oldid=38904 ; https://tibia.fandom.com/wiki/Naginata_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium.

### Noble Armor Quest
- **Other names:** Skjaar Quest, DTD Quest.
- **Location:** hidden cave below Mount Sternum. The current wiki's west entrance is around x 32450, y 32070, z 7.
- **Added / in 7.4:** version unknown. The page existed in Aug 2005, and the quest is on Tibiantis. Yes.
- **Requirements:**
  - Level 35 gate.
  - 1 player, free account.
  - Rope.
  - 1000 gp to buy **Key 3142** from NPC **Skjaar**.
- **Steps (pre8):**
  1. Take the ladder by the water on the north side of Mt Sternum (Cyclopes).
  2. Go N/W and down; SW and up; E/N and down; north and up; west past the Cyclops spawn and down.
  3. Kill the Skeletons and Ghouls, then rope up at the north end.
  4. Talk to Skjaar: hi → key → yes → yes (pay 1000 gp).
  5. Answer the quiz: "redips" (Dago's pet), "7" (fingers), "black" (demon colour). Then yes to receive Key 3142.
  6. Check first whether the door is already unlocked, or you may waste the 1000 gp.
  7. Pass the level 35 gate, unlock the crypt with Key 3142, kill the Ghouls (4 in the current wiki), and open the chests.
- **Rewards:**
  - pre8 and current wiki: Noble Armor and Crown Helmet.
  - Tibiantis: "Noble Armor" only.
  - The current wiki mentions an extra daily chest on a fire: Short Sword, 8 Poison Arrows, 34 gp, White Pearl.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=73459 ; https://tibia.fandom.com/index.php?oldid=33323 ; https://tibia.fandom.com/wiki/Noble_Armor_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium.

### Scale Armor Quest
- **Other names:** none known.
- **Location:** cave directly west of the Ancient Temple entrance, near Thais. The shovel hole is around x 32337, y 32172, z 7.
- **Added / in 7.4:** version unknown. The page existed in June 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. Shovel and Rope. Antidote is recommended.
- **Steps:**
  1. Shovel open the hole and go down.
  2. Go north and east to a room with a well.
  3. Use the lower-right corner of the well to go down. Expect Scorpions.
  4. Open the chests.
- **Rewards:**
  - pre8: Scale Armor, Piece of Iron and a Book.
  - Current wiki and Tibiantis: Scale Armor.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=24179 ; https://tibia.fandom.com/index.php?oldid=56731 ; https://tibia.fandom.com/wiki/Scale_Armor_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Our server (2026-09-24):** shovel hole 32335,32174,7 (rope spot below; the cave also has a ladder way out at 32347,32123,8); well 32354,32131,8 (aid 54545) down; chest 32357,32130,9 uid 10061 = scale armor, once per character; chest 32357,32131,9 (piece of iron, book) ordinary.
- **Confidence:** medium.

### Silver Amulet Quest
- **Other names:** Thais Silver Amulet Quest.
- **Location:** Thais Troll Cave. The entrance is around x 32503, y 32267, z 7. The box is in the SE cellar, around x 32507, y 32270, z 9.
- **Added / in 7.4:** the wiki says 5.2. The page only dates from 2011, but the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. Shovel.
- **Steps:**
  1. Shovel into the troll cave (Trolls, Wolves).
  2. Go to the SE cellar at z 9 and open the box.
- **Rewards:** Silver Amulet.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/wiki/Silver_Amulet_Quest/Spoiler ; https://tibia.fandom.com/wiki/Silver_Amulet_Quest ; https://tibiantis.info/library/quests
- **Confidence:** medium. There is no 7.x-era wiki text.

### Six Rubies Quest
- **Other names:** Double Dragon Quest.
- **Location:** Thais Ancient Temple (entrance around x 32356, y 32171, z 7).
- **Added / in 7.4:** version unknown. The page dates from Jan 2006 and the quest is on Tibiantis. Likely yes.
- **Requirements:** level 0, 1 player, free account. Rope and at least 1 Destroy Field.
- **Steps:**
  1. Go down both sets of stairs in the Ancient Temple.
  2. Go south through the first door, west, south through a second door, and straight past one intersection.
  3. At the second intersection go east, then south (Orc Warriors), and down the east hole.
  4. Below are up to about 7 Orcs.
  5. Go south, then NW, to stairs with fire underneath, and go down.
  6. Go east and south to a hole. Below it, 2 Dragons stand on a fire island; luring them to the rope spot is suggested.
  7. On the east side of the island, Destroy Field the fire covering a hole.
  8. **Use** the hole; you do not go down it. It gives the reward.
- **Rewards:** 6 Small Rubies. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=71251 ; https://tibia.fandom.com/index.php?oldid=71427 ; https://tibia.fandom.com/wiki/Six_Rubies_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium.

### Small Ruby Quest
- **Other names:** none known.
- **Location:** Mintwallin. The throne-room stairs are around x 32425, y 32136, z 15, the ladder to the pit around x 32435, y 32172, z 13, and the hole around x 32436, y 32189, z 14. These values come from wiki mapper links (the z values are as given).
- **Added / in 7.4:** version unknown. The wiki page only dates from 2012, but the quest is on Tibiantis. Likely yes, but unconfirmed.
- **Requirements:** level 0, 1 player, free account. Shovel, Rope and Destroy Field.
- **Steps:**
  1. Follow the Mintwallin route.
  2. Go south and up the stairs to the throne room, then take the ladder a bit SW into the pit (1 Dragon).
  3. Go down the hole (2 Dragons).
  4. Destroy Field or "browse" the fire field at the north of the room.
- **Rewards:** 1 Small Ruby.
- **Once / rules:** **daily respawn** (current wiki).
- **Sources:** https://tibia.fandom.com/wiki/Small_Ruby_Quest/Spoiler ; https://tibia.fandom.com/wiki/Small_Ruby_Quest ; https://tibiantis.info/library/quests
- **Confidence:** low. There is no 7.x-era documentation.

### Spike Sword Quest
- **Other names:** Fire Devil Quest.
- **Location:** small cave east of Mount Sternum, a few steps NE of Triangle Tower. Entrance around x 32593, y 32068, z 7.
- **Added / in 7.4:** version unknown. The page existed in Aug 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. Shovel, Rope and Pick. Invisible or a Stealth Ring is highly recommended.
- **Steps:**
  1. Enter the cave and go down twice.
  2. Pick a hole SW and go down (1 Fire Devil).
  3. Go around west and down (more Fire Devils).
  4. Pick a hole in the SW corner and go down to a lava room with many Fire Devils, some on islands.
  5. The reward is in a body hidden behind a pillar. There are 3 caged Dragons at the far north.
- **Rewards:** Spike Sword. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=67742 ; https://tibia.fandom.com/index.php?oldid=67142 ; https://tibia.fandom.com/wiki/Spike_Sword_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium.

### Thais Lighthouse Quest
- **Other names:** Dark Shield Quest.
- **Location:** lighthouse SW of Thais, around x 32226, y 32277, z 7.
- **Added / in 7.4:** the wiki says 3.0. Yes.
- **Requirements:** level 0, free account. **2 players**: one holds a step switch and one pulls a lever.
- **Steps:**
  1. Go down to the lighthouse basement. A corpse there holds a book about a secret dungeon (current wiki).
  2. Find the switch under crates. It makes a ladder down appear.
  3. Downstairs there are north, south and east (right) passages.
  4. North has a step switch. While one player stands on it, stairs open at the south end.
  5. The other player goes down those stairs and pulls a lever. This activates a teleporter in the east passage.
  6. The teleporter leads to the Cyclops room (2–5 Cyclopes). The chests are at the north end.
- **Rewards:** Dark Shield, Battle Hammer. All sources agree.
- **Once / rules:** unknown. The pre8 wiki notes the portal can be switched off, trapping players inside.
- **Our server (2026-09-24):** switch under the crates (32227,32278,8, aid 51001) opens trapdoor 369 at 32225,32276,8; step switch 32225,32268,9 (aid 51002) opens stairs 410 at 32225,32282,9 while occupied; lever 32225,32285,10 (aid 51003) toggles two fields: in 32233,32276,9 -> 32225,32271,10 and out 32225,32276,10 -> 32232,32276,9. No source shows the way out; the two-field lever was decided with the user. Chests once per character.
- **Sources:** https://tibia.fandom.com/index.php?oldid=61618 ; https://tibia.fandom.com/index.php?oldid=61619 ; https://tibia.fandom.com/wiki/Thais_Lighthouse_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** high.

### Throwing Star Quest
- **Other names:** none known.
- **Location:** Thais Ancient Temple, in the "underground park" (entrance around x 32356, y 32171, z 7).
- **Added / in 7.4:** version unknown. The page existed in Nov 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. Pick and Rope. Antidote is recommended.
- **Steps:**
  1. Follow the Ancient Temple route to the cyclops hole, as in the Devil Helmet Quest.
  2. Go around to the underground park and Pick where the map indicates.
  3. The quest box is just SE of the ladder.
- **Rewards:** 10 Throwing Stars. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=24062 ; https://tibia.fandom.com/index.php?oldid=34977 ; https://tibia.fandom.com/wiki/Throwing_Star_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Our server (2026-09-24):** pick spot 32517,32107,14 (ladder below); box 32522,32111,15 uid 3619 = 10 throwing stars, once per character.
- **Confidence:** medium.

### Triangle Tower Quest
- **Other names:** none known.
- **Location:** Triangle Tower, east of Thais. Around x 32561, y 32119, z 7. The desert lever that opens the tower wall is around x 32574, y 32122, z 7.
- **Added / in 7.4:** version unknown. The page existed in Aug 2005, and the quest is on Tibiantis. Yes.
- **Requirements:** level 0, 1 player, free account. A Stealth Ring or Invisible is suggested.
- **Steps:**
  1. If the tower is closed, pull the lever in the desert.
  2. Climb the tower, floor by floor:
     - Ground floor: 4 Skeletons.
     - Next floor: 4 Ghouls.
     - Next floor: 3 Demon Skeletons.
     - Next floor: 3 Demon Skeletons (2 in the current wiki), 2 Ghouls, 2 Stalkers.
     - Top floor: a Monk, a Witch and a Dwarf Geomancer.
  3. Open the box.
  4. If you get locked in, the basement (Beholder/Bonelord) has a teleporter outside.
- **Rewards:** Garlic Necklace, Dwarven Ring, 2 Small Sapphires. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=60152 ; https://tibia.fandom.com/index.php?oldid=29994 ; https://tibia.fandom.com/wiki/Triangle_Tower_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium.

### Giant Smithhammer Quest
- **Other names:** none known. The pre8 spoiler is titled "Giant Smithing Hammer Quest".
- **Location:** Plains of Havoc cyclops/minotaur camp, stairs in the north structure around x 32779, y 32235, z 7. Tibiantis files it under "Venore".
- **Added / in 7.4:** the wiki says 7.24. Yes.
- **Requirements:** level 0, 1 player, free account. Invisible is advised.
- **Steps:**
  1. Go down the stairs in the north building. Many Cyclopes, Minotaurs, Minotaur Guards, Minotaur Mages and Orcs are there.
  2. The quest box is in the room directly south.
- **Rewards:** Talon, Giant Smithhammer, 100 gp. All sources agree.
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=34890 ; https://tibia.fandom.com/index.php?oldid=34008 ; https://tibia.fandom.com/wiki/Giant_Smithhammer_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** high.

### Ornamented Shield Quest
- **Other names:** Might Ring Quest.
- **Location:** Plains of Havoc Dragon Lair. The hidden hole is around x 32775, y 32267, z 7.
- **Added / in 7.4:** the wiki says 5.1. Yes for part 1. Part 2 (the red bag) only appears in the current wiki.
- **Requirements:** level 0, free account. Rope, Shovel, Pick and Destroy Field. Part 2 needs **2 players**.
- **Steps:**
  1. Go down the hidden hole: 1 Dragon; down: 2 Dragons; down: 2 Dragon Lords, more Dragons, and Demodras as a rare spawn.
  2. In the treasure room, pick a hole 2 sqm right of the leftmost of two adjacent rocks, a little left of centre. Go down.
  3. Kill the Fire Devil. Destroy Field the fire in the NE corner of the passage, with the body under it.
  4. The body is Krendorak's corpse. It holds the brown bag.
  5. **Part 2 (current wiki only):** rope back up. A partner stands SW of the fire field in the NW corner, which removes the stalagmites in the SW corner.
  6. Open the chest behind them (Red Bag). The rope hole there exits near the Necromant House.
- **Rewards:**
  - pre8: Ornamented Shield, Steel Helmet (daily spawn), bag with Crystal Key 3702 (used to open a door in Knightwatch Tower), Spike Sword, Dragon Necklace, Might Ring, Krendorak's journal (book).
  - Current wiki and Tibiantis add an Inkwell and "Devious Dragons" book, plus a Red Bag: Time Ring, 5 Platinum Coins, Garlic Necklace, Spellbook, Lyre.
  - The treasure room also has daily floor spawns (current wiki).
- **Once / rules:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=53190 ; https://tibia.fandom.com/index.php?oldid=43513 ; https://tibia.fandom.com/wiki/Ornamented_Shield_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** medium. It is unconfirmed whether the red-bag part existed in 7.4.

## Carlin, Ghostlands, Isle of the Kings, Ab'Dendriel, Kazordoon

### Alawar's Vault Quest
- **Other names:** Senja Minotaur Quest, Senja Castle Quest, Ice Islands Quest, Dark Helmet Quest (for the part in the maze).
- **Location:** Senja and Folda, the ice islands north of Carlin. Senja ferry around (32234, 31677, 7). Senja Castle cellar around (32191, 31633, 7). Folda cave entrance around (31999, 31571, 7).
- **Version:** added in 6.5, so it was in 7.4. Tibiantis lists it.
- **Requirements:** no level requirement (wiki recommends level 25). Free account. Bring 20gp for the ferry, a Pick (long path) and a Destroy Field rune (short path).
- **Steps (short path, Senja):**
  1. Take the raft north of Carlin to Senja (20gp).
  2. Go down into the Senja Castle cellar and cross the room full of energy, fire and poison fields.
  3. At the far west, use a Destroy Field rune on the fire field to uncover a lever. Pull it: the lever vanishes and the magic walls or door to the north open.
  4. Go north into the magic forcefield (teleport) to reach Alawar's Vault. Minotaurs and a Minotaur Mage are there.
  5. Open the 2 chests by the teleporter: 3 White Pearls and a Broadsword. The vault's teleporter takes you to the castle roof.
- **Steps (long path, Folda):**
  1. Take the ferry to Folda and enter the Folda caves.
  2. Get copper **Key 4503** from a chest behind fire fields in the western room.
  3. Use Key 4503 on the door of the "protected area". At the end of that passage, use the Pick on the spot under the fire field against the wall and go down. This is one-way: you drop 2 floors.
  4. On the minotaur level, get **Key 4501** (first room) and **Key 4502** (in the maze, which has a Minotaur Mage and archers; the maze also holds the "Dark Helmet" reward boxes).
  5. Go back up the stairs and open the doors to Alawar's Vault. Beware beholders on the way.
- **Rewards:** short path gives 3 White Pearls and a Broadsword. The long path also gives the Dark Helmet, 4 Throwing Knives, a Blank Rune, 33gp and Keys 4501, 4502 and 4503. Tibiantis lists the same full set. You take all of them, not one of several.
- **Once per player:** yes (quest chests).
- **Sources:** 7.x spoiler https://tibia.fandom.com/index.php?oldid=42078 ; 7.x infobox https://tibia.fandom.com/index.php?oldid=59159 ; current https://tibia.fandom.com/wiki/Alawar%27s_Vault_Quest/Spoiler ; Tibiantis list.
- **Confidence:** high. The two sources disagree on which key opens what: the current wiki says to bring Key 4502 in advance for the short path.

### Crystal Wand Quest
- **Other names:** Double SD Quest (its 7.x name), Demona Quest.
- **Location:** Demona warlock area, reached through the Maze of Lost Souls (MoLS) north of Carlin, in the Fields of Glory. Start cave south of Northport around (32488, 31610, 7). Shovel hole around (32512, 31624, 7). Exit teleport around (32400, 31657, 15), which brings you back to the Fields of Glory.
- **Version:** the infobox has no version. The pre-8.0 wiki (Apr 2006) documents it and Tibiantis lists it, so it was probably in 7.4.
- **Requirements:** level 60 Gate of Expertise before Demona. Free account. Bring a Shovel, a light source and food.
- **Steps:**
  1. From the cave south of Northport, dig the hole with the Shovel and go down.
  2. In the small underground forest, go down the hole behind the trees and turn the switch **right** to open the MoLS entrance. If it is already right, turn it left and then right again.
  3. Follow the MoLS route, crossing some Energy Fields. The first entrance room holds the Griffin Shield Quest.
  4. Pass the level 60 Gate of Expertise, go north and then right to the stairs to reach Demona.
  5. In Demona there are Warlocks, Stone Golems, an Elf Arcanist and Dwarf Soldiers. Go to the top of the room and down the stairs to the quest room, which has 4 Warlocks and 2 Dragons.
  6. Open the chests on the north side of the quest room.
- **Rewards:** Crystal Wand, a Sudden Death rune with 2 charges and the Twinkiller Rune (Book). On the current wiki the rune is called "Silver Rune Emblem (SD)", a later cosmetic rename. The Crystal Wand is an old item, not the 7.8+ wand weapons. You get all of them.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=43217 ; https://tibia.fandom.com/index.php?oldid=34471 ; https://tibia.fandom.com/wiki/Crystal_Wand_Quest/Spoiler ; Tibiantis list and tibiantis.life.
- **Confidence:** medium-high for the route and reward. The version it was added is unknown.

### Demona Ring Quest
- **Location:** Demona. From the main pentagram room, take the north-easternmost staircase down, follow the long hall to the big Elf Arcanist and Warlock room, then go up either staircase.
- **Version:** unknown. The wiki page was first created in 2016. Tibiantis lists it (level 60, free).
- **Requirements:** level 60 (the Demona gate). Free account. Bring a Shovel and a Rope.
- **Steps:**
  1. Follow the Demona route (see Crystal Wand Quest).
  2. In the main room, fend off Warlocks and the Elf Arcanist, then go down the NE stairs.
  3. Follow the hallway to the big room and go up a staircase, where more Warlocks wait.
  4. Two chests in the south of that floor: the left one holds a Stealth Ring and the right one an Energy Ring.
- **Rewards:** Stealth Ring and Energy Ring (Tibiantis agrees). Whether you can take both or must choose one is unknown.
- **Once per player:** unknown (probably yes).
- **Sources:** https://tibia.fandom.com/wiki/Demona_Ring_Quest/Spoiler (2016) ; Tibiantis list.
- **Confidence:** low-medium. There is no 7.x-era documentation.

### Fanfare Quest
- **Other names:** Carlin Troll Quest.
- **Location:** Carlin graveyard crypt, east of town. The house with the key box is around (32375, 31803, 7) and the crypt around (32407, 31784, 7).
- **Version:** unknown. The wiki page exists from July 2005 and Tibiantis lists it, so it was probably in 7.4.
- **Requirements:** none (wiki recommends level 8). Free account.
- **Steps:**
  1. In the building just north-west of the Carlin boat, get **Key 3520** from the box in the NE corner of the big room. The door is often already open.
  2. Enter the Carlin cemetery east of town and go down into the crypt at the south end.
  3. Open the door to the west and find a hole. Go down and follow the path north through the trolls.
  4. Use the chest to get the Fanfare.
- **Rewards:** Fanfare.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=23969 ; https://tibia.fandom.com/index.php?oldid=29966 ; https://tibia.fandom.com/wiki/Fanfare_Quest/Spoiler ; Tibiantis list.
- **Confidence:** medium-high.

### Griffin Shield Quest
- **Other names:** MoLS Quest.
- **Location:** the first entrance room of the Maze of Lost Souls, at the gates of Demona. It uses the same start as the Crystal Wand Quest, around (32488, 31610, 7).
- **Version:** unknown. The wiki has documented it since July 2006 and Tibiantis lists it (level 30, free).
- **Requirements:** the infobox says level 30, but the spoiler does not mention a level door. Free account. Bring a Shovel and food.
- **Steps:**
  1. Follow the same route as the Crystal Wand Quest: the cave near Northport, then the Shovel hole, then the switch turned **right**. A sign by the switch from Zhandramon says "Turn the switch to the right and follow the blue sunshine to get to Demona."
  2. Follow the MoLS map to the final room, which holds 2 Dwarf Guards, 2 Minotaur Guards, 2 Stone Golems and 3 Elf Arcanists.
  3. Take the rewards from 2 slain skeletons and a dead body.
- **Rewards:** Griffin Shield, Dwarven Axe, Obsidian Lance (all of them).
- **Once per player:** yes (quest corpses).
- **Sources:** https://tibia.fandom.com/index.php?oldid=71210 ; https://tibia.fandom.com/index.php?oldid=43219 ; https://tibia.fandom.com/wiki/Griffin_Shield_Quest/Spoiler ; Tibiantis list.
- **Confidence:** medium. The level 30 requirement is unclear.

### Power Ring Quest
- **Other names:** Bronze Amulet Quest, Femor Hills Goblin Quest.
- **Location:** Femor Hills, south of the river just north of the magic carpet. The spoiler landmark is around (32575, 31797, 7).
- **Version:** unknown. The wiki page exists pre-8.0 and Tibiantis lists it (free).
- **Requirements:** none (wiki recommends level 15). Bring a Rope.
- **Steps:**
  1. In Femor Hills, follow the south side of the river into the mountain and rope up one level.
  2. Head east into the mountain and go down the ladder to the north.
  3. Go NE and down the hole. A rotworm may be there.
  4. That room has up to 11 Goblins, 4 Wolves and fire fields. Go SW and drop down one more level.
  5. That level has up to 11 more Goblins and a pig pen. The quest boxes are at the north end, by the beer casks.
- **Rewards:** Power Ring and Bronze Amulet.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=66277 ; https://tibia.fandom.com/index.php?oldid=66278 ; Tibiantis list.
- **Confidence:** medium-high.

### Purple Tome Quest
- **Other names:** Map Quest.
- **Location:** a library room in Demona, reached from the north-west ladder of the star room. The room is around (32421, 31595, 15).
- **Version:** unknown. The first wiki page is from 2020. Tibiantis lists it (level 60, free).
- **Requirements:** level 60 (the Demona gate). Bring a Shovel and a Rope.
- **Steps:**
  1. Reach Demona (see Crystal Wand Quest).
  2. Take the NW ladder of the star room, the one leading to the exit teleport.
  3. Take the first way north to the room full of bookcases. An Infernalist spawns there today; Infernalists did not exist in 7.4.
  4. Search the bookcases for the maps and the tome.
  5. Leave by the teleport around (32400, 31657, 15), which goes to the Fields of Glory.
- **Rewards:** Tibia Map (Book), Fields of Glory Map (Book) and Purple Tome. The first wiki revision called the maps "Map (Brown)" and "Map (Colour)".
- **Once per player:** unknown.
- **Sources:** https://tibia.fandom.com/wiki/Purple_Tome_Quest/Spoiler ; Tibiantis list.
- **Confidence:** low-medium.

### The Queen of the Banshees Quest
- **Other names:** Banshee Quest, BQ.
- **Location:** under the Ghostlands and the Isle of the Kings, west of Carlin. The entry hole in the Ghostlands is around (32223, 31861, 7). You exit to the Ghostlands surface around (32202, 31846, 7).
- **Version:** added in 7.2 (Dec 2003), so it was in 7.4.
- **Requirements:** level 60. The Banshee Queen will not give the 7th seal below level 60. There is no level door. Free account. Any vocation. A party is recommended. Bring a Rope, a Pick, a vial of blood, 1 Black Pearl and 1 White Pearl.
- **Steps (7.x wiki order):**
  1. **Seal 1:** go down the Ghostlands hole, then south and down another hole, then SE and down again. East of the rope spot are Magic Walls. Pull 2 switches to open them: the west switch lies past scorpions, demon skeletons and ghouls, and the east switch is guarded by a Giant Spider. The walls close quickly, so use haste. Go down the hole past the walls and walk north through mummies, ghosts, demon skeletons and stalkers. The current wiki adds that walking over the poison fields reveals a switch, which opens stairs down to teleporter A. In the long hall, do not walk south (a hidden teleporter returns you to the start); use the Pick in the middle of the hall and go down. Walk through the blue flame: each person who does summons 2 ghosts and 1 demon skeleton. The flame sends you to a small room whose teleporter brings you back.
  2. **Seal 2:** rope up, go south and then west, up the ramp and down into a round chamber with ghosts, stalkers and demon skeletons. Go down the stairs, then far SE. Set the switches to match the picture, then go through the flame and back through the teleporter.
  3. **Seal 3:** go down the stairs, then SW past about 10 Banshees. A quest door here hides the Spectral Dress, which belongs to the 7.6 Explorer Society. Go NW up the stairs, walk the tile pattern, then go through the flame and the teleporter.
  4. **Seal 4:** go north up into a room with 5 ghosts, 5 stalkers and 2 demon skeletons, then down, along and up into a room full of poison fields. At the north corner, pour the blood on the tile between the 2 big stones, then go through the flame and the teleporter.
  5. **Seal 5:** stepping on a special (depot-like) tile spawns 2 Warlocks per party member. Kill them, pull the switches in the order shown on the wiki picture, then go through the flame.
  6. **Seal 6:** go north past 2 Giant Spiders and use the Pick at the marked spot. Continue up to a level of demon skeletons. A rope spot there leads into the Isle of the Kings catacombs. Pick your way into the seal room, place the Black and White Pearls where the picture shows, and use either teleport.
  7. **Seal 7:** the Queen of the Banshees is near seal 4, guarded by 4 banshees. Say: `hi`, `seventh seal`, `yes` x6, `kiss`, `yes`. You are teleported to "your grave" and go upstairs to the Ghostlands.
  8. **Final room:** it is west of the Queen. Walk back in from the Ghostlands or via the Isle of the Kings. Once downstairs you cannot go back up. The room holds 6 Banshees, 2 Dragon Lords and 2 Giant Spiders. Take everything: you cannot re-enter after leaving through the magic forcefield.
- **Rewards:**
  - 7.x wiki: Boots of Haste, Giant Sword, Tower Shield, Stealth Ring, Stone Skin Amulet and 10k gp. You get all of them, not one of several.
  - Current wiki: the same list, with the 10k given as 100 Platinum Coins.
  - **Tibiantis:** Boots of Haste, Amulet of Loss, Stealth Ring, Stone Skin Amulet. This conflicts with the wiki.
- **Once per player:** yes. The seal progress is stored per player.
- **Other rules:** do not enter the 3rd floor of the Isle of the Kings monastery (restricted; you must pay a gold sacrifice).
- **Sources:** https://tibia.fandom.com/index.php?oldid=71882 (spoiler, Dec 2006) ; https://tibia.fandom.com/index.php?oldid=71869 (infobox) ; https://tibia.fandom.com/wiki/The_Queen_of_the_Banshees_Quest/Spoiler ; Tibiantis list and tibiantis.life.
- **Confidence:** high for the steps. Rewards conflict between Tibiantis and TibiaWiki (Amulet of Loss vs Giant Sword/Tower Shield/10k). The seal numbering also differs: the current wiki renumbers the seals (for example "Sixth Seal: Seal of Logic" is done second).

### The White Raven Monastery Quest (Family Brooch / Ghostlands / Dalbrect / Isle of the Kings)
- **Other names:** Family Brooch Quest (its 7.x name), Island of Kings Quest.
- **Location:**
  - The hole under the Ghostlands wall, west of Carlin, around (32219, 31768, 7).
  - The abandoned house in the Ghostlands around (32246, 31837, 7).
  - Dalbrect, at the port north of the Ghostlands, NPC position (32211, 31755, 6); his boat is around (32205, 31758, 7).
  - The Isle of the Kings around (32173, 31938, 7).
  - The Monk's Diary cave is the Banshee entry hole around (32223, 31861, 7).
- **Version:** 7.24 (Mar 15, 2004). The Blessed Ankh item is also 7.24, and Costello is 7.2. It was in 7.4.
- **Requirements:** no level. Free account. Bring a Rope and a Shovel. The diary part needs a group able to handle demon skeletons, a giant spider and a bonelord.
- **Steps, part 1 (Family Brooch and access to the Isle):**
  1. Enter the Ghostlands through the hole under the wall west of Carlin.
  2. Go to the abandoned house to the south and go down inside it. The basement has a Demon Skeleton and 1-2 Ghouls.
  3. Follow the corridor south and go down the stairs. There are 1-2 Stalkers. Going north risks more Stalkers, Demon Skeletons and a Wild Warrior disguised as a Knight Statue.
  4. Go east to the end of the passage, around to the south room (2 Demon Skeletons, 2 Stalkers, 2-4 Ghouls), and up the stairs.
  5. Use the head of the top coffin to get the **Family Brooch**. Its text reads "You see the familyname Windtrouser engraved on this brooch."
  6. Talk to **Dalbrect**: `hi`, `brooch`, `yes`, `yes`. He takes the brooch and considers you his friend.
  7. Then say `passage`, `yes` to travel to the Isle of the Kings for 10gp. The 7.x wiki gives 20gp for the return trip.
- **Steps, part 2 (investigation for Costello and the Blessed Ankh):**
  1. On the Isle, talk to **Costello**: `hi`, `fugio`, `yes`. You may now open the warded doors to the catacombs.
  2. In the Ghostlands, go into the Banshee entry cave. Pull the west switch (past scorpions and undead) and the east switch (behind a Giant Spider) to drop the magic walls. The whole team crosses together, because a tile before the hole resets the walls.
  3. Go down the hole and north. Use the Dead Human to get a Backpack containing the Monk's Diary, the book "They Are Coming". Leave through the portal.
  4. Back on the Isle, talk to Costello: `hi`, `diary`, `yes`. He gives the **Blessed Ankh**.
- **Rewards:** Family Brooch (surrendered to Dalbrect for permanent boat access), then the Blessed Ankh.
- **Once per player:** yes. Dalbrect's friendship is a permanent player flag.
- **Other access:** you can also reach the Isle through the Banshee Quest's pearl-seal area.
- **Sources:**
  - Spoiler: https://tibia.fandom.com/index.php?oldid=47837 (Aug 2006)
  - Infobox: https://tibia.fandom.com/index.php?oldid=29965
  - Dalbrect: https://tibia.fandom.com/index.php?oldid=41202
  - Family Brooch: https://tibia.fandom.com/index.php?oldid=45182
  - Ghostlands: https://tibia.fandom.com/index.php?oldid=66082
  - Isle of the Kings: https://tibia.fandom.com/index.php?oldid=66087
  - Current spoiler with transcripts: https://tibia.fandom.com/wiki/The_White_Raven_Monastery_Quest/Spoiler
  - Tibiantis list: Blessed Ankh, Family Brooch, access to the Isle.
- **Confidence:** high for part 1. Medium for part 2: the pre-8.0 spoiler covers only the brooch. The diary and ankh part comes from the current wiki, but the item and NPC versions (7.24 and 7.2) and Tibiantis's reward list support it being in 7.4.

### Draconia Quest
- **Location:**
  - Draconia pyramid, reached through Hellgate under Ab'Dendriel.
  - Shadow Caves entrance around (32655, 31670, 8).
  - Hellgate door around (32676, 31671, 10).
  - Redbone Castle, a protection zone, around (32666, 31672, 15).
- **Version:** 6.2, so it was in 7.4.
- **Requirements:**
  - Level 25 Gate of Expertise in front of the reward.
  - **At least 2 players**, for the floor switches on the 3rd floor.
  - Free account. Any vocation.
  - Key 3012 opens Hellgate. Buy it from Elathriel for 5000gp.
  - Bring a Rope and Destroy Field runes.
- **Steps:**
  1. Go down through Ab'Dendriel into the Shadow Caves, down 2 more floors, then south and east to the Hellgate door. Open it with Key 3012 and take the portal.
  2. Follow the Hellgate route to Draconia island. On the surface there are rotworms; cross to the other side, go down a hole, then up into the pyramid. A single Dragon room nearby has an escape portal to Ab'Dendriel.
  3. **Ground floor** (skeletons, scorpions):
     - **Key 3001** is in the skeleton corpses on the NW side.
     - Open the south door with it and walk the red carpet. The carpet deals fire and energy damage and has hidden holes down to 10 scorpions. **Key 3002** is in a coffin.
     - Open a door with Key 3002 and pull a lever, which removes a wall. Pull the next lever, which removes a rock, and take **Key 3003**.
     - Open the SE door with Key 3003 and go upstairs.
  4. **2nd floor** (skeletons, ghouls):
     - **Key 3004** is under an energy field: first row, third column, revealed with Destroy Field.
     - Its door leads to a maze. **Key 3005** is by a pillar or statue.
     - Its door leads to a fire and energy field room. **Key 3006** is in the SE corner.
     - Open the south-east door with Key 3006 and go up.
  5. **3rd floor** (6-8 ghouls, 2 demon skeletons): player 1 stands on the southern floor switch. Player 2 goes to the SW room and stands on its switch. Player 1 then takes the NW portal to the room with **Key 3007**.
  6. **4th floor** (mummies, demon skeletons): open the door with Key 3007. **5th floor** (8 mummies, 2 slimes): walk through.
  7. **6th floor** (3 demon skeletons, 3 mummies): the reward chests are behind the **level 25 door**. **Key 3008** is in the leftmost (western) bookcase.
  8. **7th floor:** open the door with Key 3008. Set the levers **Left, Right, Left, Right** and take the teleporter to the Ab'Dendriel sacrificial stone near the temple.
- **Rewards:** Ice Rapier, Serpent Sword, Stone Skin Amulet, Energy Ring (all). Tibiantis lists the same.
- **Once per player:** yes for the reward chests. Keys 3001-3007 are a daily respawn: whoever takes them first that day has them. The current wiki says Key 3008 can be taken once per player.
- **Sources:** https://tibia.fandom.com/index.php?oldid=63102 ; https://tibia.fandom.com/index.php?oldid=45121 ; Hellgate https://tibia.fandom.com/index.php?oldid=66086 ; https://tibia.fandom.com/wiki/Draconia_Quest/Spoiler ; Tibiantis list.
- **Confidence:** high. The 7.x text writes "use key 3011" once; this is a typo for Key 3001.

### Elvenbane Quest
- **Other names:** Elf Castle Quest.
- **Location:** Elvenbane castle, south, then west, then north from the Ab'Dendriel gate. Coordinates unknown.
- **Version:** unknown. The wiki page exists from June 2005 and Tibiantis lists it, so it was probably in 7.4.
- **Requirements:** no level (wiki recommends 35+). Free account. Destroy Field runes are optional.
- **Steps:**
  1. Drop down the hole surrounded by 4 stones into the Elvenbane basement.
  2. Run north and west to the opening, past an Orc Berserker, a Minotaur Guard, Minotaurs and an Orc Spearman.
  3. Enter the middle tower. The 1st floor is covered in poison fields. The 2nd floor has a Dragon. The 3rd floor has an Orc Shaman and a Minotaur Mage.
  4. The top floor has 2 Demon Skeletons and an Elf Arcanist, plus 2 quest chests and 2 quest drawers.
- **Rewards:**
  - 7.x wiki: Morning Star, Dwarven Shield, **Mana Fluid**, Blank Rune, Spellbook, 2 Small Diamonds, 100gp. You get all of them.
  - Current wiki: a Strong Mana Potion instead of the Mana Fluid.
  - Tibiantis: "Mana Potion", probably copied from the wiki. For 7.4, use a Mana Fluid.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=69151 ; https://tibia.fandom.com/index.php?oldid=42604 ; Tibiantis list.
- **Confidence:** medium-high.

### Orc Fortress Quest
- **Other names:** OF Quest.
- **Location:** Orc Fortress, west of Ab'Dendriel. Coordinates unknown.
- **Version:** 6.1, so it was in 7.4.
- **Requirements:** level 40 Gate of Expertise. Free account. No items needed.
- **Steps:**
  1. Enter the Orc Fortress hole and head east through the orcs.
  2. Go down the stairs, where Orc Leaders, Orc Warlords and a Dragon wait.
  3. Go east and north through the **level 40 door** into the throne room (Berserkers, Warlords, Slimes, Leaders, Orc Riders).
  4. The quest boxes are at the north end.
  5. The Orc King NPC is here. Do not say "hi": he summons many orcs.
- **Rewards:**
  - Wiki (both eras): Knight Armor, Knight Axe, Fire Sword.
  - **Tibiantis:** 10k, Stone Skin Amulet, 8 Small Emeralds.
  - It is unknown whether you get all of them or choose one; the wiki implies all.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=38820 ; https://tibia.fandom.com/index.php?oldid=49459 ; https://tibia.fandom.com/wiki/Orc_Fortress_Quest/Spoiler ; Tibiantis list and tibiantis.life.
- **Confidence:** high for the route. The rewards conflict: Tibiantis may reflect the original CipSoft data, or its own customisation.

### Circle Room Quest
- **Other names:** Dwarven Quest, Dwarf Hell Quest.
- **Location:** western dwarf mines of Kazordoon. The mine entrance is around (32495, 31975, 7).
- **Version:** unknown. The wiki page exists from Aug 2005 and Tibiantis lists it (level 32).
- **Requirements:** level 32 Door of Expertise. Free account. Bring a Rope for a quick exit.
- **Steps:**
  1. Enter the mine and go down another level.
  2. Go NE and down, then N and E and down, then S, W and N (Dwarf Soldier groups) and down, then directly S (Dwarf Guard groups) and down.
  3. Go S, W and N through the Dwarf Guards to the **level 32 door**, then go down the hole.
  4. The circle room is full of Dwarf Guards and Dwarf Geomancers, who drain mana. The quest boxes are at the far south end. Staying on the east side helps you avoid being surrounded.
- **Rewards:** Dwarven Axe, War Hammer.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=57512 ; https://tibia.fandom.com/index.php?oldid=29951 ; Tibiantis list and tibiantis.life.
- **Confidence:** high.

### Crusader Helmet Quest
- **Location:** deep Dwarf Mines (Pick 'N Shovel Mine) west of Kazordoon. The mine entrance is around (32548, 31987, 7) and the reward corpse around (32426, 31940, 14). The current wiki also describes an alternative way down from Mount Sternum at (32450, 32070, 7).
- **Version:** unknown. The wiki page exists from Sep 2005 and Tibiantis lists it (level 35).
- **Requirements:** level 35 Gate of Expertise. Free account. Bring a Rope.
- **Steps:**
  1. Enter the mines west of Kazordoon, go east and down, and immediately down again.
  2. Go far west, then N and W and down, then E and further down.
  3. Go north through the **level 35 door** and down the hole. Expect 3-5 Giant Spiders, which come one by one.
  4. The reward is in a skeleton body at the far west end of the tunnel.
- **Rewards:** wiki (both eras): Crusader Helmet. **Tibiantis:** "Dwarfen Helmet". This conflicts.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=63276 ; https://tibia.fandom.com/index.php?oldid=40697 ; https://tibia.fandom.com/wiki/Crusader_Helmet_Quest/Spoiler ; Tibiantis list.
- **Confidence:** high for the route, medium for the reward.

### Emperor's Cookies Quest
- **Other names:** Kazordoon Cookie Quest, Emperor Kruzak Quest.
- **Location:** Emperor Kruzak's chambers in Kazordoon. The Key 3800 chest is around (32605, 31909, 3) and the barracks around (32601, 31927, 6).
- **Version:** 6.1, so it was in 7.4.
- **Requirements:** none. Free account. A Rope is optional.
- **Steps:**
  1. Go to Emperor Kruzak's chambers. Walk along the north wall to avoid the Dwarf Guards, and shut the door behind you.
  2. In his private north room, at the end of the secret-passage exit, a chest holds **Key 3800**.
  3. Go back and open the small room in the emperor's chamber with Key 3800. Its chest holds a bag with 20+7 cookies and **Key 3801**.
  4. Go to the barracks. Open the door with Key 3801; the chest holds **Key 3802**. It opens the Dwacatra prison and the Mine Hub room in the Dwarf Mines.
- **Rewards:** Key 3800, a bag of cookies, Key 3801, Key 3802.
- **Once per player:** yes (quest chests).
- **Sources:** https://tibia.fandom.com/index.php?oldid=72569 ; https://tibia.fandom.com/index.php?oldid=45235 ; Tibiantis list.
- **Confidence:** high.

### Explorer Brooch Quest
- **Location:** under the sewer grates on the north side of the Jolly Axeman Tavern, Kazordoon, around (32637, 31888, 9).
- **Version:** 6.1, so it was in 7.4. The Explorer Society that later uses the brooch dates from 7.6, so in 7.4 it is only a collectible.
- **Requirements:** none. Bring a Rope.
- **Steps:** go down one of the 4 sewer grates in the tavern, kill the rat, and take the Explorer Brooch from the body.
- **Rewards:** Explorer Brooch.
- **Once per player:** yes (quest corpse).
- **Sources:** https://tibia.fandom.com/index.php?oldid=68474 ; https://tibia.fandom.com/index.php?oldid=64350 ; Tibiantis list.
- **Confidence:** high.

### Iron Hammer Quest
- **Location:** minotaur cave west of Kazordoon. The loose stone pile is around (32448, 31993, 7).
- **Version:** 6.61-6.97, so it was in 7.4.
- **Requirements:** none (wiki recommends level 30+). Bring a Rope and a Shovel.
- **Steps:**
  1. Dig the loose stone pile west of Kazordoon with the Shovel. The surface has dwarves and minotaurs.
  2. Go down and head NW past Minotaurs and Minotaur Archers to a room with beds.
  3. The quest box is between the beds.
- **Rewards:** Iron Hammer.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=24172 ; https://tibia.fandom.com/index.php?oldid=64526 ; Tibiantis list.
- **Confidence:** high.

### Longsword Quest
- **Other names:** Wedding Ring Quest (not the Edron Wedding Ring Quest).
- **Location:** troll cave east of the Dwarf Bridge, with its entrance hidden behind a tree, around (32662, 31966, 7).
- **Version:** unknown. The wiki page exists from Sep 2005 and Tibiantis lists it.
- **Requirements:** none. Bring a Shovel and a Rope.
- **Steps:**
  1. Enter the cave hidden behind a tree. Slimes are below a drain to the north.
  2. Go south and down the stairs.
  3. On the next level go north. A Minotaur Archer and a Minotaur Mage are in the north room.
  4. The quest boxes are at the north end of the large room.
- **Rewards:** Longsword, Mirror, 3 Blank Runes, Wooden Doll, Wedding Ring, 76gp.
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=53539 ; https://tibia.fandom.com/index.php?oldid=64626 ; Tibiantis list and tibiantis.life.
- **Confidence:** medium-high.

### Steel Helmet Quest
- **Other names:** Minotaur Tower Quest.
- **Location:** the minotaur tower ("Horned Fox's hideout") west of Kazordoon. The entrance is around (32489, 31965, 7).
- **Version:** 6.61-6.97, so it was in 7.4.
- **Requirements:** none (wiki recommends level 35). Bring a Shovel and a Rope.
- **Steps:**
  1. Enter the minotaur cave west of Kazordoon.
  2. Go east and north to the first intersection and rope up into the tower.
  3. Search the dressers and chests in the tower.
- **Rewards:** Steel Helmet, 47gp, 56gp and a book. The 7.x page calls it a "Scroll"; today it is The Fox Is Out (Book).
- **Once per player:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=56432 ; https://tibia.fandom.com/index.php?oldid=43499 ; Tibiantis list.
- **Confidence:** high. The Horned Fox is a later-added rare boss and should not be assumed for 7.4.

### The Paradox Tower Quest
- **Location:**
  - Paradox Tower near Kazordoon, around (32479, 31906, 1).
  - Levitate climb start, south of the Kazordoon entrance, around (32571, 31976, 7).
  - Return carvings around (32485, 31928, 7).
  - Minotaur cave shovel entry around (32489, 31966, 7), with its exit north of the tower around (32466, 31875, 7).
  - The dead tree with Key 3899 around (32496, 31888, 7).
  - NPCs: Oldrak (Plains of Havoc temple) at (32816, 32264, 7); Zoltan (Edron academy) at (33266, 31845, 4); Padreia (Carlin druid guild) at (32302, 31815, 7); Lubo (south of Mount Sternum) at (32488, 32120, 7); A Prisoner (Mintwallin prison) at (32395, 32138, 13).
- **Version:** 6.61-6.97, so it was in 7.4. The wiki page exists from Aug 2005.
- **Requirements:**
  - Level 30 per the infobox. The spoiler describes no level door.
  - **Premium account.** 1 player.
  - Bring: a Shovel; Levitate or parcels; a Machete; 4 Skulls; a Melon, Banana, Cherry, Apple, Grapes and Coconut; one White Knight and one Black Knight chess piece (from the game rooms in Edron, Carlin, Kazordoon or Thais); Key 3899. Key 3620 may be needed for the Mintwallin prison.
- **Steps:**
  1. **NPC chain** (sets knowledge flags):
     - Oldrak: `hi`, `hugo`, `myth`, `yenny the gentle`.
     - Zoltan: `yenny the gentle`, `crunors caress`.
     - Padreia: `crunor's caress`, `footnote`.
     - Lubo: `crunor's cottage`, `flower guys`, `accident`, `stable`.
  2. **Key 3899:** shovel into the minotaur caves and go far north, under the tower. It is in the dead tree north of the tower, which is booby-trapped (up to 200 HP of damage and poison fields).
  3. **Reach the tower:** from the spot south of the Kazordoon entrance, Levitate or use parcels to climb. Put one skull on each of the 4 sacrifice stones and step on the middle carving to teleport to the tower. The 4 strange carvings there send you back. You need 4 skulls every visit.
  4. **Grass:** inside the tower, cut the jungle grass along a set path (see the wiki). While it regrows, step on the SE switch plate: the big stone becomes stairs. Get everyone in before stepping on it.
  5. **Levers**, left to right: Right, Right, Left, Left, Right, Left.
  6. **Ghoul room:** flip the switch. A crate appears and the Ghoul pushes it. When it reaches the NW corner, a ladder appears; go up quickly.
  7. Open the door with **Key 3899**.
  8. **Fruit:** place fruit on the tables, left to right: melon, banana, cherry, apple, grapes, coconut. Flip the switch and go up the ladder.
  9. **Chess:** place the black and white knight chess pieces at the matching statues, pull the lever and go up.
  10. **Riddler, first visit:** `hi`, `test`, `yes`, then answer:
      - Seal of Knowledge: `goshnar`, `demonbunny`, `Tha'kull`. Say `yes` to continue.
      - Seal of the Mind: `breath`, `silence`, `old`. Say `yes` to continue.
      - Seal of Madness: `green`, `none`, then 1+1. Any number you give is wrong, and you are sent to Hellgate. Walk out to Ab'Dendriel; Key 3012 is not needed.
  11. **A Prisoner** in Mintwallin, 2 floors up in the west-side prison: `hi`, `math`, `yes`, `green` (only if asked), `yes`. He tells you your personal answer to 1+1, which differs per player. Do not say "mathemagics" early.
  12. **Riddler again:** give the same answers, with your personal number as the last. You are let into the treasure room.
  13. **Treasure room:** 4 chests and 2 rows of switchplates. Each plate you step on **destroys** one reward. Step on exactly 2 plates to keep the 2 rewards you want. The pattern (the letter is the reward destroyed) is:

      ```
      Row 1: K  W  T  T  T  K
      Row 2: E  E  E  K  W  W
      ```

      K = 10k gp, W = wand, T = 32 Talons, E = Phoenix Egg.
- **Rewards:**
  - You get 2 of 4: 10k gp, a wand, 32 Talons, Phoenix Egg.
  - For the wand, the **2005 wiki revision and Tibiantis say "Wooden Wand"**. The Dec 2006 wiki says Wand of Cosmic Energy; wand weapons are later. Use the Wooden Wand for 7.4.
- **Once per player:** yes.
- **Other rules:** the tower area is a protection zone with no regeneration. Stepping on all plates destroys all rewards. The lever, fruit and chess puzzles stay solved until the server save or until someone resets them. Skulls, grass and the ghoul are needed on every visit.
- **Sources:** https://tibia.fandom.com/index.php?oldid=73165 (spoiler, Dec 2006) ; https://tibia.fandom.com/index.php?oldid=73465 (infobox) ; https://tibia.fandom.com/index.php?oldid=14595 (first revision, 15 Aug 2005, reward "Wooden Wand") ; Paradox Tower page https://tibia.fandom.com/index.php?oldid=56289 ; https://tibia.fandom.com/wiki/The_Paradox_Tower_Quest/Spoiler ; Tibiantis list and tibiantis.life.
- **Confidence:** high for the steps and dialogue, medium for the exact wand item in 7.4.

## Venore, Darashia, Ankrahmun

### Black Knight Quest
- **Alt names:** Crown Set Quest.
- **Location:** "Villa Scapula" (Black Knight's Villa), a ruined house in the swamp north-west of Venore. Villa entrance ~(32827,31959,7). Key 5010 is in a dead tree west of the villa, ~(32813,31964,7) or (32800,31959,7).
- **Version:** TW-cur says implemented 7.1, so it existed in 7.4.
- **Requirements:** level 50 (Gate of Expertise); rope; Key 5010 if the basement door is locked. Free account. Solo is possible; no vocation check.
- **Steps (TW-pre8 2006):**
  1. Get Key 5010 from the dead tree west of the villa.
  2. Go down into the villa basement (bats and one slime). At the south end, unlock the door with Key 5010 and go down the stairs/ladder.
  3. Go down another level. Go east, then south, and drop down a hole.
  4. Go south and rope up one level.
  5. Go south to the room with skeletons and drop down either hole.
  6. On the floor with 4 beholders (bonelords), go north-east and go down (TW-cur: go east to the wall, then north to the stairs).
  7. Pass the level 50 Gate of Expertise. North of it are 1 skeleton, 2 beholders and 1 wyvern. The teleport to the north takes you up one floor.
  8. Circular Black Knight room, with fire fields and 2 scorpions + 2 beholders near the arrival point. Kill the Black Knight, who spawns in the south.
  9. Dead trees stand in the 4 corners. The two **southern** trees give the Crown Shield and the Crown Armor; the northern ones are empty. The south teleport returns you to the floor below.
- **Rewards:** Crown Armor and Crown Shield (TW-old 2005, TW-pre8, TW-cur all agree). **TI lists "nothing" and level 0.** This may mean Tibiantis emptied the trees or changed the quest. Unverified; decide your own design.
- **Once / rules:** Sources do not say. The trees are probably quest containers, once per character.
- **Sources:** https://tibia.fandom.com/index.php?oldid=70179 (spoiler, Dec 2006); https://tibia.fandom.com/index.php?oldid=70176; https://tibia.fandom.com/wiki/Black_Knight_Quest/Spoiler; https://tibiantis.info/library/quests
- **Confidence:** High for the route and rewards on real Tibia 7.x. Low for what Tibiantis actually does.

### Blood Herb Quest
- **Alt names:** Witchesbroom Quest.
- **Location:** Greenclaw Swamp, west of Venore, near Wyda's house. Rotworm-cave hole ~(32699,32018,7).
- **Version:** 6.1, so it existed in 7.4.
- **Requirements:** no level; free. Bring a machete, a shovel and a rope. Antidote is recommended.
- **Steps (TW-pre8):**
  1. Go west of Venore to the hole into the Venore rotworm cave (shovel on the stone pile) and go down.
  2. Go down again, rope up, and follow the cave north-east. Take the ladder up (not the north ramps, not the east hole).
  3. At Wyda's house: a coffin by the ladder holds Key 5000 (Wyda's door). You do not need it.
  4. Go up and walk the boards east around the house. Witches on the nearby hill can shoot fire fields at you.
  5. Go down the end ladder and cut the jungle grass (machete). There are a wasp and a skeleton.
  6. Shovel the stone pile and go down. There is a poison spider in the tunnel. Take the western ramp up.
  7. Kill the single Giant Spider. Open the dead tree by the water to get the **Blood Herb**.
  8. Optional: give the Blood Herb to NPC Wyda in exchange for her Witchesbroom.
- **Rewards:** Blood Herb, or Witchesbroom through the NPC trade.
- **Once:** The quest tree is presumably once per player.
- **Sources:** https://tibia.fandom.com/index.php?oldid=70614 ; https://tibia.fandom.com/wiki/Blood_Herb_Quest/Spoiler ; TI.
- **Confidence:** high.

### The Desert Dungeon Quest
- **Alt names:** Desert Quest, Vocation Quest, 10K Quest.
- **Location:** under the Jakundaf Desert, between Thais and Venore. The loose stone pile (entrance) is at ~(32649,32093,7).
- **Version:** 6.1, so it existed in 7.4.
- **Requirements:** 4 players, **one knight, one paladin, one druid and one sorcerer**, each level 20+ (level 20 Gate of Expertise). Free account. Each player brings a sacrifice item that is consumed:
  - knight: a Sword
  - paladin: a Crossbow
  - druid: an Apple (TW-cur says Red Apple)
  - sorcerer: a Spellbook
  
  One player must carry a shovel.
- **Steps (short path, TW-pre8):**
  1. Shovel the stone pile and go down about 5 floors to the spider floor. You cannot rope back up.
  2. Go north, then east, then south to the ladder up. Go up, then west and up again. Do **not** take the south hole with the warning sign.
  3. Follow the serpentine path and go up. Pass the slime spawn and do **not** fall into the west hole (orc warriors/berserkers below). Take the last ladder up.
  4. Go through the level 20 door into the vocation room. An exit teleport sits to the side, for groups that cannot finish.
  5. Each player puts their item on the basin behind their floor button and stands on the button:
     - paladin: north
     - druid: west
     - sorcerer: east
     - knight: south
     
     The buttons show as pressed only when the vocation and item are correct. If not, step off and back on.
  6. The paladin pulls the lever by his tile, and all 4 players are teleported to the reward room.
  7. Two chests: one holds 100 platinum coins, the other a green bag with Protection Amulet, Magic Light Wand, Ring of Healing and Ankh. Leave by the stairs north; you cannot come back in.
- **Long path (optional lore, TW-cur):**
  1. Give NPC Hagor a Roll to get Key 4022.
  2. Key 4022 opens a door with Key 4009 in a chest. Key 4009 opens the library.
  3. Read Netlios' "Dangers of Adventures" books.
  4. Pay NPC Adrenius 500 gp and pass his test to get Key 4023.
  5. Each vocation takes its own teleport and fights 2 monsters (knight: orc berserkers; paladin: minotaur archers; sorcerer: fire devils; druid: bears). Signs there name the sacrifice items.
- **Rewards:**
  - 7.x (TW-old 2005 / TW-pre8): 100 platinum coins + a green bag (Protection Amulet, Ring of Healing, Magic Light Wand, Ankh). Both chests are taken; there is no choice.
  - TW-cur uses a Golden Bag with 25 platinum coins per vocation and adds a Monk. Both changes are post-7.4.
- **Once:** Rewards once per character. The quest can be repeated to help others.
- **Sources:** https://tibia.fandom.com/index.php?oldid=67986 ; https://tibia.fandom.com/index.php?oldid=63223 ; https://tibia.fandom.com/wiki/The_Desert_Dungeon_Quest/Spoiler ; TI; TL.
- **Confidence:** high.

### Dragon Tower Quest
- **Location:** Shadowthorn (elf town in the swamps south-east of Venore), central tower.
- **Version:** 7.1, so it existed in 7.4.
- **Requirements:** none. Free account.
- **Steps (TW-pre8):**
  1. Reach Shadowthorn.
  2. Either take the west ladder up and walk the walkways west and south, then down the ladder to the tower; or take the east ladder down and follow the passage south-west, then up.
  3. Climb the tower past elves, elf scouts and elf arcanists (TW-cur floor counts: 3 scouts + 1 elf; 4 scouts + 2 arcanists; 2 dragons behind glass that cannot reach you; 6 scouts + 3 arcanists; 3 scouts + 2 arcanists).
  4. Two boxes near the top hold the rewards.
- **Rewards:**
  - TW-old (2005): 2 Small Sapphires, 30 Burst Arrows, 60 Poison Arrows, 100 gp.
  - TW-pre8: Bow instead of the 100 gp.
  - TW-cur adds Health Potion and Mana Potion (post-7.4). TI copies the modern list.
- **Once:** unknown (boxes).
- **Sources:** https://tibia.fandom.com/index.php?oldid=65460 ; https://tibia.fandom.com/index.php?oldid=65017 ; https://tibia.fandom.com/wiki/Dragon_Tower_Quest/Spoiler
- **Confidence:** medium on the exact rewards.

### Heaven Blossom Quest
- **Location:** Shadowthorn, underground (go down the ladder closest to the entrance).
- **Version / in 7.4:** No implemented version on the wiki, and the page was only created in 2014. TI and TL list it, which suggests it is in the CipSoft 7.7 data. **Uncertain for 7.4.**
- **Requirements:** none. Free account.
- **Steps (TW-cur 2014):**
  1. Enter Shadowthorn and take the nearest ladder down.
  2. Walk to the marked spot. Only elves are there, maybe a lured Elf Overseer.
  3. Open the barrel to get the Heaven Blossom.
- **Rewards:** Heaven Blossom.
- **Once:** unknown.
- **Sources:** https://tibia.fandom.com/wiki/Heaven_Blossom_Quest/Spoiler ; TI; TL.
- **Confidence:** low.

### Iron Helmet Quest
- **Alt names:** Muriel's Letter Quest.
- **Location:** Plains of Havoc, a dead body half-hidden by a tree just west of the cyclops/orc/minotaur camp, ~(32787,32232,7).
- **Version:** On TW-old (Oct 2005). No implemented field. TI lists it. Very likely in 7.4.
- **Requirements:** none. Free account.
- **Steps:** Walk to the body and open it.
- **Rewards:**
  - TW-old: Iron Helmet, Sudden Death rune, Leather Armor, Letter, Twigs.
  - TW-pre8: Iron Helmet, SD rune, Leather Armor, Letter, Worn Leather Boots. The Leather Armors, letters and boots are also lying loose around the tree.
  - TW-cur adds the book "Porgol's Strange Behaviour" and a Longsword.
- **Once:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=44102 ; https://tibia.fandom.com/index.php?oldid=38856 ; https://tibia.fandom.com/wiki/Iron_Helmet_Quest/Spoiler
- **Confidence:** medium.

### Isle of the Mists Quest
- **Alt names:** Druid Quest.
- **Location:** Isle of the Mists, south-east of the Plains of Havoc. You reach it through a magic forcefield in PoH near the orcs, ~(32831,32295,7).
- **Version:** No implemented field; the wiki page dates from Jul 2006. TI lists it. Probably in 7.4, not confirmed.
- **Requirements:** The legend implies a druid-only area. Neither spoiler states that the teleport checks vocation. Unknown. Free account.
- **Steps:**
  1. Enter the PoH teleport.
  2. On the ground floor of the isle building, open the box and the drawer. Fernfang may spawn upstairs.
- **Rewards:** TW-pre8: 3 Small Emeralds + a book. TW-cur: 2 Small Emeralds + a book.
- **Once:** unknown.
- **Sources:** https://tibia.fandom.com/index.php?oldid=43081 ; https://tibia.fandom.com/wiki/Isle_of_the_Mists_Quest/Spoiler
- **Confidence:** medium. The vocation restriction is unconfirmed.

### Orc Shaman Quest
- **Location:** Small orc outpost/cave in the swamp east of Venore's south gate. Shovel hole ~(33055,32030,7).
- **Version:** On TW-old (Aug 2005). No implemented field.
- **Requirements:** shovel, rope. Free account.
- **Steps:**
  1. Shovel the hole and go down.
  2. Go east and go down one more level.
  3. Kill the snakes, orcs, orc spearmen and 1 orc shaman.
  4. The quest box is in the south-east corner.
- **Rewards:** Magic Light Wand, Axe Ring, Blank Rune. The TW-old 2005 draft said "power ring, backpack", but the author was unsure; later revisions settled on the list above.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=24076 ; https://tibia.fandom.com/wiki/Orc_Shaman_Quest/Spoiler
- **Confidence:** high.

### The Outlaw Camp Quest
- **Alt names:** Bright Sword Quest.
- **Location:** Outlaw Camp (minotaur tower area). Tower ~(32615,32253,7).
- **Version:** 6.4, so it existed in 7.4.
- **Requirements:**
  - Level 45 (Gate of Expertise). Free account.
  - Rope, shovel, a **Power Ring** (consumed), and Levitate or 3 parcels.
  - A light **barrel**. TW-pre8 says to use the lighter, marshmallow-shaped one, fetched from under the PoH cyclops/minotaur camp.
  - Keys 3301, 3302, 3303 and 3304.
- **Steps (TW-pre8 / TW-cur):**
  1. Collect the keys from dead trees at the camp:
     - Key 3301 (copper) by the minotaur tower, next to a dead body, ~(32617,32251,7)
     - Key 3302 (silver) just north of the tower, ~(32612,32243,7)
     - Key 3303 (copper) at the south campsite, ~(32651,32245,7)
     
     (TW-pre8 lists 3301 and 3302 the other way round.)
  2. Enter the wild-warrior cave (hidden shovel hole behind a tree, ~(32633,32229,7)) and go north to the room with 4 ladders.
  3. Take the NW ladder down. Open the door with Key 3303 and flip the switch; this moves an oven. Go up, then down the south ladder, and slip behind the oven to a chest with Key 3304 (golden).
  4. Bring a barrel to the shovel hole near the water north of the camp (~(32603,32207,7)). Follow that cave to its end and leave the barrel in the NW corner of the small room.
  5. Climb the minotaur tower 2 floors to the "Point of No Return" sign and walk off the roof. You fall far underground.
  6. Go west, then north, past 2 Giant Spiders to a ledge. Levitate or use parcels to go down to the orc room (orc spearmen and berserkers).
  7. Left passage: put the Power Ring on the wooden surface and flip the switch; the ring is teleported away.
  8. Right passage: 1 orc shaman and orc warriors. Take the ladder UP. Rope up the barrel through the hole; do not fall in.
  9. Bring the barrel back and throw it down the ladder (skeletons, ghouls, 2 beholders). Drag it east through the **level 45 door** to the blocking wall and put it in the notch on the wall's south part.
  10. Leave. Fall through the pitfall by the dead tree near the tower (~(32617,32253,7)), go north through the doors for Key 3301 and then Key 3302, and take the ladder down to the room with the mill switch and fire fields. Flip the switch; the Power Ring becomes a fire field.
  11. Return past the level 45 door. The wall has opened. Kill 3 demon skeletons, open the door with Key 3304, and open the chest.
- **Rules:** The final switch works only **once per day**. With the wrong barrel or placement you must wait a day and bring another Power Ring. TW-cur says 2 Power Rings used on the first switch reset it.
- **Rewards:**
  - 7.x (TW-old 2005 / TW-pre8 / TW-cur): Bright Sword, Red Gem.
  - **TI lists "8k, 50 Power Bolts, Red Gem"** (TL agrees). This is a Tibiantis- or 7.7-data difference. Flag it.
- **Once:** yes (chest).
- **Sources:** https://tibia.fandom.com/index.php?oldid=66655 ; https://tibia.fandom.com/index.php?oldid=29950 ; https://tibia.fandom.com/wiki/The_Outlaw_Camp_Quest/Spoiler ; TI; TL.
- **Confidence:** high for the mechanics. Medium for the reward.

### Panpipe Quest
- **Alt names:** Fire Devil Quest.
- **Location:** Desert Dungeon (Jakundaf Desert). Key rock ~(32652,32108,7); dungeon entrance ~(32648,32094,7).
- **Version:** 6.1, so it existed in 7.4.
- **Requirements:** Key 4055, shovel, rope. Free account. You must know the way to the Desert Quest exit portal, because you cannot leave the way you came.
- **Steps (TW-pre8):**
  1. "Use" the hollow rock south of the dungeon entrance to get **Key 4055**.
  2. Shovel into the dungeon and go down 5 floors.
  3. Go west and south, then up.
  4. Go north-west past the Desert Dungeon Library, rope up, and rope up again.
  5. Go south and up one more level.
  6. Go south-east to the locked door (Key 4055). Kill 1 Fire Devil and open the quest box.
  7. Leave through the Desert Quest exit portal.
- **Rewards:** a bag with Panpipes, 2 Small Amethysts and a Power Ring.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=23951 ; https://tibia.fandom.com/wiki/Panpipe_Quest/Spoiler
- **Confidence:** high.

### Power Bolts Quest
- **Location:** Hole just south of the Plains of Havoc temple, ~(32815,32280,7).
- **Version:** No implemented field; wiki since 2006. TI lists it.
- **Requirements:** shovel and rope (TW-cur). Free account.
- **Steps:**
  1. Go down the hole and kill the Giant Spider.
  2. Search under the corpses: the body under the teleporter has the book, the northern body a brown bag (5 Power Bolts, 12 Burst Arrows), and a pile of bones the Two Handed Sword.
- **Rewards:**
  - TW-pre8: 5 Power Bolts, 12 Burst Arrows, Two Handed Sword, book.
  - TW-cur adds a daily respawn of 6 Throwing Stars and a Talon, which are not quest items. The book is "The Dreammaster".
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=43300 ; https://tibia.fandom.com/wiki/Power_Bolts_Quest/Spoiler
- **Confidence:** medium. The legend mentions a Nightmare Knight (7.9 lore), so the book's text may be later.

### Silver Brooch Quest
- **Alt names:** Mummy Quest.
- **Location:** Greenclaw Swamp cave, reached from the west (Dwarf Bridge) through a partly hidden pitfall, ~(32700,31992,7).
- **Version:** No implemented field; wiki since 2006. TI lists it.
- **Requirements:** shovel, rope, **pick**, and a machete depending on the route. Free account.
- **Steps:**
  1. Enter the cave and go east (poison spiders, rotworms). Go down the hole.
  2. Go through the short south passage and down the hole.
  3. Go east and south; kill 3 beholders.
  4. Use the pick on the marked spot and go down.
  5. Kill up to 5 mummies and open the north coffin.
- **Rewards:** Silver Brooch, 2 Small Rubies, 3 Small Diamonds.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=73566 ; https://tibia.fandom.com/wiki/Silver_Brooch_Quest/Spoiler
- **Confidence:** high.

### Skull of Ratha Quest (includes Wolf Tooth Chain)
- **Location:** Amazon Camp north of Venore; "Witch Hill" ~(32846,31920,7).
- **Version:** 7.24, so it existed in 7.4.
- **Requirements:** none. Free account. Destroy Field runes are useful against the witches' fire fields.
- **Steps:**
  1. On Witch Hill, kill 2 witches, 3 valkyries and 1-2 lions.
  2. Open the two boxes:
     - bag 1: White Pearl + Skull of Ratha
     - bag 2: **Wolf Tooth Chain** + Dwarven Ring
  3. East of the hill, go down into the building's basement. In the NE corner, kill 1-2 witches and 3-5 valkyries and open the chest: a bag with 100 gp, a Crystal Necklace and 2 Black Pearls.
- **Rewards:** as above; you take all three containers. The Skull of Ratha later sells to the Explorer Society (a 7.6+ feature) for 250 gp.
- **Wolf Tooth Chain:** In 7.x it is also dropped by Witch, Orc Rider, Cyclops and Gargoyle (TW-pre8 item page). The item was implemented in 5.0. It is decoration only.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=61958 ; https://tibia.fandom.com/index.php?oldid=64839 (Wolf Tooth Chain); https://tibia.fandom.com/wiki/Skull_of_Ratha_Quest/Spoiler
- **Confidence:** high.

### Time Ring Quest
- **Alt names:** Shadowthorn Quest.
- **Location:** Shadowthorn underground; hole ~(33060,32182,7).
- **Version:** 7.1, so it existed in 7.4.
- **Requirements:** machete. Free account.
- **Steps:**
  1. Enter the hole in Shadowthorn and head west down the ramp.
  2. Fight elf arcanists, elf scouts, 1-2 ghouls and 1-2 demon skeletons. Dharalion is a rare spawn. More elves shoot from behind a fence to the west.
  3. The 3 quest boxes are at the north end of the room.
- **Rewards:** Time Ring, Elven Amulet, Crystal Ball.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=71065 ; https://tibia.fandom.com/wiki/Time_Ring_Quest/Spoiler
- **Confidence:** high.

### Voodoo Doll Quest
- **Location:** Greenclaw Swamp, a hole on the north side, ~(32737,31953,7).
- **Version:** 7.24, so it existed in 7.4.
- **Requirements:** none. Free account. Antidote is recommended.
- **Steps:**
  1. Go down the hole, then west and down one more level.
  2. Kill 3 witches (up to 6 if overspawned).
  3. The quest boxes are against the east wall of the large east room.
- **Rewards:** Voodoo Doll, Magic Light Wand.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=38903 ; https://tibia.fandom.com/wiki/Voodoo_Doll_Quest/Spoiler
- **Confidence:** high.

### Medusa Shield Quest
- **Alt names:** Star Room Quest, Necromancer Quest.
- **Location:** Drefia, west of Darashia. Main dungeon entrance ~(32996,32413,7).
- **Version:** 7.3, so it existed in 7.4.
- **Requirements:** level 60 (Gate of Expertise); rope (TW-cur also needs a shovel). Premium. The Invisible spell and antidote are recommended.
- **Steps (TW-old Dec 2005):**
  1. Enter the Drefia dungeon (Invisible helps).
  2. Go south-east and down, then down again.
  3. Go north to another hole and enter it.
  4. Go east through the **level 60 door**.
  5. Go up the hole into the room with necromancers, priestesses and their summons, a vampire, and demon skeletons (Necropharus is a rare spawn).
  6. The coffin in the east part holds the rewards.
- **Rewards:**
  - TW (2005 to now): Medusa Shield, Skull Staff, Blue Robe, all in one coffin.
  - **TI/TL list "5k, Blue Spell Wand, 2x BP UH, 2x BP HMM, BP Explosion".** This is a Tibiantis-specific or 7.7-data difference. Flag it.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=61332 ; https://tibia.fandom.com/index.php?oldid=66825 ; https://tibia.fandom.com/wiki/Medusa_Shield_Quest/Spoiler ; TI; TL.
- **Confidence:** high for the route. Medium for the rewards.

### Plate Armor Quest
- **Alt names:** Ghost Ship (Ghostship) Quest.
- **Location:** The Ghost Ship. You are randomly hijacked there while sailing Venore to Darashia with Captain Fearless.
- **Version:** 6.61-6.97, so it existed in 7.4.
- **Requirements:** premium (Darashia route); boat fare. No level.
- **Steps (TW-pre8 2005):**
  1. Sail Venore to Darashia until you are hijacked (the wiki claims this is more likely at night; unconfirmed).
  2. You arrive at the steering wheel, which is safe. The main deck has skeletons and ghouls, and 1 ghost guards the teleport to Darashia.
  3. Go down the ladder; you land on a fire field. Kill 2 vampires, 1 demon skeleton and 1 ghost.
  4. Use the head of the coffin on the far (east) wall to get the Plate Armor.
  5. Exit through the magic forcefield upstairs to the Darashia boat.
- **Rewards:** Plate Armor.
- **Once:** assumed.
- **Implementation note:** You need a random-hijack travel script on the Venore to Darashia boat.
- **Sources:** https://tibia.fandom.com/index.php?oldid=24797 ; https://tibia.fandom.com/wiki/Plate_Armor_Quest/Spoiler
- **Confidence:** high.

### Stealth Ring Quest
- **Alt names:** Minotaur Pyramid Quest.
- **Location:** Minotaur Pyramid (the wiki page redirects to "Dark Pyramid"), north-east of Darashia, ~(33312,32282,7).
- **Version:** 6.61-6.97, so it existed in 7.4.
- **Requirements:** premium. No level.
- **Steps:**
  1. Ground floor has minotaurs. Go down: minotaurs and 1-2 minotaur guards.
  2. Go south-west and down: guards and archers. Go east/north-east and down: all minotaur types, about 4 mages.
  3. Go north and down: 1 mummy.
  4. SE coffin holds the Stealth Ring; NE coffin holds the Protection Amulet.
- **Rewards:** Stealth Ring, Protection Amulet.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=36335 ; https://tibia.fandom.com/wiki/Stealth_Ring_Quest/Spoiler
- **Confidence:** high.

### The Ancient Tombs Quest
- **Alt names:** Helmet of the Ancients Quest, Pharaohs Quest.
- **Location:** 8 hidden tombs in the Ankrahmun desert. Current-map entrances (dig with a shovel, sometimes more than once):

  | Tomb | Pharaoh | Entrance |
  |---|---|---|
  | Peninsula | Omruc | ~(33027,32870) |
  | Stone | Thalas | ~(33282,32743) |
  | Mountain | Dipthrah | ~(33132,32568) |
  | Shadow | Mahrdis | ~(33255,32833) |
  | Ancient Ruins | Vashresamun | ~(33207,32592) |
  | Tarpit | Morguthis | ~(33232,32704) |
  | Oasis | Rahemos | ~(33132,32641) |
  | Ankrahmun Library | Ashmunrah | ~(33159,32836) |

- **Version:** 7.4. It is part of the 7.4 update itself.
- **Requirements:**
  - Level 75 (Gates of Expertise in each tomb; TW-old 2005 said 80). Premium.
  - Scarab Coins: one per tomb, placed on the coal basin while standing on the Mystic Flame.
  - Shovel and rope. A Dwarven Ring is useful for Dipthrah.
  - Team strongly advised.
- **Steps:**
  1. In each of the 7 tombs, go down to the Mystic Flame/coal basin, sacrifice a Scarab Coin, pass the tomb's puzzle, and kill the pharaoh:
     - Vashresamun: play the instruments in order.
     - Rahemos: find the carrot under 1 of 3 hats (200 hp per miss), then walls you can pass and a lava path.
     - Mahrdis: purple fire floor (300 hp per step on fire).
     - Thalas: simultaneous switches, get poisoned, then say "hi" to the Cobra NPC.
     - Dipthrah: switches, then doors in the word order from the book.
     - Omruc: invisible-wall maze.
     - Morguthis: step in every blue flame of the Deathslicer maze.
  2. Each pharaoh drops a pass item: Crystal Arrow, Cobrafang Dagger, Ornamented Ankh, Burning Heart, Blue Note, Sword Hilt, Ancient Rune. Holding it, the teleport in the pharaoh room leads to a sarcophagus with that tomb's helmet piece. Without it, the teleport goes back to the entrance.
  3. Every team member needs their own kill of each pharaoh.
  4. Kill Ashmunrah last (Library Tomb). Set all switches to the right, then put all 7 pieces on the stone table to receive the helmet.
- **Rewards:**
  - TW-pre8: Full Helmet of the Ancients. Put a Small Ruby in it to enchant it for 30 minutes.
  - TW-cur: Helmet of the Ancients.
  - TI shows "to be discovered"; TL has no entry.
- **Once:** Each helmet piece once per character.
- **Sources:** https://tibia.fandom.com/index.php?oldid=60368 ; https://tibia.fandom.com/index.php?oldid=34030 ; https://tibia.fandom.com/wiki/The_Ancient_Tombs_Quest/Spoiler ; TI.
- **Confidence:**
  - High that the quest existed in 7.4.
  - Medium on puzzle details. The 2006 spoiler was incomplete; the tomb details come from TW-cur and may include later changes.
  - The TW-cur monster lists (Deathslicer, Shredderthrower, etc.) are old; check each creature exists in your 7.4 monster set.

### The Djinn War - Efreet Faction
- **Alt names:** Green Djinn Quest.
- **Location:**
  - Mal'ouquah (Green Djinn fortress), up the ramp west of the oasis, ~(33101,32657,7)
  - Carlin (sheriff Shauna)
  - Thais prison, ~(32320,32276,7)
  - Ashta'daramai (Blue fortress) secret entrance, ~(33177,32558,7)
  - Ulderek's Rock / Orc Fortress: Orc King at ~(32982,31736,9)
- **Version:** 7.4.
- **Requirements:**
  - Premium.
  - Level 30 (fortress Door of Expertise) and level 40 (Orc King chamber door). TW-pre8 writes "30/40".
  - You must not have sided with the Marid.
- **Steps (TW-pre8 with transcripts):**
  1. In Ankrahmun, NPC Melchior: say "word of greeting". He answers **DJANNI'HAH**.
  2. At Mal'ouquah, NPC Ubaid: say DJANNI'HAH, then "passage", "no", "yes", "yes". You pledge to Malor.
  3. NPC Baa'leal: DJANNI'HAH, "mission", "yes". He sends you to find a supply thief in Carlin.
  4. Carlin, NPC Shauna: ask "water pipe", then "prisoner". She points you to Thais.
  5. Thais prison, NPC Partos: ask "ankrahmun", then "supplies".
  6. Baa'leal: "mission", "yes", "Partos". Reward: 600 gp. He sends you to Alesar.
  7. NPC Alesar: "mission", "yes". Steal a **Tear of Daraman** from the Marid: enter Ashta'daramai by the secret south ramp between Ankrahmun and Darashia, go to the 4th floor (blue djinns, marids, fire elementals), and use the **northern** of the two fountains. The Tear appears.
  8. Give the Tear to Alesar: "mission", "yes".
  9. NPC Malor: "mission", "yes". Get Fa'hradin's lamp from the Orc King.
  10. Orc King: the first "hi" summons orc guards. On the second "hi", ask "lamp", then "malor". He gives you the lamp.
  11. Sneak to the top of Ashta'daramai and use the lamp on the lamp next to Gabel's bed.
  12. Malor: "mission", "yes". You now have permission to trade with the Efreet.
- **Rewards:** 600 gp and Efreet trade rights (7.4 era). TW-pre8 and TW-cur also list a Gemmed Lamp, and TW-cur adds hunting tasks and Yalahar, which are later.
- **Once / rules:** Once. You can never switch sides afterwards.
- **Sources:** https://tibia.fandom.com/index.php?oldid=38846 ; https://tibia.fandom.com/index.php?oldid=38847 ; https://tibia.fandom.com/wiki/The_Djinn_War_-_Efreet_Faction/Spoiler ; TL ("Djinn Quest", lvl 40, premium).
- **Confidence:** high.

### The Djinn War - Marid Faction
- **Alt names:** Blue Djinn Quest.
- **Location:**
  - Ashta'daramai, reached by the ramp west of the Giant Spider hill north of Ankrahmun, ~(33120,32578,7). Gabel is on floor 1 of the fortress.
  - Kazordoon (NPC Maryza)
  - Mal'ouquah back entrance
  - Ulderek's Rock
- **Version:** 7.4.
- **Requirements:**
  - Premium.
  - Level 30 (fortress door), level 40 (Orc King door).
  - A Cookbook (150 gp from Maryza in Kazordoon) and a Cheese.
  - You must not have sided with the Efreet.
- **Steps (TW-pre8 with transcripts):**
  1. NPC Melchior gives the greeting word DJANNI'HAH.
  2. NPC Umar: DJANNI'HAH, "passage", "yes", "yes".
  3. NPC Bo'ques: "mission", "yes". He wants a dwarven cookbook: buy it from Maryza, then give it to him ("cookbook", "yes"). Reward: 3 Small Sapphires.
  4. NPC Fa'hradin (balcony): "mission". Password **PIEDPIPER**; get the spy report from Mal'ouquah.
  5. Take the back route of Mal'ouquah, north around the fortress (lions, hyaenas, cobras, scorpions, 1 wyvern). Inside, kill hyaenas and green djinns, then go down.
  6. Rat NPC Rata'mari: say PIEDPIPER, then "spy report". Bring him the cheese ("yes") to receive the Spy Report.
  7. Fa'hradin: "mission", "yes". He sends you to Gabel.
  8. NPC Gabel: "mission", "yes". Get the lamp from the Orc King (level 40 door): "hi" twice, "lamp", "malor".
  9. Go to the top of Mal'ouquah (green djinns, efreets, gargoyles) and use the lamp on the lamp by Malor's bed.
  10. Gabel: "mission". You now have trade rights with the Marid.
- **Rewards:** 3 Small Sapphires and Marid trade rights. TW-pre8 and TW-cur also list a Gemmed Lamp.
- **Once / rules:** Once. Choosing a side is permanent.
- **Sources:** https://tibia.fandom.com/index.php?oldid=72061 ; https://tibia.fandom.com/index.php?oldid=71556 ; https://tibia.fandom.com/wiki/The_Djinn_War_-_Marid_Faction/Spoiler ; TL.
- **Confidence:** high.

### Serpentine Tower Quest / White Pearl Quest
- **Alt names:** Ankrahmun Sorcerer Guild Quest, Ankrahmun White Pearl Quest, Ankrahmun Pyramid Quest. TibiaWiki merged the two pages in 2021; TI still lists "Serpentine Tower Quest" (reward "Unknown") and "White Pearl Quest" separately.
- **Location:** Serpentine Tower (the Sorcerer guild pyramid), south-east of the Ankrahmun depot, ~(33147,32866,7).
- **Version:** TW-cur says 7.3. It is on the wiki since Feb 2006. In 7.4.
- **Requirements:** premium; a **Pot**. No level.
- **Steps:**
  1. Climb to the top of the tower, then go down to the floor below the library (TW-cur says the ground floor within the tower).
  2. In the north room, put a pot on the open fire. This activates the magic forcefield on the east side.
  3. Go through it and take the White Pearl from the chest.
  4. "Continuation" (no known reward):
     - Using the wall lamp in the pearl room releases a Fire Elemental downstairs.
     - The switch in its cage removes the magic walls holding a Green Djinn.
     - The Green Djinn's switch does nothing known. A vampire and a behemoth also sit caged.
- **Rewards:** White Pearl.
- **Once:** assumed.
- **Sources:** https://tibia.fandom.com/index.php?oldid=36597 ; https://tibia.fandom.com/index.php?oldid=62614 ; https://tibia.fandom.com/wiki/Serpentine_Tower_Quest/Spoiler ; TI.
- **Confidence:** Medium. Implementing the pearl part is enough; the cages are an unsolved puzzle.

## Edron, Postman, and excluded (post-7.4) quests

### Annihilator Quest
- **Alt names:** Anni, "Annihilator" (2005 wiki title)
- **Location:** Edron, Hero Cave, north of Edron past the mountain pass. Cave entrance x 33164, y 31638, z 7. The current spoiler links an area in the quest at x 33211, y 31672, z 13 (the exact spot is not stated).
- **Version / in 7.4:** implemented 7.24 (15 Mar 2004), so it was in 7.4. The TibiaWiki pages were first written in June 2005.
- **Requirements:** level 100 for all four players. Exactly 4 players must stand on 4 tiles. Premium (Edron). Any vocation. Current wiki: all four must not have done the quest before, and there is a level-100 door ("Gate of Expertise") at the quest entrance, which is where the exit teleport drops you.
- **Steps (7.x wiki):**
  1. Enter the Hero Cave (Hunters outside). Go down through 3 floors of Wild Warriors, Demon Skeletons and Priestesses. Floor 4 has 3 Dragons. Floor 5 has Monks and a Hero.
  2. Floor 6: take the first corridor (Demon Skeletons, Wild Warriors, Priestesses, Monks, Minotaur Guards). At the bottom go right. Continue down the passage opposite the Fire Elemental room (Hunters etc.). A door at the end leads to the teleport room.
  3. The four players line up on the 4 marked tiles and the front player pulls the lever. All four are teleported to a room with 6 Demons: 2 north, 2 south, and 2 straight ahead blocking the door.
  4. Kill the 2 blocking demons, go through the door (east) to the reward room, and take ONE reward.
  5. Take the portal back to the quest entrance.
  - Current wiki only (later mechanics): the demons are "Angry Demons", and if players are still in the room 10 minutes after the lever pull they are moved to the reward room.
- **Rewards:** choose one of 4 chests.
  - 2005 wiki: Magic (Long) Sword, Demon Armor, Stonecutter's Axe, Present Box with a Teddy Bear (the bear could be traded in Venore for a Thunder Hammer).
  - 2006 wiki: same items, with the bear called "Annihilation Bear" (tradeable for a Thunder Hammer or a Golden Helmet).
  - Current wiki adds the Demon outfit and the "Annihilator" achievement. Both are post-7.4, so exclude them.
  - Tibiantis: "One of: Demon Armor, Magic Sword, Stonecutter Axe, or a Present Box".
- **Once / rules:** "You can only enter this door once, so choose your reward wisely" (2005 and 2006 wiki). One reward per character.
- **Sources:** https://tibia.fandom.com/wiki/The_Annihilator_Quest/Spoiler ; 2005 revisions https://tibia.fandom.com/index.php?oldid=10342 and https://tibia.fandom.com/index.php?oldid=10419 ; pre8 revisions https://tibia.fandom.com/index.php?oldid=55815 and https://tibia.fandom.com/index.php?oldid=73171 ; https://tibiantis.info/library/quests ; https://tibiantis.life/
- **Confidence:** high for the mechanics. The name of the 4th reward (teddy/present) differs between sources.
- **Our server (2026-09-24):** lever 33226,31671,13 (aid 51011), squares 33222-33225,31671,13, level-100 gate 33214,31671,13; demon room arrival 33219-33222,31659,13, 6 demons (2 N, 2 S, 2 by the door 33225,31659,13); chests 33227/33229/33231/33233,31656,13 = uid 51012-51015 (one per character, storage 51012); 4th = present with the annihilation bear (item 2326); portal 33236,31659,13 -> 33210,31673,13. Lever: once per server save (decided with the user); wrong team: "Sorry, not possible.".

### Behemoth Quest
- **Alt names:** Guardian Halberd Quest, Cyclopolis Quest
- **Location:** Edron, Cyclopolis (north of Edron). Entrance x 33250, y 31698, z 7. Behemoth-floor platform about x 33296, y 31689, z 13.
- **Version / in 7.4:** 7.2 (Dec 2003) per the wiki, which marks this "confirmation needed". It was in 7.4.
- **Requirements:** level door. The current wiki's history field says the level was changed from 60 to 80 "in late 2004 or in the beginning of 2005", and the Oct 2005 wiki still said 60. Tibiantis uses 60. There is also a level-30 door partway down (pre8 spoiler). Premium. Any vocation. Players: any number, and a team or hired high-level players is advised. Items: Destroy Field rune(s).
- **Steps (pre8 wiki):**
  1. Enter Cyclopolis. Go down 4 floors through Cyclopes, Dwarf Soldiers/Guards and Fire Elementals. On floor -4 pass the **level-30 Door of Expertise**.
  2. Floor -5 has 3 Dragons, 3 Fire Elementals and 1 Dragon Lord. Go down into the large multi-level cavern.
  3. Lever: go to the SE corner of the cavern (not down to the behemoth floor) and go up one level. Kill the Dragon Lord. In the small circular room lined with fire fields, use **Destroy Field** to reveal a **lever** and pull it. The current wiki says to push the lever to the right, which moves the large rocks that block the route.
  4. Go back and down 2 levels (or levitate) to the Behemoth floor (Cyclopes, Dwarf Soldiers, 4-9 Behemoths). Go north and up the stairs.
  5. On the landing, pass the **level door** (60 in 2004, 80 later). The room at the top has 4 Behemoths, a Priestess and 2 Dragons. The quest boxes are at the north end.
- **Rewards:**
  - Wiki (2005, pre8 and current, unchanged): Demon Shield, Golden Armor, Guardian Halberd, Platinum Amulet, Life Ring, Crystal Ring, 3 Small Diamonds, 4 Small Sapphires. These are separate boxes and none of the sources says you choose one.
  - Tibiantis: 30k, Life Ring, 5 Small Diamonds, 5 Small Sapphires, 5 Small Rubies, 100 Power Bolts.
  - These conflict. Tibiantis may reflect its own (leaked 7.7 map) chest contents.
- **Once:** yes (quest chests). How many boxes one player may open: unknown.
- **Sources:** https://tibia.fandom.com/wiki/Behemoth_Quest/Spoiler ; https://tibia.fandom.com/index.php?oldid=21249 (2005, lvl 60) ; https://tibia.fandom.com/index.php?oldid=57509 (pre8 spoiler) ; https://tibia.fandom.com/index.php?oldid=70206 ; https://tibiantis.info/library/quests ; https://tibiantis.life/
- **Confidence:** medium. The route is solid, but the level (60 vs 80) and the rewards conflict. For a Dec-2004 7.4 server, level 60 matches both Tibiantis and the 2005 wiki.
- **Our server (2026-09-24):** level-60 gate 33297,31670,14 (aid 1060; the map said 80 - decided with the user; tibiaot74 has 60 too). Lever 33293,31718,12 (aid 51021, placed under the fire field and the dead wolf where tibiaot74 has it) removes / puts back the stones 1304 at 33295-33299,31677,15 on the Behemoth floor - the only walking way to the room and out of it. Chests at 33294/33295/33297/33298,31658,13: uid 51023 demon shield, 2466 golden armor, 2427 guardian halberd, 51022 bag (platinum amulet, life ring, crystal ring, 3 small diamonds, 4 small sapphires) - the wiki's list split as tibiaot74 does; each once per character (decided with the user).

### Vampire Shield Quest
- **Alt names:** Warlock Room Quest, Dragon Lance Quest, Edron Warlock Quest
- **Location:** Edron, Hero Cave. The final room is the "Temple of Xayepocax" (current name). Cave entrance x 33164, y 31638, z 7.
- **Version / in 7.4:** 6.4, so yes.
- **Requirements:** level 70 (Gate of Expertise before the chests). Premium. Any vocation. Solo or team.
- **Steps (pre8 wiki):**
  1. Hero Cave entrance (3 Hunters), then down the hole. Floors of Wild Warriors, Demon Skeletons, Priestesses and Ghouls.
  2. Go down the next hole, then north to another hole (Beholder, Monks). Go east and north to the next hole. The 3-Dragon room has its hole in the middle. Next floor: 2 Monks and a Hero.
  3. On the main floor go south to the end, then east. At the crossroads (Minotaur Guards/Archers/Mages) take the south path and go down the stairs.
  4. The room has 2 Heroes, 2 Priestesses, 2 Witches, an Orc Shaman, a Monk, a Hunter and a Warlock. Kill them, then go to the back of the room.
  5. Pass the **level-70 door**. The chests hold the Vampire Shield and the Dragon Lance.
  6. A quest box **outside** the lvl-70 door holds the Strange Symbol, Black Pearl and Mysterious Fetish.
- **Rewards:**
  - 2005 wiki: Vampire Shield, Dragon Lance.
  - Pre8 and current wiki add the outside box (Strange Symbol, Black Pearl, Mysterious Fetish).
  - Tibiantis: Ice Rapier, 2x BP SD. This conflicts with the wiki.
  - The Vampire Shield and Dragon Lance are two separate chests, and no source says you choose one.
- **Once:** yes (chests).
- **Sources:** https://tibia.fandom.com/wiki/Vampire_Shield_Quest/Spoiler ; https://tibia.fandom.com/index.php?oldid=42285 (pre8 spoiler) ; https://tibia.fandom.com/index.php?oldid=38798 ; https://tibiantis.info/library/quests
- **Confidence:** medium. The route and door are solid, but the reward set conflicts with Tibiantis.
- **Our server (2026-09-24):** level-70 gates 33190/33195,31684,14 into one room; chests 33189,31688,14 = uid 1017 dragon lance, 33195,31688,14 = uid 1016 vampire shield (real-map table; which is which: tibiaot74). The box outside the gate was missing: placed at 33188,31682,14, uid 1032 (strange symbol, black pearl, mysterious fetish). Way out needs a rope.

### Demon Helmet Quest
- **Alt names:** Demon Quest
- **Location:** Edron, Hero Cave → "Demon Hell". Entrance x 33164, y 31638, z 7. The current spoiler marks points at x 33191, y 31629, z 13 and x 33211, y 31630, z 13 (portal/hole area).
- **Version / in 7.4:** 6.4, so yes.
- **Requirements:** level 100 (Gate of Expertise). Premium. Any vocation. A large team is advised: at least 9 demons in total (5 on the way, 4 in the room) plus banshees. The current wiki also requires **Key 6010** (the golden key from the Parchment Room Quest) to open the door after the level-100 gate. The 2006 key page calls Key 6010 the "Demon key", but the pre8 spoiler does not mention the key, so this is unconfirmed for 7.4.
- **Steps (pre8 wiki):**
  1. Go down through the Hero Cave to the **level-100 gate** near the single-demon spawn. (Current wiki: then open the door with **Key 6010**.)
  2. Kill the Fire Elementals and follow the only passage (lots of fire) to a portal.
  3. Through the portal: 1 Demon. Kill it and go down the hole (2 floors).
  4. This cave has 4 Demons and Fire Elementals. Clear it heading east to the portal into the quest room.
  5. The quest room is directly below, with 4 Demons and many Banshees. A **switch on the east side** must be pulled to activate the exit portal; pull it first so people can escape. The reward boxes are on the west side.
  6. Leave through the portal. Watch for demons that have respawned on the way out.
- **Rewards:** Demon Helmet, Demon Shield, Steel Boots (2005, pre8 and current). Current wiki adds the Demon outfit addon, which is post-7.4. Tibiantis: "to be discovered". Choose-one: not stated (appears to be separate boxes).
- **Once:** yes (chests).
- **Sources:** https://tibia.fandom.com/wiki/Demon_Helmet_Quest/Spoiler ; https://tibia.fandom.com/index.php?oldid=57772 (pre8 spoiler) ; https://tibia.fandom.com/index.php?oldid=70429 ; Key 6010 2006 rev https://tibia.fandom.com/index.php?oldid=38655 ; https://tibiantis.info/library/quests
- **Confidence:** medium-high. The Key 6010 gating is not in 7.x-era text.
- **Our server (2026-09-24):** Gate of the Lost Souls: switch tiles 33190/33191,31629,13 (aid 50665), wall 33210-33212,31630,13, open while both are held. Door 33211,31634,13 = key 6010 (Parchment Room). Quest-room switch 33330,31591,15 (aid 50666) removes the stone 33314,31592,15 and opens the portal 33316,31591,15 -> 33328,31592,14. Route: level-100 gate 33211,31638,13 -> ... -> portal 33278,31592,11 -> hole 33293,31592,12 (two floors) -> portal 33324,31592,14 -> room.

### Parchment Room Quest
- **Alt names:** —
- **Location:** Edron, Hero Cave (entrance x 33164, y 31638, z 7).
- **Version / in 7.4:** 7.2, so yes.
- **Requirements:** no level. Premium. Pick and rope. Recommended level 120 (current). Any vocation.
- **Steps (pre8 stub + current wiki):**
  1. In the Hero Cave follow the route and use a **pick** to open a hole.
  2. Go down and head west to a gravestone ("De.th to those who disturb ..e slumber of .ath..") and a teleporter into the Parchment Room (1 Demon).
  3. Kill the demon, then go to the coffin in the middle. Pushing/using the **yellow parchment** ("Buried Forever" book) spawns **4 Demons** around you.
  4. Open the coffin to get the reward. You can kill the demons or grab the reward and run.
- **Rewards:** Brown Bag with Key 6010 (golden "Demon key"), Bone, Stealth Ring, 2 Talons, Skull. The 2005 wiki lists Stealth Ring, 2 Talons, Bone and Skull. Tibiantis lists the same.
- **Once:** yes.
- **Sources:** https://tibia.fandom.com/wiki/Parchment_Room_Quest/Spoiler ; https://tibia.fandom.com/index.php?oldid=66537 ; https://tibia.fandom.com/index.php?oldid=51239 ; https://tibiantis.info/library/quests
- **Confidence:** high. The detailed steps come from the current wiki, while the 7.x text is a stub that agrees with it.
- **Our server (2026-09-24):** pick spot 33094,31626,13 (rope spot below), gravestone 33071,31619,14, teleporter 33070,31620,14 -> 33070,31624,15; coffin 33063,31624,15 uid 10057 under the seal (aid 51010; 4 demons at 33060/33066,31623/31627,15; back after 60 s). Way out: stairs up to 33054,31618,13, sewer grate 33072,31622,13 down, rope up at the pick hole.

### Ring Quest
- **Alt names:** —
- **Location:** Edron, Hero Cave (x 33164, y 31638, z 7 entrance).
- **Version / in 7.4:** 7.1 per the current wiki, and Tibiantis lists it, so it was very likely in 7.4. The wiki pages were only created in 2008.
- **Requirements:** no level (recommended 60). Premium. Rope.
- **Steps (current wiki):** follow the image route inside the Hero Cave. The text only says "Follow the route below"; there are no written steps. On the way you meet Hunters, Wild Warriors, Demon Skeletons, Priestess, Stalkers, Dragons, Orc Shaman, Witch, Dark Apprentice/Magician, Minotaur Mage, Monk and Hero. GFB/area runes are advised at one point. Use the chests, then go back the same way. The exact route is unknown in text form.
- **Rewards:** Time Ring, Sword Ring (wiki and Tibiantis).
- **Once:** yes (chests).
- **Sources:** https://tibia.fandom.com/wiki/Ring_Quest/Spoiler ; https://tibia.fandom.com/wiki/Ring_Quest ; https://tibiantis.info/library/quests
- **Confidence:** medium.
- **Our server (2026-09-24):** both chests were missing: placed at 33131/33134,31624,15 (tibiaot74's spots, the empty gaps in the room), uid 2169 time ring, 2207 sword ring. No level; the way out needs a rope.

### Wedding Ring Quest (Edron Hero Cave)
- **Alt names:** —. In 2006 the wiki page "Wedding Ring Quest" redirected to the Kazordoon **Longsword Quest**, which also gives a Wedding Ring. Don't confuse the two.
- **Location:** Edron, Hero Cave (entrance x 33164, y 31638, z 7).
- **Version / in 7.4:** the current wiki says 6.4, but this Hero Cave page was only created in 2010. Tibiantis lists "Wedding Ring Quest, Edron: Wedding Ring, Dragon Necklace", which supports it being in the 7.x map.
- **Requirements:** no level (recommended 70+). Premium.
- **Steps (current wiki):** follow the image route. On "screen 8" you face 3 Heroes and a Dark Apprentice. Use the chests. There is no text route beyond that, so the details are unknown.
- **Rewards:** Wedding Ring, Dragon Necklace.
- **Once:** yes.
- **Sources:** https://tibia.fandom.com/wiki/Wedding_Ring_Quest/Spoiler ; https://tibia.fandom.com/index.php?oldid=73682 (2006 redirect) ; https://tibiantis.info/library/quests
- **Confidence:** medium-low.
- **Our server (2026-09-24):** both chests were missing: placed at 33158,31621-31622,15 (tibiaot74's spots), uid 2121 wedding ring, 2201 dragon necklace. No level; rope out.

### Double Hero Quest
- **Alt names:** Hero Quest, Red Gem Quest
- **Location:** Edron, Hero Cave.
- **Version / in 7.4:** 6.4, so yes.
- **Requirements:** no level (recommended 70). Premium. Rope.
- **Steps (pre8 wiki):**
  1. Hero Cave entrance (Hunters, Wild Warriors), then down.
  2. Next hole: Demon Skeletons, Wild Warriors, a Priestess, Beholders. Go down the stairs.
  3. Monks, Demon Skeletons, Wild Warriors. Go down the stairs.
  4. Kill 3 Dragons and enter the hole.
  5. 1 Hero and 2-3 Monks, then down. 2-3 Priestesses and 2 Monks.
  6. Go south slowly. The room holds 2 Heroes, 1 Priestess, 2 Demon Skeletons and 1 Orc Shaman. Two chests at the south of the room: open both.
- **Rewards:** Club Ring and Red Gem (both).
- **Once:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=59244 ; https://tibia.fandom.com/index.php?oldid=32239 ; https://tibia.fandom.com/wiki/Double_Hero_Quest/Spoiler
- **Confidence:** high.
- **Our server (2026-09-24):** boxes 33109/33110,31679,13 (on our map) = uid 4522 club ring, 4523 red gem (real-map table). No level; rope out.

### Triple UH Rune Quest (now "Adorned UH Rune Quest")
- **Alt names:** Triple UH Rune Quest (7.x name)
- **Location:** Edron, Hero Cave.
- **Version / in 7.4:** 6.4, so yes.
- **Requirements:** no level. Premium. Rope.
- **Steps (pre8 wiki):** Hero Cave. Floor 1: Wild Warriors. Next hole: Demon Skeletons, Wild Warriors, Priestesses, Beholders, then stairs. Monks, Demon Skeletons and Wild Warriors, then stairs. Dragons, then hole. 1 Hero and 2 Monks, then stairs. Hunters, Demon Skeletons and Priestesses, then stairs. On the last floor (current wiki: 5 Monks) the reward is in the box. The pre8 spoiler is a stub that relies on images.
- **Rewards:** 7.x: Ultimate Healing Rune with 3 charges. The 2006 infobox also says 5 Mana Fluids. Since 8.6 it gives a Silver Rune Emblem (UH), which is post-7.4. Tibiantis: "Triple UH Rune".
- **Once:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=54428 ; https://tibia.fandom.com/index.php?oldid=40228 ; https://tibia.fandom.com/wiki/Adorned_UH_Rune_Quest ; https://tibiantis.info/library/quests
- **Confidence:** medium. The 5 Mana Fluids appear only in the 2006 infobox, and Tibiantis lists only the rune.
- **Our server (2026-09-24):** the box was missing: placed at 33136,31601,15 (the 5-monk floor; tibiaot74's spot), uid 1015 = 5 mana fluids + UH rune with 3 charges (real-map table and TibiaWiki 2006). No level; rope out.

### Edron Orc Cave quests (Barbarian Axe, Berserker Treasure, Dark Armor, Poison Daggers, Shaman Treasure)
All five are in the same cave, and the wiki advises doing them in one trip.
- **Location:** Edron Orc Cave, southwest of the castle. Entrance x 33173, y 31900, z 7. It can also be reached through a drain in the basement of the Edron Flats.
- **Version / in 7.4:** all 6.4, so yes. All five are listed on Tibiantis.
- **Requirements:** no level (recommended 30-40). Premium. Shovel and rope. Any vocation.
- **Common route (pre8 Dark Armor spoiler + current spoilers):**
  1. Go down into the cave. Follow it west then south (Orcs, Spearmen, Warriors, Poison Spiders).
  2. **Shaman Treasure:** on level -2, walk west to a 3-way crossing, then go north and west to the far NW room with a **Sacrificial Stone**, guarded by 2-3 Orc Shamans. The reward is in a skeleton. *(current wiki)*
  3. **Dark Armor / Poison Daggers:** on level -2 go west, take the north passage, enter the first room on the east and drop down the hole. The next floor is full of Orc Shamans (energy doesn't hurt them; use GFB). Go north over the tiled floor and drop down.
     - **Poison Daggers:** on this floor the chest holds a backpack with 2 Poison Daggers and 30 Poison Arrows *(current wiki)*.
     - **Dark Armor:** go north to a large pit with a Giant Spider. The hole is on the NE side of the pit. Go down, kill the Giant Spider, and the Dark Armor is in a dead body *(pre8 wiki)*.
  4. **Barbarian Axe / Berserker Treasure:** from the surface go south to the hole into the cave near the southernmost coast, then down to -2, -3 and -4. Orc Berserkers (3-6+), Orc Leaders and Orc Warriors.
     - **Berserker Treasure:** walk east on the bottom floor. The box at the end holds the pearls and gold.
     - **Barbarian Axe:** the final south room has 3+ Berserkers, 2 Orc Leaders and Warriors. The box at the southern end holds it. *(current wiki; the 2007 stub only says "beat all orcs till you reach the reward")*
- **Rewards:**
  - Barbarian Axe + Scimitar.
  - 3 White Pearls + 181 gp (2006 wiki) or 175 gp (current wiki and Tibiantis).
  - Dark Armor.
  - 2 Poison Daggers + 30 Poison Arrows.
  - 3 Blank Runes.
- **Once:** yes (each chest/corpse).
- **Sources:** https://tibia.fandom.com/index.php?oldid=23978 (Dark Armor pre8 spoiler) ; https://tibia.fandom.com/wiki/Barbarian_Axe_Quest/Spoiler ; https://tibia.fandom.com/wiki/Berserker_Treasure_Quest/Spoiler ; https://tibia.fandom.com/wiki/Poison_Daggers_Quest/Spoiler ; https://tibia.fandom.com/wiki/Shaman_Treasure_Quest/Spoiler ; infobox revisions oldid=30000, 30002, 30004, 30018, 30020 ; https://tibiantis.info/library/quests
- **Confidence:** high for existence and rewards. Only the Dark Armor route is described in 7.x-era text. The other four routes come from current (2009-2023) text.
- **Our server (2026-09-24):** the entrance hole drops into a pocket closed by a stone (33171,31897,8); the lever on the counter 33172,31896,8 (on the original map, unscripted) now removes it (aid 51024, tibiaot74's script). All five containers were missing, placed at tibiaot74's spots with real-map table uids: Shaman Treasure dead skeleton 33127,31885,9 uid 1033 (3 blank runes); Poison Daggers chest 33155,31880,11 uid 1034 (backpack: 2 poison daggers, 30 poison arrows); Dark Armor dead skeleton 33176,31871,12 uid 4521; Barbarian Axe box 33185,31945,11 uid 1030 (barbarian axe + scimitar in one box, as the real map's single uid); Berserker Treasure box 33199,31923,11 uid 1031 (3 white pearls, 175 gp). Rope and shovel to get out.

### Edron Goblin Quest
- **Alt names:** Goblin King's Treasure
- **Location:** Edron Goblin Cave, west of town.
  - Drain in the SW corner of the castle (from the depot): x 33165, y 31828, z 7.
  - Exit to the grassy area: x 33129, y 31811.
  - Goblin hill: x 33107, y 31848, z 7.
- **Version / in 7.4:** 6.4, so yes.
- **Requirements:** none (recommended 15). Premium. Rope.
- **Steps (pre8 wiki):** go down the drain and follow the only path to the grassy area. Go SW to the goblin hill and down the hole (up to 10 Goblins). Go NW, then down the hole. Go to the far NE hole and down (goblins and 2 Wasps). Two chests in the throne room to the north.
- **Rewards:** Steel Shield, Silver Amulet.
- **Once:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=23973 ; https://tibia.fandom.com/wiki/Edron_Goblin_Quest/Spoiler
- **Confidence:** high.
- **Our server (2026-09-24):** the two chests were missing: placed at 33095,31800-31801,10 next to the throne, uid 1028 steel shield, 1029 silver amulet (real-map table; the Thais Silver Amulet box moved to uid 2170). The grassy area's pitfall (grass 293 at 33128,31810,7) is the way back; pitfall.lua now drops the player through it.

### Troll Cave Quest
- **Alt names:** Brass Legs Quest
- **Location:** Edron Troll Cave, west of town. Same drain and grassy exit as the Goblin quest. The troll cave hole is at x 33117, y 31776, z 7.
- **Version / in 7.4:** 6.4, so yes.
- **Requirements:** none (recommended 12). Premium. Rope.
- **Steps (pre8 wiki):** go down the drain and follow the cave to the grassy area. Go NW to the Troll Cave and down the hole (up to 9 Trolls). Go N and E, then down the hole. Go north to the room, then down the hole. That room has Trolls, Bears, Swamp Trolls and a Frost Troll. In the current wiki these are Troll Champions, which is post-7.4. The reward is in 2 boxes on the east side.
- **Rewards:** Brass Legs, Garlic Necklace.
- **Once:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=24006 ; https://tibia.fandom.com/wiki/Troll_Cave_Quest/Spoiler
- **Confidence:** high.
- **Our server (2026-09-24):** the two boxes were missing: placed at 33143,31719/31721,10, uid 1026 brass legs, 1027 garlic necklace (150 charges). Way back through the grassy area's pitfall.

### Fire Axe Quest
- **Alt names:** Triple DL Quest
- **Location:** Edron Dragon Lair. Entrance x 33097, y 31703, z 7.
- **Version / in 7.4:** 6.4, so yes.
- **Requirements:** level 60 (Gate of Expertise). Premium. Rope, pick, and Destroy Field runes (for blocked rope holes and the pick hole).
- **Steps (pre8 wiki):**
  1. Enter the dragon cave (Dragons). Go north, down a hole, a bit north, rope up, continue north to another hole.
  2. Go down (1 Dragon Lord). Continue another floor and pass the **level-60 gate**. Current wiki: the gate is to the west, then go down the hole.
  3. Below are **3 Dragon Lords** (rope them up one by one). The quest boxes are in the SW part of the room.
  4. For the Fire Axe, **pick open a hole**, go down and "use" the skeleton remains.
- **Rewards:**
  - Wiki (pre8 and current): Fire Axe (skeleton), Ring of Healing, Dragon Necklace, 7 Small Diamonds. The 2005 wiki lists only Fire Axe and Ring of Healing.
  - Tibiantis: Red Spellwand, Life Ring, BP GFB, BP UH, Paralyze Rune, 2x Soulfire, 4x Fire Bomb, 2x Energy Bomb. This conflicts with the wiki, and Tibiantis doesn't mention the Fire Axe.
- **Once:** yes.
- **Sources:** https://tibia.fandom.com/index.php?oldid=56723 ; https://tibia.fandom.com/index.php?oldid=30010 ; https://tibia.fandom.com/wiki/Fire_Axe_Quest/Spoiler ; https://tibiantis.info/library/quests ; https://tibiantis.life/
- **Confidence:** medium (rewards conflict).
- **Our server (2026-09-24):** level-60 gate 33085,31650,10 and pick spot 33081,31651,11 on our map; both containers were missing: chest 33078,31656,11 uid 1019 (ring of healing, dragon necklace, 7 small diamonds), dead skeleton 33084,31650,12 uid 1018 (fire axe) - tibiaot74's spots, real-map table contents.

### Postman Missions Quest
- **Alt names:** Postman Quest, Postmans Quest
- **Location:** starts with NPC **Kevin** (Tibia Postal Service HQ, between Thais and Kazordoon), x 32568, y 32022, z 7. Other points (current wiki coords):
  - Folda mailbox: x 32001, y 31567, z 7.
  - Waldo's sealed door (Thais troll cave): x 32514, y 32248, z 8.
  - Santa's house on Vega: x 31955, y 31712, z 7.
  - Markwin in Mintwallin: x 32420, y 32152, z 15.
- **Version / in 7.4:** 7.24 (Mar 2004), so yes. The 2005 wiki describes a "three step course" (Postman, Grand Postman, Arch Postman), while the 2006 wiki describes 5 ranks and 10 missions.
- **Requirements:** no level. Premium (Edron, Venore boats, Vega, Mintwallin). One player. Items across the quest:
  - about 650 gp of travel money
  - a Crowbar
  - 20 Bones
  - Moldy Cheese, Banana Skin, Dirty Fur
  - 12 Arrows and Grapes
  - dice gold (5 gp per roll)
  - 500 oz of free capacity
  - a shovel for Waldo's hole
  - Mintwallin must be survivable
- **Steps (pre8 wiki, 10 missions; say "mission" to Kevin each time and "advancement" after every 2nd mission):**
  1. **Postal routes:** say "mission", yes to joining. Ride Thais→Carlin (Captain Bluebear), Femor Hills→Edron (carpet, Uzon), Edron→Venore (Captain Seahorse), then Kazordoon steamboat→Cormaya (Brodrosch). Report to Kevin.
  2. **Jammed mailbox:** use a Crowbar on the mailbox on top of the Folda mountain. Report. Rank: **Assistant Postman** (cheaper parcels/letters).
  3. **Bill:** find "A Strange Fellow" below the Venore depot and say "hat" 4 times; he admits to being David Brassacres. Say "bill", then yes. Report.
  4. **Bones:** give Kevin 20 bones (one at a time is fine). Advancement: **Postman** (Post Officer's Hat).
  5. **Present:** take the present from the chest behind Kevin's right blinking door. Do NOT open it (it disappears permanently). Give it to Dermot on Fibula ("present", yes).
  6. **Uniforms:** a chain of NPC conversations:
     - Hugo in Venore: "new set of uniforms", "new dress pattern".
     - Kevin: "new dress pattern".
     - Talphion in Kazordoon: repeat "new dress patterns" about 5 times.
     - Kevin.
     - Queen Eloise in Carlin: "hail queen", "uniforms".
     - Kevin.
     - Noodles, the king's dog in Thais: "sniff <moldy cheese|banana skin|dirty fur>", then "do you like that?". The moldy cheese is the one he hates.
     - Kevin.
     - Hugo: "new dress pattern".
     - Kevin. Advancement: **Grand Postman** (boat discount).
  7. **Measurements:** collect them from 6 NPCs:
     - Benjamin (Thais depot)
     - Liane (Carlin depot; give 12 arrows)
     - Olrik (Ab'Dendriel; dice game at 5 gp per roll until he rolls a 6)
     - Lokur (Kazordoon; then ask Kroox for "Lokurs measurements")
     - Dove (Venore depot; give grapes)
     - Chrystal (Edron)
     Report.
  8. **Waldo:** only after Kevin assigns it, go to the Thais troll cave (dig with a shovel). Go east and down, then N/E past the orcs and up the ladder. The sealed door to the west opens only once the mission is active. Use Waldo's body to get the Post Horn. Return. Advancement: **Grand Postman for Special Operations** (Post Horn).
  9. **Santa:** take the 500 oz letter bag from behind Kevin's left blinking door. Go to Vega and use the bag on Santa's mailbox.
  10. **Mintwallin:** deliver the letter to King **Markwin** in Mintwallin; he summons bodyguards. Return. Advancement: **Arch Postman** (use of locked royal mailboxes).
- **Rewards:**
  - Cheaper parcels (10 gp) and letters (5 gp).
  - Boat fares 10 gp cheaper.
  - Post Officer's Hat and Post Horn.
  - Use of locked mailboxes.
  - Current wiki adds the "Archpostman" achievement and a 6k discount in the Thieves Guild Quest. Both are post-7.4, so exclude them.
- **Once:** yes (progressive NPC storage). The present is lost forever if you open it.
- **Sources:** https://tibia.fandom.com/index.php?oldid=73449 (pre8 spoiler with full dialog transcripts) ; https://tibia.fandom.com/index.php?oldid=72821 ; https://tibia.fandom.com/wiki/The_Postman_Missions_Quest/Spoiler ; https://tibiantis.info/library/quests
- **Confidence:** high for 7.x-era content. It is uncertain whether the exact 10-mission structure already existed in Dec 2004: the 2005 wiki mentions only 3 ranks.

### Hero Cave / Crown Armor note
- No "Crown Armor quest" in the Hero Cave was found. The 2005 Crown Armor item page says it was "looted only in the Hero Cave in Edron" (a Hero drop). By Dec 2006 the item page says it "can be obtained through the Black Knight Quest" (Venore, Group C). The Hero Cave itself (implemented 6.4) contains these quests: Triple UH, Ring, Double Hero, Wedding Ring, Vampire Shield, Demon Helmet, Parchment Room and Annihilator.
- Sources: https://tibia.fandom.com/index.php?oldid=73489 (Crown Armor 2006) ; https://tibia.fandom.com/index.php?oldid=55730 (Hero Cave 2006) ; https://tibia.fandom.com/wiki/Hero_Cave

## Excluded / post-7.4

- **The Pits of Inferno Quest:** wiki says implemented 7.9 (2006), level 80, premium. Not in the Tibiantis list. **Exclude.** Sources: https://tibia.fandom.com/wiki/The_Pits_of_Inferno_Quest ; https://tibiantis.info/library/quests. Confidence: high.
- **Sam's Old Backpack Quest (Dwarven Armor Quest):** wiki says implemented 7.5 (9 Aug 2005). Ulderek's Rock, level 35 (current), free. Not in the Tibiantis list. Note: Tibiantis's custom "Aruthang Quest" gives a Dwarven Armor instead. **Exclude.** Sources: https://tibia.fandom.com/wiki/Sam%27s_Old_Backpack_Quest ; https://tibia.fandom.com/index.php?oldid=41348. Confidence: high.
- **Elephant Tusk Quest:** 7.5, Port Hope (Port Hope itself is 7.5). **Exclude.** Source: https://tibia.fandom.com/wiki/Elephant_Tusk_Quest. Confidence: high.
- **Magic Sword Quest (Sword of Valor Quest, Mintwallin):** deprecated. The wiki says it predates 5.1 and was the only way to get a Magic Sword "before the implementation of The Annihilator Quest". It was repeatable, with 2 open chests in the far south of Mintwallin (x 32411, y 32247, z 15):
  - North chest: Yellow Spell Wand, Demon Armor, Demon Legs.
  - South chest: Magic Sword, Demon Armor, Demon Legs.
  
  When it was removed is not stated, but it is not in the Tibiantis list. **Exclude, very likely gone by 7.4** (uncertain). Source: https://tibia.fandom.com/wiki/Magic_Sword_Quest/Spoiler. Confidence: medium.
- **Iron Ore Quest (Dwarf Mines chest):** no implemented version on the wiki, and the page was created in 2011. Not on Tibiantis. **Probably not 7.4 (uncertain).** Source: https://tibia.fandom.com/wiki/Iron_Ore_Quest. Confidence: low.
- **Minotaur Leather Quest (raft south of Thais):** no version, and the page was created in 2011. Not on Tibiantis. **Probably not 7.4 (uncertain).** Source: https://tibia.fandom.com/wiki/Minotaur_Leather_Quest. Confidence: low.

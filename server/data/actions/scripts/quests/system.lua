-- Quest chests (docs/reference-74/quests.md): every container or object on the map with action id 2000.
-- Its unique id is the player storage that marks it as looted (once per character). The reward is the
-- unique id itself when that is an item id (the usual real-map convention, e.g. uid 2384 = a rapier), and
-- otherwise what lies inside the chest on the map (copied, the chest itself keeps it for the next player).
-- A reward the player cannot carry stays: nothing is marked, they can come back.

local ITEM_ID_LIMIT = 10000   -- unique ids below this are item ids

-- Rewards the map does not carry (the chest is empty on Tibia74.otbm): unique id -> {{item id, count,
-- action id (keys), contents {{item id, count, key, text}, ...}, text (a letter, a map)}, ...}. Lua cannot read an
-- item's text, so a reward with writing on it carries the text here. Each entry names its quest and source
-- (docs/reference-74/quests.md).
local REWARDS = {
	-- Bear Room Quest (Rookgaard): the third bear-room box, and the chest below the mud south of the big table.
	-- Real-map chest table (OTLand "Quest System for 7.4 Realots"): "12 arrows and 40 gp"; TibiaWiki Key 4601:
	-- copper key, "Bear Room Key".
	[52148] = {{2544, 12}, {2148, 40}},
	[20003] = {{2089, 1, 4601}},
	-- Present Box Quest (Rookgaard): the chest next to the Bear Room stone switch. TibiaWiki Present Quest
	-- (2006): "Backpack with Present Box, Jug, Plate, Cup" - the present is traded to Seymour for a legion helmet.
	[52149] = {{1988, 1, nil, {{1990}, {2014}, {2035}, {2013}}}},
	-- Captain Iglues Treasure Quest (Rookgaard, below the poison spider tower): the right chest of the two at
	-- 32038-32039,32121,13. TibiaWiki (current) and Tibiantis: 2 salmon; the left chest (not a quest chest)
	-- holds the stamped letter "Treasure of captain Iglue" and 12 salmon, refilled daily - as on our map.
	[52171] = {{2668, 2}},
	-- Dragon Corpse Quest (Rookgaard, bear cave, below the stone pile and the wheat): the dead dragon at
	-- 32179,32224,9. All sources: a bag with a copper shield and a legion helmet (real-map table: "You have
	-- found a bag.").
	[54322] = {{1987, 1, nil, {{2530}, {2480}}}},
	-- Katana Quest (Rookgaard): the body north of the poison fields holds key 4603 for the door down to the
	-- katana room (real-map table: silver key 4603; Tibiantis lists Key 4603 as a reward).
	[20002] = {{2088, 1, 4603}},
	-- Minotaur Hell Quest (Rookgaard): the middle of the three boxes west of the stairs (the others are uid 2395
	-- carlin sword and 2580 fishing rod). All sources: 4 poison arrows + 10 arrows (real-map table too).
	[52159] = {{2545, 4}, {2544, 10}},
	-- Goblin Temple Quest (Rookgaard premium side): the two chests up the stairs past the goblin room (32209,12).
	-- TibiaWiki (2005, 2006, current) and Tibiantis: 50 gp, 5 small stones, sandals / pan, 4 snowballs, milk. The
	-- real-map table has the same split but 100 gp - four sources against one: 50. The pan is for Billy.
	[52169] = {{2642, 1}, {1294, 5}, {2148, 50}},
	[52170] = {{2563, 1}, {2111, 4}, {2006, 6}},
	-- Parchment Room Quest (Edron Hero Cave): the coffin under the "Buried forever" parchment (33063,31624,15).
	-- Real-map table (OTLand "Quest System for 7.4 Realots"), [10057]: "goldenkey 6010 + bone, stealth ring,
	-- 2 talons, skull brown bag at Parchment Room Treasure"; TibiaWiki (current) the same. Key 6010 opens the
	-- locked door after the level-100 gate on the way to the Demon Helmet Quest (decided with the user).
	[10057] = {{1987, 1, nil, {{2091, 1, 6010}, {2230}, {2165}, {2151, 2}, {2229}}}},
	-- Battle Axe Quest (Thais sewers, below the pick hole at 32302,32257,8): the dead skeleton at 32305,32254,9 -
	-- missing on our map (and the JS engine's), placed where tibiaot74 has it. Real-map table: "[1658] = {{2378,1}},
	-- -- battle axe -- Sewers"; TibiaWiki 2006: "You will find the Battle Axe in a dead Skeleton." (1658 is below
	-- 10000, so the reward has to be named here - it is not item 1658.)
	[1658] = {{2378, 1}},
	-- Annihilator Quest: the four chests behind the demon room (33227/33229/33231/33233,31656,13), under the signs
	-- "Demon Armor", "Sword of Valor", "Stonecutter Axe", "The Surprise" (our map; the items lie on the altars above).
	-- TibiaWiki 2005/2006, Tibiantis: demon armor, magic sword, stonecutter axe, a present with a teddy bear - the
	-- "annihilation bear" (TibiaWiki 2006; item 2326 in our 7.4 item list). No real-map table entry.
	[51012] = {{2494, 1}},
	[51013] = {{2400, 1}},
	[51014] = {{2431, 1}},
	[51015] = {{1990, 1, nil, {{2326}}}},
	-- Deeper Fibula Quest (the Fibula dungeon; key 3940 from Dermot opens the dungeon door, level-50 gate). Real-map
	-- table: [10014] golden key 3980 ("Fibula golden key"), [10015] tower shield, [10016] warrior helmet, [10017]
	-- knight axe, [10018] dwarven ring, [10019] elven amulet 50 - TibiaWiki 2006 places them: key 3980 "found by
	-- using a hole" (the small hole 32219,32401,10, a crate lies on it), the tower shield in a skeleton under a
	-- fire field (NW), the warrior helmet in a skeleton south of it, the dwarven ring in a skeleton north of the
	-- exit portal, the elven amulet in a fresh dragon corpse east of it, the knight axe in a dead human south-east.
	-- Four of the five bodies were missing on our map: placed where tibiaot74 has them.
	[10014] = {{2091, 1, 3980}},
	[10015] = {{2528, 1}},
	[10016] = {{2475, 1}},
	[10017] = {{2430, 1}},
	[10018] = {{2213, 1}},
	[10019] = {{2198, 50}},
	-- Life Ring Quest (Thais Ancient Temple, south branch: over the drawbridges, a pick on the hidden hole, the box in
	-- the NE corner below). Real-map table: "[3616] = {{2168},{2201,200}}, -- Ancient Temple Life ring Quest";
	-- TibiaWiki and Tibiantis: life ring and dragon necklace.
	[3616] = {{2168, 1}, {2201, 200}},
	-- Throwing Star Quest (Ancient Temple, the underground park: a pick at 32517,32107,14, the box SE of the ladder).
	-- Real-map table: "[3619] = {{2399,10}}, -- throwing stars Mintwallin Quest"; TibiaWiki, Tibiantis: 10.
	[3619] = {{2399, 10}},
	-- Ghoul Room Quest (Ancient Temple: "Open a dead skeleton in the South-East of the room - you will get Key 3600",
	-- down the well, the key door, the reward). Real-map table: "[3601] = {{2088,1,3600}}, -- Ghoul Room key --
	-- skeleton body" and "[3602] = {{2199,150},{2209,1}}, -- garlic necklace, club ring -- Mintwallin Ghoul Room
	-- Quest". The skeleton was missing (placed where tibiaot74 has it, 32509,32181,13); the reward is in the middle
	-- one of the room's three chests (32500,32176,14) - no source says which.
	[3601] = {{2088, 1, 3600}},
	[3602] = {{2199, 150}, {2209, 1}},
	-- Mintwallin prison key (TibiaWiki Key 3620: "A Drawer in the Mintwallin barracks [...] used to lock and unlock all
	-- the doors in the Mintwallin prison"). The drawer 32411,32155,15 holds it on our map; one per character.
	[13620] = {{2088, 1, 3620}},   -- uid 13620: the real-map table's 3620 is the Spike Sword body
	-- Mad Mage Room Quest (Mintwallin: key 3666 from A Prisoner opens the door 32578,32197,15; up the ladder to the
	-- three containers). Real-map table: [10058] magician hat (the Hat of the Mad), [10059] stone skin amulet 5,
	-- [10060] star amulet - all three are taken (TibiaWiki). Which container holds which: no source; west to east.
	[10058] = {{2662, 1}},
	[10059] = {{2197, 5}},
	[10060] = {{2131, 1}},
	-- Mintwallin Cyclops Quest. TibiaWiki Key 3667: "found in a dead body in a cave behind Mad Mage Quest room [...]
	-- in the south-east corner under some rubbish" (32576,32216,15; our map has it); it opens the door to the room
	-- over the minotaur outcasts where Key 3610 is. Real-map table: "[3667] = {{2088,1,3667}}", "[3610] =
	-- {{2088,1,3610}}, -- key to secret lab -- Mintwallin Cycs Quest aka Moving Wall lever", "[3611] = {{2145,1}},
	-- -- Diamond Next To key -- Mintwallin Cyclops Treasure" (TibiaWiki 2006: small diamond).
	[3667] = {{2088, 1, 3667}},
	[3610] = {{2088, 1, 3610}},
	[3611] = {{2145, 1}},
	-- Devil Helmet Quest (Mintwallin: two players - one holds the switch tile that opens the grate -, the level-30 gate,
	-- key 3610 opens the lab). Real-map table: "[3613] = {{2462},{2381},{2146,4}}, -- devil helmet, halberd,
	-- sapphires -- Mintwallin Lab Treasure" - one container; our map had none in the lab: a box at 32459,32144,15
	-- (where tibiaot74 puts its box).
	[3613] = {{2462, 1}, {2381, 1}, {2146, 4}},
	-- Six Rubies Quest (Ancient Temple, the dragons' fire island): "Destroy Field the fire covering a hole [...] Use
	-- the hole" - the small hole under a fire field at 32370,32265,12 (our map). Real-map table [3614] says 2 small
	-- rubies ("Ancient Temple south drags"); TibiaWiki 2006, the current wiki and Tibiantis say 6 (and the quest is
	-- called Six Rubies): three against one - 6.
	[3614] = {{2147, 6}},
	-- Geomancer Quest (Mount Sternum, the dwarf camp at the bottom): "The quest box is on the east side of the room"
	-- (TibiaWiki 2006) - missing on our map, a box at 32456,32008,13 (tibiaot74's spot). Real-map table: "[3617] =
	-- {{2146},{2145},{2213}}, -- sapphire, diamond, dwarven ring -- Geomancer Quest".
	[3617] = {{2146, 1}, {2145, 1}, {2213, 1}},
	-- Naginata Quest (the Thais dragon lair, past the level-40 gate and down to the dragon lords): "The chest is at the
	-- north end" (TibiaWiki) - the room had no container: a chest at 32346,32063,12 (tibiaot74 has a dead dragon
	-- there). Real-map table: "[10065] = {{2426,1}}, -- naginata".
	[10065] = {{2426, 1}},
	-- Noble Armor Quest (Skjaar's crypt below Mount Sternum: level-35 gate, key 3142 from Skjaar). "open the chests"
	-- (TibiaWiki): real-map table [10043] noble armor, [10042] crown helmet. Our map had one chest (noble armor); the
	-- crown helmet box is at tibiaot74's spot 32455,32048,8.
	[10043] = {{2486, 1}},
	[10042] = {{2491, 1}},
	-- Edron Goblin Quest: "The reward is in two chests in the throne room to the north" (TibiaWiki pre-8.0) - missing
	-- on our map: chests at 33095,31800-31801,10 (tibiaot74's spots, next to the throne). Real-map table (Edron,
	-- "goblin cave"): "[1028] = {{2509}}, -- steel shield", "[1029] = {{2170}}, -- silver ammy". (The Thais Silver
	-- Amulet Quest's box, 32507,32270,9, is uid 2170 - the amulet itself.)
	[1028] = {{2509, 1}},
	[1029] = {{2170, 1}},
	-- Troll Cave Quest (Edron): "The reward is in two boxes on the east side of the room" (TibiaWiki pre-8.0) - missing
	-- on our map: boxes at 33143,31719/31721,10 (tibiaot74's spots). Real-map table: "[1026] = {{2478}}, -- brass
	-- legs", "[1027] = {{2199}}, -- garlic necklace" (its own 150 charges).
	[1026] = {{2478, 1}},
	[1027] = {{2199, 150}},
	-- Spike Sword Quest (the fire devils' lava cave east of Mount Sternum): "The reward is in a body hidden behind a
	-- pillar" (TibiaWiki) - missing on our map: a dead human at 32568,32085,12 (tibiaot74's spot, behind the pillar at
	-- 32569,32086). Real-map table: "[3620] = {{2383,1}}, -- Spike sword Quest".
	[3620] = {{2383, 1}},
	-- Triangle Tower Quest (the tower east of Thais, the chest on the top floor 32565,32119,3). Real-map table:
	-- "[4510] = {{2146,2},{2213},{2199,150}}, -- Triangle tower -- garlic necklace, dwarven ring, 2 small sapphires".
	[4510] = {{2199, 150}, {2213, 1}, {2146, 2}},
	-- Dead Archer Quest (Thais troll cave, the slime room two floors down): the dead human at 32513,32302,10 - missing
	-- on our map (and the JS engine's), placed where tibiaot74 has it (the north end of the room, as TibiaWiki says).
	-- Real-map table: "[1662] = {{2456},{2545,5},{2006,7},{2006,10}}, -- dead archer quest (bow, 5poison, mf, lf)";
	-- TibiaWiki pre-8.0 and Tibiantis: bow, 5 poison arrows, mana fluid, life fluid (7 = mana, 10 = life).
	[1662] = {{2456, 1}, {2545, 5}, {2006, 7}, {2006, 10}},
	-- Behemoth Quest (Cyclopolis, past the level-60 gate 33297,31670,14): the four chests at the north end of the room
	-- (33294/33295/33297/33298,31658,13). TibiaWiki (2005, pre-8.0 and current): demon shield, golden armor, guardian
	-- halberd, platinum amulet, life ring, crystal ring, 3 small diamonds, 4 small sapphires; tibiaot74 splits them the
	-- same way (the last one a bag). One of each per character (decided with the user). No real-map table entry. The
	-- golden armor and guardian halberd chests are uid 2466 / 2427 (the item); the demon shield has its own uid - 2520
	-- is the Demon Helmet Quest's demon shield.
	[51023] = {{2520, 1}},
	[51022] = {{1987, 1, nil, {{2171}, {2168}, {2124}, {2145, 3}, {2146, 4}}}},
	-- Vampire Shield Quest (Edron Hero Cave, the Temple of Xayepocax): the two chests behind the level-70 gates
	-- (33189/33195,31688,14) and "a quest box outside of the level 70 door" with "the Strange Symbol, Black Pearl and
	-- Mysterious Fetish" (TibiaWiki pre-8.0 and current; missing on our map and the JS engine's - a box at
	-- 33188,31682,14, tibiaot74's spot). Real-map table: "[1016] = {{2534}}, -- Vampire shield", "[1017] = {{2414}},
	-- -- Dragon Lance", "[1032] = {{2174},{2144},{2194}}, -- strange symbol, black pearl, mysterious fetish" - loose,
	-- not in a bag. Which chest is which: tibiaot74 (the dragon lance west, the vampire shield east).
	[1016] = {{2534, 1}},
	[1017] = {{2414, 1}},
	[1032] = {{2174, 1}, {2144, 1}, {2194, 1}},
	-- Double Hero Quest (Edron Hero Cave): "Two chests at the south of the room: open both" (TibiaWiki pre-8.0) - the
	-- boxes 33109/33110,31679,13. Real-map table: "-- 2x hero quest [4522] = {{2209}}, -- club ring [4523] = {{2156}},
	-- -- red gem"; which is which: tibiaot74 (the club ring west).
	[4522] = {{2209, 1}},
	[4523] = {{2156, 1}},
	-- Triple UH Rune Quest (Edron Hero Cave, the bottom floor with 5 monks): "Rewards are in the box" (TibiaWiki
	-- pre-8.0) - missing on our map: a box at 33136,31601,15, the gap in the row of tables where tibiaot74 has its
	-- chest. Real-map table: "[1015] = {{2006,7},{2006,7},{2006,7},{2006,7},{2006,7},{2273,3}}, -- triple uh";
	-- TibiaWiki 2006: "Ultimate Healing Rune with 3 charges, 5 Mana Fluids" (Tibiantis: the rune only).
	[1015] = {{2006, 7}, {2006, 7}, {2006, 7}, {2006, 7}, {2006, 7}, {2273, 3}},
	-- Edron Orc Cave (five quests, one cave; the entrance stone: quests/edron_orc_cave_lever.lua). Our map (and the
	-- JS engine's) lost every reward container: placed where tibiaot74 has them, with the real-map table's uids.
	-- Shaman Treasure: "The reward is in a skeleton body in a room at the far north-western end of the floor [...]
	-- it has a Sacrificial Stone" (TibiaWiki) - a dead skeleton at 33127,31885,9. Real-map table: "[1033] =
	-- {{2260},{2260},{2260}}, -- 3 blank runes - Orc Cave".
	[1033] = {{2260, 1}, {2260, 1}, {2260, 1}},
	-- Poison Daggers: "in the chest [...] you can find a backpack with 2 Poison Daggers and 30 Poison Arrows"
	-- (TibiaWiki) - a chest at 33155,31880,11. Real-map table: "[1034] = {{2411},{2411},{2545,30}}, -- 2 poison
	-- dagger, 30 poison arrows (in backpack)".
	[1034] = {{1988, 1, nil, {{2411}, {2411}, {2545, 30}}}},
	-- Dark Armor: "you can find the Dark Armor inside a dead body on the ground" (TibiaWiki pre-8.0) - tibiaot74's dead
	-- skeleton at 33176,31871,12, below the giant spider's pit. Real-map table: "[4521] = {{2489}}, -- dark armor".
	[4521] = {{2489, 1}},
	-- Barbarian Axe: "Open the box at the southern end of the room" (TibiaWiki) - a box at 33185,31945,11. Real-map
	-- table: "[1030] = {{2429},{2419}}" - the barbarian axe and a scimitar in one object; tibiaot74 and the current
	-- Berserker Treasure spoiler ("Two boxes") split them - one box, as the real map had one unique id.
	[1030] = {{2429, 1}, {2419, 1}},
	-- Berserker Treasure: "The reward is in a box at the end of the floor" (TibiaWiki) - a box at 33199,31923,11.
	-- Real-map table: "[1031] = {{2143,3},{2148,100},{2148,75}}" - 3 white pearls and 175 gold (current wiki and
	-- Tibiantis say 175 too; TibiaWiki 2006 said 181).
	[1031] = {{2143, 3}, {2148, 100}, {2148, 75}},
	-- Fire Axe Quest (Edron dragon lair, past the level-60 gate 33085,31650,10): "The quest boxes are in the SW part of
	-- the room"; "For the Fire Axe, pick open a hole, go down and use the skeleton remains" (TibiaWiki pre-8.0; the
	-- pick spot is 33081,31651,11). Both were missing on our map: a chest at 33078,31656,11 among the fire fields and a
	-- dead skeleton at 33084,31650,12 (tibiaot74's spots). Real-map table: "[1018] = {{2432}}, -- fire axe", "[1019] =
	-- {{2214,1},{2201,200},{2145,7}}, -- extra box = roh, dragoneck+7 diamonds" (TibiaWiki pre-8.0 and current too).
	[1018] = {{2432, 1}},
	[1019] = {{2214, 1}, {2201, 200}, {2145, 7}},
	-- Fanfare Quest (Carlin): "get Key 3520 from the box in the north-east corner of the big room" of the building
	-- north-west of the boat (TibiaWiki 2005) - the box 32376,31802,7; the key opens the crypt's west door
	-- (32400,31788-31789,8, aid 3520), down the hole and north through the trolls to the chest 32390,31769,9 (missing
	-- on our map, placed at tibiaot74's spot). Real-map table: "[3520] = {{2092,1,3520}}, -- Carlin graveyard key",
	-- "[4507] = {{2076,1}}, -- Carlin Fanfare".
	[3520] = {{2092, 1, 3520}},
	[4507] = {{2076, 1}},
	-- White Raven Monastery Quest part 1 (Ghostlands): "Simply use the head of the top coffin to find the Family
	-- Brooch" (TibiaWiki 2006) - the coffin 32248,31866,8 (tibiaot74 scripts the same one). Real-map table: "[4506] =
	-- {{2318,1}}, -- carlin Family Brooch Quest". Dalbrect takes it and becomes your friend (npc/scripts/dalbrect.lua).
	[4506] = {{2318, 1}},
	-- Alawar's Vault Quest (Senja and Folda). Our map (and the JS engine's copy of the 7.4 map) had the three keys lying
	-- on the floor where their chests stood - the export kept the contents and lost the containers: chests / box put
	-- back at tibiaot74's spots, the loose keys taken away. Real-map table: "[4501] = {{2089,1,4501}}, -- Alawar key 2
	-- minoroom", "[4502] = {{2490},{2410,4},{2260,1},{2160,33},{2089,1,4502}}", "[4503] = {{2088,1,4503}}", "[4504] =
	-- {{2143,3}}, -- Alawar Chest - 3 white pearl", "[4505] = {{2413,1}}, -- Alawar Chest - 1 broad sword". Key 4503 is
	-- the copper key our map had (TibiaWiki: "copper key 4503"; the table says silver); the maze bag's 33 are gold coins
	-- (TibiaWiki "33gp", tibiaot74; the table says crystal).
	[4503] = {{2089, 1, 4503}},                 -- Folda, behind the fire fields: the "Protected Area" door
	[4501] = {{2089, 1, 4501}},                 -- the minotaur level's first room: the storage room door
	[4502] = {{1987, 1, nil, {{2089, 1, 4502}, {2490}, {2410, 4}, {2260}, {2148, 33}}}},   -- the maze: the vault doors
	[4504] = {{2143, 3}},                       -- the vault, by the portal
	[4505] = {{2413, 1}},
	-- Power Ring Quest (Femor Hills goblin cave): "The Quest boxes are on the north end of this room, next to the Beer
	-- Casks" (TibiaWiki 2006) - the two chests 32599/32601,31776,9 on our map. Real-map table: "[4511] = {{2203,1}},
	-- -- Femor hills - power ring", "[4512] = {{2172,200}}, -- Femor hills - bronze ammy" (which is which: tibiaot74).
	-- The ring is 2166, the power ring as it lies in a chest (2203 is the worn one, it runs out).
	[4511] = {{2166, 1}},
	[4512] = {{2172, 200}},
	-- Griffin Shield Quest (the first room of the Maze of Lost Souls, behind the level-30 gates and before Demona's level-60
	-- gate): "take the reward (Griffin Shield, Dwarven Axe and Obsidian Lance) that is inside 2 slain skeletons and a
	-- dead body" (TibiaWiki 2006) - missing on our map, placed at tibiaot74's spots 32498,31721 / 32500,31721 /
	-- 32503,31724,15. Real-map table: "[10062] = {{2533}}, -- griffin shield", "[10063] = {{2435}}, -- dwarven axe",
	-- "[10064] = {{2425}}, -- obsidian lance".
	[10062] = {{2533, 1}},
	[10063] = {{2435, 1}},
	[10064] = {{2425, 1}},
	-- Crystal Wand Quest (Double SD Quest; Demona, the throne room): "open the chests for your Double charge SD and
	-- Crystal Wand" (TibiaWiki 2006); current wiki "chests for your Crystal Wand and a bag with Silver Rune Emblem (SD)
	-- and Twinkiller Rune (Book)"; Tibiantis: "Crystal Wand, Double SD Rune, Twinkiller Rune (Book)". The two boxes by
	-- the thrones (32479/32481,31611,15) are on our map; the left one holds Ferumbras's letter about the
	-- "twinkiller-rune" - so the left one gives the bag with it and the SD (2 charges), the right one the wand (no
	-- source says which box; tibiaot74 puts the wand left).
	[51027] = {{2184, 1}},
	[51028] = {{1987, 1, nil, {{2268, 2}, {1969, 1, nil, "Dear Gelunidas,\nI request that you send me the twinkiller-rune I ordered some months ago immediately. If I am convinced that they work as promised I will order them in greater numbers. They might be handy in my next schemes. As this letter should show you, the tales of my death are wildly exagerated. I hope you and your warlock brethren did not think you get off the hook that easy? If you don't work on the stuff I ordered and I do not receive the stuff I ordered in time, be prepared for a visit. You won't like my new friends that I would introduce to you.\n\nFerumbras"}}}},
	-- Purple Tome Quest (the Demona library, 32421-32432,31591-31601,15): "In those bookcases you will find the Maps and
	-- the tome" (current wiki); Tibiantis: "Tibia Map (Book), Fields of Glory Map (Book) and Purple Tome". Our map has the
	-- two maps in their bookcases (32423 / 32428,31591,15 - the texts below are theirs) and no purple tome: it goes in
	-- the bookcase 32421,31594,15 (tibiaot74's spot).
	[51029] = {{1982, 1}},
	[51030] = {{1956, 1, nil, nil, "*You see a map of our world Tibia*"}},
	[51031] = {{1957, 1, nil, nil, "*You see a map of the surface of the Fields of Glory. There are many red lines and two golden points on it. You wonder what their meaning is.*"}},
	-- The Queen of the Banshees Quest, the final room (floor 15, past the seven seal doors): TibiaWiki (Dec 2006):
	-- "Boots of Haste, Giant Sword, Tower Shield, Stealth Ring, Stone Skin Amulet and 10k gp" - all of them (decided with
	-- the user 2026-09-25 over Tibiantis' list); split over the four chests as tibiaot74 does (the last one a bag).
	[51061] = {{2195, 1}},
	[51062] = {{2393, 1}},
	[51063] = {{2528, 1}},
	[51064] = {{1987, 1, nil, {{2165}, {2197, 5}, {2152, 100}}}},
	-- White Raven Monastery Quest part 2: the dead monk in the Banshee dungeon (32262,31861,11) - "Use the Dead Human to
	-- get a Backpack containing the Monk's Diary" (current wiki). What our map has in him, for every character: the
	-- backpack, the diary (Costello takes it for the Blessed Ankh) and the rest.
	[51065] = {{1988, 1, nil, {{1972, 1, nil, "<the text seems to be a mostly ruined diary of some sort, found on the body of a dead monk. Most passages make no sense at all to you>\n... abbot still clueless abour my ...\n...\nAfter all those perils and puzzels I have located the throne of darkness at last. I will lead ...\n...\n... crypts and monsters ... found one of the caged demons that seem to be leached as a powersupply of some sort ...\n...\n... switches on the end of the scorpion path and the lair of the wicked web ... \n... died but I could make it to the throne. My wards are holding the howling ghosts and spectres at bay for now and I prepare to unleash the powers of the throne ... \n...\n... still impossible! My wards are fading and the ancient spirits feel that they will soon claim another victory. I failed the brotherhood and will soon join the howling hords in their eternal torment and madness. ...\n...\nhas stoped. I KNOW they are coming after me now. I can see the flickering of the shadows as they aproach. THEY ARE COMING"}, {2236}, {2237}, {2238}}}},
	-- White Raven Monastery (Isle of the Kings): Key 3350 to the monks' restricted floor, "Found in a Bookcase in the room of
	-- Costello" (TibiaWiki Key 3350) - our map has it there (32180,31934,7) in a bag with the abbot's scroll, as loot for
	-- the first comer: now for every character. Going up with it makes a trespasser (movements/scripts/isle_restricted.lua).
	[51066] = {{1987, 1, nil, {{1949, 1, nil, "I have to hide that key better. One of that greedy adventurers that came here seemingly out of nowhere and refused to tell me how he got here stole it and disturbed the contemplation of the brothers upstairs. Gladly they could defeat him. When will those people learn some respect. How could they think there would anything valuable? The next intruders will pay a bitter price for such an act of evil!"}, {2088, 1, 3350}}}},
	-- Plains of Havoc (docs/reference-74/quests.md). Giant Smithhammer Quest: "The quest box is located in the room directly to
	-- the south" of the north building's stairs (TibiaWiki 2006) - our map has two chests there; the west one gives it all
	-- (decided with the user 2026-09-25). Real-map table: "[4520] = {{2151},{2321},{2148,100}}" - talon, giant smithhammer, 100 gp.
	[4520] = {{2321, 1}, {2151, 1}, {2148, 100}},
	-- Iron Helmet Quest: "a dead body partially obscured by a tree" west of the camp - missing on our map, placed at
	-- tibiaot74's spot (32769,32225,7, by a sycamore). Decided with the user 2026-09-25: the 2006 wiki's list (iron helmet,
	-- SD rune, leather armor, letter, worn leather boots) and the longsword the real-map table, tibiaot74 and Tibiantis give;
	-- in a backpack (tibiaot74). The letter is the real-map table's "Dear Muriel!".
	[4518] = {{1988, 1, nil, {{2459}, {2268, 1}, {2467}, {2598, 1, nil, "Dear Muriel!\nMy apprentice behaves strangely lately.\nI fear he has something evil in mind.\nHe must have stolen the books about\nnecromancy you were missing after\nour last visit but I have no proof yet.\nThank the gods he does not know about\nthe fountain of life and the caves of\ninferno yet. I will send Laira to town in\nsome days. I think she's in danger\nif I'm right about Porgol.\n \nYour friend,\nArcian"}, {2238}, {2397}}}},
	-- Power Bolts Quest: "The reward is in a dead body under some other items on the floor" (TibiaWiki 2006) - the dead
	-- human 32818,32284,8 of the cave below the hole south of the temple. Real-map table: "[4514] = {{2547,5},{2546,12}},
	-- -- power bolt, burst arrow -- add brown bag" and "[4513] = {{2377}}, -- two handed sword" (one body on our map: both);
	-- the Dreammaster book lies beside it on our map.
	[4514] = {{1987, 1, nil, {{2547, 5}, {2546, 12}}}, {2377, 1}},
	-- Isle of the Mists Quest (druids only, decided with the user): "a box and a drawer in the groundfloor, where you will find
	-- the items" (TibiaWiki 2006) - our map has the box 32852,32332,7 and the book in the bookcase beside it; 3 small emeralds
	-- (the 2006 wiki; decided with the user over the current wiki's and Tibiantis' 2).
	[51067] = {{2149, 3}},
	-- Ornamented Shield Quest: Krendorak's body under the fire field in the NE corner of the cave below the pick hole (the
	-- cave our map had lost - copied from tibiaot74's map, tools/map-copy-tiles.py). 2006 wiki: "The body has a bag with the
	-- loot, including Crystal Key #3702", the steel helmet and ornamented shield under the junk by it; quests.md: key 3702,
	-- spike sword, dragon necklace, might ring, Krendorak's journal.
	[51068] = {{1987, 1, nil, {{2090, 1, 3702}, {2383}, {2201, 200}, {2164}, {1955, 1, nil, "Krendorak's journal"}}}, {2524, 1}, {2457, 1}},
	-- and part 2 (current wiki; decided with the user): the chest behind the stalagmites, a red bag. Real-map table:
	-- "[4516] = {{2169},{2152,5},{2199,150},{2175},{2071}}, -- time ring, 5plat, garlick, spellbook, lyre- add red bag".
	[4516] = {{1993, 1, nil, {{2169}, {2152, 5}, {2199, 150}, {2175}, {2071}}}},
	-- Elvenbane Quest (Ab'Dendriel): "The final floor contains 2 quest chests and 2 quest drawers" (TibiaWiki 2006) - missing
	-- on our map (the tower top 32587-32593,31642-31647,3): placed at tibiaot74's spots. Real-map table: "[10053] =
	-- {{2175,1},{2145,2},{2148,100}}, -- spellbook, diamond, gps", "[10054] = {{2006,7},{2260,1}}, -- manafluid, blank",
	-- "[10055] = {{2394}}, -- morning star", "[10056] = {{2525}}, -- dwarven shield" - the 2006 wiki's list.
	[10053] = {{1987, 1, nil, {{2175}, {2145, 2}, {2148, 100}}}},
	[10054] = {{2006, 7}, {2260, 1}},
	[10055] = {{2394, 1}},
	[10056] = {{2525, 1}},
	-- Orc Fortress Quest: "The quest boxes are located in the north end of this room" (TibiaWiki 2005) - the three chests
	-- 32980/32981/32985,31727,9 past the level-40 gate. Knight armor, knight axe, fire sword (both wikis, the real-map table
	-- [10029] fire sword / [10030] knight axe / [10031] knight armor; decided with the user over Tibiantis' list), west to
	-- east as tibiaot74.
	[10029] = {{2392, 1}},
	[10030] = {{2430, 1}},
	[10031] = {{2476, 1}},
	-- Draconia Quest: "the reward chests are behind the level 25 door" (TibiaWiki 2006) - the two chests 32803/32804,31582,2
	-- on our map; ice rapier, serpent sword, stone skin amulet, energy ring, two each (decided with the user 2026-09-26).
	[51075] = {{2396, 1}, {2409, 1}},
	[51076] = {{2197, 5}, {2167, 1}},
	-- Circle Room Quest (Kazordoon dwarf mines, below the level-32 gate 32510,31956,13 and its hole): "the quest boxes
	-- are at the far south end", dwarven axe and war hammer (TibiaWiki 2005/2006, Tibiantis). The west and east boxes
	-- 32512/32514,31944,14 (tibiaot74's), with the real-map table's ids: "[3812] = {{2435}}, -- dwarven axe",
	-- "[3813] = {{2391}}, -- war hammer".
	[3812] = {{2435, 1}},
	[3813] = {{2391, 1}},
	-- Emperor's Cookies Quest (Kazordoon, Emperor Kruzak's chambers). TibiaWiki 2006: key 3800 "at the end of the
	-- 'secret passage' exit, in a chest" (32605,31908,3); "open the door of the small room in the emperor's chamber with
	-- the key. In the chest in the room you opened will be 7 and 20 Cookies and Key 3801" (door 32645,31906,3, chest
	-- 32648,31905,3; the infobox: "a bag with 20+7 cookies & Key 3801"); "at the barracks you can open the door with
	-- Key 3801, in the chest will be the key, Key 3802" (door 32600,31926,6, chest 32599,31923,6). Doors and chests are
	-- tibiaot74's; its keys are 2030/2031, the wiki's 3800/3801. The real-map table's ids ([3808] key 3800, [3809]
	-- key 3801, [3810] 27 cookies + key 3802) with the wiki's contents - the wiki names the chest of each.
	[3808] = {{2089, 1, 3800}},
	[3809] = {{1987, 1, nil, {{2687, 20}, {2687, 7}, {2089, 1, 3801}}}},
	[3810] = {{2089, 1, 3802}},
	-- Explorer Brooch Quest (Kazordoon, below the four sewer grates north in the Jolly Axeman tavern): "Go down, kill rat
	-- and take Explorer Brooch from body" (TibiaWiki). The explorer brooch came with the Explorer Society in 7.6; it "looks
	-- the same as the Elven Brooch" - the 7.4 item it is here (decided with the user 2026-09-26). The dead human
	-- 32636,31873,10 is tibiaot74's; our map had lost it.
	[51078] = {{2122, 1}},
	-- Iron Hammer Quest (minotaur cave below the loose stone pile west of Kazordoon): "The quest box is between the beds"
	-- (TibiaWiki 2005/2006) - the box 32434,31938,8 (tibiaot74's; our map had lost it), real-map table "[3807] =
	-- {{2422}}, -- iron hammer".
	[3807] = {{2422, 1}},
	-- Steel Helmet Quest (the minotaur tower west of Kazordoon, roped up into from the cave below the loose stone pile).
	-- TibiaWiki 2005: steel helmet, 47 gp, 56 gp, a scroll, "in various dressers and chests in the tower"; the current
	-- spoiler places them: 56 gp in the drawers next to a table (32460,31951,5), the steel helmet in a box next to an
	-- anvil (32462,31947,4 - our map had lost it, tibiaot74's spot), 47 gp between two beds (32464,31957,5), the Horned
	-- Fox's scroll in a chest between a bed and a table (32467,31962,4). The real-map table's ids and the scroll's text.
	[3800] = {{2148, 56}},
	[3801] = {{2148, 47}},
	[3802] = {{2457, 1}},
	[3803] = {{1949, 1, nil, nil, "Looks like the fox is out!\nMore luck next time!\nSigned:\nthe horned fox"}},
	-- Longsword Quest (troll cave east of the Dwarf Bridge, down the hidden hole behind a tree): "The quest boxes are on
	-- the north end of the large room" (TibiaWiki 2006) - the chest and two boxes 32643,31969 / 32644,31968 /
	-- 32648,31970,8. Longsword, mirror, 3 blank runes, wooden doll, wedding ring, 76 gp (all sources), split as the
	-- real-map table's three ids: "[3804] = {{2397},{2560}}, -- long sword, mirror", "[3805] = {{2260,3},{2108}}",
	-- "[3806] = {{2121},{2148,76}}" (which container holds which is not written anywhere: west to east). Blank runes
	-- do not stack in 7.4: three of them.
	[3804] = {{2397, 1}, {2560, 1}},
	[3805] = {{2260, 1}, {2260, 1}, {2260, 1}, {2108, 1}},
	[3806] = {{2121, 1}, {2148, 76}},
	-- Crusader Helmet Quest (deep Kazordoon mines, through the level-35 gate 32475,31946,13 and down its hole): "The
	-- reward is in a skeleton body at the far west end of the tunnel" - the slain skeleton 32427,31943,14. Crusader
	-- helmet: TibiaWiki 2005 and 2006 and the real-map table ("[10034] = {{2947}}, -- crusader helmet" - its item id is a
	-- dead elf, the comment is the reward); only Tibiantis says dwarven helmet.
	[10034] = {{2497, 1}},
	-- The Paradox Tower Quest: the treasure room's four chests 32477-32480,31900,1 (tibiaot74's order: phoenix egg, 10k,
	-- 32 talons, wand). Two of the four: the switch plates in front of them destroy the others (their storage is set,
	-- movements/scripts/paradox_tower.lua). The wand is the wooden wand (TibiaWiki 2005 and Tibiantis; the 2006 wiki's
	-- wand of cosmic energy is later) and the 10k 100 platinum coins - both decided with the user 2026-09-26.
	[51091] = {{2328, 1}},
	[51092] = {{2152, 100}},
	[51093] = {{2151, 32}},
	[51094] = {{2181, 1}},
}

-- Map objects that are the same quest as another (one reward per character between them): unique id -> the
-- quest's unique id, used as storage and reward.
local SAME_QUEST = {
	-- Annihilator Quest (Edron Hero Cave): four chests, one reward per character ("You can only enter this door
	-- once, so choose your reward wisely", TibiaWiki 2005) - all four count as the first one's storage.
	[51013] = 51012, [51014] = 51012, [51015] = 51012,
	-- Banana Quest (Rookgaard): the palm on the premium wolf hill (31983,32193,5; TibiaWiki: 3 boxes to climb)
	-- shares the quest id of the north-east palm, uid 2676 = the banana (Tibiantis.life).
	[52414] = 2676,
}

-- Map objects that open only when nothing lies on them: unique id -> {item id, position}. The Parchment Room coffin
-- is an always-on-top item, so it would be used through its seal; tibiaot74 gives nothing while the seal is there
-- (moving the seal is what calls the demons: movements/scripts/parchment_room_seal.lua).
local SEALED_BY = {
	[10057] = {1953, {x=33063, y=31624, z=15}},
}

local function describe(itemid, count)
	local info = getItemDescriptions(itemid) or {}
	if isItemFluidContainer(itemid) and count > 0 then
		-- as the look text says it (item.cpp: "a vial of mana fluid"): the fluid is the name of item id = its type
		local article = (info.article ~= nil and info.article ~= "") and (info.article .. " ") or ""
		return article .. getItemName(itemid) .. " of " .. getItemName(count)
	end
	if count > 1 and not isItemStackable(itemid) then
		count = 1            -- for a rune the "count" is its charges
	end
	if count > 1 then
		return count .. " " .. (info.plural ~= nil and info.plural ~= "" and info.plural or getItemName(itemid))
	end
	local article = (info.article ~= nil and info.article ~= "") and (info.article .. " ") or ""
	return article .. getItemName(itemid)
end

local function copyInto(container, source)
	for slot = getContainerSize(source.uid) - 1, 0, -1 do
		local inner = getContainerItem(source.uid, slot)
		if inner.itemid > 0 then
			local copy = doAddContainerItem(container, inner.itemid, math.max(inner.type, 1))
			if inner.actionid ~= nil and inner.actionid > 0 then
				doSetItemActionId(copy, inner.actionid)   -- quest keys open their door by action id
			end
			if isContainer(inner.uid) then
				copyInto(copy, inner)
			end
		end
	end
end

-- one reward: {itemid, count, source} (source = the map item to copy contents / action id from)
local function give(cid, reward)
	local uid = doPlayerAddItem(cid, reward.itemid, reward.count, false)
	if not uid or uid == 0 or uid == false then
		return nil
	end
	if reward.actionid ~= nil and reward.actionid > 0 then
		doSetItemActionId(uid, reward.actionid)           -- a key: its number is the door it opens
	end
	if reward.text ~= nil then
		doSetItemText(uid, reward.text)
	end
	for _, inner in ipairs(reward.contents or {}) do    -- a container that comes filled (REWARDS): {id, count, key, text}
		local added = doAddContainerItem(uid, inner[1], inner[2] or 1)
		if added ~= nil and added ~= false and added > 0 then
			if inner[3] ~= nil then
				doSetItemActionId(added, inner[3])         -- a key inside the bag
			end
			if inner[4] ~= nil then
				doSetItemText(added, inner[4])
			end
		end
	end
	if reward.source ~= nil then
		if reward.source.actionid ~= nil and reward.source.actionid > 0 then
			doSetItemActionId(uid, reward.source.actionid)
		end
		if isContainer(reward.source.uid) then
			copyInto(uid, reward.source)
		end
	end
	return uid
end

function onUse(cid, item, frompos, item2, topos)
	local storage = SAME_QUEST[item.uid] or item.uid
	local seal = SEALED_BY[item.uid]
	if seal ~= nil and getTileItemById(seal[2], seal[1]).uid > 0 then
		doPlayerSendCancel(cid, "Sorry, not possible.")
		return true
	end
	local name = getItemName(item.itemid)
	if getPlayerStorageValue(cid, storage) > 0 then
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "The " .. name .. " is empty.")
		return true
	end

	local rewards = {}
	-- the object's own reward first: objects sharing one storage (SAME_QUEST, e.g. the Annihilator's four chests,
	-- one of which a character may take) can each give something else
	local rewardList = REWARDS[item.uid] or REWARDS[storage]
	if rewardList ~= nil then
		for _, r in ipairs(rewardList) do
			table.insert(rewards, {itemid = r[1], count = r[2] or 1, actionid = r[3], contents = r[4], text = r[5]})
		end
	elseif storage < ITEM_ID_LIMIT then
		rewards[1] = {itemid = storage, count = 1}
	elseif isContainer(item.uid) then
		for slot = getContainerSize(item.uid) - 1, 0, -1 do
			local inner = getContainerItem(item.uid, slot)
			if inner.itemid > 0 then
				table.insert(rewards, {itemid = inner.itemid, count = math.max(inner.type, 1), source = inner})
			end
		end
	end

	if #rewards == 0 then
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "The " .. name .. " is empty.")
		return true
	end

	-- all or nothing: a part given before one that does not fit is taken back, or the chest could be looted
	-- again and again for that part
	local given = {}
	for _, reward in ipairs(rewards) do
		local uid = give(cid, reward)
		if uid == nil then
			for _, g in ipairs(given) do
				doRemoveItem(g.uid, g.count)   -- only what was given: gold may have joined a stack they had
			end
			doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "You have found " .. describe(reward.itemid, reward.count)
				.. ", but you cannot carry it.")
			return true
		end
		table.insert(given, {uid = uid, count = reward.count})
	end
	for _, reward in ipairs(rewards) do
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "You have found " .. describe(reward.itemid, reward.count) .. ".")
	end
	setPlayerStorageValue(cid, storage, 1)
	return true
end

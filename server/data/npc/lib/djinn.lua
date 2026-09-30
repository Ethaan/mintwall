-- The Djinn War (docs/reference-74/quests.md, "The Djinn War - Efreet Faction" / "- Marid Faction"): what the djinn
-- NPCs, the Orc King, Partos, Maryza and the fortresses' quest objects share.
--
-- TibiaWiki 2006 (the 7.x transcripts): every djinn is greeted with the word of greeting DJANNI'HAH "instead of 'hi'";
-- Melchior: "They will not talk to human unless he says the word of greeting first ... Otherwise he will simply ignore
-- you or worse - if it is an Efreet he will kill you outright"; Rata'mari answers the password PIEDPIPER. "Once you
-- decided to follow one group of djinns you can never switch sides ... No Efreet will ever deal with a follower of the
-- Marid and vice versa." Yaman (TibiaWiki 2006) "will not trade with them until he has permission from Malor".
-- Decided with the user 2026-09-29: DJANNI'HAH only, as in 7.4; the traders trade once the player finished his side.
--
-- Storages above 65535: no map unique id (a quest chest's storage) can clash - the old keys 1015, 1026, 1029, 1032 and
-- 1034 were chests' too (the Triple UH chest counted as the Marid side done).
DJINN_EFREET = 70100      -- progress on the Efreet side (EFREET_*)
DJINN_MARID = 70101       -- progress on the Marid side (MARID_*)
DJINN_WORD = 70102        -- 1: Melchior told the word of greeting
DJINN_ORC_GUARDS = 70103  -- 1: the Orc King called his guards on this player ("the first time you say 'hi'")

EFREET_PLEDGED = 1        -- Ubaid: "welcome to Mal'ouquah"
EFREET_THIEF = 2          -- Baa'leal: find the supply thief in Carlin
EFREET_PARTOS = 3         -- Partos: "I bet, Baa'leal sent you!"
EFREET_PAID = 4           -- Baa'leal: the thief is Partos, 600 gold; Alesar has a mission
EFREET_TEAR = 5           -- Alesar: steal a Tear of Daraman from Ashta'daramai
EFREET_TEAR_GIVEN = 6     -- Alesar has the tear; Malor has a mission
EFREET_LAMP = 7           -- Malor: Fa'hradin's lamp from the Orc King into Gabel's chambers
EFREET_LAMP_PLACED = 8    -- the lamp is by Gabel's bed
EFREET_DONE = 9           -- Malor: permission to trade with Alesar and Yaman

MARID_PLEDGED = 1         -- Umar: "You may pass"
MARID_COOKBOOK = 2        -- Bo'ques: bring a dwarven cookbook
MARID_BOOK_GIVEN = 3      -- Bo'ques has it (3 small sapphires); Fa'hradin has work
MARID_SPY = 4             -- Fa'hradin: the spy report from Mal'ouquah, password PIEDPIPER
MARID_CHEESE = 5          -- Rata'mari wants a cheese for the report
MARID_REPORT = 6          -- Rata'mari gave the report
MARID_REPORT_GIVEN = 7    -- Fa'hradin has the report; talk to Gabel
MARID_LAMP = 8            -- Gabel: Fa'hradin's lamp from the Orc King into Malor's chambers
MARID_LAMP_PLACED = 9     -- the lamp is by Malor's bed
MARID_DONE = 10           -- Gabel: welcome to trade with Haroun and Nah'bob

FAHRADINS_LAMP = 2344     -- "a gemmed lamp", the one the Orc King gives
SPY_REPORT = 2345
TEAR_OF_DARAMAN = 2346
COOKBOOK = 2347
CHEESE = 2696

function djinnProgress(cid, side)
	local value = getPlayerStorageValue(cid, side)
	return value > 0 and value or 0
end

-- The side the player follows (DJINN_EFREET, DJINN_MARID), or nil.
function djinnFollower(cid)
	if djinnProgress(cid, DJINN_EFREET) > 0 then
		return DJINN_EFREET
	elseif djinnProgress(cid, DJINN_MARID) > 0 then
		return DJINN_MARID
	end
	return nil
end

function djinnCarries(cid, itemid)
	return getPlayerItemCount(cid, itemid) > 0
end

dofile(getDataDir() .. 'npc/lib/questnpc.lua')
djinnNpc = questNpc
djinnSay = questSay

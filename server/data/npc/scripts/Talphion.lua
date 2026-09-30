-- Talphion the technomancer in Kazordoon, hard of hearing (The Postman Missions Quest, mission 6; npc/lib/postman.lua).
-- TibiaWiki 2006 transcript: "new dress patterns" five times - four mishearings, then "I'LL SENT A COPY TO KEVIN
-- IMEDIATELY!". The old port had no greeting, heard only "dress pattern" and once per character only.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local HEARD = {
	"DRESS FLATTEN? WHO WANTS ME TO FLATTEN A DRESS?",
	"A PRESS LANTERN? NEVER HEARD ABOUT IT!",
	"CHESS? I DONT PLAY CHESS!",
	"A PATTERN IN THIS MESS?? HEY DON'T INSULT MY MACHINEHALL!",
}

questNpc{
	farewell = "GOOD BYE!",
	walkaway = "GOOD BYE!",
	greet = function(cid)
		return "HIHOOOO |PLAYERNAME|! <waves his hands>"
	end,
	quest = function(cid, msg, state, say)
		if postmanProgress(cid) ~= POSTMAN_TALPHION or not (containsWord(msg, "dress pattern")
				or containsWord(msg, "dress patterns")) then
			return false
		end
		if state.topic < #HEARD then
			state.topic = state.topic + 1
			say(cid, HEARD[state.topic])
		else
			state.topic = 0
			setPlayerStorageValue(cid, POSTMAN, POSTMAN_TALPHION_DONE)
			say(cid, "AH YES! I WORKED ON THE DRESS PATTERN FOR THOSE UNIFORMS. STAINLESS TROUSERES, STEAM DRIVEN BOOTS! ANOTHER MARVEL TO BEHOLD! I'LL SENT A COPY TO KEVIN IMEDIATELY!")
		end
		return true
	end,
}

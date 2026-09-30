-- Chrystal, the Edron post officer (The Postman Missions Quest, mission 7: the post officers' measurements, in any order - TibiaWiki 2006;
-- npc/lib/postman.lua). Transcript: "measurements" - "If its necessary ... <tells you her measurements>". The old port forced an order (250 = n) and kept its topic in a global every NPC shares.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local function measuring(cid, bit)
	return postmanProgress(cid) == POSTMAN_MEASUREMENTS and not postmanHas(cid, POSTMAN_MEASURES, bit)
end

questNpc{
	quest = function(cid, msg, state, say)
		if containsWord(msg, "measurements") and measuring(cid, POSTMAN_OFFICERS.chrystal) then
			postmanSet(cid, POSTMAN_MEASURES, POSTMAN_OFFICERS.chrystal)
			say(cid, "If its necessary ... <tells you her measurements>")
			return true
		end
		return false
	end,
}

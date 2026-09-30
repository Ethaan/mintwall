-- Benjamin, the Thais post officer (The Postman Missions Quest, mission 7: the post officers' measurements, in any order - TibiaWiki 2006;
-- npc/lib/postman.lua). Transcript: "measurements" - "Oh they dont change that much since in the old days as... <tells a boring and confusing story ...>". The old port forced an order (250 = n) and kept its topic in a global every NPC shares.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local function measuring(cid, bit)
	return postmanProgress(cid) == POSTMAN_MEASUREMENTS and not postmanHas(cid, POSTMAN_MEASURES, bit)
end

questNpc{
	quest = function(cid, msg, state, say)
		if containsWord(msg, "measurements") and measuring(cid, POSTMAN_OFFICERS.benjamin) then
			postmanSet(cid, POSTMAN_MEASURES, POSTMAN_OFFICERS.benjamin)
			say(cid, "Oh they dont change that much since in the old days as... <tells a boring and confusing story about a cake, a parcel, himself and two squirrels, at least he tells you his measurements in the end>")
			return true
		end
		return false
	end,
}

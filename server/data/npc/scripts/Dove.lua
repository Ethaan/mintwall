-- Dove, the Venore post officer (The Postman Missions Quest, mission 7: the post officers' measurements, in any order - TibiaWiki 2006;
-- npc/lib/postman.lua). Transcript: "measurements" - above the allowed weight: "Do you happen to have some grapes with you?"; "yes" - "Oh thank you! ... <whispers her measurements>". The old port forced an order (250 = n) and kept its topic in a global every NPC shares.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local function measuring(cid, bit)
	return postmanProgress(cid) == POSTMAN_MEASUREMENTS and not postmanHas(cid, POSTMAN_MEASURES, bit)
end

local GRAPES = 2681

questNpc{
	quest = function(cid, msg, state, say)
		if containsWord(msg, "measurements") and measuring(cid, POSTMAN_OFFICERS.dove) then
			state.topic = 1
			say(cid, "Oh no! I knew that day would come! I am slightly above the allowed weight and if you can't supply me with some grapes to slim down I will get fired. Do you happen to have some grapes with you?")
			return true
		elseif state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			if doPlayerRemoveItem(cid, GRAPES, 1) then
				postmanSet(cid, POSTMAN_MEASURES, POSTMAN_OFFICERS.dove)
				say(cid, "Oh thank you! Thank you so much! So listen ... <whispers her measurements>")
			else
				say(cid, "You don't have any grapes with you.")
			end
			return true
		elseif state.topic == 1 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Oh no! I will get fired!")
			return true
		end
		return false
	end,
}

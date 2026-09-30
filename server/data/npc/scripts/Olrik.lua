-- Olrik, the Ab'Dendriel post officer (The Postman Missions Quest, mission 7: the post officers' measurements, in any order - TibiaWiki 2006;
-- npc/lib/postman.lua). Transcript: "measurements" - "let's gamble. I will roll a dice. If I roll a 6 you win ..., else I win and get 5 gold. Deal?"; "yes" until a 6. The old port forced an order (250 = n) and kept its topic in a global every NPC shares.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local function measuring(cid, bit)
	return postmanProgress(cid) == POSTMAN_MEASUREMENTS and not postmanHas(cid, POSTMAN_MEASURES, bit)
end

questNpc{
	quest = function(cid, msg, state, say)
		if containsWord(msg, "measurements") and measuring(cid, POSTMAN_OFFICERS.olrik) then
			state.topic = 1
			say(cid, "My measurements? Listen, lets make that a bit more exciting ... No, no, not what you think! I mean let's gamble. I will roll a dice. If I roll a 6 you win and I'll tell you what you need to know, else I win and get 5 gold. Deal?")
			return true
		elseif state.topic == 1 and containsWord(msg, "yes") then
			if not doPlayerRemoveMoney(cid, 5) then
				state.topic = 0
				say(cid, "You don't even have 5 gold.")
				return true
			end
			local roll = math.random(1, 6)
			if roll == 6 then
				state.topic = 0
				doPlayerAddMoney(cid, 5)                   -- he won nothing
				postmanSet(cid, POSTMAN_MEASURES, POSTMAN_OFFICERS.olrik)
				say(cid, "Ok, here we go ... 6! You have won! How lucky you are! So listen ... <tells you what you need to know>")
			else
				say(cid, "Ok, and its ... " .. roll .. "! You have lost. He he. Another game?")
			end
			return true
		elseif state.topic == 1 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Chicken.")
			return true
		end
		return false
	end,
}

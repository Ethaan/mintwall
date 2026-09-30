-- Liane, the Carlin post officer (The Postman Missions Quest, mission 7: the post officers' measurements, in any order - TibiaWiki 2006;
-- npc/lib/postman.lua). Transcript: "measurements" - hawks hunt her carrier pigeons: "Do you have 12 arrows with you?"; "yes" - "Great! Now I'll teach them a lesson ...". The old port forced an order (250 = n) and kept its topic in a global every NPC shares.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local function measuring(cid, bit)
	return postmanProgress(cid) == POSTMAN_MEASUREMENTS and not postmanHas(cid, POSTMAN_MEASURES, bit)
end

local ARROW = 2544

questNpc{
	quest = function(cid, msg, state, say)
		if containsWord(msg, "measurements") and measuring(cid, POSTMAN_OFFICERS.liane) then
			state.topic = 1
			say(cid, "I have more urgent problem to attend then that. Those hawks are hunting my carrier pigeons. Bring me 12 arrows and I'll see if I have the time for this nonsense. Do you have 12 arrows with you?")
			return true
		elseif state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			if getPlayerItemCount(cid, ARROW) >= 12 and doPlayerRemoveItem(cid, ARROW, 12) then
				postmanSet(cid, POSTMAN_MEASURES, POSTMAN_OFFICERS.liane)
				say(cid, "Great! Now I'll teach them a lesson ... For those measurements ... <tells you her measurements>")
			else
				say(cid, "You don't have 12 arrows with you.")
			end
			return true
		elseif state.topic == 1 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Then come back when you have them.")
			return true
		end
		return false
	end,
}

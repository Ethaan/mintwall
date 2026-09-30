-- Noodles, King Tibianus's dog (The Postman Missions Quest, mission 6; npc/lib/postman.lua). TibiaWiki 2006 transcript:
-- "sniff banana skin" / "sniff dirty fur" / "sniff moldy cheese", then "do you like that?" - "Woof!" twice, the cheese
-- "Meeep! Grrrrr! <spits>". Decided with the user 2026-09-30: any order, the player must carry what he sniffs, nothing
-- is taken; the cheese reaction is what Kevin wants to know. The old port had no greeting and forced the order.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local SMELLS = {
	{words = {"banana skin", "bananaskin"}, item = 2219, bit = 1, reaction = "Woof!"},
	{words = {"dirty fur", "piece of fur", "fur"}, item = 2220, bit = 2, reaction = "Woof!"},
	{words = {"moldy cheese", "mouldy cheese", "cheese"}, item = 2235, bit = 4, reaction = "Meeep! Grrrrr! <spits>"},
}

questNpc{
	farewell = "Woof!",
	walkaway = "Woof!",
	greet = function(cid)
		return "<sniff> Woof! <sniff>"
	end,
	quest = function(cid, msg, state, say)
		if containsWord(msg, "sniff") then
			for n, smell in ipairs(SMELLS) do
				for _, word in ipairs(smell.words) do
					if containsWord(msg, word) and getPlayerItemCount(cid, smell.item) > 0 then
						state.topic = n
						say(cid, "<sniff><sniff>")
						return true
					end
				end
			end
			state.topic = 0
			say(cid, "<sniff>")
			return true
		elseif state.topic > 0 and containsWord(msg, "like") then
			local smell = SMELLS[state.topic]
			state.topic = 0
			say(cid, smell.reaction)
			if postmanProgress(cid) == POSTMAN_NOODLES then
				postmanSet(cid, POSTMAN_SNIFFED, smell.bit)
				if smell.bit == 4 then
					setPlayerStorageValue(cid, POSTMAN, POSTMAN_NOODLES_DONE)
				end
			end
			return true
		end
		return false
	end,
}

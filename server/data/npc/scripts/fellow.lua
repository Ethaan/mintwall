-- A Strange Fellow below the Venore depot - the stage magician David Brassacres, hiding from his creditors (The Postman
-- Missions Quest, mission 3; npc/lib/postman.lua). TibiaWiki 2006 transcript: "hat" four times, "bill", "yes" (rabbits
-- appear: "Still I am better in vanishing!" - the wiki). The old port had no greeting at all, kept its topic in a
-- global every NPC shares and could be asked about the hat once per character only.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local HAT = {
	"What? My hat?? Theres... nothing special about it!",
	"Stop bugging me about that hat, do you listen?",
	"Hey! Don't touch that hat! Leave it alone!!! Don't do this!!!!",
	"Noooooo! Argh, ok, ok, I guess I can't deny it anymore, I am David Brassacres, the magnificent, so what do you want?",
}

questNpc{
	farewell = "Finally.",
	walkaway = "Finally.",
	greet = function(cid)
		return "Uh? What do you want?!"
	end,
	quest = function(cid, msg, state, say)
		if postmanProgress(cid) ~= POSTMAN_BILL then
			return false
		end
		if containsWord(msg, "hat") and state.topic < #HAT then
			state.topic = state.topic + 1
			say(cid, HAT[state.topic])
			return true
		elseif containsWord(msg, "bill") and state.topic == #HAT then
			state.topic = #HAT + 1
			say(cid, "A bill? Oh boy so you are delivering another bill to poor me?")
			return true
		elseif containsWord(msg, "yes") and state.topic == #HAT + 1 then
			state.topic = 0
			setPlayerStorageValue(cid, POSTMAN, POSTMAN_BILL_DELIVERED)
			say(cid, {"Ok, ok, I'll take it. I guess I have no other choice anyways. And now leave me alone in my misery please.",
				"Still I am better in vanishing!"})
			local pos = getCreaturePosition(getNpcCid())
			for _, d in ipairs({{-1, 0}, {1, 0}, {0, 1}, {0, -1}}) do
				local at = {x = pos.x + d[1], y = pos.y + d[2], z = pos.z}
				if getTopCreature(at).uid == 0 then
					doSummonCreature("Rabbit", at)
				end
			end
			return true
		end
		return false
	end,
}

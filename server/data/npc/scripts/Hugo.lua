-- Hugo Chief, the tailor upstairs of the Venore clothes shop (The Postman Missions Quest, mission 6;
-- npc/lib/postman.lua). TibiaWiki 2006 transcript: "new set of uniforms" - his dog ate the last dress pattern; "new
-- dress pattern" - "I have no clue where Kevin Postner got it from"; at the end "new dress pattern" - "Ok, ok, you will
-- get those ugly, stinking uniforms". The old port kept its topic in a global every NPC shares.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

questNpc{
	farewell = "Good bye.",
	walkaway = "Good bye.",
	greet = function(cid)
		return "Be greeted, |PLAYERNAME|!"
	end,
	quest = function(cid, msg, state, say)
		local progress = postmanProgress(cid)
		if containsWord(msg, "uniforms") or containsWord(msg, "uniform") then
			if progress == POSTMAN_UNIFORMS then
				state.topic = 1
				say(cid, "A new uniform for the post officers? I am sorry but my dog ate the last dress pattern we used. You need to supply us with a new dress pattern.")
				return true
			end
		elseif containsWord(msg, "dress pattern") or containsWord(msg, "dress patterns") then
			if progress == POSTMAN_UNIFORMS then
				state.topic = 0
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_HUGO_ASKED)
				say(cid, "It was ... wonderous beyond wildest imaginations! I have no clue where Kevin Postner got it from. Better ask him.")
				return true
			elseif progress == POSTMAN_HUGO_ORDER then
				state.topic = 0
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_UNIFORMS_DONE)
				say(cid, "By the gods of fashion! Didn't it do that I fed the last dress pattern to my poor dog? Will this mocking of all which is taste and fashion never stop?? Ok, ok, you will get those ugly, stinking uniforms and now get lost, fashion terrorist.")
				return true
			end
		end
		return false
	end,
}

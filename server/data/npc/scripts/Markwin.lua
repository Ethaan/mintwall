-- Markwin, the king of Mintwallin (The Postman Missions Quest, mission 10; npc/lib/postman.lua). TibiaWiki 2006: "As
-- soon as you say 'hi' to Markwin, he will call for his bodyguards ... 2 Minotaur Archers, 2 Minotaur Guards, and 2
-- Minotaur Mages ... Once you prove yourself handling them, you can give him his letter." Decided with the user
-- 2026-09-30: he takes the letter only once the bodyguards he called are dead. His lines are the old port's (it burned
-- players on "bye" - no source - and counted a second "hi" as proof).
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local BODYGUARDS = {{"Minotaur Guard", -1, -1}, {"Minotaur Guard", 1, -1}, {"Minotaur Archer", -1, 1},
	{"Minotaur Archer", 1, 1}, {"Minotaur Mage", -1, 0}, {"Minotaur Mage", 1, 0}}
local called = {}                              -- player -> the bodyguards he called on them (creature ids)

local function guardsAlive(cid)
	for _, guard in ipairs(called[cid] or {}) do
		if isCreature(guard) then
			return true
		end
	end
	return false
end

questNpc{
	farewell = "Hm ... good bye.",
	walkaway = "Hm ... good bye.",
	greet = function(cid, say)
		if getPlayerStorageValue(cid, POSTMAN_MARKWIN) < 1 then
			setPlayerStorageValue(cid, POSTMAN_MARKWIN, 1)
			say(cid, "Intruder! Guards, take him down!", true)
			local pos = getCreaturePosition(getNpcCid())
			called[cid] = {}
			for _, guard in ipairs(BODYGUARDS) do
				local at = {x = pos.x + guard[2], y = pos.y + guard[3], z = pos.z}
				if getTopCreature(at).uid == 0 then
					local id = doSummonCreature(guard[1], at)
					if id and id ~= 0 then
						table.insert(called[cid], id)
					end
					doSendMagicEffect(at, CONST_ME_ENERGYAREA)
				end
			end
			return nil
		elseif guardsAlive(cid) then
			say(cid, "Guards! Take him down!", true)
			return nil
		elseif getPlayerStorageValue(cid, POSTMAN_MARKWIN) == 1 then
			setPlayerStorageValue(cid, POSTMAN_MARKWIN, 2)
			return "Well ... you defeated my guards! Now everything is over! I guess I will have to answer your questions now."
		end
		return "Oh its you again. What du you want, hornless messenger?"
	end,
	quest = function(cid, msg, state, say)
		if containsWord(msg, "letter") and postmanProgress(cid) == POSTMAN_MARKWIN_LETTER then
			state.topic = 1
			say(cid, "A letter from my Moohmy?? Do you have a letter from my Moohmy to me?")
			return true
		elseif state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			if doPlayerRemoveItem(cid, LETTER_TO_MARKWIN, 1) then
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_MARKWIN_DONE)
				say(cid, "Uhm, well thank you, hornless being.")
			else
				say(cid, "You don't have it! Do not mock me, hornless being!")
			end
			return true
		end
		return false
	end,
}

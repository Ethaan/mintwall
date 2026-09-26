local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- The Queen of the Banshees, guardian of the seventh seal (docs/reference-74/quests.md). Her words: TibiaWiki "The Queen
-- Of The Banshees/Transcripts". She asks after the six seals in this order, and gives her kiss - the seventh seal - to
-- a character of level 60 or more who passed them all; then "You will be teleported to your grave" (TibiaWiki 2006):
-- the room under the grave "In honor of those, killed for a kiss" (32202,31810,7; tibiaot74 uses the same room).
-- Lines the transcripts do not give (a missing seal, too low a level, no, a player with blood on their hands) are
-- tibiaot74's banshee_queen.lua, its typos mended. The seals: movements/scripts/banshee_seals.lua.
local SEAL = {HIDDEN = 51101, PLAGUE = 51102, DEMONRAGE = 51103, SACRIFICE = 51104, TRUE_PATH = 51105, LOGIC = 51106,
              KISS = 51107}
local LEVEL = 60
local GRAVE = {x=32202, y=31812, z=8}

-- yes number n: the seal she senses, what she says, what she says when it is missing
local SEALS_ASKED = {
	{SEAL.SACRIFICE, "Yessss, I can sense you have passed the Seal of Sacrifice. Have you passed any other seal yet?",
	 "You have not passed the Seal of Sacrifice yet. Return to me when you are better prepared."},
	{SEAL.HIDDEN, "I sense you have passed the Hidden Seal as well. Have you passed any other seal yet?",
	 "You have not found the Hidden Seal yet. Return when you are better prepared."},
	{SEAL.PLAGUE, "Oh yes, you have braved the Plague Seal. Have you passed any other seal yet?",
	 "You have not faced the Plague Seal yet. Return to me when you are better prepared."},
	{SEAL.DEMONRAGE, "Ah, I can sense the power of the Seal of Demonrage burning in your heart. Have you passed any other seal yet?",
	 "You are not filled with the fury of the imprisoned demon. Return when you are better prepared."},
	{SEAL.TRUE_PATH, "So, you have managed to pass the Seal of the True Path. Have you passed any other seal yet?",
	 "You have not found your true path yet. Return when you are better prepared."},
	{SEAL.LOGIC, "I see! You have mastered the Seal of Logic. You have made the sacrifice, you have seen the unseen, you possess fortitude, you have filled yourself with power and found your path. You may ask me for my kiss now.",
	 "You have not mastered the Seal of Logic yet. Return to me when you are better prepared."},
}
local ALL_SEALS = #SEALS_ASKED + 1   -- state after the last yes: she may be asked for her kiss
local ASKED_KISS = 20

local TALK = {
	{{"stay"}, "It's my curse to be the eternal guardian of this ancient place."},
	{{"guardian"}, "I'm the guardian of the SEVENTH and final seal. The seal to open the last door before ... but perhaps it's better to see it with your own eyes."},
	{{"place"}, "It served as a temple, a source of power and ... as a sender for an ancient race which lived a long time ago and has long been forgotten."},
	{{"race"}, "The race that built this edifice came to this place from the stars. They ran from an enemy even more horrible than themselves. But they carried the seed of their own destruction in them."},
	{{"seed"}, "This ancient race was annihilated by its own doings, that's all I know. Aeons have passed since then, but the sheer presence of this complex is still defiling and desecrating this area."},
	{{"complex"}, "Its constructors were too strange for you or even me to understand. We don't know what this ... thing they built was supposed to be good for. I feel a constant twisting and binding of souls, though, that is probably only a side-effect."},
	{{"ghostlands"}, "The place you know as the Ghostlands had a different name once ... and many names after. Too many to remember them all."},
	{{"banshee"}, "They are my maidens. They give me comfort in my eternal watch over the last seal."},
	{{"name"}, "It hurts me to even think about my mortal past. Its long lost and forgotten. So don't ask me about it!"},
}

local talkState = {}

local function says(msg, words)
	for _, w in ipairs(words) do
		if msgcontains(msg, w) then
			return true
		end
	end
	return false
end

function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	local state = talkState[cid] or 0
	local nextState = 0

	if msgcontains(msg, "seventh") or msgcontains(msg, "last") then
		if getPlayerLevel(cid) < LEVEL then
			npcHandler:say("You are not experienced enough to master the challenges ahead or to receive knowledge about the seventh seal. Go and learn more before asking me again.", cid)
		else
			npcHandler:say("If you have passed the first six seals and entered the blue fires leading to the seals' chambers, you are ready to receive my kiss ... It will open the last seal. Do you think you are ready?", cid)
			nextState = 1
		end
	elseif msgcontains(msg, "kiss") then
		if getPlayerStorageValue(cid, SEAL.KISS) > 0 then
			npcHandler:say("You've already received my kiss. You should know better than to ask for it.", cid)
		elseif state == ALL_SEALS then
			npcHandler:say("Are you prepared to receive my kiss, even though this means that your death as well as a part of your soul will forever belong to me, my dear?", cid)
			nextState = ASKED_KISS
		else
			npcHandler:say("To receive my kiss you have to pass all other seals first.", cid)
		end
	elseif msgcontains(msg, "yes") and state >= 1 and state <= #SEALS_ASKED then
		local asked = SEALS_ASKED[state]
		if getPlayerStorageValue(cid, asked[1]) == 1 then
			npcHandler:say(asked[2], cid)
			nextState = state + 1
		else
			npcHandler:say(asked[3], cid)
		end
	elseif msgcontains(msg, "yes") and state == ASKED_KISS then
		if isPzLocked(cid) then
			npcHandler:say("You have spilled too much blood recently and the dead are hungry for your soul. Perhaps return when you regained your inner balance.", cid)
		else
			npcHandler:say("So be it! Hmmmmmm...", cid)
			setPlayerStorageValue(cid, SEAL.KISS, 1)
			npcHandler:releaseFocus(cid)
			doTeleportThing(cid, GRAVE)
			doSendMagicEffect(GRAVE, CONST_ME_ENERGYAREA)
		end
	elseif msgcontains(msg, "no") and state == ASKED_KISS then
		npcHandler:say("Perhaps it is the better choice for you, my dear.", cid)
	elseif msgcontains(msg, "no") and state >= 1 and state <= #SEALS_ASKED then
		npcHandler:say("Then try to be better prepared next time we meet.", cid)
	else
		for _, entry in ipairs(TALK) do
			if says(msg, entry[1]) then
				npcHandler:say(entry[2], cid)
				break
			end
		end
		if state == ALL_SEALS then
			nextState = ALL_SEALS              -- other talk does not undo what she sensed
		end
	end
	talkState[cid] = nextState
	return true
end

npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())

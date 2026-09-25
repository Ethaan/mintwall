local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Dalbrect Windtrouser, the fisher at the port north-west of Carlin. White Raven Monastery Quest part 1
-- (docs/reference-74/quests.md; TibiaWiki "Dalbrect/Transcripts" and the quest spoiler): the family brooch from the
-- coffin under the Ghostlands makes him your friend (he keeps the brooch), then "passage" sails you to the Isle of
-- the Kings for 10 gold (Dalbrect infobox 2006: 10 gp there; Captain Jack on the Isle sails back for 20). Lines the
-- transcripts do not give: the "no" to handing over the brooch reuses his "no" line, and money / pz-lock answers are
-- the other captains'. The old script shared one conversation state between all players and its in-fight check
-- never blocked (hasCondition(...) ~= 1 on a true/false result).
local BROOCH = 2318
local FRIEND = 99999              -- player storage: gave the brooch (tibiaot74's number; Captain Jack uses 99998)
local FARE = 10
local ISLE = {x = 32188, y = 31958, z = 7}   -- the deck of the boat at the Isle of the Kings (Captain Jack's)

local talkState = {}

local TALK = {
	{{"hut", "job"}, "I am merely a humble fisher now that nothing is left of my noble legacy."},
	{{"legacy", "family"}, "Once my family was once noble and wealthy, but fate turned against us and threw us into poverty."},
	{{"fate", "poverty"}, "When Carlin tried to colonise the region now known as the ghostlands, my ancestors put their fortune in that project."},
	{{"project", "ghostlands"}, "Our family fortune was lost when the colonisation of those cursed lands failed. Now nothing is left of our fame or our fortune. If I only had something as a reminder of those better times. <sigh>"},
	{{"name"}, "My name is Dalbrect Windtrouser, of the once proud Windtrouser family."},
	{{"carlin"}, "To think my family used to belong to the local nobility! And now those arrogant women are in charge!"},
	{{"ship", "boat"}, "My ship is my only pride and joy."},
	{{"island", "isle"}, "The only isle I visit regularly is the isle of the kings. I bring food and the occasional visitor to the monastery."},
	{{"monastery", "monk", "white raven"}, "The monks are not exactly fond of visitors, so I rarely take somebody there without their permission."},
}

local function says(msg, words)
	for _, w in ipairs(words) do
		if msgcontains(msg, w) then
			return true
		end
	end
	return false
end

local function isFriend(cid)
	return getPlayerStorageValue(cid, FRIEND) == 1
end

function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	local state = talkState[cid] or 0
	local nextState = 0

	if msgcontains(msg, "brooch") then
		npcHandler:say("What? You want me to examine a brooch?", cid)
		nextState = 1
	elseif msgcontains(msg, "yes") and state == 1 then
		if getPlayerItemCount(cid, BROOCH) < 1 then
			npcHandler:say("What are you talking about? I am too poor to be interested in jewelry.", cid)
		else
			npcHandler:say("Can it be? I recognise my family's arms! You have found a treasure indeed! I am poor and all I can offer you is my friendship, but ... please ... give that brooch to me?", cid)
			nextState = 2
		end
	elseif msgcontains(msg, "yes") and state == 2 then
		if doPlayerRemoveItem(cid, BROOCH, 1) then
			setPlayerStorageValue(cid, FRIEND, 1)
			npcHandler:say("Thank you! I shall consider you my friend from now on! Just let me know if you need something!", cid)
		else
			npcHandler:say("What are you talking about? I am too poor to be interested in jewelry.", cid)
		end
	elseif msgcontains(msg, "no") and (state == 1 or state == 2) then
		npcHandler:say("Then stop being a fool. I am poor and I have to work the whole day through!", cid)
	elseif msgcontains(msg, "need") and isFriend(cid) then
		npcHandler:say("There is little I can offer you but a trip with my boat. Are you looking for a passage to the isle of kings perhaps?", cid)
	elseif says(msg, {"passage", "trip", "sail"}) then
		if isFriend(cid) then
			npcHandler:say("Since you are my friend now I will sail you to the isle of the kings for " .. FARE .. " gold. Is that okay for you?", cid)
			nextState = 3
		else
			npcHandler:say("I have only sailed to the isle of the kings once or twice. I dare not anger the monks by bringing travellers there without their permission.", cid)
		end
	elseif msgcontains(msg, "yes") and state == 3 then
		if isPzLocked(cid) then
			npcHandler:say("First get rid of those blood stains! You are not going to ruin my vehicle!", cid)
		elseif not doPlayerRemoveMoney(cid, FARE) then
			npcHandler:say("You don't have enough money.", cid)
		else
			npcHandler:say("Have a nice trip!", cid)
			npcHandler:releaseFocus(cid)
			doTeleportThing(cid, ISLE)
			doSendMagicEffect(ISLE, CONST_ME_TELEPORT)
		end
	elseif msgcontains(msg, "no") and state == 3 then
		npcHandler:say("As you wish.", cid)
	else
		for _, entry in ipairs(TALK) do
			if says(msg, entry[1]) then
				npcHandler:say(entry[2], cid)
				break
			end
		end
	end
	talkState[cid] = nextState
	return true
end

npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())

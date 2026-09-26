local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Costello, abbot of the White Raven Monastery on the Isle of the Kings. TibiaWiki "Costello/Transcripts" and the White
-- Raven Monastery Quest spoiler (docs/reference-74/quests.md, part 2): "fugio", "yes" - he lets you open the warded
-- doors to the catacombs (32169,31933,7 and 32171,31936,7: quest doors, action id = storage 51110); "diary", "yes"
-- with brother Fugio's diary (the book from the dead monk in the Banshee dungeon) - he keeps it and gives the Blessed
-- Ankh (item 2327, the "ankh" among the 7.2-7.24 quest items). Trespassers on the restricted floor (storage 99998, set
-- by movements/scripts/isle_restricted.lua) get his "WHAT? ..." instead of a greeting and pay for their absolution
-- (TibiaWiki, Isle of the Kings: below level 20 500 gp, under 40 1,000, 60 and under 5,000, over 60 10,000); the
-- transcripts' lines. Lines the sources do not give: the answer without a diary or without the money, and "no".
local TRESPASSER = 99998
local WARDED_DOORS = 51110
local ANKH_GIVEN = 51111
local DIARY, BLESSED_ANKH = 1972, 2327

local TALK = {
	{{"name"}, "My name is Costello."},
	{{"job"}, "I'm the abbot of the White Raven Monastery on the Isle of the Kings."},
	{{"isle", "order"}, "We founded our monastery to guard the royal tombs and to gather wisdom and knowledge."},
	{{"wisdom"}, "You may enter the library upstairs. Don't go any further upstairs, though, as this area is reserved for members of our order."},
	{{"king"}, "The deceased leaders of the Thaian empire rest beneath this monastery in tombs and crypts."},
	{{"caves", "crypts"}, "Anselm, the first monk of our order, discovered them while looking for a suitable burial place for his king."},
	{{"anselm"}, "He was a humble and pious man, and he was chosen by the royal family of Thais to find a resting place for their dead."},
}

local talkState = {}
local ABSOLUTION = 10

local function fine(cid)
	local level = getPlayerLevel(cid)
	if level < 20 then
		return 500
	elseif level < 40 then
		return 1000
	elseif level <= 60 then
		return 5000
	end
	return 10000
end

local function trespasser(cid)
	return getPlayerStorageValue(cid, TRESPASSER) == 1
end

-- a trespasser is not welcomed
local function greetCallback(cid)
	if not trespasser(cid) then
		return true
	end
	npcHandler:changeFocus(cid)
	npcHandler:say("WHAT? You have to be that trespasser my brothers told me about! Entering the restricted area is a horrible crime!", cid)
	talkState[cid] = ABSOLUTION
	return false
end

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

	if trespasser(cid) then
		if msgcontains(msg, "crime") or msgcontains(msg, "absolution") then
			npcHandler:say("The only way to redeem such an offence is the sacrifice of " .. fine(cid) .. " gold pieces! Are you willing to pay that sum?", cid)
			talkState[cid] = ABSOLUTION + 1
		elseif msgcontains(msg, "yes") and state == ABSOLUTION + 1 then
			if doPlayerRemoveMoney(cid, fine(cid)) then
				setPlayerStorageValue(cid, TRESPASSER, -1)
				npcHandler:say("So receive your absolution! And never do such a thing again!", cid)
				talkState[cid] = 0
			else
				npcHandler:say("You don't have enough money.", cid)
				talkState[cid] = ABSOLUTION
			end
		elseif state == ABSOLUTION + 1 then
			npcHandler:say("Then be gone!", cid)
			npcHandler:releaseFocus(cid)
			talkState[cid] = 0
		else
			npcHandler:say("Be gone!", cid)
			npcHandler:releaseFocus(cid)
			talkState[cid] = 0
		end
		return true
	end

	if msgcontains(msg, "fugio") then
		npcHandler:say("To be honest, I fear the omen in my dreams may be true. Perhaps Fugio is unable to see the danger down there. Perhaps ... you are willing to investigate this matter?", cid)
		nextState = 1
	elseif msgcontains(msg, "yes") and state == 1 then
		setPlayerStorageValue(cid, WARDED_DOORS, 1)
		npcHandler:say("Thank you very much! From now on you may open the warded doors to the catacombs.", cid)
	elseif msgcontains(msg, "diary") then
		npcHandler:say("Do you want me to inspect a diary?", cid)
		nextState = 2
	elseif msgcontains(msg, "yes") and state == 2 then
		if getPlayerStorageValue(cid, ANKH_GIVEN) == 1 then
			npcHandler:say("Thank you again for bringing brother Fugio's diary to me.", cid)
		elseif doPlayerRemoveItem(cid, DIARY, 1) then
			setPlayerStorageValue(cid, ANKH_GIVEN, 1)
			doPlayerAddItem(cid, BLESSED_ANKH, 1)
			npcHandler:say("By the gods! This is brother Fugio's handwriting and what I read is horrible indeed! You have done our order a great favour by giving this diary to me! Take this blessed Ankh. May it protect you in even your darkest hours.", cid)
		else
			npcHandler:say("You don't have any diary.", cid)
		end
	elseif msgcontains(msg, "no") and state >= 1 then
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

npcHandler:setCallback(CALLBACK_GREET, greetCallback)
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())

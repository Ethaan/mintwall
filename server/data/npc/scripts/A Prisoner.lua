local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- A Prisoner, the Mad Mage, in the Mintwallin prison (Key 3620 opens it). Dialogue from TibiaWiki "A Prisoner/
-- Transcripts". Mad Mage Room Quest (docs/reference-74/quests.md): the answer to "The Riddle" (the book in his old
-- home) and 7 apples buy Key 3666, which opens the Mad Mage reward room. Mathemagics is part of the Paradox Tower
-- Quest (mission storage 6667 = 1; the answer he gives is kept in 6668). The old script gave the key to anyone who
-- said "key", "yes", took 1000 gold in the lesson and shared one conversation state between all players.
local APPLE = 2674
local APPLES_FOR_KEY = 7
local KEY_ITEM, KEY_NUMBER = 2088, 3666
local BLANK_RUNE = 2260
local MATH_MISSION, MATH_ANSWER = 6667, 6668
local ANSWERS = {"dp-d-ks-p-dp", "dp-d-sk-p-dp", "pd-d-ks-p-pd", "pd-d-sk-p-pd",
                 "dp-p-ks-d-dp", "dp-p-sk-d-dp", "pd-p-ks-d-pd", "pd-p-sk-d-pd"}
local COLOURS = {"red", "blue", "black", "white", "orange", "green", "yellow", "brown", "violet", "pink",
                 "silver", "gold", "grey"}
local SUMS = {49, 94, 13, 1}

local talkState = {}

local TALK = {
	{{"capture"}, "Yes, they capture people. I guess that's their job."},
	{{"job"}, "Job? JOB? Hey man - I am in prison! But you know - once upon a time - I was a powerful mage! A mage ... come to think of it .., what is that - a mage?"},
	{{"name"}, "My name is - uhm - hang on? I knew it yesterday, didn't I? Doesn't matter!"},
	{{"mad mage"}, "Hey! That's me! You got it! Thanks mate - now I remember my name!"},
	{{"sorcerer"}, "I am the mightiest sorcerer from here to there! Yeah!"},
	{{"power"}, "Power. Hmmm. Once while we were crossing the mountains together a man named Aureus said to me that parcels are equal to power. Any idea what that meant?"},
	{{"books"}, "I have many books in my home. But only powerful people can read them. I bet you will only see three dots after the headline! Hehehe! Hahaha! Excellent!"},
	{{"time"}, "Better save time than comitting a crime. I am a poet and I know it!"},
	{{"riddle"}, "Great riddle, isn't it? If you can tell me the correct answer, I will give you something. Hehehe!"},
	{{"something"}, "No! I won't tell you. Shame coz it would be useful for you - hehehe."},
	{{"escape"}, "How could I escape? They only give me rotten food here. I can't regain my powers because I have no mana!"},
	{{"labyrinth", "way"}, "It's easy to find your way through it! Just follow the pools of mud. Hehe - useful hint, isn't it?"},
	{{"mino"}, "They are trying to capture me! Or hang on! Haven't they already captured me? Hmmm - I will have to think about this."},
	{{"markwin"}, "He is the worst of them all! He is the king of the minos! May he burn in hell!"},
	{{"palkar"}, "He is the leader of the outcasts. I hope he will never conquer the city of Mintwallin. That would be the end of me!"},
	{{"karl"}, "Tataah!"},
	{{"demon"}, "The only monster I cannot conjure. But soon I will be powerful enough!"},
	{{"monster", "conjure", "home"}, "Yeah! There are many monsters guarding my home. Only the bravest hero will be able to slay them!"},
}

local function says(msg, words)
	for _, w in ipairs(words) do
		if msgcontains(msg, w) then
			return true
		end
	end
	return false
end

local function isAnswer(msg)
	local m = string.lower(msg)
	for _, a in ipairs(ANSWERS) do
		if string.find(m, a, 1, true) then
			return true
		end
	end
	return false
end

local function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	local state = talkState[cid] or 0
	local nextState = 0

	if isAnswer(msg) then
		npcHandler:say("Hurray! For that I will give you my key for - hmm - let's say ... some apples. Interested?", cid)
		nextState = 10
	elseif msgcontains(msg, "yes") and state == 10 then
		if getPlayerItemCount(cid, APPLE) < APPLES_FOR_KEY then
			npcHandler:say("Get some more apples first!", cid)
		else
			doPlayerRemoveItem(cid, APPLE, APPLES_FOR_KEY)
			npcHandler:say("Mnjam - excellent apples. Now - about that key. You are sure want it?", cid)
			nextState = 11
		end
	elseif msgcontains(msg, "yes") and state == 11 then
		npcHandler:say("Really, really?", cid)
		nextState = 12
	elseif msgcontains(msg, "yes") and state == 12 then
		npcHandler:say("Really, really, really, really?", cid)
		nextState = 13
	elseif msgcontains(msg, "yes") and state == 13 then
		local key = doPlayerAddItem(cid, KEY_ITEM, 1)
		doSetItemActionId(key, KEY_NUMBER)
		npcHandler:say("Then take it and get happy - or die, hehe.", cid)
	elseif msgcontains(msg, "no") and state >= 10 and state <= 13 then
		npcHandler:say("Then go away!", cid)
	elseif msgcontains(msg, "key") then
		npcHandler:say("Sure I have the key! Hehehe! Perhaps I will give it to you. IF you can solve my riddle.", cid)
	elseif msgcontains(msg, "apple") then
		npcHandler:say("Apples! Real apples! Man I love them! Can I have one? Oh please say yes!", cid)
		nextState = 20
	elseif msgcontains(msg, "yes") and state == 20 then
		if doPlayerRemoveItem(cid, APPLE, 1) then
			npcHandler:say("Mnjam. Excellent! Thanks, man!", cid)
		else
			npcHandler:say("Do you want to trick me? You don't have one lousy apple!", cid)
		end
	elseif msgcontains(msg, "no") and state == 20 then
		npcHandler:say("Ooooooooooo.<sniff>", cid)
	elseif msgcontains(msg, "sell rune") then
		npcHandler:say("You want to sell me blank runes! I will give you 50000 gold for each rune! Interested?", cid)
		nextState = 30
	elseif msgcontains(msg, "yes") and state == 30 then
		-- TibiaWiki: "he will only pay you 10 gps once you go through with the trade"
		if doPlayerRemoveItem(cid, BLANK_RUNE, 1) then
			doPlayerAddMoney(cid, 10)
		end
		npcHandler:say("Ok. Take my money. I can summon new money anytime - hehehe.", cid)
	elseif says(msg, {"number", "math", "1+1", "1 + 1", "1 plus 1", "one plus one"}) then
		if getPlayerStorageValue(cid, MATH_ANSWER) > 0 then
			npcHandler:say("You already know the secrets of mathemagics! Now go and use them to learn.", cid)
		else
			npcHandler:say("My surreal numbers are based on astonishing facts. Are you interested in learning the secret of mathemagics?", cid)
			nextState = 40
		end
	elseif msgcontains(msg, "yes") and state == 40 then
		npcHandler:say("But first tell me your favourite colour please!", cid)
		nextState = 41
	elseif state == 41 and says(msg, COLOURS) then
		npcHandler:say("Very interesting. So are you ready to proceed in you lesson in mathemagics?", cid)
		nextState = 42
	elseif msgcontains(msg, "yes") and state == 42 then
		if getPlayerStorageValue(cid, MATH_MISSION) ~= 1 then
			npcHandler:say("I think you are not in touch with yourself, come back if you have tuned in on your own feelings.", cid)
		else
			local n = math.random(1, #SUMS)
			setPlayerStorageValue(cid, MATH_ANSWER, n)
			npcHandler:say("So know that everthing is based on the simple fact that 1 + 1 = " .. SUMS[n] .. "!", cid)
		end
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

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- The Riddler, guardian of the Paradox Tower. The test of the three seals, word for word from the TibiaWiki spoiler
-- (Dec 2006); general lines from "Riddler/Transcripts". The last question, "What is 1 plus 1?", has only one right
-- answer: the number A Prisoner told this player (storage 6668 = which of his SUMS). Right: into the treasure room
-- (32478,31905,1; the wiki: "you will be allowed into the treasure room" - no line is written down, he says nothing);
-- any other number: "WRONG!" and down into Hellgate (32725,31589,12, tibiaot74's spot). A wrong answer on the way ends
-- the test. The old script let any message with a digit through and knew only one of the four answers.
local TREASURE_ROOM = {x=32478, y=31905, z=1}
local HELLGATE = {x=32725, y=31589, z=12}
local MATH_ANSWER = 6668
local SUMS = {49, 94, 13, 1}                   -- A Prisoner's

local SEALS = {                                 -- {state, answer, the next line}
	{3, {"goshnar"}, "HOHO! You have learned your lesson well. Question number two then: Who or what is the feared Hugo?"},
	{4, {"demonbunny"}, "HOHO! Right again. All right. The final question of the first seal: Who was the first warrior to follow the path of the Mooh'Tah?"},
	{5, {"tha'kull", "thakull"}, "HOHO! Lucky you. You have passed the first seal! So ... would you like to continue with the Seal of the Mind?"},
	{7, {"breath"}, "That was an easy one. Let's try the second: If you name it, you break it."},
	{8, {"silence"}, "Hm. I bet you think you're smart. All right. How about this: What does everybody want to become but nobody to be?"},
	{9, {"old"}, "ARGH! You did it again! Well all right. Do you wish to break the Seal of Madness?"},
	{11, {"green"}, "UHM UH OH ... How could you guess that? Are you mad??? All right. Question number two: What is the opposite?"},
	{12, {"none"}, "NO! NO! NO! That can't be true. You're not only mad, you are a complete idiot! Ah well. Here is the last question: What is 1 plus 1?"},
}
local YES = {                                   -- {state, the next line}
	[2] = "FOOL! Now you're doomed! But well ... So be it! Let's start out with the Seal of Knowledge and the first question: What name did the necromant king choose for himself?",
	[6] = "As you wish, foolish one! Here is my first question: Its lighter then a feather but no living creature can hold it for ten minutes?",
	[10] = "GOOD! So I will get you at last. Answer this: What is your favourite colour?",
}
local LAST = 13

local TALK = {
	{{"paradox", "tower"}, "This tower, of course, silly one. It holds my master's treasure."},
	{{"master"}, "His name is none of your business."},
	{{"treasure", "guard"}, "I am guarding the treasures of the tower. Only those who pass the test of the three sigils may pass."},
	{{"name"}, "I am known as the riddler. That is all you need to know."},
	{{"job"}, "I am the guardian of the paradox tower."},
	{{"time"}, "It is the age of the talon."},
	{{"key", "door"}, "The key of this tower! You will never find it! A malicious plant spirit is guarding it!"},
}

local talkState = {}

local function send(cid, pos)
	npcHandler:releaseFocus(cid)
	doTeleportThing(cid, pos)
	doSendMagicEffect(pos, CONST_ME_TELEPORT)
end

function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	local state = talkState[cid] or 0
	talkState[cid] = 0

	if state == LAST then
		local number = tonumber(string.match(msg, "%-?%d+"))
		if number == nil then
			npcHandler:say("WRONG!", cid)
			send(cid, HELLGATE)
			return true
		end
		local n = getPlayerStorageValue(cid, MATH_ANSWER)
		if n >= 1 and n <= #SUMS and number == SUMS[n] then
			send(cid, TREASURE_ROOM)
		else
			npcHandler:say("WRONG!", cid)
			send(cid, HELLGATE)
		end
		return true
	end
	if msgcontains(msg, "test") and state == 0 then
		npcHandler:say("Death awaits those who fail the test of the three seals! Do you really want me to test you?", cid)
		talkState[cid] = 2
		return true
	end
	if YES[state] ~= nil then
		if msgcontains(msg, "yes") then
			npcHandler:say(YES[state], cid)
			talkState[cid] = state + 1
		end
		return true
	end
	for _, seal in ipairs(SEALS) do
		if seal[1] == state then
			for _, answer in ipairs(seal[2]) do
				if msgcontains(msg, answer) then
					npcHandler:say(seal[3], cid)
					talkState[cid] = state + 1
					return true
				end
			end
			npcHandler:say("WRONG!", cid)          -- a wrong answer ends the test
			send(cid, HELLGATE)
			return true
		end
	end
	answerTalk(npcHandler, TALK, cid, msg)
	return true
end

npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())

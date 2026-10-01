local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)
local talkState = {}

function onCreatureAppear(cid)	 npcHandler: onCreatureAppear(cid)	 end
function onCreatureDisappear(cid)	 npcHandler: onCreatureDisappear(cid)	 end
function onCreatureSay(cid, type, msg)	npcHandler: onCreatureSay(cid, type, msg)	end
function onThink()	 npcHandler: onThink()	end

-- Skjaar (Mount Sternum; Noble Armor Quest, docs/reference-74/quests.md). TibiaWiki "Skjaar/Transcripts" greets a
-- warrior with "Another creature who believes thinks physical strength is more important than wisdom! Why are you
-- disturbing me?"; this script greeted "the path of wisdom" - both: mages get the second. Key 3142 (TibiaWiki "Key
-- 3142", copper, 1000 gp from Skjaar) - the script gave tibiaot74's number 2015 - and the 1000 gold are checked.
local WISE = "It's good to see somebody who has chosen the path of wisdom. What do you want?"
local STRONG = "Another creature who believes thinks physical strength is more important than wisdom! Why are you disturbing me?"

local function greetCallback(cid)
-- Resetting talkState[talkUser]
local talkUser = NPCHANDLER_CONVBEHAVIOR == CONVERSATION_DEFAULT and 0 or cid
talkState[talkUser] = 0
npcHandler:setMessage(MESSAGE_GREET, (isSorcerer(cid) or isDruid(cid)) and WISE or STRONG)
return true
end

local function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end

local talkUser = NPCHANDLER_CONVBEHAVIOR == CONVERSATION_DEFAULT and 0 or cid

if(msgcontains(msg, "key")) then
npcHandler:say("I will give the key to the crypt only to the closest followers of my master. Would you like me to test you?",cid)	
talkState[talkUser] = 2

elseif(msgcontains(msg, "yes") and talkState[talkUser] == 2) then
npcHandler:say("Before we start I must ask you for a small donation of 1000 gold coins. Are you willing to pay 1000 gold coins for the test?",cid)	
talkState[talkUser] = 3

elseif(msgcontains(msg, "yes") and talkState[talkUser] == 3) then
if doPlayerRemoveMoney(cid, 1000) then
npcHandler:say("All right then. Here comes the first question. What was the name of Dagos favourite pet?",cid)
talkState[talkUser] = 4
else
npcHandler:say("You don't have enough money.",cid)
talkState[talkUser] = 0
end

elseif(msgcontains(msg, "redips") and talkState[talkUser] == 4) then
npcHandler:say("Perhaps you knew him after all. Tell me - how many fingers did he have when he died?",cid)	
talkState[talkUser] = 5

elseif(msgcontains(msg, "7") and talkState[talkUser] == 5) then
npcHandler:say("Also true. But can you also tell me the colour of the deamons in which master specialized?",cid)	
talkState[talkUser] = 6

elseif(msgcontains(msg, "black") and talkState[talkUser] == 6) then
npcHandler:say("It seems you are worthy after all. Do you want the key to the crypt?",cid)	
talkState[talkUser] = 7

elseif(msgcontains(msg, "yes") and talkState[talkUser] == 7) then
local key = doPlayerAddItem(cid,2089,1)
doSetItemActionId(key, 3142)
npcHandler:say("Here you go.",cid)
talkState[talkUser] = 8
else
local talk = {door = "This door seals a crypt.", job = "Once I was the master of all mages, but now I only protect this crypt.",
	crypt = "Here lies my master. Only his closest followers may enter.",
	master = "If you are one of his followers, you need not ask about him, for you will know. And if you aren't, you are not worthy anyway!",
	time = "To those who have lived for a thousand years time holds no more terror.",
	castle = "The castle was destroyed when my master tried to summon a nameless creature. All that is left is this volcano.",
	volcano = "I can still feel the magical energy in the volcano."}
for word, text in pairs(talk) do
	if msgcontains(msg, word) then
		npcHandler:say(text, cid)
		break
	end
end
end
return true
end

npcHandler:setCallback(CALLBACK_GREET, greetCallback)
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())
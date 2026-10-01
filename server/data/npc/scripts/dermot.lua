local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)
local talkState = {}

function onCreatureAppear(cid)	 npcHandler:onCreatureAppear(cid)	 end
function onCreatureDisappear(cid)	 npcHandler:onCreatureDisappear(cid)	 end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()	 npcHandler:onThink()	end

npcHandler:setMessage(MESSAGE_GREET, "Be greeted |PLAYERNAME|.")

local function greetCallback(cid)
-- Resetting talkState[talkUser]
local talkUser = NPCHANDLER_CONVBEHAVIOR == CONVERSATION_DEFAULT and 0 or cid
talkState[talkUser] = 0
return true
end

local function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end

local talkUser = NPCHANDLER_CONVBEHAVIOR == CONVERSATION_DEFAULT and 0 or cid

if(msgcontains(msg, 'key') or msgcontains(msg, 'door')) then
npcHandler:say("Do you want to buy the dungeon key for 2000 gold?",cid)
talkState[talkUser] = 1
elseif(msgcontains(msg, "yes") and talkState[talkUser] == 1) then
if doPlayerRemoveMoney(cid, 2000) then -- edit the amount of gold here
key = doPlayerAddItem(cid,2089,1)
doSetItemActionId(key, 3940)
npcHandler:say("Here you go.",cid)
talkState[talkUser] = 0
else
npcHandler:say("You don't have enough money.", cid)
talkState[talkUser] = 0
end
elseif(talkState[talkUser] == 1) then
npcHandler:say("Believe me, it's better for you that way.", cid)
talkState[talkUser] = 0
elseif(talkState[talkUser] == 2) then
-- the Postman Missions, mission 5 (npc/lib/postman.lua): "yes" and the present (was: any answer, and a big bone taken)
talkState[talkUser] = 0
if msgcontains(msg, "yes") and doPlayerRemoveItem(cid, PRESENT, 1) then
npcHandler:say("Thank you very much!", cid)
setPlayerStorageValue(cid, POSTMAN, POSTMAN_PRESENT_GIVEN)
elseif msgcontains(msg, "yes") then
npcHandler:say("But you don't have it with you!", cid)
end
end
if(msgcontains(msg, 'present') and postmanProgress(cid) == POSTMAN_PRESENT) then
npcHandler:say("You have a present for me?? Realy?", cid)
talkState[talkUser] = 2
end
return true
end

npcHandler:setCallback(CALLBACK_GREET, greetCallback)
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())
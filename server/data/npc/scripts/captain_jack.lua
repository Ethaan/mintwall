local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Captain Jack, on his boat at the Isle of the Kings (TibiaWiki 2006: "Provides passage back to the tibia mainland";
-- implemented 7.2). Dalbrect's infobox (2006): 10 gp to the Isle, 20 gp back. He sails to Dalbrect's boat north-west
-- of Carlin. Storage 99998 = trespassed on the monks' restricted floor (Costello's absolution clears it - not
-- scripted yet, nothing sets it). The old script shared one conversation state between all players and its in-fight
-- check never blocked (hasCondition(...) ~= 1 on a true/false result).
local TRESPASSER = 99998
local FARE = 20
local CARLIN = {x = 32205, y = 31756, z = 7}   -- the deck of Dalbrect's boat

local talkState = {}

function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	local state = talkState[cid] or 0
	local nextState = 0

	if msgcontains(msg, "continent") or msgcontains(msg, "tibia") or msgcontains(msg, "passage") then
		npcHandler:say("Friends of Dalbrect are my friends too! So you are looking for a passage to the continent for " .. FARE .. " gold?", cid)
		nextState = 1
	elseif msgcontains(msg, "yes") and state == 1 then
		if getPlayerStorageValue(cid, TRESPASSER) ~= -1 then
			npcHandler:say("Without the abbots permission I won't take sail you anywhere! Go and ask him for a passage first.", cid)
		elseif isPzLocked(cid) then
			npcHandler:say("First get rid of those blood stains! You are not going to ruin my vehicle!", cid)
		elseif not doPlayerRemoveMoney(cid, FARE) then
			npcHandler:say("You don't have enough money.", cid)
		else
			npcHandler:say("Have a nice trip!", cid)
			npcHandler:releaseFocus(cid)
			doTeleportThing(cid, CARLIN)
			doSendMagicEffect(CARLIN, CONST_ME_TELEPORT)
		end
	end
	talkState[cid] = nextState
	return true
end

npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())

-- The Cobra in Thalas's tomb (the Stone Tomb, 33366,32855,14; The Ancient Tombs Quest, docs/reference-74/quests.md).
-- Current wiki: "after getting poisoned say hi to the Cobra NPC to the south (he will respond with 'Begone! Hissssss!
-- You bear not the mark of the cobra!' if you are not fast enough) to get teleported to a room with Thalas [...] (after
-- getting teleported you will also receive the message from the Cobra: 'Venture the path of decay!')". Our spawns
-- file lists it among the NPCs (spawned as a plain cobra until 2026-09-28); the poison is "the mark of the cobra"
-- (decided with the user). Thalas's room: where the forcefield past the level-75 gate leads (our map).
local THALAS_ROOM = {x=33397, y=32835, z=14}

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)				npcHandler:onCreatureAppear(cid) end
function onCreatureDisappear(cid)			npcHandler:onCreatureDisappear(cid) end
function onCreatureSay(cid, type, msg)		npcHandler:onCreatureSay(cid, type, msg) end
function onThink()							npcHandler:onThink() end

function sendToThalas(cid)
	if isPlayer(cid) then
		doTeleportThing(cid, THALAS_ROOM)
		doSendMagicEffect(THALAS_ROOM, 20)     -- CONST_ME_POISONAREA
	end
end

local function greetCallback(cid)
	if not hasCondition(cid, 1) then           -- CONDITION_POISON
		selfSay("Begone! Hissssss! You bear not the mark of the cobra!")
		return false
	end
	selfSay("Venture the path of decay!")
	addEvent(sendToThalas, 500, cid)           -- once the player has heard it
	return false
end

npcHandler:setCallback(CALLBACK_GREET, greetCallback)
npcHandler:addModule(FocusModule:new())

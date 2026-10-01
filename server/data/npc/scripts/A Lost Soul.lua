local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)


-- OTServ event handling functions start
function onCreatureAppear(cid)				npcHandler:onCreatureAppear(cid) end
function onCreatureDisappear(cid) 			npcHandler:onCreatureDisappear(cid) end
function onCreatureSay(cid, type, msg) 	npcHandler:onCreatureSay(cid, type, msg) end
function onThink() 						npcHandler:onThink() end

-- A Lost Soul does not answer a greeting. This used to replace FocusModule:init for EVERY NPC (they share one
-- Lua state): all NPCs set up after it could not be greeted with "hi" (A Prisoner, among others).
local focus = FocusModule:new()
function focus:init(handler)
	self.npcHandler = handler
end
npcHandler:addModule(focus)
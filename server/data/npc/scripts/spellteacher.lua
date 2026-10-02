-- A spell teacher (npc/lib/spellteacher.lua): his XML's talk and shop, and the spells Tibiantis has him teach.
dofile(getDataDir() .. 'npc/lib/spellteacher.lua')

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)       -- module_shop / module_keywords add the XML's shop and talk

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

teachSpells(keywordHandler, npcHandler, getNpcName())
npcHandler:addModule(FocusModule:new())

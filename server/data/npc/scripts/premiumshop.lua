-- A shopkeeper of the XML shop who trades with premium accounts only (npc/lib/premiumshop.lua): Norma.
dofile(getDataDir() .. 'npc/lib/premiumshop.lua')

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)       -- module_shop adds the shop

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

premiumShop(npcHandler)
npcHandler:addModule(FocusModule:new())

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)				npcHandler:onCreatureAppear(cid) 			end
function onCreatureDisappear(cid) 			npcHandler:onCreatureDisappear(cid) 		end
function onCreatureSay(cid, type, msg) 		npcHandler:onCreatureSay(cid, type, msg) 	end
function onThink() 							npcHandler:onThink() 						end
function onPlayerEndTrade(cid)				npcHandler:onPlayerEndTrade(cid)			end
function onPlayerCloseChannel(cid)			npcHandler:onPlayerCloseChannel(cid)		end

-- sells the blessing of embrace of tibia; any word of its name works (lib/npc.lua). To free accounts too: TibiaWiki
-- Blessings 2005-2006 "can be obtained by any player", "One blessing [Eremo's, on a premium isle] and the promotion
-- require premium accounts" (docs/reference-74/premium.md). Was premium-only.
addBlessingKeywords(keywordHandler, npcHandler, 1, 'embrace of tibia', false)

npcHandler:addModule(FocusModule:new())
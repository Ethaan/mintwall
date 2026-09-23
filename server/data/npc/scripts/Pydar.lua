local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)				npcHandler:onCreatureAppear(cid) 			end
function onCreatureDisappear(cid) 			npcHandler:onCreatureDisappear(cid) 		end
function onCreatureSay(cid, type, msg) 		npcHandler:onCreatureSay(cid, type, msg) 	end
function onThink() 							npcHandler:onThink() 						end
function onPlayerEndTrade(cid)				npcHandler:onPlayerEndTrade(cid)			end
function onPlayerCloseChannel(cid)			npcHandler:onPlayerCloseChannel(cid)		end

-- Second part of the spark of the phoenix, after Kawill's (see Kawill.lua): only now is it paid,
-- 10000 gold. (This used to be an 8.x seller of all five blessings at a level-based price.)
SPARK_FIRST_PART = 30020

local function secondPart(cid, message, keywords, parameters, node)
	if(not npcHandler:isFocused(cid)) then
		return false
	end
	if(getPlayerStorageValue(cid, SPARK_FIRST_PART) ~= 1 and not getPlayerBlessing(cid, 5)) then
		npcHandler:say("You must receive the first part of the spark of the phoenix from Kawill first.", cid)
		npcHandler:resetNpc(cid)
		return true
	end
	local blessedBefore = getPlayerBlessing(cid, 5)
	StdModule.bless(cid, message, keywords, parameters, node)
	if(not blessedBefore and getPlayerBlessing(cid, 5)) then
		setPlayerStorageValue(cid, SPARK_FIRST_PART, 0)
	end
	return true
end

addBlessingKeywords(keywordHandler, npcHandler, 5, 'spark of the phoenix', false, secondPart)

npcHandler:addModule(FocusModule:new())

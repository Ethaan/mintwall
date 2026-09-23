local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)				npcHandler:onCreatureAppear(cid) 			end
function onCreatureDisappear(cid) 			npcHandler:onCreatureDisappear(cid) 		end
function onCreatureSay(cid, type, msg) 		npcHandler:onCreatureSay(cid, type, msg) 	end
function onThink() 							npcHandler:onThink() 						end
function onPlayerEndTrade(cid)				npcHandler:onPlayerEndTrade(cid)			end
function onPlayerCloseChannel(cid)			npcHandler:onPlayerCloseChannel(cid)		end

-- The spark of the phoenix is given in two parts, in this order (docs/reference-74/death.md):
-- Kawill (south of the Kazordoon temple) gives the first part for free, Pydar (north, past the fire)
-- gives the second and takes the 10000 gold. SPARK_FIRST_PART remembers Kawill's part.
SPARK_FIRST_PART = 30020

local function firstPart(cid, message, keywords, parameters, node)
	if(not npcHandler:isFocused(cid)) then
		return false
	end
	if(getPlayerBlessing(cid, 5)) then
		npcHandler:say("Gods have already blessed you with this blessing!", cid)
	elseif(getPlayerStorageValue(cid, SPARK_FIRST_PART) == 1) then
		npcHandler:say("You already have the first part of the spark of the phoenix. Go to Pydar for the second.", cid)
	else
		setPlayerStorageValue(cid, SPARK_FIRST_PART, 1)
		npcHandler:say("So be it: the first part of the spark of the phoenix is yours. Pydar, north of the temple, will complete it.", cid)
	end
	npcHandler:resetNpc(cid)
	return true
end

for word in string.gmatch("spark phoenix", "%a+") do
	local node = keywordHandler:addKeyword({word}, StdModule.say, {npcHandler = npcHandler, onlyFocus = true,
		text = 'Do you want to receive the first part of the blessing of the spark of the phoenix? Pydar will give you the second part, for 10000 gold.'})
	node:addChildKeyword({'yes'}, firstPart, {})
	node:addChildKeyword({'no'}, StdModule.say, {npcHandler = npcHandler, onlyFocus = true, reset = true, text = 'As you wish.'})
end

npcHandler:addModule(FocusModule:new())

-- Sherry McRonald, the Thais farmer (TibiaWiki 2006: sells cheese 5, cherries 1, pumpkins 10, melons 8 gp, buys bread
-- 2 gp). Her words are in her NPC file. The old script set up her shop and greeting inside a callback that never ran:
-- nobody could greet her.
local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

local shopModule = ShopModule:new()
npcHandler:addModule(shopModule)
shopModule:addBuyableItem({'cheese'}, 2696, 5, 'cheese')
shopModule:addBuyableItem({'cherry', 'cherries'}, 2679, 1, 'cherry')
shopModule:addBuyableItem({'melon'}, 2682, 8, 'melon')
shopModule:addBuyableItem({'pumpkin'}, 2683, 10, 'pumpkin')
shopModule:addSellableItem({'bread'}, 2689, 2, 'bread')

npcHandler:addModule(FocusModule:new())

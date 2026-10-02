-- Rookgaard's premium shopkeepers (Lee'Delle, Norma). TibiaWiki 2005: Lee'Delle "only sells to premium people",
-- Norma "is a premium npc, she only attends premium people". The words she refuses a free account with are not on
-- the pages - ours.
local REFUSAL = "I am sorry, but I only trade with premium adventurers."

function premiumShop(npcHandler)
	for _, module in ipairs(npcHandler.modules) do
		if getmetatable(module) == ShopModule then
			module.mayTrade = function(cid)
				if isPremium(cid) then
					return true
				end
				npcHandler:say(REFUSAL, cid)
				return false
			end
		end
	end
end

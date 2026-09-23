-- Machete: cuts wild growth (rush wood) away and jungle grass down (it grows back, items.xml decayTo).
-- It called isIntegerInArray with tables that were never defined, so every use failed.
local RUSH_WOOD = 1499            -- exevo grav vita
local JUNGLE_GRASS_GROWN = 2782   -- cut becomes 2781, which decays back to 2782

function onUse(cid, item, frompos, item2, topos)
	if item2.itemid == RUSH_WOOD then
		doRemoveItem(item2.uid)
		doSendMagicEffect(topos, CONST_ME_POFF)
		return true
	elseif item2.itemid == JUNGLE_GRASS_GROWN then
		doTransformItem(item2.uid, item2.itemid - 1)
		doDecayItem(item2.uid)
		return true
	end
	return false
end

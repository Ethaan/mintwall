-- The helmet of the ancients (The Ancient Tombs Quest, docs/reference-74/quests.md). TibiaWiki 2006: "To make the helmet
-- a Full Helmet of the Ancients, you need to place a Small Ruby on the helmet. Each ruby will only last a limited amount
-- of time (30 minutes)"; current wiki: "When you use it on a Small Ruby, it will be enchanted" (+3 armor). The glowing
-- helmet (2343) turns back after 30 minutes by itself (items.xml).
local SMALL_RUBY, GLOWING = 2147, 2343

function onUse(cid, item, frompos, item2, topos)
	if item2.itemid ~= SMALL_RUBY then
		return false
	end
	doRemoveItem(item2.uid, 1)
	doTransformItem(item.uid, GLOWING)
	doDecayItem(item.uid)
	doSendMagicEffect(getPlayerPosition(cid), CONST_ME_MAGIC_RED)
	return true
end

-- Bear Room Quest (Rookgaard, docs/reference-74/quests.md): the switch north of the big table (action id
-- 52413 at 32148,32105,11) "controls the stone which can block the door to the bear room" (TibiaWiki
-- Bear Room Quest/Spoiler): using it takes the stone away, using it again puts it back.
local STONE_POS = {x=32145, y=32101, z=11}   -- in front of the bear-room door (key 4601) at 32145,32100,11
local STONE = 1304
local ASIDE = {x=32145, y=32102, z=11}       -- whatever stands where the stone comes back is moved here

function onUse(cid, item, frompos, item2, topos)
	local stone = getTileItemById(STONE_POS, STONE)
	if stone.uid > 0 then
		doRemoveItem(stone.uid)
		doSendMagicEffect(STONE_POS, CONST_ME_POFF)
	else
		doRelocate(STONE_POS, ASIDE)
		doCreateItem(STONE, 1, STONE_POS)
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

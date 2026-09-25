-- Edron Orc Cave (docs/reference-74/quests.md, the five Orc Cave quests). The hole at the entrance (33173,31900,7)
-- drops into a small pocket; a stone (33171,31897,8) closes the way on into the cave. The lever on the counter
-- (action id 51024 at 33172,31896,8 - on our map and the JS engine's, unscripted) takes the stone away and puts it
-- back when pulled again - position and stone as tibiaot74's "edron orc stone.lua". It can be pulled from both sides.
local STONE_POS = {x=33171, y=31897, z=8}
local STONE = 1285
local POCKET = {x=33171, y=31898, z=8}

function onUse(cid, item, frompos, item2, topos)
	local stone = getTileItemById(STONE_POS, STONE)
	if stone.uid > 0 then
		doRemoveItem(stone.uid)
	else
		doRelocate(STONE_POS, POCKET)          -- whoever stands there steps aside into the pocket
		doCreateItem(STONE, 1, STONE_POS)
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

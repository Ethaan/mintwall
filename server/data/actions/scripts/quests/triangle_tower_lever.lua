-- Triangle Tower Quest (docs/reference-74/quests.md). TibiaWiki (2005/2006): "If the tower is closed, pull the lever
-- in the desert." The lever (action id 51020 at 32573,32121,7) takes away the brick wall that closes the tower at
-- 32566,32119,7, and puts it back when pulled again - position and wall as tibiaot74's "triangle tower.lua". The
-- tower starts closed (our map has the wall).
local WALL_POS = {x=32566, y=32119, z=7}
local WALL = 1025
local OUTSIDE = {x=32567, y=32119, z=7}

function onUse(cid, item, frompos, item2, topos)
	local wall = getTileItemById(WALL_POS, WALL)
	if wall.uid > 0 then
		doRemoveItem(wall.uid)
	else
		doRelocate(WALL_POS, OUTSIDE)
		doCreateItem(WALL, 1, WALL_POS)
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

-- Torch Quest (Rookgaard Academy basement, docs/reference-74/quests.md): the lever (action id 50004 at
-- 32093,32174,8, under the blackboard "The lever will open the wall.") opens the brick wall at
-- 32095,32173,8 on the way north to the torch chest; pulled again, it closes it. TibiaWiki Torch Quest/Spoiler;
-- the wall's position and item as in tibiaot74's "academy switch.lua" (their action id 3101).
local WALL_POS = {x=32095, y=32173, z=8}
local WALL = 1026
local ASIDE = {x=32095, y=32174, z=8}   -- anything where the wall comes back is moved here

function onUse(cid, item, frompos, item2, topos)
	local wall = getTileItemById(WALL_POS, WALL)
	if wall.uid > 0 then
		doRemoveItem(wall.uid)
	else
		doRelocate(WALL_POS, ASIDE)
		doCreateItem(WALL, 1, WALL_POS)
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

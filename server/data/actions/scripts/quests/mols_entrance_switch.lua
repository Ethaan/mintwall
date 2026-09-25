-- The Maze of Lost Souls (docs/reference-74/quests.md: Griffin Shield, Crystal Wand, Purple Tome). The switch in the
-- hole under the underground forest (action id 51026 at 32528,31724,10), by Zhandramon's sign "Turn the switch to the
-- right and follow the blue sunshine to get to Demona". TibiaWiki (2006): "a switch that you must turn right to open
-- the entrance to the MoLS. Note: if it is already turned right, then turn it left and right again"; current wiki
-- (Maze of Lost Souls): "Turn the lever to the right [...] Walk to this hole (126.227|123.145|9) and enter" - the
-- dirt at 32483,31633,9 opens into a hole over the ladder inside the level-30 gates. Right = open, left = shut; the
-- server save puts back the map (switch left, no hole), as the wiki's "the hole can be reset" says.
local HOLE_POS = {x=32483, y=31633, z=9, stackpos=0}
local DIRT = 353              -- the map's ground there
local HOLE = 383

function onUse(cid, item, frompos, item2, topos)
	local ground = getTileThingByPos(HOLE_POS)
	if item.itemid == 1945 then                           -- to the right: open
		if ground.itemid == DIRT then
			doTransformItem(ground.uid, HOLE)
		end
		doTransformItem(item.uid, 1946)
	else                                                  -- to the left: shut
		if ground.itemid == HOLE then
			doTransformItem(ground.uid, DIRT)
		end
		doTransformItem(item.uid, 1945)
	end
	return true
end

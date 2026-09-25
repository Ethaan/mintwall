-- Devil Helmet Quest (docs/reference-74/quests.md). TibiaWiki (2006): one player goes to "a blocked passage.
-- Standing on the open square opens a grate"; the others "go down the grate" - so it takes two. The open square is
-- the switch tile at 32468,32119,14 (stone tile 426/425, action id 51018); the grate is at 32482,32170,14 (a ladder
-- below). While someone stands on the switch the grate's ground is a hole you drop through; stepping off closes it
-- again (as tibiaot74's "main movements.lua": hole 383 / dirt 351). The grate itself: actions/scripts/quests/
-- mintwallin_grate.lua (shut otherwise).
local SWITCH = {x=32468, y=32119, z=14, stackpos=253}
local GRATE_POS = {x=32482, y=32170, z=14}
local DIRT, HOLE = 351, 383
local UP, DOWN = 426, 425

function onStepIn(cid, item, topos, frompos)
	if item.itemid == UP then
		doTransformItem(item.uid, DOWN)
	end
	local ground = getTileItemById(GRATE_POS, DIRT)
	if ground.uid > 0 then
		doTransformItem(ground.uid, HOLE)
	end
	return true
end

function onStepOut(cid, item, topos, frompos)
	if getThingfromPos(SWITCH).uid > 0 then
		return true                        -- someone else still stands on it
	end
	if item.itemid == DOWN then
		doTransformItem(item.uid, UP)
	end
	local hole = getTileItemById(GRATE_POS, HOLE)
	if hole.uid > 0 then
		doTransformItem(hole.uid, DIRT)
	end
	return true
end

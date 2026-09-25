-- Thais Lighthouse Quest (docs/reference-74/quests.md; the switch and lever are actions/scripts/quests/
-- thais_lighthouse.lua). TibiaWiki (2006): "North leads to a step switch that once a person stands on it will open
-- stairs at the south end." The step switch (stone tile 426/425, action id 51002, 32225,32268,9) opens the stairs
-- down at 32225,32282,9 (above the stairs up at 32225,32282,10) while anyone stands on it, as tibiaot74's "movement
-- tiles.lua". Stairs 410: the stairs down most used on our map in stone rooms with a wall north of the stairs below.
local PLATE = {x=32225, y=32268, z=9, stackpos=253}     -- stackpos 253: the creature on it
local STAIRS_POS = {x=32225, y=32282, z=9}
local FLOOR, STAIRS = 424, 410
local UP, DOWN = 426, 425

function onStepIn(cid, item, topos, frompos)
	if item.itemid == UP then
		doTransformItem(item.uid, DOWN)
	end
	local floor = getTileItemById(STAIRS_POS, FLOOR)
	if floor.uid > 0 then
		doTransformItem(floor.uid, STAIRS)
	end
	return true
end

function onStepOut(cid, item, topos, frompos)
	-- someone else still stands on it: it stays down (the leaving creature is already off the tile)
	if getThingfromPos(PLATE).uid > 0 then
		return true
	end
	if item.itemid == DOWN then
		doTransformItem(item.uid, UP)
	end
	local stairs = getTileItemById(STAIRS_POS, STAIRS)
	if stairs.uid > 0 then
		doTransformItem(stairs.uid, FLOOR)
	end
	return true
end

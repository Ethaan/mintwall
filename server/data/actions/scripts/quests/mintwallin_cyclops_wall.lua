-- Mintwallin Cyclops Quest (docs/reference-74/quests.md). TibiaWiki (2006): "Enter the NW corner and follow the
-- passage to the switch. Pulling it moves the wall and traps you with the Cyclopes"; the reward (key 3610 and a
-- small diamond, real-map table 3610/3611) lies behind; the way out is the north hole. The switch (action id 51016 at
-- 32602,32104,14) moves the wall: the two walls north of the passage (32593-32594,32103,14) go, two walls close it
-- behind you (32592,32104-32105,14) - positions and items as tibiaot74's "Key 3610 switch.lua". Pulled again, it
-- moves back (decided with the user 2026-09-24: both ways). Key 3667 opens the door to the reward without it.
local NORTH = {{x=32593, y=32103, z=14}, {x=32594, y=32103, z=14}}
local WEST = {{x=32592, y=32104, z=14}, {x=32592, y=32105, z=14}}
local NORTH_WALL, WEST_WALL = 1026, 1025
local READY, MOVED = 1946, 1945

local function removeWalls(list, id)
	for _, pos in ipairs(list) do
		local wall = getTileItemById(pos, id)
		if wall.uid > 0 then
			doRemoveItem(wall.uid)
		end
	end
end

local function putWalls(list, id, aside)
	for _, pos in ipairs(list) do
		if getTileItemById(pos, id).uid == 0 then
			doRelocate(pos, {x=pos.x + aside.x, y=pos.y + aside.y, z=pos.z})   -- whoever stands there steps aside
			doCreateItem(id, 1, pos)
		end
	end
end

function onUse(cid, item, frompos, item2, topos)
	if item.itemid == READY then
		removeWalls(NORTH, NORTH_WALL)
		putWalls(WEST, WEST_WALL, {x=1, y=0})             -- into the cyclops room
		doTransformItem(item.uid, MOVED)
	else
		removeWalls(WEST, WEST_WALL)
		putWalls(NORTH, NORTH_WALL, {x=0, y=1})           -- back into the cyclops room
		doTransformItem(item.uid, READY)
	end
	return true
end

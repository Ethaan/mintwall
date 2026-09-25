-- Alawar's Vault Quest, the short path (docs/reference-74/quests.md). Senja Castle cellar: "Use a Destroy Field on
-- that fire field and pull the switch under it" (TibiaWiki 2006); "Pull the lever and it will vanish, the magic walls
-- to the north will also have disappeared" (current wiki). The switch (action id 51025 at 32180,31633,8, under a fire
-- field on our map) takes away the four magic walls 32186-32189,31626,8 in front of the vault portal (positions as
-- tibiaot74's "Senja Magicwalls.lua") and vanishes itself. Decided with the user 2026-09-25 (no source gives a timer):
-- after 2 minutes the walls and the switch come back; whoever stands in the wall row steps south, out of the way.
local WALLS = {
	{x=32186, y=31626, z=8}, {x=32187, y=31626, z=8}, {x=32188, y=31626, z=8}, {x=32189, y=31626, z=8},
}
local WALL = 1497              -- magic wall, not decaying (the map's)
local SWITCH = 1945
local SWITCH_AID = 51025
local OPEN_FOR = 2 * 60 * 1000

local function closeWalls(pos)
	for _, wallPos in ipairs(WALLS) do
		if getTileItemById(wallPos, WALL).uid == 0 then
			doRelocate(wallPos, {x=wallPos.x, y=wallPos.y + 1, z=wallPos.z})
			doCreateItem(WALL, 1, wallPos)
		end
	end
	local switch = doCreateItem(SWITCH, 1, pos)
	doSetItemActionId(switch, SWITCH_AID)
end

function onUse(cid, item, frompos, item2, topos)
	for _, wallPos in ipairs(WALLS) do
		local wall = getTileItemById(wallPos, WALL)
		if wall.uid > 0 then
			doRemoveItem(wall.uid)
		end
	end
	local pos = getThingPos(item.uid)
	doRemoveItem(item.uid)
	addEvent(closeWalls, OPEN_FOR, pos)
	return true
end

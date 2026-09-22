-- Rookgaard sewer: the two switches (action id 50001) at 32098,32204,8 and 32104,32204,8
-- lay a drawbridge over the water at 32100-32101,32205,8 and raise it again.
local SWITCHES = {{x=32098, y=32204, z=8}, {x=32104, y=32204, z=8}}
local BRIDGE = {
	{pos = {x=32100, y=32205, z=8}, water = 508},
	{pos = {x=32101, y=32205, z=8}, water = 509},
}
local DRAWBRIDGE = 1284
local BANK = {x=32102, y=32205, z=8}  -- anything left on the bridge is moved here when it is raised

function onUse(cid, item, frompos, item2, topos)
	local lower = item.itemid == 1945
	for _, tile in ipairs(BRIDGE) do
		local ground = getThingFromPos({x=tile.pos.x, y=tile.pos.y, z=tile.pos.z, stackpos=0})
		if lower then
			doTransformItem(ground.uid, DRAWBRIDGE)
		else
			doRelocate(tile.pos, BANK)
			doTransformItem(ground.uid, tile.water)
		end
	end
	for _, pos in ipairs(SWITCHES) do
		local switch = getTileItemById(pos, item.itemid)
		if switch.uid > 0 then
			doTransformItem(switch.uid, lower and 1946 or 1945)
		end
	end
	return true
end

-- Thais Ancient Temple, the two drawbridges over the water on floor 10 (docs/reference-74/quests.md: Life Ring, Six
-- Rubies, Naginata and the other Ancient Temple quests cross them). TibiaWiki: "If the bridge is up, pull the lever".
-- The levers (action id 51058) at 32413,32230,10 and 32417,32254,10 had no script; the bridges (drawbridge ground
-- 1284) lie down on our map. A pull raises a lowered bridge - each tile becomes the water of its own column (the water
-- north and south of it on the map) - and lowers a raised one, like Rookgaard's sewer bridge (rook_rat_bridge.lua);
-- whatever stands on a bridge going up is moved to the lever's bank.
local DRAWBRIDGE = 1284
local BRIDGES = {
	["32413,32230"] = {bank = {x=32413, y=32231, z=10}, tiles = {
		{{x=32410, y=32231, z=10}, 508}, {{x=32411, y=32231, z=10}, 493}, {{x=32412, y=32231, z=10}, 493},
		{{x=32410, y=32232, z=10}, 508}, {{x=32411, y=32232, z=10}, 493}, {{x=32412, y=32232, z=10}, 493}}},
	["32417,32254"] = {bank = {x=32411, y=32253, z=10}, tiles = {
		{{x=32408, y=32253, z=10}, 508}, {{x=32409, y=32253, z=10}, 493}, {{x=32410, y=32253, z=10}, 509}}},
}

local function ground(pos)
	return getTileThingByPos({x=pos.x, y=pos.y, z=pos.z, stackpos=0})
end

function onUse(cid, item, frompos, item2, topos)
	local bridge = BRIDGES[frompos.x .. "," .. frompos.y]
	if bridge == nil then
		return false
	end
	local lowered = ground(bridge.tiles[1][1]).itemid == DRAWBRIDGE
	for _, tile in ipairs(bridge.tiles) do
		local pos, water = tile[1], tile[2]
		if lowered then
			doRelocate(pos, bridge.bank)
			doTransformItem(ground(pos).uid, water)
		else
			doTransformItem(ground(pos).uid, DRAWBRIDGE)
		end
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

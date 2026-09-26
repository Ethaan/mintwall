-- Draconia Quest, the pyramid (docs/reference-74/quests.md; positions: tibiaot74's "main movements.lua").
--
-- 51071, the 3rd floor's floor switches (stone tiles 426): "player 1 stands on the southern floor switch. Player 2 goes to
-- the SW room and stands on its switch. Player 1 then takes the NW portal to the room with Key 3007." The switch
-- 32810,31595,5 takes the wall 32796,31595,5 (into the SW room) away while someone stands on it, the switch 32794,31595,5
-- the wall 32795,31578,5 (to the portal into key 3007's room); stepping off puts the wall back.
-- 51074, the top floor's portal (32805,31587,1): "Set the levers Left, Right, Left, Right and take the teleporter to the
-- Ab'Dendriel sacrificial stone near the temple" (32701,31639,6); with the levers otherwise it puts you back.
local PLATES = {
	["32810,31595"] = {wall = {x=32796, y=31595, z=5}, item = 1025, aside = {x=32797, y=31595, z=5}},
	["32794,31595"] = {wall = {x=32795, y=31578, z=5}, item = 1026, aside = {x=32795, y=31579, z=5}},
}
local LEVERS = {{x=32802, y=31584, z=1}, {x=32803, y=31584, z=1}, {x=32804, y=31584, z=1}, {x=32805, y=31584, z=1}}
local LEFT, RIGHT = 1945, 1946
local ORDER = {LEFT, RIGHT, LEFT, RIGHT}
local AB_DENDRIEL = {x=32701, y=31639, z=6}
local BACK = {x=32803, y=31587, z=1}

local function plate(pos)
	return PLATES[pos.x .. "," .. pos.y]
end

function onStepIn(cid, item, topos, frompos)
	if item.actionid == 51071 then
		local p = plate(getThingPos(item.uid))
		local wall = p and getTileItemById(p.wall, p.item)
		if wall and wall.uid > 0 then
			doRemoveItem(wall.uid)
		end
	elseif item.actionid == 51074 and isPlayer(cid) then
		local right = true
		for i, pos in ipairs(LEVERS) do
			if getTileItemById(pos, ORDER[i]).uid == 0 then
				right = false
			end
		end
		local dest = right and AB_DENDRIEL or BACK
		doTeleportThing(cid, dest)
		doSendMagicEffect(dest, CONST_ME_ENERGYAREA)
	end
	return true
end

function onStepOut(cid, item, topos, frompos)
	if item.actionid ~= 51071 then
		return true
	end
	local here = getThingPos(item.uid)
	local p = plate(here)
	if p == nil then
		return true
	end
	if getThingfromPos({x=here.x, y=here.y, z=here.z, stackpos=253}).uid > 0 then
		return true                                  -- someone else still stands on it
	end
	if getTileItemById(p.wall, p.item).uid == 0 then
		doRelocate(p.wall, p.aside)
		doCreateItem(p.item, 1, p.wall)
	end
	return true
end

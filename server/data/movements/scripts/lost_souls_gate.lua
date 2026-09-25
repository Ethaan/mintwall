-- Gate of the Lost Souls, Edron Hero Cave (Demon Helmet Quest, docs/reference-74/quests.md). TibiaWiki (current
-- spoiler): "you will still need two other players, namely to stand on the switches [33191,31629,13], which open the
-- Gate of the Lost Souls [33211,31630,13]". Our 7.4 map has both switch tiles (stone tile 426/425, action id 50665
-- at 33190 and 33191,31629,13) and the gate: a row of stone walls (1050) at 33210-33212,31630,13 between the
-- "Gate of the Lost Souls" monuments. Decided with the user 2026-09-24: open only while both switches are held;
-- when one is left the wall comes back and whoever stands in the gap is pushed south, out of it.
local SWITCHES = {{x=33190, y=31629, z=13}, {x=33191, y=31629, z=13}}
local GATE = {{x=33210, y=31630, z=13}, {x=33211, y=31630, z=13}, {x=33212, y=31630, z=13}}
local WALL = 1050
local UP, DOWN = 426, 425

local function held(pos)
	return getThingfromPos({x=pos.x, y=pos.y, z=pos.z, stackpos=253}).uid > 0
end

local function setGate(open)
	for _, pos in ipairs(GATE) do
		local wall = getTileItemById(pos, WALL)
		if open and wall.uid > 0 then
			doRemoveItem(wall.uid)
		elseif not open and wall.uid == 0 then
			doRelocate(pos, {x=pos.x, y=pos.y + 1, z=pos.z})
			doCreateItem(WALL, 1, pos)
		end
	end
end

function onStepIn(cid, item, topos, frompos)
	if item.itemid == UP then
		doTransformItem(item.uid, DOWN)
	end
	if held(SWITCHES[1]) and held(SWITCHES[2]) then
		setGate(true)
	end
	return true
end

function onStepOut(cid, item, topos, frompos)
	if item.itemid == DOWN then
		doTransformItem(item.uid, UP)
	end
	-- the one leaving is already off its tile: both held means someone else stepped onto it at once
	if not (held(SWITCHES[1]) and held(SWITCHES[2])) then
		setGate(false)
	end
	return true
end

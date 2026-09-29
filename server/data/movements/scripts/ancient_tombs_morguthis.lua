-- The Ancient Tombs Quest, Morguthis's tomb (Tarpit Tomb; docs/reference-74/quests.md). Current wiki: past the level-75
-- doors "there's a puzzle before you can reach Morguthis. There are Deathslicers all around [...] The arena also
-- contains trapdoors. Trapdoors lead to caves which will all lead to different parts of the maze. To complete the
-- puzzle you must step in each blue flame in the maze. [...] Each teleport will take you upstairs of a nearby
-- 'sandstone switch tile' [...] these correspond to trapdoors". Decided with the user 2026-09-28:
--
-- 51129, the arena's closed trapdoors (floor 13): stepped on, one opens (it closes by itself, items.xml) and drops you
--   into the cave below. The caves' teleports lead up beside a trapdoor (map destinations, tibiaot74's).
-- 51150, the seven blue (mystic) flames in the caves: stepping in one marks it for you (storages 51151-51157).
-- 51158, the arena's last teleport (33263,32668,13): to Morguthis (33164,32694,14, tibiaot74's) once you have stepped
--   in all seven flames - they count again for the next time; otherwise back to the pocket before the level doors.
local CLOSED, OPEN = 461, 462
local FLAMES = {                          -- "x,y,z" -> its storage
	["33263,32681,14"] = 51151, ["33279,32682,14"] = 51152, ["33275,32685,14"] = 51153, ["33269,32698,14"] = 51154,
	["33270,32667,15"] = 51155, ["33245,32686,15"] = 51156, ["33252,32703,15"] = 51157,
}
local MORGUTHIS = {x=33164, y=32694, z=14}
local POCKET = {x=33260, y=32707, z=13}

local function allFlames(cid)
	for _, storage in pairs(FLAMES) do
		if getPlayerStorageValue(cid, storage) ~= 1 then
			return false
		end
	end
	return true
end

function onStepIn(cid, item, topos, frompos)
	if not isPlayer(cid) then
		return true
	end
	if item.actionid == 51129 and item.itemid == CLOSED then
		doTransformItem(item.uid, OPEN)
		local below = {x=topos.x, y=topos.y, z=topos.z + 1}
		doTeleportThing(cid, below)
		doSendMagicEffect(below, CONST_ME_POFF)
	elseif item.actionid == 51150 then
		local storage = FLAMES[topos.x .. "," .. topos.y .. "," .. topos.z]
		if storage ~= nil then
			setPlayerStorageValue(cid, storage, 1)
			doSendMagicEffect(topos, CONST_ME_MAGIC_BLUE)
		end
	elseif item.actionid == 51158 then
		local dest = POCKET
		if allFlames(cid) then
			for _, storage in pairs(FLAMES) do
				setPlayerStorageValue(cid, storage, 0)
			end
			dest = MORGUTHIS
		end
		doTeleportThing(cid, dest)
		doSendMagicEffect(dest, CONST_ME_ENERGYAREA)
	end
	return true
end

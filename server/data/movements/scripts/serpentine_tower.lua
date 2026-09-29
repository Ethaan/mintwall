-- Serpentine Tower Quest / White Pearl Quest (docs/reference-74/quests.md). TibiaWiki 2005: "Once at the top of the
-- pyramid, go down one level below the Library. In the room to the North, you need to place a pot on an open fire
-- (unless it is already there) - this will activate the portal on the East side of the room, so that it teleports
-- you into the quest room."
--
-- 51100, the open fire 33145,32862,7 (our map: the middle of three campfires, the other two already carry a pot): a pot
--   put on it becomes the campfire with a pot (1428). Decided with the user 2026-09-27: it stays so until the server
--   restarts (the map pot 33147,32867,7 is used up meanwhile).
-- 51101, the magic forcefield 33148,32864,7: into the pearl room (33151,32864,7, tibiaot74's destination) while the pot
--   is on the fire; otherwise it does nothing. The way out (33150,32864,7 -> 33147,32864,7, tibiaot74) is a plain map
--   teleport, always open (decided with the user).
local FIRE_POS = {x=33145, y=32862, z=7}
local OPEN_FIRE, POT_ON_FIRE = 1424, 1428
local POT = 2562
local PEARL_ROOM = {x=33151, y=32864, z=7}

local function potOnFire(pos)
	local pot = getTileItemById(pos, POT)
	local fire = getTileItemById(pos, OPEN_FIRE)
	if pot.uid > 0 and fire.uid > 0 then
		doRemoveItem(pot.uid)
		doTransformItem(fire.uid, POT_ON_FIRE)
		doSendMagicEffect(pos, CONST_ME_MAGIC_RED)
	end
end

function serpentinePotOnFire()
	return getTileItemById(FIRE_POS, POT_ON_FIRE).uid > 0
end

function onAddItem(moveitem, tileitem, pos)
	if moveitem.itemid == POT and tileitem.itemid == OPEN_FIRE then
		-- not while the engine is still moving the pot
		addEvent(potOnFire, 0, pos)
	end
	return true
end

function onStepIn(cid, item, topos, frompos)
	if item.actionid == 51101 and isPlayer(cid) and serpentinePotOnFire() then
		doTeleportThing(cid, PEARL_ROOM)
		doSendMagicEffect(PEARL_ROOM, CONST_ME_ENERGYAREA)
	end
	return true
end

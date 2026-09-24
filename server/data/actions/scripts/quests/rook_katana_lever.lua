-- Katana Quest (Rookgaard, docs/reference-74/quests.md): the hidden lever behind the northern white pillar
-- (action id 52412 at 32182,32145,11) unlocks the door of the katana room (32177,32148,11); pulled again it
-- locks it, and a teleport inside the room (32171,32149,11) then lets whoever is shut in get out (TibiaWiki
-- Katana Quest/Spoiler: "A teleport lets you out if you get locked in"). Positions as in tibiaot74's
-- "katana door.lua"; our map has a locked door (1209) where theirs has a wall.
local DOOR_POS = {x=32177, y=32148, z=11}
local LOCKED, UNLOCKED = 1209, 1210              -- locked door / closed door anyone can open (increment.lua)
local OPEN = 1211
local TELEPORT_POS = {x=32171, y=32149, z=11}
local OUTSIDE = {x=32178, y=32148, z=11}         -- where the teleport (and anyone in the doorway) goes
local TELEPORT = 1387

function onUse(cid, item, frompos, item2, topos)
	local locked = getTileItemById(DOOR_POS, LOCKED)
	if locked.uid > 0 then
		doTransformItem(locked.uid, UNLOCKED)
		local teleport = getTileItemById(TELEPORT_POS, TELEPORT)
		if teleport.uid > 0 then
			doRemoveItem(teleport.uid)
		end
	else
		local door = getTileItemById(DOOR_POS, OPEN)
		if door.uid == 0 then
			door = getTileItemById(DOOR_POS, UNLOCKED)
		end
		if door.uid > 0 then
			doRelocate(DOOR_POS, OUTSIDE)
			doTransformItem(door.uid, LOCKED)
		end
		if getTileItemById(TELEPORT_POS, TELEPORT).uid == 0 then
			doCreateTeleport(TELEPORT, OUTSIDE, TELEPORT_POS)
		end
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

-- The Ancient Tombs Quest, Rahemos's tomb (Oasis Tomb; docs/reference-74/quests.md). TibiaWiki 2006: "You need to
-- use levers to get a Carrot to be able to go through the next door. Each fault will cost you 200 hp"; current wiki:
-- "Each member of your team must find the Carrot under one of the three hats in order to enter the door. If you guess
-- wrong you will lose 200 hp."
--
-- 51124, the three switches behind the counters (33118,32761-32763,14): each lifts the hat on the counter in front of
--   it (33117, same y; unique ids 51140-51142 keep the hats there). The carrot is under a random one of the three on
--   every pull; found, it shows for a moment and the door opens for this player from then on (storage 51125), else
--   200 hp. Decided with the user 2026-09-28 (random, per player).
-- The door (33122,32765,14): a gap in our map's wall (and the JS engine's) - the quest door 1243 tibiaot74 has there,
--   action id 51125 = the storage (doors/questdoor_closed.lua).
local HAT, CARROT = 2662, 2684
local SWITCH_LEFT, SWITCH_RIGHT = 1945, 1946
local FOUND = 51125                     -- storage: this player found the carrot (the door's action id)
local SHOW_FOR = 3000

local function coverCarrot(pos)
	local carrot = getTileItemById(pos, CARROT)
	if carrot.uid > 0 then
		doTransformItem(carrot.uid, HAT)
	end
end

function onUse(cid, item, frompos, item2, topos)
	doTransformItem(item.uid, item.itemid == SWITCH_LEFT and SWITCH_RIGHT or SWITCH_LEFT)
	local hatPos = {x=frompos.x - 1, y=frompos.y, z=frompos.z}
	local hat = getTileItemById(hatPos, HAT)
	if hat.uid == 0 then
		return true                     -- this hat is up already
	end
	if math.random(1, 3) == 1 then
		doTransformItem(hat.uid, CARROT)
		addEvent(coverCarrot, SHOW_FOR, hatPos)
		setPlayerStorageValue(cid, FOUND, 1)
		doSendMagicEffect(hatPos, CONST_ME_MAGIC_GREEN)
	else
		doSendMagicEffect(hatPos, CONST_ME_POFF)
		doTargetCombatHealth(0, cid, COMBAT_UNDEFINEDDAMAGE, -200, -200, CONST_ME_DRAWBLOOD)
	end
	return true
end

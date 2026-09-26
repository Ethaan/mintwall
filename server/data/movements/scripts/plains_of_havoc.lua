-- Plains of Havoc quests (docs/reference-74/quests.md).
--
-- 51059, Ornamented Shield Quest part 2 (current wiki; the red bag is the real-map table's [4516] - decided with the
-- user 2026-09-25): "To remove these stalagmites, have your partner stand on the spot directly southwest of the fire
-- field in the northwest corner of the room" - the tile 32770,32282,10 in the dragon lair's treasure room holds the
-- stalagmites 32771,32297,10 (the way to the chest and the rope hole in the south-west corner) away while someone
-- stands on it; "you can either go back the way you came in (if the stalagmites are still being blocked by your
-- partner) or ... rope yourself up near the chest".
--
-- 51060, the Isle of the Mists portal near the orcs (32831,32294,7): the isle is druids only - decided with the user
-- 2026-09-25 (the quest's legend; no spoiler says the portal checks it). Druids and elder druids pass to the isle
-- (32851,32339,6, the map's destination); anyone else stays where they were.
local PLATE = {x=32770, y=32282, z=10, stackpos=253}     -- stackpos 253: a creature on it
local STALAGMITES_POS = {x=32771, y=32297, z=10}
local STALAGMITES = 387
local NORTH_OF_THEM = {x=32771, y=32296, z=10}

local ISLE = {x=32851, y=32339, z=6}
local DRUIDS = {[2] = true, [6] = true}

function onStepIn(cid, item, topos, frompos)
	if item.actionid == 51059 then
		local stalagmites = getTileItemById(STALAGMITES_POS, STALAGMITES)
		if stalagmites.uid > 0 then
			doRemoveItem(stalagmites.uid)
			doSendMagicEffect(STALAGMITES_POS, CONST_ME_POFF)
		end
	elseif item.actionid == 51060 and isPlayer(cid) then
		if DRUIDS[getPlayerVocation(cid)] then
			doTeleportThing(cid, ISLE)
			doSendMagicEffect(ISLE, CONST_ME_ENERGYAREA)
		else
			doTeleportThing(cid, frompos)
			doSendMagicEffect(frompos, CONST_ME_POFF)
		end
	end
	return true
end

function onStepOut(cid, item, topos, frompos)
	if item.actionid ~= 51059 then
		return true
	end
	if getThingfromPos(PLATE).uid > 0 then       -- someone else still stands on it
		return true
	end
	if getTileItemById(STALAGMITES_POS, STALAGMITES).uid == 0 then
		doRelocate(STALAGMITES_POS, NORTH_OF_THEM)
		doCreateItem(STALAGMITES, 1, STALAGMITES_POS)
	end
	return true
end

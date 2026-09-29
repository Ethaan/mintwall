-- The Ancient Tombs Quest (docs/reference-74/quests.md), what all eight tombs share.
--
-- 51120, the empty coal basin beside each tomb's mystic flame: TibiaWiki 2006, "At the bottom of the tombs will be an
--   empty coal basin, and a Mystic Flame. Stand on the flame, and place a Scarab Coin on the coal basin to be
--   teleported to the deeper parts of the tomb." One coin is used up and whoever stands on the flame goes to where our
--   map's flame pointed; with nobody on the flame the coin just lies there (decided with the user 2026-09-27: coin
--   needed, used up). The flames lost their map destinations; the flames back out are plain map teleports.
-- 51121, the magic forcefield in each pharaoh's room: current wiki, "Normally when entering the Magic Forcefield the
--   player will be taken to the start of the tomb; when this pass item is held by a character, the portal will instead
--   lead to a small room with the pharaoh's Sarcophagus". Our map's forcefields led into the sarcophagus rooms; the
--   start of the tomb is where each sarcophagus room's exit leads (by the entrance). The portal takes the pass item
--   (decided with the user: the item pages say "Trade this item for a <piece>"; a team of five kills each pharaoh five
--   times, TibiaWiki 2005).
local SCARAB_COIN = 2159

-- basin "x,y,z" -> the flame and where it leads (our map's flame destinations)
local FLAMES = {
	["33098,32816,13"] = {flame = {x=33097, y=32816, z=13}, to = {x=33093, y=32824, z=13}},   -- Peninsula Tomb (Omruc)
	["33293,32741,13"] = {flame = {x=33293, y=32742, z=13}, to = {x=33300, y=32742, z=13}},   -- Stone Tomb (Thalas)
	["33073,32589,13"] = {flame = {x=33073, y=32590, z=13}, to = {x=33080, y=32588, z=13}},   -- Mountain Tomb (Dipthrah)
	["33240,32855,13"] = {flame = {x=33240, y=32856, z=13}, to = {x=33246, y=32850, z=13}},   -- Shadow Tomb (Mahrdis)
	["33276,32552,14"] = {flame = {x=33276, y=32553, z=14}, to = {x=33271, y=32553, z=14}},   -- Ancient Ruins Tomb (Vashresamun)
	["33233,32692,13"] = {flame = {x=33234, y=32692, z=13}, to = {x=33234, y=32687, z=13}},   -- Tarpit Tomb (Morguthis)
	["33135,32682,12"] = {flame = {x=33135, y=32683, z=12}, to = {x=33130, y=32683, z=12}},   -- Oasis Tomb (Rahemos)
	["33161,32831,10"] = {flame = {x=33162, y=32831, z=10}, to = {x=33148, y=32870, z=11}},   -- Ankrahmun Library Tomb (Ashmunrah)
}

-- pharaoh portal "x,y,z" -> the pass item, the sarcophagus room (our map's destination), the start of the tomb
local PORTALS = {
	["33195,33002,14"] = {pass = 2352, room = {x=33179, y=33017, z=14}, back = {x=33028, y=32869, z=7}},   -- Omruc, crystal arrow
	["33396,32852,14"] = {pass = 2351, room = {x=33349, y=32830, z=14}, back = {x=33282, y=32742, z=7}},   -- Thalas, cobrafang dagger
	["33103,32590,15"] = {pass = 2354, room = {x=33127, y=32593, z=15}, back = {x=33132, y=32570, z=7}},   -- Dipthrah, ornamented ankh
	["33191,32959,15"] = {pass = 2353, room = {x=33175, y=32936, z=15}, back = {x=33254, y=32833, z=7}},   -- Mahrdis, burning heart
	["33116,32656,15"] = {pass = 2349, room = {x=33145, y=32667, z=15}, back = {x=33208, y=32589, z=7}},   -- Vashresamun, blue note
	["33174,32694,14"] = {pass = 2350, room = {x=33183, y=32716, z=14}, back = {x=33232, y=32704, z=7}},   -- Morguthis, sword hilt
	["33073,32781,14"] = {pass = 2348, room = {x=33052, y=32778, z=14}, back = {x=33133, y=32642, z=7}},   -- Rahemos, ancient rune
}

local function key(pos)
	return pos.x .. "," .. pos.y .. "," .. pos.z
end

local function sacrifice(basinPos)
	local flame = FLAMES[key(basinPos)]
	local coin = getTileItemById(basinPos, SCARAB_COIN)
	if flame == nil or coin.uid == 0 or getTopCreature(flame.flame).uid == 0 then
		return
	end
	doRemoveItem(coin.uid, 1)
	doSendMagicEffect(basinPos, CONST_ME_MAGIC_RED)
	doRelocate(flame.flame, flame.to)
	doSendMagicEffect(flame.to, CONST_ME_ENERGYAREA)
end

function onAddItem(moveitem, tileitem, pos)
	if moveitem.itemid == SCARAB_COIN then
		-- not while the engine is still moving the coin
		addEvent(sacrifice, 0, pos)
	end
	return true
end

function onStepIn(cid, item, topos, frompos)
	local portal = PORTALS[key(topos)]
	if portal == nil or not isPlayer(cid) then
		return true
	end
	local dest = portal.back
	if getPlayerItemCount(cid, portal.pass) > 0 then
		doPlayerRemoveItem(cid, portal.pass, 1)
		dest = portal.room
	end
	doTeleportThing(cid, dest)
	doSendMagicEffect(dest, CONST_ME_ENERGYAREA)
	return true
end

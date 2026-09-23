-- NPC-side compatibility for TFS/OTX 0.3-era NPC scripts and Jiddo's NpcSystem.
-- Loaded by scripts/lib/npc.lua before the NpcSystem itself.

-- Avesta's selfSay(msg, delay) vs TFS's selfSay(msg, cid, public): the TFS-era
-- scripts never pass a delay, so drop everything after the message.
if _nativeSelfSay == nil then
	_nativeSelfSay = selfSay
end
function selfSay(message)
	return _nativeSelfSay(tostring(message))
end
NPCSay = selfSay

getNpcId = getNpcCid

if os.mtime == nil then
	function os.mtime() return os.time() * 1000 end
end

function doSteerCreature(cid, position)
	return selfMoveTo(position.x, position.y, position.z)
end

-- TFS doTeleportThing(uid, pos, pushMove): Avesta takes (uid, pos) and reads the position off the
-- top of the stack, so a third argument made every boat trip fail - after taking the fare.
if _nativeTeleportThing == nil then
	_nativeTeleportThing = doTeleportThing
end
function doTeleportThing(uid, pos)
	return _nativeTeleportThing(uid, pos)
end

-- No trade window in 7.4, only talk-based shopping
function getShopOwner(cid) return nil end
function openShopWindow() return false end
function closeShopWindow() return false end

local containerCaps = {[1987] = 8, [1988] = 20}
function getContainerCapById(itemid)
	return containerCaps[itemid] or 20
end

-- "buy a backpack of <runes>"
function doPlayerBuyItemContainer(cid, containerid, itemid, count, cost, charges)
	if not doPlayerRemoveMoney(cid, cost) then
		return false
	end

	local cap = getContainerCapById(containerid)
	for i = 1, count do
		local container = doCreateItemEx(containerid, 1)
		for j = 1, cap do
			doAddContainerItem(container, itemid, charges or 1)
		end
		if doPlayerAddItemEx(cid, container, true) ~= RETURNVALUE_NOERROR then
			return false
		end
	end
	return true
end

dofile(getDataDir() .. 'npc/lib/itemconstants.lua')

-- Distance (in sqm) from this NPC to a creature, or -1 if on another floor / not found
function getNpcDistanceTo(cid)
	local pos = getCreaturePosition(cid)
	if type(pos) ~= "table" or pos.x == nil then
		return -1
	end
	local x, y, z = selfGetPosition()
	if z ~= pos.z then
		return -1
	end
	return math.max(math.abs(x - pos.x), math.abs(y - pos.y))
end

-- Used by a few quest NPCs as "does the player carry this item?"
function getPlayerItem(cid, itemid)
	return getPlayerItemCount(cid, itemid) > 0
end

function doPlayerSave(cid) return doSavePlayer(cid) end
function isValidMoney(value) return tonumber(value) ~= nil and tonumber(value) > 0 end
function doAddMapMark(cid, pos, markType, description) return false end

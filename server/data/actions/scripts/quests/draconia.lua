-- Draconia Quest, the pyramid (docs/reference-74/quests.md). TibiaWiki (2006, current), positions and pairs from
-- tibiaot74's draconia1/2.lua and "main movements.lua". Decided with the user 2026-09-26: the keys are the 7.x daily
-- ones - they lie in the pyramid and come back at the server save, the first one there takes them.
--
-- 51070, the ground floor: "Open a door with Key 3002 and pull a lever, which removes a wall. Pull the next lever, which
-- removes a rock, and take Key 3003." The lever 32792,31595,7 takes the framework wall 32792,31581,7 away / puts it back;
-- the lever 32792,31579,7 the stone 32790,31594,7 in front of key 3003.
-- 51073, the top floor's four levers (32802-32805,31584,1): they only turn; the portal reads them
-- (movements/scripts/draconia.lua: Left, Right, Left, Right).
-- 51077, the coffin 32802,31576,7: "Key 3002 is in a coffin" - a coffin is no container in 7.4, so the key comes from
-- here: the first one to open it after a server start takes it.
local BLOCKS = {
	["32792,31595"] = {pos = {x=32792, y=31581, z=7}, item = 1037, aside = {x=32792, y=31582, z=7}},
	["32792,31579"] = {pos = {x=32790, y=31594, z=7}, item = 1285, aside = {x=32790, y=31595, z=7}},
}
local KEY, KEY_3002 = 2088, 3002
local keyTaken = false

function onUse(cid, item, frompos, item2, topos)
	local aid = item.actionid
	if aid == 51070 then
		local block = BLOCKS[frompos.x .. "," .. frompos.y]
		if block == nil then
			return false
		end
		local thing = getTileItemById(block.pos, block.item)
		if thing.uid > 0 then
			doRemoveItem(thing.uid)
		else
			doRelocate(block.pos, block.aside)
			doCreateItem(block.item, 1, block.pos)
		end
	elseif aid == 51077 then
		if keyTaken then
			doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "The wooden coffin is empty.")
			return true
		end
		local key = doPlayerAddItem(cid, KEY, 1)
		if key == nil or key == false or key == 0 then
			return true
		end
		doSetItemActionId(key, KEY_3002)
		keyTaken = true
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "You have found a silver key.")
		return true
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

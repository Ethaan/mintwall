-- A locked door. With a key number (action id) only that key opens it (key.lua). Without one it is
-- either a house door - the engine already checked the player may enter (Door::canUse), so open it -
-- or a door the map keeps locked for good, like the one to Rookgaard's premium side at 32042,32205,6.
-- Opening those for anyone used to let free accounts walk around King's Bridge.
function onUse(cid, item, frompos, item2, topos)
	if(item.actionid == 0 and getTileHouseInfo(frompos) ~= 0) then
		doTransformItem(item.uid, item.itemid + 2)
		return true
	end

	doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "It is locked.")
	return true
end

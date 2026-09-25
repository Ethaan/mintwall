-- Draw wells you can climb down (action id 54545 on the map: Fibula 32172,32439,7 - "enter the dungeon through the
-- well", TibiaWiki Deeper Fibula Quest 2006 - and the Ancient Temple's at 32508,32176,13). Using one takes you to the
-- tile right below, where a ladder leads back up (as tibiaot74's "fibula draw well.lua").
function onUse(cid, item, frompos, item2, topos)
	local below = {x=frompos.x, y=frompos.y, z=frompos.z + 1}
	if getTileThingByPos({x=below.x, y=below.y, z=below.z, stackpos=0}).itemid == 0 then
		doPlayerSendCancel(cid, "Sorry, not possible.")
		return true
	end
	doTeleportThing(cid, below)
	return true
end

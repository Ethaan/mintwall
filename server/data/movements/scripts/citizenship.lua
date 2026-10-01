-- The portals of citizenship (TibiaWiki 2005, Portal of Citizenship: "a portal that you enter to become citizen of a
-- city. For example, in Ab'Dendriel to be a citizen you need to pass through a maze, and in Carlin the portal is right
-- under the temple"). The original map has one per town, action id 1001-1008 (Thais, Carlin, Kazordoon, Ab'Dendriel,
-- Edron, Darashia, Venore, Ankrahmun = town id 2-9, action id - 999), its destination that town's temple - but
-- nothing made you a citizen. The destination is the script's now (a portal with a map destination and a movement
-- script crashes the server). The message is ours (no 7.4 source).
function onStepIn(cid, item, topos, frompos)
	if not isPlayer(cid) then
		return true
	end
	local town = item.actionid - 999
	local temple = getTownTemplePosition(town)
	doPlayerSetTown(cid, town)
	doTeleportThing(cid, temple)
	doSendMagicEffect(temple, CONST_ME_ENERGYAREA)
	doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "You are now a citizen of " .. getTownNameById(town) .. ".")
	return true
end

-- Ground with action id 50003 is premium-only on the map (King's Bridge on Rookgaard: "Only premium
-- citizens may pass."). A free account that steps on it is sent back where it came from.
local function yes(v) return v == true or v == 1 end

function onStepIn(cid, item, topos, frompos)
	if(not yes(isPlayer(cid)) or yes(isPremium(cid))) then
		return true
	end

	doPlayerSendCancel(cid, "Only premium citizens may pass.")
	if(frompos.x ~= topos.x or frompos.y ~= topos.y or frompos.z ~= topos.z) then
		doTeleportThing(cid, frompos)
	else   -- logged in or teleported onto it: nowhere to step back to
		doTeleportThing(cid, getTownTemplePosition(getPlayerTown(cid)))
	end
	return true
end

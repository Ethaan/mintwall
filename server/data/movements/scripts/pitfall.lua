-- Pitfall (grass 293, 38 on the map; items.xml: pitfall 294 = floorchange down, decays back to grass after 300 s).
-- A player who steps on the grass falls through: the grass opens into the pitfall and the player drops to the floor
-- below. The engine takes floor changes when a step is planned (Tile::__queryDestination), not after a step-in script
-- changed the ground, so the old script left the player standing on the open pitfall. Only players spring it (the
-- old script opened it for monsters too, which then stood on the hole).
local function yes(v) return v == true or v == 1 end

function onStepIn(cid, item, topos, frompos)
	if item.itemid ~= 293 or not yes(isPlayer(cid)) then
		return true
	end
	doTransformItem(item.uid, 294)
	doDecayItem(item.uid)                  -- back to grass after its 300 s (items.xml)
	doTeleportThing(cid, {x=topos.x, y=topos.y, z=topos.z + 1})
	return true
end

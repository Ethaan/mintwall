-- Rookgaard Academy training arena (docs/reference-74/quests.md): four levers (action ids 50005-50008 at
-- 32088/32090/32092/32094,32148,9) under the blackboards "bug", "wolf", "troll", "spider". Each opens the gate
-- (framework wall 1037) of that monster's cage one floor down (same x, 32149,10); pulled back, it closes it.
-- Gate positions and item as in tibiaot74's "train monster1-4.lua". The sign by the levers (our map): "Pull a
-- lever to fight a monster of your choice. You have to close the door before you can open a new one." - so a
-- gate opens only while every other gate is shut.
local GATE = 1037
local GATES = {
	[50005] = {x=32088, y=32149, z=10},
	[50006] = {x=32090, y=32149, z=10},
	[50007] = {x=32092, y=32149, z=10},
	[50008] = {x=32094, y=32149, z=10},
}

local function isOpen(pos)
	return getTileItemById(pos, GATE).uid == 0
end

function onUse(cid, item, frompos, item2, topos)
	local gatePos = GATES[item.actionid]
	if gatePos == nil then
		return false
	end
	if item.itemid == 1945 then
		for aid, pos in pairs(GATES) do
			if aid ~= item.actionid and isOpen(pos) then
				doPlayerSendCancel(cid, "Sorry, not possible.")
				return true
			end
		end
		local gate = getTileItemById(gatePos, GATE)
		if gate.uid > 0 then
			doRemoveItem(gate.uid)
		end
	else
		if isOpen(gatePos) then
			-- whoever stands in the gateway (player or monster) goes out to the arena side, as tibiaot74's dumppos
			doRelocate(gatePos, {x=gatePos.x, y=gatePos.y + 1, z=gatePos.z})
			doCreateItem(GATE, 1, gatePos)
		end
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

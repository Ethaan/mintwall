-- Parchment Room Quest (docs/reference-74/quests.md), Edron Hero Cave. The coffin (quest uid 10057, quests/system.lua)
-- lies under a parchment: "Buried forever that he never shall return. Don't remove this seal or bad things may
-- happen." Taking the seal off the coffin (action id 51010, to the floor or into a backpack) calls 4 demons
-- (TibiaWiki: "4 Demons spawn around you"), beside the four stones of the room - positions as tibiaot74's
-- "Parchment.lua". A new seal lies on the coffin again after a minute (tibiaot74's time; no source gives one), so
-- the next group meets the same trap; the one taken away is just a parchment.
local COFFIN = {x=33063, y=31624, z=15}
local DEMONS = {{x=33060, y=31623, z=15}, {x=33066, y=31623, z=15}, {x=33060, y=31627, z=15}, {x=33066, y=31627, z=15}}
local SEAL = 1953
local SEAL_AID = 51010
local SEAL_TEXT = "Buried forever that he never shall return. Don't remove this seal or bad things may happen."
local RESEAL_MS = 60 * 1000

local function reseal()
	if getTileItemById(COFFIN, SEAL).uid == 0 then
		local seal = doCreateItem(SEAL, 1, COFFIN)
		doSetItemText(seal, SEAL_TEXT)
		doSetItemActionId(seal, SEAL_AID)
	end
end

function onRemoveItem(moveitem, tileitem, pos)
	if pos.x ~= COFFIN.x or pos.y ~= COFFIN.y or pos.z ~= COFFIN.z then
		return true                    -- a taken seal moved about elsewhere: nothing happens
	end
	for _, at in ipairs(DEMONS) do
		doSummonCreature("Demon", at)
	end
	addEvent(reseal, RESEAL_MS)
	return true
end

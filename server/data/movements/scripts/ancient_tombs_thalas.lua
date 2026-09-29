-- The Ancient Tombs Quest, Thalas's tomb (Stone Tomb; docs/reference-74/quests.md). Current wiki: "Everyone must step
-- on the switch to get poisoned, after getting poisoned say hi to the Cobra NPC to the south". Our map's floor-14
-- corridor ends in a forcefield (33399,32802,14) that pointed one tile back (a destination left to a script); behind
-- it lies the Cobra's corridor (npc/scripts/Cobra.lua), whose north end has the level-75 gate and the forcefield to
-- Thalas. The wiki's switches are not on the 7.4 map.
--
-- 51127, that forcefield: poisoned, into the Cobra's corridor near the Cobra; else back north as the map had it
--   (decided with the user 2026-09-28).
local CORRIDOR = {x=33367, y=32853, z=14}
local BACK = {x=33399, y=32801, z=14}

function onStepIn(cid, item, topos, frompos)
	if not isPlayer(cid) then
		return true
	end
	local dest = hasCondition(cid, CONDITION_POISON) and CORRIDOR or BACK
	doTeleportThing(cid, dest)
	doSendMagicEffect(dest, CONST_ME_ENERGYAREA)
	return true
end

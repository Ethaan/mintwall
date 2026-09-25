-- Thais Lighthouse Quest (docs/reference-74/quests.md). TibiaWiki (2006, oldid 61618): "there is a switch under
-- some crates which will open a ladder down which may already be open. [...] The other person must go down the
-- stairs and turn a lever. The lever turns on a teleporter in the right passage which leads to the quest room.
-- [...] People have also been known to trap others by turning off the portal so that they are trapped in the
-- cyclops room." The step switch is quests/thais_lighthouse_step.lua (movements).
--   51001: the switch under the crates (32227,32278,8) opens/closes the trapdoor above the ladder (32225,32276,8).
--   51002: (movements) the step switch.
--   51003: the lever (32225,32285,10) turns the portals on/off. The room has no other way out on any map we have,
--          so the lever makes two fields: in (east passage, 32233,32276,9 - tibiaot74's position and arrival
--          32225,32271,10) and out (the room's south corridor, 32225,32276,10). Decided with the user 2026-09-24.
-- Items: trapdoor 369 is what lies above ladders in dirt rooms on our map (290 of them).
local TRAPDOOR_POS = {x=32225, y=32276, z=8}
local DIRT, TRAPDOOR = 351, 369

local PORTAL_IN = {x=32233, y=32276, z=9}
local ROOM = {x=32225, y=32271, z=10}
local PORTAL_OUT = {x=32225, y=32276, z=10}
local EAST_PASSAGE = {x=32232, y=32276, z=9}
local FIELD = 1387

local function toggleTrapdoor()
	local closed = getTileItemById(TRAPDOOR_POS, DIRT)
	if closed.uid > 0 then
		doTransformItem(closed.uid, TRAPDOOR)
	else
		local open = getTileItemById(TRAPDOOR_POS, TRAPDOOR)
		if open.uid > 0 then
			doTransformItem(open.uid, DIRT)
		end
	end
end

local function portals(on)
	for _, field in ipairs({{PORTAL_IN, ROOM}, {PORTAL_OUT, EAST_PASSAGE}}) do
		local existing = getTileItemById(field[1], FIELD)
		if on and existing.uid == 0 then
			doCreateTeleport(FIELD, field[2], field[1])
		elseif not on and existing.uid > 0 then
			doRemoveItem(existing.uid)
		end
	end
end

function onUse(cid, item, frompos, item2, topos)
	if item.actionid == 51001 then
		toggleTrapdoor()
	elseif item.actionid == 51003 then
		portals(item.itemid == 1945)
	else
		return false
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

-- Serpentine Tower Quest, the "continuation" below the pearl room (docs/reference-74/quests.md). TibiaWiki 2005: "The
-- torch on the wall above the barrel lets the Fire Elemental downstairs out, the switch under where the Fire Elemental
-- was then lets the Green Djinn downstairs out." TibiaWiki 2006 / current: "Use the lamp. It will sparkle (red
-- sparkles on your body), but will not light. Go down the steps to the room with the caged creatures. BE CAREFUL! The
-- Fire Elemental will now be loose! Kill the Fire Elemental and flip the switch that is inside his cage. This will
-- remove the Magic Walls holding the Green Djinn downstairs." No reward is known.
--
-- 51182, the wall lamp above the barrel (33151,32861,7): not on our map, placed where tibiaot74 has an object on that
--   wall. Using it opens the fire elemental's cage (its front wall 33151,32866,8).
-- 51183, the switch in the fire elemental's cage (33152,32866,8): takes away the magic walls 33148-33149,32867-32868,9
--   between the stairs room and the hall where the green djinn stands (33149,32864,9).
-- Decided with the user 2026-09-27 (no source gives times): both close again after 5 minutes, but only while no player
-- is inside (the cage, the hall), so nobody is trapped; retried every 10 s. The green djinn's and the vampire's cage
-- switches flip and do nothing, as every wiki describes them (increment.lua / decrement.lua).
local CAGE_WALL, CAGE_WALL_POS = 1100, {x=33151, y=32866, z=8}
local CAGE = {x=33152, y=32866, z=8}
local CORRIDOR = {x=33150, y=32866, z=8}
local MAGIC_WALL = 1497               -- not decaying (the map's)
local MAGIC_WALLS = {{x=33148, y=32867, z=9}, {x=33149, y=32867, z=9}, {x=33148, y=32868, z=9}, {x=33149, y=32868, z=9}}
local STAIRS_ROOM = {x=33148, y=32869, z=9}
local HALL = {x=33147, y=32865, z=9}  -- the djinn's hall and the gap to the magic walls, x 33143-33152, y 32862-32868
local OPEN_FOR = 5 * 60 * 1000
local RETRY = 10 * 1000
local SWITCH_LEFT, SWITCH_RIGHT = 1945, 1946

local function playerAmong(center, rangex, rangey)
	for _, cid in ipairs(getSpectators(center, rangex, rangey) or {}) do
		if isPlayer(cid) then
			return true
		end
	end
	return false
end

local function playerOn(pos)
	local creature = getTopCreature(pos).uid
	return creature > 0 and isPlayer(creature)
end

local function closeCage()
	if getTileItemById(CAGE_WALL_POS, CAGE_WALL).uid > 0 then
		return
	end
	if playerOn(CAGE) or playerOn(CAGE_WALL_POS) then
		addEvent(closeCage, RETRY)
		return
	end
	doRelocate(CAGE_WALL_POS, CORRIDOR)
	doCreateItem(CAGE_WALL, 1, CAGE_WALL_POS)
end

local function closeMagicWalls()
	if playerAmong(HALL, 5, 3) then
		addEvent(closeMagicWalls, RETRY)
		return
	end
	for _, pos in ipairs(MAGIC_WALLS) do
		if getTileItemById(pos, MAGIC_WALL).uid == 0 then
			doRelocate(pos, STAIRS_ROOM)
			doCreateItem(MAGIC_WALL, 1, pos)
		end
	end
end

function onUse(cid, item, frompos, item2, topos)
	if item.actionid == 51182 then
		doSendMagicEffect(getPlayerPosition(cid), CONST_ME_MAGIC_RED)
		local wall = getTileItemById(CAGE_WALL_POS, CAGE_WALL)
		if wall.uid > 0 then
			doRemoveItem(wall.uid)
			addEvent(closeCage, OPEN_FOR)
		end
	elseif item.actionid == 51183 then
		doTransformItem(item.uid, item.itemid == SWITCH_LEFT and SWITCH_RIGHT or SWITCH_LEFT)
		local opened = false
		for _, pos in ipairs(MAGIC_WALLS) do
			local wall = getTileItemById(pos, MAGIC_WALL)
			if wall.uid > 0 then
				doRemoveItem(wall.uid)
				doSendMagicEffect(pos, CONST_ME_POFF)
				opened = true
			end
		end
		if opened then
			addEvent(closeMagicWalls, OPEN_FOR)
		end
	end
	return true
end

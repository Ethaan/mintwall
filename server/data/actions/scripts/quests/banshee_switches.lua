-- The Queen of the Banshees Quest (docs/reference-74/quests.md): the switches. The seal flames, the hidden buttons and
-- the rest are movements/scripts/banshee_seals.lua.
local DEMON_LEVERS = 51109            -- player storage: how many of the Demonrage levers they pulled in the right order

-- 51050: the two switches on the way to the Hidden Seal. "To open the Magic Walls you need to use 2 switches. There is
-- 1 switch west of here and 1 switch east" (TibiaWiki 2006); one wall each (tibiaot74's "Banshee mwall" scripts). The
-- walls close when someone steps on the hidden buttons behind them (current wiki) and, decided with the user
-- 2026-09-25 ("the walls close pretty fast", 2006), a minute after they opened.
local WALL_OF = {[32212] = {x=32259, y=31890, z=10}, [32315] = {x=32259, y=31891, z=10}}   -- switch x -> its wall
local WALL = 1497
local WALL_OPEN_FOR = 60 * 1000
local opened = {}                     -- wall -> times opened, so an older timer does not close a newer opening

local function closeWall(p)
	local key = p.pos.y
	if opened[key] ~= p.generation then
		return
	end
	if getTileItemById(p.pos, WALL).uid == 0 then
		local aside = {x=p.pos.x, y=(p.pos.y == 31890) and 31889 or 31892, z=p.pos.z}
		doRelocate(p.pos, aside)
		doCreateItem(WALL, 1, p.pos)
	end
end

-- 51051: floor 11, the room with the dead monk: "Use the switch to reveal some stairs" (current wiki) - a magic wall
-- lies on the trapdoor 32266,31860,11 on our map; the switch to the right takes it away, to the left puts it back.
local TRAPDOOR_WALL = {x=32266, y=31860, z=11}

-- 51053: the Seal of Demonrage levers 32220,31842-31846,15. Current wiki picture (coins beside the levers): the second,
-- the fourth, the third, the first, then the fifth from the north. Each player pulls them in that order; a wrong one
-- starts them over.
local LEVER_ORDER = {31843, 31845, 31844, 31842, 31846}

function onUse(cid, item, frompos, item2, topos)
	local aid = item.actionid
	local flipped = (item.itemid == 1945) and 1946 or 1945
	if aid == 51050 then
		local wallPos = WALL_OF[frompos.x]
		local wall = getTileItemById(wallPos, WALL)
		if wall.uid > 0 then
			doRemoveItem(wall.uid)
			opened[wallPos.y] = (opened[wallPos.y] or 0) + 1
			addEvent(closeWall, WALL_OPEN_FOR, {pos = wallPos, generation = opened[wallPos.y]})
		end
	elseif aid == 51051 then
		local wall = getTileItemById(TRAPDOOR_WALL, WALL)
		if item.itemid == 1945 and wall.uid > 0 then
			doRemoveItem(wall.uid)
		elseif item.itemid == 1946 and wall.uid == 0 then
			doCreateItem(WALL, 1, TRAPDOOR_WALL)
		end
	elseif aid == 51053 then
		local done = math.max(getPlayerStorageValue(cid, DEMON_LEVERS), 0)
		if done < #LEVER_ORDER and LEVER_ORDER[done + 1] == frompos.y then
			setPlayerStorageValue(cid, DEMON_LEVERS, done + 1)
		elseif done < #LEVER_ORDER then
			setPlayerStorageValue(cid, DEMON_LEVERS, (LEVER_ORDER[1] == frompos.y) and 1 or 0)
		end
	end
	-- 51052, the Seal of Logic's six switches: they only turn; the flame reads them
	doTransformItem(item.uid, flipped)
	return true
end

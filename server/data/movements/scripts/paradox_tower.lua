-- The Paradox Tower Quest (docs/reference-74/quests.md). TibiaWiki spoiler (Dec 2006); positions from our map and
-- tibiaot74 (movements/scripts/main_quests.lua, Main_OnAddItems.lua).
--
-- 51081, the strange carving between the four sacrifice stones (32566,31957,1): "place one skull on each stone and walk
--   to the teleport spot in the middle - you will be teleported to the tower"; "the skulls will be replaced by Poison
--   Fields". Arrival 32479,31923,7 (tibiaot74). Without four skulls nothing happens.
-- 51082, the four strange carvings by the arrival (32486-32487,31927-31928,7): "If you step on one of the four strange
--   carvings here, you will be teleported back away from the tower" - to 32566,31958,1 (tibiaot74).
-- 51083, the switch plate in the tower's south-east corner (32481,31905,7): "The big stone will turn into a staircase"
--   (the stone 32478,31902,7). 51084, the doorway (32478-32479,31907,7): "Stepping into the doorway makes the staircase
--   disappear again".
-- 51087, the ghoul room's north-west corner (32476,31900,5): "Wait until the ghoul pushes the box into the north-west
--   corner of his area, and a ladder will appear. Go up the ladder before the ghoul moves the box again." - a crate
--   put there makes the ladder 32478,31904,5 (our map's spot), taken away it removes it.
-- 51090, the treasure room's switch plates (x 32476-32481, y 31902/31903, z 1): "Each switch will DESTROY one of the
--   rewards for you" - the wiki's pattern, row 1 K W T T T K, row 2 E E E K W W (K 10k, W wand, T talons, E phoenix
--   egg). A destroyed reward is its chest's storage set: the chest then is "empty" for that character
--   (quests/system.lua), as tibiaot74 does it.
local SKULL, POISON_FIELD = 2229, 1496
local STONES = {{x=32563, y=31957, z=1}, {x=32565, y=31957, z=1}, {x=32567, y=31957, z=1}, {x=32569, y=31957, z=1}}
local TOWER = {x=32479, y=31923, z=7}
local BACK = {x=32566, y=31958, z=1}

local STONE, STAIRS = 1304, 1385
local STAIRS_POS = {x=32478, y=31902, z=7}

local CRATE, LADDER = 1739, 1386
local GHOUL_LADDER = {x=32478, y=31904, z=5}

local EGG, TEN_K, TALONS, WAND = 51091, 51092, 51093, 51094      -- the chests' unique ids = storages
local CHEST_POS = {[EGG] = {x=32477, y=31900, z=1}, [TEN_K] = {x=32478, y=31900, z=1},
                   [TALONS] = {x=32479, y=31900, z=1}, [WAND] = {x=32480, y=31900, z=1}}
local PLATES = {
	[31902] = {TEN_K, WAND, TALONS, TALONS, TALONS, TEN_K},
	[31903] = {EGG, EGG, EGG, TEN_K, WAND, WAND},
}

local function teleport(cid, pos)
	doTeleportThing(cid, pos)
	doSendMagicEffect(pos, CONST_ME_TELEPORT)
end

local function sacrifice(cid)
	local skulls = {}
	for i, pos in ipairs(STONES) do
		local skull = getTileItemById(pos, SKULL)
		if skull.uid == 0 then
			return
		end
		skulls[i] = skull
	end
	for i, skull in ipairs(skulls) do
		doRemoveItem(skull.uid, 1)
		doCreateItem(POISON_FIELD, 1, STONES[i])
	end
	teleport(cid, TOWER)
end

function onStepIn(cid, item, topos, frompos)
	if not isPlayer(cid) then
		return true
	end
	local aid = item.actionid
	if aid == 51081 then
		sacrifice(cid)
	elseif aid == 51082 then
		teleport(cid, BACK)
	elseif aid == 51083 then
		local stone = getTileItemById(STAIRS_POS, STONE)
		if stone.uid > 0 then
			doTransformItem(stone.uid, STAIRS)
			doSendMagicEffect(STAIRS_POS, CONST_ME_POFF)
		end
	elseif aid == 51084 then
		local stairs = getTileItemById(STAIRS_POS, STAIRS)
		if stairs.uid > 0 then
			doTransformItem(stairs.uid, STONE)
			doSendMagicEffect(STAIRS_POS, CONST_ME_POFF)
		end
	elseif aid == 51090 then
		local row = PLATES[topos.y]
		local chest = row and row[topos.x - 32475]
		if chest ~= nil then
			if getPlayerStorageValue(cid, chest) ~= 1 then
				setPlayerStorageValue(cid, chest, 1)
			end
			doSendMagicEffect(CHEST_POS[chest], CONST_ME_EXPLOSIONAREA)
		end
	end
	return true
end

function onAddItem(moveitem, tileitem, pos)
	if moveitem.itemid == CRATE and getTileItemById(GHOUL_LADDER, LADDER).uid == 0 then
		doCreateItem(LADDER, 1, GHOUL_LADDER)
		doSendMagicEffect(GHOUL_LADDER, CONST_ME_MAGIC_BLUE)
	end
	return true
end

function onRemoveItem(moveitem, tileitem, pos)
	if moveitem.itemid == CRATE then
		local ladder = getTileItemById(GHOUL_LADDER, LADDER)
		if ladder.uid > 0 then
			doRemoveItem(ladder.uid, 1)
			doSendMagicEffect(GHOUL_LADDER, CONST_ME_POFF)
		end
	end
	return true
end

-- The Paradox Tower Quest (docs/reference-74/quests.md). TibiaWiki spoiler (Dec 2006) and the first revision (2005);
-- positions and item checks from tibiaot74 (switch/main/paradox_*.lua, quest.lua), our map's own ladder spots.
--
-- 51080, the dead tree north of the tower (32497,31887,7): Key 3899 - "The tree is booby trapped so you might lose up to
--   200hp and Poison Fields may block your path when you go to leave the tree (this trap is not always triggered)".
--   Once per character (storage 51080); the trap: half the time, up to 200 damage (never the last hit point - a
--   scripted loss of health is no death here) and poison fields where tibiaot74 has them.
-- 51085, the lever room's switch (32479,31905,6): the six levers "need to be in the following directions (from left to
--   right): Right, Right, Left, Left, Right, Left" (a lever pulled right is 1946) - then the ladder 32479,31903,6.
-- 51086, the ghoul room's switch (32481,31904,5): "Flip the switch and a crate will appear with the ghoul" (32479,31901,5,
--   tibiaot74's spot; one crate at a time). The ladder comes from the crate in the corner (movements/paradox_tower.lua).
-- 51088, the fruit switch (32479,31905,4): melon, banana, cherry, apple, grapes, coconut on the six counters
--   32476-32481,31900,4, left to right - they are eaten and the ladder 32476,31904,4 appears.
-- 51089, the chess switch (32478,31904,3): the white knight on the plate below Cedric's side (32478,31903,3), the black
--   knight on Tristan's (32479,31903,3) - the pieces are taken and the ladder 32479,31904,3 appears.
-- The ladders stay until the server restarts ("You only need to set the levers, sacrifice the fruit, and use the chess
-- pieces one time. Only exception to this would be a server reset").
local KEY_TREE = 51080
local COPPER_KEY, KEY_3899 = 2089, 3899
local POISON_FIELD = 1496
local TRAP_FIELDS = {{x=32494, y=31888, z=7}, {x=32497, y=31889, z=7}, {x=32498, y=31889, z=7}, {x=32499, y=31889, z=7},
                     {x=32497, y=31890, z=7}, {x=32498, y=31890, z=7}, {x=32499, y=31890, z=7}}
local LADDER, CRATE = 1386, 1739
local LEFT, RIGHT = 1945, 1946

local LEVERS = {{x=32476, y=31900, z=6}, {x=32477, y=31900, z=6}, {x=32478, y=31900, z=6},
                {x=32479, y=31900, z=6}, {x=32480, y=31900, z=6}, {x=32481, y=31900, z=6}}
local LEVER_ORDER = {RIGHT, RIGHT, LEFT, LEFT, RIGHT, LEFT}
local LEVER_LADDER = {x=32479, y=31903, z=6}

local GHOUL_CRATE = {x=32479, y=31901, z=5}
local GHOUL_ROOM = {x1=32476, y1=31900, x2=32481, y2=31901, z=5}

local FRUIT = {2682, 2676, 2679, 2674, 2681, 2678}       -- melon, banana, cherry, apple, grapes, coconut
local FRUIT_LADDER = {x=32476, y=31904, z=4}

local WHITE_KNIGHT, BLACK_KNIGHT = 2628, 2634
local CHESS = {{pos = {x=32478, y=31903, z=3}, piece = WHITE_KNIGHT}, {pos = {x=32479, y=31903, z=3}, piece = BLACK_KNIGHT}}
local CHESS_LADDER = {x=32479, y=31904, z=3}

local function flip(item)
	doTransformItem(item.uid, item.itemid == LEFT and RIGHT or LEFT)
end

local function ladder(pos)
	if getTileItemById(pos, LADDER).uid == 0 then
		doCreateItem(LADDER, 1, pos)
		doSendMagicEffect(pos, CONST_ME_MAGIC_BLUE)
	end
end

local function tree(cid)
	if getPlayerStorageValue(cid, KEY_TREE) == 1 then
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "The dead tree is empty.")
		return true
	end
	local key = doPlayerAddItem(cid, COPPER_KEY, 1)
	if key == nil or key == false or key == 0 then
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, string.format("You have found a copper key. Weighing %.2f oz it is too heavy.",
			getItemWeightById ~= nil and getItemWeightById(COPPER_KEY, 1) or 1))   -- Cip's words (quests/system.lua)
		return true
	end
	doSetItemActionId(key, KEY_3899)
	setPlayerStorageValue(cid, KEY_TREE, 1)
	doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "You have found a copper key.")
	if math.random(1, 2) == 1 then
		local damage = math.min(math.random(1, 200), getCreatureHealth(cid) - 1)
		if damage > 0 then
			doCreatureAddHealth(cid, -damage)
		end
		doSendMagicEffect(getThingPos(cid), CONST_ME_POISONAREA)
		for _, pos in ipairs(TRAP_FIELDS) do
			if getTileItemById(pos, POISON_FIELD).uid == 0 then
				doCreateItem(POISON_FIELD, 1, pos)
			end
		end
	end
	return true
end

local function levers()
	for i, pos in ipairs(LEVERS) do
		if getTileItemById(pos, LEVER_ORDER[i]).uid == 0 then
			return false
		end
	end
	return true
end

local function crateInGhoulRoom()
	for x = GHOUL_ROOM.x1, GHOUL_ROOM.x2 do
		for y = GHOUL_ROOM.y1, GHOUL_ROOM.y2 do
			if getTileItemById({x=x, y=y, z=GHOUL_ROOM.z}, CRATE).uid > 0 then
				return true
			end
		end
	end
	return false
end

local function fruit()
	local found = {}
	for i, id in ipairs(FRUIT) do
		local item = getTileItemById({x=32475 + i, y=31900, z=4}, id)
		if item.uid == 0 then
			return false
		end
		found[i] = item
	end
	for _, item in ipairs(found) do
		doRemoveItem(item.uid, 1)
	end
	return true
end

local function chess()
	local found = {}
	for i, square in ipairs(CHESS) do
		local item = getTileItemById(square.pos, square.piece)
		if item.uid == 0 then
			return false
		end
		found[i] = item
	end
	for _, item in ipairs(found) do
		doRemoveItem(item.uid, 1)
	end
	return true
end

function onUse(cid, item, frompos, item2, topos)
	local aid = item.actionid
	if aid == KEY_TREE then
		return tree(cid)
	end
	flip(item)
	if aid == 51085 then
		if levers() then
			ladder(LEVER_LADDER)
		end
	elseif aid == 51086 then
		if not crateInGhoulRoom() then
			doCreateItem(CRATE, 1, GHOUL_CRATE)
			doSendMagicEffect(GHOUL_CRATE, CONST_ME_MAGIC_BLUE)
		end
	elseif aid == 51088 then
		if fruit() then
			ladder(FRUIT_LADDER)
		end
	elseif aid == 51089 then
		if chess() then
			ladder(CHESS_LADDER)
		end
	end
	return true
end

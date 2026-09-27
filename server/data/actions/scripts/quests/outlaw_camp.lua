-- The Outlaw Camp Quest (Bright Sword Quest, docs/reference-74/quests.md). TibiaWiki spoiler (2006); positions from our
-- map and tibiaot74 (switch/main/Outlaw oven.lua, Bright sword wall.lua, bright-sword-quest-switch2.lua).
--
-- 51035, the switch behind the key-3303 door (32614,32173,9): "This switch moves an oven in the room directly south of
--   you [...] If the switch is in the correct position, you can fit behind the oven and open the chest" - the oven
--   32623,32188,9 (lost on our map; tibiaot74's) goes and comes back.
-- 51036, the switch by the wooden surface (32594,32212,9): "Place the Power Ring on the wooden surface, and then flip the
--   switch. The Power Ring will disappear. Actually, it is simply teleported to another location" - from the counter
--   32594,32214,9 to the counter behind the mill room's wall (32613,32220,10), and the right passage opens (the walls
--   32603-32604,32216,9).
-- 51037, the mill's switch (32616,32222,10): "The Power Ring will turn into a fire field, and there will also be a fire
--   field that appears near the switch" - and the wall past the level-45 gate moves (the stone 32614,32206,10) as far
--   as the barrel in its notch (32614,32209,10) lets it: with no barrel there it stays shut. "The last switch you use
--   can only be flipped ONCE per day" - once per server start here, like the Draconia keys. The right passage closes
--   again; after 5 minutes the stone is back and the barrel gone (tibiaot74).
local OVEN, OVEN_POS = 1787, {x=32623, y=32188, z=9}
local POWER_RING = 2166
local PAYMENT = {x=32594, y=32214, z=9}
local RING_BEHIND_WALL = {x=32613, y=32220, z=10}
local PASSAGE = {{x=32603, y=32216, z=9}, {x=32604, y=32216, z=9}}
local BRICK_WALL = 1026
local STONE, STONE_POS = 1304, {x=32614, y=32206, z=10}
local BARREL, NOTCH = 1774, {x=32614, y=32209, z=10}
local FIRE_FIELD = 1492
local NEAR_SWITCH = {x=32615, y=32221, z=10}
local RESET = 5 * 60 * 1000

local millUsed = false

local function flip(item)
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
end

local function closePassage()
	for _, pos in ipairs(PASSAGE) do
		if getTileItemById(pos, BRICK_WALL).uid == 0 then
			doCreateItem(BRICK_WALL, 1, pos)
		end
	end
end

local function resetMill()
	if getTileItemById(STONE_POS, STONE).uid == 0 then
		doRelocate(STONE_POS, {x=STONE_POS.x, y=STONE_POS.y - 1, z=STONE_POS.z})
		doCreateItem(STONE, 1, STONE_POS)
	end
	local barrel = getTileItemById(NOTCH, BARREL)
	if barrel.uid > 0 then
		doRemoveItem(barrel.uid, 1)
	end
end

function onUse(cid, item, frompos, item2, topos)
	local aid = item.actionid
	if aid == 51035 then
		local oven = getTileItemById(OVEN_POS, OVEN)
		if oven.uid > 0 then
			doRemoveItem(oven.uid, 1)
		else
			doRelocate(OVEN_POS, {x=OVEN_POS.x, y=OVEN_POS.y + 1, z=OVEN_POS.z})
			doCreateItem(OVEN, 1, OVEN_POS)
		end
		flip(item)
	elseif aid == 51036 then
		local ring = getTileItemById(PAYMENT, POWER_RING)
		flip(item)
		if ring.uid == 0 then
			doSendMagicEffect(getThingPos(item.uid), CONST_ME_POFF)
			return true
		end
		doRemoveItem(ring.uid, 1)
		doSendMagicEffect(PAYMENT, CONST_ME_TELEPORT)
		doCreateItem(POWER_RING, 1, RING_BEHIND_WALL)
		for _, pos in ipairs(PASSAGE) do
			local wall = getTileItemById(pos, BRICK_WALL)
			if wall.uid > 0 then
				doRemoveItem(wall.uid, 1)
			end
		end
	elseif aid == 51037 then
		local ring = getTileItemById(RING_BEHIND_WALL, POWER_RING)
		if millUsed or ring.uid == 0 then
			doPlayerSendCancel(cid, "Sorry, not possible.")
			return true
		end
		millUsed = true
		flip(item)
		doRemoveItem(ring.uid, 1)
		doCreateItem(FIRE_FIELD, 1, RING_BEHIND_WALL)
		doCreateItem(FIRE_FIELD, 1, NEAR_SWITCH)
		closePassage()
		if getTileItemById(NOTCH, BARREL).uid > 0 then
			local stone = getTileItemById(STONE_POS, STONE)
			if stone.uid > 0 then
				doRemoveItem(stone.uid, 1)
				doSendMagicEffect(STONE_POS, CONST_ME_POFF)
			end
			addEvent(resetMill, RESET)
		end
	end
	return true
end

-- The Queen of the Banshees Quest (docs/reference-74/quests.md). TibiaWiki spoiler (Dec 2006 and current), positions
-- from our map and tibiaot74's banshee scripts. Six blue flames (mystic flame 1397), one per seal: stepping into one
-- whose task is done marks the seal for the player and sends them to its chamber on floor 15 (the six rooms around
-- 32259-32274,31847-31858 with the seals' monuments); the chamber's portal leads back to the seal. The Queen (npc)
-- gives the seventh. Each seal is a player storage, and each of the seven doors in front of the final room
-- (32223,31872-31890,14) opens for the one storage it carries as its action id (doors/questdoor_closed.lua).
local SEAL = {HIDDEN = 51101, PLAGUE = 51102, DEMONRAGE = 51103, SACRIFICE = 51104, TRUE_PATH = 51105, LOGIC = 51106,
              KISS = 51107}
local DEMON_TILE, DEMON_LEVERS = 51108, 51109   -- stepped on a warlock tile / levers pulled in order (actions script)

-- action id -> the flame: its seal, the chamber it sends you to, and what must be done first
local FLAMES = {
	-- First, the Hidden Seal (32278,31903,13, down the pick hole in the long hall): "for every party member that goes
	-- through, 2 ghosts and a demon skeleton will be summoned" (positions: tibiaot74's seal_1.lua)
	[51040] = {seal = SEAL.HIDDEN, chamber = {x=32266, y=31849, z=15}},
	-- Second, the Plague Seal (32171,31853,15): past the pearls (51049 below) and the poison fields
	[51041] = {seal = SEAL.PLAGUE, chamber = {x=32273, y=31849, z=15}},
	-- Third, the Seal of Demonrage (32215,31849,15): a warlock tile stepped on, the five levers pulled in order
	[51042] = {seal = SEAL.DEMONRAGE, chamber = {x=32273, y=31856, z=15}},
	-- Fourth, the Seal of Sacrifice (32250,31892,14): blood spilled "between the two stones" (32243,31892,14)
	[51043] = {seal = SEAL.SACRIFICE, chamber = {x=32261, y=31849, z=15}},
	-- Fifth, the Seal of the True Path (32192,31938,14): only the path's tiles lead here (51046 below)
	[51044] = {seal = SEAL.TRUE_PATH, chamber = {x=32268, y=31856, z=15}},
	-- Sixth, the Seal of Logic (32311,31978,13): the six switches set as the wiki's picture shows
	[51045] = {seal = SEAL.LOGIC, chamber = {x=32261, y=31856, z=15}},
}

local HIDDEN_GUARDS = {{"Ghost", {x=32274, y=31902, z=13}}, {"Ghost", {x=32274, y=31904, z=13}},
                       {"Demon Skeleton", {x=32276, y=31902, z=13}}}
local BLOOD_SPOT = {x=32243, y=31892, z=14}
local SPLASH, BLOOD = 2025, 2
-- Seal of Logic, current wiki picture: in both rows the two western switches thrown to the right, the eastern one not
local LOGIC_SWITCHES = {
	{{x=32310, y=31975, z=13}, 1946}, {{x=32312, y=31975, z=13}, 1946}, {{x=32314, y=31975, z=13}, 1945},
	{{x=32310, y=31976, z=13}, 1946}, {{x=32312, y=31976, z=13}, 1946}, {{x=32314, y=31976, z=13}, 1945},
}
local LEVERS_IN_ORDER = 5

local function logicSolved()
	for _, s in ipairs(LOGIC_SWITCHES) do
		if getTileItemById(s[1], s[2]).uid == 0 then
			return false
		end
	end
	return true
end

local function ready(cid, aid)
	if aid == 51043 then
		local pool = getTileItemById(BLOOD_SPOT, SPLASH)
		if pool.uid == 0 or pool.type ~= BLOOD then
			return false
		end
		doRemoveItem(pool.uid)                   -- each one spills their own
		doSendMagicEffect(BLOOD_SPOT, CONST_ME_MAGIC_RED)
	elseif aid == 51042 then
		return getPlayerStorageValue(cid, DEMON_TILE) == 1 and getPlayerStorageValue(cid, DEMON_LEVERS) >= LEVERS_IN_ORDER
	elseif aid == 51045 then
		return logicSolved()
	end
	return true
end

local function back(cid, frompos)
	doTeleportThing(cid, frompos)
	doSendMagicEffect(frompos, CONST_ME_POFF)
end

-- True Path: the puzzle tiles off the path (current wiki picture) send you back to the start of the room
local TRUE_PATH_START = {x=32185, y=31938, z=14}
-- the walls on the way to the Hidden Seal (actions/scripts/quests/banshee_switches.lua opens them)
local WALLS = {{x=32259, y=31890, z=10}, {x=32259, y=31891, z=10}}
local WALL = 1497
-- warlocks for every player who steps on a tile the first time ("One will spawn north of the tiles, in the corridor,
-- while another will spawn south in the room below"; tibiaot74's seal_5.lua positions)
local WARLOCKS = {{x=32216, y=31833, z=15}, {x=32217, y=31840, z=15}}
-- the pearls: white on the west table, black on the east one (current wiki picture; tibiaot74)
local WHITE_TABLE, BLACK_TABLE = {x=32173, y=31871, z=15}, {x=32180, y=31871, z=15}
local WHITE_PEARL, BLACK_PEARL = 2143, 2144
local BEHIND_PEARLS = {[32176] = {x=32176, y=31863, z=15}, [32177] = {x=32177, y=31863, z=15}}
-- the long hall on floor 12: "Somewhere in the middle of this is a secret teleporter that teleports you back to the
-- beginning. Pick a hole in the middle of the hall, and go under the teleporter" (TibiaWiki 2006) - the row right south
-- of the pick spot 32266,31892,12 (the wiki's picture: between it and where the first seal's rope comes back up), so
-- the hall's south end is reached only through the Hidden Seal. Back to where the portal into the hall puts you.
local HALL_START = {x=32266, y=31864, z=12}
-- the final room's way out: to the Ghostlands, and "Once you leave the room ... you can't enter again"
local GHOSTLANDS = {x=32199, y=31834, z=7}

local function closeWalls()
	for i, pos in ipairs(WALLS) do
		if getTileItemById(pos, WALL).uid == 0 then
			doRelocate(pos, {x=pos.x, y=(i == 1) and pos.y - 1 or pos.y + 1, z=pos.z})
			doCreateItem(WALL, 1, pos)
		end
	end
end

function onStepIn(cid, item, topos, frompos)
	if not isPlayer(cid) then
		return true
	end
	local aid = item.actionid
	local flame = FLAMES[aid]
	if flame ~= nil then
		if not ready(cid, aid) then
			back(cid, frompos)
			return true
		end
		setPlayerStorageValue(cid, flame.seal, 1)
		if aid == 51040 then
			for _, guard in ipairs(HIDDEN_GUARDS) do
				doSummonCreature(guard[1], guard[2])
			end
		end
		doTeleportThing(cid, flame.chamber)
		doSendMagicEffect(flame.chamber, CONST_ME_ENERGYAREA)
	elseif aid == 51046 then
		doTeleportThing(cid, TRUE_PATH_START)
		doSendMagicEffect(TRUE_PATH_START, CONST_ME_MAGIC_RED)
	elseif aid == 51047 then
		closeWalls()
	elseif aid == 51048 then
		if getPlayerStorageValue(cid, DEMON_TILE) ~= 1 then
			setPlayerStorageValue(cid, DEMON_TILE, 1)
			for _, pos in ipairs(WARLOCKS) do
				doSummonCreature("Warlock", pos)
			end
		end
	elseif aid == 51049 then
		local white = getTileItemById(WHITE_TABLE, WHITE_PEARL)
		local black = getTileItemById(BLACK_TABLE, BLACK_PEARL)
		if white.uid > 0 and black.uid > 0 then
			doRemoveItem(white.uid, 1)
			doRemoveItem(black.uid, 1)
			doSendMagicEffect(WHITE_TABLE, CONST_ME_POFF)
			doSendMagicEffect(BLACK_TABLE, CONST_ME_POFF)
			local dest = BEHIND_PEARLS[topos.x]
			doTeleportThing(cid, dest)
			doSendMagicEffect(dest, CONST_ME_ENERGYAREA)
		else
			back(cid, frompos)
		end
	elseif aid == 51056 then
		doTeleportThing(cid, HALL_START)
		doSendMagicEffect(HALL_START, CONST_ME_ENERGYAREA)
	elseif aid == 51055 then
		if getPlayerStorageValue(cid, SEAL.KISS) == 1 then
			setPlayerStorageValue(cid, SEAL.KISS, 2)    -- the seventh door stays shut for them from now on
		end
		doTeleportThing(cid, GHOSTLANDS)
		doSendMagicEffect(GHOSTLANDS, CONST_ME_ENERGYAREA)
	end
	return true
end

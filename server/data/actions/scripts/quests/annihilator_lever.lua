-- Annihilator Quest (docs/reference-74/quests.md), Edron Hero Cave. TibiaWiki (2005): "The four level 100's line up
-- on the designated squares and the formost pulls the lever. You are sent to a nearby room with six Demons. Two
-- north, two south and two dead ahead blocking the door." The lever (action id 51011 at 33226,31671,13) and the four
-- squares (33222-33225,31671,13) are on our map under the blackboard "Pull the lever and die with your friends";
-- where the players land and where the six demons appear are tibiaot74's positions (quest/annihilator.lua).
-- One reward per character (the four chests share storage 51012, quests/system.lua): nobody who has one may come.
-- Decided with the user 2026-09-24: the lever works once per server save - pulled, it stays down until the
-- restart (the map loads it up again) - and any wrong team gets the engine's "Sorry, not possible.".
local SQUARES = {                                   -- front (next to the lever) first
	{x=33225, y=31671, z=13}, {x=33224, y=31671, z=13}, {x=33223, y=31671, z=13}, {x=33222, y=31671, z=13},
}
local ARRIVAL = {
	{x=33222, y=31659, z=13}, {x=33221, y=31659, z=13}, {x=33220, y=31659, z=13}, {x=33219, y=31659, z=13},
}
local DEMONS = {
	{x=33219, y=31657, z=13}, {x=33221, y=31657, z=13},     -- north
	{x=33220, y=31661, z=13}, {x=33222, y=31661, z=13},     -- south
	{x=33223, y=31659, z=13}, {x=33224, y=31659, z=13},     -- ahead, in front of the door
}
local LEVEL = 100
local DONE = 51012                                  -- the reward chests' storage
local READY, PULLED = 1946, 1945

local function notPossible(cid)
	doPlayerSendCancel(cid, "Sorry, not possible.")
	return true
end

function onUse(cid, item, frompos, item2, topos)
	if item.itemid ~= READY then
		return notPossible(cid)                     -- pulled already: until the next server save
	end
	local team = {}
	for i, square in ipairs(SQUARES) do
		local thing = getThingfromPos({x=square.x, y=square.y, z=square.z, stackpos=253})
		if thing.uid == 0 or not isPlayer(thing.uid) then
			return notPossible(cid)
		end
		if getPlayerLevel(thing.uid) < LEVEL or getPlayerStorageValue(thing.uid, DONE) > 0 then
			return notPossible(cid)
		end
		team[i] = thing.uid
	end
	for _, at in ipairs(DEMONS) do
		doSummonCreature("Demon", at)
	end
	for i, player in ipairs(team) do
		doSendMagicEffect(SQUARES[i], CONST_ME_TELEPORT)
		doTeleportThing(player, ARRIVAL[i])
		doSendMagicEffect(ARRIVAL[i], CONST_ME_TELEPORT)
	end
	doTransformItem(item.uid, PULLED)
	return true
end

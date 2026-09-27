-- The Desert Dungeon Quest (docs/reference-74/quests.md): the lever next to the paladin's switch (32673,32086,8).
-- TibiaWiki 2006: with all four on their switches - one of each vocation, level 20 or more, each with his sacrifice on
-- the basin behind him - "the paladin pulls the lever", the sacrifices are gone and the four stand in the reward room
-- (two chests; the stairs north lead out, there is no way back in). tibiaot74's "desert quest.lua" for the positions.
-- The same switches as movements/scripts/desert_dungeon.lua (the two script kinds do not share Lua globals).
local SWITCHES = {
	{pos = {x=32677, y=32089, z=8}, vocations = {1, 5}, basin = {x=32679, y=32089, z=8}, item = 2175, arrive = {x=32671, y=32069, z=8}},
	{pos = {x=32669, y=32089, z=8}, vocations = {2, 6}, basin = {x=32667, y=32089, z=8}, item = 2674, arrive = {x=32672, y=32069, z=8}},
	{pos = {x=32673, y=32085, z=8}, vocations = {3, 7}, basin = {x=32673, y=32083, z=8}, item = 2455, arrive = {x=32671, y=32070, z=8}},
	{pos = {x=32673, y=32093, z=8}, vocations = {4, 8}, basin = {x=32673, y=32094, z=8}, item = 2376, arrive = {x=32672, y=32070, z=8}},
}
local LEVEL = 20

function onUse(cid, item, frompos, item2, topos)
	local players, sacrifices = {}, {}
	for i, switch in ipairs(SWITCHES) do
		local thing = getThingfromPos({x=switch.pos.x, y=switch.pos.y, z=switch.pos.z, stackpos=253})
		local vocation = thing.uid > 0 and isPlayer(thing.uid) and getPlayerVocation(thing.uid) or 0
		local sacrifice = getTileItemById(switch.basin, switch.item)
		if (vocation ~= switch.vocations[1] and vocation ~= switch.vocations[2]) or getPlayerLevel(thing.uid) < LEVEL
				or sacrifice.uid == 0 then
			doPlayerSendCancel(cid, "Sorry, not possible.")
			return true
		end
		players[i], sacrifices[i] = thing.uid, sacrifice.uid
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	for i, switch in ipairs(SWITCHES) do
		doRemoveItem(sacrifices[i], 1)
		doSendMagicEffect(switch.pos, CONST_ME_TELEPORT)
		doTeleportThing(players[i], switch.arrive)
		doSendMagicEffect(switch.arrive, CONST_ME_TELEPORT)
	end
	return true
end

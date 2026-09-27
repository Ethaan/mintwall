-- The Desert Dungeon Quest (docs/reference-74/quests.md). TibiaWiki 2006: four players, one of each vocation, each puts
-- a sacrifice on the basin behind his floor switch and stands on it - "A switch only goes down if the right vocation
-- with the right item stands on it" (paladin a crossbow, north; druid an apple, west; sorcerer a spellbook, east; knight
-- a sword, south); the paladin pulls the lever (actions/scripts/quests/desert_dungeon.lua). Positions: our map and
-- tibiaot74's "desert quest.lua".
DESERT_SWITCHES = {
	["32677,32089"] = {vocations = {1, 5}, basin = {x=32679, y=32089, z=8}, item = 2175, arrive = {x=32671, y=32069, z=8}},
	["32669,32089"] = {vocations = {2, 6}, basin = {x=32667, y=32089, z=8}, item = 2674, arrive = {x=32672, y=32069, z=8}},
	["32673,32085"] = {vocations = {3, 7}, basin = {x=32673, y=32083, z=8}, item = 2455, arrive = {x=32671, y=32070, z=8}},
	["32673,32093"] = {vocations = {4, 8}, basin = {x=32673, y=32094, z=8}, item = 2376, arrive = {x=32672, y=32070, z=8}},
}
local UP, DOWN = 426, 425

function desertSwitchHolds(cid, switch)
	if not isPlayer(cid) then
		return false
	end
	local vocation = getPlayerVocation(cid)
	if vocation ~= switch.vocations[1] and vocation ~= switch.vocations[2] then
		return false
	end
	return getTileItemById(switch.basin, switch.item).uid > 0
end

function onStepIn(cid, item, topos, frompos)
	local switch = DESERT_SWITCHES[topos.x .. "," .. topos.y]
	if switch ~= nil and item.itemid == UP and desertSwitchHolds(cid, switch) then
		doTransformItem(item.uid, DOWN)
	end
	return true
end

function onStepOut(cid, item, topos, frompos)
	if item.itemid == DOWN then
		doTransformItem(item.uid, UP)
	end
	return true
end

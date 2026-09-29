-- The Ancient Tombs Quest, Vashresamun's tomb (Ancient Ruins Tomb; docs/reference-74/quests.md). TibiaWiki 2006:
-- "When you go trough it [the level-75 gate], there are many musical instruments. You have to play them in right
-- order to get trough the next door. [...] Play the instruments in the order showed by the gp. After this you are
-- able to go through the next door." The order in the wiki's picture (2007) is the same as tibiaot74's
-- (actions/scripts/hota/instrumento.lua): the drum, the panpipes, the lute, the lyre, the cornucopia.
--
-- 51122, the eight instruments on the altar stones (33188-33191,32660/32669,15; unique ids 51130-51137 keep them in
--   place): each player plays his own sequence (storage 51122 counts the right ones); a wrong one starts it over.
-- 51123, the door behind (33184,32665,15, a plain door on our map, a quest door on tibiaot74's): opens for a player
--   who has played the five in order - once; closed again it needs the tune again.
local ORDER = {2367, 2373, 2370, 2372, 2369}     -- drum, panpipes, lute, lyre, cornucopia
local PLAYED = 51122                              -- storage: how many of ORDER this player has played in a row
local DOOR_CLOSED, DOOR_OPEN = 1232, 1233

function onUse(cid, item, frompos, item2, topos)
	if item.actionid == 51122 then
		local played = math.max(getPlayerStorageValue(cid, PLAYED), 0)
		if played < #ORDER and ORDER[played + 1] == item.itemid then
			setPlayerStorageValue(cid, PLAYED, played + 1)
		elseif ORDER[1] == item.itemid then
			setPlayerStorageValue(cid, PLAYED, 1)
		else
			setPlayerStorageValue(cid, PLAYED, 0)
		end
		doSendMagicEffect(frompos, CONST_ME_SOUND_BLUE)
	elseif item.actionid == 51123 and item.itemid == DOOR_CLOSED then
		if getPlayerStorageValue(cid, PLAYED) ~= #ORDER then
			doPlayerSendCancel(cid, "It is locked.")
			return true
		end
		setPlayerStorageValue(cid, PLAYED, 0)
		doTransformItem(item.uid, DOOR_OPEN)
	elseif item.actionid == 51123 then
		-- as doors/door_open_horizontal.lua: whatever stands in the doorway goes aside
		doRelocate(frompos, {x=frompos.x + 1, y=frompos.y, z=frompos.z})
		if isValidUID(item.uid) then
			doTransformItem(item.uid, DOOR_CLOSED)
		end
	end
	return true
end

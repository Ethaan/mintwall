-- The Ancient Tombs Quest, Morguthis's tomb (Tarpit Tomb; docs/reference-74/quests.md).
-- 51128, the two paintings 33212,32693,13 (outside) and 33209,32701,13 (inside): they take away / put back the wall
--   33211,32698,13 of the sealed room whose teleport leads on (tibiaot74's switch/scarabank.lua; decided with the user
--   2026-09-28).
local WALL, WALL_POS = 1061, {x=33211, y=32698, z=13}
local ASIDE = {x=33211, y=32699, z=13}

function onUse(cid, item, frompos, item2, topos)
	local wall = getTileItemById(WALL_POS, WALL)
	if wall.uid > 0 then
		doRemoveItem(wall.uid)
		doSendMagicEffect(WALL_POS, CONST_ME_POFF)
	else
		doRelocate(WALL_POS, ASIDE)
		doCreateItem(WALL, 1, WALL_POS)
	end
	return true
end

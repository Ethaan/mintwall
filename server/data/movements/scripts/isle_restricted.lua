-- The Isle of the Kings, the White Raven Monastery's restricted floor (docs/reference-74/quests.md, White Raven
-- Monastery Quest). TibiaWiki (Isle of the Kings): "The third floor, accessible through a locked door on the second
-- floor via Key 3350, holds the restricted area. This floor is only for the monks themselves and trespassing will be
-- severely punished. If you still enter you will need to sacrifice a variable amount of gold [...] take your money to
-- Costello and say crime or absolution. If you refuse to pay this amount, Dalbrect will not allow you aboard his ferry
-- to or from the isle." The only way up is the stairs behind the key-3350 door (32178,31928,6): the tile they put you
-- on (32180,31925,5, action id 51057) marks the trespasser - storage 99998, which Costello (npc/scripts/costello.lua)
-- clears for the fine and Captain Jack checks. Decided with the user 2026-09-25: done now.
local TRESPASSER = 99998

function onStepIn(cid, item, topos, frompos)
	if isPlayer(cid) and getPlayerStorageValue(cid, TRESPASSER) ~= 1 then
		setPlayerStorageValue(cid, TRESPASSER, 1)
	end
	return true
end

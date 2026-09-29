-- The Ancient Tombs Quest, Ashmunrah's tomb (Ankrahmun Library Tomb; docs/reference-74/quests.md). Current wiki: "To
-- enter the teleporter to the reward room, all the switches must be switched to the right for the teleporter to work.
-- This must be done for each member of your team once. Put all 7 pieces of the Helmet of the Ancients on the small
-- stone table to the north to get your reward." TibiaWiki 2006 (quests.md): the Full Helmet of the Ancients.
--
-- 51161, the forcefield in Ashmunrah's room (33179,32890,11): with the four switches right (33175,32884 / 33176,32880 /
--   33182,32880 / 33183,32884, on the altar stones - lost on our map, placed at tibiaot74's spots; the wiki's picture
--   has switches on altar stones) into the reward room (our map's destination), and the switches go back left for the
--   next one; otherwise back into the room (tibiaot74).
-- 51162, the stone table in the reward room (33198,32876,11): the seven pieces on it become the helmet of the ancients.
local LEFT, RIGHT = 1945, 1946
local SWITCHES = {{x=33175, y=32884, z=11}, {x=33176, y=32880, z=11}, {x=33182, y=32880, z=11}, {x=33183, y=32884, z=11}}
local REWARD_ROOM = {x=33198, y=32886, z=11}
local BACK = {x=33179, y=32889, z=11}
local PIECES = {2335, 2336, 2337, 2338, 2339, 2340, 2341}   -- ornament, gem holder, horns, damaged helmet, piece, adornment
local HELMET = 2342

function onStepIn(cid, item, topos, frompos)
	if not isPlayer(cid) then
		return true
	end
	for _, pos in ipairs(SWITCHES) do
		if getTileItemById(pos, RIGHT).uid == 0 then
			doTeleportThing(cid, BACK)
			doSendMagicEffect(BACK, CONST_ME_POFF)
			return true
		end
	end
	for _, pos in ipairs(SWITCHES) do
		doTransformItem(getTileItemById(pos, RIGHT).uid, LEFT)
	end
	doTeleportThing(cid, REWARD_ROOM)
	doSendMagicEffect(REWARD_ROOM, CONST_ME_ENERGYAREA)
	return true
end

local function assemble(pos)
	local found = {}
	for _, piece in ipairs(PIECES) do
		local thing = getTileItemById(pos, piece)
		if thing.uid == 0 then
			return
		end
		table.insert(found, thing.uid)
	end
	for _, uid in ipairs(found) do
		doRemoveItem(uid, 1)
	end
	doCreateItem(HELMET, 1, pos)
	doSendMagicEffect(pos, CONST_ME_MAGIC_RED)
end

function onAddItem(moveitem, tileitem, pos)
	-- not while the engine is still moving the piece
	addEvent(assemble, 0, pos)
	return true
end

-- The Djinn War (docs/reference-74/quests.md; npc/lib/djinn.lua): the fortresses' quest objects. Neither was on our
-- map (no ids) nor scripted.
--
-- 51170, the water basin on Ashta'daramai's 4th floor (33109-33110,32529,3 - its northern half): TibiaWiki 2006 "use
--   the northern of the two fountains. The Tear appears"; current wiki "There will be ripples in the water, and a Tear
--   of Daraman will appear on the floor beneath you". Our map (and the original) has one 2x2 basin there: its northern
--   tiles give it (decided with the user 2026-09-29) - to a player on Alesar's mission who has none (tibiaot74: its
--   NW tile, uid 8133).
-- 51171, the gemmed lamps by Gabel's bed (33094,32524,1, Ashta'daramai) and Malor's (33048,32630,1, Mal'ouquah):
--   current wiki: '"use" the gemmed lamp that is on his counter, while carrying Fa'hradin's Gemmed Lamp' - Malor's
--   followers at Gabel's, Gabel's at Malor's; the sleeping lamp is exchanged for Fa'hradin's (the player's is gone,
--   the bedside lamp looks the same). Using Fa'hradin's lamp on it works too.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local GABELS_LAMP = {x=33094, y=32524, z=1}
local MALORS_LAMP = {x=33048, y=32630, z=1}

local function samePos(a, b)
	return a.x == b.x and a.y == b.y and a.z == b.z
end

local function tear(cid, pos)
	if djinnProgress(cid, DJINN_EFREET) ~= EFREET_TEAR or djinnCarries(cid, TEAR_OF_DARAMAN) then
		return false
	end
	doSendMagicEffect(pos, CONST_ME_LOSEENERGY)
	local here = getPlayerPosition(cid)
	doCreateItem(TEAR_OF_DARAMAN, 1, here)
	doSendMagicEffect(here, CONST_ME_MAGIC_BLUE)
	return true
end

local function exchangeLamp(cid, pos)
	local side, step, placed
	if samePos(pos, GABELS_LAMP) then
		side, step, placed = DJINN_EFREET, EFREET_LAMP, EFREET_LAMP_PLACED
	elseif samePos(pos, MALORS_LAMP) then
		side, step, placed = DJINN_MARID, MARID_LAMP, MARID_LAMP_PLACED
	else
		return false
	end
	if djinnProgress(cid, side) ~= step or not doPlayerRemoveItem(cid, FAHRADINS_LAMP, 1) then
		return false
	end
	setPlayerStorageValue(cid, side, placed)
	doSendMagicEffect(pos, CONST_ME_MAGIC_RED)
	return true
end

function onUse(cid, item, frompos, item2, topos)
	if item.itemid == FAHRADINS_LAMP then          -- Fa'hradin's lamp used on the bedside lamp
		if item2 == nil or item2.actionid ~= 51171 then
			return false
		end
		return exchangeLamp(cid, topos)
	elseif item.actionid == 51170 then
		return tear(cid, frompos)
	elseif item.actionid == 51171 then
		return exchangeLamp(cid, frompos)
	end
	return false
end

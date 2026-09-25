-- Demon Helmet Quest (docs/reference-74/quests.md), the quest room at the bottom of the Edron Hero Cave. TibiaWiki
-- (pre-8.0 spoiler, oldid 57772): "there is a switch on the east side of the room that must be pulled to activate
-- the portal to get out [...] The boxes containing the rewards are on the west side of the room." On our map (and
-- tibiaot74's) the boxes stand in an alcove closed by an immovable stone (1355 at 33314,31592,15). The switch
-- (action id 50666 at 33330,31591,15) takes the stone away and opens the exit portal (33316,31591,15 -> 33328,31592,14);
-- pulled back, both close again. Positions and items as tibiaot74's "switch/dhq.lua".
local STONE_POS = {x=33314, y=31592, z=15}
local STONE = 1355
local ASIDE = {x=33315, y=31592, z=15}     -- whoever stands in the gap when it closes
local PORTAL_POS = {x=33316, y=31591, z=15}
local PORTAL_TO = {x=33328, y=31592, z=14}
local FIELD = 1387

function onUse(cid, item, frompos, item2, topos)
	if item.itemid == 1945 then
		local stone = getTileItemById(STONE_POS, STONE)
		if stone.uid > 0 then
			doRemoveItem(stone.uid)
		end
		if getTileItemById(PORTAL_POS, FIELD).uid == 0 then
			doCreateTeleport(FIELD, PORTAL_TO, PORTAL_POS)
		end
	else
		local portal = getTileItemById(PORTAL_POS, FIELD)
		if portal.uid > 0 then
			doRemoveItem(portal.uid)
		end
		if getTileItemById(STONE_POS, STONE).uid == 0 then
			doRelocate(STONE_POS, ASIDE)
			doCreateItem(STONE, 1, STONE_POS)
		end
	end
	doTransformItem(item.uid, item.itemid == 1945 and 1946 or 1945)
	return true
end

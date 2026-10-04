-- Behemoth Quest (docs/reference-74/quests.md). TibiaWiki pre-8.0: "You'll have to move some stones in order to reach
-- the quest room. Go to the southeastern corner of this multi-level cavern [...] and go up a level. [...] a small
-- circular room with Fire Field in the border. Use Destroy Field on one of these fields to discover a lever. Push the
-- lever"; current wiki: "You may have to move corpses to find the lever. When the lever is to the right, backtrack to
-- the rocks". The lever (action id 51021 at 33290,31715,12, the map's own, under a fire field and a dead orc; a second
-- one we had placed at tibiaot74's spot 33293,31718 was removed 2026-10-03 - the user found it, a decoy) takes away the five stones across the Behemoth floor's passage north
-- (33295-33299,31677,15) and puts them back when pulled again - positions and stone as tibiaot74's
-- "edron-behemoth quest open.lua".
local STONES = {{x=33295, y=31677, z=15}, {x=33296, y=31677, z=15}, {x=33297, y=31677, z=15},
                {x=33298, y=31677, z=15}, {x=33299, y=31677, z=15}}
local STONE = 1304

function onUse(cid, item, frompos, item2, topos)
	if item.itemid == 1945 then
		for _, pos in ipairs(STONES) do
			local stone = getTileItemById(pos, STONE)
			if stone.uid > 0 then
				doRemoveItem(stone.uid)
			end
		end
		doTransformItem(item.uid, 1946)
	else
		for _, pos in ipairs(STONES) do
			if getTileItemById(pos, STONE).uid == 0 then
				doRelocate(pos, {x=pos.x, y=pos.y + 1, z=pos.z})   -- whoever stands there steps south
				doCreateItem(STONE, 1, pos)
			end
		end
		doTransformItem(item.uid, 1945)
	end
	return true
end

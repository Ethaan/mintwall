-- The Ancient Tombs Quest, Dipthrah's tomb (Mountain Tomb; docs/reference-74/quests.md). Current wiki: "Go through the
-- doors listed below: endless, pale-faced, deceased, unholy, doomed, righteous, sharpened, mortal. Note: this sequence
-- is found in a book" - the poem "In ancient tombs beneath the burning endless sands ..." (Ankrahmun Tombs (Book));
-- a monument by the first row (33078,32638,15) has it scratched out. Eight rows of three doors (x 33070/33073/33076,
-- y 32637 up to 32609, z 15), a sign east of each names it; on our map all three open into the next chamber.
--
-- 51126, the sixteen wrong doors: stepping into one sends you back to the gauntlet's first room (decided with the user
--   2026-09-28; no source says what a wrong door does).
local START = {x=33072, y=32640, z=15}

function onStepIn(cid, item, topos, frompos)
	if isPlayer(cid) then
		doTeleportThing(cid, START)
		doSendMagicEffect(START, CONST_ME_ENERGYAREA)
	end
	return true
end

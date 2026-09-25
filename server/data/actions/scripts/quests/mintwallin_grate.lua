-- The grate in Mintwallin (32482,32170,14, action id 51019): shut - it opens only while someone stands on the switch
-- tile far away (movements/scripts/mintwallin_grate_switch.lua; Devil Helmet Quest, two players). Other sewer grates
-- are used to climb down (teleport.lua); this one does not open by hand.
function onUse(cid, item, frompos, item2, topos)
	doPlayerSendCancel(cid, "Sorry, not possible.")
	return true
end

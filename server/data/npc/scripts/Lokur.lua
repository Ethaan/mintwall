-- Lokur Stampsmasher, the Kazordoon post officer (TibiaWiki 2006: "Postman" - parcels and letters; his words and shop
-- are in his NPC file). The bank (deposit, withdraw, transfer, balance, changing coins, PINs) came with the 2007 bank
-- update, not 7.4 - removed (decided with the user 2026-10-01). Mission 7 of the Postman Missions: he sends you to his
-- armorer Kroox for his measurements (npc/lib/postman.lua).
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

questNpc{
	quest = function(cid, msg, state, say)
		if containsWord(msg, "measurements") and postmanProgress(cid) == POSTMAN_MEASUREMENTS
				and not postmanHas(cid, POSTMAN_MEASURES, POSTMAN_OFFICERS.lokur) then
			say(cid, "Come on, I have no clue what they are. Better ask my armorer Kroox for such nonsense. Go and ask him for good ol' Lokurs measurements, he'll know.")
			postmanSet(cid, POSTMAN_MEASURES, POSTMAN_OFFICERS.lokur_asked)
			return true
		end
		return false
	end,
}

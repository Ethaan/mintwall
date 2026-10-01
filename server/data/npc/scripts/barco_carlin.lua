-- Captain Greyhound, the Carlin harbour (docs/reference-74/travel.md; npc/lib/captain.lua). TibiaWiki
-- 2005-11-05: "any seaside town" - the prices the other captains charge for Carlin.
dofile(getDataDir() .. 'npc/lib/captain.lua')

captainNpc{
	routes = {
		{town = "Ab'Dendriel", cost = 80, words = {"ab'dendriel", "abdendriel"}},
		{town = "Edron", cost = 110},
		{town = "Thais", cost = 110},
		{town = "Venore", cost = 130},
	},
}

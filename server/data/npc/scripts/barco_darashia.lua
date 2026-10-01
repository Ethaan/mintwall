-- Petros, the Darashia harbour (docs/reference-74/travel.md; npc/lib/captain.lua). TibiaWiki 2005-11-30:
-- "Ankrahmun 100 gp, Venore 60 gp" (and Port Hope, 7.5). The old script also sailed to Port Hope.
dofile(getDataDir() .. 'npc/lib/captain.lua')

captainNpc{
	routes = {
		{town = "Ankrahmun", cost = 100},
		{town = "Venore", cost = 60},
	},
}

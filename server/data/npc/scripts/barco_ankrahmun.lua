-- Captain Sinbeard, the Ankrahmun harbour (docs/reference-74/travel.md; npc/lib/captain.lua). TibiaWiki
-- 2005-07-28: "Darashia 100 gp, Venore 150 gp, Edron 160 gp ... he does not travel to Ab'Dendriel, Carlin, or
-- Thais". The old script also sailed to Port Hope (7.5).
dofile(getDataDir() .. 'npc/lib/captain.lua')

captainNpc{
	routes = {
		{town = "Darashia", cost = 100},
		{town = "Edron", cost = 160},
		{town = "Venore", cost = 150},
	},
}

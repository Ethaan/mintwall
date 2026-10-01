-- Captain Seagull, the Ab'Dendriel harbour (docs/reference-74/travel.md; npc/lib/captain.lua). TibiaWiki
-- 2005-11-30: "Carlin 80, Edron 70, Thais 130, Venore 90".
dofile(getDataDir() .. 'npc/lib/captain.lua')

captainNpc{
	routes = {
		{town = "Carlin", cost = 80},
		{town = "Edron", cost = 70},
		{town = "Thais", cost = 130},
		{town = "Venore", cost = 90},
	},
}

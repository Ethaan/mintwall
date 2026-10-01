-- Captain Seahorse, the Edron harbour (docs/reference-74/travel.md; npc/lib/captain.lua). TibiaWiki 2005-12-01:
-- "Ab'Dendriel 70, Ankrahmun 160, Carlin 110, Thais 160, Venore 40" (and Port Hope, 7.5); Cormaya 20 gp as before
-- (the wiki leaves it out, Pemaret sails back). The old script took nothing for Carlin.
dofile(getDataDir() .. 'npc/lib/captain.lua')

captainNpc{
	routes = {
		{town = "Ab'Dendriel", cost = 70, words = {"ab'dendriel", "abdendriel"}},
		{town = "Ankrahmun", cost = 160},
		{town = "Carlin", cost = 110},
		{town = "Cormaya", cost = 20},
		{town = "Thais", cost = 160},
		{town = "Venore", cost = 40},
	},
}

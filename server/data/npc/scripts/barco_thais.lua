-- Captain Bluebear, the Thais harbour (docs/reference-74/travel.md; npc/lib/captain.lua). TibiaWiki 2005-11-30:
-- "Ab'Dendriel 130, Carlin 110, Edron 150, Venore 170". The old script also sailed to Port Hope (7.5) and Svargrond
-- (8.0) and charged 110 for Edron.
dofile(getDataDir() .. 'npc/lib/captain.lua')

captainNpc{
	routes = {
		{town = "Ab'Dendriel", cost = 130, words = {"ab'dendriel", "abdendriel"}},
		{town = "Carlin", cost = 110},
		{town = "Edron", cost = 150},
		{town = "Venore", cost = 170},
	},
}

-- Captain Fearless, the Venore harbour (docs/reference-74/travel.md; npc/lib/captain.lua). TibiaWiki 2005-11-30:
-- "Ab'Dendriel 90, Carlin 130, Edron 40, Darashia 60 ... Beware the Ghost Ship!, Thais 170"; Ankrahmun 150 as before
-- (Captain Sinbeard's "Venore 150" the other way). The old script also sailed to Port Hope (7.5).
--
-- The Ghost Ship (Plate Armor Quest): "When travelling with Captain Fearless from Venore to Darashia you may be randomly
-- hijacked [...] before you reach Darashia" (TibiaWiki 2005) - one trip in ten (decided with the user 2026-09-26), onto
-- the deck by the steering wheel (33319,32172,6); the ship's forcefield then takes you on to Darashia.
dofile(getDataDir() .. 'npc/lib/captain.lua')

local GHOST_SHIP = {x=33319, y=32172, z=6}
local GHOST_SHIP_CHANCE = 10

captainNpc{
	routes = {
		{town = "Ab'Dendriel", cost = 90, words = {"ab'dendriel", "abdendriel"}},
		{town = "Ankrahmun", cost = 150},
		{town = "Carlin", cost = 130},
		{town = "Darashia", cost = 60, divert = function()
			if math.random(1, GHOST_SHIP_CHANCE) == 1 then
				return GHOST_SHIP
			end
			return nil
		end},
		{town = "Edron", cost = 40},
		{town = "Thais", cost = 170},
	},
}

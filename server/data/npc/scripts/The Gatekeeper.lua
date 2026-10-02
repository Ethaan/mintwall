-- The Gatekeeper (Rookgaard, the premium side, west of King's Bridge): level 8 picks Ab'Dendriel, Ankrahmun, Darashia
-- or Kazordoon and a vocation (npc/lib/oracle.lua). Only premium players cross King's Bridge to him.
dofile(getDataDir() .. 'npc/lib/questnpc.lua')
dofile(getDataDir() .. 'npc/lib/oracle.lua')

oracleNpc{
	towns = {"Ab'Dendriel", "Ankrahmun", "Darashia", "Kazordoon"},
	minLevel = 8,
	greeting = "Hello |PLAYERNAME|. Are you prepared to face your destiny?",
	tooYoung = "CHILD! COME BACK WHEN YOU HAVE GROWN UP!",
	farewell = "Then come back when you are ready.",
	text = {
		town = function(list) return "What city do you wish to live in? " .. list .. "?" end,
		chosen = function(town)
			return town .. " will be your home-town! So what vocation do you wish to become? Sorcerer, druid, paladin or knight?"
		end,
		vocation = {"So, you wish to be a powerful magician? Are you sure about that? This decision is irreversible!",
			"A mighty druid! Are you sure? This decision is irreversible!",
			"A nimble paladin! Are you sure? This decision is irreversible!",
			"A valorous knight! Are you sure? This decision is irreversible!"},
		vocations = "Sorcerer, druid, paladin or knight?",
		again = "Then what vocation do you want to become?",
		done = "So be it!",
	},
}

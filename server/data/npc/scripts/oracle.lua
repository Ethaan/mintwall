-- The Oracle (Rookgaard, the free side): level 8 or 9 picks Carlin, Thais or Venore and a vocation (npc/lib/oracle.lua).
dofile(getDataDir() .. 'npc/lib/questnpc.lua')
dofile(getDataDir() .. 'npc/lib/oracle.lua')

oracleNpc{
	caps = true,
	towns = {"Carlin", "Thais", "Venore"},
	minLevel = 8,
	maxLevel = 9,
	greeting = "|PLAYERNAME|, ARE YOU PREPARED TO FACE YOUR DESTINY?",
	tooYoung = "CHILD! COME BACK WHEN YOU HAVE GROWN UP!",
	tooOld = "|PLAYERNAME|, I CAN'T LET YOU LEAVE - YOU ARE TOO STRONG ALREADY! YOU CAN ONLY LEAVE WITH LEVEL 9 OR LOWER.",
	farewell = "COME BACK WHEN YOU ARE PREPARED TO FACE YOUR DESTINY!",
	text = {
		town = function(list) return "IN WHICH TOWN DO YOU WANT TO LIVE: " .. list .. "?" end,
		chosen = function(town)
			return "IN " .. town .. "! AND WHAT PROFESSION HAVE YOU CHOSEN: KNIGHT, PALADIN, SORCERER, OR DRUID?"
		end,
		vocation = {"A SORCERER! ARE YOU SURE? THIS DECISION IS IRREVERSIBLE!",
			"A DRUID! ARE YOU SURE? THIS DECISION IS IRREVERSIBLE!",
			"A PALADIN! ARE YOU SURE? THIS DECISION IS IRREVERSIBLE!",
			"A KNIGHT! ARE YOU SURE? THIS DECISION IS IRREVERSIBLE!"},
		vocations = "KNIGHT, PALADIN, SORCERER, OR DRUID?",
		done = "SO BE IT!",
	},
}

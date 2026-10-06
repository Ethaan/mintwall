-- The Orc King in Ulderek's Rock, behind the level-40 gate (The Djinn War, both sides; docs/reference-74/quests.md;
-- npc/lib/djinn.lua). TibiaWiki 2006 transcripts: "hi" "Arrrrgh! A dirty paleskin! To me my children! Kill them my
-- guards!" (the first time only: "The first time you say 'hi' to the Orc King, he will spawn a lot of Orc Warlords and
-- Orc Berserkers"); "hi" "Harrrrk! You think you are strong now? ..."; "lamp" "I can sense your evil intentions to
-- imprison a djinn! ... Who do you want to trap in this cursed lamp?"; "malor" "I was waiting for this day! Take the
-- lamp and let Malor feel my wrath!" - on both sides (Malor or Gabel sent the player for Fa'hradin's lamp). The guards
-- and the other lines are the old script's.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local TALK = {
	{"good djinn", "I will not share anything more about that topic with you paleskins."},
	{"underling", "The orcish horde of this hive is under my control. I sense their emotions and their needs and provide them with the leadership they need to focus their hate and rage."},
	{"direction", "To conquer, to destroy and to dominate. Orcs are born to rule the world."},
	{"deathwish", "His ancient fortress on Darama was deserted as the evil Djinn fled this world after his imprisonment. Now the time has come for the evil Djinns to return to their master although this will certainly awaken the good Djinn too."},
	{"abandoned", "His ancient fortress on Darama was deserted as the evil Djinn fled this world after his imprisonment. Now the time has come for the evil Djinns to return to their master although this will certainly awaken the good Djinn too."},
	{"paleskins", "You are as ugly as maggots, although not quite as as tasty."},
	{"minion", "The orcish horde of this hive is under my control. I sense their emotions and their needs and provide them with the leadership they need to focus their hate and rage."},
	{"divine", "The orcs are the bearers of Blogs rage. This makes us the ultimate fighters and the most powerful of all races."},
	{"awaken", "I will not share anything more about that topic with you paleskins."},
	{"horde", "The orcish horde of this hive is under my control. I sense their emotions and their needs and provide them with the leadership they need to focus their hate and rage."},
	{"focus", "To conquer, to destroy and to dominate. Orcs are born to rule the world."},
	{"slime", "Pah! Don't mock me, mortal! This shape is a curse which the evil djinn bestowed upon me!"},
	{"cheat", "Because I freed him he granted me three wishes. He was true to his word in the first two wishes."},
	{"third", "I wished to father more healthy and fertile children as any orc has ever done. But the djinn cheated me and made me a slime! Then he laughed at me and left for his abandoned fortress in the Deathwish Mountains."},
	{"hive", "I can sense the presence and the feelings of my underlings and minions. I embrace the rage of the horde."},
	{"hate", "Hate and rage are the true blessings of Blog, since they are powerful weapons. They give the hive strength. I provide them with direction and focus."},
	{"rage", "Hate and rage are the true blessings of Blog, since they are powerful weapons. They give the hive strength. I provide them with direction and focus."},
	{"blog", "The Raging One blessed us with his burning hate. We are truly his children and therefore divine."},
	{"wish", "He built this fortress over Uldrek's grave within a single night. Also, he granted me my second wish and gave me immortality. Test it and try to kill me if you want. Har Har!"},
	{"orc", "The orcs are the bearers of Blogs rage. This makes us the ultimate fighters and the most powerful of all races."},
}

local GUARDS = {{"Orc Leader", -1, 0}, {"Slime", 1, 0}, {"Orc Warlord", 0, 1}, {"Orc Warlord", 0, -1},
	{"Orc Leader", 1, 1}, {"Slime", -1, -1}, {"Slime", 1, -1}, {"Orc Leader", -1, 1}}

local function wantsTheLamp(cid)
	return (djinnProgress(cid, DJINN_EFREET) == EFREET_LAMP or djinnProgress(cid, DJINN_MARID) == MARID_LAMP)
		and not djinnCarries(cid, FAHRADINS_LAMP)
end

djinnNpc{
	farewell = "We will meet again.",
	walkaway = "Yes, flee this place, but you will never escape my revenge!",
	busy = "Harrrrk!",
	greet = function(cid, say)
		if getPlayerStorageValue(cid, DJINN_ORC_GUARDS) ~= 1 then
			setPlayerStorageValue(cid, DJINN_ORC_GUARDS, 1)
			say(cid, "Arrrrgh! A dirty paleskin! To me my children! Kill them my guards!", true)
			local pos = getCreaturePosition(getNpcCid())
			for _, guard in ipairs(GUARDS) do
				local at = {x = pos.x + guard[2], y = pos.y + guard[3], z = pos.z}
				-- only on a free, walkable tile (getTopCreature: the guards another player's "hi" called may still
				-- stand there) - the king wanders (radius 3), so a tile beside him can be a wall, and summoning onto
				-- one made placeCreature fail ("Can not summon monster"). Without extendedPos it matches Markwin.lua.
				if getTopCreature(at).uid == 0 and queryTileAddThing(getNpcCid(), at) == RETURNVALUE_NOERROR then
					doSummonCreature(guard[1], at)
				end
			end
			return nil
		end
		return "Harrrrk! You think you are strong now? You shall never escape my wrath! I am immortal!"
	end,
	quest = function(cid, msg, state, say)
		if state.topic == 1 then
			state.topic = 0
			if containsWord(msg, "malor") and wantsTheLamp(cid) then
				doPlayerAddItem(cid, FAHRADINS_LAMP, 1)
				say(cid, "I was waiting for this day! Take the lamp and let Malor feel my wrath!")
			else
				say(cid, "I don't know your enemy, paleskin! Begone!")
			end
			return true
		elseif containsWord(msg, "lamp") and wantsTheLamp(cid) then
			state.topic = 1
			say(cid, {"I can sense your evil intentions to imprison a djinn! You are longing for the lamp, which I still possess. ...",
				"Who do you want to trap in this cursed lamp?"})
			return true
		elseif containsWord(msg, "malor") or containsWord(msg, "djinn") then
			state.topic = 0
			say(cid, "This cursed djinn king! I set him free from an enchanted lamp, and he cheated me!")
			return true
		end
		return false
	end,
	talk = TALK,
}

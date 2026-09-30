-- Alesar, the Efreet's smith in Mal'ouquah (The Djinn War - Efreet Faction, docs/reference-74/quests.md;
-- npc/lib/djinn.lua). TibiaWiki 2006 transcripts: DJANNI'HAH "What do you want from me, player?"; "mission" "So
-- Baa'leal thinks you are up to do a mission for us? ... Are you prepared to embark on a dangerous mission for us?";
-- "yes" the Tear of Daraman; back: "mission" "Did you find the tear of Daraman?"; "yes" "So you have made it? ...
-- talk to Malor"; "bye" "Finally.". He trades only with those Malor gave permission (TibiaWiki 2006: "He does not like
-- humans, but will tolerate those who help fight for his green djinn brethren"; decided with the user 2026-09-29).
-- The refusals are ours (no source).
dofile(getDataDir() .. 'npc/lib/djinn.lua')

djinnNpc{
	word = "djanni'hah",
	farewell = "Finally.",
	walkaway = "Finally.",
	busy = "I am already talking to one of you creeps. So shut up until it is your turn, |PLAYERNAME|.",
	greet = function(cid)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			return nil
		end
		return "What do you want from me, |PLAYERNAME|?"
	end,
	quest = function(cid, msg, state, say)
		if djinnFollower(cid) ~= DJINN_EFREET then
			return false
		end
		local progress = djinnProgress(cid, DJINN_EFREET)
		if state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			setPlayerStorageValue(cid, DJINN_EFREET, EFREET_TEAR)
			say(cid, {"All right then, human. Have you ever heard of the 'Tears of Daraman'? ...",
				"They are precious gemstones made of some unknown blue mineral and possess enormous magical power. ...",
				"If you want to learn more about these gemstones don't forget to visit our library. ...",
				"Anyway, one of them is enough to create thousands of our mighty djinn blades. ...",
				"Unfortunately my last gemstone broke and therefore I'm not able to create new blades anymore. ...",
				"To my knowledge there is only one place where you can find these gemstones - I know for a fact that the Marid have at least one of them. ...",
				"Well... to cut a long story short, your mission is to sneak into Ashta'daramai and to steal it. ...",
				"Needless to say, the Marid won't be too eager to part with it. Try not to get killed until you have delivered the stone to me."})
			return true
		elseif state.topic == 2 and containsWord(msg, "yes") then
			state.topic = 0
			if doPlayerRemoveItem(cid, TEAR_OF_DARAMAN, 1) then
				setPlayerStorageValue(cid, DJINN_EFREET, EFREET_TEAR_GIVEN)
				say(cid, {"So you have made it? You have really managed to steal a Tear of Daraman? ...",
					"Amazing how you humans are just impossible to get rid of. Incidentally, you have this character trait in common with many insects and with other vermin. ...",
					"Nevermind. I hate to say it, but it you have done us a favour, human. That gemstone will serve us well. ...",
					"Baa'leal, wants you to talk to Malor concerning some new mission. ...",
					"Looks like you have managed to extended your life expectancy - for just a bit longer."})
			else
				say(cid, "You do not have it, human. Don't waste my time.")
			end
			return true
		elseif state.topic ~= 0 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Don't waste my time, human.")
			return true
		elseif containsWord(msg, "mission") or containsWord(msg, "tear") then
			state.topic = 0
			if progress == EFREET_PAID then
				state.topic = 1
				say(cid, {"So Baa'leal thinks you are up to do a mission for us? ...",
					"I think he is getting old, entrusting human scum such as you are with an important mission like that. ...",
					"Personally, I don't understand why you haven't been slaughtered right at the gates. ...",
					"Anyway. Are you prepared to embark on a dangerous mission for us?"})
			elseif progress == EFREET_TEAR then
				state.topic = 2
				say(cid, "Did you find the tear of Daraman?")
			elseif progress > EFREET_TEAR then
				say(cid, "Baa'leal, wants you to talk to Malor concerning some new mission.")
			else
				return false
			end
			return true
		end
		return false
	end,
	mayTrade = function(cid)
		if djinnProgress(cid, DJINN_EFREET) >= EFREET_DONE then
			return true
		end
		selfSay("I don't trade with humans Malor has not given his permission.")
		return false
	end,
	shop = function(shopModule)
		shopModule:addSellableItem({'scimitar'}, 2419, 150, 'scimitar')
		shopModule:addSellableItem({'giant sword'}, 2393, 17000, 'giant sword')
		shopModule:addSellableItem({'serpent sword'}, 2409, 900, 'serpent sword')
		shopModule:addSellableItem({'poison dagger'}, 2411, 50, 'poison dagger')
		shopModule:addSellableItem({'knight axe'}, 2430, 2000, 'knight axe')
		shopModule:addSellableItem({'dragon hammer'}, 2434, 2000, 'dragon hammer')
		shopModule:addSellableItem({'skull staff'}, 2436, 6000, 'skull staff')
		shopModule:addSellableItem({'dark armor'}, 2489, 400, 'dark armor')
		shopModule:addSellableItem({'knight armor'}, 2476, 5000, 'knight armor')
		shopModule:addSellableItem({'dark helmet'}, 2490, 250, 'dark helmet')
		shopModule:addSellableItem({'warrior helmet'}, 2475, 5000, 'warrior helmet')
		shopModule:addSellableItem({'strange helmet'}, 2479, 500, 'strange helmet')
		shopModule:addSellableItem({'mystic turban'}, 2663, 150, 'mystic turban')
		shopModule:addSellableItem({'knight legs'}, 2477, 5000, 'knight legs')
		shopModule:addSellableItem({'tower shield'}, 2528, 8000, 'tower shield')
		shopModule:addSellableItem({'black shield'}, 2529, 800, 'black shield')
		shopModule:addSellableItem({'ancient shield'}, 2532, 900, 'ancient shield')
		shopModule:addSellableItem({'vampire shield'}, 2534, 15000, 'vampire shield')

		shopModule:addBuyableItem({'ice rapier'}, 2396, 5000, 'ice rapier')
		shopModule:addBuyableItem({'serpent sword'}, 2409, 6000, 'serpent sword')
		shopModule:addBuyableItem({'dark armor'}, 2489, 1500, 'dark armor')
		shopModule:addBuyableItem({'dark helmet'}, 2490, 1000, 'dark helmet')
		shopModule:addBuyableItem({'ancient shield'}, 2532, 5000, 'ancient shield')
	end,
}

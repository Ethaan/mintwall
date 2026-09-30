-- Yaman, a Efreet trader in Mal'ouquah (The Djinn War, docs/reference-74/quests.md; npc/lib/djinn.lua). A djinn:
-- greeted with DJANNI'HAH only (TibiaWiki 2006). He trades only with those who finished the
-- Efreet side - "will not trade with them until he has permission from Malor" (TibiaWiki 2006; decided with the user
-- 2026-09-29). Greeting and wares: the old script and NPC file; the refusal is ours (no source).
dofile(getDataDir() .. 'npc/lib/djinn.lua')

djinnNpc{
	word = "djanni'hah",
	greet = function(cid)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			return nil
		end
		return "What do you want from me, |PLAYERNAME|?"
	end,
	mayTrade = function(cid)
		if djinnProgress(cid, DJINN_EFREET) >= EFREET_DONE then
			return true
		end
		selfSay("I don't trade with humans Malor has not given his permission.")
		return false
	end,
	shop = function(shopModule)
		shopModule:addSellableItem({'might ring'}, 2164, 250, 'might ring')
		shopModule:addSellableItem({'energy ring'}, 2167, 100, 'energy ring')
		shopModule:addSellableItem({'life ring'}, 2168, 50, 'life ring')
		shopModule:addSellableItem({'time ring'}, 2169, 100, 'time ring')
		shopModule:addSellableItem({'dwarven ring'}, 2213, 100, 'dwarven ring')
		shopModule:addSellableItem({'ring of healing'}, 2214, 100, 'ring of healing')
		shopModule:addSellableItem({'strange talisman'}, 2161, 30, 'strange talisman')
		shopModule:addSellableItem({'silver amulet'}, 2170, 50, 'silver amulet')
		shopModule:addSellableItem({'protection amulet'}, 2200, 100, 'protection amulet')
		shopModule:addSellableItem({'dragon necklace'}, 2201, 100, 'dragon necklace')
		shopModule:addSellableItem({'snakebite rod'}, 2182, 100, 'snakebite rod')
		shopModule:addSellableItem({'moonlight rod'}, 2186, 200, 'moonlight rod')
		shopModule:addSellableItem({'volcanic rod'}, 2185, 1000, 'volcanic rod')
		shopModule:addSellableItem({'quagmire rod'}, 2181, 2000, 'quagmire rod')
		shopModule:addSellableItem({'tempest rod'}, 2183, 3000, 'tempest rod')
		shopModule:addSellableItem({'ankh'}, 2193, 100, 'ankh')
		shopModule:addSellableItem({'mysterious fetish'}, 2194, 50, 'mysterious fetish')
		shopModule:addBuyableItem({'might ring'}, 2164, 5000, 'might ring')
		shopModule:addBuyableItem({'energy ring'}, 2167, 2000, 'energy ring')
		shopModule:addBuyableItem({'life ring'}, 2168, 900, 'life ring')
		shopModule:addBuyableItem({'time ring'}, 2169, 2000, 'time ring')
		shopModule:addBuyableItem({'dwarven ring'}, 2213, 2000, 'dwarven ring')
		shopModule:addBuyableItem({'ring of healing'}, 2214, 2000, 'ring of healing')
		shopModule:addBuyableItem({'strange talisman'}, 2161, 100, 'strange talisman')
		shopModule:addBuyableItem({'silver amulet'}, 2170, 100, 'silver amulet')
		shopModule:addBuyableItem({'protection amulet'}, 2200, 700, 'protection amulet')
		shopModule:addBuyableItem({'dragon necklace'}, 2201, 1000, 'dragon necklace')
	end,
}

-- Haroun, a Marid trader in Ashta'daramai (The Djinn War, docs/reference-74/quests.md; npc/lib/djinn.lua). A djinn:
-- greeted with DJANNI'HAH only (TibiaWiki 2006). He trades only with those who finished the
-- Marid side - Gabel: "welcome to trade with Haroun and Nah'bob" once his mission is done (TibiaWiki 2006; decided
-- with the user 2026-09-29). Greeting and wares: the old script and NPC file; the refusal is ours (no source).
dofile(getDataDir() .. 'npc/lib/djinn.lua')

djinnNpc{
	word = "djanni'hah",
	greet = function(cid)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			return nil
		end
		return "Hello |PLAYERNAME|. I sell and buy different kinds of rings and also amulets."
	end,
	mayTrade = function(cid)
		if djinnProgress(cid, DJINN_MARID) >= MARID_DONE then
			return true
		end
		selfSay("I am sorry, I only trade with those Gabel trusts.")
		return false
	end,
	shop = function(shopModule)
		shopModule:addSellableItem({'sword ring'}, 2207, 500, 'sword ring')
		shopModule:addSellableItem({'club ring'}, 2209, 500, 'club ring')
		shopModule:addSellableItem({'axe ring'}, 2208, 500, 'axe ring')
		shopModule:addSellableItem({'power ring'}, 2166, 100, 'power ring')
		shopModule:addSellableItem({'stealth ring'}, 2165, 200, 'stealth ring')
		shopModule:addSellableItem({'stone skin amulet'}, 2197, 5000, 'stone skin amulet')
		shopModule:addSellableItem({'elven amulet'}, 2198, 500, 'elven amulet')
		shopModule:addSellableItem({'bronze amulet'}, 2172, 100, 'bronze amulet')
		shopModule:addSellableItem({'garlic necklace'}, 2199, 100, 'garlic necklace')
		shopModule:addSellableItem({'magic light wand'}, 2162, 35, 'magic light wand')
		shopModule:addSellableItem({'orb'}, 2176, 750, 'orb')
		shopModule:addSellableItem({'mind stone'}, 2178, 100, 'mind stone')
		shopModule:addSellableItem({'life crystal'}, 2177, 50, 'life crystal')
		shopModule:addBuyableItem({'sword ring'}, 2207, 500, 'sword ring')
		shopModule:addBuyableItem({'club ring'}, 2209, 500, 'club ring')
		shopModule:addBuyableItem({'axe ring'}, 2208, 500, 'axe ring')
		shopModule:addBuyableItem({'power ring'}, 2166, 100, 'power ring')
		shopModule:addBuyableItem({'stealth ring'}, 2165, 5000, 'stealth ring')
		shopModule:addBuyableItem({'stone skin amulet'}, 2197, 5000, 'stone skin amulet')
		shopModule:addBuyableItem({'elven amulet'}, 2198, 500, 'elven amulet')
		shopModule:addBuyableItem({'bronze amulet'}, 2172, 100, 'bronze amulet')
		shopModule:addBuyableItem({'garlic necklace'}, 2199, 100, 'garlic necklace')
	end,
}

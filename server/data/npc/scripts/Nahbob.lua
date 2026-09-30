-- Nah'bob, a Marid trader in Ashta'daramai (The Djinn War, docs/reference-74/quests.md; npc/lib/djinn.lua). A djinn:
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
		return "Sighs.. Another customer! I've only just sat down! What is it, |PLAYERNAME|?"
	end,
	mayTrade = function(cid)
		if djinnProgress(cid, DJINN_MARID) >= MARID_DONE then
			return true
		end
		selfSay("Sorry, old Bob only trades with those Gabel trusts.")
		return false
	end,
	shop = function(shopModule)
		shopModule:addSellableItem({'dragon lance'}, 2414, 9000, 'dragon lance')
		shopModule:addSellableItem({'fire axe'}, 2432, 8000, 'fire axe')
		shopModule:addSellableItem({'fire sword'}, 2392, 4000, 'fire sword')
		shopModule:addSellableItem({'war hammer'}, 2391, 1200, 'war hammer')
		shopModule:addSellableItem({'spike sword'}, 2383, 1000, 'spike sword')
		shopModule:addSellableItem({'ice rapier'}, 2396, 1000, 'ice rapier')
		shopModule:addSellableItem({'broad sword'}, 2413, 500, 'broad sword')
		shopModule:addSellableItem({'obsidian lance'}, 2425, 500, 'obsidian lance')
		shopModule:addSellableItem({'crown armor'}, 2487, 12000, 'crown armor')
		shopModule:addSellableItem({'blue robe'}, 2656, 10000, 'blue robe')
		shopModule:addSellableItem({'noble armor'}, 2486, 900, 'noble armor')
		shopModule:addSellableItem({'royal helmet'}, 2498, 30000, 'royal helmet')
		shopModule:addSellableItem({'crusader helmet'}, 2497, 6000, 'crusader helmet')
		shopModule:addSellableItem({'crown helmet'}, 2491, 2500, 'crown helmet')
		shopModule:addSellableItem({'crown legs'}, 2488, 12000, 'crown legs')
		shopModule:addSellableItem({'boots of haste'}, 2195, 30000, 'boots of haste')
		shopModule:addSellableItem({'phoenix shield'}, 2539, 16000, 'phoenix shield')
		shopModule:addSellableItem({'crown shield'}, 2519, 8000, 'crown shield')
		shopModule:addSellableItem({'dragon shield'}, 2516, 4000, 'dragon shield')
		shopModule:addSellableItem({'guardian shield'}, 2515, 2000, 'guardian shield')
		shopModule:addSellableItem({'beholder shield'}, 2518, 1200, 'beholder shield')
		shopModule:addBuyableItem({'war hammer'}, 2391, 10000, 'war hammer')
		shopModule:addBuyableItem({'spike sword'}, 2383, 8000, 'spike sword')
		shopModule:addBuyableItem({'noble armor'}, 2486, 8000, 'noble armor')
		shopModule:addBuyableItem({'beholder shield'}, 2518, 7000, 'beholder shield')
	end,
}

-- Spell teachers. Decided with the user 2026-10-01: every spell must be learned from an NPC, as in 7.4, and the
-- spells, their prices and magic levels and who teaches what to which vocation are Tibiantis' (a 7.4 server):
-- npc/lib/spells74.lua, made by tools/apply-tibiantis-spells.py. No character level - the magic level only. Eremo's
-- spells (Challenge, Power Bolt, Wild Growth, Enchant Staff) are for the promoted. The lines are the old Marvik
-- script's (the 7.x teachers': "Do you want to learn the spell '...' for ... gold?").
dofile(getDataDir() .. 'npc/lib/questnpc.lua')         -- questSay
dofile(getDataDir() .. 'npc/lib/spells74.lua')

local VOCATION_NAMES = {"sorcerers", "druids", "paladins", "knights"}

local function baseVocation(cid)
	local vocation = getPlayerVocation(cid)
	return vocation > 4 and vocation - 4 or vocation
end

local function only(vocations)
	local names = {}
	for i, v in ipairs(vocations) do
		names[i] = VOCATION_NAMES[v]
	end
	if #names == 1 then
		return names[1]
	end
	return table.concat(names, ", ", 1, #names - 1) .. " and " .. names[#names]
end

-- Adds the spells TEACHERS74[npcName] teaches to an NPC's keywords: "<spell>" -> "yes" learns it; "spells" lists them.
function teachSpells(keywordHandler, npcHandler, npcName)
	local teaches = TEACHERS74[npcName]
	if teaches == nil then
		error("no spells for " .. tostring(npcName) .. " in npc/lib/spells74.lua")
	end

	local function learn(cid, message, keywords, parameters, node)
		if not npcHandler:isFocused(cid) then
			return false
		end
		local name, spell = parameters.name, SPELLS74[parameters.name]
		if getPlayerLearnedInstantSpell(cid, string.lower(name)) then
			npcHandler:say("You already know how to cast this spell.", cid)
		elseif spell.promoted and getPlayerVocation(cid) <= 4 then
			npcHandler:say("Sorry, this spell is only for promoted " .. only(teaches[name]) .. ".", cid)
		elseif getPlayerMagLevel(cid) < spell.maglevel then
			npcHandler:say("You must have magic level " .. spell.maglevel .. " or better to learn this spell!", cid)
		elseif not doPlayerRemoveMoney(cid, spell.price) then
			npcHandler:say("Oh. You do not have enough money.", cid)
		else
			playerLearnInstantSpell(cid, string.lower(name))   -- the engine looks it up in lower case
			doSendMagicEffect(getPlayerPosition(cid), CONST_ME_MAGIC_BLUE)
			npcHandler:say("Here you are. Look in your spellbook for the pronunciation of this spell.", cid)
		end
		npcHandler:resetNpc(cid)
		return true
	end

	local function ask(cid, message, keywords, parameters, node)
		if not npcHandler:isFocused(cid) then
			return false
		end
		local name = parameters.name
		if not isInArray(teaches[name], baseVocation(cid)) then
			npcHandler:say("I am sorry but this spell is only for " .. only(teaches[name]) .. ".", cid)
			npcHandler:resetNpc(cid)
			return true
		end
		npcHandler:say("Do you want to learn the spell '" .. name .. "' for " .. SPELLS74[name].price .. " gold?", cid)
		return true
	end

	local function decline(cid, message, keywords, parameters, node)
		if not npcHandler:isFocused(cid) then
			return false
		end
		npcHandler:say("Maybe next time.", cid)
		npcHandler:resetNpc(cid)
		return true
	end

	for name in pairs(teaches) do
		for _, keyword in ipairs(SPELLS74[name].keywords) do
			local node = keywordHandler:addKeyword({keyword}, ask, {name = name})
			node:addChildKeyword({"yes"}, learn, {name = name})
			node:addChildKeyword({"no"}, decline, {})
		end
	end

	-- what he teaches the player's vocation, cheapest first
	local function list(cid)
		if not npcHandler:isFocused(cid) then
			return false
		end
		local names = {}
		for name, vocations in pairs(teaches) do
			if isInArray(vocations, baseVocation(cid)) then
				table.insert(names, name)
			end
		end
		if #names == 0 then
			npcHandler:say("Sorry, I have no spells for your vocation.", cid)
			return true
		end
		table.sort(names, function(a, b)
			local pa, pb = SPELLS74[a].price, SPELLS74[b].price
			return pa < pb or (pa == pb and a < b)
		end)
		local lines, line = {}, ""
		for _, name in ipairs(names) do
			local entry = "'" .. name .. "'"
			if string.len(line) + string.len(entry) > 200 then
				table.insert(lines, line .. " ...")
				line = ""
			end
			line = line .. (line == "" and "" or ", ") .. entry
		end
		table.insert(lines, line .. ".")
		lines[1] = "I teach " .. lines[1]
		questSay(npcHandler, cid, lines)
		return true
	end
	keywordHandler:addKeyword({"spells"}, list, {})
	keywordHandler:addKeyword({"spell"}, list, {})
end

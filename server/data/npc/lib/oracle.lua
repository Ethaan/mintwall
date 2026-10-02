-- The Oracle (Rookgaard, the free side) and the Gatekeeper (Rookgaard, the premium side, west of King's Bridge): a
-- player of level 8 picks his home town and his vocation and leaves Rookgaard for good. Decided with the user
-- 2026-10-01: no starter kit (7.4 gave none - the bag of runes and weapons was TFS's), and the towns of the 2005
-- TibiaWiki pages - the Oracle Carlin, Thais and Venore, the Gatekeeper Ab'Dendriel, Ankrahmun, Darashia and
-- Kazordoon (no Edron, no Port Hope, no Island of Destiny). The player is teleported a moment after "SO BE IT!", so
-- he sees it (it used to be said after he was gone). spec:
--   towns       {"Carlin", ...} - the names of the towns (towns.xml), in the order he lists them
--   minLevel    below it: spec.tooYoung
--   maxLevel    above it: spec.tooOld (nil: no limit)
--   caps        the Oracle speaks in capitals
--   greeting, tooYoung, tooOld, farewell
--   text        {town = function(list), chosen = function(town), vocation = {[1] = ..., [2] = ...}, vocations = ...,
--                done = ..., again = ... (to a no when he asks "are you sure"; nil: the talk ends)}
local VOCATIONS = {{"sorcerer", 1}, {"druid", 2}, {"paladin", 3}, {"knight", 4}}
local TELEPORT_AFTER = 1000          -- ms: the player sees the NPC's last words, then goes

local function listTowns(towns, caps)
	local names = {}
	for i, town in ipairs(towns) do
		names[i] = caps and string.upper(town) or town
	end
	if #names == 1 then
		return names[1]
	end
	return table.concat(names, ", ", 1, #names - 1) .. (caps and ", OR " or " or ") .. names[#names]
end

local function sendAway(cid, destination)
	if isPlayer(cid) then
		doSendMagicEffect(getCreaturePosition(cid), CONST_ME_TELEPORT)
		doTeleportThing(cid, destination)
		doSendMagicEffect(destination, CONST_ME_TELEPORT)
	end
end

function oracleNpc(spec)
	local chosen = {}                -- the town and vocation of the player he is talking to
	local npcHandler
	npcHandler = questNpc{
		farewell = spec.farewell,
		walkaway = spec.farewell,
		greet = function(cid, say)
			local level = getPlayerLevel(cid)
			if level < spec.minLevel then
				say(cid, spec.tooYoung, true)
				return nil
			elseif spec.maxLevel and level > spec.maxLevel then
				say(cid, string.gsub(spec.tooOld, "|PLAYERNAME|", getCreatureName(cid)), true)
				return nil
			end
			chosen = {}
			return spec.greeting
		end,
		quest = function(cid, msg, state, say)
			if state.topic == 0 then
				if containsWord(msg, "yes") then
					state.topic = 1
					say(cid, spec.text.town(listTowns(spec.towns, spec.caps)))
				else
					npcHandler:unGreet(cid)
				end
				return true
			elseif state.topic == 1 then
				for _, town in ipairs(spec.towns) do
					if containsWord(msg, string.lower(town)) then
						chosen.town = town
						state.topic = 2
						say(cid, spec.text.chosen(spec.caps and string.upper(town) or town))
						return true
					end
				end
				say(cid, listTowns(spec.towns, spec.caps) .. "?")
				return true
			elseif state.topic == 2 then
				for _, vocation in ipairs(VOCATIONS) do
					if containsWord(msg, vocation[1]) then
						chosen.vocation = vocation[2]
						state.topic = 3
						say(cid, spec.text.vocation[vocation[2]])
						return true
					end
				end
				say(cid, spec.text.vocations)
				return true
			elseif state.topic == 3 then
				state.topic = 0
				if not containsWord(msg, "yes") then
					if spec.text.again then       -- the Gatekeeper asks again; the Oracle ends the talk
						say(cid, spec.text.again)
						state.topic = 2
					else
						npcHandler:unGreet(cid)
					end
					return true
				end
				local town = getTownIdByName(chosen.town)
				local destination = getTownTemplePosition(town)
				say(cid, spec.text.done)
				doPlayerSetVocation(cid, chosen.vocation)
				doPlayerSetTown(cid, town)
				npcHandler:releaseFocus(cid)
				addEvent(sendAway, TELEPORT_AFTER, cid, destination)
				return true
			end
		end,
	}
	return npcHandler
end

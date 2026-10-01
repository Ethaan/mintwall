-- The sea captains (docs/reference-74/travel: TibiaWiki's ship captain pages as they stood before 7.5 - Port Hope
-- came with 7.5, Liberty Bay with 7.8, Svargrond with 8.0 - so a captain sails only the routes below). "<town>" asks
-- "Do you want to travel to <town> for <price> gold coins?", "yes" sails (premium only: "Captain Bluebear will transport
-- any premium players by ship"); "bring me to <town>", not talking to him, sails at once. A Grand Postman pays 10 gp
-- less (npc/lib/postman.lua) and the quoted price says so. A route may divert the ship (the Ghost Ship).
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

HARBOURS = {
	["Thais"] = {x = 32313, y = 32212, z = 7},
	["Carlin"] = {x = 32388, y = 31821, z = 7},
	["Ab'Dendriel"] = {x = 32734, y = 31669, z = 7},
	["Venore"] = {x = 32954, y = 32022, z = 7},
	["Edron"] = {x = 33176, y = 31764, z = 7},
	["Darashia"] = {x = 33290, y = 32481, z = 7},
	["Ankrahmun"] = {x = 33092, y = 32884, z = 7},
	["Cormaya"] = {x = 33288, y = 31956, z = 7},
}

local function travel(cid, route, say, spec, force)
	if not isPremium(cid) then
		say(cid, "I'm sorry, but you need a premium account in order to travel onboard our ships.", force)
		return false
	end
	if not doPlayerRemoveMoney(cid, travelCost(cid, route.cost)) then
		say(cid, "You don't have enough money.", force)
		return false
	end
	local destination = HARBOURS[route.town]
	if route.divert then
		destination = route.divert() or destination
	end
	postmanTravelled(cid, getCreatureName(getNpcCid()), HARBOURS[route.town])
	return destination
end

-- spec: routes = {{town = "Carlin", cost = 110, words = {"carlin"}, divert = function() -> position or nil}, ...},
-- greet, farewell, talk (as questNpc).
function captainNpc(spec)
	local towns = {}
	for _, route in ipairs(spec.routes) do
		route.words = route.words or {string.lower(route.town)}
		table.insert(towns, route.town)
	end
	local list = table.concat(towns, ", ", 1, #towns - 1) .. (#towns > 1 and " and " or "") .. towns[#towns]

	local function routeFor(msg)
		for _, route in ipairs(spec.routes) do
			for _, word in ipairs(route.words) do
				if containsWord(msg, word) then
					return route
				end
			end
		end
		return nil
	end

	local npcHandler
	npcHandler = questNpc{
		greet = spec.greet,
		farewell = spec.farewell or "Good bye. Recommend us if you were satisfied with our service.",
		walkaway = spec.farewell or "Good bye then.",
		anyone = function(cid, msg, say)
			if not (containsWord(msg, "bring") and containsWord(msg, "me") and containsWord(msg, "to")) then
				return false
			end
			if npcHandler and npcHandler:isFocused(cid) then
				return false
			end
			local route = routeFor(msg)
			if route == nil then
				return false
			end
			local destination = travel(cid, route, say, spec, true)
			if destination then
				doTeleportThing(cid, destination)
				doSendMagicEffect(destination, CONST_ME_ENERGYAREA)
			end
			return true
		end,
		quest = function(cid, msg, state, say)
			if state.topic > 0 and containsWord(msg, "yes") then
				local route = spec.routes[state.topic]
				state.topic = 0
				local destination = travel(cid, route, say, spec)
				if destination then
					say(cid, "Set the sails!")
					npcHandler:releaseFocus(cid)
					teleportAfterWords(cid, destination)
				end
				return true
			elseif state.topic > 0 and containsWord(msg, "no") then
				state.topic = 0
				say(cid, "We would like to serve you some time.")
				return true
			end
			local route = routeFor(msg)
			if route then
				for n, r in ipairs(spec.routes) do
					if r == route then
						state.topic = n
					end
				end
				say(cid, "Do you want to travel to " .. route.town .. " for " .. travelCost(cid, route.cost) .. " gold coins?")
				return true
			elseif containsWord(msg, "destination") or containsWord(msg, "passage") or containsWord(msg, "travel")
					or containsWord(msg, "sail") or containsWord(msg, "route") then
				state.topic = 0
				say(cid, "Where do you want to go? To " .. list .. "?")
				return true
			end
			return false
		end,
		talk = spec.talk,
	}
	return npcHandler
end

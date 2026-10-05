-- /sellhouse <name>[, <house>]: the engine's house transfer (Commands::sellHouse offers the house document in a trade;
-- the house changes hands when the trade completes, House::executeTransfer). This runs first and refuses a receiver
-- who may not have the house (data/lib/houses.lua houseTransferProblem: premium, one house and one guildhall per
-- account, guildhalls for guild leaders); otherwise it lets the engine's command go on (return true). The engine
-- checks the same rules again when the trade is offered, accepted and carried out (House::canTransferTo).
--
-- A character may own a house and a guildhall: the house sold is the one named after a comma, else the one he
-- stands in or faces, else the only one he owns - as Commands::sellHouse picks it. Older builds always sold the first
-- house the engine found (getHouseByPlayerGUID) and read no house name: there another choice is refused.

dofile(getDataDir() .. 'lib/houses.lua')

local function cancel(cid, text)
	doPlayerSendTextMessage(cid, MESSAGE_STATUS_SMALL, text)
end

local function trim(s)
	return (string.gsub(s or "", "^%s*(.-)%s*$", "%1"))
end

-- the houses `guid` owns: {house id, ...}
local function ownedHouses(guid)
	local owned = {}
	for _, id in pairs(getHouseList() or {}) do
		if getHouseOwner(id) == guid then
			table.insert(owned, id)
		end
	end
	return owned
end

local function ownHouseAt(guid, pos)
	local house = getTileHouseInfo(pos)
	if house ~= false and house ~= nil and house ~= 0 and getHouseOwner(house) == guid then
		return house
	end
	return nil
end

-- the house to sell, or nil and why not (nil, nil: let the engine answer)
local function houseToSell(cid, houseName)
	local guid = getPlayerGUID(cid)
	local owned = ownedHouses(guid)
	if #owned == 0 then
		return nil, nil                -- "You do not own any house."
	end
	if houseName ~= "" then
		for _, id in ipairs(owned) do
			if string.lower(getHouseName(id)) == string.lower(houseName) then
				return id
			end
		end
		return nil, "You do not own a house of that name."
	end
	local here = getCreaturePosition(cid)
	local house = ownHouseAt(guid, here)
		or ownHouseAt(guid, getPosByDir({x = here.x, y = here.y, z = here.z}, getCreatureLookDir(cid)))
	if house ~= nil then
		return house
	end
	if #owned > 1 then
		return nil, "You own a house and a guildhall. Stand in the one you want to sell, or name it: /sellhouse"
			.. " <player>, <house>."
	end
	return owned[1]
end

function onSay(cid, words, param)
	local name, houseName = trim(param), ""
	local comma = string.find(name, ",", 1, true)
	if comma ~= nil then
		name, houseName = trim(string.sub(name, 1, comma - 1)), trim(string.sub(name, comma + 1))
	end
	if name == "" then
		return true                    -- the engine's answer
	end
	local house, why = houseToSell(cid, houseName)
	if house == nil then
		if why == nil then
			return true                -- "You do not own any house."
		end
		cancel(cid, why)
		return false
	end
	if not HOUSE_ENGINE_CHECKS then    -- an older build sells the first house it finds and takes the whole param as a name
		local first = getHouseByPlayerGUID(getPlayerGUID(cid))
		if first ~= house or houseName ~= "" then
			cancel(cid, "For now /sellhouse can only sell " .. getHouseName(first) .. ": say /sellhouse <player>.")
			return false
		end
	end
	local partner = getPlayerByNameWildcard(name)
	if partner == nil or partner == false or partner == 0 or not isPlayer(partner) then
		return true                    -- "Trade player not found."
	end
	houseRequestsTable()
	local problem = houseTransferProblem(getPlayerGUID(partner), house)
	if problem ~= nil then
		cancel(cid, problem)
		return false
	end
	return true
end

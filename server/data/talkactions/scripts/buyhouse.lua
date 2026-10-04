-- /buyhouse said in front of a house door, facing it: asks for the house, handed over at the next server save.
-- /buyhouse anywhere else: shows the account's pending request. /cancelhouse: withdraws it.
-- The rules and the request table: data/lib/houses.lua.

dofile(getDataDir() .. 'lib/houses.lua')

local function cancel(cid, text)
	doPlayerSendTextMessage(cid, MESSAGE_STATUS_SMALL, text)
end

local function info(cid, text)
	doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, text)
end

-- the house whose door the character faces from outside, or nil
local function houseInFront(cid)
	local here = getCreaturePosition(cid)
	if getTileHouseInfo(here) ~= 0 then
		return nil
	end
	local front = getPosByDir({x = here.x, y = here.y, z = here.z}, getCreatureLookDir(cid))
	local house = getTileHouseInfo(front)
	if house == false or house == 0 then
		return nil
	end
	local door = getTileItemByType(front, ITEM_TYPE_DOOR)
	if door == nil or door == false or door.itemid == 0 then
		return nil
	end
	return house
end

local function ask(cid, guid, house)
	if not isPlayer(cid) or getPlayerGUID(cid) ~= guid then   -- logged out meanwhile
		return
	end
	local ok, text = requestHouse(guid, house)
	if ok then
		info(cid, text)
	else
		cancel(cid, text)
	end
end

function onSay(cid, words, param)
	houseRequestsTable()
	local account = getPlayerAccountId(cid)

	if words == "/cancelhouse" then
		local ok, r = cancelHouseRequest(account)
		if ok then
			info(cid, "You have withdrawn the request for the house " .. getHouseName(r.house) .. ".")
		else
			cancel(cid, "Your account has not asked for a house.")
		end
		return false
	end

	local house = houseInFront(cid)
	if house == nil then
		local r = getAccountHouseRequest(account)
		if r ~= nil then
			info(cid, describeHouseRequest(r))
		else
			cancel(cid, "Stand in front of the door of the house you want, facing it, and say /buyhouse. The house"
				.. " is handed over at the next server save.")
		end
		return false
	end

	if getHouseOwner(house) == getPlayerGUID(cid) then
		cancel(cid, "You are already the owner of this house.")
		return false
	end
	if not isPremium(cid) then                  -- answered at once; the rest needs the depot as saved
		cancel(cid, "You need a premium account.")
		return false
	end
	-- the depot is read from the database: save the character, read it when the save is written
	doSavePlayer(cid)
	addEvent(ask, HOUSE_CHECK_DELAY, cid, getPlayerGUID(cid), house)
	return false
end

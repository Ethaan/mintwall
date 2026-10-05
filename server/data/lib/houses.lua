-- Getting a house (task.md Q17, decided with the user 2026-10-04). In 7.4 a house was auctioned on tibia.com: the
-- winner paid the bid plus the first month's rent from the depot of the house's town (no banks before 7.9), one house
-- per account, guildhalls for guild leaders only. Tibiantis' houses page: "Each account can only rent one house and
-- one guildhouse, but guildhouses are restricted only to the leaders of active guilds [...] the winner will have the
-- bid plus the first rent debited to their depot of the corresponding town during the next server start". Ours, like
-- Tibiantis: one house and one guildhall per account (decided with the user 2026-10-04; it was one of any kind).
--
-- Until there is a website, /buyhouse (talkactions/scripts/buyhouse.lua) is the auction's stand-in: said in front of
-- a house door it records a REQUEST in the table house_requests; the next daily server save
-- (globalevents/scripts/serversave.lua) hands the house over. A website can write the same rows (state 0) and the
-- save does the rest. First come, first served: a house with a pending request takes no other one.
--
-- The rules, checked when the request is made and again at the save:
--   - the house has no owner and no other pending request;
--   - the character has a premium account;
--   - no character of the account owns a house of the same kind (house or guildhall) or has a pending request for
--     one: an account may have one house and one guildhall;
--   - a guildhall: the character is the leader of a guild (guild rank level 3, the engine's "Leader" rank);
--   - the depot of the house's town holds the first month's rent in coins (only the depot, as in 7.4: carried gold
--     does not count). The save does not take it here: setHouseOwner leaves the house unpaid, so Houses::payHouses
--     in the same save takes the first month's rent from that depot, as it takes every rent.
-- A request whose checks fail at the save is cancelled. The outcome stays in the table (state 1 done, 2 cancelled)
-- until the character's next login shows it (creaturescripts/scripts/login.lua).
--
-- The depot: getDepotMoneyByGUID (the engine) counts it in memory for a character online and loads a character
-- offline once his pending saves are written - so /buyhouse answers at once and the server save goes on right after
-- the kick. Older builds have no getDepotMoneyByGUID (nor a working isHouseGuildHall): there the depot is read from
-- the database (player_depotitems), so the character is saved first, /buyhouse answers after HOUSE_CHECK_DELAY and
-- the server save waits as long after kicking everyone (saves are written by a background thread).

HOUSE_REQUEST_PENDING, HOUSE_REQUEST_DONE, HOUSE_REQUEST_CANCELLED = 0, 1, 2
HOUSE_ENGINE_CHECKS = getDepotMoneyByGUID ~= nil   -- the engine reads guildhall="true" and counts depots in memory
HOUSE_CHECK_DELAY = HOUSE_ENGINE_CHECKS and 0 or 1500   -- ms between saving a character and reading its depot

local GUILD_LEADER = 3                 -- guild_ranks.level of a guild's leader (Leader 3, Vice-Leader 2, Member 1)
local COINS = {[2148] = 1, [2152] = 100, [2160] = 10000}   -- gold, platinum, crystal coin
local ALWAYS_PREMIUM = 2 ^ 37          -- PlayerFlag_IsAlwaysPremium (const.h): a GM group

local function query(sql)
	local res = db.storeQuery(sql)
	if res == false or res == nil then
		return nil
	end
	return res
end

function houseRequestsTable()
	db.query("CREATE TABLE IF NOT EXISTS `house_requests` (`id` INTEGER PRIMARY KEY, `house_id` INTEGER NOT NULL,"
		.. " `player_id` INTEGER NOT NULL, `account_id` INTEGER NOT NULL, `created` INTEGER NOT NULL,"
		.. " `state` INTEGER NOT NULL DEFAULT 0, `message` VARCHAR(255) NOT NULL DEFAULT '')")
end

-- The guildhalls: the houses with guildhall="true" in Tibia74-houses.xml (Tibiantis' 46 guildhouses and Ankrahmun's
-- 4), read by Houses::loadHousesXML (isHouseGuildHall). OLD_BUILD_GUILDHALLS only serves builds older than that, whose
-- isHouseGuildHall was a stub: delete it (and its test in tests/test_houses.py) once every server runs a newer build.
local OLD_BUILD_GUILDHALLS = {1, 2, 3, 4, 5, 58, 71, 77, 111, 112, 120, 122, 123, 133, 134, 135, 136, 194, 220, 226,
	229, 243, 244, 245, 246, 315, 316, 317, 332, 333, 334, 335, 336, 337, 397, 398, 409, 410, 559, 560, 561, 563, 591,
	618, 666, 687, 734, 744, 813, 814}

local guildhalls = nil                 -- {house id = true}, built at the first use

local function guildhallSet()
	if guildhalls == nil then
		guildhalls = {}
		if HOUSE_ENGINE_CHECKS then
			for _, id in pairs(getHouseList() or {}) do
				if isHouseGuildHall(id) == true then
					guildhalls[id] = true
				end
			end
		else
			for _, id in ipairs(OLD_BUILD_GUILDHALLS) do
				guildhalls[id] = true
			end
		end
	end
	return guildhalls
end

function isGuildhall(house)
	return guildhallSet()[house] == true
end

-- the guildhalls' ids
function guildhallIds()
	local ids = {}
	for id in pairs(guildhallSet()) do
		table.insert(ids, id)
	end
	table.sort(ids)
	return ids
end

local function accountOf(guid)
	local res = query("SELECT `account_id` FROM `players` WHERE `id` = " .. guid)
	if res == nil then
		return nil
	end
	local account = result.getDataInt(res, "account_id")
	result.free(res)
	return account
end

local function hasPremium(guid)
	local res = query("SELECT `accounts`.`premend` AS `premend`, `groups`.`flags` AS `flags` FROM `players`"
		.. " JOIN `accounts` ON `accounts`.`id` = `players`.`account_id`"
		.. " LEFT JOIN `groups` ON `groups`.`id` = `players`.`group_id` WHERE `players`.`id` = " .. guid)
	if res == nil then
		return false
	end
	local premend = tonumber(result.getDataInt(res, "premend")) or 0
	local flags = tonumber(result.getDataLong(res, "flags")) or 0
	result.free(res)
	return premend > os.time() or math.floor(flags / ALWAYS_PREMIUM) % 2 == 1
end

local function isGuildLeader(guid)
	local res = query("SELECT `guild_ranks`.`level` AS `level` FROM `players` JOIN `guild_ranks`"
		.. " ON `guild_ranks`.`id` = `players`.`rank_id` WHERE `players`.`id` = " .. guid)
	if res == nil then
		return false
	end
	local level = result.getDataInt(res, "level")
	result.free(res)
	return level >= GUILD_LEADER
end

-- the coins in a character's depot of one town: as they are (the engine), else as last saved (older builds)
function getDepotMoney(guid, depot)
	if HOUSE_ENGINE_CHECKS then
		return tonumber(getDepotMoneyByGUID(guid, depot)) or 0
	end
	return getSavedDepotMoney(guid, depot)
end

-- the coins in a character's depot of one town, as last saved (player_depotitems)
function getSavedDepotMoney(guid, depot)
	local res = query("SELECT `pid`, `sid`, `itemtype`, `count` FROM `player_depotitems` WHERE `player_id` = " .. guid)
	if res == nil then
		return 0
	end
	local parent, coins = {}, {}
	repeat
		local pid, sid = result.getDataInt(res, "pid"), result.getDataInt(res, "sid")
		parent[sid] = pid
		local value = COINS[result.getDataInt(res, "itemtype")]
		if value ~= nil then
			table.insert(coins, {pid, value * math.max(1, result.getDataInt(res, "count"))})
		end
	until not result.next(res)
	result.free(res)
	local money = 0
	for _, c in ipairs(coins) do
		local pid, steps = c[1], 0
		while parent[pid] ~= nil and steps < 1000 do   -- up to the depot locker, whose pid is the depot id
			pid, steps = parent[pid], steps + 1
		end
		if pid == depot then
			money = money + c[2]
		end
	end
	return money
end

-- "house" or "guildhall": an account may have one of each (decided with the user 2026-10-04)
local function kindOf(house)
	return isGuildhall(house) and "guildhall" or "house"
end

-- SQL: the requests (`house_id`) for a house of the same kind as `house`
local function sameKind(house)
	return "`house_id` " .. (isGuildhall(house) and "IN" or "NOT IN") .. " (" .. table.concat(guildhallIds(), ", ")
		.. ")"
end

-- the house of the same kind as `house` (house or guildhall) a character of this account owns: house id, owner guid.
-- Every house is looked at: getHouseByPlayerGUID gives one house a character owns, and one may own both kinds.
local function accountHouse(account, house)
	local res = query("SELECT `id` FROM `players` WHERE `account_id` = " .. account)
	if res == nil then
		return nil
	end
	local mine = {}
	repeat
		mine[result.getDataInt(res, "id")] = true
	until not result.next(res)
	result.free(res)
	local guildhall = isGuildhall(house)
	for _, id in pairs(getHouseList() or {}) do
		local owner = getHouseOwner(id)
		if owner ~= false and owner ~= 0 and mine[owner] and isGuildhall(id) == guildhall then
			return id, owner
		end
	end
	return nil
end

-- pending request of this account / for this house: {id, house, guid, account} or nil
local function pendingRequest(where)
	local res = query("SELECT `id`, `house_id`, `player_id`, `account_id` FROM `house_requests` WHERE `state` = "
		.. HOUSE_REQUEST_PENDING .. " AND " .. where .. " ORDER BY `id` LIMIT 1")
	if res == nil then
		return nil
	end
	local r = {id = result.getDataInt(res, "id"), house = result.getDataInt(res, "house_id"),
		guid = result.getDataInt(res, "player_id"), account = result.getDataInt(res, "account_id")}
	result.free(res)
	return r
end

function getAccountHouseRequest(account)
	houseRequestsTable()
	return pendingRequest("`account_id` = " .. account)
end

-- every pending request of the account, oldest first: a house and a guildhall at most
function getAccountHouseRequests(account)
	houseRequestsTable()
	local requests = {}
	local res = query("SELECT `id`, `house_id`, `player_id`, `account_id` FROM `house_requests` WHERE `state` = "
		.. HOUSE_REQUEST_PENDING .. " AND `account_id` = " .. account .. " ORDER BY `id`")
	if res ~= nil then
		repeat
			table.insert(requests, {id = result.getDataInt(res, "id"), house = result.getDataInt(res, "house_id"),
				guid = result.getDataInt(res, "player_id"), account = result.getDataInt(res, "account_id")})
		until not result.next(res)
		result.free(res)
	end
	return requests
end

local function townName(house)
	return getTownNameById(getHouseTown(house)) or "?"
end

-- nil if `guid` may have `house` now, else why not. `request`: the request being handed over (it does not count as
-- another pending request).
function houseRequestProblem(guid, house, request)
	local account = accountOf(guid)
	if account == nil then
		return "the character does not exist"
	end
	local owner = getHouseOwner(house)
	if owner == false then
		return "there is no such house"
	end
	if owner ~= 0 then
		return "This house already has an owner."
	end
	if not hasPremium(guid) then
		return "You need a premium account."
	end
	local kind = kindOf(house)
	local owned, ownedBy = accountHouse(account, house)
	if owned ~= nil then
		return "Your account already has a " .. kind .. ": " .. getHouseName(owned) .. " (" .. (getPlayerNameByGUID(ownedBy)
			or "?") .. "). Each account can have one house and one guildhall."
	end
	local mine = pendingRequest("`account_id` = " .. account .. " AND " .. sameKind(house)
		.. (request and (" AND `id` <> " .. request) or ""))
	if mine ~= nil then
		return "Your account has already asked for a " .. kind .. ": " .. getHouseName(mine.house) .. ". Each account"
			.. " can have one house and one guildhall."
	end
	local other = pendingRequest("`house_id` = " .. house .. (request and (" AND `id` <> " .. request) or ""))
	if other ~= nil then
		return "Someone has already asked for this house. It is handed over at the next server save."
	end
	if isGuildhall(house) and not isGuildLeader(guid) then
		return "Only the leader of a guild can rent a guildhall."
	end
	local rent, money = getHouseRent(house), getDepotMoney(guid, getHouseTown(house))
	if money < rent then
		return "You need the first month's rent of " .. rent .. " gold in your depot in " .. townName(house) .. "."
			.. " You have " .. money .. " gold there."
	end
	return nil
end

-- /sellhouse (the engine's house transfer, a trade of the house document): nil if the character `guid` may take
-- `house` from its owner, else why not - the same rules as a request: premium, one house and one guildhall per account
-- (the house itself excepted: a transfer between two characters of one account), a guildhall only to a guild leader
function houseTransferProblem(guid, house)
	local account = accountOf(guid)
	if account == nil then
		return "There is no such character."
	end
	local name = getPlayerNameByGUID(guid) or "?"
	if not hasPremium(guid) then
		return name .. " has no premium account."
	end
	local kind = kindOf(house)
	local owned = accountHouse(account, house)
	if owned ~= nil and owned ~= house then
		return name .. "'s account already has a " .. kind .. ". Each account can have one house and one guildhall."
	end
	if pendingRequest("`account_id` = " .. account .. " AND " .. sameKind(house)) ~= nil then
		return name .. "'s account has asked for a " .. kind .. " already. Each account can have one house and one"
			.. " guildhall."
	end
	if isGuildhall(house) and not isGuildLeader(guid) then
		return "Only the leader of a guild can rent a guildhall."
	end
	return nil
end

-- /buyhouse in front of the door (after the character was saved): the request, or why not
function requestHouse(guid, house)
	houseRequestsTable()
	local problem = houseRequestProblem(guid, house, nil)
	if problem ~= nil then
		return false, problem
	end
	db.query("INSERT INTO `house_requests` (`house_id`, `player_id`, `account_id`, `created`, `state`) VALUES ("
		.. house .. ", " .. guid .. ", " .. accountOf(guid) .. ", " .. os.time() .. ", " .. HOUSE_REQUEST_PENDING .. ")")
	return true, "You have asked for the house " .. getHouseName(house) .. ". It will be yours after the next server"
		.. " save, if you still have a premium account then and the first month's rent of " .. getHouseRent(house)
		.. " gold in your depot in " .. townName(house) .. " (taken at the save). Say /cancelhouse to withdraw."
end

function describeHouseRequest(r)
	return "Your account has asked for the house " .. getHouseName(r.house) .. " (" .. townName(r.house) .. ", rent "
		.. getHouseRent(r.house) .. " gold a month) for " .. (getPlayerNameByGUID(r.guid) or "?") .. ". It is handed"
		.. " over at the next server save. Say /cancelhouse to withdraw."
end

-- withdraw the account's pending requests (a house and a guildhall at most): true and the list, or false
function cancelHouseRequests(account)
	local requests = getAccountHouseRequests(account)
	if #requests == 0 then
		return false
	end
	for _, r in ipairs(requests) do
		db.query("DELETE FROM `house_requests` WHERE `id` = " .. r.id)
	end
	return true, requests
end

local function finish(r, state, message)
	db.query("UPDATE `house_requests` SET `state` = " .. state .. ", `message` = " .. db.escapeString(message)
		.. " WHERE `id` = " .. r.id)
end

-- the server save (everyone kicked and saved, before payHouses): hand the requested houses over, oldest first
function handOverRequestedHouses()
	houseRequestsTable()
	local requests = {}
	local res = query("SELECT `id`, `house_id`, `player_id`, `account_id` FROM `house_requests` WHERE `state` = "
		.. HOUSE_REQUEST_PENDING .. " ORDER BY `id`")
	if res ~= nil then
		repeat
			table.insert(requests, {id = result.getDataInt(res, "id"), house = result.getDataInt(res, "house_id"),
				guid = result.getDataInt(res, "player_id"), account = result.getDataInt(res, "account_id")})
		until not result.next(res)
		result.free(res)
	end
	for _, r in ipairs(requests) do
		local name = getPlayerNameByGUID(r.guid) or tostring(r.guid)
		local problem = houseRequestProblem(r.guid, r.house, r.id)
		local houseName = getHouseOwner(r.house) ~= false and getHouseName(r.house) or ("house " .. r.house)
		if problem == nil then
			setHouseOwner(r.house, r.guid)
			finish(r, HOUSE_REQUEST_DONE, "The house " .. houseName .. " is yours now. The first month's rent of "
				.. getHouseRent(r.house) .. " gold was taken from your depot in " .. townName(r.house) .. ".")
			print("> Server save: house " .. houseName .. " handed over to " .. name .. ".")
		else
			finish(r, HOUSE_REQUEST_CANCELLED, "Your request for the house " .. houseName .. " was cancelled at the"
				.. " server save: " .. problem)
			print("> Server save: request of " .. name .. " for house " .. houseName .. " cancelled: " .. problem)
		end
	end
end

-- login: what became of the character's requests
function showHouseRequestResults(cid)
	houseRequestsTable()
	local guid = getPlayerGUID(cid)
	local res = query("SELECT `id`, `message` FROM `house_requests` WHERE `player_id` = " .. guid .. " AND `state` <> "
		.. HOUSE_REQUEST_PENDING .. " ORDER BY `id`")
	if res == nil then
		return
	end
	local ids = {}
	repeat
		table.insert(ids, result.getDataInt(res, "id"))
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, result.getDataString(res, "message"))
	until not result.next(res)
	result.free(res)
	db.query("DELETE FROM `house_requests` WHERE `id` IN (" .. table.concat(ids, ", ") .. ")")
end

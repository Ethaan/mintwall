-- Daily server save (task.md "Daily server save", Q5 decided with the user 2026-10-04: like Tibiantis - "every day at
-- 9:00 a.m. CET/CEST [...] about 10 minutes during which the game worlds are offline, you won't be able to log into
-- the game 5 minutes (or less) before the save" (tibiantis.online FAQ) - but at an hour of our own: config.lua
-- ServerSaveHour, the machine's local time; ServerSaveEnabled = false switches it off).
--
-- 5, 3 and 1 minutes before: Tibia's warnings (TibiaWiki "Server Save": "Server is saving game in 5 minutes. Please
-- come back in 10 minutes." ... "in 1 minute. Please log out."), red in the middle of the screen; from 5 minutes
-- before no one logs in (GAME_STATE_CLOSING: the engine's "The game is just going down. Please try again later.").
-- At the hour, in this order:
--   1. close the game and kick everyone (GMs too); a kick saves the character (Player::onRemoved);
--   2. release the house of every owner without premium (Tibiantis FAQ: "Houses are lost during the next server
--      save") - setHouseOwner(house, 0) moves its items to the owner's depot in the house's town
--      (House::transferToDepot), the same rule as creaturescripts/scripts/login.lua premiumExpired. Before the
--      rent, so a lost house is not charged;
--   3. hand over the houses asked for with /buyhouse (data/lib/houses.lua: the checks again, the owner set; the
--      first month's rent is then taken by payHouses below) - 2 to 3 s after the kick, when the kicked characters'
--      saves (written by a background thread) are in the database the checks read;
--   4. doSaveServer(1): everything saved + Houses::payHouses (the monthly rent from the depot of the house's town;
--      without the money a warning letter there, one a day, the house lost after 7) + temporary bans cleared;
--   5. shut down: GAME_STATE_SHUTDOWN saves once more, waits for the save writer and the process exits with
--      EXIT_CODE so the supervisor restarts it (docs/production-plan.md "Restart"; until one exists the server
--      stays down). A restart, not close-and-reopen: the "once per server save" quest states (the Annihilator
--      lever, the Draconia keys, the Paradox Tower ladders...) come back only when the map loads again.
-- No "refresh" (map items reset at the save): our map has no refresh-flag tiles (task.md).
--
-- Tests only (tests/test_server_save.py): ServerSaveTestIn = N runs the save N seconds after the start instead of at
-- the hour, ServerSaveTestMinute = N makes a warning "minute" N seconds long.

dofile(getDataDir() .. 'lib/houses.lua')

local GAME_STATE_CLOSED, GAME_STATE_SHUTDOWN, GAME_STATE_CLOSING = 3, 4, 5
local EXIT_CODE = 10                   -- the process exit code after the save (otserv.cpp main): restart me
local WARNINGS = {5, 3, 1}             -- minutes before the save
local CLOSE_LOGINS = 5                 -- minutes before the save
local ALWAYS_PREMIUM = 2 ^ 37          -- PlayerFlag_IsAlwaysPremium (const.h): a GM group

local due = nil                        -- os.time() of the next save, set at the first think
local warned = {}
local closed, done = false, false
local kickedAt = nil                   -- os.time() of the kick: the rest of the save follows HOUSE_CHECK_DELAY later

local function enabled()
	local v = getConfigValue("ServerSaveEnabled")
	return v == true or v == 1
end

local function nextSave(now)
	local test = tonumber(getConfigValue("ServerSaveTestIn"))
	if test ~= nil then
		return now + test
	end
	local t = os.date("*t", now)
	t.hour, t.min, t.sec, t.isdst = tonumber(getConfigValue("ServerSaveHour")) or 9, 0, 0, nil
	local at = os.time(t)
	if at <= now then                  -- today's is past (e.g. the restart right after it): tomorrow's
		t.day = t.day + 1
		at = os.time(t)
	end
	return at
end

local function warningText(minutes)
	if minutes == 1 then
		return "Server is saving game in 1 minute. Please log out."
	end
	return "Server is saving game in " .. minutes .. " minutes. Please come back in 10 minutes."
end

local function tellEveryone(text)
	for _, cid in ipairs(getPlayersOnlineList()) do
		doPlayerSendTextMessage(cid, MESSAGE_STATUS_WARNING, text)
	end
end

-- premium of a character that is not online (Account::getPremiumDaysLeft, Player::isPremium); unknown: true (keep)
local function hasPremium(guid)
	local res = db.storeQuery("SELECT `accounts`.`premend` AS `premend`, `groups`.`flags` AS `flags` FROM `players`"
		.. " JOIN `accounts` ON `accounts`.`id` = `players`.`account_id`"
		.. " LEFT JOIN `groups` ON `groups`.`id` = `players`.`group_id` WHERE `players`.`id` = " .. guid)
	if not res then
		return true
	end
	local premend = tonumber(result.getDataInt(res, "premend")) or 0
	local flags = tonumber(result.getDataLong(res, "flags")) or 0
	result.free(res)
	return premend > os.time() or math.floor(flags / ALWAYS_PREMIUM) % 2 == 1
end

local function releaseHousesWithoutPremium()
	for _, house in ipairs(getHouseList()) do
		local owner = getHouseOwner(house)
		if owner ~= false and owner ~= 0 and not hasPremium(owner) then
			local name, town = getHouseName(house), getTownNameById(getHouseTown(house))
			local ownerName = getPlayerNameByGUID(owner) or tostring(owner)
			setHouseOwner(house, 0)    -- the items to the owner's depot in the house's town
			print("> Server save: " .. ownerName .. " has no premium, house " .. name .. " released, its items in the"
				.. " depot in " .. town .. ".")
		end
	end
end

local function saveAndShutDown()
	releaseHousesWithoutPremium()
	handOverRequestedHouses()          -- before the rent: payHouses takes the first month of a house handed over

	if not doSaveServer(1) then        -- with the rent (Houses::payHouses)
		print("> Server save: the save FAILED - the server stays up, closed (/openserver opens it).")
		return
	end
	print("> Server save: done, shutting down (exit code " .. EXIT_CODE .. ").")
	if doSetExitCode ~= nil then       -- older builds have no doSetExitCode: they exit with 0
		doSetExitCode(EXIT_CODE)
	end
	doSetGameState(GAME_STATE_SHUTDOWN)
end

local function serverSave()
	print("> Server save: kicking everyone.")
	doSetGameState(GAME_STATE_CLOSED)
	for _, cid in ipairs(getPlayersOnlineList()) do
		doRemoveCreature(cid)
	end
	kickedAt = os.time()               -- onThink goes on with saveAndShutDown (not from an addEvent: the shutdown
end                                    -- frees the script environment the event still runs in)

function onThink(interval)
	if kickedAt ~= nil then
		if os.time() >= kickedAt + math.ceil(HOUSE_CHECK_DELAY / 1000) + 1 then   -- whole seconds: at least the delay
			kickedAt = nil
			saveAndShutDown()
		end
		return true
	end
	if done or not enabled() then
		return true
	end
	local now = os.time()
	if due == nil then
		due = nextSave(now)
		print("> Server save at " .. os.date("%Y-%m-%d %H:%M:%S", due) .. ".")
	end
	local minute = tonumber(getConfigValue("ServerSaveTestMinute")) or 60

	if now >= due then
		done = true
		serverSave()
		return true
	end

	if not closed and now >= due - CLOSE_LOGINS * minute then
		closed = true
		doSetGameState(GAME_STATE_CLOSING)   -- no more logins (GMs: PlayerFlag_CanAlwaysLogin)
	end

	-- the closest warning due; the earlier ones are skipped (a server started at 8:58 only warns "1 minute")
	local current = nil
	for _, m in ipairs(WARNINGS) do
		if now >= due - m * minute then
			current = m
		end
	end
	if current ~= nil and not warned[current] then
		for _, m in ipairs(WARNINGS) do
			if m >= current then
				warned[m] = true
			end
		end
		tellEveryone(warningText(current))
	end
	return true
end

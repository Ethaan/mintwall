-- Runs on every login. On the very first one the character gets the 7.4 beginner set
-- (club, torch, bag with a red apple, jacket for men / coat for women) and the classic look. On every login a character
-- whose premium ran out loses what premium gave it (premiumExpired below).

dofile(getDataDir() .. 'creaturescripts/lib/premium_areas.lua')
dofile(getDataDir() .. 'lib/houses.lua')

local STORAGE_BEGINNER_SET = 30001

local CLUB, TORCH, BAG, RED_APPLE = 2382, 2050, 1987, 2674
local JACKET, COAT = 2650, 2651

-- The "noob outfit": golden hair, blue shirt, brown legs, dark shoes
-- (picked in the real client's outfit dialog: #FFAA00 / #3F3FBF / #BF6A3F / #242424)
local LOOK = {head = 78, body = 69, legs = 58, feet = 114}
local LOOKTYPE_MALE, LOOKTYPE_FEMALE = 128, 136

-- Premium ran out (task.md "Premium runs out -> free"; decided with the user 2026-10-03: Tibiantis' rules). Tibiantis
-- FAQ: "Houses are lost during the next server save, character is moved out of premium area upon the next login,
-- promotion is deactivated [...] The selected premium outfit can still be used until it is changed."
-- - the promotion: suspended in C++ (ioplayer.cpp); the outfit: kept until changed (protocolgame.cpp parseSetOutfit);
-- - the house: not here - lost at the next daily server save (globalevents/scripts/serversave.lua), its items to the
--   depot of the house's town (House::transferToDepot); tibia.com support: "You will keep all items, even those that
--   were stored in your house when your Premium Time ran out [...] transferred to your depot";
-- - standing in a premium area (lib/premium_areas.lua): to the Thais temple (the Rookgaard premium side: to the
--   Rookgaard temple - a Rookgaard character does not leave the island that way);
-- - a citizen of a premium town (Edron, Darashia, Ankrahmun) becomes a citizen of Thais, or it would respawn there
--   after a death (TibiaWiki "Premium Time": players in premium areas log in "at the temple of Thais (if they are a
--   citizen of a premium city or Thais)"; the Tibiantis FAQ does not say).
-- The messages are ours (no 7.4 source). isPremium is true for a GM (PlayerFlag_IsAlwaysPremium).
local PREMIUM_TOWNS = {["Edron"] = true, ["Darashia"] = true, ["Ankrahmun"] = true}

local function yes(v) return v == true or v == 1 end

local function premiumExpired(cid)
	if yes(isPremium(cid)) then
		return
	end

	local thais = getTownIdByName("Thais")
	if PREMIUM_TOWNS[getTownNameById(getPlayerTown(cid))] then
		doPlayerSetTown(cid, thais)
	end

	local area = getPremiumArea(getCreaturePosition(cid))
	if area ~= nil then
		local temple = getTownTemplePosition(area == "rookgaard" and getTownIdByName("Rookgaard") or thais)
		doTeleportThing(cid, temple)
		doSendMagicEffect(temple, CONST_ME_ENERGYAREA)
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR,
			"Your premium time has run out. You have been moved out of the premium area.")
	end
end

function onLogin(cid)
	premiumExpired(cid)
	showHouseRequestResults(cid)       -- a house asked for with /buyhouse: handed over or cancelled at the server save

	if getPlayerStorageValue(cid, STORAGE_BEGINNER_SET) > 0 then
		return TRUE
	end
	setPlayerStorageValue(cid, STORAGE_BEGINNER_SET, 1)

	local male = getPlayerSex(cid) == 1
	doPlayerAddItem(cid, male and JACKET or COAT, 1)
	doPlayerAddItem(cid, CLUB, 1)
	local bag = doPlayerAddItem(cid, BAG, 1)
	if bag ~= nil and bag ~= 0 then
		doAddContainerItem(bag, RED_APPLE, 1)
		doAddContainerItem(bag, TORCH, 1)
	end

	doCreatureChangeOutfit(cid, {lookType = male and LOOKTYPE_MALE or LOOKTYPE_FEMALE,
		lookHead = LOOK.head, lookBody = LOOK.body, lookLegs = LOOK.legs, lookFeet = LOOK.feet})

	return TRUE
end

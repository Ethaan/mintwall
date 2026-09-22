-- Runs on every login. On the very first one the character gets the 7.4 beginner set
-- (club, torch, bag with a red apple, jacket for men / coat for women) and the classic look.

local STORAGE_BEGINNER_SET = 30001

local CLUB, TORCH, BAG, RED_APPLE = 2382, 2050, 1987, 2674
local JACKET, COAT = 2650, 2651

-- Colours from the client's palette: yellow hair, blue shirt, brown legs, dark shoes
local LOOK = {head = 79, body = 69, legs = 116, feet = 114}
local LOOKTYPE_MALE, LOOKTYPE_FEMALE = 128, 136

function onLogin(cid)
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

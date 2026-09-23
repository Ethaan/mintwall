-- Compatibility helpers for scripts written for TFS/OTX 0.3-era servers.
-- Loaded from global.lua, so available to every script interface.

-- Pure Lua helpers
function isInArray(array, value, caseSensitive)
	if (caseSensitive == nil or caseSensitive == false) and type(value) == "string" then
		local lowerValue = value:lower()
		for _, v in ipairs(array) do
			if type(v) == "string" and v:lower() == lowerValue then
				return true
			end
		end
	else
		for _, v in ipairs(array) do
			if v == value then
				return true
			end
		end
	end
	return false
end

function getBooleanFromString(input)
	local s = tostring(input):lower()
	return s == "yes" or s == "true" or s == "y" or s == "1"
end

function isNumber(str)
	return tonumber(str) ~= nil
end
isNumeric = isNumber

function Position(x, y, z, stackpos)
	return {x = x or 0, y = y or 0, z = z or 0, stackpos = stackpos or 0}
end

function isValidPosition(position)
	return type(position) == "table" and tonumber(position.x) ~= nil and position.x > 0
		and position.y > 0 and position.z >= 0 and position.z <= 15
end

-- Renamed engine functions
getPlayerName = getCreatureName
getPlayerPosition = getCreaturePosition
getThingPosition = getThingPos
getThingfromPos = getThingFromPos
isPlayerPzLocked = isPzLocked
doPlayerSetStorageValue = setPlayerStorageValue
doCreatureSetStorage = setPlayerStorageValue
getCreatureStorage = getPlayerStorageValue
doCreatureSetLookDirection = doSetCreatureDirection
getItemNameById = getItemName
getPlayerBalance = getPlayerAccountBalance
doPlayerAddHealth = doCreatureAddHealth   -- life fluids called it and failed

-- 7.4 magic power for spell and rune formulas: level*2 + mlvl*3, but never below 100
-- (docs/reference-74/formulas.md §5; the engine does the same in Combat::getMinMaxValues)
function magicPower(level, maglevel)
	return math.max(100, level * 2 + maglevel * 3)
end

-- TFS doTeleportThing(uid, pos, pushMove): Avesta takes (uid, pos) and pops the position first,
-- so a third argument breaks the teleport
if _nativeTeleportThing == nil then
	_nativeTeleportThing = doTeleportThing
end
function doTeleportThing(uid, pos)
	return _nativeTeleportThing(uid, pos)
end

-- TFS doPlayerSay(cid, text, type): fluids.lua uses it for "Aaaah..." - without it every drink failed
function doPlayerSay(cid, text, type)
	return doCreatureSay(cid, text, type or 1)
end

function getItemInfo(itemid)
	local d = getItemDescriptions(itemid) or {}
	return {
		name = d.name or getItemName(itemid),
		article = d.article or "",
		plural = d.plural or "",
		stackable = isItemStackable(itemid) == true,
		charges = 0,
	}
end

function getPlayersOnline()
	return getPlayersOnlineList()
end

-- No-ops for features that did not exist in 7.4
function errors(value) return true end
function doPlayerAddBlessing(cid, blessing) return false end
function getPlayerBlessing(cid, blessing) return false end
function doPlayerSetPVPBlessing(cid, value) return false end
function canPlayerWearOutfit(cid, looktype, addons) return true end
function canPlayerWearOutfitId(cid, outfitId, addons) return true end
function doPlayerAddOutfit(cid, looktype, addons) return false end

-- 7.4 promotion: vocations 1-4 become 5-8
function doPlayerSetPromotionLevel(cid, level)
	local voc = getPlayerVocation(cid)
	if level >= 1 and voc >= 1 and voc <= 4 then
		return doPlayerSetVocation(cid, voc + 4)
	end
	return true
end

-- Constants TFS-era scripts expect
CONST_ME_TELEPORT = CONST_ME_ENERGYAREA   -- 7.4 has no dedicated teleport effect; energy sparkles were used
EMPTY_STORAGE = -1
ITEM_PARCEL = 2595
ITEM_LABEL = 2599
MAPMARK_EXCLAMATION = 0                   -- map marks did not exist in 7.4 (doAddMapMark is a no-op)
MAPMARK_GREENNORTH = 0

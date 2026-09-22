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

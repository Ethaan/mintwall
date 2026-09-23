function getDistanceToCreature(id)
	if id == 0 or id == nil then
		return nil
	end

	local creaturePosition = getCreaturePosition(id)
	cx = creaturePosition.x
	cy = creaturePosition.y
	cz = creaturePosition.z
	if cx == nil then
		return nil
	end

	sx, sy, sz = selfGetPosition()
	return math.max(math.abs(sx - cx), math.abs(sy - cy))
end

function moveToPosition(x,y,z)
	selfMoveTo(x, y, z)
end

function moveToCreature(id)
	if id == 0 or id == nil then
		return nil
	end

	tx, ty, tz = getCreaturePosition(id)
	if tx == nil then
		selfGotoIdle()
	else
		moveToPosition(tx, ty, tz)
	end
end

function selfGotoIdle()

end

function isPlayerPremiumCallback(cid)
	return isPremium(cid) and true or false
end

-- keyword is supposed to be lowercase without lowering it
function msgcontains(message, keyword)
	message = string.lower(message)
	keyword = string.lower(keyword)   -- keywords like "Norma" in an NPC's XML must match too
	return (string.find(message, keyword) and 
			not string.find(message, '(%w+)' .. keyword) and 
			not string.find(message, keyword .. '(%w+)'))
end

function selfSayChannel(cid, message)
	return selfSay(message, cid, FALSE)
end

function doPosRemoveItem(_itemid, n, position)
	local thing = getThingfromPos({x = position.x, y = position.y, z = position.z, stackpos = 1})
	if thing.itemid == _itemid then
		doRemoveItem(thing.uid, n)
	else
		return false
	end
	return true
end

function getCount(message)
	if (string.find(message, '[0-9]+')) then
		i, j = string.find(message, '[0-9]+')
		count = string.sub(message, i, j)
		
		if (msgcontains(message, count)) then
			return tonumber(count)
		end
	end
	
	return 1
end

function creatureHasLeft(cid, distance)
	local c = getCreaturePosition(cid)
	sx, sy, sz = selfGetPosition()
	
	if (c.z ~= sz or getDistanceToCreature(cid) > distance) then
		return true
	end
	
	return false
end








-- TFS-era NPC scripts: compatibility layer + Jiddo NpcSystem
dofile(getDataDir() .. 'npc/lib/compat.lua')
dofile(getDataDir() .. 'npc/lib/_npcsystem.lua')

-- Many NPC texts come from 8.x+ datapacks that mark keywords as {trade}; that highlighting does not
-- exist in the 7.4 client, which would print the braces. Every NPC line goes through selfSay.
local rawSelfSay = selfSay
function selfSay(message, ...)
	if(type(message) == 'string') then
		message = string.gsub(message, '[{}]', '')
	end
	return rawSelfSay(message, ...)
end

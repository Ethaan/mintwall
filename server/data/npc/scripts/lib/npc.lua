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
dofile(getDataDir() .. 'npc/lib/postman.lua')   -- the Postman Missions: ranks, passage and postal prices

-- Many NPC texts come from 8.x+ datapacks that mark keywords as {trade}; that highlighting does not
-- exist in the 7.4 client, which would print the braces. Every NPC line goes through selfSay.
local rawSelfSay = selfSay
function selfSay(message, ...)
	if(type(message) == 'string') then
		message = string.gsub(message, '[{}]', '')
	end
	return rawSelfSay(message, ...)
end

-- Blessings (docs/reference-74/death.md). A blessing NPC answers any word of the blessing's name
-- ("spiritual", "shielding"...), offers it for 10000 gold and on "yes" sells it through StdModule.bless
-- (storage BLESSING_STORAGE + number, compat.lua). Returns the offer nodes for extra children.
BLESSING_WORDS_IGNORED = {["of"] = true, ["the"] = true}
function addBlessingKeywords(keywordHandler, npcHandler, number, name, premium, onYes)
	local yes = KeywordNode:new({'yes'}, onYes or StdModule.bless,
		{npcHandler = npcHandler, number = number, premium = premium, cost = 10000})
	local no = KeywordNode:new({'no'}, StdModule.say, {npcHandler = npcHandler, onlyFocus = true, reset = true,
		text = 'Too expensive, eh?'})
	local nodes = {}
	for word in string.gmatch(name, "%a+") do
		if(not BLESSING_WORDS_IGNORED[word]) then
			local node = keywordHandler:addKeyword({word}, StdModule.say, {npcHandler = npcHandler, onlyFocus = true,
				text = 'Do you want to receive the blessing of ' .. name .. ' for 10000 gold?'})
			node:addChildKeywordNode(yes)
			node:addChildKeywordNode(no)
			table.insert(nodes, node)
		end
	end
	return nodes
end

-- A chain of knowledge (the Paradox Tower Quest's Oldrak -> Zoltan -> Padreia -> Lubo): an NPC answers each of its
-- keywords whenever asked; asked in order in one conversation, the last one sets `storage` - once the chain before it
-- (another NPC's storage `requires`) is done. steps = {{{words}, text}, ...}. Returns a function(cid, msg) that
-- answers and returns true when the message was one of the steps.
function knowledgeChain(npcHandler, steps, storage, requires)
	local reached = {}
	return function(cid, msg)
		for i, step in ipairs(steps) do
			for _, word in ipairs(step[1]) do
				if msgcontains(msg, word) then
					npcHandler:say(step[2], cid)
					local before = reached[cid] or 0
					if before >= i - 1 then
						reached[cid] = math.max(before, i)
					end
					if i == #steps and reached[cid] == #steps
							and (requires == nil or getPlayerStorageValue(cid, requires) == 1) then
						setPlayerStorageValue(cid, storage, 1)
					end
					return true
				end
			end
		end
		return false
	end
end

-- Answers the first entry of `talk` ({{{words}, text}, ...}) one of whose words the message contains; true if one did.
function answerTalk(npcHandler, talk, cid, msg)
	for _, entry in ipairs(talk) do
		for _, word in ipairs(entry[1]) do
			if msgcontains(msg, word) then
				npcHandler:say(entry[2], cid)
				return true
			end
		end
	end
	return false
end

-- Travel NPCs: "Set the sails!" is spoken through the scheduler (selfSay), a teleport in the same call went first and
-- the passenger never saw the words. The trip starts a moment after them.
function teleportAfterWords(cid, destination)
	addEvent(function()
		if isPlayer(cid) then
			doTeleportThing(cid, destination, false)
			doSendMagicEffect(destination, CONST_ME_TELEPORT)
		end
	end, 300)
end

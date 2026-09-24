-- Quest chests (docs/reference-74/quests.md): every container or object on the map with action id 2000.
-- Its unique id is the player storage that marks it as looted (once per character). The reward is the
-- unique id itself when that is an item id (the usual real-map convention, e.g. uid 2384 = a rapier), and
-- otherwise what lies inside the chest on the map (copied, the chest itself keeps it for the next player).
-- A reward the player cannot carry stays: nothing is marked, they can come back.

local ITEM_ID_LIMIT = 10000   -- unique ids below this are item ids

-- Rewards the map does not carry (the chest is empty on Tibia74.otbm): unique id -> {{item id, count,
-- action id (keys), contents {{item id, count}, ...}}, ...}. Each entry names its quest and source (docs/reference-74/quests.md).
local REWARDS = {
	-- Bear Room Quest (Rookgaard): the third bear-room box, and the chest below the mud south of the big table.
	-- Real-map chest table (OTLand "Quest System for 7.4 Realots"): "12 arrows and 40 gp"; TibiaWiki Key 4601:
	-- copper key, "Bear Room Key".
	[52148] = {{2544, 12}, {2148, 40}},
	[20003] = {{2089, 1, 4601}},
	-- Present Box Quest (Rookgaard): the chest next to the Bear Room stone switch. TibiaWiki Present Quest
	-- (2006): "Backpack with Present Box, Jug, Plate, Cup" - the present is traded to Seymour for a legion helmet.
	[52149] = {{1988, 1, nil, {{1990}, {2014}, {2035}, {2013}}}},
	-- Captain Iglues Treasure Quest (Rookgaard, below the poison spider tower): the right chest of the two at
	-- 32038-32039,32121,13. TibiaWiki (current) and Tibiantis: 2 salmon; the left chest (not a quest chest)
	-- holds the stamped letter "Treasure of captain Iglue" and 12 salmon, refilled daily - as on our map.
	[52171] = {{2668, 2}},
}

local function describe(itemid, count)
	local info = getItemDescriptions(itemid) or {}
	if count > 1 then
		return count .. " " .. (info.plural ~= nil and info.plural ~= "" and info.plural or getItemName(itemid))
	end
	local article = (info.article ~= nil and info.article ~= "") and (info.article .. " ") or ""
	return article .. getItemName(itemid)
end

local function copyInto(container, source)
	for slot = getContainerSize(source.uid) - 1, 0, -1 do
		local inner = getContainerItem(source.uid, slot)
		if inner.itemid > 0 then
			local copy = doAddContainerItem(container, inner.itemid, math.max(inner.type, 1))
			if inner.actionid ~= nil and inner.actionid > 0 then
				doSetItemActionId(copy, inner.actionid)   -- quest keys open their door by action id
			end
			if isContainer(inner.uid) then
				copyInto(copy, inner)
			end
		end
	end
end

-- one reward: {itemid, count, source} (source = the map item to copy contents / action id from)
local function give(cid, reward)
	local uid = doPlayerAddItem(cid, reward.itemid, reward.count, false)
	if not uid or uid == 0 or uid == false then
		return nil
	end
	if reward.actionid ~= nil and reward.actionid > 0 then
		doSetItemActionId(uid, reward.actionid)           -- a key: its number is the door it opens
	end
	for _, inner in ipairs(reward.contents or {}) do    -- a container that comes filled (REWARDS)
		doAddContainerItem(uid, inner[1], inner[2] or 1)
	end
	if reward.source ~= nil then
		if reward.source.actionid ~= nil and reward.source.actionid > 0 then
			doSetItemActionId(uid, reward.source.actionid)
		end
		if isContainer(reward.source.uid) then
			copyInto(uid, reward.source)
		end
	end
	return uid
end

function onUse(cid, item, frompos, item2, topos)
	local storage = item.uid
	local name = getItemName(item.itemid)
	if getPlayerStorageValue(cid, storage) > 0 then
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "The " .. name .. " is empty.")
		return true
	end

	local rewards = {}
	if REWARDS[storage] ~= nil then
		for _, r in ipairs(REWARDS[storage]) do
			table.insert(rewards, {itemid = r[1], count = r[2] or 1, actionid = r[3], contents = r[4]})
		end
	elseif storage < ITEM_ID_LIMIT then
		rewards[1] = {itemid = storage, count = 1}
	elseif isContainer(item.uid) then
		for slot = getContainerSize(item.uid) - 1, 0, -1 do
			local inner = getContainerItem(item.uid, slot)
			if inner.itemid > 0 then
				table.insert(rewards, {itemid = inner.itemid, count = math.max(inner.type, 1), source = inner})
			end
		end
	end

	if #rewards == 0 then
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "The " .. name .. " is empty.")
		return true
	end

	-- all or nothing: a part given before one that does not fit is taken back, or the chest could be looted
	-- again and again for that part
	local given = {}
	for _, reward in ipairs(rewards) do
		local uid = give(cid, reward)
		if uid == nil then
			for _, g in ipairs(given) do
				doRemoveItem(g.uid, g.count)   -- only what was given: gold may have joined a stack they had
			end
			doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "You have found " .. describe(reward.itemid, reward.count)
				.. ", but you cannot carry it.")
			return true
		end
		table.insert(given, {uid = uid, count = reward.count})
	end
	for _, reward in ipairs(rewards) do
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "You have found " .. describe(reward.itemid, reward.count) .. ".")
	end
	setPlayerStorageValue(cid, storage, 1)
	return true
end

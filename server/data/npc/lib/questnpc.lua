-- What quest NPCs share (npc/lib/djinn.lua, npc/lib/postman.lua): speaking a long text line by line, and an NPC
-- built from a spec - its greeting (a word other than "hi" if it has one), its quest topics, its other answers, its shop.
-- Says lines one after the other, the way NPCs speak a long text ("..." at the end of each but the last).
-- force: say them although the NPC is not talking to the player (an answer to "hi").
function questSay(npcHandler, cid, lines, force)
	if type(lines) == "string" then
		lines = {lines}
	end
	local name = getCreatureName(cid)
	local delay = 0
	for i, line in ipairs(lines) do
		line = string.gsub(line, "|PLAYERNAME|", name)
		if i == 1 then
			npcHandler:say(line, cid)
		else
			npcHandler:say(line, cid, delay, force)
		end
		delay = delay + 1500 + string.len(line) * 30
	end
end

-- An NPC who talks by keywords and topics (npc/lib/djinn.lua, npc/lib/postman.lua). spec:
--   word      the greeting ("djanni'hah"; Rata'mari "piedpiper"); nil: "hi" like any NPC (Melchior)
--   greet     function(cid, say) -> the lines he greets with, or nil to not talk (he says why with say); none: the
--             NPC file's message_greet
--   hi        function(cid, say): a human says "hi" - no conversation
--   farewell, walkaway, busy (MESSAGE_PLACEDINQUEUE)
--   quest     function(cid, msg, state, say) -> true when it answered; state.topic is the open question (0 none)
--   talk      {{keyword, line, line...}, ...} - everything else he answers, first match (longest keywords first)
--   shop      function(shopModule) adds his wares; mayTrade function(cid) -> true, or says why not and returns false
--   anyone    function(cid, msg, say) -> true when it answered something said near him, talking to him or not
-- Returns npcHandler.
function questNpc(spec)
	local keywordHandler = KeywordHandler:new()
	local npcHandler = NpcHandler:new(keywordHandler)
	NpcSystem.parseParameters(npcHandler)
	local state = {topic = 0}

	function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid) end
	function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid) end
	function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg) end
	function onThink()						npcHandler:onThink() end

	local function say(cid, lines, force)
		questSay(npcHandler, cid, lines, force)
	end

	-- anything said near him, talking to him or not (a captain's "bring me to <town>"): true = answered
	if spec.anyone then
		npcHandler:setCallback(CALLBACK_CREATURE_SAY, function(cid, type, msg)
			return not spec.anyone(cid, string.lower(msg), say)
		end)
	end

	if spec.farewell then npcHandler:setMessage(MESSAGE_FAREWELL, spec.farewell) end
	if spec.walkaway then npcHandler:setMessage(MESSAGE_WALKAWAY, spec.walkaway) end
	if spec.busy then npcHandler:setMessage(MESSAGE_PLACEDINQUEUE, spec.busy) end

	npcHandler:setCallback(CALLBACK_GREET, function(cid)
		state.topic = 0
		if spec.greet == nil then                  -- the greeting of its NPC file
			return true
		end
		local lines = spec.greet(cid, say)
		if lines == nil then
			return false
		end
		if type(lines) == "string" then
			lines = {lines}
		end
		state.topic = 0
		npcHandler:setMessage(MESSAGE_GREET, lines[1])
		local delay = 1500 + string.len(lines[1]) * 30
		for i = 2, #lines do
			local line = string.gsub(lines[i], "|PLAYERNAME|", getCreatureName(cid))
			npcHandler:say(line, cid, delay)
			delay = delay + 1500 + string.len(line) * 30
		end
		return true
	end)

	-- a djinn's greeting is the word, not "hi"; "hi" gets spec.hi and no conversation
	local focus = FocusModule:new()
	if spec.word ~= nil then
		function focus:init(handler)
			self.npcHandler = handler
			handler.keywordHandler:addKeyword({spec.word, callback = FocusModule.messageMatcher}, FocusModule.onGreet,
				{module = self})
			for _, word in ipairs(FOCUS_FAREWELLWORDS) do
				handler.keywordHandler:addKeyword({word, callback = FocusModule.messageMatcher}, FocusModule.onFarewell,
					{module = self})
			end
			for _, word in ipairs(FOCUS_GREETWORDS) do
				handler.keywordHandler:addKeyword({word, callback = FocusModule.messageMatcher}, function(cid)
					if not handler:isFocused(cid) and handler:isInRange(cid) and spec.hi then
						spec.hi(cid, say)
					end
					return true
				end, {})
			end
		end
	end
	npcHandler:addModule(focus)

	if spec.shop then
		local shopModule = ShopModule:new()
		npcHandler:addModule(shopModule)
		shopModule.mayTrade = spec.mayTrade
		spec.shop(shopModule)
	end

	npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, function(cid, type, msg)
		if not npcHandler:isFocused(cid) then
			return false
		end
		msg = string.lower(msg)
		if spec.quest and spec.quest(cid, msg, state, say) then
			return true
		end
		state.topic = 0
		for _, entry in ipairs(spec.talk or {}) do
			if containsWord(msg, entry[1]) then
				say(cid, {unpack(entry, 2)})
				return true
			end
		end
		return false
	end)
	return npcHandler
end

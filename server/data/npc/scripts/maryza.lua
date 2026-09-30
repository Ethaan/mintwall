-- Maryza, the cook of the Jolly Axeman in Kazordoon. Food from her NPC file's shop; the dwarven cookbook for Bo'ques
-- (The Djinn War - Marid Faction, docs/reference-74/quests.md): TibiaWiki 2006 "A Cookbook (150 gp from Maryza in
-- Kazordoon)". She sells it again any time (decided with the user 2026-09-29; the current wiki: one per player).
-- Greeted by name ("hi maryza", current wiki - Jimbin serves in the same tavern). The other lines are the old script's.
local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

local COOKBOOK = 2347
local topic = 0

local poison = createConditionObject(CONDITION_POISON)
addDamageCondition(poison, 15, 2000, -1)

npcHandler:setMessage(MESSAGE_GREET, "Welcome to the Jolly Axeman, |PLAYERNAME|. Have a good time!")
npcHandler:setMessage(MESSAGE_PLACEDINQUEUE, "Shut up |PLAYERNAME|. Busy. You wait!")
npcHandler:setMessage(MESSAGE_WALKAWAY, "HEY! You lousy....!")
npcHandler:setMessage(MESSAGE_FAREWELL, "Yeah, bye")

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid) end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid) end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg) end
function onThink()						npcHandler:onThink() end

local KEYWORDS = {
	{"do you sell", "I can offer you some food if ye like."},
	{"do you have", "I can offer you some food if ye like."},
	{"excalibug", "Would slice a dragon or two for steaks if i'd get it."},
	{"ferumbras", "Heard that's what the humans call one of their boggiemen."},
	{"general", "A fine drinker and strategist. Wastes his skill with these idiots of the army. What a shame."},
	{"jimbin", "I am so proud of him. In drinking, he's second only to our mighty general."},
	{"tavern", "I'm the cook of the Jolly Axeman."},
	{"carlin", "Don't like it, has an elfish touch, ye know?"},
	{"rumors", "The boys of the Savage Axe at the bridge are running wild in these days."},
	{"thais", "Puny town for puny guys."},
	{"tibia", "We don't care much about outsiders anymore."},
	{"army", "We could better feed some dragons instead of these fools."},
	{"name", "I am Maryza Firehand, daughter of Earth, from the Molten Rock."},
	{"time", "To busy, ask my husband."},
	{"king", "Don't like these upper cave guys."},
	{"tark", "He loved my dragonsteaks. Heard he died by a cave in while fighting drags in the Plains of Havoc."},
	{"news", "The boys of the Savage Axe at the bridge are running wild in these days."},
	{"food", "I sell normal and brown bread, meat, ham, cookies, rolls, and cheese made of mushrooms."},
	{"job", "I'm the cook of the Jolly Axeman."},
	{"buy", "I can offer you some food if ye like."},
}

local function onGreet(cid)
	topic = 0
	return true
end

local function onMessage(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	msg = string.lower(msg)
	if topic == 1 and containsWord(msg, "yes") then
		topic = 0
		if doPlayerRemoveMoney(cid, 150) then
			doPlayerAddItem(cid, COOKBOOK, 1)
			npcHandler:say("Here you are. Happy cooking!", cid)
		else
			npcHandler:say("No gold, no sale, that's it.", cid)
		end
		return true
	end
	topic = 0
	if containsWord(msg, "cookbook") or containsWord(msg, "book") then
		topic = 1
		npcHandler:say("The cook book of the famous dwarfish kitchen. You're lucky. I have a few copies on sale. Do you like one for 150 gold?", cid)
		return true
	elseif containsWord(msg, "bloody mary") then
		doTargetCombatCondition(0, cid, poison, CONST_ME_NONE)
		doSendMagicEffect(getCreaturePosition(getNpcCid()), CONST_ME_POFF)
		npcHandler:say("YOU &/$#@!", cid)
		return true
	end
	for _, entry in ipairs(KEYWORDS) do
		if containsWord(msg, entry[1]) then
			npcHandler:say(entry[2], cid)
			return true
		end
	end
	return false
end

-- greeted by name: "hi maryza"
local focus = FocusModule:new()
function focus:init(handler)
	self.npcHandler = handler
	for _, word in ipairs({"hi maryza", "hello maryza", "hiho maryza"}) do
		handler.keywordHandler:addKeyword({word, callback = FocusModule.messageMatcher}, FocusModule.onGreet, {module = self})
	end
	for _, word in ipairs(FOCUS_FAREWELLWORDS) do
		handler.keywordHandler:addKeyword({word, callback = FocusModule.messageMatcher}, FocusModule.onFarewell, {module = self})
	end
end

npcHandler:setCallback(CALLBACK_GREET, onGreet)
npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, onMessage)
npcHandler:addModule(focus)

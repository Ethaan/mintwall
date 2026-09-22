-- Blind Orc (Rookgaard orc fortress). Speaks only orcish; a port of his old OTServ <interaction> XML,
-- which Avesta cannot run. charach = hi, futchi = bye, goshak = buy, mok = yes, burp = no.
local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

npcHandler:setMessage(MESSAGE_GREET, 'Ikem Charach maruk.')
npcHandler:setMessage(MESSAGE_FAREWELL, 'Futchi!')
npcHandler:setMessage(MESSAGE_WALKAWAY, 'Futchi!')
npcHandler:setMessage(MESSAGE_PLACEDINQUEUE, 'Ikem napak aluk.')

local offer = {}   -- cid -> ware the player asked about

local function greet(cid)
	npcHandler:onGreet(cid)
	return true
end

local function farewell(cid)
	if(npcHandler:isFocused(cid)) then
		offer[cid] = nil
		npcHandler:onFarewell(cid)
	end
	return true
end

local function say(text)
	return function(cid)
		if(not npcHandler:isFocused(cid)) then
			return false
		end
		npcHandler:say(text)
		return true
	end
end

local function ask(ware)
	return function(cid)
		if(not npcHandler:isFocused(cid)) then
			return false
		end
		offer[cid] = ware
		npcHandler:say(ware.question or 'Maruk goshak ta?')
		return true
	end
end

local function answer(yes)
	return function(cid)
		if(not npcHandler:isFocused(cid) or offer[cid] == nil) then
			return false
		end
		local ware = offer[cid]
		offer[cid] = nil
		if(not yes) then
			npcHandler:say('Buta maruk klamuk!')
		elseif(doPlayerBuyItem(cid, ware.item, ware.amount or 1, ware.price)) then
			npcHandler:say('Maruk rambo zambo!')
		else
			npcHandler:say('Maruk nixda!')
		end
		return true
	end
end

keywordHandler:addKeyword({'charach'}, greet)
keywordHandler:addKeyword({'futchi'}, farewell)
keywordHandler:addKeyword({'mok'}, answer(true))
keywordHandler:addKeyword({'burp'}, answer(false))

keywordHandler:addKeyword({'ikem', 'goshak'}, say('Ikem pashak porak, bata, dora. Ba goshak maruk?'))
keywordHandler:addKeyword({'goshak', 'porak'}, say('Ikem pashak charcha, burka, burka bata, hakhak. Ba goshak maruk?'))
keywordHandler:addKeyword({'goshak', 'bata'}, say('Ikem pashak aka bora, tulak bora, grofa. Ba goshak maruk?'))
keywordHandler:addKeyword({'goshak', 'dora'}, say('Ikem pashak donga. Ba goshak maruk?'))

local WARES = {
	{words = {'goshak', 'charcha'}, item = 2385, price = 25},                 -- sabre
	{words = {'goshak', 'burka'}, item = 2406, price = 30},                   -- short sword
	{words = {'goshak', 'burka', 'bata'}, item = 2376, price = 85},           -- sword
	{words = {'goshak', 'hakhak'}, item = 2388, price = 85},                  -- hatchet
	{words = {'goshak', 'bora'}, item = 2467, price = 25},                    -- leather armor
	{words = {'goshak', 'tulak', 'bora'}, item = 2484, price = 90},           -- studded armor
	{words = {'goshak', 'grofa'}, item = 2482, price = 60},                   -- studded helmet
	{words = {'goshak', 'batuk'}, item = 2456, price = 400, question = 'Ahhhh, maruk goshak batuk?'},  -- bow
	{words = {'goshak', 'pixo'}, item = 2544, amount = 10, price = 30,
		question = 'Maruk goshak tefar pixo ul batuk?'},                     -- 10 arrows
}
for _, ware in ipairs(WARES) do
	keywordHandler:addKeyword(ware.words, ask(ware))
end

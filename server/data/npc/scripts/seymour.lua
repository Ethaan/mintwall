local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Present Box Quest (docs/reference-74/quests.md): he trades the present box (item 1990, from the chest next
-- to the Bear Room switch) for a legion helmet: hi, box, yes. TibiaWiki Present Quest (2006): at level 6+ he
-- tells you he is looking for a suitable box. He also sells the Key to Adventure (key 4600, Katana Quest).
-- The conversation state is per player (it was one global: two players could answer each other's questions).
local BOX_LEVEL = 6
local talkState = {}

function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	local state = talkState[cid] or 0
	local level = getPlayerLevel(cid)

	if msgcontains(msg, 'dungeon') then
		if level < 3 then
			selfSay('There are some dungeons on this isle, but almost all of them are too dangerous for you at the moment.')
		else
			selfSay('There are some dungeons on this isle. You should be strong enough to explore them now, but make sure to take a rope with you.')
		end
	elseif msgcontains(msg, 'mission') or msgcontains(msg, 'quest') then
		if level < BOX_LEVEL then
			selfSay('You are pretty inexperienced. I think killing rats is a suitable challenge for you. For each fresh rat I will give you two shiny coins of gold.')
		else
			selfSay('Well I would like to send our king a little present, but I do not have a suitable box. If you find a nice box, please bring it to me.')
		end
	elseif msgcontains(msg, 'key') then
		selfSay('Do you want to buy the Key to Adventure for 5 gold coins?')
		state = 1
	elseif msgcontains(msg, 'yes') and state == 1 then
		if doPlayerRemoveMoney(cid, 5) then
			selfSay('Here you are.')
			local key = doPlayerAddItem(cid, 2088, 1)
			doSetItemActionId(key, 4600)
		else
			selfSay("You don't have enough money.")
		end
		state = 0
	elseif msgcontains(msg, 'no') and state == 1 then
		selfSay('As you wish.')
		state = 0
	elseif msgcontains(msg, 'box') then
		selfSay('Do you have a suitable present box for me?')
		state = 2
	elseif msgcontains(msg, 'yes') and state == 2 then
		if getPlayerItemCount(cid, 1990) >= 1 then
			selfSay('THANK YOU! Here is a helmet that will serve you well.')
			doPlayerRemoveItem(cid, 1990, 1)
			doPlayerAddItem(cid, 2480, 1)
		else
			selfSay("HEY! You don't have one! Stop playing tricks on fooling me or I will give you some extra work!")
		end
		state = 0
	elseif msgcontains(msg, 'bye') and state ~= 0 then
		selfSay('See you later.')
		state = 0
	end
	talkState[cid] = state
	return true
end

npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())
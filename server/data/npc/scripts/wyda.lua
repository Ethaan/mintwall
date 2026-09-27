local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Wyda, the witch in the Venore swamp. TibiaWiki 2006: "She needs a Blood Herb for her potions and is willing to offer
-- her Witchesbroom for it" (the Blood Herb Quest's end: "you can trade Wyda the Blood Herb for her Witchesbroom").
-- Lines: "Wyda/Transcripts" (the first of each pair - the second is a later world change). The offer and her answers
-- to it are not written down anywhere: ours, short.
local BLOOD_HERB, WITCHESBROOM = 2798, 2324

local TALK = {
	{{"job", "profession"}, "I am a witch. Didn't you notice?"},
	{{"gods"}, "I believe that nature itself is God."},
	{{"nature"}, "There are many swamp plants, mushrooms, and herbs around here."},
	{{"plants"}, "There are many kinds of swamp plants, some can be used for potions, some not."},
	{{"mushrooms"}, "Mushrooms taste good and are useful for potions."},
	{{"herbs"}, "The swamp is home to a wide variety of herbs, but the most famous is the blood herb."},
	{{"potion", "recipe", "secret"}, "The recipe of the potions is one of the witches' secrets!"},
	{{"magic", "spell"}, "The magic of the witches is one of our secrets!"},
	{{"key"}, "I keep my keys where they belong - in my pocket."},
	{{"help"}, "I can only help with knowledge. About what do you want me to tell you something?"},
	{{"king"}, "There are too many royals on this continent if you ask me..."},
	{{"tibianus"}, "Haha, that's a stupid name. Who's that?"},
	{{"eloise"}, "Eloise is Queen of Carlin. I don't care about royals much, as long as they don't try to tax me."},
	{{"name"}, "My name is Wyda, and what's yours?"},
	{{"quest"}, "A quest? Well, if you're so keen on doing me a favour... Why don't you try to find a blood herb?"},
	{{"time"}, "I think it is the fourth year after Queen Eloise's crowning, but I cannot tell you date or time."},
	{{"swamp"}, "Be careful of the swamp water, it's poisonous!"},
	{{"druid"}, "Druids are mostly fine people. I'm always happy when I meet one."},
	{{"sorcerer"}, "Sorcerers have forgotten about the root of all beings: nature."},
	{{"knight"}, "Knights succumb to the blindness of rage and the desire for violence and blood."},
	{{"paladin"}, "Paladins can use bows, but not brains."},
	{{"monsters", "creatures"}, "Many creatures live in, around, and beneath the swamp. Be careful!"},
	{{"bonelord"}, "Bonelords? Strange creatures that have mysterious magical abilities."},
	{{"broom"}, "What about it?"},
}

local talkState = {}

function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	local state = talkState[cid] or 0
	talkState[cid] = 0
	if msgcontains(msg, "blood herb") or msgcontains(msg, "bloodherb") then
		if getPlayerItemCount(cid, BLOOD_HERB) > 0 then
			npcHandler:say("A blood herb! Will you give it to me for my witchesbroom?", cid)
			talkState[cid] = 1
		else
			npcHandler:say("The blood herb is very rare. This plant would be very useful for me, but I don't know any accessible places to find it.", cid)
		end
	elseif state == 1 and msgcontains(msg, "yes") then
		if doPlayerRemoveItem(cid, BLOOD_HERB, 1) then
			doPlayerAddItem(cid, WITCHESBROOM, 1)
			npcHandler:say("Thank you! Here, take my witchesbroom.", cid)
		else
			npcHandler:say("You don't have a blood herb.", cid)
		end
	elseif state == 1 then
		npcHandler:say("Then keep it.", cid)
	else
		answerTalk(npcHandler, TALK, cid, msg)
	end
	return true
end

npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())

local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Lubo, the adventurer shop south of Mount Sternum. The Paradox Tower Quest's fourth mission (TibiaWiki spoiler, Dec
-- 2006): "crunor's cottage", "flower guys", "accident", "stable" - storage 6667, once Padreia's part (6666) is done;
-- A Prisoner asks for it. His shop is the XML's (module_shop). General lines: "Lubo/Transcripts".
local chain = knowledgeChain(npcHandler, {
	{{"crunor's cottage", "crunors cottage"}, "Ah yes, I remember my grandfather talking about that name. This house used to be an inn a long time ago. My family bought it from some of these flower guys."},
	{{"flower guys"}, "Oh, I mean druids of course. They sold the cottage to my family after some of them died in an accident or something like that."},
	{{"accident"}, "As far as I can remember the story, a pet escaped its stable behind the inn. It got somehow involved with powerfull magic at a ritual and was transformed in some way."},
	{{"stable"}, "My grandpa told me, in the old days there were some behind this cottage. Nothing big though, just small ones, for chicken or rabbits."},
}, 6667, 6666)

local TALK = {
	{{"name"}, "I am Lubo, the owner of this shop."},
	{{"job"}, "I am selling equipment for adventurers. If you need anything, let me know."},
	{{"maps"}, "Oh! I'm sorry, I sold the last one just five minutes ago."},
	{{"magic"}, "There's a lot of magic flowing in the mountain to the north."},
	{{"dog"}, "This is Ruffy my dog, please don't do him any harm."},
	{{"mountain"}, "It is said that once there lived a great magician on the top of this mountain."},
	{{"magician"}, "I don't remember his name, but it's said that his banner was the black eye."},
	{{"pet"}, "There are some strange stories about a magicians pet names. Ask Hoggle about it."},
	{{"finger"}, "Oh, you sure mean this old story about the mage Dago, who lost two fingers when he conjured a dragon."},
}

function creatureSayCallback(cid, type, msg)
	if not npcHandler:isFocused(cid) then
		return false
	end
	if not chain(cid, msg) then
		answerTalk(npcHandler, TALK, cid, msg)
	end
	return true
end

npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)
npcHandler:addModule(FocusModule:new())

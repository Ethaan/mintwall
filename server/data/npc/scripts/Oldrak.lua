local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Oldrak, keeper of the Nightmare Knights' temple in the Plains of Havoc. The Paradox Tower Quest's first mission
-- (TibiaWiki spoiler, Dec 2006): "hugo", "myth", "yenny the gentle" - storage 6664, which Zoltan's part needs.
-- Lines: the spoiler's (the 7.x wording) and "Oldrak/Transcripts". The hallowed axe trade tibiaot74 gave him is 8.x.
local chain = knowledgeChain(npcHandler, {
	{{"hugo"}, "Ah, the bane of the Plains of Havoc, the hidden beast, the unbeatable foe. I live here for years and I am sure it's only a myth."},
	{{"myth"}, "There are many tales about the fearsome Hugo. It's said it is an abomination, accidently created by Yenny the Gentle. It's halve demon, halve something else and people say it's still alive after dozens of years."},
	{{"yenny the gentle", "yenny"}, "Yenny, known as the Gentle, was one of most powerfull magicwielders in ancient times and known throughout the world for her mercy and kindness."},
}, 6664)

local TALK = {
	{{"name"}, "My name is Oldrak."},
	{{"job"}, "I guard this humble temple as a monument for the order of the nightmare knights."},
	{{"excalibug"}, "A weapon of myth and legend. It was lost in ancient times ... perhaps lost forever."},
	{{"gods"}, "They created Tibia and all life on it ... and unlife, too."},
	{{"nightmare knights"}, "This ancient order was created by a circle of wise humans who were called 'The Dreamers'. The order became extinct a long time ago."},
	{{"goshnar"}, "He was the greatest necromant who ever cursed our land with the steps of his feet. He was defeated by the Nightmare Knights."},
	{{"undead", "unlife"}, "Beware the foul undead!"},
}

local function creatureSayCallback(cid, type, msg)
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

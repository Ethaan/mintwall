dofile(getDataDir() .. 'npc/lib/spellteacher.lua')   -- teachSpells: the spells Tibiantis has him teach
local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Zoltan, Edron academy. The Paradox Tower Quest's second mission (TibiaWiki spoiler, Dec 2006): "yenny the gentle",
-- "crunors caress" - storage 6665, once Oldrak's part (6664) is done. General lines: "Zoltan/Transcripts".
local chain = knowledgeChain(npcHandler, {
	{{"yenny the gentle", "yenny"}, "Ah, Yenny the Gentle was one of the founders of the druid order called Crunors Caress, that has been originated in her hometown Carlin."},
	{{"crunors caress", "crunor's caress"}, "A quite undruidic order of druids they were, as far as we know. I have no more enlightening knowledge about them though."},
}, 6665, 6664)

local TALK = {
	{{"name"}, "My name is Zoltan."},
	{{"job"}, "I am a teacher of the most powerful spells in Tibia."},   -- 7.4: he still taught (Tibiantis); the 8.x line said "once"
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
teachSpells(keywordHandler, npcHandler, getNpcName())
npcHandler:addModule(FocusModule:new())

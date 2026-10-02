dofile(getDataDir() .. 'npc/lib/spellteacher.lua')   -- teachSpells: the spells Tibiantis has him teach
local keywordHandler = KeywordHandler:new()
local npcHandler = NpcHandler:new(keywordHandler)
NpcSystem.parseParameters(npcHandler)

function onCreatureAppear(cid)			npcHandler:onCreatureAppear(cid)			end
function onCreatureDisappear(cid)		npcHandler:onCreatureDisappear(cid)			end
function onCreatureSay(cid, type, msg)	npcHandler:onCreatureSay(cid, type, msg)	end
function onThink()						npcHandler:onThink()						end

-- Padreia, grand druid of Carlin. The Paradox Tower Quest's third mission (TibiaWiki spoiler, Dec 2006): "crunor's
-- caress", "footnote" - storage 6666, once Zoltan's part (6665) is done. General lines: "Padreia/Transcripts".
local chain = knowledgeChain(npcHandler, {
	{{"crunor's caress", "crunors caress"}, "Don't ask. They were only an unimportant footnote of history."},
	{{"footnote"}, "They thought they have to bring Crunor to the people, if people did not find to Crunor of their own. To achieve that they founded the inn Crunor's Cottage, south of Mt. Sternum."},
}, 6666, 6665)

local TALK = {
	{{"name"}, "I am Padreia, grand druid of our fine city."},
	{{"job"}, "I am the grand druid of Carlin. I am responsible for the guild, the fields, and our citizens' health."},
	{{"magic"}, "Every druid is able to learn the numerous spells of our craft."},
	{{"time"}, "Time is just a crystal pillar - the centre of creation and life."},
	{{"druids"}, "We are druids, preservers of life. Our magic is about defence, healing, and nature."},
	{{"sorcerers"}, "Sorcerers are destructive. Their power lies in destruction and pain."},
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

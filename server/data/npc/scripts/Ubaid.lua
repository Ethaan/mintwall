-- Ubaid, the gatekeeper of Mal'ouquah (The Djinn War - Efreet Faction, docs/reference-74/quests.md; npc/lib/djinn.lua).
-- TibiaWiki 2006 transcript: DJANNI'HAH "What? You know the word, player? ..."; "passage" "Only the mighty Efreet ...
-- Am I right?"; "no" "Of cour... Huh!? No!? ... Helping to fight the Marid?"; "yes" "So you pledge loyalty to king
-- Malor ... Yes?"; "yes" "Well then - welcome to Mal'ouquah. ...". The other lines are the old script's.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local TALK = {
	{"ashta'daramai", "The Marids' hideout, isn't it? I have never been there, but I am sure one day I will. That will be the day Ashta'daramai falls into our hands!"},
	{"ab'dendriel", "Isn't that the name of some petty human settlement?"},
	{"mal'ouquah", "This place is our home, and as long as I'm here no meddler will trespass!"},
	{"kazordoon", "Isn't that the name of some petty human settlement?"},
	{"ascension", "I think I've heard that term before. Has to do with that weirdo pharaoh, right?"},
	{"kha'labal", "I like the desert. Just ruins and sand. And no human scum to be seen. The Kha'labal is a foretaste of what the djinn will do to the whole of Tibia!"},
	{"fa'hradin", "The old wizard is dangerous, but he will get what he deserves sooner or later."},
	{"zathroth", "Zathroth is our father! Of course, the son always has a right to hate his father, right."},
	{"darashia", "A human settlement to the west? I have not been there yet, but when I do I'm sure I will be remembered."},
	{"kha'zeel", "This mountain range is our home. Too bad we have to share it with the Marid. That will change, though. And pretty soon, believe me."},
	{"baa'leal", "General Baa'leal is our commander-in-chief of all his minions. He is as tough as an ancient scarab's buttocks and as sly a sand weasel."},
	{"daraman", "How dare you utter that name in my presence, human. Don't strain my patience, worm! You may know the secret word, but... who knows... it is always possible that your head is torn off in some terrible accident."},
	{"pharaoh", "They say Ankrahmun is now ruled by a crazy pharaoh who wants to tell his whole people into drooling undead. That's humans. Sickos and weirdos the lot of them."},
	{"efreet", "The Efreet are the true djinn! Those namby-pamby milksops who call themselves the Marid and still follow Gabel, no longer deserve the honour to call themselves djinn."},
	{"scarab", "They make good pets if you know how to keep them. Did you know they just adore human flesh?"},
	{"venore", "Isn't that the name of some petty human settlement?"},
	{"carlin", "Isn't that the name of some petty human settlement?"},
	{"palace", "One day we will sack that place and burn it to the ground."},
	{"temple", "One day we will sack that place and burn it to the ground."},
	{"alesar", "I am not used to the sight of blueskins here in Mal'ouquah, and it does not make me too happy to see one. I am keeping an eye on this guy, and if I should ever find that he is playing games with us I will personally break his neck!"},
	{"ubaid", "That is my name. I don't like it when a human pronounces it."},
	{"malor", "Well, Malor is not officially king of all djinn yet, but now our beloved leader is back that is a mere formality."},
	{"djinn", "We are a race of rulers and dominators! Or at least we, the Efreet, are."},
	{"gabel", "I used to serve under Gabel, but he is no longer my king. If that wacky wimp should ever come here to Mal'ouquah I will personally... you know... turn him away. Yes!"},
	{"human", "You are an inferior race of feeble, scheming jerks. No offence."},
	{"tibia", "This world is ours by right, and we will take it."},
	{"edron", "Isn't that the name of some petty human settlement?"},
	{"thais", "Isn't that the name of some petty human settlement?"},
	{"uthun", "Are you drunk?"},
	{"name", "My name is Ubaid. Why do you want to know that, human? Hmm... suspicious."},
	{"king", "Well, Malor is not officially king of all djinn yet, but now our beloved leader is back that is a mere formality."},
	{"lamp", "I am not taking a nap! I am on duty!"},
	{"job", "Well, what do you think? I keep watch around here to make sure people like you don't enter."},
	{"rah", "Are you drunk?"},
	{"akh", "Are you drunk?"},
	{"war", "I don't know why I am stuck here! I should be at the front, killing Marid and humans. Well, perhaps I will kill you..."},
}

local SHOVE_OFF = "Of course. Then don't waste my time and shove off."

djinnNpc{
	word = "djanni'hah",
	farewell = "Hail King Malor! See you on the battlefield, human worm.",
	walkaway = "Hail King Malor! See you on the battlefield, human worm.",
	busy = "Oh no! More of you humans! I'm busy, |PLAYERNAME|, so you better hold your tongue until I have time for you.",
	greet = function(cid, say)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			say(cid, "Hmmm? Is this human |PLAYERNAME| trying to say something? I don't think so.", true)
			return nil
		elseif djinnProgress(cid, DJINN_EFREET) > 0 then
			return "Still alive, |PLAYERNAME|?"
		end
		return "What? You know the word, |PLAYERNAME|? All right then - I won't kill you. At least, not now."
	end,
	hi = function(cid, say)
		say(cid, "Shove off, little one! Humans are not welcome here, |PLAYERNAME|!", true)
	end,
	quest = function(cid, msg, state, say)
		if state.topic == 1 and containsWord(msg, "no") then
			state.topic = 2
			say(cid, {"Of cour... Huh!? No!? I can't believe it! ...", "You... you got some nerves... Hmm. ...",
				"Maybe we have some use for someone like you. Would you be interested in working for us. Helping to fight the Marid?"})
			return true
		elseif state.topic == 2 and containsWord(msg, "yes") then
			state.topic = 3
			say(cid, "So you pledge loyalty to king Malor and you are willing to never ever set foot on Marids' territory, unless you want to kill them? Yes?")
			return true
		elseif state.topic == 3 and containsWord(msg, "yes") then
			state.topic = 0
			setPlayerStorageValue(cid, DJINN_EFREET, EFREET_PLEDGED)
			say(cid, {"Well then - welcome to Mal'ouquah. ...", "Go now to general Baa'leal and don't forget to greet him correctly! ...",
				"And don't touch anything!"})
			return true
		elseif state.topic ~= 0 and (containsWord(msg, "yes") or containsWord(msg, "no")) then
			state.topic = 0
			say(cid, SHOVE_OFF)
			return true
		elseif containsWord(msg, "passage") or containsWord(msg, "pass") or containsWord(msg, "enter") or containsWord(msg, "join") then
			state.topic = 0
			if djinnFollower(cid) == DJINN_MARID then
				say(cid, "Who do you think you are? A Marid? Shove off, moron.")
			elseif djinnProgress(cid, DJINN_EFREET) > 0 then
				say(cid, "You already pledged loyalty to king Malor.")
			else
				state.topic = 1
				say(cid, {"Only the mighty Efreet, the true djinn of Tibia, may enter Mal'ouquah! ...",
					"All Marids and little worms like yourself should leave now or something bad may happen. Am I right?"})
			end
			return true
		end
		return false
	end,
	talk = TALK,
}

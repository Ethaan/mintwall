-- Malor, the Efreet's leader in Mal'ouquah (The Djinn War - Efreet Faction, docs/reference-74/quests.md;
-- npc/lib/djinn.lua). TibiaWiki 2006 transcripts: DJANNI'HAH "Greetings, human player. ..."; "mission" "I guess this
-- is the first time I entrust a human with a mission. ... Are you prepared to embark on this mission?"; "yes"
-- Fa'hradin's lamp from the Orc King into Gabel's chambers. Back: "mission" "Have you found Fa'hradin's lamp and
-- placed it in Malor's personal chambers?" (the current wiki: Gabel's - the 2006 text's slip); "yes" "Well well,
-- human. ... the permission to trade with my people". The other lines are the old script's.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local TALK = {
	{"ashta'daramai", "Ashta'daramai is the fortress of our sworn enemies, the oh so powerful Marid. The day will come when I see its smouldering walls collapse."},
	{"ab'dendriel", "I hear the humans have built impressive cities on the great continent. It looks like many things have changed while I was caught in that stupid lamp."},
	{"mal'ouquah", "Do you like this place? I have built Mal'ouquah as a home for those among my kind who did not fall for Daraman's sugar covered lies. From here I shall rule the world when the time has come."},
	{"fa'hradin", "Fa'hradin is Gabel's lieutenant. I have known him for a long time, and I have always respected him. ...", "Unfortunately he chose the wrong side when the time to chose sides came. I have not given up hope of winning him over for some reason, but if I meet him on the battlefield I will not hesitate to kill him myself."},
	{"kazordoon", "I hear the humans have built impressive cities on the great continent. It looks like many things have changed while I was caught in that stupid lamp."},
	{"ankrahmun", "Even though it always was a human settlement I have always had a soft spot for the place. I am even thinking about making it my capital once I have taken over the world."},
	{"ascension", "Ascension? That does ring a bell. Isn't that an element of the pharaoh's doctrines."},
	{"kha'labal", "Kha'labal. I do not like that desert. Looking at it brings up bad memories."},
	{"orc king", "Ah yes. My good old friend the foolish orc. He has rendered me a great service, you know? He released me from that accursed lamp! ...", "In return I have fulfilled three wishes for him, but somehow I can't help the feeling that he is not wonderfully happy about the way things have turned out."},
	{"melchior", "Melchior! Hah, that fool! Is he still alive? I never thought the old wretch would make it after I gave him my special treatment and sent him out into the Kha'labal. ...", "Amazing, really. It has often occurred to me how much humans resemble rats - they are just as hard to kill!"},
	{"baa'leal", "I suppose you have met Baa'leal already? The fact that you have survived that encounter shows that you are surprisingly strong for a human. ...", "I almost feel some respect for you... Well, almost."},
	{"zathroth", "Our father. He made us a race of masters, not of servants. We will live to fulfill his promise or die trying."},
	{"darashia", "Darashia is a very rich city. Once this war is won I will drop by at the Caliph's palace and pay my respects, if you know what I mean."},
	{"kha'zeel", "They say the Kha'zeel mountains have been made by gods. If that is true they must have left long ago, because I have lived here for eons, and I have never met one of them."},
	{"daraman", "Of all human liars and schemers he was the worst. This self-styled prophet single-handedly managed to disunite my race and to spark a bloody civil war. ...", "If somebody fulfilled a wish for me for a change I would bring him back to life and make him pay."},
	{"pharaoh", "I have heard that pompous pharaoh believes himself to be some sort of deity. That pathetic bonehead a god? Don't make me laugh!"},
	{"efreet", "We are djinn! The true djinn! Those who have not let themselves be fooled by the silver-tongued blathering of that perfidious snake called Daraman."},
	{"scarab", "Scarabs are ancient creatures, which is why I respect them. But I will never allow any of these critters to undermine the foundations of my fortress."},
	{"venore", "I hear the humans have built impressive cities on the great continent. It looks like many things have changed while I was caught in that stupid lamp."},
	{"carlin", "I hear the humans have built impressive cities on the great continent. It looks like many things have changed while I was caught in that stupid lamp."},
	{"djinn", "We are strong and proud. One day we will take our rightful place on the throne of creation, and your vulgar race will either serve us or perish. ...", "Nothing personal, human. It is a natural process. And you humans will find that the djinn can be just masters."},
	{"gabel", "That fool. He thought he'd got rid of me for good. But I'm back, and this time I will finish what I have begun. That weak-willed wimp has held on to power far too long."},
	{"marid", "The so-called Marid have forgotten what it is like to be djinn! They are weak!"},
	{"malor", "That is me. I was away for a long time, but now I am back with a vengeance."},
	{"human", "Your race is weak, but incurably treacherous. I will never forgive humanity the fact that it was one of your kind who spread the seed of dissent among the djinn."},
	{"tibia", "The world of Tibia is ours by right. I will not rest until we have conquered it."},
	{"edron", "I hear the humans have built impressive cities on the great continent. It looks like many things have changed while I was caught in that stupid lamp."},
	{"thais", "I hear the humans have built impressive cities on the great continent. It looks like many things have changed while I was caught in that stupid lamp."},
	{"uthun", "Another one of that loony pharaoh's bright ideas. Nothing but nonsense and balderdash."},
	{"name", "Is it true you don't know who I am? Well, then listen. My name is Malor. ...", "You should better memorise that name because you are bound to hear it more often in future."},
	{"king", "I may not have reached my goal yet, but neither has that accursed Gabel. As long as the Marid and Efreet are disunited neither of us can call himself the king of all djinn."},
	{"gods", "Are not the creators reflected in their creations? Look around! What do you see? There is nothing but cowardice and treachery in the world of humans. ...", "How low the gods must be who made them. I have no respect for them."},
	{"lamp", "We djinn use them to sleep."},
	{"job", "I am the true leader of all djinn - perhaps not by birth, but certainly by merit. One day all djinn will come to recognise that I alone deserve to be king."},
	{"rah", "Another one of that loony pharaoh's bright ideas. Nothing but nonsense and balderdash."},
	{"akh", "Another one of that loony pharaoh's bright ideas. Nothing but nonsense and balderdash."},
	{"war", "Gabel and Fa'hradin thought the war was over when they managed to trap me in that accursed lamp. But they have been a bit rash. After all those years I'm still here, and my thirst for revenge is stronger than ever!"},
}

djinnNpc{
	word = "djanni'hah",
	farewell = "Farewell, human. When I have taken my rightful place I shall remember those who served me well. Even if they are only humans.",
	walkaway = "Farewell, human.",
	busy = "It might have escaped your limited human perception, but I am already talking to somebody else.",
	greet = function(cid)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			return nil
		end
		return "Greetings, human |PLAYERNAME|. My patience with your kind is limited, so speak quickly and choose your words well."
	end,
	quest = function(cid, msg, state, say)
		local progress = djinnProgress(cid, DJINN_EFREET)
		if containsWord(msg, "permission") then
			state.topic = 0
			if progress >= EFREET_DONE then
				say(cid, "You are welcome to trade with Alesar and Yaman whenever you want to, |PLAYERNAME|!")
			else
				say(cid, "I have no reason to give you my permission to trade with Alesar or Yaman.")
			end
			return true
		elseif djinnFollower(cid) ~= DJINN_EFREET then
			return false
		elseif state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			if progress < EFREET_LAMP then
				setPlayerStorageValue(cid, DJINN_EFREET, EFREET_LAMP)
			end
			say(cid, {"Well, listen. We are trying to acquire the ultimate weapon to defeat Gabel: Fa'hradin's lamp! ...",
				"At the moment it is still in the possession of that good old friend of mine, the Orc King, who kindly released me from it. ...",
				"However, for some reason he is not as friendly as he used to be. You better watch out, human, because I don't think you will get the lamp without a fight. ...",
				"Once you have found the lamp you must enter Ashta'daramai again. Sneak into Gabel's personal chambers and exchange his sleeping lamp with Fa'hradin's lamp! ...",
				"If you succeed, the war could be over one night later!"})
			return true
		elseif state.topic == 1 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Your choice.")
			return true
		elseif state.topic == 2 and containsWord(msg, "yes") then
			state.topic = 0
			setPlayerStorageValue(cid, DJINN_EFREET, EFREET_DONE)
			say(cid, {"Well well, human. So you really have made it - you have smuggled the modified lamp into Gabel's bedroom! ...",
				"I never thought I would say this to a human, but I must confess I am impressed. ...",
				"Perhaps I have underestimated you and your kind after all. ...",
				"I guess I will take this as a lesson to keep in mind when I meet you on the battlefield. ...",
				"But that's in the future. For now, I will confine myself to give you the permission to trade with my people whenever you want to. ...",
				"Farewell, human!"})
			return true
		elseif state.topic == 2 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Just do it.")
			return true
		elseif containsWord(msg, "mission") or containsWord(msg, "work") then
			state.topic = 0
			if progress == EFREET_TEAR_GIVEN then
				state.topic = 1
				say(cid, {"I guess this is the first time I entrust a human with a mission. And such an important mission, too. But well, we live in hard times, and I am a bit short of adequate staff. ...",
					"Besides, Baa'leal told me you have distinguished yourself well in previous missions, so I think you might be the right person for the job. ...",
					"But think carefully, human, for this mission will bring you close to certain death. Are you prepared to embark on this mission?"})
			elseif progress == EFREET_LAMP then
				state.topic = 1
				say(cid, "You haven't finished your final mission yet. Shall I explain it again to you?")
			elseif progress == EFREET_LAMP_PLACED then
				state.topic = 2
				say(cid, "Have you found Fa'hradin's lamp and placed it in Gabel's personal chambers?")
			elseif progress >= EFREET_DONE then
				say(cid, "You are welcome to trade with Alesar and Yaman whenever you want to, |PLAYERNAME|!")
			else
				say(cid, {"So you would like to fight for us. Hmm. ...",
					"You show true courage, human, but I will not accept your offer at this point of time."})
			end
			return true
		end
		return false
	end,
	talk = TALK,
}

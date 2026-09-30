-- Fa'hradin, Gabel's counsellor in Ashta'daramai (The Djinn War - Marid Faction, docs/reference-74/quests.md;
-- npc/lib/djinn.lua). TibiaWiki 2006 transcripts: DJANNI'HAH "Aaaah... what have we here. ..."; "mission" "I have
-- heard some good things about you from Bo'ques. ... The password is PIEDPIPER. ..."; back: "mission" "Did you
-- already retrieve the spyreport?"; "yes" "You really have made it? ... Perhaps you should have a word with him
-- [Gabel], too." The other lines are the old script's.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local TALK = {
	{"fa'hradin lamp", "I hate to flatter myself, but that lamp was a masterpiece. Malor would have been imprisoned in it for the rest of his miserable life if it had not been for that nincompoop who calls himself an orc king. That foolish troglodyte!"},
	{"ashta'daramai", "That is what this place is called. It is not difficult to guess that that name was not my idea."},
	{"ab'dendriel", "I am not much of a traveller, but I would like to see the northern cities everbody is talking about. Perhaps one day I will do that. Oh, I will use some kind of magical disguise, of course."},
	{"fa'hradin", "Yes, that is me. It seems you have heard my name before."},
	{"kazordoon", "I am not much of a traveller, but I would like to see the northern cities everbody is talking about. Perhaps one day I will do that. Oh, I will use some kind of magical disguise, of course."},
	{"ankrahmun", "That is one of the oldest human settlements in the whole of Tibia. I understand it is currently ruled by the pharaoh - some sort of undead priest-king. I am sure that must be a charming fellow."},
	{"ascension", "A fundamental part of the pharaoh's cult. I have not studied it in any detail, though."},
	{"kha'labal", "The Kha'labal used to be a paradise. I remember it well. The fact that it is a barren desert today might give you an idea of the things that happened during the war."},
	{"rata'mari", "Ah yes. Have you seen him? One of my best works so far. Nobody will ever suspect he is in fact a transformed djinn. The only problem is I'm much better with transforming people into other forms than with transforming them back. Poor fellow."},
	{"zathroth", "He created our race, but we find it hard to love him. Sometimes I think that whole war has erupted because there is something like a design flaw in us djinns, an inconsistency in the way we are. ...", "I have never been able to put my finger on it, but it keeps me wondering..."},
	{"darashia", "Darashia is comparatively young. The local ruler managed to establish his own little caliphate thanks to the riches he accumulated. ...", "As long as he continues to control the eastern trade routes Darashia will continue to flourish."},
	{"baa'leal", "Oh, you just have to love that djinn. We have met on the battlefield on half a dozen occasions, and he lost each single one of these battles. ...", "To be sure, he is a great warrior, but he is also lousy general and a complete dunce. As long as he is Malor's commander-in-chief I think we're safe."},
	{"kha'zeel", "None of the mountains here has developed naturally. The whole range has been raised by using powerful magic, and a lot of this magic lingers to this very day. A great place to be a wizard, but a dangerous place to travel."},
	{"melchior", "Ah. I remember him. A trader, was he not? I haven't seen him for a long time."},
	{"daraman", "I have met him myself. He was a sharp thinker and a charismatic conversationalist. ...", "I suppose he never managed to convince me quite as thoroughly as he managed to convince Gabel, but I came to admire his amazing personal integrity. ...", "In the end I chose to follow his creed because I felt that we djinn lacked something, and I thought that perhaps Daraman had an answer."},
	{"efreet", "I have not be been able to figure out exactly why the Efreet have developed a different skin colour. ...", "This poses an interesting scientific problem, you know. Perhaps it is a magical effect, but I have a feeling that there are other forces at work here."},
	{"scarab", "An interesting species. Oh, they are as thick as two short planks, of course, but there is definitely something magic about them. ...", "I have not carried out many studies, however, because dissecting scarabs is a real hassle."},
	{"palace", "The pharaoh's palace in Ankrahmun is an impressive building. At least that is how I remember it to be. ...", "I suppose it is a little less cheerful these days, with all that undead riff-raff roaming its halls."},
	{"venore", "I am not much of a traveller, but I would like to see the northern cities everbody is talking about. Perhaps one day I will do that. Oh, I will use some kind of magical disguise, of course."},
	{"carlin", "I am not much of a traveller, but I would like to see the northern cities everbody is talking about. Perhaps one day I will do that. Oh, I will use some kind of magical disguise, of course."},
	{"alesar", "That name brings up bad memories. I never really liked him, but you just had to admire his skills at the forge. His desertion was a great loss for our cause."},
	{"human", "You are a curious species: Weak, yet strong. Stupid, yet clever. Evil, yet good. Fascinating, really. ...", "For thousands of years we regarded the northern continent as barbaric and wild. ...", "And all of sudden there are roads and pastures and mighty cities. The problem with us djinn is that we always underestimate other species, especially humans."},
	{"tibia", "Eons ago when I was still young I felt the world was a place of wonder and joy. Now all I see is a badly working system full of design flaws. ...", "Must have been the first world the gods have created. Who knows? Perhaps they have learnt from their mistakes, and they are creating a better world somewhere else?"},
	{"djinn", "Our race is in a deplorable state at the moment. However, it is interesting from a scientific point of view. I am really curious to see if the Efreet and the Marid are really going to develop into two completely different species..."},
	{"marid", "That is what we call ourselves. We like to think of ourselves as the true inheritors of the djinn legacy."},
	{"gabel", "He is our leader. He does have his mistakes, but then he always tries to do what he thinks is right, and I suppose that makes him a good leader."},
	{"malor", "That treacherous snake has been waiting for a chance to seize power for as long as I can remember. He and Gabel used to be as close as brothers, you know."},
	{"edron", "I am not much of a traveller, but I would like to see the northern cities everbody is talking about. Perhaps one day I will do that. Oh, I will use some kind of magical disguise, of course."},
	{"thais", "I am not much of a traveller, but I would like to see the northern cities everbody is talking about. Perhaps one day I will do that. Oh, I will use some kind of magical disguise, of course."},
	{"uthun", "Another cornerstone of the undead pharaoh's theological theories. I do not know much more about it, I'm afraid."},
	{"lamp", "Ah yes. We djinn sleep in lamps. We have a natural ability to dematerialise, you see."},
	{"name", "I am known as Fa'hradin."},
	{"king", "Djinns do not have kings. Gabel has long abdicated the title because of his convictions, and Malor... Well, I suppose he would not refuse to take the crown, but I doubt he will ever get a chance to do so."},
	{"war", "For a long time it seemed that the war was over for good. But now that Malor is free again he will surely kindle the flame of war again. ...", "Damn that foolish orc. If I manage to get hold of him he will be turned into something much worse than a slime."},
	{"job", "Well, you could say I am the wizard of the Marid. Of course, I know that all djinn are magical creatures. But let us put it this way: I am slightly better at wielding magic then your average djinn in the street."},
	{"rah", "Another cornerstone of the undead pharaoh's theological theories. I do not know much more about it, I'm afraid."},
	{"akh", "Another cornerstone of the undead pharaoh's theological theories. I do not know much more about it, I'm afraid."},
}

djinnNpc{
	word = "djanni'hah",
	farewell = "Farewell, human. I will always remember you. Unless I forget you, of course.",
	walkaway = "Farewell, human.",
	busy = "Wait human. I'll take care of you in a minute, |PLAYERNAME|.",
	greet = function(cid)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			return nil
		end
		return "Aaaah... what have we here. A human - interesting. And such an ugly specimen, too... All right, human |PLAYERNAME|. How can I help you?"
	end,
	quest = function(cid, msg, state, say)
		local progress = djinnProgress(cid, DJINN_MARID)
		if containsWord(msg, "mal'ouquah") then
			state.topic = 0
			if djinnFollower(cid) == DJINN_MARID and progress >= MARID_SPY then
				say(cid, "Mal'ouquah is Malor's fortress which lies to the south. Of course you cannot enter it through the front door. But there's also an unguarded back door in the north-west corner of the fortress...")
			else
				say(cid, "Mal'ouquah is Malor's fortress which lies to the south. I know it well even though I have never been there myself. Insider information, you know.")
			end
			return true
		elseif djinnFollower(cid) ~= DJINN_MARID then
			return false
		elseif state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			if progress == MARID_REPORT and doPlayerRemoveItem(cid, SPY_REPORT, 1) then
				setPlayerStorageValue(cid, DJINN_MARID, MARID_REPORT_GIVEN)
				say(cid, {"You really have made it? You have the report? How come you did not get slaughtered? I must say I'm impressed. Your race will never cease to surprise me. ...",
					"Well, let's see. ...",
					"I think I need to talk to Gabel about this. I am sure he will know what to do. Perhaps you should have a word with him, too."})
			else
				say(cid, {"Don't waste any more time. We need the spyreport of our man in Mal'ouquah as soon as possible! ...",
					"Also don't forget the password to contact our man: PIEDPIPER!"})
			end
			return true
		elseif state.topic == 1 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, {"Don't waste any more time. We need the spyreport of our man in Mal'ouquah as soon as possible! ...",
				"Also don't forget the password to contact our man: PIEDPIPER!"})
			return true
		elseif containsWord(msg, "mission") or containsWord(msg, "work") or containsWord(msg, "report") or containsWord(msg, "spyreport") then
			state.topic = 0
			if progress == MARID_BOOK_GIVEN then
				setPlayerStorageValue(cid, DJINN_MARID, MARID_SPY)
				say(cid, {"I have heard some good things about you from Bo'ques. But I don't know. ...",
					"Well, all right. I do have a job for you. ...",
					"In order to stay informed about our enemy's doings, we have managed to plant a spy in Mal'ouquah. ...",
					"He has kept the Efreet and Malor under surveillance for quite some time. ...",
					"But unfortunately, I have lost contact with him months ago. ...",
					"I do not fear for his safety because his cover is foolproof, but I cannot contact him either. This is where you come in. ...",
					"I need you to infiltrate Mal'ouqhah, contact our man there and get his latest spyreport. The password is PIEDPIPER. Remember it well! ...",
					"I do not have to add that this is a dangerous mission, do I? If you are discovered expect to be attacked! So good luck, human!"})
			elseif progress >= MARID_SPY and progress <= MARID_REPORT then
				state.topic = 1
				say(cid, "Did you already retrieve the spyreport?")
			elseif progress >= MARID_REPORT_GIVEN then
				say(cid, "Did you already talk to Gabel about the report? I think he will have further instructions for you.")
			else
				say(cid, "Looking for work, are you? Well, it's very tempting, you know, but I'm afraid we do not really employ beginners. Perhaps our cook could need a helping hand in the kitchen.")
			end
			return true
		end
		return false
	end,
	talk = TALK,
}

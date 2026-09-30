-- Rata'mari, the Marid's spy in Mal'ouquah - a djinn turned into a rat (The Djinn War - Marid Faction,
-- docs/reference-74/quests.md; npc/lib/djinn.lua). TibiaWiki 2006 transcript: "Say the password PIEDPIPER instead of
-- 'hi'": "Meep? I mean - hello! ..."; "spy report" "You have come for the report? Great! ... I need some cheese! ...
-- Meep!"; again: "spy report" "Ok, have you brought me the cheese, I've asked for?"; "yes" "Meep! Meep! Great! Here is
-- the spyreport for you!". He talks only to those Fa'hradin sent (the password). The other lines are the old script's.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local TALK = {
	{"ashta'daramai", "I miss the place. I really feel homesick, you know? ...", "It makes my mouth water just to think of all the delicious cheese Bo'ques is hiding in his private larder."},
	{"ab'dendriel", "I have heard lots about the human cities to the north. Perhaps I will be sent there one day. That would be a lovely change."},
	{"mal'ouquah", "I hate this place. It is cold and damp! And the local rats are real snobs!"},
	{"rata'mari", "Shh! The walls have ears, you know!?"},
	{"fa'hradin", "That damn dabbler! 'I am going to disguise you', he said. 'Nobody will ever recognise you', he said! Now look at me! That botching fool! And I can't even bite his ankles!"},
	{"kazordoon", "I have heard lots about the human cities to the north. Perhaps I will be sent there one day. That would be a lovely change."},
	{"ankrahmun", "That is the one place where I would hate to work even more. My sources there have told me the city is now controlled by some loony who thinks he is a god or something."},
	{"ascension", "I am not much into religion, but from what I know this is an important part of that foolish pharaoh's creed."},
	{"kha'labal", "The Kha'labal is a huge desert to the east. It is a cruel, inhospitable land. Not even a rat could survive there very long."},
	{"baa'leal", "Baa'leal is Malor's lieutenant. He is fiercely loyal to his boss, and that is one of the main reasons why no Efreet has ever dared challenge Malor's authority. If it hadn't been for him a new leader would have come up in Malor's absence. ...", "I guess that is why despite all of his shortcomings he still has Malor's trust and support. He is not the brightest djinn under the sun, you know."},
	{"password", "'Pied Piper'. Hilarious. Fa'Hradin has a very strange sense of humour."},
	{"zathroth", "Zathroth was the creator of our race. Which doesn't mean we like him. But too be honest, I don't think this is the time and place to discuss religious matters."},
	{"darashia", "I have heard nice things about that city. I wish I had an assignment there rather than in this god-forsaken place."},
	{"kha'zeel", "Gosh, these mountains! Can you imagine what they look like to somebody who is moving three inches above the floor? They are so... massive!"},
	{"melchior", "Hm. No - doesn't ring a bell."},
	{"daraman", "Daraman? Well, he was a great prophet, but... look, this is not a good point of time to discuss philosophy, ok?"},
	{"pharaoh", "They say the new pharaoh is completely out of his mind. Rumour has it that he became an undead on his own free will! I think that says it all."},
	{"alesar", "His defection was a serious blow to our cause. Both Gabel and Fa'hradin are more concerned about it than they dare admit. ...", "Alesar is the most gifted smith the djinn race has ever produced, and now he works for the enemy. I am not entirely sure why he defected, but I am convinced it had nothing to do with money. ...", "Alesar has been a devout follower of Daraman for as long as I can remember, and he thought little of worldly possessions. In fact, from what I've seen Malor and Baa'leal were quite as astonished about it all as Gabel and Fa'hradin. ...", "All I know is that Alesar used to be a kind, helpful djinn. Then one day he disappeared. When he returned he had changed. He had become taciturn and bitter. And all of a sudden he hated humans. All of them. ...", "I think he suffered a deep spiritual crisis. Whatever caused this crisis is anyone's guess."},
	{"efreet", "After many months of careful study I have come to the conclusion the efreet are much more different from us Marid then I thought! Their skin is green, for a start!"},
	{"scarab", "A scarab? What? Where? Hey, don't give me shock like that! Did you know they eat rats?!"},
	{"venore", "I have heard lots about the human cities to the north. Perhaps I will be sent there one day. That would be a lovely change."},
	{"carlin", "I have heard lots about the human cities to the north. Perhaps I will be sent there one day. That would be a lovely change."},
	{"palace", "The palace in Ankrahmun used to be renowned for its splendour and its hospitable atmosphere. Now I suppose rats are the only living creatures that are still tolerated in this place. Hang on... I hope this does not give Gabel ideas."},
	{"trade", "Trade? Look at me! Do I look as if I had any pockets to stash stuff in?"},
	{"human", "So Fa'hradin turned you into a human? That's really hard, buddy. Rats, humans... what comes next?"},
	{"djinn", "I used to be one, too. That was before Fa'hradin had the bright idea to turn me into a flea-ridden rodent."},
	{"marid", "I haven't seen my brothers for a long time!"},
	{"gabel", "Gabel is our undisputed leader, even though he is too modest to brag with it. Even though Fa'hradin coordinates all military operations it is always Gabel who has the final say."},
	{"malor", "I have found out all kinds of things about him! He is left-handed, his favourite dish is hyena chop roasted in sandwasp honey marinade, and he has this weird habit of scratching his right ear whenever he is angry - which happens quite often, I might add."},
	{"tibia", "A nice world. I think I prefer it to all others. Not that I have seen any others, of course."},
	{"edron", "I have heard lots about the human cities to the north. Perhaps I will be sent there one day. That would be a lovely change."},
	{"thais", "I have heard lots about the human cities to the north. Perhaps I will be sent there one day. That would be a lovely change."},
	{"uthun", "Yes... rings a bell. Has to do with Ankrahmun's pharaoh, hasn't it?"},
	{"name", "I have many names and faces. But I suppose you can call me Rata'mari."},
	{"king", "No more kings for us! We are a democratic people now! Well, sort of."},
	{"lamp", "Oh to sleep in warm, comfy lamp! It's been such a long time."},
	{"rat", "Your power of observation is stunning. Yes, I'm a rat."},
	{"job", "I'm a spy. Now guess what I've come here for!"},
	{"rah", "Yes... rings a bell. Has to do with Ankrahmun's pharaoh, hasn't it?"},
	{"akh", "Yes... rings a bell. Has to do with Ankrahmun's pharaoh, hasn't it?"},
}

djinnNpc{
	word = "piedpiper",
	farewell = "Remember - this conversation never took place!",
	walkaway = "Meep!",
	busy = "And now there's more of you? Great! More attention is just what I need. Step back and wait, |PLAYERNAME|!",
	greet = function(cid)
		if djinnFollower(cid) ~= DJINN_MARID or djinnProgress(cid, DJINN_MARID) < MARID_SPY then
			return nil
		end
		return "Meep? I mean - hello! Sorry, |PLAYERNAME|... Being a rat has kind of grown on me."
	end,
	quest = function(cid, msg, state, say)
		local progress = djinnProgress(cid, DJINN_MARID)
		if state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			if doPlayerRemoveItem(cid, CHEESE, 1) then
				setPlayerStorageValue(cid, DJINN_MARID, MARID_REPORT)
				doPlayerAddItem(cid, SPY_REPORT, 1)
				say(cid, "Meep! Meep! Great! Here is the spyreport for you!")
			else
				say(cid, "No cheese - no report.")
			end
			return true
		elseif state.topic == 1 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "No cheese - no report.")
			return true
		elseif containsWord(msg, "spy report") or containsWord(msg, "report") or containsWord(msg, "spyreport") or containsWord(msg, "cheese") then
			state.topic = 0
			if progress == MARID_SPY then
				setPlayerStorageValue(cid, DJINN_MARID, MARID_CHEESE)
				say(cid, {"You have come for the report? Great! I have been working hard on it during the last months. And nobody came to pick it up. I thought everybody had forgotten about me! ...",
					"Do you have any idea how difficult it is to hold a pen when you have claws instead of hands? ...",
					"But - you know - now I have worked so hard on this report I somehow don't want to part with it. At least not without some decent payment. ...",
					"All right - listen - I know Fa'hradin would not approve of this, but I can't help it. I need some cheese! I need it now! ...",
					"And I will not give the report to you until you get me some! Meep!"})
			elseif progress == MARID_CHEESE then
				state.topic = 1
				say(cid, "Ok, have you brought me the cheese, I've asked for?")
			else
				say(cid, "I already gave you the report. I'm not going to write another one.")
			end
			return true
		elseif containsWord(msg, "piedpiper") then
			state.topic = 0
			say(cid, "'Pied Piper'. Hilarious. Fa'Hradin has a very strange sense of humour.")
			return true
		end
		return false
	end,
	talk = TALK,
}

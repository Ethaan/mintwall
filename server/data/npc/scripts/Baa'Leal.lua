-- General Baa'leal in Mal'ouquah (The Djinn War - Efreet Faction, docs/reference-74/quests.md; npc/lib/djinn.lua).
-- TibiaWiki 2006 transcripts: DJANNI'HAH "You know the code human! ..."; "mission" "Each mission and operation ...
-- Are you interested, human?"; "yes" the supply thief in Carlin. Back: "mission" "Did you find the thief of our
-- supplies?"; "yes" "Finally! What is his name then?"; "partos" "You found the thief! ... Here - take this as a
-- reward" (600 gold, quests.md) "... go to Alesar"; "hail malor" "Hail to our great leader!". "hi" burns (the old
-- script's; Melchior: an Efreet "will kill you outright"). The other lines are the old script's.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local TALK = {
	{"ashta'daramai", "Ashta'daramai is the enemy's base of operations. I am looking forward to the moment when we raise our flag there!"},
	{"ab'dendriel", "They say the humans have built some big cities over there. I am looking forward to see them burn."},
	{"mal'ouquah", "At the moment Mal'ouquah is our headquarter. However, I am already working on a cunning plan to move our base of operations deep into the enemy's territory."},
	{"ankrahmun", "That old city has some impressive defensive structures. But I swear I will bring it down one day... I have a cunning plan already! ...", "I am thinking of a huge wooden camel."},
	{"kazordoon", "They say the humans have built some big cities over there. I am looking forward to see them burn."},
	{"ascension", "Apparently, ascension is what the followers of the pharaoh are after. No idea what exactly that is, though."},
	{"kha'labal", "Kha'labal? Yes, it was me who devastated it. Couldn't leave it to the enemy, you see? We had to destroy it in order to save it!"},
	{"fa'hradin", "He is Gabel's lieutenant and confidant. He is a powerful wizard, one has to admit that - and that's the only reason he is still alive. Without all his magical mumbo jumbo we would have long since won this war."},
	{"darashia", "The humans living in the northern deserts used to be nomads. Even though they are just humans they used to be respectable fighters. ...", "However, now they are living in this city they have grown fat and decadent. They will be easy prey."},
	{"baa'leal", "That is GENERAL Baa'leal for you, human."},
	{"zathroth", "I understand he created us. Must have been a great general."},
	{"kha'zeel", "It was an excellent idea to build our headquarter in the mountains of kha'zeel. Easy to defend, you know. Too bad the enemy had the same idea."},
	{"melchior", "Melchior! I remember that greedy little civilian. I would have court-martialled him, but I suppose it is just as well the way it is."},
	{"daraman", "Damn that liberal peacenik, that treacherous mealy-mouthed double-faced good-for-nothing surrender monkey! ...", "He has infected this proud people's minds with his peace-for-all blabber."},
	{"general", "I'm general Baa'leal. What do you want in Mal'ouquah?"},
	{"pharaoh", "Ankrahmun's pharaoh apparently believes himself to be some sort of god. Ah well. A solid blow with my scimitar will bring him back to earth soon enough!"},
	{"efreet", "We are the true djinn! We do not live in denial of our true nature like those damn liberals, the Marid."},
	{"scarab", "Impressive animals. I have this idea of training them as battle steeds. Imagine this: Djinns mounted on scarabs! With a battalion of those I would crush the enemy in the blink of an eye!"},
	{"venore", "They say the humans have built some big cities over there. I am looking forward to see them burn."},
	{"carlin", "They say the humans have built some big cities over there. I am looking forward to see them burn."},
	{"palace", "I suppose the palace is where the pharaoh resides. I have a distinct feeling I shall see it burn rather soon."},
	{"alesar", "Ah yes, Alesar! Excellent smith, that man!"},
	{"gabel", "He is weak. Much too weak to be our leader."},
	{"djinn", "We are a race of warriors! We Efreets are destined to rule and to conquer."},
	{"marid", "Nothing but a bunch of mealy-mouthed, mollycoddled wimps and milksops the lot of them. They may be superior in numbers, but we will win anyway because of our superior strategic thinking."},
	{"malor", "Hail to our great leader."},
	{"human", "No offence, but your race is weak. You lack both the physical strength and the true warrior spirit. And worst of all, you have no strategic thinking."},
	{"tibia", "It is our mission to achieve total and decisive dominion of this world within two years. Well perhaps ... three. Always be realistic, that's what I say."},
	{"edron", "They say the humans have built some big cities over there. I am looking forward to see them burn."},
	{"thais", "They say the humans have built some big cities over there. I am looking forward to see them burn."},
	{"uthun", "Spare me that pseudo-theological hogwash."},
	{"udla", "Yes. The United Djinn Liberation Army. ...", "The title has been given to our valiant armed forces in order to stress both the revolutionary focus of our agenda and the universalist nature of our political approach. ...", "Hence I'm responsible for all operations in the enemy's territory."},
	{"name", "I'm general Baa'leal. What do you want in Mal'ouquah?"},
	{"king", "The UDLA does not serve a king because there isn't any. Of course, that is bound to change."},
	{"lamp", "We sleep in those lamps. I like them - they are small and functional. We do not need cozy beds and fluffy duvets like decadent humans."},
	{"job", "I am commander-in-chief of the armed forces of the UDLA, all branches of service. ...", "Hence I'm responsible for all operations in the enemy's territory."},
	{"war", "War is the father of things, and I live and breathe it. Ok, it's a tad bit silly that we are forced to fight against our own kind, but as a good soldier I will do my duty! <salutes> ...", "And if I hear anybody talking about 'peace' he will be court-martialled and summarily executed! Or vice versa!"},
	{"rah", "Spare me that pseudo-theological hogwash."},
	{"akh", "Spare me that pseudo-theological hogwash."},
}

local fire = createConditionObject(CONDITION_FIRE)
addDamageCondition(fire, 150, 4000, -10)

djinnNpc{
	word = "djanni'hah",
	farewell = "Stand down, soldier!",
	walkaway = "Hail Malor!",
	busy = "Can't you see I am already talking to somebody here, |PLAYERNAME|? You civilians don't understand the concept of discipline at all, do you!",
	greet = function(cid, say)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			say(cid, "A human! TAKE THIS!", true)
			doTargetCombatCondition(0, cid, fire, CONST_ME_NONE)
			return nil
		elseif djinnProgress(cid, DJINN_EFREET) >= EFREET_THIEF then
			return "You are still alive, |PLAYERNAME|? Well, what do you want?"
		end
		return "You know the code human! Very well then... What do you want, |PLAYERNAME|?"
	end,
	hi = function(cid, say)
		say(cid, "A human! TAKE THIS!", true)
		doTargetCombatCondition(0, cid, fire, CONST_ME_NONE)
	end,
	quest = function(cid, msg, state, say)
		if djinnFollower(cid) ~= DJINN_EFREET then
			return false
		end
		local progress = djinnProgress(cid, DJINN_EFREET)
		if state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			setPlayerStorageValue(cid, DJINN_EFREET, EFREET_THIEF)
			say(cid, {"Well ... All right. You may only be a human, but you do seem to have the right spirit. ...",
				"Listen! Since our base of operations is set in this isolated spot we depend on supplies from outside. These supplies are crucial for us to win the war. ...",
				"Unfortunately, it has happened that some of our supplies have disappeared on their way to this fortress. At first we thought it was the Marid, but intelligence reports suggest a different explanation. ...",
				"We now believe that a human was behind the theft! ...",
				"His identity is still unknown but we have been told that the thief fled to the human settlement called Carlin. I want you to find him and report back to me. Nobody messes with the Efreet and lives to tell the tale! ...",
				"Now go! Travel to the northern city Carlin! Keep your eyes open and look around for something that might give you a clue!"})
			return true
		elseif state.topic == 2 and containsWord(msg, "yes") then
			if progress == EFREET_PARTOS then
				state.topic = 3
				say(cid, "Finally! What is his name then?")
			else
				state.topic = 0
				say(cid, "Hmmm... I don't think so. Return to Carlin and continue your search.")
			end
			return true
		elseif state.topic == 2 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Then go to Carlin and search for him! Look for something that might give you a clue!")
			return true
		elseif state.topic == 3 then
			state.topic = 0
			if containsWord(msg, "partos") then
				setPlayerStorageValue(cid, DJINN_EFREET, EFREET_PAID)
				doPlayerAddMoney(cid, 600)
				say(cid, {"You found the thief! Excellent work, soldier! You are doing well - for a human, that is. Here - take this as a reward. ...",
					"Since you have proven to be a capable soldier, we have another mission for you. ...",
					"If you are interested go to Alesar and ask him about it."})
			else
				say(cid, "Hmmm... I don't think so. Return to Carlin and continue your search.")
			end
			return true
		elseif containsWord(msg, "mission") or containsWord(msg, "work") or containsWord(msg, "operation") or containsWord(msg, "thief") then
			if progress == EFREET_PLEDGED then
				state.topic = 1
				say(cid, {"Each mission and operation is a crucial step towards our victory! ...", "Now that we speak of it ...",
					"Since you are no djinn, there is something you could help us with. Are you interested, human?"})
			elseif progress == EFREET_THIEF or progress == EFREET_PARTOS then
				state.topic = 2
				say(cid, "Did you find the thief of our supplies?")
			else
				state.topic = 0
				say(cid, "Did you already talk to Alesar? He has another mission for you.")
			end
			return true
		elseif containsWord(msg, "hail malor") then
			state.topic = 0
			say(cid, "Hail to our great leader!")
			return true
		end
		return false
	end,
	talk = TALK,
}

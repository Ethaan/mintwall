-- Kevin Postner, the Postmaster General (The Postman Missions Quest, docs/reference-74/quests.md; npc/lib/postman.lua).
-- Every line is the TibiaWiki 2006 transcript's (pre-8.0 spoiler); "mission" moves the quest on, "advancement" after
-- every second mission. The old port kept its topic in a global every NPC shares (its step 7 could reset the quest)
-- and could not be finished (nothing counted the passages, no present, bag or letter).
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

local JOIN = {
	"Hm, I might consider your proposal, but first you will have to prove your worth by doing some tasks for us. Are you willing to do that?",
	"Excellent! Your first task will be quite simple. But you should better write my instructions down anyways. You can read and write?",
	"So listen, you will check certain tours our members have to take to see if there is some trouble. First travel with Captain Bluebear's ship from Thais to Carlin, understood?",
	"Excellent! Once you have done that you will travel with Uzon to Edron. You will find him in the Femor Hills. Understood?",
	"Fine, fine! Next, travel with Captain Seahorse to the city of Venore. Understood?",
	"Good! Finally, find the technomancer Brodrosch and travel with him to the Isle of Cormaya. After this passage report back to me here. Understood?",
}
local TOPIC_JOIN, TOPIC_NEXT, TOPIC_BONE, TOPIC_ADVANCE, TOPIC_POSTHORN, TOPIC_NOODLES = 1, 20, 21, 22, 23, 24

local function bones(cid)
	return getPlayerItemCount(cid, BONE) + getPlayerItemCount(cid, BIG_BONE)
end

local function takeBone(cid)
	return doPlayerRemoveItem(cid, BONE, 1) or doPlayerRemoveItem(cid, BIG_BONE, 1)
end

-- "mission" after a finished one: another assignment? (yes: accept)
local function offer(cid, state, say, progress)
	state.topic = TOPIC_NEXT
	if progress == POSTMAN_ROUTES then
		say(cid, "So you have finally made it! I did not think that you would have it in you ... However: are you ready for another assignment?")
	elseif progress == POSTMAN_FOLDA_FIXED then
		say(cid, "Excellent, you got it fixed! This will teach this mailbox a lesson indeed! Are you interested in another assignment?")
	elseif progress == POSTMAN_BILL_DELIVERED then
		say(cid, "You truly got him? Quite impressive. You are a very promising candidate! I think I have another mission for you. Are you interested?")
	elseif progress == POSTMAN_RANK_POSTMAN then
		say(cid, "You have made it! We have enough bones for the fund! You remind me of myself when I was young! Interested in another mission?")
	elseif progress == POSTMAN_PRESENT_GIVEN then
		say(cid, "Splendid, I knew we could trust you. I would like to ask for your help in another matter. Are you interested?")
	elseif progress == POSTMAN_RANK_GRAND then
		say(cid, "Excellent! Another job well done! Would you accept another mission?")
	elseif progress == POSTMAN_MEASURED then
		say(cid, "Once more you have impressed me! Are you willing to do another job?")
	elseif progress == POSTMAN_RANK_SPECIAL then
		say(cid, "So are you ready for another Mission?")
	elseif progress == POSTMAN_SANTA_DONE then
		say(cid, "You did it? I hope you did not catch a flu in the cold! However theres another mission for you. Are you interested?")
	else
		state.topic = 0
		return false
	end
	return true
end

local function accept(cid, state, say, progress)
	state.topic = 0
	if progress == POSTMAN_ROUTES then
		setPlayerStorageValue(cid, POSTMAN, POSTMAN_FOLDA)
		say(cid, "I am glad to hear that. One of our mailboxes was reported to be jammed. It is located on the so called 'mountain' on the isle Folda. Get a crowbar and fix the mailbox. Report about your mission when you have done so.")
	elseif progress == POSTMAN_FOLDA_FIXED then
		state.topic = TOPIC_NEXT + 100              -- the title first, then "Do you feel ready for it?"
		setPlayerStorageValue(cid, POSTMAN, POSTMAN_BILL)
		say(cid, "For your noble deeds I grant you the title Assistant Postofficer. All Postofficers will charge you less money from now on. After every second mission ask me for an ADVANCEMENT. Your next task will be a bit more challenging. Do you feel ready for it?")
	elseif progress == POSTMAN_BILL_DELIVERED then
		setPlayerStorageValue(cid, POSTMAN, POSTMAN_BONES_MISSION)
		say(cid, "Ok, listen: we have some serious trouble with agressive dogs lately. We have accumulated some bones as a sort of pacifier but we need more. Collect 20 bones like the one in my room to the left and report here.")
	elseif progress == POSTMAN_RANK_POSTMAN then
		setPlayerStorageValue(cid, POSTMAN, POSTMAN_PRESENT)
		say(cid, "Since I am convinced I can trust you, this time you must deliver a valuable present to Dermot on Fibula. Do NOT open it!!! You will find the present behind the door here on the lower right side of this room.")
	elseif progress == POSTMAN_PRESENT_GIVEN then
		setPlayerStorageValue(cid, POSTMAN, POSTMAN_UNIFORMS)
		say(cid, "Ok. We need a new set of uniforms, and only the best will do for us. Please travel to Venore and negotiate with Hugo Chief a contract for new uniforms.")
	elseif progress == POSTMAN_RANK_GRAND then
		setPlayerStorageValue(cid, POSTMAN, POSTMAN_MEASUREMENTS)
		say(cid, "Good, so listen. Hugo Chief informed me that he needs the measurements of our postofficers. Go and bring me the measurements of Ben, Lokur, Dove, Liane, Chrystal and Olrik.")
	elseif progress == POSTMAN_MEASURED then
		state.topic = TOPIC_NEXT + 101
		say(cid, "Ok but your next assignment might be dangerous. Our Courier Waldo has been missing for a while. I must assume he is dead. Can you follow me so far?")
	elseif progress == POSTMAN_RANK_SPECIAL then
		setPlayerStorageValue(cid, POSTMAN, POSTMAN_SANTA)
		say(cid, "So listen well. Behind the lower left door you will find a bag. The letters in the bag are for none other than Santa Claus! Deliver them to his house on the isle of Vega, USE the bag on his mailbox and report back here.")
	elseif progress == POSTMAN_SANTA_DONE then
		setPlayerStorageValue(cid, POSTMAN, POSTMAN_MARKWIN_LETTER)
		doPlayerAddItem(cid, LETTER_TO_MARKWIN, 1)
		say(cid, "Excellent. Here is a letter for you to deliver. Well, to be honest, no one else volunteered. It's a letter from the mother of Markwin, the king of Mintwallin. Deliver that letter to him, but note that you will not be welcome there.")
	end
end

local RANKS = {
	[POSTMAN_BONES_DONE] = {POSTMAN_RANK_POSTMAN, POST_OFFICERS_HAT,
		"From now on it shall be known that you are a postman. As a sign of your rank, take this hat."},
	[POSTMAN_UNIFORMS_DONE] = {POSTMAN_RANK_GRAND, nil,
		"From now on it shall be known that you are a grand postman. You are now a privileged member until the end of days. Most captains around the world have an agreement with our guild to transport our privileged members, like you, for less gold."},
	[POSTMAN_WALDO_DONE] = {POSTMAN_RANK_SPECIAL, POST_HORN,
		"From now on you are a grand postman for special operations. You are an honoured member of our guild and earned the privilege of your own post horn. Here, take it."},
	[POSTMAN_MARKWIN_DONE] = {POSTMAN_RANK_ARCH, nil,
		"I grant you the title of archpostman. You are a legend in our guild. As privilege of your newly aquired status you are allowed to make use of certain mailboxes in dangerous areas. Just look out for them and you'll see."},
}

local function mission(cid, state, say, progress)
	state.topic = 0
	if progress == 0 then
		state.topic = TOPIC_JOIN
		say(cid, "You are not a member of our guild yet! We have high standards for our members. To rise in our guild is a difficult but rewarding task. Are you interested in joining?")
	elseif progress == POSTMAN_ROUTES then
		if getPlayerStorageValue(cid, POSTMAN_LEGS) >= 15 then
			offer(cid, state, say, progress)
		else
			say(cid, "You have not checked all the tours yet: Captain Bluebear from Thais to Carlin, Uzon to Edron, Captain Seahorse to Venore and Brodrosch to Cormaya.")
		end
	elseif progress == POSTMAN_FOLDA then
		say(cid, "The mailbox on Folda is still jammed. Get a crowbar and fix it.")
	elseif progress == POSTMAN_BILL then
		say(cid, "Deliver the bill to the stage magician David Brassacres. He's hiding from his creditors somewhere in Venore.")
	elseif progress == POSTMAN_BONES_MISSION then
		state.topic = TOPIC_BONE
		say(cid, "Do you bring a bone for our officers' safety fund?")
	elseif progress == POSTMAN_PRESENT then
		say(cid, "Deliver the present to Dermot on Fibula. Do NOT open it!!!")
	elseif progress >= POSTMAN_UNIFORMS and progress < POSTMAN_UNIFORMS_DONE then
		say(cid, "Did you get us those new uniforms? Ask about the NEW DRESS PATTERN.")
	elseif progress == POSTMAN_MEASUREMENTS then
		if getPlayerStorageValue(cid, POSTMAN_MEASURES) >= 0 and
				getPlayerStorageValue(cid, POSTMAN_MEASURES) % 64 == POSTMAN_ALL_MEASURED then
			setPlayerStorageValue(cid, POSTMAN, POSTMAN_MEASURED)
			offer(cid, state, say, POSTMAN_MEASURED)
		else
			say(cid, "Bring me the measurements of Ben, Lokur, Dove, Liane, Chrystal and Olrik.")
		end
	elseif progress == POSTMAN_WALDO then
		state.topic = TOPIC_POSTHORN
		say(cid, "So Waldo is dead? This is grave news indeed. Did you recover his posthorn?")
	elseif progress == POSTMAN_SANTA then
		say(cid, "Deliver the letters to Santa's house on the isle of Vega and USE the bag on his mailbox.")
	elseif progress == POSTMAN_MARKWIN_LETTER then
		say(cid, "Deliver the letter to Markwin, the king of Mintwallin.")
	elseif progress == POSTMAN_MARKWIN_DONE then
		say(cid, "You have delivered that letter? You are a true postofficer. All over the land bards shall praise your name. There are no missions for you left right now.")
	elseif RANKS[progress] then
		say(cid, "Your eagerness is a virtue, young one, but first lets talk about advancement.")
	elseif progress >= POSTMAN_RANK_ARCH then
		say(cid, "There are no missions for you left right now.")
	else
		offer(cid, state, say, progress)
	end
end

questNpc{
	farewell = "Good bye.",
	walkaway = "Good bye.",
	greet = function(cid)
		return "Greetings |PLAYERNAME|, what brings you here?"
	end,
	quest = function(cid, msg, state, say)
		local progress = postmanProgress(cid)
		local yes, no = containsWord(msg, "yes"), containsWord(msg, "no")
		if state.topic >= TOPIC_JOIN and state.topic < TOPIC_JOIN + #JOIN + 1 and (yes or no) then
			if no then
				state.topic = 0
				say(cid, "Then not.")
			elseif state.topic <= #JOIN then
				say(cid, JOIN[state.topic])
				state.topic = state.topic + 1
			else
				state.topic = 0
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_ROUTES)
				setPlayerStorageValue(cid, POSTMAN_LEGS, 0)
				say(cid, "Ok, remember: the Tibian mail service puts trust in you! Don't fail and report back soon. Just tell me about your MISSION.")
			end
			return true
		elseif state.topic == TOPIC_NEXT and yes then
			accept(cid, state, say, progress)
			return true
		elseif state.topic == TOPIC_NEXT + 100 and yes then          -- mission 3, after the title
			state.topic = 0
			say(cid, "I need you to deliver a bill to the stage magician David Brassacres. He's hiding from his creditors somewhere in Venore. It's likely you will have to trick him somehow to reveal his identity. Report back when you delivered this bill.")
			return true
		elseif state.topic == TOPIC_NEXT + 101 and yes then          -- mission 8, after "Can you follow me so far?"
			state.topic = 0
			setPlayerStorageValue(cid, POSTMAN, POSTMAN_WALDO)
			say(cid, "Find out about his whereabouts and retrieve him or at least his posthorn. He was looking for a new underground passage that is rumoured to be found underneath the troll-infested Mountain east of Thais.")
			return true
		elseif state.topic == TOPIC_BONE and (yes or containsWord(msg, "all")) then
			state.topic = 0
			local given = math.max(getPlayerStorageValue(cid, POSTMAN_BONES), 0)
			local wanted = containsWord(msg, "all") and 20 - given or 1
			local n = 0
			while n < wanted and takeBone(cid) do
				n = n + 1
			end
			if n == 0 then
				say(cid, "You don't have a bone with you.")
				return true
			end
			given = given + n
			setPlayerStorageValue(cid, POSTMAN_BONES, given)
			if given >= 20 then
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_BONES_DONE)
				say(cid, "Excellent! We have enough bones for the fund now. Ask me for an ADVANCEMENT.")
			else
				say(cid, "Excellent! You have collected " .. given .. " bones. Just report about your mission again if you find more.")
			end
			return true
		elseif state.topic == TOPIC_POSTHORN and yes then
			state.topic = 0
			if doPlayerRemoveItem(cid, WALDOS_POSTHORN, 1) then
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_WALDO_DONE)
				say(cid, "Thank you. We will honour this. Your next mission will be a very special one. Good thing you are a special person as well. Ask me for an ADVANCEMENT.")
			else
				say(cid, "You don't have it with you. Find Waldo, or at least his posthorn.")
			end
			return true
		elseif state.topic == TOPIC_ADVANCE and yes then
			state.topic = 0
			local rank = RANKS[progress]
			if rank then
				setPlayerStorageValue(cid, POSTMAN, rank[1])
				if rank[2] then
					doPlayerAddItem(cid, rank[2], 1)
				end
				say(cid, rank[3])
			end
			return true
		elseif state.topic == TOPIC_NOODLES and yes then
			state.topic = 0
			setPlayerStorageValue(cid, POSTMAN, POSTMAN_NOODLES)
			setPlayerStorageValue(cid, POSTMAN_SNIFFED, 0)
			say(cid, "Good. Go there and find out what taste he dislikes most: moldy cheese, a piece of fur or a banana skin. Tell him to SNIFF, then the object. Show him the object and ask 'Do you like that?'. DONT let the guards know what you are doing.")
			return true
		elseif state.topic ~= 0 and no then
			state.topic = 0
			say(cid, "Then not.")
			return true
		elseif containsWord(msg, "mission") then
			mission(cid, state, say, progress)
			return true
		elseif containsWord(msg, "advancement") then
			if RANKS[progress] then
				state.topic = TOPIC_ADVANCE
				say(cid, "You are worthy indeed. Do you want to advance in our guild?")
			else
				state.topic = 0
				say(cid, "You are not ready for an advancement yet.")
			end
			return true
		elseif containsWord(msg, "dress pattern") or containsWord(msg, "dress patterns") then
			state.topic = 0
			if progress == POSTMAN_HUGO_ASKED then
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_TALPHION)
				say(cid, "Oh yes, where did we get that from ...? Let's see, first ask the great technomancer in Kazordoon for the technical details. Return here afterwards.")
			elseif progress == POSTMAN_TALPHION_DONE then
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_ELOISE)
				say(cid, "The mail with Talphion's instructions just arived. I remember we asked Queen Eloise of Carlin for the perfect colours. Go there, ask her about the UNIFORMS and report back here.")
			elseif progress == POSTMAN_ELOISE_DONE then
				state.topic = TOPIC_NOODLES
				say(cid, "The queen has sent me the samples we needed. The next part is tricky. We need the uniforms to emanate some odor that dogs hate. The dog with the best 'taste' in that field is Noodles, the dog of King Tibianus. Do you understand so far?")
			elseif progress == POSTMAN_NOODLES_DONE then
				setPlayerStorageValue(cid, POSTMAN, POSTMAN_HUGO_ORDER)
				say(cid, "Fine, fine. I think that should do it. Tell Hugo that we order those uniforms. The completed dress pattern will soon arrive in Venore. Report to me when you have talked to him.")
			elseif progress == POSTMAN_UNIFORMS_DONE then
				say(cid, "Excellent! Another job well done! Ask me for an ADVANCEMENT.")
			else
				say(cid, "Talk to Hugo in Venore about the new uniforms first.")
			end
			return true
		end
		return false
	end,
	talk = {
		{"job", "I am the Postmaster General of the Tibian mail service."},
		{"name", "My name is Kevin Postner."},
	},
}

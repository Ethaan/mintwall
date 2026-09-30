-- Umar, the gatekeeper of Ashta'daramai (The Djinn War - Marid Faction, docs/reference-74/quests.md; npc/lib/djinn.lua).
-- TibiaWiki 2006 transcript: DJANNI'HAH "Whoa? You know the word! Amazing, player! ..."; "passage" "If you want to
-- enter our fortress you have to become one of us and fight the Efreet. ... So, are you willing to do so?"; "yes"
-- "Are you sure? You pledge loyalty to king Gabel ... Yes?"; "yes" "Oh. Ok. Welcome then. You may pass. ...". The
-- other lines are the old script's.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local TALK = {
	{"ashta'daramai", "This place is the Marids' safe haven. No enemy has ever managed to take this fortress by assault, and we will see to it that it stays this way."},
	{"philosopher", "Yes. Comes with the job. You see - here I am, sitting on the same chair all day and staring at the same blank wall. So what happens is that my mind starts wandering. And, you know, I start thinking. You know - about all kinds of things."},
	{"ab'dendriel", "I understand the humans have founded some beautiful cities. I would like to see them, but as long as I have to stay here that won't happen. Which means I will not go anywhere as long as the war goes on."},
	{"mal'ouquah", "That is the Efreets fortress. I have never seen it, but I'm sure it can't compare to this place."},
	{"kha'labal", "Ah yes - the desert. I still remember how beautiful that land was back in the days before the war. ...", "A land full of song and bliss it was - a veritable paradise. Fa'hradin once said its destruction was a supreme example of the transitoriness of all things mortal. ...", "I am not sure I agree because I don't know what 'transitoriness' means."},
	{"kazordoon", "I understand the humans have founded some beautiful cities. I would like to see them, but as long as I have to stay here that won't happen. Which means I will not go anywhere as long as the war goes on."},
	{"ankrahmun", "I was there, long ago. We had a garrison based in Ankrahmun during the early phases of the war. That was before the whole plains of the Kha'labal were set on fire."},
	{"ascension", "Apparently that is what the followers of the pharaoh are striving for. It has to do with that pharaoh's teachings."},
	{"fa'hradin", "Fa'hradin is a powerful wizard and the smartest djinn I know. I love talking to him because there is so much he can teach me, but he rarely has time for me."},
	{"zathroth", "Zathroth is not very popular among the djinn because it is said that he abandoned us even though he was our creator. Legend has it that we failed to meet his expectations. ...", "Fa'hradin once said that all djinn are oedipally traumatised because of this, but I have no idea what he is talking about."},
	{"melchior", "That name rings a bell. A trader from Ankrahmun... or was it Darashia? I remember him and his mule. He used to come up here quite often to do business with Haroun. ...", "Lately I haven't seen him around, though. I think last time he came here was about 20 years ago."},
	{"darashia", "They say Darashia is a beautiful human city somewhere to the north. I would really love to see it, but I can't abandon my post."},
	{"kha'zeel", "When I look up from my wall, what do I see? Huge, forbidding mountains! No wonder I feel claustrophobic."},
	{"daraman", "Daraman has changed our lives. I mean, we were not stupid or anything before he came, but still it was different. Fa'hradin says that while Zathroth made us intelligent, Daraman made us think."},
	{"pharaoh", "They say the new pharaoh is mad!"},
	{"bo'ques", "That fat old cook. I like his food, but I find him a bit boring. Food and cooking is all he ever talks about."},
	{"things", "Yes. About the world and the gods and all that. And about girls. Yes, about girls, mostly."},
	{"efreet", "I have thought long and hard about this and I have come to the conclusion that all Efreet are scum."},
	{"venore", "I understand the humans have founded some beautiful cities. I would like to see them, but as long as I have to stay here that won't happen. Which means I will not go anywhere as long as the war goes on."},
	{"carlin", "I understand the humans have founded some beautiful cities. I would like to see them, but as long as I have to stay here that won't happen. Which means I will not go anywhere as long as the war goes on."},
	{"scarab", "I don't care whether or not they are special animals. None of that creeping vermin will enter Ashta'daramai as long as I am here!"},
	{"palace", "I remember the palace. It was a beautiful place. Ah... those were happy days."},
	{"temple", "In these heretic times the priests at Ankrahmun's temple are devoted to the teachings of that pompous pharaoh."},
	{"alesar", "Ah. That guy. He was one of us, a Marid, but he left long ago. I have no idea why. Rumours and hearsay is all I ever get."},
	{"dwarf", "Yes. Consider this: Dwarves live in the mountains. So do I. And just like dwarves I really like gold. But most of all, dwarves like beer. ...", "Isn't that amazing? I think that is more than a coincidence. You know - perhaps I am a reincarnated dwarf or something. You never know."},
	{"human", "See. That's another problem. In the past, it was us against you - djinn against humans. But one day this guy came along, and all of a sudden things were so much more complicated. ...", "All of a sudden there was good djinn and evil djinn, and good humans and evil humans. Everything got so damn complicated. ...", "All of a sudden we did not know who to trust and who to fight. Should we join the evil djnn and battle all humans? ...", "Or was it smarter to ally with the good humans and to battle the bad djinn? ...", "Perhaps we should join nobody and fight the bad humans? So many choices."},
	{"girls", "You did not know there are female djinns, did you? That's because they are quite rare. They are the greatest treasures of our race, and we guard them jealously."},
	{"gabel", "He is our king and leader. Well, he isn't a king, you know. I mean, from a technical point of view he is, but he does not wear a crown or anything, and he says he isn't one, so even though he is one he isn't. Right?"},
	{"djinn", "Well, I am a djinn, but only as far as my physical aspect is concerned. As far as my way of thinking is concerned I think I might actually be somebody else. You now - not even a djinn. In fact, I think I might be a dwarf."},
	{"marid", "That's us. I suppose we are the good guys in this war. Although good is relative, of course. So let's say, we are relatively good. Depends on the point of view, really."},
	{"malor", "Malor is evil. I mean - really evil. Things used to be much better when he was still locked away in that lamp."},
	{"tibia", "Tibia is a beautiful world. Not that I see much of it, staring at this wall night and day."},
	{"world", "Tibia is a beautiful world. Not that I see much of it, staring at this wall night and day."},
	{"edron", "I understand the humans have founded some beautiful cities. I would like to see them, but as long as I have to stay here that won't happen. Which means I will not go anywhere as long as the war goes on."},
	{"thais", "I understand the humans have founded some beautiful cities. I would like to see them, but as long as I have to stay here that won't happen. Which means I will not go anywhere as long as the war goes on."},
	{"uthun", "That's just some heretic drivel. Don't ask me about it."},
	{"djema", "You know her? She's a human like you. I like her lots because she often comes down here for a chat. Nobody else around here does that."},
	{"king", "Okay, let's do this again. Gabel says he isn't a king, but he acts like one, which makes him one anyway - right? ...", "But you know, he does not really act like one, either. I mean, he does give us orders and all that, and we obey sure enough, but it's not that we have to, I mean, technically speaking. ...", "I mean - I don't know what would happen if anybody would not follow his orders for a change. After all he is no longer a king, right? ...", "But then I don't want to be the first one to find out what happens if you disobey, so I always do as I'm told. ...", "Which means I do not really know whether or not he is king. <sighs> Things were so much easier when Gabel still said he was king. Matters were so much clearer then."},
	{"name", "I am Umar. Pleased to meet you!"},
	{"gods", "I have not made my mind up what to think about the gods yet. I am still struggling with Daraman's teachings."},
	{"lamp", "Djinns sleep in lamps. I don't know what is so special about that."},
	{"job", "I am the gatekeeper of Ashta'daramai. That's what Gabel told me to do. You know - keeping the courtyard clean, getting rid of salesmen, keeping Efreet scum out... that kind of thing. But in my spare time I work as a part-time philosopher."},
	{"war", "We had thought the war was over for good when Malor was finally imprisoned. That little creep is as obstinate as... as... well, as a really obstinate djinn."},
	{"rah", "That's just some heretic drivel. Don't ask me about it."},
	{"akh", "That's just some heretic drivel. Don't ask me about it."},
}

djinnNpc{
	word = "djanni'hah",
	farewell = "<salutes>Aaaa -tention!",
	walkaway = "<salutes>Aaaa -tention!",
	busy = "Yikes! Another human? Where did you come from? Well, ehm - if you could please wait a second, |PLAYERNAME|?",
	greet = function(cid, say)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			say(cid, {"Hahahaha! ...", "|PLAYERNAME|, that almost sounded like the word of greeting. Humans - cute they are!"}, true)
			return nil
		elseif djinnProgress(cid, DJINN_MARID) > 0 then
			return "|PLAYERNAME|! How's it going these days?"
		end
		return {"Whoa? You know the word! Amazing, |PLAYERNAME|! ...", "I should go and tell Fa'hradin. ...",
			"Well. Why are you here anyway, |PLAYERNAME|?"}
	end,
	hi = function(cid, say)
		say(cid, {"Whoa! A human! This is no place for you, |PLAYERNAME|. ...", "Go and play somewhere else."}, true)
	end,
	quest = function(cid, msg, state, say)
		if state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 2
			say(cid, "Are you sure? You pledge loyalty to king Gabel, who is... you know. And you are willing to never ever set foot on Efreets' territory, unless you want to kill them? Yes?")
			return true
		elseif state.topic == 2 and containsWord(msg, "yes") then
			state.topic = 0
			setPlayerStorageValue(cid, DJINN_MARID, MARID_PLEDGED)
			say(cid, {"Oh. Ok. Welcome then. You may pass. ...", "And don't forget to kill some Efreets, now and then."})
			return true
		elseif state.topic ~= 0 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "This isn't your war anyway, human.")
			return true
		elseif containsWord(msg, "passage") or containsWord(msg, "pass") or containsWord(msg, "enter") or containsWord(msg, "join") then
			state.topic = 0
			if djinnFollower(cid) == DJINN_EFREET then
				say(cid, "I don't believe you! You better go now.")
			elseif djinnProgress(cid, DJINN_MARID) > 0 then
				say(cid, "You already have the permission to enter Ashta'daramai.")
			else
				state.topic = 1
				say(cid, {"If you want to enter our fortress you have to become one of us and fight the Efreet. ...",
					"So, are you willing to do so?"})
			end
			return true
		end
		return false
	end,
	talk = TALK,
}

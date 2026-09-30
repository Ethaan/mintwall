-- Bo'ques, the Marid's cook in Ashta'daramai (The Djinn War - Marid Faction, docs/reference-74/quests.md;
-- npc/lib/djinn.lua). TibiaWiki 2006 transcripts: DJANNI'HAH "Hey! A human! What are you doing in my kitchen,
-- player?"; "mission" "My collection of recipes is almost complete. ... Are you interested?"; "yes" a cookbook of the
-- dwarven kitchen; back: "cookbook" "Do you have the cookbook of the dwarven kitchen with you? Can I have it?"; "yes"
-- "The book! You have it! ..." - 3 small sapphires (quests.md) - "... talk to him [Fa'hradin]". The other lines are the
-- old script's.
dofile(getDataDir() .. 'npc/lib/djinn.lua')

local TALK = {
	{"ashta'daramai", "That is our little fortress - our home. Nice, isn't it? I find it inspirational, although I find the culinary facilities could do with some improvements."},
	{"connoisseur", "Yes! That's it! I have always trouble with pronouncing that damn word. A conno... conni... ah, hang it all!"},
	{"ab'dendriel", "Ah, the northern cities. One day I will start an extensive culinary expedition there. I have this dream of writing some sort of culinary guide, you know. Isn't that a great idea?"},
	{"mal'ouquah", "Ah yes. The efreets' notorious fortress. I have never been there. That is no place for an artist such as myself."},
	{"kazordoon", "Ah, the northern cities. One day I will start an extensive culinary expedition there. I have this dream of writing some sort of culinary guide, you know. Isn't that a great idea?"},
	{"ankrahmun", "No djinn who is in his right state of mind would want to go there? What for? The land is ruled by an undead nut case, and from what I have heard his subjects are no better."},
	{"ascension", "As far as I know that is one of the pharaoh's crazy ideas. Just a load of baloney."},
	{"kha'labal", "Such a shame about that land. It wasn't always a desert, you know. That land was garden, a veritable paradise. Just the thought of the fruit that used to grow there makes my mouth water <sighs>. Well, guess who messed it up."},
	{"fa'hradin", "That djinn is so engrossed in his work! I constantly have to remind him to eat because if I didn't he would simply forget. Forgetting to eat! Can you imagine that?"},
	{"zathroth", "That is a sad story, and like most djinn I dislike talking about it. Let's put it this way. Once there was a great cook who worked hard to prepare the finest meal of his life. ...", "But when he found that the product of his efforts did not meet his expectations he just ditched it even though it was wonderfully unique in its own special way. ...", "You know what I think? I think Zathroth was a bad cook."},
	{"kha'zeel", "These mountains are a nice place to live in, but food-wise they are pretty lousy. We basically import everything we eat from the lowlands, trading them for magic trinkets and for gold. ...", "The only plants that grow well in these mountains are potatoes, and they are not really my idea of Haute Cuisine."},
	{"darashia", "I have heard good things about this place. I understand the Caliph is a true gourmet. People who eat good food can't be bad, that's what I say."},
	{"melchior", "Ah yes, the trader - right? I remember him. He used to travel the mountains with his mule. A tough haggler and a real skinflint, he was. I thought he had fallen down a cliff with all his money."},
	{"daraman", "Ah yes. That human WAS special, believe me. Did you know I talked to him myself, back in those days? In fact, I even had an argument with him because he dared to insult my work! He drove me mad when he called me a self-indulgent glutton. ...", "But you know, eventually we came to respect each other! He taught me to stress quality rather than quantity, and he came to appreciate my 'Chili con Cobra'. Today I know that having met him was a major step forward in my development as a culinary artist."},
	{"bo'ques", "You want Bo'ques? Well, you have found him, I'd say."},
	{"pharaoh", "Apparently he is an undead! And what's worse, he actually chose that fate for himself! Undead! Imagine that! Never sleep, never laugh, and worst of all: Never eat! What a crackpot!"},
	{"efreet", "A bunch of ignorants and primitives, that's what they are. You should see the things they eat! ...", "You know they serve ketchup with just about every kind of meal! Ketchup! Oh, those barbarians."},
	{"scarab", "Ah yes. I like them well. Especially with a good sauce or in a stew. But they have to be young! Have you tried ancient scarab? Their meat is impossible to chew unless you have teeth made of titanium."},
	{"venore", "Ah, the northern cities. One day I will start an extensive culinary expedition there. I have this dream of writing some sort of culinary guide, you know. Isn't that a great idea?"},
	{"carlin", "Ah, the northern cities. One day I will start an extensive culinary expedition there. I have this dream of writing some sort of culinary guide, you know. Isn't that a great idea?"},
	{"palace", "Who would like to live in a palace if there is never the delicious smell of freshly prepared food! I would not want to live there. Not for love nor for money."},
	{"alesar", "Ah - that guy. You probably don't know it, but nobody around here likes to hear that name. It brings back painful memories, you know. His betrayal was such a heavy blow to us. I think I will never understand what made him do it? It is a mystery."},
	{"human", "I totally agree with Gabel that djinn and humans can learn from each other. ...", "Take cooking, for example. It has such a long tradition among humans - even I could still learn a thing or two from the famous cooks at king Tibianus' court!"},
	{"gabel", "He is my boss. A most loyal customer and a real con... conni... well, a man of taste, at any rate. His favourite dish is Scarabée au Vin served with onions and rice."},
	{"marid", "That is us - the loyalists who have have remained faithful to Gabel and to good cooking."},
	{"malor", "That accursed traitor! I think there will never be peace until he is completely vanquished. If only he would allow me to cook for him. I would fix him a dinner he would never forget."},
	{"tibia", "It may be that this world is wide and full of adventure, but to be honest I am not at all keen to see it myself. A comfortable lamp to sleep in and a well equipped kitchen is all I need."},
	{"edron", "Ah, the northern cities. One day I will start an extensive culinary expedition there. I have this dream of writing some sort of culinary guide, you know. Isn't that a great idea?"},
	{"thais", "Ah, the northern cities. One day I will start an extensive culinary expedition there. I have this dream of writing some sort of culinary guide, you know. Isn't that a great idea?"},
	{"uthun", "Hm. Is that some exotic spice? Hang on, I know! It is a kind of lizard stew - right?"},
	{"djema", "Djema is a nice girl, but she eats so little. It's frustrating, really. Humans and their little stomachs!"},
	{"cook", "I'm preparing the food for all djinn in Ashta'daramai. ...", "Therefore I'm what is commonly called a cook, although I do not like that word too much. It is vulgar. I prefer to call myself 'chef'."},
	{"name", "My name is Bo'ques. Perhaps you know my name from a restaurant guide."},
	{"chef", "Chef sounds nice, doesn't it? Well... I must admit I do not really know what it means, but it certainly sounds classy."},
	{"food", "I know many recipes for preparing the finest food on Darama and maybe even whole Tibia!"},
	{"king", "Gabel used to be king, you know. I must confess I miss those days a bit because I was allowed to carry the title of his royal majesty's personal cook. Ah, those were the days."},
	{"lamp", "You would not believe it, but those lamps are actually quite comfy. And on top of that they are immensely practical! Did you ever try to stash one of your beds into your pocket?"},
	{"job", "I'm preparing the food for all djinn in Ashta'daramai. ...", "Therefore I'm what is commonly called a cook, although I do not like that word too much. It is vulgar. I prefer to call myself 'chef'."},
	{"rah", "Hm. Is that some exotic spice? Hang on, I know! It is a kind of lizard stew - right?"},
	{"akh", "Hm. Is that some exotic spice? Hang on, I know! It is a kind of lizard stew - right?"},
	{"war", "I have never been much of a warrior, but I will storm into battle swinging my meat cleaver if necessary. We simply must win this war!"},
}

local SMALL_SAPPHIRE = 2146

djinnNpc{
	word = "djanni'hah",
	farewell = "Goodbye. I am sure you will come back for more. They all do.",
	walkaway = "Now, where was I?",
	busy = "Whoa. Do I look as if I had two heads? Only one at a time, |PLAYERNAME|!",
	greet = function(cid)
		if getPlayerStorageValue(cid, DJINN_WORD) ~= 1 then
			return nil
		end
		return "Hey! A human! What are you doing in my kitchen, |PLAYERNAME|?"
	end,
	quest = function(cid, msg, state, say)
		if djinnFollower(cid) ~= DJINN_MARID then
			return false
		end
		local progress = djinnProgress(cid, DJINN_MARID)
		if state.topic == 1 and containsWord(msg, "yes") then
			state.topic = 0
			setPlayerStorageValue(cid, DJINN_MARID, MARID_COOKBOOK)
			say(cid, {"Fine! Even though I know so many recipes, I'm looking for the description of some dwarven meals. ...",
				"So, if you could bring me a cookbook of the dwarven kitchen I will reward you well."})
			return true
		elseif state.topic == 1 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Well, too bad.")
			return true
		elseif state.topic == 2 and containsWord(msg, "yes") then
			state.topic = 0
			if doPlayerRemoveItem(cid, COOKBOOK, 1) then
				setPlayerStorageValue(cid, DJINN_MARID, MARID_BOOK_GIVEN)
				doPlayerAddItem(cid, SMALL_SAPPHIRE, 3)
				say(cid, {"The book! You have it! Let me see! <browses the book> ...",
					"Dragon Egg Omelette, Dwarven beer sauce... it's all there. This is great! Here is your well-deserved reward. ...",
					"Incidentally, I have talked to Fa'hradin about you during dinner. I think he might have some work for you. Why don't you talk to him about it?"})
			else
				say(cid, "Too bad. I must have this book.")
			end
			return true
		elseif state.topic == 2 and containsWord(msg, "no") then
			state.topic = 0
			say(cid, "Too bad. I must have this book.")
			return true
		elseif containsWord(msg, "mission") or containsWord(msg, "recipe") then
			state.topic = 0
			if progress == MARID_PLEDGED then
				state.topic = 1
				say(cid, {"My collection of recipes is almost complete. There are only but a few that are missing. ...",
					"Hmmm... now that we talk about it. There is something you could help me with. Are you interested?"})
			elseif progress == MARID_COOKBOOK then
				say(cid, "So, if you could bring me a cookbook of the dwarven kitchen I will reward you well.")
			else
				say(cid, "Thanks again, for bringing me that book.")
			end
			return true
		elseif containsWord(msg, "cookbook") or containsWord(msg, "book") then
			if progress == MARID_COOKBOOK then
				state.topic = 2
				say(cid, "Do you have the cookbook of the dwarven kitchen with you? Can I have it?")
				return true
			elseif progress > MARID_COOKBOOK then
				state.topic = 0
				say(cid, "Thanks again, for bringing me that book.")
				return true
			end
		end
		return false
	end,
	talk = TALK,
}

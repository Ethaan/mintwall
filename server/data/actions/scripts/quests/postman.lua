-- The Postman Missions Quest (docs/reference-74/quests.md; npc/lib/postman.lua): the quest objects. None of them was
-- scripted on our map (nor given an id); positions are our map's, the chests tibiaot74's (on the closets' counters).
--
-- 51190 the jammed mailbox on Folda's mountain (32013,31562,4): "use the crowbar on the mailbox" (TibiaWiki 2005)
-- 51191 / 51192 Kevin's lower right / left doors (32569 / 32567,32023,6): open once he gave the present / the Santa
--       mission ("You will not be able to open the door until you have talked to Kevin", the wiki's Waldo note)
-- 51193 Waldo's door in the troll cave east of Thais (32515,32248,8): opens once Kevin sent you after Waldo
-- 51194 the chest behind the right door (32569,32024,6): the present - once: "If you try to open it, you will get
--       nothing and the present will disappear. Once it disappears, you can never get it back with that character."
-- 51195 the chest behind the left door (32567,32024,6): the letter bag (500 oz) - "it won't come out of the chest
--       unless you have the capacity"
-- 51196 Waldo's body (32514,32248,8): "use it to get Waldo's Post Horn"
-- 51197 Santa's mailbox on Vega (31948,31711,6): "Use the bag on the mailbox ... You will keep the nice red bag,
--       but after you deliver the letters, it will be a normal red bag"
dofile(getDataDir() .. 'npc/lib/postman.lua')

local PRESENT_TAKEN = 70206            -- the present came out of the chest (only ever once)
local RED_BAG = 1993

local function questDoor(cid, item, frompos, open)
	if not open then
		doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, "The door is sealed against unwanted intruders.")
		return true
	end
	doTransformItem(item.uid, item.itemid + 1)
	if queryTileAddThing(cid, frompos, bit.bor(2, 4)) == RETURNVALUE_NOERROR then
		doMoveCreature(cid, getDirectionTo(getPlayerPosition(cid), frompos))
	end
	return true
end

local function found(cid, text)
	doPlayerSendTextMessage(cid, MESSAGE_INFO_DESCR, text)
end

function onUse(cid, item, frompos, item2, topos)
	local progress = postmanProgress(cid)

	if item.itemid == CROWBAR then
		if item2 == nil or item2.actionid ~= 51190 then
			return false
		end
		if progress == POSTMAN_FOLDA then
			setPlayerStorageValue(cid, POSTMAN, POSTMAN_FOLDA_FIXED)
			doSendMagicEffect(topos, CONST_ME_BLOCKHIT)
			found(cid, "You fixed the mailbox.")
		else
			doSendMagicEffect(topos, CONST_ME_POFF)
		end
		return true
	elseif item.itemid == LETTER_BAG then
		if item2 == nil or item2.actionid ~= 51197 then
			return false
		end
		if progress == POSTMAN_SANTA then
			setPlayerStorageValue(cid, POSTMAN, POSTMAN_SANTA_DONE)
			doTransformItem(item.uid, RED_BAG)
			doSendMagicEffect(topos, CONST_ME_MAGIC_BLUE)
			found(cid, "You delivered the letters to Santa's mailbox.")
		end
		return true
	elseif item.itemid == PRESENT then
		-- opened: nothing inside, and the present is gone for good
		doRemoveItem(item.uid, 1)
		doSendMagicEffect(getPlayerPosition(cid), CONST_ME_POFF)
		return true
	end

	if item.actionid == 51191 then
		return questDoor(cid, item, frompos, progress >= POSTMAN_PRESENT)
	elseif item.actionid == 51192 then
		return questDoor(cid, item, frompos, progress >= POSTMAN_SANTA)
	elseif item.actionid == 51193 then
		return questDoor(cid, item, frompos, progress >= POSTMAN_WALDO)
	elseif item.actionid == 51194 then
		if progress ~= POSTMAN_PRESENT or getPlayerStorageValue(cid, PRESENT_TAKEN) == 1 then
			found(cid, "The chest is empty.")
		else
			setPlayerStorageValue(cid, PRESENT_TAKEN, 1)
			doPlayerAddItem(cid, PRESENT, 1)
			found(cid, "You have found a present.")
		end
		return true
	elseif item.actionid == 51195 then
		if progress ~= POSTMAN_SANTA or getPlayerItemCount(cid, LETTER_BAG) > 0 then
			found(cid, "The chest is empty.")
		elseif getPlayerFreeCap(cid) < 500 then
			found(cid, "You have found a letterbag. It weighs 500.00 oz. It is too heavy.")
		else
			doPlayerAddItem(cid, LETTER_BAG, 1)
			found(cid, "You have found a letterbag.")
		end
		return true
	elseif item.actionid == 51196 then
		if progress ~= POSTMAN_WALDO or getPlayerItemCount(cid, WALDOS_POSTHORN) > 0 then
			found(cid, "The dead human is empty.")
		else
			doPlayerAddItem(cid, WALDOS_POSTHORN, 1)
			found(cid, "You have found Waldo's posthorn.")
		end
		return true
	end
	return false
end

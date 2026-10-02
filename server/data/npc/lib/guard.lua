-- The Thais gate guards (Grof, Tim, Kulag, Walter). TibiaWiki 2006: each "protects the city from creatures" at one of
-- the gates. Decided with the user 2026-09-30: a guard kills a wild monster that comes within GUARD_RANGE tiles on his
-- floor ("Get lost, you beast!"); a player's summon is left alone. Their rat bounty (1 gold for a dead rat) and their
-- answer to insults (a fire burn, "Take this!") are the old scripts' - they did not work (no gold, no rat taken, the
-- fire was not a condition, and the monster check was a global every NPC shares).
dofile(getDataDir() .. 'npc/lib/questnpc.lua')

GUARD_RANGE = 4
local GUARD_EVERY = 2                -- seconds between looks around
local DEAD_RAT, GOLD = 2813, 2148
local INSULTS = {"idiot", "stupid", "tyrant", "asshole", "fuck", "shit", "shut up", "ugly", "sucker", "retard", "bitch"}

local burn = createConditionObject(CONDITION_FIRE)
setConditionParam(burn, CONDITION_PARAM_DELAYED, 10)
addDamageCondition(burn, 10, 3000, -10)

local function isWildMonster(cid)
	-- creature ids: players 0x10000000, monsters 0x40000000, NPCs 0x80000000
	return cid >= 0x40000000 and cid < 0x80000000 and getCreatureMaster(cid) == cid
end

function guardNpc(spec)
	local lastLook = 0
	local npcHandler = questNpc{
		farewell = spec.farewell or "Be careful out there.",
		walkaway = spec.farewell or "Be careful out there.",
		quest = function(cid, msg, state, say)
			for _, word in ipairs(INSULTS) do
				if containsWord(msg, word) then
					state.topic = 0
					doSendMagicEffect(getCreaturePosition(getNpcCid()), CONST_ME_MAGIC_RED)
					doSendMagicEffect(getPlayerPosition(cid), CONST_ME_HITBYFIRE)
					doAddCondition(cid, burn)
					say(cid, "Take this!")
					return true
				end
			end
			if state.topic == 1 and containsWord(msg, "yes") then
				state.topic = 0
				if doPlayerRemoveItem(cid, DEAD_RAT, 1) then
					doPlayerAddItem(cid, GOLD, 1)
					say(cid, "Here is your reward. You will become a great warrior some day.")
				else
					say(cid, "Look like it wasn't as dead as you thought ... it's gone.")
				end
				return true
			elseif state.topic == 1 and containsWord(msg, "no") then
				state.topic = 0
				say(cid, "Come on. Don't waste my time with your jests.")
				return true
			elseif containsWord(msg, "rat") or containsWord(msg, "rats") then
				state.topic = 1
				say(cid, "Do you bring a freshly killed rat for a bounty of 1 gold?")
				return true
			end
			return false
		end,
		talk = {
			{"job", "It's my duty to protect the city."},
			{"city", "Behave while in the city or we get you!"},
			{"sell", "Visit Tibia's shopkeepers to buy their fine wares."},
			{"buy", "Visit Tibia's shopkeepers to buy their fine wares."},
		},
	}

	-- on watch: the wild monsters within range on his floor die
	local talking = onThink
	function onThink()
		talking()
		if os.time() - lastLook < GUARD_EVERY then
			return
		end
		lastLook = os.time()
		local here = getCreaturePosition(getNpcCid())
		for _, cid in ipairs(getSpectators(here, GUARD_RANGE, GUARD_RANGE) or {}) do
			local pos = getCreaturePosition(cid)
			if isWildMonster(cid) and pos.z == here.z then
				doSendMagicEffect(pos, CONST_ME_HITBYFIRE)
				doCreatureAddHealth(cid, -getCreatureHealth(cid))
				selfSay("Get lost, you beast!")
			end
		end
	end
	return npcHandler
end

-- 7.4 Soulfire: no hit, the target burns for 100-140 % of the caster's magic power in total (tibiantis-notes Magic,
-- TibiaWiki 2005 "120+/-20", OTHire 120/20), 10 a turn (TibiaWiki 2007: "10 damage for a number of turns ... depends
-- upon your level and magic level"); a turn every 10 s as the fire fields (items.xml). It was a fixed 80 here.
-- docs/reference-74/spell-formulas.md
-- A condition's damage is fixed when the script loads, so there is one combat per number of turns.
local MIN, MAX = 1.0, 1.4
local TOP = 210                  -- turns: magic power 1500

local combats = {}
for turns = 1, TOP do
	local combat = createCombatObject()
	setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_FIREDAMAGE)
	setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_FIREAREA)
	setCombatParam(combat, COMBAT_PARAM_DISTANCEEFFECT, CONST_ANI_FIRE)

	local condition = createConditionObject(CONDITION_FIRE)
	setConditionParam(condition, CONDITION_PARAM_DELAYED, 1)
	addDamageCondition(condition, turns, 10000, -10)
	setCombatCondition(combat, condition)
	combats[turns] = combat
end

function onCastSpell(cid, var)
	local power = magicPower(getPlayerLevel(cid), getPlayerMagLevel(cid))
	local total = math.random(math.floor(power * MIN), math.floor(power * MAX))
	local turns = math.max(1, math.min(TOP, math.floor(total / 10 + 0.5)))
	return doCombat(cid, combats[turns], var)
end

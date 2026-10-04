-- 7.4 Envenom: no hit, the target is poisoned for 50-90 % of the caster's magic power in total (tibiantis-notes
-- Magic/poison, OTHire 70/20), dealt as 7.4 poison: 5% of what is left every 4 s (ConditionDamage::generateDamageList).
-- It was a burn of a fixed ~80 here. docs/reference-74/spell-formulas.md
-- A condition's damage is fixed when the script loads, so there is one combat per magic power step of 5.
local MIN, MAX = 0.5, 0.9
local STEP, TOP = 5, 1500
-- src/enums.h ConditionParam_t; global.lua's CONDITION_PARAM_MINVALUE and the ones after it are 2 too low
local PARAM_MINVALUE, PARAM_MAXVALUE, PARAM_TICKINTERVAL = 14, 15, 17

local combats = {}
for power = 100, TOP, STEP do
	local combat = createCombatObject()
	setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_POISONDAMAGE)
	setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_GREEN_RINGS)
	setCombatParam(combat, COMBAT_PARAM_DISTANCEEFFECT, CONST_ANI_POISON)

	local condition = createConditionObject(CONDITION_POISON)
	setConditionParam(condition, CONDITION_PARAM_DELAYED, 1)
	setConditionParam(condition, PARAM_MINVALUE, math.floor(power * MIN))
	setConditionParam(condition, PARAM_MAXVALUE, math.floor(power * MAX))
	setConditionParam(condition, PARAM_TICKINTERVAL, 4000)
	setCombatCondition(combat, condition)
	combats[power] = combat
end

function onCastSpell(cid, var)
	local power = magicPower(getPlayerLevel(cid), getPlayerMagLevel(cid))
	power = math.min(TOP, math.floor((power + STEP / 2) / STEP) * STEP)
	return doCombat(cid, combats[power], var)
end

-- 7.4 Poison Storm: no hit, every creature in the area is poisoned for 150-250 % of the caster's magic power in total
-- (tibiantis-notes Magic/poison, TibiaWiki 2005-2007 "poisons the enemy with 200+/-50", OTHire 200/50), dealt as 7.4
-- poison: 5% of what is left every 4 s, the first tick ceil(total / 20) (ConditionDamage::generateDamageList).
-- docs/reference-74/spell-formulas.md
-- A condition's damage is fixed when the script loads, so there is one combat per magic power step of 5.
local MIN, MAX = 1.5, 2.5
local STEP, TOP = 5, 1500
-- src/enums.h ConditionParam_t; global.lua's CONDITION_PARAM_MINVALUE and the ones after it are 2 too low
local PARAM_MINVALUE, PARAM_MAXVALUE, PARAM_TICKINTERVAL = 14, 15, 17

local arr = {
    {0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0},
    {0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0},
    {0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0},
    {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0},
    {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0},
    {1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1},
    {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0},
    {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0},
    {0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0},
    {0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0},
    {0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0}
}

local combats = {}
for power = 100, TOP, STEP do
	local combat = createCombatObject()
	setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_POISONDAMAGE)
	setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_GREEN_RINGS)

	local condition = createConditionObject(CONDITION_POISON)
	setConditionParam(condition, CONDITION_PARAM_DELAYED, 1)
	setConditionParam(condition, PARAM_MINVALUE, math.floor(power * MIN))
	setConditionParam(condition, PARAM_MAXVALUE, math.floor(power * MAX))
	setConditionParam(condition, PARAM_TICKINTERVAL, 4000)
	setCombatCondition(combat, condition)

	setCombatArea(combat, createCombatArea(arr))   -- a combat owns (and deletes) its area: one each
	combats[power] = combat
end

function onCastSpell(cid, var)
	local power = magicPower(getPlayerLevel(cid), getPlayerMagLevel(cid))
	power = math.min(TOP, math.floor((power + STEP / 2) / STEP) * STEP)
	return doCombat(cid, combats[power], var)
end

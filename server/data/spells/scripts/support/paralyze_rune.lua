local combat = createCombatObject()
setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_MAGIC_RED)

local condition = createConditionObject(CONDITION_PARALYZE)
-- 7.4 (Tibiantis-notes, speed): speed set to 40 whatever the level, for about 10 s; speed items still
-- add, haste is cancelled (Creature::addCondition), healing spells/runes and haste remove it
setConditionParam(condition, CONDITION_PARAM_TICKS, 10000)
setConditionFormula(condition, -1.0, 40, -1.0, 40)   -- base speed x -1 + 40: speed 40 (it was 0 for 60 s)
setCombatCondition(combat, condition)

function onCastSpell(cid, var)
	return doCombat(cid, combat, var)
end
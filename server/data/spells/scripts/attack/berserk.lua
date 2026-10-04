local combat = createCombatObject()
setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_PHYSICALDAMAGE)
setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_HITAREA)
-- 7.4: level only, 2.4-4.0 x level (TI-Calc level/25 x 60..100; decided with the user 2026-10-04;
-- docs/reference-74/formulas.md §2, spell-formulas.md). It used to be (2L + 3ML) x 1.4..1.65.
function onGetFormulaValues(cid, level, maglevel)
	return -level * 4.0, -level * 2.4
end

setCombatCallback(combat, CALLBACK_PARAM_LEVELMAGICVALUE, "onGetFormulaValues")

local arr = {
{1, 1, 1},
{1, 3, 1},
{1, 1, 1}
}

local area = createCombatArea(arr)
setCombatArea(combat, area)

function onCastSpell(cid, var)
	return doCombat(cid, combat, var)
end
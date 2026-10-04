local combat = createCombatObject()
setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_PHYSICALDAMAGE)
setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_MORTAREA)
setCombatParam(combat, COMBAT_PARAM_DISTANCEEFFECT, CONST_ANI_SUDDENDEATH)
setCombatFormula(combat, COMBAT_FORMULA_LEVELMAGIC, -1.3, 0, -1.7, 0)   -- 7.4: 130-170 %P (decided with the user 2026-10-04; docs/reference-74/spell-formulas.md)

function onCastSpell(cid, var)
	return doCombat(cid, combat, var)
end
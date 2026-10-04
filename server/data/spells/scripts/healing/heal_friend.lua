local combat = createCombatObject()
setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_HEALING)
setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_MAGIC_GREEN)
setCombatParam(combat, COMBAT_PARAM_AGGRESSIVE, 0)
setCombatParam(combat, COMBAT_PARAM_DISPEL, CONDITION_PARALYZE)

setCombatFormula(combat, COMBAT_FORMULA_LEVELMAGIC, 0.8, 0, 1.6, 0)   -- 7.4: 80-160 %P (docs/reference-74/spell-formulas.md)

function onCastSpell(cid, var)
	doSendMagicEffect(getCreaturePosition(cid), CONST_ME_MAGIC_BLUE)
	return doCombat(cid, combat, var)
end
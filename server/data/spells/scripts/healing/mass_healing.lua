local combat = createCombatObject()
setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_HEALING)
setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_MAGIC_BLUE)
setCombatParam(combat, COMBAT_PARAM_AGGRESSIVE, 0)
setCombatParam(combat, COMBAT_PARAM_TARGETCASTERORTOPMOST, 1)
setCombatFormula(combat, COMBAT_FORMULA_LEVELMAGIC, 1.6, 0, 2.4, 0)   -- 7.4: 160-240 %P

local arr = {
 {0, 0, 0, 0, 0, 0, 0},
 {0, 0, 1, 1, 1, 0, 0},
 {0, 1, 1, 1, 1, 1, 0},
 {0, 1, 1, 3, 1, 1, 0},
 {0, 1, 1, 1, 1, 1, 0},
 {0, 0, 1, 1, 1, 0, 0},
 {0, 0, 0, 0, 0, 0, 0}
 }

local area = createCombatArea(arr)
setCombatArea(combat, area)

function onCastSpell(cid, var)
	return doCombat(cid, combat, var)
end
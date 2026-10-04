-- Poison arrow, 7.4: an arrow hit (physical, the distance formula with the arrow's attack from items.xml, armor
-- applies, no shield block) that also poisons. Poison power 50 (tibiantis-notes poison "Poison Arrows"), dealt the
-- 7.4 way: 5% of what is left, rounded up, every 4 s - 3 x4, 2 x9, 1 x20 = 50.
-- It used to do poison damage from a magic level formula (0.1-0.2 x magic power + 30) and ignore the skill.
local combat = createCombatObject()
setCombatParam(combat, COMBAT_PARAM_BLOCKARMOR, 1)
setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_PHYSICALDAMAGE)
setCombatParam(combat, COMBAT_PARAM_DISTANCEEFFECT, CONST_ANI_POISONARROW)
setCombatFormula(combat, COMBAT_FORMULA_SKILL, 0, 0, 1, 0)

local condition = createConditionObject(CONDITION_POISON)
setConditionParam(condition, CONDITION_PARAM_DELAYED, 1)
addDamageCondition(condition, 4, 4000, -3)
addDamageCondition(condition, 9, 4000, -2)
addDamageCondition(condition, 20, 4000, -1)
setCombatCondition(combat, condition)

local VARIANT_TARGETPOSITION = 3

function onUseWeapon(cid, var)
	if var.type == VARIANT_TARGETPOSITION then
		-- a miss (WeaponDistance::useWeapon sends it to a tile around the target): no damage, as other ammunition
		doSendDistanceShoot(getCreaturePosition(cid), var.pos, CONST_ANI_POISONARROW)
		doSendMagicEffect(var.pos, CONST_ME_POFF)
		return true
	end
	return doCombat(cid, combat, var)
end

-- Burst arrow, 7.4: physical damage of 0-60% magic power (level x 2 + magic level x 3, at least 100) on every
-- creature in the 3x3 around the tile it lands on (tibiantis-notes Magic "Burst Arrow 0 60", distance_calculator;
-- TibiaWiki rev 93104). Armor takes its part ("magic power to overcome ... monster armor", tibiantis-notes Classes);
-- shields do not block distance attacks (distance_calculator: "Shielding does not reduce damage for PvE or PvP
-- distance attacks"). A miss lands on a tile of the 3x3 around the target (WeaponDistance::useWeapon) and still
-- explodes there.
local combat = createCombatObject()
setCombatParam(combat, COMBAT_PARAM_BLOCKARMOR, 1)
setCombatParam(combat, COMBAT_PARAM_TYPE, COMBAT_PHYSICALDAMAGE)
setCombatParam(combat, COMBAT_PARAM_EFFECT, CONST_ME_FIREAREA)
setCombatParam(combat, COMBAT_PARAM_DISTANCEEFFECT, CONST_ANI_BURSTARROW)
setCombatFormula(combat, COMBAT_FORMULA_LEVELMAGIC, 0, 0, -0.6, 0)

local area = createCombatArea( { {1, 1, 1}, {1, 3, 1}, {1, 1, 1} } )
setCombatArea(combat, area)

function onUseWeapon(cid, var)
	return doCombat(cid, combat, var)
end

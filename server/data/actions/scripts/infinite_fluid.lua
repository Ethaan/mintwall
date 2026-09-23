-- Test-character item, not 7.4: a vial with action id 64000 works like a normal one (fluids.lua)
-- and, for the characters in config.lua InfiniteItemPlayers only, is filled again after every use.
dofile(getDataDir() .. 'actions/scripts/fluids.lua')
local useFluid = onUse

function onUse(cid, item, frompos, item2, topos)
	-- The same action id marks the never-ending runes and amulets: leave those to the engine
	-- (returning false lets the rune be cast; Item::isInfiniteTestItem keeps its charges)
	local fluid = isItemFluidContainer(item.itemid)
	if(fluid ~= true and fluid ~= 1) then
		return false
	end
	local ret = useFluid(cid, item, frompos, item2, topos)
	-- only for the characters in config.lua InfiniteItemPlayers; anyone else drinks it empty
	if(isAllowedToUseInfinite(cid)) then
		doTransformItem(item.uid, item.itemid, item.type)
	end
	return ret
end

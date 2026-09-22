-- Test-character item, not 7.4: a vial with action id 64000 works like a normal one (fluids.lua)
-- but is filled again with the same fluid after every use.
dofile(getDataDir() .. 'actions/scripts/fluids.lua')
local useFluid = onUse

function onUse(cid, item, frompos, item2, topos)
	local ret = useFluid(cid, item, frompos, item2, topos)
	doTransformItem(item.uid, item.itemid, item.type)
	return ret
end

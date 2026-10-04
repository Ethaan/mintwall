-- /sellhouse <name>: the engine's house transfer (Commands::sellHouse offers the house document in a trade; the house
-- changes hands when the trade completes, House::executeTransfer). This runs first and refuses a receiver who may not
-- have the house (data/lib/houses.lua houseTransferProblem: premium, one house per account, guildhalls for guild
-- leaders); otherwise it lets the engine's command go on (return true).

dofile(getDataDir() .. 'lib/houses.lua')

function onSay(cid, words, param)
	local house = getHouseByPlayerGUID(getPlayerGUID(cid))
	local name = string.gsub(param or "", "^%s*(.-)%s*$", "%1")
	if house == nil or house == false or name == "" then
		return true                    -- the engine's answers ("You do not own any house." ...)
	end
	local partner = getPlayerByNameWildcard(name)
	if partner == nil or partner == false or partner == 0 or not isPlayer(partner) then
		return true                    -- "Trade player not found."
	end
	houseRequestsTable()
	local problem = houseTransferProblem(getPlayerGUID(partner), house)
	if problem ~= nil then
		doPlayerSendTextMessage(cid, MESSAGE_STATUS_SMALL, problem)
		return false
	end
	return true
end

-- Timed save (docs/production-plan.md §3): players, houses and the map every SaveInterval seconds
-- (config.lua). Without it only logouts and /save saved, so a crash lost all progress since login.
local lastSave = os.time()

function onThink(interval)
	local every = tonumber(getConfigValue("SaveInterval")) or 600
	if os.time() - lastSave < every then
		return true
	end
	lastSave = os.time()
	doSaveServer(0, 1)                        -- 0: no house rent (the global save's job); 1: changed houses only
	return true                               -- Game::saveServer logs "> Server saved in N ms"
end

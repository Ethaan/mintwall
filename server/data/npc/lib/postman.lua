-- The Postman Missions Quest (docs/reference-74/quests.md): what Kevin, the post officers, the captains and the quest
-- objects share. TibiaWiki 2005/2006 (the 7.x spoiler and transcripts): 10 missions, an ADVANCEMENT after every second
-- one - Assistant Postman ("All Postofficers will charge you less money from now on": parcels 10 gp, letters 5 gp -
-- TibiaWiki 2006, Wally / Letter), Postman (Post Officer's Hat), Grand Postman ("Most captains around the world have an
-- agreement with our guild to transport our privileged members, like you, for less gold": 10 gp less a trip, decided
-- with the user 2026-09-30), Grand Postman for Special Operations (a post horn), Arch Postman (the royal mailboxes).
--
-- Storages above 65535 (no quest chest's unique id can clash); the old port's 250-258 are no longer used.
POSTMAN = 70200            -- progress, POSTMAN_* below
POSTMAN_LEGS = 70201       -- mission 1: the four passages taken (1 Bluebear, 2 Uzon, 4 Seahorse, 8 Brodrosch)
POSTMAN_BONES = 70202      -- mission 4: bones given so far
POSTMAN_SNIFFED = 70203    -- mission 6: what Noodles sniffed (1 banana skin, 2 dirty fur, 4 moldy cheese)
POSTMAN_MEASURES = 70204   -- mission 7: officers measured (see POSTMAN_OFFICERS)
POSTMAN_MARKWIN = 70205    -- mission 10: 1 = Markwin called his bodyguards

POSTMAN_ROUTES = 1         -- mission 1: travel the four passages
POSTMAN_FOLDA = 2          -- mission 2: fix the jammed mailbox on Folda with a crowbar
POSTMAN_FOLDA_FIXED = 3
POSTMAN_BILL = 4           -- mission 3: the bill for David Brassacres (Assistant Postman from here)
POSTMAN_BILL_DELIVERED = 5
POSTMAN_BONES_MISSION = 6  -- mission 4: 20 bones
POSTMAN_BONES_DONE = 7     -- ask for ADVANCEMENT
POSTMAN_RANK_POSTMAN = 8   -- Postman: the Post Officer's Hat
POSTMAN_PRESENT = 9        -- mission 5: the present (behind the lower right door) for Dermot
POSTMAN_PRESENT_GIVEN = 10
POSTMAN_UNIFORMS = 11      -- mission 6: Hugo
POSTMAN_HUGO_ASKED = 12    -- Hugo: ask Kevin where the pattern came from
POSTMAN_TALPHION = 13      -- Kevin: ask Talphion
POSTMAN_TALPHION_DONE = 14
POSTMAN_ELOISE = 15        -- Kevin: ask Queen Eloise about the uniforms
POSTMAN_ELOISE_DONE = 16
POSTMAN_NOODLES = 17       -- Kevin: find out what smell Noodles hates
POSTMAN_NOODLES_DONE = 18
POSTMAN_HUGO_ORDER = 19    -- Kevin: tell Hugo we order the uniforms
POSTMAN_UNIFORMS_DONE = 20 -- ask for ADVANCEMENT
POSTMAN_RANK_GRAND = 21    -- Grand Postman: 10 gp less a passage
POSTMAN_MEASUREMENTS = 22  -- mission 7: the six officers' measurements
POSTMAN_MEASURED = 23
POSTMAN_WALDO = 24         -- mission 8: find Waldo (his door opens from here), bring his posthorn
POSTMAN_WALDO_DONE = 25    -- ask for ADVANCEMENT
POSTMAN_RANK_SPECIAL = 26  -- Grand Postman for Special Operations: a post horn
POSTMAN_SANTA = 27         -- mission 9: the letter bag (behind the lower left door) into Santa's mailbox on Vega
POSTMAN_SANTA_DONE = 28
POSTMAN_MARKWIN_LETTER = 29 -- mission 10: the letter from his mother to Markwin in Mintwallin
POSTMAN_MARKWIN_DONE = 30  -- ask for ADVANCEMENT
POSTMAN_RANK_ARCH = 31     -- Arch Postman: the royal mailboxes

POSTMAN_OFFICERS = {benjamin = 1, liane = 2, olrik = 4, lokur = 8, dove = 16, chrystal = 32, lokur_asked = 64}
POSTMAN_ALL_MEASURED = 63

PRESENT, LETTER_BAG, WALDOS_POSTHORN, LETTER_TO_MARKWIN = 2331, 2330, 2332, 2333
POST_OFFICERS_HAT, POST_HORN, CROWBAR, BONE, BIG_BONE = 2665, 2078, 2416, 2230, 2231
PARCEL, LETTER = 2595, 2597

function postmanProgress(cid)
	local value = getPlayerStorageValue(cid, POSTMAN)
	return value > 0 and value or 0
end

function postmanHas(cid, key, bit)
	local value = getPlayerStorageValue(cid, key)
	return value > 0 and math.floor(value / bit) % 2 == 1
end

function postmanSet(cid, key, bit)
	if not postmanHas(cid, key, bit) then
		setPlayerStorageValue(cid, key, math.max(getPlayerStorageValue(cid, key), 0) + bit)
	end
end

-- A passage's price for this player: 10 gp less for a Grand Postman (never below 0).
function travelCost(cid, cost)
	if postmanProgress(cid) >= POSTMAN_RANK_GRAND then
		return math.max(cost - 10, 0)
	end
	return cost
end

-- What a post officer charges for a parcel or a letter: 10 / 5 gp for an Assistant Postman and up.
function postalPrice(cid, itemid, cost)
	if postmanProgress(cid) >= POSTMAN_BILL then
		if itemid == PARCEL then
			return math.min(cost, 10)
		elseif itemid == LETTER then
			return math.min(cost, 5)
		end
	end
	return cost
end

-- Mission 1 ("travel with Captain Bluebear's ship from Thais to Carlin ... with Uzon to Edron ... with Captain Seahorse
-- to the city of Venore ... with Brodrosch to the Isle of Cormaya"): a passage with one of them to that town counts.
local LEGS = {
	["Captain Bluebear"] = {bit = 1, town = {x = 32388, y = 31821}},
	["Uzon"] = {bit = 2, town = {x = 33193, y = 31783}},
	["Captain Seahorse"] = {bit = 4, town = {x = 32954, y = 32022}},
	["Brodrosch"] = {bit = 8, town = {x = 33310, y = 31989}},
}

function postmanTravelled(cid, captain, destination)
	local leg = LEGS[captain]
	if leg == nil or postmanProgress(cid) ~= POSTMAN_ROUTES then
		return
	end
	if math.abs(destination.x - leg.town.x) <= 30 and math.abs(destination.y - leg.town.y) <= 30 then
		postmanSet(cid, POSTMAN_LEGS, leg.bit)
	end
end

-- A captain's "bring me to <town>" shortcut: the passage as the travel module would make it.
function travelTo(cid, destination)
	postmanTravelled(cid, getCreatureName(getNpcId()), destination)
	doTeleportThing(cid, destination)
end

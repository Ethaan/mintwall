# Premium in 7.4

What a premium account gave in 7.4 (released 2004-12-14), how mintwall enforces each part, and which tests cover it.

## Sources

| Id | Source |
|---|---|
| TC-Prem | tibia.com "Features of Premium Accounts", last modified 30 Nov 2004 - http://web.archive.org/web/20041208073841/http://www.tibia.com/home/?subtopic=premium |
| TC-World | tibia.com manual "World" (2004-08) - http://web.archive.org/web/20040805140715/http://www.tibia.com:80/guide/?subtopic=manual&section=world |
| TC-Comm | tibia.com manual "Communication" (2004-08) - .../20040805185615/...section=communication |
| TC-Guilds | tibia.com manual "Guilds" (2004-06) - .../20040618090637/...section=guilds |
| TC-Houses | tibia.com manual "Houses" (2004-06) - .../20040619101337/...section=houses |
| TC-Acc | tibia.com manual "Accounts" (2004-08) - .../20040805184930/...section=accounts |
| TC-FAQ | tibia.com FAQ "promotion" (17 May 2004), "premiumaccount" (1 Oct 2004), "free" |
| TW | TibiaWiki revisions of 2005-2006: Levitate oldid 8776 (2005-05-25), Blessings 30381 / 52698 (2006), Outfits 47913 (2006-08, already with the summer-2006 outfits), Private Chat Channel 29856 (2006-02) |
| TA | Tibiantis (a 7.4 server) FAQ https://tibiantis.online/?page=faq and premium page ?page=premium; its spell table docs/reference-74/spells-tibiantis.json |

TC-Prem lists the benefits (verbatim headings): Access to Premium Areas, Improved Login, Cool New Spells, Character
Promotions, Renting Houses, Guild Leadership, Access to a Premium-Only Game World, Improved Chat Options, Account
Personalisation. TA adds: "sleep in bed", "6 additional outfits for premium characters (3 for each sex)".

## What premium gave, and ours

| Benefit (7.4) | Source | Ours | Tests |
|---|---|---|---|
| **Premium areas**: Edron, Darama (Darashia, Ankrahmun), "a further premium area on Rookgaard" (the south-west). "The only way [...] is by boat, so only premium players can go there." Captains sail "provided you are a premium player"; carpets too | TC-Prem, TC-World, TA | Every ship and carpet asks for premium (npc/lib/captain.lua `travel()`, StdModule.travel `premium = true`: Chemar, Pino, Uzon, Pemaret, Eremo, Brodrosch, Gurbasch); King's Bridge (action id 50003, movements/scripts/premium_tile.lua); the Gatekeeper; Lee'Delle and Norma trade with premium only. The free ferries (Ice Islands, Dalbrect, Captain Jack) go to free land. Premium areas worked out from the map (creaturescripts/lib/premium_areas.lua) | test_premium.py `test_a_free_account_is_refused_every_trip_into_a_premium_area` (9 trips from free ground), `test_a_premium_account_flies_from_femor_hills_to_darashia`, `test_every_npc_trip_into_a_premium_area_takes_premium_accounts_only`; test_travel.py `test_ships_take_premium_players_only`; test_rookgaard.py King's Bridge, Gatekeeper, Norma; test_premium_expiry.py `test_premium_areas_match_the_map` (no free tile reachable on foot inside a premium box) |
| **Premium runs out**: moved out of the premium area at the next login, house lost at the next server save, promotion suspended, the worn premium outfit kept until changed | TA (decided with the user 2026-10-03) | creaturescripts/scripts/login.lua `premiumExpired`, globalevents/scripts/serversave.lua, ioplayer.cpp, protocolgame.cpp parseSetOutfit | test_premium_expiry.py, test_server_save.py, test_death.py |
| **Spells**: "The mighty wizards from the magic guild of Edron have developed new spells. Cast haste [...] Ultimate Explosion! [...] premium players simply have more spells to cast" | TC-Prem; TA "learn new spells" | The spells only taught in Edron (Puffels, Ursula, Gundralph, Zoltan) and on Eremo's isle - Tibiantis' teacher table, npc/lib/spells74.lua: 15 sorcerer, 20 druid, 6 paladin, 5 knight spells, e.g. Haste, Strong Haste, Magic Rope, Levitate, Magic Wall, Ultimate Explosion, Paralyze, Berserk. The teachers do not check premium: a free account never meets them. **Decided with the user 2026-10-04**: all 28 of them (no free-ground teacher teaches them to any vocation) need premium to cast too - spells.xml `prem="1"` (was Levitate alone, TW Levitate 2005); a character whose premium ran out loses them until renewed; runes made with them stay usable by anyone. Refusal: "You need a premium account to use this spell." (spells.cpp, NEEDS REBUILD; was "You need a premium account.") | test_premium.py `test_the_spells_of_the_edron_magic_guild_are_taught_in_premium_areas_only`, `test_the_premium_spells_are_the_ones_taught_in_premium_areas_only` (spells.xml against the teachers), `test_a_free_account_cannot_cast_a_premium_spell_it_knows` (4, wait on the rebuild), `test_a_premium_account_casts_the_premium_spell` (4), `test_a_free_account_casts_a_spell_taught_on_free_ground` (4), `test_levitate_needs_premium_to_cast`; quests/kazordoon/test_paradox_tower.py `test_paradox_tower_levitate_is_premium` |
| **Promotion**: level 20, 20,000 gp, "only available to premium players"; faster regeneration, less death loss | TC-FAQ, TC-Prem, TA | npc/lib/npcsystem/modules.lua `promotePlayer` ("You need a premium account in order to get promoted.") | test_promotion.py (free account refused), test_death.py |
| **Houses**: "Premium players are allowed to rent houses"; guildhalls "only by guild leaders" | TC-Prem, TC-Houses | lib/houses.lua (/buyhouse request checks premium, again at the server save) | test_houses.py `test_buying_a_house_end_to_end` ("You need a premium account."), `test_sellhouse_keeps_one_house_per_account` |
| **Beds** (house beds, offline regeneration) | TA "sleep in bed" (TC-Houses describes beds, no premium word) | config.lua `PremOnlyBeds = true` (beds.cpp BedItem::canUse) | test_premium.py `test_a_free_account_cannot_sleep_in_a_bed`, `test_a_premium_account_sleeps_in_its_bed` |
| **Outfits**: citizen, hunter, mage, knight for all; nobleman/noblewoman, summoner, warrior for premium | TA ("3 for each sex"), TW Outfits 2006 | protocolgame.cpp: the outfit dialog offers 128-131 / 136-139 free, up to 134 / 142 premium; parseSetOutfit refuses the others | test_premium.py `test_the_outfit_dialog_offers_the_premium_outfits_to_premium_accounts_only` (4), `test_a_free_account_cannot_wear_a_premium_outfit`, `test_a_premium_account_wears_a_premium_outfit`; test_premium_expiry.py (kept outfit) |
| **Private chat channel**: "Premium players are allowed to open up private chat channels" (anyone can be invited) | TC-Prem, TC-Comm, TW | chat.cpp: offered in the channel list to premium only; **fixed**: the create packet (0xAA) itself is now refused for a free account (it was not checked) - NEEDS REBUILD | test_premium.py `test_the_private_chat_channel_is_offered_to_premium_accounts_only` (2), `test_only_a_premium_account_opens_a_private_chat_channel` (2; the free case waits on the rebuild) |
| **VIP list**: "up to 20 names [...] premium players have their VIP lists extended to a total of 50" | TC-Comm, TC-Prem | **fixed**: player.cpp Player::addVIP - 20 without premium, the group's maxviplist (50) with it; was 51 for everyone (`>` let one more in). A list loaded at login is kept whole (premium ran out: names kept, none added) - NEEDS REBUILD | test_premium.py `test_the_vip_list_holds_20_names_or_50_with_premium` (2; wait on the rebuild) |
| **Blessings**: "can be obtained by any player [...] One blessing [Eremo's Wisdom of Solitude, on his premium isle] and the promotion require premium accounts" | TW Blessings 2005-2006 | **fixed**: Humphrey's Embrace of Tibia (Carlin) was premium-only (npc/scripts/Humphrey.lua); Norf, Edala, Kawill/Pydar free; Eremo premium | test_premium.py `test_a_free_account_is_blessed_on_free_ground` (Norf, Humphrey, Edala); test_death.py blessings |
| **Improved login**: "you will be able to log in on all game worlds even if the regular player limit has already been reached" | TC-Prem | waitlist.cpp: a premium player goes ahead of every free one in the waiting list, but still waits for a free slot (MaxPlayers 100) | none - see question 3 |
| **Guild leadership**: found a guild; the leader and vice-leaders must be premium | TC-Prem, TC-Guilds, TA "found guilds" | No guild management in game or on a website yet (guilds only in the database) | none - for the website |
| **Premia** (premium-only world), **account personalisation**, sex change (5 premium days), tutor applications | TC-Prem, TC-Acc | not applicable (one world, no website) | - |
| Depot size, regeneration, skills, items | - | No premium difference in 7.4 (no premium-only items: no `prem`/`premium` attribute in weapons.xml / movements.xml) | - |

Not found in any 7.4 source and so not done: a
premium depot limit (8.x), premium-only doors in towns.

## How players got premium

7.4: bought on tibia.com - "log into your account and click on 'Get Premium Account'" (TC-FAQ); the order (credit card,
bank transfer, later game codes) adds premium days to the account; the client shows the days left at login. Premium
time could not be bought in game.

Ours: `accounts.premend` (a Unix time; read as 32 bit, so no later than 2038) - set by hand in the database (the seed
accounts 2-6 have it). No payment system, no GM command (Lua has `doPlayerAddPremiumDays`). Question 1.

## Findings outside premium

- **Fixed (NEEDS REBUILD)**: Levitate was only understood as `exani hur "up` / `exani hur "down`: spells.cpp `Spells::getInstantSpell` treated any
  text after the words that does not start with ` "` as "not this spell", so `exani hur up` (the 7.4 words, TW
  2005 "exani hur up / exani hur down") was plain speech. Now a spell with a parameter takes the rest of the text,
  quoted or not (`exani hur up`, `exiva Name`, `exura sio Name`, `utevo res rat`); a spell without one still only
  allows a quote after its words. test_premium.py `test_levitate_up_and_down` (3 forms).

## Open questions

1. How do players get premium? Recommended: a GM command (`/premium <name>, <days>`, a talkaction around
   doPlayerAddPremiumDays / accounts.premend) now, the website later; no payment system and no in-game premium item
   (Tibiantis' piggy bank is not 7.4).
2. ~~Premium spells at cast time~~ - answered 2026-10-04: every spell taught only in premium areas needs premium.
3. Improved login: let premium players in past MaxPlayers (and up to what hard cap), or keep "premium first in the
   waiting list"? Recommended: keep while MaxPlayers is far above the player count.
4. VIP list when premium runs out: kept whole (no new names past 20) - or cut to 20? Recommended: kept.
5. ~~Levitate without the quote~~ - done (spells.cpp, needs the rebuild).

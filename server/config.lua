--- DIRECTORY PATH ---

    DataDir = "data/"

--- BANS ---

    NotationsToBan = 3
    WarningsToFinalBan = 4
    WarningsToDeletion = 5
    BanLength = 1 * 24 * 60 * 60   -- bans by a gamemaster; the automatic ban for unjustified kills is 7 / 30 / 60 / 90... days (Player::addUnjustifiedDead)
    FinalBanLength = 7 * 24 * 60 * 60
    IPBanishmentLength = 24 * 60 * 60
    KillsToBan = 7   -- no longer used: 7.4 rules in Player::addUnjustifiedDead (ban at 6 a day / 10 a week / 20 a month)

--- COMBAT ---

    -- World type
    -- options: pvp, no-pvp, pvp-enforced
    WorldType = "pvp"

    -- Exhausted time in ms (1000 = 1 second) for yelling
    Exhausted = 1000

    -- Exhausted time in ms (1000 = 1 second) for aggressive spells/weapons
    FightExhausted = 2000

    -- Exhausted time in ms (1000 = 1 second) for none-aggressive spells/weapons
    HealExhausted = 1000

    -- How many ms to add if the player is already exhausted and tries to yell (1000 = 1 second)
    ExhaustedAdd = 200

    -- How long does the player has to stay out of fight to get pz unlocked in ms (1000 = 1 second)
    PZLock = 60000   -- 7.4: 60 s after the last violence (tibia.com manual 4.3.4, 2005; tests/test_skulls.py)

    -- How long a field belongs to a player before it no longer causes PZ lock for the owner
    FieldOwnershipDuration = 5000

    -- In mili seconds
    TimeToDecreaseFrags = 24 * 60 * 60 * 1000   -- no longer used (see KillsToRedSkull)

    -- Time white skull will remain after killing a player, in minutes
    WhiteSkullTime = 15   -- minutes; 7.4: a killer is blocked 15 min (tibia.com manual 4.3.4, 2005; TibiaWiki White Skull 2006)

    -- amount of kills that leads to red skull
    KillsToRedSkull = 5   -- no longer used: red skull at 3 a day / 5 a week / 10 a month, for 30 days

    -- Remove ammunition
    -- If false, ammunition will not be removed when using distance weapons
    -- (or other weapons that use ammunition)
    RemoveAmmunition = true

    -- Remove rune charges
    -- This only applies to runes done using the default functions. 
    -- Custom runes made using actions will not be affected.
    RemoveRuneCharges = true

    -- Remove weapon charges
    -- Set to false to disable charges disappearing from weapons on use
    RemoveWeaponCharges = true

    -- Top player on a stacked tile will be unable to heal
    UHTrap = true

---- CONNECTION ----

    -- Server ip (the ip that server listens on)
    IP = "127.0.0.1"

    -- Server port (the port that server listens on)
    Port = "7171"

    -- How many logins attempts until ip is temporary disabled 
    -- Set to 0 to disable
    LoginTries = 5

    -- How long the retry timeout until a new login can be made (without disabling the ip)
    RetryTimeout = 5000

    -- How long the player need to wait until the ip is allowed again
    LoginTimeout = 60 * 1000

    -- Allow clones (multiple logins of the same char)
    AllowClones = false

    -- Only one player online per account
    CheckAccounts = false
	
	-- Kick player when trying to log on his character
	KickOnLogin = false

---- DATABASE ----

    -- SQL type
    -- options: mysql, sqlite, odbc or pgsql
    SQL_Type = "sqlite"

    --- SQL connection part
    SQL_DB   = "db.db3"

    -- These settings are not used by SQLite
    SQL_Host = "localhost"
    SQL_Port = 3306
    SQL_User = "root"
    SQL_Pass = ""

---- HOUSES ----

    -- House rent period
    -- Options: daily, weekly, monthly
    HouseRentPeriod = "monthly"

	
	-- Beds only for premium players
    PremOnlyBeds = true

--- INFO ---

    -- Login message
    LoginMsg = "Welcome to Mintwall."

    -- Server name
    ServerName = "Mintwall"

    -- World name
    WorldName = "Mintwall"

    -- Server owner name
    OwnerName = "Mintwall"

    -- Server owner email
    OwnerEmail = ""

    -- Server url
    URL = ""

    -- Server location
    Location = "Poland"


---- ITEM USAGE ----

    -- Minimum amount of time between actions ('Use') (1000 = 1 second)
    MinActionInterval = 200

    -- Minimum amount of time between extended actions ('Use with...') (1000 = 1 second)
    MinActionExInterval = 1000

---- MAP ----

    -- Map location
    Map = "data/world/Tibia74.otbm"

    -- Mapkind
    -- Options: OTBM for binary map, XML for OTX map
    MapKind = "OTBM"

    -- Type of map storage, 
    -- 'relational' - Slower, but possible to run database queries to change all items to another id for example.
    -- 'binary' - Faster, but you cannot run DB queries.
    -- To switch, load server with the current type, change the type in config.lua 
    -- type /reload config and the save the server with /closeserver serversave
    MapStoreType = "binary"

---- RATES ----

    -- Rates (experience, skill, magic level, loot and spawn)
    RateExp = 1
    RateSkill = 1
    RateMag = 1
    RateLoot = 1
    -- Respawn speed: each spawn spot's time (data/world/Tibia74-spawns.xml, CipSoft's) is divided by it.
    -- 1 = 7.x respawn (src/spawn.cpp); the test server uses 20 (tests/tibia74/server.py).
    RateSpawn = 1


--- SPAWNS ---

    -- Despawn configs
    -- How many floors can a monster go from his spawn before despawning
    DespawnRange = 2

    -- How many square metters can a monster be far from his spawn before despawning
    DespawnRadius = 50

--- STATUS ---

    -- Message Of The Day box that you sometimes get before you choose characters)
    MOTD = "Welcome to Mintwall!"
    MOTD_Num = "2"

    -- Max number of players allowed
    MaxPlayers = "100"
	
--- WAR ---

	-- Players with same Guild ID can't attack each other
	TeamMode = false
	
	-- The damage percent guild members deal to each other with magic spells/runes
	-- Works only with TeamMode on
	DamagePercent = 20

--- OTHER ---

    -- Accounts password type
    -- options: plain, md5, sha1
    -- pbkdf2: salted PBKDF2-HMAC-SHA256 (docs/production-plan.md §2). Rows still stored as typed (seed.sql,
    -- tests) log in and are rehashed on their first login. plain / md5 / sha1 are the old unsalted modes.
    PasswordType = "pbkdf2"
    -- PBKDF2 iterations for new hashes (OWASP 2023: 600000); older entries are rehashed on login
    PasswordIterations = 600000

    -- Seconds between timed saves of players, houses and the map (data/globalevents/scripts/save.lua).
    -- Without it a crash lost everything since each player logged in.
    SaveInterval = 600

    -- Daily server save (data/globalevents/scripts/serversave.lua; decided with the user 2026-10-04: like
    -- Tibiantis, 9:00 CET with about 10 minutes offline, but at an hour of our own). At ServerSaveHour:00 (the
    -- machine's local time) everyone is kicked, everything saved, house rents collected, houses of owners without
    -- premium released (items to the depot of the house's town), then the server exits with code 10 so the
    -- supervisor restarts it (docs/production-plan.md, "Restart" - without one it stays down). Warnings 5, 3 and 1
    -- minutes before; no logins in the last 5 minutes.
    ServerSaveEnabled = true
    ServerSaveHour = 6          -- decided with the user 2026-10-04: early morning (5 or 6); local time of the server machine

    -- Max number of messages a player can say before getting muted (default 4), set to 0 to disable muting
    MaxMessageBuffer = 4

    -- Save client debug assertion reports
    SaveClientDebug = false

    -- Should the server use account balance system or depot system for paying houses?
    UseAccBalance = false

    -- Time after player will be warned and kicked, in miliseconds
    IdleTimeKick = 900000       -- 15 minutes, like real Tibia
	IdleTimeWarning = 840000    -- warned at 14 minutes

    -- Test characters whose items with action id 64000 never run out (runes, amulets, fluids).
    -- Comma-separated names, any case. Empty = nobody. Never put a real player here.
    -- Blessings (7.4 had the five of 7.2, 10000 gp each, each -1 point of death loss). Read by the
    -- NPC system (StdModule.bless): "yes" to sell them; only-premium lets NPCs mark some as premium.
    blessings = "yes"
    blessingsOnlyPremium = "yes"

    InfiniteItemPlayers = "Centurion, Gandalf, Radagast, Legolas"

    -- Level on which player will get rooked
    LevelToRook = 5

    -- TownId to which player will be teleported
    RookTempleId = 1

    -- if your website is not showing player deaths, then keep this as false
    StorePlayerDeaths = false

    -- ID of temple to which player will get teleported when his prem end out
    -- 0 to disable
    -- not tested
    FACCTempleID = 0

 

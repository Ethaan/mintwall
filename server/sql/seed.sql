-- Local test data. Account 111111 / password "tibia" (PasswordType = "plain" in config.lua)
INSERT INTO "groups" ("id", "name", "flags", "access", "maxdepotitems", "maxviplist") VALUES (1, 'Player', 0, 0, 1000, 50);
INSERT INTO "accounts" ("id", "password") VALUES (111111, 'tibia');
-- Position 0,0,0 = spawn at the temple of town_id (1 = Rookgaard in Tibia74.otbm)
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "health", "healthmax", "mana", "manamax", "cap", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('Mintwall', 111111, 1, 1, 0, 1, 150, 150, 0, 0, 400, 0, 0, 0, X'', 0, 1);

-- God account for local administration: 9 / 9. Change it before exposing the server to anyone.
INSERT INTO "groups" ("id", "name", "flags", "access", "maxdepotitems", "maxviplist") VALUES (3, 'God', 5480948670456, 3, 10000, 200);
INSERT INTO "accounts" ("id", "password") VALUES (9, '9');
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "health", "healthmax", "mana", "manamax", "cap", "looktype", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('GM Mintwall', 9, 3, 1, 0, 1, 150, 150, 0, 0, 400, 75, 0, 0, 0, X'', 0, 2);

-- Quick manual test accounts: 1 / 1 free, 2 / 2 premium (premend = May 2033; the server reads it as 32-bit)
INSERT INTO "accounts" ("id", "password") VALUES (1, '1');
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "experience", "health", "healthmax", "mana", "manamax", "cap", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('Free Tester', 1, 1, 1, 0, 1, 0, 150, 150, 0, 0, 400, 0, 0, 0, X'', 0, 1);
INSERT INTO "accounts" ("id", "password", "premend") VALUES (2, '2', 2000000000);
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "experience", "health", "healthmax", "mana", "manamax", "cap", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('Premium Tester', 2, 1, 1, 0, 8, 4200, 185, 185, 35, 35, 435, 0, 0, 0, X'', 0, 1);

-- Manual test account 222222 / test: one fresh Rookgaard character, one level 8 next to the Oracle
INSERT INTO "accounts" ("id", "password") VALUES (222222, 'test');
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "experience", "health", "healthmax", "mana", "manamax", "cap", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('Rook Tester', 222222, 1, 1, 0, 1, 0, 150, 150, 0, 0, 400, 0, 0, 0, X'', 0, 1);
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "experience", "health", "healthmax", "mana", "manamax", "cap", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('Oracle Tester', 222222, 1, 1, 0, 8, 4200, 185, 185, 35, 35, 435, 32104, 32192, 6, X'', 0, 1);

-- Account 3 / 3: "Centurion", premium level 171 elite knight in Thais, for exploring the mainland.
-- Magic level 9, sword/shield 90. The backpack's mana fluid refills itself (action id 64000,
-- actions/scripts/infinite_fluid.lua) - a test item, not 7.4. Runes hold 100 charges.
INSERT INTO "accounts" ("id", "password", "premend") VALUES (3, '3', 2000000000);
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "experience", "maglevel", "health", "healthmax", "mana", "manamax", "cap", "looktype", "lookhead", "lookbody", "looklegs", "lookfeet", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('Centurion', 3, 1, 1, 8, 171, 80461000, 9, 2700, 2700, 850, 850, 4650, 131, 78, 69, 58, 114, 0, 0, 0, X'', 0, 2);
UPDATE "player_skills" SET "value" = 90 WHERE "skillid" IN (2, 5) AND "player_id" = (SELECT "id" FROM "players" WHERE "name" = 'Centurion');
INSERT INTO "player_storage" ("player_id", "key", "value") SELECT "id", 30001, 1 FROM "players" WHERE "name" = 'Centurion';
INSERT INTO "player_items" ("player_id", "pid", "sid", "itemtype", "count", "attributes")
SELECT p."id", i.pid, i.sid, i.itemtype, i.count, i.attributes FROM "players" p, (
          SELECT 1 AS pid, 101 AS sid, 2498 AS itemtype, 1 AS count, X'' AS attributes  -- royal helmet
    UNION ALL SELECT 3, 102, 1988, 1, X''       -- backpack
    UNION ALL SELECT 4, 103, 2656, 1, X''       -- blue robe
    UNION ALL SELECT 5, 104, 2400, 1, X''       -- magic sword
    UNION ALL SELECT 6, 105, 2520, 1, X''       -- demon shield
    UNION ALL SELECT 7, 106, 2470, 1, X''       -- golden legs
    UNION ALL SELECT 8, 107, 2195, 1, X''       -- boots of haste
    UNION ALL SELECT 102, 108, 2006, 7, X'0400FA'   -- mana fluid (type 7), action id 64000: refills
    UNION ALL SELECT 102, 109, 2268, 100, X''   -- sudden death rune
    UNION ALL SELECT 102, 110, 2293, 100, X''   -- magic wall rune
    UNION ALL SELECT 102, 111, 2273, 100, X''   -- ultimate healing rune
    UNION ALL SELECT 102, 112, 2120, 1, X''     -- rope
    UNION ALL SELECT 102, 113, 2554, 1, X''     -- shovel
    UNION ALL SELECT 102, 114, 2553, 1, X''     -- pick
) i WHERE p."name" = 'Centurion';
-- Centurion's jewellery: amulet of loss (1 charge) worn, a time ring worn with the longest possible
-- time left (duration attribute 0x10 = 2^31-1 ms, ~24.8 days of wearing: effectively infinite),
-- and a ring of the sky in the backpack (one ring slot).
INSERT INTO "player_items" ("player_id", "pid", "sid", "itemtype", "count", "attributes")
SELECT p."id", i.pid, i.sid, i.itemtype, i.count, i.attributes FROM "players" p, (
          SELECT 2 AS pid, 115 AS sid, 2173 AS itemtype, 1 AS count, X'' AS attributes  -- amulet of loss
    UNION ALL SELECT 9, 116, 2169, 1, X'10FFFFFF7F'   -- time ring, ~24.8 days
    UNION ALL SELECT 102, 117, 2123, 1, X''           -- ring of the sky
) i WHERE p."name" = 'Centurion';
-- ...and 100 crystal coins (1,000,000 gp) in the backpack
INSERT INTO "player_items" ("player_id", "pid", "sid", "itemtype", "count", "attributes")
SELECT "id", 102, 118, 2160, 100, X'' FROM "players" WHERE "name" = 'Centurion';
-- ...and never-ending supplies (action id 64000: charges are never used up, Item::isInfiniteTestItem):
-- an ultimate healing rune, an explosion rune and a stone skin amulet, in the backpack
INSERT INTO "player_items" ("player_id", "pid", "sid", "itemtype", "count", "attributes")
SELECT p."id", 102, i.sid, i.itemtype, i.count, X'0400FA' FROM "players" p, (
          SELECT 119 AS sid, 2273 AS itemtype, 100 AS count    -- ultimate healing rune
    UNION ALL SELECT 120, 2313, 100                            -- explosion rune
    UNION ALL SELECT 121, 2197, 5                              -- stone skin amulet
) i WHERE p."name" = 'Centurion';

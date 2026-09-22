-- Local test data. Account 111111 / password "tibia" (PasswordType = "plain" in config.lua)
INSERT INTO "groups" ("id", "name", "flags", "access", "maxdepotitems", "maxviplist") VALUES (1, 'Player', 0, 0, 1000, 50);
INSERT INTO "accounts" ("id", "password") VALUES (111111, 'tibia');
-- Position 0,0,0 = spawn at the temple of town_id (1 = Rookgaard in Tibia74.otbm)
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "health", "healthmax", "mana", "manamax", "cap", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('Mintwall', 111111, 1, 1, 0, 1, 150, 150, 0, 0, 400, 0, 0, 0, X'', 0, 1);

-- God account for local administration. Change the password before exposing the server to anyone.
INSERT INTO "groups" ("id", "name", "flags", "access", "maxdepotitems", "maxviplist") VALUES (3, 'God', 5480948670456, 3, 10000, 200);
INSERT INTO "accounts" ("id", "password") VALUES (999999, '833qzdzobz');
INSERT INTO "players" ("name", "account_id", "group_id", "sex", "vocation", "level", "health", "healthmax", "mana", "manamax", "cap", "looktype", "posx", "posy", "posz", "conditions", "rank_id", "town_id")
VALUES ('GM Mintwall', 999999, 3, 1, 0, 1, 150, 150, 0, 0, 400, 75, 0, 0, 0, X'', 0, 2);

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

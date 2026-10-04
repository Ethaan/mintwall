# Spawn times and radius vs 7.4

Task (task.md, Monsters): "Check spawn times/radius are sane for 7.4". Research 2026-10-03.

## Summary

- **Positions are authentic, times are not.** Our 18,666 monster entries (server/data/world/Tibia74-spawns.xml,
  222222's 7.4 real map) match CipSoft-derived spawn data almost exactly: 18,645 of them have a same-name twin on
  the same floor within 8 tiles in Nostalrius' file (most at distance 0-1). But **every** entry (monsters and
  NPCs) has `spawntime="60"`, the map editor's default. Cip's data has 600 s for 78% of the same spots and
  300-20,000 s for the rest.
- With our engine a killed monster comes back after **60-120 s** (see Engine). In Cip's data it is 600 s,
  randomised and scaled by the number of players online (5-10 min on a small world). That makes our respawn
  about **5-10x faster** than 7.x. This changes the whole game feel, so it is not changed here (question Q1).
- **Fixed (clear data errors):** the 8 tomb pharaohs and the Black Knight respawned every 60 s.
  All references differ from that (below).
- Radius: 97% of our spawn blocks have radius 1 (Cip: mostly 3-5). In our engine the radius only decides
  **overspawn**: a monster that leaves its spawn zone frees its slot. With radius 1 that happens very easily
  (Q4).
- No boss, rare or NPC-like monsters are spawned wrongly. Orshabaal, Ferumbras, Demodras, the Horned Fox,
  Dharalion, General Murius, Grorlam, Necropharus, the Old Widow, the Evil Eye and Yeti are not in our spawn
  file. That matches the 2007 wiki ("Bosses do not spawn like normal creatures").

## Sources

| id | source | what it says |
|---|---|---|
| TW-Respawn | TibiaWiki "Respawn": rev 23340 (2005-11-05), **32483** (2006-03-13), **38110** (2006-05-24), last pre-8.0 rev 80739 (2007-01-25) | "Monsters used to respawn on a single spot, but recently this was changed. A monster can now respawn on any square up to ten squares away". "Player presence interrupts respawning (go some squares away and wait there)". |
| TW-Spawn | TibiaWiki "Spawn" rev 51720 (2006-08-28), last pre-8.0 rev 103371 | "Spawns used to be set positions, but in recent updates they have become a little random". So in 7.4 a monster came back on its exact spot. |
| TW-BK | TibiaWiki "Black Knight": rev 22115 (2005-10-14) "slow spawn time"; **rev 57201 (2006-09-26)** "slow spawn time (around a constant 12 minutes not affected by players online)" | Black Knight about 720 s. "Not affected by players online" implies that other spawns were. |
| TW-Demon | TibiaWiki "Demon" rev 8745 (2005-06-04) | Hero Cave: "in one of the rooms where they respawn, they do it even if there are people". |
| TW-Bosses | TibiaWiki "Bosses" rev 106691 (2007-06-18) | Bosses "do not spawn like normal creatures ... rare occasions ... if not killed in one day, they disappear". |
| TW-HornedFox | TibiaWiki "The Horned Fox" rev 80849 (2007-01-25) | "Semi-rare respawn". |
| TI-trivia | tibiantis.info/library/trivia (fetched 2026-10-03). Tibiantis says it uses "the same algorithm as Tibia 7.4" (from its analysis of the leaked engine). | Overspawn: a monster respawns again when the old one "went too far from the spawn site (or changed floor)"; monsters do not move when nobody is near. "Player will block respawns 2 floors above and 2 below when they are underground and all levels above if on surface". Mino Hell: a monster respawns after being roped up 1 floor, or when lured more than 10 squares away. The Black Knight room (8 squares each side) never had two. "The respawn time is not constant, but each time partly randomized and depending on the number of players online." |
| NOST | Ezzz-dev/Nostalrius (GitHub, master): `data/world/spawns.xml`, `src/spawn.cpp`. A 7.7 clone built on CipSoft's files. | Per-spot regen (seconds, table below). `Spawn::getInterval`: for intervals over 500 s, 200 players or fewer = full value; 201-800 players = `200*t/(players/2+100)`; over 800 = 0.4*t; then a random value between t/2 and t. The player check is multi-floor (`getSpectators(..., multifloor=true)`). |
| TOT | tibiaot74 `server/data/world/world-spawn.xml` (scratchpad) | Not Cip-derived (later map, 8.x monsters). 150 s default; pharaohs 360, Ashmunrah 150, Black Knight 600. |
| RL | Qwizer/rlmap740x `data/world/world-spawn.xml` (a 7.40 global map on OTHire) | 60 s default like ours (same map-editor lineage); a few 120-1000. |
| JS | jsengine `data/740/spawns/definitions.json` | One test entry (slime, 4 s). No spawn data to compare. |
| TN | tibiantis-notes.github.io/Creature | Only flee distance from the spawn point. Nothing on timing. |

Caveat: NOST is 7.7 data (2006). Nothing in the sources gives Cip's 7.4 regen values. The 2006 wiki observation
(Black Knight about 12 min) fits the 7.7 order of magnitude, not 60 s.

## Our file (before the fix)

- 8,022 spawn blocks: 18,666 monsters, 303 NPCs.
- spawntime: **60 s for all 18,969 entries.**
- radius: 1 = 7,806 blocks (97%), 2 = 110, 3 = 55, 4 = 24, 5-10 = 24, 14 = 2, 20 = 1. Radius 7-20 is only used by
  NPCs (their walking area).
- Monsters per block: 1 = 2,099, 2 = 2,684, 3 = 2,043, 4 = 855, 5-8 = 333, 9-18 = 8. The largest are 18 spiders
  (32380,32079,10, r3), 12 rats (32573,32215,15), 10 snakes, bugs and orc spearmen.
- No monster lies outside its block's radius. 4 Ghost/Ghoul entries near 33322,32180 have a `z` that differs from
  `centerz`. This is harmless: the engine ignores a monster's `z` and uses `centerz`.
- No radius 0. No huge monster radius.

## Comparison per monster (positions matched within 8 tiles, same floor)

Cip regen (NOST) for our spots: 600 s = 14,512; 300-599 = 1,837; 601-1,799 = 2,034; 1,800 or more = 77; 60-299
= 185 (tomb traps, Rookgaard/sewer rats, sheep, wolves); not matched = 21 (9 "demongoblin" = Cip's "illusion",
which has 600 s).

| monster (ours, n) | ours | NOST median (range) | TOT | RL |
|---|---|---|---|---|
| larva 1442, scarab 866, ghoul 818, skeleton 748, demon skeleton 650, troll 591, ... (most) | 60 | 600 | 150 | 60 |
| rotworm 1235 | 60 | 500 (300-1100) | 150 | 60 |
| dragon 179 | 60 | 700 (500-7500) | 150 | 60 |
| dragon lord 61 | 60 | 600 (550-7200) | 150 | 130 |
| giant spider 43 | 60 | 850 (600-19200) | 150 | 60 |
| behemoth 49 | 60 | 700 (500-6000) | 150 | 60 |
| demon 23 | 60 | 700 (600-20000) | 150 | 60 |
| warlock 19 | 60 | 1000 (550-1200) | 150 | 1000 |
| hero 9 | 60 | 750 | 150 | 60 |
| pig 58 | 60 | 900 | 150 | 60 |
| tomb pharaohs (7) + Ashmunrah | 60 | **600** | 360 (Ashmunrah 150) | 60 |
| black knight 1 | 60 | **2000** | 600 | 60 |
| magic/flame/plague/shredderthrower, deathslicer (tomb traps) | 60 | 60 | 150 / - | 60 |

The full tables come from the scratchpad scripts (an.py, match.py). The comparison is easy to redo:
`Ezzz-dev/Nostalrius/master/data/world/spawns.xml` and the same nearest-twin match.

Cip's rare spots (1,800 s or more) on our map, 77 entries. These are mostly quest guardians:

| where (ours) | monsters | Cip regen |
|---|---|---|
| 33336-33340,31954-31958,15 | 4 demons | 20000 |
| 32439,31985,14 | giant spider | 19200 |
| 32178,31926,2-4 / 32179,31830,12 / 32262,31862,11 / 32968,31759,7 | 3 monks, vampire, mummy, elf | 9999 |
| 32159,31924,7 / 33149,32864,9 | 2 pigs / green djinn | 9000 |
| 32451-32454,32007,13 | 2 dwarf guards + geomancer | 8000 |
| 32688,31844,8 / 32348,32071,12 | dragon / 2 dragon lords (Thais ancient temple) | 7500 / 7200 |
| 33063,31623,15 and 33203,31640,15 (Hero Cave) | 3 demons | 6000 |
| 33152,32864-32868,8 / 32830,31873,8 / 32114,31921,14 / 32164,31954,14 | behemoth, vampire / beholder / mummy / giant spider | 6000 |
| Fibula, Ankrahmun tombs, PoH, Edron, ... | dragons, dragon lords, mummies, banshee, witch | 1800-3600 |
| 32874,31948,11 | black knight | 2000 (wiki: about 720) |
| 32023-32040,32207-32239,8 | 8 rats | 2000 |

## Engine (server/src/spawn.cpp, config.lua)

- **Interval:** `spawntime` x 1000 ms. Values under 10 s are refused. Each spawn block checks every
  min(spawntime of its monsters). A slot is due at `lastSpawn + interval`, but it is only looked at on the
  block's check tick. So a kill waits **between 1x and 2x the spawntime** (60-120 s now). There is no
  randomisation and no players-online scaling.
- **Spot:** a monster comes back on its exact spot (`placeCreature(..., forced)`). This matches 7.4 (TW-Spawn,
  TW-Respawn: random squares only came after 7.4).
- **Player blocking:** `findPlayer` = any player (without IgnoredByMonsters) within ±11 x ±11 tiles **on the
  same floor only** (`getSpectators` default, multifloor=false). When a player is there, the slot's timer
  **restarts from zero**. 7.4 (TI-trivia; NOST uses multifloor) also blocked from 2 floors above and below
  underground, and from all floors above on the surface.
- **Overspawn:** on each check, a monster outside the block's zone (`|dx|,|dy| <= radius` around the block
  centre; the floor is not checked) is let go and its slot respawns. It stays in the world until it despawns
  (DespawnRadius 50 / DespawnRange 2 floors). This is 7.4's overspawn, but with radius 1 it triggers when a
  monster is 2 tiles from its block centre. 7.4: "more than 10 squares" or a floor change (TI-trivia).
- **RateSpawn = 1** (config.lua) caps respawns at 1 monster per block per check. A block of 18 spiders refills
  one spider per minute now, and one per 10-20 min if the times become Cip's.
- NPC `spawntime` is not used (NPCs never respawn).

## Fixed (2026-10-03)

server/data/world/Tibia74-spawns.xml:

| monster | spot | was | now | why |
|---|---|---|---|---|
| Rahemos, Dipthrah, Vashresamun, Morguthis, Mahrdis, Omruc, Thalas, Ashmunrah | their tomb lairs | 60 | **600** | NOST (Cip data) 600 for all eight; TOT 360/150; ours was the editor default. A quest boss coming back every minute is clearly wrong. |
| Black Knight | 32874,31948,11 | 60 | **720** | TW-BK 2006: "around a constant 12 minutes not affected by players online"; TOT 600, NOST 2000. The wiki's observed value is used because our engine has no players-online scaling. |

With the check-tick effect these take 600-1200 s and 720-1440 s. The spawn file is only read at startup, so the
change applies after a server restart. Each tomb test kills its pharaoh once, so the tests are not affected.

## Questions for the user

**Q1 - Global respawn speed (biggest difference).** All 18,657 other monsters respawn after 60-120 s. 7.x
(Cip data) used 600 s for most spots (300-1,100 for common ones), with a random value between t/2 and t, and
faster only above 200 players online. So 7.x on a small world is about 5-10 min, 5-10x slower than ours.
Evidence: NOST per-spot data matching our positions, TI-trivia "partly randomized and depending on the number of
players online", TW-BK 12 min, TW-Respawn tips about waiting for respawn.
Options:
(a) keep 60 s (fast, private-server feel);
(b) take NOST's per-spot values for all 18,645 matched entries (one script; this includes Q3's rare spots);
(c) as (b) plus Cip's randomisation and players-online scaling in spawn.cpp, and a per-slot timer instead of
the block tick;
(d) a uniform value or factor (for example 300 s everywhere).
Recommendation: (c) if 7.4 authenticity wins, otherwise (b). Note: a hunt will feel much emptier. The
`RateSpawn` / block-tick issues (Q5) must be fixed with it.

**Q2 - Respawn blocked from other floors.** Ours checks the same floor only. 7.4 also blocked from ±2 floors
underground and from all floors above on the surface (TI-trivia; NOST). Fix: one line,
`g_game.getSpectators(list, pos, false, true)` in `Spawn::findPlayer`. Recommendation: yes. It is small and
authentic. It needs a rebuild and a test.

**Q3 - Rare / quest-guardian spots** (77 entries with Cip regen 1,800-20,000 s). Examples: the 4 demons at
33336-33340,31954-31958,15 (20,000 s), the Hero Cave demons (6,000), the Thais ancient-temple dragon lords
(7,200), the Kazordoon dwarf guards + geomancer at 32451,32007,13 (8,000), and the Fibula/PoH dragon lords
(1,800-3,600). They all respawn in 60 s now. Recommendation: take Cip's values for these even if Q1 stays (a).
These are the "rare spawn" rooms of the era. (TW-Demon says one Hero Cave room respawned even with people
present. That is not modelled.)

**Q4 - Radius / overspawn distance.** 97% of our blocks have radius 1, so a monster that moves 2 tiles from its
block centre (for example when it chases a player) frees its slot. The slot respawns as soon as no player is
within 11 tiles, and you get a doubled spawn. 7.4: overspawn when lured more than about 10 squares away or onto
another floor. Cip's radii for the same spots are mostly 3-5.
Options:
(a) keep;
(b) take NOST's radius per matched block;
(c) in the engine, a fixed overspawn distance (for example 10) plus a floor change, independent of the radius.
Recommendation: (c). It is closest to the documented 7.4 behaviour and leaves the map data alone. It needs a
spawn.cpp change and a test.

**Q5 - Refill of large blocks and the timer.** RateSpawn=1 and the per-block check tick mean that a block of N
monsters takes N ticks to refill. A kill also waits 1-2x the spawntime, and a player nearby restarts the timer
from zero. If Q1 (b)/(c) is chosen, recommendation: an independent timer per slot, so that each monster comes
back t after its own death; RateSpawn is then only a safety cap.

## Suggested task.md note

- [x] Check spawn times/radius are sane for 7.4
      Done 2026-10-03: docs/reference-74/spawns.md. Our 18,666 spawn positions match CipSoft-derived data
      (Nostalrius 7.7) almost 1:1, but every spawntime is the map editor's 60 s (7.x: 600 s for most spots,
      randomised and players-online scaled; Black Knight about 12 min per the 2006 wiki). Fixed: the 8 tomb
      pharaohs 60 -> 600 s, the Black Knight 60 -> 720 s. Open: Q1 global respawn speed (ours 5-10x faster), Q2 multi-floor
      respawn blocking, Q3 rare/quest-guardian spots, Q4 radius-1 overspawn, Q5 refill/timer.

## Decided 2026-10-04: option (c), with Q2, Q3, Q4 (c) and Q5

- **Data:** `tools/apply-cip-spawntimes.py` sets every monster's spawntime from its Nostalrius twin (same name,
  same floor, nearest within 8 tiles; the Nostalrius entries are kept in `docs/reference-74/nostalrius-spawns.csv`,
  `--fetch` downloads them again). 18,636 twins, 9 kept (the 8 pharaohs 600 s, the Black Knight 720 s), 21 without
  a twin get 600 s. 60 s is left only on Cip's own 60 s spots (112, the tomb traps etc.). NPC entries are untouched.
- **Engine** (`server/src/spawn.cpp`, rules from Nostalrius `src/spawn.cpp` and TI-trivia):
  - one timer per slot, from its monster's death (or overspawn / convince);
  - delay: spawntime over 500 s: shortened only above 200 players online (`200*t/(players/2+100)` up to 800, `0.4*t`
    above), then random between t/2 and t (normal distribution, cut at both ends); 500 s or less: exactly t;
  - a player in view when the slot is due blocks it (a new delay): same floor and +-2 floors underground; on the
    surface its own floor and every floor above (TI-trivia; Nostalrius' multi-floor check also counts the surface
    floors below);
  - overspawn: a monster more than 10 squares from its spot or on another floor frees its slot (checked on every
    step of the monster, `Monster::onCreatureMove`); the block radius no longer decides it;
  - `RateSpawn` (config.lua) now divides every delay (1 = Cip's times). The old meaning (at most N respawns per
    block per check tick) has no use with per-slot timers. The test server uses 20.
- Tests: `tests/test_spawns.py` (data rules; live: a rotworm's respawn window, blocking by a player next to it and
  one floor up).

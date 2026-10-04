# Spell and rune formulas: ours vs Tibia 7.4

Research date: 2026-10-04. Covers every attack and healing spell and rune 7.4 had, plus the field runes and the conjure
counts. Supersedes the spell rows of formulas.md §4-§5 (several of those were fixed since).

## The formula

7.4: `amount = base% × P`, magic power **P = level × 2 + magic level × 3, never below 100** (TN-Magic: "If magic
power is less than 100, spell base damage is used"; TI-Calc; OTL-Mech; OTHire's `max(base, P × base / 100)`). C2+.

Ours: `server/src/combat.cpp` `Combat::getMinMaxValues`, `FORMULA_LEVELMAGIC`: `P = max(100, level*2 + mlvl*3)`,
amount from `P × mina + minb` to `P × maxa + maxb` (the floor was added 2026-09). Scripts with a callback use
`magicPower()` (`data/compat.lua`), the same P. The roll between min and max is `random_range(..., DISTRO_NORMAL)` (a
normal curve clipped to the range, `tools.cpp`); direct damage is halved player against player (`combat.cpp`
`CombatHealthFunc`), damage over time (poison, burning) is not, as in 7.4 (TN-Poison: "PvP damage is not halved for
poison spells").

## Sources

| Key | What | Notes |
|---|---|---|
| TN | tibiantis-notes "Magic" (damage-per-mana table: min/max base per spell) and "poison" pages; `docs/reference-74/tibiantis-notes/Magic.txt`, `poison.txt` | 7.4; marks Tibiantis changes ("classic" values) |
| OTHire | OTHire commit 43d3b1f "Real spell formulas from leaked files" (peonso, 2017-10-11), github.com/Ezzz-dev/OTHire: base and variation per spell | said to come from CipSoft's 7.7 files; used only to corroborate. Its values equal TN's 7.4 ones everywhere they overlap |
| TW | TibiaWiki revisions before 8.0 (2005-05 .. 2007-06), `api.php?action=parse&oldid=<rev>`; revision ids below | notes, rarely numbers |
| TI-Calc | tibiantis.info calculators (formulas.md) | healing |
| OTL-Mech | otland "game mechanics through time" (formulas.md) | 7.x era memories |
| Tibiantis | `docs/reference-74/tibiantis/spells.json`, `spells-tibiantis.json` | mana, levels, charges; no damage |

## Attack spells and runes

`%P` = per cent of magic power. "Ours before" is the value before 2026-10-04; "now" the value in the script.

| Spell / rune | 7.4 | Sources | Ours before | Ours now (file) | Verdict |
|---|---|---|---|---|---|
| Light magic missile (adori) | 10-20 | TN, OTHire 15/5 | 10-20 | same (`attack/light_magic_missile.lua`) | OK |
| Heavy magic missile (adori gran) | 20-40 | TN, OTHire 30/10 | 20-40 | same; measured in `test_combat_formulas.py` | OK |
| Fireball (adori flam) | 15-25 | TN, OTHire 20/5 | 16-33 | **15-25** (`fireball.lua`) | fixed |
| Great fireball (adori gran flam) | 35-65 | TN, OTHire 50/15 | 40 + 30 .. 70 | **35-65** (`great_fireball.lua`) | fixed |
| Explosion (adevo mas hur), physical | 20-100 | TN, OTHire 60/40; TW 83953 "the damage is very random" | 15-90 | **20-100** (`explosion.lua`) | fixed |
| Sudden death (adori vita vis), physical | 130-170 | TN, OTHire 150/20 | 125 + 30 .. 170 | unchanged | **Q1** |
| Energy strike (exori vis) | 35-55 | TN, OTHire 45/10 (OTL-Mech 25-55) | 25-55 | **35-55** (`energy_strike.lua`) | fixed |
| Flame strike (exori flam) | 35-55 | OTHire 45/10 (same as energy strike; TN lists only energy strike; OTL-Mech 25-55) | 25-55 | **35-55** (`flame_strike.lua`) | fixed |
| Force strike (exori mort), physical | 35-55 ? | OTHire 45/10; OTL-Mech 18 (-30) .. 33 | 20-50 | unchanged | **Q2** |
| Fire wave (exevo flam hur) | 20-40 | TN, OTHire 30/10; TW 89085 "about half the damage of a GFB" | 20-40 | same | OK |
| Energy beam (exevo vis lux) | 40-80 | TN, OTHire 60/20 | 40-80 | same | OK |
| Great energy beam (exevo gran vis lux) | 40-200 | TN, OTHire 120/80; TW 89045 "its damage range is quite random" | 40-200 | same | OK |
| Energy wave (exevo mort hur) | 100-200 | TN, OTHire 150/50 | 115-190 | **100-200** (`energy_wave.lua`) | fixed |
| Ultimate explosion (exevo gran mas vis), physical | 200-300 | TN, OTHire 250/50 (OTL-Mech 230 (-30) .. 300) | 192-300 | **200-300** (`ultimate_explosion.lua`) | fixed |
| Poison storm (exevo gran mas pox) | **no hit**; poison of 150-250 in total, 5% of what is left every 4 s | TN (Magic, poison: "A level 200 druid with magic level 80 will cause up to 1600 damage, start at 80 damage"), TW 8830/108058 "poisons the enemy with 200+/-50 ... it won't make full damage as you attack", OTHire 200/50 | a hit of 150-250 %P **plus** a poison of 100 | **poison of 150-250 %P**, no hit, 4 s ticks starting at ceil(total/20) (`poison_storm.lua`) | fixed |
| Envenom (adevo res pox) | no hit; poison of 50-90 in total | TN (Magic, poison), OTHire 70/20 | a fire burn (!) of a fixed 79, any P | **poison of 50-90 %P** as poison storm (`envenom.lua`) | fixed |
| Soulfire (adevo res flam) | no hit; burning of 100-140 in total, 10 a turn | TN, TW 8876 "120+/-20", TW 99343 "10 damage for a number of turns ... depends upon your level and magic level", OTHire 120/20 | a fixed 80 (3×10 + 10×5) | **100-140 %P in 10s**, a turn every 10 s (`soulfire.lua`) | fixed (tick: Q4) |
| Berserk (exori), physical | level-based, see formulas.md §2 | TI-Calc level/25 × 60..100; OTL-Mech 2.2..3.85 × level; OTHire 80/20 "complex formula, not added" | (2L+3ML) × 1.4..1.65 | unchanged | **Q3** |

How the damage-over-time spells work now: a condition's damage is fixed when a script loads (Avesta), so
`poison_storm.lua` and `envenom.lua` build one combat per magic power step of 5 (P 100..1500), each with a poison
condition of min..max = share × P, tick 4 s; the engine (`ConditionDamage::init` / `generateDamageList`) rolls the
total per target and deals it starting at ceil(total/20), falling - the 7.4 "5% of the remaining damage, rounded up"
(TN-Poison). `soulfire.lua` rolls the total in Lua and picks one of 210 prebuilt burns of N × 10.

Note: `data/global.lua`'s `CONDITION_PARAM_MINVALUE` and every constant after it are 2 lower than
`src/enums.h` `ConditionParam_t` (the soul params 12/13 are numbered there even with `__PROTOCOL_76__` off): `MINVALUE`
is 14, not 12. No script used them until now; the new scripts use the numbers directly. Fixing global.lua is
suggested (§Questions, Q7).

## Fields and bombs (damage on the field items)

The rune scripts only create the field (`attack/*field*.lua`, `*bomb.lua`, `*wall.lua`: 1492 fire, 1495 energy, 1496
poison; `combat.cpp` swaps in the non-PvP 1500 / 1503 / 1504 on a no-PvP world or tile); the damage is on the field
item in `data/items/items.xml` (`field` attribute, `items.cpp`: a `damage` before any `ticks` is the hit on stepping in,
the rest come every `ticks` ms; poison `start` 5 spreads `damage` 100 over falling hits). Checked and partly fixed
2026-10-04 (fields task); measured in `tests/test_fields.py`.

TibiaWiki revisions read (pre-8.0; 7.5 came in December 2005, so only revisions up to November 2005 are 7.4):
Fire Field rune 8837 (2005-05), 72254 (2006-12), 85637 (2007-02); Energy Field rune 8844, 46213 (2006-08), 85636
(2007-02); Poison Field rune 55636 (2006-09), 91945 (2007-03); Fire 8305 (2005-06), **23177 (2005-11)**, 55965
(2006-09), 107239 (2007-06); Energy **23178 (2005-11)**, 60466 (2006-10), 99685 (2007-05); Poison (page "Poison Gas")
8037 (2005-05), 23179 (2005-11); Poison Bomb 71886 (2006-12).

| Field | 7.4 | Sources | Ours before | Ours now (items.xml) | Verdict |
|---|---|---|---|---|---|
| Fire field (1492, big; map 1487) | 20 on stepping in, then 10 × 7 (90 in all) | TW 72254 / 85637 Fire Field ("20 fire damage ... then 10 fire damage for 7 times", 2007: "each 9 seconds"); TW Fire 23177 (2005-11) "Large: 7 turns, 90 damage" | 20, then 7 × 10 every 10 s | same; measured 20 at once, 10 at +10.8, +20.9, +31.0 s | OK (tick 10 s vs "9 s" / "2 turns": soulfire's Q4) |
| Fire field, medium (1493; map 1488) | 70 (TW Fire 23177, 2005-11 and 55965, 2006-09: "5 turns, 70 damage", the page's "20 ... initial hit ... then 10 each 2 turns" = 20 + 5 × 10); 60 in 2007 (TW 107239: "6 turns, 60") | TW Fire | 7 × 10 = 70, no hit on stepping in | unchanged | **Q8** |
| Fire field, small (1494; map 1489) | no damage | TW Fire (all) | no damage | same | OK |
| Fire field stage times | big + medium last longer than 248 s (TN-Poison: the poison field's 248 s "is less than the first two stages of a fire field") | TN | 120 + 120 + 120 s | unchanged | **Q9** |
| Energy field (1495; map 1491) | 30, then 25 (55) per 2007; 30, then 25 twice (80) per 2005-2006 | TW Energy 23178 (2005-11) and 60466 (2006-10): "30 HP of initial damage, and then two additional hits for 25 HP each ... Total Damage: 80"; TW 99685 (2007-05) "an additional hit for 25 ... Total Damage: 55"; TW Energy Field rune 85636 (2007-02) "30 and later 25 ... 55 hp in 10 seconds" | 30, then 25 after 10 s | unchanged; measured 30 at once, 25 at +10.8 s | **Q10** |
| Poison field (1496; map 1490) | poison of 100, first hit 5, a hit every 4 s; lasts 248 s | TN-Poison ("Poison fields do 100 periodic poison damage. Damage cycles start at 5. The fields lasts for 248 seconds"; "Damage starts after 4 seconds and at 4 second intervals"); TW 55636 / 91945 "initial damage of 5 per hit ... 103 hp" | 100 from 5, **every 5 s**, **120 s** | **every 4 s** (1490, 1496, 1503), **248 s** (1496); measured 5 at once, then 5, 5, 5, 4, 4 at +4.8, +8.8, +12.9, +16.9, +20.9 s | fixed |
| Poison hit sequence | 5% of what is left, rounded up: 5 ×4, 4 ×5, 3 ×7, 2 ×10, 1 ×19 (45 hits) | TN-Poison | the engine's `generateDamageList(100, 5)`: 5 ×4, 4 ×5, 3 ×7, then 2 ×9 and 1 ×21 (or 2 ×10, 1 ×19: a float tie at 79 of 80), 100 in all | unchanged (engine code, every poison) | ~OK (note) |
| First poison hit | TN: "Damage starts after 4 seconds" (said of periodic poison in general) | TN-Poison | at once on stepping in (`ConditionDamage::startCondition`, not delayed) | unchanged | **Q11** |
| Non-PvP fields (1500-1502 fire, 1503 poison, 1504 energy) | vanish fast: fire "the 8 seconds it lasts (in Non-PvP Worlds)" (TW 8837, 2005-05, and 44630); poison bomb fields "dissapear in 3 seconds" (TW 71886, 2006-12); energy "vanishes much faster on Non-PvP worlds" (TW 46213) | TW | fire 10 + 10 + 10 s, poison 10 s, energy 10 s | unchanged (our world is PvP; used only on no-PvP tiles) | **Q12** |
| Bombs, walls | the same fields in a 3×3 / a line | TN, TW Firebomb 19507, Energybomb 19540, Fire Wall 19530, Poison Wall 19518 (2005-09) | same fields | same | OK |

## Healing spells and runes

| Spell / rune | 7.4 | Sources | Ours before | Ours now | Verdict |
|---|---|---|---|---|---|
| Light healing (exura) | 10-30 | TN, TI-Calc, OTHire 20/10 | 10-30 | same (`healing/light_healing.lua`) | OK |
| Intense healing (exura gran) | 20-60 | TN, TI-Calc, OTHire 40/20 | 20-60 | same | OK |
| Ultimate healing (exura vita) | 200-300 | TN, TI-Calc, OTHire 250/50; TW 8788/83130 "heals from 250" | 200-300 | same; measured | OK |
| Heal friend (exura sio) | 80-160 | TN "Heal Friend (classic) 80-160" (Tibiantis buffed it to 160-240), TW 7956 "about 120+/-40", OTHire 120/40 | P - 30 .. 1.35 P (the formula's -30 lowered the minimum) | **80-160** (`healing/heal_friend.lua`) | fixed |
| Mass healing (exura gran mas res) | 160-240 | TN, OTHire 200/40, TW 8825 "about 200" | 160-240 | same | OK |
| Intense healing rune (adura gran) | 40-100 | TN, OTHire 70/30 | 40-100 | same | OK |
| Ultimate healing rune (adura vita) | a fixed 250, not random | TN 250-250, OTHire 250/0, TW 107141 "The amount of healing is not random on use" | 250 | same; measured | OK |

## Conjure counts and rune charges

Checked 2026-10-04 at the distance task's request (it read 2006 TibiaWiki pages: poison arrows 5, power bolts 5 or 10).
Every count of ours equals Tibiantis and the TibiaWiki revisions from before 7.5 (May-Nov 2005). The lower counts in
later revisions came with 7.5 (December 2005, soul points): the wiki edits cluster on 2005-12-12..14 (arrows 15 -> 10,
fireball charges 3 -> 2) and 2006-02/03 (burst arrows 5 -> 3, bolts 10 -> 5); power bolts became 10 only with 8.0
(rev 105212, 2007-06-15). **No change.**

| Spell | Ours (`spells.xml` conjureCount) | Tibiantis | TibiaWiki before 7.5 | Later TibiaWiki |
|---|---|---|---|---|
| Conjure arrow (exevo con) | 15 | 15 | 15 (revs 6815, 8771, 2005-05) | 10 (rev 24519, 2005-12-12) |
| Conjure bolt (exevo con mort) | 10 | 10 | 10 (rev 7947, 2005-05) | 5 (rev 30680, 2006-03) |
| Conjure explosive arrow (exevo con flam) | 5 | 5 | 5 (rev 8808, 2005-05) | 3 (rev 28948, 2006-02) |
| Conjure poisoned arrow (exevo con pox) | 10 | 10 | 10 (rev 7941, 2005-05) | 5 (rev 86869, 2007-03) |
| Conjure power bolt (exevo con vis) | 1 | 1 | 1 (rev 7963, 2005-05: "only creates one Power Bolt"; still 1 in 2006-03) | 10 (rev 105212, 8.0) |
| Rune charges (32 runes) | as Tibiantis | equal for all 32 | equal for all 31 the 2005 revisions list (`spells.json`; Fireball's rev 6803 is a copy of the UH page - its next revision 7943 says 3) | fireball 2 from 2005-12-13 |

## Measured (tests/test_spell_damage.py)

Player against player (damage halved), at P 100 (the floor) and P 380 (level 100, magic level 60):

| Spell / rune | P 100 (halved) expected / seen | P 380 (halved) expected / seen |
|---|---|---|
| Fireball | 7-12 / 7-12 | 28-47 / 31-42 |
| Great fireball | 17-32 / 22-31 | 66-123 / 66-107 |
| Explosion | 10-50 / 13-41 | 38-190 / 103-139 |
| Energy wave (level 15, ML 20) | 50-100 / 51-100 | 190-380 / 248-380 |
| Energy beam | 20-40 / 23-35 | 76-152 / 88-138 |
| Flame strike | 17-27 / 17-25 | 66-104 / 71-99 |
| UH rune | 250 / 250 ×4 | 950 / 950 ×4 |
| exura vita | 200-300 / 227-281 | 760-1140 / 760-1140 |
| Poison storm, first tick (not halved) | 8-13 / 10, 12, 13 | - |
| Envenom, first tick (not halved) | - | 10-18 / 11, 12, 15 |

Light and heavy magic missile and sudden death: `test_combat_formulas.py`.

## Questions

- **Q1 Sudden death**: 7.4 130-170 %P (TN; OTHire 150/20), ours 125 %P + 30 .. 170 %P. Ours is 155-170 at the floor
  instead of 130-170, and a little higher at the low end above it. `test_combat_formulas.py`
  `test_stone_skin_amulet_takes_80_percent_of_a_sudden_death` asserts our current formula
  (`_range(power, 1.25, 30, 1.7)`), so changing the script alone would break it. Recommendation: `sudden_death.lua`
  `-1.3, 0, -1.7, 0` and that test's `_range(power, 1.3, 0, 1.7)`.
- **Q2 Force strike**: OTHire 45/10 (35-55, like the other strikes) against OTL-Mech's 18 (-30) .. 33; TN does not list
  it. Ours 20-50. Recommendation: 35-55 like energy and flame strike (OTHire is the only source with real data).
- **Q3 Berserk**: see formulas.md §2: ours scales with magic level, the 7.4 sources say level only (TI-Calc
  level/25 × 60..100 = 2.4-4.0 × level). Recommendation: a callback `level * 2.4 .. level * 4.0` if TI-Calc is taken.
- **Q4 Soulfire / burning tick**: 7.4 burns 10 a turn; how long a turn is is unclear (TibiaWiki: "each 9 seconds" on
  Fire Field, "10 HP each 2 turns" on Fire). Ours uses 10 s like the fire fields.
- **Q5 Fields**: answered by the fields task (2026-10-04): the poison field now ticks every 4 s and lasts 248 s
  (TN-Poison); the medium fire field's 70 matches the 7.4-era TibiaWiki (2005-11), see Q8.
- **Q6 Roll distribution**: ours rolls magic damage on a clipped normal curve (most hits near the middle, about 2% at
  each end); no source says how 7.4 rolled spell damage (the TN melee calculator uses the average of two rolls for
  melee only).
- **Q7 global.lua condition params**: renumber `CONDITION_PARAM_MINVALUE` .. `CONDITION_PARAM_SKILL_FISHINGPERCENT` to
  `src/enums.h` (MINVALUE 14, MAXVALUE 15, STARTVALUE 16, TICKINTERVAL 17, ... SKILL_FISHINGPERCENT 43). Unused today.
- **Q8 Medium fire field**: ours 7 × 10 = 70 with no hit on stepping in. TibiaWiki Fire in 2005-11 (7.4) and 2006-09:
  "Medium Fire Fields: 5 turns, 70 damage", with "20 HP as an initial hit for stepping in the fire, and then 10 HP each
  2 turns" = 20 + 5 × 10; in 2007-06 (8.0 era): "6 turns, 60 damage". Recommendation: 20 on stepping in, then 5 × 10
  (the 2005 text; the total 70 stays), i.e. `damage 20` before `ticks` and `count 5` on 1493 and 1488.
- **Q9 Fire field stage times**: ours 120 s each stage. TN-Poison says the poison field's 248 s "is less than the
  first two stages of a fire field", so big + medium > 248 s in 7.4 (ours 240). No source gives the stage times.
  Recommendation: leave 120 s each (8 s short at most) unless a source turns up.
- **Q10 Energy field**: ours 30 then 25 (55). TibiaWiki in 2005-11 (7.4) and 2006-10: 30 then two hits of 25 (80);
  from 2007: 30 then 25 (55). Recommendation: 30, then 25 twice 10 s apart (`count 2` on 1495, 1491, 1504), the only
  7.4-era text; keep 55 if the 2007 text is preferred.
- **Q11 First poison hit**: on our server the first 5 comes at once on stepping in; TN says periodic poison "starts
  after 4 seconds" (stated in general, not for fields). Changing it means a delayed poison condition on the field item
  (engine: `items.cpp` field parsing). Recommendation: leave it (stepping in shows the hit, which also tells the player
  the field poisoned them).
- **Q12 Non-PvP fields**: ours last 10 s (fire 10 + 10 + 10 s); TibiaWiki: fire 8 s (2005), poison bomb 3 s (2006).
  Only used on no-PvP worlds or tiles; our world is PvP. Recommendation: fire 1500 decays to nothing after 8 s (skip the
  medium and small stages), poison 1503 and energy 1504 3-8 s, if no-PvP areas matter.

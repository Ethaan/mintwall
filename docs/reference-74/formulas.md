# Tibia 7.4 formulas: reference and comparison with our server

Research date: 2026-09-22. Scope: real Tibia 7.4 (Dec 2004) mechanics, from public fan sources only. No CipSoft server code or binaries were used.

Confidence labels:
- **C2**: confirmed by 2 or more independent sources.
- **C1**: one source.
- **INF**: inferred (worked out from related data or later versions).

Note on sources: tibiantis.info and tibiantis-notes describe *Tibiantis*, a 7.4 remake. Its authors mark some values as custom. For example, tibiantis-notes says Paralyze costs 600 mana on Tibiantis but "for real 7.4 Tibia it was 900 mana". A value backed only by a Tibiantis source is therefore marked C1, even when it is very likely correct.

## Sources

| Key | URL |
|---|---|
| TN-Magic | https://tibiantis-notes.github.io/Magic |
| TN-Creature | https://tibiantis-notes.github.io/Creature (data in https://tibiantis-notes.github.io/js/creature.js) |
| TN-Summons | https://tibiantis-notes.github.io/summons |
| TN-Melee | https://tibiantis-notes.github.io/Melee_and_Distance |
| TN-DmgCalc | https://tibiantis-notes.github.io/Physical_Damage_Calculator , https://tibiantis-notes.github.io/distance_calculator |
| TN-Classes | https://tibiantis-notes.github.io/Classes |
| TN-Skills | https://tibiantis-notes.github.io/Skills |
| TN-Food | https://tibiantis-notes.github.io/Food_and_regeneration |
| TN-Speed | https://tibiantis-notes.github.io/speed |
| TI-Spells | https://tibiantis.info/library/spells |
| TI-Calc | https://tibiantis.info/calc/exori , /calc/healing , /calc/magic , /calc/skill , /calc/experience (formulas in https://usa.michal.es/tibiantis/js/calc.js) |
| TW-Formulae | https://tibia.fandom.com/wiki/Formulae |
| TW-Berserk | https://tibia.fandom.com/wiki/Berserk (history section) |
| TW-Promotion | https://tibia.fandom.com/wiki/Promotion |
| TW-DL / TW-Dragon / TW-Hydra | https://tibia.fandom.com/wiki/Dragon_Lord , /wiki/Dragon , /wiki/Hydra |
| TW-7.5, TW-7.6, TW-8.41 | https://tibia.fandom.com/wiki/Updates/7.5 , /Updates/7.6 , /Updates/8.41 |
| TW-Death | https://tibia.fandom.com/wiki/Death_Penalty |
| OTL-Mech | https://otland.net/threads/game-mechanics-through-time.216072/ |
| OTL-Bless | https://otland.net/threads/blessing-mechanics-for-7-4-7-6-lose-bp.288896/ |

---

## 1. Monster self-healing and how often monsters cast spells (TOP PRIORITY)

### 1.1 How 7.4 decides when a monster casts

- Each monster spell, including self-heal, has a *frequency* F. Each time the creature's "stimulus" (think) function runs, the spell fires with probability 1/F. **C1** (TN-Summons: "Spell/projectile chance is 1/'frequency' for each time the stimulus function is called").
- How often the stimulus runs:
  - **Melee creatures:** once every 2 s.
  - **Creatures that keep distance** (fire devil, minotaur archer, hunter and similar): once every 1 s.
  - **C2**: TN-Summons, and OTL-Mech ("Melee range: 2-second interval; far range: 1-second interval; the casting chance remained constant, only the interval varied by distance", written for 7.7 and earlier).
- Self-heal belongs to the same spell list, so it follows the same 1 s / 2 s timing. **INF** (neither source names healing specifically).

### 1.2 7.4 heal values per monster, compared with ours

7.4 heal is `base ± var`, cast with probability 1/F per stimulus. These values are in TN-Creature's `creature.js` (`heal_base`, `heal_var`, `heal_frequency`). **C1**.

Ours: `<defense name="healing" interval= chance= min= max=>` in `server/data/monster/<name>.xml`. The "melee?" column is our `targetdistance="1"`.

| Monster | 7.4 heal (F) | 7.4 HP/s ¹ | Ours (file:line) | Ours HP/s ² | Match |
|---|---|---|---|---|---|
| Dragon Lord | 57-93 (1/4), melee | **9.4** | `dragon lord.xml:34` interval 1000 chance 25, 57-93 | **18.8** | amount OK, **rate 2x** |
| Dragon | 34-56 (1/8), melee | 2.8 | `dragon.xml:31` 1000/13, 34-56 | 5.9 | amount OK, **rate 2x** |
| Demon | 90-150 (1/7), melee | 8.6 | `demon.xml:40` 1000/15, 90-150 | 18.0 | **rate 2x** |
| Hero | 200-250 (1/10), melee | 11.3 | `hero.xml:27` 1000/10, **200-350** | 27.5 | **amount + rate** |
| Lich | 50-150 (1/6), melee | 8.3 | `lich.xml:39` 1000/17, 50-150 | 17.0 | **rate 2x** |
| Banshee | 113-187 (1/4), melee | 18.8 | `banshee.xml:30` 1000/25 | 37.5 | **rate 2x** |
| Monk | 30-50 (1/6), melee | 3.3 | `monk.xml:24` 1000/17 | 6.8 | **rate 2x** |
| Efreet / Marid | 50-80 (1/7), melee | 4.6 | `efreet.xml:46`, `marid.xml:46` 1000/15 | 9.8 | **rate 2x** |
| Bone Beast | 30-60 (1/9), melee | 2.5 | `bone beast.xml:34` 1000/12 | 5.4 | **rate 2x** |
| Gargoyle | 5-15 (1/10), melee | 0.5 | `gargoyle.xml:27` 1000/10 | 1.0 | rate 2x (negligible) |
| Ghoul | 9-15 (1/8), melee | 0.75 | `ghoul.xml:25` 1000/13 | 1.6 | rate 2x |
| Warlock | 60-100 (1/4), distance | 20 | `warlock.xml:44` 1000/25 | 20 | OK |
| Necromancer | 42-68 (1/4), distance | 13.8 | `necromancer.xml:31` 1000/25 | 13.8 | OK |
| Priestess | 34-56 (1/7), distance | 6.4 | `priestess.xml:30` 1000/15 | 6.8 | OK |
| Orc Shaman | 27-43 (1/4), distance | 8.8 | `orc shaman.xml:32` 1000/25 | 8.8 | OK |
| Elf Arcanist | 42-68 (1/5), distance | 11 | `elf arcanist.xml:34` 1000/20 | 11 | OK |
| Dwarf Geomancer | **75-125** (1/2), distance | 50 | `dwarf geomancer.xml:32` 1000/50, **75-325** | 100 | **amount 2x** |

¹ 7.4 HP/s = avg heal / F / stimulus interval, using 2 s for melee and 1 s for distance creatures.
² Ours HP/s = avg heal × chance / 100 per second. See 1.3.

TibiaWiki's *current* values differ (dragon 40-70; DL armor 34), so they reflect later rebalances. TW-DL does agree on the Dragon Lord's 57-93 heal range, so the heal amount is **C2**.

**Hydra:** TW-Hydra lists `implemented = 7.5`, so hydras were **not** in 7.4. **C1** (TibiaWiki infobox). Our server correctly has none.

### 1.3 Our engine timing

- `server/src/game.cpp:3610-3630`, `Game::checkCreatures`: every creature gets `onThink(1000)` exactly once per second. `EVENT_CREATURE_THINK_INTERVAL 1000`, `creature.h:102`.
- `server/src/monster.cpp:766-789`, `Monster::onThinkDefense`: each defense with `interval` ≤ elapsed ticks rolls `chance` once per think. Every healing entry uses `interval="1000"`, so it rolls every second. This happens whether or not the monster is in melee range, and even while it has no target or is fleeing.
- `server/src/monsters.cpp:479`: "healing" becomes a plain `COMBAT_HEALING` with min/max taken straight from the XML. No hidden multiplier.

**Dragon Lord verdict.** The per-cast amount (57-93) and the 25% chance equal the 7.4 data. The difference is the roll frequency: ours rolls every 1 s, while a melee creature in 7.4 rolled every 2 s. As a result every melee monster self-heals **about 2x** as fast as in 7.4 (Dragon Lord 18.8 HP/s, about 1,125 HP/min, against about 560 HP/min in 7.4).

Other things make a Dragon Lord feel harder in melee on our server:
- Our heal also runs while it flees at `runonhealth="300"` (`dragon lord.xml:18`).
- Our knights take harder hits: melee max 250 against about 204 in 7.4, and our shield blocks much less (see §6).

The Dragon Lord itself is actually *less* defended than in 7.4 (§6.3). The heal rate is the main outlier.

Our other monster timings:
- The Dragon Lord's attack spells already use `interval="2000"` (lines 21-22, 29), which matches the 2 s melee stimulus.
- Its `firefield` uses `interval="1000"` (line 26), so it too is rolled twice as often as in 7.4. **INF**

---

## 2. Berserk (exori)

| Item | 7.4 | Source / confidence | Ours | Match |
|---|---|---|---|---|
| Mana | level × 4 | TW-Berserk history ("Before the Summer Update 2007 … mana equal to the character level times four"); TI-Spells ("mana = level * 4"); TI-Calc `countExori` **C2** | `spells.xml:105` `lvpercent="400"`, and `spells.cpp:935-938` gives level×400/100 | **Yes** |
| Requirement | magic level 5, knights only (7.4 spells were gated by magic level; the level-35 requirement is from a later version) | TI-Spells (mlvl 5) **C1**; TW-Berserk shows the current level 35 | `spells.xml:105` `maglv="5"`, Knight/Elite Knight | Yes |
| Damage | level/25 × [60..100] = **2.4×L … 4.0×L** (no skill or ML term) | TI-Calc `countExori` **C1**. OTL-Mech gives 2.2×L … 3.85×L **C1**. The two are close, so the shape (level only) is **C2** | `attack/berserk.lua:4` `LEVELMAGIC -1.4, 0, -1.65, 0` gives (2L+3ML)×1.4 … ×1.65 = 2.8L+4.2ML … 3.3L+4.95ML | Close but different shape. L60/ML5: ours 189-222 (avg 205), 7.4 144-240 (avg 192). Ours has a narrower spread and scales with ML |
| Damage type / area | physical, 3×3 around caster | TW-Berserk | `berserk.lua` physical, 3×3 | Yes |

## 3. Other spells with level-based mana in 7.4

- In 7.4 only **Berserk** (level×4) and **Summon Creature** (`utevo res`, where the mana depends on the creature's summon cost) had variable mana. Every other spell had a fixed cost. **C1** (TI-Spells: only these two rows have mana 0 with a usage formula).
- Ours: `spells.xml:51` Summon Creature uses `function="summonMonster"`, which takes the monster's `manacost`. Matches.
- Mana costs where TI-Spells differs from our `spells.xml`. Tibiantis may have changed some of these (it changed Paralyze).

| Spell | TI-Spells | Ours (`spells.xml` line) |
|---|---|---|
| Cancel Invisibility | 250 | 200 (95) |
| Mass Healing | 120 (TN-Magic lists the "classic" cost as 150) | 150 (113). Matches classic |
| Poison Storm | 400 | 600 (122) |
| Paralyze | 600 (TN-Speed: real 7.4 was 900) | 900 (240). Matches real 7.4 |
| Undead Legion | 400 | 500 (116) |
| Wild Growth | 150 | 220 (128) |

All other instant/rune mana costs and magic-level requirements match TI-Spells, including the rune "usage" ML (e.g. SD 15, UH 4, MW 9, GFB 4, HMM 1, LMM 0). Rune charges also match (e.g. `spells.xml:25` SD 1, GFB 2, explosion 3).

## 4. Fluids and healing spells/runes

The 7.4 heal is `base × P / 100`, where **P = 2×level + 3×ML, with a floor of P = 100**. Source: TI-Calc `countHealing` (`if (power < 100) power = 100`). **C1** for the floor, but see §5, where TN-Classes shows the same floor for damage. The base min/max come from TN-Magic and TI-Calc. **C2** where both agree.

| Item | 7.4 | Conf. | Ours | Match |
|---|---|---|---|---|
| Mana fluid | 25-75 mana (flat) | TI-Calc and TN-Magic **C2** (OTL-Mech: 20-75 before 7.6) | `actions/scripts/fluids.lua:41` `math.random(40, 80)` | **No**: avg 60 vs 50 |
| Life fluid | 25-75 HP (flat) | TI-Calc **C1**; OTL-Mech "≈25-75" **C2** | `fluids.lua:52` `math.random(40, 80)` | **No** |
| exura | 10-30 %P | TN-Magic, TI-Calc **C2** (OTL-Mech 8-33 %) | `healing/light_healing.lua:9-13`: 10-35 %P, min 15 | ~Yes (no P-floor) |
| exura gran | 20-60 %P | **C2** | `intense_healing.lua:9-10`: 20-60 %P | **Yes** (no P-floor) |
| exura vita | 200-300 %P | **C2** (TN-Magic, TI-Calc) | `ultimate_healing.lua:9-10`: 220-260 %P | Avg 240 vs 250; narrower spread |
| exura sio | 7.4 "classic" 80-160 %P (Tibiantis buffed to 160-240) | TN-Magic **C1** | `heal_friend.lua:7`: 100 %P+30 … 135 %P | Roughly |
| exura gran mas res | 160-240 %P | **C2** | `mass_healing.lua:6`: 120 %P+30 … 150 %P | **No** (about 30% weaker) |
| IH rune (adura gran) | 40-100 %P | **C2** | `intense_healing_rune.lua:9-10`: 40-75 %P | **No** (avg 57 vs 70 %P) |
| UH rune (adura vita) | fixed 250 %P (= 250 at P≤100) | **C2** | `ultimate_healing_rune.lua:10-14`: 210-250 %P, min 250 | Slightly low (avg 230 vs 250 %P) |

Life ring (7.4): 1 HP and 1 mana per 3 s for 20 min. Ring of healing (7.4): 1 HP and 1 mana per 1 s for 7.5 min. Sources: TN-Magic, and OTL-Mech's "pre-7.6" values, **C2**. Our ring regeneration (`movement.cpp:824` item regen) was not checked.

## 5. Magic damage formula

- 7.4: `damage = base × P / 100`, with `P = mlv×3 + lv×2` and a floor of **P = 100** (magic power ≥ 1). **C2**:
  - TN-Magic formula.
  - TN-Classes "magic power" table, which shows 1.00 for every low-power row.
  - TI-Calc P-floor.
  - OTL-Mech `MAGIC_FORMULA = level*2 + magiclevel*3`, "if below base value, base value is used".
- Ours: `server/src/combat.cpp:80-84` `FORMULA_LEVELMAGIC`: `(lv*2 + ml*3) * a + b`. Same core (**match**), but **there is no P ≥ 100 floor**. For example, a level-8, ML-0 LMM does 1-3 damage here but 10-20 in 7.4.
- Our range is `[|mina|×P + |minb|, |maxa|×P]`, from `combat.cpp:82-83`, with minb usually 0 or 30.

| Spell | 7.4 base %P (TN-Magic) | Ours %P (`data/spells/scripts/attack/*.lua:4-5`) | Verdict |
|---|---|---|---|
| Light Magic Missile | 10-20 | 10-20 | OK |
| Heavy Magic Missile | 20-40 | 20-40 | OK |
| Fireball | 15-25 | 16-33 | ours higher |
| Great Fireball | 35-65 | 40 (+30) - 70 | ours higher |
| Explosion | 20-100 | 15-90 | ~OK |
| Sudden Death | 130-170 | 125 (+30) - 170 | OK |
| Energy/Flame Strike | 35-55 (TN) / 25-55 (OTL) | 25-55 | OK per OTL; TN conflicts |
| Force Strike | OTL 18(-30)-33 | 20-50 | ours higher (C1) |
| Fire Wave | 20-40 | 25 (+30) - 60 | **ours ~50% higher** |
| Energy Beam | 40-80 | 68-130 | **ours ~65% higher** |
| Great Energy Beam | 40-200 | 130-170 | avg 150 vs 120, much less variance |
| Energy Wave | 100-200 | 115-190 | OK |
| Ultimate Explosion | 200-300 (OTL 230(-30)-300) | 192-300 | OK |
| Poison Storm | 150-250 | 90-150 | **ours ~40% lower** |

## 6. Melee, distance, armor and defense

### 6.1 Players attacking

| Item | 7.4 | Conf. | Ours | Match |
|---|---|---|---|---|
| Melee max | `floor((5×skill+50) × atk' × 0.99 / 100)`, about 0.05·skill·atk + 0.5·atk | TN-DmgCalc **C1**. OTL-Mech gives "0.06×skill×atk×d" for ≤8.0 **C1** | `weapons.cpp:164-170` `ceil(skill/20*atk + atk/attackFactor)` = 0.05·skill·atk + **1.0**·atk | Ours adds a full atk instead of 0.5 atk (e.g. skill 70, atk 40: 180 vs 158) |
| Roll distribution | average of two 0-99 rolls (triangular) | TN-DmgCalc **C1** | `random_range(0,max,DISTRO_NORMAL)` (`weapons.cpp:750`) | similar shape |
| Stance multipliers | offensive atk ×1.2 / def ×0.6; balanced 1.0 / 1.0; defensive atk ×0.6 / def ×1.8. With no target, defense uses defensive stance | TN-Melee **C1**. OTL-Mech d = 1 / 0.7-0.75 / 0.5 **C1** | `player.cpp:529-548` attack factor 1.0/1.2/2.0 is a *divisor* applied only to the `+atk` term (operator precedence in `weapons.cpp:169`); defense factor 1.0/1.2/2.0 is a multiplier | **No**: offensive gets no ×1.2 and keeps full defense; balanced gets +20% defense |
| Distance max | same formula as melee, with atk' = bow + ammo atk | TN-DmgCalc **C1** | `weapons.cpp:172-181` `((skill*atk)/20 + skill)/factor`: adds *skill*, not atk | **No** (formula shape differs) |
| Distance min | none (0) in the TN calc; OTL-Mech gives level/5 | conflicting | `weapons.cpp:1003-1010` ceil(level×0.2) vs monsters, ×0.1 vs players | ? |
| Distance hit chance | `min(skill / (15×d − 1), 1)`, where adjacent counts as d = 5 | TN distance_calculator **C1** | `weapons.cpp:869-915` TFS-style table per distance, capped at 75% (1-handed) or 90% (ammo) | **No** (different model) |

### 6.2 Defense and armor (players receiving hits)

| Item | 7.4 | Conf. | Ours | Match |
|---|---|---|---|---|
| Shield block | same formula as the attack roll, using shielding skill and def × stance: max ≈ (5×shield+50)×def/100. Up to 2 blocks per 2 s turn | TN-Melee / TN-DmgCalc **C1** | `player.cpp:497-526` max = ceil((shield×def×0.015 + def×0.1)×factor); `creature.cpp:907-910` removes rand(max/2, max); blockCount +1 per s, max 2 (`creature.cpp:204-208`) | **No**: ours blocks about 3x less at the top end. Shield 70, def 30, balanced: 7.4 max ~120, ours 17-35 (×1.2) |
| Armor | reduction = floor(A/2) + floor(A/2 × r/99), i.e. 50-100% of A; A=1-2 gives 1 | TN-Melee and TN distance_calculator `fn_armor` **C1** | `creature.cpp:919-932` ceil(0.475A) … ≈0.95A−1 | ~OK (about 5% lower) |

### 6.3 Monsters (attack, defense, armor)

- 7.4 creatures have Attack, Defence, Armor and a fighting skill. Their melee max and block max use the same formula as players, with the monster in balanced stance. **C1** (TN-Creature `max_damage` and `max_block`).
- Dragon Lord (7.4): Atk 55, Def 48, Armor 32, skill 65. Melee max = floor(375×55×0.99/100) = **204**, block max = **178**.
- Our Dragon Lord (`dragon lord.xml:21,33`): melee −80 … −250, armor 22, defense 35. Our monsters block only rand(def/2, def), i.e. 17-35, with no skill scaling.

Our monsters hit harder than 7.4 but block far less. The average armor reduction happens to be similar (DL: ~15 in both).

## 7. Regeneration, food, soul

HP/mana ticks, 7.4 vs ours (`data/vocations.xml` `gainhpticks` / `gainmanaticks`, amount 1, seconds). The 7.4 values come from:
- TN-Classes (per hour: K 600/900 HP and 300 mana; P 450/600 and 450/600; mage 300 HP and 600/900 mana).
- TW-Promotion and OTL-Mech modern tables. Their HP values are the same, and their mana values are ×4 because 7.6 raised mana regeneration (TW-7.6: "Mana regeneration was increased").

**C2** for HP, **C2** (ratio) for mana.

| Vocation | 7.4 HP / mana (1 per N s) | Ours HP / mana (`vocations.xml` line) | Match |
|---|---|---|---|
| Knight | 6 / 12 | 6 / 12 (l.43) | Yes |
| Elite Knight | **4** / **12** | **3 / 6** (l.83) | **No**: HP +33%, mana 2x |
| Paladin | **8 / 8** | 9 / 9 (l.33) | No (≈11% slow) |
| Royal Paladin | **6 / 6** | 7 / 7 (l.73) | No (≈14% slow) |
| Sorcerer / Druid | 12 / 6 | 12 / 6 (l.13, l.23) | Yes |
| Master Sorcerer / Elder Druid | **12** / 4 | **10** / 4 (l.53, l.63) | HP 20% fast |

- **Food:** regeneration time = nutrition × 12 s, capped at 1200 s. Meat 180, ham 360, dragon ham 720, brown mushroom 264 and so on (TN-Food, **C1**). Ours: `actions/lib/actions.lua:66-75` and `actions/scripts/food.lua:1` `MAX_FOOD = 1200`. Durations are in seconds (`luascript.cpp:2745` `food*1000` ms). **Matches.**
- **Soul points:** introduced in 7.5 (TW-7.5), so 7.4 has none. Ours: soul code is only compiled under `__PROTOCOL_76__`, which is off by default (`definitions.h:27-33`, client 7.40). Matches.
- **Speed:** base = 220 + 2×(level−1). Haste is ×1.3 − 24 and strong haste ×1.7 − 56 (TI-Calc `countSpeed`, TN-Speed, **C2**). Ours: `player.h:768`, `support/haste.lua` (0.3, −24) and `strong_haste.lua` (0.7, −56). **Matches.**

## 8. Experience, skills, magic level, death

| Item | 7.4 | Conf. | Ours | Match |
|---|---|---|---|---|
| Exp for level L | (50(L−1)³ − 150(L−1)² + 400(L−1))/3 | TW-Formulae, TI-Calc **C2** | `player.h:135-139` identical | Yes |
| Skill tries to go L→L+1 | A·b^(L−10), where A = 50 melee/fist, 30 distance, 100 shielding, 20 fishing | TW-Formulae, TI-Calc `countSkill` **C2** | `vocation.cpp:192,243` `skillBase{50,50,50,50,30,100,20}`, `base*b^(level-11)` called with level+1 | Yes |
| Skill constants b | K 1.1 melee/fist/shield, 1.4 dist; P 1.2/1.2/1.1 dist/1.1 shield; S 2.0 melee/dist, 1.5 fist/shield; D 1.8 melee/dist, 1.5 fist/shield; fishing 1.1 | TW-Formulae, TI-Calc, TN-Skills **C2** | `vocations.xml` skill multipliers | Yes |
| Mana for ML → ML+1 | 1600 × b^ML, where b = 1.1 mage, 1.4 paladin, 3.0 knight, **3.0 none** | TW-Formulae **C1** (TI-Calc uses 400×b^ML, which looks like a Tibiantis rate) | `vocation.cpp:254` `1600*pow(b, ML)`. b is in `vocations.xml` (`manamultiplier`): mage 1.1, pal 1.4, knight 3.0, **none 4.0** (l.3) | Yes, except rookie b = 4.0 vs 3.0 |
| Death: exp / ML / skills | 10% each. Promoted players lose 7% (−30%). No level scaling before 8.41 | TW-8.41 (the level-scaled formula came in 8.41), OTL-Bless ("10%, promotion 7%") **C2** for 10%, **C1** for promotion | `player.cpp:147-148` 10% defaults, taken from the DB `loss_*` columns (`ioplayer.cpp:161-164`); no promotion reduction in code | 10% OK; promotion −30% missing (unless set per-row in DB) |
| Death: items | each equipped item has a 10% chance; only the Amulet of Loss protects | OTL-Bless **C1**. Backpack chance in 7.4 is unconfirmed (current TibiaWiki says 100%) | `player.cpp:801-823`: containers always drop, other slots 10% | Probably OK |

---

## Mismatches, ranked by player impact

1. **Melee monsters self-heal about 2x faster than in 7.4.** Our heal is rolled every 1 s; 7.4 rolled it every 2 s for melee creatures.
   - Affects Dragon Lord, Dragon, Demon, Hero, Lich, Banshee, Monk, Djinns, Bone Beast and others.
   - Heal amounts and chances match the 7.4 data; only the roll interval is wrong. Dragon Lord: 18.8 HP/s here vs about 9.4 HP/s in 7.4.
   - This is the likely cause of "dragon lords heal super fast".
   - Data fix: `interval="2000"` on healing defenses of `targetdistance="1"` monsters. Engine alternative: do the defense stimulus every 2 s while in melee.
   - Files: `server/data/monster/*.xml` healing lines, `server/src/monster.cpp:766`.
2. **Heal amount outliers:** Dwarf Geomancer 75-325 (7.4: 75-125, rolled every 1 s at 50%), and Hero 200-350 (7.4: 200-250).
3. **Player shield blocking is about 3x weaker than in 7.4, and the stances are wrong** (§6.1-6.2). Knights take much more melee damage. Combined with monster melee maxima above the 7.4 formula (DL 250 vs 204), this makes melee creatures much deadlier.
   - Files: `server/src/player.cpp:497-548`, `server/src/weapons.cpp:164-181`, `server/src/creature.cpp:892-932`.
4. **No magic-power floor (P ≥ 100)** for rune, spell and heal formulas. Low-level characters get tiny LMM/HMM/IH/exura values (for example, LMM at level 8 does 1-3 damage instead of 10-20). File: `server/src/combat.cpp:80-84`, or per-script callbacks.
5. **Fluids give 40-80 instead of 25-75** (mana and life). File: `server/data/actions/scripts/fluids.lua:41,52`.
6. **Spell damage bases off:**
   - Energy Beam about +65%, Fire Wave about +50%.
   - Poison Storm about −40%, Mass Healing about −30%, IH rune about −20%.
   - Great Energy Beam and Berserk have the wrong spread.
   - Files: `server/data/spells/scripts/attack/*.lua`, `server/data/spells/scripts/healing/*.lua`.
7. **Promoted regeneration:** Elite Knight regenerates mana 2x and HP 1.33x too fast; Royal Paladin and Paladin are 11-14% too slow; Master Sorcerer and Elder Druid HP is 20% too fast. File: `server/data/vocations.xml` lines 33, 53, 63, 73, 83.
8. **Distance formula** adds skill instead of attack and uses the TFS hit-chance table (`weapons.cpp:172-181, 869-915`). Monsters block only def/2..def with no skill scaling, so our monsters are easier for melee and distance damage.
9. **Death penalty:** there is no promotion reduction (7% for promoted players). Minor.
10. **Minor:** rookie ML constant 4.0 vs 3.0 (`vocations.xml:3`), and a few mana costs that differ from Tibiantis but are unconfirmed for real 7.4 (§3).

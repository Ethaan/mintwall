# Tibia 7.4 death rules: reference and comparison with our server

Research date: 2026-09-22. Scope: real Tibia 7.4 (Dec 2004 to Aug 2005), from public fan sources only. No CipSoft server code or binaries were used. No server code or data was changed.

Confidence labels (same as `formulas.md`):
- **C2**: confirmed by 2 or more independent sources.
- **C1**: one source.
- **INF**: inferred (worked out from related data or later versions).

Notes on sources:
- Most of the evidence comes from **old TibiaWiki revisions**, pulled through the MediaWiki API (`api.php?action=query&prop=revisions&rvdir=newer`). The May 2005 revisions were written **during the 7.4 era**: 7.4 ran until 7.5 on 9 Aug 2005. TibiaWiki revisions count as one source, however many revisions agree.
- Tibiantis says very little about death. Its FAQ and premium pages cover promotion and premium expiry, and its frag calculator and rules cover the skull limits. Nothing public on tibiantis.info or tibiantis-notes covers item loss.
- tibia.com (news archive, manual) returned HTTP 403, and web.archive.org was offline. The manual is therefore cited only as quoted on TibiaWiki's talk page.

## Sources

| Key | URL |
|---|---|
| TW-Death-2005 | https://tibia.fandom.com/wiki/Death?oldid=6509 (2005-05-05), ?oldid=6542 (2005-05-05), ?oldid=19247 (2005-05-06), ?oldid=23124 (2005-11-02) |
| TW-Death-2008 | https://tibia.fandom.com/wiki/Death?oldid=138184 (2008-01-08, still before 8.41) |
| TW-Death | https://tibia.fandom.com/wiki/Death (current, 8.41+ rules) |
| TW-TalkDeath | https://tibia.fandom.com/wiki/Talk:Death (2007 posts, quoting the tibia.com manual) |
| TW-Bless-2005 | https://tibia.fandom.com/wiki/Blessings?oldid=6510 (2005-05-05) |
| TW-Bless-2008 | https://tibia.fandom.com/wiki/Blessings?oldid=141925 (2008-01-26) |
| TW-Bless | https://tibia.fandom.com/wiki/Blessings (infobox "implemented 7.2") |
| TW-AoL | https://tibia.fandom.com/wiki/Amulet_of_Loss (current; "implemented 7.2"), ?oldid=11120 (2005-06-14), ?oldid=140976 (2008-01-22) |
| TW-AoLife | https://tibia.fandom.com/wiki/Amulet_of_Life |
| TW-Skull-2005 | https://tibia.fandom.com/wiki/Skull_System?oldid=11103 (2005-07-10); https://tibia.fandom.com/wiki/Red_Skull?oldid=15905 (2005-09-09) |
| TW-Skull-2008 | https://tibia.fandom.com/wiki/Skull_System?oldid=180775 (2008-08-13) |
| TW-Promo | https://tibia.fandom.com/wiki/Promotion ; https://tibia.fandom.com/wiki/Vocation_Promotion?oldid=127 (2005-01-23) |
| TW-Rooking | https://tibia.fandom.com/wiki/Rooking |
| TW-7.2 / 7.24 / 7.9 / 8.41 | https://tibia.fandom.com/wiki/Updates/7.2 , /Updates/7.24 , /Updates/7.9 , /Updates/8.41 |
| TA-FAQ | https://tibiantis.online/?page=faq |
| TA-Prem | https://tibiantis.online/?page=premium |
| TA-Rules | https://tibiantis.online/?page=rules |
| TI-Frags | https://tibiantis.info/calc/frags |
| OTL-Bless | https://otland.net/threads/blessing-mechanics-for-7-4-7-6-lose-bp.288896/ (poster emil92b) |
| OTL-Mech | https://otland.net/threads/game-mechanics-through-time.216072/ |

---

## 1. Experience loss

**7.4:** you lose **10% of total experience**. A promoted character loses **7%**, which is 30% less. The loss is a flat percentage of total experience. The level-scaled formula `((L+50)/100)*50*(L²-5L+8)` only arrived in **8.41** (18 Mar 2009).
- 10% and promoted 7%: **C2**. Sources: TW-Death-2005 ("10% loss of experience"), TW-Bless-2005 ("premium with 0 blessings is 7%"), TW-Bless-2008 ("promoted players only lose 7%"), OTL-Bless (emil92b: "10% … promotion 7%"), and TA-FAQ/TA-Prem (promotion "decreases death penalty", with no number).
- Level formula only from 8.41: **C2**. TW-8.41 ("From level 24 and above the experience and skill loss will slowly decrease") and TW-Death.

**Ours:** `player.h:783-785` gives `getLostExperience = experience * lossPercent[LOSS_EXPERIENCE]/100 * getDeathLossFactor()`, where `getDeathLossFactor()` (`player.h:780-782`) is 0.7 for vocations 5-8. `lossPercent` defaults to 10 (`player.cpp:148-150`) and is loaded per player from `loss_experience` (`ioplayer.cpp:161`, DB default 10 at `sql/schema.sqlite:54`). The loss is applied in `preSave()` (`player.cpp:2236-2250`). **MATCH.** One caveat: the per-player DB columns can override the 10 without any warning.

## 2. Magic level (mana spent) and skill loss

**7.4:** skills lose **10%** (promoted **7%**). Magic level is lost the same way, as a share of the total mana spent. The loss is a percentage of the total tries or mana accumulated, not of the current level's progress.
- Skills at 10% and 7%: **C2** (TW-Death-2005, TW-Bless-2008 "experience and skills", OTL-Bless).
- Magic level uses the same percentage: **C1/INF**. Old pages only say "skills"; the current TW-Death says "skill tries, and spent mana"; TW-TalkDeath (2007) says "levels and magic levels".

**Ours:** `die()` handles magic level at `player.cpp:2114-2133`: it sums `getReqMana(1..ML)` plus `manaSpent`, multiplies by `loss_mana`% times the factor, and can drop ML. Skills are handled at `player.cpp:2135-2166`: it sums the tries from level 11 up to the current level, plus current tries, multiplies by `loss_skills`% times the factor, and can drop levels down to a floor of 10. **MATCH.**

## 3. Level loss removes the level's HP, mana and capacity

**7.4:** each level lost takes away that level's vocation HP, mana and capacity gains. After death the character returns at full health. **INF**: stats are a pure function of level and vocation (see TW-Formulae in `formulas.md`).

**Ours:** `preSave()` at `player.cpp:2240-2246` subtracts `getHPGain/getManaGain/getCapGain` once per lost level. `player.cpp:2248-2249` sets health and mana to max. **MATCH.**

## 4. Item loss

**7.4 behaviour:**
- **Containers: always lost, 100%, with all their contents.** They go into the corpse. The earliest text says the backpack slot. The 2005-05-06 and later revisions say "**any container**, like bags and backpacks". **C2**: TW-Death-2005 (oldid 6509: "loss of any item in the … backpack slot"; oldid 19247: "You'll drop any container"), TW-Death-2008 ("Any container … and all its contents will be dropped"), current TW-Bless ("100% chance of dropping your container equipped in the backpack slot and its entire content"), and OTL-Bless (the thread title and answer are about "lose bp"; only an AoL protects it). **This confirms the owner's statement.**
- **Every other equipped item: 10% each, rolled independently.** Promotion does not reduce this chance. Before 8.41, blessings did not reduce it either. **C2**: TW-Death-2005, TW-Death-2008, TW-TalkDeath (quotes the tibia.com manual: "the chance of dropping items will not be reduced if a character is promoted"; "10% per item"), and TW-8.41 ("Blessings **can now** reduce the probability of losing items").
- **Ammo slot:** the very first revision (2005-05-05) said the ammo slot is always lost. It was rewritten the next day and never repeated. **C1, unconfirmed.** Treat the ammo slot as a normal 10% slot.
- Dropped items go into the player's corpse; nothing simply vanishes, except a consumed AoL. **C2** (TW-Death-2005, TW-AoL-2008).
- If the backpack slot was empty, 7.4 did **not** give the player an empty bag. The free bag after death came in 7.9. **C1** (TW-7.9).

**Ours:** `dropLoot()` at `player.cpp:842-866` moves any item with `getContainer()` in any slot into the corpse (100%). Every other slot item moves with `random_range(1,100) <= loss_items` (default 10, `ioplayer.cpp:164`). **MATCH.** It covers any container in any slot, which agrees with the 2005-2008 wiki wording. There is no empty bag after death, which also matches.

## 5. Amulet of Loss (id 2173)

**7.4 behaviour:**
- It protects **all** items, including the backpack and its contents. **C2** (TW-Death-2005 "reduce the drop chance of your items to 0", TW-AoL-2005, OTL-Bless "only amulet of loss protects your backpack and equipment").
- It is **consumed** on death: it disappears and is not dropped. **C2** (TW-Death-2005 "the amulet will be lost (not dropped)", TW-AoL-2008, TW-TalkDeath).
- It does **not** reduce experience or skill loss. Only the Amulet of Life did that, and it was removed in 7.2 (16 Dec 2003) when the AoL replaced it. **C2** (TW-AoLife, TW-7.2, TW-AoL).
- It does **not work with a red skull**. All items drop, and the AoL is still used up, so it cannot be looted. **C2** (TW-Death-2005, TW-Skull-2005 "drop all items … no matter if an Amulet of Loss is worn", TW-AoL-2008, TW-TalkDeath 2007). **This confirms the owner's statement.**

**Ours:**
- `items.xml:3601-3606`: `preventitemloss=1`, `charges=1`.
- `onDie()` at `player.cpp:2060-2093` finds the amulet and drops its charge to 0. `Game::transformItem` (`game.cpp:1809-1827`) then removes it, because it has no `decayTo`. This happens even with a red skull.
- `player.cpp:2084` turns off the drop only when the skull is not red.
- Eremo sells it for 50,000 and buys it for 45,000 (`npc/Eremo.xml:11-12`).
- No item has `preventSkillLoss`.

**MATCH** on all four points.

## 6. Skulls and unjustified kills

**7.4 behaviour:**
- **Red skull**: you lose **all** items on death, AoL or not (**C2**, see §4 and §5). A red skull is given after **3** unjustified kills in 24 h, **5** in 7 days, or **10** in 30 days. It lasts **30 days** after the last unjustified kill over the limit. **C2** for the limits (TW-Skull-2005, TI-Frags "daily 3, weekly 5, monthly 10"). **C1** for the 30 days (TW-Skull-2005, TW-Red Skull 2005).
- **Banishment** comes at twice the red-skull limits (6/10/20). Automatic bans for this were added in 7.24. **C2** (TW-7.24, TW-Skull-2005, TA-Rules and TI-Frags "for ban: 6 / 10 / 20").
- **White skull**: death rules are unchanged; a white-skulled player dies like anyone else. After a kill the white skull lasts **15 min**, and each new offence resets it. **C1** (TW-Skull-2008).
- A kill counts as unjustified only against an unmarked victim, and only when the killer made the last hit or did the most damage. **C1** (TA-Rules).
- The skull system itself dates from 7.2, so it was in 7.4. **C2** (TW-7.2, TW-Skull infobox).

**Ours:**
- On death, the red skull gives 100% item loss (`player.cpp:850-853`). **MATCH.**
- Red skull limits: `addUnjustifiedDead()` (`player.cpp:3779-3800`) keeps one frag counter that decays over 24 h. With `KillsToRedSkull = 5` (`config.lua:46`) the skull comes at 5 overlapping 24 h frags, and bans come at `KillsToBan = 7` (`config.lua:13`). **MISMATCH.** 7.4 used three windows: 3 per day, 5 per week and 10 per month for the red skull, and 6/10/20 for bans.
- Red skull duration: `checkRedSkullTicks()` (`player.cpp:3825-3834`) removes the skull once the frag ticks run out, which takes about 24 h per frag. 7.4 used a fixed 30 days. **MISMATCH.**
- White skull time: `WhiteSkullTime = 3` minutes (`config.lua:43`, used at `player.cpp:3526-3528`), against 15 min in 7.4. **MISMATCH (C1).**

## 7. Promotion

**7.4 behaviour:**
- Promotion needs premium and level 20 and costs 20,000 gp. **C2** (TW-Promo-2005, TA-FAQ).
- On death it lowers experience and skill loss to 7% (§1). It does **not** change item loss (§4).
- It is **kept on death** unless the character is rooked. Rooking removes the promotion permanently. **C1** (TW-Promo history).
- It is **suspended while premium is inactive** and comes back free when premium returns. A suspended promotion also means the character loses 10% again. **C2** (TA-FAQ "promotion is deactivated … automatically granted back", TW-Promo, TW Premium_Account).

**Ours:**
- The 0.7 factor applies to vocation ids 5-8 (`player.h:780-782`). **MATCH.**
- Rooking resets the vocation (`player.cpp:2017`). **MATCH.**
- Nothing demotes a character, or cancels the 0.7 factor, when premium runs out. The code at `ioplayer.cpp:183-187` also uses a default-built `Account acc` whose `premEnd` is always 0, so that block never runs (and `FACCTempleID = 0` in `config.lua:239` disables it anyway). **MISMATCH:** a promoted free account keeps the 7% loss and the promoted regeneration.

## 8. Respawn

**7.4 behaviour:**
- You respawn in your **home town's temple**. **C2** (TW-Death-2005, TW-Temple).
- You come back with **full HP and mana**. **INF**; a reduced respawn with 40 HP and 0 mana applies only to black skulls, which did not exist in 7.4.
- Conditions such as poison, fire and haste end on death. **INF**.
- **Blessings did exist in 7.4.** The five original blessings were added in **7.2 (Dec 2003)**. Each one cost 10k and cut the loss by **1 percentage point**, from 10 to 9 … 5%, or from 7 down to 2% when promoted. They did not protect items, and all of them are lost on death. This contradicts the brief's "no blessings in 7.4" (**C2**: TW-7.2, TW-Bless infobox, TW-Bless-2005 written during 7.4, TW-Bless-2008, OTL-Bless). We could not confirm whether Tibiantis has them.

**Ours:**
- `die()` sets `loginPosition = masterPos` (`player.cpp:2111`), which is the town temple (`ioplayer.cpp:170-173`). **MATCH.**
- Full HP and mana are restored in `player.cpp:2248-2249`. **MATCH.**
- Persistent conditions are cleared at `player.cpp:2097-2109`. **MATCH.**
- Blessings: **not implemented.** The blessing NPCs (e.g. `npc/Edala.xml:8-10`, `npc/Humphrey.xml:9-10`) only reply with text, and `compat.lua:93-95` stubs return false. **MISMATCH** if blessings are wanted. It is a design choice if the owner decides 7.4 should have none.

## 9. Other death details

- **Rooking**: a mainland character whose experience falls below level 6 (under 1500 exp, so level 5 or lower) is reset to level 1 in Rookgaard, and loses its vocation, promotion and equipment. **C1** (TW-Rooking; its 7.4 details are INF).
  - Ours: `player.cpp:2180-2186` (`LevelToRook = 5`, `config.lua:228`) calls `sendToRook()` (`player.cpp:2015-2058`). That function deletes the inventory and equips a starter backpack, club and coat **before** `dropCorpse()`/`dropLoot()` runs. The new starter **backpack is then always dropped into the corpse on the mainland**, and the club and coat each have a 10% chance of dropping too. The rooked player arrives with no backpack. **BUG** (whatever the exact 7.4 rooking details were).
- **PvP zones / arenas**: no source shows player arenas in 7.4. **INF.** Ours: in `ZONE_PVP` there is no loss, the AoL is not used, and the player is teleported to the temple (`player.cpp:2062`, `2198-2211`). This is harmless if the map has no PvP zones.
- **Death message**: in 7.4 the client showed a "You are dead" dialog. **C1** (TW-Death-2005: "you must log out and login again"). Ours: `game.cpp:3823` sends "You are dead."; the level-down message is at `player.cpp:2192`. Close enough.
- **Corpse**: "You recognize X. He was killed by Y." (`player.cpp:2214-2233`). No source found for the 7.4 player-corpse text or for any loot protection on player corpses. **Not verified.**

---

## Mismatches, ranked by player impact

1. **Red skull limits and duration (§6).** Ours: 5 kills within about 24 h each, the skull fades with the frags, ban at 7. 7.4: red skull at 3/day, 5/week or 10/month, lasting 30 days; ban at 6/10/20. Because a red skull means losing every item, this decides how often PKers lose everything. (C2 limits, C1 duration)
2. **Promotion is never suspended when premium ends (§7).** Promoted free accounts keep the 7% loss (and promoted regeneration). The premium-expiry temple code in `ioplayer.cpp:183-187` never runs. (C2)
3. **Rooking drops the fresh starter kit into the mainland corpse (§9).** The rooked character arrives in Rook without a backpack. (bug)
4. **No blessings (§8).** 7.4 had five blessings, each cutting 1 percentage point, down to 5% (2% promoted). The NPCs exist but do nothing. This mismatches only if the owner wants them; it contradicts the brief's assumption. (C2)
5. **White skull lasts 3 min instead of 15 min (§6).** (C1)
6. Minor: the `loss_*` DB columns can silently override 10% per player (`ioplayer.cpp:161-164`). The ammo-slot "always lost" claim is C1 and was withdrawn, so no change is needed.

Confirmed matches: exp 10% and promoted 7% as a flat share of total experience (no 8.41 formula); magic level and skills 10%/7%; level loss removes its HP, mana and capacity; containers 100% with contents; 10% per other item; the AoL protects all items, is consumed, does not reduce exp/skill loss and fails under a red skull; red skull means all items lost; temple respawn at full HP and mana.

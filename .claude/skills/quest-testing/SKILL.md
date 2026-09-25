---
name: quest-testing
description: Make one Tibia 7.4 quest work on mintwall and prove it with tests - research the sources, ask the user the open questions, fix the map and scripts, and write an end-to-end test from a temple plus rule tests (level door, key, way in, way out). Use for any quest in task.md's quest list, or when the user asks to do, fix, check or test a quest.
---

# Quest testing (mintwall, Tibia 7.4)

A quest is always the same shape: **a way in** (walk, a hole, a pick, a portal), **gates on the way** (level door,
vocation door, key door, quest door, switches that need players, NPC talk), **the goal** (chests, a reward, an NPC
trade), and **a way out** (or none - some rooms trap you). Everything below serves one goal: a player gets exactly
the 7.4 experience. Never skip a step to make a test pass; what cannot be done yet becomes a todo in task.md.

One quest at a time. Work the steps in order.

## 1. Research - collect, never assume

Start from `docs/reference-74/quests.md` (the quest's section and the "Our server" line if there is one), then check
the sources below. Where they disagree, weigh them: 7.4-era text beats the current wiki; the map beats a guide.

| Source | How |
|---|---|
| TibiaWiki, pre-8.0 revision (the 7.x text) | `curl -s -A "Mozilla/5.0" "https://tibia.fandom.com/api.php?action=parse&oldid=<rev>&prop=wikitext&format=json"` - revision ids are in quests.md. WebFetch gets HTTP 402 there. |
| TibiaWiki, current spoiler | same API with `page=<Quest_Name>/Spoiler`. `{{Mapper Coords|129.167|123.141|13` = x 129*256+167, y 123*256+141. |
| Real-map chest table | `scratchpad/otland_quests.html` ("Quest System for 7.4 Realots"): `[uid] = {{item, count, aid}...}` - unique ids and rewards. |
| tibiaot74 (map + scripts) | clone at `scratchpad/otserver/server/data`; grep its `actions.xml` / `movements.xml` for the unique / action ids its map puts on the quest objects. Its items are 7.7 ids (>= 3000 unknown to us). |
| Inconcessus JS engine | `scratchpad/jsengine/data/740/world/Tibia74.otbm` - same source map as ours; shows what the original map data had. |
| Tibiantis | `tibiantis.life` quest list (scratchpad `life_quests.txt`): 7.4-server quest list, levels, rewards. |

Do not use Miracle, and no leaked CipSoft code.

## 2. Ask the good questions - then ask the user what the sources leave open

Answer each from the sources and write the answer down:

- **Level?** Is there a level door (gate of expertise, action id 1000 + level)? Which level, where?
- **Vocation?** Vocation door (action id 2001-2008)?
- **Premium?** (the city, the area)
- **Players?** 1, 2 (a switch someone must hold), 3+ (two switches), a team (monsters)?
- **Keys / items needed?** Key number (a locked door's action id = the key), pick, shovel, rope, scythe, boxes...
- **Order?** Does another quest come first (a key from it)?
- **NPC?** Which words move it on (`hi`, keyword, `yes`)? Level-dependent answers?
- **Reward?** Exact items and counts; one box each or choose one; once per character?
- **Way out?** Is there one without a switch / portal? Can a player be trapped (a lever turned off)?
- **Timers?** Things that close or respawn by themselves (how long?).

When a source does not settle one, **ask the user** (AskUserQuestion) with the options the sources suggest,
recommended first, and say what each source says. Examples that had to be asked: the Lighthouse room's way out
(no map has one), the Demon Helmet door key (current wiki says key 6010, 7.x text says nothing), how long the Gate
of the Lost Souls stays open. Record each decision in task.md and quests.md ("decided with the user <date>").

## 3. Read our map - what is there, what is missing

- Scan the area for scripted objects: `tests/tibia74/otbm.py` `read_tiles(path, area=((x1,y1,z1),(x2,y2,z2)))`,
  print items with `m.attrs` (action_id, unique_id, text, teleport). Compare the same area on tibiaot74's and the
  JS engine's maps.
- `python tools\quest-audit.py x1,y1,x2,y2` lists tibiaot74's quest objects in the area and whether ours has them
  (done / unscripted / missing). Our map lost many quest containers (Battle Axe skeleton, Dead Archer body): a
  missing reward container is the first thing to suspect. Place one with `map-set-attrs.py --add`.
- Is every action id / unique id on the quest's objects registered in `server/data/actions/actions.xml` /
  `movements/movements.xml`? Unregistered ids are the usual reason a quest does nothing.
- Can the planner get there? `plan(world, temple, goal, level=..., keys={...}, rope=True, pick=True, ...)`. If not,
  `python tools\map-regions.py <x,y,z> ...` traces regions backwards from the goal; the region with no way in shows
  the missing piece (an unscripted switch, a key door without a key number, a grate, a pick spot, a teleport that
  lands on another teleport).
- Things that bit before: the view range is x +-8 / y +-6 (check tiles only when near them); always-on-top items
  (coffins, counters) are used through whatever lies on them; the server teleports again when you land on a
  teleport or a hole ("down 2 floors"); a gate of expertise puts you in the doorway; two players cannot share a tile.

## 4. Fix the map and scripts

- Map edits: `python tools\map-set-attrs.py server\data\world\Tibia74.otbm x,y,z --id <item> --aid <n> --uid <n>`
  (also `--teleport x,y,z`, and `--add` to put a new item on top of a tile); `tools\map-remove-item.py` removes an
  item. Only the tile changes; unique ids are
  checked for clashes.
- Quest chests: action id 2000 + unique id = the storage; uid < 10000 is the reward item itself, otherwise
  `REWARDS[uid]` in `actions/scripts/quests/system.lua` (`{item, count, key aid, {contents {id, count, key aid}}}`),
  or the chest's own contents. `SAME_QUEST` (two objects, one reward), `SEALED_BY` (opens only when nothing lies on
  it) live there too. Prefer the real-map table's unique id.
- Switches / levers / step tiles: one script per quest in `actions/scripts/quests/` or `movements/scripts/`,
  header comment = the source quote, positions, which source gave each value, what was decided with the user.
  Pick the item for anything you create from how the map does it elsewhere (count what lies above ladders in
  dirt rooms, etc.), never by guess.
- Free action ids for new objects: check the map and both xml files first (51001-51010 are the Lighthouse and the
  Parchment Room).
- Engine (C++) changes need a rebuild: `cmd //c "C:\mintwall\server\build.bat"`. Never kill the user's server or
  client - ask them to stop it.

## 5. Test - end to end from a temple, plus the rules

One file per quest: `tests/quests/<city>/test_<quest>.py` (positions, the full run, the rule tests), starting
with `from quests.common import *` (temples, item ids, `edron_player`...; put anything a second quest needs
there). Helpers: `tests/tibia74/quest.py`, `route.py`.

- **The full run**: `strong(new_player, TEMPLE, premium_days=..., items=[Item(PICK), ...], group_id=TESTER_GROUP)`
  (testers are never attacked - demons would kill a waiting test), `walk_next_to` / `follow` with the ability
  (`level, vocation, keys, rope, pick, shovel, scythe, open_tiles`), `use_map_item` (moves things off the target like
  a player), `step_onto` (floor changes a switch made), `talk_to` (NPCs), `open_carried` (a reward bag). More
  players: create the second one after the first has left the temple. Assert every visible effect (the wall is
  gone, the portal is there) and every reward message, then "is empty" on a second use.
- **The rules** (fast, separate tests):
  - `assert_level_door(new_player, items, door, outside, level)` - level - 1 is refused ("Only the worthy may
    pass."), level passes.
  - `assert_no_way(world_map, start, goal, **ability)` / `assert_way(...)` - no way in without the key / the pick /
    the switch held; a way out, or none (trapped until a switch).
  - NPC gates: the answer below the level, and at the level (see `test_seymour_speaks_of_the_box_from_level_6`).
- Run the quest's file, then the whole `quests test_route.py test_spells.py` (the router is shared); a city
  alone: `pytest quests/thais`.
  `test_spells.py` fails on any Lua script that does not load.

## 6. Record it

- task.md: tick the quest with "Done <date>: what was scripted / fixed, decisions, the test names"; new todos for
  anything left.
- quests.md: an "**Our server (<date>):**" line with positions, ids and decisions.
- Tell the user what changed, what was decided, what is still open, and that a server restart picks it up. If they
  want to try it in game, move their character (only while it is logged out - the server saves over the database
  otherwise) with a sqlite UPDATE of `players.posx/posy/posz` in `server/db.db3`.

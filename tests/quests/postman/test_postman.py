"""The Postman Missions Quest (docs/reference-74/quests.md; server/data/npc/lib/postman.lua).

TibiaWiki 2005/2006 (the 7.x spoiler and transcripts): Kevin Postner between Thais and Kazordoon gives 10 missions and
an ADVANCEMENT after every second one. 1 the passages (Captain Bluebear Thais-Carlin, Uzon to Edron, Captain Seahorse to
Venore, Brodrosch to Cormaya), 2 the jammed mailbox on Folda (crowbar), 3 the bill for David Brassacres ("hat" x4),
4 twenty bones, 5 the present for Dermot on Fibula (never open it), 6 the new uniforms (Hugo, Talphion, Queen Eloise,
Noodles), 7 the six post officers' measurements, 8 Waldo's posthorn in the troll cave, 9 the letter bag into Santa's
mailbox on Vega, 10 the letter to Markwin in Mintwallin. Ranks: Assistant Postman (parcels 10 gp, letters 5 gp),
Postman (hat), Grand Postman (10 gp off a passage), Grand Postman for Special Operations (post horn), Arch Postman
(the royal mailboxes). Decided with the user 2026-09-30: 10 gp off; the royal mailboxes locked; Markwin wants his
bodyguards dead first; Noodles sniffs in any order and keeps nothing.

The quest crosses the whole map: each part starts at the nearest temple (or next to the NPC for Kevin's own steps)
with the progress the part before it leaves (storage 70200), and checks it by what the next NPC says.
"""
from quests.common import *  # noqa: F401,F403
from tibia74 import BACKPACK, Item
from tibia74.quest import next_to, talk_to

POSTMAN, LEGS, BONES_GIVEN, SNIFFED, MEASURES, MARKWIN_CALLED, PRESENT_TAKEN = \
    70200, 70201, 70202, 70203, 70204, 70205, 70206
(ROUTES, FOLDA, FOLDA_FIXED, BILL, BILL_DELIVERED, BONES_MISSION, BONES_DONE, RANK_POSTMAN, PRESENT, PRESENT_GIVEN,
 UNIFORMS, HUGO_ASKED, TALPHION, TALPHION_DONE, ELOISE, ELOISE_DONE, NOODLES, NOODLES_DONE, HUGO_ORDER, UNIFORMS_DONE,
 RANK_GRAND, MEASUREMENTS, MEASURED, WALDO, WALDO_DONE, RANK_SPECIAL, SANTA, SANTA_DONE, MARKWIN_LETTER, MARKWIN_DONE,
 RANK_ARCH) = range(1, 32)

CROWBAR, BONE, PRESENT_ITEM, LETTER_BAG, WALDOS_POSTHORN, LETTER_TO_MARKWIN = 2416, 2230, 2331, 2330, 2332, 2333
PARCEL, LETTER, GOLD = 2595, 2597, 2148
FOLDA_MAILBOX = (32013, 31562, 4)
KEVIN_RIGHT_DOOR, KEVIN_LEFT_DOOR = (32569, 32023, 6), (32567, 32023, 6)
PRESENT_CHEST, BAG_CHEST = (32569, 32024, 6), (32567, 32024, 6)
WALDO_DOOR, WALDO_BODY = (32515, 32248, 8), (32514, 32248, 8)
SANTA_MAILBOX = (31948, 31711, 6)
ROYAL_MAILBOX = (32423, 32095, 15)          # Mintwallin's
# "Four locations in Kazordoon Dwarf Mines, all surrounding the Mine Hub; you can also find one on the surface"
# (TibiaWiki 2006 Mailbox, oldid 72704: tibianews xcor=-304 ycor=-171 = about 32535,31970 by the other mailboxes' links;
# the current wiki's Mapper Coords 127.23|124.227|7 = 32535,31971): the map's mailbox in a brick nook west of Kazordoon
SURFACE_ROYAL_MAILBOX = (32535, 31969, 7)
# every royal (locked) mailbox of the 7.4 map: TibiaWiki 2006 Mailbox, the ones in 7.4 (task.md, Postman)
ROYAL_MAILBOXES = [(33307, 32292, 7), (32448, 31964, 10), (32454, 31975, 10), (32459, 31964, 10), (32995, 32446, 7),
                   ROYAL_MAILBOX, (33271, 31656, 8), (33083, 32184, 8), (32970, 31778, 7), SURFACE_ROYAL_MAILBOX]
ABILITY = dict(level=2000, vocation=4, rope=True, shovel=True, floors=12)


def postman(new_player, pos, progress=None, items=(), storage=None, **kwargs):
    """A strong premium tester with the quest's progress so far."""
    from tibia74.quest import strong
    storage = dict(storage or {})
    if progress:
        storage[POSTMAN] = progress
    p = strong(new_player, pos, premium_days=30, items=list(items), group_id=TESTER_GROUP, storage=storage, **kwargs)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def visit(p, items, world_map, npc, *lines, radius=2):
    from tibia74.route import walk_near
    walk_near(p, items, world_map, npc_pos(npc), radius=radius, **ABILITY)
    return talk_to(p, npc, *lines)


def said(replies, text):
    return any(text in r for r in replies)


def at_kevin(new_player, progress, items=(), storage=None):
    """Kevin's own steps: a character next to him."""
    storage = dict(storage or {})
    storage[POSTMAN] = progress
    storage[30001] = 1
    p = next_to(new_player, npc_pos("Kevin"), level=2000, premium_days=30, group_id=TESTER_GROUP, storage=storage,
                inventory={3: Item(1988, contents=list(items))})
    p.open_container(3)
    return p


def gold(p):
    worth = {"gold coin": 1, "platinum coin": 100, "crystal coin": 10000}
    return sum(worth.get(i.name, 0) * max(i.count, 1) for i in p.all_items())


# --- mission 1: the passages -----------------------------------------------------------------------------------------

def test_mission_1_kevin_sends_you_on_the_postal_routes(new_player):
    p = at_kevin(new_player, 0)
    replies = talk_to(p, "Kevin", "hi", "mission", "yes", "yes", "yes", "yes", "yes", "yes", "yes")
    assert said(replies, "You are not a member of our guild yet!"), replies
    assert said(replies, "First travel with Captain Bluebear's ship from Thais to Carlin"), replies
    assert said(replies, "Finally, find the technomancer Brodrosch and travel with him to the Isle of Cormaya."), replies
    assert said(replies, "Ok, remember: the Tibian mail service puts trust in you!"), replies
    # not before the four passages
    assert said(talk_to(p, "Kevin", "hi", "mission"), "You have not checked all the tours yet")


@pytest.mark.parametrize("captain, town, bit", [
    ("Captain Bluebear", "carlin", 1), ("Uzon", "edron", 2), ("Captain Seahorse", "venore", 4),
    ("Brodrosch", "cormaya", 8)])
def test_mission_1_each_passage_counts(new_player, db, captain, town, bit):
    p = next_to(new_player, npc_pos(captain), level=50, premium_days=30, group_id=TESTER_GROUP,
                storage={30001: 1, POSTMAN: ROUTES, LEGS: 0}, inventory={3: Item(1988, contents=[Item(2152, 3)])})
    before = p.pos
    replies = talk_to(p, captain, "hi", town, "yes")
    assert p.wait_for(lambda: p.pos != before and abs(p.pos[0] - before[0]) > 20, timeout=6), (p.pos, replies)
    p.logout()
    assert db.storage_after_logout(p.character.guid, LEGS, bit) == bit


def test_mission_1_another_passage_does_not_count(new_player, db):
    p = next_to(new_player, npc_pos("Captain Bluebear"), level=50, premium_days=30, group_id=TESTER_GROUP,
                storage={30001: 1, POSTMAN: ROUTES, LEGS: 0}, inventory={3: Item(1988, contents=[Item(2152, 3)])})
    before = p.pos
    talk_to(p, "Captain Bluebear", "hi", "venore", "yes")
    assert p.wait_for(lambda: p.pos != before and abs(p.pos[0] - before[0]) > 20, timeout=6), p.pos
    p.logout()
    assert db.storage_after_logout(p.character.guid, LEGS, 0) == 0


def test_mission_1_report_and_mission_2(new_player, items, world_map):
    """From the Thais temple to Kevin, once the four passages are done."""
    p = postman(new_player, THAIS_TEMPLE, ROUTES, storage={LEGS: 15})
    replies = visit(p, items, world_map, "Kevin", "hi", "mission", "yes")
    assert said(replies, "So you have finally made it!"), replies
    assert said(replies, "One of our mailboxes was reported to be jammed."), replies


# --- mission 2: Folda's mailbox --------------------------------------------------------------------------------------

def test_mission_2_the_jammed_mailbox_on_folda(new_player, items, world_map):
    from tibia74.route import carried, walk_next_to
    p = postman(new_player, CARLIN_TEMPLE, FOLDA, items=[Item(CROWBAR), Item(GOLD, 100)])
    replies = visit(p, items, world_map, "Nielson", "hi", "folda", "yes")
    assert p.wait_for(lambda: p.pos and abs(p.pos[0] - 32047) < 5 and abs(p.pos[1] - 31581) < 5, timeout=6), \
        (p.pos, replies)
    walk_next_to(p, items, world_map, FOLDA_MAILBOX, **ABILITY)
    crowbar = carried(p, items, lambda n: n == "crowbar")
    stack = p.tiles.get(FOLDA_MAILBOX, [])
    at = next(n for n, t in enumerate(stack) if getattr(t, "client_id", None) == items.by_server[2593].client_id)
    p.use_item_with(*crowbar, FOLDA_MAILBOX, items.by_server[2593].client_id, at)
    assert p.wait_for(lambda: p.messages("You fixed the mailbox."), timeout=3), p.text_messages[-2:]


# --- mission 3: the bill -----------------------------------------------------------------------------------------

def test_mission_3_the_bill_for_david_brassacres(new_player, items, world_map):
    p = postman(new_player, VENORE_TEMPLE, BILL)
    replies = visit(p, items, world_map, "A Strange Fellow", "hi", "hat", "hat", "hat", "hat", "bill", "yes")
    assert said(replies, "Uh? What do you want?!"), replies
    assert said(replies, "I am David Brassacres, the magnificent"), replies
    assert said(replies, "A bill? Oh boy so you are delivering another bill to poor me?"), replies
    assert said(replies, "Ok, ok, I'll take it."), replies
    assert p.wait_for(lambda: any(c.name.lower() == "rabbit" for c in p.creatures.values()), timeout=3)


def test_mission_3_the_fellow_denies_it_to_others(new_player, items, world_map):
    p = postman(new_player, VENORE_TEMPLE, FOLDA_FIXED)
    replies = visit(p, items, world_map, "A Strange Fellow", "hi", "hat", "hat", "hat", "hat", "bill")
    assert not said(replies, "I am David Brassacres"), replies


# --- missions 4 and 5: Kevin's bones, the present ---------------------------------------------------------------

def test_mission_4_bones_and_the_postman_hat(new_player):
    p = at_kevin(new_player, BONES_MISSION, items=[Item(BONE)] * 20)
    replies = talk_to(p, "Kevin", "hi", "mission", "yes")
    assert said(replies, "You have collected 1 bones."), replies
    replies = talk_to(p, "Kevin", "hi", "mission", "all")
    assert said(replies, "We have enough bones for the fund now."), replies
    assert not carries(p, "bone")
    replies = talk_to(p, "Kevin", "hi", "advancement", "yes")
    assert said(replies, "From now on it shall be known that you are a postman."), replies
    assert p.wait_for(lambda: carries(p, "post officers hat"), timeout=3), p.inventory_names()


def test_mission_5_the_present_for_dermot(new_player, items, world_map):
    from tibia74.route import walk_next_to
    p = at_kevin(new_player, RANK_POSTMAN)
    replies = talk_to(p, "Kevin", "hi", "mission", "yes")
    assert said(replies, "You will find the present behind the door here on the lower right side"), replies
    walk_next_to(p, items, world_map, KEVIN_RIGHT_DOOR, **ABILITY)
    use_map_item(p, items, KEVIN_RIGHT_DOOR, "closed door")
    assert p.wait_for(lambda: p.pos == KEVIN_RIGHT_DOOR, timeout=3), (p.pos, p.text_messages[-2:])
    use_map_item(p, items, PRESENT_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found a present."), timeout=3), p.text_messages[-2:]
    p.sleep(1.1)
    use_map_item(p, items, PRESENT_CHEST, "chest")              # only one, ever
    assert p.wait_for(lambda: p.messages("The chest is empty."), timeout=3), p.text_messages[-2:]
    assert carries(p, "present")
    p.logout()

    p = postman(new_player, FIBULA_TEMPLE, PRESENT, items=[Item(PRESENT_ITEM)])
    replies = visit(p, items, world_map, "Dermot", "hi", "present", "yes")
    assert said(replies, "You have a present for me?? Realy?"), replies
    assert said(replies, "Thank you very much!"), replies
    assert not carries(p, "present")


def test_mission_5_rules(new_player, items, world_map):
    """The door is sealed before the mission; an opened present is gone."""
    from tibia74.route import carried, walk_next_to
    p = at_kevin(new_player, BONES_DONE, items=[Item(PRESENT_ITEM)])
    walk_next_to(p, items, world_map, KEVIN_RIGHT_DOOR, **ABILITY)
    use_map_item(p, items, KEVIN_RIGHT_DOOR, "closed door")
    assert p.wait_for(lambda: p.messages("The door is sealed against unwanted intruders."), timeout=3), \
        p.text_messages[-2:]
    present = carried(p, items, lambda n: n == "present")
    p.use_item(*present)
    assert p.wait_for(lambda: not carries(p, "present"), timeout=3), p.inventory_names()


# --- mission 6: the uniforms ----------------------------------------------------------------------------------------

def test_mission_6_hugo_talphion_eloise_noodles(new_player, items, world_map):
    p = postman(new_player, VENORE_TEMPLE, UNIFORMS)
    replies = visit(p, items, world_map, "Hugo", "hi", "new set of uniforms", "new dress pattern")
    assert said(replies, "my dog ate the last dress pattern"), replies
    assert said(replies, "I have no clue where Kevin Postner got it from"), replies
    p.logout()

    p = postman(new_player, KAZORDOON_TEMPLE, TALPHION)
    replies = visit(p, items, world_map, "Talphion", "hi", *["new dress patterns"] * 5)
    assert said(replies, "DRESS FLATTEN?"), replies
    assert said(replies, "I'LL SENT A COPY TO KEVIN IMEDIATELY!"), replies
    p.logout()

    p = postman(new_player, CARLIN_TEMPLE, ELOISE)
    replies = visit(p, items, world_map, "Queen Eloise", "hail queen eloise", "uniforms")
    assert said(replies, "I will send some color samples via mail to Mr. Postner."), replies
    p.logout()

    p = postman(new_player, THAIS_TEMPLE, NOODLES, items=[Item(2235), Item(2219)])
    replies = visit(p, items, world_map, "Noodles", "hi", "sniff moldy cheese", "do you like that?")
    assert said(replies, "Meeep! Grrrrr! <spits>"), replies
    assert carries(p, "moldy cheese")                           # he keeps nothing
    p.logout()

    p = postman(new_player, VENORE_TEMPLE, HUGO_ORDER)
    replies = visit(p, items, world_map, "Hugo", "hi", "new dress pattern")
    assert said(replies, "you will get those ugly, stinking uniforms"), replies


def test_mission_6_kevin_between_the_steps(new_player):
    steps = [(HUGO_ASKED, "first ask the great technomancer in Kazordoon"),
             (TALPHION_DONE, "The mail with Talphion's instructions just arived."),
             (NOODLES_DONE, "Tell Hugo that we order those uniforms.")]
    for progress, text in steps:
        p = at_kevin(new_player, progress)
        replies = talk_to(p, "Kevin", "hi", "new dress pattern")
        assert said(replies, text), (progress, replies)
        p.logout()
    p = at_kevin(new_player, UNIFORMS_DONE)
    replies = talk_to(p, "Kevin", "hi", "advancement", "yes")
    assert said(replies, "you are a grand postman"), replies


# --- mission 7: the measurements -------------------------------------------------------------------------------------

def test_mission_7_the_six_measurements(new_player, items, world_map):
    visits = [(THAIS_TEMPLE, "Benjamin", ["hi", "measurements"], [], "tells you his measurements"),
              (CARLIN_TEMPLE, "Liane", ["hi", "measurements", "yes"], [Item(2544, 12)], "tells you her measurements"),
              (VENORE_TEMPLE, "Dove", ["hi", "measurements", "yes"], [Item(2681)], "whispers her measurements"),
              (EDRON_TEMPLE, "Chrystal", ["hi", "measurements"], [], "tells you her measurements")]
    for temple, npc, lines, carry, text in visits:
        p = postman(new_player, temple, MEASUREMENTS, items=carry)
        replies = visit(p, items, world_map, npc, *lines)
        assert said(replies, text), (npc, replies)
        p.logout()

    p = postman(new_player, KAZORDOON_TEMPLE, MEASUREMENTS)
    assert said(visit(p, items, world_map, "Lokur", "hi", "measurements", radius=3), "Better ask my armorer Kroox")
    assert said(visit(p, items, world_map, "Kroox", "hi", "lokurs measurements", radius=3),
                "tells you about Lokurs measurements")
    p.logout()

    p = postman(new_player, ABDENDRIEL_TEMPLE, MEASUREMENTS, items=[Item(GOLD, 100)] * 3)
    # 5 gold a roll until he rolls a 6 - forty rolls miss it once in 1500 runs
    replies = visit(p, items, world_map, "Olrik", "hi", "measurements", *["yes"] * 40)
    assert said(replies, "I will roll a dice."), replies
    assert said(replies, "You have won!"), replies


def test_mission_7_kevin_wants_all_six(new_player):
    p = at_kevin(new_player, MEASUREMENTS, storage={MEASURES: 1 + 2 + 4 + 8 + 16})
    assert said(talk_to(p, "Kevin", "hi", "mission"), "Bring me the measurements of Ben")
    p.logout()
    p = at_kevin(new_player, MEASUREMENTS, storage={MEASURES: 63 + 64})
    replies = talk_to(p, "Kevin", "hi", "mission", "yes", "yes")
    assert said(replies, "Our Courier Waldo has been missing for a while."), replies
    assert said(replies, "troll-infested Mountain east of Thais"), replies


# --- mission 8: Waldo ------------------------------------------------------------------------------------------------

def test_mission_8_waldo(new_player, items, world_map):
    from tibia74.route import walk_next_to
    p = postman(new_player, THAIS_TEMPLE, WALDO, items=[Item(SHOVEL)])
    walk_next_to(p, items, world_map, WALDO_DOOR, open_tiles={WALDO_DOOR}, **ABILITY)
    use_map_item(p, items, WALDO_DOOR, "closed door")
    assert p.wait_for(lambda: p.pos == WALDO_DOOR, timeout=3), (p.pos, p.text_messages[-2:])
    use_map_item(p, items, WALDO_BODY, "dead human")
    assert p.wait_for(lambda: p.messages("You have found Waldo's posthorn."), timeout=3), p.text_messages[-2:]
    assert carries(p, "Waldo's posthorn")
    p.logout()

    p = at_kevin(new_player, WALDO, items=[Item(WALDOS_POSTHORN)])
    replies = talk_to(p, "Kevin", "hi", "mission", "yes")
    assert said(replies, "Did you recover his posthorn?"), replies
    replies = talk_to(p, "Kevin", "hi", "advancement", "yes")
    assert said(replies, "you are a grand postman for special operations"), replies
    assert p.wait_for(lambda: carries(p, "post horn"), timeout=3), p.inventory_names()


def test_mission_8_waldos_door_is_sealed_before(new_player, items, world_map):
    from tibia74.route import walk_next_to
    p = postman(new_player, THAIS_TEMPLE, MEASURED, items=[Item(SHOVEL)])
    walk_next_to(p, items, world_map, WALDO_DOOR, open_tiles={WALDO_DOOR}, **ABILITY)
    use_map_item(p, items, WALDO_DOOR, "closed door")
    assert p.wait_for(lambda: p.messages("The door is sealed against unwanted intruders."), timeout=3), \
        p.text_messages[-2:]


# --- mission 9: Santa ------------------------------------------------------------------------------------------------

def test_mission_9_the_letter_bag_for_santa(new_player, items, world_map):
    from tibia74.route import carried, walk_next_to
    p = at_kevin(new_player, SANTA)
    walk_next_to(p, items, world_map, KEVIN_LEFT_DOOR, **ABILITY)
    use_map_item(p, items, KEVIN_LEFT_DOOR, "closed door")
    assert p.wait_for(lambda: p.pos == KEVIN_LEFT_DOOR, timeout=3), (p.pos, p.text_messages[-2:])
    use_map_item(p, items, BAG_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found a letterbag."), timeout=3), p.text_messages[-2:]
    p.logout()

    p = postman(new_player, CARLIN_TEMPLE, SANTA, items=[Item(LETTER_BAG), Item(GOLD, 100)])
    visit(p, items, world_map, "Nielson", "hi", "vega", "yes")
    assert p.wait_for(lambda: p.pos and abs(p.pos[0] - 32025) < 5 and abs(p.pos[1] - 31692) < 5, timeout=6), p.pos
    walk_next_to(p, items, world_map, SANTA_MAILBOX, **ABILITY)
    bag = carried(p, items, lambda n: n == "letterbag")
    mailbox = items.by_server[2334].client_id
    at = next(n for n, t in enumerate(p.tiles.get(SANTA_MAILBOX, [])) if getattr(t, "client_id", None) == mailbox)
    p.use_item_with(*bag, SANTA_MAILBOX, mailbox, at)
    assert p.wait_for(lambda: p.messages("You delivered the letters to Santa's mailbox."), timeout=3), \
        p.text_messages[-2:]
    assert p.wait_for(lambda: carries(p, "red bag"), timeout=3), p.inventory_names()


def test_mission_9_the_bag_needs_500_oz(new_player, items, world_map):
    from tibia74.route import walk_next_to
    storage = {30001: 1, POSTMAN: SANTA}
    p = next_to(new_player, npc_pos("Kevin"), level=8, premium_days=30, group_id=TESTER_GROUP, storage=storage)
    walk_next_to(p, items, world_map, KEVIN_LEFT_DOOR, level=8, rope=True)
    use_map_item(p, items, KEVIN_LEFT_DOOR, "closed door")
    assert p.wait_for(lambda: p.pos == KEVIN_LEFT_DOOR, timeout=3), (p.pos, p.text_messages[-2:])
    use_map_item(p, items, BAG_CHEST, "chest")
    assert p.wait_for(lambda: p.messages("You have found a letterbag. Weighing 500.00 oz it is too heavy."),
                      timeout=3), p.text_messages[-2:]
    assert not carries(p, "letterbag")


# --- mission 10: Markwin ---------------------------------------------------------------------------------------------

def test_mission_10_markwin(new_player, items, world_map):
    from tibia74.route import walk_near
    p = at_kevin(new_player, SANTA_DONE)
    replies = talk_to(p, "Kevin", "hi", "mission", "yes")
    assert said(replies, "It's a letter from the mother of Markwin, the king of Mintwallin."), replies
    assert p.wait_for(lambda: carries(p, "letter to Markwin"), timeout=3), p.inventory_names()
    p.logout()

    p = postman(new_player, THAIS_TEMPLE, MARKWIN_LETTER, items=[Item(LETTER_TO_MARKWIN)])
    walk_near(p, items, world_map, npc_pos("Markwin"), radius=2, **ABILITY)
    before = set(p.creatures)
    replies = talk_to(p, "Markwin", "hi")
    assert said(replies, "Intruder! Guards, take him down!"), replies
    names = ("minotaur guard", "minotaur archer", "minotaur mage")
    # his bodyguards: the minotaurs his "hi" called (Mintwallin's own stay out of it)
    new_guards = lambda: {c.id for c in p.creatures.values()  # noqa: E731
                          if c.id not in before and c.name.lower() in names}
    assert p.wait_for(lambda: len(new_guards()) >= 4, timeout=3), [c.name for c in p.creatures.values()]
    p.sleep(1)                                                  # all of them: up to 6 show (a taken tile gets none)
    called = new_guards()
    # alive until the client saw its health drop to 0 - not "removed from view": a guard that wanders (a tester is
    # left alone) off the screen is removed from view too, and Markwin counts it ("Guards! Take him down!")
    guards = lambda: [p.creatures[i] for i in called if i in p.creatures and p.creatures[i].health > 0]  # noqa: E731
    assert not said(talk_to(p, "Markwin", "hi", "letter", "yes"), "Uhm, well thank you")   # not while they live
    for _ in range(40):                                         # kill them, one after the other
        alive = guards()
        if not alive:
            break
        seen = [g for g in alive if g.pos]                      # they wander (a tester is left alone): in view now
        if not seen:                                            # out of view: back to Markwin, they stay near him
            walk_near(p, items, world_map, npc_pos("Markwin"), radius=2, **ABILITY)
            p.wait_for(lambda: any(g.pos for g in guards()), timeout=5)
            continue
        guard = min(seen, key=lambda g: max(abs(g.pos[0] - p.pos[0]), abs(g.pos[1] - p.pos[1])))
        walk_near(p, items, world_map, tuple(guard.pos), radius=1, **ABILITY)
        # after it, not at the tile it stood on: archers and mages keep moving (and keep their distance)
        p.set_fight_modes(fight=1, chase=1, safe=1)
        p.attack(guard.id)
        p.wait_for(lambda: guard.health == 0 or not guard.pos, timeout=15)
        p.attack(0)
        p.set_fight_modes(fight=1, chase=0, safe=1)
    assert not guards(), guards()
    walk_near(p, items, world_map, npc_pos("Markwin"), radius=2, **ABILITY)
    replies = talk_to(p, "Markwin", "hi", "letter", "yes")
    assert said(replies, "you defeated my guards!"), replies
    assert said(replies, "Uhm, well thank you, hornless being."), replies
    assert not carries(p, "letter to Markwin")
    p.logout()

    p = at_kevin(new_player, MARKWIN_DONE)
    replies = talk_to(p, "Kevin", "hi", "mission", "advancement", "yes")
    assert said(replies, "You are a true postofficer."), replies
    assert said(replies, "I grant you the title of archpostman."), replies


# --- the ranks' privileges -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("progress, letter, parcel", [(0, 8, 15), (BILL, 5, 10)], ids=["anyone", "assistant"])
def test_post_officers_charge_postmen_less(new_player, progress, letter, parcel):
    p = next_to(new_player, npc_pos("Benjamin"), level=50, group_id=TESTER_GROUP,
                storage={30001: 1, POSTMAN: progress} if progress else {30001: 1},
                inventory={3: Item(1988, contents=[Item(GOLD, 100)])})
    p.open_container(3)
    replies = talk_to(p, "Benjamin", "hi", "buy letter")
    assert said(replies, f"for {letter} gold"), replies
    replies = talk_to(p, "Benjamin", "hi", "buy parcel")
    assert said(replies, f"for {parcel} gold"), replies


def test_grand_postmen_sail_for_10_gp_less(new_player, db):
    p = next_to(new_player, npc_pos("Captain Bluebear"), level=50, premium_days=30, group_id=TESTER_GROUP,
                storage={30001: 1, POSTMAN: RANK_GRAND}, inventory={3: Item(1988, contents=[Item(2152, 2)])})
    before = p.pos
    replies = talk_to(p, "Captain Bluebear", "hi", "carlin", "yes")
    assert said(replies, "for 100 gold coins"), replies               # he quotes the postman's price
    assert p.wait_for(lambda: p.pos != before and abs(p.pos[1] - before[1]) > 20, timeout=6), p.pos
    p.logout()
    money = sum({2148: 1, 2152: 100, 2160: 10000}.get(r["itemtype"], 0) * r["count"]
                for r in db.items(p.character.guid))
    assert money == 200 - 100, f"paid {200 - money} gp"


def test_the_royal_mailboxes_are_locked_on_the_map():
    """Game::playerMoveItem refuses a non-Arch Postman on a mailbox with action id 51199."""
    from tibia74 import SERVER_DIR
    from tibia74.otbm import read_tiles
    xs, ys, zs = zip(*ROYAL_MAILBOXES)
    found = {t.pos: [i.attrs.get("action_id") for i in t.items if i.id == 2593]
             for t in read_tiles(SERVER_DIR / "data" / "world" / "Tibia74.otbm",
                                 area=((min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))))
             if t.pos in ROYAL_MAILBOXES}
    assert {pos: found.get(pos) for pos in ROYAL_MAILBOXES} == {pos: [51199] for pos in ROYAL_MAILBOXES}


@pytest.mark.parametrize("mailbox", [ROYAL_MAILBOX, SURFACE_ROYAL_MAILBOX], ids=["mintwallin", "kazordoon-surface"])
@pytest.mark.parametrize("progress, refused", [(MARKWIN_DONE, True), (RANK_ARCH, False)], ids=["not-yet", "archpostman"])
def test_royal_mailboxes_are_for_archpostmen(new_player, items, progress, refused, mailbox):
    storage = {30001: 1, POSTMAN: progress}
    # both stand in a small brick room with the door south of them: open it and post from the doorway
    door = (mailbox[0], mailbox[1] + 1, mailbox[2])
    p = new_player(pos=(door[0], door[1] + 1, door[2]), level=50, group_id=TESTER_GROUP, storage=storage,
                   inventory={3: Item(1988, contents=[Item(LETTER)])})
    p.open_container(3)
    if any(getattr(t, "client_id", None) == items.by_server[1225].client_id for t in p.tiles.get(door, [])):
        use_map_item(p, items, door, "closed door")             # the other case may have left it open
        p.sleep(0.5)
    step_onto(p, door)
    letter = items.by_server[LETTER].client_id
    cid, n = next((cid, n) for cid, c in p.containers.items() for n, i in enumerate(c.items) if i.client_id == letter)
    p.move_item(p.container_pos(cid, n), letter, n, mailbox, 1)
    p.sleep(1.5)
    assert bool(p.messages("Only archpostmen may use this mailbox.")) == refused, p.text_messages[-2:]

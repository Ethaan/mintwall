"""The Djinn War, both sides (docs/reference-74/quests.md; server/data/npc/lib/djinn.lua).

TibiaWiki 2006 (the 7.x transcripts): Melchior in Ankrahmun tells the word of greeting DJANNI'HAH; every djinn is
greeted with it "instead of 'hi'". Efreet: Ubaid (passage, no, yes, yes), Baa'leal (the supply thief - Shauna in
Carlin, Partos in the Thais prison - 600 gold), Alesar (a Tear of Daraman from Ashta'daramai's 4th floor), Malor
(Fa'hradin's lamp from the Orc King into Gabel's bedroom), then trade with Alesar and Yaman. Marid: Umar, Bo'ques (a
cookbook from Maryza in Kazordoon, 3 small sapphires), Fa'hradin (the spy report - Rata'mari in Mal'ouquah wants a
cheese), Gabel (the lamp into Malor's bedroom), then trade with Haroun and Nah'bob. Level 30 at the fortress gates,
40 at the Orc King's. Decided with the user 2026-09-29: DJANNI'HAH only; traders trade once the side is done; the
basin's northern tiles give the Tear; Maryza sells the cookbook any time.

The runs are split where the quest travels far (Carlin, Thais, Ulderek's Rock, Kazordoon): each part starts at the
nearest temple with the progress the part before it leaves (the storages), and checks that progress by what the next
NPC says.
"""
from quests.common import *  # noqa: F401,F403
from tibia74 import Item
from tibia74.quest import talk_to

DJINN_EFREET, DJINN_MARID, DJINN_WORD, DJINN_ORC_GUARDS = 70100, 70101, 70102, 70103
EFREET_PLEDGED, EFREET_THIEF, EFREET_PARTOS, EFREET_PAID, EFREET_TEAR, EFREET_TEAR_GIVEN, EFREET_LAMP, \
    EFREET_LAMP_PLACED, EFREET_DONE = range(1, 10)
MARID_PLEDGED, MARID_COOKBOOK, MARID_BOOK_GIVEN, MARID_SPY, MARID_CHEESE, MARID_REPORT, MARID_REPORT_GIVEN, \
    MARID_LAMP, MARID_LAMP_PLACED, MARID_DONE = range(1, 11)

FAHRADINS_LAMP, SPY_REPORT, TEAR_OF_DARAMAN, COOKBOOK, CHEESE = 2344, 2345, 2346, 2347, 2696
GOLD = 2148

MALOUQUAH_GATE, MALOUQUAH_OUTSIDE = (33050, 32622, 6), (33051, 32622, 6)
ASHTA_GATE, ASHTA_OUTSIDE = (33102, 32537, 6), (33102, 32538, 6)
ORC_KING_GATE = (32981, 31760, 9)
BASIN_NORTH, BASIN_SOUTH = (33109, 32529, 3), (33109, 32530, 3)
GABELS_LAMP, MALORS_LAMP = (33094, 32524, 1), (33048, 32630, 1)
ABILITY = dict(level=2000, rope=True, floors=12)


def djinn_player(new_player, pos=ANKRAHMUN_TEMPLE, efreet=None, marid=None, word=True, items=(), **kwargs):
    """A strong premium tester with the quest's progress so far."""
    from tibia74 import BACKPACK
    from tibia74.quest import strong
    storage = dict(kwargs.pop("storage", {}))
    if word:
        storage[DJINN_WORD] = 1
    if efreet:
        storage[DJINN_EFREET] = efreet
    if marid:
        storage[DJINN_MARID] = marid
    p = strong(new_player, pos, premium_days=30, items=list(items), group_id=TESTER_GROUP, storage=storage, **kwargs)
    p.open_container(BACKPACK)
    p.set_fight_modes(fight=1, chase=0, safe=1)
    return p


def visit(p, items, world_map, npc, *lines, radius=2, **ability):
    """Walk to where the NPC spawns and say the lines to it; returns everything it answered."""
    from tibia74.route import walk_near
    walk_near(p, items, world_map, npc_pos(npc), radius=radius, **{**ABILITY, **ability})
    return talk_to(p, npc, *lines)


def said(replies, text):
    return any(text in r for r in replies)


def gold(p):
    worth = {"gold coin": 1, "platinum coin": 100, "crystal coin": 10000}
    return sum(worth.get(i.name, 0) * max(i.count, 1) for i in p.all_items())


# --- Efreet ----------------------------------------------------------------------------------------------------------

def test_efreet_pledge_to_malor(new_player, items, world_map):
    p = djinn_player(new_player, word=False)
    replies = visit(p, items, world_map, "Melchior", "hi", "word of greeting")
    assert said(replies, "The djinns have an ancient code of honour."), replies

    replies = visit(p, items, world_map, "Ubaid", "djanni'hah", "passage")
    assert said(replies, "What? You know the word"), replies
    assert said(replies, "Only the mighty Efreet, the true djinn of Tibia, may enter Mal'ouquah!"), replies
    assert said(talk_to(p, "Ubaid", "djanni'hah", "passage", "no"), "Of cour... Huh!? No!?")
    replies = talk_to(p, "Ubaid", "djanni'hah", "passage", "no", "yes", "yes")
    assert said(replies, "So you pledge loyalty to king Malor"), replies
    assert said(replies, "Well then - welcome to Mal'ouquah."), replies

    replies = visit(p, items, world_map, "Baa'leal", "djanni'hah", "mission", "yes")
    assert said(replies, "You know the code human!"), replies
    assert said(replies, "Each mission and operation is a crucial step towards our victory!"), replies
    assert said(replies, "Well ... All right. You may only be a human"), replies


def test_efreet_supply_thief(new_player, items, world_map):
    # Carlin: the sheriff remembers a prisoner from Darama who went on to Thais
    p = djinn_player(new_player, CARLIN_TEMPLE, efreet=EFREET_THIEF)
    replies = visit(p, items, world_map, "Shauna", "hi", "water pipe", "prisoner")
    assert said(replies, "Oh, there's a waterpipe in one of my cells?"), replies
    assert said(replies, "My last prisoner? Hmm."), replies
    p.logout()

    # Thais prison: Partos gives himself away
    p = djinn_player(new_player, THAIS_TEMPLE, efreet=EFREET_THIEF)
    replies = visit(p, items, world_map, "Partos", "hi", "supplies", radius=3)     # through his cell door
    assert said(replies, "What!? I bet, Baa'leal sent you!"), replies
    p.logout()

    # back in Mal'ouquah: his name, 600 gold
    p = djinn_player(new_player, efreet=EFREET_PARTOS)
    before = gold(p)
    replies = visit(p, items, world_map, "Baa'leal", "djanni'hah", "mission", "yes", "partos")
    assert said(replies, "Did you find the thief of our supplies?"), replies
    assert said(replies, "Finally! What is his name then?"), replies
    assert said(replies, "You found the thief! Excellent work, soldier!"), replies
    assert p.wait_for(lambda: gold(p) == before + 600, timeout=3), gold(p) - before
    assert said(talk_to(p, "Baa'leal", "djanni'hah", "mission"), "Did you already talk to Alesar?")


def test_efreet_thief_needs_partos_first(new_player, items, world_map):
    """No reward for the name alone: Baa'leal wants the player to have found him."""
    p = djinn_player(new_player, efreet=EFREET_THIEF)
    before = gold(p)
    replies = visit(p, items, world_map, "Baa'leal", "djanni'hah", "mission", "yes", "partos")
    assert said(replies, "Hmmm... I don't think so. Return to Carlin and continue your search."), replies
    assert not said(replies, "You found the thief!"), replies
    p.sleep(1)
    assert gold(p) == before


def test_efreet_tear_of_daraman(new_player, items, world_map):
    from tibia74.quest import pick_up
    from tibia74.route import walk_next_to
    p = djinn_player(new_player, efreet=EFREET_PAID)
    replies = visit(p, items, world_map, "Alesar", "djanni'hah", "mission", "yes")
    assert said(replies, "So Baa'leal thinks you are up to do a mission for us?"), replies
    assert said(replies, "All right then, human. Have you ever heard of the 'Tears of Daraman'?"), replies

    # Ashta'daramai's 4th floor: the basin's southern half gives nothing, the northern half the tear
    walk_next_to(p, items, world_map, BASIN_SOUTH, **ABILITY)
    use_map_item(p, items, BASIN_SOUTH, "water basin")
    p.sleep(1)
    assert not any(getattr(t, "client_id", None) == items.by_server[TEAR_OF_DARAMAN].client_id
                   for t in p.tiles.get(p.pos, [])), p.tiles.get(p.pos)
    walk_next_to(p, items, world_map, BASIN_NORTH, **ABILITY)
    use_map_item(p, items, BASIN_NORTH, "water basin")
    tear = items.by_server[TEAR_OF_DARAMAN].client_id
    assert p.wait_for(lambda: any(getattr(t, "client_id", None) == tear for t in p.tiles.get(p.pos, [])), timeout=3), \
        (p.pos, p.tiles.get(p.pos), p.text_messages[-2:])
    here = p.pos
    pick_up(p, items, here, "tear of daraman")
    use_map_item(p, items, BASIN_NORTH, "water basin")          # one at a time
    p.sleep(1)
    assert not any(getattr(t, "client_id", None) == tear for t in p.tiles.get(here, []))

    replies = visit(p, items, world_map, "Alesar", "djanni'hah", "mission", "yes")
    assert said(replies, "Did you find the tear of Daraman?"), replies
    assert said(replies, "So you have made it? You have really managed to steal a Tear of Daraman?"), replies
    assert not carries(p, "tear of daraman")


def test_efreet_lamp_for_malor(new_player, items, world_map):
    p = djinn_player(new_player, efreet=EFREET_TEAR_GIVEN)
    replies = visit(p, items, world_map, "Malor", "djanni'hah", "mission", "yes")
    assert said(replies, "I guess this is the first time I entrust a human with a mission."), replies
    assert said(replies, "Well, listen. We are trying to acquire the ultimate weapon to defeat Gabel"), replies
    p.logout()

    # Ulderek's Rock: the Orc King calls his guards the first time, gives the lamp the second
    p = orc_king_gives_the_lamp(new_player, items, world_map, efreet=EFREET_LAMP)
    p.logout()

    # Gabel's bedroom: the lamp by his bed is exchanged for Fa'hradin's
    p = djinn_player(new_player, efreet=EFREET_LAMP, items=[Item(FAHRADINS_LAMP)])
    exchange_lamp(p, items, world_map, GABELS_LAMP)
    replies = visit(p, items, world_map, "Malor", "djanni'hah", "mission", "yes")
    assert said(replies, "Have you found Fa'hradin's lamp and placed it in Gabel's personal chambers?"), replies
    assert said(replies, "Well well, human. So you really have made it"), replies
    assert said(talk_to(p, "Malor", "djanni'hah", "permission"), "You are welcome to trade with Alesar and Yaman")


def orc_king_gives_the_lamp(new_player, items, world_map, **progress):
    p = djinn_player(new_player, VENORE_TEMPLE, **progress)
    replies = visit(p, items, world_map, "The Orc King", "hi")
    assert said(replies, "Arrrrgh! A dirty paleskin! To me my children! Kill them my guards!"), replies
    guards = lambda: sum(1 for c in p.creatures.values()  # noqa: E731
                         if c.pos and c.name.lower() in ("orc leader", "orc warlord", "slime"))
    assert p.wait_for(lambda: guards() >= 8, timeout=3), [c.name for c in p.creatures.values()]
    replies = talk_to(p, "The Orc King", "hi", "lamp", "malor")
    assert said(replies, "Harrrrk! You think you are strong now?"), replies
    assert said(replies, "I can sense your evil intentions to imprison a djinn!"), replies
    assert said(replies, "I was waiting for this day! Take the lamp and let Malor feel my wrath!"), replies
    assert p.wait_for(lambda: carries(p, "gemmed lamp"), timeout=3), p.inventory_names()
    # only one lamp
    assert not said(talk_to(p, "The Orc King", "hi", "lamp"), "I can sense your evil intentions")
    return p


def exchange_lamp(p, items, world_map, lamp):
    from tibia74.route import walk_next_to
    walk_next_to(p, items, world_map, lamp, **ABILITY)
    use_map_item(p, items, lamp, "gemmed lamp")
    assert p.wait_for(lambda: not carries(p, "gemmed lamp"), timeout=3), p.text_messages[-2:]


def test_efreet_traders(new_player, items, world_map):
    """Alesar and Yaman trade once Malor gave his permission - not before, and a "yes" then buys nothing."""
    p = djinn_player(new_player, efreet=EFREET_LAMP_PLACED, items=[Item(PLATINUM, 60)])   # 6000 gp in one stack: room in the bag for the wares
    replies = visit(p, items, world_map, "Yaman", "djanni'hah", "buy life ring", "yes")
    assert said(replies, "I don't trade with humans Malor has not given his permission."), replies
    assert not carries(p, "life ring")
    p.logout()

    p = djinn_player(new_player, efreet=EFREET_DONE, items=[Item(PLATINUM, 60)])   # 6000 gp in one stack: room in the bag for the wares
    replies = visit(p, items, world_map, "Yaman", "djanni'hah", "buy life ring", "yes")
    assert p.wait_for(lambda: carries(p, "life ring"), timeout=3), replies
    replies = visit(p, items, world_map, "Alesar", "djanni'hah", "buy dark helmet", "yes")
    assert p.wait_for(lambda: carries(p, "dark helmet"), timeout=3), replies


# --- Marid -----------------------------------------------------------------------------------------------------------

def test_marid_pledge_to_gabel(new_player, items, world_map):
    p = djinn_player(new_player, DARASHIA_TEMPLE, word=False)
    replies = visit(p, items, world_map, "Umar", "djanni'hah")                  # not yet: he laughs
    assert said(replies, "Hahahaha!"), replies
    p.logout()

    p = djinn_player(new_player, DARASHIA_TEMPLE)
    replies = visit(p, items, world_map, "Umar", "djanni'hah", "passage", "yes", "yes")
    assert said(replies, "Whoa? You know the word! Amazing"), replies
    assert said(replies, "If you want to enter our fortress you have to become one of us and fight the Efreet."), replies
    assert said(replies, "Are you sure? You pledge loyalty to king Gabel"), replies
    assert said(replies, "Oh. Ok. Welcome then. You may pass."), replies

    replies = visit(p, items, world_map, "Bo'ques", "djanni'hah", "mission", "yes")
    assert said(replies, "Hey! A human! What are you doing in my kitchen"), replies
    assert said(replies, "My collection of recipes is almost complete."), replies
    assert said(replies, "Fine! Even though I know so many recipes"), replies


def test_marid_cookbook(new_player, items, world_map):
    # Kazordoon: Maryza sells the cookbook for 150 gold, again and again
    p = djinn_player(new_player, KAZORDOON_TEMPLE, marid=MARID_COOKBOOK, items=[Item(GOLD, 100)] * 4)
    before = gold(p)
    replies = visit(p, items, world_map, "Maryza", "hi maryza", "cookbook", "yes")
    assert said(replies, "Do you like one for 150 gold?"), replies
    assert said(replies, "Here you are. Happy cooking!"), replies
    assert p.wait_for(lambda: carries(p, "cookbook"), timeout=3)
    assert gold(p) == before - 150
    assert said(talk_to(p, "Maryza", "hi maryza", "cookbook", "yes"), "Here you are. Happy cooking!")
    p.logout()

    # Ashta'daramai: Bo'ques takes it for 3 small sapphires; without it there is nothing
    p = djinn_player(new_player, DARASHIA_TEMPLE, marid=MARID_COOKBOOK)
    replies = visit(p, items, world_map, "Bo'ques", "djanni'hah", "cookbook", "yes")
    assert said(replies, "Too bad. I must have this book."), replies
    assert not carries(p, "small sapphire")
    p.logout()
    p = djinn_player(new_player, DARASHIA_TEMPLE, marid=MARID_COOKBOOK, items=[Item(COOKBOOK)])
    replies = visit(p, items, world_map, "Bo'ques", "djanni'hah", "cookbook", "yes")
    assert said(replies, "Do you have the cookbook of the dwarven kitchen with you? Can I have it?"), replies
    assert said(replies, "The book! You have it! Let me see!"), replies
    assert p.wait_for(lambda: sum(max(i.count, 1) for i in p.all_items() if i.name == "small sapphire") == 3, timeout=3)
    assert not carries(p, "cookbook")


def test_marid_spy_report(new_player, items, world_map):
    p = djinn_player(new_player, DARASHIA_TEMPLE, marid=MARID_BOOK_GIVEN, items=[Item(CHEESE)])
    replies = visit(p, items, world_map, "Fa'hradin", "djanni'hah", "mission")
    assert said(replies, "I have heard some good things about you from Bo'ques."), replies

    # Mal'ouquah's back door, the rat below: the password, not "hi"; first the cheese he wants, then the report
    assert not talk_to_near(p, items, world_map, "Rata'mari", "hi")
    replies = talk_to(p, "Rata'mari", "piedpiper", "spy report")
    assert said(replies, "Meep? I mean - hello!"), replies
    assert said(replies, "You have come for the report? Great!"), replies
    replies = talk_to(p, "Rata'mari", "piedpiper", "spy report", "yes")
    assert said(replies, "Ok, have you brought me the cheese, I've asked for?"), replies
    assert said(replies, "Meep! Meep! Great! Here is the spyreport for you!"), replies
    assert p.wait_for(lambda: carries(p, "spy report"), timeout=3), p.inventory_names()
    assert not carries(p, "cheese")

    replies = visit(p, items, world_map, "Fa'hradin", "djanni'hah", "mission", "yes")
    assert said(replies, "Did you already retrieve the spyreport?"), replies
    assert said(replies, "You really have made it? You have the report?"), replies


def talk_to_near(p, items, world_map, npc, *lines):
    from tibia74.route import walk_near
    walk_near(p, items, world_map, npc_pos(npc), radius=2, **ABILITY)
    return talk_to(p, npc, *lines)


def test_marid_lamp_for_gabel(new_player, items, world_map):
    p = djinn_player(new_player, DARASHIA_TEMPLE, marid=MARID_REPORT_GIVEN)
    replies = visit(p, items, world_map, "Gabel", "djanni'hah", "mission", "yes")
    assert said(replies, "Sooo. Fa'hradin has told me about your extraordinary exploit"), replies
    assert said(replies, "All right. Listen! Thanks to Rata'mari's report"), replies
    p.logout()

    p = orc_king_gives_the_lamp(new_player, items, world_map, marid=MARID_LAMP)
    p.logout()

    # Malor's bedroom: Gabel's followers exchange his lamp; the lamp by Gabel's bed does nothing for them
    p = djinn_player(new_player, marid=MARID_LAMP, items=[Item(FAHRADINS_LAMP)])
    exchange_lamp(p, items, world_map, MALORS_LAMP)
    p.logout()
    p = djinn_player(new_player, DARASHIA_TEMPLE, marid=MARID_LAMP_PLACED, items=[Item(GOLD, 100)] * 10)
    replies = visit(p, items, world_map, "Gabel", "djanni'hah", "mission", "yes")
    assert said(replies, "Have you found Fa'hradin's lamp and placed it in Malor's personal chambers?"), replies
    assert said(replies, "Daraman shall bless you and all humans!"), replies
    replies = visit(p, items, world_map, "Haroun", "djanni'hah", "buy power ring", "yes")
    assert p.wait_for(lambda: carries(p, "power ring"), timeout=3), replies


# --- the rules -------------------------------------------------------------------------------------------------------

def test_fortress_gates_are_level_30(new_player, items):
    assert_level_door(new_player, items, MALOUQUAH_GATE, MALOUQUAH_OUTSIDE, 30)
    assert_level_door(new_player, items, ASHTA_GATE, ASHTA_OUTSIDE, 30)


def test_djinns_do_not_answer_hi(new_player, items, world_map):
    """A djinn is greeted with DJANNI'HAH: "hi" gets a gatekeeper's jeer or nothing, never a conversation."""
    p = djinn_player(new_player, DARASHIA_TEMPLE)
    replies = visit(p, items, world_map, "Umar", "hi", "passage")
    assert said(replies, "Whoa! A human! This is no place for you"), replies
    assert not said(replies, "If you want to enter our fortress"), replies
    replies = visit(p, items, world_map, "Gabel", "hi", "job")
    assert replies == [], replies


def test_no_switching_sides(new_player, items, world_map):
    """A follower of one side gets no passage, missions or trade from the other."""
    p = djinn_player(new_player, DARASHIA_TEMPLE, efreet=EFREET_PLEDGED)
    replies = visit(p, items, world_map, "Umar", "djanni'hah", "passage")
    assert said(replies, "I don't believe you! You better go now."), replies
    p.logout()
    p = djinn_player(new_player, marid=MARID_PLEDGED)
    replies = visit(p, items, world_map, "Ubaid", "djanni'hah", "passage")
    assert said(replies, "Who do you think you are? A Marid? Shove off, moron."), replies
    replies = visit(p, items, world_map, "Baa'leal", "djanni'hah", "mission")
    assert not said(replies, "Each mission and operation"), replies


def test_orc_king_calls_his_guards_once(new_player, items, world_map):
    p = djinn_player(new_player, VENORE_TEMPLE, storage={DJINN_ORC_GUARDS: 1})
    replies = visit(p, items, world_map, "The Orc King", "hi", "lamp")
    assert said(replies, "Harrrrk! You think you are strong now?"), replies
    assert not said(replies, "I can sense your evil intentions"), replies       # nobody sent this one
    assert_level_door(new_player, items, ORC_KING_GATE, (ORC_KING_GATE[0], ORC_KING_GATE[1] + 1, 9), 40)

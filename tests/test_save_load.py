"""Timed save under load (task.md 3c, docs/production-plan.md §3): with many players online the save must not
freeze the game. The test server saves every 15 s (tibia74/server.py); here 100 characters carrying ~30
items each are online while one more keeps walking. The slowest step answer during the saves is the freeze
players would feel."""
import re
import threading
import time

from tibia74 import BACKPACK, EAST, WEST, Item

PLAYERS = 100
WALK = (32097, 32209, 7)             # Rookgaard, north of the temple, two rows off test_save.py's spot
PAUSE_BUDGET = 0.150                 # seconds: a step answered later than this is a visible freeze


def _loaded_backpack():
    bag = Item(1987, contents=[Item(2148, 50), Item(2152, 10), Item(2674, 5), Item(2666, 3)] + [Item(2120)] * 4)
    loose = [Item(2376), Item(2398), Item(2461), Item(2467), Item(2649), Item(2643), Item(2160, 2), Item(2787, 10),
             Item(2265), Item(2268, 3)]
    return Item(1988, contents=[bag] + loose + loose[:9])             # a backpack holds 20: ~29 items in all


def test_saving_many_players_does_not_freeze_the_game(new_player, server):
    players = []
    lock = threading.Lock()

    def login_batch(n):
        for _ in range(n):
            p = new_player(level=30, storage={30001: 1}, inventory={BACKPACK: _loaded_backpack()})
            with lock:
                players.append(p)

    threads = [threading.Thread(target=login_batch, args=(PLAYERS // 10,)) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(players) == PLAYERS

    walker = new_player(pos=WALK, level=8)
    start_log = server.log_offset()
    answers = []
    deadline = time.time() + 45                      # at least two 15 s saves
    while time.time() < deadline:
        start = time.time()
        assert walker.step(EAST if walker.pos[0] == WALK[0] else WEST), f"step refused at {walker.pos}"
        answers.append(time.time() - start)
        walker.sleep(1.0)                            # longer than a step takes: only a freeze delays the answer

    saves = [int(ms) for ms in re.findall(r"> Server saved in (\d+) ms", server.log()[start_log:])]
    assert len(saves) >= 2, f"saves seen: {saves}"
    slowest = max(answers)
    report = (f"{PLAYERS} players online: saves took {saves} ms; slowest step answer {slowest * 1000:.0f} ms "
              f"(median {sorted(answers)[len(answers) // 2] * 1000:.0f} ms, {len(answers)} steps)")
    print("\n" + report)
    assert slowest <= PAUSE_BUDGET, report

"""Watch a test live in the real client (MINTWALL_WATCH=1).

    set MINTWALL_TEST_PORT=7171        (your client is patched for 7171: stop the dev server first)
    set MINTWALL_WATCH=1
    tests\\.venv\\Scripts\\python.exe -m pytest tests\\test_quests.py -k bear -s

Log in with the real client as 9 / 9 (GM Mintwall - the test database is seed.sql) and type the /goto the
test prints. The quest character waits until it sees you next to it, then walks at a pace you can follow,
and stays a few seconds after the test before logging out.
"""
import os
import sys
import time

WATCH = os.environ.get("MINTWALL_WATCH", "") not in ("", "0")
STEP_DELAY = float(os.environ.get("MINTWALL_WATCH_STEP", "0.35")) if WATCH else 0.0
END_PAUSE = float(os.environ.get("MINTWALL_WATCH_END", "6")) if WATCH else 0.0
VIEWER = os.environ.get("MINTWALL_WATCH_VIEWER", "GM Mintwall")


def say(text):
    print(f"\n[watch] {text}", file=sys.stderr, flush=True)


def wait_for_viewer(p, timeout=180):
    """Hold the test until the viewer (a GM in the real client) stands in view of this character."""
    if not WATCH:
        return
    say(f"log in as 9/9 ({VIEWER}) and type:  /goto {p.name}    (waiting up to {timeout} s)")
    seen = p.wait_for(lambda: any(c.name == VIEWER for c in p.creatures.values()), timeout=timeout)
    say(f"{VIEWER} is here - starting" if seen else f"no {VIEWER} after {timeout} s - running anyway")
    time.sleep(2 if seen else 0)


def pace():
    if STEP_DELAY:
        time.sleep(STEP_DELAY)

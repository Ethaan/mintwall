"""Measures walking smoothness with the real client: a logging proxy between client and server.

    mise run walk-trace         (or: tests\\.venv\\Scripts\\python.exe tools\\walk-trace.py)

Stop the dev server first. This starts its own copy on port 7172 (same db.db3, so your characters
work) and listens on 7171 in its place, relaying bytes unchanged except the character list's port.
Log in, walk around (hold keys, change direction), then press Ctrl+C for a summary.
Every event is written to tools/.run/walk-trace.csv:

    ms            time since the proxy started
    event         step-request (client asked to walk), step-ok (server moved us), cancel-walk
                  (server refused/stopped the walk), text, teleport, turn, autowalk, stop-autowalk
    detail        direction / from -> to / message
    expected_step_ms   for step-ok: how long that step takes (1000 * ground speed / our speed)
"""
import asyncio
import csv
import os
import re
import queue
import subprocess
import threading
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER_DIR = ROOT / "server"
RUN_DIR = ROOT / "tools" / ".run"
PROXY_PORT, SERVER_PORT = 7171, 7172
DB = Path(os.environ.get("WALKTRACE_DB", SERVER_DIR / "db.db3")).resolve()

sys.path.insert(0, str(ROOT / "tests"))
from tibia74.client import GameClient   # noqa: E402  (the test suite's full 7.4 protocol parser)
from tibia74.items import Items         # noqa: E402
from tibia74.net import Reader          # noqa: E402

ITEMS = Items(SERVER_DIR / "data")
STEP_OPS = {0x65: "N", 0x66: "E", 0x67: "S", 0x68: "W", 0x6A: "NE", 0x6B: "SE", 0x6C: "SW", 0x6D: "NW"}
TURN_OPS = {0x6F: "N", 0x70: "E", 0x71: "S", 0x72: "W"}

t0 = time.perf_counter()
events = []   # (ms, event, detail, expected step ms)


def log(event, detail="", expected="", at=None):
    """at = time.perf_counter() when the packet arrived (packets are parsed later, off the relay path)."""
    ms = round(((at or time.perf_counter()) - t0) * 1000, 1)
    events.append((ms, event, detail, expected))
    print(f"{ms:10.1f}  {event:14} {detail}" + (f"  (step should take {expected} ms)" if expected else ""))


def on_client_packet(body: bytes, at: float):
    op = body[0]
    if op in STEP_OPS:
        log("step-request", STEP_OPS[op], at=at)
    elif op in TURN_OPS:
        log("turn", TURN_OPS[op], at=at)
    elif op == 0x64:
        log("autowalk", f"{body[1]} steps", at=at)
    elif op == 0x69:
        log("stop-autowalk", at=at)


def server_packet_handler():
    """Parses the server stream like the client does and logs our moves, cancel-walks and texts."""
    view = GameClient(ITEMS)
    view._send = lambda w: None   # passive: the real client answers pings itself
    broken = []

    def step_ms(frm, to):
        ground = next(iter(view.tiles.get(frm, [])), None)
        me = view.creatures.get(view.player_id)
        if ground is None or not me or not me.speed or not hasattr(ground, "client_id"):
            return ""
        ms = 1000 * ITEMS.client(ground.client_id).speed // me.speed
        return ms * 2 if frm[0] != to[0] and frm[1] != to[1] else ms

    def handle(body: bytes, at: float):
        if broken:
            return
        pos, cancels, texts = view.pos, view.cancel_walks, len(view.text_messages)
        try:
            view._parse_packet(Reader(body))
        except Exception as e:  # never break the relay because of the parser
            broken.append(e)
            log("parser-error", repr(e), at=at)
            return
        if pos and view.pos != pos:
            dist = max(abs(view.pos[0] - pos[0]), abs(view.pos[1] - pos[1]))
            if view.pos[2] == pos[2] and dist == 1:
                log("step-ok", f"{pos} -> {view.pos}", step_ms(pos, view.pos), at=at)
            elif abs(view.pos[2] - pos[2]) == 1 and dist <= 2:   # stairs, ramps, holes
                log("floor-change", f"{pos} -> {view.pos} ({len(body)} bytes)", step_ms(pos, view.pos), at=at)
            else:
                log("teleport", f"{pos} -> {view.pos}", at=at)
        if view.cancel_walks != cancels:
            log("cancel-walk", at=at)
        for _, text in view.text_messages[texts:]:
            log("text", text, at=at)

    return handle


def rewrite_charlist(body: bytes) -> bytes:
    """Login reply: [0x14 motd] 0x64 count {name, world, ip u32, port u16}* premdays -> port = proxy's."""
    b, p = bytearray(body), 0
    while p < len(b):
        op = b[p]; p += 1
        if op in (0x0A, 0x0B, 0x14):          # error / motd: one string
            p += 2 + int.from_bytes(b[p:p + 2], "little")
        elif op == 0x64:
            count = b[p]; p += 1
            for _ in range(count):
                for _string in range(2):      # character name, world name
                    p += 2 + int.from_bytes(b[p:p + 2], "little")
                p += 4                        # ip
                b[p:p + 2] = PROXY_PORT.to_bytes(2, "little")
                p += 2
            break
        else:
            break
    return bytes(b)


async def read_packet(reader):
    head = await reader.readexactly(2)
    return head, await reader.readexactly(int.from_bytes(head, "little"))


_work = queue.Queue()   # (handler, body, arrival time): parsed on a worker thread, not in the relay


def _worker():
    while True:
        handler, body, at = _work.get()
        handler(body, at)


async def pump(reader, writer, on_packet=None, transform=None):
    try:
        while True:
            head, body = await read_packet(reader)
            at = time.perf_counter()
            out = transform(body) if (body and transform) else body
            writer.write(head + out)       # forward first: the proxy must not slow the game down
            await writer.drain()
            if body and on_packet:
                _work.put((on_packet, body, at))
    except (asyncio.IncompleteReadError, ConnectionError):
        pass
    finally:
        writer.close()


def nodelay(writer):
    import socket
    writer.get_extra_info("socket").setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)


async def handle(c_reader, c_writer):
    try:
        head, first = await read_packet(c_reader)
    except (asyncio.IncompleteReadError, ConnectionError):
        return                                 # connected and left without a packet (port probe)
    s_reader, s_writer = await asyncio.open_connection("127.0.0.1", SERVER_PORT)
    nodelay(c_writer); nodelay(s_writer)   # the proxy itself must not add Nagle delays
    s_writer.write(head + first)
    is_login = first[:1] == b"\x01"
    if not is_login:
        log("game-connect")
    await asyncio.gather(
        pump(c_reader, s_writer, None if is_login else on_client_packet),
        pump(s_reader, c_writer, None if is_login else server_packet_handler(),
             rewrite_charlist if is_login else None),
    )


def start_server():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    cfg = (SERVER_DIR / "config.lua").read_text(encoding="latin-1")
    cfg = re.sub(r'(\bPort\s*=\s*)"[^"]*"', rf'\g<1>"{SERVER_PORT}"', cfg)
    cfg = re.sub(r'(\bSQL_DB\s*=\s*)"[^"]*"', lambda m: f'{m.group(1)}"{DB.as_posix()}"', cfg)
    config = RUN_DIR / "walk-trace.config.lua"
    config.write_text(cfg, encoding="latin-1")
    log_file = open(RUN_DIR / "walk-trace.server.log", "wb")
    proc = subprocess.Popen([str(SERVER_DIR / "avesta74.exe"), "-c", str(config)], cwd=SERVER_DIR,
                            stdout=log_file, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    print(f"starting server on {SERVER_PORT} (map load takes a few seconds)...")
    while b"Server Running" not in (RUN_DIR / "walk-trace.server.log").read_bytes():
        if proc.poll() is not None:
            sys.exit("server exited - is the dev server still running? see tools/.run/walk-trace.server.log")
        time.sleep(0.5)
    return proc


def summary():
    with open(RUN_DIR / "walk-trace.csv", "w", newline="") as f:
        csv.writer(f).writerows([("ms", "event", "detail", "expected_step_ms"), *events])
    reqs = sum(1 for e in events if e[1] == "step-request")
    oks = [e for e in events if e[1] == "step-ok"]
    cancels = sum(1 for e in events if e[1] == "cancel-walk")
    # How much later than its expected duration did each step end (next step started)?
    late = [b[0] - a[0] - a[3] for a, b in zip(oks, oks[1:]) if a[3] and b[0] - a[0] < 2000]
    print(f"\n{reqs} step requests, {len(oks)} steps, {cancels} cancel-walks, "
          f"{reqs - len(oks) - cancels} requests with no answer -> tools/.run/walk-trace.csv")
    if late:
        late.sort()
        print(f"step end vs expected: median {late[len(late) // 2]:+.0f} ms, worst {late[-1]:+.0f} ms, "
              f"{sum(x > 50 for x in late)} of {len(late)} steps more than 50 ms late")


async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", PROXY_PORT)
    print(f"proxy on {PROXY_PORT} -> {SERVER_PORT}. Log in with the client and walk; Ctrl+C to stop.")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    if len(sys.argv) == 3:            # other ports, e.g. to try it while the dev server runs
        PROXY_PORT, SERVER_PORT = int(sys.argv[1]), int(sys.argv[2])
    proc = start_server()
    threading.Thread(target=_worker, daemon=True).start()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        for _ in range(50):            # let the worker parse what is still queued
            if _work.empty():
                break
            time.sleep(0.1)
        summary()
        proc.terminate()

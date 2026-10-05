// Tests walk_pacer.h against a model of the 7.4 client's keyboard walking (client-mod\test.bat).
//
// The model, from walk-trace (2026-09-22): a key-down while standing walks at once; a key-down
// during a step is remembered (latest wins, or first wins - the tests run both) and walked when the
// step ends, also if the key was let go; a step ends rtt + the step time after it was sent.
// Windows repeats a held key after 500 ms, then every 33 ms. Our timer ticks every 15 ms.
//
// The first test also runs the DLL that is deployed since 2026-09-22 13:30 (a repeat every 33 ms
// from the press on) to show what the user felt: a tap walks two squares, letting go walks one more.
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <vector>
#include "walk_pacer.h"

using mintwall::Ms;

namespace {

const int N = 1, E = 2, S = 3, W = 4, NE = 5;   // our "virtual keys"
bool IsDiagonal(int vk) { return vk >= NE; }
const char* Name(int vk) { static const char* n[] = {"-", "N", "E", "S", "W", "NE"}; return n[vk]; }

// The deployed DLL of 2026-09-22 13:30: a repeat every 33 ms while held, no step learning
struct OldPacer {
    std::vector<int> held;
    bool pending = false;
    Ms next = 0;
    bool OnKeyDown(int vk, bool alreadyDown, Ms now) {
        for (int h : held) if (h == vk && alreadyDown) return false;
        Forget(vk);
        held.push_back(vk);
        next = now + 33;
        return true;
    }
    bool OnRepeatArrived(int, Ms) { pending = false; return true; }
    void OnKeyUp(int vk, Ms now) { Forget(vk); if (!held.empty()) next = now; }
    void Forget(int vk) { for (size_t i = 0; i < held.size(); ++i) if (held[i] == vk) { held.erase(held.begin() + i); break; } }
    void OnWalkSent(bool, Ms) {}
    int Due(Ms now) { return (held.empty() || pending || mintwall::Before(now, next)) ? 0 : held.back(); }
    void Posted(Ms now) { pending = true; next = now + 33; }
};

struct Walk { Ms at; int vk; };

struct Sim {
    // the client
    Ms rtt = 30;
    bool latestWins = true;
    std::function<Ms(int)> stepMs = [](int) { return Ms(450); };   // straight step time of walk #i
    Ms busyUntil = 0;
    int remembered = 0;
    std::vector<Walk> walks;
    // the user: key-downs/ups at given times
    struct KeyEvent { Ms at; int vk; bool down; };
    std::vector<KeyEvent> script;

    template <class Pacer> void Run(Pacer& p, Ms until) {
        std::vector<int> physical;                 // keys down, most recent last (Windows repeats it)
        std::vector<Ms> downAt(8, 0);
        struct Posted { Ms at; int vk; };
        std::vector<Posted> queue;                 // our posted repeats, picked up 1 ms later
        for (Ms now = 1000; now < until; ++now) {
            for (auto& e : script) {
                if (e.at != now) continue;
                if (e.down) {
                    physical.push_back(e.vk);
                    downAt[e.vk] = now;
                    if (p.OnKeyDown(e.vk, false, now)) ClientKey(p, e.vk, now);
                } else {
                    for (size_t i = 0; i < physical.size(); ++i)
                        if (physical[i] == e.vk) { physical.erase(physical.begin() + i); break; }
                    p.OnKeyUp(e.vk, now);
                }
            }
            // Windows' typematic repeat of the last key pressed, while it is down
            if (!physical.empty()) {
                int vk = physical.back();
                Ms held = now - downAt[vk];
                if (held >= 500 && (held - 500) % 33 == 0 && p.OnKeyDown(vk, true, now)) ClientKey(p, vk, now);
            }
            for (size_t i = 0; i < queue.size();) {
                if (queue[i].at + 1 <= now) {
                    int vk = queue[i].vk;
                    queue.erase(queue.begin() + i);
                    if (p.OnRepeatArrived(vk, now)) ClientKey(p, vk, now);
                } else {
                    ++i;
                }
            }
            if (remembered && !mintwall::Before(now, busyUntil)) {
                int vk = remembered;
                remembered = 0;
                Send(p, vk, now);
            }
            if (now % 15 == 0) {
                if (int vk = p.Due(now)) { queue.push_back({now, vk}); p.Posted(now); }
            }
        }
    }

    template <class Pacer> void ClientKey(Pacer& p, int vk, Ms now) {
        if (!mintwall::Before(now, busyUntil)) Send(p, vk, now);
        else if (latestWins || !remembered) remembered = vk;
    }

    template <class Pacer> void Send(Pacer& p, int vk, Ms now) {
        Ms step = stepMs(static_cast<int>(walks.size())) * (IsDiagonal(vk) ? 2 : 1);
        walks.push_back({now, vk});
        p.OnWalkSent(IsDiagonal(vk), now);
        busyUntil = now + rtt + step;
    }

    std::vector<int> Keys() const { std::vector<int> v; for (auto& w : walks) v.push_back(w.vk); return v; }
    // longest wait between the end of one step and the start of the next, walks [from, to)
    Ms WorstGap(size_t from, size_t to = static_cast<size_t>(-1)) const {
        Ms worst = 0;
        for (size_t i = from + 1; i < walks.size() && i < to; ++i) {
            Ms end = walks[i - 1].at + rtt + stepMs(static_cast<int>(i - 1)) * (IsDiagonal(walks[i - 1].vk) ? 2 : 1);
            Ms gap = walks[i].at > end ? walks[i].at - end : 0;
            if (gap > worst) worst = gap;
        }
        return worst;
    }
};

int g_failed = 0, g_run = 0;

void Check(bool ok, const char* test, const char* what, const Sim& sim) {
    ++g_run;
    if (ok) { std::printf("  ok    %s: %s\n", test, what); return; }
    ++g_failed;
    std::printf("  FAIL  %s: %s - walked", test, what);
    for (auto& w : sim.walks) std::printf(" %s@%u", Name(w.vk), w.at);
    std::printf("\n");
}

Sim Hold(int vk, Ms from, Ms to) { Sim s; s.script = {{from, vk, true}, {to, vk, false}}; return s; }

void ForBothMemories(const std::function<void(bool latestWins, const char* label)>& test) {
    test(true, "latest-wins");
    test(false, "first-wins");
}

void TestTap() {
    // A tap (key down ~120 ms) while standing walks one square
    for (Ms len : {60u, 120u, 200u, 300u}) {
        Sim s = Hold(N, 2000, 2000 + len);
        mintwall::WalkPacer p;
        s.Run(p, 5000);
        char what[64]; std::snprintf(what, sizeof what, "a %u ms tap walks 1 square", len);
        Check(s.walks.size() == 1, "tap", what, s);
    }
    Sim old = Hold(N, 2000, 2120);
    OldPacer op;
    old.Run(op, 5000);
    std::printf("  (the deployed 2026-09-22 DLL walks %zu squares for a 120 ms tap)\n", old.walks.size());
}

void TestHoldAndRelease() {
    // Steps take 480 ms (450 + rtt 30). Holding for 3.5 steps walks 4 squares and stops: no step
    // starts after the key is let go (the old DLL walked a 5th). A first walk teaches the DLL the
    // step time (it keeps it); the very first walk of a session may pause once while it learns.
    ForBothMemories([](bool latest, const char* label) {
        for (Ms stepMs : {450u, 300u, 700u, 150u}) {
            Ms cycle = stepMs + 30, test = 2000 + 10 * cycle;
            Sim s;
            s.script = {{2000, E, true}, {2000 + 5 * cycle, E, false},              // learning
                        {test, E, true}, {test + cycle * 7 / 2, E, false}};
            s.latestWins = latest;
            s.stepMs = [stepMs](int) { return stepMs; };
            mintwall::WalkPacer p;
            s.Run(p, test + 8 * cycle);
            size_t first = 0;
            while (first < s.walks.size() && s.walks[first].at < test) ++first;
            char what[128];
            std::snprintf(what, sizeof what, "[%s] step %u ms: learning walk pauses at most once (worst %u ms)",
                          label, stepMs, s.WorstGap(0, first));
            Check(s.WorstGap(1, first) <= 20, "hold", what, s);
            std::snprintf(what, sizeof what, "[%s] step %u ms, held 3.5 steps -> 4 squares", label, stepMs);
            Check(s.walks.size() - first == 4, "hold", what, s);
            std::snprintf(what, sizeof what, "[%s] step %u ms, no pause between steps (worst %u ms)", label,
                          stepMs, s.WorstGap(first));
            Check(s.WorstGap(first) <= 20, "hold", what, s);
        }
    });
    Sim old = Hold(E, 2000, 2000 + 480 * 7 / 2);
    OldPacer op;
    old.Run(op, 9000);
    std::printf("  (the deployed 2026-09-22 DLL walks %zu squares when held 3.5 steps)\n", old.walks.size());
}

void TestLongHoldPace() {
    // A long walk: one step per step time, never faster than the client walks, no pauses after learning
    ForBothMemories([](bool latest, const char* label) {
        Sim s = Hold(W, 2000, 2000 + 20 * 480 - 240);
        s.latestWins = latest;
        mintwall::WalkPacer p;
        s.Run(p, 14000);
        char what[96];
        std::snprintf(what, sizeof what, "[%s] held 19.5 steps -> 20 squares, worst pause %u ms", label, s.WorstGap(0));
        Check(s.walks.size() == 20 && s.WorstGap(0) <= 20, "long hold", what, s);
        std::snprintf(what, sizeof what, "[%s] learned step %u ms (client: 480)", label, p.StepMs());
        Check(p.StepMs() >= 470 && p.StepMs() <= 490, "long hold", what, s);
    });
}

void TestGroundChanges() {
    // Mud (900 ms) then road (200 ms) then grass (450): pauses only right after a change, and short
    Sim s = Hold(S, 2000, 2000 + 4 * 930 + 6 * 230 + 6 * 480 - 100);
    s.stepMs = [](int i) { return Ms(i < 4 ? 900 : i < 10 ? 200 : 450); };
    mintwall::WalkPacer p;
    s.Run(p, 14000);
    char what[96];
    std::snprintf(what, sizeof what, "mud -> road -> grass: 16 squares, worst pause %u ms", s.WorstGap(0));
    Check(s.walks.size() == 16 && s.WorstGap(0) <= 250, "ground", what, s);
    // on the road, pauses are gone after 2 steps
    Ms worstRoad = 0;
    for (size_t i = 6; i < 10; ++i) {
        Ms end = s.walks[i - 1].at + 230;
        if (s.walks[i].at > end + worstRoad) worstRoad = s.walks[i].at - end;
    }
    std::snprintf(what, sizeof what, "road: no pause from the 3rd step on (worst %u ms)", worstRoad);
    Check(worstRoad <= 20, "ground", what, s);
}

void TestCorner() {
    // Holding N, a tap on E mid-step: the step after this one is E, then N goes on - nothing lost,
    // nothing extra
    ForBothMemories([](bool latest, const char* label) {
        Sim s;
        s.latestWins = latest;
        s.script = {{2000, N, true}, {2000 + 480 + 200, E, true}, {2000 + 480 + 300, E, false}, {2000 + 5 * 480 - 240, N, false}};
        mintwall::WalkPacer p;
        s.Run(p, 9000);
        std::vector<int> want = {N, N, E, N, N};
        char what[96];
        std::snprintf(what, sizeof what, "[%s] hold N, tap E mid-step -> N N E N N", label);
        Check(s.Keys() == want, "corner", what, s);
    });
}

void TestSecondKeyTakesOver() {
    // Hold N, press and hold E (E walks), let go of E: N goes on without a pause and without an extra E
    Sim s;
    s.script = {{2000, N, true}, {2000 + 480 + 100, E, true}, {2000 + 3 * 480 + 100, E, false}, {2000 + 6 * 480 - 240, N, false}};
    mintwall::WalkPacer p;
    s.Run(p, 9000);
    std::vector<int> want = {N, N, E, E, N, N};
    char what[96];
    std::snprintf(what, sizeof what, "hold N, hold E for 2 steps, let go of E -> N N E E N N (worst pause %u ms)", s.WorstGap(0));
    Check(s.Keys() == want && s.WorstGap(0) <= 20, "two keys", what, s);
}

void TestDiagonal() {
    Sim s = Hold(NE, 2000, 2000 + 3 * 930 + 300);
    mintwall::WalkPacer p;
    s.Run(p, 9000);
    char what[96];
    std::snprintf(what, sizeof what, "diagonal held 3.3 steps -> 4 squares, worst pause %u ms", s.WorstGap(0));
    Check(s.walks.size() == 4 && s.WorstGap(0) <= 20, "diagonal", what, s);
}

void TestQuickTaps() {
    // Tapping the same key 3 times, once per step, walks 3 squares
    Sim s;
    for (int i = 0; i < 3; ++i) {
        s.script.push_back({Ms(2000 + i * 600), E, true});
        s.script.push_back({Ms(2000 + i * 600 + 100), E, false});
    }
    mintwall::WalkPacer p;
    s.Run(p, 6000);
    Check(s.walks.size() == 3, "taps", "3 taps -> 3 squares", s);
}

}  // namespace

int main() {
    TestTap();
    TestHoldAndRelease();
    TestLongHoldPace();
    TestGroundChanges();
    TestCorner();
    TestSecondKeyTakesOver();
    TestDiagonal();
    TestQuickTaps();
    std::printf("%d of %d checks passed\n", g_run - g_failed, g_run);
    return g_failed ? EXIT_FAILURE : EXIT_SUCCESS;
}

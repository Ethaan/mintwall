// walk_pacer.h - when mintwall.dll gives the 7.4 client a movement-key repeat. No Win32 here, so
// test_walk_pacer.cpp can run it against a model of the client (client-mod\test.bat).
//
// What the 7.4 client does with movement keys (walk-trace, 2026-09-22):
//  - a key-down while it stands still walks at once (sends the step, 0x65-0x6D);
//  - a key-down during a step is remembered and walked when the step ends - even if the key was
//    let go meanwhile;
//  - it keeps one step in flight, so its own pace is the step time (+ the server's answer).
// Windows repeats a held key after 500 ms and then ~30 times a second. The first is the pause
// after every new direction; the second keeps the client's memory always full, so letting go of a
// key walks one square too many and a quick tap walks two.
//
// So: Windows' repeats of movement keys are dropped, and the client gets exactly one repeat per
// step, `leadMs` before the step should end. The step time is learned from the client's own walk
// packets (haste, roads, mud are followed); the most recently pressed key still held decides.
#pragma once
#include <cstdint>

namespace mintwall {

typedef uint32_t Ms;   // a millisecond clock that may wrap: compare with Before()

inline bool Before(Ms a, Ms b) { return static_cast<int32_t>(a - b) < 0; }
inline Ms Later(Ms a, Ms b) { return Before(a, b) ? b : a; }

class WalkPacer {
public:
    Ms defaultStepMs = 450;    // until a step time is learned: a fresh character on grass
    Ms leadMs = 60;            // our repeat reaches the client this long before its step ends
    Ms retryMs = 250;          // a key-down that led to no step (wall, busy): offer the key again
    Ms maxLearnGapMs = 1500;   // longer gaps between walk packets are not one step
    Ms pendingTimeoutMs = 500; // a posted repeat that never arrived (window gone) is forgotten
    Ms immediateMs = 25;       // a step sent this soon after our repeat: the client was idle (we were late)
    Ms minStepMs = 50;

    // A key-down of a movement key from Windows (not one of ours). false = drop it.
    bool OnKeyDown(int vk, bool alreadyDown, Ms now) {
        if (alreadyDown && IsHeld(vk)) return false;   // Windows' own repeat: ours replace it
        Press(vk, now);                                // a press goes through: the client walks it
        return true;
    }

    // One of our repeats reached the client's queue. false = drop it (the key was let go meanwhile).
    bool OnRepeatArrived(int vk, Ms now) {
        pending_ = false;
        if (!IsHeld(vk)) return false;
        walkFromRepeat_ = true;
        repeatArrivedAt_ = now;
        return true;
    }

    void OnKeyUp(int vk, Ms now) {
        bool wasTop = heldCount_ && held_[heldCount_ - 1] == vk;
        Release(vk);
        // The key still held takes over at the next step end - not at once: a key-down now would
        // replace a tapped key the client still remembers (a corner) or just walk one too many.
        if (wasTop && heldCount_ && !pressUnwalked_) nextRepeat_ = Later(now, StepEnd(now) - Lead());
    }

    // The timer found a key up whose key-up we did not see (it went to another window).
    void Forget(int vk) { Release(vk); }

    // The client sent a step (diagonal: 0x6A-0x6D).
    void OnWalkSent(bool diagonal, Ms now) {
        if (walkFromRepeat_ && walked_ && Before(now - lastWalk_, maxLearnGapMs)) {
            Ms took = now - lastWalk_;                     // the previous step, walked back to back
            if (lastDiagonal_) took /= 2;
            // Sent as soon as our repeat came: the client had been standing for who knows how long,
            // so the step is shorter than this (haste, a road). Come in well early next time: an
            // early repeat is remembered and walked when the step ends, which measures it exactly.
            if (Before(now - repeatArrivedAt_, immediateMs + 1)) took /= 2;
            stepMs_ = Later(took, minStepMs);
        }
        walkFromRepeat_ = false;
        pressUnwalked_ = false;
        walked_ = true;
        lastWalk_ = now;
        lastDiagonal_ = diagonal;
        Ms step = StepFor(diagonal);
        nextRepeat_ = now + (step > Lead() ? step - Lead() : 0);
    }

    // The movement key to give the client a repeat of now, or 0. Call Posted() once it is posted.
    int Due(Ms now) {
        if (pending_ && !Before(now - pendingSince_, pendingTimeoutMs)) pending_ = false;
        if (!heldCount_ || pending_ || Before(now, nextRepeat_)) return 0;
        return held_[heldCount_ - 1];
    }

    void Posted(Ms now) {
        pending_ = true;
        pendingSince_ = now;
        pressUnwalked_ = false;
        nextRepeat_ = now + retryMs;   // the step it leads to reschedules; if none comes, again
    }

    int HeldCount() const { return heldCount_; }
    int Held(int i) const { return held_[i]; }
    Ms StepMs() const { return stepMs_ ? stepMs_ : defaultStepMs; }

private:
    static const int kMaxHeld = 8;
    int held_[kMaxHeld] = {};          // movement keys held down, most recent last
    int heldCount_ = 0;
    bool pending_ = false;             // one repeat posted and not yet picked up
    Ms pendingSince_ = 0;
    Ms nextRepeat_ = 0;
    Ms stepMs_ = 0;                    // learned duration of a straight step, 0 = not yet
    bool walked_ = false;
    Ms lastWalk_ = 0;
    bool lastDiagonal_ = false;
    bool walkFromRepeat_ = false;      // the client was just given one of our repeats
    Ms repeatArrivedAt_ = 0;
    bool pressUnwalked_ = false;       // a real press the client has not walked yet (remembered mid-step)

    Ms Lead() const { return leadMs; }
    Ms StepFor(bool diagonal) const { return StepMs() * (diagonal ? 2 : 1); }
    Ms StepEnd(Ms now) const { return walked_ ? lastWalk_ + StepFor(lastDiagonal_) : now; }

    bool IsHeld(int vk) const {
        for (int i = 0; i < heldCount_; ++i)
            if (held_[i] == vk) return true;
        return false;
    }

    void Release(int vk) {
        int out = 0;
        for (int i = 0; i < heldCount_; ++i)
            if (held_[i] != vk) held_[out++] = held_[i];
        heldCount_ = out;
    }

    void Press(int vk, Ms now) {
        Release(vk);
        if (heldCount_ == kMaxHeld) Release(held_[0]);
        held_[heldCount_++] = vk;
        walkFromRepeat_ = false;
        pressUnwalked_ = true;
        // Standing still, the client walks this press at once; mid-step it remembers it and walks it
        // when the step ends. Either way its walk packet schedules our first repeat. Until then no
        // repeat (it could replace the remembered press); if no step comes at all, offer it again.
        nextRepeat_ = Later(now, StepEnd(now)) + retryMs;
    }
};

}  // namespace mintwall

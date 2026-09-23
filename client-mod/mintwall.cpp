// mintwall.dll - client-side improvements for Tibia-mintwall.exe (the original 7.4 client).
// tools/patch-client.ps1 adds this DLL to the exe's import table, so Windows loads it at start-up.
//
// Smooth keyboard walking. The 7.4 client walks on WM_KEYDOWN: after pressing a direction it takes
// one step and waits for Windows' key-repeat delay (500 ms by default) before walking on. And a
// key-down that arrives during a step is remembered and walked when the step ends - so with fast
// repeats, letting go mid-step still walks one square too many.
//
// So we drop Windows' own repeats for the movement keys and give the client exactly one repeat per
// step, timed to arrive shortly before the step ends: then holding a key walks without a pause, and
// letting go stops at once. Step times are learned from the client's own walk packets (its send()
// is hooked; the 7.4 protocol is not encrypted), so haste, rings and roads are followed. The most
// recently pressed movement key that is still held decides the direction.
//
// The keyboard hook sits on the UI thread's message queue (WH_GETMESSAGE), before MFC and
// TranslateMessage, so it works whichever of the client's windows has the keyboard focus. The
// client sends from that same thread (WSAAsyncSelect), so no locking is needed.
#include <winsock2.h>
#include <windows.h>

namespace {

const DWORD kDefaultStepMs = 450;        // until a step time is learned: a fresh character's step
const DWORD kLeadMs = 60;                // our repeat must reach the client before its step ends
const DWORD kRetryMs = 250;              // no step came of a repeat (wall, busy): offer the key again
const DWORD kMaxLearnGapMs = 1500;       // longer gaps between walk packets are not one step
const DWORD kPendingTimeoutMs = 500;     // a posted repeat that never arrived (window gone) is forgotten
const LPARAM kSynthetic = 1 << 25;       // reserved bit of a keystroke's lParam: marks our own repeats
const LPARAM kRepeatBit = 1 << 30;       // "the key was already down"

struct HeldKey { WPARAM vk; LPARAM lParam; HWND hwnd; };
HeldKey g_held[8];                       // movement keys held down, most recent last
int g_heldCount = 0;
bool g_pending = false;                  // one repeat posted and not yet picked up
DWORD g_pendingSince = 0;
DWORD g_nextRepeat = 0;                  // when to give the client the next repeat
HHOOK g_hook = nullptr;
UINT_PTR g_timer = 0;

DWORD g_stepMs = 0;                      // learned duration of a straight step, 0 = not yet
DWORD g_lastWalkSend = 0;
bool g_lastWalkDiagonal = false;
bool g_walkFromRepeat = false;           // the client was just given one of our repeats

typedef int (WSAAPI* SendFn)(SOCKET, const char*, int, int);
SendFn g_realSend = nullptr;

bool IsMoveKey(WPARAM vk) {
    switch (vk) {
    case VK_LEFT: case VK_UP: case VK_RIGHT: case VK_DOWN:
    case VK_HOME: case VK_PRIOR: case VK_END: case VK_NEXT:            // numpad diagonals, NumLock off
    case VK_NUMPAD1: case VK_NUMPAD2: case VK_NUMPAD3: case VK_NUMPAD4:
    case VK_NUMPAD6: case VK_NUMPAD7: case VK_NUMPAD8: case VK_NUMPAD9:
        return true;
    }
    return false;
}

int ScanCode(LPARAM lParam) { return (lParam >> 16) & 0x1FF; }   // scan code + extended-key flag

bool IsHeld(WPARAM vk) {
    for (int i = 0; i < g_heldCount; ++i)
        if (g_held[i].vk == vk) return true;
    return false;
}

void Release(WPARAM vk) {
    int out = 0;
    for (int i = 0; i < g_heldCount; ++i)
        if (g_held[i].vk != vk) g_held[out++] = g_held[i];
    g_heldCount = out;
}

void Press(const MSG& msg) {
    Release(msg.wParam);
    if (g_heldCount == ARRAYSIZE(g_held)) Release(g_held[0].vk);
    g_held[g_heldCount++] = { msg.wParam, msg.lParam, msg.hwnd };
    // The client walks on this press itself; its walk packet schedules our first repeat. If it
    // does not walk now (busy), it remembers the press - offer the key again a little later.
    g_nextRepeat = GetTickCount() + kRetryMs;
}

// WM_CHAR that Windows made from one of its own repeats of a held key (numpad digits with NumLock on)
bool IsRepeatOfHeldKey(LPARAM lParam) {
    for (int i = 0; i < g_heldCount; ++i)
        if (ScanCode(g_held[i].lParam) == ScanCode(lParam)) return true;
    return false;
}

// The client just sent a step (0x65-0x68 straight, 0x6A-0x6D diagonal): learn how long steps take,
// and have the next repeat arrive just before this one ends.
void OnWalkSent(unsigned char opcode) {
    DWORD now = GetTickCount();
    bool diagonal = opcode >= 0x6A;
    if (g_walkFromRepeat && g_lastWalkSend && now - g_lastWalkSend < kMaxLearnGapMs) {
        DWORD took = now - g_lastWalkSend;               // the previous step, walked back to back
        g_stepMs = g_lastWalkDiagonal ? took / 2 : took;
    }
    g_walkFromRepeat = false;
    g_lastWalkSend = now;
    g_lastWalkDiagonal = diagonal;

    DWORD step = (g_stepMs ? g_stepMs : kDefaultStepMs) * (diagonal ? 2 : 1);
    g_nextRepeat = now + (step > kLeadMs ? step - kLeadMs : 0);
}

int WSAAPI HookedSend(SOCKET s, const char* buf, int len, int flags) {
    // 7.4 packets are [u16 length][opcode ...], unencrypted
    if (buf && len >= 3) {
        unsigned char opcode = static_cast<unsigned char>(buf[2]);
        if (opcode >= 0x65 && opcode <= 0x6D && opcode != 0x69) OnWalkSent(opcode);
    }
    return g_realSend(s, buf, len, flags);
}

// Point the client's imported send() at HookedSend.
void HookSend() {
    HMODULE ws2 = GetModuleHandleA("ws2_32.dll");
    void* realSend = ws2 ? reinterpret_cast<void*>(GetProcAddress(ws2, "send")) : nullptr;
    if (!realSend) return;
    BYTE* base = reinterpret_cast<BYTE*>(GetModuleHandleA(nullptr));
    auto dos = reinterpret_cast<IMAGE_DOS_HEADER*>(base);
    auto nt = reinterpret_cast<IMAGE_NT_HEADERS*>(base + dos->e_lfanew);
    auto& dir = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT];
    for (auto imp = reinterpret_cast<IMAGE_IMPORT_DESCRIPTOR*>(base + dir.VirtualAddress); imp->Name; ++imp) {
        if (lstrcmpiA(reinterpret_cast<char*>(base + imp->Name), "ws2_32.dll") != 0) continue;
        for (auto slot = reinterpret_cast<void**>(base + imp->FirstThunk); *slot; ++slot) {
            if (*slot != realSend) continue;
            DWORD old;
            if (VirtualProtect(slot, sizeof(void*), PAGE_READWRITE, &old)) {
                g_realSend = reinterpret_cast<SendFn>(realSend);
                *slot = reinterpret_cast<void*>(&HookedSend);
                VirtualProtect(slot, sizeof(void*), old, &old);
            }
            return;
        }
    }
}

void CALLBACK OnTimer(HWND, UINT, UINT_PTR, DWORD now) {
    // Keys released while we were not looking (key-up went to another app) no longer count
    for (int i = g_heldCount - 1; i >= 0; --i)
        if (!(GetAsyncKeyState(static_cast<int>(g_held[i].vk)) & 0x8000)) Release(g_held[i].vk);

    if (g_pending && now - g_pendingSince > kPendingTimeoutMs) g_pending = false;
    if (g_heldCount == 0 || g_pending || static_cast<int>(now - g_nextRepeat) < 0) return;

    const HeldKey& key = g_held[g_heldCount - 1];
    if (GetForegroundWindow() != GetAncestor(key.hwnd, GA_ROOT)) return;
    // Posted, not sent: it goes through the client's own pump (and TranslateMessage) like a real repeat
    LPARAM lParam = (key.lParam & 0x01FF0000) | 1 | kRepeatBit | kSynthetic;
    if (PostMessageA(key.hwnd, WM_KEYDOWN, key.vk, lParam)) {
        g_pending = true;
        g_pendingSince = now;
    }
    g_nextRepeat = now + kRetryMs;   // the walk packet it leads to reschedules; if none comes, again
}

LRESULT CALLBACK OnGetMessage(int code, WPARAM removal, LPARAM lParam) {
    if (code == HC_ACTION && removal == PM_REMOVE) {
        MSG& msg = *reinterpret_cast<MSG*>(lParam);
        if (!g_timer) {                                   // first message: set up on the UI thread
            g_timer = SetTimer(nullptr, 0, 10, OnTimer);
            HookSend();
        }
        switch (msg.message) {
        case WM_KEYDOWN:
            if (!IsMoveKey(msg.wParam)) break;
            if (msg.lParam & kSynthetic) {
                g_pending = false;
                if (IsHeld(msg.wParam)) {
                    msg.lParam &= ~kSynthetic;
                    g_walkFromRepeat = true;
                } else {
                    msg.message = WM_NULL;    // let go while our repeat was on its way: no extra step
                }
            } else if ((msg.lParam & kRepeatBit) && IsHeld(msg.wParam)) {
                msg.message = WM_NULL;        // Windows' own repeat: ours replace it
            } else {
                Press(msg);                   // first press goes through untouched: the step starts now
            }
            break;
        case WM_CHAR:
            if (msg.lParam & kSynthetic) msg.lParam &= ~kSynthetic;
            else if ((msg.lParam & kRepeatBit) && IsRepeatOfHeldKey(msg.lParam)) msg.message = WM_NULL;
            break;
        case WM_KEYUP:
            if (IsMoveKey(msg.wParam)) {
                Release(msg.wParam);
                if (g_heldCount) g_nextRepeat = GetTickCount();   // the key still held takes over at once
            }
            break;
        }
    }
    return CallNextHookEx(g_hook, code, removal, lParam);
}

}  // namespace

// The one import Tibia-mintwall.exe refers to; loading the DLL is all it is for.
extern "C" __declspec(dllexport) void MintwallInit() {}

BOOL APIENTRY DllMain(HMODULE module, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(module);
        // Loaded as a static import, so this is the client's main thread - the one that runs its UI
        g_hook = SetWindowsHookExA(WH_GETMESSAGE, OnGetMessage, nullptr, GetCurrentThreadId());
    }
    return TRUE;
}

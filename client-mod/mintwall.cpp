// mintwall.dll - client-side improvements for Tibia-mintwall.exe (the original 7.4 client).
// tools/patch-client.ps1 adds this DLL to the exe's import table, so Windows loads it at start-up.
//
// Smooth keyboard walking: the 7.4 client walks on WM_KEYDOWN, so after pressing a direction it
// takes one step and then waits for Windows' key-repeat delay (500 ms by default) before walking on.
// We drop Windows' own repeats for the movement keys and send the client our own, starting right
// away. The most recently pressed movement key that is still held decides the direction, so letting
// go of one key while another is held keeps walking that way.
//
// The hook sits on the UI thread's message queue (WH_GETMESSAGE), before MFC and TranslateMessage,
// so it works whichever of the client's windows has the keyboard focus.
#include <windows.h>

namespace {

const DWORD kRepeatMs = 33;              // like Windows' fastest repeat rate; the client paces steps itself
const DWORD kPendingTimeoutMs = 500;     // a posted repeat that never arrived (window gone) is forgotten
const LPARAM kSynthetic = 1 << 25;       // reserved bit of a keystroke's lParam: marks our own repeats
const LPARAM kRepeatBit = 1 << 30;       // "the key was already down"

struct HeldKey { WPARAM vk; LPARAM lParam; HWND hwnd; };
HeldKey g_held[8];                       // movement keys held down, most recent last
int g_heldCount = 0;
bool g_pending = false;                  // one repeat posted and not yet picked up
DWORD g_pendingSince = 0;
DWORD g_nextRepeat = 0;
HHOOK g_hook = nullptr;
UINT_PTR g_timer = 0;

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
    g_nextRepeat = GetTickCount() + kRepeatMs;
}

// WM_CHAR that Windows made from one of its own repeats of a held key (numpad digits with NumLock on)
bool IsRepeatOfHeldKey(LPARAM lParam) {
    for (int i = 0; i < g_heldCount; ++i)
        if (ScanCode(g_held[i].lParam) == ScanCode(lParam)) return true;
    return false;
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
    g_nextRepeat = now + kRepeatMs;
}

LRESULT CALLBACK OnGetMessage(int code, WPARAM removal, LPARAM lParam) {
    if (code == HC_ACTION && removal == PM_REMOVE) {
        MSG& msg = *reinterpret_cast<MSG*>(lParam);
        if (!g_timer) g_timer = SetTimer(nullptr, 0, 10, OnTimer);   // on the UI thread, like the hook
        switch (msg.message) {
        case WM_KEYDOWN:
            if (!IsMoveKey(msg.wParam)) break;
            if (msg.lParam & kSynthetic) {
                msg.lParam &= ~kSynthetic;
                g_pending = false;
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

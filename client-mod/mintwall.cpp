// mintwall.dll - client-side improvements for Tibia-mintwall.exe (the original 7.4 client).
// tools/patch-client.ps1 adds this DLL to the exe's import table, so Windows loads it at start-up.
//
// Smooth keyboard walking: Windows' key repeats of the movement keys are dropped and the client
// gets exactly one repeat per step, shortly before the step ends - so holding a key walks without
// the 500 ms pause, a tap walks one square and letting go stops at once. When to repeat is
// walk_pacer.h (with the reasons); this file is the Win32 side. Step times are learned from the
// client's own walk packets (its send() is hooked; the 7.4 protocol is not encrypted).
//
// The keyboard hook sits on the UI thread's message queue (WH_GETMESSAGE), before MFC and
// TranslateMessage, so it works whichever of the client's windows has the keyboard focus. The
// client sends from that same thread (WSAAsyncSelect), so no locking is needed.
#include <winsock2.h>
#include <windows.h>
#include <cstdio>
#include "walk_pacer.h"

namespace {

const LPARAM kSynthetic = 1 << 25;       // reserved bit of a keystroke's lParam: marks our own repeats
const LPARAM kRepeatBit = 1 << 30;       // "the key was already down"

mintwall::WalkPacer g_pacer;
struct KeyPress { LPARAM lParam; HWND hwnd; };
KeyPress g_press[256];                   // last real key-down of each movement key: our repeats copy it
HHOOK g_hook = nullptr;
UINT_PTR g_timer = 0;

typedef int (WSAAPI* SendFn)(SOCKET, const char*, int, int);
SendFn g_realSend = nullptr;

// A millisecond clock finer than GetTickCount's 15.6 ms (the pacer tells a step sent at once from
// one sent ~60 ms later)
mintwall::Ms NowMs() {
    static LARGE_INTEGER freq = {};
    if (!freq.QuadPart) QueryPerformanceFrequency(&freq);
    LARGE_INTEGER now;
    QueryPerformanceCounter(&now);
    return static_cast<mintwall::Ms>(now.QuadPart * 1000 / freq.QuadPart);
}

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

// Set MINTWALL_WALK_LOG=<file> before starting the client to log every movement key and step
// ("<ms> <event> <key or opcode>"): what a key press, a repeat and a let-go led to, on one clock.
FILE* g_log = nullptr;

void Log(const char* event, unsigned value) {
    if (!g_log) return;
    std::fprintf(g_log, "%u %s 0x%02X\n", NowMs(), event, value);
    std::fflush(g_log);
}

void OpenLog() {
    char path[MAX_PATH];
    DWORD n = GetEnvironmentVariableA("MINTWALL_WALK_LOG", path, MAX_PATH);
    if (n && n < MAX_PATH && fopen_s(&g_log, path, "a") != 0) g_log = nullptr;
}

int ScanCode(LPARAM lParam) { return (lParam >> 16) & 0x1FF; }   // scan code + extended-key flag

// WM_CHAR that Windows made from one of its own repeats of a held key (numpad digits with NumLock on)
bool IsRepeatOfHeldKey(LPARAM lParam) {
    for (int i = 0; i < g_pacer.HeldCount(); ++i)
        if (ScanCode(g_press[g_pacer.Held(i)].lParam) == ScanCode(lParam)) return true;
    return false;
}

int WSAAPI HookedSend(SOCKET s, const char* buf, int len, int flags) {
    // 7.4 packets are [u16 length][opcode ...], unencrypted
    if (buf && len >= 3) {
        unsigned char opcode = static_cast<unsigned char>(buf[2]);
        // steps: 0x65-0x68 straight, 0x6A-0x6D diagonal
        if (opcode >= 0x65 && opcode <= 0x6D && opcode != 0x69) {
            Log("step", opcode);
            g_pacer.OnWalkSent(opcode >= 0x6A, NowMs());
        }
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

void CALLBACK OnTimer(HWND, UINT, UINT_PTR, DWORD) {
    // Keys released while we were not looking (key-up went to another app) no longer count
    for (int i = g_pacer.HeldCount() - 1; i >= 0; --i)
        if (!(GetAsyncKeyState(g_pacer.Held(i)) & 0x8000)) g_pacer.Forget(g_pacer.Held(i));

    mintwall::Ms now = NowMs();
    int vk = g_pacer.Due(now);
    if (!vk) return;
    const KeyPress& key = g_press[vk];
    if (GetForegroundWindow() != GetAncestor(key.hwnd, GA_ROOT)) return;
    // Posted, not sent: it goes through the client's own pump (and TranslateMessage) like a real repeat
    LPARAM lParam = (key.lParam & 0x01FF0000) | 1 | kRepeatBit | kSynthetic;
    if (PostMessageA(key.hwnd, WM_KEYDOWN, vk, lParam)) {
        Log("post", vk);
        g_pacer.Posted(now);
    }
}

LRESULT CALLBACK OnGetMessage(int code, WPARAM removal, LPARAM lParam) {
    if (code == HC_ACTION && removal == PM_REMOVE) {
        MSG& msg = *reinterpret_cast<MSG*>(lParam);
        if (!g_timer) {                                   // first message: set up on the UI thread
            g_timer = SetTimer(nullptr, 0, 10, OnTimer);
            HookSend();
            OpenLog();
        }
        switch (msg.message) {
        case WM_KEYDOWN:
            if (!IsMoveKey(msg.wParam)) break;
            if (msg.lParam & kSynthetic) {
                msg.lParam &= ~kSynthetic;
                if (g_pacer.OnRepeatArrived(static_cast<int>(msg.wParam), NowMs())) {
                    Log("repeat", static_cast<unsigned>(msg.wParam));
                } else {
                    Log("repeat-dropped", static_cast<unsigned>(msg.wParam));
                    msg.message = WM_NULL;    // let go while our repeat was on its way: no extra step
                }
            } else {
                bool alreadyDown = (msg.lParam & kRepeatBit) != 0;
                if (g_pacer.OnKeyDown(static_cast<int>(msg.wParam), alreadyDown, NowMs())) {
                    Log("down", static_cast<unsigned>(msg.wParam));
                    g_press[msg.wParam] = { msg.lParam, msg.hwnd };   // a press: goes through untouched
                } else {
                    msg.message = WM_NULL;    // Windows' own repeat: ours replace it
                }
            }
            break;
        case WM_CHAR:
            if (msg.lParam & kSynthetic) msg.lParam &= ~kSynthetic;
            else if ((msg.lParam & kRepeatBit) && IsRepeatOfHeldKey(msg.lParam)) msg.message = WM_NULL;
            break;
        case WM_KEYUP:
            if (IsMoveKey(msg.wParam)) {
                Log("up", static_cast<unsigned>(msg.wParam));
                g_pacer.OnKeyUp(static_cast<int>(msg.wParam), NowMs());
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

"""tools/patch-client.ps1 on a COPY of the original 7.4 Tibia.exe: login IP, mintwall.dll import and the
www.tibia.com -> www.mintwalling.com text table (decision of 2026-10-05). The client is proprietary and not
in the repo (README: unpack Tibia740.zip to client/Tibia740/); without it these tests skip."""
import shutil
import struct
import subprocess

import pytest

from tibia74.server import ROOT

ORIGINAL = ROOT / "client" / "Tibia740" / "Tibia.exe"
SCRIPT = ROOT / "tools" / "patch-client.ps1"
ORIGINAL_SIZE = 647168
IP = "192.168.100.200"    # 15 characters: longer than any default, still fits the 16-byte host slots
SITE = b"http://www.mintwalling.com"

pytestmark = pytest.mark.skipif(
    not ORIGINAL.is_file(),
    reason=f"original 7.4 client not present at {ORIGINAL} (proprietary, not in the repo - see README)")

# offset -> (original text, patched text); the patched exe must hold exactly this followed by NUL
TEXTS = {
    0x7B588: (b"http://www.tibia.com/home/?subtopic=signup", SITE),
    0x7B5B4: (b"http://www.tibia.com/home/?subtopic=account", SITE),
    0x7B5E0: (b"http://www.tibia.com/guide/?subtopic=manual&section=options#networkoptions", SITE),
    0x7B62C: (b"http://www.tibia.com/guide/?subtopic=manual-options#console", SITE),
    0x7B668: (b"http://www.tibia.com/guide/?subtopic=manual-options#graphics", SITE),
    0x7B6A8: (b"http://www.tibia.com/guide/?subtopic=manual-options#general", SITE),
    0x7B6E4: (b"http://www.tibia.com/guide/?subtopic=faq", SITE),
    0x7B710: (b"http://www.tibia.com/guide/?subtopic=manual", SITE),
    0x7B73C: (b"http://www.tibia.com/", b"http://mintwalling.com/"),
    0x81204: (b"www.tibia.com", b"mintwalling.com"),
    0x88A1A: (b"on our offical website www.tibia.com.", b"on our website www.mintwalling.com."),
    0x8940C: (b"\nguide section at www.tibia.com.", b"\nguide at www.mintwalling.com."),
    0x89468: (b"\n\nThe game server is offline. Check www.tibia.com",
              b"\n\nGame server offline. Check www.mintwalling.com"),
    0x894E0: (b"\n\nAll login server are offline. Check www.tibia.com",
              b"\n\nLogin servers offline. Check www.mintwalling.com"),
    0x895BC: (b"\n\nCheck www.tibia.com for more information on ", b"\n\nSee www.mintwalling.com for information on "),
    0x89618: (b"\n\nThe test server is offline. Check www.tibia.com",
              b"\n\nTest server offline. Check www.mintwalling.com"),
    0x8A91C: (b"Please submit a detailed bugreport to cip@tibia.com.",
              b"Please submit a bug report at www.mintwalling.com."),
}
# Copied by the client with a fixed-length inline strcat sized for the original: may never grow
FIXED_COPY = {0x8940C, 0x89468, 0x894E0, 0x895BC, 0x89618}
# offset -> (original VA, patched VA)
ROOT_URL_POINTERS = [0x95308, 0x95520, 0x95744, 0x95968, 0x95B8C, 0x95DD4, 0x95FEC, 0x96210,
                     0x96434, 0x96674, 0x968B8, 0x96AF0, 0x96D14, 0x96F38, 0x972E0]
POINTERS = {0x2C690: (0x481204, 0x47B58F), **{o: (0x47B73C, 0x47B588) for o in ROOT_URL_POINTERS}}
HOSTS = {0x893AC: b"tibia2.cipsoft.com", 0x893C0: b"tibia1.cipsoft.com",
         0x893D4: b"server.tibia.com", 0x893E8: b"server2.tibia.com"}
COPYRIGHT = [b"Tibia Client\nVersion 7.4 \nCopyright (C) 2002-2004\nCipSoft GmbH\nAll rights reserved.\0",
             b"Copyright by\nCipSoft GmbH\nVersion 7\0"]


def va_string(data, va):
    o = va - 0x400000    # .rdata: file offset == RVA
    return data[o:data.index(b"\0", o)]


def run_patch(client_dir, *extra):
    dll = client_dir / "dummy-mintwall.dll"
    dll.write_bytes(b"MZ")
    return subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
         "-Ip", IP, "-ClientDir", str(client_dir), "-ModDll", str(dll), *extra],
        capture_output=True, text=True, timeout=120)


@pytest.fixture(scope="module")
def patched(tmp_path_factory):
    work = tmp_path_factory.mktemp("client")
    shutil.copyfile(ORIGINAL, work / "Tibia.exe")
    r = run_patch(work)
    assert r.returncode == 0, r.stdout + r.stderr
    original = ORIGINAL.read_bytes()
    assert (work / "Tibia.exe").read_bytes() == original, "the script modified its input exe"
    return original, (work / "Tibia-mintwall.exe").read_bytes()


def test_original_is_the_known_7_4_exe(patched):
    original, _ = patched
    assert len(original) == ORIGINAL_SIZE
    for o, (old, _) in TEXTS.items():
        assert original[o:o + len(old) + 1] == old + b"\0", hex(o)


def test_every_text_entry_applied(patched):
    _, out = patched
    for o, (old, new) in TEXTS.items():
        n = max(len(old), len(new)) + 1
        assert out[o:o + n] == new.ljust(n, b"\0"), hex(o)
        if o in FIXED_COPY:
            assert len(new) <= len(old), f"0x{o:X} is copied with a fixed length and may not grow"


def test_every_pointer_entry_applied(patched):
    original, out = patched
    for o, (old, new) in POINTERS.items():
        assert struct.unpack_from("<I", original, o)[0] == old, hex(o)
        assert struct.unpack_from("<I", out, o)[0] == new, hex(o)
    assert out[0x2C68F] == 0x68    # push imm32
    assert va_string(out, 0x47B58F) == b"www.mintwalling.com"
    assert va_string(out, 0x47B588) == SITE


def test_size_unchanged_apart_from_the_import_section(patched):
    original, out = patched
    # the text table is in place; the only growth is the one 4 KB ".mintw" import section appended
    assert len(out) == len(original) + 0x1000
    pe = struct.unpack_from("<I", out, 0x3C)[0]
    sections = struct.unpack_from("<H", out, pe + 6)[0]
    last = pe + 24 + struct.unpack_from("<H", out, pe + 20)[0] + (sections - 1) * 40
    assert out[last:last + 6] == b".mintw"
    assert struct.unpack_from("<I", out, last + 20)[0] == len(original)


def test_only_the_intended_bytes_changed(patched):
    original, out = patched
    allowed = [(0, 0x1000)]    # PE headers: section count, new section header, SizeOfImage, import dir
    for o, (old, new) in TEXTS.items():
        allowed.append((o, o + max(len(old), len(new)) + 1))
    allowed += [(o, o + 4) for o in POINTERS]
    allowed += [(o, o + len(h)) for o, h in HOSTS.items()]
    changed = [i for i in range(len(original)) if original[i] != out[i]]
    stray = [hex(i) for i in changed if not any(a <= i < b for a, b in allowed)]
    assert not stray, stray[:20]


def test_no_tibia_com_left(patched):
    _, out = patched
    assert b"tibia.com" not in out.lower()
    assert out.count(b"mintwalling.com") == len(TEXTS)


def test_copyright_unchanged(patched):
    original, out = patched
    for c in COPYRIGHT:
        o = original.index(c)
        assert out[o:o + len(c)] == c
    assert out.count(b"CipSoft GmbH") == original.count(b"CipSoft GmbH")


def test_ip_patch_still_works(patched):
    _, out = patched
    for o, h in HOSTS.items():
        assert out[o:o + len(h) + 1] == IP.encode().ljust(len(h) + 1, b"\0"), hex(o)
    assert b"mintwall.dll\0" in out[-0x1000:] and b"MintwallInit\0" in out[-0x1000:]


def test_refuses_a_different_exe(tmp_path):
    exe = bytearray(ORIGINAL.read_bytes())
    exe[0x8946A] ^= 0x20    # "The game server..." -> "the game server..."
    (tmp_path / "Tibia.exe").write_bytes(exe)
    r = run_patch(tmp_path)
    assert r.returncode != 0
    assert "0x89468" in r.stdout + r.stderr
    assert not (tmp_path / "Tibia-mintwall.exe").exists()

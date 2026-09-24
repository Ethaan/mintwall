"""Static checks over the server's Lua scripts (server/data/**/*.lua).

Calls to functions nothing defines fail only when the line runs (a Lua error in the log, and the action
silently does nothing): rope, shovel, pick, keys and the machete all called an undefined isIntegerInArray.
"""
import re
from collections import defaultdict
from pathlib import Path

KEYWORDS = set("and break do else elseif end false for function if in local nil not or repeat return then "
               "true until while".split())
BUILTINS = set("assert collectgarbage dofile error getmetatable ipairs load loadfile loadstring next pairs "
               "pcall print rawequal rawget rawset require select setmetatable tonumber tostring type unpack "
               "xpcall module setfenv getfenv".split())


def _strip(text: str) -> str:
    """Lua source without comments and string contents (names inside them are not calls)."""
    text = re.sub(r"--\[(=*)\[.*?\]\1\]", "", text, flags=re.S)
    text = re.sub(r"\[(=*)\[.*?\]\1\]", '""', text, flags=re.S)
    text = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', text)
    text = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", text)
    return re.sub(r"--[^\n]*", "", text)


def engine_functions(server_dir: Path) -> set:
    src = "\n".join(f.read_text(encoding="latin-1") for f in (server_dir / "src").glob("*.cpp"))   # npc.cpp too
    names = set(re.findall(r'lua_register\(\s*m_luaState\s*,\s*"(\w+)"', src))
    names |= set(re.findall(r'\{\s*"(\w+)"\s*,\s*LuaScriptInterface::', src))    # library tables (bit.*)
    return names


def undefined_calls(server_dir: Path) -> dict:
    """{function name: [script, ...]} for every call to a global function nothing defines."""
    scripts = {f: _strip(f.read_text(encoding="latin-1")) for f in (server_dir / "data").rglob("*.lua")}
    known = KEYWORDS | BUILTINS | engine_functions(server_dir)
    for text in scripts.values():
        known |= set(re.findall(r"^\s*function\s+([A-Za-z_]\w*)\s*\(", text, re.M))
        known |= set(re.findall(r"^\s*([A-Za-z_]\w*)\s*=", text, re.M))       # globals and aliases
    missing = defaultdict(list)
    for path, text in scripts.items():
        local = set(re.findall(r"\blocal\s+function\s+([A-Za-z_]\w*)", text))
        local |= set(re.findall(r"\blocal\s+([A-Za-z_]\w*)", text))
        for params in re.findall(r"\bfunction\b[^(]*\(([^)]*)\)", text):
            local |= {p.strip() for p in params.split(",") if p.strip()}
        for name in sorted(set(re.findall(r"(?<![\w.:])([A-Za-z_]\w*)\s*\(", text))):
            if name not in known and name not in local:
                missing[name].append(str(path.relative_to(server_dir)))
    return dict(missing)

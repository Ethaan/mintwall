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
    """Lua source without comments and string contents (names inside them are not calls), on the same lines."""
    lines = lambda m: "\n" * m.group(0).count("\n")
    text = re.sub(r"--\[(=*)\[.*?\]\1\]", lines, text, flags=re.S)
    text = re.sub(r"\[(=*)\[.*?\]\1\]", lambda m: '""' + lines(m), text, flags=re.S)
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


def boolean_functions(server_dir: Path) -> set:
    """Functions that return only true/false: engine functions whose C++ pushes nothing but lua_pushboolean
    (unless a script redefines them), and top-level Lua functions whose every return is true, false, a `not`
    or a comparison - with no and/or, since `return x > 0 and x or 0` is a number."""
    src = "\n".join(f.read_text(encoding="latin-1") for f in (server_dir / "src").glob("*.cpp"))
    registered = dict(re.findall(r'lua_register\(\s*m_luaState\s*,\s*"(\w+)"\s*,\s*\w+::(\w+)\)', src))
    bodies = dict(re.findall(r"^int \w+::(\w+)\(lua_State\s*\*\s*L\)\s*\n\{(.*?)\n\}", src, re.M | re.S))
    pushes = lambda body: set(re.findall(r"\b(lua_push\w+|lua_newtable|push[A-Z]\w*|setField\w*)\b", body))
    names = {name for name, impl in registered.items() if impl in bodies and pushes(bodies[impl]) == {"lua_pushboolean"}}

    scripts = [_strip(f.read_text(encoding="latin-1")) for f in (server_dir / "data").rglob("*.lua")]
    boolean = r"\s*(true|false|(?!.*\b(and|or)\b)(not\b.*|.*([=~<>]=|[<>]).*))\s*"
    verdict = {}
    for text in scripts:
        names -= set(re.findall(r"^\s*function\s+([A-Za-z_]\w*)\s*\(", text, re.M))
        names -= set(re.findall(r"^\s*([A-Za-z_]\w*)\s*=", text, re.M))
        for name, body in re.findall(r"^function\s+([A-Za-z_]\w*)\s*\([^)]*\)(.*?)^end\b", text, re.M | re.S):
            returns = re.findall(r"\breturn\b([^\n;]*)", body)
            ok = bool(returns) and "function" not in body and all(re.fullmatch(boolean, r) for r in returns)
            verdict[name] = verdict.get(name, True) and ok           # every definition of the name
    return names | {name for name, ok in verdict.items() if ok and not name.startswith("on")}   # not callbacks


def boolean_compared_with_number(server_dir: Path) -> list:
    """`isPlayer(cid) == 1`, `isInArray(t, v) ~= 0`...: true is not 1, so the test never holds (or always does)."""
    call = r"\b(?:%s)\s*\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\)\s*[=~]=\s*[01]\b" % "|".join(
        sorted(boolean_functions(server_dir)))
    bad = []
    for path in (server_dir / "data").rglob("*.lua"):
        for n, line in enumerate(_strip(path.read_text(encoding="latin-1")).splitlines(), 1):
            if re.search(call, line):
                bad.append(f"{path.relative_to(server_dir)}:{n}: {line.strip()}")
    return bad

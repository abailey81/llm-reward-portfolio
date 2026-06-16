"""Sandboxed execution of UNTRUSTED LLM-generated reward code (CLAUDE.md R6).

Hardened per the week plan (sandbox-hardening block; ADR-008). Defence layers, outermost
first — the threat model is misbehaving generated code (resource bombs, stray I/O,
namespace escapes), not a determined human adversary:

  1. STATIC GATE (`static_check`, AST-based): only `numpy` imports; no dunder names or
     attributes; no exec/eval/open/getattr-style escape hatches; no classes, decorators,
     async, yield, global/nonlocal; numpy's file/FFI surface (np.load, np.save,
     np.fromfile, np.lib, DataSource, ctypeslib, ...) rejected by attribute name;
     `compute_reward` must be defined. Runs BEFORE any subprocess is spawned.
  2. PROCESS ISOLATION: `python -I` (isolated mode) in a fresh temp cwd with a MINIMAL
     environment (no inherited secrets such as LLM_API_KEY; BLAS thread pools pinned to
     1 so RLIMIT_NPROC cannot break numpy).
  3. RESOURCE LIMITS (best-effort per-resource, each clamped to the current hard limit
     and skipped if the platform refuses — macOS rejects some combos; the Linux/4090
     experiment box enforces all): address space, CPU seconds, open files, file size,
     process count. Wall-clock timeout (SIGKILL) is the platform-independent backstop.
  4. NAMESPACE: candidate runs under a whitelisted-builtins dict with `__import__`
     disabled; only `np`/`numpy` are provided.
  5. CONTRACT VALIDATION (`validate_sandbox_results`, parent-side): rewards/components
     finite and bounded per `config eureka_loop.contract`; component keys non-empty and
     STABLE across calls (the system prompt's requirement #3).

Never exec() candidate code in the main process. Every candidate, valid or not, is
archived verbatim with prompt/snapshot/outcome via `src/candidate_archive.py`.
"""
from __future__ import annotations

import ast
import json
import math
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import get
from .reward_contract import RewardContext, probe_contexts

MAX_SOURCE_BYTES = 50_000

#: names whose mere appearance is rejected — escape hatches and introspection tools.
#: (They would NameError at runtime under the whitelisted builtins anyway; the static
#: gate makes the failure immediate, free, and loggable.)
_BANNED_NAMES = frozenset({
    "exec", "eval", "compile", "open", "input", "breakpoint", "help",
    "globals", "locals", "vars", "dir", "getattr", "setattr", "delattr", "hasattr",
    "type", "object", "super", "memoryview", "bytearray", "bytes",
    "staticmethod", "classmethod", "property", "id", "hash", "repr", "format",
})

#: attribute names rejected anywhere — numpy's file/FFI/loader surface plus generic
#: object-model escape routes. Candidates need none of these for reward arithmetic.
_BANNED_ATTRS = frozenset({
    "load", "loads", "save", "savez", "savez_compressed", "savetxt", "loadtxt",
    "genfromtxt", "fromfile", "tofile", "memmap", "DataSource", "frombuffer",
    "lib", "ctypeslib", "f2py", "testing", "open", "mro",
})

_BANNED_NODES: tuple[type, ...] = (
    ast.ClassDef, ast.AsyncFunctionDef, ast.Await, ast.AsyncFor, ast.AsyncWith,
    ast.Yield, ast.YieldFrom, ast.Global, ast.Nonlocal,
)


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def static_check(code: str) -> str | None:
    """Return a rejection reason, or None if the candidate passes the static gate."""
    if len(code.encode()) > MAX_SOURCE_BYTES:
        return f"candidate too large (> {MAX_SOURCE_BYTES} bytes)"
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"syntax error: {e.msg} (line {e.lineno})"
    has_compute_reward = any(
        isinstance(n, ast.FunctionDef) and n.name == "compute_reward" for n in tree.body
    )
    if not has_compute_reward:
        return "no top-level compute_reward defined"
    for node in ast.walk(tree):
        if isinstance(node, _BANNED_NODES):
            return f"forbidden construct: {type(node).__name__}"
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] != "numpy":
                    return f"static check: only numpy imports permitted (saw '{alias.name}')"
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if node.level != 0 or root != "numpy":
                return f"static check: only numpy imports permitted (saw 'from {node.module}')"
        elif isinstance(node, ast.FunctionDef) and node.decorator_list:
            return "forbidden construct: decorator"
        elif isinstance(node, ast.Name):
            if node.id in _BANNED_NAMES:
                return f"forbidden name: {node.id}"
            if _is_dunder(node.id):
                return f"forbidden dunder name: {node.id}"
        elif isinstance(node, ast.Attribute):
            if node.attr in _BANNED_ATTRS:
                return f"forbidden attribute: .{node.attr}"
            if _is_dunder(node.attr):
                return f"forbidden dunder attribute: .{node.attr}"
    return None


# Runner template. Limits arrive via argv (no str.format brace-escaping); candidate
# source is embedded via repr(). Whitelisted builtins; __import__ disabled.
_RUNNER = r'''
import json, sys
import numpy as np

def _limit(mem_mb, cpu_s, fsize_mb, nproc):
    try:
        import resource
    except ImportError:          # non-POSIX: wall-clock timeout remains the backstop
        return
    def _set(name, soft):
        res = getattr(resource, name, None)
        if res is None:
            return
        try:
            _, hard = resource.getrlimit(res)
            tgt = soft if hard == resource.RLIM_INFINITY else min(soft, hard)
            resource.setrlimit(res, (tgt, tgt))
        except (ValueError, OSError):
            pass                 # best-effort per-resource (Darwin rejects some combos)
    _set("RLIMIT_AS", mem_mb * 1024 * 1024)
    _set("RLIMIT_CPU", cpu_s)
    _set("RLIMIT_NOFILE", 8)
    _set("RLIMIT_FSIZE", fsize_mb * 1024 * 1024)
    _set("RLIMIT_NPROC", nproc)

_limit(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))

def _numpy_only_import(name, *args, **kwargs):
    # The static gate already rejects non-numpy imports; this is the runtime
    # belt-and-braces so `import numpy as np` (which the system prompt mandates)
    # works while everything else fails loudly.
    if name == "numpy" or name.startswith("numpy."):
        return __import__(name, *args, **kwargs)
    raise ImportError("sandbox: only numpy may be imported")

_SAFE_BUILTINS = {
    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
    "enumerate": enumerate, "filter": filter, "float": float, "int": int,
    "isinstance": isinstance, "len": len, "list": list, "map": map, "max": max,
    "min": min, "pow": pow, "range": range, "round": round, "sorted": sorted,
    "str": str, "sum": sum, "tuple": tuple, "zip": zip,
    "ValueError": ValueError, "ZeroDivisionError": ZeroDivisionError,
    "FloatingPointError": FloatingPointError, "Exception": Exception,
    "__import__": _numpy_only_import,
}
ns = {"np": np, "numpy": np, "__builtins__": _SAFE_BUILTINS}
try:
    exec(CANDIDATE_SOURCE, ns)
except Exception as e:
    print(json.dumps({"ok": False, "error": "definition error: %s: %s" % (type(e).__name__, e)}))
    sys.exit(0)
fn = ns.get("compute_reward")
if fn is None:
    print(json.dumps({"ok": False, "error": "no compute_reward defined"}))
    sys.exit(0)

class Ctx:  # rebuild ctx from JSON payload
    pass

results = []
for payload in json.loads(sys.stdin.read()):
    ctx = Ctx()
    for k, v in payload.items():
        setattr(ctx, k, np.array(v) if isinstance(v, list) else v)
    try:
        r, comps = fn(ctx)
        results.append({"ok": True, "reward": float(r),
                        "components": {str(k): float(v) for k, v in comps.items()}})
    except Exception as e:
        results.append({"ok": False, "error": "%s: %s" % (type(e).__name__, e)})
print(json.dumps(results))
'''


@dataclass
class SandboxResult:
    ok: bool
    results: list | None
    error: str | None
    raw_stderr: str


def payload_from_context(ctx: RewardContext) -> dict:
    """Serialize a RewardContext to the JSON payload the runner rebuilds."""
    out = {}
    for k, v in asdict(ctx).items():
        out[k] = v.tolist() if hasattr(v, "tolist") else v
    return out


def probe_payloads(n_assets: int = 5, t_lookback: int = 60,
                   n_probe: int = 32, seed: int = 0) -> list[dict]:
    """The serialized probe battery — same contexts as `validate_reward_callable`."""
    return [payload_from_context(c) for c in probe_contexts(n_assets, t_lookback, n_probe, seed)]


def run_candidate(code: str, ctx_payloads: list[dict], timeout_s: int = 20,
                  mem_mb: int = 1024, cpu_s: int = 15, fsize_mb: int = 1,
                  nproc: int = 1) -> SandboxResult:
    """Execute candidate `code` against serialized ctx payloads in an isolated process.

    `ok=True` means the RUNNER completed and returned parseable per-payload results;
    individual payloads may still have failed (`results[i]["ok"]`). Apply
    `validate_sandbox_results` before accepting a candidate for training.
    """
    code = textwrap.dedent(code)
    reason = static_check(code)
    if reason is not None:
        return SandboxResult(False, None, reason, "")
    with tempfile.TemporaryDirectory() as td:
        rpath = Path(td) / "runner.py"
        rpath.write_text("CANDIDATE_SOURCE = " + repr(code) + "\n" + _RUNNER)
        clean_env = {
            "TMPDIR": td,
            "OPENBLAS_NUM_THREADS": "1", "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
            "PYTHONHASHSEED": "0",
        }
        try:
            proc = subprocess.run(
                [sys.executable, "-I", str(rpath),
                 str(mem_mb), str(cpu_s), str(fsize_mb), str(nproc)],
                input=json.dumps(ctx_payloads),
                capture_output=True, text=True, timeout=timeout_s, cwd=td,
                env=clean_env, start_new_session=True,
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(False, None, "timeout", "")
    if proc.returncode != 0:
        return SandboxResult(False, None, f"runner exit {proc.returncode}", proc.stderr[-2000:])
    try:
        parsed = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return SandboxResult(False, None, "unparseable runner output", proc.stderr[-2000:])
    if isinstance(parsed, dict):                       # runner-level early error
        return SandboxResult(False, None, parsed.get("error", "runner error"), proc.stderr[-2000:])
    return SandboxResult(True, parsed, None, proc.stderr[-2000:])


def validate_sandbox_results(results: list, max_abs: float | None = None) -> tuple[bool, str]:
    """Parent-side contract gate over runner results: every payload ok; rewards and
    components finite and |.| < max_abs; component keysets non-empty and IDENTICAL
    across calls (component-name stability — system prompt requirement #3)."""
    max_abs = float(max_abs if max_abs is not None else get("eureka_loop.contract.max_abs_reward"))
    if not results:
        return False, "no results"
    keyset: frozenset | None = None
    for i, res in enumerate(results):
        if not res.get("ok"):
            return False, f"payload {i}: {res.get('error', 'failed')}"
        r = res.get("reward")
        if not isinstance(r, (int, float)) or not math.isfinite(r) or abs(r) >= max_abs:
            return False, f"payload {i}: reward not finite/bounded: {r}"
        comps = res.get("components")
        if not isinstance(comps, dict) or not comps:
            return False, f"payload {i}: components must be a non-empty dict"
        for k, v in comps.items():
            if not isinstance(v, (int, float)) or not math.isfinite(v) or abs(v) >= max_abs:
                return False, f"payload {i}: component '{k}' not finite/bounded: {v}"
        ks = frozenset(comps)
        if keyset is None:
            keyset = ks
        elif ks != keyset:
            return False, f"payload {i}: component names not stable across calls"
    return True, "ok"

"""Two-stage sandbox for untrusted LLM reward code (F.5, audit A-5).

LLM-authored reward code is untrusted. Per audit A-5 it is executed in two stages:

  1. VALIDATE ONCE per candidate (`validate_once`): AST-gate the source, then exec
     it once in a restricted namespace `{"np": numpy}` on a small fixture under a
     timeout. Reject crashers, timeouts, and contract violators here. This is the
     only stage that can be slow / use a timeout.
  2. DURING TRAINING (`safe_call`): the already-compiled function runs IN-PROCESS
     (fast) wrapped in a cheap per-call try/except. On NaN / inf / exception it
     substitutes SAFE_DEFAULT and flags the candidate. NO subprocess, NO per-step
     timeout (that would dominate the training cost).

The AST gate (`ast_gate`) rejects:
  - imports outside the allowlist (ALLOWED_IMPORTS = numpy only);
  - dunder attribute access (`x.__class__`, etc.);
  - calls to open / exec / eval / __import__.

Anonymized arrays only — no tickers, no dates — ever reach a reward (enforced by
the contract and exercised by the tests).

Audit refs: A-5 (gate-once then in-process), B-4 (state round-tripped via info).

Tests (test_sandbox.py):
  - os-import / file-read / date-reference source is rejected at the gate.
  - an infinite loop is killed at validate_once (timeout).
  - an in-process error is caught, SAFE_DEFAULT substituted, candidate flagged, and
    the training loop continues.
  - a reward never receives tickers or dates (anonymized arrays only).
"""

from __future__ import annotations

import ast
import builtins
import math
import signal
import sys
from typing import Any

import numpy as np

from src.reward.contract import ALLOWED_IMPORTS, RewardFn, SAFE_DEFAULT

# Names that may never be called from untrusted reward source.
_FORBIDDEN_CALLS: frozenset[str] = frozenset(
    {"open", "exec", "eval", "__import__", "compile", "getattr", "setattr", "input"}
)

def _safe_import(
    name: str,
    globals: dict[str, Any] | None = None,  # noqa: A002 - matches builtins.__import__ signature
    locals: dict[str, Any] | None = None,  # noqa: A002
    fromlist: tuple[str, ...] = (),
    level: int = 0,
) -> Any:
    """A restricted ``__import__`` for the reward sandbox.

    NumPy lazily imports its own submodules (e.g. on the first ``ndarray.mean()`` /
    ``ndarray.var()`` call), and those imports resolve ``__builtins__['__import__']``
    from the *calling frame* — i.e. this sandbox namespace. Omitting ``__import__``
    therefore makes legitimate numpy reward code crash with ``KeyError('__import__')``
    both at validation and (worse) silently during training via ``safe_call``.

    The untrusted reward source itself can never reach this function: the AST gate
    rejects ``import`` statements, references to the ``__import__`` name (a dunder),
    and calls to ``__import__``. So the only callers are trusted numpy/Python
    internals. As defence-in-depth we still permit only numpy-rooted modules and
    modules already loaded at process start (numpy's transitive deps), denying any
    brand-new non-numpy import.
    """
    root = name.split(".")[0]
    if root == "numpy" or name in sys.modules:
        return builtins.__import__(name, globals, locals, fromlist, level)
    raise ImportError(f"import of {name!r} is not permitted in the reward sandbox")


# Builtins handed to exec'd reward source. Excludes open/exec/eval/compile/getattr/
# setattr/input and every IO primitive (the AST gate also statically rejects them).
# ``__import__`` is the *restricted* ``_safe_import`` above — required so numpy's lazy
# submodule loads work for legitimate reward code (e.g. ``returns.mean()``).
SAFE_BUILTINS: dict[str, Any] = {
    "__import__": _safe_import,
    "abs": abs,
    "min": min,
    "max": max,
    "sum": sum,
    "len": len,
    "range": range,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    "all": all,
    "any": any,
    "sorted": sorted,
    "reversed": reversed,
    "float": float,
    "int": int,
    "bool": bool,
    "str": str,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "set": set,
    "round": round,
    "pow": pow,
    "divmod": divmod,
    "slice": slice,
    "isinstance": isinstance,
    "True": True,
    "False": False,
    "None": None,
}

# Module-level flag mechanism: set True when safe_call substitutes SAFE_DEFAULT so
# the orchestrating loop can mark the current candidate as failed and move on.
_LAST_CALL_FAILED: bool = False


class SandboxError(Exception):
    """Raised by validate_once when a candidate reward is rejected."""


class _Timeout(Exception):
    """Internal: raised by the SIGALRM handler to abort a runaway reward."""


def _alarm_handler(signum: int, frame: Any) -> None:  # noqa: ARG001
    raise _Timeout()


def candidate_failed() -> bool:
    """Return True iff the most recent ``safe_call`` substituted SAFE_DEFAULT.

    The orchestrating training loop polls this flag to mark a candidate reward as
    failed (and stop using it) while continuing to train other candidates.
    """
    return _LAST_CALL_FAILED


def reset_failure_flag() -> None:
    """Clear the module-level failure flag before evaluating a new candidate."""
    global _LAST_CALL_FAILED
    _LAST_CALL_FAILED = False


def ast_gate(src: str) -> bool:
    """Statically reject unsafe reward source before any execution.

    Algorithm (FINAL_PLAN F.5):
        Parse `src` and walk the AST. Reject if any node is:
          - an Import / ImportFrom outside ALLOWED_IMPORTS;
          - an Attribute whose name starts with "__" (dunder access);
          - a Call to one of {open, exec, eval, __import__}.
        Otherwise accept.

    Args:
        src: The candidate reward source code.

    Returns:
        True iff the source passes every gate check.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        # 1. Imports must be inside the numpy allowlist.
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in ALLOWED_IMPORTS:
                    return False
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in ALLOWED_IMPORTS:
                return False

        # 2. No dunder attribute access (e.g. ().__class__, x.__globals__).
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                return False

        # 3. No dunder *name* references (e.g. __import__, __builtins__).
        elif isinstance(node, ast.Name):
            if node.id.startswith("__"):
                return False

        # 4. No calls to dangerous builtins.
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in _FORBIDDEN_CALLS:
                return False
            if isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_CALLS:
                return False

    return True


def validate_once(src: str, fixture: Any, timeout_s: float = 2.0) -> RewardFn:
    """Gate the source, then run it exactly once on a fixture under a timeout.

    Algorithm (stage 1 of audit A-5):
        Assert ast_gate(src); compile/exec the source in the restricted namespace
        {"np": numpy}; invoke the resulting `reward` once on `fixture` under a
        wall-clock timeout. Reject (raise) on gate failure, crash, timeout, or a
        contract violation. Return the compiled callable on success.

    Args:
        src: The candidate reward source code.
        fixture: A small anonymized fixture matching the reward contract args.
        timeout_s: Wall-clock timeout for the single validation run.

    Returns:
        The validated, compiled reward callable.

    Raises:
        SandboxError: on gate failure, exec/compile error, missing/non-callable
            ``reward``, runtime crash, timeout, or a contract violation.

    Notes
    -----
    The wall-clock timeout uses ``signal.SIGALRM``, which is only deliverable on
    the main thread of a Unix process (macOS / Linux). On Windows, or when called
    off the main thread, the timeout is silently skipped and only crash/contract
    checks apply.
    """
    if not ast_gate(src):
        raise SandboxError("ast_gate rejected the candidate source")

    namespace: dict[str, Any] = {"np": np, "__builtins__": SAFE_BUILTINS}
    try:
        code = compile(src, "<candidate_reward>", "exec")
        exec(code, namespace)  # noqa: S102 — gated, restricted-builtins namespace
    except Exception as exc:  # noqa: BLE001
        raise SandboxError(f"reward source failed to compile/exec: {exc!r}") from exc

    fn = namespace.get("reward")
    if not callable(fn):
        raise SandboxError("source defines no callable named 'reward'")

    # Install the alarm only when we are on the main thread of a Unix process.
    use_alarm = hasattr(signal, "SIGALRM")
    if use_alarm:
        try:
            old_handler = signal.signal(signal.SIGALRM, _alarm_handler)
        except (ValueError, OSError):
            use_alarm = False

    try:
        if use_alarm:
            signal.setitimer(signal.ITIMER_REAL, float(timeout_s))
        try:
            out = fn(*fixture)
        except _Timeout as exc:
            raise SandboxError(
                f"reward exceeded the {timeout_s}s validation timeout"
            ) from exc
        except Exception as exc:  # noqa: BLE001
            raise SandboxError(f"reward crashed during validation: {exc!r}") from exc
    finally:
        if use_alarm:
            signal.setitimer(signal.ITIMER_REAL, 0.0)
            signal.signal(signal.SIGALRM, old_handler)

    # Contract check: must return (float total, dict components, state).
    if not (isinstance(out, tuple) and len(out) == 3):
        raise SandboxError("reward did not return a 3-tuple (total, components, state)")
    total, components, _state = out
    try:
        total_f = float(total)
    except (TypeError, ValueError) as exc:
        raise SandboxError("reward total is not coercible to float") from exc
    if not math.isfinite(total_f):
        raise SandboxError("reward returned a non-finite total")
    if not isinstance(components, dict):
        raise SandboxError("reward components is not a dict")

    return fn  # type: ignore[return-value]


def safe_call(fn: RewardFn, *args: Any) -> tuple[float, dict[str, float], object]:
    """Invoke a validated reward in-process, substituting SAFE_DEFAULT on failure.

    Algorithm (stage 2 of audit A-5):
        try: total, components, state = fn(*args); require np.isfinite(total);
             return (float(total), components, state).
        except (or non-finite total): return (SAFE_DEFAULT, {}, None) and flag the
             candidate. No subprocess, no per-step timeout.

    Args:
        fn: A reward callable already cleared by `validate_once`.
        *args: The contract arguments (weights, returns, prev_weights, port_ret, info).

    Returns:
        (total, components, reward_state); the safe-default triple on failure.
    """
    global _LAST_CALL_FAILED
    try:
        out = fn(*args)
        total, components, state = out
        total_f = float(total)
        if not math.isfinite(total_f):
            raise ValueError("non-finite total")
    except Exception:  # noqa: BLE001 — any failure is a candidate failure, not fatal
        _LAST_CALL_FAILED = True
        return (SAFE_DEFAULT, {}, None)

    _LAST_CALL_FAILED = False
    return (total_f, components, state)

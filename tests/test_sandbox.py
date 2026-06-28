"""Tests for src/sandbox/executor.py — two-stage untrusted execution (F.5, A-5)."""

from __future__ import annotations

import importlib.util
import multiprocessing as mp

import numpy as np
import pytest

from src.reward.contract import SAFE_DEFAULT
from src.sandbox import executor
from src.sandbox.executor import (
    _ALLOWED_ATTRS,
    SandboxError,
    ast_gate,
    candidate_failed,
    extract_reward_source,
    reset_failure_flag,
    safe_call,
    safe_call_count,
    safe_default_count,
    validate_once,
)

# A minimal, contract-conforming numpy-only reward used across tests.
VALID_SRC = """
def reward(weights, returns, prev_weights, port_ret, info):
    total = float(np.sum(weights * returns))
    return total, {"raw": total}, None
"""


def _fixture(rng: np.random.Generator) -> tuple:
    """A contract fixture of anonymized numpy arrays only."""
    n = 5
    weights = np.full(n, 1.0 / n)
    returns = rng.standard_normal(n) * 0.01
    prev_weights = np.full(n, 1.0 / n)
    port_ret = float(np.sum(weights * returns))
    info: dict = {}
    return (weights, returns, prev_weights, port_ret, info)


def test_os_import_rejected_at_gate() -> None:
    """ast_gate rejects `import os` (imports outside the numpy allowlist)."""
    assert ast_gate("import os\n") is False
    assert ast_gate("import numpy as np\n") is True
    assert ast_gate("from os import path\n") is False


def test_from_numpy_import_rce_rejected_at_gate() -> None:
    """RCE fix (2026-06-25): `from numpy import load` passed a root-module-only ImportFrom check
    (numpy allowlisted), then `load(...)` was a BARE ast.Name the _BANNED_ATTRS attribute-allowlist
    never inspected -> np.load pickle-RCE. ALL `from ... import` (incl. wildcard) are now rejected;
    `import numpy as np` stays the only legitimate import."""
    assert ast_gate("from numpy import load\n") is False
    assert ast_gate("from numpy import load as l\n") is False
    assert ast_gate("from numpy import *\n") is False
    assert ast_gate("from numpy.lib import npyio\n") is False
    assert ast_gate("import numpy as np\n") is True
    # End-to-end: validate_once must also refuse the bypass.
    with pytest.raises(SandboxError):
        validate_once(
            "def reward(weights, returns, prev_weights, port_ret, info):\n"
            "    from numpy import load\n"
            "    return 0.0, {}, None\n",
            _fixture(np.random.default_rng(0)),
        )


def test_file_read_rejected_at_gate() -> None:
    """ast_gate rejects open()/eval()/exec() attempts in the reward source."""
    assert ast_gate("def reward(*a):\n    open('/etc/passwd')\n") is False
    assert ast_gate("def reward(*a):\n    eval('1+1')\n") is False
    assert ast_gate("def reward(*a):\n    exec('x=1')\n") is False
    # Dunder attribute escape (().__class__...) must also be rejected.
    assert ast_gate("def reward(*a):\n    return ().__class__\n") is False
    assert ast_gate("def reward(*a):\n    return __import__('os')\n") is False


def test_str_format_dunder_escape_rejected() -> None:
    """str.format can walk dunders INSIDE a string literal (invisible to the Attribute AST walk):
    '{0.__class__.__mro__[1].__subclasses__}'.format(x) -> object.__subclasses__ (RCE). The gate must
    reject it via (a) 'format' no longer allowlisted and (b) the format-field-access literal scan."""
    assert ast_gate(
        "def reward(w,r,pw,pr,info):\n"
        "    s = '{0.__class__.__mro__[1].__subclasses__}'.format(w)\n    return 0.0,{},None"
    ) is False
    assert ast_gate("def reward(*a):\n    x = '{}'.format(3)\n    return 0.0,{},None") is False  # format gone
    assert ast_gate("def reward(*a):\n    s = '{0[0]}'.format([1])\n    return 0.0,{},None") is False
    # a legit numeric reward (no string formatting) still passes
    assert ast_gate(
        "import numpy as np\ndef reward(w,r,pw,pr,info):\n    return float(pr-0.5*float(np.var(r))),{},None"
    ) is True


def test_date_reference_rejected() -> None:
    """Source importing datetime is rejected (anonymized arrays only, no dates)."""
    assert ast_gate("import datetime\n") is False
    assert ast_gate("from datetime import date\n") is False


def test_infinite_loop_killed_at_validate_once(rng: np.random.Generator) -> None:
    """validate_once kills a non-terminating reward at its timeout (stage 1)."""
    src = """
def reward(weights, returns, prev_weights, port_ret, info):
    while True:
        pass
    return 0.0, {}, None
"""
    with pytest.raises(SandboxError):
        validate_once(src, _fixture(rng), timeout_s=1.0)


def test_valid_reward_passes_gate_validates_and_runs(rng: np.random.Generator) -> None:
    """A valid numpy reward passes the gate, validates, and safe_call returns its value."""
    assert ast_gate(VALID_SRC) is True
    fixture = _fixture(rng)
    fn = validate_once(VALID_SRC, fixture, timeout_s=2.0)
    reset_failure_flag()
    total, components, state = safe_call(fn, *fixture)
    expected = float(np.sum(fixture[0] * fixture[1]))
    assert np.isclose(total, expected)
    assert components == {"raw": expected}
    assert state is None
    assert candidate_failed() is False


def test_in_process_error_caught_flagged_and_loop_continues(
    rng: np.random.Generator,
) -> None:
    """safe_call catches an in-process error, substitutes SAFE_DEFAULT, flags, continues."""

    def boom(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        raise RuntimeError("kaboom")

    reset_failure_flag()
    fixture = _fixture(rng)
    total, components, state = safe_call(boom, *fixture)
    assert total == SAFE_DEFAULT
    assert components == {}
    assert state is None
    assert candidate_failed() is True

    # A NaN-returning reward is also caught.
    def nanny(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        return float("nan"), {}, None

    reset_failure_flag()
    total, _, _ = safe_call(nanny, *fixture)
    assert total == SAFE_DEFAULT
    assert candidate_failed() is True

    # The loop continues: a subsequent good reward succeeds and clears the flag.
    def good(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        return float(port_ret), {"r": float(port_ret)}, None

    total, _, _ = safe_call(good, *fixture)
    assert np.isclose(total, fixture[3])
    assert candidate_failed() is False


def test_safe_default_count_accumulates_over_window(rng: np.random.Generator) -> None:
    """R66: ``safe_default_count`` accumulates EVERY substitution in a window (not last-call only), so an
    intermittent reward that recovers on the final step is still quantified — while ``candidate_failed``
    keeps its documented last-call semantics (a later success clears the boolean)."""
    fixture = _fixture(rng)

    def boom(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        raise RuntimeError("boom")

    def good(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        return float(port_ret), {}, None

    reset_failure_flag()
    assert safe_default_count() == 0 and safe_call_count() == 0
    safe_call(boom, *fixture)  # fail -> count 1
    safe_call(boom, *fixture)  # fail -> count 2
    safe_call(good, *fixture)  # succeed on the LAST call -> count stays 2
    assert safe_call_count() == 3
    assert safe_default_count() == 2  # accumulates across the whole window
    assert candidate_failed() is False  # last-call contract preserved (a later success clears the bool)
    reset_failure_flag()
    assert safe_default_count() == 0 and safe_call_count() == 0


def test_reward_never_receives_tickers_or_dates(rng: np.random.Generator) -> None:
    """A reward is only ever passed anonymized arrays — no tickers, no dates."""
    captured: dict = {}

    def spy(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        captured["weights"] = weights
        captured["returns"] = returns
        captured["prev_weights"] = prev_weights
        captured["port_ret"] = port_ret
        return float(port_ret), {}, None

    fixture = _fixture(rng)
    safe_call(spy, *fixture)
    for key in ("weights", "returns", "prev_weights"):
        assert isinstance(captured[key], np.ndarray)
        assert np.issubdtype(captured[key].dtype, np.number)
    assert isinstance(captured["port_ret"], float)


def test_failure_flag_module_level() -> None:
    """The failure flag is module-level so an orchestrator can mark a candidate."""
    reset_failure_flag()
    assert executor.candidate_failed() is False


# Regression: ndarray METHODS (.mean()/.var()) and other numpy ops trigger numpy's
# lazy submodule imports, which resolve __import__ from the sandbox namespace. With a
# restricted-builtins namespace lacking __import__ these crashed with KeyError, both at
# validation and SILENTLY during training via safe_call (every such candidate flagged
# "failed"). The fix is the controlled _safe_import in SAFE_BUILTINS.
@pytest.mark.parametrize(
    "body",
    [
        "    return float(port_ret - 0.5 * returns.var()), {'m': float(returns.mean())}, None",
        "    q = np.quantile(returns, 0.05); return float(port_ret + q), {'q': float(q)}, None",
        "    s = np.sort(returns); return float(port_ret + float(s[0])), {}, None",
        "    xs = [float(x) for x in returns]; return float(port_ret * len(xs)), {'n': float(len(xs))}, None",
    ],
)
def test_numpy_method_rewards_validate_and_run_without_failing(
    body: str, rng: np.random.Generator
) -> None:
    """Legitimate numpy reward code (methods, np funcs, comprehensions) must validate AND
    run via safe_call WITHOUT being flagged failed — guards the __import__ sandbox fix."""
    src = "def reward(weights, returns, prev_weights, port_ret, info):\n" + body
    assert ast_gate(src) is True
    fixture = _fixture(rng)
    fn = validate_once(src, fixture, timeout_s=2.0)
    reset_failure_flag()
    total, _components, _state = safe_call(fn, *fixture)
    assert np.isfinite(total)
    assert candidate_failed() is False  # the silent-failure bug would set this True


def test_safe_import_denies_fresh_non_numpy_module() -> None:
    """Defence-in-depth: the sandbox __import__ denies a brand-new non-numpy import."""
    with pytest.raises(ImportError):
        executor._safe_import("a_module_that_is_definitely_not_loaded_zzz")


# --- ADR-008: numpy IO/FFI attribute denylist at the gate ---------------------------

# Each source is well-formed numpy that the OLD gate (dunder-only) would have PASSED but
# whose attribute is a filesystem / pickle-RCE / FFI vector. The hardened gate must
# REJECT every one of them (np.load with allow_pickle=True is arbitrary code execution).
@pytest.mark.parametrize(
    "src",
    [
        "def reward(*a):\n    return float(np.load('x.npy', allow_pickle=True).sum()), {}, None\n",
        "def reward(*a):\n    np.save('out.npy', a[0]); return 0.0, {}, None\n",
        "def reward(*a):\n    return float(np.fromfile('x.bin').sum()), {}, None\n",
        "def reward(*a):\n    return float(np.genfromtxt('x.csv').sum()), {}, None\n",
        "def reward(*a):\n    return float(np.loadtxt('x.csv').sum()), {}, None\n",
        "def reward(*a):\n    m = np.memmap('x.bin', dtype='f8'); return float(m[0]), {}, None\n",
        "def reward(*a):\n    return float(np.DataSource().open('x').read()), {}, None\n",
        "def reward(*a):\n    a[0].tofile('leak.bin'); return 0.0, {}, None\n",
        "def reward(*a):\n    return np.lib.format.read_magic, {}, None\n",
        "def reward(*a):\n    return np.ctypeslib.as_array, {}, None\n",
        # final-acceptance-audit 2026-06-19 P1 READ-escapes (genfromtxt aliases + file-first read):
        "def reward(*a):\n    return float(np.recfromtxt('x.csv').sum()), {}, None\n",
        "def reward(*a):\n    return float(np.recfromcsv('x.csv').sum()), {}, None\n",
        "def reward(*a):\n    return float(np.fromregex('x', '.', float).sum()), {}, None\n",
        # final-acceptance-audit 2026-06-19 P1 WRITE-escapes (ndarray.dump/dumps pickle to a path):
        "def reward(*a):\n    a[0].dump('leak.pkl'); return 0.0, {}, None\n",
        "def reward(*a):\n    return float(len(a[0].dumps())), {}, None\n",
    ],
)
def test_gate_rejects_numpy_io_and_ffi_attributes(src: str) -> None:
    """ast_gate REJECTS numpy's file/FFI/loader surface (ADR-008 attribute denylist)."""
    assert ast_gate(src) is False


def test_gate_rejects_mro_object_model_escape() -> None:
    """The .mro object-model escape route is rejected as a banned attribute (ADR-008)."""
    assert ast_gate("def reward(*a):\n    return type(a).mro(), {}, None\n") is False


def test_gate_rejects_np_seterr_global_state_leak() -> None:
    """np.seterr sets numpy's PROCESS-GLOBAL float-error mode and does not restore it, so an
    untrusted reward calling it would leak that mode into every LATER candidate -> order-dependent,
    non-deterministic campaign (V15b). It must be rejected at the gate (``seterr`` de-allowlisted)."""
    assert ast_gate("def reward(*a):\n    np.seterr(all='ignore'); return 0.0, {}, None\n") is False
    assert ast_gate("def reward(*a):\n    np.seterr(divide='raise'); return 0.0, {}, None\n") is False
    # End-to-end: validate_once must also refuse a seterr reward (gate runs first).
    with pytest.raises(SandboxError):
        validate_once(
            "def reward(weights, returns, prev_weights, port_ret, info):\n"
            "    np.seterr(all='ignore')\n"
            "    return float(port_ret), {}, None\n",
            _fixture(np.random.default_rng(0)),
        )
    # The leak-FREE alternatives stay allowed: errstate (a context manager that RESTORES the prior
    # mode on exit) and geterr (read-only) are not global-state leaks, so a reward may still use them.
    assert ast_gate(
        "def reward(*a):\n"
        "    with np.errstate(divide='ignore'):\n"
        "        x = np.geterr()\n"
        "    return 0.0, {}, None\n"
    ) is True


def test_legitimate_reward_math_still_passes_gate(rng: np.random.Generator) -> None:
    """POSITIVE control: real reward math (reductions, indexing, np.abs/where/clip/dot,
    arithmetic) STILL PASSES — the IO/FFI denylist must not over-block (ADR-008)."""
    src = (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    pnl = np.sum(weights * returns)\n"
        "    mu = np.mean(returns)\n"
        "    sd = np.std(returns)\n"
        "    v = np.var(returns)\n"
        "    dd = np.dot(weights, returns)\n"
        "    turnover = np.sum(np.abs(weights - prev_weights))\n"
        "    downside = np.where(returns < 0.0, returns, 0.0)\n"
        "    worst = returns[0] - np.clip(sd, 0.0, 1.0)\n"
        "    total = float(pnl + mu - 0.5 * v + dd - 0.01 * turnover"
        " + float(np.sum(downside)) + float(worst))\n"
        "    return total, {'pnl': float(pnl), 'sd': float(sd)}, None\n"
    )
    # Passes the static gate ...
    assert ast_gate(src) is True
    # ... and actually validates + runs without being flagged failed.
    fixture = _fixture(rng)
    fn = validate_once(src, fixture, timeout_s=2.0)
    reset_failure_flag()
    total, components, _state = safe_call(fn, *fixture)
    assert np.isfinite(total)
    assert set(components) == {"pnl", "sd"}
    assert candidate_failed() is False


# The address-space (RLIMIT_AS) cap is POSIX-only; on Windows `resource` is absent and
# the wall-clock timeout is the backstop, so skip there (ADR-008 documented gap).
_HAS_RESOURCE = importlib.util.find_spec("resource") is not None


@pytest.mark.skipif(not _HAS_RESOURCE, reason="POSIX 'resource' module unavailable (Windows)")
def test_memory_bomb_rejected_at_validate_once(rng: np.random.Generator) -> None:
    """A reward that allocates far past RLIMIT_AS is killed/rejected at validate_once.

    The child caps address space at ~2 GiB (clamped to the hard limit); a multi-GiB
    allocation must raise MemoryError in the child -> reported as a SandboxError, not an
    OOM of the host. The source itself is gate-clean (only arithmetic + np.ones)."""
    src = (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    big = np.ones((8, 1024, 1024, 1024), dtype=np.float64)\n"  # ~64 GiB
        "    return float(big.sum()), {}, None\n"
    )
    assert ast_gate(src) is True
    with pytest.raises(SandboxError):
        validate_once(src, _fixture(rng), timeout_s=10.0)


# =====================================================================================
# ADDED (this task): strict security/determinism net for the AST gate + sandbox.
# Each test cites the threat it locks; every test EXTENDS coverage above (no duplicates).
# =====================================================================================


def test_v15b_seterr_absent_from_allowlist_determinism_rationale() -> None:
    """V15b REGRESSION-LOCK (determinism). The reason ``np.seterr`` is gated is that it mutates
    numpy's PROCESS-GLOBAL float-error mode without restoring it, leaking that mode into every
    LATER candidate and making the campaign order-dependent / non-deterministic. The mechanism
    that enforces this is ``seterr`` being absent from ``_ALLOWED_ATTRS`` (the allowlist) while the
    leak-free alternatives stay present. Assert that invariant directly so a future allowlist edit
    that re-adds ``seterr`` fails LOUDLY here, independent of any payload-level gate test."""
    assert "seterr" not in _ALLOWED_ATTRS  # de-allowlisted on purpose (determinism)
    # The leak-free alternatives MUST remain allowlisted (errstate restores on exit; geterr is read-only).
    assert "errstate" in _ALLOWED_ATTRS
    assert "geterr" in _ALLOWED_ATTRS


def test_v15b_errstate_geterr_reward_validates_and_runs(rng: np.random.Generator) -> None:
    """V15b (positive half). A reward using the leak-FREE float-error API — ``with np.errstate(...)``
    (restores the prior mode on exit) and ``np.geterr()`` (read-only) — must not only pass the gate
    but actually VALIDATE and run finite via safe_call, proving the determinism carve-out is usable."""
    src = (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    with np.errstate(divide='ignore', invalid='ignore'):\n"
        "        x = np.log1p(np.abs(returns))\n"
        "        _mode = np.geterr()\n"
        "    return float(port_ret + float(np.sum(x))), {'mode_keys': float(len(_mode))}, None\n"
    )
    assert ast_gate(src) is True
    fixture = _fixture(rng)
    fn = validate_once(src, fixture, timeout_s=2.0)
    reset_failure_flag()
    total, _components, _state = safe_call(fn, *fixture)
    assert np.isfinite(total)
    assert candidate_failed() is False


# RCE / sandbox-ESCAPE payloads. Each is a known object-model / FFI / IO / dynamic-eval escape that
# MUST be stopped — either statically (ast_gate -> False) or end-to-end (validate_once -> SandboxError).
# The threat: the gate is an allowlist net; any payload reaching os/builtins/pickle/FFI is an RCE.
# Some overlap with focused tests above is intentional — this is the consolidated belt-and-braces sweep.
_RCE_ESCAPE_PAYLOADS: list[str] = [
    # --- import-surface escapes ---
    "def reward(*a):\n    from numpy import *\n    return 0.0, {}, None\n",
    "def reward(*a):\n    from numpy import load\n    return 0.0, {}, None\n",
    "def reward(*a):\n    return __import__('os').getcwd(), {}, None\n",
    # --- object-model / dunder-walk escapes ---
    "def reward(*a):\n    return ().__class__.__mro__, {}, None\n",
    "def reward(*a):\n    return type(a).mro(), {}, None\n",
    "def reward(*a):\n    return '{0.__class__}'.format(a), {}, None\n",
    # --- numpy submodule traversal to os/builtins (the _pytesttester chain) ---
    "def reward(*a):\n    return np._pytesttester, {}, None\n",
    # --- dynamic-attribute fetch (getattr is a forbidden call) ---
    "def reward(*a):\n    return getattr(np, 'load'), {}, None\n",
    # --- numpy IO / pickle-RCE / FFI surface ---
    "def reward(*a):\n    return np.load('x.npy'), {}, None\n",
    "def reward(*a):\n    np.save('x.npy', a[0]); return 0.0, {}, None\n",
    "def reward(*a):\n    return np.fromfile('x.bin'), {}, None\n",
    "def reward(*a):\n    m = np.memmap('x.bin', dtype='f8'); return float(m[0]), {}, None\n",
    "def reward(*a):\n    a[0].dump('leak.pkl'); return 0.0, {}, None\n",
    "def reward(*a):\n    return np.ctypeslib.as_array, {}, None\n",
    "def reward(*a):\n    return a[0].ctypes, {}, None\n",
    "def reward(*a):\n    return a[0].data, {}, None\n",
    # --- dynamic-eval / IO builtins ---
    "def reward(*a):\n    return eval('1+1'), {}, None\n",
    "def reward(*a):\n    exec('x=1'); return 0.0, {}, None\n",
    "def reward(*a):\n    return compile('1', '<s>', 'eval'), {}, None\n",
    "def reward(*a):\n    return open('/etc/passwd').read(), {}, None\n",
]


@pytest.mark.parametrize("payload", _RCE_ESCAPE_PAYLOADS)
def test_rce_and_escape_payloads_all_blocked(payload: str, rng: np.random.Generator) -> None:
    """EVERY RCE / sandbox-escape payload is blocked — gated statically (ast_gate False) OR refused
    end-to-end (validate_once raises SandboxError). A payload that passes BOTH would be a live escape
    to os/builtins/pickle/FFI: a security finding, so the assertion is hard and the test is permanent."""
    gated = ast_gate(payload) is False
    if gated:
        return  # blocked at the static gate — the cheapest, preferred stop
    # If somehow gate-clean, the runtime stage MUST still reject it (else it is a real escape).
    with pytest.raises(SandboxError):
        validate_once(payload, _fixture(rng), timeout_s=5.0)


def test_benign_pure_numpy_reward_validates_and_runs_finite(rng: np.random.Generator) -> None:
    """POSITIVE control: a pure-numpy reward using mean/std/clip/percentile/where/log1p/errstate must
    validate and safe_call must return a finite (total, dict, state). Guards against the allowlist
    over-blocking real risk-sensitive reward arithmetic (the gate is a net, not a wall)."""
    src = (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    mu = np.mean(returns)\n"
        "    sd = np.std(returns)\n"
        "    var5 = np.percentile(returns, 5.0)\n"
        "    downside = np.where(returns < 0.0, returns, 0.0)\n"
        "    with np.errstate(divide='ignore', invalid='ignore'):\n"
        "        damp = np.log1p(np.abs(np.clip(returns, -1.0, 1.0)))\n"
        "    total = float(port_ret + float(mu) - 0.5 * float(sd) + float(var5)"
        " + float(np.sum(downside)) + float(np.sum(damp)))\n"
        "    return total, {'mu': float(mu), 'var5': float(var5)}, None\n"
    )
    assert ast_gate(src) is True
    fixture = _fixture(rng)
    fn = validate_once(src, fixture, timeout_s=2.0)
    reset_failure_flag()
    total, components, state = safe_call(fn, *fixture)
    assert isinstance(total, float) and np.isfinite(total)
    assert isinstance(components, dict) and set(components) == {"mu", "var5"}
    assert state is None
    assert candidate_failed() is False


# --- FENCE / PROSE SALVAGE: extract_reward_source recovers runnable code from raw LLM output -------

_CLEAN_REWARD = (
    "import numpy as np\n"
    "def reward(weights, returns, prev_weights, port_ret, info):\n"
    "    return float(port_ret), {}, None"
)


def test_extract_reward_source_strips_python_fence() -> None:
    """FENCE SALVAGE: an LLM wraps the function in a ```python ... ``` fence despite the
    'return only the function' instruction; ast.parse(whole) would SyntaxError and starve the arm.
    extract_reward_source must recover the runnable function from the fence."""
    wrapped = "```python\n" + _CLEAN_REWARD + "\n```"
    out = extract_reward_source(wrapped)
    assert "def reward(" in out
    assert ast_gate(out) is True


def test_extract_reward_source_strips_prose_preamble() -> None:
    """PROSE SALVAGE: a prose preamble + trailing prose around the code (no fence). The shim slices
    from the first code-start line and trims to the longest parsing suffix."""
    completion = (
        "Sure! Here is a risk-sensitive reward function for you:\n\n"
        + _CLEAN_REWARD
        + "\n\nThis penalizes downside variance. Let me know if you want changes."
    )
    out = extract_reward_source(completion)
    assert "def reward(" in out
    assert ast_gate(out) is True


def test_extract_reward_source_multi_fence_picks_parsing_reward_block() -> None:
    """MULTI-FENCE SALVAGE: a 'first attempt / corrected version' completion has two fences; the first
    is syntactically broken. extract_reward_source must pick a block that PARSES and defines reward,
    not commit to the broken first block (audit fix: recoverable candidate must not be starved)."""
    broken = "```python\ndef reward(weights, returns,   # oops truncated\n```"
    good = "```python\n" + _CLEAN_REWARD + "\n```"
    completion = "First attempt:\n" + broken + "\n\nCorrected version:\n" + good
    out = extract_reward_source(completion)
    assert "def reward(" in out
    assert ast_gate(out) is True


def test_extract_reward_source_clean_code_is_byte_identical() -> None:
    """NO-OP path: already-clean code that parses is returned BYTE-IDENTICAL (exact bytes) so the
    archived source and its hash stay stable (re-audit invariant)."""
    assert extract_reward_source(_CLEAN_REWARD) == _CLEAN_REWARD
    # Even clean code that merely CONTAINS a ``` inside a string literal still parses -> unchanged.
    with_ticks = (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    note = 'see ```docs```'\n"
        "    return float(port_ret), {}, None"
    )
    assert extract_reward_source(with_ticks) == with_ticks


# --- safe_call CONTAINMENT: the in-process training path never propagates a candidate failure ------


def test_safe_call_contains_wrong_arity_return(rng: np.random.Generator) -> None:
    """CONTAINMENT: a reward returning the WRONG ARITY (not a 3-tuple) is contained by safe_call ->
    SAFE_DEFAULT, flag flips True, no exception escapes into the training loop; reset clears it."""
    fixture = _fixture(rng)

    def two_tuple(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        return float(port_ret), {}  # wrong arity (2-tuple): unpack to 3 raises in safe_call

    reset_failure_flag()
    total, components, state = safe_call(two_tuple, *fixture)
    assert total == SAFE_DEFAULT
    assert components == {} and state is None
    assert candidate_failed() is True

    # A non-tuple return is likewise contained (cannot unpack a scalar to 3).
    def scalar_only(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        return 1.0

    reset_failure_flag()
    total, _, _ = safe_call(scalar_only, *fixture)
    assert total == SAFE_DEFAULT
    assert candidate_failed() is True

    # reset_failure_flag clears the flag for the next candidate.
    reset_failure_flag()
    assert candidate_failed() is False


def test_safe_call_never_raises_into_training_path(rng: np.random.Generator) -> None:
    """CONTAINMENT: whatever a malicious/buggy reward does (raise, +inf, -inf, wrong arity),
    safe_call MUST return a 3-tuple with a finite total and never let the exception propagate —
    the training rollout depends on this for forward progress."""
    fixture = _fixture(rng)

    def raiser(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        raise ValueError("boom")

    def pos_inf(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        return float("inf"), {}, None

    def neg_inf(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        return float("-inf"), {}, None

    for fn in (raiser, pos_inf, neg_inf):
        reset_failure_flag()
        out = safe_call(fn, *fixture)  # must NOT raise
        assert isinstance(out, tuple) and len(out) == 3
        total, components, state = out
        assert total == SAFE_DEFAULT and np.isfinite(total)
        assert components == {} and state is None
        assert candidate_failed() is True


# --- POSIX-guarded: a resource bomb is killed at validate_once and the PARENT survives -------------


def _parent_survives_marker() -> str:
    """A trivial computation the parent runs AFTER a kill, proving it is still alive and usable."""
    return str(int(np.sum(np.arange(10))))


@pytest.mark.skipif(not _HAS_RESOURCE, reason="POSIX 'resource' module unavailable (Windows)")
def test_resource_bomb_killed_and_parent_survives(rng: np.random.Generator) -> None:
    """CONTAINMENT (POSIX): a gate-clean reward that allocates far past RLIMIT_AS is killed in the
    KILLABLE child and surfaces as a SandboxError — and crucially the PARENT (test) process survives
    and keeps running. This is the cross-platform-timeout / rlimit boundary (C2 / ADR-008)."""
    src = (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    big = np.ones((8, 1024, 1024, 1024), dtype=np.float64)\n"  # ~64 GiB > 2 GiB cap
        "    return float(big.sum()), {}, None\n"
    )
    assert ast_gate(src) is True
    # validate_once uses the 'spawn' mp context; a runaway/oversized child must not take us down.
    assert mp.get_context("spawn") is not None  # the context the module itself uses (spawn)
    with pytest.raises(SandboxError):
        validate_once(src, _fixture(rng), timeout_s=10.0)
    # PARENT SURVIVES: we are still executing and can still compute.
    assert _parent_survives_marker() == "45"


@pytest.mark.skipif(not _HAS_RESOURCE, reason="POSIX 'resource' module unavailable (Windows)")
def test_infinite_loop_killed_and_parent_survives(rng: np.random.Generator) -> None:
    """CONTAINMENT (POSIX): a non-terminating reward is killed at the validate_once wall-clock
    timeout (the child is terminated) and the PARENT survives — the runaway cannot hang the run."""
    src = (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    while True:\n"
        "        pass\n"
        "    return 0.0, {}, None\n"
    )
    assert ast_gate(src) is True
    with pytest.raises(SandboxError):
        validate_once(src, _fixture(rng), timeout_s=1.0)
    assert _parent_survives_marker() == "45"

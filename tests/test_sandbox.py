"""Tests for src/sandbox/executor.py — two-stage untrusted execution (F.5, A-5)."""

from __future__ import annotations

import numpy as np
import pytest

from src.reward.contract import SAFE_DEFAULT
from src.sandbox import executor
from src.sandbox.executor import (
    SandboxError,
    ast_gate,
    candidate_failed,
    reset_failure_flag,
    safe_call,
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


def test_file_read_rejected_at_gate() -> None:
    """ast_gate rejects open()/eval()/exec() attempts in the reward source."""
    assert ast_gate("def reward(*a):\n    open('/etc/passwd')\n") is False
    assert ast_gate("def reward(*a):\n    eval('1+1')\n") is False
    assert ast_gate("def reward(*a):\n    exec('x=1')\n") is False
    # Dunder attribute escape (().__class__...) must also be rejected.
    assert ast_gate("def reward(*a):\n    return ().__class__\n") is False
    assert ast_gate("def reward(*a):\n    return __import__('os')\n") is False


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

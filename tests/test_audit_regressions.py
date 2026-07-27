"""Regression guards for the 2026-06-19 deep-audit fixes.

Each test pins a specific confirmed audit finding so the fix cannot silently regress. Findings are
referenced by their audit number (#N) in the test name/docstring. Kept in one file for traceability.
"""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

from src.data.panel import Panel
from src.env.portfolio_env import PortfolioEnv
from src.sandbox.executor import ast_gate, extract_reward_source, validate_once
from src.utils.config import load_config

_SCRIPTS = str(Path(__file__).resolve().parents[1] / "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)


def _reward(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
    return float(port_ret), {}, None


_CLEAN = (
    "def reward(weights, returns, prev_weights, port_ret, info):\n"
    "    return float(port_ret), {'pnl': float(port_ret)}, None\n"
)
_FIXTURE = (np.full(4, 0.25), np.full(4, 0.001), np.full(4, 0.25), 0.0, {})


# --------------------------------------------------------------------------- #
# #1 — code extraction salvages fenced / prose-wrapped LLM output              #
# --------------------------------------------------------------------------- #
def test_extract_strips_python_fence() -> None:
    wrapped = f"```python\n{_CLEAN}```"
    out = extract_reward_source(wrapped)
    assert out.startswith("def reward")
    assert "```" not in out
    assert ast_gate(out)


def test_extract_strips_prose_preamble_and_epilogue() -> None:
    wrapped = f"Here is the reward function:\n\n{_CLEAN}\nThis penalizes tail risk."
    out = extract_reward_source(wrapped)
    assert out.startswith("def reward")
    assert ast_gate(out)


def test_extract_clean_source_is_byte_identical_noop() -> None:
    # The stub / well-behaved author path must NOT be mutated (archived source + hash stay stable).
    assert extract_reward_source(_CLEAN) == _CLEAN


def test_extract_picks_the_reward_defining_fenced_block() -> None:
    text = f"```python\nx = 1\n```\nand the reward:\n```python\n{_CLEAN}```"
    out = extract_reward_source(text)
    assert "def reward" in out and out.strip().startswith("def reward")


def test_extract_empty_is_safe() -> None:
    assert extract_reward_source("") == ""
    assert extract_reward_source("   ") == "   "


def test_validate_once_salvages_fenced_source() -> None:
    # End-to-end: a fenced reward validates (the gate would otherwise SyntaxError on the fences).
    fn = validate_once(f"```python\n{_CLEAN}```", _FIXTURE)
    assert callable(fn)


# --------------------------------------------------------------------------- #
# #3 — AST allowlist blocks numpy-submodule RCE chains (and FFI), keeps numeric #
# --------------------------------------------------------------------------- #
_RCE_VECTORS = [
    "def reward(w, r, p, pr, i):\n    m = np._pytesttester.os\n    m.system('echo x')\n    return 0.0, {}, None\n",
    "def reward(w, r, p, pr, i):\n    m = np.compat.py3k.os\n    return 0.0, {}, None\n",
    "def reward(w, r, p, pr, i):\n    z = np.char.overrides.os.popen('id')\n    return 0.0, {}, None\n",
    "def reward(w, r, p, pr, i):\n    c = np.ones(3).ctypes\n    return 0.0, {}, None\n",
    "def reward(w, r, p, pr, i):\n    d = np.ones(3).data\n    return 0.0, {}, None\n",
]


@pytest.mark.parametrize("src", _RCE_VECTORS)
def test_ast_gate_blocks_rce_and_ffi_vectors(src: str) -> None:
    assert ast_gate(src) is False


# Attribute MUTATION (Store/Del ctx) on allowlisted names: numpy is process-global and
# workers are reused across candidates, so `np.mean = ...` would poison every later
# candidate in the worker (2026-07-05 map finding M03).
_ATTR_MUTATION_VECTORS = [
    "def reward(w, r, p, pr, i):\n    np.mean = lambda *a, **k: 0.0\n    return 0.0, {}, None\n",
    "def reward(w, r, p, pr, i):\n    del np.mean\n    return 0.0, {}, None\n",
    "def reward(w, r, p, pr, i):\n    np.pi += 1.0\n    return 0.0, {}, None\n",
]


@pytest.mark.parametrize("src", _ATTR_MUTATION_VECTORS)
def test_ast_gate_blocks_attribute_mutation(src: str) -> None:
    assert ast_gate(src) is False


def test_ast_gate_admits_numeric_reward() -> None:
    numeric = (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    state = info.get('reward_state')\n"
        "    hist = list(state) if state is not None else []\n"
        "    hist.append(float(port_ret))\n"
        "    arr = np.asarray(hist, dtype=float)\n"
        "    turnover = float(np.sum(np.abs(weights - prev_weights)))\n"
        "    sigma = float(np.std(arr)) if arr.size > 1 else 0.0\n"
        "    k = max(1, int(np.ceil(0.05 * arr.size)))\n"
        "    cvar = float(np.mean(np.sort(arr)[:k]))\n"
        "    total = float(port_ret) - 0.5 * sigma - turnover - max(0.0, -cvar)\n"
        "    return total, {'sigma': sigma, 'cvar': cvar}, hist\n"
    )
    assert ast_gate(numeric) is True


# --------------------------------------------------------------------------- #
# #7 — gold (vix_prelagged) panel is NOT double-lagged by the env              #
# --------------------------------------------------------------------------- #
def _vix_panel(prelagged: bool, n_days: int = 90, n_assets: int = 3) -> Panel:
    rng = np.random.default_rng(0)
    returns = rng.normal(0.0, 0.01, size=(n_days, n_assets))
    vix = 100.0 + np.arange(n_days, dtype=float)  # vix[t] = 100 + t: recoverable from the obs
    dates = np.arange("2010-01-04", n_days, dtype="datetime64[D]")
    return Panel(
        returns=returns,
        vix=vix,
        dates=dates,
        asset_ids=np.arange(n_assets, dtype=np.int64),
        market_caps=np.full((n_days, n_assets), 1e9),
        vix_prelagged=prelagged,
    )


@pytest.mark.parametrize("prelagged,offset", [(True, 0), (False, -1)])
def test_vix_prelagged_controls_env_lag(prelagged: bool, offset: int) -> None:
    cfg = load_config("environment")
    if not cfg["state"].get("include_vix", True):
        pytest.skip("env config has include_vix off")
    env = PortfolioEnv(_vix_panel(prelagged), cfg, _reward)
    env.t = env.start
    obs = env._obs()
    vix_idx = env.lookback * env.N + len(env.vol_windows) * env.N  # obs layout offset of the vix scalar
    assert float(obs[vix_idx]) == 100.0 + (env.start + offset)


def test_panel_slice_propagates_vix_prelagged() -> None:
    # Re-audit regression: slice() dropped the flag, so a sliced GOLD panel reverted to False and the
    # env double-lagged it. slice() must carry vix_prelagged.
    gold = _vix_panel(prelagged=True)
    assert gold.slice(0, 50).vix_prelagged is True
    syn = _vix_panel(prelagged=False)
    assert syn.slice(0, 50).vix_prelagged is False


def test_prelagged_env_steps_to_termination_without_indexerror() -> None:
    # Re-audit regression: the terminal step() builds _obs() at t == panel.T; a prelagged read of
    # vix[t] is out of bounds (would crash the gold campaign's final sealed-eval step). The clamped
    # index must let a prelagged env roll out to termination cleanly.
    cfg = load_config("environment")
    if not cfg["state"].get("include_vix", True):
        pytest.skip("env config has include_vix off")
    panel = _vix_panel(prelagged=True, n_days=90)  # env.end defaults to panel.T -> terminal reads vix[T]
    env = PortfolioEnv(panel, cfg, _reward)
    env.reset()
    n_act = panel.N + 1
    # The window edge is a TRUNCATION, not a termination (audit 2026-06-20): drive the loop on either
    # flag so it stops at the boundary instead of stepping past panel.T into an IndexError.
    terminated, truncated, steps = False, False, 0
    while not (terminated or truncated) and steps < 10_000:
        _obs, _r, terminated, truncated, _info = env.step(np.zeros(n_act, dtype=np.float32))
        steps += 1
    assert truncated  # reached the sealed-leg end via truncation, no IndexError on the terminal prelagged read


# --------------------------------------------------------------------------- #
# #28 — env rejects a realized-vol window larger than the lookback             #
# --------------------------------------------------------------------------- #
def test_env_rejects_vol_window_exceeding_lookback() -> None:
    cfg = deepcopy(load_config("environment"))
    lookback = int(cfg["state"]["lookback_days"])
    cfg["state"]["realized_vol_windows"] = [lookback + 40]  # > lookback -> empty/negative slice
    with pytest.raises(ValueError, match="realized_vol_window"):
        PortfolioEnv(_vix_panel(False, n_days=lookback + 60), cfg, _reward)


# --------------------------------------------------------------------------- #
# #35 — the OpenAI-compatible transport sends max_tokens                        #
# --------------------------------------------------------------------------- #
def test_openai_transport_sends_max_tokens() -> None:
    from src.llm.client import _OpenAITransport

    captured: dict = {}

    class _Client:
        class chat:  # noqa: N801
            class completions:  # noqa: N801
                @staticmethod
                def create(**kwargs):  # noqa: ANN003
                    captured.update(kwargs)
                    msg = type("M", (), {"content": "def reward(): return 0.0"})()
                    return type("R", (), {"choices": [type("C", (), {"message": msg})()], "usage": None})()

    _OpenAITransport(_Client(), "gemini-3.5-flash", temperature=None, retrying=None, max_tokens=8192)("s", "u")
    assert captured["max_tokens"] == 8192   # R103: gemini cap raised 2048->8192 (mandatory-thinking headroom)


# --------------------------------------------------------------------------- #
# #31 — deflated_sharpe alias rejects an unsupported sr_benchmark loudly        #
# --------------------------------------------------------------------------- #
def test_deflated_sharpe_alias_rejects_sr_benchmark() -> None:
    from src.inference.deflated_sharpe import deflated_sharpe

    rng = np.random.default_rng(0)
    rets = rng.normal(0.0005, 0.01, size=300)
    # default (0.0) works; a non-zero benchmark is rejected rather than silently ignored
    assert np.isfinite(deflated_sharpe(rets, 10))
    with pytest.raises(NotImplementedError):
        deflated_sharpe(rets, 10, sr_benchmark=0.5)


# --------------------------------------------------------------------------- #
# #30 — winner_returns handles an ndarray-valued val_returns (no truthiness)    #
# --------------------------------------------------------------------------- #
def test_winner_returns_accepts_ndarray_val_returns() -> None:
    import analyze_results as ar

    records = [
        {"metrics": {"val_fitness": 1.0, "val_returns": np.array([0.01, -0.02, 0.03])}},
        {"metrics": {"val_fitness": 0.5, "val_returns": [0.0, 0.0]}},
    ]
    out = ar.winner_returns(records)  # must NOT raise "truth value of an array is ambiguous"
    assert out is not None
    np.testing.assert_allclose(out, [0.01, -0.02, 0.03])


# --------------------------------------------------------------------------- #
# #9/#14 — the per-seed headline inference is correctly sized; the prior        #
#          seed-AVERAGED-series bootstrap over-rejects a true null              #
# --------------------------------------------------------------------------- #
def test_per_seed_test_correctly_sized_vs_seed_averaged_overrejection() -> None:
    """Empirical proof of the #9/#14 fix. Under a TRUE NULL with across-seed (training-RNG) variance,
    the per-seed paired bootstrap (the new headline inference) rejects at ~5% — correctly sized —
    whereas feeding the per-period SEED-AVERAGE to a single-strategy bootstrap (the prior method)
    over-rejects badly (the averaging shrinks the tested object's variance ~N×)."""
    from src.inference.bootstrap import (
        paired_seed_difference_test,
        sharpe_difference_test,
        sharpe_ratio,
    )

    rng = np.random.default_rng(20_260_620)
    n_rep, n_seeds, t = 120, 20, 400

    def seed_sharpes() -> np.ndarray:  # per-seed Sharpes under the null (mean 0 + seed-level shift)
        return np.array(
            [sharpe_ratio(rng.standard_normal(t) * 0.01 + rng.normal(0.0, 0.0005)) for _ in range(n_seeds)]
        )

    def averaged() -> np.ndarray:  # the OLD method's per-period seed-average under the same null
        return np.vstack(
            [rng.standard_normal(t) * 0.01 + rng.normal(0.0, 0.0005) for _ in range(n_seeds)]
        ).mean(axis=0)

    new_rej = old_rej = 0
    for _ in range(n_rep):
        if paired_seed_difference_test(seed_sharpes(), seed_sharpes(), n_boot=250, rng=rng)["pvalue"] < 0.05:
            new_rej += 1
        if sharpe_difference_test(averaged(), averaged(), n_boot=250, rng=rng)["pvalue"] < 0.05:
            old_rej += 1
    new_rate, old_rate = new_rej / n_rep, old_rej / n_rep
    assert new_rate < 0.13, f"per-seed test should be ~5% under the null; got {new_rate:.3f}"
    assert old_rate > new_rate + 0.05, f"seed-averaged should over-reject; new={new_rate:.3f} old={old_rate:.3f}"


# --------------------------------------------------------------------------- #
# Batch-5 M2 (2026-07-03) — vectorized IQM bootstrap fast path is bit-identical #
# --------------------------------------------------------------------------- #
def test_vectorized_iqm_fast_path_is_bit_identical_to_reference_loop() -> None:
    """The ``statistic is iqm`` fast path must EQUAL the reference per-row loop bitwise, not approx.

    Same seed -> the same pre-drawn (n_boot, n) index matrix; ``statistic=iqm`` takes the vectorized
    row-wise path while a distinct-but-equivalent callable (``lambda x: iqm(x)`` fails the ``is``
    check) takes the reference loop over the SAME index rows. The fast path is a pure re-expression
    of the loop — every returned float must be identical. Guards the power simulator's speed fix
    from ever drifting the campaign's REAL paired test.
    """
    from src.inference.bootstrap import iqm, paired_seed_difference_test

    gen = np.random.default_rng(7)
    a = gen.normal(0.5, 1.0, size=30)
    b = gen.normal(0.4, 1.0, size=30)
    fast = paired_seed_difference_test(a, b, statistic=iqm, n_boot=257, rng=np.random.default_rng(123))
    ref = paired_seed_difference_test(
        a, b, statistic=lambda x: iqm(x), n_boot=257, rng=np.random.default_rng(123)
    )
    for key in ("stat", "pvalue", "pvalue_one_sided_greater", "effect", "ci_low", "ci_high"):
        assert fast[key] == ref[key], f"{key}: fast={fast[key]!r} != ref={ref[key]!r}"


def test_vectorized_fast_path_small_n_and_nonfinite_gate() -> None:
    """Fast-path edges: n < 4 rows use the plain row mean (iqm parity); non-finite input falls back.

    n=3 exercises the ``n < 4`` branch of ``_iqm_rows`` against the loop. A NaN in one arm must
    route BOTH calls through the reference loop (the finite gate), where iqm's per-resample finite
    filter applies — the two paths again agree exactly because they are the same code.
    """
    from src.inference.bootstrap import iqm, paired_seed_difference_test

    gen = np.random.default_rng(11)
    a3 = gen.normal(size=3)
    b3 = gen.normal(size=3)
    fast = paired_seed_difference_test(a3, b3, statistic=iqm, n_boot=64, rng=np.random.default_rng(5))
    ref = paired_seed_difference_test(
        a3, b3, statistic=lambda x: iqm(x), n_boot=64, rng=np.random.default_rng(5)
    )
    for key in ("pvalue", "effect", "ci_low", "ci_high"):
        assert fast[key] == ref[key]

    a_nan = gen.normal(size=8)
    a_nan[2] = float("nan")
    b8 = gen.normal(size=8)
    gated = paired_seed_difference_test(a_nan, b8, statistic=iqm, n_boot=64, rng=np.random.default_rng(9))
    loop = paired_seed_difference_test(
        a_nan, b8, statistic=lambda x: iqm(x), n_boot=64, rng=np.random.default_rng(9)
    )
    for key in ("pvalue", "effect", "ci_low", "ci_high"):
        assert gated[key] == loop[key]


def test_every_text_read_and_write_in_the_repo_pins_encoding_utf8() -> None:
    """Whole-repo structural lock on the encoding rule (deep review 2026-07-26, loop 96).

    `src/utils/config.py::load_config` documents the confirmed CRITICAL finding: `path.open()` uses the
    PLATFORM LOCALE codec, so on the cp1251 Windows box 30+ registered `preregistration.yaml`
    `model_suite` values came back with "—" mojibake'd to "вЂ”" -- i.e. the LOADED design of record
    differed from the file on disk, and differed BETWEEN machines, breaking the PROTOCOL layer of the
    reproducibility claim. Some sequences (U+2605) are undefined in cp1251 and raise outright, so the
    failure ranges from silent corruption to a hard crash.

    That was fixed at the ONE site where it bit. Every text read/write in the repo is in fact compliant
    (215/215 measured), but nothing STOPPED a new file from reintroducing it -- and the sibling
    whole-repo lock in `tests/test_sandbox.py` (the `except SandboxError` ordering rule) proved its worth
    on 2026-07-26 by catching exactly that in a brand-new untracked script. This is the same kind of
    structural lock, for the same kind of documented-critical rule.

    Binary I/O is exempt (no codec applies) and `os.open`/`os.fdopen` are file-descriptor APIs, not text
    APIs -- both exclusions are load-bearing: without them the scan reports four false positives
    (`Path.open("rb")` puts the mode in the FIRST positional arg, unlike builtin `open(path, mode)`).
    """
    import ast as _ast

    root = Path(__file__).resolve().parents[1]
    offenders: list[str] = []
    for path in sorted([*(root / "src").rglob("*.py"), *(root / "scripts").rglob("*.py")]):
        try:
            tree = _ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover - a syntactically broken file fails elsewhere
            continue
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Call):
                continue
            is_attr = isinstance(node.func, _ast.Attribute)
            name = node.func.attr if is_attr else getattr(node.func, "id", "")
            if name not in ("read_text", "write_text", "open"):
                continue
            if is_attr and isinstance(node.func.value, _ast.Name) and node.func.value.id == "os":
                continue  # os.open / os.fdopen take flags + an fd, not a text codec
            if "encoding" in {kw.arg for kw in node.keywords}:
                continue
            if name == "open":
                mode_idx = 0 if is_attr else 1  # Path.open(mode) vs builtin open(path, mode)
                mode = ""
                if len(node.args) > mode_idx and isinstance(node.args[mode_idx], _ast.Constant):
                    mode = str(node.args[mode_idx].value)
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, _ast.Constant):
                        mode = str(kw.value.value)
                if "b" in mode:
                    continue  # binary: no codec applies
            offenders.append(f"{path.relative_to(root).as_posix()}:{node.lineno} ({name})")

    assert not offenders, (
        "these TEXT reads/writes do not pin encoding='utf-8', so on a non-UTF-8 locale they decode "
        "through the platform codepage -- the confirmed mojibake failure that made the loaded design "
        f"of record differ between machines: {offenders}"
    )

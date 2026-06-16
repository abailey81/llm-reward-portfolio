"""Random search over the reward CODE space (LLM-free ablation; H4a).

Purpose
-------
A non-LLM control arm (FINAL_PLAN F.10, hypothesis H4a). It samples reward
functions from the SAME code space the LLM draws from, but uniformly at random
from a fixed grammar rather than via a model. Compared under the MATCHED budget,
it isolates how much of the LLM's value comes from *intelligent* proposals
versus mere search over a rich code space.

The code grammar
----------------
Every sampled reward is a linear combination of three risk-aware primitives, all
expressible against the reward contract (src/reward/contract.py):

    total = a * port_ret
            - b * variance(recent portfolio returns)
            - c * cvar_5pct(recent portfolio returns)

with random non-negative coefficients ``a, b, c`` drawn from a fixed grid. The
recent-return window is carried in ``reward_state`` so the reward is stateful and
hidden-global-free (audit B-4), exactly like the hand-designed canon. The
generated source is a Python ``def reward(...)`` string that passes the sandbox
AST gate and the reward contract.

Algorithm (FINAL_PLAN F.10, H4a)
--------------------------------
    1. For each of ``candidate_budget`` units, sample a coefficient triple and
       render the reward source from the grammar.
    2. Gate + validate the source via ``src.sandbox.executor`` (skip-and-log
       gate failures; they do NOT consume a budget unit — we keep sampling until
       the full matched budget of *valid* candidates has been evaluated).
    3. Score each validated reward with the injected ``fitness_fn`` (which maps a
       reward callable to a held-out score; deterministic in the tests).
    4. Track the best candidate; stop when the matched budget is exhausted.
    5. Return the best reward + an archive of every evaluated candidate.

Tests (tests/test_search.py)
----------------------------
    - returns a valid (gate-passing) best reward and consumes EXACTLY the matched
      budget;
    - every sampled source passes ``ast_gate``.
"""

from __future__ import annotations


from typing import Any, Callable, Optional

import numpy as np

from src.sandbox.executor import SandboxError, ast_gate, validate_once
from src.utils.config import DotDict

__all__ = ["random_search_over_code", "sample_reward_source", "code_grid"]

#: Coefficient grid the random sampler draws from. Non-negative so the variance
#: and CVaR terms always act as penalties (matching the LLM's risk-aware space).
_COEFF_GRID: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0)


def code_grid() -> tuple[float, ...]:
    """Return the fixed coefficient grid the random search draws from."""
    return _COEFF_GRID


def sample_reward_source(rng: np.random.Generator) -> str:
    """Render one reward source string from the fixed code grammar.

    Parameters
    ----------
    rng : numpy.random.Generator
        Source of randomness for the coefficient draws.

    Returns
    -------
    str
        A ``def reward(...)`` source string composing
        ``a*port_ret - b*variance - c*cvar`` with grid-sampled coefficients.
        The source obeys the reward contract and passes the sandbox AST gate.
    """
    a = float(rng.choice(_COEFF_GRID))
    b = float(rng.choice(_COEFF_GRID))
    c = float(rng.choice(_COEFF_GRID))
    # Guarantee at least the return term so the reward is never identically zero.
    if a == 0.0 and b == 0.0 and c == 0.0:
        a = 1.0
    return _render_source(a, b, c)


def _render_source(a: float, b: float, c: float) -> str:
    """Render the grammar's reward source for coefficients ``(a, b, c)``."""
    return (
        "def reward(weights, returns, prev_weights, port_ret, info):\n"
        "    state = info.get('reward_state')\n"
        "    prev = np.asarray(state, dtype=float) if state is not None "
        "else np.zeros(0, dtype=float)\n"
        "    history = np.append(prev, float(port_ret))\n"
        "    window = 50\n"
        "    if history.size > window:\n"
        "        history = history[-window:]\n"
        "    var = float(np.var(history)) if history.size >= 2 else 0.0\n"
        "    thresh = float(np.quantile(history, 0.05))\n"
        "    tail = history[history <= thresh]\n"
        "    cvar = -float(np.mean(tail)) if tail.size > 0 else 0.0\n"
        "    cvar = cvar if cvar > 0.0 else 0.0\n"
        f"    total = {a!r} * float(port_ret) - {b!r} * var - {c!r} * cvar\n"
        "    components = {\n"
        "        'return': float(port_ret),\n"
        "        'variance': var,\n"
        "        'cvar': cvar,\n"
        "    }\n"
        "    return float(total), components, history\n"
    )


def _default_fixture() -> tuple:
    """Small anonymized contract fixture for one-shot validation."""
    weights = np.array([0.4, 0.3, 0.3], dtype=float)
    returns = np.array([0.01, -0.02, 0.005], dtype=float)
    prev_weights = np.array([0.34, 0.33, 0.33], dtype=float)
    port_ret = 0.002
    info: dict[str, Any] = {}
    return (weights, returns, prev_weights, port_ret, info)


def _budget(cfg: Any) -> int:
    """Read the matched candidate budget from ``cfg``."""
    if cfg is None:
        raise ValueError("random_search_over_code requires a cfg with a budget")
    if isinstance(cfg, (DotDict, dict)):
        for key in ("matched_budget", "candidate_budget", "candidate_budget_total"):
            if key in cfg:
                return int(cfg[key])
        raise KeyError(
            "cfg must carry one of matched_budget / candidate_budget / "
            "candidate_budget_total"
        )
    return int(cfg)


def random_search_over_code(
    env_builder: Any,
    fitness_fn: Callable[[Any], float],
    cfg: Any,
    rng: Optional[np.random.Generator] = None,
) -> dict[str, Any]:
    """Randomly search the reward code space under the matched budget (H4a).

    Parameters
    ----------
    env_builder : Any
        Callable building a fresh training/eval environment. Forwarded to the
        injected ``fitness_fn`` when it accepts an environment; otherwise unused
        (the tests inject a closure that scores a reward directly).
    fitness_fn : Callable[[reward], float]
        Maps a validated reward callable to a held-out fitness score. In
        production this trains the fixed headline agent on the candidate reward
        and scores its validation returns; in tests it is a deterministic
        closure (no agent training required).
    cfg : DotDict or dict or int
        Carries the matched candidate budget (``matched_budget`` /
        ``candidate_budget`` / ``candidate_budget_total``), or the budget int
        directly.
    rng : numpy.random.Generator, optional
        Source of randomness; a fresh default generator is created when ``None``.

    Returns
    -------
    dict
        ``{"best_source", "best_reward", "best_score", "archive", "n_evaluated",
        "budget"}`` where ``archive`` is a list of per-candidate records
        ``{"source", "score"}`` for every evaluated (validated) candidate.

    Notes
    -----
    Gate/validation failures are skipped without consuming a budget unit, so the
    search always evaluates EXACTLY ``budget`` valid candidates. The grammar is
    constructed so every sampled source passes ``ast_gate`` (no imports, no
    dunders, no forbidden calls); the assertion in the loop is a defensive
    invariant, not an expected branch.
    """
    budget = _budget(cfg)
    if budget <= 0:
        raise ValueError(f"matched budget must be positive; got {budget}")
    if rng is None:
        rng = np.random.default_rng()

    fixture = _default_fixture()

    archive: list[dict[str, Any]] = []
    best_score = -np.inf
    best_source: Optional[str] = None
    best_reward: Optional[Any] = None

    # Defensive cap so a (hypothetical) pathological gate-failure streak cannot
    # loop forever; the grammar is gate-clean, so this is never reached.
    max_attempts = max(1000, budget * 100)
    attempts = 0

    while len(archive) < budget and attempts < max_attempts:
        attempts += 1
        source = sample_reward_source(rng)

        # Invariant: every sampled source passes the AST gate.
        assert ast_gate(source), "sampled source must pass ast_gate"

        try:
            reward = validate_once(source, fixture)
        except SandboxError:
            # Should not happen for the gate-clean grammar; skip without
            # consuming a budget unit if it ever does.
            continue

        score = float(fitness_fn(reward))
        archive.append({"source": source, "score": score})

        if score > best_score:
            best_score = score
            best_source = source
            best_reward = reward

    if len(archive) < budget:
        raise SandboxError(
            f"exhausted {attempts} attempts before reaching the matched budget "
            f"of {budget} valid candidates"
        )

    return {
        "best_source": best_source,
        "best_reward": best_reward,
        "best_score": best_score,
        "archive": archive,
        "n_evaluated": len(archive),
        "budget": budget,
    }

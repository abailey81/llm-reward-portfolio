"""Hand-designed reward canon for portfolio allocation agents.

Purpose
-------
This module holds the *fixed*, human-authored reward functions against which
LLM-discovered and search-discovered rewards are benchmarked (FINAL_PLAN F.6).
Every reward in this module obeys a single, audited contract so that any agent
training loop can swap rewards without code changes. The contract is the unit
of comparison for the entire dissertation: discovered rewards must satisfy the
same signature, so the baselines define the *shape* of all legal rewards.

Reward contract (audit B-4)
---------------------------
Every reward is a callable::

    def reward(weights, returns, prev_weights, port_ret, info)
        -> tuple[float, dict[str, float], object]

where:
    weights      : portfolio weights chosen for the current step (simplex).
    returns      : per-asset realized returns for the current step.
    prev_weights : portfolio weights held into the current step (for turnover).
    port_ret     : realized scalar portfolio return for the current step.
    info         : free-form dict of auxiliary signals (e.g. risk estimates).

returns a triple:
    total        : scalar reward fed to the RL algorithm.
    components   : dict mapping named sub-terms -> their scalar contribution
                   (for diagnostics, plotting, and audit trails).
    reward_state : opaque carry object threaded between consecutive calls.
                   STATELESS rewards return it unchanged (or ``None``);
                   STATEFUL rewards (``differential_sharpe``) mutate/return it.

The ``reward_state`` slot is what makes online/recursive rewards expressible
without hidden globals — it is the *only* legal place to keep memory between
steps, which keeps every reward replayable and auditable (audit B-4).

Reward canon (FINAL_PLAN F.6)
-----------------------------
    raw_return            : the bare portfolio return (myopic baseline).
    return_minus_variance : return penalized by a variance proxy.
    return_minus_cvar     : return penalized by tail risk (CVaR).
    differential_sharpe   : Moody-Saffell online incremental Sharpe ratio,
                            STATEFUL via ``reward_state``.

Tests (tests/test_baselines.py)
-------------------------------
    - test_rewards_obey_contract: each reward returns (total, components, state)
      under the contract.
    - test_differential_sharpe_sequence: differential_sharpe reproduces a
      hand-computed A/B/eta update sequence.
"""

from __future__ import annotations


from typing import Any

import numpy as np


def raw_return(
    weights: Any,
    returns: Any,
    prev_weights: Any,
    port_ret: float,
    info: dict[str, Any],
) -> tuple[float, dict[str, float], object]:
    """Bare portfolio return reward (myopic baseline).

    Algorithm sketch
    -----------------
    total = port_ret; components = {"raw_return": port_ret}; state unchanged.
    Stateless: reward_state is ``None`` and ignored.

    FINAL_PLAN F.6 (reward canon, raw return).
    """
    total = float(port_ret)
    components = {"raw_return": total}
    return total, components, info.get("reward_state")


def return_minus_variance(
    weights: Any,
    returns: Any,
    prev_weights: Any,
    port_ret: float,
    info: dict[str, Any],
) -> tuple[float, dict[str, float], object]:
    """Return penalized by a variance proxy.

    Algorithm sketch
    -----------------
    var = variance estimate from ``info`` (or weights' quadratic form against a
    covariance supplied in ``info``); total = port_ret - lambda * var.
    components = {"return": port_ret, "variance_penalty": -lambda * var}.

    The rolling window of realized portfolio returns is carried in
    ``reward_state`` (a list) so the variance is estimated online without hidden
    globals. ``info`` may supply ``lambda`` (risk-aversion) and ``window``.

    FINAL_PLAN F.6 (reward canon, mean-variance).
    """
    lam = float(info.get("lambda", 1.0))
    window = int(info.get("window", 20))

    state = info.get("reward_state")
    history: list[float] = list(state) if state is not None else []
    history.append(float(port_ret))
    if len(history) > window:
        history = history[-window:]

    # Population variance over the rolling window (0.0 until we have >= 2 obs).
    var = float(np.var(history)) if len(history) >= 2 else 0.0
    penalty = lam * var
    total = float(port_ret) - penalty
    components = {
        "return": float(port_ret),
        "variance": var,
        "variance_penalty": -penalty,
    }
    return total, components, history


def return_minus_cvar(
    weights: Any,
    returns: Any,
    prev_weights: Any,
    port_ret: float,
    info: dict[str, Any],
) -> tuple[float, dict[str, float], object]:
    """Return penalized by tail risk (Conditional Value-at-Risk).

    Algorithm sketch
    -----------------
    cvar = CVaR estimate at level alpha (from ``info`` history or a rolling
    window of portfolio returns); total = port_ret - lambda * cvar.
    components = {"return": port_ret, "cvar_penalty": -lambda * cvar}.

    The recent realized portfolio returns are carried in ``reward_state`` (a
    rolling list); CVaR penalizes the lower tail (mean of the worst ``alpha``
    fraction). ``info`` may supply ``lambda``, ``alpha`` (tail level), and
    ``window``.

    FINAL_PLAN F.6 (reward canon, mean-CVaR).
    """
    lam = float(info.get("lambda", 1.0))
    alpha = float(info.get("alpha", 0.05))
    window = int(info.get("window", 50))

    state = info.get("reward_state")
    history: list[float] = list(state) if state is not None else []
    history.append(float(port_ret))
    if len(history) > window:
        history = history[-window:]

    arr = np.asarray(history, dtype=float)
    # Lower-tail Value-at-Risk threshold; CVaR = mean of returns at or below it.
    var_threshold = float(np.quantile(arr, alpha))
    tail = arr[arr <= var_threshold]
    cvar_loss = -float(tail.mean()) if tail.size > 0 else 0.0
    # Only penalize genuine downside (positive expected loss).
    tail_penalty = lam * max(cvar_loss, 0.0)
    total = float(port_ret) - tail_penalty
    components = {
        "return": float(port_ret),
        "cvar": cvar_loss,
        "cvar_penalty": -tail_penalty,
    }
    return total, components, history


def differential_sharpe(
    weights: Any,
    returns: Any,
    prev_weights: Any,
    port_ret: float,
    info: dict[str, Any],
) -> tuple[float, dict[str, float], object]:
    """Moody-Saffell online incremental (differential) Sharpe ratio.

    This reward is STATEFUL: it accumulates exponential moving averages of the
    first and second moments of the portfolio return in ``reward_state`` and
    emits the *marginal* contribution of the current return to the Sharpe ratio
    (audit B-4). It is the canonical example of a reward that legally uses the
    reward_state carry slot instead of hidden globals.

    Algorithm sketch (Moody & Saffell, 1998)
    -----------------------------------------
    State carries A (EMA of return) and B (EMA of squared return), with decay
    eta. On each step with return R_t:

        dA = R_t - A_{t-1}
        dB = R_t^2 - B_{t-1}
        D_t = (B_{t-1} * dA - 0.5 * A_{t-1} * dB)
              / (B_{t-1} - A_{t-1}^2) ** 1.5      # differential Sharpe
        A_t = A_{t-1} + eta * dA
        B_t = B_{t-1} + eta * dB

    total = D_t; components = {"dsr": D_t, "A": A_t, "B": B_t};
    reward_state = updated (A_t, B_t, eta) carry.

    Worked example
    --------------
    Let eta = 0.1, and initialize A_0 = 0, B_0 = 0 (warm-up returns D = 0 / a
    sentinel until B - A^2 > 0). Feed R_1 = 0.02 then R_2 = -0.01:

      Step 1 (R_1 = 0.02):
        dA = 0.02 - 0 = 0.02
        dB = 0.0004 - 0 = 0.0004
        denom = (0 - 0) ** 1.5 = 0  -> warm-up: D_1 = 0 (guarded).
        A_1 = 0 + 0.1 * 0.02 = 0.002
        B_1 = 0 + 0.1 * 0.0004 = 0.00004

      Step 2 (R_2 = -0.01):
        dA = -0.01 - 0.002 = -0.012
        dB = 0.0001 - 0.00004 = 0.00006
        denom = (B_1 - A_1**2) ** 1.5
              = (0.00004 - 0.000004) ** 1.5
              = (0.000036) ** 1.5
        D_2 = (B_1 * dA - 0.5 * A_1 * dB) / denom
            = (0.00004 * -0.012 - 0.5 * 0.002 * 0.00006) / (0.000036 ** 1.5)
        A_2 = 0.002 + 0.1 * -0.012 = 0.0008
        B_2 = 0.00004 + 0.1 * 0.00006 = 0.000046

    The test in tests/test_baselines.py replays exactly this A/B/eta sequence.

    FINAL_PLAN F.6 (reward canon, differential Sharpe; audit B-4 statefulness).
    """
    r = float(port_ret)

    state = info.get("reward_state")
    if state is None:
        eta = float(info.get("eta", 0.1))
        a_prev, b_prev = 0.0, 0.0
    else:
        a_prev = float(state["A"])
        b_prev = float(state["B"])
        eta = float(state["eta"])

    d_a = r - a_prev
    d_b = r * r - b_prev

    denom_base = b_prev - a_prev * a_prev
    # Warm-up guard: with A_0 = B_0 = 0 (or any degenerate variance) the
    # differential Sharpe is undefined; emit 0.0 until variance is positive.
    if denom_base > 0.0:
        dsr = (b_prev * d_a - 0.5 * a_prev * d_b) / (denom_base**1.5)
    else:
        dsr = 0.0

    a_new = a_prev + eta * d_a
    b_new = b_prev + eta * d_b

    total = float(dsr)
    components = {"dsr": total, "A": float(a_new), "B": float(b_new)}
    new_state = {"A": float(a_new), "B": float(b_new), "eta": eta}
    return total, components, new_state

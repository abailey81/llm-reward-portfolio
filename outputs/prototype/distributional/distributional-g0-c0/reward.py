def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore / initialise state ────────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],          # rolling window of port_ret values
            "peak":           0.0,         # running peak for drawdown
            "cum_ret":        0.0,         # cumulative log-approx return
            "step":           0,
        }

    state["step"] += 1
    step = state["step"]

    # ── Rolling window of returns (for vol & CVaR) ────────────────────────────
    WINDOW = 60
    rw = state["returns_window"]
    rw.append(float(port_ret))
    if len(rw) > WINDOW:
        rw.pop(0)
    arr = np.array(rw, dtype=np.float64)

    # ── 1. Sharpe-like component (rolling) ────────────────────────────────────
    if len(arr) >= 2:
        mu   = np.mean(arr)
        sigma = np.std(arr, ddof=1) + 1e-8
        rolling_sharpe = mu / sigma  # per-step, not annualised
    else:
        rolling_sharpe = float(port_ret)

    # ── 2. Drawdown penalty ───────────────────────────────────────────────────
    state["cum_ret"] += float(port_ret)           # approximate cumulative return
    cum = state["cum_ret"]
    if cum > state["peak"]:
        state["peak"] = cum
    drawdown = state["peak"] - cum                # >= 0
    dd_penalty = drawdown                         # penalise proportionally

    # ── 3. CVaR / tail-loss component (5 % tail of rolling window) ───────────
    if len(arr) >= 10:
        cvar_q    = 0.05
        n_tail    = max(1, int(np.floor(len(arr) * cvar_q)))
        sorted_r  = np.sort(arr)                  # ascending
        tail_mean = np.mean(sorted_r[:n_tail])    # mean of worst n_tail returns
        cvar_penalty = -tail_mean                 # positive when tail is bad
    else:
        cvar_penalty = max(0.0, -float(port_ret))

    # ── 4. Turnover cost signal (redundant but explicit) ─────────────────────
    risky_w      = weights[:30]
    risky_pw     = prev_weights[:30]
    turnover     = 0.5 * float(np.sum(np.abs(risky_w - risky_pw)))
    cost_penalty = 0.001 * turnover               # 10 bps scale

    # ── 5. Concentration penalty (encourage diversification) ─────────────────
    hhi = float(np.sum(risky_w ** 2))             # Herfindahl index [1/30, 1]
    concentration_penalty = hhi                   # small = more diversified

    # ── Combine ───────────────────────────────────────────────────────────────
    # Weights chosen to balance scale of each component
    w_sharpe  =  1.00
    w_dd      =  1.50
    w_cvar    =  1.50
    w_cost    =  0.50
    w_conc    =  0.20

    total = (
        w_sharpe * rolling_sharpe
        - w_dd   * dd_penalty
        - w_cvar * cvar_penalty
        - w_cost * cost_penalty
        - w_conc * concentration_penalty
    )

    components = {
        "rolling_sharpe":        rolling_sharpe,
        "port_ret":              float(port_ret),
        "dd_penalty":            dd_penalty,
        "cvar_penalty":          cvar_penalty,
        "cost_penalty":          cost_penalty,
        "concentration_penalty": concentration_penalty,
        "total":                 float(total),
    }

    state["returns_window"] = rw
    return float(total), components, state
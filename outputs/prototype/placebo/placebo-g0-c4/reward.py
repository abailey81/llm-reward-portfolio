def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore / initialise state ──────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],   # rolling window of port_ret values
            "peak":           0.0,  # for drawdown tracking (cumulative wealth index)
            "cum_wealth":     1.0,  # cumulative wealth index
            "ema_ret":        None, # exponential moving average of returns
            "ema_sq":         None, # EMA of squared returns (for vol estimate)
        }

    # ── 2. Update cumulative wealth & drawdown ─────────────────────────────
    state["cum_wealth"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_wealth"])
    drawdown = (state["peak"] - state["cum_wealth"]) / (state["peak"] + 1e-8)

    # ── 3. Update rolling returns window (last 60 steps) ──────────────────
    window = state["returns_window"]
    window.append(float(port_ret))
    if len(window) > 60:
        window.pop(0)
    state["returns_window"] = window

    arr = np.array(window, dtype=np.float64)
    n   = len(arr)

    # ── 4. Rolling volatility (EMA-based, fast) ────────────────────────────
    alpha = 2.0 / (21.0 + 1.0)          # ~20-step half-life
    if state["ema_ret"] is None:
        state["ema_ret"] = port_ret
        state["ema_sq"]  = port_ret ** 2
    else:
        state["ema_ret"] = alpha * port_ret + (1 - alpha) * state["ema_ret"]
        state["ema_sq"]  = alpha * port_ret**2 + (1 - alpha) * state["ema_sq"]

    ema_var = max(state["ema_sq"] - state["ema_ret"]**2, 1e-10)
    ema_vol = np.sqrt(ema_var)

    # ── 5. CVaR / tail-loss (5 % tail over rolling window) ────────────────
    if n >= 10:
        tail_cutoff = max(1, int(np.floor(0.05 * n)))
        sorted_rets = np.sort(arr)                     # ascending
        cvar_5      = float(np.mean(sorted_rets[:tail_cutoff]))   # negative = bad
    else:
        cvar_5 = float(port_ret)

    # ── 6. Rolling Sharpe (annualised, daily rf ≈ 0) ─────────────────────
    if n >= 5:
        roll_mean = float(np.mean(arr))
        roll_std  = float(np.std(arr, ddof=1)) + 1e-8
        sharpe    = roll_mean / roll_std * np.sqrt(252)
    else:
        sharpe = 0.0

    # ── 7. Turnover cost penalty (extra signal beyond port_ret deduction) ──
    turnover = float(np.sum(np.abs(weights - prev_weights))) * 0.5
    cost_penalty = turnover * 0.001      # 10 bps per side ≈ already in port_ret;
                                          # small additional penalty to discourage churn

    # ── 8. Concentration penalty (encourage diversification) ──────────────
    risky_w = weights[:30]
    herfindahl = float(np.sum(risky_w ** 2))           # 1/30 = fully diversified
    concentration_penalty = max(0.0, herfindahl - 1.0 / 30.0)

    # ── 9. Assemble total reward ───────────────────────────────────────────
    # Weights chosen so each component is roughly O(1e-3) – O(1e-2).
    w_ret         =  1.00
    w_sharpe      =  0.10
    w_cvar        =  0.30
    w_dd          = -0.50
    w_cost        = -1.00
    w_conc        = -0.05

    r_return      = w_ret    * float(port_ret)
    r_sharpe      = w_sharpe * np.tanh(sharpe / 3.0) * 1e-3   # bounded contribution
    r_cvar        = w_cvar   * cvar_5                          # negative cvar5 → penalty
    r_dd          = w_dd     * drawdown
    r_cost        = w_cost   * cost_penalty
    r_conc        = w_conc   * concentration_penalty

    total = r_return + r_sharpe + r_cvar + r_dd + r_cost + r_conc

    components = {
        "port_ret":            float(port_ret),
        "r_return":            r_return,
        "r_sharpe":            r_sharpe,
        "rolling_sharpe":      sharpe,
        "r_cvar":              r_cvar,
        "cvar_5pct":           cvar_5,
        "r_drawdown":          r_dd,
        "drawdown":            drawdown,
        "r_cost":              r_cost,
        "turnover":            turnover,
        "r_concentration":     r_conc,
        "herfindahl":          herfindahl,
        "ema_vol":             float(ema_vol),
    }

    return float(total), components, state
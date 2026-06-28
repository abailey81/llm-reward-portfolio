def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Recover / initialise state ──────────────────────────────────────────
    state = info.get("reward_state")
    if state is None:
        state = {
            "ret_history": [],          # rolling window of port_ret values
            "peak":        1.0,         # for drawdown tracking
            "cum_value":   1.0,         # cumulative portfolio value
            "ema_ret":     0.0,         # exponential moving average of return
            "ema_sq":      0.0,         # EMA of squared return (for variance)
            "step":        0,
        }

    state["step"] += 1
    step = state["step"]

    # ── Update cumulative value & drawdown ──────────────────────────────────
    state["cum_value"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_value"])
    drawdown = (state["peak"] - state["cum_value"]) / (state["peak"] + 1e-8)

    # ── Rolling return history (window = 60 steps) ──────────────────────────
    WINDOW = 60
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > WINDOW:
        state["ret_history"].pop(0)

    hist = np.array(state["ret_history"], dtype=np.float64)

    # ── Online EMA Sharpe ───────────────────────────────────────────────────
    alpha = 0.05  # smoothing factor (~20-step half-life)
    state["ema_ret"] = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    state["ema_sq"]  = alpha * port_ret**2 + (1 - alpha) * state["ema_sq"]
    ema_var = max(state["ema_sq"] - state["ema_ret"]**2, 1e-10)
    ema_vol = np.sqrt(ema_var)
    ema_sharpe = state["ema_ret"] / ema_vol   # dimensionless, no annualisation

    # ── CVaR tail penalty (5% tail of rolling window) ──────────────────────
    if len(hist) >= 10:
        tail_cutoff = int(max(1, 0.05 * len(hist)))
        sorted_hist = np.sort(hist)
        cvar_loss = -np.mean(sorted_hist[:tail_cutoff])   # positive = bad
    else:
        cvar_loss = max(-port_ret, 0.0)

    # ── Turnover penalty ────────────────────────────────────────────────────
    turnover = np.sum(np.abs(weights - prev_weights))

    # ── Drawdown penalty ────────────────────────────────────────────────────
    dd_penalty = drawdown ** 2   # quadratic to punish deep drawdowns more

    # ── Concentration penalty (encourage diversification) ──────────────────
    # Penalise Herfindahl index of risky weights (exclude cash = last element)
    risky_w = weights[:-1] if len(weights) > 1 else weights
    herfindahl = np.sum(risky_w ** 2)   # 1/N when equal, 1 when concentrated

    # ── Combine ─────────────────────────────────────────────────────────────
    # Core signal: EMA Sharpe (risk-adjusted return)
    # Subtract penalties for tail risk, drawdown, turnover, concentration
    w_sharpe      = 1.0
    w_cvar        = 2.0
    w_dd          = 1.5
    w_turnover    = 0.5
    w_herfindahl  = 0.3

    total = (
        w_sharpe     * ema_sharpe
        - w_cvar     * cvar_loss
        - w_dd       * dd_penalty
        - w_turnover * turnover
        - w_herfindahl * herfindahl
    )

    components = {
        "ema_sharpe":    float(ema_sharpe),
        "cvar_loss":     float(cvar_loss),
        "dd_penalty":    float(dd_penalty),
        "turnover":      float(turnover),
        "herfindahl":    float(herfindahl),
        "port_ret":      float(port_ret),
        "drawdown":      float(drawdown),
    }

    return float(total), components, state
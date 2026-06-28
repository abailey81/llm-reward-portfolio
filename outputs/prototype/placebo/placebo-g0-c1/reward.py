def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ------------------------------------------------------------------ #
    # 0. Restore / initialise reward state
    # ------------------------------------------------------------------ #
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history":    [],          # rolling window of port_ret values
            "peak":           0.0,         # running peak of cumulative wealth
            "cum_wealth":     1.0,         # cumulative wealth index
            "ema_ret":        0.0,         # exponential moving average of returns
            "ema_sq":         0.0,         # EMA of squared returns (for vol)
            "step":           0,
        }

    # ------------------------------------------------------------------ #
    # 1. Update cumulative state
    # ------------------------------------------------------------------ #
    state["step"] += 1
    t = state["step"]

    # Rolling history (keep last 60 steps)
    WINDOW = 60
    state["ret_history"].append(float(port_ret))
    if len(state["ret_history"]) > WINDOW:
        state["ret_history"].pop(0)

    # Cumulative wealth & drawdown
    state["cum_wealth"] *= (1.0 + float(port_ret))
    if state["cum_wealth"] > state["peak"]:
        state["peak"] = state["cum_wealth"]
    drawdown = (state["peak"] - state["cum_wealth"]) / (state["peak"] + 1e-8)

    # EMA parameters
    alpha = 2.0 / (WINDOW + 1)          # ~60-step EMA
    state["ema_ret"] = alpha * float(port_ret) + (1 - alpha) * state["ema_ret"]
    state["ema_sq"]  = alpha * float(port_ret)**2 + (1 - alpha) * state["ema_sq"]

    # ------------------------------------------------------------------ #
    # 2. Risk metrics from rolling history
    # ------------------------------------------------------------------ #
    hist = np.array(state["ret_history"], dtype=np.float64)
    n    = len(hist)

    # Rolling volatility
    if n >= 5:
        roll_vol = float(np.std(hist, ddof=1)) + 1e-8
    else:
        roll_vol = 1e-3

    # Online (EMA) volatility
    ema_var  = max(state["ema_sq"] - state["ema_ret"]**2, 1e-10)
    ema_vol  = float(np.sqrt(ema_var)) + 1e-8

    # Blended volatility estimate
    vol = 0.5 * roll_vol + 0.5 * ema_vol

    # Rolling Sharpe (annualised proxy using daily scale)
    ANNUAL = 252.0
    sharpe_roll = float(np.mean(hist)) / (roll_vol + 1e-8) * np.sqrt(ANNUAL) if n >= 5 else 0.0

    # CVaR / Expected Shortfall at 10% tail (worst 10% outcomes)
    if n >= 10:
        cutoff    = max(1, int(np.floor(0.10 * n)))
        tail_rets = np.sort(hist)[:cutoff]
        cvar      = float(np.mean(tail_rets))          # negative number → bad
    else:
        cvar = float(port_ret)

    # ------------------------------------------------------------------ #
    # 3. Turnover / transaction-cost penalty
    # ------------------------------------------------------------------ #
    turnover = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    # Additional penalty to discourage excessive churn (beyond what cost already penalises)
    turnover_penalty = 10.0 * turnover          # 10× multiplier

    # ------------------------------------------------------------------ #
    # 4. Concentration penalty (encourage diversification)
    # ------------------------------------------------------------------ #
    risky_w = weights[:30]
    herfindahl = float(np.sum(risky_w**2))      # 1/30 ≈ 0.033 when perfectly spread
    concentration_penalty = 5.0 * max(0.0, herfindahl - 1.0 / 30.0)

    # ------------------------------------------------------------------ #
    # 5. Component rewards
    # ------------------------------------------------------------------ #
    # (a) Sharpe-like: normalise raw return by vol
    sharpe_step = float(port_ret) / vol         # single-step Sharpe contribution

    # (b) Drawdown penalty (convex in drawdown size)
    dd_penalty = 20.0 * drawdown**2

    # (c) CVaR penalty: penalise when current return is in the tail
    cvar_penalty = 0.0
    if n >= 10:
        cvar_threshold = float(np.percentile(hist, 10))
        if float(port_ret) <= cvar_threshold:
            cvar_penalty = 5.0 * abs(float(port_ret) - cvar_threshold)

    # (d) Mild rolling-Sharpe bonus (stabilises long-run direction)
    sharpe_bonus = 0.05 * np.clip(sharpe_roll, -3.0, 3.0)

    # ------------------------------------------------------------------ #
    # 6. Total reward
    # ------------------------------------------------------------------ #
    total = (
          sharpe_step
        - dd_penalty
        - cvar_penalty
        - turnover_penalty
        - concentration_penalty
        + sharpe_bonus
    )

    components = {
        "port_ret":             float(port_ret),
        "sharpe_step":          sharpe_step,
        "vol":                  vol,
        "drawdown":             drawdown,
        "dd_penalty":           -dd_penalty,
        "cvar":                 cvar,
        "cvar_penalty":         -cvar_penalty,
        "turnover":             turnover,
        "turnover_penalty":     -turnover_penalty,
        "concentration":        herfindahl,
        "concentration_penalty":-concentration_penalty,
        "sharpe_roll":          sharpe_roll,
        "sharpe_bonus":         sharpe_bonus,
        "total":                float(total),
    }

    return float(total), components, state
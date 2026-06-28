def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore or initialise state ───────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history":    [],          # rolling window of port_ret values
            "peak":           0.0,         # running peak for drawdown
            "cum_ret":        0.0,         # cumulative log-approximate return
            "ema_ret":        0.0,         # EMA of returns  (for Sharpe approx)
            "ema_sq":         0.0,         # EMA of squared returns
            "step":           0,
        }

    # ── 2. Update state ───────────────────────────────────────────────────────
    step = state["step"] + 1
    pr   = float(port_ret)

    # Rolling history (keep last 126 steps ≈ 6 months of trading days)
    WINDOW = 126
    hist = state["ret_history"] + [pr]
    if len(hist) > WINDOW:
        hist = hist[-WINDOW:]

    # Cumulative return & peak (for drawdown)
    cum_ret  = state["cum_ret"] + pr          # simple sum of log-like returns
    peak     = max(state["peak"], cum_ret)
    drawdown = peak - cum_ret                 # ≥ 0, bigger = worse

    # EMA Sharpe (λ = 0.94 ≈ 20-day half-life)
    lam      = 0.94
    ema_ret  = lam * state["ema_ret"]  + (1 - lam) * pr
    ema_sq   = lam * state["ema_sq"]   + (1 - lam) * pr ** 2
    ema_var  = max(ema_sq - ema_ret ** 2, 1e-10)
    ema_std  = np.sqrt(ema_var)

    # ── 3. Risk-adjusted return component ────────────────────────────────────
    # Annualised Sharpe-like signal (daily std → annualised via sqrt(252))
    sharpe_daily = pr / (ema_std + 1e-8)          # signed, dimensionless

    # ── 4. CVaR / tail-loss component (5 % tail over rolling window) ─────────
    if len(hist) >= 10:
        arr      = np.array(hist)
        cutoff   = np.percentile(arr, 5)           # 5th-percentile return
        tail     = arr[arr <= cutoff]
        cvar_5   = float(np.mean(tail))            # negative = bad
    else:
        cvar_5   = 0.0

    # ── 5. Drawdown penalty ───────────────────────────────────────────────────
    # Penalise proportionally to drawdown depth
    dd_penalty = -drawdown                         # negative contribution

    # ── 6. Turnover cost signal ───────────────────────────────────────────────
    # Already embedded in port_ret via cost, but we add explicit signal
    # to discourage excessive churn beyond what the cost captures.
    turnover      = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    turnover_pen  = -turnover * 0.5               # extra soft penalty (× 50 bps)

    # ── 7. Concentration penalty (encourage diversification) ─────────────────
    risky_w   = weights[:30]
    hhi       = float(np.sum(risky_w ** 2))       # Herfindahl index ∈ [1/30, 1]
    conc_pen  = -(hhi - 1.0 / 30.0)              # penalise excess concentration

    # ── 8. Combine into total reward ──────────────────────────────────────────
    # Weights chosen to keep total on the same scale as port_ret (≈ daily pct)
    w_sharpe  = 0.40
    w_cvar    = 0.25
    w_dd      = 0.15
    w_turn    = 0.10
    w_conc    = 0.10

    total = (
          w_sharpe * sharpe_daily * ema_std   # reconstruct pr-like scale
        + w_cvar   * cvar_5
        + w_dd     * dd_penalty
        + w_turn   * turnover_pen
        + w_conc   * conc_pen
    )

    # Safety: keep total numerically sane
    total = float(np.clip(total, -1.0, 1.0))

    # ── 9. Update state dict ──────────────────────────────────────────────────
    state["ret_history"] = hist
    state["peak"]        = peak
    state["cum_ret"]     = cum_ret
    state["ema_ret"]     = ema_ret
    state["ema_sq"]      = ema_sq
    state["step"]        = step

    # ── 10. Components for logging ────────────────────────────────────────────
    components = {
        "port_ret":       pr,
        "sharpe_contrib": float(w_sharpe * sharpe_daily * ema_std),
        "cvar_contrib":   float(w_cvar   * cvar_5),
        "dd_contrib":     float(w_dd     * dd_penalty),
        "turnover_contrib": float(w_turn * turnover_pen),
        "conc_contrib":   float(w_conc   * conc_pen),
        "drawdown":       drawdown,
        "cvar_5pct":      cvar_5,
        "ema_std":        float(ema_std),
        "turnover":       turnover,
        "hhi":            hhi,
    }

    return total, components, state
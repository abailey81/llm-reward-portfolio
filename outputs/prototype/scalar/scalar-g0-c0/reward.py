def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore or initialise state ───────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history":    [],          # rolling window of port_ret values
            "peak":           0.0,         # peak cumulative wealth (log)
            "cum_log_ret":    0.0,         # running cumulative log return
            "step":           0,
        }

    step            = state["step"]
    ret_history     = state["ret_history"]
    peak            = state["peak"]
    cum_log_ret     = state["cum_log_ret"]

    # ── Rolling window length ─────────────────────────────────────────────────
    WINDOW = 60          # ~3 months of daily data

    # ── 1. Update cumulative log-return & drawdown ────────────────────────────
    log_ret      = np.log1p(np.clip(port_ret, -0.999, None))
    cum_log_ret  = cum_log_ret + log_ret
    peak         = max(peak, cum_log_ret)
    drawdown     = peak - cum_log_ret          # non-negative, in log-return units

    # ── 2. Maintain rolling history ───────────────────────────────────────────
    ret_history.append(float(port_ret))
    if len(ret_history) > WINDOW:
        ret_history.pop(0)

    hist = np.array(ret_history, dtype=np.float64)

    # ── 3. Rolling volatility (annualised daily σ) ────────────────────────────
    if len(hist) >= 5:
        roll_vol = float(np.std(hist, ddof=1)) * np.sqrt(252)
    else:
        roll_vol = 1e-4      # tiny default until we have data

    roll_vol = max(roll_vol, 1e-6)   # numerical guard

    # ── 4. Rolling Sharpe (annualised) ────────────────────────────────────────
    if len(hist) >= 5:
        roll_mean  = float(np.mean(hist)) * 252
        sharpe     = roll_mean / roll_vol
    else:
        sharpe = 0.0

    # ── 5. CVaR / tail-risk penalty (5th-percentile CVaR of rolling window) ───
    if len(hist) >= 10:
        var_5   = float(np.percentile(hist, 5))
        tail    = hist[hist <= var_5]
        cvar_5  = float(np.mean(tail)) if len(tail) > 0 else var_5
    else:
        cvar_5  = 0.0          # not enough data yet

    # ── 6. Turnover cost signal (already baked into port_ret, but penalise
    #        large turnover explicitly to discourage churn)  ───────────────────
    turnover        = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 10.0 * turnover   # scale so it matters vs Sharpe term

    # ── 7. Drawdown penalty ───────────────────────────────────────────────────
    dd_penalty = 2.0 * drawdown          # proportional to depth in log-ret units

    # ── 8. Concentration penalty (encourage diversification) ─────────────────
    risky_w       = weights[:30]
    hhi           = float(np.sum(risky_w ** 2))     # Herfindahl index ∈ [1/30, 1]
    conc_penalty  = 2.0 * hhi                        # penalise concentration

    # ── 9. Tail penalty (CVaR is negative when bad) ───────────────────────────
    # We want to penalise deeply negative tails
    cvar_penalty  = -5.0 * min(cvar_5, 0.0)         # positive penalty when CVaR < 0

    # ── 10. Combine ───────────────────────────────────────────────────────────
    # Core signal: risk-adjusted return (Sharpe normalised to per-step scale)
    core   = sharpe / 252.0      # bring annualised Sharpe to ~daily magnitude

    total  = (core
              - dd_penalty
              - cvar_penalty
              - turnover_penalty
              - conc_penalty)

    # ── 11. Save state ────────────────────────────────────────────────────────
    new_state = {
        "ret_history":   ret_history,
        "peak":          float(peak),
        "cum_log_ret":   float(cum_log_ret),
        "step":          step + 1,
    }

    components = {
        "port_ret":         float(port_ret),
        "sharpe_daily":     float(core),
        "roll_vol":         float(roll_vol),
        "cvar_5":           float(cvar_5),
        "drawdown":         float(drawdown),
        "turnover_pen":     float(turnover_penalty),
        "conc_pen":         float(conc_penalty),
        "cvar_pen":         float(cvar_penalty),
        "dd_pen":           float(dd_penalty),
        "total":            float(total),
    }

    return float(total), components, new_state
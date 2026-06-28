def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore / initialise state ────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history":    [],        # list of port_ret values
            "peak":           0.0,       # running peak of cumulative wealth
            "cum_wealth":     0.0,       # log-cumulative wealth proxy
            "ema_ret":        0.0,       # EMA of returns  (for Sharpe)
            "ema_sq":         0.0,       # EMA of squared returns
            "ema_neg":        0.0,       # EMA of negative returns  (for CVaR)
            "ema_neg_sq":     0.0,
            "step":           0,
        }

    step        = state["step"]
    ret_history = state["ret_history"]
    peak        = state["peak"]
    cum_wealth  = state["cum_wealth"]
    ema_ret     = state["ema_ret"]
    ema_sq      = state["ema_sq"]
    ema_neg     = state["ema_neg"]
    ema_neg_sq  = state["ema_neg_sq"]

    r = float(port_ret)

    # ── 2. Update running statistics (EMA, α chosen for ~60-step half-life) ──
    alpha = 0.033          # ≈ 2/(60+1)
    if step == 0:
        ema_ret    = r
        ema_sq     = r * r
        ema_neg    = min(r, 0.0)
        ema_neg_sq = min(r, 0.0) ** 2
    else:
        ema_ret    = alpha * r       + (1 - alpha) * ema_ret
        ema_sq     = alpha * r**2    + (1 - alpha) * ema_sq
        neg_r      = min(r, 0.0)
        ema_neg    = alpha * neg_r   + (1 - alpha) * ema_neg
        ema_neg_sq = alpha * neg_r**2 + (1 - alpha) * ema_neg_sq

    # ── 3. Keep a short rolling window for exact CVaR ─────────────────────────
    ret_history.append(r)
    window = 120
    if len(ret_history) > window:
        ret_history.pop(0)

    # ── 4. Drawdown ──────────────────────────────────────────────────────────
    cum_wealth  += r                     # simple sum (≈ log-wealth for small r)
    if cum_wealth > peak:
        peak = cum_wealth
    drawdown = peak - cum_wealth         # ≥ 0

    # ── 5. Rolling Sharpe (EMA-based) ─────────────────────────────────────────
    variance = max(ema_sq - ema_ret**2, 1e-8)
    vol      = np.sqrt(variance)
    sharpe   = ema_ret / vol             # de-meaned Sharpe proxy

    # ── 6. CVaR at 5 % from rolling window ────────────────────────────────────
    if len(ret_history) >= 20:
        arr        = np.array(ret_history)
        cutoff     = np.percentile(arr, 5)          # 5th-percentile (VaR)
        tail_rets  = arr[arr <= cutoff]
        cvar5      = float(np.mean(tail_rets)) if len(tail_rets) > 0 else cutoff
    else:
        # fall back to EMA-based semi-deviation
        semi_dev = np.sqrt(max(ema_neg_sq - ema_neg**2, 1e-8))
        cvar5    = ema_neg - semi_dev    # approximate left-tail mean

    # ── 7. Turnover cost proxy (raw turnover for transparency) ────────────────
    raw_turnover = float(np.sum(np.abs(weights - prev_weights)))

    # ── 8. Concentration penalty (Herfindahl on risky weights) ────────────────
    risky_w = weights[:30]
    hhi     = float(np.sum(risky_w**2))   # 1/30 (uniform) … 1 (all in one)

    # ── 9. Combine into a single scalar ──────────────────────────────────────
    # All terms are in "return-like" units or dimensionless ratios.
    #
    #  +  Sharpe-scaled return     — primary risk-adjusted signal
    #  +  raw return               — make sure agent cares about actual P&L
    #  -  drawdown penalty         — penalise underwater periods
    #  -  CVaR penalty             — penalise left-tail outcomes
    #  -  turnover penalty         — keep costs down (already in port_ret, but extra nudge)
    #  -  concentration penalty    — encourage diversification

    w_sharpe   = 0.40
    w_ret      = 0.25
    w_dd       = 0.15
    w_cvar     = 0.15
    w_to       = 0.025
    w_hhi      = 0.025

    total = (
        w_sharpe * sharpe
      + w_ret    * r
      - w_dd     * drawdown
      - w_cvar   * abs(cvar5)            # cvar5 ≤ 0, so abs gives a penalty
      - w_to     * raw_turnover
      - w_hhi    * hhi
    )

    # ── 10. Save state ────────────────────────────────────────────────────────
    state.update({
        "ret_history": ret_history,
        "peak":        peak,
        "cum_wealth":  cum_wealth,
        "ema_ret":     ema_ret,
        "ema_sq":      ema_sq,
        "ema_neg":     ema_neg,
        "ema_neg_sq":  ema_neg_sq,
        "step":        step + 1,
    })

    components = {
        "port_ret":    r,
        "sharpe_ema":  sharpe,
        "drawdown":    drawdown,
        "cvar5":       cvar5,
        "turnover":    raw_turnover,
        "hhi":         hhi,
        "total":       total,
    }

    return float(total), components, state
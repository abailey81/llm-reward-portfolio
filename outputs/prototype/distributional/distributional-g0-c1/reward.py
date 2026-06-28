def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore / initialise state ────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history":    [],          # rolling window of port_ret values
            "peak":           0.0,         # running peak for drawdown
            "cum_ret":        0.0,         # cumulative log-approx equity
        }

    ret_history: list = state["ret_history"]
    peak:        float = state["peak"]
    cum_ret:     float = state["cum_ret"]

    # ── 2. Update history ────────────────────────────────────────────────────
    ret_history.append(float(port_ret))
    WINDOW = 60                            # rolling window length
    if len(ret_history) > WINDOW:
        ret_history.pop(0)

    arr = np.array(ret_history, dtype=np.float64)
    n   = len(arr)

    # ── 3. Rolling volatility (annualised) ───────────────────────────────────
    if n >= 2:
        roll_vol = float(np.std(arr, ddof=1)) * np.sqrt(252)
    else:
        roll_vol = 1e-4
    roll_vol = max(roll_vol, 1e-4)

    # ── 4. Rolling CVaR / Expected Shortfall (5 % tail) ─────────────────────
    if n >= 10:
        cutoff   = max(1, int(np.floor(0.05 * n)))
        sorted_r = np.sort(arr)
        cvar     = float(np.mean(sorted_r[:cutoff]))   # negative = bad
    else:
        cvar = float(port_ret)

    # ── 5. Drawdown ──────────────────────────────────────────────────────────
    cum_ret  += float(port_ret)
    peak      = max(peak, cum_ret)
    drawdown  = peak - cum_ret             # >= 0; larger = deeper drawdown

    # ── 6. Turnover cost penalty ─────────────────────────────────────────────
    # Already baked into port_ret, but we add a small extra signal to
    # discourage churn beyond what the environment charges.
    turnover      = float(np.sum(np.abs(weights - prev_weights))) * 0.5
    turnover_pen  = 0.10 * turnover        # 10× basis-point extra penalty

    # ── 7. Concentration penalty (encourage diversification) ─────────────────
    risky_w       = weights[:-1]           # drop cash
    herfindahl    = float(np.sum(risky_w ** 2))
    max_herfindahl = 1.0                   # fully concentrated
    min_herfindahl = 1.0 / len(risky_w)   # perfectly uniform
    conc_pen      = 0.05 * (herfindahl - min_herfindahl) / (max_herfindahl - min_herfindahl + 1e-8)

    # ── 8. Sharpe-like core ──────────────────────────────────────────────────
    # Use rolling mean / vol; scale to daily so magnitudes are interpretable.
    roll_mean     = float(np.mean(arr)) if n >= 1 else float(port_ret)
    daily_vol     = roll_vol / np.sqrt(252)
    sharpe_core   = roll_mean / (daily_vol + 1e-8)   # dimensionless daily Sharpe

    # ── 9. CVaR penalty ──────────────────────────────────────────────────────
    # Penalise negative tail; scale relative to daily vol.
    cvar_pen      = -0.5 * min(cvar, 0.0) / (daily_vol + 1e-8)

    # ── 10. Drawdown penalty ─────────────────────────────────────────────────
    # Soft quadratic penalty that grows with depth.
    dd_pen        = 0.5 * (drawdown ** 2)

    # ── 11. Compose total ────────────────────────────────────────────────────
    total = (
        sharpe_core          # risk-adjusted return (main signal)
        - cvar_pen           # tail-loss penalty (already sign-flipped above)
        - dd_pen             # drawdown penalty
        - turnover_pen       # extra churn penalty
        - conc_pen           # concentration penalty
    )

    # ── 12. Components dict (logging only) ───────────────────────────────────
    components = {
        "port_ret":     float(port_ret),
        "sharpe_core":  float(sharpe_core),
        "roll_vol":     float(roll_vol),
        "cvar":         float(cvar),
        "cvar_pen":     float(cvar_pen),
        "drawdown":     float(drawdown),
        "dd_pen":       float(dd_pen),
        "turnover":     float(turnover),
        "turnover_pen": float(turnover_pen),
        "conc_pen":     float(conc_pen),
        "total":        float(total),
    }

    # ── 13. Save state ───────────────────────────────────────────────────────
    reward_state = {
        "ret_history": ret_history,
        "peak":        peak,
        "cum_ret":     cum_ret,
    }

    return float(total), components, reward_state
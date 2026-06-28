def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Unpack / initialise state ────────────────────────────────────────────
    state = info.get("reward_state") if info is not None else None
    if state is None:
        state = {
            "ret_history":    [],          # rolling daily port returns
            "peak":           0.0,         # cumulative log-return peak (for drawdown)
            "cum_log_ret":    0.0,         # running cumulative log-return
            "step":           0,
        }

    state["step"] += 1
    step = state["step"]

    # ── Book-keeping ─────────────────────────────────────────────────────────
    log_ret = np.log1p(max(port_ret, -0.9999))          # guard against -100%
    state["cum_log_ret"] += log_ret
    state["peak"]         = max(state["peak"], state["cum_log_ret"])

    # Append return; keep rolling window of 252 steps (≈1 trading year)
    state["ret_history"].append(float(port_ret))
    WINDOW = 252
    if len(state["ret_history"]) > WINDOW:
        state["ret_history"].pop(0)

    hist = np.array(state["ret_history"], dtype=np.float64)

    # ── 1. Sharpe-like signal (rolling, annualised) ──────────────────────────
    if len(hist) >= 20:
        mu_r  = np.mean(hist)
        sig_r = np.std(hist, ddof=1)
        sig_r = max(sig_r, 1e-8)
        sharpe_signal = mu_r / sig_r           # daily; sign & magnitude matter
    else:
        # Not enough data: just use the raw return as a weak signal
        sharpe_signal = float(port_ret)

    # ── 2. Drawdown penalty ──────────────────────────────────────────────────
    drawdown       = state["cum_log_ret"] - state["peak"]   # ≤ 0
    drawdown_pen   = abs(drawdown)                           # penalty magnitude

    # ── 3. Tail / CVaR penalty (5% CVaR on rolling window) ──────────────────
    if len(hist) >= 20:
        pct5          = np.percentile(hist, 5)               # VaR-5%
        tail_returns  = hist[hist <= pct5]
        cvar5         = float(np.mean(tail_returns)) if len(tail_returns) > 0 else pct5
        tail_pen      = abs(min(cvar5, 0.0))                 # positive penalty
    else:
        tail_pen = abs(min(float(port_ret), 0.0))

    # ── 4. Turnover penalty (beyond what the env already charges) ────────────
    # Encourage stability; the 10 bps cost is already in port_ret, but we add
    # a mild extra term to further discourage excessive churn.
    turnover      = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    turnover_pen  = turnover                                 # ∈ [0, 1]

    # ── 5. Concentration penalty (encourage diversification) ─────────────────
    risky_w      = weights[:30]
    herfindahl   = float(np.sum(risky_w ** 2))              # ∈ [0, 1]
    # Penalise only above a reasonable threshold (e.g. equal-weight HHI ≈ 1/30)
    hhi_baseline = 1.0 / 30.0
    conc_pen     = max(herfindahl - hhi_baseline, 0.0)

    # ── Combine ──────────────────────────────────────────────────────────────
    # Weights chosen so that at normal vol (~1% daily) each term is O(1e-2).
    W_SHARPE   = 1.0
    W_DD       = 0.5
    W_TAIL     = 0.8
    W_TURNOVER = 0.2
    W_CONC     = 0.1

    total = (  W_SHARPE   * sharpe_signal
             - W_DD       * drawdown_pen
             - W_TAIL     * tail_pen
             - W_TURNOVER * turnover_pen
             - W_CONC     * conc_pen   )

    components = {
        "sharpe_signal":  float(sharpe_signal),
        "drawdown_pen":   float(drawdown_pen),
        "tail_pen":       float(tail_pen),
        "turnover_pen":   float(turnover_pen),
        "conc_pen":       float(conc_pen),
        "port_ret":       float(port_ret),
    }

    return float(total), components, state
def reward(weights, returns, prev_weights, port_ret, info):
    # ── Recover / initialise state ──────────────────────────────────────
    state = info.get("reward_state") or {}
    
    # Rolling window of portfolio returns (for Sharpe & CVaR)
    ret_history = list(state.get("ret_history", []))
    peak        = float(state.get("peak", 1.0))
    cum_val     = float(state.get("cum_val", 1.0))
    
    # ── Update cumulative value & drawdown ──────────────────────────────
    cum_val = cum_val * (1.0 + port_ret)
    peak    = max(peak, cum_val)
    drawdown = (peak - cum_val) / (peak + 1e-8)
    
    # ── Append current return to history ────────────────────────────────
    ret_history.append(port_ret)
    WINDOW = 60  # rolling window
    if len(ret_history) > WINDOW:
        ret_history = ret_history[-WINDOW:]
    
    hist = np.array(ret_history, dtype=np.float64)
    n    = len(hist)
    
    # ── Online Sharpe (annualised-ish, robust to short history) ─────────
    if n >= 5:
        mu  = np.mean(hist)
        sig = np.std(hist, ddof=1) + 1e-8
        sharpe = mu / sig  # per-step; scale factor cancels in ratio
    else:
        mu  = port_ret
        sig = 1e-8
        sharpe = 0.0
    
    # ── CVaR penalty (5% tail of rolling history) ───────────────────────
    if n >= 10:
        cutoff  = max(1, int(np.floor(0.05 * n)))
        tail    = np.sort(hist)[:cutoff]
        cvar_5  = np.mean(tail)          # negative number = bad
        cvar_pen = -cvar_5               # positive = worse tail loss
    else:
        cvar_pen = max(0.0, -port_ret)
    
    # ── Turnover penalty ────────────────────────────────────────────────
    turnover    = float(np.sum(np.abs(weights - prev_weights)))
    tc_pen      = 0.5 * turnover         # proportional penalty
    
    # ── Drawdown penalty (quadratic to discourage deep drawdowns) ───────
    dd_pen = 2.0 * (drawdown ** 2)
    
    # ── Concentration penalty (encourage diversification) ───────────────
    # Herfindahl index minus 1/n baseline
    n_assets    = len(weights)
    hhi         = float(np.sum(weights ** 2))
    hhi_min     = 1.0 / n_assets
    conc_pen    = max(0.0, hhi - hhi_min)
    
    # ── Combine components ───────────────────────────────────────────────
    # Primary: Sharpe-like signal
    # Secondary: penalise tail risk, drawdown, turnover, concentration
    sharpe_w  = 1.0
    cvar_w    = 3.0   # heavy weight on tail risk given poor CVaR
    dd_w      = 1.5
    tc_w      = 0.5
    conc_w    = 0.3
    
    total = (sharpe_w  * sharpe
           - cvar_w   * cvar_pen
           - dd_w     * dd_pen
           - tc_w     * tc_pen
           - conc_w   * conc_pen)
    
    components = {
        "sharpe_contrib": sharpe_w  * sharpe,
        "cvar_pen":       cvar_w    * cvar_pen,
        "dd_pen":         dd_w      * dd_pen,
        "tc_pen":         tc_w      * tc_pen,
        "conc_pen":       conc_w    * conc_pen,
        "port_ret":       port_ret,
        "drawdown":       drawdown,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak":        peak,
        "cum_val":     cum_val,
    }
    
    return float(total), components, reward_state
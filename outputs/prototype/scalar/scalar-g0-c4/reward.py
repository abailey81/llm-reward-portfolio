def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore or initialise state ──────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history":    [],          # rolling window of port_ret values
            "peak":           0.0,         # for drawdown tracking (cumulative log-return)
            "cum_log_ret":    0.0,
            "step":           0,
        }

    ret_history = state["ret_history"]
    peak        = state["peak"]
    cum_log_ret = state["cum_log_ret"]
    step        = state["step"]

    # ── Basic quantities ─────────────────────────────────────────────────────
    r = float(port_ret)

    # Update cumulative log-return and peak (for drawdown)
    log_r       = np.log1p(r)
    cum_log_ret += log_r
    peak         = max(peak, cum_log_ret)
    drawdown     = peak - cum_log_ret          # non-negative, 0 = at new high

    # Rolling history (keep last 252 steps ≈ 1 trading year)
    WINDOW = 252
    ret_history.append(r)
    if len(ret_history) > WINDOW:
        ret_history.pop(0)

    arr = np.array(ret_history, dtype=np.float64)
    n   = len(arr)

    # ── Rolling volatility ───────────────────────────────────────────────────
    if n >= 2:
        roll_vol = float(np.std(arr, ddof=1))
    else:
        roll_vol = 1e-4                        # tiny positive to avoid div/0

    roll_vol = max(roll_vol, 1e-6)

    # ── Sharpe-like component  (annualised units don't matter here) ──────────
    roll_mean  = float(np.mean(arr))
    sharpe_inc = r / roll_vol                  # per-step contribution to Sharpe

    # ── CVaR / tail-loss component (worst 5 % of window) ────────────────────
    if n >= 20:
        tail_cutoff = int(max(1, np.floor(0.05 * n)))
        sorted_arr  = np.sort(arr)
        cvar_05     = float(np.mean(sorted_arr[:tail_cutoff]))
    else:
        cvar_05 = min(r, 0.0)                  # conservative when history is short

    # Penalise only when CVaR is negative
    cvar_penalty = min(cvar_05, 0.0)           # ≤ 0

    # ── Drawdown penalty ─────────────────────────────────────────────────────
    dd_penalty = -drawdown                     # non-positive contribution

    # ── Turnover cost (additional soft penalty beyond the env's hard cost) ───
    turnover    = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    turn_penalty = -0.5 * turnover             # mild extra friction signal

    # ── Concentration penalty (encourage some diversification) ───────────────
    risky_w      = weights[:30]
    herfindahl   = float(np.sum(risky_w ** 2))
    # Maximum possible HHI for 30 assets is 1.0 (all in one asset)
    # Penalise only extreme concentration
    conc_penalty = -max(0.0, herfindahl - 0.20)

    # ── Combine ───────────────────────────────────────────────────────────────
    # Weights chosen so reward is centred near Sharpe contribution during
    # normal trading, with meaningful but not overwhelming risk penalties.
    w_sharpe  = 1.0
    w_cvar    = 2.0    # tail losses matter more than mean
    w_dd      = 1.0
    w_turn    = 0.5
    w_conc    = 0.3

    total = (
        w_sharpe * sharpe_inc
        + w_cvar  * cvar_penalty
        + w_dd    * dd_penalty
        + w_turn  * turn_penalty
        + w_conc  * conc_penalty
    )

    components = {
        "port_ret":     r,
        "sharpe_inc":   float(w_sharpe * sharpe_inc),
        "cvar_penalty": float(w_cvar   * cvar_penalty),
        "dd_penalty":   float(w_dd     * dd_penalty),
        "turn_penalty": float(w_turn   * turn_penalty),
        "conc_penalty": float(w_conc   * conc_penalty),
        "roll_vol":     roll_vol,
        "drawdown":     drawdown,
        "cvar_05":      cvar_05,
        "herfindahl":   herfindahl,
        "turnover":     turnover,
    }

    # ── Save state ────────────────────────────────────────────────────────────
    new_state = {
        "ret_history":  ret_history,
        "peak":         peak,
        "cum_log_ret":  cum_log_ret,
        "step":         step + 1,
    }

    return float(total), components, new_state
def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore / initialise state ──────────────────────────────────────────
    state = info.get("reward_state") if info is not None else None
    if state is None:
        state = {
            "ret_history":    [],      # rolling window of port_ret values
            "peak":           0.0,     # cumulative-return peak (for drawdown)
            "cum_ret":        0.0,     # running cumulative return (log-approx)
            "ema_mean":       None,    # EMA of returns
            "ema_var":        None,    # EMA of return variance
        }

    # ── Parameters ──────────────────────────────────────────────────────────
    WINDOW      = 60      # rolling window for vol / CVaR
    ALPHA       = 0.05    # CVaR tail fraction
    EMA_DECAY   = 0.94    # λ for EMA vol estimator
    SHARPE_W    = 1.0     # weight on Sharpe contribution
    DD_W        = 0.5     # weight on drawdown penalty
    CVAR_W      = 0.5     # weight on CVaR penalty
    CONC_W      = 0.05    # weight on concentration penalty
    TURNOVER_W  = 0.3     # extra explicit turnover penalty

    r = float(port_ret)

    # ── Update rolling return history ────────────────────────────────────────
    state["ret_history"].append(r)
    if len(state["ret_history"]) > WINDOW:
        state["ret_history"].pop(0)
    hist = np.array(state["ret_history"], dtype=np.float64)

    # ── EMA mean & variance (for online Sharpe) ──────────────────────────────
    lam = EMA_DECAY
    if state["ema_mean"] is None:
        state["ema_mean"] = r
        state["ema_var"]  = 1e-8
    else:
        prev_mean         = state["ema_mean"]
        state["ema_mean"] = lam * prev_mean + (1 - lam) * r
        state["ema_var"]  = lam * state["ema_var"] + (1 - lam) * (r - prev_mean) ** 2

    ema_std = float(np.sqrt(max(state["ema_var"], 1e-8)))
    ema_mean = float(state["ema_mean"])

    # ── Rolling Sharpe contribution ──────────────────────────────────────────
    if len(hist) >= 5:
        roll_std  = float(np.std(hist, ddof=1)) + 1e-8
        roll_mean = float(np.mean(hist))
    else:
        roll_std  = ema_std
        roll_mean = ema_mean

    sharpe_contrib = r / roll_std        # one-step contribution to Sharpe

    # ── Drawdown penalty ─────────────────────────────────────────────────────
    state["cum_ret"] += r                # simple sum as proxy for log-cum-ret
    if state["cum_ret"] > state["peak"]:
        state["peak"] = state["cum_ret"]
    drawdown = state["peak"] - state["cum_ret"]   # >= 0

    # ── CVaR (Expected Shortfall) penalty ───────────────────────────────────
    if len(hist) >= 10:
        tail_cutoff = int(np.floor(ALPHA * len(hist)))
        tail_cutoff = max(tail_cutoff, 1)
        sorted_hist = np.sort(hist)
        cvar_loss   = float(-np.mean(sorted_hist[:tail_cutoff]))   # > 0 means loss
    else:
        cvar_loss = float(max(-r, 0.0))

    # ── Turnover penalty (supplement to env cost already in port_ret) ────────
    turnover = float(np.sum(np.abs(weights - prev_weights))) * 0.5

    # ── Concentration penalty (Herfindahl on risky weights) ─────────────────
    risky_w     = weights[:30]
    risky_sum   = float(np.sum(risky_w))
    if risky_sum > 1e-8:
        norm_w      = risky_w / risky_sum
        herfindahl  = float(np.sum(norm_w ** 2))   # 1/N…1
    else:
        herfindahl  = 1.0

    # ── Assemble total reward ────────────────────────────────────────────────
    sharpe_term   =  SHARPE_W  * sharpe_contrib
    dd_term       = -DD_W      * drawdown
    cvar_term     = -CVAR_W    * cvar_loss
    turnover_term = -TURNOVER_W * turnover
    conc_term     = -CONC_W    * herfindahl

    total = sharpe_term + dd_term + cvar_term + turnover_term + conc_term

    components = {
        "port_ret":     r,
        "sharpe_term":  sharpe_term,
        "dd_term":      dd_term,
        "cvar_term":    cvar_term,
        "turnover_term":turnover_term,
        "conc_term":    conc_term,
        "roll_std":     roll_std,
        "drawdown":     drawdown,
        "cvar_loss":    cvar_loss,
        "herfindahl":   herfindahl,
        "turnover":     turnover,
    }

    return float(total), components, state
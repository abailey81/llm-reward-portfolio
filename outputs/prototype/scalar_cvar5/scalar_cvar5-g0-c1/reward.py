def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Hyperparameters ──────────────────────────────────────────────────────
    WINDOW          = 60      # rolling window for vol / CVaR
    CVaR_ALPHA      = 0.05    # tail level (worst 5 %)
    SHARPE_SCALE    = 252.0   # annualisation
    LAMBDA_VOL      = 0.5     # penalty on realised vol
    LAMBDA_DD       = 1.0     # penalty on current drawdown
    LAMBDA_CVAR     = 0.5     # penalty on tail loss
    LAMBDA_TURNOVER = 2.0     # extra turnover penalty (cost already in port_ret)
    LAMBDA_CONC     = 0.2     # concentration / Herfindahl penalty
    MIN_HIST        = 5       # steps before we activate risk penalties

    # ── Restore / initialise state ───────────────────────────────────────────
    state = info.get("reward_state") if info is not None else None
    if state is None:
        state = {
            "ret_history":  [],          # list of floats
            "peak_value":   1.0,
            "port_value":   1.0,
        }

    ret_history  = state["ret_history"]
    peak_value   = state["peak_value"]
    port_value   = state["port_value"]

    # ── Update portfolio value & drawdown ────────────────────────────────────
    port_value  = port_value * (1.0 + port_ret)
    peak_value  = max(peak_value, port_value)
    drawdown    = (peak_value - port_value) / (peak_value + 1e-8)   # ≥ 0

    # ── Append return to history ─────────────────────────────────────────────
    ret_history.append(float(port_ret))
    if len(ret_history) > WINDOW:
        ret_history = ret_history[-WINDOW:]

    # ── Rolling statistics ───────────────────────────────────────────────────
    hist = np.array(ret_history, dtype=np.float64)
    n    = len(hist)

    if n >= MIN_HIST:
        roll_mean = hist.mean()
        roll_std  = hist.std() + 1e-8

        # Sharpe-like signal (not yet annualised — single step)
        sharpe_step = roll_mean / roll_std

        # CVaR (expected shortfall) — mean of worst α fraction
        k         = max(1, int(np.floor(CVaR_ALPHA * n)))
        worst_k   = np.sort(hist)[:k]
        cvar      = -worst_k.mean()          # positive = bad tail loss

        vol_penalty  = LAMBDA_VOL  * roll_std
        cvar_penalty = LAMBDA_CVAR * max(cvar, 0.0)
    else:
        sharpe_step  = 0.0
        vol_penalty  = 0.0
        cvar_penalty = 0.0

    # ── Drawdown penalty ─────────────────────────────────────────────────────
    dd_penalty = LAMBDA_DD * drawdown

    # ── Turnover penalty (on top of the cost already deducted) ──────────────
    turnover     = 0.5 * np.sum(np.abs(weights - prev_weights))
    to_penalty   = LAMBDA_TURNOVER * turnover

    # ── Concentration penalty (Herfindahl index on risky weights) ───────────
    risky_w      = weights[:30]
    herfindahl   = float(np.sum(risky_w ** 2))
    conc_penalty = LAMBDA_CONC * herfindahl

    # ── Core return signal ───────────────────────────────────────────────────
    # Use port_ret directly plus a mild Sharpe bonus
    ret_signal = float(port_ret) + 0.1 * sharpe_step

    # ── Combine ──────────────────────────────────────────────────────────────
    total = (
        ret_signal
        - vol_penalty
        - dd_penalty
        - cvar_penalty
        - to_penalty
        - conc_penalty
    )

    components = {
        "port_ret":     float(port_ret),
        "ret_signal":   float(ret_signal),
        "sharpe_step":  float(sharpe_step),
        "vol_penalty":  float(vol_penalty),
        "dd_penalty":   float(dd_penalty),
        "cvar_penalty": float(cvar_penalty),
        "to_penalty":   float(to_penalty),
        "conc_penalty": float(conc_penalty),
        "drawdown":     float(drawdown),
        "turnover":     float(turnover),
        "port_value":   float(port_value),
    }

    # ── Save state ───────────────────────────────────────────────────────────
    state["ret_history"] = ret_history
    state["peak_value"]  = float(peak_value)
    state["port_value"]  = float(port_value)

    return float(total), components, state
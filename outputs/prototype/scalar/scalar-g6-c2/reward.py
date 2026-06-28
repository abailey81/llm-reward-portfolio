def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Recover / initialise state ────────────────────────────────────────────
    state = info.get("reward_state") or {}

    # Exponential-moving-average parameters
    alpha_fast = 0.10   # ~10-step memory  (for mean/var)
    alpha_slow = 0.02   # ~50-step memory  (for drawdown baseline)

    ema_r   = state.get("ema_r",   0.0)
    ema_r2  = state.get("ema_r2",  1e-4)
    peak    = state.get("peak",    0.0)   # cumulative log-wealth peak
    cum_log = state.get("cum_log", 0.0)   # cumulative log-wealth
    step    = state.get("step",    0)

    # Rolling window for tail-risk (CVaR)
    window_size = 60
    hist = list(state.get("hist", []))

    # ── Update running statistics ─────────────────────────────────────────────
    log_r = np.log1p(max(port_ret, -0.9999))   # log return this step

    ema_r  = (1 - alpha_fast) * ema_r  + alpha_fast * log_r
    ema_r2 = (1 - alpha_fast) * ema_r2 + alpha_fast * log_r ** 2

    cum_log += log_r
    peak     = max(peak, cum_log)

    hist.append(log_r)
    if len(hist) > window_size:
        hist.pop(0)

    step += 1

    # ── Component 1 : incremental Sharpe signal ───────────────────────────────
    var_r = max(ema_r2 - ema_r ** 2, 1e-8)
    std_r = np.sqrt(var_r)

    # Differential Sharpe (Moody & Saffell): gradient of Sharpe w.r.t. new obs
    # S = mean / std  →  dS/dr ≈ (1/std) * (1 - 0.5 * S * (r - mean) / std)
    sharpe_est = ema_r / std_r
    diff_sharpe = (log_r - ema_r) / std_r - 0.5 * sharpe_est * ((log_r - ema_r) ** 2 / var_r - 1)
    diff_sharpe = np.clip(diff_sharpe, -5.0, 5.0)

    # ── Component 2 : drawdown penalty ───────────────────────────────────────
    drawdown     = cum_log - peak          # ≤ 0
    dd_penalty   = np.clip(drawdown, -1.0, 0.0)   # bounded

    # ── Component 3 : CVaR penalty (tail loss from recent history) ────────────
    if len(hist) >= 10:
        arr       = np.array(hist)
        cvar_q    = 0.10                            # worst 10 %
        cutoff    = np.quantile(arr, cvar_q)
        tail      = arr[arr <= cutoff]
        cvar      = float(np.mean(tail)) if len(tail) > 0 else 0.0
        cvar_pen  = np.clip(cvar, -1.0, 0.0)       # already negative
    else:
        cvar_pen  = 0.0

    # ── Warmup: ramp weights so first steps don't dominate ────────────────────
    warmup_steps = 20
    warmup_scale = min(1.0, step / warmup_steps)

    # ── Combine ───────────────────────────────────────────────────────────────
    w_sharpe = 1.0
    w_dd     = 0.5
    w_cvar   = 0.3

    total = warmup_scale * (
        w_sharpe * diff_sharpe
        + w_dd   * dd_penalty
        + w_cvar * cvar_pen
    )

    components = {
        "diff_sharpe": float(diff_sharpe),
        "dd_penalty":  float(dd_penalty),
        "cvar_pen":    float(cvar_pen),
        "warmup":      float(warmup_scale),
        "sharpe_est":  float(sharpe_est),
    }

    reward_state = {
        "ema_r":   ema_r,
        "ema_r2":  ema_r2,
        "peak":    peak,
        "cum_log": cum_log,
        "step":    step,
        "hist":    hist,
    }

    return float(total), components, reward_state
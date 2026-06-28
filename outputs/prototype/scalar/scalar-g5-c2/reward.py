def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore / initialise state ──────────────────────────────────────────
    state = info.get("reward_state") or {}

    # Exponential-moving-average parameters
    alpha_fast = 0.05   # ~20-step half-life  (Sharpe signal)
    alpha_slow = 0.02   # ~50-step half-life  (baseline / drawdown)

    ema_ret  = state.get("ema_ret",  0.0)
    ema_sq   = state.get("ema_sq",   1e-6)
    peak_val = state.get("peak_val", 1.0)
    port_val = state.get("port_val", 1.0)
    recent_returns = state.get("recent_returns", [])
    step     = state.get("step", 0)

    # ── Update portfolio value ──────────────────────────────────────────────
    port_val = port_val * (1.0 + port_ret)
    peak_val = max(peak_val, port_val)

    # ── Update EMA statistics ───────────────────────────────────────────────
    ema_ret = (1 - alpha_fast) * ema_ret + alpha_fast * port_ret
    ema_sq  = (1 - alpha_fast) * ema_sq  + alpha_fast * (port_ret ** 2)

    variance = max(ema_sq - ema_ret ** 2, 1e-8)
    std_est  = np.sqrt(variance)

    # Online Sharpe (annualised-ish, but kept as ratio for stability)
    online_sharpe = ema_ret / std_est

    # ── Drawdown penalty ───────────────────────────────────────────────────
    drawdown = (peak_val - port_val) / (peak_val + 1e-8)
    drawdown_penalty = drawdown ** 2   # quadratic: punish deep drawdowns harder

    # ── Tail / CVaR penalty from recent window ────────────────────────────
    recent_returns.append(port_ret)
    window = 60
    if len(recent_returns) > window:
        recent_returns = recent_returns[-window:]

    if len(recent_returns) >= 10:
        arr = np.array(recent_returns)
        cutoff = np.percentile(arr, 10)          # 10th percentile (tail)
        tail_losses = arr[arr <= cutoff]
        cvar = float(np.mean(tail_losses))       # negative number = bad
        cvar_penalty = max(-cvar, 0.0)           # penalise tail losses
    else:
        cvar_penalty = 0.0

    # ── Turnover penalty ──────────────────────────────────────────────────
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.1 * turnover

    # ── Warm-up: suppress noisy early signal ─────────────────────────────
    step += 1
    warmup = min(step / 30.0, 1.0)   # ramp up over first 30 steps

    # ── Combine components ───────────────────────────────────────────────
    sharpe_reward    = warmup * online_sharpe
    dd_penalty_term  = 2.0 * drawdown_penalty
    cvar_term        = 1.5 * cvar_penalty
    turnover_term    = turnover_penalty

    total = sharpe_reward - dd_penalty_term - cvar_term - turnover_term

    components = {
        "sharpe_reward":    float(sharpe_reward),
        "drawdown_penalty": float(dd_penalty_term),
        "cvar_penalty":     float(cvar_term),
        "turnover_penalty": float(turnover_term),
        "online_sharpe":    float(online_sharpe),
        "drawdown":         float(drawdown),
    }

    reward_state = {
        "ema_ret":        ema_ret,
        "ema_sq":         ema_sq,
        "peak_val":       peak_val,
        "port_val":       port_val,
        "recent_returns": recent_returns,
        "step":           step,
    }

    return float(total), components, reward_state
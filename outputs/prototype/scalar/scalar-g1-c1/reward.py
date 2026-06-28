def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}
    
    # Running statistics for Sharpe (exponential moving average)
    alpha = 0.05  # EMA decay for ~20-step window
    ema_ret   = state.get("ema_ret",   port_ret)
    ema_sq    = state.get("ema_sq",    port_ret ** 2)
    peak      = state.get("peak",      1.0)
    nav       = state.get("nav",       1.0)
    step      = state.get("step",      0)

    # Update NAV and peak
    nav  = nav * (1.0 + port_ret)
    peak = max(peak, nav)

    # Update EMA of return and squared return
    ema_ret = alpha * port_ret + (1 - alpha) * ema_ret
    ema_sq  = alpha * port_ret**2 + (1 - alpha) * ema_sq

    step += 1

    # --- Component 1: Online Sharpe signal ---
    var_est = max(ema_sq - ema_ret**2, 1e-8)
    std_est = np.sqrt(var_est)
    sharpe_signal = ema_ret / std_est  # dimensionless

    # Scale the Sharpe signal to a per-step reward
    sharpe_reward = np.clip(sharpe_signal * 0.1, -2.0, 2.0)

    # --- Component 2: Raw return (lightly weighted) ---
    ret_reward = np.clip(port_ret * 5.0, -1.0, 1.0)

    # --- Component 3: Drawdown penalty ---
    drawdown = (peak - nav) / (peak + 1e-8)
    drawdown_penalty = -np.clip(drawdown * 2.0, 0.0, 1.0)

    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -np.clip(turnover * 0.5, 0.0, 0.5)

    # --- Component 5: Tail-loss penalty (downside emphasis) ---
    neg_ret = min(port_ret, 0.0)
    tail_penalty = -np.clip(neg_ret**2 * 50.0, 0.0, 0.5)

    # --- Total reward (weighted combination) ---
    # Ramp up Sharpe weight vs raw return over time
    sharpe_weight = min(step / 50.0, 1.0)
    ret_weight    = 1.0 - 0.5 * sharpe_weight

    total = (
        sharpe_weight * sharpe_reward
        + ret_weight  * ret_reward
        + 0.5 * drawdown_penalty
        + turnover_penalty
        + 0.3 * tail_penalty
    )

    components = {
        "sharpe_signal":    float(sharpe_signal),
        "sharpe_reward":    float(sharpe_reward),
        "ret_reward":       float(ret_reward),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "tail_penalty":     float(tail_penalty),
        "nav":              float(nav),
        "drawdown":         float(drawdown),
    }

    reward_state = {
        "ema_ret": float(ema_ret),
        "ema_sq":  float(ema_sq),
        "peak":    float(peak),
        "nav":     float(nav),
        "step":    step,
    }

    return float(total), components, reward_state
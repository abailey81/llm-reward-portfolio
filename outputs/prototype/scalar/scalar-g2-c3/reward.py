def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize reward state
    state = info.get("reward_state")
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_var": 1e-6,
            "peak": 1.0,
            "cumulative": 1.0,
            "step": 0,
            "alpha": 0.06,  # EMA decay ~ 1/16 steps
        }

    alpha = state["alpha"]
    ema_ret = state["ema_ret"]
    ema_var = state["ema_var"]
    peak = state["peak"]
    cumulative = state["cumulative"]
    step = state["step"]

    # --- Update EMA of returns and variance ---
    ema_ret_new = alpha * port_ret + (1.0 - alpha) * ema_ret
    var_update = alpha * (port_ret - ema_ret) ** 2 + (1.0 - alpha) * ema_var
    ema_var_new = max(var_update, 1e-8)

    # --- Online Sharpe component ---
    sharpe_approx = ema_ret_new / np.sqrt(ema_var_new)

    # Scale to be a per-step signal (not cumulative)
    sharpe_signal = sharpe_approx * alpha  # weight by how much new info contributed

    # --- Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.002 * turnover  # mild penalty

    # --- Drawdown penalty ---
    cumulative_new = cumulative * (1.0 + port_ret)
    peak_new = max(peak, cumulative_new)
    drawdown = (peak_new - cumulative_new) / (peak_new + 1e-8)
    # Penalize more severely for large drawdowns (convex penalty)
    drawdown_penalty = 0.5 * drawdown ** 2

    # --- Direct return signal (scaled down) ---
    # Small direct return signal helps early learning
    direct = port_ret * 0.1

    # --- Total reward ---
    total = sharpe_signal + direct - turnover_penalty - drawdown_penalty

    components = {
        "sharpe_signal": float(sharpe_signal),
        "direct_return": float(direct),
        "turnover_penalty": float(-turnover_penalty),
        "drawdown_penalty": float(-drawdown_penalty),
    }

    # Update state
    state["ema_ret"] = ema_ret_new
    state["ema_var"] = ema_var_new
    state["peak"] = peak_new
    state["cumulative"] = cumulative_new
    state["step"] = step + 1

    return float(total), components, state
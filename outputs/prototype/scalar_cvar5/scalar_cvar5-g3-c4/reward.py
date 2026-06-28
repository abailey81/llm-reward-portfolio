def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize reward state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_var": 1e-6,
            "peak": 1.0,
            "cum_ret": 1.0,
            "recent_rets": [],
            "step": 0,
        }

    alpha_fast = 0.05   # EMA decay for mean/variance (longer window)
    alpha_slow = 0.02   # slower decay for tail tracking

    step = state["step"] + 1
    state["step"] = step

    # --- Update EMA of returns and variance ---
    ema_ret = state["ema_ret"]
    ema_var = state["ema_var"]

    ema_ret_new = (1 - alpha_fast) * ema_ret + alpha_fast * port_ret
    ema_var_new = (1 - alpha_fast) * ema_var + alpha_fast * (port_ret - ema_ret) ** 2
    ema_var_new = max(ema_var_new, 1e-8)

    state["ema_ret"] = ema_ret_new
    state["ema_var"] = ema_var_new

    # --- Online Sharpe component ---
    online_sharpe = ema_ret_new / np.sqrt(ema_var_new)
    sharpe_reward = np.clip(online_sharpe, -3.0, 3.0) * 0.3

    # --- Tail loss (CVaR proxy): track recent returns window ---
    recent = state["recent_rets"]
    recent.append(port_ret)
    if len(recent) > 60:
        recent.pop(0)
    state["recent_rets"] = recent

    if len(recent) >= 10:
        arr = np.array(recent)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        cvar_est = float(np.mean(tail)) if len(tail) > 0 else cutoff
    else:
        cvar_est = port_ret

    # Penalize bad CVaR (encourage it to be positive / less negative)
    cvar_penalty = np.clip(cvar_est, -0.1, 0.0) * 2.0  # negative contribution

    # --- Drawdown penalty ---
    cum_ret = state["cum_ret"] * (1.0 + port_ret)
    state["cum_ret"] = cum_ret
    peak = state["peak"]
    if cum_ret > peak:
        peak = cum_ret
        state["peak"] = peak
    drawdown = (cum_ret - peak) / (peak + 1e-8)
    drawdown_penalty = np.clip(drawdown, -0.5, 0.0) * 0.5  # negative contribution

    # --- Return component: direct log-return proxy ---
    log_ret = np.log1p(np.clip(port_ret, -0.5, 2.0))
    return_reward = np.clip(log_ret, -0.3, 0.3) * 1.0

    # --- Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.05 * turnover

    # --- Concentration penalty (encourage diversification) ---
    herfindahl = float(np.sum(weights ** 2))
    concentration_penalty = -0.05 * herfindahl

    # --- Combine all components ---
    total = (
        return_reward
        + sharpe_reward
        + cvar_penalty
        + drawdown_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "return_reward": float(return_reward),
        "sharpe_reward": float(sharpe_reward),
        "cvar_penalty": float(cvar_penalty),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
    }

    return float(total), components, state
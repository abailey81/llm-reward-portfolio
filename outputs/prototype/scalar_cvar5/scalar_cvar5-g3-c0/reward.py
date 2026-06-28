def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize reward state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_var": 1e-6,
            "peak": 0.0,
            "cum_ret": 0.0,
            "recent_rets": [],
            "step": 0,
        }

    # Hyperparameters
    alpha = 0.05          # EMA decay (fast)
    alpha_slow = 0.02     # EMA decay (slow, for variance)
    tail_window = 60      # window for CVaR computation
    cvar_quantile = 0.05  # 5% CVaR
    turnover_penalty = 0.002  # cost per unit turnover
    drawdown_penalty = 0.5    # multiplier on drawdown component
    sharpe_weight = 1.0
    cvar_weight = 2.0
    dd_weight = 1.0

    step = state["step"]

    # --- Update EMA of returns and variance ---
    ema_ret = state["ema_ret"]
    ema_var = state["ema_var"]

    ema_ret = (1 - alpha) * ema_ret + alpha * port_ret
    ema_var = (1 - alpha_slow) * ema_var + alpha_slow * (port_ret - ema_ret) ** 2
    ema_std = np.sqrt(max(ema_var, 1e-8))

    # --- Online Sharpe component ---
    sharpe_component = ema_ret / ema_std

    # --- CVaR component using recent returns history ---
    recent_rets = state["recent_rets"]
    recent_rets.append(port_ret)
    if len(recent_rets) > tail_window:
        recent_rets.pop(0)

    if len(recent_rets) >= 10:
        arr = np.array(recent_rets)
        cutoff = np.percentile(arr, cvar_quantile * 100)
        tail = arr[arr <= cutoff]
        cvar = float(np.mean(tail)) if len(tail) > 0 else cutoff
    else:
        cvar = 0.0  # not enough data yet

    # CVaR penalty: negative CVaR is bad, we want to maximize (reduce loss)
    cvar_component = cvar  # will be negative for losses

    # --- Drawdown component ---
    cum_ret = state["cum_ret"]
    cum_ret = cum_ret + port_ret + cum_ret * port_ret  # compound
    peak = state["peak"]
    if cum_ret > peak:
        peak = cum_ret
    drawdown = (peak - cum_ret) / (1.0 + peak) if peak > cum_ret else 0.0
    dd_component = -drawdown  # penalty

    # --- Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_component = -turnover_penalty * turnover

    # --- Combine reward ---
    # Scale sharpe to be in a reasonable range
    total = (
        sharpe_weight * sharpe_component
        + cvar_weight * cvar_component
        + dd_weight * dd_component
        + turnover_component
    )

    components = {
        "sharpe_component": float(sharpe_component),
        "cvar_component": float(cvar_component),
        "dd_component": float(dd_component),
        "turnover_component": float(turnover_component),
        "ema_ret": float(ema_ret),
        "ema_std": float(ema_std),
        "drawdown": float(drawdown),
    }

    # Update state
    state["ema_ret"] = ema_ret
    state["ema_var"] = ema_var
    state["peak"] = peak
    state["cum_ret"] = cum_ret
    state["recent_rets"] = recent_rets
    state["step"] = step + 1

    return float(total), components, state
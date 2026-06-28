def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Recover or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_log_ret": 0.0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "step": 0,
        }

    step = state["step"]
    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_log_ret = state["cum_log_ret"]
    ema_mean = state["ema_mean"]
    ema_var = state["ema_var"]

    # --- Online EMA for mean and variance (for Sharpe-like signal) ---
    alpha = 0.05  # smoothing factor; ~20-step half-life
    ema_mean = alpha * port_ret + (1 - alpha) * ema_mean
    ema_var = alpha * (port_ret - ema_mean) ** 2 + (1 - alpha) * ema_var
    ema_std = np.sqrt(max(ema_var, 1e-8))

    # --- Cumulative log return and drawdown ---
    log_ret = np.log1p(max(port_ret, -0.9999))
    cum_log_ret = cum_log_ret + log_ret
    peak = max(peak, cum_log_ret)
    drawdown = peak - cum_log_ret  # always >= 0

    # --- Append to history for tail risk ---
    ret_history.append(port_ret)
    # Keep a rolling window
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # --- Compute CVaR (expected shortfall at 5%) from recent history ---
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        cvar = float(np.mean(tail)) if len(tail) > 0 else cutoff
    else:
        cvar = -0.01  # mild default penalty

    # --- Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))

    # --- Component rewards ---
    # 1. Risk-adjusted return: EMA Sharpe ratio signal
    sharpe_signal = ema_mean / ema_std  # dimensionless, centered near 0

    # 2. Drawdown penalty (relative, scaled)
    drawdown_penalty = -drawdown * 0.5

    # 3. Tail risk penalty (CVaR, scaled)
    cvar_penalty = cvar * 0.5  # cvar is negative when losses occur

    # 4. Turnover cost penalty
    turnover_penalty = -0.002 * turnover

    # 5. Direct return signal (scaled down to not dominate)
    ret_signal = port_ret * 10.0

    # --- Combine ---
    # Warm-start: gradually introduce sharpe signal to avoid noise early
    sharpe_weight = min(1.0, step / 30.0)

    total = (
        ret_signal
        + sharpe_weight * sharpe_signal * 0.5
        + drawdown_penalty
        + cvar_penalty
        + turnover_penalty
    )

    components = {
        "ret_signal": ret_signal,
        "sharpe_signal": sharpe_weight * sharpe_signal * 0.5,
        "drawdown_penalty": drawdown_penalty,
        "cvar_penalty": cvar_penalty,
        "turnover_penalty": turnover_penalty,
    }

    # --- Update state ---
    state["ret_history"] = ret_history
    state["peak"] = peak
    state["cum_log_ret"] = cum_log_ret
    state["ema_mean"] = ema_mean
    state["ema_var"] = ema_var
    state["step"] = step + 1

    return float(total), components, state
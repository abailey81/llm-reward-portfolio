def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state") or {}

    # --- Retrieve or initialize state ---
    ew_mean = state.get("ew_mean", 0.0)
    ew_var  = state.get("ew_var", 1e-6)
    peak    = state.get("peak", 1.0)
    cum_ret = state.get("cum_ret", 1.0)
    ret_history = state.get("ret_history", [])

    # --- Exponential smoothing parameters ---
    alpha = 0.06  # ~16-step half-life, responsive but stable

    # --- Update exponential weighted mean & variance ---
    ew_mean_new = alpha * port_ret + (1 - alpha) * ew_mean
    ew_var_new  = (1 - alpha) * (ew_var + alpha * (port_ret - ew_mean) ** 2)
    ew_var_new  = max(ew_var_new, 1e-8)
    ew_std      = np.sqrt(ew_var_new)

    # --- Online Sharpe (risk-adjusted return) ---
    sharpe_signal = ew_mean_new / ew_std

    # --- Drawdown penalty ---
    cum_ret_new = cum_ret * (1.0 + port_ret)
    peak_new    = max(peak, cum_ret_new)
    drawdown    = (cum_ret_new - peak_new) / peak_new  # <= 0

    # Scale drawdown penalty — stronger if deep drawdown
    dd_penalty = 2.0 * drawdown  # negative contribution

    # --- Tail / downside penalty (recent window) ---
    ret_history = (ret_history + [port_ret])[-60:]  # keep last 60 steps
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        # CVaR at 10% tail
        cutoff = np.percentile(arr, 10)
        tail   = arr[arr <= cutoff]
        cvar   = float(np.mean(tail))
        tail_penalty = 1.5 * cvar  # negative if bad tail
    else:
        tail_penalty = 0.0

    # --- Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.05 * turnover

    # --- Concentration penalty (Herfindahl) ---
    hhi = float(np.sum(weights ** 2))
    concentration_penalty = -0.02 * hhi

    # --- Combine components ---
    total = (
        sharpe_signal
        + dd_penalty
        + tail_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "sharpe_signal":        float(sharpe_signal),
        "dd_penalty":           float(dd_penalty),
        "tail_penalty":         float(tail_penalty),
        "turnover_penalty":     float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
    }

    reward_state = {
        "ew_mean":      ew_mean_new,
        "ew_var":       ew_var_new,
        "peak":         peak_new,
        "cum_ret":      cum_ret_new,
        "ret_history":  ret_history,
    }

    return float(total), components, reward_state
def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}

    # Rolling window for return history
    window = 60
    ret_history = list(state.get("ret_history", []))
    ret_history.append(port_ret)
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # Peak for drawdown tracking
    cum_ret = state.get("cum_ret", 1.0)
    cum_ret = cum_ret * (1.0 + port_ret)
    peak = state.get("peak", 1.0)
    peak = max(peak, cum_ret)
    drawdown = (cum_ret - peak) / (peak + 1e-8)  # <= 0

    # --- Component 1: Online Sharpe ratio (annualized) ---
    arr = np.array(ret_history)
    n = len(arr)
    if n >= 5:
        mu = np.mean(arr)
        sigma = np.std(arr) + 1e-8
        sharpe = (mu / sigma) * np.sqrt(252)
    else:
        sharpe = 0.0

    # --- Component 2: CVaR penalty ---
    # Penalize based on left tail of recent returns
    if n >= 10:
        tail_cutoff = max(1, int(0.05 * n))  # ~5% tail
        sorted_rets = np.sort(arr)
        cvar = np.mean(sorted_rets[:tail_cutoff])  # mean of worst returns
        cvar_penalty = min(0.0, cvar) * 10.0  # negative penalty
    else:
        cvar_penalty = 0.0

    # --- Component 3: Drawdown penalty ---
    # Penalize current drawdown magnitude
    dd_penalty = drawdown * 5.0  # drawdown <= 0, so this is <= 0

    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # --- Component 5: Raw return signal (scaled) ---
    # Give immediate feedback, scaled to reduce noise
    raw_ret = np.clip(port_ret, -0.1, 0.1) * 10.0

    # --- Combine ---
    # Sharpe is primary driver; others refine behavior
    if n >= 5:
        total = (
            0.4 * sharpe
            + 0.2 * raw_ret
            + 0.2 * cvar_penalty
            + 0.1 * dd_penalty
            + 0.1 * turnover_penalty
        )
    else:
        # Warm-up: use raw return only to get signal early
        total = raw_ret + turnover_penalty

    components = {
        "sharpe": float(sharpe),
        "raw_ret": float(raw_ret),
        "cvar_penalty": float(cvar_penalty),
        "dd_penalty": float(dd_penalty),
        "turnover_penalty": float(turnover_penalty),
    }

    reward_state = {
        "ret_history": ret_history,
        "cum_ret": float(cum_ret),
        "peak": float(peak),
    }

    return float(total), components, reward_state
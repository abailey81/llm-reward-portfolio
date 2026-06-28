def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve reward state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "n": 0,
            "mean": 0.0,
            "M2": 0.0,   # Welford's online variance
        }

    # Welford's online mean and variance update
    n = state["n"] + 1
    mean = state["mean"]
    M2 = state["M2"]

    delta = port_ret - mean
    mean = mean + delta / n
    delta2 = port_ret - mean
    M2 = M2 + delta * delta2

    state["n"] = n
    state["mean"] = mean
    state["M2"] = M2

    # Compute online Sharpe-like signal
    if n < 2:
        # Not enough data yet: use raw return only
        sharpe_signal = port_ret
    else:
        variance = M2 / (n - 1)
        std = np.sqrt(variance) if variance > 1e-12 else 1e-6
        # Annualized Sharpe approximation (daily steps assumed ~252)
        sharpe_signal = (mean / std) * np.sqrt(252)

    # Turnover penalty: L1 distance between current and previous weights
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.001 * turnover

    # Tail loss penalty: penalize large negative returns (CVaR-like)
    # Use exponential penalty for very bad steps
    tail_penalty = 0.0
    if port_ret < -0.02:  # worse than -2%
        tail_penalty = 5.0 * (port_ret + 0.02) ** 2

    # Concentration penalty: encourage diversification via entropy
    # Avoid degenerate all-cash or all-one-asset portfolios
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    max_entropy = np.log(len(weights))
    concentration_penalty = 0.01 * (max_entropy - entropy) / (max_entropy + 1e-8)

    # Primary reward: blend of immediate return signal and running Sharpe
    # Weight Sharpe more as we accumulate data
    sharpe_weight = min(0.8, n / 100.0 * 0.8)
    ret_weight = 1.0 - sharpe_weight

    primary = sharpe_weight * np.tanh(sharpe_signal * 0.1) + ret_weight * np.tanh(port_ret * 10.0)

    total = primary - turnover_penalty - tail_penalty - concentration_penalty

    components = {
        "sharpe_signal": float(sharpe_signal),
        "primary": float(primary),
        "turnover_penalty": float(turnover_penalty),
        "tail_penalty": float(tail_penalty),
        "concentration_penalty": float(concentration_penalty),
        "port_ret": float(port_ret),
        "running_mean": float(mean),
        "running_std": float(np.sqrt(M2 / max(n - 1, 1))),
    }

    return float(total), components, state
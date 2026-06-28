def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve reward state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "n": 0,
            "mean_ret": 0.0,
            "M2": 0.0,  # for Welford's online variance
        }

    # Unpack state
    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_ret = state["cum_ret"]
    n = state["n"]
    mean_ret = state["mean_ret"]
    M2 = state["M2"]

    # Update cumulative return and drawdown
    cum_ret = cum_ret + port_ret  # approximate log-sum
    peak = max(peak, cum_ret)
    drawdown = peak - cum_ret  # >= 0

    # Welford online mean and variance
    n += 1
    delta = port_ret - mean_ret
    mean_ret = mean_ret + delta / n
    delta2 = port_ret - mean_ret
    M2 = M2 + delta * delta2

    # Store return history (rolling window for tail risk)
    ret_history.append(port_ret)
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # Compute online Sharpe contribution
    if n >= 5:
        variance = M2 / n  # population variance
        std = np.sqrt(variance) if variance > 1e-10 else 1e-5
        sharpe_approx = mean_ret / std
    else:
        sharpe_approx = 0.0

    # CVaR-like tail risk penalty (worst 10% of rolling window)
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        cutoff = int(np.ceil(0.1 * len(arr)))
        tail_losses = np.sort(arr)[:cutoff]
        cvar = np.mean(tail_losses)  # negative means loss
        tail_penalty = min(0.0, cvar)  # penalize negative tail mean
    else:
        tail_penalty = 0.0

    # Turnover penalty (encourages stability)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.05 * turnover

    # Drawdown penalty (scaled)
    drawdown_penalty = 0.5 * drawdown

    # Concentration penalty (encourage diversification via entropy)
    w_noncash = weights[:-1]  # exclude cash if last element is cash
    w_safe = np.clip(w_noncash, 1e-8, 1.0)
    w_safe = w_safe / w_safe.sum()
    entropy = -np.sum(w_safe * np.log(w_safe))
    max_entropy = np.log(len(w_safe)) if len(w_safe) > 1 else 1.0
    norm_entropy = entropy / max_entropy
    concentration_penalty = 0.1 * (1.0 - norm_entropy)

    # Composite reward
    # Core: smoothed Sharpe direction + current return
    core = 0.5 * port_ret + 0.5 * sharpe_approx * 0.01
    total = (core
             - turnover_penalty
             - drawdown_penalty * 0.1
             + tail_penalty * 0.3
             - concentration_penalty)

    components = {
        "port_ret": port_ret,
        "sharpe_approx": sharpe_approx,
        "tail_penalty": tail_penalty,
        "turnover_penalty": turnover_penalty,
        "drawdown_penalty": drawdown_penalty,
        "concentration_penalty": concentration_penalty,
        "core": core,
    }

    state["ret_history"] = ret_history
    state["peak"] = peak
    state["cum_ret"] = cum_ret
    state["n"] = n
    state["mean_ret"] = mean_ret
    state["M2"] = M2

    return total, components, state
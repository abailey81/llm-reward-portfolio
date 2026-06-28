def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_mean": 0.0,
            "ret_var": 1e-8,
            "n": 0,
            "peak_value": 1.0,
            "portfolio_value": 1.0,
            "downside_var": 1e-8,
            "n_downside": 0,
        }

    # Update portfolio value
    portfolio_value = state["portfolio_value"] * (1.0 + port_ret)
    peak_value = max(state["peak_value"], portfolio_value)

    # Online update of mean and variance (Welford's)
    n = state["n"] + 1
    old_mean = state["ret_mean"]
    new_mean = old_mean + (port_ret - old_mean) / n
    old_var = state["ret_var"]
    # Welford variance update
    new_var = old_var + ((port_ret - old_mean) * (port_ret - new_mean) - old_var) / n
    new_var = max(new_var, 1e-8)

    # Online downside variance (returns below 0)
    n_down = state["n_downside"]
    down_var = state["downside_var"]
    if port_ret < 0.0:
        n_down += 1
        down_var = down_var + ((port_ret ** 2) - down_var) / n_down
    down_var = max(down_var, 1e-8)

    # --- Reward components ---

    # 1. Online Sharpe contribution (differential Sharpe-like)
    sharpe_est = new_mean / np.sqrt(new_var)
    # Scale to be roughly in [-3, 3]
    sharpe_reward = np.clip(sharpe_est, -3.0, 3.0)

    # 2. Drawdown penalty
    drawdown = (peak_value - portfolio_value) / (peak_value + 1e-8)
    drawdown_penalty = -np.clip(drawdown, 0.0, 1.0) * 2.0

    # 3. Turnover penalty (transaction cost proxy)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover

    # 4. Downside risk penalty (Sortino-inspired)
    sortino_est = new_mean / np.sqrt(down_var)
    sortino_reward = np.clip(sortino_est, -3.0, 3.0) * 0.5

    # 5. Concentration penalty (encourage diversification slightly)
    # Herfindahl index
    hhi = np.sum(weights ** 2)
    concentration_penalty = -0.2 * hhi

    # Combine: primary signal is Sharpe + Sortino, with risk penalties
    # During warm-up (n < 20), rely more on raw return to bootstrap
    if n < 20:
        warm_weight = (20 - n) / 20.0
        raw_ret_signal = np.clip(port_ret * 50.0, -2.0, 2.0)  # scale raw return
        base_signal = warm_weight * raw_ret_signal + (1.0 - warm_weight) * sharpe_reward
    else:
        base_signal = sharpe_reward

    total = (
        base_signal
        + 0.5 * sortino_reward
        + drawdown_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "sharpe_reward": float(sharpe_reward),
        "sortino_reward": float(0.5 * sortino_reward),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
        "port_ret": float(port_ret),
        "n_steps": float(n),
    }

    reward_state = {
        "ret_mean": new_mean,
        "ret_var": new_var,
        "n": n,
        "peak_value": peak_value,
        "portfolio_value": portfolio_value,
        "downside_var": down_var,
        "n_downside": n_down,
    }

    return float(total), components, reward_state
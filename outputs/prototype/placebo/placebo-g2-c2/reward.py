def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize reward state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cumulative": 1.0,
            "n": 0,
            "running_mean": 0.0,
            "running_m2": 0.0,  # for Welford's online variance
        }

    # Update cumulative return and drawdown tracking
    state["cumulative"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cumulative"])
    drawdown = (state["peak"] - state["cumulative"]) / (state["peak"] + 1e-8)

    # Welford's online mean and variance for Sharpe
    state["n"] += 1
    n = state["n"]
    delta = port_ret - state["running_mean"]
    state["running_mean"] += delta / n
    delta2 = port_ret - state["running_mean"]
    state["running_m2"] += delta * delta2

    mean_ret = state["running_mean"]
    if n >= 2:
        variance = state["running_m2"] / (n - 1)
        std_ret = np.sqrt(max(variance, 1e-10))
    else:
        std_ret = 1e-5

    # Keep a rolling window for tail risk (CVaR)
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > 60:
        state["ret_history"].pop(0)

    hist = np.array(state["ret_history"])
    # CVaR: mean of worst 10% returns
    if len(hist) >= 10:
        cutoff = int(max(1, 0.10 * len(hist)))
        sorted_hist = np.sort(hist)
        cvar = np.mean(sorted_hist[:cutoff])
    else:
        cvar = port_ret

    # Turnover cost penalty
    turnover = np.sum(np.abs(weights - prev_weights))

    # --- Reward components ---
    # 1. Incremental Sharpe contribution (annualized style, step-wise)
    sharpe_reward = port_ret / (std_ret + 1e-8)

    # 2. Drawdown penalty (convex to penalize large drawdowns more)
    dd_penalty = 2.0 * drawdown ** 2

    # 3. Tail risk penalty
    cvar_penalty = max(0.0, -cvar) * 3.0

    # 4. Turnover penalty (mild)
    turnover_penalty = 0.05 * turnover

    # 5. Direct return signal (scaled)
    ret_signal = port_ret * 10.0

    total = ret_signal + sharpe_reward - dd_penalty - cvar_penalty - turnover_penalty

    components = {
        "ret_signal": ret_signal,
        "sharpe_reward": sharpe_reward,
        "dd_penalty": -dd_penalty,
        "cvar_penalty": -cvar_penalty,
        "turnover_penalty": -turnover_penalty,
        "port_ret": port_ret,
        "drawdown": drawdown,
    }

    return float(total), components, state
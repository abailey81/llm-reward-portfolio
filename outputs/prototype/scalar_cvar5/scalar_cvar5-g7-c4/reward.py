def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
        }

    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_value = state["cum_value"]

    # Update cumulative value and drawdown tracking
    cum_value = cum_value * (1.0 + port_ret)
    if cum_value > peak:
        peak = cum_value
    drawdown = (peak - cum_value) / (peak + 1e-8)

    # Store return
    ret_history.append(port_ret)
    # Keep rolling window
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    ret_arr = np.array(ret_history)

    # --- Core components ---

    # 1. Online Sharpe contribution (annualized daily)
    if len(ret_arr) >= 5:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr, ddof=1) + 1e-8
        sharpe_approx = mu / sigma  # per-step Sharpe
        sharpe_signal = np.clip(sharpe_approx, -3.0, 3.0) * 0.5
    else:
        sharpe_signal = port_ret

    # 2. CVaR penalty (Expected Shortfall at 5%)
    if len(ret_arr) >= 10:
        sorted_rets = np.sort(ret_arr)
        cutoff_idx = max(1, int(np.floor(0.05 * len(ret_arr))))
        cvar_5 = np.mean(sorted_rets[:cutoff_idx])
        # Penalize negative CVaR (tail losses)
        cvar_penalty = np.clip(cvar_5, -1.0, 0.0) * 2.0
    else:
        cvar_penalty = 0.0

    # 3. Drawdown penalty - penalize being in drawdown
    dd_penalty = -drawdown * 0.5

    # 4. Turnover penalty (transaction costs already in port_ret, but extra regularization)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.005 * turnover

    # 5. Concentration penalty - encourage diversification but not force it
    # Herfindahl index on risky weights (exclude cash = last element)
    risky_weights = weights[:-1] if len(weights) > 1 else weights
    hhi = np.sum(risky_weights ** 2)
    concentration_penalty = -0.05 * hhi

    # --- Total reward ---
    total = (
        sharpe_signal
        + cvar_penalty
        + dd_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "sharpe_signal": sharpe_signal,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "port_ret": port_ret,
        "drawdown": drawdown,
    }

    state["ret_history"] = ret_history
    state["peak"] = peak
    state["cum_value"] = cum_value

    return float(total), components, state
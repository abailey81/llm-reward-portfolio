def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # Retrieve or initialize reward state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "cum_ret": 1.0,
            "peak": 1.0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "step": 0,
        }

    state["step"] += 1
    step = state["step"]

    # Update cumulative return and drawdown tracking
    state["cum_ret"] *= (1.0 + port_ret)
    if state["cum_ret"] > state["peak"]:
        state["peak"] = state["cum_ret"]
    drawdown = (state["cum_ret"] - state["peak"]) / (state["peak"] + 1e-8)

    # Append to return history (rolling window)
    history = state["ret_history"]
    history.append(port_ret)
    window = 120
    if len(history) > window:
        history.pop(0)

    # EMA-based Sharpe estimation
    alpha = 0.05
    state["ema_mean"] = (1 - alpha) * state["ema_mean"] + alpha * port_ret
    state["ema_var"] = (1 - alpha) * state["ema_var"] + alpha * (port_ret - state["ema_mean"]) ** 2
    ema_std = np.sqrt(state["ema_var"] + 1e-8)
    ema_sharpe = state["ema_mean"] / ema_std

    # --- Component 1: EMA Sharpe signal ---
    sharpe_reward = np.clip(ema_sharpe, -3.0, 3.0) * 0.03

    # --- Component 2: Direct return (scaled) ---
    ret_reward = port_ret * 5.0

    # --- Component 3: CVaR penalty from rolling history ---
    cvar_penalty = 0.0
    if len(history) >= 20:
        arr = np.array(history)
        sorted_arr = np.sort(arr)
        n = len(sorted_arr)
        # CVaR at 10% level
        cutoff = max(1, int(np.floor(0.10 * n)))
        cvar_10 = np.mean(sorted_arr[:cutoff])
        # Penalize bad CVaR (negative values hurt)
        cvar_penalty = np.clip(cvar_10, -0.1, 0.0) * 8.0

    # --- Component 4: Drawdown penalty ---
    dd_penalty = drawdown * 2.0  # drawdown is <= 0, so this is negative

    # --- Component 5: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.005 * turnover

    # --- Component 6: Concentration penalty (encourage diversification) ---
    # Penalize high Herfindahl index (excluding cash, last element)
    asset_weights = weights[:-1] if len(weights) > 1 else weights
    herfindahl = np.sum(asset_weights ** 2)
    concentration_penalty = -0.01 * np.clip(herfindahl - 0.2, 0.0, None)

    total = (
        ret_reward
        + sharpe_reward
        + cvar_penalty
        + dd_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "ret_reward": ret_reward,
        "sharpe_reward": sharpe_reward,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    state["ret_history"] = history
    return float(total), components, state
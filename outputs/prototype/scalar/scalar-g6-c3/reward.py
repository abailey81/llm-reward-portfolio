def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
        }

    ret_history = state["ret_history"]
    ret_history.append(port_ret)

    # Keep a rolling window for Sharpe estimation
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    state["ret_history"] = ret_history

    # --- Cumulative return & drawdown ---
    state["cum_ret"] = state["cum_ret"] + port_ret
    cum_val = state["cum_ret"]
    state["peak"] = max(state["peak"], cum_val)
    drawdown = state["peak"] - cum_val  # >= 0

    # --- Online Sharpe (annualized, scaled) ---
    n = len(ret_history)
    if n >= 5:
        arr = np.array(ret_history)
        mu = np.mean(arr)
        sigma = np.std(arr, ddof=1) + 1e-8
        sharpe = mu / sigma  # per-step Sharpe
    else:
        sharpe = 0.0

    # --- Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.05 * turnover

    # --- Tail / drawdown penalty ---
    drawdown_penalty = 0.1 * drawdown

    # --- Downside deviation penalty (Sortino-style) ---
    if n >= 5:
        arr = np.array(ret_history)
        downside = arr[arr < 0]
        if len(downside) > 1:
            semi_std = np.std(downside, ddof=1) + 1e-8
            sortino_adj = np.mean(arr) / semi_std
        else:
            sortino_adj = sharpe
    else:
        sortino_adj = 0.0

    # --- Combine: blend Sharpe + Sortino, penalize turnover & drawdown ---
    core = 0.5 * sharpe + 0.5 * sortino_adj
    total = core - turnover_penalty - drawdown_penalty

    components = {
        "sharpe_contrib": sharpe,
        "sortino_contrib": sortino_adj,
        "turnover_penalty": -turnover_penalty,
        "drawdown_penalty": -drawdown_penalty,
        "port_ret": port_ret,
    }

    return float(total), components, state
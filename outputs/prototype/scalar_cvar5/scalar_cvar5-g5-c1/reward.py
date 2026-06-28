def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # Initialize reward state
    state = info.get("reward_state") if info is not None else None
    if state is None:
        state = {
            "returns_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
        }

    # Update cumulative return and history
    state["returns_history"].append(float(port_ret))
    state["cum_ret"] += float(port_ret)
    hist = np.array(state["returns_history"], dtype=float)

    # Update peak for drawdown
    state["peak"] = max(state["peak"], state["cum_ret"])
    drawdown = state["peak"] - state["cum_ret"]

    # --- Component 1: Base return ---
    ret_component = float(port_ret)

    # --- Component 2: Online Sharpe (rolling window) ---
    window = 60
    recent = hist[-window:] if len(hist) >= window else hist
    sharpe_component = 0.0
    if len(recent) >= 8:
        mu = np.mean(recent)
        sigma = np.std(recent) + 1e-8
        sharpe_component = float(mu / sigma) * 0.1  # scaled

    # --- Component 3: CVaR penalty (tail risk) ---
    cvar_penalty = 0.0
    if len(hist) >= 20:
        sorted_ret = np.sort(recent)
        cutoff = max(1, int(len(sorted_ret) * 0.05))
        cvar = np.mean(sorted_ret[:cutoff])
        # Penalize negative CVaR (bad tail)
        cvar_penalty = float(min(0.0, cvar)) * 2.0

    # --- Component 4: Drawdown penalty ---
    drawdown_penalty = -float(drawdown) * 0.5

    # --- Component 5: Downside deviation (Sortino-like) ---
    sortino_component = 0.0
    if len(recent) >= 8:
        downside = recent[recent < 0.0]
        if len(downside) > 0:
            downside_std = np.sqrt(np.mean(downside**2)) + 1e-8
            sortino_component = float(np.mean(recent)) / downside_std * 0.05

    # --- Component 6: Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -turnover * 0.002

    # --- Total reward ---
    total = (
        ret_component
        + sharpe_component
        + cvar_penalty
        + drawdown_penalty
        + sortino_component
        + turnover_penalty
    )

    components = {
        "ret": ret_component,
        "sharpe": sharpe_component,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "sortino": sortino_component,
        "turnover_penalty": turnover_penalty,
    }

    return float(total), components, state
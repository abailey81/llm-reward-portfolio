def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "step": 0,
        }

    state["step"] += 1
    state["returns_history"].append(port_ret)
    state["cum_ret"] = (1 + state["cum_ret"]) * (1 + port_ret) - 1
    state["peak"] = max(state["peak"], state["cum_ret"])

    hist = np.array(state["returns_history"])
    n = len(hist)

    # --- Component 1: Base return signal (dampened) ---
    base_ret = np.tanh(port_ret * 20) * 0.05

    # --- Component 2: Online Sharpe (rolling, annualized approx) ---
    sharpe_reward = 0.0
    if n >= 10:
        mu = np.mean(hist)
        sigma = np.std(hist) + 1e-8
        sharpe = mu / sigma
        # Normalize to reasonable scale
        sharpe_reward = np.tanh(sharpe * 2) * 0.1

    # --- Component 3: CVaR penalty (tail risk) ---
    cvar_penalty = 0.0
    if n >= 20:
        threshold = int(np.ceil(0.05 * n))
        threshold = max(1, threshold)
        sorted_ret = np.sort(hist)
        cvar_5 = np.mean(sorted_ret[:threshold])
        # Penalize bad CVaR
        cvar_penalty = np.tanh(cvar_5 * 30) * 0.1  # negative if cvar_5 < 0

    # --- Component 4: Drawdown penalty ---
    drawdown = state["peak"] - state["cum_ret"]
    drawdown_penalty = -np.tanh(drawdown * 10) * 0.05

    # --- Component 5: Turnover penalty (transaction costs proxy) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -np.tanh(turnover * 2) * 0.03

    # --- Component 6: Concentration penalty (encourage diversification) ---
    # Penalize extreme concentration (high Herfindahl index)
    herfindahl = np.sum(weights ** 2)
    n_assets = len(weights)
    # Normalized: 0 (equal weight) to 1 (full concentration)
    min_herf = 1.0 / n_assets
    normalized_herf = (herfindahl - min_herf) / (1.0 - min_herf + 1e-8)
    concentration_penalty = -normalized_herf * 0.02

    # --- Component 7: Downside deviation penalty (Sortino-like) ---
    sortino_reward = 0.0
    if n >= 10:
        neg_rets = hist[hist < 0]
        if len(neg_rets) > 1:
            downside_std = np.std(neg_rets) + 1e-8
            mu = np.mean(hist)
            sortino = mu / downside_std
            sortino_reward = np.tanh(sortino * 2) * 0.05

    total = (
        base_ret
        + sharpe_reward
        + cvar_penalty
        + drawdown_penalty
        + turnover_penalty
        + concentration_penalty
        + sortino_reward
    )

    components = {
        "base_ret": base_ret,
        "sharpe_reward": sharpe_reward,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "sortino_reward": sortino_reward,
    }

    return float(total), components, state
def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "max_port_value": 1.0,
            "port_value": 1.0,
            "step": 0,
        }

    state["step"] += 1

    # Update portfolio value
    state["port_value"] = state["port_value"] * (1.0 + port_ret)
    if state["port_value"] > state["max_port_value"]:
        state["max_port_value"] = state["port_value"]

    # Store return history (rolling window)
    window = 60
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > window:
        state["ret_history"].pop(0)

    ret_arr = np.array(state["ret_history"])
    n = len(ret_arr)

    # --- Component 1: Immediate return signal ---
    ret_signal = port_ret

    # --- Component 2: Rolling Sharpe (annualized-ish) ---
    sharpe_signal = 0.0
    if n >= 5:
        mean_r = np.mean(ret_arr)
        std_r = np.std(ret_arr) + 1e-8
        sharpe_signal = mean_r / std_r  # rolling Sharpe (unscaled)

    # --- Component 3: CVaR penalty (Expected Shortfall at 5%) ---
    cvar_penalty = 0.0
    if n >= 10:
        alpha = 0.05
        k = max(1, int(np.floor(alpha * n)))
        sorted_rets = np.sort(ret_arr)
        tail = sorted_rets[:k]
        cvar = np.mean(tail)  # negative in bad scenarios
        cvar_penalty = min(0.0, cvar)  # only penalize losses

    # --- Component 4: Drawdown penalty ---
    drawdown = 0.0
    if state["max_port_value"] > 0:
        drawdown = (state["port_value"] - state["max_port_value"]) / state["max_port_value"]
    drawdown_penalty = min(0.0, drawdown)  # only negative

    # --- Component 5: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover * 0.01  # light penalty

    # --- Component 6: Concentration penalty (entropy-based) ---
    # Encourage diversification
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    max_entropy = np.log(len(weights))
    concentration_penalty = -0.02 * (max_entropy - entropy) / (max_entropy + 1e-8)

    # --- Combine ---
    # Weight sharpe heavily, with tail-risk and drawdown penalties
    w_ret = 0.3
    w_sharpe = 0.5
    w_cvar = 2.0
    w_dd = 0.5
    w_turn = 1.0
    w_conc = 1.0

    total = (
        w_ret * ret_signal
        + w_sharpe * sharpe_signal
        + w_cvar * cvar_penalty
        + w_dd * drawdown_penalty
        + w_turn * turnover_penalty
        + w_conc * concentration_penalty
    )

    components = {
        "ret_signal": float(w_ret * ret_signal),
        "sharpe_signal": float(w_sharpe * sharpe_signal),
        "cvar_penalty": float(w_cvar * cvar_penalty),
        "drawdown_penalty": float(w_dd * drawdown_penalty),
        "turnover_penalty": float(w_turn * turnover_penalty),
        "concentration_penalty": float(w_conc * concentration_penalty),
    }

    return float(total), components, state
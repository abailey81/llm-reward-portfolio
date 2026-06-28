def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "peak": 1.0,
            "cumulative": 1.0,
            "step": 0,
        }

    state["step"] += 1
    state["cumulative"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cumulative"])

    # Rolling window for statistics
    window = 60
    hist = state["returns_history"]
    hist.append(port_ret)
    if len(hist) > window:
        hist.pop(0)
    state["returns_history"] = hist

    n = len(hist)

    # --- Component 1: Baseline return signal ---
    ret_component = port_ret

    # --- Component 2: Online Sharpe contribution ---
    if n >= 5:
        arr = np.array(hist)
        mean_r = np.mean(arr)
        std_r = np.std(arr) + 1e-8
        sharpe_component = mean_r / std_r
    else:
        sharpe_component = 0.0

    # --- Component 3: CVaR penalty (tail risk) ---
    # Penalize based on rolling tail losses
    if n >= 10:
        arr = np.array(hist)
        cvar_level = 0.05
        cutoff = max(1, int(np.floor(cvar_level * n)))
        sorted_r = np.sort(arr)
        cvar_est = np.mean(sorted_r[:cutoff])
        # Penalty: negative CVaR (CVaR is negative when losses occur)
        cvar_penalty = min(0.0, cvar_est)  # Only penalize losses
    else:
        cvar_penalty = 0.0

    # --- Component 4: Drawdown penalty ---
    drawdown = (state["cumulative"] - state["peak"]) / (state["peak"] + 1e-8)
    # Convex penalty: hurts more the deeper the drawdown
    dd_penalty = min(0.0, drawdown) ** 2 * np.sign(drawdown)  # negative squared

    # --- Component 5: Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.002 * turnover  # small but consistent friction

    # --- Component 6: Diversification bonus ---
    # Entropy of weights (excluding cash if last element) to encourage spread
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    max_entropy = np.log(len(weights))
    diversification_bonus = 0.01 * (entropy / (max_entropy + 1e-8))

    # --- Component 7: Downside deviation penalty ---
    if n >= 5:
        arr = np.array(hist)
        downside = arr[arr < 0.0]
        if len(downside) > 0:
            downside_dev = np.sqrt(np.mean(downside ** 2))
            sortino_component = (np.mean(arr) / (downside_dev + 1e-8))
        else:
            sortino_component = sharpe_component  # no downside
    else:
        sortino_component = 0.0

    # --- Combine components with tuned weights ---
    # Primary: Sharpe/Sortino blend
    # Secondary: CVaR and drawdown risk penalties
    risk_adjusted_signal = 0.5 * sharpe_component + 0.5 * sortino_component

    total = (
        0.4  * ret_component
        + 0.3  * risk_adjusted_signal
        + 2.0  * cvar_penalty          # strong CVaR penalty
        + 1.0  * dd_penalty            # drawdown penalty
        + turnover_penalty
        + diversification_bonus
    )

    components = {
        "ret": ret_component,
        "sharpe_contrib": sharpe_component,
        "sortino_contrib": sortino_component,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "diversification": diversification_bonus,
    }

    return float(total), components, state
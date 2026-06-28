def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve reward state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "portfolio_value": 1.0,
            "peak_value": 1.0,
            "ema_ret": 0.0,
            "ema_sq_ret": 0.0,
            "ema_alpha": 0.05,   # smoothing factor for EMA
            "step": 0,
        }

    state["step"] += 1
    alpha = state["ema_alpha"]
    step = state["step"]

    # --- Update portfolio value and drawdown ---
    state["portfolio_value"] *= (1.0 + port_ret)
    pv = state["portfolio_value"]
    if pv > state["peak_value"]:
        state["peak_value"] = pv
    drawdown = (state["peak_value"] - pv) / (state["peak_value"] + 1e-8)

    # --- Online EMA-based Sharpe estimation ---
    state["ema_ret"] = alpha * port_ret + (1.0 - alpha) * state["ema_ret"]
    state["ema_sq_ret"] = alpha * (port_ret ** 2) + (1.0 - alpha) * state["ema_sq_ret"]

    ema_ret = state["ema_ret"]
    ema_sq_ret = state["ema_sq_ret"]
    ema_var = max(ema_sq_ret - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)

    # Annualized (252 steps/year assumed)
    sharpe_est = (ema_ret / ema_std) * np.sqrt(252)

    # --- Turnover penalty (transaction costs proxy) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover

    # --- Downside / tail risk penalty ---
    # Penalize negative returns more strongly (Sortino-like)
    downside_penalty = 0.0
    if port_ret < 0:
        downside_penalty = 2.0 * (port_ret ** 2)

    # --- Drawdown penalty ---
    drawdown_penalty = 0.5 * (drawdown ** 2)

    # --- Concentration penalty: discourage extreme concentration ---
    # Entropy-based: encourage diversification
    w_clip = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clip * np.log(w_clip))
    max_entropy = np.log(len(weights))
    concentration_penalty = 0.05 * (1.0 - entropy / (max_entropy + 1e-8))

    # --- Primary reward: blend return signal and Sharpe signal ---
    # Use a warm-up: initially weight raw returns, then shift to Sharpe
    warmup = min(step / 50.0, 1.0)
    base_reward = (1.0 - warmup) * port_ret + warmup * (ema_ret + 0.1 * sharpe_est)

    # --- Combine components ---
    total = (
        base_reward
        - turnover_penalty
        - downside_penalty
        - drawdown_penalty
        - concentration_penalty
    )

    components = {
        "base_reward": base_reward,
        "sharpe_est": sharpe_est,
        "turnover_penalty": -turnover_penalty,
        "downside_penalty": -downside_penalty,
        "drawdown_penalty": -drawdown_penalty,
        "concentration_penalty": -concentration_penalty,
        "port_ret": port_ret,
        "drawdown": drawdown,
    }

    return float(total), components, state
def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_sq_ret": 0.0,
            "alpha": 0.05,          # EMA decay for ~20-step memory
            "peak": 1.0,
            "cumulative": 1.0,
            "step": 0,
            "ema_ret_slow": 0.0,
            "ema_sq_ret_slow": 0.0,
            "alpha_slow": 0.01,     # ~100-step memory
        }

    alpha = state["alpha"]
    alpha_slow = state["alpha_slow"]
    step = state["step"] + 1

    # Update EMA statistics (fast)
    ema_ret = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    ema_sq_ret = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq_ret"]

    # Update EMA statistics (slow)
    ema_ret_slow = alpha_slow * port_ret + (1 - alpha_slow) * state["ema_ret_slow"]
    ema_sq_ret_slow = alpha_slow * (port_ret ** 2) + (1 - alpha_slow) * state["ema_sq_ret_slow"]

    # Bias-corrected estimates
    bc_fast = 1.0 - (1 - alpha) ** step
    bc_slow = 1.0 - (1 - alpha_slow) ** step

    mean_fast = ema_ret / bc_fast
    sq_fast = ema_sq_ret / bc_fast
    var_fast = max(sq_fast - mean_fast ** 2, 1e-8)
    std_fast = np.sqrt(var_fast)

    mean_slow = ema_ret_slow / bc_slow
    sq_slow = ema_sq_ret_slow / bc_slow
    var_slow = max(sq_slow - mean_slow ** 2, 1e-8)
    std_slow = np.sqrt(var_slow)

    # Sharpe components (annualized ~252 steps)
    sharpe_fast = mean_fast / std_fast
    sharpe_slow = mean_slow / std_slow

    # Blend fast and slow Sharpe for stability
    blend = min(step / 50.0, 1.0)  # ramp from fast to blended
    sharpe_signal = (1 - blend) * sharpe_fast + blend * (0.4 * sharpe_fast + 0.6 * sharpe_slow)

    # Drawdown penalty
    cumulative = state["cumulative"] * (1.0 + port_ret)
    peak = max(state["peak"], cumulative)
    drawdown = (peak - cumulative) / (peak + 1e-8)
    drawdown_penalty = drawdown ** 2  # quadratic penalty

    # Tail loss penalty (downside): penalize returns below -1.5 * std
    downside_threshold = -1.5 * std_fast
    tail_penalty = min(port_ret - downside_threshold, 0.0) ** 2 if port_ret < downside_threshold else 0.0

    # Turnover cost penalty (discourages excessive rebalancing)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover

    # Concentration penalty (encourage diversification slightly)
    n_assets = len(weights)
    concentration = np.sum(weights ** 2)  # Herfindahl index
    max_concentration = 1.0
    min_concentration = 1.0 / n_assets
    norm_concentration = (concentration - min_concentration) / (max_concentration - min_concentration + 1e-8)
    concentration_penalty = 0.05 * norm_concentration

    # Primary reward: port_ret (direct) + sharpe_signal scaled down
    # Keep port_ret dominant so agent learns to make money
    r_return = port_ret
    r_sharpe = 0.02 * sharpe_signal
    r_drawdown = -0.5 * drawdown_penalty
    r_tail = -1.0 * tail_penalty
    r_turnover = -turnover_penalty
    r_concentration = -concentration_penalty

    total = r_return + r_sharpe + r_drawdown + r_tail + r_turnover + r_concentration

    components = {
        "r_return": r_return,
        "r_sharpe": r_sharpe,
        "r_drawdown": r_drawdown,
        "r_tail": r_tail,
        "r_turnover": r_turnover,
        "r_concentration": r_concentration,
        "sharpe_fast": sharpe_fast,
        "sharpe_slow": sharpe_slow,
        "drawdown": drawdown,
        "turnover": turnover,
    }

    state["ema_ret"] = ema_ret
    state["ema_sq_ret"] = ema_sq_ret
    state["ema_ret_slow"] = ema_ret_slow
    state["ema_sq_ret_slow"] = ema_sq_ret_slow
    state["peak"] = peak
    state["cumulative"] = cumulative
    state["step"] = step

    return total, components, state
def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "alpha": 0.05,           # EMA decay for ~20-step window
            "alpha_slow": 0.02,      # slower EMA for ~50-step window
            "ema_ret_slow": 0.0,
            "ema_sq_slow": 0.0,
            "ret_history": [],
            "max_cum": 0.0,
            "cum_ret": 0.0,
            "step": 0,
        }

    alpha = state["alpha"]
    alpha_slow = state["alpha_slow"]
    step = state["step"]

    # Update EMAs for fast Sharpe
    state["ema_ret"] = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    state["ema_sq"] = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq"]

    # Update EMAs for slow Sharpe
    state["ema_ret_slow"] = alpha_slow * port_ret + (1 - alpha_slow) * state["ema_ret_slow"]
    state["ema_sq_slow"] = alpha_slow * (port_ret ** 2) + (1 - alpha_slow) * state["ema_sq_slow"]

    # Bias correction
    bc_fast = 1.0 - (1 - alpha) ** (step + 1)
    bc_slow = 1.0 - (1 - alpha_slow) ** (step + 1)

    mu_fast = state["ema_ret"] / bc_fast
    sq_fast = state["ema_sq"] / bc_fast
    var_fast = max(sq_fast - mu_fast ** 2, 1e-8)
    std_fast = np.sqrt(var_fast)

    mu_slow = state["ema_ret_slow"] / bc_slow
    sq_slow = state["ema_sq_slow"] / bc_slow
    var_slow = max(sq_slow - mu_slow ** 2, 1e-8)
    std_slow = np.sqrt(var_slow)

    # Online Sharpe (blend fast and slow for stability)
    sharpe_fast = mu_fast / std_fast
    sharpe_slow = mu_slow / std_slow
    sharpe_blend = 0.5 * sharpe_fast + 0.5 * sharpe_slow

    # Rolling return history for CVaR (keep last 60 steps)
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > 60:
        state["ret_history"].pop(0)

    # CVaR penalty (expected shortfall at 10%)
    cvar_penalty = 0.0
    if len(state["ret_history"]) >= 10:
        hist = np.array(state["ret_history"])
        cutoff = int(np.ceil(0.10 * len(hist)))
        sorted_rets = np.sort(hist)
        cvar_10 = np.mean(sorted_rets[:cutoff])  # negative number if losses
        cvar_penalty = min(cvar_10, 0.0)  # only penalize negative CVaR

    # Drawdown penalty
    state["cum_ret"] = state["cum_ret"] + port_ret  # log-approx cumulative
    if state["cum_ret"] > state["max_cum"]:
        state["max_cum"] = state["cum_ret"]
    drawdown = state["cum_ret"] - state["max_cum"]  # <= 0
    drawdown_penalty = min(drawdown, 0.0)

    # Turnover penalty (L1 change in weights)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover

    # Concentration penalty (encourage diversification via entropy)
    # Exclude cash (last element) for concentration measure
    asset_weights = weights[:-1] if len(weights) > 1 else weights
    asset_weights_safe = np.clip(asset_weights, 1e-8, 1.0)
    entropy = -np.sum(asset_weights_safe * np.log(asset_weights_safe))
    max_entropy = np.log(max(len(asset_weights), 1))
    concentration_penalty = -0.1 * (1.0 - entropy / (max_entropy + 1e-8))

    # Combine components
    w_sharpe = 1.0
    w_cvar = 2.0
    w_drawdown = 0.5
    w_turnover = 1.0
    w_conc = 1.0

    total = (
        w_sharpe * sharpe_blend
        + w_cvar * cvar_penalty
        + w_drawdown * drawdown_penalty
        + w_turnover * turnover_penalty
        + w_conc * concentration_penalty
    )

    components = {
        "sharpe_blend": sharpe_blend,
        "sharpe_fast": sharpe_fast,
        "sharpe_slow": sharpe_slow,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "port_ret": port_ret,
    }

    state["step"] += 1
    return float(total), components, state
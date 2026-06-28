def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_ret": 1.0,
        }

    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_ret = state["cum_ret"]

    # Update cumulative return and peak
    cum_ret = cum_ret * (1.0 + port_ret)
    peak = max(peak, cum_ret)

    # Store return in history (keep last 60 steps)
    ret_history.append(port_ret)
    if len(ret_history) > 60:
        ret_history = ret_history[-60:]

    ret_arr = np.array(ret_history, dtype=np.float64)

    # --- Component 1: Sharpe-like signal ---
    # Use a small window for online estimate; need at least 5 obs
    n = len(ret_arr)
    if n >= 5:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr) + 1e-8
        sharpe_signal = mu / sigma
    else:
        sharpe_signal = port_ret  # fallback early on

    # --- Component 2: CVaR penalty (5% tail) ---
    if n >= 20:
        sorted_rets = np.sort(ret_arr)
        cutoff_idx = max(1, int(np.floor(0.05 * n)))
        cvar = np.mean(sorted_rets[:cutoff_idx])
        # Penalize negative CVaR
        cvar_penalty = min(0.0, cvar)
    else:
        cvar_penalty = 0.0

    # --- Component 3: Drawdown penalty ---
    drawdown = (cum_ret - peak) / (peak + 1e-8)
    # drawdown is <= 0; penalize proportionally
    drawdown_penalty = drawdown  # already negative or zero

    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover

    # --- Component 5: Diversification bonus (entropy of weights) ---
    # Encourage spread; cash included
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    max_entropy = np.log(len(weights) + 1e-8)
    diversity_bonus = 0.1 * (entropy / (max_entropy + 1e-8))

    # --- Combine ---
    # Scale components to keep total on a reasonable scale
    total = (
        2.0 * sharpe_signal       # dominant term: risk-adjusted return
        + 5.0 * cvar_penalty       # penalize tail losses
        + 1.0 * drawdown_penalty   # penalize drawdown
        + turnover_penalty         # penalize trading costs
        + diversity_bonus          # mild diversification
    )

    components = {
        "sharpe_signal": sharpe_signal,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "diversity_bonus": diversity_bonus,
    }

    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cum_ret": cum_ret,
    }

    return float(total), components, reward_state
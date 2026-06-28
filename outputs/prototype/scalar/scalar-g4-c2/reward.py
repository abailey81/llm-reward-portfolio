def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)

    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "step": 0,
            "peak": 1.0,
            "cum_value": 1.0,
        }

    state = reward_state
    state["step"] += 1
    step = state["step"]

    # Track cumulative value and drawdown
    state["cum_value"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_value"])

    # Store return history (keep last 60 steps)
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > 60:
        state["ret_history"].pop(0)

    # EMA-based mean and variance (alpha ~ 1/60 decay)
    alpha = 0.05
    state["ema_ret"] = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    state["ema_sq"] = (1 - alpha) * state["ema_sq"] + alpha * (port_ret ** 2)

    ema_mean = state["ema_ret"]
    ema_var = max(state["ema_sq"] - ema_mean ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)

    # --- Component 1: Online Sharpe (annualized roughly) ---
    sharpe_signal = ema_mean / ema_std if step > 5 else 0.0

    # --- Component 2: Tail risk penalty (CVaR on recent history) ---
    cvar_penalty = 0.0
    if len(state["ret_history"]) >= 10:
        hist = np.array(state["ret_history"])
        cutoff = int(len(hist) * 0.1) + 1  # worst 10%
        sorted_rets = np.sort(hist)
        tail = sorted_rets[:cutoff]
        cvar = np.mean(tail)  # negative number for losses
        cvar_penalty = min(cvar, 0.0)  # only penalize losses in tail

    # --- Component 3: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # --- Component 4: Drawdown penalty ---
    drawdown = (state["cum_value"] - state["peak"]) / state["peak"]
    dd_penalty = 0.5 * min(drawdown, 0.0)  # small penalty on current drawdown

    # --- Component 5: Direct return signal (scaled) ---
    # Give direct return signal for immediate feedback
    direct_ret = port_ret * 10.0  # scale up for gradient signal

    # Combine: weight Sharpe heavily, add tail/drawdown penalties
    total = (
        sharpe_signal * 1.0
        + cvar_penalty * 2.0
        + turnover_penalty
        + dd_penalty
        + direct_ret * 0.3
    )

    components = {
        "sharpe_signal": sharpe_signal,
        "cvar_penalty": cvar_penalty,
        "turnover_penalty": turnover_penalty,
        "dd_penalty": dd_penalty,
        "direct_ret": direct_ret,
    }

    return float(total), components, state
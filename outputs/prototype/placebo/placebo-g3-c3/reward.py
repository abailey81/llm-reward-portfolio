def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_ret": 1.0,
            "step": 0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "alpha": 0.05,  # EMA decay for mean/var
        }

    alpha = state["alpha"]
    step = state["step"]

    # Update cumulative return and drawdown tracking
    state["cum_ret"] *= (1.0 + port_ret)
    if state["cum_ret"] > state["peak"]:
        state["peak"] = state["cum_ret"]
    drawdown = (state["peak"] - state["cum_ret"]) / (state["peak"] + 1e-8)

    # EMA-based online mean and variance of port_ret
    old_mean = state["ema_mean"]
    state["ema_mean"] = (1 - alpha) * old_mean + alpha * port_ret
    state["ema_var"] = (1 - alpha) * state["ema_var"] + alpha * (port_ret - old_mean) ** 2
    ema_std = np.sqrt(max(state["ema_var"], 1e-8))

    # Keep a rolling window of returns for tail risk
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > 60:
        state["ret_history"].pop(0)

    hist = np.array(state["ret_history"])

    # Sharpe-like signal (annualized slightly)
    sharpe_signal = state["ema_mean"] / ema_std if step > 5 else 0.0

    # Drawdown penalty - penalize being in drawdown
    drawdown_penalty = -2.0 * drawdown

    # CVaR penalty: mean of worst 10% of returns in history
    if len(hist) >= 10:
        cutoff = int(np.ceil(0.1 * len(hist)))
        worst = np.sort(hist)[:cutoff]
        cvar = np.mean(worst)
        cvar_penalty = 2.0 * min(cvar, 0.0)  # only penalize negative CVaR
    else:
        cvar_penalty = 0.0

    # Concentration penalty (encourage diversification slightly)
    # Herfindahl index - penalize extreme concentration
    risky_weights = weights[:-1]  # exclude cash
    herfindahl = np.sum(risky_weights ** 2)
    concentration_penalty = -0.1 * herfindahl

    # Base return signal
    ret_signal = port_ret * 10.0  # scale up for gradient clarity

    # Combine components
    total = (
        ret_signal
        + 0.5 * sharpe_signal
        + drawdown_penalty
        + cvar_penalty
        + concentration_penalty
    )

    state["step"] += 1

    components = {
        "ret_signal": ret_signal,
        "sharpe_signal": sharpe_signal,
        "drawdown_penalty": drawdown_penalty,
        "cvar_penalty": cvar_penalty,
        "concentration_penalty": concentration_penalty,
    }

    return float(total), components, state
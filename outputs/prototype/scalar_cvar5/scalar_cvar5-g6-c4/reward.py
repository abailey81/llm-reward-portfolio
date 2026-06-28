def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Recover or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "step": 0,
        }

    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_value = state["cum_value"]
    ema_mean = state["ema_mean"]
    ema_var = state["ema_var"]
    step = state["step"]

    # --- Update cumulative portfolio value ---
    cum_value = cum_value * (1.0 + port_ret)
    peak = max(peak, cum_value)

    # --- Drawdown penalty ---
    drawdown = (peak - cum_value) / (peak + 1e-8)
    drawdown_penalty = -drawdown ** 1.5  # superlinear penalty for deep drawdowns

    # --- EMA-based Sharpe (fast, stateful) ---
    alpha = 0.05  # decay factor (~20-step half-life)
    ema_mean = alpha * port_ret + (1 - alpha) * ema_mean
    ema_var = alpha * (port_ret - ema_mean) ** 2 + (1 - alpha) * ema_var
    ema_std = np.sqrt(max(ema_var, 1e-8))
    ema_sharpe = ema_mean / ema_std

    # --- Rolling window for tail-risk (CVaR) ---
    ret_history.append(port_ret)
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        tail_pct = 0.05
        cutoff = np.quantile(arr, tail_pct)
        tail_returns = arr[arr <= cutoff]
        cvar = float(np.mean(tail_returns)) if len(tail_returns) > 0 else cutoff
        cvar_penalty = min(cvar, 0.0) * 3.0  # amplify tail-loss penalty
    else:
        cvar_penalty = 0.0

    # --- Turnover penalty (transaction cost proxy) ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.005 * turnover

    # --- Concentration penalty (encourage diversification) ---
    # Herfindahl index
    hhi = float(np.sum(weights ** 2))
    concentration_penalty = -0.02 * hhi

    # --- Core return component ---
    # Clip extreme returns to reduce reward hacking
    clipped_ret = np.clip(port_ret, -0.05, 0.05)

    # --- Step scaling: reduce noise in early steps ---
    step += 1
    ramp = min(1.0, step / 20.0)

    # --- Combine components ---
    sharpe_component = ramp * ema_sharpe * 0.1
    return_component = clipped_ret
    dd_component = ramp * drawdown_penalty * 0.5
    cvar_component = ramp * cvar_penalty
    to_component = turnover_penalty
    conc_component = ramp * concentration_penalty

    total = (
        return_component
        + sharpe_component
        + dd_component
        + cvar_component
        + to_component
        + conc_component
    )

    components = {
        "return": return_component,
        "ema_sharpe": sharpe_component,
        "drawdown": dd_component,
        "cvar": cvar_component,
        "turnover": to_component,
        "concentration": conc_component,
    }

    # --- Save state ---
    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cum_value": cum_value,
        "ema_mean": ema_mean,
        "ema_var": ema_var,
        "step": step,
    }

    return float(total), components, reward_state
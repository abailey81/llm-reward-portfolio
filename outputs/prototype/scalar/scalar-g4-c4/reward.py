def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ew_mean": 0.0,
            "ew_var": 1e-6,
            "peak": 1.0,
            "cumulative": 1.0,
            "ret_history": [],
            "decay": 0.97,
        }

    decay = state["decay"]
    ew_mean = state["ew_mean"]
    ew_var = state["ew_var"]
    peak = state["peak"]
    cumulative = state["cumulative"]
    ret_history = state["ret_history"]

    # Update cumulative return and drawdown
    cumulative = cumulative * (1.0 + port_ret)
    if cumulative > peak:
        peak = cumulative
    drawdown = (peak - cumulative) / (peak + 1e-8)

    # Update exponentially weighted mean and variance
    ew_mean = decay * ew_mean + (1.0 - decay) * port_ret
    ew_var = decay * ew_var + (1.0 - decay) * (port_ret - ew_mean) ** 2
    ew_std = np.sqrt(ew_var + 1e-8)

    # Annualized Sharpe-like signal (scaled to per-step)
    sharpe_signal = ew_mean / ew_std

    # Keep rolling history for CVaR tail penalty (last 50 steps)
    ret_history.append(port_ret)
    if len(ret_history) > 50:
        ret_history.pop(0)

    # CVaR tail penalty: mean of worst 10% returns
    cvar_penalty = 0.0
    if len(ret_history) >= 10:
        hist_arr = np.array(ret_history)
        cutoff = int(np.floor(0.1 * len(hist_arr)))
        if cutoff >= 1:
            sorted_rets = np.sort(hist_arr)
            cvar = np.mean(sorted_rets[:cutoff])  # negative when bad
            cvar_penalty = min(0.0, cvar)  # penalize only negative CVaR

    # Turnover penalty (moderate)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.005 * turnover

    # Drawdown penalty (progressive)
    dd_penalty = -0.5 * (drawdown ** 2)

    # Concentration penalty (encourage mild diversification)
    # Herfindahl index
    herfindahl = np.sum(weights ** 2)
    concentration_penalty = -0.05 * herfindahl

    # Compose total reward
    # Primary: per-step return
    ret_component = port_ret

    # Secondary: Sharpe signal (scaled)
    sharpe_component = 0.1 * sharpe_signal

    # Tail penalty
    tail_component = 0.5 * cvar_penalty

    total = (
        ret_component
        + sharpe_component
        + tail_component
        + turnover_penalty
        + dd_penalty
        + concentration_penalty
    )

    components = {
        "ret": ret_component,
        "sharpe_signal": sharpe_component,
        "tail_cvar": tail_component,
        "turnover": turnover_penalty,
        "drawdown": dd_penalty,
        "concentration": concentration_penalty,
    }

    # Update state
    state["ew_mean"] = ew_mean
    state["ew_var"] = ew_var
    state["peak"] = peak
    state["cumulative"] = cumulative
    state["ret_history"] = ret_history

    return float(total), components, state
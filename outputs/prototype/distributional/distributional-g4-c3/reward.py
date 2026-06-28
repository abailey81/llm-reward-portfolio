def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Recover or initialize reward state ---
    state = info.get("reward_state") or {}
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cumulative = state.get("cumulative", 1.0)

    # Update cumulative and peak
    cumulative = cumulative * (1.0 + port_ret)
    peak = max(peak, cumulative)
    drawdown = (peak - cumulative) / peak  # fraction below peak

    # Append current return
    ret_history.append(port_ret)
    # Keep a rolling window
    window = 120
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    arr = np.array(ret_history, dtype=np.float64)
    n = len(arr)

    # --- Online Sharpe (annualized, steps assumed ~daily) ---
    if n >= 10:
        mu = np.mean(arr)
        sigma = np.std(arr, ddof=1) + 1e-8
        sharpe = mu / sigma * np.sqrt(252)
    else:
        sharpe = 0.0

    # --- CVaR penalty (Expected Shortfall at 10%) ---
    if n >= 20:
        cutoff = max(1, int(np.floor(0.10 * n)))
        sorted_arr = np.sort(arr)
        cvar_10 = np.mean(sorted_arr[:cutoff])  # negative value = loss
        tail_penalty = min(0.0, cvar_10)  # penalize only losses
    else:
        tail_penalty = 0.0

    # --- Drawdown penalty ---
    # Penalize current drawdown level
    dd_penalty = -drawdown ** 1.5  # super-linear in drawdown severity

    # --- Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover

    # --- Concentration penalty (Herfindahl index) ---
    # Penalize concentrated portfolios (squared weights sum, minus cash weight)
    n_assets = len(weights) - 1  # last element assumed cash
    asset_weights = weights[:n_assets]
    herfindahl = np.sum(asset_weights ** 2)
    # Baseline for equal weight
    if n_assets > 0:
        equal_hhi = 1.0 / n_assets
        concentration_penalty = -max(0.0, herfindahl - 2.0 * equal_hhi)
    else:
        concentration_penalty = 0.0

    # --- Downside return penalty (direct step penalty for bad steps) ---
    # Extra penalize large single-step losses
    if port_ret < -0.02:
        step_tail_penalty = 5.0 * port_ret  # amplify large losses
    else:
        step_tail_penalty = 0.0

    # --- Combine components ---
    # Scale Sharpe contribution; it's the primary driver
    sharpe_component = 0.4 * sharpe
    cvar_component = 8.0 * tail_penalty       # penalize sustained tail losses
    dd_component = 1.5 * dd_penalty
    step_tail_component = step_tail_penalty
    turnover_component = turnover_penalty
    concentration_component = 0.5 * concentration_penalty

    total = (
        sharpe_component
        + cvar_component
        + dd_component
        + step_tail_component
        + turnover_component
        + concentration_component
    )

    components = {
        "sharpe": sharpe_component,
        "cvar_10": cvar_component,
        "drawdown": dd_component,
        "step_tail": step_tail_component,
        "turnover": turnover_component,
        "concentration": concentration_component,
    }

    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cumulative": cumulative,
    }

    return float(total), components, reward_state
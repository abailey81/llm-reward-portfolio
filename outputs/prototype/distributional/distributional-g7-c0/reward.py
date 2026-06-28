def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cumulative = state.get("cumulative", 1.0)

    # Update cumulative value and peak
    cumulative = cumulative * (1.0 + port_ret)
    peak = max(peak, cumulative)
    drawdown = (peak - cumulative) / peak  # current drawdown fraction

    # Append current return to history
    ret_history.append(port_ret)
    # Keep a rolling window
    window = 120
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    ret_arr = np.array(ret_history)
    n = len(ret_arr)

    # --- Component 1: Online Sharpe (annualized-ish) ---
    if n >= 8:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr, ddof=1) + 1e-8
        sharpe = mu / sigma  # per-step Sharpe
    else:
        sharpe = 0.0

    # --- Component 2: CVaR penalty (Expected Shortfall at 10%) ---
    if n >= 20:
        threshold = np.percentile(ret_arr, 10)
        tail_returns = ret_arr[ret_arr <= threshold]
        cvar_10 = np.mean(tail_returns) if len(tail_returns) > 0 else 0.0
        # cvar_10 is negative; penalty = -cvar_10 (positive penalty for bad tails)
        cvar_penalty = -cvar_10
    else:
        cvar_penalty = 0.0

    # --- Component 3: Drawdown penalty ---
    drawdown_penalty = drawdown  # ranges [0, 1], penalize current drawdown

    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = turnover

    # --- Component 5: Diversification bonus (negative entropy penalty) ---
    # Encourage spreading weights; penalize concentration
    # Use Herfindahl index (sum of squared weights) — lower is more diversified
    herfindahl = np.sum(weights ** 2)
    concentration_penalty = herfindahl  # ranges [1/n, 1]

    # --- Combine components ---
    # Primary signal: Sharpe
    # Secondary: penalize tail risk, drawdown, turnover, concentration
    w_sharpe = 1.0
    w_cvar = 3.0        # strong tail penalty
    w_dd = 1.5          # drawdown penalty
    w_turnover = 0.3    # mild turnover cost
    w_conc = 0.5        # mild concentration penalty

    total = (
        w_sharpe * sharpe
        - w_cvar * cvar_penalty
        - w_dd * drawdown_penalty
        - w_turnover * turnover_penalty
        - w_conc * concentration_penalty
    )

    components = {
        "sharpe": sharpe,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cumulative": cumulative,
    }

    return float(total), components, reward_state
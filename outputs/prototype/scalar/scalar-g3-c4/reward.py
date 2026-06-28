def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    equity = state.get("equity", 1.0)

    # --- Update equity curve ---
    equity = equity * (1.0 + port_ret)
    peak = max(peak, equity)

    # --- Store return history (rolling window) ---
    WINDOW = 60
    ret_history.append(port_ret)
    if len(ret_history) > WINDOW:
        ret_history = ret_history[-WINDOW:]

    arr = np.array(ret_history, dtype=np.float64)

    # --- Component 1: Online Sharpe (annualized, rolling) ---
    if len(arr) >= 5:
        mu = np.mean(arr)
        sigma = np.std(arr) + 1e-8
        sharpe_raw = mu / sigma  # per-step Sharpe
        # Annualize assuming ~252 steps/year
        sharpe_component = float(np.clip(sharpe_raw * np.sqrt(252), -3.0, 3.0))
    else:
        sharpe_component = 0.0

    # --- Component 2: CVaR / tail-loss penalty ---
    if len(arr) >= 10:
        # 5th percentile CVaR (expected loss in worst 5% of steps)
        cutoff = np.percentile(arr, 5)
        tail_losses = arr[arr <= cutoff]
        cvar = float(np.mean(tail_losses)) if len(tail_losses) > 0 else 0.0
        # Penalize only negative CVaR
        cvar_penalty = min(cvar, 0.0) * 5.0  # amplify tail loss penalty
    else:
        cvar_penalty = 0.0

    # --- Component 3: Drawdown penalty ---
    drawdown = (equity - peak) / (peak + 1e-8)
    # Penalize proportional to current drawdown depth
    dd_penalty = float(np.clip(drawdown, -0.5, 0.0)) * 2.0

    # --- Component 4: Turnover / transaction cost penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.1 * turnover

    # --- Component 5: Direct return signal (small, for early learning) ---
    direct_ret = float(np.clip(port_ret * 10.0, -1.0, 1.0))

    # --- Combine components ---
    # Primary: rolling Sharpe; secondary: tail + drawdown + turnover controls
    total = (
        0.5 * sharpe_component
        + 0.2 * cvar_penalty
        + 0.15 * dd_penalty
        + 0.1 * turnover_penalty
        + 0.05 * direct_ret
    )

    total = float(np.clip(total, -5.0, 5.0))

    components = {
        "sharpe_component": sharpe_component,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "direct_ret": direct_ret,
    }

    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "equity": equity,
    }

    return total, components, reward_state
def reward(weights, returns, prev_weights, port_ret, info):
    # --- State initialization ---
    state = info.get("reward_state") or {}
    
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    equity = state.get("equity", 1.0)
    ema_ret = state.get("ema_ret", 0.0)
    ema_var = state.get("ema_var", 1e-4)
    step = state.get("step", 0)
    
    # --- Update equity curve ---
    equity = equity * (1.0 + port_ret)
    peak = max(peak, equity)
    drawdown = (peak - equity) / (peak + 1e-8)
    
    # --- Maintain return history (rolling window) ---
    ret_history.append(float(port_ret))
    window = 120
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    # --- Online EMA Sharpe (fast, stable signal) ---
    alpha = 0.05  # ~20-step halflife
    ema_ret = alpha * port_ret + (1 - alpha) * ema_ret
    ema_var = alpha * (port_ret - ema_ret) ** 2 + (1 - alpha) * ema_var
    ema_std = np.sqrt(max(ema_var, 1e-8))
    sharpe_signal = ema_ret / ema_std  # dimensionless
    
    # --- CVaR penalty from rolling history ---
    cvar_penalty = 0.0
    if len(ret_history) >= 20:
        arr = np.array(ret_history)
        # 5th percentile tail
        threshold_5 = np.percentile(arr, 5)
        tail_5 = arr[arr <= threshold_5]
        cvar_5 = float(np.mean(tail_5)) if len(tail_5) > 0 else 0.0
        # 10th percentile tail
        threshold_10 = np.percentile(arr, 10)
        tail_10 = arr[arr <= threshold_10]
        cvar_10 = float(np.mean(tail_10)) if len(tail_10) > 0 else 0.0
        # Combined CVaR penalty (negative numbers, so subtract to penalize)
        cvar_penalty = 0.6 * cvar_5 + 0.4 * cvar_10  # negative value
    
    # --- Drawdown penalty (convex — penalize large drawdowns more) ---
    dd_penalty = -(drawdown ** 1.5) * 2.0
    
    # --- Turnover penalty (transaction costs already in port_ret, but discourage churn) ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.02 * turnover
    
    # --- Concentration penalty (encourage diversification) ---
    # Herfindahl index penalizes concentration in risky assets (exclude cash = last weight)
    risky_weights = weights[:-1] if len(weights) > 1 else weights
    herfindahl = float(np.sum(risky_weights ** 2))
    concentration_penalty = -0.05 * herfindahl
    
    # --- Asymmetric return component (reward gains, penalize losses extra) ---
    if port_ret < 0:
        ret_component = 2.5 * port_ret   # extra penalty for losses
    else:
        ret_component = 1.5 * port_ret
    
    # --- Combine components ---
    # Scale sharpe_signal to be comparable in magnitude
    sharpe_component = 0.4 * np.clip(sharpe_signal, -3.0, 3.0)
    
    total = (
        sharpe_component
        + ret_component
        + 1.5 * cvar_penalty      # amplify tail penalty
        + dd_penalty
        + turnover_penalty
        + concentration_penalty
    )
    
    step += 1
    
    components = {
        "sharpe_component": float(sharpe_component),
        "ret_component": float(ret_component),
        "cvar_penalty": float(1.5 * cvar_penalty),
        "dd_penalty": float(dd_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
        "drawdown": float(drawdown),
        "ema_sharpe": float(sharpe_signal),
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "equity": equity,
        "ema_ret": ema_ret,
        "ema_var": ema_var,
        "step": step,
    }
    
    return float(total), components, reward_state
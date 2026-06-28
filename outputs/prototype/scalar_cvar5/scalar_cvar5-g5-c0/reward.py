def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    # Initialize state
    if state is None:
        state = {
            "ret_history": [],       # rolling portfolio returns
            "peak": 1.0,             # for drawdown tracking
            "equity": 1.0,           # cumulative equity
            "step": 0,
        }
    
    # Unpack state
    ret_history = state["ret_history"]
    peak = state["peak"]
    equity = state["equity"]
    step = state["step"]
    
    # Update equity and peak
    equity = equity * (1.0 + port_ret)
    peak = max(peak, equity)
    
    # Track return history (rolling window of 60)
    ret_history.append(port_ret)
    WINDOW = 60
    if len(ret_history) > WINDOW:
        ret_history = ret_history[-WINDOW:]
    
    step += 1
    
    # ---- Component 1: Incremental Sharpe contribution ----
    # Online Sharpe: mean/std of recent returns, annualized-ish
    if len(ret_history) >= 5:
        arr = np.array(ret_history)
        mu = np.mean(arr)
        sigma = np.std(arr) + 1e-8
        sharpe_contrib = mu / sigma
    else:
        sharpe_contrib = port_ret / (abs(port_ret) + 1e-8) * 0.01
    
    # ---- Component 2: Drawdown penalty ----
    drawdown = (peak - equity) / (peak + 1e-8)
    # Progressive penalty: drawdown^1.5 to hit hard on large drawdowns
    dd_penalty = -(drawdown ** 1.5) * 2.0
    
    # ---- Component 3: CVaR / tail loss penalty ----
    # Penalize if current return is in the tail (below 5th percentile of history)
    if len(ret_history) >= 20:
        arr = np.array(ret_history)
        var_5 = np.percentile(arr, 5)
        # CVaR: mean of returns below VaR
        tail_returns = arr[arr <= var_5]
        cvar = np.mean(tail_returns) if len(tail_returns) > 0 else var_5
        cvar_penalty = cvar * 3.0   # amplify tail penalty
    else:
        cvar_penalty = min(port_ret, 0.0) * 2.0  # early steps: penalize losses directly
    
    # ---- Component 4: Turnover penalty (transaction costs) ----
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover
    
    # ---- Component 5: Direct return signal (small, to avoid pure Sharpe gaming) ----
    direct_ret = port_ret * 5.0
    
    # ---- Combine components ----
    # Sharpe contribution is main driver, with risk penalties
    total = (
        0.4 * sharpe_contrib       # primary: risk-adjusted return
        + 0.3 * direct_ret         # secondary: actual return
        + 0.15 * cvar_penalty      # tail risk control
        + 0.1 * dd_penalty         # drawdown control
        + 0.05 * turnover_penalty  # cost control
    )
    
    # Clip to prevent extreme reward signals destabilizing training
    total = float(np.clip(total, -2.0, 2.0))
    
    components = {
        "sharpe_contrib": float(sharpe_contrib),
        "direct_ret": float(direct_ret),
        "cvar_penalty": float(cvar_penalty),
        "dd_penalty": float(dd_penalty),
        "turnover_penalty": float(turnover_penalty),
        "drawdown": float(drawdown),
    }
    
    # Save state
    state["ret_history"] = ret_history
    state["peak"] = float(peak)
    state["equity"] = float(equity)
    state["step"] = step
    
    return total, components, state
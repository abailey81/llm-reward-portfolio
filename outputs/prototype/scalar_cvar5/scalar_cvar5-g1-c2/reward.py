def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}
    
    # Rolling window for return history
    window = 60
    ret_history = state.get("ret_history", [])
    ret_history.append(float(port_ret))
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    # Cumulative wealth tracking for drawdown
    cum_wealth = state.get("cum_wealth", 1.0)
    cum_wealth = cum_wealth * (1.0 + float(port_ret))
    peak_wealth = state.get("peak_wealth", 1.0)
    peak_wealth = max(peak_wealth, cum_wealth)
    drawdown = (peak_wealth - cum_wealth) / (peak_wealth + 1e-8)
    
    arr = np.array(ret_history, dtype=np.float64)
    n = len(arr)
    
    # --- Component 1: Online Sharpe (annualized proxy) ---
    if n >= 2:
        mu = np.mean(arr)
        sigma = np.std(arr, ddof=1) + 1e-8
        sharpe = mu / sigma  # per-step Sharpe
    else:
        sharpe = 0.0
    
    # --- Component 2: CVaR penalty (5% tail) ---
    if n >= 10:
        alpha = 0.05
        k = max(1, int(np.floor(alpha * n)))
        sorted_rets = np.sort(arr)
        cvar = np.mean(sorted_rets[:k])  # negative = bad
        cvar_penalty = min(0.0, cvar)  # only penalize losses
    else:
        cvar_penalty = 0.0
    
    # --- Component 3: Drawdown penalty ---
    drawdown_penalty = -drawdown  # negative, larger drawdown = larger penalty
    
    # --- Component 4: Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.5 * turnover
    
    # --- Component 5: Diversification (entropy of weights) ---
    w = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w * np.log(w))
    max_entropy = np.log(len(w) + 1e-8)
    diversification = entropy / (max_entropy + 1e-8)
    
    # --- Component 6: Downside deviation reward ---
    if n >= 5:
        negative_rets = arr[arr < 0]
        if len(negative_rets) > 0:
            downside_std = np.sqrt(np.mean(negative_rets**2)) + 1e-8
            sortino_like = np.mean(arr) / downside_std
        else:
            sortino_like = np.mean(arr) / 1e-8
        sortino_like = np.clip(sortino_like, -3.0, 3.0)
    else:
        sortino_like = 0.0
    
    # --- Combine components with calibrated weights ---
    # Core return signal
    base_ret = float(port_ret)
    
    total = (
        1.5 * sharpe            # primary: online Sharpe
        + 1.0 * sortino_like    # downside focus
        + 3.0 * cvar_penalty    # strong tail penalty
        + 2.0 * drawdown_penalty  # drawdown aversion
        + 0.3 * diversification  # mild diversification bonus
        + turnover_penalty       # transaction cost awareness
        + 2.0 * base_ret        # direct return signal
    )
    
    components = {
        "sharpe": sharpe,
        "sortino_like": sortino_like,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "diversification": diversification,
        "turnover_penalty": turnover_penalty,
        "base_ret": base_ret,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "cum_wealth": cum_wealth,
        "peak_wealth": peak_wealth,
    }
    
    return float(total), components, reward_state
def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- State initialization ---
    state = info.get("reward_state") or {}
    
    # Online moments for Sharpe estimation
    n = state.get("n", 0)
    mean_ret = state.get("mean_ret", 0.0)
    m2_ret = state.get("m2_ret", 0.0)
    
    # Return history for CVaR/drawdown (rolling window)
    window = 60
    ret_history = list(state.get("ret_history", []))
    
    # Peak for drawdown tracking
    cum_val = state.get("cum_val", 1.0)
    peak_val = state.get("peak_val", 1.0)

    # --- Update cumulative value and drawdown ---
    cum_val = cum_val * (1.0 + port_ret)
    peak_val = max(peak_val, cum_val)
    drawdown = (peak_val - cum_val) / (peak_val + 1e-8)

    # --- Update online mean/variance (Welford) ---
    n += 1
    delta = port_ret - mean_ret
    mean_ret += delta / n
    delta2 = port_ret - mean_ret
    m2_ret += delta * delta2

    # --- Update rolling return history ---
    ret_history.append(port_ret)
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # --- Component 1: Online Sharpe-based reward ---
    if n >= 5:
        var_ret = m2_ret / max(n - 1, 1)
        std_ret = np.sqrt(max(var_ret, 1e-10))
        sharpe_component = mean_ret / std_ret
    else:
        sharpe_component = port_ret  # fallback for early steps

    # --- Component 2: CVaR penalty (tail risk) ---
    if len(ret_history) >= 10:
        sorted_rets = np.sort(ret_history)
        cutoff = max(int(0.05 * len(sorted_rets)), 1)
        cvar = np.mean(sorted_rets[:cutoff])
        cvar_penalty = min(cvar, 0.0)  # only penalize negative CVaR
    else:
        cvar_penalty = 0.0

    # --- Component 3: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover

    # --- Component 4: Drawdown penalty ---
    drawdown_penalty = -0.5 * (drawdown ** 2)

    # --- Component 5: Direct return signal (scaled down) ---
    direct_ret = 0.3 * port_ret

    # --- Combine components ---
    # Main signal: online Sharpe + CVaR + drawdown + turnover + direct return
    sharpe_weight = 0.5
    cvar_weight = 2.0
    
    total = (
        sharpe_weight * sharpe_component
        + cvar_weight * cvar_penalty
        + turnover_penalty
        + drawdown_penalty
        + direct_ret
    )

    components = {
        "sharpe_component": sharpe_weight * sharpe_component,
        "cvar_penalty": cvar_weight * cvar_penalty,
        "turnover_penalty": turnover_penalty,
        "drawdown_penalty": drawdown_penalty,
        "direct_ret": direct_ret,
    }

    # --- Save state ---
    reward_state = {
        "n": n,
        "mean_ret": mean_ret,
        "m2_ret": m2_ret,
        "ret_history": ret_history,
        "cum_val": cum_val,
        "peak_val": peak_val,
    }

    return float(total), components, reward_state
def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_log": 0.0,
            "step": 0,
        }

    state["step"] += 1
    state["ret_history"].append(port_ret)
    state["cum_log"] += np.log1p(port_ret)

    hist = np.array(state["ret_history"])
    n = len(hist)

    # --- 1. Online Sharpe (annualized-ish) ---
    if n >= 2:
        mu = np.mean(hist)
        sigma = np.std(hist, ddof=1) + 1e-8
        sharpe_raw = mu / sigma
        # Scale: encourage positive but don't let it dominate
        sharpe_component = np.clip(sharpe_raw, -3.0, 3.0) * 0.15
    else:
        sharpe_component = 0.0

    # --- 2. Direct return signal (scaled) ---
    ret_component = np.clip(port_ret, -0.1, 0.1) * 2.0

    # --- 3. CVaR penalty: penalize tail losses ---
    if n >= 10:
        sorted_rets = np.sort(hist)
        # 5% CVaR
        cutoff_5 = max(1, int(np.floor(0.05 * n)))
        cvar_5 = np.mean(sorted_rets[:cutoff_5])
        # 10% CVaR
        cutoff_10 = max(1, int(np.floor(0.10 * n)))
        cvar_10 = np.mean(sorted_rets[:cutoff_10])
        # Penalize negative CVaR (tail losses)
        cvar_penalty = np.clip(cvar_5, -0.1, 0.0) * 1.5 + np.clip(cvar_10, -0.1, 0.0) * 0.5
    else:
        cvar_penalty = 0.0

    # --- 4. Drawdown penalty ---
    state["peak"] = max(state["peak"], state["cum_log"])
    drawdown = state["peak"] - state["cum_log"]  # always >= 0
    dd_penalty = -np.clip(drawdown, 0.0, 0.5) * 0.3

    # --- 5. Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -np.clip(turnover, 0.0, 2.0) * 0.01

    # --- 6. Concentration penalty (encourage diversification, mild) ---
    # Herfindahl index on risky weights (exclude last element if cash)
    risky = weights[:-1] if len(weights) > 1 else weights
    hhi = np.sum(risky ** 2)
    concentration_penalty = -np.clip(hhi - 1.0 / max(len(risky), 1), 0.0, 1.0) * 0.02

    # --- Combine ---
    total = (
        ret_component
        + sharpe_component
        + cvar_penalty
        + dd_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "ret": ret_component,
        "sharpe": sharpe_component,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    return float(total), components, state
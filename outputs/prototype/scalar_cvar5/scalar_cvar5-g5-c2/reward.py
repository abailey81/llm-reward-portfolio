def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Restore or initialize state ---
    state = info.get("reward_state") if info is not None else None
    if state is None:
        state = {
            "returns_history": [],
            "peak_value": 1.0,
            "portfolio_value": 1.0,
            "n": 0,
            "mean": 0.0,
            "M2": 0.0,   # for Welford online variance
        }

    # Update portfolio value and drawdown tracking
    pv = state["portfolio_value"] * (1.0 + port_ret)
    state["portfolio_value"] = pv
    peak = state["peak_value"]
    if pv > peak:
        state["peak_value"] = pv
        peak = pv
    drawdown = (peak - pv) / (peak + 1e-8)

    # Online Welford mean/variance of port_ret
    n = state["n"] + 1
    state["n"] = n
    delta = port_ret - state["mean"]
    state["mean"] += delta / n
    delta2 = port_ret - state["mean"]
    state["M2"] += delta * delta2

    mu = state["mean"]
    var = state["M2"] / n if n > 1 else 1e-6
    sigma = np.sqrt(var + 1e-8)

    # Rolling returns history for CVaR estimation (keep last 100)
    history = state["returns_history"]
    history.append(float(port_ret))
    if len(history) > 100:
        history.pop(0)
    state["returns_history"] = history

    # --- Component 1: Incremental Sharpe contribution ---
    # Annualized-ish Sharpe signal (daily step assumed ~252/yr)
    sharpe_signal = mu / sigma
    sharpe_component = sharpe_signal * 0.3

    # --- Component 2: Step return (scaled) ---
    return_component = port_ret * 5.0

    # --- Component 3: CVaR penalty ---
    # Penalize expected loss in worst 10% of observed returns
    if len(history) >= 10:
        arr = np.array(history)
        cutoff = np.percentile(arr, 10)
        tail = arr[arr <= cutoff]
        cvar = float(np.mean(tail)) if len(tail) > 0 else 0.0
    else:
        cvar = 0.0
    cvar_penalty = min(cvar, 0.0) * 3.0  # penalize negative CVaR

    # --- Component 4: Drawdown penalty ---
    drawdown_penalty = -drawdown * 2.0

    # --- Component 5: Diversification bonus ---
    # Entropy of weights (encourages spread, reduces concentration risk)
    w = np.clip(weights, 1e-8, 1.0)
    entropy = -float(np.sum(w * np.log(w)))
    max_entropy = np.log(len(w) + 1e-8)
    diversification = (entropy / (max_entropy + 1e-8)) * 0.1

    # --- Component 6: Tail loss penalty per step ---
    # Extra penalty if this step's return is in bad territory
    tail_threshold = -0.015
    tail_penalty = min(port_ret - tail_threshold, 0.0) * 4.0 if port_ret < tail_threshold else 0.0

    total = (return_component
             + sharpe_component
             + cvar_penalty
             + drawdown_penalty
             + diversification
             + tail_penalty)

    components = {
        "return": return_component,
        "sharpe_signal": sharpe_component,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "diversification": diversification,
        "tail_penalty": tail_penalty,
    }

    return float(total), components, state
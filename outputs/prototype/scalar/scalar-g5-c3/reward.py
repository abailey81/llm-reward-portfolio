def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize reward state ---
    state = info.get("reward_state")
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cumulative": 0.0,
        }

    ret_history = state["ret_history"]
    peak = state["peak"]
    cumulative = state["cumulative"]

    # Update cumulative log return (for drawdown)
    cumulative += np.log1p(port_ret)
    if cumulative > peak:
        peak = cumulative
    drawdown = peak - cumulative  # always >= 0

    # Store return in history
    ret_history.append(port_ret)
    # Keep a rolling window
    window = 100
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # --- Compute online Sharpe (annualized roughly) ---
    arr = np.array(ret_history)
    n = len(arr)
    if n >= 8:
        mu = np.mean(arr)
        sigma = np.std(arr, ddof=1) + 1e-8
        sharpe = mu / sigma  # per-step Sharpe
    else:
        # Early steps: just use return signal lightly
        mu = np.mean(arr) if n > 0 else 0.0
        sigma = 1e-8
        sharpe = mu / sigma * 0.1  # dampen early

    # --- Tail loss (CVaR-style) penalty ---
    if n >= 16:
        sorted_rets = np.sort(arr)
        tail_n = max(1, int(0.1 * n))  # worst 10%
        cvar = np.mean(sorted_rets[:tail_n])  # negative = bad
        tail_penalty = min(0.0, cvar) * 2.0  # penalize negative tail
    else:
        tail_penalty = 0.0

    # --- Drawdown penalty ---
    # Penalize proportionally to current drawdown
    dd_penalty = -drawdown * 2.0

    # --- Turnover penalty (transaction costs proxy) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.005 * turnover

    # --- Concentration penalty (encourage diversification) ---
    # Herfindahl index — penalize extreme concentration
    hhi = np.sum(weights ** 2)
    concentration_penalty = -0.05 * hhi

    # --- Combine ---
    # Primary: Sharpe; secondary: tail, drawdown, turnover, concentration
    total = (
        sharpe * 1.0
        + tail_penalty
        + dd_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "sharpe": sharpe,
        "tail_penalty": tail_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    new_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cumulative": cumulative,
    }

    return float(total), components, new_state
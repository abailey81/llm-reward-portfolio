def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or restore state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_log": 0.0,
            "step": 0,
        }

    state["step"] += 1
    step = state["step"]

    # Log return for this step
    log_ret = np.log1p(port_ret)
    state["cum_log"] += log_ret
    state["ret_history"].append(port_ret)

    # Keep a rolling window
    window = 120
    hist = state["ret_history"]
    if len(hist) > window:
        state["ret_history"] = hist[-window:]
    hist_arr = np.array(state["ret_history"])

    # ── 1. Sharpe-style component (rolling) ──────────────────────────────────
    if len(hist_arr) >= 5:
        mu = np.mean(hist_arr)
        sigma = np.std(hist_arr) + 1e-8
        sharpe_component = mu / sigma
    else:
        sharpe_component = port_ret / (abs(port_ret) + 1e-8) * 0.01

    # ── 2. CVaR penalty (rolling 5% tail) ────────────────────────────────────
    if len(hist_arr) >= 20:
        sorted_r = np.sort(hist_arr)
        cutoff_idx = max(1, int(0.05 * len(hist_arr)))
        cvar_5 = np.mean(sorted_r[:cutoff_idx])
        cvar_penalty = min(cvar_5, 0.0)   # only penalize losses
    else:
        cvar_penalty = 0.0

    # ── 3. Drawdown penalty ───────────────────────────────────────────────────
    cum_val = np.exp(state["cum_log"])
    if cum_val > state["peak"]:
        state["peak"] = cum_val
    drawdown = (cum_val - state["peak"]) / (state["peak"] + 1e-8)
    dd_penalty = min(drawdown, 0.0)   # <= 0

    # ── 4. Turnover penalty ───────────────────────────────────────────────────
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover

    # ── 5. Concentration penalty (entropy) ───────────────────────────────────
    w_safe = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_safe * np.log(w_safe))
    max_entropy = np.log(len(weights) + 1e-8)
    concentration_penalty = -0.3 * (1.0 - entropy / (max_entropy + 1e-8))

    # ── 6. Downside penalty on this step ─────────────────────────────────────
    downside = min(port_ret, 0.0)
    downside_penalty = 2.0 * downside   # amplify immediate losses

    # ── Combine ───────────────────────────────────────────────────────────────
    # Weights tuned to focus heavily on risk-adjusted return
    total = (
        3.0  * sharpe_component
        + 8.0  * cvar_penalty        # heavy tail-loss penalty
        + 4.0  * dd_penalty          # drawdown aversion
        + turnover_penalty
        + concentration_penalty
        + downside_penalty
    )

    components = {
        "sharpe_component":    sharpe_component,
        "cvar_penalty":        cvar_penalty,
        "dd_penalty":          dd_penalty,
        "turnover_penalty":    turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "downside_penalty":    downside_penalty,
    }

    return float(total), components, state
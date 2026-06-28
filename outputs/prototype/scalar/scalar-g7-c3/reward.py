def reward(weights, returns, prev_weights, port_ret, info):
    # --- State initialization ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_mean":   0.0,
            "ret_var":    1e-8,
            "n":          0,
            "peak":       1.0,
            "nav":        1.0,
        }

    n          = state["n"]
    ret_mean   = state["ret_mean"]
    ret_var    = state["ret_var"]
    peak       = state["peak"]
    nav        = state["nav"]

    # --- Online mean & variance (Welford) ---
    n += 1
    delta       = port_ret - ret_mean
    ret_mean   += delta / n
    delta2      = port_ret - ret_mean
    ret_var    += delta * delta2          # accumulates sum of squared deviations
    var_est     = ret_var / n if n > 1 else 1e-8
    std_est     = np.sqrt(max(var_est, 1e-10))

    # --- NAV & drawdown ---
    nav  = nav * (1.0 + port_ret)
    peak = max(peak, nav)
    drawdown = (peak - nav) / peak        # in [0, 1]

    # --- Components ---
    # 1. Incremental Sharpe contribution (annualised approximately)
    sharpe_approx = ret_mean / std_est    # dimensionless ratio

    # 2. Step return (scaled)
    ret_component = port_ret * 10.0

    # 3. Drawdown penalty — quadratic to be harsh on large DDs
    dd_penalty = -5.0 * (drawdown ** 2)

    # 4. Turnover penalty — discourage excessive rebalancing
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.5 * turnover

    # 5. Tail-loss penalty: extra penalty when step return is very negative
    tail_threshold = -0.02          # -2% per step
    tail_penalty = 0.0
    if port_ret < tail_threshold:
        tail_penalty = -2.0 * (port_ret - tail_threshold) ** 2

    # --- Total reward ---
    # Blend online Sharpe direction with per-step feedback
    total = (
        0.4 * sharpe_approx
        + 0.3 * ret_component
        + 0.2 * dd_penalty
        + 0.05 * turnover_penalty
        + 0.05 * tail_penalty
    )

    components = {
        "sharpe_approx":   sharpe_approx,
        "ret_component":   ret_component,
        "dd_penalty":      dd_penalty,
        "turnover_penalty":turnover_penalty,
        "tail_penalty":    tail_penalty,
    }

    # --- Save state ---
    state["n"]        = n
    state["ret_mean"] = ret_mean
    state["ret_var"]  = ret_var
    state["peak"]     = peak
    state["nav"]      = nav

    return float(total), components, state
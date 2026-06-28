def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Recover or initialize reward state ---
    state = info.get("reward_state") if info else None
    if state is None:
        state = {
            "ema_ret":    0.0,
            "ema_sq":     0.0,
            "alpha":      0.05,       # EMA decay (fast)
            "alpha_slow": 0.01,       # EMA decay (slow, for variance)
            "peak":       1.0,        # for drawdown tracking
            "nav":        1.0,
            "ret_window": [],         # rolling window for CVaR
            "window_size": 100,
        }

    alpha      = state["alpha"]
    alpha_slow = state["alpha_slow"]

    # --- Update NAV and drawdown ---
    state["nav"]  *= (1.0 + port_ret)
    peak           = state["peak"]
    if state["nav"] > peak:
        state["peak"] = state["nav"]
        peak = state["nav"]
    drawdown = (peak - state["nav"]) / (peak + 1e-8)

    # --- Update rolling return window for CVaR ---
    window = state["ret_window"]
    window.append(port_ret)
    if len(window) > state["window_size"]:
        window.pop(0)

    # --- Online mean/variance via EMA ---
    state["ema_ret"] = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    state["ema_sq"]  = (1 - alpha_slow) * state["ema_sq"] + alpha_slow * (port_ret ** 2)
    ema_var  = max(state["ema_sq"] - state["ema_ret"] ** 2, 1e-8)
    ema_std  = np.sqrt(ema_var)

    # --- Sharpe-like component (annualized feel, but raw scale) ---
    sharpe_component = state["ema_ret"] / (ema_std + 1e-8)

    # --- CVaR penalty: mean of worst 5% returns in window ---
    cvar_penalty = 0.0
    if len(window) >= 20:
        arr = np.array(window)
        cutoff = np.percentile(arr, 5)
        tail   = arr[arr <= cutoff]
        cvar   = tail.mean() if len(tail) > 0 else cutoff
        cvar_penalty = min(cvar, 0.0)  # only penalize negative CVaR

    # --- Drawdown penalty (convex: penalize large drawdowns more) ---
    drawdown_penalty = -(drawdown ** 1.5)

    # --- Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover

    # --- Concentration penalty (encourage diversification) ---
    n_assets = len(weights)
    hhi = np.sum(weights ** 2)           # Herfindahl index: 1/n (diverse) to 1 (concentrated)
    concentration_penalty = -0.1 * hhi

    # --- Assemble total reward ---
    # Primary driver: Sharpe-like signal + realized return
    # Secondary: tail risk, drawdown, turnover, concentration
    w_sharpe        = 0.4
    w_ret           = 0.3
    w_cvar          = 0.5
    w_drawdown      = 0.3
    w_turnover      = 1.0
    w_concentration = 1.0

    total = (
        w_sharpe   * sharpe_component
        + w_ret    * port_ret
        + w_cvar   * cvar_penalty
        + w_drawdown * drawdown_penalty
        + w_turnover * turnover_penalty
        + w_concentration * concentration_penalty
    )

    components = {
        "sharpe_component":    w_sharpe * sharpe_component,
        "ret_component":       w_ret * port_ret,
        "cvar_penalty":        w_cvar * cvar_penalty,
        "drawdown_penalty":    w_drawdown * drawdown_penalty,
        "turnover_penalty":    w_turnover * turnover_penalty,
        "concentration_penalty": w_concentration * concentration_penalty,
        "ema_ret":             state["ema_ret"],
        "ema_std":             ema_std,
        "drawdown":            drawdown,
    }

    return total, components, state
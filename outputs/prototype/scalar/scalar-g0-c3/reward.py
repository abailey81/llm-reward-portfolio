def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore / initialise state ────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history":   [],          # rolling window of port_ret values
            "peak":          0.0,         # for max-drawdown tracking
            "cum_ret":       0.0,         # log-scale cumulative return proxy
            "step":          0,
        }

    ret_history: list = state["ret_history"]
    peak:        float = state["peak"]
    cum_ret:     float = state["cum_ret"]
    step:        int   = state["step"]

    # ── 2. Update running state ───────────────────────────────────────────────
    r = float(port_ret)
    ret_history.append(r)

    WINDOW = 60                          # rolling window length
    if len(ret_history) > WINDOW:
        ret_history.pop(0)

    cum_ret += r
    if cum_ret > peak:
        peak = cum_ret
    drawdown = peak - cum_ret            # always >= 0

    step += 1

    # ── 3. Rolling statistics ─────────────────────────────────────────────────
    arr = np.array(ret_history, dtype=np.float64)
    n   = len(arr)

    # Volatility (annualised proxy, daily * sqrt(252))
    if n >= 2:
        roll_vol = float(np.std(arr, ddof=1)) * np.sqrt(252)
    else:
        roll_vol = 1e-4          # tiny positive so we don't divide by zero

    roll_vol = max(roll_vol, 1e-4)

    # Annualised mean return proxy
    roll_mean = float(np.mean(arr)) * 252

    # Rolling Sharpe (annualised, no risk-free rate for simplicity)
    roll_sharpe = roll_mean / roll_vol

    # CVaR / Expected Shortfall at 5 % tail
    if n >= 10:
        sorted_arr  = np.sort(arr)
        tail_cutoff = max(1, int(np.floor(0.05 * n)))
        cvar_5      = float(np.mean(sorted_arr[:tail_cutoff]))
    else:
        cvar_5 = r                       # not enough history yet

    # ── 4. Turnover cost signal (extra penalisation beyond env cost) ──────────
    # The env already deducts cost from port_ret, but we add a small extra
    # incentive to keep turnover low to reinforce stable behaviour.
    turnover = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    # extra cost: 5 bps per 1-way unit of turnover (above the env's 10 bps)
    extra_cost = 0.0005 * turnover

    # ── 5. Concentration penalty (encourage diversification) ─────────────────
    # Herfindahl index on risky weights; 0 = perfectly spread, 1 = all in one
    risky_w        = weights[:30]
    herfindahl     = float(np.sum(risky_w ** 2))
    concentration  = max(0.0, herfindahl - 1.0 / 30.0)   # excess over uniform

    # ── 6. Drawdown penalty ───────────────────────────────────────────────────
    # Penalise being in drawdown; scale by current depth
    dd_penalty = 0.5 * drawdown          # drawdown is in return units

    # ── 7. Tail-loss penalty ──────────────────────────────────────────────────
    # Penalise bad CVaR (if cvar_5 is very negative)
    tail_penalty = max(0.0, -cvar_5) * 2.0

    # ── 8. Compose total reward ───────────────────────────────────────────────
    # Primary signal: rolling Sharpe (clipped to avoid blow-ups early on)
    sharpe_component  = np.clip(roll_sharpe, -3.0, 3.0)

    # Smooth the overall signal with the realised step return (scaled)
    ret_component     = r * 252          # annualise single-step return

    # Blend: 60 % Sharpe-based, 40 % step return; then subtract penalties
    primary = 0.6 * sharpe_component + 0.4 * ret_component

    total = (
        primary
        - dd_penalty
        - tail_penalty
        - extra_cost
        - 0.1 * concentration        # light concentration penalty
    )
    total = float(total)

    # ── 9. Pack state ─────────────────────────────────────────────────────────
    reward_state = {
        "ret_history": ret_history,
        "peak":        peak,
        "cum_ret":     cum_ret,
        "step":        step,
    }

    # ── 10. Components dict (for logging) ─────────────────────────────────────
    components = {
        "port_ret":         r,
        "roll_sharpe":      float(roll_sharpe),
        "roll_vol":         float(roll_vol),
        "cvar_5":           float(cvar_5),
        "drawdown":         float(drawdown),
        "dd_penalty":       float(dd_penalty),
        "tail_penalty":     float(tail_penalty),
        "turnover":         float(turnover),
        "extra_cost":       float(extra_cost),
        "concentration":    float(concentration),
        "primary":          float(primary),
        "total":            total,
    }

    return total, components, reward_state
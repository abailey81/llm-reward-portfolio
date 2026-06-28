def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore or initialise state ──────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],        # rolling window of port_ret
            "peak":           0.0,       # for drawdown
            "cum_ret":        0.0,       # log-cumulative return proxy
        }

    returns_window: list = state["returns_window"]
    peak:           float = state["peak"]
    cum_ret:        float = state["cum_ret"]

    # ── 2. Update rolling state ──────────────────────────────────────────────
    WINDOW = 60  # rolling window length

    returns_window.append(float(port_ret))
    if len(returns_window) > WINDOW:
        returns_window.pop(0)

    cum_ret += float(port_ret)
    if cum_ret > peak:
        peak = cum_ret
    drawdown = peak - cum_ret  # always >= 0

    arr = np.array(returns_window, dtype=np.float64)
    n   = len(arr)

    # ── 3. Rolling volatility ────────────────────────────────────────────────
    if n >= 2:
        roll_vol = float(np.std(arr, ddof=1))
    else:
        roll_vol = 1e-6
    roll_vol = max(roll_vol, 1e-6)

    # ── 4. Rolling CVaR (expected shortfall at 5 % tail) ────────────────────
    if n >= 10:
        cutoff   = max(1, int(np.floor(0.05 * n)))
        sorted_r = np.sort(arr)
        cvar     = float(np.mean(sorted_r[:cutoff]))   # negative = bad
    else:
        cvar = float(np.mean(arr)) if n > 0 else 0.0

    # ── 5. Turnover cost penalty ─────────────────────────────────────────────
    turnover = float(0.5 * np.sum(np.abs(weights - prev_weights)))

    # ── 6. Concentration penalty (Herfindahl on risky weights) ───────────────
    risky_w      = weights[:30]
    herfindahl   = float(np.sum(risky_w ** 2))          # 0 = diverse, 1 = fully concentrated
    conc_penalty = max(0.0, herfindahl - 1.0 / 30.0)   # penalise above equal-weight level

    # ── 7. Compose reward ────────────────────────────────────────────────────
    # Sharpe-like term: mean / vol (over rolling window)
    roll_mean = float(np.mean(arr)) if n > 0 else 0.0
    sharpe_term = roll_mean / roll_vol

    # Tail-risk term: normalise CVaR by vol
    cvar_term   = cvar / roll_vol   # negative when tail losses are large

    # Drawdown penalty (scaled by vol to keep commensurate)
    dd_penalty  = drawdown / (roll_vol + 1e-6)

    # Weights (tuned conservatively to avoid dominating the return signal)
    W_SHARPE  =  1.00
    W_CVAR    =  0.50   # extra penalty for tail losses on top of the sharpe term
    W_DD      =  0.30
    W_TO      =  2.00   # turnover already paid in port_ret, but we add a small extra nudge
    W_CONC    =  0.50

    total = (
          W_SHARPE  * sharpe_term
        + W_CVAR    * cvar_term          # cvar_term is negative → penalty
        - W_DD      * dd_penalty
        - W_TO      * turnover
        - W_CONC    * conc_penalty
    )

    components = {
        "port_ret":     float(port_ret),
        "sharpe_term":  sharpe_term,
        "cvar_term":    cvar_term,
        "dd_penalty":   dd_penalty,
        "turnover":     turnover,
        "conc_penalty": conc_penalty,
        "roll_vol":     roll_vol,
        "drawdown":     drawdown,
    }

    new_state = {
        "returns_window": returns_window,
        "peak":           peak,
        "cum_ret":        cum_ret,
    }

    return float(total), components, new_state
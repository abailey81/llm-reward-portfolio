def reward(weights, returns, prev_weights, port_ret, info):
    """
    Risk-adjusted reward combining:
    1. Online Sharpe ratio signal (primary)
    2. Turnover penalty (transaction cost awareness)
    3. Drawdown penalty (tail risk)
    """
    import numpy as np

    # --- Restore or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_log": 0.0,
        }

    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_log = state["cum_log"]

    # --- Accumulate return history ---
    ret_history.append(float(port_ret))
    # Keep a rolling window for online estimates
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # --- 1. Sharpe-like signal ---
    arr = np.array(ret_history, dtype=np.float64)
    if len(arr) >= 2:
        mu = np.mean(arr)
        sigma = np.std(arr, ddof=1)
        sigma = max(sigma, 1e-8)
        sharpe_signal = mu / sigma
    else:
        sharpe_signal = 0.0

    # --- 2. Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.1 * turnover

    # --- 3. Drawdown penalty ---
    cum_log += np.log1p(max(port_ret, -0.9999))
    if cum_log > peak:
        peak = cum_log
    drawdown = peak - cum_log  # >= 0
    drawdown_penalty = 0.5 * drawdown

    # --- 4. Diversification: mild concentration penalty ---
    # Penalize extreme concentration (but don't force uniform)
    hhi = float(np.sum(weights ** 2))
    n = len(weights)
    hhi_min = 1.0 / n
    conc_penalty = 0.05 * max(hhi - hhi_min, 0.0)

    # --- Combine ---
    total = (
        sharpe_signal          # primary: risk-adjusted return signal
        - turnover_penalty     # discourage excessive trading
        - drawdown_penalty     # penalize drawdowns
        - conc_penalty         # mild diversification nudge
    )

    components = {
        "sharpe_signal": sharpe_signal,
        "turnover_penalty": turnover_penalty,
        "drawdown_penalty": drawdown_penalty,
        "conc_penalty": conc_penalty,
        "port_ret": port_ret,
    }

    state["ret_history"] = ret_history
    state["peak"] = peak
    state["cum_log"] = cum_log

    return float(total), components, state
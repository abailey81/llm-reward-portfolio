def reward(weights, returns, prev_weights, port_ret, info):
    w_return, w_log, w_turnover, w_drawdown, w_cvar, w_vol = (
        1.2256888282392187, 0.024136645834995862, 0.006761200154032492, 0.0008856766467997268, 1.5394216846768756, 0.9008349257505854,
    )
    alpha = 0.05
    win = 20
    state = info.get('reward_state')
    if state is None:
        hist, peak, cum = [], 0.0, 0.0
    else:
        hist, peak, cum = list(state[0]), float(state[1]), float(state[2])
    r = float(port_ret)
    hist.append(r)
    if len(hist) > win:
        hist = hist[-win:]
    arr = np.asarray(hist, dtype=float)
    turnover = float(np.sum(np.abs(np.asarray(weights) - np.asarray(prev_weights))))
    cum = cum + float(np.log1p(max(r, -0.9999)))
    peak = max(peak, cum)
    drawdown = peak - cum
    sigma = float(np.std(arr)) if arr.size > 1 else 0.0
    k = max(1, int(np.ceil(alpha * arr.size)))
    cvar = float(np.mean(np.sort(arr)[:k]))
    total = (
        w_return * r
        + w_log * float(np.log1p(max(r, -0.9999)))
        - w_turnover * turnover
        - w_drawdown * drawdown
        - w_cvar * max(0.0, -cvar)
        - w_vol * sigma
    )
    components = {
        'return': r,
        'turnover': turnover,
        'drawdown': float(drawdown),
        'cvar': cvar,
        'sigma': sigma,
    }
    return float(total), components, (hist, peak, cum)

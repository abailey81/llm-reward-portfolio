
def reward(weights, returns, prev_weights, port_ret, info):
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    total = float(port_ret) - 0.1 * turnover
    return total, {"port_ret": float(port_ret), "turnover": turnover}, None

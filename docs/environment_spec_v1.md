# Portfolio environment specification v1  (plan block F1)
<!-- Verified as-built 2026-06-10: state/action/accounting/reward-injection sections match
     src/portfolio_env.py + src/features.py incl. the ADR-007 cash-feature block. -->

Precedents: Sood et al. 2023 (JPM/ICAPS FinPlan) for state/action/reward; Jiang et al. 2017 for
prev-weight injection; FinRL-Meta conventions met for comparability. Implementation: `src/portfolio_env.py`.

**State.** Matrix [(n+1) × T], T=60: per-asset log-return lookback rows; row n+1 (cash) carries current
weights head + {vol20, vol20/vol60, VIX} tail (Sood). Build flattens [prev_weights ‖ lookback ‖ cash_features].
Cash-row features (ADR-007, `src/features.py`): rolling SAMPLE std of the equal-weight market proxy (or an
explicit index series) over {20, 60} days and the VIX close, ALL shift(1)-lagged so row t holds information
through t−1 only; VIX scaled by 1/100 (stateless); vol ratio = 1 (neutral) under zero variance; warm-up rows
NaN and the env REJECTS non-finite features on any decision row. Leakage is unit-tested by truncation- and
future-perturbation-invariance (`tests/test_features.py`). The block is optional — omitted, observations are
[prev_weights ‖ lookback] as before (dims unchanged).

**Action.** Logits ∈ ℝ^{n+1} → softmax → weights (long-only, Σ=1, cash last). Logit clip ±10.

**Dynamics & accounting (implemented + unit-tested).** At step t the agent sets target w_t; one-way
turnover = ½Σ|w_t − w̃_{t-1}| where w̃ = previous weights DRIFTED by realised returns
(w̃_i = w_{t-1,i}(1+r_{t-1,i}) / (1+r_p,{t-1})); cost = turnover × bps; gross r_p = w_t·r_t (cash at
cash_daily_rate); net = gross − cost; wealth compounds on net. Identity test: zero-cost wealth equals
Π(1+w·r) to 1e-10 (`tests/test_portfolio_env.py`).

**Reward injection.** Env calls `reward_fn(ctx) -> (float, components)`; ctx fields are exactly those in
`reward_contract.RewardContext` — the same fields promised to the LLM in the system prompt. Fitness is
NEVER computed inside the env (CLAUDE.md R3).

**Episode.** Daily steps over the assigned split slice; terminal at slice end; `info` carries components,
turnover, cost, wealth for logging sidecars.

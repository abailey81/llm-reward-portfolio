# Portfolio environment specification v1.1  (plan block F1; v1.1 2026-07-03 — State / Dynamics / Reward-injection corrected to the IMPLEMENTED conventions, see the dated notes inline)

Precedents: Sood et al. 2023 (JPM/ICAPS FinPlan) for state/action/reward; Jiang et al. 2017 for
prev-weight injection; FinRL-Meta conventions met for comparability. Implementation:
`src/env/portfolio_env.py` (post-merge path; the ADR-007 cash-feature block lives in the gold panel's
`cash_features`, built by `data_pipeline/src/features.py`).

**State (v1.1: corrected to the implemented observation, `portfolio_env._obs`).** A flat float32
vector built ONLY from data knowable at decision time t, concatenated in this order:
`[returns[t−60:t].ravel() ‖ vol_20 ‖ vol_60 ‖ VIX_(t−1) ‖ 1.0 ‖ w_prev]` —
(i) the strictly-past `state.lookback_days`=60-day window of per-asset **simple** daily returns
(the panel stores simple returns, `src/data/panel.py` — matching the drift/gross arithmetic below;
v1.0 said "log-return" in error); (ii) per-asset realized vol = sample std of the same strictly-past
returns over each `realized_vol_windows` entry {20, 60}, computed by the env itself (no vol-ratio
feature); (iii) the VIX close knowable at t — the t−1 close, exposed exactly once (a prelagged gold
panel is read at index t via `vix_prelagged=True`; the contemporaneous synthetic convention is lagged
to t−1 in the env), unscaled from `panel.vix`; (iv) a constant cash-row marker 1.0; (v) the previous
weights (N+1, cash last). Dim = 60·N + 2·N + 1 + 1 + (N+1) = **1,893 at N=30**. The returns window
never reads an index ≥ t (`returns[t]` is the future realisation consumed only in `step`; no
look-ahead, unit-tested). v1.0 described a Sood-style [(n+1) × T] matrix with a cash-feature row
`[prev_weights ‖ lookback ‖ cash_features]` and a vol20/vol60 ratio — that was the plan's rendering,
not the implementation; the env consumes only `panel.returns` + `panel.vix` (the ADR-007
`cash_features` block is a gold-pipeline artefact from which the panel's prelagged `vix` is drawn).

**Action.** Logits ∈ ℝ^{n+1} → softmax → weights (long-only, Σ=1, cash last). Logit clip ±10.

**Dynamics & accounting (implemented + unit-tested).** At step t the agent sets target w_t; one-way
turnover = ½Σ|w_t − w̃| where w̃ = previous weights DRIFTED by the returns realised **at t**
(w̃_i = w_{t-1,i}·g_i / (w_{t-1}·g), with g_i = 1+r_{t,i} for the N risky assets and g_cash =
1 + cash_daily_rate); cost = turnover × bps; gross r_p = w_t·r_t + w_cash·cash_daily_rate
(`config/environment.yaml: state.cash_daily_rate`, 0.0 → cash grows at 1.0; R20); net = gross − cost;
wealth compounds on net (log1p, floored at −99.99%). Turnover is emitted as `info["turnover"]`. Cost
identity test: `cost == ½·c·Σ|w − w̃|` and the realized `info["turnover"]` on a hand-computed
2-risky-asset + cash example, to 1e-12 (`tests/test_env.py::test_cost_is_half_l1_drifted_turnover`).

> **v1.1 note (2026-07-03) — drift convention aligned to the implemented one.** v1.0 wrote the drift
> with r_{t−1} (holdings drifted by the *previous* step's returns before the trade at t). The
> implemented — and test-locked (`test_cost_is_half_l1_drifted_turnover`) — convention drifts with
> **r_t** (`src/env/portfolio_env.py:284-305`): the step-t trade is priced against holdings drifted
> by the same returns r_t that settle at t. This document is hereby the implemented convention.
> Magnitude of the difference ≈ c·0.5·|r_t−r_{t−1}|·‖w‖₁ ~ hundredths of a bp/step at the 10 bps
> headline cost, and it is identical across arms (the env is fixed, audit A-1), so it cannot confound
> H2; aligning the doc was chosen over a code change pre-freeze to preserve prototype comparability.

**Reward injection (v1.1: corrected to the implemented contract — v1.0 described a `reward_fn(ctx)` /
`RewardContext` API that does not exist in this line).** The env invokes the injected callable through
the stage-2 sandbox (`src/sandbox/executor.py::safe_call`) with the FIVE-argument contract of
`src/reward/contract.py:54-63`:
`reward(weights, returns, prev_weights, port_ret, info) -> (total, components, reward_state)` —
`weights`/`prev_weights` are read-only (N+1,) copies (cash last), `returns` the read-only (N,) risky
return row r_t, `port_ret` the net portfolio return (float), and `info` a shallow copy whose
`reward_state` round-trips stateful rewards via the RETURNED third element (audit B-4). The agent
optimizes `total`; `components` is logged only. The identical signature is promised to the LLM in the
system prompt. Fitness is NEVER computed inside the env (CLAUDE.md R3).

**Episode.** Daily steps over the assigned split slice; terminal at slice end; `info` carries components,
turnover, cost, wealth for logging sidecars.

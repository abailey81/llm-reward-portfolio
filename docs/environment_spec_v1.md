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
turnover = ½Σ|w_t − w̃| where w̃ is the book the agent ACTUALLY HOLDS into step t — the previous
target drifted by the return **that target earned**, r_{t−1}
(w̃_i = w_{t-1,i}·g_i / (w_{t-1}·g), with g_i = 1+r_{t−1,i} for the N risky assets and g_cash =
1 + cash_daily_rate; at the opening step nothing has drifted yet, so w̃ is the uniform reset book);
cost = turnover × bps; gross r_p = w_t·r_t + w_cash·cash_daily_rate
(`config/environment.yaml: state.cash_daily_rate`, 0.0 → cash grows at 1.0; R20); net = gross − cost;
wealth compounds on net (log1p, floored at −99.99%). Turnover is emitted as `info["turnover"]`. Cost
identity test: `cost == ½·c·Σ|w − w̃|` and the realized `info["turnover"]` on a hand-computed
2-risky-asset + cash example over TWO steps — a single step cannot exercise the drift, since the
reset book has not drifted yet — to 1e-12
(`tests/test_env.py::test_cost_is_half_l1_drifted_turnover`).

> **v1.2 note (2026-07-27) — the drift index CORRECTED to r_{t−1}; v1.1 is WITHDRAWN.** v1.0 wrote
> the drift with r_{t−1}. v1.1 (2026-07-03) rewrote the *document* to match a code path that drifted
> with r_t, calling it a benign convention. That was wrong, and it is exactly the **P6** finding
> raised in `docs/DEEP_SWEEP_30_FINAL_2026-07-04.md` (pre-freeze checklist #2) and left
> undispositioned for 23 days. The r_t form applied one return under two mutually exclusive execution
> times — `gross` has the NEW weights earning r_t (the trade settles BEFORE r_t) while the drift had
> the PRE-trade book already absorbing r_t (it settles after) — and w_{t−1} never earned r_t; it
> earned r_{t−1}, which drifted nothing. The practical consequence was a contemporaneous look-ahead
> in the cost ledger: reaching zero turnover required w_t = drift(w_{t−1}, r_t), a function of the
> UNOBSERVED r_t, so a pure buy-and-hold policy was unreachable and paid a MEASURED **0.139 %/yr —
> 0.0082 Sharpe-equivalent, 16 % of the 0.05 SESOI** — that it could neither avoid nor predict. The
> env now carries the held book as state (`PortfolioEnv.w_held`), which makes the no-trade target
> OBSERVABLE (a function of w_{t−1} and the r_{t−1} row already inside the observation window) and
> charges exactly zero for it. Fixed pre-data and pre-freeze in `src/env/portfolio_env.py` (deep
> review loop 117, #92). The convention-locking tests now assert the r_{t−1} index decisively over
> two steps (one step cannot exercise the drift at all), and
> `tests/test_env.py::test_cost_ledger_has_no_contemporaneous_look_ahead` proves that corrupting
> `returns[t]` cannot move the turnover charged at t — the adversarial guard the OBSERVATION already
> had (`tests/test_env_nolookahead.py`) and the cost ledger did not.
>
> **MEASURED impact — taken on the gold panel as the env loads it (3,021 × 30) at the headline
> 10 bps, BEFORE anything was changed.** The tail contamination P6 alleged is **not present**:
> CVaR-5% of a daily-rebalanced equal-weight book moves 0.005 % relative, mean cost on down days is
> 0.0440 bp vs 0.0437 bp corrected, and corr(cost, same-day return) was +0.0415 under the old ledger
> vs +0.0515 corrected — marginally *less* coupled, not more. v1.1's own magnitude claim ("hundredths
> of a bp/step") is CORRECT at 0.0385 bp/step, and the DEEP_SWEEP's "~10× understated" is refuted.
> So this is a **look-ahead correction, not a results correction**. It is common-mode across all 7
> arms and all 9 benchmarks (one shared env, audit A-1), so it cannot confound H2, and the σ_D /
> convergence pilots do NOT need re-running: the ledger difference for a rebalancing policy is 6e-10
> per step, orders of magnitude below the seed-to-seed σ that dominates them. The golden synthetic
> reproduction WAS re-baselined (`tests/golden/synthetic_summary.json`, 2026-07-27): only the trained
> `val_fitness` / `cvar_05` moved — panel hash, record set and reward hashes byte-identical — and
> single-seed trained numbers moving percent-level under a 1e-5 dynamics perturbation is the
> σ_seed-dominance result restated, not evidence of a systematic effect.

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

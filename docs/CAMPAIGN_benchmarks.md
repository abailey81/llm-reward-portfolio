# CAMPAIGN benchmark suite — verification + research dossier

**Status:** verification doc (read-only on code). Prepared as a quant-finance reviewer making the
CAMPAIGN "does it work?" comparison defensible. NOT dissertation prose. No code was edited.
**Date:** 2026-06-24. **Repo:** `llm-reward-portfolio`. **Verifier env:** `.venv\Scripts\python.exe`.

> **Split-C / univ5 update (2026-07-02, ADR-044/051, R73).** The ACTIVE panel is now **univ5**
> (5,406 × 963, 2005-01-03 → 2026-06-30 settled cutoff) and the sealed test era is **2020–2026H1**
> (train 2005–2016 / val 2017–2019). The first-hand verification below was executed 2026-06-24 on the
> then-current panel and a 2018 window; it stands as an allocator-correctness record, and the ladder /
> band conclusions are unchanged. **The G1 blocker below has since been CLOSED:** the 4-name H1
> baseline panel is dispatched automatically (`config/campaign.yaml: h1_baselines` = raw_return,
> return_minus_variance, return_minus_cvar, differential_sharpe; guarded by
> `freeze.py::assert_h1_baselines_match`; 120 H1 trainings = 4 × 30 seeds — R30/R72), with the 10-name (R97)
> `REWARD_CANON` documented as the secondary panel (`config/eureka_loop.yaml` note).

> **11-canon / E1-ladder / min_cvar update (2026-07-26) — supersedes the counts in this dossier.** The H1
> hand-reward panel is now the **FULL 11-name canon** (`h1_baselines` == `REWARD_CANON`, expanded 4 → 11:
> +differential_downside_ratio, mean_variance_utility, return_minus_drawdown, return_minus_downside,
> return_minus_turnover, log_growth, volatility_scaled_return), trained at the **E1 assurance-tier seed
> ladder** (NOT the old 4 × 30 = 120), and promoted to the confirmatory node **N6** — a snoop-free IUT (the
> LLM reward DOMINATES the canon == beats the best human; Berger 1982). The classical allocator suite is now
> **9** (the 8 + `min_cvar`, the tail-optimal Rockafellar–Uryasev CVaR-min benchmark). Every "4-name / 120 /
> 10-name / 9-reward / 8-allocator / six-arm" figure BELOW is a HISTORICAL 2026-06-24 audit snapshot,
> superseded by these numbers; the authoritative live count is `learning_curve.campaign_run_breakdown()`.

Scope: the benchmark **ladder** the comparative claim needs —

| Tier | What | Where it lives | Runnable today? |
|---|---|---|---|
| **T0** classical allocators | 8 published non-learned allocators (the DeMiguel 1/N floor + 7 more) | `src/baselines/strategies.py::STRATEGY_CANON` → `analyze_campaign.benchmark_floor` | **YES** — wired + invoked |
| **T1** hand-designed rewards (Eureka "beat-the-human") | 9 hand-authored reward functions | `src/baselines/rewards.py::REWARD_CANON` | **NO — defined + unit-tested, but NOT wired as a trained arm** (the central GAP) |
| **T2** search baselines | random-search-over-code (H4a) + BO-over-template (H4b) | `src/search/*`, `src/baselines/reward_family.py` | **YES** — they are two of the six frozen arms |
| **T4** FinRL / FinRL-Meta SOTA band | external literature band (not run here) | this doc, §3 | reference band only |

Bottom line up front: **T0, T2 are real and runnable; T1 is a wiring GAP that must be closed before
the campaign if the dissertation is to claim "the LLM beat the hand-written rewards" (H1).** The reward
functions, a worker branch that can train a baseline reward, and a config list all exist — but nothing
in the live orchestration constructs or dispatches a baseline-reward training run, and no analysis
computes the Eureka-style success metric. Details + the precise fix in §2 and §4.

---

## 1. Verification table — the 8 classical allocators (T0)

All eight allocators were instantiated **first-hand on the real gold panel**
(`data/gold/returns_panel_univ.parquet`, 5283×953), on a 30-asset, 251-day 2018 window (the test era
at the time; the sealed test era is 2020–2026H1 since Split C, R73),
30 live-ish columns chosen by finite-fraction > 0.99 and σ > 1e-6. Every allocator returns valid simplex
weights and the cross-allocator sanity rankings hold.

| Allocator (`STRATEGY_CANON` key) | Canonical reference | Computes? | Weights sane (sum=1, w≥0)? | Value sanity check (verified) |
|---|---|---|---|---|
| `equal_weight` (1/N floor) | DeMiguel, Garlappi & Uppal (2009), *RFS* 22(5):1915–1953 | ✅ | ✅ sum 1.0000, all 1/30=0.0333 | exactly uniform; the floor every arm must clear |
| `mean_variance` (Ledoit-Wolf) | Markowitz (1952); Ledoit & Wolf (2004) | ✅ | ✅ sum 1.0000, max 0.3288 | long-only **tangency** QP (NOT Σ⁻¹μ projection); concentrates to 5 names — sensible for max-Sharpe |
| `risk_parity` (ERC) | Maillard, Roncalli & Teïletche (2010); Spinu (2013) | ✅ | ✅ sum 1.0000, spread 0.017–0.103 | **risk contributions equalised** to <1e-3 (test); convex log-barrier, L-BFGS-B |
| `hrp` | López de Prado (2016), *J. Portfolio Mgmt* | ✅ | ✅ sum 1.0000, spread 0.008–0.092 | clustering→quasi-diag→recursive-bisection; robust to zero-variance (delisted) cols |
| `minimum_variance` | Clarke, de Silva & Thorley (2011); Markowitz (1952) | ✅ | ✅ sum 1.0000, max 0.4292, 13 names | **GMV variance 5.50e-5 < equal-weight 1.24e-4** ✓ (constrained long-only QP) |
| `maximum_diversification` | Choueifaty & Coignard (2008), *J. Portfolio Mgmt* | ✅ | ✅ sum 1.0000, max 0.4206, 15 names | **div-ratio 2.069 > equal-weight 1.699** ✓ (GMV-of-correlation, de-scaled by 1/σ) |
| `inverse_volatility` (naive RP) | Leote de Carvalho et al. (2012) "naive risk parity" | ✅ | ✅ sum 1.0000, spread 0.017–0.052 | wᵢ ∝ 1/σᵢ; dead names excluded so σ→0 cannot grab ~100% |
| `cross_sectional_momentum` | Jegadeesh & Titman (1993), *J. Finance* | ✅ | ✅ sum 1.0000, 10 names @ 0.1 | long-only top-tertile (10/30) of the **live** universe; dead/NaN sink to −∞ rank |

`spy_buy_and_hold` is present in `STRATEGY_CANON` but is **honestly an exact 1/N duplicate** (the
anonymised PIT panel has no index column or market caps) and is **correctly excluded** from the gate's
`_BENCHMARK_NAMES` (8 names, no `spy_buy_and_hold`) to avoid double-counting the DeMiguel floor (R19).

**Wiring (T0 is live).** `analyze_campaign.benchmark_floor(panel, cfg, test_window, …)`:
- rolls each of the 8 allocators through the **identical** `PortfolioEnv` over the test window via
  `WeightPolicy` + `rollout_port_returns`, so **every benchmark pays the same transaction cost** as the
  learned winner;
- reports per-benchmark `{sharpe, cvar(α=0.05), max_drawdown, dsr, n_steps}`;
- the **DeMiguel gate**: the frozen winner's **median-per-seed** Deflated Sharpe (deflated by the
  search-candidate multiplicity `winner_n_trials`) must **strictly exceed** the best benchmark's
  single-path DSR. Median-per-seed (not seed-mean) is used deliberately — seed-averaging the paths first
  shrinks variance ~√S and inflates the DSR (the same anti-conservatism the H2 fix removed).
- **Confirmed invoked** from the analysis entry point (`analyze()` → `out["benchmark_floor"] =
  benchmark_floor(...)`), so T0 runs automatically on every campaign analysis. ✅

**Robustness engineering verified.** Every covariance/vol allocator runs on a `_live_mask` sub-panel
(σ > 1e-10) so the `liquidate_to_cash` zero-fill of delisted names cannot capture weight via 1/σ→∞;
the long-only QPs are solved directly (a removed Euclidean-projection footgun used to collapse min-var
/ max-div to a single asset). `tests/test_baselines.py` asserts: simplex for all; GMV variance < 1/N;
max-div ratio > 1/N; ERC equalises risk contributions; delisted-name exclusion; **no collapse to <3
names**; HRP finite on zero-variance columns. These passed first-hand.

**Verdict T0: defensible and runnable. No gap.** One *optional* enhancement (not a defect): the suite
has **no genuine market benchmark** (SPX-TR / cap-weighted). The code documents this as a gated data
addition (needs a non-anonymised pull); `market_reference` in `benchmark_floor` already prices a
full-universe equal-weight proxy + the winner's β/α/IR when the (gated) `market_proxy_*.parquet` is
present, as additive reporting outside the same-universe gate. Acceptable as a documented limitation.

---

## 2. REWARD_CANON readiness — the T1 "beat-the-human" bar (Eureka)

### 2a. What exists and was verified
`src/baselines/rewards.py::REWARD_CANON` holds **9** hand-authored rewards, each obeying the audited
contract `reward(weights, returns, prev_weights, port_ret, info) -> (total, components, reward_state)`:

| Reward | Reference | Verified finite over 251-step path | Last-step total (sanity) |
|---|---|---|---|
| `raw_return` | myopic baseline | ✅ | +0.007965 (= port_ret) |
| `return_minus_variance` | mean-variance | ✅ | +0.007635 |
| `return_minus_cvar` | Rockafellar & Uryasev (2000) | ✅ | −0.024185 (tail-penalised) |
| `differential_sharpe` | Moody & Saffell (2001) IEEE TNN; Moody, Wu, Liao & Saffell (1998) | ✅ | +0.507552 (stateful EMA) |
| `mean_variance_utility` | Markowitz (1952), 0.5λ form | ✅ | +0.007800 |
| `return_minus_drawdown` | Chekhlov, Uryasev & Zabarankin (2005) | ✅ | −0.175541 |
| `return_minus_downside` | Sortino & van der Meer (1991) | ✅ | −0.006884 |
| `return_minus_turnover` | Gârleanu & Pedersen (2013) | ✅ | +0.007965 |
| `log_growth` | Kelly (1956); Thorp (1971) | ✅ | +0.007934 |

`tests/test_baselines.py` covers the contract for the 4 core rewards + the exact `differential_sharpe`
A/B/η update sequence. All passed first-hand. The functions are **correct and individually runnable.**

### 2b. The success metric you asked to confirm — and the bar
The intended T1 metric (Eureka-faithful): over a grid of {seeds × evaluation windows}, the LLM-designed
winner's **fraction of cells in which it beats the best member of `REWARD_CANON`**, plus the **normalized
improvement** over that best hand-reward. The Eureka bar to cite:

> **Eureka (Ma et al., ICLR 2024; arXiv:2310.12931):** LLM-authored rewards beat expert
> human-engineered rewards on **83% of 29 tasks**, with an **average normalized improvement of +52%**.
> (Normalized improvement there is `(Eureka − Human)/|Human|`, aggregated across tasks.)

So the dissertation's H1 framing should read: *fraction of (seed, window) cells where the LLM winner's
OOS risk-adjusted score > best-REWARD_CANON score* vs the 83% reference, and *median normalized
improvement* vs the +52% reference. This is a **direct, headline-grade analogue** of the Eureka result
and is the strongest single "does it work?" sentence available to the project.

### 2c. The GAP (critical) — T1 is NOT wired, and the metric does not exist
First-hand tracing of the live code:

1. **`REWARD_CANON` is imported nowhere** in `src/` or `scripts/` except its own definition
   (grep: the only hits are the definition site + docs/CHANGELOG). `benchmark_floor` imports
   **`strategies`** (the allocators), never `rewards`.
2. **There IS a worker branch that can train a baseline reward** — `src/orchestration/parallel.py::
   train_candidate`, `kind == "baseline"` does `getattr(R, spec["reward"])` where `R =
   src.baselines.rewards`, then trains the fixed SAC on it through the identical env builder. So the
   *capability* exists at the worker level.
3. **But nothing constructs a `reward_kind="baseline"` spec.** The only three `_spec(...)` call sites
   (`parallel.py:565,623,640`) use `"source"` (LLM + random-search) and `"coeffs"` (BO). There is **no
   `_spec(arm, "baseline", …)` caller anywhere.** `run_prototype.run_arm` / `run_campaign` dispatch only
   the six frozen arms; neither iterates a baseline list. **The baseline branch is unreachable in the
   campaign.**
4. **`analyze_campaign` has no reward-baseline panel** — no function computes "fraction LLM beats best
   hand-reward" or the normalized improvement. `scripts/inspect_rewards.py` is reward **forensics**
   (qualitative interpretability / hacking taxonomy), not a hand-reward evaluator.
5. **The config that would feed it is broken anyway.** `config/eureka_loop.yaml: baseline_rewards`
   lists `[differential_sharpe, log_wealth, sharpe_episodic, cvar_penalised_mean, drawdown_penalised,
   turnover_penalised]`. The branch resolves names via `getattr(rewards, name)`, but **5 of these 6
   names do not exist** in `rewards.py`:

   | `eureka_loop.yaml` name | exists in `rewards.py`? | actual function name |
   |---|---|---|
   | `differential_sharpe` | ✅ | `differential_sharpe` |
   | `log_wealth` | ❌ | should be `log_growth` |
   | `sharpe_episodic` | ❌ | **no such function** |
   | `cvar_penalised_mean` | ❌ | should be `return_minus_cvar` |
   | `drawdown_penalised` | ❌ | should be `return_minus_drawdown` |
   | `turnover_penalised` | ❌ | should be `return_minus_turnover` |

   If the baseline path were ever invoked as-is, 5/6 would raise `AttributeError`. (This also drifts from
   PREREGISTRATION §9, which names the **9**-strong secondary panel: raw return, return−var, return−CVaR,
   differential Sharpe, mean–variance utility, return−drawdown, return−downside, return−turnover,
   log-growth.)

**Net:** PREREGISTRATION §9 and §1-H1 promise a hand-reward "did the LLM beat the human?" panel; the
machinery is ~70% present (rewards ✅, a worker branch ✅) but the **orchestration + the metric are
absent**, and the only config that references baselines is stale. The H1 claim is currently
**unsupported by any executable** in the repo.

---

## 3. The FinRL plausible-Sharpe band (T4) — with citations + overfit flags

Purpose: a **plausibility band**, not a leaderboard. The agent here trades a 30-name PIT US-equity
sleeve, long-only, fully-invested, costed, OOS 2020–2026H1 (2018–2025 pre-Split-C) — so the relevant
comparator is *honest, costed, walk-forward, US-equity* DRL. The literature clusters there around **Sharpe ≈ 0.8–1.6**.
Anything materially above ~2.0 on US equity, or any crypto number, should be treated as out-of-band
(regime-specific or overfit) and **excluded** from the "plausible SOTA" framing.

### 3a. In-band reference points (realistic, US-equity, costed)

| Source | Universe / window | Method | Reported Sharpe | Note |
|---|---|---|---|---|
| Yang et al. (2020) FinRL **ensemble**, *ICAIF* | DJIA, test 2020-07→2022-03 | PPO/A2C/DDPG ensemble | **1.53** (ensemble); A2C 1.37, PPO 0.99, DDPG 0.88; **DJIA baseline 1.32** | the canonical FinRL US-equity result; ann. ret 25.9%, vol 15.9%, MaxDD −11.4% |
| **FinRL-Meta** (Liu et al., NeurIPS 2022 D&B; arXiv:2211.03107) | US stocks (Dow) | ElegantRL / Stable-Baselines3 | **ElegantRL 1.457** (ann. 22.4%); **SB3 1.621** (ann. 32.1%) — both beat DJIA | the library's headline stock-task benchmark |
| Multimodal DRL (arXiv:2412.17293) | 29/30 DJIA | PPO + signals/forecasts in FinRL | **0.86** (ann. 16.24%, vol 17.49%; Sortino 1.27) | a **conservative, more realistic** point with explicit vol |
| **FinRL Contest 2025** (FinRL-DeepSeek lineage; arXiv:2504.02281) | Nasdaq-100, test 2019→2023 | CPPO + LLM (DeepSeek) sentiment/risk | **Otago Alpha 1.08** (top); Ruijian&Sally 0.95; Queen's Gambit 0.29 | LLM-signal agents; note the **Sharpe/return decoupling** (Queen's Gambit 0.29 Sharpe but +342% cumret) |

**Recommended in-band citation band for the dissertation: realistic costed OOS US-equity DRL Sharpe
≈ 0.85–1.6**, centred near ~1.3–1.5 for the well-tuned FinRL agents, with the DJIA passive baseline
itself at ~1.3 in the 2020–22 window. Use the multimodal 0.86 as the floor of "credible" and FinRL-Meta
~1.6 as the optimistic edge of credible.

### 3b. Out-of-band — the overfit / exclude flags (cite these as cautions)

- **>2.0 on US equity = overfit red flag.** The literature is explicit that extremely high backtest
  Sharpes signal overfitting, not alpha; less-overfit DRL agents tend to have *lower* Sharpe than
  more-overfit ones, and single-validation-set DRL "easily overfits." Standard safeguards (walk-forward
  + embargo, after-cost OOS, factor attribution, multiple-testing reality checks) are exactly what
  separate credible from inflated — and are what this project already implements (PBO/CSCV, Deflated
  Sharpe, embargoed purge, Romano-Wolf/BH).
- **FinRL **Contest 2023** Sharpe 9.56 (cumret 3.50%) — textbook artifact.** A Sharpe of 9.56 on a
  **3-week** window (2023-10-25→11-14) with only 3.5% cumulative return is a short-window /
  annualisation artifact, not deployable alpha. **Exclude.** (Cite it as the cautionary illustration of
  why short-window contest Sharpes must not enter a SOTA band.)
- **Crypto numbers — EXCLUDE wholesale.** FinRL-Meta crypto: **Sharpe 2.992 (ann. return 360.8%)**.
  Different asset class, different volatility/vol-of-vol regime, no survivorship-free PIT equivalent.
- **Jiang & Liang (2017), EIIE (arXiv:1706.10059) — EXCLUDE, with rationale.** Crypto-only; ~4-fold
  returns in 50 days even at 0.25% commission. Two disqualifiers for use as a US-equity bar:
  (i) **the authors themselves report performance was only "average" when EIIE was tested on the stock
  market** despite dominating in crypto — i.e. it does **not** transfer to equities; and (ii) a
  **look-ahead leak** — the cross-validation set is placed at the *end* of the global price matrix,
  *in the future of the test set*. It is a crypto, momentum-rich, leakage-flagged result and is not a
  legitimate equity SOTA comparator.

### 3c. How to use the band defensibly
The headline of this dissertation is **comparative** ("distributional vs scalar feedback at matched
compute"), explicitly **not** "beats the market" (PREREGISTRATION §10). The FinRL band is therefore a
**context/plausibility ribbon** to show the learned arms' realised OOS Sharpe sits in the credible
0.85–1.6 zone (and is not a >2.0 fantasy), **not** a tier the project must win. Plot the arms' realised
Sharpe against this ribbon; state plainly that FinRL numbers are (a) different universes/windows, (b)
not matched-compute, (c) frequently overfit above 2.0, so they bound *plausibility*, not *ranking*.

---

## 4. GAPs to close before the run

**G1 — (BLOCKER for H1) Wire the T1 REWARD_CANON "beat-the-human" arm + metric.** This is the only
gap that touches a *frozen hypothesis* (H1). Three sub-tasks:
- (a) **Dispatch baseline-reward training.** Add a caller that builds `_spec(arm, "baseline",
  reward_name, …)` for each of the 9 `REWARD_CANON` names and trains them at the **same per-candidate
  budget** as the arms (the worker branch already exists; this is orchestration, not new numerics). Run
  them at the winner seed count (30) so the comparison is apples-to-apples with the LLM winners. Note:
  the baselines are **fixed** (no search), so their Deflated Sharpe is deflated by N=1, not by the
  search multiplicity — keep that asymmetry explicit (it favours the baselines, i.e. conservative for
  H1).
- (b) **Compute the Eureka metric.** Add an `analyze_campaign` panel: for each (seed, window) cell,
  `1[LLM_winner_score > max_k REWARD_CANON_k_score]`, report the **fraction** and the **median
  normalized improvement** `(LLM − best_hand)/|best_hand|`, against the **83% / +52%** Eureka reference.
- (c) **Fix the stale config.** `config/eureka_loop.yaml: baseline_rewards` must use the real function
  names (`log_growth`, `return_minus_cvar`, `return_minus_drawdown`, `return_minus_turnover`, drop
  `sharpe_episodic`) — ideally enumerate the **§9 panel** directly from `REWARD_CANON.keys()` to
  prevent drift. As-is, 5/6 names would `AttributeError`. [RESOLVED, R97: the 10-name panel is now
  test-locked to `REWARD_CANON.keys()` in both directions — tests/test_baselines.py.]

**G2 — (documentation) The referenced deep-research findings doc is absent.** The task pointed to
`00_planning/CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md` (the "6-tier ladder + FinRL band"). **There
is no `00_planning/` directory and no such file anywhere in the repo** (verified by glob + find). The
6-tier ladder and FinRL band it was meant to contain are reconstructed in this doc (§3) from primary
sources. If that planning doc is meant to be canonical, it needs to be (re)created or its absence noted;
the campaign should not depend on an un-versioned source.

**G3 — (optional, documented) No genuine market benchmark in the gate.** T0 has no SPX-TR / cap-weighted
line inside the same-universe DeMiguel gate (the anonymised panel has no caps). `market_reference`
already reports a gated full-universe EW proxy + β/α/IR additively. Acceptable as a **documented
limitation**; only close if a non-anonymised market series is pulled.

**Non-gaps (verified OK, do not touch):** the 8 allocators compute correctly and sanely on the real
panel; `benchmark_floor` is wired into `analyze()` and costs every benchmark identically; the
median-per-seed DSR gate avoids seed-averaging inflation; `spy_buy_and_hold` is correctly de-duped out
of `_BENCHMARK_NAMES`; the H4 reward family vertex exactly recovers `raw_return` (max|diff| = 0.0) and
`params_to_source` emits a runnable, sandbox-passable `def reward(...)` for the BO winner's sealed-test
round-trip; T2 (random-search, BO) are live frozen arms.

---

## Appendix — provenance of every claim

**Code, read first-hand:** `src/baselines/strategies.py` (9 allocators incl. spy alias), `src/baselines/
rewards.py` (9 `REWARD_CANON`), `src/baselines/reward_family.py` (6-term H4 family + `params_to_source`),
`scripts/analyze_campaign.py` (`_BENCHMARK_NAMES` L1238, `benchmark_floor` L1262, `analyze()` invocation
L1563), `src/orchestration/parallel.py` (`train_candidate` baseline branch L210-215, `_spec` L406 + its
3 call sites L565/623/640), `scripts/run_prototype.py::run_arm` L224, `scripts/inspect_rewards.py`
(forensics, not an evaluator), `tests/test_baselines.py`, `config/eureka_loop.yaml`, `config/arms.yaml`,
`config/campaign.yaml`, `PREREGISTRATION.md` §1/§5/§9/§10 + R19.

**First-hand execution:** all 8 allocators + 9 rewards + the H4 family run on
`data/gold/returns_panel_univ.parquet` (2018 window, 30 live assets) — every allocator simplex-valid;
GMV var 5.50e-5 < EW 1.24e-4; max-div ratio 2.069 > EW 1.699; all 9 rewards finite over 251 steps; H4
`w_return=1` vertex reproduces `raw_return` to max|diff|=0.0.

**Web sources (citations):**
- Eureka 83% / +52%: Ma et al., *Eureka: Human-Level Reward Design via Coding LLMs*, ICLR 2024 —
  https://arxiv.org/abs/2310.12931 , https://eureka-research.github.io/
- FinRL ensemble (Sharpe 1.53 / DJIA 1.32): Yang et al. (2020) ensemble strategy, FinRL —
  https://arxiv.org/pdf/2111.09395 , https://finrl.readthedocs.io/en/latest/finrl_meta/Benchmark.html
- FinRL-Meta (ElegantRL 1.457 / SB3 1.621 stock; crypto 2.992): Liu et al., NeurIPS 2022 D&B —
  https://arxiv.org/abs/2211.03107 ,
  https://proceedings.neurips.cc/paper_files/paper/2022/file/0bf54b80686d2c4dc0808c2e98d430f7-Paper-Datasets_and_Benchmarks.pdf
- Multimodal PPO Sharpe 0.86 on Dow-29: https://arxiv.org/pdf/2412.17293
- FinRL Contests (Sharpe 9.56/3.5% cumret 2023 overfit artifact; Otago Alpha 1.08, 2025 FinRL-DeepSeek):
  https://arxiv.org/html/2504.02281v3
- Jiang & Liang (2017) EIIE crypto, "average on stocks" + CV-in-the-future leak:
  https://arxiv.org/abs/1706.10059 , https://ar5iv.labs.arxiv.org/html/1612.01277
- DeMiguel, Garlappi & Uppal (2009), *RFS* 22(5):1915–1953, doi:10.1093/rfs/hhm075:
  https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901
- Overfit / >2.0 Sharpe red-flag synthesis: backtest-overfitting literature surfaced via
  https://arxiv.org/pdf/2511.11481 and the Deflated Sharpe Ratio (Bailey & López de Prado 2014)
  https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf

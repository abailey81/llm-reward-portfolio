# Architecture blocks + world-class elevation plan (2026-06-20)

A precise functional decomposition of the **prototype** (laptop de-risking run) and the **project** (the
rented-GPU headline campaign) into blocks, each with: files, responsibility, current state, the
**supervisor-grade gaps** (assessed as a 50-yr ML/stats/quant examiner would), and the elevation plan with
literature anchors. The prototype and project SHARE these blocks (the campaign reuses `run_prototype.run_arm`);
they differ only in scale (candidates/seeds/steps), the LLM author (Gemini vs Opus 4.8), and the sealed test.

> **Guiding principle (scope discipline).** Elevate *engineering, analytics, benchmarking, rigor, and
> throughput* to publishable quality. Do **not** alter the frozen scientific contribution — H2 (distributional
> feedback beats scalar), the fixed SB3-SAC learner, the Eureka loop, the arms, the fitness, the splits — except
> as a flagged, dated pre-registration amendment. Reporting MORE metrics / MORE benchmarks does not touch H2;
> changing the env obs / arms / hypotheses does.

| # | Block | Primary files | Current state | Gap (1=world-class … 5=thin) |
|---|---|---|---|---|
| B1 | **Data pipeline & gold** | `data_pipeline/`, `src/data/{loaders,panel,pipeline,synthetic}.py` | Refinitiv survivorship-free PIT, 953 RICs, checksums, PIT top-30, delisting policy, vix points | **2** |
| B2 | **Environment & regimes** | `src/env/{portfolio_env,runner}.py`, `src/regimes/definition.py` | simplex action, turnover cost, no-look-ahead, vix-lag fixed, 3 regimes | **2** |
| B3 | **Reward contract & sandbox** | `src/reward/contract.py`, `src/sandbox/executor.py` | AST allowlist gate, 2-stage validate, RLIMIT, extraction shim | **1** |
| B4 | **LLM Eureka loop** | `src/llm/{client,loop,prompts,stub_designer}.py` | provider-neutral transport, reflection, diversity, provenance | **2** |
| B5 | **Feedback / measurement (H2 core)** | `src/feedback/{measurement,schema}.py` | empirical+EVT tail stats fed to the LLM | **2** |
| B6 | **Agent / training** | `src/agents/{trainer,factory,evaluator}.py` | SB3-SAC (+TQC), VecNormalize, seeding | **3** (throughput) |
| B7 | **Search baselines (H4)** | `src/search/{random_search,bayes_opt}.py`, `src/baselines/reward_family.py` | random-code + BO-over-template, seeded | **2** |
| B8 | **Reward & strategy baselines** | `src/baselines/{rewards,strategies}.py` | 4 hand rewards (incl. differential Sharpe) + SPY/1N/MV/RP/HRP | **3** (breadth + wiring) |
| B9 | **Selection / fitness** | `src/selection/fitness.py` | held-out DSR-based winner selection | **2** |
| B10 | **Inference / statistics** | `src/inference/*` | per-seed rliable, PBO/CSCV, DSR/PSR, BH/Romano-Wolf, FZ0 ES backtest, null-cal | **1** |
| B11 | **Backtesting & performance analytics** | (NEW `src/backtest/`), `analyze_campaign.benchmark_floor`, `cost_sweep.py` | ~5 metrics (Sharpe/CVaR/maxDD/DSR) + cost sweep | **4 → the headline gap** |
| B12 | **Orchestration & compute** | `scripts/run_{prototype,campaign}.py`, `src/orchestration/parallel.py`, `scripts/bench_compute.py` | per-arm + device-pool parallel scheduler | **3** (full-hardware) |
| B13 | **Analysis / reporting** | `scripts/{analyze_campaign,analyze_results,inspect_rewards}.py`, `power_analysis.py` | PBO/DSR/H2 report, power analysis | **3** (tearsheets) |
| B14 | **Provenance / reproducibility / freeze** | `src/io/results.py`, `src/utils/{provenance,seeding}.py`, `scripts/{freeze,capture_env}.py`, `PREREGISTRATION.md` | env.json, freeze hash, prose↔yaml assert | **1** |

## Supervisor gap analysis + elevation plan (per block)

**B11 — Backtesting & performance analytics (the headline elevation).** Currently the test leg reports only
Sharpe, CVaR-5%, max-drawdown, DSR. A world-class tail-risk study reports a *coherent, citation-anchored* suite
and stratifies it by regime. **Plan:** new `src/backtest/metrics.py` — annualised return/vol, **Sharpe,
Sortino** (Sortino 1994), **Calmar/MAR** (Young 1991), **Omega** (Keating-Shadwick 2002), **Ulcer index +
pain ratio** (Martin 1989), max-drawdown + **drawdown duration**, **CVaR/ES** at {1,5,10}% (Rockafellar-Uryasev
2000), **VaR** historical (empirical quantile; Cornish-Fisher REMOVED 2026-06-20 — non-monotonic for fat
tails, ES dominates), **tail ratio**, downside deviation, skew,
excess kurtosis, **turnover + cost drag**, hit rate, gain/loss & profit factor, information ratio + alpha/beta
vs benchmark, **deflated Sharpe + PSR** (Bailey-López de Prado 2014). Reuse `src/inference` primitives (DRY).
Add a **regime-conditional** breakdown (calm/normal/stress) and a markdown **tearsheet**. Wire into
`analyze_campaign` + `benchmark_floor` so every arm + benchmark is reported on the full suite.

**B8 — Reward & strategy baselines (breadth + wiring).** Expand the hand-reward canon with the canonical
published designs (Sortino reward, drawdown-penalised, Calmar-style, quadratic/MV utility, return-minus-turnover)
and ENSURE all are *run and reported* as reward-design baselines (a strong "did the LLM beat hand-crafted
rewards?" comparison — the user's explicit ask). Expand allocators with **minimum-variance,
maximum-diversification** (Choueifaty-Coignard 2008), **inverse-volatility**, and a **cross-sectional momentum**
(Jegadeesh-Titman) benchmark. All as benchmarks/baselines — NOT new H2 arms.

**B6/B12 — throughput / full-hardware.** Confirm + tune: vectorised envs, `train_freq`/`gradient_steps`,
torch threads, AMP, and (gated) the **SBX/JAX** drop-in for ~order-of-magnitude SAC speedups; saturate the GPU
with concurrent candidate/seed training. Benchmark with `scripts/bench_compute.py`. Research-gated.

**Cross-cutting — leakage & rigor audit (the supervisor's lens).** A documented, checklist-driven audit of
EVERY leakage mode (VecNormalize running-stats during eval, feature scaling fit window, embargo/purge
sufficiency, survivorship, PIT universe, regime labels, reward peeking at future returns, benchmark/strategy
cost symmetry, selection/multiple-testing) — López de Prado, *Advances in Financial ML*. Fix any found.

**Literature grounding.** Every metric/benchmark/design choice cites a primary source; a methods + limitations
writeup positions the contribution against Eureka (Ma et al. 2024) and the recent LLM-reward / risk-sensitive-RL
literature. Recorded in CHANGELOG + DECISION_LOG.

## Execution order (highest grade-value, lowest risk first)
1. **B11 backtest analytics** (additive, the user's explicit example) — new module + wiring + tests.
2. **B8 baselines** (additive comparison strength) — expand + wire + tests.
3. **Leakage/rigor audit** (supervisor lens) — workflow + fixes.
4. **B6/B12 throughput** (research-gated tuning).
5. **B13 tearsheets + literature writeup**; docs throughout.
6. **Exhaustive verify loop** until consecutive-clean; final re-audit.

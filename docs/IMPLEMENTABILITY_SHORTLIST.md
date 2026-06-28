# IMPLEMENTABILITY_SHORTLIST

Consolidated from 195 first-hand per-paper deep-dives. Every item was re-checked
**skeptically** against the four hard gates before promotion:

- **DETERMINISM** — must preserve byte-identical replay (no GARCH/EVT MLE, no
  stochastic solver, no work-stealing async, no live LLM-in-loop).
- **LSEG LICENCE** — must use only the already-licensed in-repo PIT panel / its
  own logged outputs; no new external data, nothing egressed to third-party cloud.
- **FROZEN SAC SCOPE** — must NOT touch the pre-registered SAC agent, env, reward
  grammar, or confirmatory IUT. Only the **report-only/analysis layer** is
  pre-freeze-addable (scope directive 2 bars new agent architectures / multi-agent
  / RAG / new asset classes).
- **REPORT-ONLY** — must be a reporting metric, baseline comparator, or robustness
  diagnostic, not a change to what is measured confirmatorily.

Counts (implementability class as labelled, 195 papers):
- **IMPLEMENT-NOW (as labelled):** 8
- **FUTURE-WORK (as labelled):** 14
- **RELATED-WORK (as labelled):** 168
- **NOT-RELEVANT (as labelled):** 5

---

## 1. IMPLEMENT-NOW — after skeptical re-check

I re-audited every IMPLEMENT-NOW-labelled paper. The honest finding: **most pass,
but several need downgrading or sharp caveats** because the work is *already built*
(so there is nothing net-new to "implement"), or because the confirmatory inference
design is *frozen* and a new statistic can only enter as a clearly-labelled
**supplementary/exploratory** diagnostic, never as a confirmatory test.

### 1a. PASS cleanly — genuine, deterministic, no-data, report-only ADDITIONS

These touch only the analysis layer, run on already-logged returns/p-values, are
closed-form/seedable, and add material value the repo does not already have.

| Paper | Concrete add | Why it truly passes all gates |
|---|---|---|
| **AlphaSharpe** (2502.00029) | Add **AS1–AS4** closed-form higher-moment / downside / regime risk-adjusted metrics as extra results columns beside Sharpe/CVaR/PSR/DSR. **Reject** the LLM-metric-evolution loop and the AlphaSharpe portfolio allocator. | Pure algebra on existing test-leg return series (mean/std/skew/kurt/MDD/regime + fixed ε). Byte-identical; no new data; analysis-layer only; stress-tests whether the scalar-vs-tail ranking is stable under alternative risk lenses. |
| **Quantile-Targeted-Portfolio** (2510.19271) | Add **Tail-Adjusted Sharpe** report-only: Sharpe/\|CVaR95\| and Sharpe-by-modified-VaR95 (Cornish–Fisher). **Reject** the Q-A2C agent (new architecture). | Closed-form post-hoc statistic; directly operationalises the stored "Sharpe is tail-blind" limitation; descriptive only, not in the IUT. |
| **ProbabilisticSharpe-Bailey** (2012) | Add **PSR(SR\*=0)**, **PSR(SR\*=scalar-baseline)** and **MinTRL@95%** per arm, computed from already-logged per-seed equity-curve moments (scipy.stats.norm only). | Skew/kurtosis/length-adjusted closed form; answers "is the eval window long enough to claim a Sharpe gap on non-Normal RL returns?"; reinforces the severity/null framing. |

### 1b. PASS but EFFECTIVELY ALREADY BUILT — cite, do not re-implement

These pass the gates, but project memory shows the machinery is **already wired**.
Net-new code is unwarranted; the correct action is a **provenance citation**, not an
implementation. Honestly classing these as "implement-now" overstates the payload.

| Paper | Status in repo | Action |
|---|---|---|
| **rliable** (2108.13264) | Already the headline inference backbone (per-seed IQM + stratified bootstrap CIs + performance profiles). | Confirm/keep; cite. No new work; just pin the bootstrap RNG seed. |
| **Bailey-DSR** (2014) | DSR + 2nd-PBO-on-DSR already in the analysis layer (memory: PBO full-enumeration + DSR). | Cite as provenance; disclose Witzany-2021 near-zero-mean CSCV bias + effective-N for correlated arms. |
| **Bailey-PBO** (2017)* | PBO/CSCV full-enumeration already implemented. | Cite as the source paper; nothing to add. (*labelled RELATED-WORK; included here for completeness.) |
| **BenjaminiHochberg-FDR** (1995) | BH/conjunction correction already pre-registered (R25/R31). | Cite as canonical source; disclose Benjamini–Yekutieli as the dependence-robust honest variant. |
| **HarveyLiuZhu-CrossSection** (2016) | Same FDR/FWER (Holm/BHY) machinery already in the multiplicity design (R31). | Cite as the field hurdle; redundant to re-add (double-correction risk). |
| **PolitisRomano-StationaryBootstrap** (1994) | Block bootstrap already underpins the headline pipeline ("block-length confound" in memory). | Cite as source; ensure the block RNG is seeded for byte-identical replay. |

### 1c. PASS as a SUPPLEMENTARY diagnostic ONLY — downgraded from "headline-grade"

These are deterministic, no-data, report-only, and genuinely useful — **but** the
confirmatory inference family is frozen/pre-registered, so they may enter **only as
clearly-labelled supplementary/robustness** statistics, never as new confirmatory
tests (adding them to the IUT family would be a post-freeze design change).

| Paper | Concrete add (supplementary only) | Caveat that forces the downgrade |
|---|---|---|
| **LedoitWolf-SharpeTest** (2008) | Studentized **circular-block-bootstrap Sharpe-difference** test (tail/dependence-robust) on tail-arm vs scalar vs placebo. | Must use a **fixed block size / deterministic block grid** (NOT the GARCH-residual calibration, which is an MLE determinism hazard) and a pinned RNG. Must **supplement**, not replace, the pre-registered rliable inference. |
| **NoldeZiegel-ElicitabilityBacktesting** (2017) | DM **comparative backtest on the strictly-consistent joint (VaR,ES) score** + a T2 calibration test, HAC variance, red/yellow/green verdict, tail-arm vs scalar/placebo. **Port only the scoring/test formulae; NOT the AR-GARCH/EVT forecasting layer.** | The AR-GARCH-MLE+EVT forecasting layer is non-deterministic and out of scope; only the closed-form scoring/test math is admissible, as a robustness diagnostic. |
| **ScientificOutlook-Harvey** (2017) | **SD-MBF = −e·p·ln(p)** and the Bayesianized p-value over a **pre-registered grid of prior odds** (even, skeptical 4:1-against), beside the frequentist H2-RA/H2-Tail p-values. | The prior grid must itself be pre-stated (else it is prior-hacking, which Harvey warns against). Supplementary transform, not a replacement of the decision rule. |

### 1d. The one new REPORT-ONLY BASELINE worth adding

| Paper | Concrete add | Gate verdict |
|---|---|---|
| **DeMiguel-1overN** (2009) | **1/N equal-weight** arm in the benchmark ladder, same walk-forward/purge-embargo splits, same Sharpe/CVaR/turnover reporting. | PASS: parameter-free, deterministic, no new data, report-only comparator (the canonical "severe floor"). **Must be declared pre-freeze** as a baseline. |
| **LopezDePrado-HRP** (2016) | **HRP** allocator comparator (scipy hierarchical clustering + recursive inverse-variance bisection) on the same panel covariance, same rebalance schedule. | PASS *conditionally*: deterministic only if the **linkage method + asset tie-break ordering are pinned**; report-only baseline; static, so value is purely as a comparator. **Declare pre-freeze.** |

---

## 2. HONEST BOTTOM LINE on IMPLEMENT-NOW

**Do any truly pass as net-new, headline-grade additions? A few — but the payload is
thin and mostly "reporting hygiene," not result-changing.** Specifically:

- The genuinely **net-new, clean** additions are: **AlphaSharpe AS1–AS4**,
  **Tail-Adjusted Sharpe**, **PSR/MinTRL** (§1a), and the **1/N** (and optionally
  **HRP**) baselines (§1d). All are report-only robustness/comparator metrics.
- **DSR, PBO, BH, block-bootstrap, rliable** are **already built** — promote them to
  *citations*, not implementations (§1b). Listing them as "implement-now" would be
  double-counting work already done.
- **LedoitWolf Sharpe-diff, joint-(VaR,ES) DM backtest, SD-MBF** are deterministic
  and useful but can only be **supplementary** because the confirmatory IUT family is
  frozen (§1c).

**Therefore the honest characterisation:** *no IMPLEMENT-NOW item changes the
confirmatory result or the agent.* They strengthen the **severity/null-framing and
robustness story** of an already-frozen study. If the user wants a minimal, maximally
defensible set, ship exactly four: **1/N baseline + AS1–AS4 + Tail-Adjusted Sharpe +
PSR/MinTRL**, all report-only, plus the provenance citations in §1b. Everything else
is RELATED-WORK or FUTURE-WORK.

---

## 3. FUTURE-WORK (deferred; scope/determinism/data forbids pre-freeze)

These are genuinely relevant but blocked by the frozen-SAC scope, a nondeterministic
dependency, or new-data needs. They are v2 / second-paper / robustness-appendix items.

| Paper | Deferred item | Blocking gate |
|---|---|---|
| **Platoon-Reward / PCRD** (2504.19480) | Convergence-aware training screen over SAC learning curves (maps to the undertraining/critic-explosion limitation). | Touches candidate-selection (confirmatory) unless kept purely descriptive. |
| **REvolve** (2406.01309) | Population-based reward evolution (LLM crossover + island migration) vs greedy single-shot. | New search architecture; human-Elo loop. |
| **URDP** (2507.02256) | Self-consistency uncertainty score over sampled reward programs (cheap descriptive diagnostic); UABO loop deferred. | Bi-level search redesign touches frozen pipeline. |
| **QuantaAlpha** (2602.07085) | Trajectory-level mutation/crossover search; AST-complexity/redundancy diagnostic is the only report-only sliver. | New multi-agent evolutionary engine. |
| **Coache-Jaimungal DynamicRisk** (2112.13414) | Recursive (time-consistent) per-step CVaR reward primitive; report-only time-consistency diagnostic. | New actor-critic agent for the full method. |
| **CarteaCoacheJaimungal** (2022) | Strictly-consistent (VaR,CVaR) scoring as a dynamic-CVaR diagnostic on realized per-step PnL. | Full elicitable actor-critic is a new agent. |
| **Acerbi-Spectral** (2002) | Spectral risk measure (exp risk-spectrum) as ex-post whole-tail coherent metric. | New post-freeze confirmatory metric; report-only/robustness only. |
| **AhmadiJavid-EVaR** (2012) | EVaR_5% + α-ladder companion to CVaR-5% (Gaussian closed-form + deterministic empirical inf over z). | Confirmatory metric set is frozen. |
| **BayerDimitriadis-RegressionESBacktest** (2022) | ES-calibration (Intercept/Strict ESR) backtest on SAC OOS returns. | Needs a per-step OOS ES forecast series not yet defined. |
| **FisslerZiegel** (2016) | FZ joint (VaR,ES) consistent-score backtest as secondary tail evaluation. | Cannot enter frozen IUT; report-only/secondary. |
| **Hansen-SPA** (2005) | SPA test (scalar/placebo benchmark vs tail arms) on per-seed OOS series. | Adding to confirmatory family alters frozen design; supplementary only. |
| **RomanoWolf-Stepwise** (2005) | Studentized StepM stepdown FWE across the 7-arm roster. | Supplementary robustness only (primary multiplicity already pre-registered). |
| **White-RealityCheck** (2000) | Stationary-bootstrap RC max-statistic p-value over arms. | Supplementary selection-bias control; PBO already covers the headline. |
| **FunSearch** (2024) | Evolutionary search over reward-program space (skeleton + island model) — v2 search-ablation. | New search architecture; async nondeterminism. |
| **BiasCorrectedPOT-CVaR / Troop** (2021) | UPOT bias-corrected extreme-CVaR (α≥0.99) cross-check vs CVaR-5%. | GPD-MLE determinism hazard; needs large pooled tail samples. |
| **Kyle-PriceImpact** (1985), **SquareRootLaw-Toth** (2011), **TradingCosts-Frazzini** (2018) | Nonlinear (Kyle-λ / √-law) transaction-cost robustness re-scoring. | Changes env cost dynamics; needs ADV/volume series. |

---

## 4. USER-GATED-DATA (relevant methods blocked purely by data licence / new asset class)

None of these are addable now; each would require **new external/licensed data** (or
a new asset class), which only the user can sanction under the LSEG agreement. They
are listed so the user can decide whether any data acquisition is worth pursuing.

| Paper | Data it needs (all NEW / external) |
|---|---|
| **Adaptive-Alpha-Weighting-PPO** (2509.01393) | yfinance equities + EODHD news-sentiment API + Groq LLM. |
| **Darmanin-Vella** (2508.02366) | Interactive Brokers + iVolatility + SEC-API + Alpaca news. |
| **FinRL-DAPO** (2505.06408), **FinRL-DeepSeek** (2502.07393) | FNSPID news corpus + DeepSeek-extracted sentiment/risk. |
| **News-Driven-LLM-RL-Portfolio** (2411.11059) | Finnhub news + GPT sentiment. |
| **Alpha-Mining-MCTS** (2505.11122), **CogAlpha** (2511.18850), **Alpha-R1** (2512.23515), **QuantAgent** (2412…), **RD-Agent** (2505…) | Chinese A-share CSI 300/500 + Qlib factor libs (new asset class). |
| **Expert-Investment-Team** (2602.23330) | Japanese TOPIX 100 via Yahoo/EDINET/Ceek.jp (new market). |
| **Macro-Economist-Agent** (2606.08283) | FRED macro + commodity ETFs (new asset class). |
| **Decision-Language-Model** (2402.14807) | Gated ARMMAN maternal-health RMAB data. |
| **ProfitMirage** (2510.07920) | Yahoo/Alpaca/FNSPID + HK/CN equities + crypto (new asset classes). |
| **Trade-R1** (2601.03948), **Trading-R1** (2509.11420), **TradingGroup** (2508.17565), **FinAgent** (2024), **FinMem** (2023), **TradingAgents** (2024), **Stock-Evol-Instruct** (2024) | External news/price feeds (Finnhub/Alpaca/yfinance/Reddit/X) + cloud LLM calls. |
| **NatGas-Distributional-RL** (2501.04421) | Proprietary Predictive Layer TTF gas-futures (1141 features). |

> Note: most of these *also* fail the frozen-scope gate (LLM-as-policy / multi-agent /
> RAG), so even with data they would be FUTURE-WORK at best, not implement-now.

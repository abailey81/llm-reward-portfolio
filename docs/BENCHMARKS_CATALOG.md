# Benchmark & baseline catalogue (the "beat-the-human" panel)

Every human-designed reward baseline and classical allocator the LLM-authored reward is compared against —
each with its **implemented per-step formula**, **primary paper**, and **citation status**. These are
**report-only comparators** (the Eureka "beat-the-human" standard; Ma et al. 2024): they position the
LLM-designed winner, they are **NOT** new confirmatory IUTs and do not enter the H2 multiplicity family.
Pre-registered pre-freeze (see PREREGISTRATION R62). All are **deterministic + numpy/scipy** (replayable).

Formulas are stated as IMPLEMENTED in `src/baselines/{rewards.py, strategies.py}`; primary coordinates that
were verified first-hand from the on-disk PDFs are tagged ✓ (see `docs/PAPER_BENCHMARK_EXTRACTIONS.md`).
Citation reconciliation (published vol/pages) is the P6/P7 reference-round task; flags live in
`docs/CITATION_VERIFICATION_TODO.md`.

## A. Human-designed reward baselines — `REWARD_CANON` (9), `src/baselines/rewards.py`
| Reward | Implemented per-step formula | Primary paper | Cite status |
|---|---|---|---|
| `raw_return` | `r_t = wᵀr` (realized portfolio return) | — (foundational; risk-neutral control) | n/a |
| `log_growth` | `log(1 + r_t)` (growth-optimal) | Kelly (1956); Thorp (1971); = Jiang EIIE per-step `ln(μ_t y_t·w_{t-1})` ✓ | `jiang2017eiie` ✓; Kelly/Thorp pending |
| `return_minus_variance` | `r_t − λ·Var_w(r)` (rolling-window pop. variance) | Markowitz (1952) E-V ✓ | pending (P6) |
| `mean_variance_utility` | `r_t − ½λ·Var` (quadratic utility) | Markowitz (1952), *J. Finance* 7(1):77–91 ✓ | pending (P6) |
| `return_minus_cvar` | `r_t − λ·max(CVaR_α, 0)`, CVaR = mean of lower-α tail | Rockafellar & Uryasev (2000), *J. Risk* 2(3):21–41 ✓ | `rockafellar2000cvar` |
| `return_minus_downside` | `r_t − λ·downside-semideviation` (below target) | Sortino & van der Meer (1991), *JPM* | pending (P6) |
| `return_minus_drawdown` | `r_t − λ·drawdown` | Calmar/MAR lineage (Young 1991; Magdon-Ismail) | pending (P6) |
| `return_minus_turnover` | `r_t − c·‖w − w_prev‖₁` (transaction-cost-penalised) | turnover/cost lineage | pending (P6) |
| `differential_sharpe` | Moody-Saffell online `Dₜ = (B_{t−1}ΔA − ½A_{t−1}ΔB)/(B_{t−1}−A_{t−1}²)^{1.5}` ✓ | Moody & Saffell (2001), *IEEE TNN* 12(4):875–889 ✓ | `moody2001directrl` ✓ |

## B. Classical allocator benchmarks — `STRATEGY_CANON` (10), `src/baselines/strategies.py`
| Allocator | Algorithm | Primary paper | Cite status |
|---|---|---|---|
| `spy_buy_and_hold` | static market hold (passive benchmark) | — | n/a |
| `equal_weight` | `wᵢ = 1/N` | DeMiguel, Garlappi & Uppal (2009), *RFS* 22(5):1915–1953 ✓ | `demiguel2009naive` |
| `mean_variance` | Markowitz max-Sharpe w/ **Ledoit-Wolf shrinkage** cov | Markowitz (1952) ✓ + Ledoit & Wolf (2004) ✓ | `ledoit2004honey` ✓ (added) |
| `minimum_variance` | long-only GMV `argmin wᵀΣw` | Markowitz lineage | pending (P7) |
| `inverse_volatility` | `wᵢ ∝ 1/σᵢ` | risk-budgeting lineage | pending (P7) |
| `risk_parity` | equal-risk-contribution `σᵢ·(Σw)ᵢ` equalised | Maillard, Roncalli & Teiletche (2010), *JPM* 36(4) | ⚠ **re-acquire REAL Maillard** (on-disk file mislabeled Cagna-Casuccio 2014) |
| `hrp` | Hierarchical Risk Parity: corr-dist `d=√(½(1−ρ))` → quasi-diag → recursive bisection ✓ | López de Prado (2016), *JPM* 42(4):59–69 ✓ | pending (P7) |
| `maximum_diversification` | max diversification ratio `(wᵀσ)/√(wᵀΣw)` | Choueifaty & Coignard (2008), *JPM* 35(1):40–51 | pending (P7) |
| `cross_sectional_momentum` | rank by trailing return, long top | Jegadeesh & Titman (1993); Moskowitz, Ooi & Pedersen (2012) | pending (P7) |
| (`_long_only_max_sharpe`) | tangency / max-Sharpe (internal helper) | Markowitz lineage | pending (P7) |

## C. Statistical-reporting + inference comparators (already implemented + cited/verified)
- **rliable** (Agarwal et al. 2021): `iqm`, `probability_of_improvement`, `stratified_bootstrap_ci`, and the new
  `performance_profile` — all in `src/inference/reporting.py`, **oracle-validated against the `rliable` library**.
- **Multiple-testing**: Benjamini-Hochberg (1995) FDR `benjamini1995fdr`; **Romano-Wolf (2005)** stepdown FWER
  `romanowolf2005stepwise` ✓ (Econometrica 73(4):1237–1282, verified first-hand) — `src/inference/multiple_testing.py`.

## D. Decision: do any *new* baselines pass the add-now gate? — NO (honest verdict)
The publication-gap research (3-0 verified) confirmed the panel above already covers the canonical reward +
allocator literature top venues expect. Candidate additions were assessed against the gate
(verified-first-hand cite ∧ deterministic ∧ numpy-only ∧ no arbitrary inputs ∧ no scope-creep, CLAUDE.md
directive 2):
- **Black-Litterman** — DEFERRED. The 1992 FAJ master posterior is verified ✓, but a faithful BL comparator
  needs market-cap equilibrium weights (Π via reverse optimisation) **and** a view specification (P, Q, Ω, τ).
  The panel has no market-cap series, and arbitrary views would make it a non-reproducible "human baseline".
  A no-views BL collapses to the equilibrium/market portfolio (≈ `spy_buy_and_hold`). → Future Work, not added.
- **Time-series momentum (Moskowitz 2012), 60/40, cap-weight** — either duplicate `cross_sectional_momentum`'s
  signal or need data not in the panel. → not added.
- **Spectral-risk / prospect-theory rewards** — interesting but add arbitrary curvature parameters and are not
  established portfolio-RL baselines; they would dilute, not strengthen, the comparison. → Future Work.

**Verdict: no new baseline is added.** The grade/publishability work is *completeness* (citations, the
performance-profile reporting, the Eureka-ablation framing), not volume — adding redundant or
arbitrary-parameter comparators would be noise. This is recorded as the P8/P9 outcome.

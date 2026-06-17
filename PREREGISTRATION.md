# PRE-REGISTRATION — frozen design record

**Status:** 🟡 DRAFT — to be FROZEN at the end of Phase 1 (target Mon 23 Jun 2026), then hashed into
`docs/DECISION_LOG.md` via `scripts/freeze.py`. Until frozen, editable; after freeze, changes require
an explicit, dated **amendment** entry approved by the user. The machine-readable mirror is
`config/preregistration.yaml` (the two must agree; `freeze.py` checks).

**Why pre-register.** The headline H2 can return a null. Fixing the hypotheses, budgets, metrics, and
analysis plan *before* the campaign makes a null a credible finding about the question as posed, not a
moved goalpost. This document is the spine of that guarantee.

---

## 1. Hypotheses (frozen)
The unit of inference is **a reward function's out-of-sample risk-adjusted performance**, over the
test span, across seeds and the candidate population — NOT the cross-section of assets.

- **H1 — LLM vs hand-designed.** H0: median OOS risk-adjusted performance of LLM-designed rewards ≤
  the best hand-designed baseline (raw return; return−variance; return−CVaR; differential Sharpe).
- **H2 — distributional vs scalar (HEADLINE).** H0: the distributional-feedback arm ≤ the scalar arm,
  OOS, at matched compute. The contrast must **also survive beyond the placebo** (information ≠
  token-count) **and beyond scalar+CVaR-5%** (tail-*shape* ≠ any-downside-number).
- **H3 — iterative vs single-shot.** H0: multi-generation ≤ single-shot at matched candidate budget.
- **H4 — LLM vs uninformed search.** (a) vs random-search-over-code; (b) vs Bayesian-optimization-
  over-template. Two separate tests.
- **Secondary (not numbered) — distributional vs mean critic.** SAC (mean) vs TQC (quantile), same
  family. Reported separately from H2; run only if the Phase-0 TQC smoke is green.

## 2. The contribution axis (frozen framing; audit A-1)
The headline is the **feedback channel**. All feedback arms run the **same fixed agent (SB3 SAC)**.
The distributional feedback is **measured off-critic** from realized returns, so it does not depend on
the agent's critic.

## 3. The six arms (matched compute)
`distributional` · `scalar` · `placebo` · `scalar_cvar5` · `random_search` (H4a, over code) ·
`bayes_opt` (H4b, over a fixed parametric template). All consume the **same candidate budget** — the
property that licenses the comparative claim.

## 4. The frozen tail-diagnostic set (audit B-1, B-2, B-7)
Measured on the **training-period** realized portfolio log-returns (measuring on validation while also
*selecting* on validation would re-introduce overfitting). Estimator: **empirical primary** for the
body (CVaR/quantiles/left-tail-mass/robust-skew); **GPD/EVT tail fit** for the extreme levels.
- `cvar_25`, `cvar_10` — empirical (headline-estimable)
- `cvar_05`, `cvar_01` — EVT/GPD peaks-over-threshold; a **threshold-sensitivity diagnostic** is
  implemented (`ReturnDistribution.threshold_sensitivity`) and **bias-corrected POT** (Troop et al.
  2021) is the **frozen Phase-1 enhancement** (deep-research #2, RESEARCH-2). CVaR-1% **retained but
  flagged high-variance** (~7–8 exceedances on ~750 returns).
- `left_tail_mass` — fraction below `−k·σ`, **k = 2.0** (frozen).
- `robust_skew` — quantile-based (Bowley) skewness `((Q95−Q50)−(Q50−Q05))/(Q95−Q05)`, **frozen sign
  convention: NEGATIVE when the left tail is longer** (resolves decision-log IMPL-2; matches
  `src/feedback/measurement.py`).
- **Reliability diagnostic** (old "quantile-crossing rate"): identically zero for sorted empirical
  quantiles → **DROPPED from the headline set** (decision frozen), kept only as a diagnostic of the
  *optional* secondary neural instrument. **Moors kurtosis excluded.**

## 5. Fitness / selection (frozen; audit B-3)
Winner selected on **validation Deflated Sharpe** (realized validation returns; independent of the
candidate reward's own units, so selection cannot be reward-hacked). Optional `−λ·validation-CVaR`
(λ pre-registered). Fed-back signal (train returns) and selection signal (val returns) are on
**different splits**.

## 6. Loop protocol (frozen; audit B-3, B-5)
The reward-design loop runs **once** with a **fixed per-candidate training-step budget**.
CPCV is applied to the **fixed winners afterward** for inference — NOT inside each fold (that would be
~16× the compute). Single-shot arm (H3) draws the whole budget in one generation.

## 7. Data (frozen; audit B-2, C-3)
Point-in-time, survivorship-free US large-cap equities, **2005–2025 (full 20 years — not a scoping
lever)**; top-30 by PIT market cap; delisting returns retained; two-vendor reconciled; SHA-256 frozen.
Splits: **train 2005–2014** (agent learns + feedback measured), **val 2015–2017** (selection),
**test 2018–2025** (untouched until final inference); embargo between splits. Data is licensed and
**not redistributable** — ship checksums + pipeline + a synthetic panel of identical shape.

## 8. Contamination protocol (N3)
Structural blinding (anonymised arrays, no tickers/dates) · cutoff-stratified evaluation around the
model's training cutoff · one open-weights second model with a different cutoff · explicit statement
that reward-design contamination ≠ forecasting contamination; reward-design priors are the **object of
study** (H4), not a defended weakness.

## 9. Benchmark suite (frozen)
SPY buy-and-hold · equal-weight (1/N) · mean-variance with Ledoit-Wolf shrinkage · risk parity · HRP.

## 10. Inference / analysis plan (frozen; audit B-8, C-7)
**PBO/CSCV = primary** overfitting guard. Deflated Sharpe reported but **secondary** (effective trial
count ill-defined under guided search). Stationary-bootstrap (Politis-Romano 1994) difference tests:
**Sharpe** (studentized, Ledoit-Wolf 2008 in spirit — note LW use the *circular* block bootstrap of
Politis-Romano 1992) and **two-sample CVaR-difference** (the Ledoit-Wolf-for-Sharpe analogue; no
published named test exists, so bespoke + null-calibration, audit C-7). **Separately**, for *forecast*
comparison the **DM comparative ES backtest** on the strictly consistent FZ0 (VaR, ES) score is used
(Fissler-Ziegel 2016 joint elicitability; Nolde-Ziegel 2017) — implemented in `src/inference/es_backtest`.
**Power caveat** (Bauer 2025): tail-risk difference tests have low power at the most extreme quantiles
(CVaR-1%/2.5%) and short windows. **rliable** seed reporting (IQM, probability of improvement, stratified
bootstrap CIs). **Cross-arm/metric multiple-testing correction** (Romano-Wolf or Benjamini-Hochberg FDR).
**Harvey-Liu t>3** hurdle on any alpha claim. **The trial count is stated explicitly.** The headline
claim is **comparative**
("distributional vs scalar at matched compute"), not "beats the market".

## 11. Algorithms (frozen)
Headline: **SB3 SAC** (fixed across all feedback arms). Secondary critic: **TQC** (sb3-contrib).
Robustness on winners only: PPO, TD3. Continuous-only fallback: D4PG (never QR-DQN — discrete-only).
Library-default hyperparameters, identical across arms, with a runtime equivalence test.

## 12. Compute (frozen plan; audit A-6/C-4)
RTX 4090 for development; **UCL Myriad** for the parallel campaign as an array job over
arms × seeds × folds. Contingency only if both unavailable: one Colab Pro+ GPU + down-rank H3/H4 +
the CVaR-5% arm.

> **Pre-freeze amendment (2026-06-17, ADR-023).** UCL Myriad is **not available** and
> Azure-for-Students/GCP GPU quota is blocked. The recorded compute plan is now: Phase-0 on the owned RTX
> 4050; campaign on a **rented RTX 4090 + seeds-on-winners** (≈$13–16, ~1.5 days), free fallback =
> Kaggle+Lightning+Colab+laptop. The matched-compute design, arms, seeds, and folds are **unchanged** —
> only the hardware/venue. Authoritative detail: `docs/COMPUTE_AND_TRAINING_TIME.md`.

---

### Freeze record
| Item | Value |
|---|---|
| Frozen on | _(to fill at Phase-1 freeze)_ |
| Content hash (SHA-256) | _(emitted by `scripts/freeze.py`)_ |
| Phase-0 smoke pass recorded | _(DECISION_LOG entry id)_ |
| Amendments | _(none yet)_ |

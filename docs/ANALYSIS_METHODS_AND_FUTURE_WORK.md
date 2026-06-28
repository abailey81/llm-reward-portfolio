# Analysis & backtest methods — what is implemented, and Future Work

**Purpose.** A reader's map of the statistical/backtest machinery that is **already implemented and
pre-registered**, and a clearly-labelled **Future Work** list of further methods (rolling-window analytics,
expanded Monte-Carlo) that are deliberately **NOT** added to the confirmatory pipeline.

**Why nothing new is bolted onto the confirmatory analysis.** The grade strategy is a *pre-registered,
frozen* design (`PREREGISTRATION.md` + the canonical freeze hash over `inference.yaml`). The inference plan,
benchmark suite, and analysis statistics are fixed *before* results are seen. Adding new analyses after the
fact — however "advanced" — is **researcher degrees of freedom** (a garden of forking paths) that *weakens*
a pre-registered null rather than strengthening it (CLAUDE.md PD-2/PD-3). So the methods below are the
frozen set; §3 lists extensions as exploratory Future Work, explicitly outside the confirmatory claims.

---

## 1. Already implemented — the confirmatory backtest & inference stack

These live in `src/inference/`, `src/backtest/metrics.py`, and `scripts/analyze_campaign.py`.

### Resampling / Monte-Carlo (already present, in rigorous forms)
- **Stationary block bootstrap** (`inference/bootstrap.py`, Politis–Romano 1994): Monte-Carlo resampling that
  *preserves serial dependence* — the correct MC scheme for return series (a naive i.i.d. MC would be wrong
  here). Drives the Sharpe re-centred basic-bootstrap difference test and the CVaR-difference test.
- **CSCV / PBO** (`inference/overfitting.py`; `campaign_pbo`, `campaign_pbo_dsr`): combinatorially-symmetric
  cross-validation (Bailey–López de Prado 2014) — the probability-of-backtest-overfitting estimate. This is
  the principled "many resamples" overfitting control, applied to winners (audit B-3).
- **Monte-Carlo size/power calibration** of the DM/ES backtest (`inference/es_backtest.py`,
  `dm_size_power_calibration`): empirical Type-I size + power of the tail test under simulation.

### Risk-adjusted performance & deflation
- **Deflated / Probabilistic Sharpe Ratio** + effective-N (`inference/deflated_sharpe.py`;
  `winner_dsr`, `dsr_effective_n`) — Bailey–López de Prado 2014; non-normality- and trials-adjusted.
- **Core metrics** (`backtest/metrics.py`): Sharpe/Sortino, max-drawdown/Calmar, volatility, turnover,
  VaR/CVaR.

### Tail / coherent-risk backtesting
- **FZ0 joint (VaR, ES) backtest** with the **Harvey–Leybourne–Newbold** small-sample DM correction
  (`inference/es_backtest.py`) — Fissler–Ziegel elicitability; Diebold–Mariano corroboration.
- **EVT/GPD tail estimator** with threshold-sensitivity diagnostic (`feedback/measurement.py`).

### Multiplicity, equivalence & power
- **Romano–Wolf step-down** + **Benjamini–Hochberg** + **cross-hypothesis multiplicity**
  (`inference/multiple_testing.py`, `analyze_campaign.py::cross_hypothesis_multiplicity`).
- **TOST equivalence** in DSR units (`analyze_campaign.py::_iqm_tost`, `h2_tost_dsr`) — the bankable-null bound.
- **Power analysis** (`analyze_campaign.py::_power_analysis`, `scripts/power_analysis.py`).

### Robustness, leakage & accounting (already in the frozen plan)
- **Walk-forward + purge/embargo splits**; **CPCV on winners**; **cost-sweep** re-pricing across a bps grid;
  **delisting-band** sensitivity sweep; **benchmark-floor** + **beat-the-human** (Eureka-style H1);
  **OOD stress** + **contamination** screens; **divergence report**; **compute accounting**.

> Net: the "advanced moving-window / Monte-Carlo" capability a reader might ask for is **already present** —
> as the walk-forward + CPCV design, the stationary bootstrap, CSCV/PBO, and the MC-calibrated tail test —
> in their *methodologically defensible, pre-registered* forms.

### New pre-freeze methodology upgrades — tail-uncertainty propagation (`feedback/measurement.py`)

Added **before** the freeze (so they are part of the confirmatory apparatus, not post-hoc): the fed CVaR
point estimate is now accompanied by an honest uncertainty report, computed by the same estimator class.
These are genuine methodology upgrades over a bare point estimate, not new hypotheses.

- **Stationary-block-bootstrap CVaR confidence intervals** (`ReturnDistribution.cvar_ci`, driven by
  `_stationary_block_indices` / `_bootstrap_cvars`): a percentile CI for each CVaR-`α` from Politis–Romano
  (1994) block resamples of the **time-ordered** finite returns — resampling in serial order to preserve
  dependence (an i.i.d. CI would be wrong for return series). Same stationary scheme as the confirmatory
  CVaR-difference test, so the uncertainty statement is internally consistent.
- **Reliability tier** (`ReturnDistribution.reliability`): a small-sample evidence tier for CVaR-`α` keyed
  to the tail exceedance count (Belzile–Davison 2022) — `high` (>30 exceedances) / `medium` (7–30) / `low`
  (<7) — so a consumer can weight an estimate by its evidence. At `T≈750` the CVaR-1% tail sample is small
  and is flagged as such rather than reported at face value.
- **Bootstrap bias estimate** (`ReturnDistribution.cvar_bias`): the block-bootstrap estimate of the
  small-sample bias of CVaR-`α` (mean bootstrap CVaR − point estimate), reported as a **sensitivity**
  beside the point estimate. The verified verdict is that plain-MLE CVaR error at this `n` is dominated by
  variance, not bias, so we *report* the bootstrap bias rather than assert a correction (the full Troop et
  al. 2021 UPOT bias-correction remains Future Work — §3).

These are surfaced together in the per-estimate uncertainty artifact
(`ReturnDistribution.cvar_uncertainty_report`): per level, the point estimate, the block-bootstrap 90% CI,
the bias estimate, the effective exceedance count, and the reliability tier. The fed feedback block itself
is unchanged — enriching it with the CI is a flagged, arms-parity-gated option, not the default.

---

## 2. Test-rigor evidence (engineering, not a frozen-design item)
- ~900+ behaviour/property/invariance tests; property-based (Hypothesis), metamorphic, adversarial-security
  (sandbox), determinism/replay, and cross-file freeze-gate guards.
- A **mutation-testing** exhibit on the core numeric modules (see `docs/TEST_RIGOR.md`) demonstrates the
  suite *kills injected faults* — stronger evidence of test quality than coverage % alone.
- Measured line coverage with a CI floor.

These strengthen the *credibility* of the frozen results without changing the design.

---

## 3. Future Work — exploratory extensions (NOT in the confirmatory pipeline)

Explicitly outside the pre-registered claims; suitable for an exploratory appendix / a v2 paper. Each would
require a dated pre-registration amendment + supervisor sign-off **before** it could inform any hypothesis.

- **Rolling-window performance analytics:** rolling Sharpe/Sortino/CVaR and rolling factor-betas over the
  walk-forward, as *descriptive* exhibits (regime-conditional behaviour). Caveat: overlapping windows induce
  strong serial correlation → inference must use the existing block-bootstrap, not naive CIs.
- **Expanded Monte-Carlo:** parametric/filtered historical simulation (e.g. GARCH-filtered, or a copula on
  the residuals) as an *alternative* resampling scheme to cross-check the stationary bootstrap — reported as
  a sensitivity, never as a second confirmatory test (multiplicity).
- **Non-stationary EVT:** time-/covariate-varying GPD tail parameters (e.g. VIX-driven), cf. `nsEVDx`
  (arXiv:2509.07261) — would replace the frozen stationary GPD, so strictly Future Work.
- **Bias-corrected POT (Troop et al. 2021):** documented in `measurement.py` as Future Work — its
  second-order correction is undefined/ill-conditioned at this sample size and tail level.
- **Duration/severity ES backtest** (Hué–Hurlin–Lu 2024, arXiv:2405.02012) as an additional tail diagnostic.
- **Block-length sensitivity** for the stationary bootstrap (sweep the expected block length) as a robustness
  exhibit on the existing test.
- **Conditional GARCH-EVT (McNeil–Frey filtered EVT) — INVESTIGATED and REJECTED for the confirmatory
  pipeline.** A two-stage GARCH-filter-then-EVT-on-standardised-residuals tail estimator was considered and
  deliberately *not* adopted, for three first-hand reasons: (i) **wrong domain** — the fed tail is computed
  on **aggregated** portfolio returns (already a sum over names/sessions), not a single conditionally-
  heteroskedastic asset series, so the GARCH conditioning McNeil–Frey assumes is largely averaged out;
  (ii) **model risk at `n≈750`** — adding a GARCH mean/variance model on top of the GPD multiplies the
  estimated parameters and the failure modes at a sample size where even the plain GPD tail is already
  high-variance; (iii) **determinism** — the `arch` package's MLE optimiser breaks the byte-identical
  replay guarantee the pipeline relies on (provenance/replay, CLAUDE.md PD-6). It is retained **only as a
  Future-Work A/B** sensitivity against the frozen unconditional GPD, never as a confirmatory estimator.
- **Reproducibility container:** a pinned **Docker repro image** (locked CUDA / Python / wheel set) for
  third-party bit-reproduction of the campaign. Grade-neutral pre-freeze (the version pins + freeze
  manifest already secure determinism), so deferred to Future Work.

**Bottom line for the write-up:** the methods chapter should *showcase* the already-present machinery (§1)
and present §3 as disciplined Future Work — this reads as methodological maturity, whereas bolting §3 onto
the frozen pipeline now would read as p-hacking. See `RELATED_WORK_WATCH.md` /
`docs/RESEARCH_SCAN_2026-06-27.md` for the supporting citations.

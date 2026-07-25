# Contamination (N3) + OOD tail-stress — method, claims, and wiring spec

**Modules:** `src/inference/contamination.py`, `src/inference/ood_stress.py`
**Tests:** `tests/test_contamination_ood.py` (synthetic; ruff/mypy/test-green)
**Specs:** `00_planning/CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md` §5.9 (contamination), §5.12 (OOD); `PREREGISTRATION.md` §8 (contamination protocol)
**Status:** built, standalone, **degrades gracefully without campaign data**; reported in **separate declared families**, never merged into the frozen `m = 6` (Part-2 "amendment-free additions"). Neither is the headline.

> **Deps confirmed pinned** (no new dependencies): `scipy` 1.17.1, `numpy` 1.26.4 (contamination); `arch` 7.2.0, `statsmodels` 0.14.6, `scipy.stats.genpareto` (OOD). All already in `pyproject.toml`.

---

## Part A — N3 contamination: the named-vs-blinded A/B

### A.1 What the threat actually is (reward designer ≠ forecaster)

The leakage risk for an LLM **reward designer** is **concept leakage** — priors that
CVaR/drawdown-penalised reward terms work on famous regimes, and implicit coefficient-tuning
toward crisis dates the model has read about. It is **not outcome recall**: the reward sees
only anonymised arrays (no tickers, no dates — `src/reward/contract.py:18-19`). The
reward-design priors are the **object of study** (this is H4 — LLM-vs-uninformed-search), not a
defended weakness. So the question is *not* "did the model memorise a label" but **"does
revealing the data's identity change the reward code it writes, holding the data itself fixed?"**

### A.2 The load-bearing test vs the theatre (state this explicitly in the write-up)

| | Method | Why |
|---|---|---|
| **LOAD-BEARING** | **Named-vs-blinded A/B** (`named_vs_blinded_tost`, primary) | Holds the data FIXED; only labels differ → isolates concept use; **escapes the MIA distribution-shift confound**. |
| **LOAD-BEARING** | **Post-cutoff persistence** of the H2 gap (`post_cutoff_persistence`) | The designer cannot have memorised post-cutoff regimes; if the H2 gap persists past the cutoff it is not memorised priors. |
| **LOAD-BEARING** | **Cutoff-dated 2nd model** (`cross_model_disagreement`) | Agreement across models with different cutoffs argues the design is data-driven. |
| **THEATRE / CATEGORY ERROR** (deliberately **NOT** implemented) | Min-K%-prob / loss / perplexity "on the reward function" | There is **no realised target token sequence** — the reward is *generated*, not *recalled*, so a per-token membership score has no estimand. |
| **THEATRE** (not implemented) | MIA on Opus closed-weight logprobs | Only top-k logprobs are exposed, no reference model; MIAs **barely beat chance** at frontier scale (Duan et al. 2024, arXiv:2402.07841). |

**Why the A/B escapes the confound that sinks MIA.** The single biggest reason post-hoc
contamination claims fail is a **distribution shift** between the "member" and "non-member" sets
that a bag-of-words classifier can exploit, which invalidates the memorisation claim (Meeus et
al. 2024, "SoK: MIAs on LLMs are Rushing Nowhere", arXiv:2406.17975; the recommended fix is
randomised / held-fixed splits). The named-vs-blinded A/B **is** that fix: both arms receive the
*identical* numerical arrays — only the surrounding labels differ — so a measured difference is
concept use, not a distribution artefact. Structural blinding itself is **necessary but
mixed-effectiveness hygiene** (Glasserman-Lin 2023: anonymisation removes *distraction*, not
look-ahead; Sarkar-Vafa: masking can be defeated by reconstruction); its **sufficiency is the
empirical question this A/B answers**, not an assumption.

### A.3 The primary statistic — paired TOST → "bounded contamination as a positive claim"

The dependent variable is the **reward-coefficient vector** `theta` extracted from each authored
reward (a probe-regression coefficient vector is the primary instrument; a static AST/structural
read corroborates), arranged as a `(n_seeds, n_coeffs)` matrix per arm (NAMED, BLINDED), **paired
by seed**. For each coefficient `k`:

1. compute the within-arm seed SD `sd_k` (pooled across the two arms);
2. set the equivalence bound `Delta_k = equivalence_sd_frac * sd_k` with
   `equivalence_sd_frac = 0.5` (§5.9: half the seed-to-seed noise; pre-registered, overridable),
   **or** pass a pre-registered absolute `equivalence_abs` vector;
3. run a **paired TOST** (two one-sided t-tests; Lakens 2017, Schuirmann 1987) on the named-minus-
   blinded differences against `[-Delta_k, +Delta_k]`. TOST p-value = **max** of the two one-sided
   p-values; equivalence (the 5% decision) ⇔ the **90% CI lies inside** `(-Delta_k, +Delta_k)`.

Rejecting *both* one-sided nulls licenses the **positive** claim *"the coefficient is invariant to
identity revelation within ±Delta_k"* — **bounded contamination stated as a result**, not the
absence-of-evidence non-result a bare two-sided `p > 0.05` would be.

> **⚠ POWER WARNING (a load-bearing limitation, not a bug).** With `Delta = 0.5 * SD` the bound is
> TIGHT. At the campaign's **30** main-experiment seeds the 90% CI half-width on the paired mean
> difference is comparable to `Delta`, so a genuinely null coefficient **typically does not clear
> the bound** — `all_equivalent = False` at n=30 is *underpowered*, NOT evidence of contamination.
> Measured power for the all-coefficient claim at `Delta = 0.5 * SD`: **P≈0.00 at n=30, ≈0.27 at
> n=60, ≈0.80 at n=100, ≈0.97 at n=150, ≈1.00 at n=200** (see
> `test_named_vs_blinded_tost_is_underpowered_at_30_seeds`). **Action:** the named-vs-blinded A/B is
> a CHEAP dedicated sub-experiment — each seed is one reward authoring + one cheap eval (it does
> **not** re-run the 50k-step main training) — so it must run **~150–200 seeds**, OR pre-register a
> wider `Delta`. Report the per-coefficient CIs and the achieved power; never read a low-power
> non-rejection as contamination.

### A.4 The complementary and downstream legs

| Function | Direction | What it adds |
|---|---|---|
| `coefficient_mahalanobis_permutation` | **difference** (omnibus) | Paired sign-flip permutation on the Mahalanobis distance between the named/blinded coefficient centroids (exchangeable label per seed). Small p = evidence of contamination; large p = absence of evidence (NOT equivalence). |
| `structural_mcnemar` | **difference** (structural) | McNemar on a binary motif vector `s` (does a CVaR / drawdown / turnover term appear?). Exact-binomial for small discordant counts. |
| `named_vs_blinded_oos_gap` | **equivalence**, downstream | NAMED−BLINDED **OOS-Sharpe** gap, gated to the pre-registered SESOI = 0.05; reuses `bootstrap.paired_seed_difference_test` (rliable IQM + paired seed bootstrap). |
| `post_cutoff_persistence` | **difference** | Pre- vs post-cutoff H2 gap (paired seed bootstrap). **Carries the underpowered-short-window caveat in its output** (`res["caveat"]`); report effect + CI, not the p-value. |
| `cross_model_disagreement` | triangulation | Per-coefficient standardised mean difference (Cohen's d) + L2 centroid distance between Opus 5 and a 2nd model. NOT a hypothesis test — a robustness triangulation. |

`contamination_report(...)` runs every available leg; any leg whose inputs are absent returns
`{"status": "no_data", "reason": ...}` (**never fabricates**), and the top-level
`load_bearing_note` re-states the load-bearing-vs-theatre distinction inline.

### A.5 Wiring spec (campaign)

1. **Two labelling arms, regime content held FIXED.** Build a NAMED variant of the existing
   feedback prompt that *exposes* real dates/ticker/regime labels, alongside the live BLINDED
   (anonymised-array) prompt. **Everything except the labels is byte-identical** — assert it with
   the existing `assert_arm_prompt_equality` SHA gate over the non-label portion. Run each across
   **the dedicated A/B seed budget (~150–200)**, *not* the campaign's 30. This is Door C-adjacent: a
   sealed side-experiment, never an H2 arm.
2. **Extract `theta` per (arm, seed).** Primary = a probe-regression of the authored reward's per-
   step output on a fixed feature basis (return, return², downside, turnover, drawdown, CVaR-proxy);
   corroborate with a static AST read of the bounded-coefficient grammar (`src/reward/grammar.py`,
   when built). Stack into `(n_seeds, n_coeffs)` NAMED / BLINDED matrices; build the binary motif
   matrix `s` likewise.
3. **Call** `named_vs_blinded_tost(named_theta, blinded_theta, coefficient_names=...)` (primary),
   then `coefficient_mahalanobis_permutation`, `structural_mcnemar`, and — after rolling each
   labelling's winner through the sealed test leg — `named_vs_blinded_oos_gap(named_seed_sharpe,
   blinded_seed_sharpe)`. The per-seed Sharpe maps are built exactly as
   `scripts/analyze_campaign.py::_seed_scores` already builds them from `metrics['test_returns']`.
4. **Post-cutoff persistence:** split each frozen-winner's sealed-test return series at the
   pre-registered Opus cutoff date; compute the per-seed distributional−scalar gap on each slice;
   call `post_cutoff_persistence(pre_gap, post_gap)`. Report the caveat.
5. **2nd model:** add one registry entry for a commit-pinned open-weights model (ideally a
   ChronoGPT/DatedGPT pre-cutoff model) via the provider-neutral transport; author rewards under it;
   call `cross_model_disagreement(opus_theta, model_b_theta)`.
6. **Reporting family:** a **separate declared family** keyed on `theta`/coefficient (disjoint from
   the frozen `arm_a/arm_b/metric/level` keys, so `assert_realized_family_matches_frozen` stays
   green). No BH correction is applied to the *equivalence* decisions (TOST controls its own
   per-test error); report `fraction_equivalent` + per-coefficient CIs.

---

## Part B — OOD tail-stress on frozen winners (robustness appendix)

### B.1 The protocol and the over-claim guard

Freeze the winners → roll each frozen policy (trained on the real train window) through **synthetic
test-length paths** → score with the same per-seed rliable tail metrics → **report only as a
robustness appendix, never the headline** (§5.12).

> **The decisive caveat (bounds every claim).** The generators are **calibrated to the SAME history
> the winners were selected on.** This makes the exercise a **falsification / stress-probe, NOT
> out-of-sample generalisation**: it can *break* a winner (show its tail edge was fragile to a
> plausible re-draw of the dynamics) but cannot *certify* generalisation to unseen futures. No
> generator reproduces all stylised facts at once → every path set must pass a **validation
> battery** before use. Report **Sharpe + drawdown beside every tail metric** so a "tail win" is not
> tautological. The Bauer (2025) low-power caveat applies to the CVaR-1% leg. `ood_stress.claims()`
> is the single source of truth for this statement.

### B.2 The Tier-1 stressors (no new deps)

| Function | Method | Cross-section | Notes |
|---|---|---|---|
| `garch_evt_fhs` | **GARCH-EVT filtered historical simulation** (McNeil & Frey 2000) | **preserved** (joint residual-row resample) | Per asset: AR(1)-GJR-GARCH(1,1)-t filter → standardised residuals → semi-parametric residual law (empirical body + **GPD/POT tails both sides**) → forward GARCH recursion. Resampling residual *rows jointly* keeps the cross-sectional copula so **portfolio** tails are real. Falls back per-asset to i.i.d. residuals at constant vol on a fit failure (logged WARNING). |
| `block_bootstrap_paths` | **stationary block bootstrap** of panel rows jointly (Politis-Romano 1994) | **preserved** (whole rows kept) | Block length from `arch.bootstrap.optimal_block_length` (Politis-White / PPW-2009) via `optimal_block_length`; `p = 1/block_length`. The most assumption-light stressor — re-orders history, cannot invent an unseen extreme, never breaks the copula. |
| `markov_crash_paths` | **Markov-switching crash regimes** via `statsmodels.MarkovAutoregression` (Hamilton 1989) | single-factor (β + idiosyncratic) | **FILTERED** state inference (info up to `t`), **never smoothed** (smoothed conditions on the future → leaks). Simulates a regime path from the estimated transition matrix; draws per-regime Gaussian shocks; spreads to assets via market β. Returns `{"status": "fit_failed", ...}` on a fit failure (graceful). |
| `vol_spike_paths` | parametric **mean-preserving** variance scaling (×1.5 / ×2) | exact correlation preserved | Inflates deviations-from-mean by `sqrt(multiplier)`; a cheap deterministic sensitivity sweep. |

**Scope-out** (documented in the module + `claims()`): ABIDES/JAX-LOB microstructure sims (wrong
granularity for daily rebalancing) and diffusion/GFlowNet generators (same fatal same-path
objection). **TAIL-GAN** (Cont et al. 2025) is a hard-caveated **Tier-2 stretch — intentionally not
implemented** (data-thin for daily 20y; its elicitability guarantee holds only for its benchmark
strategy class, which excludes the learned policy).

### B.3 Validation battery + scoring

* `validate_stylized_facts(synthetic, historical)` — directional sanity gates on the EW portfolio
  return: **fat tails** (excess kurtosis > 0.5), **volatility clustering** (ACF(1) of |returns| >
  0.02 — a *materially*-positive threshold so an i.i.d. generator fails it), **leverage** (corr(rₜ,
  |rₜ₊₁|) < 0). `passed` requires fat-tails ∧ vol-clustering. *Gates, not formal tests* — a failed
  gate flags an unrealistic generator to disclose. (Verified: the GARCH-EVT FHS output reproduces
  ACF≈0.26 vs historical≈0.31 and heavy tails; an i.i.d.-Gaussian generator fails the clustering
  gate.)
* `score_paths(paths, policy_returns=...)` — reduces a `(n_paths, H, n_assets)` path set to
  aggregate tail+performance metrics. **`policy_returns` is the seam** where a frozen winner's
  rolled-out policy is injected (a closure that runs the env+agent on each synthetic path). When
  `None`, an equal-weight portfolio is the placeholder so the module self-tests **without** the
  agent — this is NOT a substitute for the real policy.
* `tail_metrics(port_returns)` — per-path Sharpe, max-drawdown, and CVaR at each level, each
  aggregated across paths to an **IQM** + [5th, 95th] band. CVaR-1% carries the Bauer flag.

### B.4 Wiring spec (campaign)

1. **Calibrate** on the real historical return panel: `load_gold_panel(...)` → a `(T, n_assets)`
   NET return panel (the same panel the frozen winners trade). The harness needs *only* this numeric
   panel — no campaign artefacts — so it also runs on `src.data.synthetic.make_synthetic_panel` when
   real gold is gated.
2. **Generate** each Tier-1 path set (`n_paths` ≈ 100, `horizon` = the sealed-test length). **Run the
   validation battery and discard / disclose any set that fails.**
3. **Roll the frozen policy.** Provide `policy_returns` = a closure that, for each synthetic path,
   feeds the path as the env's return stream and runs the **frozen** SB3-SAC winner (deterministic
   action), returning the realised per-step portfolio return. This module deliberately **does NOT
   import the env or the agent** (kept dependency-light and Door-C clean); the closure lives in
   `scripts/run_ood_stress.py` (the net-new driver named in Part 3 of the findings, to be added —
   it is the only piece that touches `src/env` + `src/agents`).
4. **Score** per (winner, generator) with `score_paths`; **report Sharpe + drawdown beside every
   tail metric**; aggregate per-seed across the frozen winners' seeds (rliable IQM).
5. **Reporting family:** a **separate declared family** keyed on `generator` (disjoint from the
   frozen family keys → `assert_realized_family_matches_frozen` stays green). Headline = the
   **worst-(stress)-generator** tail outcome of the distributional arm, framed strictly as
   falsification, never as the H2 result.

---

## Part C — What these harnesses can and cannot claim (one-paragraph summary for the viva)

* **Contamination (load-bearing):** *"Holding the regime data fixed and revealing only its identity
  does not move the LLM's reward coefficients beyond ±0.5·(seed SD)"* — a **bounded** statement of
  concept-contamination as a positive claim (TOST), corroborated by post-cutoff persistence and a
  cutoff-dated second model. It does **not** and **cannot** claim "the model never saw these dates"
  (a membership claim with no estimand for a generated reward; MIA ≈ chance on closed weights).
* **OOD stress (robustness appendix):** *"The frozen distributional winner's tail edge survives a
  plausible re-draw of the calibrated dynamics (GARCH-EVT FHS / block bootstrap / Markov crash)."*
  It is a **falsification / stress-probe**, reported with Sharpe + drawdown; it does **not** and
  **cannot** claim out-of-sample generalisation (the generators are calibrated to the same history),
  and it never replaces the sealed test leg or enters the headline.

---

## References

McNeil & Frey (2000) *J. Empirical Finance* 7:271-300 (GARCH-EVT FHS) · Politis & Romano (1994)
(stationary bootstrap) · Politis & White (2004) / Patton-Politis-White (2009) (optimal block
length) · Hamilton (1989) (regime switching) · Glosten-Jagannathan-Runkle (1993) (GJR-GARCH) ·
Bauer (2025) (tail-power ceiling) · Lakens (2017) *Equivalence Tests* (TOST) · Schuirmann (1987)
*JPB&P* 15:657 · McNemar (1947) · Duan et al. (2024) COLM, arXiv:2402.07841 (MIAs ≈ chance) · Meeus
et al. (2024) "SoK" arXiv:2406.17975 (MIA distribution-shift confound) · Glasserman & Lin (2023)
arXiv:2309.17322 (anonymisation kills distraction not look-ahead) · Agarwal et al. (2021) rliable,
arXiv:2108.13264.

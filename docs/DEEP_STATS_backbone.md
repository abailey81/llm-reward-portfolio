# DEEP_STATS_backbone — adversarial audit of the statistical-inference backbone

**Scope.** Exhaustive, harsh-critic scrutiny of the inference stack that underlies every hypothesis
(H1–H4) and the benchmark gates: Deflated Sharpe Ratio (DSR), PBO/CSCV (full enumeration C(16,8) =
12,870), the per-seed rliable IQM paired bootstrap (n=30), the m=6 Benjamini–Hochberg family + the
joint Romano–Wolf stepdown, and TOST equivalence. PDF-only grade, supervisor Dr Okhrati (this is his
exact expertise). Goal: make the inference integrity bulletproof, or at minimum *honestly bounded and
pre-registered*, before the freeze.

**Method.** Code read first-hand (`scripts/analyze_campaign.py`, `src/inference/{bootstrap,
deflated_sharpe, overfitting, multiple_testing, attribution, es_backtest}.py`, `scripts/power_analysis.py`,
`src/selection/fitness.py`); pre-registration (`PREREGISTRATION.md` §10, `config/preregistration.yaml`,
`config/inference.yaml`) cross-checked; literature grounded against the primary sources (Bailey–López de
Prado DSR 2014; Bailey–Borwein–López de Prado–Zhu PBO/CSCV 2015/2017; Harvey–Liu 2015 *Evaluating Trading
Strategies*; Harvey–Liu–Zhu 2016; Harvey–Liu 2020 *False (and Missed) Discoveries*; Romano–Wolf 2005;
Benjamini–Hochberg 1995; Benjamini–Yekutieli 2001; Agarwal et al. *rliable* 2021; Politis–Romano 1994;
Lakens 2017 TOST; Gelman–Loken garden-of-forking-paths).

**Headline verdict.** The backbone is **unusually strong for an MSc** — the hard, commonly-botched parts
are correct: PBO is the right *primary* guard precisely because the DSR trial count is ill-defined under
guided search; the per-seed rliable bootstrap (R16) fixed a genuine ~21%→~5% anti-conservativeness bug
that most students never catch; the family is enumerated, frozen, hashed, and guarded by a fail-loud
assert; secondary analyses are in disjoint, internally-corrected families. **But there are five real
integrity threats**, two of them HIGH, that a López-de-Prado-literate examiner *will* probe. None require
re-running the campaign; all are fixable by tightening the pre-registration prose and/or a small,
report-only code addition. They are prioritised in §C.

---

## Epistemic basis of the null

The null is credited on **error-statistical severity**, not Popperian corroboration: the **frozen,
deviation-free** cryptographic protocol admits no sample-based deviations, so there is no unknown Type-I
inflation (Rubin 2025 — pre-registration alone does not improve Popperian severity, but a deviation-free
protocol supports Mayoian severity; Mayo 2018). The whole analysis plan is fixed in advance, foreclosing the
**garden of forking paths** (Gelman & Loken 2014). The null is therefore reported as a **TOST equivalence
against the pre-registered SESOI** (Lakens 2018; Campbell & Gustafson 2018 CET), never as a bare *p* > 0.05.
*(Citations Rubin 2025 / Mayo 2018 / Gelman & Loken 2014 / Lakens 2018 / Campbell & Gustafson 2018 to be
VERIFIED against `paper/refs.bib` before entering the PDF.)*

---

## A. Threat register (each: claim, evidence, severity, fix-pointer)

Severity scale: **CRITICAL** (could invalidate a headline claim) · **HIGH** (a sharp examiner attack with
no current written defence) · **MEDIUM** (a defensible choice that must be *stated*, not silently made) ·
**LOW** (polish / reporting hygiene).

### A1 — DSR trial count under *sequential* guided search is not just "ill-defined", it is *correlated-down* (HIGH)

**Claim.** The DSR deflation uses `n_trials = candidates_per_arm = 30` (`config/campaign.yaml:4`,
threaded `run_campaign.py:1150-1153` → `winner_dsr` uses `len(arm_records)`). But those 30 candidates are
**6 generations × 5 candidates** of *Eureka-style reflective* search (`config/campaign.yaml:33`,
`search.headline_reflect_protocol = parallel_reflect_on_best`). Each generation conditions on the prior
generation's best. **The trials are therefore positively correlated and sequential, not the i.i.d. draws
the expected-max-Sharpe formula assumes.**

**Evidence (literature).** The DSR's E[max SR] = √Var[{SRₙ}]·((1−γ)Φ⁻¹(1−1/N) + γΦ⁻¹(1−1/(Ne))) is derived
**under N independent trials** (Bailey–López de Prado 2014). The paper *itself* cautions that "sequential
testing or overlapping backtests violate independence assumptions" and that N should count
*non-overlapping, independent* tests. López de Prado (2018, AFML) prescribes an **effective N** via
clustering correlated trials (the ONC algorithm) used as a **conservative upper bound**. The code's own
docstring (`deflated_sharpe.py:12-20`) states exactly this and is why PBO is primary — good. **The subtlety
the examiner will press:** guided reflection makes the 30 trials *more* correlated than a random grid, so
the *naïve* N=30 actually **over-deflates** (too conservative) on the multiplicity axis — but the
*effective* N could be as low as ~6 (the number of generations) or even ~1 (if reflection collapses onto
one basin), which would make the deflation *too weak*. The direction of the bias is **not signed without
measuring the inter-candidate Sharpe correlation**. Right now the dissertation has no number for it.

**Why it matters here specifically.** DSR feeds three places: (i) the **selection fitness**
(`fitness.held_out_fitness` → `deflated_sharpe_ratio`, but with `var_sr=None` proxy, see A2); (ii) the
**secondary headline winner-DSR table** (`winner_dsr`, canonical var); (iii) the **benchmark-floor gate**
and **H1 beat-human gate** (winner DSR deflated by N=30 vs benchmarks at N=1). A wrong N moves the floor
gate pass/fail and the H1 normalised-improvement bar.

**Severity HIGH** — not CRITICAL because DSR is *declared secondary* and PBO carries the headline
overfitting claim; but the floor/H1 gates *do* consume DSR and *are* reported, so an attacked N has teeth.

**Fix → C1.**

### A2 — The canonical-vs-proxy DSR variance is correct, but the *selection-time* DSR still uses the wrong variance (MEDIUM, already self-disclosed)

**Claim.** `deflated_sharpe_ratio(var_sr=None)` substitutes the **within-series sampling variance**
Var[ŜR] = (1 − γ₃·SR + (γ₄−1)/4·SR²)/(n−1) for the **cross-trial Sharpe dispersion** Var[{SRₙ}] that the
canonical DSR requires. These are *different quantities* (sampling SE of one estimator vs dispersion of
Sharpes across candidates) and coincide only under the homogeneous zero-skill null. The **wired selection
path** (`fitness.py:90`) passes `var_sr=None` — so candidate *selection* used the proxy — while
`winner_dsr` recomputes the headline number with the empirical cross-candidate `Var(sharpes, ddof=1)`
(`analyze_campaign.py:389-390`). The code and docstrings are exemplary about this (`deflated_sharpe.py:172-185`).

**Evidence (literature).** Confirmed against the DSR paper: Var[{SRₙ}] is "variance across independent
trial outcomes, not the standard error of a single estimator." So the canonical recompute is *right* and
the proxy is *acknowledged wrong-but-bounded*.

**The residual threat.** Selection *did* run on the proxy. Because selection is argmax over candidates and
the proxy multiplies a *common* monotone transform, the **ranking** of candidates by validation fitness is
**unchanged** by which var_sr is used *only if* var_sr is constant across candidates within an arm — which
it is (it's one arm-level dispersion). So the winner identity is robust. **But** the *value* of the
selection DSR (used if λ>0 ever combined DSR with a CVaR penalty) would differ. Since λ is frozen to **0.0**
(R22), selection is pure DSR-rank and this is moot for the winner. **State this explicitly**: "winner
identity is invariant to the var_sr proxy because (a) it is a within-arm constant and (b) λ=0, so selection
is a pure monotone ranking of per-candidate validation DSR."

**Severity MEDIUM** — fully self-disclosed in code; needs one sentence in the write-up to close it as an
examiner question. **Fix → C2.**

### A3 — PBO/CSCV is the right tool, but the candidate-matrix it runs on may violate a CSCV precondition (HIGH)

**Claim.** PBO is computed **per arm** over the arm's candidate **validation** return matrix
(`build_perf_matrix` → `campaign_pbo` → `overfitting.pbo`), full enumeration C(16,8)=12,870
(`analyze_campaign.py:288-289`). The implementation is **correct** (verified line-by-line: contiguous
equal blocks, IS=best-mean, OOS average-rank → logit, strict λ<0, ties handled). This is the textbook
Bailey–Borwein–López de Prado–Zhu CSCV.

**The threat is *applicability*, not implementation.** CSCV's PBO measures **IS-vs-OOS rank consistency
across a matrix whose N columns are the candidate strategies' per-period performance**. Three structural
mismatches with this campaign:

1. **N is small and heterogeneous-in-availability.** PBO needs ≥2 candidates with usable validation
   vectors; with 30 candidates that is fine, **but** vectorless candidates are *dropped from the matrix*
   while *counted* in the DSR multiplicity (`_is_search_candidate`, `winner_dsr.n_trials = len(arm_records)`).
   So PBO's effective N (columns with vectors) and DSR's N (all candidates) **differ by design** — correct
   and documented, but must be reported side-by-side so a reader isn't confused why "n_candidates" differs
   between the PBO table and the DSR table.
2. **CSCV assumes the columns are *comparable* candidate strategies ranked on the *same* metric.** Here the
   ranking statistic inside PBO is the **mean validation return** (`is_perf = is_data.mean(axis=0)`),
   **not** the validation *DSR* that actually selected the winner. So PBO answers "does picking the
   highest-mean-return candidate IS generalise OOS?" while selection picked the **highest-DSR** candidate.
   These are *different selection rules*. PBO is therefore a **proxy** for the overfitting of the *realised*
   selection rule, not a direct measure of it. Defensible (mean-return rank and DSR rank are highly
   correlated on the same window), but an examiner can say "your overfitting guard doesn't guard the rule
   you actually used." **This needs a sentence** and ideally a robustness PBO ranked on per-block DSR.
3. **The validation window is short (~750 sessions) and S=16 blocks → ~47 rows/block.** CSCV's logit is
   noisy when blocks are short; the EVT-flagged tail metrics are *not* what PBO ranks on (it ranks on mean
   return), so this is less acute, but the block count should be justified (why 16, not 10 or 8) against
   the López de Prado guidance that S be even and large enough that C(S,S/2) is "large" — 12,870 is ample.

**Evidence (literature).** Bailey et al. (PBO/CSCV) explicitly position PBO as **model-free, nonparametric,
rank-based** and trial-count-free — which is *exactly* why it is the correct primary guard here (the DSR's N
is ill-defined, A1). The applicability caveats (1)–(3) are not flaws in CSCV; they are *mapping* choices
this design made that must be **stated**.

**Severity HIGH** — because point (2) is a clean "you didn't guard the rule you used" attack with no
current written rebuttal. **Fix → C3.**

### A4 — Cross-hypothesis multiplicity: H1/H2/H3/H4 are four hypotheses with their own tests and there is **no global correction** across them (CRITICAL for honesty, defensible by design)

**Claim.** The frozen m=6 family (R13) covers **only the H2 conjunction's legs** (distributional vs
{scalar, placebo, scalar_cvar5} × {Sharpe, CVaR-0.05}). H1 (beat-human), H3 (iterative vs single-shot),
H4a/H4b (vs random-search / Bayes-opt), and the secondary SAC-vs-TQC critic experiment are **separate
tests in separate (or undeclared) families**. There is **no family-wise or FDR correction *across* the four
hypotheses.** This is the single biggest "garden of forking paths" exposure.

**Evidence (code).** `assert_realized_family_matches_frozen` enforces the m=6 set and *rejects* any drift —
good, it prevents silent family growth. H1 (`beat_human_baseline`) writes **disjoint keys**
(`h1_beat_human`, no arm_a/arm_b/metric/level) so the assert never sees it; attribution writes its **own**
BH family (`campaign_attribution`, `rung/factor/alpha_diff`); the cost sweep, rf-robustness, variance
decomposition, contamination are all disjoint, report-only. So **within** each declared family multiplicity
*is* controlled. **Across** the four headline hypotheses it is **not**.

**Evidence (literature).** This is a *real and contested* question. Harvey–Liu (2015, *Evaluating Trading
Strategies*) and Harvey–Liu–Zhu (2016, *…and the Cross-Section of Expected Returns*) argue that **when many
strategies/combinations have been tried, the entire research programme's testing count must inflate the
hurdle** — the "many rewards tried" analogue the companion explicitly invokes. Gelman–Loken's garden of
forking paths makes the same point for *any* multi-outcome study. **However**: the *standard and defensible*
counter-position is that **H1–H4 are distinct, pre-registered scientific questions with distinct
estimands**, not a fishing family scanned for *one* winner; FDR/FWER control is for a *family from which a
discovery is selected*, and **pre-registration with separate declared families is the accepted alternative
to a global correction** (it removes the selection-from-family that multiplicity corrects). The dissertation
is *already* on the right side of this (pre-registered, disjoint, frozen) — but the **decision to treat the
four hypotheses as separate families rather than one corrected family is itself a researcher degree of
freedom that is currently *implicit*.**

**Severity CRITICAL-for-honesty** — not because the design is wrong (it's defensible and arguably correct),
but because **the choice is unstated**. An examiner who asks "why no Bonferroni across H1–H4?" must meet a
*pre-written, cited* answer, or the whole pre-registration's credibility wobbles. **Fix → C4 (highest
priority: this is a prose/pre-reg fix, not code).**

### A5 — One-sided hypotheses tested with two-sided p-values, then a *post-hoc* directional gate that is **not itself in the corrected family** (HIGH)

**Claim.** Every H2 leg is **directional** ("distributional *better* than b"). The implementation runs a
**two-sided** re-centred bootstrap p-value (`paired_seed_difference_test`: `P(|boot−obs| ≥ |obs|)`,
`bootstrap.py:162`), BH-corrects the two-sided p-values, **then** layers a separate `direction_ok =
effect > 0` flag and requires `reject_bh AND direction_ok` (`h2_conjunction`, `analyze_campaign.py:1044-1051`).

**Why this is subtle (and partly *good*).** Using a two-sided p-value for a one-sided hypothesis is
**conservative on the p-value** (the tail probability is doubled vs a correct one-sided test), so the BH
rejection is *harder* to obtain — this *protects* against false H2 support. **But** the directional gate is
applied **outside** the BH correction. The logically clean object is a **one-sided** test (p_one =
P(boot−obs ≥ |obs|) when effect>0) fed to BH. The current construction is *almost* equivalent to "one-sided
at α/2 then BH", which is **valid but loses power** and, more importantly, **mixes a corrected quantity
(BH on two-sided p) with an uncorrected quantity (sign of effect).** Under the global null the sign is a
coin flip, so the *joint* event {BH-reject AND correct sign} has familywise behaviour that is **not** the
nominal BH guarantee on the one-sided family — it is *more conservative* (good for Type-I) but the
write-up currently calls it "BH at q=0.05" without noting the two-sided→directional construction.

**Evidence (literature).** Standard multiple-testing practice (Benjamini–Hochberg 1995; and the one-sided
treatment in Romano–Wolf) is to **correct the p-values that match the hypotheses' sidedness.** The
Romano–Wolf path here (`romano_wolf_joint`) **is** correctly one-sided (it builds `obs = stat_a − stat_b`,
recentres, and `romano_wolf` rejects on the *upper* tail) — so the two correction routes are **not
testing the identical statistic** (BH: two-sided + sign gate; RW: one-sided). That asymmetry should be
acknowledged, and ideally the BH leg should consume **one-sided** p-values to match the RW leg and the
hypotheses.

**Severity HIGH** — it is a correctness-of-construction question a statistician examiner *will* see, and the
two routes (BH vs RW) currently test subtly different nulls. The bias is *conservative*, so it cannot
*manufacture* H2 support — which is the saving grace — but it must be documented and, preferably, unified.
**Fix → C5.**

### A6 — The CVaR-difference test is bespoke (no published named test) — size certified only empirically (MEDIUM, well-handled)

**Claim.** `cvar_difference_test` is a re-centred stationary-block bootstrap on the ES functional; the
module is explicit that **no published, named two-sample difference-in-CVaR test exists** and that its size
is certified by `null_calibration` (audit C-7), **not** by a citation. The per-seed family CVaR leg uses
`paired_seed_difference_test` with `statistic=iqm` over per-seed CVaR scores — i.e. the **across-seed**
bootstrap, which is the right unit.

**Evidence (literature).** Correct that ES alone is **not elicitable** (so no strictly consistent loss);
the **pair (VaR, ES) is jointly elicitable** (Fissler–Ziegel 2016), which is why the *comparative forecast*
backtest (`es_backtest.comparative_es_backtest`, Nolde–Ziegel 2017, FZ0 loss) is the principled route for
*forecast* comparison — and the code correctly **separates** that from the *realised two-sample* CVaR
comparison. The Bauer (2025) low-power-at-extreme-α caveat is cited and the CVaR-1% leg is flagged
high-variance and kept **out of the frozen m=6** (opt-in to m=9). This is handled about as well as the
literature allows.

**Residual threat.** A bespoke test's *empirical* size certification (`null_calibration`, 200 reps at the
5% level) is weaker evidence than an asymptotic result. The certification should be **reported with its
Monte-Carlo numbers in the appendix** (rejection rate ≈ 0.05 under the matched-null sampler), and the
*power* of the CVaR leg at the realised n=30 / window length should be stated (it is likely the
lowest-power leg, so a CVaR-leg null is "underpowered", not "no tail effect").

**Severity MEDIUM** — defensible, but the empirical certification must be *shown*, not asserted. **Fix → C6.**

### A7 — rliable IQM at n=30 with a 25% trim, and the percentile-bootstrap CI vs the re-centred-bootstrap p-value (MEDIUM)

**Claim.** The headline unit is the per-seed IQM (`iqm`, `bootstrap.py:82-100`): at n=30 it trims
⌊30/4⌋=7 from each tail and means the middle 16. The paired test resamples the 30 seed indices i.i.d.,
recomputes IQMₐ−IQM_b, and reports a **two-sided re-centred empirical p-value** plus a **percentile CI**.

**Evidence (literature).** This is faithful to Agarwal et al. (2021): IQM = 25%-trimmed mean, stratified
**percentile** bootstrap with B=2000 resampling seeds with replacement, "even with a handful of runs."
n=30 is well above rliable's "handful" regime, so the IQM/bootstrap is on solid ground here — *better* than
the median or mean. The R16 fix (per-seed scores, not a seed-*averaged* series) is the genuinely important
correctness move and is correct: averaging N i.i.d. seed paths shrinks the tested object's variance ~N×
and made the *prior* construction anti-conservative (~21% true-null rejection vs ~5%); the calibration
evidence is in `tests/test_audit_regressions.py`. **Good.**

**Residual threats (two small ones):**
- **CI/p-value engine mismatch.** The **p-value** comes from a *re-centred basic* bootstrap (`|boot−obs| ≥
  |obs|`), while the reported **CI** is a *percentile* interval (`quantile(boot, [.025,.975])`). These are
  two different bootstrap principles (basic vs percentile). They will *usually* agree on the
  reject/not-reject decision, but for a skewed bootstrap distribution they can disagree at the boundary.
  rliable itself uses the **percentile** CI; the p-value should ideally be derived from the **same**
  percentile/inversion principle (or the CI reported as the *decision object*, with the p-value as
  secondary), so a reader can't find a case where "CI excludes 0 but p>0.05" or vice-versa. State that the
  **decision is the BH-corrected p-value** and the CI is descriptive, OR switch the p-value to a
  bootstrap-t / percentile-consistent form.
- **IQM at n=30 discards 14 of 30 seeds.** That is the *point* (robustness to lucky/unlucky seeds), but it
  **reduces effective sample size**, so the IQM test has *less* power than a mean test — relevant to the
  power story (the MDE in `power_analysis.py` *does* use the real IQM test, so the power numbers already
  pay this cost — good). Worth one sentence: "IQM trims to the central 16 seeds by design (Agarwal 2021);
  the power analysis is computed on the *same* trimmed statistic, so the reported MDE already reflects it."

**Severity MEDIUM.** **Fix → C7.**

### A8 — The benchmark-floor / H1 gates compare a **deflated** winner DSR (N=30) against **undeflated** benchmark DSRs (N=1) — the asymmetry is intended but the *N* is the disputed one from A1 (MEDIUM)

**Claim.** `benchmark_floor` gates median-per-seed winner DSR (deflated by `winner_n_trials`=30) **>** best
benchmark DSR (deflated by N=1). H1 does the same vs hand rewards. The asymmetry is **deliberately
conservative** (a higher bar for the LLM) and well-argued (`analyze_campaign.py:1359`, `beat_human_baseline`
docstring). The median-per-seed (not seed-*averaged*) DSR correctly avoids re-introducing the seed-averaging
anti-conservativeness (`analyze_campaign.py:1362-1372`).

**Threat.** The winner's N=30 is the *same disputed naïve trial count* from A1. If the effective N is
smaller (correlated reflection), the winner DSR is *under-stated* and the floor/H1 gates are **even more
conservative** than reported — which is *safe* for the claim direction (it can only make passing *harder*),
so this is a **benign** instance of A1. Worth noting precisely because it *bounds the direction*: "any
error in N makes the floor/H1 gates more conservative, never less, so a *pass* is robust to the trial-count
dispute." That is a *strong* defensive sentence — use it.

**Severity MEDIUM** (benign-direction). **Fix → C1 (shared) + state the direction.**

### A9 — Annualised-Sharpe i.i.d. scaling (Lo 2002) in the *reported* point estimate (LOW, self-disclosed)

`sharpe_ratio` uses √252 i.i.d. scaling; the docstring (`bootstrap.py:239-245`) correctly notes Lo (2002)
shows this biases the *annualised point estimate* under autocorrelation and that the **headline test never
relies on it** (the per-seed paired bootstrap operates on the raw per-period series → per-seed score; the
annualised number is descriptive). Correct and disclosed. **Severity LOW** — keep the disclosure; optionally
report a Lo-corrected annualised Sharpe in a footnote. **Fix → C8 (optional).**

### A10 — Pairing across the shared seed is a *valid* paired design only if the seed indexes the *same* training-RNG stream across arms (LOW–MEDIUM, verify)

`paired_seed_difference_test` pairs arm A's seed-s score with arm B's seed-s score and resamples seed
*indices* jointly (so the common "lucky-seed" variance cancels). This is valid **iff** seed s drives the
*same* stochastic elements (env reset, network init, action noise) in both arms so that the pairing
genuinely shares variance. Per `project-runready-gotchas` the arms differ **only** in the feedback block
(agent fixed SB3 SAC, same seed → same init/replay), so the pairing is legitimate. **But** the *winners*
are different reward *code*, so seed s induces a *different trajectory* per arm — the pairing shares the
*seed* but not the *reward*. This is the **same caveat the H1 `beat_fraction_paired` already flags as
"secondary, not a common-noise paired draw."** The H2 paired test relies on the weaker (still valid)
assumption that the seed-level common component (init/noise stream) is shared; the *reward-induced* part is
the signal. **State that the pairing cancels the shared training-RNG component and that this is the
intended, weaker-than-identical pairing** — don't let an examiner conflate it with a matched-pairs-on-
identical-units design. **Severity LOW–MEDIUM.** **Fix → C9.**

---

## B. What is *correct* and should be defended confidently (the strong narrative inputs)

1. **PBO is the right *primary* guard.** Rank-based, trial-count-free, model-free (Bailey et al.). It
   sidesteps exactly the DSR-N problem (A1). Full enumeration (12,870 splits) → **deterministic, not
   seed-dependent** — a real rigor win over a sampled CSCV. Implementation verified correct (strict λ<0,
   average-rank ties, equal contiguous blocks).
2. **The R16 per-seed rliable fix is a genuine, citable correctness victory.** Catching that a
   seed-averaged series shrinks variance ~N× and is anti-conservative (~21%→~5%) is exactly the kind of
   subtle multiple-comparisons-in-RL error rliable (Agarwal 2021) was written to prevent. This is a
   *highlight*, not a liability.
3. **The family is enumerated, frozen, hashed (`freeze.py`), and a fail-loud assert blocks drift.** This is
   textbook pre-registration discipline and pre-empts the "you grew the family after seeing results" attack.
4. **Secondary analyses are in disjoint, internally-BH-corrected families** (attribution, cost sweep,
   rf-robustness, variance, contamination, H1). Each is "one declared family, corrected within." This is
   the *correct* structure for keeping the headline m=6 clean.
5. **DSR is correctly demoted to secondary, with the canonical cross-trial variance recomputed at analysis
   time** and the proxy's bias explicitly documented. The var_sr handling is more careful than most
   published quant work.
6. **Forecast-CVaR vs realised-CVaR are correctly separated** (FZ0/Nolde–Ziegel comparative backtest vs the
   bespoke two-sample test), grounded in Fissler–Ziegel joint elicitability. This is PhD-level care.
7. **TOST/SESOI pre-committed** so a null is a *bounded effect*, not a shrug (Lakens 2017) — the right move
   for a PDF-only grade where a null must still read as a finding.
8. **The headline claim is *comparative* ("distributional vs scalar at matched compute"), not "beats the
   market".** This is the correct, defensible scope and dodges the absolute-alpha multiple-testing morass
   (Harvey–Liu–Zhu t>3 is correctly scoped to absolute-alpha claims only, R13).

---

## C. Prioritised pre-freeze hardening (concrete, mostly prose + small report-only code)

Ordered by examiner-attack severity × ease. **None require re-running the campaign.**

### C1 (HIGH, ~½ day) — Report an *effective* DSR trial count and bound the direction of the N error
- **Code (report-only):** after the candidate archive exists, compute the **inter-candidate validation
  Sharpe correlation** per arm and an **effective N** — either López de Prado's ONC cluster count or the
  simple `N_eff = N / (1 + (N−1)·ρ̄)` from the mean pairwise correlation of per-candidate validation return
  vectors. Report **DSR at both N=30 and N=N_eff** in `winner_dsr_markdown` as a sensitivity band. This is
  ~30 lines reusing `build_perf_matrix`'s columns.
- **Prose (pre-reg note):** state that (i) the naïve N=30 is a *conservative upper bound on multiplicity*
  for the *random*-search arms and an *over*-count for the *guided* arms; (ii) PBO (trial-count-free) is the
  primary guard precisely for this reason; (iii) for the floor/H1 gates, **any N error is benign-direction**
  (smaller N_eff → smaller deflation → the winner DSR can only *rise*, making a *pass* robust; A8). Cite
  Bailey–López de Prado 2014 (independence caveat) + López de Prado 2018 (ONC effective-N).

### C2 (MEDIUM, 1 sentence) — Close the selection-time var_sr proxy
Add to the methods: "Candidate selection ranks per-candidate validation DSR with the within-series variance
proxy; because that proxy is a within-arm constant and λ=0, the argmax (winner identity) is invariant to it.
The headline winner DSR is recomputed with the canonical cross-candidate Sharpe dispersion (Bailey–López de
Prado 2014)." No code change.

### C3 (HIGH, ~½ day) — State PBO's selection-rule proxy + add a DSR-ranked robustness PBO
- **Prose:** PBO ranks candidates on **mean validation return** while selection used **validation DSR**;
  state that the two rankings are highly correlated on the same window and that PBO is therefore a (tight)
  proxy for the overfitting of the realised rule.
- **Code (optional, report-only):** add a second PBO column where the IS/OOS ranking statistic is the
  per-block **DSR** (or annualised Sharpe) instead of mean return, as a robustness PBO. If the two PBO
  columns agree, the proxy concern is empirically closed. Also surface why **S=16** (even; C(16,8)=12,870 ≫
  "large enough" per Bailey et al.) and report the **PBO N (vectorful candidates) alongside the DSR N (all
  candidates)** so the two tables' "n_candidates" are reconciled.

### C4 (CRITICAL-for-honesty, ~½ day, PROSE/PRE-REG) — Pre-register the cross-hypothesis multiplicity stance
This is the **single highest-value fix.** Add a frozen pre-registration paragraph (PREREGISTRATION §10):

> *Cross-hypothesis multiplicity.* H1–H4 are **distinct, pre-registered scientific questions with distinct
> estimands**, each tested within its **own declared family** (the H2 conjunction = the frozen m=6;
> attribution, cost-sweep, rf-robustness, contamination, variance, and H1 each their own internally-BH-
> corrected family). We deliberately **do not** impose a global FWER/FDR correction *across* the four
> hypotheses, because (a) multiplicity control corrects *selection of a discovery from a family scanned for
> the best*, whereas these are pre-specified separate questions not selected-from; (b) pre-registration of
> disjoint families is the accepted alternative to a programme-wide correction (Gelman–Loken; the logic of
> Harvey–Liu 2015/2016 is that *the count of strategies tried* inflates the hurdle — we hold that count
> fixed and matched across arms, and state it explicitly); (c) the headline claim rests on **H2 alone**,
> which is *internally* fully corrected. We **report all four** hypotheses' results regardless of outcome
> (no selective reporting), and flag that a reader preferring a programme-wide Bonferroni would multiply the
> per-hypothesis hurdle by ~4.

Then **also report**, as a one-line sensitivity, what H2's headline p-values would be under a Bonferroni-
across-4 (×4) hurdle — so the examiner sees you *considered* the global correction and it does/doesn't
survive. Cite Harvey–Liu (2015), Harvey–Liu–Zhu (2016), Harvey–Liu (2020), Gelman–Loken, Benjamini–
Yekutieli (2001, for FDR under dependence if you mention FDR-across-families).

### C5 (HIGH, ~¼ day) — Unify the BH leg to **one-sided** p-values (match RW + the hypotheses)
- **Code:** give `paired_seed_difference_test` (and the family collector) a **one-sided** p-value option
  `P(boot − obs ≥ |obs|)` aligned with the hypothesis direction, and feed **those** to BH — so the BH leg
  and the RW leg test the *same* one-sided null and the directional gate is *inside* the corrected object,
  not bolted on. Keep the two-sided p-value as a reported sensitivity (it is strictly more conservative).
  This is a small, contained change (one branch in the p-value computation; the conjunction's
  `reject AND direction_ok` becomes simply `reject` on the one-sided p).
- **If you choose not to change code:** at minimum, **document** that the BH leg uses a two-sided p-value
  with a post-hoc sign gate (conservative; cannot manufacture support) while the RW leg is one-sided, and
  that the headline decision is the *more conservative* of the two.

### C6 (MEDIUM, ~¼ day) — Show the CVaR-test size-calibration numbers + state its power
Put the `null_calibration` output (rejection rate under the matched null ≈ 0.05, with the sampler described)
into an appendix table for **both** `sharpe_difference_test`/`paired_seed_difference_test` and the bespoke
CVaR test. State the **CVaR leg's power** at n=30 and the test window (cite Bauer 2025): the CVaR-0.05 leg
is the lowest-power member of m=6, so a CVaR-leg non-rejection is "underpowered for the tail effect", not
"no tail effect" — and the H2 *conjunction gate is the Sharpe leg* anyway (R13), so a weak CVaR leg does not
sink H2.

### C7 (MEDIUM, ~¼ day) — Resolve the CI-vs-p-value bootstrap-principle mismatch
State explicitly that **the decision object is the BH-corrected re-centred-bootstrap p-value** and the
reported percentile CI (rliable-style, Agarwal 2021) is **descriptive**; OR switch the reported p-value to a
percentile/inversion form consistent with the CI. Add one sentence that IQM trims to the central 16 of 30
seeds by design and that the power analysis uses the *same* trimmed statistic (so the MDE already reflects
the trim).

### C8 (LOW, optional) — Lo-2002 annualised-Sharpe footnote
Optionally report a Lo (2002)-autocorrelation-corrected annualised Sharpe in a footnote; the headline test
is unaffected (it never uses the √252 scalar).

### C9 (LOW, 1 sentence) — Document the pairing assumption
State that the paired seed bootstrap cancels the **shared training-RNG component** (init/replay/noise stream
under the fixed SB3 SAC + shared seed), which is the intended, weaker-than-identical-units pairing; the
reward-induced trajectory difference is the signal. This is the same honesty already applied to H1's
`beat_fraction_paired`.

---

## D. The strongest defensible inference-integrity narrative (for the PDF)

Structure the methods/results defence around this spine — it converts every threat above into a
pre-empted, cited strength:

> **"We treat backtest overfitting and multiple testing as first-class threats and control them with a
> layered, pre-registered stack, choosing rank-based, trial-count-free guards wherever the trial count is
> ill-defined under guided search."**

1. **Primary overfitting guard is PBO/CSCV** (Bailey–Borwein–López de Prado–Zhu): model-free, rank-based,
   **trial-count-free**, **fully enumerated** (12,870 splits → deterministic). We use it *because* the DSR's
   expected-max-Sharpe deflation assumes **independent** trials (Bailey–López de Prado 2014), which
   Eureka-style *sequential reflective* search violates — so a trial-count-free guard is the principled
   headline. *(Closes A1, A3.)*
2. **The Deflated Sharpe is reported but secondary**, with the **canonical cross-trial Sharpe dispersion**
   recomputed at analysis time and the within-series proxy's bias documented; we report DSR at both the
   naïve N=30 and an **effective N** (López de Prado 2018 ONC / correlation-deflated), and note that for the
   floor/H1 gates **any N error is benign-direction** (it can only make a *pass* harder). *(C1, C2, A8.)*
3. **The headline H2 family is enumerated, frozen, hashed, and assert-guarded** (m=6 = the conjunction's
   distributional-vs-{scalar, placebo, scalar_cvar5} × {Sharpe, CVaR-0.05} legs), corrected by
   **Benjamini–Hochberg q=0.05** with the **joint Romano–Wolf stepdown** (one shared seed-resample per
   replication → preserves cross-hypothesis dependence, Romano–Wolf 2005) as the FWER alternative. We chose
   **FDR-primary** because the family is small and the legs are positively dependent (BH is valid and more
   powerful than FWER here); RW is reported as the stricter cross-check. *(B3, A5.)*
4. **The inference UNIT is per-seed rliable IQM with a paired across-seed bootstrap** (Agarwal 2021), at
   **n=30** winner seeds — *not* a seed-averaged series, which we show is anti-conservative by ~√N (a
   measured ~21%→~5% true-null rejection correction). This is the relevant uncertainty (training-RNG
   variance) in a multi-seed RL evaluation. *(B2, A7.)*
5. **Cross-hypothesis multiplicity is pre-registered as separate declared families**, with the rationale
   (distinct estimands; pre-registration replaces selection-from-family; matched, fixed trial count) stated
   and a **Bonferroni-across-4 sensitivity** reported so the reader sees the stricter hurdle. *(C4 — the
   linchpin.)*
6. **A null is a bounded effect, not a shrug:** SESOI=0.05 + symmetric **TOST** (Lakens 2017), plus a
   pre-committed MDE/power analysis run on the *actual* paired IQM test (not a re-implementation). *(B7.)*
7. **Tail inference is honest about power and elicitability:** realised-CVaR two-sample comparison
   (bespoke, *empirically* size-certified, calibration numbers shown) is kept distinct from the
   *forecast*-CVaR comparative backtest (FZ0 / Fissler–Ziegel joint elicitability / Nolde–Ziegel 2017); the
   CVaR-1% leg is flagged high-variance and excluded from the frozen family; Bauer (2025) low-power caveat
   stated. *(B6, A6, C6.)*
8. **Scope discipline:** the claim is **comparative at matched compute**, not absolute alpha; the
   Harvey–Liu–Zhu t>3 hurdle is correctly reserved for any absolute-alpha statement. *(B8.)*

**One-paragraph examiner-proof summary to put in the abstract/limitations:**
*"Overfitting and multiplicity are controlled by a pre-registered, hash-frozen stack: a trial-count-free
PBO/CSCV primary guard (full 12,870-split enumeration), a secondary Deflated Sharpe reported at both naïve
and effective trial counts, and a per-seed rliable IQM paired bootstrap (n=30) over a frozen m=6 family
corrected by Benjamini–Hochberg (Romano–Wolf as the FWER cross-check). The four hypotheses are
pre-registered as separate declared families with internal correction; we report a programme-wide
Bonferroni sensitivity and treat any non-rejection as a TOST-bounded effect. The single residual judgement
calls — the effective trial count under guided search and the absence of a global cross-hypothesis
correction — are stated explicitly with their bias directions, not concealed."*

---

## E. Literature anchors (precise)

- **DSR / PSR / expected-max-Sharpe + independence caveat + ONC effective-N:** Bailey & López de Prado
  (2014), *The Deflated Sharpe Ratio*, J. Portfolio Management 40(5); López de Prado (2018), *Advances in
  Financial Machine Learning*, ch. on the "effective number of trials" (ONC clustering). The PSR variance
  term `1 − γ₃·SR + (γ₄−1)/4·SR²` and E[max SR] = √Var[{SRₙ}]·((1−γ)Φ⁻¹(1−1/N)+γΦ⁻¹(1−1/(Ne))) match the
  code in `deflated_sharpe.py` (verified against the paper; Var[{SRₙ}] is cross-trial dispersion, not
  one-estimator SE).
- **PBO / CSCV:** Bailey, Borwein, López de Prado & Zhu (2015/2017), *The Probability of Backtest
  Overfitting*, J. Computational Finance 20(4). Model-free, rank-based, trial-count-free; the campaign's
  implementation is the canonical strict-λ<0 CSCV.
- **Multiple testing in finance / garden of forking paths:** Harvey & Liu (2015), *Evaluating Trading
  Strategies*, J. Portfolio Management; Harvey, Liu & Zhu (2016), *…and the Cross-Section of Expected
  Returns*, RFS; Harvey & Liu (2020), *False (and Missed) Discoveries in Financial Economics*, J. Finance;
  Gelman & Loken (2013/2014), *The garden of forking paths*. These ground both the "many rewards tried"
  hurdle and the defence that pre-registered separate estimands are not a scanned family.
- **FWER stepdown vs FDR:** Romano & Wolf (2005), *Stepwise multiple testing as formalized data snooping*,
  Econometrica 73(4) — FWER under arbitrary dependence via the bootstrap max-statistic (matches
  `multiple_testing.romano_wolf`). Benjamini & Hochberg (1995), *Controlling the FDR*, JRSS-B 57(1);
  Benjamini & Yekutieli (2001) for FDR under dependence (cite if claiming FDR across families). BH is more
  powerful for the small, positively-dependent m=6; RW is the stricter cross-check.
- **rliable / IQM / stratified percentile bootstrap:** Agarwal, Schwarzer, Castro, Courville & Bellemare
  (2021), *Deep RL at the Edge of the Statistical Precipice*, NeurIPS (Outstanding Paper). IQM = 25%-trimmed
  mean; percentile bootstrap B=2000 resampling seeds; reliable "with a handful of runs" — n=30 is
  comfortably above that.
- **Stationary bootstrap:** Politis & Romano (1994), *The Stationary Bootstrap*, JASA 89(428) — geometric
  block lengths, wrap-around (matches `stationary_bootstrap_indices`).
- **Equivalence / TOST:** Lakens (2017), *Equivalence Tests*, Soc. Psych. & Pers. Sci.; Schuirmann (1987).
  Bounds on the raw scale (the code applies the margin in the score's own units — correct, but the
  DSR-units-vs-Sharpe-units caveat is flagged in `power_analysis.py` and must carry to the write-up).
- **ES elicitability / comparative backtest:** Fissler & Ziegel (2016), *Higher order elicitability and
  Osband's principle*, Ann. Statist. 44(4) — (VaR, ES) jointly elicitable; Nolde & Ziegel (2017),
  *Elicitability and backtesting*, Ann. Appl. Statist. 11(4) — comparative ES backtest on the FZ0 score.
- **Sharpe time-scaling under autocorrelation:** Lo (2002), *The Statistics of Sharpe Ratios*, FAJ 58(4) —
  the √252 i.i.d.-scaling caveat (descriptive only; the headline test does not use it).
- **Tail-test power caveat:** Bauer (2025), arXiv:2505.23333 — low power at the most extreme quantiles /
  short windows.

---

## F. Bottom line

The backbone is **defensible and, in its hardest parts, exemplary**. The *implementation* is correct where
it is hardest to get right (PBO enumeration, the R16 per-seed fix, canonical DSR variance, forecast-vs-
realised CVaR separation). The exposure is **not** broken code — it is **five unstated judgement calls** an
expert examiner will probe: (A1/A8) the effective DSR trial count under guided search; (A3) PBO ranking on
mean-return vs the DSR selection rule; (A4) the absence of a global cross-hypothesis correction; (A5) the
two-sided-p + post-hoc-sign-gate construction vs the one-sided RW leg; (A6/A7) the bespoke CVaR test's
empirically-certified size and the CI/p-value principle mismatch. **All are closable before the freeze with
prose + small report-only code (C1–C9); the linchpin is C4 (pre-register the cross-hypothesis stance) and
C1 (effective-N sensitivity).** After those, the inference integrity is bulletproof *as an argument*, which
— for a PDF-only grade in front of this supervisor — is exactly the target.

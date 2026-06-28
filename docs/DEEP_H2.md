# DEEP_H2 — exhaustive scrutiny of the headline hypothesis

**Scope.** A harsh, no-shortcut interrogation of **H2** — *feeding the LLM reward-designer the realized-return
distribution (tail statistics) beats feeding it a scalar (Sharpe) at matched compute* — for an MSc dissertation
graded on the PDF alone (no viva; supervisor Dr Ramin Okhrati, who co-authored backtest-statistics and RL-finance
papers in the corpus). Everything below is grounded in code read first-hand (paths cited inline) and in the
literature cache + web research. The goal is to make H2 **bulletproof and the strongest defensible version**, and
to bank a **pre-registered null** as a Distinction-grade outcome.

**Verdict in one line.** H2 is well-posed and falsifiable, its feedback-channel isolation is unusually clean, and
its inference stack is more careful than most published RL work. But there are **three structural threats that
are currently mis-stated or under-powered** (the conjunction-vs-BH double-correction, the λ=0 / Sharpe-gate
construct-validity gap, and the EVT-measurement-noise → feedback-content confound), plus a cluster of
statistical-power and reporting issues. None is fatal; several are framing fixes; two need a pre-freeze code or
pre-registration amendment. The single highest-leverage move is to **reframe H2's primary claim around the
mechanism the design actually optimizes** (see §7).

Files audited: `scripts/analyze_campaign.py` (`h2_conjunction`, `collect_family_pvalues`, `romano_wolf_joint`,
`h2_sharpe_rf_robustness`, `beat_human_baseline`); `src/feedback/{schema.py,measurement.py}`;
`src/inference/{bootstrap.py,deflated_sharpe.py,multiple_testing.py,overfitting.py,es_backtest.py}`;
`src/selection/fitness.py`; `src/llm/{loop.py,prompts.py}`; `prompts/reflection.txt`;
`PREREGISTRATION.md` §1/§4/§5/§6/§10; `config/{preregistration,inference}.yaml`;
`00_planning/LIMITATIONS_REGISTER.md` (L1–L14); `docs/POWER_ANALYSIS.md`.

---

## 1. Is H2 well-posed and falsifiable? Is the feedback-channel isolation clean?

### 1.1 Well-posedness — PASS, with one wording risk
H2 has a fixed unit of inference (a reward function's OOS risk-adjusted performance, across seeds and the candidate
population; `PREREGISTRATION.md` §1), a fixed comparator (the scalar arm), a fixed estimand (the IQM of per-seed
test Sharpe, with a paired across-seed bootstrap), a frozen rejection rule (the three-leg conjunction after
BH/FWER correction; `analyze_campaign.h2_conjunction`), a frozen direction (distributional > comparator), and a
pre-registered equivalence margin (TOST ±0.05 DSR; `config/preregistration.yaml: inference.equivalence_margin`).
It is therefore **falsifiable in both directions**: it can reject (all three Sharpe legs clear, correct sign) or
fail to reject (and a TOST-inside-margin result is reportable as practical equivalence, not silent failure). This
is the correct skeleton for a bankable null.

**Wording risk (construct validity, MODERATE).** The headline sentence says "beats … at matched compute," but the
*operational* H2 is a **conjunction**: distributional must beat scalar **and** placebo **and** scalar_cvar5 on the
Sharpe leg. These are not the same hypothesis. The placebo and scalar_cvar5 legs are not "H2"; they are
**construct-validity controls** that rule out two confounds (token-count and any-downside-number). The dissertation
must state this explicitly, because an examiner who reads "distributional beats scalar" in the abstract and then
finds the verdict gated on two extra arms will (correctly) ask which hypothesis was actually tested. Recommended:
present H2 as *"distributional feedback beats scalar feedback, and the advantage is attributable to tail-shape
information specifically (survives placebo and single-CVaR controls)."* That is what the code tests.

### 1.2 Feedback-channel isolation — the strongest part of the design
The contribution axis is the **feedback block only**; the agent is a fixed SB3-SAC and the tail statistics are
measured **off-critic** from realized returns (`src/feedback/measurement.py`; `CLAUDE.md` audit A-1). I verified
the isolation holds at three levels:

1. **Shared loop machinery.** `src/llm/loop.py::run_loop` is arm-agnostic; the *only* arm-dependent line is
   `feedback_block = schema.build_block(arm, val_fitness, tail_for_block)` (loop.py:403) and the gating of
   `tail_for_block` to the two tail-carrying arms (loop.py:400–402). System prompt, initial prompt, env interface,
   diversity directive (`_diversity_directive`, loop.py:189), training budget, fitness, and selection are
   byte-identical across the five LLM arms. **This is a genuinely clean instrument** and is the project's core
   methodological strength.

2. **Matched block structure (the token-count control).** `src/feedback/schema.py` builds blocks with **identical
   line-count and ±15% character length** across distributional/placebo (the placebo emits `len(_DIST_FIELDS)`
   inert "reference value N" lines, schema.py:111–118). `scalar_cvar5` is scalar + exactly one CVaR-5% line. So
   the distributional-vs-scalar contrast is confounded with length, but distributional-vs-**placebo** removes
   length, and distributional-vs-**scalar_cvar5** removes "one downside number." The conjunction is what isolates
   *tail-shape information*. This is a textbook construct-validity scaffold and should be sold as such.

3. **Split hygiene.** Feedback is measured on **training** returns; selection is on **validation** Deflated Sharpe;
   the test leg is sealed (`measurement.py` docstring; `fitness.py::held_out_fitness` rejects non-val splits,
   fitness.py:79–83). The feedback channel cannot tune-then-select on the same data.

### 1.3 Residual confounds between distributional and scalar — graded
Even with the off-critic isolation, four residual confounds remain. Severity is for the **distributional-vs-scalar
contrast specifically**; the placebo/scalar_cvar5 legs neutralize some of them.

| # | Confound | Neutralized by | Residual severity |
|---|---|---|---|
| C-a | **Prompt length / token count** (more text → more "thinking") | placebo leg (matched length, inert) | LOW — directly controlled |
| C-b | **Numeric anchoring / priming** (any extra number, even non-tail, nudges the author toward risk terms) | scalar_cvar5 leg (one downside number) | LOW–MODERATE — *partially* controlled: scalar_cvar5 supplies ONE risk number; distributional supplies SIX. Anchoring could scale with the *count* of numbers, which only the placebo (zero informative numbers) bounds. The conjunction over BOTH controls is the defense. |
| C-c | **Measurement noise in the fed statistics** (the EVT CVaR-5%/1% the distributional arm sees is itself a noisy estimate; see §6) | none — this is intrinsic to the arm | MODERATE — the distributional arm is fed a *noisier* signal than scalar's clean DSR; if it loses, is it the channel or the noise? (Analyzed in §6.4.) |
| C-d | **LLM stochasticity across arms** (different reward code is sampled per arm; the contrast is between *populations* of authored rewards, not a controlled edit) | matched budget + 30 winner seeds + per-seed IQM bootstrap | MODERATE — carried by the inference, not eliminated; this is the "one-lucky-reward" risk the variance-decomposition appendix addresses (`analyze_campaign.analyze(variance_run_roots=...)`). |

**The honest position:** the feedback-channel isolation is clean for *information content vs token count* (C-a, via
placebo) and *tail-shape vs any-downside-number* (C-b, via scalar_cvar5). It is **not** clean for *information vs
information-noise* (C-c) — and the design should disclose that the distributional arm is handed a higher-variance
signal, which biases **against** H2 (good for a null, bad for a positive claim). See §6.4 and the L-register
addition recommended in §8.

---

## 2. Is "distributional feedback = EVT tail stats" the right operationalization?

### 2.1 The construct, and the gap between label and operationalization
The *construct* is "the realized-return distribution." The *operationalization* is six scalars: `cvar_05`, `cvar_10`,
`cvar_25`, `cvar_01`, `left_tail_mass` (P(r < −2σ)), `robust_skew` (Bowley) (`measurement.py::tail_stats`,
schema.py `_DIST_FIELDS`). This is **a lower-tail summary, not the distribution** — there is no mode, no
right-tail, no full quantile grid, no volatility-of-volatility, no autocorrelation. Two readings:

- **Too narrow.** "Distribution" oversells six left-tail numbers. An examiner can say: you fed *downside risk
  statistics*, not "the distribution"; a fairer label is **"multi-level tail-risk feedback."** I think this critique
  is correct and the dissertation should **retitle the construct to "tail/distributional risk feedback"** and state
  precisely what is and isn't in the vector. This is a one-paragraph fix that pre-empts the easiest construct hit.

- **Defensibly principled (the strong rebuttal).** The *choice* of CVaR-at-multiple-levels is not arbitrary: by the
  **Kusuoka (2001) representation**, every law-invariant coherent risk measure is a mixture of CVaRs across levels,
  so a CVaR profile at {1, 5, 10, 25}% is a principled spanning summary of the *coherent* risk content of the lower
  tail (Acerbi 2002 spectral measures). CVaR (not VaR) follows from **Artzner et al. (1999)** coherence
  (subadditivity). So "CVaR at several levels + tail mass + skew" is a *theory-grounded* tail descriptor, not a
  grab-bag. This is the framing to lead with (it is already in `LITERATURE_AND_DEFENSE_COMPANION` §3.1 / Part-5 map).

### 2.2 Is it too broad / could the result be driven by one field?
The block carries six numbers; the LLM could be responding to **just `robust_skew`** or **just `cvar_05`**. The
design cannot attribute the effect to a *specific* tail statistic — only to the *bundle* vs the controls. That is
acceptable for H2 (the hypothesis is about the channel, not the field), but it is a known **interpretability
limit**: a positive H2 says "tail-shape information helps," not "CVaR-5% specifically helps." Disclose it. (A
field-ablation — drop one field at a time — is *not* in the frozen design and should stay out of scope; flag as
future work, not a gap.)

### 2.3 The scalar comparator is the right "null channel"
The scalar arm is fed **validation Deflated Sharpe** — a single risk-adjusted scalar (schema.py:34, `_HEADER`).
This is the correct minimal comparator: it is the *same* fitness number the selection uses, so the scalar arm sees
"how good was the last reward" with **zero** distributional content. Good. One subtlety: the scalar metric is
*DSR*, which already embeds skew/kurtosis penalties (`deflated_sharpe.py`). So the scalar arm is not fed a
*mean-only* signal — it is fed a *non-normality-aware* scalar. This **strengthens** the null channel (the scalar
arm already "knows" something about higher moments through DSR), making H2 *harder* to win — which is conservative
and good for a bankable null. Worth one sentence: "even the scalar comparator carries non-normality information via
the DSR, so H2 tests whether *explicit, multi-level* tail feedback adds value beyond a higher-moment-aware scalar."

---

## 3. The conjunction logic — does it bias the result? Is it the most defensible structure?

This is the **most important statistical issue in the file**, and it is currently **mis-specified in a way that
makes H2 harder to support than the pre-registration intends.**

### 3.1 What the code does (verified)
`analyze_campaign.collect_family_pvalues` builds the m=6 family `{3 contrasts × (Sharpe, CVaR-0.05)}`, runs the
per-seed paired bootstrap on each, and applies **Benjamini-Hochberg across all six** (`benjamini_hochberg(pvals,
q=0.05)`, analyze_campaign.py:801). Then `h2_conjunction` requires **all three Sharpe legs** to be `reject_bh AND
direction_ok` (analyze_campaign.py:1057–1059). So the headline gate = **(3-way conjunction) of (BH-corrected
across 6) p-values**.

### 3.2 Why this is statistically incoherent (double penalty)
A conjunction ("reject H2 only if all legs reject") is an **intersection–union test (IUT; Berger 1982)**. The
defining property of an IUT, confirmed in the multiple-testing literature, is:

> *"An alpha adjustment is appropriate when making an inference about an intersection null on the basis of a
> union-intersection test … [but] the intersection-union test … is conservative in nature, as the rejection region
> has a level that is the maximum of the levels of the constituent tests."* (SenGupta; Brunner 2004; "When to
> Adjust Alpha," arXiv:2107.02947.)

In plain terms: **a conjunction test controls its own type-I error at α without any multiplicity correction on the
legs.** Requiring *all* legs to reject is already conservative; the joint size is ≤ max(leg sizes) = α. Applying
**BH on top of the conjunction double-penalizes**: each leg's bar is raised by BH *and* the conjunction requires all
of them to clear it. The result is a test whose true size is far below α, i.e. **under-powered against H2** — it
will fail to reject even when distributional genuinely dominates.

Concretely with the current code: the three Sharpe legs are buried in an m=6 BH family that *also* contains three
CVaR legs. If the CVaR legs have large p-values (likely — tail tests are low-power, §6/Bauer 2025), they **inflate
the BH thresholds** the Sharpe legs must clear (BH ranks all six; a few large p-values push the step-up boundary
down for the rest). So the CVaR legs' noise **leaks into and weakens the Sharpe conjunction** — the headline gate.
This is a real, demonstrable bias **against** H2.

### 3.3 What the defensible structure is
There are two clean, standard options. **Pick one and pre-register it as the primary; report the other as
sensitivity.**

- **(A) IUT on the three Sharpe legs at α=0.05, no leg correction.** The conjunction *is* the correction. Each leg
  tested one-sided at 0.05; H2 supported iff all three reject in the predicted direction. This is the textbook IUT
  and the most powerful coherent choice. The three CVaR legs become a **separate, explicitly-labeled secondary
  family** (their own BH), reported as "the tail-outcome corroboration," not part of the headline gate. **This is
  my recommended primary** because (i) it is standard, (ii) it is maximally powerful for the headline, and (iii) it
  cleanly separates "did distributional win on risk-adjusted performance" (Sharpe conjunction) from "did the tail
  improve" (CVaR family) — which is exactly the §1 split between "risk-adjusted performance" and the tail outcome.

- **(B) Keep BH over m=6, but DROP the conjunction; report the BH rejection set directly.** Then H2's distributional
  > scalar Sharpe leg is one of six FDR-controlled tests, and you report which of the six survive. This is also
  coherent (no double penalty) but *weaker as a headline* because it doesn't enforce the placebo/scalar_cvar5
  controls as gates — they become reported-alongside rather than required.

**The current code is neither (A) nor (B): it is (conjunction) ∘ (BH over 6), which double-corrects.** This is the
single most consequential pre-freeze fix. Note the asymmetry of the error: the bug makes H2 *harder* to support, so
it does not threaten a **null** result's credibility (a null under an over-conservative test is still a valid null,
arguably *more* bankable). But it materially reduces power if the true effect is real, and an expert examiner
(Okhrati) will spot the IUT-plus-FDR double-counting immediately. **Fix it regardless**, and frame the null (if it
arises) as robust to the choice.

### 3.4 The CVaR-leg direction convention — verify it is not silently wrong
`collect_family_pvalues` sets `direction_ok = effect > 0` where `effect = stat_a − stat_b` and `stat` is
`cvar(v, level)` (a **signed**, negative-for-loss quantity; `bootstrap.cvar` returns the mean of the worst tail,
negative). So "a better than b" on CVaR means **less negative** (higher/safer) CVaR — correct (analyze_campaign.py
comment at :696 confirms "higher = less-negative tail = better"). Good, but **state this sign convention in the
write-up** because a CVaR "improvement" that is *more negative* would be a wrong-sign (type-III) error, exactly the
Bauer (2025) failure mode the pre-registration cites. The code is right; the prose must be explicit.

### 3.5 Does the Sharpe-only gate (CVaR reported but not gated) bias toward a positive H2?
No — it biases *conservative* for the **tail** claim and is correct for the **risk-adjusted-performance** claim.
The conjunction gate is the Sharpe leg (§1's "risk-adjusted performance"); the CVaR legs are corrected and reported
but do not decide H2 (analyze_campaign.py:937–938 docstring). This is defensible **provided the abstract does not
claim a tail improvement** unless the CVaR family also rejects. Recommended: a two-tier verdict — *"H2 (risk-adjusted)
supported/not"* from the Sharpe IUT, and *"tail-shape improvement supported/not"* from the CVaR family — reported
separately. Conflating them is the trap.

---

## 4. λ=0 tail-blind selection — clean isolation or under-powered H2?

### 4.1 What it does and why
Selection is **pure validation Deflated Sharpe, λ=0** — no CVaR penalty (`fitness.py::held_out_fitness`, the `lam`
default is 0.0; `config/preregistration.yaml: fitness.lambda_cvar: 0.0`; PREREGISTRATION §5 PROPOSED amendment
R22). Within each arm the winner is the candidate with the best risk-adjusted **mean** performance, not the best
tail. This is documented as a deliberate, conservative choice in L13.

### 4.2 The genuine tension (this is the crux the prototype exposed)
The prototype showed exactly the predicted symptom: **scalar led on DSR winner-fitness (0.110 > 0.060) while
distributional won on CVaR (p≈0.004) and on mean-Sharpe / floor-raising** (memory: prototype-results).
**⚠ Reversed-under-control (2026-06-26 re-analysis):** that "p≈0.004 distributional-beats-scalar" tail is
a *directional NULL*, not a win — against the zero-info `placebo` the distributional tail is significantly
**worse** (CVaR-5% placebo −0.01711 *safest* > distributional −0.01896; `distributional_vs_placebo`
p=0.0005; responsiveness −0.053). No prototype number enters the dissertation; the reframe below builds the
*structure* to bank a **campaign** tail win, not a prototype claim. Read
carefully, this is still a **construct-validity problem for the Sharpe-gated H2**, not just a power issue:

- The thing the distributional feedback most plausibly improves is the **tail** (that is the information it adds).
- But selection picks the **DSR-best** candidate per arm, and the headline gate is the **Sharpe** leg.
- So the design selects-on and tests-on the dimension where the distributional arm has the *weakest* predicted
  edge, and relegates the dimension where it has the *strongest* predicted edge (CVaR) to a non-gating, low-power
  (Bauer 2025) secondary.

This is **a real risk of under-powering H2 against its own mechanism.** If distributional rewards genuinely produce
better tails but similar or slightly-worse means (a very plausible risk/return trade-off — tail-hedging costs mean
return), then: λ=0 selection passes over the tail-better candidate; the Sharpe leg shows no effect or a negative
effect; H2 "fails" on the gate **even though the distributional channel did exactly what it should.** The prototype
is a warning shot for precisely this.

### 4.3 Is λ=0 still the right call? — Yes, but the framing must change
Despite §4.2, λ=0 is the **correct** choice for three reasons, and the fix is in the *claim*, not the λ:

1. **Reward-independence / un-hackability.** A tail-aware selection rule (λ>0) would advantage the distributional
   arm *by construction* (it rewards the very thing that arm is fed), making any tail win circular. λ=0 keeps
   selection identical, reward-independent, and tail-blind across arms — the only way the tail outcome on the
   sealed test leg is *causally attributable to the feedback channel* rather than to a tail-favoring selector.
   (L13 makes this argument; it is correct.)

2. **Eureka-faithfulness.** Eureka selects on a single scalar fitness, not a multi-objective. λ=0 mirrors that.

3. **No calibration available.** A principled λ>0 needs a pre-2015 calibration that was never performed
   (`config/inference.yaml: lambda_frozen: null`). A guessed λ is worse than λ=0.

**But the design must then NOT make the Sharpe leg carry the whole headline.** The resolution is §3.3-(A) plus a
framing change (§7): the **risk-adjusted-performance** claim (Sharpe IUT) and the **tail-improvement** claim (CVaR
family + the FZ0/ES comparative backtest) are **co-primary**, reported as a two-part verdict. Then:

- If distributional wins on Sharpe → strong H2 (it improved risk-adjusted performance *without* a tail-favoring
  selector — a *stronger* result than if you'd tuned λ).
- If distributional wins only on CVaR → the honest, defensible finding is *"tail-shape feedback shifts the realized
  tail (CVaR p<0.05, FZ0/ES corroborated) at parity of risk-adjusted mean performance"* — which is a **publishable,
  bankable result**, not a null, *provided* the CVaR family is pre-registered as co-primary rather than secondary.
- If neither → a clean, pre-registered null with a TOST equivalence bound.

**Recommended pre-freeze action:** elevate the **CVaR-0.05 distributional-vs-{scalar, placebo, scalar_cvar5}**
legs from "reported within the family" to a **declared co-primary tail hypothesis (H2-tail)** with its own IUT,
distinct from the Sharpe H2 (H2-risk-adjusted). This is the change that gives a **campaign** tail signal a
co-primary home. *(Caveat: the prototype's "CVaR p=0.004" is NOT that signal — it is a directional null that
REVERSES under the zero-info placebo, p=0.0005; the elevation builds the structure to bank a campaign win, it
does not retro-bank the prototype number.)* It does not touch λ, the budget, the arms, or the seeds — it re-labels
the existing CVaR legs as co-primary and gives them their own conjunction (mirroring the Sharpe one). Flag to the
user as a pre-freeze amendment; it strictly *improves* H2's ability to detect its own mechanism.

### 4.4 A subtle interaction: λ=0 + DSR-argmax winner selection + 30 seeds
The winner is chosen by **single-seed** validation DSR during search (`select_winner` reads `val_fitness`,
run_campaign.py:331), then re-run at 30 seeds for the test inference. So the *winner identity* is fixed by one
noisy DSR draw, and the across-seed bootstrap only quantifies uncertainty *given that winner*. If the
single-seed DSR-argmax picks a tail-mediocre distributional candidate (because λ=0 ignores the tail and the one
search seed was noisy), the 30-seed test inference faithfully measures a sub-optimal winner. This is a
**selection-noise** threat distinct from λ: the winner-selection is under-powered (1 seed) relative to the
evaluation (30 seeds). The PBO guard addresses *overfitting* of selection but not *seed-noise* of selection.
**Disclose** this as a known asymmetry (it is the L14 buffer asymmetry's cousin) and note it biases toward *noise*,
i.e. against detecting a real effect — conservative, but power-reducing.

---

## 5. Per-seed inference (paired across-seed bootstrap, IQM, n=30); TOST; the m=6 family

### 5.1 The per-seed rliable construction — correct and well-motivated
`bootstrap.paired_seed_difference_test` resamples **seed indices** i.i.d. with replacement, applies the **same
draw to both arms** (paired, so seed-level common variance cancels), recomputes `IQM(a)−IQM(b)`, and uses the
re-centred basic two-sided p-value (`|boot−obs| ≥ |obs|`). This is **exactly the rliable paired stratified
bootstrap** (Agarwal et al. 2021): "seeds are sampled with replacement, used as indices for both algorithms …
the difference between the IQMs is computed … centered by the observed IQM … two-sided p-value from the proportion
of centered replicates whose magnitude exceeds the observed." The R16 amendment (moving from a seed-**averaged**
single series to per-seed scores) is **the correct fix** — the averaged-series construction was anti-conservative
(~21% true-null rejection; certified by `null_calibration`, audit C-7). I verified the implementation matches the
rliable method. This is a strength; cite Agarwal et al. (2021) precisely and note Eureka itself used rliable.

### 5.2 Power at n=30 seeds — adequate for the headline, weak for the tail
n=30 winner seeds clears the Henderson (2018) / Colas et al. (≥20) bar and is *above* typical deep-RL practice.
But three power caveats are real:

- **IQM trims 25% per tail → effective n ≈ 15** for the central-tendency estimate (`iqm` keeps the middle 50%,
  bootstrap.py:99–100). The robustness is bought with variance: the bootstrap correctly carries this (it resamples
  all 30 then trims inside each replicate), but the *effective* sample for the point estimate is ~15, so the CIs
  are wider than a mean-based n=30. This is the intended robustness/power trade and is fine — but the
  `POWER_ANALYSIS.md` MDE (Δ≈0.27 DSR at σ=0.30 placeholder) is computed for a **mean**-based difference test, not
  the IQM bootstrap. **The power analysis does not match the realized test.** Recommended: re-run
  `power_analysis.py` with the **IQM paired-seed bootstrap** as the test statistic and the **pilot σ**, so the MDE
  is the MDE of the test you actually run. (The doc itself flags σ as a placeholder TBD.)

- **The p-value floor `1/(n_boot+1)` with n_boot=2000** caps resolution at p≈0.0005 — fine. But the *bootstrap
  granularity* over **30 paired seeds** is the real limit: with 30 seeds the paired-difference distribution is
  coarse, and IQM on resampled-with-replacement 30-vectors takes few distinct values, so p-values are **granular**
  (the achievable p-values are not continuous). At n=30 this is acceptable but worth a sentence; it slightly
  inflates the smallest achievable p and is conservative.

- **CVaR-per-seed legs are doubly under-powered:** each seed's *test-leg* CVaR-5% is itself estimated on the
  sealed window's tail (~8 years daily ≈ 2000 steps, 5% tail ≈ 100 obs — OK), but the **across-seed** IQM of those
  CVaRs over 30 seeds, then bootstrapped, inherits the Bauer (2025) low-power-at-extreme-quantiles problem. This is
  why CVaR-1% must never gate (it doesn't) and why the CVaR-5% co-primary (§4.3) is the right tail level.

### 5.3 TOST equivalence (±0.05 DSR) — correct in principle, mind the units
The TOST margin is ±0.05 **validation-DSR** units (`config/preregistration.yaml: inference.equivalence_margin`).
Two checks:

- **Unit consistency.** The headline test is on **test-leg Sharpe IQM** (annualized), not validation DSR. The SESOI
  and TOST margin are in *DSR* units (a probability-like [0,1] quantity), but the difference test is in *annualized
  Sharpe* units. **These are not the same scale.** `POWER_ANALYSIS.md` line ~27 hand-waves "≈0.10–0.15 annualised
  test-Sharpe" as the SESOI's Sharpe equivalent, but the TOST CI the code would compute is in Sharpe units while
  the margin is stated in DSR. **This is a latent units mismatch that an examiner could exploit.** Recommended:
  state the TOST margin in the **same units as the test statistic** (annualized test-Sharpe IQM), and derive it
  from the SESOI explicitly, or run the TOST on the validation-DSR difference (matching the margin's units) and
  label it as such. Pick one and make units agree.

- **Is TOST even wired for the per-seed IQM test?** I did **not** find a TOST function operating on the per-seed
  bootstrap in `analyze_campaign.py` (the equivalence margin lives in config and `POWER_ANALYSIS.md`, but the
  90%-CI-inside-±margin check is not obviously implemented against the IQM paired bootstrap). **Verify and, if
  absent, wire it**: a non-rejection without the TOST bound is just "we didn't find an effect"; *with* the bound it
  is "the effect is smaller than the SESOI" — the bankable-null upgrade. This is a concrete pre-freeze gap.

### 5.4 The m=6 family freeze + fail-loud assert — a genuine rigor asset
`assert_realized_family_matches_frozen` re-derives the realized family and asserts byte-equality with
`config/preregistration.yaml: inference.testing_family` (analyze_campaign.py:496–565), fired inside
`collect_family_pvalues` when the full contrast set runs. This is **exactly** the guard that stops silent family
drift, and it is the kind of pre-registration discipline that reads as rigor. Keep it. (If you adopt §3.3-(A) /
§4.3, **update the frozen family** to reflect the Sharpe-IUT-primary + CVaR-IUT-co-primary structure, and update
this assert and the YAML mirror in lockstep — the freeze.py check enforces agreement.)

### 5.5 The DSR `var_sr` proxy-vs-canonical recompute — correct and worth a sentence
`winner_dsr` recomputes the headline DSR with the **empirical cross-candidate** Sharpe dispersion (canonical
Bailey–López de Prado) rather than the within-series proxy the search path records
(`deflated_sharpe.py:198–201` proxy vs `analyze_campaign.winner_dsr:389–390` canonical). The per-period-vs-annualized
`var_sr` consistency (the P1 fix at analyze_campaign.py:380–390, using `_sample_moments` not the annualized
`sharpe_ratio`) is **correctly handled** — I verified the canonical path uses per-period Sharpes so `sr_star` is on
the right scale. This is a subtle correctness point the audit got right; it is DSR-secondary so it doesn't gate H2,
but it is a clean detail to mention.

---

## 6. The tail MEASUREMENT (EVT/GPD on training returns) — leakage? stability? bias?

### 6.1 Leakage — clean
The EVT fit is on **training** realized returns (`measurement.py` docstring, B-2); feedback is fed to the
*designer* of the reward the agent then optimizes; selection is on **validation**; test is sealed. There is **no
test-leg leakage** in the measurement. The only "leakage"-adjacent concern is that the *same* training returns
both (a) train the agent and (b) are summarized into feedback — but that is *by design* (the feedback describes the
in-sample distribution the reward shaped) and is identical across the two tail-carrying arms, so it cannot
confound the contrast. PASS.

### 6.2 Estimator bias — the GPD MLE on few exceedances is biased, and the headline CVaR-5% uses it
`measurement.py::cvar` routes **α ≤ 0.05 to the EVT/GPD fit** (`EVT_ALPHA_CUTOFF = 0.05`, measurement.py:224). So
the **headline CVaR-5%** that gates nothing but *is fed to the distributional arm* and *is a co-primary tail
metric* (§4.3) is **EVT-extrapolated**, and the GPD MLE is fit on exceedances above the 90th loss percentile
(`threshold_q=0.10`, measurement.py:84). On ~750 training returns that is ~75 exceedances for the *fit*, but the
**5% and 1% CVaR are extrapolations** beyond/within that tail. The literature is unambiguous:

> *"Small-sample biases can arise even when the assumed model is correct … with small samples, shape parameter
> estimates are highly variable … too high a threshold leaves too few data points for reliable estimation."*
> (arXiv:2007.10780; Giles GPD bias notes; tandfonline 2021 "Risk Analysis via GPD".)

The design **already knows this** and stages a fix: `threshold_sensitivity` diagnostic (measurement.py:266) + the
**bias-corrected POT (Troop et al. 2021)** as the frozen Phase-1 enhancement (PREREGISTRATION §4, RESEARCH-2).
**Two actions:** (i) confirm the Troop bias-correction is actually implemented before freeze (I found the
*diagnostic* `threshold_sensitivity` but **not** a bias-corrected estimator in `measurement.py` — the docstring
calls it "the frozen Phase-1 enhancement," i.e. possibly not yet built). If it is not built, either build it or
demote the claim to "bias-corrected POT is future work" — do **not** ship a docstring promising a fix that the code
doesn't perform (that is exactly the kind of mismatch an examiner who reads the code will catch). (ii) **Report the
`threshold_sensitivity` spread** for the fed CVaR-5%/1% in the dissertation as an honest stability exhibit.

### 6.3 Stability / internal contradiction in the EVT routing — verify
`cvar(alpha)` for α ≤ 0.05 calls `_evt_cvar`, which **falls back to empirical** if `alpha > exceed_frac`
(measurement.py:177). With `threshold_q=0.10`, `exceed_frac ≈ 0.10`, so α=0.05 and α=0.01 are *within* the tail
mass and **do** use EVT — consistent. But note the fed CVaR-5% can **silently switch** between EVT and empirical
across seeds/arms if `exceed_frac` drifts near 0.05 (e.g. a reward producing few losses). This would make the fed
signal's *estimator* arm-dependent — a subtle confound. **Low severity** (exceed_frac≈0.10 ≫ 0.05 in practice),
but worth a guard/assert that the headline fed levels use a *consistent* estimator, and a sentence disclosing it.

### 6.4 The measurement-noise → H2-content confound (C-c, the deep one)
This is the threat that most undercuts a **positive** H2 and most *protects* a **null** H2. The distributional arm
is fed CVaR-5%/1% values that are **EVT extrapolations with non-trivial estimator variance** (the GPD shape
parameter is "highly variable" on tail data). So the distributional arm is handed a *noisier* feedback signal than
the scalar arm's clean DSR. Consequences:

- If distributional **wins**, the noise only makes that harder, so the win is *conservative-certified* — good.
- If distributional **loses or ties**, you cannot cleanly say "tail information doesn't help" — it might be "tail
  information helps but we fed it through a noisy estimator." This **weakens a null's interpretation**, which is the
  one thing you cannot afford for a bankable-null strategy.

**Mitigation / framing:** (a) the **empirical** CVaR-10%/25% and **left_tail_mass** in the same block are
low-variance (not EVT), so the distributional arm is not *entirely* fed noise — the bundle mixes clean and noisy
tail stats; lead with that. (b) Report the `threshold_sensitivity` CV so the reader can see the fed-signal noise is
bounded. (c) In the null write-up, state the honest scope: *"H2 tests the value of multi-level tail feedback **as
operationalized by an empirical-body + EVT-tail estimator**; a different (lower-variance) tail estimator could
change the result"* — turning the limitation into a precise scope statement rather than a hole. This is the L-register
entry I recommend adding (§8, L15).

### 6.5 robust_skew and left_tail_mass — minor but check the sign and the σ
- `robust_skew` (Bowley) is `((Q95−Q50)−(Q50−Q05))/(Q95−Q05+eps)`, **negative when the left tail is longer**
  (measurement.py:256; schema labels it "left-tail skew"). Sign convention is frozen and matches the prose. Fine.
- `left_tail_mass = mean(r < −2σ)` uses the **population** σ (`arr.std()`, measurement.py:254, ddof=0) of the
  *training* returns. Two returns regimes with the same tail but different overall vol get different `left_tail_mass`
  — it is a *standardized* tail count, which is intended. No bug, but note it is vol-relative (an examiner might
  ask "is −2σ the same threshold across arms?" — answer: each arm's reward induces its own σ, so the threshold is
  reward-relative; that is correct because the feedback describes *that reward's* induced distribution).

---

## 7. The strongest defensible H2 framing + the bankable-null statement

### 7.1 The reframe (the highest-leverage change)
Make H2 **two co-primary claims**, mapped to the two dimensions the design can actually move, and decided by two
clean IUTs:

> **H2-RA (risk-adjusted performance).** Feeding the reward-designer multi-level tail-risk statistics (vs a
> scalar) yields rewards whose frozen winners achieve **higher out-of-sample risk-adjusted performance (Sharpe IQM)**
> at matched compute — and this advantage is attributable to tail-shape *information* (survives the length-matched
> **placebo** and the single-number **scalar_cvar5** controls). Decided by a **3-leg intersection–union test on the
> Sharpe legs at α=0.05** (no further leg correction — the conjunction is the correction).
>
> **H2-Tail (tail outcome).** The same feedback yields rewards whose frozen winners achieve a **less-severe realized
> left tail (higher CVaR-5%)** out-of-sample, again surviving placebo and scalar_cvar5. Decided by a **parallel
> 3-leg IUT on the CVaR-5% legs**, corroborated by the **FZ0/(VaR,ES) Diebold–Mariano comparative backtest**
> (Fissler–Ziegel 2016; Nolde–Ziegel 2017; `es_backtest.comparative_es_backtest`).

This reframe (i) removes the double-correction (§3), (ii) gives a **campaign** tail signal a *primary*
home (§4) — *not* the prototype's CVaR-p=0.004, which is a directional null that reverses under the zero-info
placebo (p=0.0005); no prototype number enters the result — (iii) honestly separates "did it help
risk-adjusted return" from "did it shift the tail," and (iv) makes
**any** of {both reject, only-RA, only-Tail, neither} a *clean, pre-registered, reportable* outcome. It is strictly
stronger than the current single-Sharpe-conjunction gate and costs no compute.

### 7.2 The exact bankable-null statement (to pre-register verbatim)
> *"We pre-registered, before observing the sealed 2018–2025 test leg, the hypotheses H2-RA and H2-Tail above,
> their three-leg intersection–union decision rules at α=0.05, the directional predictions, the per-seed rliable
> IQM paired-bootstrap test over 30 winner seeds (Agarwal et al. 2021), the SESOI of 0.05 DSR, and a symmetric
> TOST equivalence margin of ±0.05 (in the test-statistic's units). If neither H2-RA nor H2-Tail rejects, we report
> a **null**: at matched compute and with a fixed SB3-SAC agent, multi-level tail-risk feedback to an LLM
> reward-designer did **not** produce detectably better out-of-sample risk-adjusted performance or tail outcomes
> than scalar feedback, **and** — where the TOST 90% bootstrap CI lies inside ±0.05 — the two feedback channels are
> **practically equivalent within the smallest effect we deemed worth detecting**. Because the design, budget,
> metrics, decision rules, and equivalence margin were fixed in advance (PREREGISTRATION §1/§5/§10; freeze hash in
> DECISION_LOG), this null is a calibrated statement about the feedback channel as posed, not a moved goalpost. The
> contrast is common-mode across all confounds applied byte-identically to every arm (universe composition,
> delisting fill, costs, rf convention, seed budget; LIMITATIONS_REGISTER closing framing), so it isolates the
> feedback channel, and the result bounds the channel's value rather than the market's."*

This statement is bankable because it (a) names the estimand, (b) carries an equivalence bound (not just "no
effect"), (c) is pre-registered and hashed, (d) scopes to the operationalization (tail-stats-via-EVT, fixed agent,
matched compute) so it cannot be over-read, and (e) ties the common-mode-confound argument to the comparative
claim. An examiner cannot dismiss it as a failed fishing trip.

### 7.3 What to claim if only one rejects (the most likely outcome, per the prototype)
- **Only H2-Tail rejects** *(a possible CAMPAIGN outcome — NOT corroborated by the prototype, whose CVaR
  p=0.004 reverses under the zero-info placebo, p=0.0005, i.e. a directional null)*: *"Multi-level tail feedback measurably improved the
  realized left tail (CVaR-5%) of the resulting policies at parity of risk-adjusted mean performance — the feedback
  channel acts on the dimension it informs (the tail), not on average return."* This is a **positive, novel,
  publishable** finding and the design should be set up to bank it (hence the §4.3 co-primary elevation).
- **Only H2-RA rejects:** the cleaner headline ("tail feedback improved risk-adjusted performance without a
  tail-favoring selector"), unusually strong because λ=0 means the win was not engineered.

---

## 8. Prioritized pre-freeze hardening actions (for the maintainer)

**Severity key:** [S1] must-fix before freeze (correctness/credibility); [S2] should-fix (power/framing/units);
[S3] disclose/polish.

1. **[S1] Fix the conjunction × BH double-correction (§3).** Replace the headline gate with an **intersection–union
   test on the three Sharpe legs at α=0.05, no leg correction**, and move the three CVaR legs to a **separate,
   explicitly-labeled family** (their own BH or co-primary IUT). Update `h2_conjunction`, `collect_family_pvalues`,
   the frozen `inference.testing_family`, and `assert_realized_family_matches_frozen` in lockstep. Re-state the
   m=6 freeze as "Sharpe IUT (m=3, primary) + CVaR IUT/family (m=3, co-primary/secondary)." This is the one change
   an expert (Okhrati) will otherwise flag as statistically incoherent. *Note: the current bug only makes H2 harder
   to support, so a null already obtained under it remains valid — but fix it for the positive case and for
   credibility.*

2. **[S1] Reconcile the EVT bias-correction claim with the code (§6.2).** Confirm whether bias-corrected POT (Troop
   et al. 2021) is implemented in `measurement.py`. I found only the `threshold_sensitivity` *diagnostic*. If the
   correction is not built, either build it or change the docstring/PREREGISTRATION §4 from "frozen Phase-1
   enhancement" to "future work" — do not ship a promised fix the code doesn't perform.

3. **[S1] Elevate CVaR-5% to a co-primary tail hypothesis H2-Tail (§4.3, §7).** Re-label the existing CVaR legs as
   co-primary with their own IUT, so a **campaign** tail signal can be banked as a primary result rather than
   relegated to secondary. *(The prototype's CVaR p=0.004 is NOT bankable — it reverses under the zero-info
   placebo, p=0.0005; this elevation builds structure for the campaign, it does not retro-validate the
   prototype.)* No compute cost; pure pre-registration/labeling + a parallel conjunction in `h2_conjunction`.
   **User-approval amendment required** (touches the hypothesis set).

4. **[S2] Wire and unit-match the TOST equivalence test (§5.3).** Verify a TOST against the **per-seed IQM paired
   bootstrap** exists; if not, add it. State the margin in the **test statistic's units** (annualized Sharpe IQM)
   derived from the SESOI, or run TOST on validation-DSR to match the DSR-unit margin — but make units agree. A
   non-rejection without the TOST bound is not a bankable null.

5. **[S2] Re-run the power analysis against the realized test (§5.2).** `POWER_ANALYSIS.md`'s MDE uses a mean-based
   difference test; the headline uses the **IQM paired-seed bootstrap**. Re-run `power_analysis.py` with that
   statistic and the **pilot σ** (currently a 0.30 placeholder). Report the MDE of the test you actually run, and
   the IQM's effective-n≈15 trade-off.

6. **[S2] Add an explicit two-tier verdict to the report (§3.5, §7).** `h2_markdown` currently renders one
   conjunction verdict. Render **two**: H2-RA (Sharpe IUT) and H2-Tail (CVaR IUT + FZ0/ES). Never let the abstract
   claim a tail improvement off the Sharpe gate alone.

7. **[S2] Guard the EVT-vs-empirical estimator switch for the fed headline levels (§6.3).** Assert/log that
   CVaR-5% (and 1%) use a *consistent* estimator across all arms/seeds, so the fed signal's estimator is not
   silently arm-dependent.

8. **[S3] Add LIMITATIONS_REGISTER entry L15 — measurement-noise → content confound (§6.4).** State that the
   distributional arm is fed a higher-variance signal (EVT tail estimates), that this biases against H2 (good for a
   null, conservative for a positive), that the bundle mixes low-variance empirical stats (CVaR-10/25%,
   left_tail_mass) with the noisier EVT levels, and that the null is scoped to *this operationalization* of tail
   feedback. Report the `threshold_sensitivity` CV as the bounding exhibit.

9. **[S3] Retitle the construct from "the distribution" to "multi-level tail-risk feedback" (§2.1),** and state the
   Kusuoka/Acerbi/Artzner principled-spanning justification for the CVaR-profile choice in one paragraph. Pre-empts
   the easiest construct hit.

10. **[S3] State the CVaR sign convention and the wrong-sign (type-III) risk explicitly (§3.4),** citing Bauer
    (2025) — "higher/less-negative CVaR = safer = better," and that extreme-quantile tests can err in sign on short
    windows (which is why CVaR-1% never gates).

11. **[S3] Disclose the single-seed-winner-selection vs 30-seed-evaluation asymmetry (§4.4),** noting it adds
    selection noise (conservative, power-reducing), of the same family as the L14 buffer asymmetry.

12. **[S3] Add the Lo (2002) annualized-Sharpe caveat where the descriptive Sharpe is reported.** The code already
    notes it (`bootstrap.sharpe_ratio` docstring): the √252 scaling is biased under autocorrelation, but the
    **headline test is the per-seed paired bootstrap on the actual return series**, which never relies on the
    annualized scalar — so this is a reporting caveat, not a test flaw. Say exactly that.

---

## 9. Literature grounding (precise, with verification status)

**Established, safe to cite (substance reliable; verify year/venue):**
- **Eureka** — Ma, Liang, Wang, Huang, Bastani, Jayaraman, Zhu, Fan, Anandkumar, *Human-Level Reward Design via
  Coding Large Language Models*, arXiv:2310.12931, **ICLR 2024**. The loop, reward-reflection, evolutionary
  selection on a scalar fitness, and the "reflection > sampling-more" ablation. Note for §4.2: Eureka reflects on
  **best-so-far** and selects on a single scalar — your λ=0 + parallel-reflect-on-best (R24) is faithful; cite this
  to defend λ=0 as Eureka-faithful, not an oversight.
- **rliable** — Agarwal, Schwarzer, Castro, Courville, Bellemare, *Deep RL at the Edge of the Statistical
  Precipice*, **NeurIPS 2021** (oral). IQM, stratified bootstrap, probability of improvement, the **paired**
  bootstrap your `paired_seed_difference_test` implements. The web confirms the exact paired-IQM-centered-two-sided
  construction you use. This is your headline-inference citation.
- **Distributional RL line** — Bellemare–Dabney–Munos C51 (ICML 2017); Dabney et al. QR-DQN (AAAI 2018); Dabney,
  Ostrovski, Silver, Munos **IQN** (ICML 2018). Cite as the *ancestry* of the quantile machinery; be explicit that
  the headline does **not** use a distributional critic (off-critic measurement, audit A-1) — IQN/TQC are the
  *secondary* critic experiment.
- **Risk measures** — Artzner–Delbaen–Eber–Heath, *Coherent Measures of Risk* (Math. Finance 1999) → CVaR over
  VaR; Rockafellar–Uryasev (2000) CVaR optimization/tractability; **Acerbi (2002)** spectral + **Kusuoka (2001)**
  representation → the multi-level-CVaR-as-principled-tail-summary defense (§2.1).
- **Backtest inference** — Bailey & López de Prado, *The Deflated Sharpe Ratio* (J. Portfolio Mgmt 2014) +
  Probabilistic SR (2012); Bailey–Borwein–López de Prado–Zhu **PBO/CSCV** (2017) — your primary, trial-count-free
  guard; Harvey–Liu–Zhu (2016) t>3 (scoped to absolute-alpha only); Politis–Romano **stationary bootstrap (1994)**;
  Benjamini–Hochberg (1995); Romano–Wolf (2005) stepdown.
- **Forecast comparison / tail backtesting** — Fissler & Ziegel (2016), *Higher order elicitability and Osband's
  principle*, Ann. Statist. 44(4):1680–1707 (joint elicitability of (VaR, ES)); Nolde & Ziegel (2017),
  *Elicitability and backtesting*, Ann. Appl. Statist. 11(4):1833–1874 (the comparative ES backtest your
  `es_backtest` implements via FZ0). The web confirms the FZ0 0-homogeneous score and the DM-style construction.
- **Intersection–union testing (the §3 fix)** — Berger (1982) IUT; SenGupta P³ IUT; Brunner (2004)
  union-intersection comparisons; "When to Adjust Alpha During Multiple Testing," arXiv:2107.02947 — *the
  conjunction is the correction; legs need no further α-adjustment; IUT is conservative.* This is your authority for
  removing the BH-on-top double penalty.
- **GPD small-sample bias (the §6 caveat)** — analytic O(n⁻¹) bias correction (Giles/Feuerverger; ideas.repec.org
  vic0902); "Improved inference on risk measures for univariate extremes," arXiv:2007.10780; "Risk Analysis via
  GPD," tandfonline 2021 — *shape estimates highly variable on few exceedances; bias-corrected POT effective.*
  Pair with **Troop et al. (2021)** bias-corrected POT, which your PREREGISTRATION §4 names.
- **DM finite-sample size distortion (the §5 power note)** — Harvey–Leybourne–Newbold (1997) correction (oversized
  DM at small T; use t(T−1) + bias-corrected variance). Relevant because your FZ0/ES backtest is DM-style on a
  short OOS window; cite HLN and consider the small-sample correction or report it as a caveat.
- **RL / reward-design canon** — SAC (Haarnoja et al. 2018, fixed agent); TQC (Kuznetsov et al. ICML 2020,
  secondary critic); Singh–Sorg Optimal Reward; Ng–Harada–Russell (1999) potential-based shaping; Skalse et al.
  (NeurIPS 2022) reward hacking; Hadfield-Menell et al. inverse reward design (reward-design priors as object of
  study); DeMiguel–Garlappi–Uppal (2009) 1/N; Cont (2001) stylized facts (tail motivation).
- **Bauer (2025)**, arXiv:2505.23333 — low power / wrong-sign at extreme quantiles on short windows. Already cited
  in PREREGISTRATION §10; central to §3.4/§5.2/§6.

**Position-only — VERIFY before the PDF (your supervisor co-authored two corpus papers; a fabricated claim is
caught in the worst place):** EX-DRL (EVT-in-distributional-RL, the off-critic-tail-estimation analogue); Decision-
Language Model (Behari et al. 2024, NeurIPS) — the nearest neighbor (LLM writes reward + shown a distribution, but
the *object* is population-across-states, not the return tail); Qu et al. (2025) reward-code-evolution-in-fraud (why
you claim a first for a *trading* agent); Troop et al. (2021) bias-corrected POT (confirm it exists and matches what
you implement/promise). Mark each `% VERIFY` in `refs.bib`.

---

## 10. Threat-to-validity summary table

| Class | Threat | Where | Severity | Direction of bias | Action |
|---|---|---|---|---|---|
| Statistical | Conjunction × BH double-correction | §3.2 | **HIGH** | against H2 (under-powered) | #1 [S1] |
| Construct | Sharpe-gate tests the dimension distributional helps least; λ=0 selects on it | §4.2 | **HIGH** | against H2's mechanism | #3 [S1], reframe §7 |
| Construct | "Distribution" = 6 left-tail scalars (label > operationalization) | §2.1 | MODERATE | n/a (interpretation) | #9 [S3] |
| Construct | Measurement noise in fed EVT tail stats → can't cleanly read a null | §6.4 | MODERATE | against H2; weakens null interpretation | #8 [S3], #2 [S1] |
| Statistical | EVT/GPD MLE bias on few exceedances (headline CVaR-5% is EVT) | §6.2 | MODERATE | unsigned (estimator) | #2 [S1], #7 [S3] |
| Statistical | TOST margin in DSR units vs test in Sharpe units; TOST maybe unwired | §5.3 | MODERATE | blocks bankable-null upgrade | #4 [S2] |
| Statistical | Power analysis uses mean test, not the IQM bootstrap; σ placeholder | §5.2 | MODERATE | overstates power | #5 [S2] |
| Statistical | CVaR legs low-power (Bauer 2025); inflate BH thresholds in current code | §3.2/§5.2 | MODERATE | against Sharpe legs (via #1) | resolved by #1 |
| Internal | 1-seed winner selection vs 30-seed evaluation (selection noise) | §4.4 | LOW–MOD | against H2 (conservative) | #11 [S3] |
| Internal | EVT-vs-empirical estimator can switch for fed CVaR-5% across arms | §6.3 | LOW | unsigned (confound) | #7 [S3] |
| Construct | Anchoring scales with count-of-numbers (6 vs 1 vs 0) | §1.3 C-b | LOW–MOD | toward H2 | bounded by placebo; disclose |
| Internal | LLM stochasticity: contrast is population-vs-population | §1.3 C-d | MODERATE | unsigned | variance-decomp appendix; disclose |
| External | Single 2005-cohort universe; replay; rf=0; costs | L1/L3/L10 | LOW (common-mode) | common-mode (cannot make the contrast) | already in L-register |
| Reporting | Annualized Sharpe biased under autocorrelation (Lo 2002) | §8.12 | LOW | descriptive only | #12 [S3] |

**Bottom line.** H2 is a well-built, falsifiable, pre-registered hypothesis with an unusually clean feedback-channel
instrument and an inference stack (rliable per-seed IQM bootstrap, PBO-primary, frozen family, FZ0/ES) that exceeds
typical RL-finance rigor. The three high-severity issues are all *fixable before freeze* and all currently bias
**against** H2 — which is comfortable for a null but costs real power for a positive. The decisive moves are: (1)
remove the conjunction×BH double penalty (use a clean IUT), (3) elevate CVaR-5% to a co-primary tail hypothesis so
a **campaign** tail signal can be banked as a primary result *(the prototype's CVaR p=0.004 is NOT that signal —
it reverses under the zero-info placebo, p=0.0005; the elevation builds structure, it does not retro-bank the
prototype)*, and (7) reframe H2 as two co-primary claims (risk-adjusted + tail)
with the verbatim bankable-null statement in §7.2. Done, H2 is bulletproof in every outcome branch — reject, partial,
or null.

# PRE-REGISTRATION — frozen design record

**Status:** 🟡 PRE-FREEZE (as of 2026-07-01) — design content RATIFIED; awaiting pilots. The 2026-07-01 design
amendments — the **mechanism-headline + numeracy reframe (§2a)**, **λ=0 (§5)**, the **rf/cash numeraire (§10)**,
and the **serial-headline protocol (§6)** — are **RATIFIED** (user-delegated authority 2026-07-01) and mirrored in
`config/preregistration.yaml`. The freeze (`scripts/freeze.py`, which hashes this into `docs/DECISION_LOG.md`) is
now **fully determined**: the **σ_D pilot** has run and its result (σ_D = 0.369) is recorded in
**Amendment E1 (2026-07-10)**, which sets the winner seeds to the assurance-tier ladder and retires the
old "30 vs 50" rule — so every design parameter is FIXED/DECIDED and the pre-registration is freeze-ready.
**B\* is SET: 400,000 (R77, 2026-07-18 — raised from R74's 200,000 to the MEASURED KNEE by the pre-committed
extended-curve rule; R74's range-limited flatness finding stands as superseded-by-wider-measurement).** An **OPTIONAL** model-panel (ADR-039)
amendment remains (a secondary, budget-dependent generality probe — the headline is Opus-single). The freeze runs only on the user's explicit go. Until frozen, editable; after freeze, changes require an explicit,
dated **amendment** approved by the user. The machine-readable mirror is `config/preregistration.yaml` (the two
must agree; `freeze.py` checks).

**Why pre-register.** The headline H2 can return a null. Fixing the hypotheses, budgets, metrics, and
analysis plan *before* the campaign makes a null a credible finding about the question as posed, not a
moved goalpost. This document is the spine of that guarantee.

---

## 1. Hypotheses (frozen)
The unit of inference is **a reward function's out-of-sample risk-adjusted performance**, over the
test span, across seeds and the candidate population — NOT the cross-section of assets.

- **H1 — LLM vs hand-designed.** H0: median OOS risk-adjusted performance of LLM-designed rewards ≤
  the best hand-designed baseline (raw return; return−variance; return−CVaR; differential Sharpe).
  Reported **descriptive / report-only** (subordinate to the H2 headline): the best-of-4 baseline
  identity is selected on **validation where a validation fitness is archived; where it is not, the
  executed pipeline falls back to selection on the sealed leg and this is DISCLOSED as
  snooped-descriptive** (R49; the executed reality — `run_campaign._baseline_winner_record` archives
  baselines without a validation fitness, and CH4/CH7 carry the disclosure), the baselines are
  disclosed as un-tuned (L16; DEEP_H1), and "is the search worth it?" is routed to H4 — so the bare
  max-of-4 comparison carries no inferential multiple-comparison claim (R30). *(Sentence corrected
  2026-07-02: the previous text asserted unconditional validation-selection, which the pipeline does
  not deliver — the freeze must not hash a claim the code contradicts.)*
- **H2 — distributional vs scalar (HEADLINE).** Decided as **two co-primary intersection–union tests**
  (R25, 2026-06-25; DEEP_H2 §7.1), each over the distributional arm vs the three comparators, each
  supported iff **all three** of its legs reject **one-sided at α = 0.05** in the predicted direction
  (distributional strictly better) with **no further leg correction** (the conjunction *is* the
  correction — Berger 1982):
  > **H2-RA (risk-adjusted performance).** Feeding the reward-designer multi-level tail-risk statistics
  > (vs a scalar) yields rewards whose frozen winners achieve **higher out-of-sample risk-adjusted
  > performance (Sharpe IQM)** at matched compute — and this advantage is attributable to tail-shape
  > *information* (survives the length-matched **placebo** and the single-number **scalar_cvar5**
  > controls). Decided by a **3-leg intersection–union test on the Sharpe legs at α = 0.05** (no further
  > leg correction — the conjunction is the correction).
  >
  > **H2-Tail (tail outcome).** The same feedback yields rewards whose frozen winners achieve a
  > **less-severe realized left tail (higher CVaR-5%)** out-of-sample, again surviving placebo and
  > scalar_cvar5. Decided by a **parallel 3-leg IUT on the CVaR-5% legs**, corroborated by the
  > **FZ0/(VaR, ES) Diebold–Mariano comparative backtest** (Fissler–Ziegel 2016; Nolde–Ziegel 2017;
  > `es_backtest.comparative_es_backtest`) — reported, not gated.

  H0 (both): the distributional-feedback arm ≤ the scalar arm (and ≤ placebo, ≤ scalar_cvar5), OOS, at
  matched compute, on that family's metric. Reporting is a **two-tier verdict** (H2-RA and H2-Tail
  reported separately); the abstract never claims a tail improvement off the Sharpe gate alone.
- **H3 — iterative vs single-shot.** H0: multi-generation ≤ single-shot at matched candidate budget.
- **H4 — LLM vs uninformed search.** (a) vs random-search-over-code; (b) vs Bayesian-optimization-
  over-template. Two separate tests.
- **Secondary (not numbered) — distributional vs mean critic.** SAC (mean) vs TQC (quantile), same
  family. Reported separately from H2; run only if the Phase-0 TQC smoke is green.

### 1a. Pre-registered predictions (frozen BEFORE the sealed test — error-statistical severity + forking-paths commitment, R45/R61)
We state, in advance, the observable signature each mechanism condition must produce, so a result of
ANY sign is a CONFIRMED or REFUTED prediction, not a post-hoc measurement. The epistemic credit for a
null here rests on **Mayoian error-statistical severity** — licensed by the *frozen, deviation-free*
protocol (no sample-based deviations ⇒ no unknown Type-I inflation; Rubin 2025, Synthese) — plus
**garden-of-forking-paths avoidance** (Gelman & Loken 2014), and is *reported* via TOST equivalence
against the pre-registered SESOI (Lakens et al. 2018; Campbell & Gustafson 2018), NOT a bare p>0.05.
(R61: this supersedes the earlier "corroborated Popperian prediction" label — pre-registration does not
improve *Popperian* severity, Rubin 2025; the commitment below is unchanged, only its epistemic basis is
correctly named.) Selection is **λ = 0**
(tail-blind validation DSR), so the Sharpe legs carry no a-priori channel edge; the tail legs are
where the distributional channel can act.

| Mechanism condition | H2-RA (Sharpe IUT) | H2-Tail (CVaR-5% IUT) | Responsiveness (Spearman) | Reward-program differential | Pre-registered verdict |
|---|---|---|---|---|---|
| **Strict** — fed tail distribution shapes the reward code | tie (λ=0 ⇒ no Sharpe edge) | **dist > {scalar, placebo, scalar_cvar5} reject** | **> 0** | dist code references tail stats MORE than scalar/placebo | **H2-Tail supported, H2-RA not** |
| **Weak** — tail info helps but not robustly | tie | partial (≤ 2 legs reject) | ≈ 0 | weak/mixed differential | **inconclusive** (TOST-bounded) |
| **Null** — LLM not a Bayes-responsive user of the distribution | tie | tie (placebo not beaten) | **≤ 0** | no cross-arm code signature | **both null (clean, bankable)** |

**The specific a-priori prediction.** We predict a **tie on the Sharpe legs** (H2-RA not supported)
*regardless of channel* (λ=0 is tail-blind), and **separation on the CVaR-5% legs** (H2-Tail supported)
**iff** the fed tail distribution leaves a code-level signature (responsiveness > 0). The Sonnet
prototype is exploratory (no number enters the result), but its **negative responsiveness (≈ −0.05) and
un-beaten placebo predict the NULL branch** — a clean, bankable result the campaign will confirm or
refute. The **reward-program differential** (the per-arm code characterisation in `inspect_rewards`) is
the mechanism instrument that adjudicates which branch obtains, corroborated by `placebo_shuffled`.

## 2. The contribution axis (frozen framing; audit A-1)
The headline is the **feedback channel**. All feedback arms run the **same fixed agent (SB3 SAC)**.
The distributional feedback is **measured off-critic** from realized returns, so it does not depend on
the agent's critic.

## 2a. Mechanism-headline reframe (RATIFIED 2026-07-01 — the foregrounded research question)

> **Pre-freeze amendment (2026-07-01, RATIFIED — mechanism-headline reframe + report-only mechanism
> instruments; user-delegated authority, mirrored in `config/preregistration.yaml: mechanism`).** This amendment changes the **write-up headline and the
> foregrounded research question**, NOT the confirmatory test. The confirmatory hypotheses (§1, H1–H4), the
> seven arms (§3), the frozen tail-diagnostic set (§4), the λ = 0 selection (§5), the splits (§7), the
> **m = 6** testing family, the two co-primary IUTs (R25), and the SESOI/TOST (R12) are **ALL UNCHANGED**, as
> is the freeze hash's testing-family partition. What changes is the narrative spine: the dissertation is led
> by the **mechanism**, with the H2 performance result as its rigorous backdrop. Motivation: depth over
> breadth and an original, mechanism-level question are the dominant grade levers (Grade & examiner strategy),
> and the predicted H2 null is far more informative as *"where does the feedback channel break?"* than as a
> bare non-result.
>
> **Primary research question (RQ).** *Does showing an LLM reward-designer the **downside** — the
> realized-return left-tail distribution, rather than a scalar — change the reward-function **code** it
> writes, and does that change propagate to the trained agent's realized tail behaviour?* The object of study
> is the **three-link causal chain**
>
> > fed tail signal  —(SQ1)→  authored reward CODE  —(SQ2)→  trained policy  →  realized tail outcome
>
> (with surface-echo-vs-genuine-use and numeric legibility adjudicated by **SQ3**), and a null is reported as
> a result that **LOCATES where the chain breaks**, not an absence of evidence.
>
> **Sub-questions + pre-registered instruments (all report-only, DISJOINT from the m = 6 family).**
> - **SQ1 — responsiveness.** *Does the fed tail signal change the authored reward code?* Instruments: the
>   per-generation responsiveness statistic (Spearman of Δ(fed tail) vs Δ(authored-reward feature), bootstrap
>   CI; `src/inference/responsiveness.py`) **and** the reward-program differential (§1a; `inspect_rewards`).
>   Pre-registered direction: responsiveness **> 0** if the channel acts; the Sonnet prototype's *negative*
>   responsiveness predicts the break is **here**.
> - **SQ2 — transmission.** *Does the change in code propagate to the realized tail outcome?* Instrument: a
>   single-mediator decomposition of fed → code → outcome (indirect effect a·b with a percentile bootstrap CI;
>   `src/inference/mediation.py`). Registered consequence: if SQ1 is null (path a ≈ 0) then a·b ≈ 0 for **any**
>   downstream link — the chain is severed at the first hop, the predicted outcome.
> - **SQ3 — specificity / genuine use.** *Is any effect genuine use of the tail **content** or a surface echo,
>   and is a failure a **numeric-legibility** bottleneck?* Instruments: the AST-structural named-vs-blinded test
>   (`src/inference/contamination.named_vs_blinded_structural` — identifier-invariant program structure, so a
>   placebo that echoes tail *tokens* yet writes a different *program* is caught) **and** the legible-format
>   responsiveness differential (`responsiveness.legible_format_responsiveness_differential`).
>
> **Registered numeracy-bottleneck hypothesis (falsifiable).** We pre-register, before the sealed leg, that
> any SQ1 failure is **in part a numeric-legibility bottleneck** — frontier LLMs compare close small floats at
> ~50–70% accuracy (arXiv:2602.07812; NUMCoT, arXiv:2406.02864), and the fed CVaR values (e.g. −0.0577 vs a
> sibling reward's −0.0582) sit in that failure regime — **not** evidence that tail information is useless. The
> **legible-format ablation** (the identical tail content re-rendered legibly — basis points / rank framing)
> tests it: a positive, CI-separated legible-minus-raw responsiveness differential **confirms** the bottleneck
> (a concrete scaling/legibility lever and a contribution in its own right); a null **refutes** it. This is a
> falsifiable hypothesis with a registered decision rule, not a post-hoc rationalisation.
>
> **Micro-anchors (pre-freeze addendum, 2026-07-02 — declared ex-ante so the write-up's sharpened analyses
> are REGISTERED, not post-hoc).**
> - **(a) SQ3b adjudicates two named rival accounts.** The legible-format ablation discriminates between the
>   **READOUT account** — the numeric content is *encoded but not reliably verbalized/used* (probing studies
>   find >90% internal discriminability against 50–70% verbal comparison accuracy; arXiv:2602.07812), which
>   predicts the legible re-rendering **recovers** responsiveness (positive differential) — and the
>   **EXECUTION account** — the failure is in *executing* multi-step numeric comparison regardless of format
>   (arXiv:2507.10624), which predicts the re-rendering does **not** help (null differential). Either outcome
>   is informative and names its winner ex-ante.
> - **(b) Declared-exploratory distance moderator (report-only, outside every confirmatory family).** Within
>   the CVaR-fed arms only: per-generation designer responsiveness regressed on the **numeric distance**
>   between consecutively fed CVaR values (controlling magnitude, iteration index, and fitness-plateau state).
>   The numeracy account predicts responsiveness rises with numeric distance (a psychophysics-style distance
>   effect); declared EXPLORATORY — no confirmatory weight, reported with CIs.
> - **(c) Severity summary.** The write-up's summary of the headline TOST result will include a **post-data
>   severity assessment** (severity curve at the SESOI per co-primary leg, Mayo–Spanos) as the planned
>   presentation of how severely the null passed — registered here so the presentation choice is ex-ante.
> - **(d) Information-utilization gap (report-only, archive-computed; NEW instrument).** A null invites the
>   objection *"the fed tail carried no information beyond the scalar anyway."* We pre-register its direct
>   measurement: on the ACTUAL fed feedback sequences archived per generation, the **redundancy of the
>   multi-level tail vector given the scalar** (per-component R²/rank-correlation of the six tail components
>   on the concurrently fed scalar summary, pooled over generations; the `placebo_shuffled` arm — whose
>   vector's information is destroyed by construction — serves as the calibration floor). The complement
>   (1 − redundancy) is the **fed-but-unusable-by-a-scalar information**; contrasted with the SQ1
>   responsiveness estimate it yields the **information-utilization gap**: how much extra signal the
>   designer was GIVEN vs how much its code USED. Registered direction under the numeracy hypothesis:
>   substantial non-redundant information, near-zero utilization.
> - **(e) Validation-headroom (oracle-selection) bound (report-only, archive-computed; NEW instrument).** A
>   null equally invites *"perhaps no better reward existed to find."* We pre-register the direct check: from
>   the archived per-candidate validation returns (every candidate, every arm), the **oracle-selection
>   frontier** — the best achievable validation CVaR-5% (and DSR) over ALL authored candidates, per arm and
>   pooled — against what each arm's frozen selection achieved. A material frontier-minus-achieved gap
>   establishes that headroom EXISTED in the authored search space; combined with (d) and SQ1 this completes
>   the quantitative localisation of the break (information present → headroom present → designer
>   unresponsive). VALIDATION data only (the sealed test leg is never used for this bound; a winners-only
>   test-leg analogue may be reported as an appendix caveat since only winners have test scores).
> - **(f) The MECHANISM FINGERPRINT — five rival accounts × the instrument suite, signatures registered
>   ex-ante (report-only interpretation scaffolding; no gate, no multiplicity claim; A5 added by
>   Amendment R76, 2026-07-11, pre-freeze and pre-data).** A SQ1-null admits
>   five nameable rival explanations. We register each account's PREDICTED SIGNATURE across the instruments,
>   so the observed pattern SCORES the accounts against one another rather than testing them piecemeal:
>
> | Instrument | A1 GENUINE-USE (channel works) | A2 READOUT / numeric illegibility (arXiv:2602.07812) | A3 EXECUTION failure (arXiv:2507.10624) | A4 PRIOR-DOMINANCE (objective prior overrides all feedback) | A5 RATIONAL INSENSITIVITY (small deltas discounted as noise — R76) |
> |---|---|---|---|---|---|
> | SQ1 responsiveness (tail arms) | **> 0** | ≈ 0 (raw) | ≈ 0 | ≈ 0 | ≈ 0 (raw, un-annotated) |
> | Scalar-arm responsiveness (same statistic, its own fed scalar) | > 0 | **> 0** (scalar is legible) | ≈ 0 | **≈ 0** (ignores ALL feedback) | > 0 on clearly-resolvable changes |
> | SQ3b legible-format differential (format-only re-rendering: bp / ranks) | ≈ 0 (already used) | **> 0** (the key discriminator) | **≈ 0** (format cannot fix execution) | ≈ 0 | **≈ 0** (salience does not convey significance) |
> | CI-/significance-annotated re-rendering (D2+ (iv), Stage-2 adjudicator) | ≈ 0 | ≈ 0 beyond format-only | ≈ 0 | ≈ 0 | **> 0** (the A5-vs-A2 discriminator: responds once told which deltas are signal) |
> | Distance moderator (b) | ≈ 0 | **> 0** (psychophysics distance effect) | weak/≈ 0 | ≈ 0 | > 0 (confounded with A2 — adjudicated by the CI-annotated row) |
> | Information-utilization gap (d) | small | large | large | large | large on sub-noise deltas, smaller on resolvable ones |
> | Fed-delta SNR conditioning (h) | use regardless of SNR | non-use regardless of SNR | non-use regardless of SNR | non-use regardless of SNR | **use CONCENTRATED on high-SNR deltas** |
> | Reward-program diversity (taxonomy concentration) | responsive/diverse | moderate | moderate | **templated/concentrated** | moderate |
>
>   The discriminating cells are bolded: A2-vs-A3 is decided by the legible-format differential; A4 is
>   uniquely identified by the SCALAR arm's own responsiveness (computable from the same archived records
>   with the same SQ1 statistic — registered here as an instrument application, not a new hypothesis) joint
>   with taxonomy concentration; A1 is identified by SQ1 itself. Mixtures are expected and will be reported
>   as the observed pattern's distance to each registered signature — never forced into a single account.
>   To our knowledge no prior study of LLM agents registers a multi-account × multi-instrument fingerprint
>   ex-ante; this converts the instrument suite into a theory-adjudication matrix and is registered
>   PRE-FREEZE so the adjudication is a design property, not a post-hoc narrative. (A4 has an independent
>   empirical anchor: LLMs carry measurable risk-preference profiles (Hartley et al., ACL 2025) — a
>   designer whose prior risk attitude dominates fed evidence is a live, literature-grounded account, not a
>   straw man.)
>
>   **A5 — RATIONAL INSENSITIVITY (added by Amendment R76, 2026-07-11; pre-freeze, pre-data).** The fed
>   block carries point estimates with NO uncertainty annotation (the R61 `cvar_ci` machinery exists but
>   the fed block is deliberately not CI-enriched — arms-parity choice). A designer — numerate or not —
>   that treats small decimal differences as probable estimation noise and declines to act on them is
>   therefore behaving *defensibly*, not failing: an SQ1-null under A5 is an epistemic-stance result, not
>   a numeracy deficit. This is a materially different scientific conclusion from A2/A3, which is why it
>   must be named ex-ante. Quantitative anchor (measured 2026-07-11 on the univ5 train window,
>   equal-weight top-30 proxy, stationary-block bootstrap): the MARGINAL sampling SE of a fed CVaR-5%
>   level is ≈ 0.0033, but candidate DIFFERENCES are paired on the common market path, so the paired
>   diff-SE is ≈ 1e-4 (sibling-close books) to ≈ 8e-4 (structurally different books) — i.e. typical fed
>   deltas of a few × 1e-4 range from clearly-resolvable signal (vs the sibling floor) to borderline
>   (vs the distant floor). A5 is adjudicated against A2 by the **CI-/significance-annotated
>   re-rendering** (D2+ (iv), Stage-2): under A5 responsiveness rises when significance is annotated
>   (format-only re-rendering does nothing); under A2 format-only re-rendering already helps. The M2
>   cross-LLM numeracy survey (Stage-2) separates ability from stance: A2 predicts low raw
>   discrimination accuracy, A5 predicts adequate accuracy that goes unused absent significance
>   information.
> - **(g) Reflection-funnel content analysis (report-only, archive-only; declared exploratory).** The
>   archive stores every reflection the designer writes. We register a staged FUNNEL coding of the tail-fed
>   arms' reflections — for each generation: (i) **QUOTE** — does the text reference the fed tail values at
>   all; (ii) **COMPARE** — does it compare them across candidates/levels (the numeracy-critical step);
>   (iii) **CONCLUDE** — does it draw an explicit design implication from the comparison; (iv) **IMPLEMENT**
>   — does the authored code change realise that implication (cross-checked against the SQ1 code-feature
>   deltas). Reported as per-stage pass rates with the funnel's drop-off location — the qualitative twin of
>   the fingerprint (f): the accounts predict DIFFERENT drop-off stages (A2 readout → falls at COMPARE;
>   A3 execution → falls at COMPARE/CONCLUDE despite quoting; A4 prior-dominance → often falls at QUOTE, or
>   CONCLUDEs generically without using the numbers; A1 genuine-use → survives to IMPLEMENT). Coding
>   protocol: two independent coders (one LLM-assisted with a frozen rubric prompt + one human-checked
>   sample ≥ 20%), inter-coder agreement reported (Cohen's κ); all reflections of the tail-fed arms coded
>   (≈ generations × candidates, bounded); declared EXPLORATORY, outside every confirmatory family. To our
>   knowledge the first staged content analysis of an LLM reward-designer's verbalized reasoning.
> - **(h) Fed-delta SNR + responsiveness-attenuation exhibit (report-only, archive-computed; added by
>   Amendment R76, 2026-07-11 — pre-freeze, pre-data).** The SQ1 responsiveness statistic correlates
>   Δ(fed tail) with Δ(authored-code feature); if part of the fed deltas is estimation noise, the
>   estimate suffers errors-in-variables ATTENUATION toward 0 — a statistical objection that must be
>   quantified, not waved at. From the archived per-generation fed vectors and train-window returns
>   (no new data; the R61 `cvar_ci`/stationary-block machinery): (i) the distribution of |Δ fed
>   component| across consecutive candidates per arm-chain against the PAIRED block-bootstrap SE of
>   that difference (paired on the common market path — the common-path design makes fed differences
>   far better determined than their marginal CIs suggest, and this exhibit shows exactly how much);
>   (ii) the **resolvable-signal share** = fraction of fed deltas exceeding 2× their paired SE;
>   (iii) an errors-in-variables attenuation factor λ_att = Var(signal)/(Var(signal)+Var(noise)) with
>   a disattenuated SQ1 responsiveness reported as a SENSITIVITY (never replacing the primary
>   statistic); (iv) responsiveness computed separately on the high-SNR vs sub-noise delta subsets —
>   the A5 fingerprint row. Registered directions: under A1 the primary SQ1 is > 0 and attenuation
>   is immaterial; under A2/A3/A4 responsiveness ≈ 0 on BOTH SNR subsets; under A5 it concentrates
>   on the high-SNR subset. Declared report-only, outside every confirmatory family; VALIDATION/train
>   data only.
>
> **Robustness to the σ_D pilot (a deliberate design property).** The mechanism headline is **independent of
> whether H2 lands as equivalence (σ_D small) or non-rejection (σ_D larger)**: in both cases the SQ1–SQ3
> instruments locate the break in the chain. The performance result (§1/§10) sets only HOW TIGHT the
> equivalence statement can be (the TOST CI against the ±0.05 SESOI); it does not determine the thesis. This
> intentionally decouples the dissertation's headline from the one genuinely uncertain pilot outcome.
>
> **Honesty (registered limitations).** (i) The decomposition is **observational/associational**: the fed tail
> is **endogenous** (the trained policy's own realized returns; §2), so SQ2's mediation has a causal reading
> only under sequential ignorability (Imai, Keele & Tingley 2010) — reported as a descriptive mechanism
> decomposition, never a causal proof. (ii) At the tier-0 floor (n = 30) some sub-tests (e.g. the
> named-vs-blinded equivalence) are underpowered; the dedicated, cheap A/B sub-experiments run more seeds than that floor, and
> effect sizes + CIs + achieved power are reported, never a bare non-rejection. (iii) Search width K = 5 and
> the single Claude model family bound the generality of any mechanism claim; the multi-model panel (ADR-039)
> is the registered generality probe.
>
> **Machine-readable mirror.** A report-only `mechanism:` block (RQ; `sub_questions.{sq1,sq2,sq3}` with their
> instruments + pre-registered directions; the `numeracy_bottleneck` hypothesis + its ablation decision rule;
> `report_only: true`; `disjoint_from_m6: true`) is added to `config/preregistration.yaml` **at ratification**;
> it carries no member of the frozen testing family. **No other frozen quantity changes.**

## 3. The seven arms (matched compute)
`distributional` · `scalar` · `placebo` · `scalar_cvar5` · `placebo_shuffled` (R32, the
structure-vs-content control — the distributional block with its six tail values candidate-seeded-
deranged) · `random_search` (H4a, over code) · `bayes_opt` (H4b, over a fixed parametric template).
All consume the **same candidate budget** — the property that licenses the comparative claim. The
**m = 6 testing family** is fed by only {`distributional`, `scalar`, `placebo`, `scalar_cvar5`};
`placebo_shuffled` is a **DISJOINT** secondary control (`out["h2_structure"]`), never in the frozen
m = 6 (V1 reconcile 2026-06-26 — the seventh arm had been dropped from the frozen roster).

## 4. The frozen tail-diagnostic set (audit B-1, B-2, B-7)
Measured on the **training-period** realized portfolio log-returns (measuring on validation while also
*selecting* on validation would re-introduce overfitting). Estimator: **empirical primary** for the
body (CVaR/quantiles/left-tail-mass/robust-skew); **GPD/EVT tail fit** for the extreme levels.
- `cvar_25`, `cvar_10` — empirical (headline-estimable)
- `cvar_05`, `cvar_01` — EVT/GPD peaks-over-threshold, fitted by **plain maximum likelihood**
  (`scipy.stats.genpareto.fit`; McNeil–Frey–Embrechts 2005 §7.2.3 POT, no small-sample bias correction).
  A **threshold-sensitivity diagnostic** (`ReturnDistribution.threshold_sensitivity`) is implemented and
  reported as the fed-signal stability exhibit. The **bias-corrected POT of Troop, Godin & Yu (2021,
  arXiv:2103.05059) is NOT implemented — documented as FUTURE WORK** (R27): its second-order
  regular-variation correction is built for heavy tails (ξ > 0) at large samples (n ∈ [5e3, 5e4],
  α ∈ {0.998, 0.999}); in the measured regime (n ≈ 750, α ∈ {0.05, 0.01}, ~75 exceedances) the GPD-MLE
  error is variance-dominated (measured CVaR bias ≈ −0.1% at 5%, +0.9% at 1%) and the correction is
  ill-conditioned at this sample size — Troop's second-order ρ and A(n/k) estimators carry the GPD shape estimate in the denominator and are consistent only in the heavy-tail, large-sample regime the authors validate. (The GPD-MLE shape estimate landing ≤ 0 in ~94% of n ≈ 750 draws is a SMALL-SAMPLE NEGATIVE-BIAS fact — the GPD-MLE systematically UNDER-estimates the shape at n ≈ 750 with ~75 exceedances (DEEP_H2 §6.2), so the shape estimate is CENTERED ≤ 0 by that bias, and with an asymptotic shape SE ≈ (1+ξ)/√k ≈ 0.14 at ~75 exceedances it lands ≤ 0 in the great majority of draws even for a genuinely heavy tail — NOT a claim that portfolio losses are light-tailed: diversifying regularly-varying constituents preserves the tail INDEX, so the underlying loss tail stays genuinely heavy (only its scale shrinks).) So the correction would not reduce RMSE here, regardless of the true tail-index sign. CVaR-1%
  **retained but flagged high-variance** — measured at n ≈ 750 (the pre-Split-C fed window, ~7–8
  exceedances); the executed Split-C fed window is the full train rollout ≈ 2,961 sessions ⇒ ~296
  exceedances at threshold_q=0.10 and ~30 cvar_01 tail points — direction unchanged, the estimator
  strictly better-fed. See `docs/DEEP_H2.md` §6.2/§6.4.
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

> **Pre-freeze amendment (2026-06-24, RATIFIED 2026-07-01 — λ formalization).** The frozen `lambda_cvar` is set to
> **0.0** (`config/preregistration.yaml: fitness.lambda_cvar`; executed via the `held_out_fitness` default
> `lam=0.0` — no config term is threaded into the selection hot path): selection is **pure validation Deflated
> Sharpe** with NO CVaR penalty, and the planned `lambda_grid` / `calibration_fold` scaffolding — INERT,
> read by NO live code, specified but never calibrated (`lambda_frozen: null`) — was DELETED 2026-07-02,
> executing this instruction (`config/inference.yaml:43-45` records the deletion). RATIONALE: the H2 contribution is the
> FEEDBACK CHANNEL — multi-level tail-risk feedback (six left-tail scalars — the lower tail, NOT the full distribution; R53) is fed to the reward-DESIGNER (shaping the authored
> reward code the agent then optimizes), NOT a tail term bolted onto the selection criterion. A
> reward-independent, tail-blind DSR selection keeps the arms' selection identical and un-reward-hackable;
> the tail OUTCOME is measured downstream on the sealed test leg (the CVaR-difference test + the
> FZ0/(VaR,ES) elicitable backtest, §10). This formalizes the existing default; it was **RATIFIED 2026-07-01**
> (user-delegated authority; the rejected alternative — a pre-2015-calibrated λ>0 that
> rewards tail-aware winners at selection — is recorded here). No other frozen quantity changes.

## 6. Loop protocol (frozen; audit B-3, B-5)
The reward-design loop runs **once** with a **fixed per-candidate training-step budget**.
CPCV is applied to the **fixed winners afterward** for inference — NOT inside each fold (that would be
~16× the compute). Single-shot arm (H3) draws the whole budget in one generation.

> **Amendment D2 (2026-06-19, user-approved) — winner seed count 5→30.** The per-arm WINNER seed count is
> raised from 5 to ≥20 (target **30**) for the H2 IQM/CI (Henderson 2018; Colas et al. ≥20). Matched compute
> is unchanged — the SEARCH budget is untouched: each candidate is trained at **1 seed during search**; only
> the per-arm **winners** are re-run at **30 seeds** (the "seeds-on-winners" lever, ADR-023). Candidate
> budget, fitness, λ, splits, and hypotheses are unchanged. See §12 and the amendment record;
> at D2 `config/preregistration.yaml: seeds` was `0–29` (n=30) — **superseded by Amendment E1 (2026-07-10),
> below**, which raises the winner seeds to the assurance-tier ladder.

> **Amendment E1 (2026-07-10, supervisor-approved) — winner seed count → the assurance-tier ladder.**
> The σ_D pilot has now run (`scripts/sigma_seed_pilot.py`): across 15 CRN seed-pairs the difference
> standard deviation is **σ_D = 0.369** (σ_seed = 0.244, ρ = −0.141, not significant), which **fires the
> pre-registered σ_D > 0.10 trigger**. The old rule ("30 → 50 seeds if σ_D > 0.10") is therefore
> **retired**: 50 seeds cannot bring the Sharpe-leg equivalence interval inside the SESOI = 0.05 when
> σ_D = 0.369, so the fixed "50" is unattainable and is replaced by a variance-anchored **assurance
> ladder**. The per-arm WINNER seed count becomes the tiered schema
> `seeds: {mode: tiered, tiers: [30, 100, 189, 279, 340, 403, 568]}`, resolving to the flat set
> **[0..567]** — a **headline seed count 568**. The tiers are cumulative and order-only (CRN pairing
> preserved; each tier a COMPLETE study), and each rung has a pre-registered meaning:
> **30** = the distinction-bankable core (H2 + mechanism + H1 + H3 all complete; the CVaR-5% co-primary
> leg — σ_D = 0.0015, ρ = +0.47 — is already conclusive here); **100** = the σ-precision insurance rung
> (the σ_D estimate itself tightens to ≈ ±10%, so the seed-noise-dominance finding becomes precise);
> **189** = the Monte-Carlo point-estimate power rung (the Sharpe-leg TOST is decisive if σ_D is as
> measured; naive-normal analogue ≈ 147); **279 / 340 / 403 / 568** = 80% / 90% / **95% (the primary
> target)** / 99% equivalence assurance, powering the SESOI at the χ²-upper confidence bound on σ_D
> (`power_analysis.ASSURANCE_TIER_BOUNDS`). Because a truncated run falls back to the largest COMPLETED
> rung, the rung spacing also caps the worst-case number of completed-but-unusable seeds — the
> insurance rationale for the intermediate rungs. The STOPPING tier is determined **EXOGENOUSLY** by
> measured Myriad throughput against the 1 Sep deadline, **never by inspecting results** — an exogenous
> truncation that preserves the single confirmatory look. SEARCH budget, matched compute, candidate
> budget, fitness, λ, splits, arms, and hypotheses are all unchanged. See §12 and the amendment record.

> **Pre-freeze amendment (2026-06-24) — optional reflect-on-BEST parallel SEARCH + matched 50k buffer.**
> A parallel SEARCH scheduler (`scripts/run_campaign.py --search-gpu N`, default **0 = serial**) is now
> AVAILABLE for the development-split search: it trains candidates within a generation (and across arms)
> concurrently and seeds the next generation's reflection from that generation's **BEST** candidate, whereas
> the serial loop (`src/llm/loop.py`) seeds from its **LAST**. This changes the reflection prompt SEQUENCE —
> a frozen-decision item — so the serial-vs-parallel-search choice is RECORDED at freeze time and is NOT
> silently switched (the default stays the serial reflect-on-last path the prototype de-risked). Everything
> else is matched (same panel / windows / candidate budget / fixed agent / Opus author / fitness);
> reflect-on-best is the more Eureka-faithful protocol (Eureka reflects on best-so-far) and is ~4× faster on
> the search half. SECONDARY FIX folded in: the parallel worker couples `buffer_size == train_steps` (50k),
> so parallel SEARCH trains the fixed agent at the SAME replay budget as the TEST leg — resolving the
> documented serial-search 25k-buffer skew (the serial `run_arm` builds its buffer from prototype.yaml's
> pinned 25k). Reproducibility is preserved (replay-from-archive; the parallel archive writes the same
> `val_fitness`/`val_returns` schema `select_winner` reads). Built + unit-tested 2026-06-24
> (`tests/test_run_campaign.py`); CHANGELOG 2026-06-24.
>
> **R24 (2026-06-25) — headline RECORDED = parallel reflect-on-best.** The R21 "recorded at freeze" choice
> is now MADE: the parallel best-of-generation path is the **headline** search protocol (`--search-gpu 2`
> on the laptop; matched 50k buffer), because it resolves the L14 25k/50k buffer asymmetry the serial
> default otherwise ships, is Eureka-faithful (reflection on best-so-far), and ~halves the laptop run (more
> write-up time — the dominant no-viva grade lever). Serial reflect-on-last is RETAINED as the
> de-risked fallback (`--search-gpu 0`); the parallel run is GATED on a GREEN single-arm 50k GPU-smoke
> (RAM/thermal). `config/preregistration.yaml: search.headline_reflect_protocol = parallel_reflect_on_best`.

> **Pre-freeze amendment (2026-07-01, RATIFIED — headline search protocol REVERTED to SERIAL reflect-on-last;
> supersedes R24; user-delegated authority, mirrored in `config/preregistration.yaml: search.headline_reflect_protocol`).** The headline search protocol is set to the **SERIAL
> reflect-on-LAST** path (`--search-gpu 0`, the default), superseding R24's parallel reflect-on-best. RATIONALE
> — two of R24's three rationales have dissolved, and a reliability argument decides it: **(i) Speed is moot** —
> ADR-040 established that the 1-Sep deadline comfortably accommodates the longer serial laptop run, so R24's
> "~halves the run" benefit is no longer needed. **(ii) The buffer asymmetry is resolved on BOTH paths** — the
> campaign config pins `buffer_size = 50k` and the serial trainer and the parallel worker both clamp to it
> (verified 2026-07-01), so R24's "serial ships a 25k/50k skew" was a prototype-config artefact, not a campaign
> one. **(iii) Reliability of the unattended run** — the serial path is the one the Sonnet prototype validated
> END-TO-END; for a ~2–3 week UNATTENDED, auto-restarting laptop campaign its far smaller concurrency surface
> (no `DevicePool`/thread/future orchestration) is the lower-risk choice, and **reproducibility is now EQUAL on
> both paths** because the parallel resume cache was added 2026-07-01 (so parallel is no longer the only
> resume-safe path — that advantage is gone). The ONE cost — reflect-on-LAST is a minor deviation from Eureka's
> reflect-on-best — is handled by **honest disclosure in METHODS** (the reflection seed is the generation's last
> accepted candidate, not its best) and by RETAINING the **parallel reflect-on-best path as a documented,
> now-resume-safe robustness variant** (`--search-gpu 2`). Everything else is matched (panel / windows /
> candidate budget / fixed agent / Opus author / fitness / λ / splits). Mirror at ratification:
> `config/preregistration.yaml: search.headline_reflect_protocol = serial_reflect_on_last`. No other frozen
> quantity changes. (The code comment `parallel.py:632` "the headline campaign uses the SERIAL path" is now the
> ratified intent, resolving the R24-vs-code inconsistency.)
>
> **CORRECTION (2026-07-02, pre-freeze; code-verified).** The paragraph above rests on a STALE premise: the
> serial path no longer reflects on the LAST candidate — the earlier **R32/M5 amendment had already upgraded
> the serial loop to reflect on the generation's BEST** (verified at `src/llm/loop.py:604-615`: "the
> generation's BEST candidate seeds the next prompt (M5 reflect-on-best — Eureka-faithful)"), and CH4 §4.5
> already describes reflect-on-best. The RATIFIED DECISION — **SERIAL execution** for unattended-run
> reliability, with parallel retained as robustness variant — is UNCHANGED. What is corrected is the protocol
> LABEL: the headline is **serial reflect-on-BEST**, i.e. Eureka-faithful, and the "one cost / reflect-on-last
> deviation" disclosure above is hereby DISSOLVED (there is no deviation to disclose). Mirror updated:
> `config/preregistration.yaml: search.{reflect_protocol_default, headline_reflect_protocol} =
> serial_reflect_on_best`. Found by the 2026-07-02 pre-freeze audit; freezing the uncorrected text would have
> hashed a protocol description the campaign does not execute.

## 7. Data (frozen; audit B-2, C-3)

> **★ SPLIT-C + univ5 AMENDMENT (ADR-044 ratified 2026-07-01; EXECUTED 2026-07-02 with ADR-051 — a
> PRE-FREEZE design choice, never results-contingent).** The panel is extended to the **settled
> 2026-06-30 cutoff** and rebuilt as **`univ5` (5,406 sessions × 963 names, 2005-01-03→2026-06-30)**,
> the new **frozen headline panel**. Integrity: the 2005–2025 overlap of `univ5` vs the frozen `univ3`
> is **byte-identical (0 changed cells, verified `scripts/verify_gold.py` 2026-07-02)** — only 123
> 2026-H1 sessions and 10 new-member columns are appended; the frozen membership record remains
> authoritative for its own span (a vendor event-history revision detected on first re-contact —
> `EVHC.N^L16`, externally verified immaterial: never top-30 — is allowlisted and disclosed, ADR-051
> addendum). **Delisting upgrade:** the OBSERVED-terminal recovery (DATA_REPULL_DELISTING.md decided
> route) recovered the realised terminal return for **all 333 dead names** (`vendor_terminal_kept: 333`,
> **zero surcharges booked**) — the corrected Shumway panel (`univ5s`) is therefore byte-identical to
> the zero-fill headline on returns, demonstrating that `univ4`'s un-gated −30/−55% surcharge was
> **double-counting terminals already present in the vendor series** on top of its M&A contamination.
> The R39/R44 narrative below is retained as the amendment trail; the delisting sensitivity band remains
> reported, with `univ4` as its disclosed contaminated heavy end.

Point-in-time, survivorship-free US large-cap equities, **2005–2026-06-30 (21.5 years — not a scoping
lever)**; top-30 by PIT market cap; delisting returns retained; two-vendor reconciled; SHA-256 frozen.
The **headline data panel is `univ5`** (ADR-044/051, extending R44's `univ3` conventions): the **zero-fill**
(`liquidate_to_cash`) build — a dead name's post-event return booked 0.0 — which **understates** rather
than **invents** the delisting tail, the honest conservative choice on the data-fabrication axis. `univ4`
is the survivorship-corrected alternative that books **Shumway** delisting returns (−30% NYSE/AMEX, −55%
NASDAQ; Shumway 1997 JF, Shumway & Warther 1999 JF) onto each dead name's last valid session — the **same
953-name universe / 5283×953 shape** as `univ3`, differing only in the **333 delisting cells** — but its
surcharge is un-gated (R39 below), so `univ4` is the **heavy end** of the reported delisting-return
sensitivity band (`analyze_campaign.delisting_band`), not the headline; `univ3` anchors the band's **0%
end**. **R39
correction:** `univ4`'s −30/−55% surcharge hits **all** 333 delistings incl. premium M&A (no reason field
on disk), so it is the band's **M&A-contaminated heavy end**, NOT the true tail — the **delisting band is
the headline tail instrument** (the d∈{0,−30,−55,−100%} sweep moves CVaR-5% only ~2% — measured
pre-Split-C on the 2018–2025 window, re-derived at analyze time on the executed window — so the H2 tail
ordering is invariant), and the **reason-gated `univ4r` (a brief documented re-pull) is the correct panel**
(`docs/DATA_REPULL_DELISTING.md`; recommended, optional for H2 — SUPERSEDED 2026-07-02: the correction was
EXECUTED as `univ5s` via observed-terminal recovery, ADR-051, which found the vendor series already books
every dead name's realised terminal — 333/333 `vendor_terminal_kept`, ZERO surcharges — so `univ5s ≡ univ5`
byte-identically and `univ4`'s flat surcharge was terminal DOUBLE-COUNTING on top of its M&A contamination).
The loader's live default is **`univ5`**, which is ALSO the **FROZEN headline panel (R73, 2026-07-02,
extending R44's zero-fill conventions)** — zero-fill, NO fabricated losses — so the campaign runs on it with
NO `LLM_RP_GOLD_SUFFIX` override; `univ4` (which fabricates M&A losses on 100% of delistings, R39) is the
band's heavy END, not the headline (the band is computed on the univ3/univ4-era overlap through 2025-12,
where `univ5` and `univ3` are byte-identical).
Splits (**SPLIT C**, ADR-044): **train 2005–2016** (agent learns + feedback measured), **val 2017–2019**
(selection), **test 2020–2026-06-30** (untouched until final inference — the post-COVID-crash recovery and
elevated-vol regime [the 19 Feb–23 Mar 2020 crash itself falls INSIDE the test-boundary purge, so the
scored sealed-test outcomes begin post-crash, ~2020-03-30; §4.2], the 2022 hiking cycle,
the 2023–25 AI rally, and settled H1-2026); an inter-split **purge of
max(embargo=21, lookback=60) = 60 trading sessions** at each boundary (R18 — the purge must cover the
60-day feature lookback, not merely the 21-day embargo, so no observation's feature window crosses a
split; López de Prado 2018). Data is licensed and **not redistributable** — ship checksums + pipeline
+ a synthetic panel of identical shape.

## 8. Contamination protocol (N3)
Structural blinding (anonymised arrays, no tickers/dates) · cutoff-stratified evaluation around the
model's training cutoff · one open-weights second model with a different cutoff · explicit statement
that reward-design contamination ≠ forecasting contamination; reward-design priors are the **object of
study** (H4), not a defended weakness.

> **Open-weights second-model status (V10, 2026-06-26 — disclosure; PIN EXECUTED 2026-07-02).** The
> open-weights cross-model leg specifies a commit-pinned, different-cutoff second model
> (`open_weights_check_model`). **As of 2026-07-02 the pin is set: `qwen/qwen3-coder` via OpenRouter**
> (R71 follow-through; provider wiring + key-gated smoke test built and verified; the exact SERVED
> snapshot string is recorded in the archive at first live call — the reproducibility anchor). Until the
> secondary panel RUNS, `cross_model_disagreement` still returns `no_data` (`executed: False`) and the
> HEADLINE remains the **single Claude model family** (Sonnet 4.6 → Opus 4.8, same vendor + API key) —
> any plural "LLMs"/"models" reference to the authored rewards denotes that single family until the
> secondary Qwen panel is executed (report-only, never confirmatory; scheduled at/after the campaign).

## 9. Benchmark suite (frozen; R19)
equal-weight (1/N, DeMiguel floor) · mean-variance (Ledoit-Wolf shrinkage) · risk parity (equal-risk-
contribution) · HRP · minimum-variance · maximum-diversification · inverse-volatility · cross-sectional
momentum. **R19 (2026-06-20):** the original "SPY buy-and-hold" was a mislabelled **1/N duplicate**
(the anonymized PIT panel carries no index column or market caps), so it is de-duplicated into the 1/N
floor; the suite is expanded with four further published, distinct allocators. A genuine market
benchmark (SPX total-return or a cap-weighted index of the PIT universe) is a documented **gated data
addition** (needs a non-anonymized pull). The hand-crafted **reward** baselines (raw return, return−var,
return−CVaR, differential Sharpe, mean–variance utility, return−drawdown, return−downside, return−turnover,
log-growth) are reported as a secondary "did the LLM beat hand-written rewards?" panel.

## 10. Inference / analysis plan (frozen; audit B-8, C-7)
**PBO/CSCV = primary** overfitting guard. Deflated Sharpe reported but **secondary** (effective trial
count ill-defined under guided search). Stationary-bootstrap (Politis-Romano 1994) difference tests:
**Sharpe** — a re-centred basic (empirical) stationary block-bootstrap test; the bootstrap SE cancels in
the two-sided p-value (`|boot−obs| ≥ |obs|`), so size is empirically certified by `null_calibration`
(audit C-7), not studentized; the bootstrap (Politis-Romano 1994 stationary) and all numerics unchanged
— label correction only (Amendment 2026-06-19, R11) — and **two-sample CVaR-difference** (the
Ledoit-Wolf-for-Sharpe analogue; no published named test exists, so bespoke + null-calibration, audit
C-7). **Separately**, for *forecast*
comparison the **DM comparative ES backtest** on the strictly consistent FZ0 (VaR, ES) score is used
(Fissler-Ziegel 2016 joint elicitability; Nolde-Ziegel 2017) — implemented in `src/inference/es_backtest`.
**Power caveat** (Bauer 2025): tail-risk difference tests have low power at the most extreme quantiles
(CVaR-1%/2.5%) and short windows. **rliable** seed reporting (IQM, probability of improvement, stratified
bootstrap CIs). **Cross-arm/metric multiple-testing correction** (Romano-Wolf or Benjamini-Hochberg FDR).
**Harvey-Liu t>3** hurdle on any alpha claim. **The trial count is stated explicitly.** The headline
claim is **comparative**
("distributional vs scalar at matched compute"), not "beats the market".

> **Amendment 2026-06-20 (R16) — the arm-contrast family difference tests aggregate ACROSS SEEDS
> (rliable per-seed), not over a seed-averaged series.** Each arm's PER-SEED Sharpe/CVaR scores (one per
> frozen-winner test seed) are reduced to an **IQM** point estimate, and a **paired stratified bootstrap
> over the shared training seeds** (re-centred basic empirical p-value, exactly as R11;
> `src/inference/bootstrap.paired_seed_difference_test`) tests the IQM difference — carrying the
> across-seed (training-RNG) variance. This *realizes* the pre-registered "rliable seed reporting (IQM,
> stratified bootstrap CIs)" AT the significance test, and **supersedes** the prior implementation, which
> averaged the per-seed return series per arm before a single-strategy stationary block-bootstrap.
> Averaging N i.i.d.-seed paths shrinks the tested object's variance ~N×, so that construction was
> **anti-conservative** — the inflation scales with the across-seed variance: a representative 30-seed
> calibration (training-RNG-scale seed variance) measured a true-null rejection ≈21% at the 5% level vs
> the correctly-sized ≈5% of the per-seed test (certified by `null_calibration`, audit C-7). The frozen
> family (R13, m = 6),
> the BH/Romano-Wolf correction, the directional H2 conjunction gate, the SESOI/TOST (R12), and the
> re-centred bootstrap convention (R11) are **UNCHANGED** — only the resampling UNIT moves from
> time-blocks-on-a-seed-averaged-series to **seeds-on-per-seed-scores**. The stationary block-bootstrap
> (`sharpe_difference_test`/`cvar_difference_test`) is retained as the single-series tool. Separately,
> `analyze_campaign.h2_conjunction` (with the R13 family-equals-frozen assertion) is now **invoked by the
> analysis entry point** `analyze()`/`write_report` — it was implemented and unit-tested but previously
> unwired, so the documented headline test never actually ran. Pre-freeze refinement (the design is still
> `frozen: false`); `config/preregistration.yaml: inference.seed_reporting` already specified
> `rliable_iqm_poi_stratified_ci`, so this aligns the implementation with the frozen intent.

> **Note 2026-06-20 (R17; R73 follow-up correction 2026-07-02 — re-scoped to the executed Split C) --
> headline test-universe construction + the point-in-time robustness check.**
> The fixed SB3-SAC agent allocates over a FIXED 30-asset action space, so SEARCH/SELECT and the sealed
> TEST share ONE universe: the development-phase **point-in-time top-30** (selected 2005-01-03;
> survivorship-free PIT). The sealed test leg (2020--2026-06-30, Split C) therefore trades the **2005
> cohort** -- a known
> COMPOSITION limitation (names delisted by 2020 are held at 0% under `liquidate_to_cash`; later
> large-caps never enter), **NOT** dev->test leakage (the splits are disjoint + embargoed). It is
> accepted for train/test universe consistency and is **reported as a headline limitation**, not silently
> inherited. **ROBUSTNESS:** the gold ships point-in-time walk-forward selections (incl. a **2020 PIT
> top-30 cohort** at the Split-C test boundary; its overlap with the 2005 cohort is recomputed at run --
> the previously quoted **11/30** differing names was the pre-Split-C 2018-cohort measurement);
> `load_gold_panel(phase="walk_forward", window_start="2020-01-02", end="2026-06-30")` loads that PIT
> universe, enabling a re-evaluation of the frozen winners on the point-in-time universe as a robustness
> check on the H2 conclusion (gated compute). Whether to elevate the PIT universe to the headline or keep
> the consistent fixed cohort with this robustness check is a methodological design choice for the
> supervisor, **not** a code defect -- the capability + the bias magnitude are documented here.

> **Amendment 2026-06-19 (R13) — the multiple-testing family is enumerated and FROZEN.** The realized
> testing family is `{arm-contrast × held-out-metric}`, enumerated by
> `scripts/analyze_campaign.collect_family_pvalues` and gated by `h2_conjunction`: each of the three H2
> contrasts is tested on the Sharpe ratio and on the CVaR at the pre-registered tail level (the headline
> α = 0.05; the EVT-flagged `cvar_01` is opt-in and grows the family to 9, not part of the frozen default
> family). This **includes the H2 conjunction's distributional-vs-{scalar, placebo, scalar_cvar5} legs**.
> The integer family size is **m = 6**:
>
> | # | Hypothesis (contrast, read "a better than b") | Held-out metric | Level α |
> |---|---|---|---|
> | 1 | distributional > scalar | Sharpe | — |
> | 2 | distributional > scalar | CVaR | 0.05 |
> | 3 | distributional > placebo | Sharpe | — |
> | 4 | distributional > placebo | CVaR | 0.05 |
> | 5 | distributional > scalar_cvar5 | Sharpe | — |
> | 6 | distributional > scalar_cvar5 | CVaR | 0.05 |
>
> **Benjamini-Hochberg at q = 0.05 is the PRIMARY** correction over this m = 6 family (the FDR rejection
> set; `config/inference.yaml: multiplicity`); the **joint Romano-Wolf stepdown** (one shared
> stationary-bootstrap path per replication, `romano_wolf_joint`) is the FWER alternative. The
> **Harvey-Liu t>3 hurdle is scoped to ABSOLUTE-alpha claims ONLY**; arm contrasts use the bootstrap
> difference test (R11) + FDR, not the t>3 hurdle. The frozen family + `m` are mirrored machine-readably
> in `config/preregistration.yaml` (`inference.testing_family`), and `analyze_campaign`/`run_campaign`
> carry a fail-loud assertion that the realized contrast set equals the frozen family. **(The headline
> GATE over this enumerated family is superseded by R25 below — the m = 6 enumeration is retained as the
> frozen realized-family assert + a reported BH-over-6 sensitivity, but it no longer gates the verdict.)**

> **Amendment 2026-06-25 (R25) — H2 decided by TWO co-primary intersection–union tests; BH-over-6 demoted
> to a reported sensitivity.** The headline H2 decision rule is changed from `(3-leg Sharpe conjunction) ∘
> (Benjamini-Hochberg over the m = 6 family)` to **two co-primary intersection–union tests (IUTs)**, each
> decided **one-sided at α = 0.05** in the predicted direction with **no further leg correction**:
>
> - **H2-RA (risk-adjusted):** the three **Sharpe** legs {distributional > scalar, > placebo, >
>   scalar_cvar5}. Supported iff **all three** reject one-sided at 0.05 in the predicted direction. A
>   3-leg IUT, **m = 3**.
> - **H2-Tail (tail outcome):** the three **CVaR-5%** legs (same three contrasts). Supported iff **all
>   three** reject one-sided at 0.05 in the predicted direction. A parallel 3-leg IUT, **m = 3**.
>   Corroborated — **not gated** — by the FZ0/(VaR, ES) Diebold–Mariano comparative backtest
>   (`src.inference.es_backtest.comparative_es_backtest`) where available.
>
> Both verdicts are reported (a **two-tier headline**: H2-RA and H2-Tail). The m = 6 BH set (the R13
> family) is **retained as a reported SENSITIVITY** (DEEP_H2 §3.3 option B), never the gate.
>
> **Leg decision (one-sided).** Each leg's per-seed rliable paired bootstrap (R16) returns a two-sided p;
> the genuinely one-sided in-direction decision is `p_one = p_two / 2` when the effect is in the predicted
> direction (`distributional` strictly better), else the leg does not reject (DEEP_H2 stats note A5). **(Superseded by R64, 2026-06-28: the leg p is now the DIRECT upper-tail bootstrap probability `pvalue_one_sided_greater = P(boot − obs ≥ obs)`, NOT `p_two/2` — halving the symmetric two-sided p is exactly valid ONLY under a symmetric bootstrap, whereas the direct upper-tail probability is exactly valid under ANY skew of the CVaR-difference bootstrap; the one-sided intersection-union METHOD is unchanged. See the amendment table, R64.)** No
> change to the resampling unit, the IQM, the seed set, the arms, the budget, λ, or the splits.
>
> **Rationale (a design CORRECTION justified a priori by the theory spine, NOT a post-hoc data switch).**
> (i) A conjunction *is* an intersection–union test (Berger 1982), whose joint size is already ≤ the max
> leg size = α, so it **is** the multiplicity correction; applying BH **on top** of the conjunction
> **double-corrects** and is under-powered against H2 (the prior `(conjunction ∘ BH-over-6)` was neither a
> clean IUT nor a clean BH set; DEEP_H2 §3.2). (ii) The Sharpe gate is **tail-blind** — by the λ = 0,
> reward-independent selection (R22) the design selects on and tests on the dimension the distributional
> channel helps *least*, relegating the tail (the dimension it informs most) to a non-gating secondary;
> elevating **CVaR-5% from secondary to co-primary** makes the contribution's **tail dimension bankable**
> (DEEP_H2 §4.3 / §7). Both points follow from the theory spine fixed before the sealed test leg was
> seen, so this is a pre-specified design correction, not a moved goalpost. The pilot CVaR signal (a
> directional CVaR-5% advantage in the Sonnet prototype) is disclosed **as confirmatory** of the a-priori
> mechanism, not as the reason for the change. Mirrored in `config/preregistration.yaml:
> inference.testing_family` (`structure: two_co_primary_iut`, `families.{h2_ra, h2_tail}`,
> `alpha_one_sided: 0.05`, `bh_over_6: reported_sensitivity_not_gate`); the m = 6 union, its `members`,
> and the fail-loud realized-family assert are unchanged.
>
> **Pre-registered bankable-null statement (verbatim; DEEP_H2 §7.2; sealed-leg span corrected to the
> R73 window 2026-07-02 — the statement must name the leg it actually protects).**
> > *"We pre-registered, before observing the sealed 2020–2026H1 test leg, the hypotheses H2-RA and H2-Tail
> > above, their three-leg intersection–union decision rules at α = 0.05, the directional predictions, the
> > per-seed rliable IQM paired-bootstrap test over the pre-registered winner-seed ladder (Amendment E1:
> > tier-0 core n = 30 up to n = 568, primary target 403, exogenous stopping tier) (Agarwal et al. 2021), the SESOI of
> > 0.05 DSR, and a symmetric TOST equivalence margin of ±0.05 (in the test-statistic's units). If neither
> > H2-RA nor H2-Tail rejects, we report a **null**: at matched compute and with a fixed SB3-SAC agent,
> > multi-level tail-risk feedback to an LLM reward-designer did **not** produce detectably better
> > out-of-sample risk-adjusted performance or tail outcomes than scalar feedback, **and** — where the
> > TOST 90% bootstrap CI lies inside ±0.05 — the two feedback channels are **practically equivalent
> > within the smallest effect we deemed worth detecting**. Because the design, budget, metrics, decision
> > rules, and equivalence margin were fixed in advance (PREREGISTRATION §1/§5/§10; freeze hash in
> > DECISION_LOG), this null is a calibrated statement about the feedback channel as posed, not a moved
> > goalpost. The contrast is common-mode across all confounds applied byte-identically to every arm
> > (universe composition, delisting fill, costs, rf convention, seed budget; LIMITATIONS_REGISTER closing
> > framing), so it isolates the feedback channel, and the result bounds the channel's value rather than
> > the market's."*

> **Cost-robustness sweep (pre-registered, Amendment 2026-06-19, R15).** The frozen winners are RE-PRICED
> across `costs.grid_bps = [0, 5, 10, 25, 50]` bps WITHOUT retraining (`net_c = gross − bps·1e-4·turnover`;
> exact because cost is charged after the action), report-only/post-freeze, never re-selecting; the
> winner-identity-vs-cost table confirms the distributional edge is a risk-shape effect, not a trade-less
> artefact. Mirrored in `config/preregistration.yaml: cost_sweep`.

> **Pre-freeze amendment (2026-06-19, R12 — power analysis / viva Q21) — SESOI + TOST.** The analysis plan
> adds a pre-registered SESOI = **0.05 validation-DSR units** + a symmetric TOST equivalence margin =
> **±0.05 DSR** for the headline H2 (distributional vs scalar) contrast; a non-rejection is reported as a
> bounded effect (the MDE at 80% power / Šidák-α in `docs/POWER_ANALYSIS.md`), and if the TOST 90%
> bootstrap CI for the mean-DSR difference lies inside ±0.05 the arms are practically equivalent within the
> SESOI; the seed-to-seed σ is filled from the pilot pre-freeze; hypotheses/arms/seeds/budget/splits
> unchanged. Mirrored in `config/preregistration.yaml: inference.{sesoi, equivalence_margin}`.

> **Pre-freeze amendment (2026-07-01, RATIFIED — risk-free numeraire (R20): headline rf = 0 + a reported
> rf-excess robustness; idle cash = 0; user-delegated authority, mirrored in `config/preregistration.yaml: numeraire`).** The headline H2 Sharpe uses
> **rf = 0** (excess ≡ total return; `analyze_campaign._sharpe_score` with `risk_free=None`, byte-identical to
> a frozen rf = 0; `src/inference/bootstrap.sharpe_ratio` carries no rf term), and the portfolio environment
> books **0 % on idle cash** (`config/environment.yaml: cash_daily_rate = 0.0`; the env *prices* cash when the
> rate is set — `portfolio_env.py:294,305` — but the frozen value is zero). **Rationale (why rf = 0 cannot
> change the headline):** H2 is a **comparative, common-mode** test (distributional vs scalar, every confound
> applied byte-identically to all seven arms). In a Sharpe *difference* `(μ_a−rf)/σ_a − (μ_b−rf)/σ_b`, the
> risk-free term is `rf·(1/σ_b − 1/σ_a)`, which **cancels to first order** when the arms share volatility (same
> fixed SB3-SAC agent, same universe) — so rf moves only the *absolute* Sharpe level, never the arm ordering.
> To **demonstrate** this rather than assert it, the FRED **`DGS3MO`** daily rate **is** wired into a reported
> **risk-free-excess robustness sensitivity** (`analyze_campaign.h2_sharpe_rf_robustness`, sourced from
> `market_reference.load_risk_free_daily(...).daily`), which re-runs the family on excess returns and confirms
> the headline ordering is rf-invariant. This **ratifies the existing default as the deliberate frozen choice**
> (closing the open "ratify λ/cash" pre-freeze item and the R20 rf-threading note). The rejected alternative —
> rf-excess as the *headline* numeraire + a per-session `DGS3MO` series threaded into the env idle-cash leg
> (which would require `PortfolioEnv` to accept a rate *series*, not just the scalar knob) — is recorded as
> available but NOT adopted, because it changes no comparative conclusion while enlarging the frozen-decision
> surface. No other frozen quantity changes.

## 11. Algorithms (frozen)
Headline: **SB3 SAC** (fixed across all feedback arms). Secondary critic: **TQC** (sb3-contrib).
Robustness on winners only: PPO, TD3. Continuous-only fallback: D4PG (never QR-DQN — discrete-only).
Library-default hyperparameters, identical across arms, with a runtime equivalence test.

> **Pre-freeze amendment (2026-06-24) — float32 (TF32) precision is config-driven and uniform.** The agent's
> matmul precision is ONE setting (`agent.tf32`, default ON for Ampere/Ada throughput), applied in
> `src.agents.trainer.train_agent` so the serial trainer, the parallel SEARCH worker, and the parallel TEST
> worker share IDENTICAL float32 numerics. This resolves a latent SELECT-vs-EVALUATE asymmetry (the SEARCH
> worker previously enabled TF32 while the serial / TEST trainers used the PyTorch default) — the numeric
> cousin of the batch_size 256/512 drift the audit caught. Library-default hyperparameters and the runtime
> equivalence test are otherwise unchanged; the precision is a SINGLE `train_agent` setting (config key
> `tf32`, default-on, overridable — `src/agents/trainer.py`), applied uniformly across the serial / SEARCH /
> TEST paths — set in `config/prototype.yaml` (`agent.tf32`) and threaded through `_agent_cfg` /
> `build_parallel_opts` → `_spec` → `train_candidate` to every trainer — so it is config-driven and no
> longer a per-scheduler side-effect.

## 12. Compute (frozen plan; audit A-6/C-4)
RTX 4090 for development; **UCL Myriad** for the parallel campaign as an array job over
arms × seeds × folds. Contingency only if both unavailable: one Colab Pro+ GPU + down-rank H3/H4 +
the CVaR-5% arm.

> **Pre-freeze amendment (2026-06-17, ADR-023).** UCL Myriad is **not available** and
> Azure-for-Students/GCP GPU quota is blocked. The recorded compute plan is now: Phase-0 on the owned RTX
> 4050; campaign on a **rented RTX 4090 + seeds-on-winners** (≈$13–16, ~1.5 days), free fallback =
> Kaggle+Lightning+Colab+laptop. The matched-compute design, arms, and folds are **unchanged** — only the
> hardware/venue (seeds: see amendment D2 (winners 5→30), §6/§12 and the amendment record).
> Authoritative detail: `docs/COMPUTE_AND_TRAINING_TIME.md`.

> **Pre-freeze amendment (2026-07-01, ADR-040 — LAPTOP-ONLY; supersedes ADR-023's rented-4090 venue;
> dated note added 2026-07-02).** The EXECUTED compute plan is **laptop-only on the owned RTX 4050**: the
> TEST leg runs the parallel scheduler at **3 workers** on the **Turbo** power profile; the SEARCH leg runs
> **SERIAL** (§6, reflect-on-best). The longer wall-clock is ACCEPTED — the deadline math (ADR-040) absorbs
> the multi-week unattended run, and renting reintroduces venue/ops risk for no design gain. The
> matched-compute design, arms, seeds, and folds are unchanged — venue only; the Myriad → rented-4090 trail
> above is retained as the amendment history.

> **Amendment D2 (2026-06-19, user-approved) — winner seed count 5→30 (re-affirmed at §12; D2's winner
> count 30 was subsequently raised to the E1 tiered ladder, 2026-07-10 — see the E1 note below and the
> amendment record; the winners×30 ≈ 210 figures here are the D2-era historical bands).** The per-arm
> WINNER seed count is raised from 5 to ≥20 (target **30**); the SEARCH budget is untouched (1 seed per
> candidate during search; only the per-arm winners re-run at 30 seeds), so matched compute is unchanged.
> The campaign run-count / GPU-hour bands are recomputed as **winners × 30** (now **≈7 arms × 30 ≈ 210**
> winner trainings — the 7th arm `placebo_shuffled` was added post-D2 [V1/V12, 2026-06-26] — PLUS the
> pre-registered H1 best-of-4 baseline stage and the H3 single-shot stage, each its own block, so the total
> test-leg trainings and the DSR trial count EXCEED the bare 180; the exact per-arm tally is read from the
> run artifacts by `analyze_campaign.compute_accounting` (R35). The search legs are unchanged); see
> `docs/COMPUTE_AND_TRAINING_TIME.md`. `config/{prereg,
> campaign,inference}.yaml` carry the assurance-tier ladder `{mode: tiered, tiers: [30, 100, 189, 279,
> 340, 403, 568]}`, resolving to `[0..567]` — a headline seed count 568 (Amendment E1, 2026-07-10;
> tier 0 = 0–29).

---

### Freeze record
| Item | Value |
|---|---|
| Frozen on | _(to fill at Phase-1 freeze)_ |
| Content hash (SHA-256) | _(emitted by `scripts/freeze.py`)_ |
| Phase-0 smoke pass recorded | _(DECISION_LOG entry id)_ |
| Amendments | See the amendment record below. |

### Amendment record
All post-draft changes to this frozen design are dated amendment entries (the protocol), never silent
edits; each is mirrored in `config/preregistration.yaml` (which `scripts/freeze.py` checks against this
prose). Newest at the bottom.

| Date | Id | § | Summary | YAML mirror |
|---|---|---|---|---|
| 2026-06-17 | ADR-023 | §12 | Compute venue: rented RTX 4090 + seeds-on-winners; no UCL Myriad. | — (compute venue) |
| 2026-06-19 | D2 | §6, §12 | **Winner seed count 5→30** (target 30, ≥20; Henderson 2018, Colas et al.); search budget untouched (1 seed/candidate); GPU-hour bands recomputed as winners×30. User-approved. **Superseded by E1.** | `seeds: 0–29` (n=30) |
| 2026-07-10 | E1 | §6, §12 | **Winner seeds → assurance-tier ladder** `{mode: tiered, tiers: [30, 100, 189, 279, 340, 403, 568]}` (flat `[0..567]`, headline 568). σ_D pilot fired the σ_D>0.10 trigger (σ_D=0.369, ρ=−0.141); the unattainable "30→50" rule is **retired**; cumulative order-only tiers, each a complete study with a pre-registered meaning (30 core / 100 σ-precision / 189 point-estimate power / 279=80% / 340=90% / 403=95% target / 568=99%); truncation falls back to the largest completed rung (spacing caps waste); **exogenous** stopping tier (throughput vs deadline, never results) preserves the single look. Search budget, matched compute, arms, hypotheses unchanged. Supervisor-approved. | `seeds: {mode: tiered, tiers: [30, 100, 189, 279, 340, 403, 568]}` |
| 2026-06-20 | R17 | §10 | **Test-universe limitation + PIT robustness**: the sealed test leg trades the development-phase 2005-cohort PIT top-30 (fixed action space -> consistent train/test universe), a documented composition bias (11/30 names differ from the 2018 PIT cohort); `load_gold_panel(phase="walk_forward", window_start=...)` enables a PIT-universe robustness re-evaluation (gated). Reported as a limitation, not silently inherited. | loader `window_start`; run_campaign caveat |
| 2026-06-20 | R16 | §10 | **Per-seed (rliable) arm-contrast difference tests**: per-seed Sharpe/CVaR → IQM → paired stratified bootstrap over the shared training seeds (carries across-seed variance), realizing `seed_reporting: rliable_iqm`; supersedes the seed-AVERAGED-series bootstrap (anti-conservative ~21%→~5% null rejection). Family (m=6), correction, conjunction, R11 convention unchanged. `h2_conjunction` now wired into the analysis entry point. | `inference.{difference_test_unit, seed_reporting}` |
| 2026-06-19 | R13 | §10 | **Multiple-testing family enumerated + FROZEN**: `{arm-contrast × {Sharpe, CVaR-0.05}}`, **m = 6** (incl. the H2 conjunction's 3 legs); BH q=0.05 primary, joint Romano-Wolf the FWER alternative; Harvey-Liu t>3 scoped to absolute-alpha claims only. | `inference.testing_family` (`m: 6`) |
| 2026-06-19 | R11 | §10 | **Sharpe test relabel**: "studentized (Ledoit-Wolf 2008)" → re-centred basic stationary block-bootstrap (SE cancels; size certified by null_calibration); numerics unchanged. | `difference_tests: [sharpe_recentred_bootstrap, cvar_difference]` |
| 2026-06-19 | R15 | §10 | **Cost-robustness sweep** (pre-registered): re-price frozen winners over `grid_bps=[0,5,10,25,50]` without retraining; report-only, never re-selecting. | `cost_sweep` |
| 2026-06-19 | R12 | §10 | **SESOI + TOST**: SESOI = 0.05 val-DSR; symmetric TOST margin ±0.05 DSR for H2 (distributional vs scalar); non-rejection reported as a bounded effect. | `inference.{sesoi, equivalence_margin}` |
| 2026-06-20 | R20 | §10 | **Risk-free convention + additive H2 robustness** (critical-review). The headline Sharpe/Deflated-Sharpe hardwired rf=0; the "rf cancels in the pairwise arm contrast" defence is FALSE in general — the per-seed Sharpe rf penalty `mean(rf)·√252/σ` is LARGER for lower-volatility arms, so if the distributional (tail-aware) arm wins partly via lower realised vol, the real rf SHRINKS the measured H2 edge (empirically confirmed). The **frozen rf=0 headline is RETAINED as the pre-registered primary** (it is byte-identical; `collect_family_pvalues(risk_free=None)`); an **additive sensitivity** recomputes the Sharpe leg on EXCESS returns (r − FRED DGS3MO; CVaR left raw) via `h2_sharpe_rf_robustness`, reporting per-leg effect/shrinkage/rejection BOTH ways and whether H2 survives. The real T-bill (DGS3MO, frozen on disk) also feeds the reported benchmark-relative Sharpe/alpha. The env now PRICES a configurable cash sleeve (`state.cash_daily_rate`), held at **0.0** for now: a constant biases the risk study (the 3-mo T-bill ranged 0–5.6%/yr 2005–2025, overpaying cash in the ZIRP stress the tail-aware arm exploits), so a per-session DGS3MO SERIES is the correct refinement before enabling. | `analyze_campaign.{collect_family_pvalues(risk_free=), h2_sharpe_rf_robustness}`; `market_reference.load_risk_free_daily`; `portfolio_env.cash_daily_rate` |
| 2026-06-20 | R19 | §9 | **Benchmark suite de-duped + expanded** (leakage/rigor audit). "SPY buy-and-hold" was an EXACT 1/N duplicate of equal-weight mislabelled as the S&P 500 (the anonymized PIT panel has no index/caps) → removed from the gate (de-dupes the DeMiguel floor, fixes a best-benchmark double-count). Suite expanded with four further published allocators (minimum-variance, maximum-diversification, inverse-volatility, cross-sectional momentum) → 8 distinct allocators. Hand-crafted reward baselines (9) reported as a secondary panel. A true SPX-TR/cap-weighted market benchmark is a documented gated data addition. | `analyze_campaign._BENCHMARK_NAMES`; `baselines.{STRATEGY_CANON, REWARD_CANON}` |
| 2026-06-20 | R18 | §7 | **Inter-split purge now covers the feature lookback** (leakage fix; supervisor-panel audit 2026-06-20). Every observation reads `returns[t-lookback:t]` (lookback=60), so a split-boundary gap of only `embargo`=21 left the downstream window's first (lookback−embargo)=**39 observations reading prior-split returns** — a López de Prado (2018) purge-insufficiency. The effective inter-split purge is now **max(embargo, lookback) = 60** sessions at BOTH boundaries (train→val and val→test); the embargo (21) is retained as the label/serial-correlation floor, the lookback (60) dominates. No feature window crosses a split. Applied in `resolve_windows` (campaign val+test legs) and `embargoed_val_start` (search val leg, new `lookback=` arg); the test asserts `gap ≥ lookback`. Selection/inference math unchanged; the sealed test leg loses its first ~39 sessions (of ~1,700). | `run_campaign.resolve_windows`; `loaders.embargoed_val_start(lookback=)`; `test_embargo_splits` |
| 2026-06-24 | R21 | §6 | **Optional reflect-on-BEST parallel SEARCH + matched 50k buffer**: `run_campaign.py --search-gpu N` (default 0 = serial reflect-on-last, the prototype-de-risked path) routes the dev-split search through the within-generation/cross-arm scheduler, seeding reflection from each generation's BEST candidate (Eureka Alg.1 line 9-faithful; the serial loop seeds from the LAST) and training at `buffer==train_steps=50k` (resolves the serial 25k-buffer skew, matches TEST). Symmetric across arms (not an H2 confound); SELECT/FREEZE/TEST schema unchanged. The serial-vs-parallel headline choice is RECORDED at freeze. | `search.{reflect_protocol_default, reflect_protocol_parallel, headline_reflect_protocol}` |
| 2026-06-24 | R22 | §5 | **λ formalization (PROPOSED)**: `lambda_cvar = 0.0` (pure validation-DSR selection, no tail penalty — the tail is the FEEDBACK channel's job, measured on the sealed test leg). Eureka-faithful, reward-independent, biases AGAINST H2 (conservative). The inert `lambda_grid`/`calibration_fold` (read by no live code) are deleted from `config/inference.yaml` at freeze IF ratified. | `fitness.lambda_cvar: 0.0` |
| 2026-06-24 | R23 | §11 | **Config-driven TF32 (uniform)**: matmul precision is a single `train_agent` setting (`tf32`, default-on, overridable), applied identically to the serial trainer, the SEARCH worker, and the TEST worker — resolving a latent select-vs-evaluate numerics asymmetry (the SEARCH worker had enabled TF32 while serial/TEST used the PyTorch default). | `agent_numerics.tf32: true` |
| 2026-06-25 | R24 | §6 | **Headline reflection protocol RECORDED = parallel reflect-on-best** (the R21 "record at freeze" choice, now made). Parallel best-of-generation (`--search-gpu 2`, matched 50k buffer) is the HEADLINE: it resolves the L14 serial 25k-buffer asymmetry, is Eureka-faithful (reflect on best-so-far), and ~halves the laptop run. Serial reflect-on-last retained as the de-risked fallback (`--search-gpu 0`); parallel gated on a GREEN single-arm 50k GPU-smoke. | `search.headline_reflect_protocol: parallel_reflect_on_best` |
| 2026-06-25 | R26 | §9 | **Factor attribution pre-registered as a declared secondary family (the BAB/low-vol pre-empt).** A long-only volatility-lowering agent structurally loads on Betting-Against-Beta (Frazzini–Pedersen 2014) and low-volatility, so the headline could be recast as a repackaged anomaly harvest. The factor-attribution module (`src/inference/attribution.py`: difference-in-alpha across CAPM/FF3/Carhart-4/FF5/FF6(+BAB,QMJ) with Newey-West HAC SEs, paired across-seed) is now a PRE-REGISTERED secondary declared family (disjoint from the frozen m=6), reporting whether the distributional−scalar alpha difference survives the factor controls. CAPM/FF3/Carhart-4 run on on-disk factors; BAB/QMJ need a small AQR pull. See LIMITATIONS_REGISTER L15. | `out["attribution"]` (disjoint Door-C family) |
| 2026-06-25 | R27 | §4 | **EVT tail estimator = plain GPD MLE; Troop (2021) bias-correction is FUTURE WORK (not implemented).** Corrects the §4 over-claim ("frozen Phase-1 enhancement"). Measured in-regime (n≈750, α∈{0.05,0.01}): plain-MLE CVaR error is variance-dominated (bias ≈ −0.1%/+0.9%) and Troop's second-order correction is ill-conditioned (GPD ξ≤0 for ~94% of samples), so it would not reduce RMSE — implementing it would be theatre. The shipped tail is plain MLE; the threshold-sensitivity diagnostic is the stability exhibit. Matters now that CVaR-5% is co-primary (R25). | `measurement.py::_evt_cvar` (plain MLE; `EVT_ESTIMATOR_NOTE`) |
| 2026-06-25 | R28 | §3 | **H4a random-search grammar widened to the shared six-term reward family (aligns ADR-010).** The H4a control previously sampled a 3-term grammar (return−var−cvar), strictly poorer than the BO family + the LLM, so a positive H4a was partly a richness artefact. It now samples the SAME six-primitive family as H4b (`reward_family.params_to_source`: return/log/turnover/drawdown/cvar/vol) from a coarse grid at the BO arm's fixed cvar_alpha=0.05/window=20 — realizing the frozen ADR-010 intent that `params_to_reward` is the shared constructor. H4a is now a genuine procedure-only control at comparable richness; budget unchanged (matched compute holds). Scope: the LLM still authors strictly-richer free-form code, so a positive H4 = open-ended-language + procedure, not procedure alone. | `src/search/random_search.py` → six-term family |
| 2026-06-25 | R29 | §3 | **H4b method relabel (integrity, no science change): GP-EI Bayesian optimisation, NOT Optuna-TPE.** The H4b arm is scikit-learn GP + Matérn-2.5 Expected-Improvement (n_init=5, matched budget 30); the `eureka_loop.yaml` label `bayesopt_tpe` / "Optuna TPE, 240 trials" was factually false (Optuna is not a dependency; budget is 30/40, not 240). Method citation: Snoek, Larochelle & Adams (2012, NeurIPS), replacing any Bergstra-2011 (TPE). The frozen arm name `bayes_opt` is unchanged. | `config/eureka_loop.yaml` relabel; `snoek2012bayesopt` |
| 2026-06-25 | R25 | §1, §10 | **H2 = TWO co-primary intersection–union tests; BH-over-6 demoted to a reported sensitivity.** Replaces `(3-leg Sharpe conjunction) ∘ (BH over m = 6)` — which **double-corrected** (a conjunction is already an IUT, joint size ≤ α; Berger 1982) — with **H2-RA** (3 Sharpe legs, IUT, **m = 3**) and **H2-Tail** (3 CVaR-5% legs, IUT, **m = 3**), each decided **one-sided at α = 0.05** in the predicted direction with **no leg correction** (the conjunction is the correction). Elevates **CVaR-5% from secondary to co-primary** so the tail dimension is bankable; a design CORRECTION justified a priori by the theory spine (the λ = 0 Sharpe gate is tail-blind) — NOT a post-hoc data switch; the pilot CVaR signal is disclosed as confirmatory. The m = 6 union/`members` + the fail-loud realized-family assert are unchanged; the BH-over-6 set is **reported, not gated**. H2-Tail corroborated (not gated) by the FZ0/(VaR, ES) comparative backtest. Verbatim bankable-null statement pre-registered in §10. | `inference.testing_family.{structure: two_co_primary_iut, families.{h2_ra, h2_tail}, alpha_one_sided: 0.05, bh_over_6: reported_sensitivity_not_gate}` |
| 2026-06-25 | R30 | §1, §6 | **H3 + H4 sealed-leg tests wired (the asymmetric-rigor fix); H1 hardened descriptive.** Closes the gap that H3/H4 were pre-registered but lacked a campaign-grade sealed-leg test (only H1/H2 had one). **H3** (`out["h3"]`): the iterative distributional winner (gen 6, reflect-on-best) vs a matched **single-shot** condition (`generations:1`, best-of-N, no reflection; identical 30-candidate budget / 30 seeds / 50k buffer / validation-DSR selector; disjoint `*_h3_singleshot/` roots; `--h3-singleshot` / `--single-shot-root`) — per-seed IQM paired difference + a **TOST ±0.05** equivalence (the bankable null). **H4** (`out["h4"]`): distributional vs random_search (H4a) + bayes_opt (H4b), per-seed IQM paired, a **2-test family with a Bonferroni-over-2** sensitivity. Both report-only, OUTSIDE the frozen m=6. **H1 hardened** (DEEP_H1): the best-of-4 baseline identity is selected on **validation** not test (data-snoop fix; flagged fallback if no val signal archived); the §18-19→§1/§9 citation is fixed; the metric is relabelled **Eureka-STYLE** (Eureka's HNS is not computable single-task). + report-only sensitivities: headline TOST (`h2_tost`), DSR effective-N (`dsr_effective_n`, benign direction), EVT-estimator consistency across arms (`evt_consistency`), and the T0 turnover/cost table + undeflated-N=1 DSR (`benchmark_floor`). | `out["h3"]/["h4"]/["h2_tost"]/["dsr_effective_n"]/["evt_consistency"]`; `run_h3_singleshot`; `campaign.yaml: h3_singleshot_generations` |
| 2026-06-25 | R31 | §10 | **Cross-hypothesis (H1–H4) multiplicity stance pre-registered (the linchpin; DEEP_STATS C4).** H1–H4 are **separate pre-registered estimands**, each with its own multiplicity control (H2 = the two IUT families; H4 = Bonferroni-over-2; H1 = descriptive; H3 = single contrast + TOST). There is **no global FWER correction across the four** by design (they answer distinct questions); a **Bonferroni-across-4 SENSITIVITY** on the four headline decisions is reported (`out["cross_hypothesis_multiplicity"]`) so a reader can see the corrected picture. Makes the garden-of-forking-paths stance explicit, not implicit. | `out["cross_hypothesis_multiplicity"]` (report-only) |
| 2026-06-25 | R32 | §1, §10 | **`placebo_shuffled` structure-vs-content control (the 5th LLM arm; closes the Gupta–Hartford format-vs-content threat).** Adds an LLM arm whose feedback block is **byte-structurally identical** to the distributional block (same header / intro / six labels / CVaR-1% high-variance annotation) but with the six real tail VALUES **candidate-seeded-DERANGED** across their labels — matching the FORMAT and the MARGINAL set of numbers while breaking ONLY the coherent label→value mapping (the tail SHAPE). Reported as a **DISJOINT secondary** (`out["h2_structure"]`: distributional > placebo_shuffled, Sharpe + CVaR-5%, one-sided, both legs), **NOT folded into the frozen m = 6 union** (which is unchanged) and **never a gate**: a win on both metrics isolates the coherent tail information (content) from a plausible-looking numeric table (format). The inert all-zeros `placebo` controls token-count only (DEEP_SYSTEM red-team HIGH — "the single most reviewer-convincing experiment"); this is that structure control. Also lands serial reflect-on-**best** parity (M5), so the serial fallback matches the R24 parallel headline. | `arms.placebo_shuffled` + `inference.secondary_families.h2_structure_control`; `out["h2_structure"]` |
| 2026-06-25 | R33 | §7 | **Survivorship-corrected `univ4` adopted as the FROZEN headline panel; ADR-024's PROVISIONAL `liquidate_to_cash` RESOLVED for the headline tail; the delisting-return sensitivity band pre-registered.** ADR-024 shipped the env on `univ3` with a **PROVISIONAL** zero-fill delisting policy (`liquidate_to_cash`: a dead name's post-event return → 0.0), flagged as a defensible prototype default but **not** a ratified headline choice. The headline panel is now **`univ4`**: the survivorship-corrected build that books **Shumway** delisting returns (−30% NYSE/AMEX, −55% NASDAQ; Shumway 1997 JF, Shumway & Warther 1999 JF) **multiplicatively** `(1+r)(1+dl)−1` onto each delisted name's **last valid session** (`data_pipeline` `apply_shumway_corrections`). It is the **same 953-name universe** and the **same 5283×953 shape**; only the **333 delisting cells differ** from `univ3` (0 of them in the 620 continuously-live columns), giving a **heavier, correct** left tail (test-window pooled CVaR-5% −0.0577 → −0.0582). `univ3` (= `liquidate_to_cash`/zero-fill) is **retained as the 0%-delisting-return END** of a reported, report-only **delisting-return sensitivity band** (`scripts/analyze_campaign.delisting_band`, DATA-level, no policy re-run): the 333 test-window delisting cells are overwritten with `d ∈ {0.0, −0.30, −0.55, −1.00}` and the **pooled CVaR-5% / CVaR-1%** recomputed at each `d`. `univ4` (the −30/−55 Shumway headline) sits at the band's **structural extreme** — Refinitiv carries no vendor delisting terminal, so the fixed surcharge is applied to **100%** of delistings. **LOW-RISK adoption:** the loader's LIVE default stays `univ3` (dev + the test suite are untouched); the campaign launch + analyze stages export `LLM_RP_GOLD_SUFFIX=univ4`. The frozen m=6 union, all hypotheses, splits, budget, and fitness are unchanged; the band is **DISJOINT** (no family-tuple keys) and **never a gate**. | `data_panel.{headline: univ4, band_zero_end: univ3, resolves: ADR-024}` + `inference.secondary_families.delisting_band`; `out["delisting_band"]`; `docs/CAMPAIGN_RUNBOOK.md` `LLM_RP_GOLD_SUFFIX=univ4` |
| 2026-06-25 | R34 | §10 | **Training-divergence diagnostic (the unbounded-reward confound, report-only).** Campaign monitoring appends every `critic_explosion` event to one append-only `anomalies.jsonl`, so the LINE count over-states how many distinct training RUNS diverged. `analyze_campaign.divergence_report` READS that log (the trainer is NOT modified), clusters the lines into RUNS by step-reset (a step that goes backwards = a new training), and reports the true diverged-RUN count + rate plus whether any frozen WINNER's training diverged. The verified prototype fact: 64 anomaly LINES = **6 diverged RUNS** (≈2.5% of the candidate budget), mostly TRANSIENT single-step spikes. **Disclosure:** the reward is UNBOUNDED on purpose (`norm_reward=False` is DELIBERATE — the reward is the object of study, so its scale is left as authored), so a mis-scaled candidate can transiently blow the critic up; but a diverged candidate scores POORLY on held-out validation and LOSES selection, so divergence biases toward NOISE in the dropped tail, NOT toward the H2 headline. Report-only; DISJOINT (no family-tuple keys); never a gate. | `out["divergence"]`; `analyze_campaign.divergence_report` |
| 2026-06-25 | R35 | §10 | **Compute-accounting table (the matched-budget asymmetries, report-only).** `analyze_campaign.compute_accounting` tabulates per arm, from the archived `failures.jsonl` + `llm_calls.jsonl` (token usage), candidates attempted/accepted/failed + total prompt-tokens. It discloses two asymmetries, both favourable-or-controlled for the headline: **(i)** the LLM arms BURN a budget slot on a gate-failure (`src/llm/loop.py` ~338,380) while the search arms RESAMPLE to a full valid slate (`src/search/random_search.py` ~259), so the search arms get strictly MORE valid candidates per matched budget — a handicap on the LLM arms, i.e. CONSERVATIVE (favours search, against the LLM H2 headline); **(ii)** the tail-aware feedback block sends ~8 feedback lines vs the scalar arm's 1, and that token-count difference is the EXACT quantity the inert `placebo` leg controls for in the H2 placebo contrast. Report-only; DISJOINT; never a gate. | `out["compute_accounting"]`; `analyze_campaign.compute_accounting` |
| 2026-06-25 | R36 | §10 | **Second PBO ranked on the DSR-proxy (guards the SELECTION rule; report-only).** The frozen PRIMARY PBO/CSCV (`src/inference/overfitting.py`) ranks IS/OOS on the MEAN validation return, but winner SELECTION used the validation **DSR** (`src/selection/fitness.py`; a monotone transform of the per-series Sharpe at the frozen λ=0). `analyze_campaign.campaign_pbo_dsr` adds a SECOND PBO ranked on the per-block annualised Sharpe — the DSR-proxy statistic selection actually used — reported ALONGSIDE the mean-return column; the frozen primary guard is **UNCHANGED** (additive only, `overfitting.pbo` is never modified). Close agreement empirically closes the DEEP_STATS A3 "you didn't guard the rule you used" concern (with λ=0 the two ranking rules should agree closely). Report-only; DISJOINT; never a gate. | `out["pbo_dsr"]`; `analyze_campaign.{campaign_pbo_dsr, pbo_dsr_markdown}` |
| 2026-06-25 | R37 | §10 | **Power doc regenerated under the LIVE one-sided-IUT framing; the Šidák figure RETAINED as the BH-over-6 sensitivity.** `scripts/power_analysis.py` gains a one-sided-IUT mode (`--mode iut_one_sided`, the default): the live per-leg test is ONE-SIDED at α=0.05 inside an intersection-union test (the IUT/conjunction IS the within-H2 correction, R25), and multiplicity across the frozen m=6 union is the LIVE Benjamini-Hochberg / Romano-Wolf — NOT a fixed Šidák-α_eff. `docs/CAMPAIGN_power.md` is regenerated reporting this as the PRIMARY minimum detectable effect, with σ_seed still flagged as the directional (pessimistic upper-bound) proxy. The pre-R25 Šidák-over-m=6 figure is **NOT deleted** — it is reported as the conservative BH-over-6 sensitivity ALONGSIDE the primary one-sided MDE (the live MDE is no larger). Report-only doc/framing change; the frozen m=6 union, the headline gate, and all hypotheses are unchanged. | `power_analysis.{PowerConfig.iut_one_sided, --mode}`; `docs/CAMPAIGN_power.md` |
| 2026-06-25 | R38 | §2, §3 | **De-seed the contract prompt (construct validity) + the `placebo_shuffled` routing fix.** The shared base prompts EVERY arm sees — `prompts/system.txt`, `prompts/initial_generation.txt`, the built-in `src/llm/prompts.py`, AND the per-candidate diversity directive in `src/llm/loop.py` — pre-seeded the tail VOCABULARY ("weigh return against … drawdown, and TAIL losses"; "rolling statistics (volatility, drawdown, tail/CVaR)"; "vary the risk-aware term (CVaR vs … drawdown …)"). So even the inert `placebo` wrote real CVaR code (≈78% of its candidates), and the H2 feedback contrast could not isolate its own mechanism (the Gupta–Hartford format-vs-content threat). The specific tail naming is REMOVED from all four sources, keeping only the general "risk-adjusted performance" task framing + "the feedback steers how to shape risk", so ONLY the distributional arm's FEEDBACK introduces the tail. The de-seeded diversity directive stays IDENTICAL across arms (no differential confound) but no longer pre-seeds the tail. Separately, a routing bug is fixed: `placebo_shuffled` (R32) was ABSENT from the hard-coded `_LLM_ARMS` tuples in `src/orchestration/parallel.py` AND `scripts/run_prototype.py`, so the 5th LLM arm would have mis-routed to the SEARCH driver in BOTH run paths — now corrected, with a drift-guard test asserting `_LLM_ARMS` == the config's LLM arms. Prompts are not in the freeze hash (not a bound config); disclosed here. | `prompts/*.txt` + `src/llm/{prompts,loop}.py` de-seeded; `_LLM_ARMS += placebo_shuffled` (×2) + `test_llm_arms_routing_tuples_match_config` |
| 2026-06-25 | R39 | §7 | **Delisting surcharge is UN-GATED (M&A bias) → `univ4` re-framed from "headline tail" to the M&A-contaminated heavy END of the band; integrity screens wired into the research panel.** Verified first-hand: Refinitiv's frozen `rf_meta_*` carries NO delisting reason and NO terminal return (fields pulled = `TR.InstrumentDelistedDate` [empty for all 333], `ExchangeName`, `TRBCSector`), so `apply_shumway_corrections` surcharges **100 % (333/333)** of delistings −30/−55 %, INCLUDING premium M&A booked at a fabricated loss (ABMD→J&J −55 %, ALTR→Intel −55 %, AGN→AbbVie −30 %, …; ~75 of 105 test-window cells; 3 of the 30 headline-cohort names — DELL/TWX/WB). The R33 "structural extreme" wording is CORRECTED: `univ4` is the M&A-CONTAMINATED upper bracket — NEITHER `univ3` (zero-fill, too light) NOR `univ4` (too heavy) is the true tail; the truth lies INSIDE the pre-registered `delisting_band`. Empirically the full d∈{0,−30,−55,−100 %} sweep moves pooled test CVaR-5 % only **~2 % (−0.0493 → −0.0504)**, so the H2 tail ORDERING is INVARIANT across the band. The surcharge CANNOT be reason-gated from the on-disk vault (R4: no fabrication); the gating logic is wired as a NO-OP until a documented re-pull (`docs/DATA_REPULL_DELISTING.md`; proven byte-identical). Separately, the datasheet-claimed **Ince–Porter + split-artifact integrity screens** ran ONLY on the yfinance pilot path — now wired into `build_universe(screen=True)` on the RESEARCH panel (+ new `forward_split_artifact_flags`), materialised as `univ3s` (returns byte-identical to univ3; flags 24 cells incl. JCI +200 %). No change to the frozen m=6 union, hypotheses, splits, budget, or fitness; loader default stays univ3. | `data_panel` note; `membership.classify_delist_reason` + `data.series.delisting_reason_classes`; `build_universe.screen_research_returns`; `integrity.forward_split_artifact_flags`; `out["delisting_band"]/["ma_contamination"]`; `docs/DATA_REPULL_DELISTING.md`; `univ3s` |
| 2026-06-25 | R40 | §12 | **Mechanical freeze ENFORCEMENT in the campaign driver.** `scripts/freeze.py` is real + tested (canonical SHA-256 over the prereg + bound configs, prose↔YAML gate, OTS), but `scripts/run_campaign.py` never called it — the by-hand `--check` was the only guard, so nothing stopped a drifted/unfrozen REAL run. `run_campaign` now calls `enforce_freeze()` (reusing `freeze.verify()` — the hash is never reimplemented) before any non-dry-run campaign: it REFUSES to launch unless `frozen: true` AND the recorded hash == the recomputed hash (drift guard), with an explicit `--allow-unfrozen` dev flag (default OFF, synthetic dev only). The canonical freeze hash is STAMPED into `campaign_summary.json`. Converts the by-hand gate into a guarantee the real run cannot bypass; no frozen quantity changes — a provenance/integrity hardening. Verified: refuses on the current unfrozen repo; `--allow-unfrozen` warns + proceeds with the hash recorded; existing dry-run/Pass-A tests untouched. | `run_campaign.enforce_freeze`; `--allow-unfrozen`; `campaign_summary.json["freeze"]` |
| 2026-06-25 | R41 | §10 | **Reward-forensics taxonomy reframed: a variance-floor / unbounded-magnitude specification-gaming class + responsiveness as the headline (report-only, DIRECTIONAL).** `scripts/inspect_rewards.py` (i) adds a first-class **`unbounded_magnitude`** class — rewards of the form `return / (variance + ε)`, unbounded above as realized variance → 0 (the critic-explosion mechanism; Skalse 2022; Pan et al. 2022) — flagged on CODE SHAPE independent of fitness (the old `specification_gaming` flag, gated on `val_fitness ≤ 0`, MISSED them: the worst offenders post POSITIVE fitness, because fitness is measured from realized `port_ret`, not the reward `total`); (ii) fixes two tautology false-positives (regex anchored to statement start); (iii) promotes **feedback responsiveness** (does reflection steer the generated code toward the fed tail signal? — measured ≈ −0.05/−0.07, the qualitative counterpart to the H2 null) to the HEADLINE forensics signal. All forensics output remains DIRECTIONAL (no number enters the inferential result; the causal H2 test is the matched-budget ablation, unchanged). Turns a null headline into a characterized "what a frontier LLM invents — and games — about tail risk." | `inspect_rewards.{unbounded_magnitude, responsiveness headline, reward_magnitude_audit}` |
| 2026-06-25 | R42 | §5, §11 | **Engine de-biasing of the FIXED SB3-SAC (NOT a design change): PopArt value-target scale-normalization + gated `learning_starts`.** The prototype showed late-training critic explosions (`anomalies.jsonl`: `critic_loss` → 1.1e7 at the FINAL step) traced first-hand to (i) LLM rewards that divide a return by a variance floored at 1e-8, emitting `|reward|` ≈ 1e4 (e.g. `scalar-g5-c3` = 1.15e4) → SAC Q-target ≈ R/(1−γ) ≈ 1e6 → the ~5e6 critic loss; and (ii) `learning_starts` left at SB3's default 100 while the Phase-0 gate validated 1000. **Fix:** (a) a PopArt-style scale normalizer (`src/agents/popart.py`) divides ONLY the critic's learning TARGET by a running √EMA[r²] — a positive affine map that leaves the optimal policy INVARIANT (van Hasselt et al. 2016); the reward stays the object of study (`norm_reward=False`; `info["port_ret"]`, fitness, tails, and ALL inference are byte-for-byte identical), applied UNIFORMLY across arms (not an H2 confound); (b) `learning_starts` resolved + floored at 1000. Both config-gated, default on / 1000. **NOT in the frozen design hash** (agent hyperparameters are not in `freeze.py::_BOUND_CONFIGS`). Proof: a variance-floor reward that diverges the critic to 1.31e9 stays bounded at ~37 with PopArt. The pre-registered `train_steps_per_candidate` is UNCHANGED; the new `scripts/learning_curve.py` informs the user's budget choice (a future amendment if the plateau sits past 50k). | `src/agents/popart.py`; `agent.{popart, learning_starts}`; `scripts/learning_curve.py` |
| 2026-06-26 | R43 | §7 | **Frozen inference scheme corrected to the EXECUTED single sealed split (closes a prereg↔code contradiction).** `config/inference.yaml` declared `scheme: walk_forward` (rolling 5y-train/1y-test) but the campaign runs ONE contiguous split (train 2005–2014 / val 2015–2017 / test 2018–2025, per §7 and `run_campaign`). The frozen scheme is now `single_sealed_split` with the executed span; the rolling parameters are demoted to a `deferred_walk_forward` future-work block. No executed quantity changes — the code already did single-split; the frozen prose now matches it. | `config/inference.yaml validation.scheme: single_sealed_split` |
| 2026-06-26 | R44 | §7 | **Headline data panel reverted `univ4` → `univ3` (the honest conservative panel; supersedes R33's headline choice).** `univ4`'s Shumway −30/−55% surcharge hits 100% of delistings incl. premium M&A (R39: no reason field on disk), FABRICATING M&A losses — training a tail-risk study on fabricated tail losses is indefensible. `univ3` (zero-fill / `liquidate_to_cash`, NO fabrication; understates rather than invents the tail) is the FROZEN headline; the `delisting_band` d∈{0,−30,−55,−100%} is the tail INSTRUMENT (univ3 at d=0, univ4 the −30/−55 heavy end), the H2 ordering invariant across it (~2% CVaR-5% sweep); `univ4r` (reason-gated re-pull) is the correct-on-re-pull ideal. The loader default is already univ3 ⇒ the campaign runs with NO `LLM_RP_GOLD_SUFFIX` override. | `config/preregistration.yaml data_panel.{headline: univ3, tail_instrument: delisting_band, band_heavy_end: univ4, correct_panel_on_repull: univ4r}`; §7 prose; `docs/CAMPAIGN_RUNBOOK.md` |
| 2026-06-26 | R45 | §1a | **Pre-registered prediction table (a-priori falsifiable commitment; epistemic basis re-named to error-statistical severity by R61).** A new §1a maps three mechanism conditions (Strict / Weak / Null) to their a-priori signatures across H2-RA (Sharpe legs), H2-Tail (CVaR-5% legs), responsiveness, and the reward-program differential, committed BEFORE the campaign reads out. The specific a-priori prediction: the λ=0 selector is tail-blind so the Sharpe legs TIE; separation appears on CVaR-5% iff feedback responsiveness > 0; the prototype's NEGATIVE responsiveness predicts the NULL branch — a pre-committed expectation, not a post-hoc narrative. (Originally labelled a "Popperian" commitment; R61 corrects the epistemic basis to Mayoian error-statistical severity + forking-paths — the commitment is unchanged.) | `PREREGISTRATION.md §1a` |
| 2026-06-26 | R46 | §4 | **EVT tail-CVaR estimator hardened: `xi ≤ −0.5` non-regular-GPD fallback + cross-candidate estimator-switch log (report-only).** `measurement.py::_evt_cvar` had a `xi ≥ 1` infinite-mean guard but none for the non-regular `xi ≤ −0.5` region (Smith 1985) where the GPD MLE is unreliable — it now falls back to empirical there, via a single `_evt_falls_back` source-of-truth the analysis-time mirror (`analyze_campaign._estimator_path`) delegates to (cannot drift). Separately, the FED headline CVaR-5% logs a WARNING the first time its `exceed_frac`-driven EVT↔empirical routing differs across candidates, making the estimator path auditable. Returned values on real returns are unchanged (the guard fires only on bounded-support loss tails). | `measurement.py::{_evt_falls_back, _record_fed_estimator, FED_HEADLINE_CVAR_LEVELS}` |
| 2026-06-26 | R47 | §10 | **Power MDE reconciled across units: Sharpe-MDE → validation-DSR-SESOI, with an explicit INCONCLUSIVE branch (report-only).** `power_analysis.py` reported MDE@80% ≈ 0.256 in annualised-Sharpe while the SESOI is 0.05 in validation-DSR — never reconciled. A documented conservative delta-method ceiling (`sharpe_mde_to_dsr`, PSR max-sensitivity at z=0, T=756 val sessions) maps 0.256 Sharpe → **0.177 DSR ≫ 0.05 SESOI**, so a Sharpe non-rejection alone licenses only INCONCLUSIVE unless the TOST 90% CI computed *in DSR units* lands inside ±0.05. `docs/CAMPAIGN_power.md` regenerated (headline figures byte-identical; the reconciliation is additive). | `power_analysis.sharpe_mde_to_dsr`; `docs/CAMPAIGN_power.md` |
| 2026-06-26 | R48 | §5, §11 | **PopArt scale-dependence made AUDITABLE + a robustness ablation (refines R42; report-only).** R42's PopArt scaler is "uniform across arms" in MECHANISM, but the realised divisor `sigma = √EMA[r²]` (clamped ≥1) differs across arms when authored rewards differ in magnitude, and `ent_coef="auto"` re-adapts to the normalised scale — a latent scale-driven entropy-regularisation difference. Two report-only safeguards: every training path now logs the realised per-candidate `sigma_max`/`sigma_last` into the candidate AND test records (`sigma_max == 1` ⇒ the wrapper was the identity ⇒ no confound), and `scripts/popart_ablation.py` re-evaluates the frozen winners with `popart=False` at one seed and reports whether the H2 ordering (Sharpe + CVaR-5%) is preserved. `info["port_ret"]`, fitness, tails, all inference byte-identical; not in the freeze hash. | `popart.realized_scale_stats`; `popart_scale` in candidate/test records; `scripts/popart_ablation.py` |
| 2026-06-26 | R49 | §1, §10 | **H1 "beat-the-human" is data-snooped on the comparator → demoted to DESCRIPTIVE-ONLY with an unmissable warning.** `run_campaign._baseline_winner_record` archives `val_fitness=NaN` and no `val_returns`, so the best-of-4 human-bar identity falls back to selection on the SEALED test leg (a comparator data-snoop, White 2000). H1 therefore carries NO inferential beat-the-human claim here; `beat_human_baseline` now emits a structured `inference_status` (`val_selected` | `test_snooped_descriptive_only`) + `caveat`, and the H1 panel surfaces a prominent ⚠️ WARNING at the TOP (was a buried bullet). *Future remedy:* roll each baseline on validation so it archives `val_returns`, restoring the pre-committed Dunnett-valid val-selected bar the analysis already prefers when present. | `analyze_campaign.beat_human_baseline.inference_status`; `h1_beat_human_markdown` warning |
| 2026-06-26 | R50 | §1 | **H3/H4 equivalence symmetrised + references named (report-only, DISJOINT).** H4 gained a per-leg ±0.05 TOST equivalence bound (mirroring H3's existing TOST) so a non-rejection reads as a bounded null; H4a/H4b are promoted to NAMED references (in-family / fixed-template) so H4 reads procedure-vs-richness, not a nested horse-race; and H3 adds a paired placebo-relative uplift difference ([iter−ss]_dist − [iter−ss]_placebo) so a null reads as "reflection left no tracking signature beyond content-free reflection." All under `out["h3"]`/`out["h4"]`; the frozen m=6 union is untouched. | `analyze_campaign.{h4_search_controls TOST, _H4_REFERENCE_FRAMING, _h3_placebo_relative_uplift}` |
| 2026-06-26 | R51 | §10 | **Reward-program differential forensics — the mechanism loop made measurable (report-only, DIRECTIONAL).** `inspect_rewards.reward_program_differential` quantifies, per arm, the tail-construct prevalence / declared components / CVaR levels / coefficient magnitudes the LLM actually wrote. Honest scope: per-step component VALUES are not persisted, so only DECLARED structure is read (no fabricated runtime activity). The prototype finding: distributional references FEWER tail constructs (1.69/program) than scalar (2.02), placebo (1.90), or scalar_cvar5 (2.23) — a mildly NEGATIVE cross-arm tail differential that is the expected fingerprint of the R38 prompt-leak (the shared prompt pre-seeded the tail to every arm), exactly the confound the de-seeded campaign removes. Distributional separates on FORM (quantile/drawdown primitives; hard-coded CVaR level on 35/39 vs scalar 13/40). | `inspect_rewards.reward_program_differential` |
| 2026-06-26 | R52 | §2, §12 | **Sandbox from-import RCE closed + freeze line-ending invariance hardened (security/integrity).** (1) `sandbox/executor.py::ast_gate` checked only the ROOT module of `from X import Y`, so `from numpy import load` (numpy allowlisted) passed and `load(...)` became a BARE name the `_BANNED_ATTRS` allowlist never inspected → the `np.load` pickle-RCE the banlist exists to stop (confirmed end-to-end). All `from … import` (and wildcard) are now forbidden — reward code only needs `import numpy as np`; regression-tested. (2) `freeze.py::_normalize_bytes` now collapses any CR-run + optional LF to one LF, so the canonical hash is invariant to a doubled `\r\r\n` (Windows-dev ≡ Linux-campaign); the canonical hash is UNCHANGED for real files. | `executor.py ast_gate`; `test_audit_regressions`; `freeze.py::_normalize_bytes` |
| 2026-06-26 | R53 | §3 | **Novelty / citation / proposal honesty (integrity).** (1) The fed vector is six left-tail scalars, so the README construct is retitled "realized-return DISTRIBUTION" → "multi-level tail-risk feedback" with a what-is/isn't-in-the-vector disclosure (the theory-spine distributional-sufficiency argument is untouched). (2) DLM (Behari et al. 2024, NeurIPS) — the nearest neighbour — is cited and DISTINGUISHED on four deltas (object: population-across-states vs return-tail; the off-critic 3-way decoupling; financial domain; pre-registered identifiability); Khraishi–Okhrati fixed to its ICAIF '22 record + DOI; 8 near-misses (OPRO/GEPA/CARD/Singh/Sorg/IRD/Qu) added `% VERIFY`. (3) `PROPOSAL_PIVOT_DISCLOSURE.md` rewritten as a supervisor-approved CHANGE OF RESEARCH QUESTION (the docx is a 10-component FinBERT-sentiment framework with zero reward-design content — a near-total replacement, not "narrowing"); `docs/RIGOUR_LEDGER.md` added. | `README.md`; `paper/refs.bib`; `docs/{PROPOSAL_PIVOT_DISCLOSURE,RIGOUR_LEDGER}.md` |
| 2026-06-26 | R54 | §3, §12 | **Frozen arm roster reconciled to SEVEN + a fail-loud freeze guard (7-agent verification-pass V1/V16).** The frozen `config/preregistration.yaml arms` listed SIX (it dropped `placebo_shuffled`, the R32 structure-vs-content control) while `campaign.yaml`, the arm factory, and the campaign run SEVEN — and `freeze.py` never checked the roster, so the hash would have bound a 6-arm design while a 7-arm campaign ran, the missing arm being the headline construct-validity control. Restored `placebo_shuffled` to the frozen roster + §3 ("six"→"seven arms", with the m=6 testing family explicitly noted as fed by only the four {distributional, scalar, placebo, scalar_cvar5}); added an arm-roster check to `assert_prose_matches_yaml` (every frozen arm named in prose + the §3 count word == len(arms)) and a `test_config_arm_rosters_match_factory` drift guard (preregistration.yaml == campaign.yaml == factory); plus a direct `_normalize_bytes` doubled-`\r\r\n` unit test (V16). The m=6 family is UNCHANGED. | `config/preregistration.yaml arms`; §3; `freeze.py` arm guard; `test_arms`/`test_freeze` |
| 2026-06-26 | R55 | §3, §5, §7, §11 | **Honest-framing reconciliation of the R43–R53 burst (V4/V5/V6/V8/V12/V17/V19; no science change).** §7 LEAD rewritten univ4→**univ3** as the headline (the paragraph had self-contradicted); `docs/RIGOUR_LEDGER.md` extended R42→R53 (it omitted itself) with the R33→R44 supersession; `loaders.py` docstrings corrected to univ3-default/no-override; the stale "distributional CVaR p≈0.004 bankable" claims in `docs/DEEP_H2.md`/`EXAMINER_grade_audit.md` annotated with the placebo REVERSAL (distributional tail worse than the zero-info placebo, p=0.0005 — a directional null, reversed under control); the estimator reframed **critic-agnostic ≠ agent-independent** with an endogeneity disclosure (the fed tail is fit on the policy's own returns under the candidate reward; H2 compares coupled reward→policy→measurement loops) in `measurement.py`/`CLAUDE.md`; the measurement input relabelled "log-return"→"simple (arithmetic) return" (env emits no `log1p`; numerics unchanged); run-count re-tallied 6×30≈180 → **7×30≈210** + the H1/H3 stages (exact tally via `compute_accounting`); the unbound `data_pipeline/config/inference.yaml` banner-marked SUPERSEDED. (V2 "implies executed placebo_shuffled results" = FALSE POSITIVE — docs already frame it as pending.) | §7 lead; `docs/{RIGOUR_LEDGER,DEEP_H2,EXAMINER_grade_audit}.md`; `loaders.py`/`measurement.py`/`CLAUDE.md`; §5 prose |
| 2026-06-26 | R56 | §5, §8 | **Agent-fidelity + single-model disclosures (V7/V10).** (i) "Fixed agent" reworded to **fixed ARCHITECTURE + hyperparameters; the effective entropy regularisation can vary with authored reward magnitude** (PopArt σ clamped ≥1 is magnitude-dependent; SAC `ent_coef="auto"` re-adapts to the normalised scale), made auditable by the per-candidate σ_max logging (R48) and bounded by the `popart=False` ablation (both pending the campaign run) — docstrings only, no numerics change. (ii) §8 open-weights cross-model check disclosed as **SPECIFIED-but-UNEXECUTED** (`open_weights_check_model: "PIN_ME"`; `cross_model_disagreement` returns `no_data`/`executed:false`); the study runs only the single Claude family (Sonnet 4.6→Opus 4.8, same vendor/key), so plural "LLMs"/"models" for the authored rewards denotes that one family; a second-model run is a deferred decision. | `popart.py`/`trainer.py` docstrings; `config/llm.yaml`; `contamination.py`; §8 |
| 2026-06-26 | R57 | §7 | **`delisting_band` pinned to the univ4 audit so the headline tail instrument produces numbers under the univ3 default (V3 — a real regression from R44).** Post-R44 the band resolved its suffix via `gold_suffix()`=univ3 and tried to load `shumway_audit_log_univ3.parquet` (which does not exist; only `…_univ4.parquet` carries the 333 Shumway cells) → it silently `status="skipped"`, so the load-bearing "ordering invariant across the band" evidence produced NOTHING. Pinned via `DELISTING_BAND_AUDIT_SUFFIX="univ4"` (decoupled from the headline default). Arg-less now: 105 test-window cells, pooled CVaR-5% −0.04934 (d=0 ≈ univ3 liquidation end, not byte-identical) → −0.05041 (d=−1), real univ4 (−0.04974) INSIDE the band — the ~2% sweep / invariant ordering now substantiated. Report-only. | `analyze_campaign.delisting_band` (`DELISTING_BAND_AUDIT_SUFFIX`, `cells_source`/`brackets_to`) |
| 2026-06-26 | R58 | §1, §10 | **Report-only analysis hardening (V9/V11), DISJOINT from the frozen m=6.** (i) `h2_tost_dsr`: the bankable-null TOST is now also computed in the SESOI's own **validation-DSR units** (±0.05) via the documented conservative Sharpe→DSR ceiling (`power_analysis.sharpe_mde_to_dsr`, k=0.6905 at T=756, then `tost_equivalence`), so a campaign non-rejection actually evaluates the equivalence `docs/CAMPAIGN_power.md` requires (RA-only; CVaR stays in the Sharpe-units `h2_tost`); a non-equivalent verdict reads INCONCLUSIVE. (ii) The reward-program tail-construct differential (R51) now pools the LLM arms ONLY; `random_search`/`bayes_opt` (fixed tail-construct skeleton, constant tail-count, only coefficients vary) are reported separately as fixed-skeleton descriptors — removing a category error. LLM-arm numbers unchanged (distributional 1.692 / scalar 2.025 / placebo 1.900 / scalar_cvar5 2.225). | `analyze_campaign.h2_tost_dsr`; `inspect_rewards.reward_program_differential` |
| 2026-06-26 | R59 | §2 | **Untrusted-reward boundary hardened against cross-candidate state corruption (V15/V14).** Proven first-hand: a reward doing `returns[:]=0` aliased and ZEROED a row of the SHARED frozen panel (`np.shares_memory`), `weights[:]=…` leaked into the env's `w_prev`, and `info[...]=…` polluted the env dict — a determinism / no-cross-contamination violation (not an RCE). Fix: the realized-return row is COPIED (not a panel view); `returns`/`weights`/`prev_weights` handed to the reward READ-ONLY (`setflags(write=False)`) with a shallow-copied `info`; the env keeps its own writable copies (logging byte-identical). **Benign-reward numerics proven unchanged.** Separately, `np.seterr` removed from the sandbox allowlist (process-global float-error-mode leak across candidates; leak-free `np.errstate`/`np.geterr` retained). Disclosure: the frozen softmax projection cannot reach an exact cash corner (damps flee-to-cash equally across arms — a shared ceiling, not an H2 confound). | `env/portfolio_env.py`; `sandbox/executor.py` (`seterr` removed) |
| 2026-06-26 | R60 | §4, §10 | **FZ0/ES tail-corroboration backtest given a small-sample correction + size/power calibration (V13 — the supervisor small-sample point).** The Diebold-Mariano-style FZ0/(VaR,ES) comparative backtest (`comparative_es_backtest`, corroborating H2-Tail) had no small-sample correction and no certified size. Added the Harvey–Leybourne–Newbold (1997) correction as a closed-form classical-DM **companion** (statistic ×√[(T+1−2h+h(h−1)/T)/T], referenced to Student-t(T−1)) alongside the existing HAC stationary-bootstrap p-value (corrected = the conservative headline); and `dm_size_power_calibration`, a deterministic Monte-Carlo certifying empirical size/power at the realised window length (i.i.d. h=1: T=60 size 5.5%→4.9% HLN; under dependence AR1=0.3/h=5: 7.9%→7.3%, power 0.48→0.98). A latent near-zero-variance DM-SE guard bug fixed in passing. Report-only; does not gate m=6. | `es_backtest.py` (`hln_factor`, `dm_hln_test`, `dm_size_power_calibration`) |
| 2026-06-28 | R61 | §1a, §4, §10 | **Pre-freeze methodology upgrade: tail-uncertainty propagation + epistemic re-basing (deep-research-verified).** (a) EPISTEMIC: the null's basis is re-named from "corroborated Popperian prediction" to **Mayoian error-statistical severity** (licensed by the frozen deviation-free protocol; pre-registration does NOT improve *Popperian* severity — Rubin 2025, Synthese arXiv:2408.12347) **+ garden-of-forking-paths avoidance** (Gelman & Loken 2014), reported via the existing TOST/SESOI equivalence (Lakens et al. 2018; Campbell & Gustafson 2018) — the commitment in §1a is unchanged, only correctly named. (b) METHODOLOGY (added pre-results, so part of the confirmatory apparatus, not post-hoc): the CVaR point estimate is now accompanied by an honest uncertainty report — **stationary-block-bootstrap CVaR confidence intervals** (`ReturnDistribution.cvar_ci`), a **bootstrap bias estimate** (`cvar_bias`; verified verdict: analytic≈bootstrap, neither superior — error is variance-dominated at n≈750, so report not correct), an **exceedance-count reliability tier** (`reliability`; Belzile-Davison 2022 small-sample), and the combined `cvar_uncertainty_report`. ALL additive + DETERMINISTIC (seeded block bootstrap; numpy PCG64) and report-only: the **fed feedback block values + all m=6 inference are byte-identical** (the fed block is NOT enriched with the CI by default — that is an arms-parity-gated option). (c) GARCH-EVT (conditional McNeil-Frey two-stage) was INVESTIGATED and **REJECTED**: validated on single-asset not aggregated-portfolio returns, adds model-risk at n≈750/few exceedances, and `arch` GARCH MLE is not byte-identical cross-platform (optimizer convergence) ⇒ breaks the determinism guarantee — retained only as a Future-Work A/B. Pre-freeze design improvement ⇒ the canonical freeze hash recomputes (still `frozen:false`; USER flips). | `measurement.py` (`cvar_ci`, `cvar_bias`, `reliability`, `cvar_uncertainty_report`); `docs/{ANALYSIS_METHODS_AND_FUTURE_WORK,EXAMINER_OBJECTIONS_AND_DEFENCES}.md`; `tests/test_measurement_uncertainty.py` |
| 2026-06-28 | R62 | §12 | **Treatment text bound into the freeze hash (closes the unhashed-manipulated-variable gap; deep-audit 2026-06-28).** The canonical SHA-256 covered the prose + prereg-yaml + the three executed configs (inference/environment/data) but NOT the files that DEFINE the manipulated variable: `config/arms.yaml` (the per-arm feedback spec) and the two LOADED prompts `prompts/system.txt` + `prompts/initial_generation.txt` — so the treatment could change post-freeze without tripping `freeze.py --check`. A new `_BOUND_TREATMENT` tuple binds their CONTENT into the hash (after the bound configs, in a fixed documented order); the pre-commit + CI drift-guard globs and the docstrings are updated; `arms.yaml` remains additionally roster-checked. `prompts/reflection.txt` is excluded (dead — no runtime path loads it). The canonical hash recomputes (still `frozen:false`; USER flips). | `freeze.py::_BOUND_TREATMENT`; `.pre-commit-config.yaml`/`ci.yml` globs; `tests/test_freeze.py` |
| 2026-06-28 | R63 | §2 | **Dead `prompts/reflection.txt` banner-marked (examiner grep-trap; cosmetic).** The file is not loaded at runtime (the reflection turn is built in-code from `_REFLECTION_PREAMBLE` + `schema.build_block`) yet is tail-saturated, so a reviewer greps `prompts/` and may wrongly infer all arms are tail-primed. A prominent ARCHIVED/DEAD banner now caps it, stating it is illustrative-only and excluded from the freeze hash. No code path changes. | `prompts/reflection.txt` banner |
| 2026-06-28 | R64 | §10 | **Headline one-sided leg p computed DIRECTLY from the bootstrap tail (corrects the symmetry-assuming half-of-two-sided on the skewed CVaR leg).** The two co-primary IUT legs are decided ONE-SIDED in the predicted direction; the analysis layer derived the one-sided p by halving the symmetric two-sided p, which equals the true upper-tail probability ONLY under a symmetric bootstrap and departs from it under ANY skew of the CVaR-difference bootstrap — potentially flipping the bankable tail leg at the decision threshold. `paired_seed_difference_test` now returns `pvalue_one_sided_greater` = the direct upper-tail probability `P(boot − obs ≥ obs)`; `collect_family_pvalues._one_sided` and the H3/H4 helpers use it (the in-direction gate unchanged). Pre-freeze inference-implementation correction; the METHOD (one-sided intersection-union test) is unchanged. | `bootstrap.paired_seed_difference_test["pvalue_one_sided_greater"]`; `analyze_campaign._one_sided`/`_one_sided_from_two` |
| 2026-06-28 | R65 | §9, §10 | **DSR saturation bug fixed — `expected_max_sharpe` returned −∞ for a single un-searched trial, pinning every benchmark/winner DSR at 1.0.** The guard read `n_trials <= 0` but the documented contract (and the maths) require `n_trials <= 1` to return the no-multiplicity benchmark 0.0: with one trial `norm.ppf(1 − 1/1) = ppf(0) = −∞`, so `sr_star = −∞` and `deflated_sharpe_ratio(x, n_trials=1) == 1.0` for ANY series — even a strongly NEGATIVE-Sharpe one. This silently broke the H1/T0 benchmark-FLOOR gate (every un-searched benchmark DSR saturated to 1.0, so the frozen winner could never strictly clear the floor) and the report-only `winner_dsr_undeflated_n1` value. Fixed to `n_trials <= 1`; a negative-Sharpe series now correctly scores DSR≈0. No frozen-design quantity changes — a correctness fix to a pre-registered diagnostic; the previously-red floor-gate test is now green. | `deflated_sharpe.expected_max_sharpe` (`n<=1`); `test_campaign_inference` floor gate |
| 2026-06-28 | R66 | §5, §11 | **Two correctness/disclosure hardenings (report-only).** (i) SAFE_DEFAULT accounting: the sandbox `candidate_failed()` boolean is LAST-call only (a later success clears it, by design), so an intermittently-failing reward that recovers on the final rollout step was invisible; new accumulating counters (`safe_default_count`/`safe_call_count`, reset per rollout) surface + quantify every substitution, and `src/env/runner.py` now warns on the COUNT (with the substitution fraction) instead of the last-call flag. (ii) Determinism: `set_global_seed` sets `CUBLAS_WORKSPACE_CONFIG` EXPLICITLY (a pre-existing NON-deterministic value formerly survived via `setdefault`, silently defeating reproducible cuBLAS on the campaign GPU), preserving an already-deterministic ":16:8"; and the `PYTHONHASHSEED` comment is corrected (it governs spawned-child workers, not the current interpreter). Byte-identical benign-reward numerics; not in the freeze hash. | `executor.{safe_default_count,safe_call_count}`; `runner.py` warning; `utils/seeding.py` |
| 2026-06-28 | R67 | §1, §10 | **(RATIFIED 2026-06-28, user-delegated: prior `r = sqrt(2)/2`, ROPE = the frozen equivalence margin, robustness curve over `r ∈ {0.5, sqrt(2)/2, 1, sqrt(2)}` — a confirmatory complement to TOST.) Bayesian evidence-FOR-the-null complement to TOST (report-only, DISJOINT from the m=6 family).** A pre-registered METHODOLOGY upgrade, not a new hypothesis: the SAME paired per-seed difference the headline IUT already consumes is additionally expressed in a Bayesian frame to give POSITIVE evidence for practical equivalence — a JZS default Bayes factor `BF01` (Rouder et al. 2009) with a prior-free BIC cross-check (Wagenmakers 2007), a conjugate-Student-t posterior + ROPE mass, and a 90% HDI⊂ROPE decision (Kruschke 2018) that mirrors the existing 90% TOST interval — directly answering the "informative or merely underpowered?" attack TOST alone cannot (Lakens et al. 2020; Campbell & Gustafson 2024 show TOST/HDI-ROPE/interval-null-BF reverse-engineer one another at matched error, so agreement across the two machineries severely tests the null). Report-only; never gates the frozen testing family; pure scipy/numpy, deterministic, NO new dependency. The single researcher degree of freedom — the Cauchy prior scale — is PINNED to `r = sqrt(2)/2` (BayesFactor "medium") with a MANDATORY robustness curve over `r ∈ {0.5, sqrt(2)/2, 1, sqrt(2)}` (the null is "supported" only across the whole band; an un-pinned prior would manufacture null evidence by Bartlett's / the Jeffreys–Lindley paradox, `BF01 → ∞` as `r → ∞`), and the ROPE reuses the already-frozen equivalence margin. **USER must ratify the pinned prior `r` (and that the ROPE = the frozen equivalence margin) BEFORE the freeze for this to be confirmatory; otherwise it is reported as a disclosed exploratory appendix.** | `src/inference/bayes_null.py` (`bayesian_null_report`); `tests/test_bayes_null.py` |
| 2026-06-28 | R68 | §10 | **Reward-code STRUCTURAL similarity — report-only mechanism enrichment (DISJOINT from the m=6 family).** An identifier- and literal-invariant test of whether the LLM routes the fed tail signal into the *structure* of the reward code it writes (not merely cosmetic tokens, which the `placebo`/`placebo_shuffled` controls already neutralise): each reward's AST is canonicalised (variable/argument names AND constant VALUES discarded — only the node-type structure survives), its depth-bounded canonicalised subtree shapes are enumerated (the AST Distinct-N / TSED family), and pairwise Jaccard similarity is computed, with the headline statistic the mean WITHIN-condition vs ACROSS-condition structural similarity and a DETERMINISTIC seeded label-permutation p-value. A stronger, identifier-invariant companion to the reward-program differential (R51) that closes the placebo construct-validity gap the deep audits flagged. Pure standard-library `ast` (+ numpy, present), deterministic, NO new dependency; report-only, never gates the frozen testing family. | `src/inference/reward_code_distance.py` (`reward_code_structure_report`); `tests/test_reward_code_distance.py` |
| 2026-06-28 | R69 | §10 | **Model Confidence Set over the arms — report-only multiplicity-honest ranking (DISJOINT).** The Hansen–Lunde–Nason (2011) MCS returns the set of arms statistically indistinguishable from the best at level `size`, correcting for ALL pairwise comparisons at once — a multiplicity-aware companion to the H2 IUTs whose shape exactly fits the predicted null (no dominant arm → the set contains nearly all arms, the honest corrected "indistinguishable" statement). Computed on the PER-SEED scores (the same per-seed Sharpe / CVaR values the rliable IQM and the headline IUT consume, so the inferential unit matches the stack), loss = negated metric, `method='R'`, with the level and seed PINNED. Built on `arch` (an EXISTING dependency — already the StationaryBootstrap / optimal_block_length oracle in `tests/test_inference_crosscheck.py`), DETERMINISTIC via the pinned seed, `block_size=1` (i.i.d. seeds), no model fit (none of the McNeil–Frey optimiser non-determinism the team rejected). Report-only; never gates the frozen family; pre-registered as a secondary descriptive ranking with its per-seed-Sharpe (risk-adjusted) and per-seed-CVaR (tail) losses pinned. (The Andrews–Kitagawa–McCloskey winner's-curse CI was CONSIDERED and is not adopted: the fed→select→test decoupling selects on validation and reports on the SEALED test, so the headline estimate carries no winner's curse — a strength to state, not a gap to patch.) | `src/inference/model_confidence_set.py`; `tests/test_model_confidence_set.py` |
| 2026-06-29 | R70 | §5, §6 | **Train-to-convergence: `train_steps_per_candidate` set at the OBJECTIVE convergence knee (activates the R42-anticipated amendment; user-approved).** The per-candidate budget (was 50k, set from Phase-0 TIMING not convergence) is replaced by the budget at the held-out eval-return PLATEAU, chosen by a pre-registered, eyeball-free criterion (`scripts/learning_curve.py::recommend_budget`): the smallest budget past which the seed-median held-out eval-IQM is flat within 3% of the curve's range AND the critic loss is finite, all the way to the ladder ceiling — with the ladder EXTENDED (default 50k→800k, higher on demand) until the detector reports CONVERGED (it loudly flags "still rising at the ceiling" = under-trained, demanding a higher ceiling). This neutralises the single biggest threat to the corroborated null — that the H2 contrast measures under-training noise rather than the reward (audit B-5) — which is also the dominant publishability risk. SAME fixed budget across all arms (not an H2 confound); the explosion-fixed agent (R42 PopArt + gated `learning_starts`) means longer training CONVERGES rather than re-diverges. The chosen number is RECORDED here once the operator runs the ladder on the campaign GPU; the laptop is run 24/7 to afford it, scaling to UCL if the knee sits very high. | `scripts/learning_curve.py` (`recommend_budget`, +5 tests); `agent.train_steps_per_candidate`; `tests/test_learning_curve.py` |
| 2026-06-29 | R71 | §8 | **Multi-model SECONDARY robustness panel — activates the R56-deferred open-weights second model (user-delegated decision; grade-first scoping).** The single Claude family (Opus 4.8) train-to-convergence run REMAINS the confirmatory headline; a second, different-family LLM designer is added as a PRE-REGISTERED SECONDARY (exploratory, NOT co-primary) panel that (a) makes the plural "LLMs" genuine and (b) executes the N3 contamination cross-check (`cross_model_disagreement`). Compute-bounded scope: the second family authors rewards on the HEADLINE arms only (distributional, scalar, +placebo) at REDUCED seeds, reported as a robustness/generalisation panel — NEVER folded into the m=6 confirmatory family or the H2 IUTs. Rationale: a FULL second *confirmatory* family on the laptop would force the agents back into UNDER-training (sabotaging the R70 convergence lever, the #1 grade move); the headline stays clean + laptop-feasible while the secondary panel scales to the full design on UCL. Authoring is cheap API calls (only the SAC training of the winners adds compute, scoped down), so the second model is a commit-pinned, different-training-cutoff OPEN-WEIGHTS model (`open_weights_check_model`, set from `'PIN_ME'`; recommended Qwen2.5-Coder family — strong code authorship, Apache-2.0, non-Anthropic vendor/cutoff). **PIN EXECUTED 2026-07-02: `qwen/qwen3-coder` via OpenRouter** (provider wiring + key-gated smoke built + tested; served-snapshot anchor archived at first live call; see the §8 V10 note). Conditional on compute; run when UCL/extended time allows. | `config/llm.yaml` (`open_weights_check_model`); `src/inference/contamination.py`; §8 |
| 2026-06-29 | R72 | H1; related work | **H1 "beat-the-human" baseline integrity + the related-work novelty fence (pre-freeze, from the deep resource sweep).** (a) `raw_return` is NAMED as the field-standard FinRL-default net-wealth reward and cited (Liu et al. 2020 arXiv:2011.09607; 2021 arXiv:2111.09395) so the human panel visibly contains the most-cited DRL-finance reward as the FLOOR (the binding "human bar" in H1's max-over-panel stays `return_minus_cvar`/`differential_sharpe`). (b) The `differential_sharpe` CITATION is CORRECTED: canonical = Moody & Saffell (2001) IEEE TNN 12(4):875-889 (primary) + Moody, Wu, Liao & Saffell (1998) J. Forecasting 17(5-6):441-470 (the four-author derivation); the prior "Moody & Saffell 1998" conflated them. (c) Disclosure (DEEP_H1 T-UNTUNED): the canon trains at canonical defaults (λ=1.0/η=0.1/α=0.05) because the env injects no per-reward params — stated as "evaluated at canonical defaults, not re-tuned" (a budget-matched validation tune remains an open option). (d) The novelty cell is TRIPLE-confirmed EMPTY (exhaustive 2023-26 scoop sweep); the nearest-neighbor fence — FinRL-DeepSeek (2502.07393, LLM-as-signal not reward-author), Eureka (2310.12931), Behari Decision-Language-Model (2402.14807, reward-code + a distribution but public-health RMAB not finance), LEARN-Opt (2511.19355, a methodological ally), Qu et al. (2509.18719, fraud not portfolio) — is added to related work, with the wording guardrails "first reward-CODE synthesis for a TRADING/PORTFOLIO agent" and "distribution of realized OUTCOMES vs Eureka's reward-COMPONENT point statistics". | `src/baselines/rewards.py`; `docs/CAMPAIGN_benchmarks.md`; `docs/LIT_gap_llm_reward_optimizer.md`; `refs.bib` |
| 2026-07-02 | R74 | §5, §6 | **B\* = 200,000 set from the Split-C convergence pilot — amends R70's termination criterion, which is structurally unsatisfiable on this workload (pre-freeze; evidence-cited).** R70 committed to "extend the ladder until the knee detector reports CONVERGED". The executed pilots reveal that commitment cannot terminate: the held-out eval-IQM is **flat within seed noise across the full 25k→350k ladder** (14× budget range) on BOTH the pre-Split-C ladder and the clean Split-C rerun (3 seeds, uniform max-power conditions), and the detector's plateau tolerance is *relative to the curve's own range* — on a flat-noise curve the range IS the noise, the tolerance collapses, and every run returns "no confirmed plateau" regardless of extension (verified branch-analysis of `recommend_budget`; two independent ladders reproduce it). The under-training threat R70 exists to neutralise (audit B-5) is therefore answered by the totality of evidence rather than the single blind criterion: (i) eval outcome flat/noise across all budgets — no signal improves past the small-budget region; (ii) the critic's terminal loss completes its steep descent **by 100k** (seed-median ≈0.59→0.10; only internal polish thereafter, →0.01 at 350k); (iii) 350k evals are nominally WORSE than 200k (the mild-overfit direction the old-window pilot measured independently); (iv) finite-data regime: ≈17 full passes over the train window at 200k with the 50k buffer — past-knee steps memorise the single realised path. **Decision: B\* = 200,000** — ≥2× the critic-descent knee, eval-indistinguishable-from-or-better-than the 350k ceiling, below the measured overfit onset — IDENTICAL across all arms (identification preserved; matched compute). Mirrors: `config/campaign.yaml` + `config/algos.yaml` (the preflight budget-mirror guard asserts the pair) + the machine mirror below. Dossier archived: `outputs/tables/learning_curve.json` (Split-C, Turbo-uniform) + `learning_curve_baseline_preTurbo_2026-07-01.json`. `determine_design` reports the parameter **DECIDED** (diagnostic disclosed — the same honest semantics as `candidates_per_arm`); the σ_D pilot (2 rewards × 15 seeds at B\*) adds 30 further stability observations at 200k before the freeze. | `config/campaign.yaml`; `config/algos.yaml`; `config/preregistration.yaml`; `scripts/determine_design.py`; `outputs/tables/learning_curve.json` |
| 2026-07-02 | R73 | §7 | **SPLIT C EXECUTED + the univ5 panel (ADR-044 ratified 2026-07-01; ADR-051 execution — pre-freeze, never results-contingent).** The panel extends to the SETTLED 2026-06-30 cutoff and rebuilds as `univ5` (5,406×963): splits move to **train 2005–2016 / val 2017–2019 / test 2020–2026H1**. Integrity gates all PASSED: (a) the 2005–2025 overlap vs frozen `univ3` is **byte-identical (0 changed cells)**; (b) the frozen membership record stays authoritative for its span (SPLICE rule; the `EVHC.N^L16` vendor event-revision was caught by the overlap gate, externally verified immaterial — never top-30 — and allowlisted); (c) the OBSERVED-terminal recovery booked the realised terminal for **all 333 dead names (zero surcharges)** → the corrected Shumway `univ5s` equals the zero-fill headline on returns, exposing `univ4`'s surcharge as terminal double-counting + M&A contamination (the band keeps `univ4` as its disclosed contaminated heavy end). `expected_windows.univ5 = [60,3021]/[3081,3775]/[3835,5406]` recorded; `gold.suffix: univ5`; FRED macro refreshed to the cutoff (`fred_macro_x26`). | `config/{data,inference,preregistration}.yaml`; `src/data/loaders.py`; `scripts/run_campaign.py`; `data_pipeline/scripts/{extend_universe_2026,refresh_fred_2026,build_univ5,purge_suffix}.py`; DECISIONS ADR-051(+addendum) |
| 2026-07-04 | R75 | §4, §7, §10 | **Pre-freeze WORDING corrections (NO decision changed).** Three claims in the frozen-design text were tightened to be factually exact before the freeze; no hypothesis, split, SESOI, seed, arm, budget, λ, or the Troop-deferral DECISION is altered — only accuracy. (a) §10 leg-decision: the `p_one = p_two/2` line is annotated **(superseded by R64)** — the leg p is the direct upper-tail bootstrap probability `pvalue_one_sided_greater`, not half the two-sided p (R64 already made the code change; this supplies the missing cross-reference). (b) §4 EVT: the "GPD ξ ≤ 0 for ~94% of samples" rationale for deferring Troop et al. (2021) is reworded as a SMALL-SAMPLE NEGATIVE-BIAS fact at n ≈ 750 (the GPD-MLE systematically UNDER-estimates the shape ⇒ the estimate is centred ≤ 0 even for a genuinely heavy tail; the ≈ 0.14 asymptotic shape SE at ~75 exceedances does not overcome the bias), NOT a claim that portfolio losses are light-tailed — diversifying regularly-varying constituents preserves the tail INDEX, so the underlying loss tail stays genuinely heavy; the deferral now rests on small-sample bias + Troop's heavy-tail/large-sample validated scope, holding regardless of the true tail-index sign (matches DEEP_H2 §6.2). (c) §7 test-regime: "COVID" is tightened to "post-COVID-crash recovery + elevated-vol regime" in `config/inference.yaml` + this file — the 19 Feb–23 Mar 2020 crash falls INSIDE the val→test purge, so the SCORED sealed-test outcomes begin post-crash (~2020-03-30), mirroring the already-correct CH4 §4.2 disclosure. Pre-freeze wording ⇒ the canonical freeze hash recomputes (still `frozen:false`; USER flips). | `config/inference.yaml`; `PREREGISTRATION.md` §4/§7/§10; §7 mirrors CH4 §4.2, §4 EVT mirrors DEEP_H2 §6.2 |
| 2026-07-11 | R76 | §2a(f), §2a(h) | **A5 RATIONAL-INSENSITIVITY account added to the mechanism fingerprint + the fed-delta SNR/attenuation exhibit (report-only, pre-freeze, PRE-DATA — no campaign data exists).** A SQ1-null admits a fifth rival account: the fed block carries point estimates with NO uncertainty annotation, so a designer that discounts small decimal deltas as probable estimation noise behaves *defensibly* — an epistemic-stance result, not a numeracy deficit (a materially different conclusion from A2/A3, so it must be named ex-ante). Quantitative anchor (measured 2026-07-11, univ5 train window, EW-30 proxy, stationary-block bootstrap): marginal fed-CVaR-5% SE ≈ 0.0033, but candidate differences are PAIRED on the common market path → paired diff-SE ≈ 1e-4 (sibling books) to 8e-4 (distant books), so typical fed deltas straddle the resolvability boundary. Fingerprint (f) extended 4→5 accounts with A5's registered signature; the A5-vs-A2 discriminator = the CI-/significance-annotated re-rendering (D2+ (iv), Stage-2 adjudicator; the format-only differential remains the A2 ablation); M2 separates ability from stance. New instrument (h): the fed-delta SNR + responsiveness-attenuation exhibit — resolvable-signal share, errors-in-variables λ_att with a disattenuated SQ1 SENSITIVITY (never the primary), and SNR-conditioned responsiveness (the A5 row); archive-computed via the R61 `cvar_ci` machinery, validation/train data only, outside every confirmatory family. NO frozen quantity changes (hypotheses, m=6, arms, seeds, SESOI, splits, budgets all untouched — report-only interpretation scaffolding in the exact spirit of (f)). | `mechanism.fingerprint_accounts`; `mechanism.fed_delta_snr_exhibit` |
| 2026-07-18 | R77 | §5, §6 | **B\* = 400,000 — raised to the MEASURED KNEE by the PRE-COMMITTED extended-curve rule (pre-freeze; rule registered 2026-07-13 BEFORE the data; supersedes R74's 200,000).** R74 set 200k from a pilot whose measured ceiling was 350k; the extended same-protocol cluster ladder (5 budgets 100k→1.6M × 3 CRN seeds × BOTH archived authored winners, validation-DSR units, 30/30 points) shows the flat-extrapolation was wrong beyond that ceiling: the pre-committed rule — paired mean ascent vs 200k > 2×SE over the CRN seed pairs, per winner — FIRES at every extended rung (distributional: +0.145/+0.161/+0.162 at 400k/800k/1.6M, mean/SE 2.9–3.6; scalar: +0.032 at 400k, 5.4×; +0.092 at 1.6M, 2.4×), and the increments BEYOND 400k collapse an order of magnitude (dist +0.016/+0.017; still 3.1–3.8× SE but ~1/9th the 200k→400k jump): **the knee is at 400k**, which captures ≈90% of the attainable gain at 2× compute (deadline-feasible) versus 4–8× (not). Decision: B\* = 400,000, IDENTICAL across all arms (identification preserved; matched compute); the E1 seed ladder is unchanged and remains the grade/deadline securitization (every rung × the fixed budget = a complete design). Disclosures carried into the design: (i) σ_D was measured at 200k — the rung-100 in-campaign σ_D re-estimate (E1, designed-in) recalibrates power expectations at 400k; (ii) the budget dose-response instrument (report-only, outside every confirmatory family) re-centres on {B\*/2, B\*, 2B\*} × 10 CRN seeds on the CAMPAIGN winners; (iii) the curve exhibit (both winners, 16× range) is a MANDATORY figure; (iv) the seed×budget dispersion fan-out observed in the curve is disclosed alongside the σ_D caveat. Verdict artifact: `outputs/tables/bstar_rule_verdict.json` (reproducible via `scripts/apply_bstar_rule.py`); curve dossier `outputs/p6ladder/p6_summary.json`. Mirrors: `config/campaign.yaml` + `config/algos.yaml` (preflight budget-mirror guard) + `config/preregistration.yaml`. | `config/{campaign,algos,preregistration}.yaml`; `outputs/tables/bstar_rule_verdict.json`; `scripts/apply_bstar_rule.py` |
| 2026-07-20 | R78 | ALL (freeze state) | **THE UNFREEZE — v1.0 (`ce5db62c`, frozen 2026-07-18) superseded PRE-DATA; v2 redesign opened (ADR-059; Tamer's instruction).** Zero campaign data exists and the sealed 2020–2026 test leg is untouched, so this is a documented pre-data revision, not a forking path. Trigger: industry-supervisor feedback (2026-07-19, NatWest AI R&D + industry supervisor): the model axis (open-weight + multi-model evidence; permanence of reproducibility), compute allocation (seed-assurance vs model-breadth), method-usefulness success metrics, multi-paper structure. Axes OPEN: model roster/depth, E1 realized-rung policy, metrics/story, reporting structure. Axes CLOSED (invariants): the sealed leg stays sealed; a v2 RE-FREEZE (new canonical hash, gate green, Dr Okhrati sign-off) is REQUIRED before any real-spend launch (`enforce_freeze` keeps refusing unfrozen launches); the 1 Sep deadline time-boxes the rethink (decisions ≤07-22, re-freeze+launch ≤07-28). v1.0 records (tags `prereg-v1.0`/`prereg-freeze-ce5db62c`, bundle, DECISION_LOG entry) are preserved as history. The ADR-058 S12 venue correction folds into the v2 re-hash as that ADR anticipated. | `config/preregistration.yaml` (`frozen: false`, `freeze_hash: null`); `DECISIONS.md` ADR-059 |
| 2026-07-20 | R79 | prompts (treatment text) | **Model-agnostic OUTPUT-FORMAT strengthening of the two loaded prompts (pre-freeze-v2; NO semantic or risk-vocabulary change).** "Return ONLY the function definition" → "Respond with a single Python code block containing ONLY the function definition — no prose before or after the code" (both files). Rationale: the v2 multi-model suite authors with models of widely varying format discipline; format failures would confound the authoring-reliability comparison. Tail-neutrality gate re-verified GREEN post-edit (11 tokens, 2 prompts). | `prompts/system.txt`; `prompts/initial_generation.txt` |
| 2026-07-20 | R80 | NEW `model_suite` (report-only) | **THE V2 MODEL REPLICATION SUITE.** 9 report-only legs at the tier-30 floor (5 LLM arms × 30 candidates each; byte-identical prompts; unified prompt-variation diversity; provider/quantization/reasoning pins incl. the SiliconFlow-fp8-paired Qwen family pair; Luna effort-low + 2k cap; Gemini 3.5 Flash = seat-10 stretch, first-to-truncate), queue-ordered with the 2026-08-14 calendar gate; contamination screens + author smokes + license verifications run PRE-freeze for every leg; Kimi-K3/KAT-Coder = rule-driven Stage-2 triggers only. Pre-registered synthesis: DESCRIPTIVE cross-leg sign count (legs share panel + CRN seeds — not independent) + the per-seed joint-flip permutation test (10,000 reps) + the capability regression (pre-declared external composite primary; M2 reading score secondary) + the registered gradient prediction (responsiveness monotone in capability) + the two-family pair contrast. Reliability metrics + per-model taxonomy registered. The confirmatory core (author, arms, m=6, IUTs, SESOI, E1 ladder) is UNCHANGED. | `config/preregistration.yaml: model_suite`; `docs/MODEL_SWEEP_2026-07-20_v2.md`; DECISIONS ADR-060 |
| 2026-07-20 | R81 | budget + process | **THE $30 SPEND CEILING + the post-launch feedback protocol.** Total LLM spend across ALL providers is HARD-capped at $30 USD, enforced in code, trimmed in the pre-registered priority order (Opus confirmatory → legs in queue order → M2 open → M2 closed) — an exogenous economic stopping rule. Post-launch supervisor/industry feedback informs presentation and interpretation ONLY (the interim floor-tier report pack ~2026-08-06/08 to Dr Okhrati + the industry supervisors is registered here); data-collection decisions follow the pre-registered exogenous rules exclusively — no results-contingent stopping by any party. | `config/preregistration.yaml: model_suite.spend_ceiling_usd/.feedback_protocol/.interim_report` |

---

## §14 — The v2 model replication suite (2026-07-20; R79–R82; placed after the amendment table by v2-addendum convention)

**Design.** The frozen v1 confirmatory core — the Opus 4.8 author, the seven arms, the m=6 family,
the two co-primary IUTs, the ±0.05 SESOI, the E1 seed ladder — is unchanged. Around it, nine
REPORT-ONLY replication legs run the identical five LLM arms (30 candidates each; byte-identical
prompts incl. the R79 format pass; unified R38-de-seeded prompt-variation diversity; provider,
quantization, reasoning-mode, and max-token pins per the machine mirror) at the tier-30 seed floor:
DeepSeek V4-Pro (MIT; contamination-screen gate, GLM-5.2 absorbing on failure), GLM-5.2 (MIT),
the open family pair Qwen3.6-27B + Qwen3.5-9B (Apache; one provider, one quantization), the closed
family ladder Haiku 4.5 + Sonnet 4.6 (the latter = the PILOT BRIDGE: the prototype's author
re-measured under the frozen design), GPT-5.6 Luna (cross-vendor closed; effort-low, 2k cap),
Nemotron 3 Super (NVIDIA Open Model License; major portions of training data published), and
Gemini 3.5 Flash (seat-10 stretch, first-to-truncate). Per R85, every open-weight leg
additionally pins the Hugging Face repo + commit hash of its exact weights release (retrieved
from the official card at gate time; the freeze refuses placeholders), the served quantization is
disclosed as the executed variant of those weights, OpenRouter legs pin temperature = 1.0
(uniform decoding; rejection → provider default, disclosed), and every reasoning pin is
round-trip-evidenced by the gate smoke's archived usage. Legs execute in the pre-declared queue
order behind the confirmatory core and truncate — never reorder — at the calendar gate
(2026-08-14T23:59Z). Kimi K3 and KAT-Coder are rule-driven Stage-2 triggers only.

**Why.** (i) External validity: the single-family limitation (B.3.1) becomes a measured
cross-model result. (ii) Reproducibility permanence: six open-weight legs, hash-pinned, give the
lineage its first systematically re-runnable replication suite (the 2026-07-20 survey found 15/15
lineage papers used closed primary authors). (iii) The capability question: the suite TRACES the
envelope–realization gap g(capability) — the Blackwell envelope binds every author; the legs
measure the realized distance to it along the capability axis, with the numeracy bottleneck as
the registered hypothesized shape, and the two family pairs (one open, one closed) as the
controlled two-ecosystem estimate of the content-effect × capability interaction (computed on the
common floor-30 CRN seed subset; seed-paired bootstrap CI).

**Inference discipline.** Nothing here gates H1–H4. The cross-leg synthesis is pre-registered as:
a DESCRIPTIVE replication count on the CVaR-leg contrast (the Sharpe leg is predicted-tie for
every model), restricted to legs whose winners clear the T0 naive floor in both contrasted arms —
**the floor pinned by R84: the EQUAL-WEIGHT benchmark's mean per-seed Sharpe on the common floor
seeds 0–29 from the shared core baseline records; the filter is arm-symmetric, so it preserves
the null's sign-flip symmetry and cannot distort the permutation test's size** (failing legs
report as authoring/search failures — a finding, never a vote); the per-seed
joint-flip permutation test on the POOLED MEAN difference (10,000 reps, one-sided; the sign count
is descriptive only — a count statistic is near-powerless under joint flips with correlated legs;
shared-seed and shared-panel dependence live inside the null); **the R86 bounded-effect tier: the
90% seed-block-bootstrap CI on the pooled mean CVaR-5% difference (the same joint-draw scheme —
dependence-honest), reported in daily-return units and relative to the scalar-arm pooled CVaR
level — the registered cross-model bounded-null statement (per-leg TOSTs at the floor tier are
inconclusive by construction; pooling is where the precision lives)**; the capability regression
on the R84-pinned SWE-bench-Verified anchor under its discretion-free retrieval rule (M2 reading
score secondary — secondary precisely because it shares method variance with the outcome;
DESCRIPTIVE at n=9 legs, the two family-pair DiDs being the identified estimates); **the R87
three-signature gradient adjudication (capacity=rising / representational=flat-at-zero, THE
registered prediction / echo=decreasing) plus the ex-ante sonnet-bridge direction (≤ 0)**; BH
across the nine-leg report-only CVaR-contrast TOST family for any starred statement. The legs'
sealed-leg evaluations are part of this SAME single pre-registered protocol — every run is
specified before any result is observed, so no adaptive reuse of the test window occurs. Per-model
authoring-reliability metrics (format-compliance baseline, sandbox pass rate, violation taxonomy,
refusal/truncation rates, code diversity, per-model program taxonomy), generation-indexed
responsiveness (does feedback-use strengthen across the loop's generations?), and the M2 probes —
the legible-format probe, the guided-comparison probe, and the responsiveness POSITIVE CONTROL
(overt-directive stimuli where the SQ1 metric must fire, proving its sensitivity) — are all
registered report-only. The total LLM spend is tracked per-call in a cross-provider ledger
against the $30 ADVISORY planning ceiling (R81, softened by R83: warned at 80%/100%, never
refused — spend decisions rest with the researcher; realized spend is reported in full), with
the pre-declared priority order governing execution and reporting order (no automatic
trimming). Post-launch supervisor/industry feedback informs
presentation only (R81); the interim floor-tier report pack (~2026-08-06/08) is registered with
no effect on data collection. At the v2 freeze the pre-registration bundle is DEPOSITED PUBLICLY
(OSF/Zenodo, DOI) as the externally verifiable timestamp anchor.
| 2026-07-20 | R82 | §14 / model_suite | **The completeness supplement (pre-freeze-v2, same-day).** Uniform max-token pins per leg (provider output defaults differ — silent truncation guard); the leg gate made exact (2026-08-14T23:59Z); the synthesis ambiguities closed (sign statistic = the CVaR-leg contrast; T0-floor leg-inclusion criterion; the family-pair DiD estimator on the common floor-30 seed subset; BH across the leg family); the M2 guided-comparison + responsiveness-positive-control probes registered; generation-indexed responsiveness + the Stage-2 qwen3.5-9b search replicate registered; per-leg bank gates; the PUBLIC deposit (OSF/Zenodo) added to the freeze-day checklist; the g(capability) envelope-gap theory bridge named for CH3/CH7. | `config/preregistration.yaml: model_suite` (R82 supplement keys); §14 prose |
| 2026-07-21 | R83 | budget (softening) | **The spend ceiling is ADVISORY, not enforced (Tamer's instruction).** The $30 figure remains the planning ceiling and the reported transparency metric (per-call costs captured, summed, warned at thresholds), but the ledger NEVER refuses a call — spending decisions rest with the researcher. Scientific integrity is unaffected: the exogenous stopping rules that protect the design are the seed-rung rule and the leg calendar gate; the dollar figure was cost discipline, and reporting realized spend serves it fully. | `config/preregistration.yaml: model_suite.spend_ceiling_usd` (comment); `src/llm/spend_ledger.py` |
| 2026-07-21 | R84 | model_suite (pre-declaration completeness) | **The two unpinned selection rules PINNED (pre-freeze, pre-data; deep-sweep findings — each was a registered NAME without a registered VALUE, i.e. a forking path).** (a) **Capability anchor:** primary = the model's **SWE-bench-Verified** score from its official card/vendor announcement under a discretion-free retrieval rule (retrieval date + per-model source archived at gate time; a model with no published score is MISSING — excluded from the primary regression, reported under the M2 secondary anchor, never imputed or benchmark-swapped; sweep-verified so far: qwen3.6-27b 77.2, haiku-4.5 73.3; gpt-5.6-luna documented ABSENT). The M2 secondary's method-variance circularity (our instrument, same models) is named as the reason it is secondary. A benchmark-free tertiary: the within-family ordinal order embodied in the two pair contrasts. (b) **T0 leg-inclusion floor:** floor = the **EQUAL-WEIGHT** benchmark's mean per-seed Sharpe over the common floor seeds 0–29 from the shared core baseline records (was "the T0 naive-benchmark floor" with 8 registered benchmarks to choose from post-hoc). Plus the size argument registered ex-ante: the filter is arm-symmetric, so it preserves the null's sign-flip symmetry — selection-then-test cannot distort the permutation test's size. | `config/preregistration.yaml: model_suite.capability_anchor/.synthesis_exactness.t0_floor_definition/.t0_filter_size_note` |
| 2026-07-21 | R85 | model_suite (reproducibility permanence + decoding uniformity) | **The adopted-but-unimplemented reproducibility mechanics LANDED.** (a) **HF weights pins:** every open-weight leg must carry the Hugging Face repo + commit hash of the exact weights release, retrieved from the official HF card at gate time (never inferred), mirrored in `config/legs.yaml`; **`freeze.py` REFUSES the real freeze while any placeholder remains** (adopted in MODEL_SWEEP §4.1 and claimed in the NatWest brief, but absent from the executed config — the permanence claim was unfulfilled). The served-variant disclosure: the Qwen pair is served fp8 — the pin+provider+quantization together define the executed author. (b) **Temperature:** OpenRouter legs pin temperature=1.0 (uniform — providers default differently, an uncontrolled cross-leg nuisance the prior "provider default, recorded" wording could not actually record); rejection falls back to provider default, disclosed per leg from the gate smoke; Anthropic legs keep the no-temperature Opus convention. Within-leg arm contrasts are temperature-common-mode either way. (c) **Reasoning pins must round-trip:** the gate smoke archives full usage (incl. reasoning-token counts) + served provider as evidence each pin FUNCTIONED; Gemini's prior `budget: default` pin used an undocumented OpenRouter key (silent-ignore = fictional pin) → replaced by provider-default-DISCLOSED with the smoke as the record; DeepSeek's think-high pass-through is harmless-if-ignored (vendor default IS think-high). | `config/legs.yaml`; `config/preregistration.yaml: model_suite.hf_weights_pins/.served_variant_disclosure/.temperature_policy/.reasoning_pin_evidence`; `scripts/freeze.py` (pending_hf_pins refusal); `scripts/leg_gates.py` |
| 2026-07-21 | R86 | model_suite (synthesis: the bounded-effect tier) | **The pooled equivalence-style BOUND registered — the synthesis's missing null-branch statement.** The registered synthesis could only say "no evidence" (a large one-sided permutation p), while per-leg TOSTs at the 30-seed floor are inconclusive by construction. Registered now: the **90% seed-block-bootstrap CI on the pooled mean (dist − scalar) CVaR-5% difference** over T0-included legs (seed indices resampled i.i.d., the SAME draw applied to every leg — k perfectly-correlated legs yield one leg's CI, never a fake √k shrink), reported in daily-return units AND as a fraction of the scalar-arm pooled CVaR level — the cross-model bounded-effect sentence of record. Also: the 9-leg report-only TOST family is pinned to the CVaR contrast; the cross-family capability regression is labeled DESCRIPTIVE (n=9 legs) with the two family-pair DiDs as the identified estimates. Implemented: `cross_model.pooled_bound` (+3 property tests incl. dependence honesty). | `config/preregistration.yaml: model_suite.synthesis_exactness.pooled_bound/.leg_tost_family`; `src/inference/cross_model.py::pooled_bound` |
| 2026-07-21 | R87 | model_suite (falsifiability) | **The capability-gradient prediction made FALSIFIABLE (deep-sweep finding: "monotone non-decreasing" is satisfied by BOTH a flat and a rising gradient — near-unfalsifiable — and is the signature of the RIVAL capacity account, not of this dissertation's own headline theory).** Three rival signatures registered ex-ante: **capacity account** = responsiveness RISES with capability; **representational account (THE REGISTERED PREDICTION** — the numeracy bottleneck binds every author incl. the frontier**)** = responsiveness FLAT at ≈0 across capability, with the legibility/guided-comparison probes (not capability) as the predicted levers; **echo account** = responsiveness DECREASING. Decision read jointly from the regression + both pair DiDs + the M2 probe grid, adjudicated by the A1–A5 fingerprint. Plus the **sonnet-bridge prediction registered ex-ante**: the sonnet-4.6 leg (the prototype's author re-tested under the frozen design) replicates the pilot's responsiveness direction (≤ 0) — the only leg with prior directional data, hence the only leg-level directional pre-registration made. | `config/preregistration.yaml: model_suite.gradient_signatures/.sonnet_bridge_prediction` |
| 2026-07-21 | R88 | model_suite (queue semantics; ops-only) | **The queue order is a PRIORITY ladder, not a serial schedule (mode-D maximum-parallel execution).** The registered queue is realized as SGE priorities (core search/floor/tier-100 above the legs; the 9 legs at −200…−280 in queue order; tier-189+ assurance blocks from −300 below the legs), so ALL lines may execute concurrently while **completion and calendar-gate truncation order remain exactly the pre-declared queue** — under scarce capacity the scheduler starves back-of-queue work first, reproducing the serial semantics; under abundant capacity everything simply finishes sooner. Compute-only knobs added the same day (no registered quantity changes): phase-adaptive packing (search waves at pack-2 with a matching tight walltime — the reflection chains are latency-critical; winner/rung bursts keep pack-5 throughput) and pipelined C4 rung submission (all blocks eligible at once under the descending ladder; a rung still BANKS only when it and every rung below are complete — the cumulative-tier definition is untouched). Seeds, arms, budgets, stopping rules, and the single-look discipline are all unchanged. | `config/preregistration.yaml: model_suite.queue_semantics`; `src/cluster/campaign.py` (search_pack / pipeline_rungs / PRIORITY_RUNG_BASE); `scripts/run_campaign_cluster.py` (--search-pack / --pipeline-rungs); `scripts/mode_d_{launch,supervisor}.ps1` |
| 2026-07-21 | R89 | M2 extras (+2; report-only) | **Freshness adds from the as-of-today model research (2026-07-21).** Two `extras_budget_permitting` M2 rows (7→9, inclusion-rule-gated, never gating anything): **claude-sonnet-5** (released 2026-06-30 — extends the closed Anthropic reading-ladder to five points including a Claude-5-generation one) and **qwen4-coder-32b-a3b** (2026-06-02, Apache — the Qwen family's newest coder; MoE, so M2-ONLY: promoting it to a leg would break the registered dense–dense architecture invariant of the Qwen pair). The same research re-verified every leg pin as current (DeepSeek V4-Pro, GLM-5.2, Qwen3.6-27B/3.5-9B, Haiku 4.5, Sonnet 4.6, GPT-5.6 Luna GA 07-09, Nemotron 3, Gemini 3.5 Flash — Pro still unshipped on its third slip) and the Kimi-K3 Stage-2 trigger's facts (API live 07-16; weights promised 07-27 — the registered rule stands; any seat-11 promotion would be a separate pre-freeze amendment on Tamer's word). | `config/m2_models.yaml: extras_budget_permitting` |
| 2026-07-21 | R90 | model_suite (the latest-generation seat + the K3 conditional; report-only) | **"Use the latest models" (Tamer's instruction) implemented WITHOUT cutting science.** (a) **claude-sonnet-5 promoted from M2-extra to LEG seat 9-of-10** (queue: after nemotron, before gemini — gemini remains the first-to-truncate stretch): released 2026-06-30, $2/$10 introductory through 2026-08-31 (covers the campaign window; leg ≈ $3 expected); scientifically it creates the **GENERATION PAIR** (sonnet-4.6 ↔ sonnet-5: same vendor, same tier, one generation apart) — a THIRD controlled instrument beside the two capability pairs, estimating the content-effect × generation interaction on the common floor-30 CRN seeds (the Sonnet-5 tokenizer change is disclosed as a pair covariate). Roster: 10 legs + Opus = **11 full-loop models**. (b) **The Kimi-K3 CONDITIONAL SEAT registered as a rule** (never results-contingent): weights + permissive license on/before the freeze day (vendor-promised 2026-07-27) + gates pass → last stretch seat after gemini; else the Stage-2 trigger stands. What was NOT changed, deliberately: the confirmatory stays Opus 4.8 (one-frontier rule; Fable 5's June government-directive suspension validates the permanence-risk rejection); sonnet-4.6 stays (the pilot-bridge seat is defined by being the prototype's author); the Qwen pair stays dense–dense (Qwen-4-Coder is MoE → M2-only, R89); Gemini Flash stays (Pro unshipped, third slip). BH family + descriptive-n strings updated 9→10; leg ladder priorities re-spanned −200…−290. | `config/preregistration.yaml: model_suite` (legs/queue_order/generation_pair/conditional_seat_kimi_k3); `config/legs.yaml`; `scripts/mode_d_supervisor.ps1` |
| 2026-07-21 | R91 | model_suite (the Opus-5 conditional; report-only) | **The Opus-5 rumor converted into a pre-declared RULE (leak-stage: "Honeycomb EAP" surfaced in Cursor 2026-07-09 and was pulled; aggregated leaks point mid-July→early-August; NO official announcement, NO API id, no system card as of today).** IF `claude-opus-5` reaches GA with a public API id on/before the v2 freeze day AND passes the leg gates AND **single-author attribution is verifiable** — the leaked spec mentions a safety fallback routing to Opus 4.8 on trigger; every gate call's served-model metadata must identify opus-5, and any silent fallback-routing FAILS the seat on the Sakana-Fugu exclusion principle — THEN it joins as a stretch leg forming the **second generation pair** (Opus 4.8 ↔ Opus 5, mirroring the Sonnet pair). **The confirmatory seat remains Opus 4.8 regardless**: a days-old model in the seat that gates H1–H4 fails the registered stability bar; the swap-to-Fable-5 question was analysed and declined the same day (classifier-fallback = a treatment-correlated interference channel; the June suspension = the permanence contradiction). | `config/preregistration.yaml: model_suite.conditional_seat_opus_5` |

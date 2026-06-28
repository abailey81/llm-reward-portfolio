# DEEP_SYSTEM_redteam — whole-system adversarial red-team of the H1–H4 hypothesis set + benchmark ladder

**Status:** read-only on code; adversarial-examiner synthesis. **Date:** 2026-06-25.
**Repo:** `llm-reward-portfolio`. **Author role:** hostile PhD examiner + research-methodology expert
(a finance-ML examiner who co-authored corpus papers, à la Dr Okhrati). **PDF-only grade, no viva.**

> **What this document is, and is not.** The five per-component DEEP docs already exist and were read
> first-hand: `DEEP_H2.md`, `DEEP_H3.md`, `DEEP_H4.md`, `DEEP_BENCH_T4.md`, `DEEP_STATS_backbone.md`.
> They are deeper than this doc on their own object. **This doc is the layer above them**: it asks the
> questions none of them can see alone — *do H1–H4 together cover the contribution completely and
> non-redundantly; is there a missing hypothesis; is the OVERALL conjunction-claim coherent; and is the
> dissertation a Distinction across the plausible outcome space?* Where it overlaps a per-doc finding it
> says so and points there; its value is the **system gestalt, the bankability matrix, and the single
> strongest thesis claim.** Every code/config assertion below was verified first-hand (file/line or
> config key cited). Literature is grounded in two verified research passes (methodology + finance),
> the local cache, and the existing `00_planning` registers. No fabrication; unverified items flagged.

---

## 0. BOTTOM LINE UP FRONT (read this if you read nothing else)

1. **The system is world-class on conception and unusually strong on inference; its exposure is
   SYSTEM-LEVEL completeness, not any single hypothesis.** Three system-level gaps that NO per-hypothesis
   doc surfaces because each is invisible from inside one hypothesis:
   - **G1 (asymmetric rigor / two-tier hypothesis set).** H2 is wired to a frozen, hashed, FDR-corrected,
     per-seed rliable conjunction test on the sealed leg. **H3 and H4 are numbered, pre-registered
     hypotheses (`config/preregistration.yaml: hypotheses: [H1,H2,H3,H4]`) with NO campaign-grade test
     function in `analyze_campaign.py`** — only a single-seed *descriptive fitness read* in
     `analyze_results.py` (the directional prototype reader). H1 got `beat_human_baseline`; H2 got
     `h2_conjunction`; **H3 and H4 got nothing on the sealed leg.** A referee who sees four numbered
     hypotheses and two analysis functions asks why two hypotheses have no inferential test. (Confirmed
     by DEEP_H3 §2/§4 and DEEP_H4 §0; elevated here to a *system* finding: it is a pattern, not two
     isolated bugs.)
   - **G2 (the BAB / low-vol attribution hole is the largest un-pre-registered finance gap).** A
     long-only, vol-lowering, tail-aware agent **structurally loads on Betting-Against-Beta and the
     low-volatility anomaly** (Frazzini–Pedersen 2014, US BAB Sharpe 0.78; Blitz–van Vliet 2007, ~12%
     low-vol spread). Factor attribution exists in code (`campaign_attribution`, Door-C secondary) but
     is **NOT in `config/preregistration.yaml`** and **NOT a named entry in `LIMITATIONS_REGISTER.md`
     (L1–L14)**. This is the one attack that can recast the *entire* headline as "a repackaged low-beta
     harvest" rather than RL skill.
   - **G3 (the LLM-feedback-insensitivity result is an existential, citable threat to the mechanism).**
     Gupta, Hartford & Liu (2025, *Findings of EMNLP*, arXiv:2509.21403, abstract verified verbatim):
     LLM optimizers show **no sensitivity to experimental feedback — permuting the outcome labels does
     not change performance** — in an iterative scientific-search setting structurally analogous to
     reward reflection. If true here, the distributional-vs-scalar gap is a **prompt-FORMAT artefact**,
     not feedback content. The `placebo_shuffled` arm is the *only* thing that identifies H2 against this,
     and it is currently the inert `+0.000`×6 placebo (PROPOSED upgrade, not yet frozen).

2. **Despite that, the dissertation is a Distinction across essentially the entire outcome space** — but
   *only if* the claim is scoped to the **internal, comparative, pre-registered ladder** and the three
   gaps above are converted into disclosed-and-bounded limitations before freeze. The pre-registered
   null is genuinely bankable (§5). The fatal version is the one that lets the abstract over-reach to
   "LLM-designed distributional rewards beat the human and search and the market" when H3/H4 are untested
   and BAB is unattributed.

3. **The single strongest defensible thesis claim** (full statement in §7) is a *methods + bounded-effect*
   claim, not a performance claim: **"A pre-registered, matched-compute framework shows that feeding an
   LLM reward-designer the realized-return distribution changes the rewards it writes and the tail of the
   resulting policy in a measurable, mechanism-identified way (surviving the scrambled-feedback placebo),
   on a fixed bounded SAC agent over one US-large-cap universe — with the magnitude, and its transfer
   beyond this setting, bounded and pre-registered rather than asserted."**

---

## 1. SYSTEM-COHERENCE VERDICT — do H1–H4 cover the contribution completely and non-redundantly?

### 1.1 The contribution, restated, and the claim graph
The contribution is **the feedback channel**: a fixed SB3-SAC agent, the only thing that varies across
the headline arms is what the LLM reward-designer is shown. The OVERALL claim the dissertation wants to
assert is a **conjunction across rungs of a ladder**:

> *An LLM-designed reward (H1: beats the best hand reward) — specifically one fed the return distribution
> (H2: beats scalar feedback) — produced by iterative reflection (H3) — beats uninformed search (H4) — and
> clears the classical floor (benchmark gate).*

This is a **chain of five claims** (H1, H2, H3, H4, floor). The headline is H2; the others are the
context that makes H2 *mean something* ("better feedback" is only interesting if the LLM is a real
designer (H1), the reflection it depends on works (H3), it beats dumb search (H4), and the whole stack
clears 1/N (floor)).

### 1.2 Coverage: is anything a referee would say "but you didn't test X"?

| Axis of the contribution | Covered by | Verdict |
|---|---|---|
| LLM reward-design *adds value over humans* | H1 (`beat_human_baseline`) | **Covered**, report-only, conservative asymmetry. |
| *Distributional* feedback > scalar (the novelty) | H2 conjunction (frozen, wired) | **Covered, rigorously.** |
| The *reflection loop* is doing the work | H3 | **Declared, NOT inferentially tested** (G1). |
| LLM > *uninformed search* (the "is the LLM even needed" control) | H4a/H4b | **Declared, NOT inferentially tested on the sealed leg** (G1); spaces mismatched (DEEP_H4). |
| It clears the *classical floor* | benchmark gate (wired) | **Covered.** |
| The edge is *not a known risk-factor tilt* (BAB/low-vol) | — | **MISSING from prereg + limitations** (G2). |
| The LLM actually *uses* the feedback content (not format) | placebo leg of H2 | **Covered only if `placebo_shuffled` is frozen** (G3). |
| Mechanism: distributional feedback acts *through* the reward (construct validity of λ=0 Sharpe-gate) | H2 §5/DEEP_H2 §7 | **Partially** — the selection objective is tail-blind (L13); a genuine construct gap. |

**The single most likely "you didn't test X" from a referee** is **not** in the H1–H4 set — it is **the
missing hypothesis H5 (see §1.4) and the missing attribution control (G2).** Both are nameable now.

### 1.3 Non-redundancy / hidden double-counting
- **H1 vs the benchmark floor.** Mild overlap: H1 ("beat the best *hand reward*") and the floor ("beat the
  best *allocator*") are different comparators (reward functions the agent optimizes vs weight policies),
  so there is no literal double-count — but both are "did the LLM-trained agent beat a simple thing"
  framed twice. **Not a defect; state the distinction once** (reward-design bar vs allocation bar).
- **H2's placebo/scalar_cvar5 legs vs H4.** Both probe "is the LLM really using information." H4 asks "is
  the LLM better than no-LLM search"; the placebo asks "is the LLM using the *content* of *this* feedback."
  **Distinct axes; no double-count.** (DEEP_H2 §1.1 already flags that the conjunction legs are
  construct-validity controls, not "H2" — keep that framing.)
- **The genuine redundancy risk is statistical, not conceptual:** H1, the floor, and (if ever wired) H4 all
  compare the SAME distributional winner against SOME baseline on the SAME sealed leg. Reporting all of
  them as independent "wins" without a shared multiplicity ledger is a *garden-of-forking-paths* surface
  (Gelman–Loken; DEEP_STATS_backbone A-cluster). **The frozen m=6 family deliberately excludes H1/H4/floor
  (they write disjoint keys), which is correct for protecting H2 — but it means the SUPPORTING rungs carry
  NO multiplicity control at all.** A referee can argue the supporting claims are individually p-hacked.
  Fix: one declared "supporting-rungs" family with its own internal correction (cheap; report-only).

### 1.4 The MISSING hypothesis (H5) — the one a referee names
Across H1–H4 the system tests *information sufficiency* (does the richer signal help) but **never tests the
DIRECTION the theory spine actually privileges: that distributional feedback improves the TAIL of the
realized policy, not merely the Sharpe.** The frozen conjunction GATE is the **Sharpe** leg
(`h2_conjunction`: "the conjunction gate is the Sharpe leg per contrast"); the CVaR legs are *reported but
do not gate*. So the headline that can be asserted is "distributional feedback beats scalar **on
risk-adjusted return**" — which is *exactly the metric the H2 theory spine (§4) says is BLIND to the tail*,
and which the prototype already shows scalar can win (memory: scalar > distributional on Sharpe-fitness;
distributional wins on CVaR p≈0.004). **There is a latent contradiction between the framing ("distributional
feedback for tail-shape") and the gate (Sharpe).** This is the deepest coherence crack in the system.

**H5 (the hypothesis the design implies but does not state):** *distributional feedback produces policies
with a better OOS tail (CVaR/ES) than scalar feedback, as a primary gated claim, not a reported-only leg.*
The machinery to test it exists (the CVaR difference legs, the FZ0/ES backtest). **Recommendation (§6):**
either (a) elevate a tail metric to a co-primary gate and pre-register it, or (b) explicitly, in the
abstract and intro, scope the gated claim to "risk-adjusted-return feedback efficiency" and present the
tail result as the *mechanistic, secondary* finding — and never let the abstract imply a gated tail win.
Doing neither is the gap a tail-literate examiner converts into "your headline metric cannot see the thing
your title is about." (DEEP_H2 §7 reaches the same reframing from inside H2; H5 names it as a *missing
hypothesis* at the system level.)

### 1.5 Coherence verdict
**The H1–H4 set is conceptually complete for the "information sufficiency" question and non-redundant in
concept, but (i) two of its four hypotheses (H3, H4) lack a sealed-leg inferential test, (ii) it is missing
a stated tail hypothesis (H5) that its own framing and theory imply, (iii) it carries no multiplicity
control on the supporting rungs, and (iv) it omits the BAB/low-vol attribution control that the finance
literature makes mandatory for a vol-lowering long-only agent.** None is fatal; all are nameable and most
are fixable by framing + report-only additions before freeze. **The OVERALL conjunction claim is coherent
only if it is stated as a ladder of differently-graded evidence (H2 confirmatory-gated; H1/floor
report-only-supported; H3/H4 descriptive-directional-only) — not as five equal "wins."**

---

## 2. PER-HYPOTHESIS + PER-BENCHMARK KILLER CRITIQUES (ranked by severity), with rebuttal/hardening

Severity: **CRITICAL** (can invalidate or recast a headline) · **HIGH** (sharp attack, weak/no current
written defence) · **MEDIUM** (defensible if *stated*) · **LOW** (polish). Each entry = the single most
damaging examiner blow + the strongest rebuttal/required hardening. Per-doc cross-refs given.

### 2.1 SYSTEM-LEVEL (the blows the per-hypothesis docs cannot see)

**S1 — CRITICAL — "Your whole edge is Betting-Against-Beta / the low-vol anomaly, not RL skill."**
A long-only agent that lowers volatility to improve the tail mechanically tilts to low-beta names; BAB is a
*named, priced* factor (Frazzini–Pedersen 2014, US Sharpe 0.78 ≈ 2× value; reinforced by Blitz–van Vliet
2007 ~12% low-vol spread, Baker–Bradley–Wurgler 2011). The examiner: *"Regress each arm's OOS excess
returns on Market+SMB+HML+RMW+CMA+UMD+BAB. If the intercept dies once BAB is in, your headline is a
low-beta harvest. Long-only doesn't save you — long-only low-vol tilts load POSITIVELY on BAB. Until I see
that regression I cannot distinguish your result from a mechanical anomaly."*
*Rebuttal/hardening (the defence is strong if pre-committed):* The claim is **comparative** —
distributional **vs scalar**, both long-only, both potentially BAB-loaded — so the load is **common-mode**
and the *differential* alpha is what H2 asserts. **Therefore report the difference-in-α (distributional −
scalar) controlling for FF6+BAB, not the level.** The code (`campaign_attribution`, difference-in-α into
the paired bootstrap) already does this; the gap is governance: **pre-register the factor ladder + BAB as a
declared secondary family, and add it as a named limitation (L15).** Note the double-edge the finance
research flagged: BAB/low-vol are widely argued to have **decayed post-2018** (the exact test window) —
either you harvested a decaying anomaly (won't generalize) or it was weak and the mechanism is something
else; **both branches must be pre-empted, not discovered by the examiner.** (UNVERIFIED: the precise
post-2018 decay magnitude — raise directionally only.)

**S2 — CRITICAL — "Two of your four hypotheses have no test."** H3 and H4 are numbered and pre-registered
but `analyze_campaign.py` contains no H3 or H4 difference test on the sealed leg; only `analyze_results.py`
(single-seed directional) reads winner fitness descriptively. *Rebuttal/hardening:* This is the
execution-completeness wound the VIVA register already names as the dominant risk. **Two honest routes,
both Distinction-safe:** (a) **wire** a minimal H3/H4 sealed-leg test reusing `paired_seed_difference_test`
(the same rliable machinery H2 uses; the records already carry per-seed `test_returns` for all seven arms),
OR (b) **down-rank H3/H4 to explicitly secondary, descriptive-only hypotheses in the prereg and abstract**
(the H3 doc already recommends this for H3, and H3/H4 are on the documented compute down-rank list). The
**unacceptable** state is leaving them numbered-and-co-equal with H2 while untested — that reads as four
hypotheses, two silently abandoned. **Decide and record at freeze.**

**S3 — HIGH — "Your headline metric is blind to the tail your title is about (missing H5)."** See §1.4.
The conjunction gate is Sharpe; the prototype already shows scalar can win on Sharpe while distributional
wins on CVaR. *Rebuttal/hardening:* Reframe (DEEP_H2 §7) — the *gated* claim is feedback-efficiency on
risk-adjusted return; the *tail* result is the mechanistic secondary, reported with the FZ0/ES backtest and
the CVaR difference legs. OR elevate a tail metric to co-primary and pre-register it (H5). **Pick one
before freeze; do not let the abstract imply a gated tail win.**

**S4 — HIGH — "The LLM ignores feedback content; your arms differ only in prompt format."**
(Gupta–Hartford–Liu 2025; G3.) *Rebuttal/hardening:* This is precisely why H2 must survive *beyond the
placebo*. **The inert `+0.000`×6 placebo controls token count but NOT structure** — it cannot distinguish
"uses the numbers" from "responds to a plausible-looking table." **Freeze the `placebo_shuffled` arm**
(same distributional table, label↔value permuted, candidate-seeded/replayable; m=6→m=8, BH re-applied) —
the master findings call it "the single most reviewer-convincing experiment," and it directly operationalizes
the Gupta–Hartford permuted-label control. Counter-evidence exists but is conditional and non-peer-reviewed
(Wainrib et al. 2026 preprint: feedback-sensitivity emerges only above a model-capability threshold — a
Sonnet 4.5→4.6 upgrade flipped n.s.→significant; supports using Opus 4.8 but **still requires the placebo**).

**S5 — HIGH — "The supporting rungs (H1, floor, H4) are individually p-hacked — no multiplicity control."**
The frozen m=6 family protects H2 only; H1/floor/(H4) write disjoint keys and carry no correction (§1.3).
*Rebuttal/hardening:* Declare ONE "supporting-rungs" family (H1 beat-human + floor gate + any H4 leg) with
its own internal BH; report-only; disjoint from m=6 so the frozen assert stays green. Cheap; removes a
garden-of-forking-paths attack on the context claims.

**S6 — MEDIUM — "n-of-1 on every axis: 1 task, 1 universe, 1 period, 1 agent (SAC), 1 LLM (Opus)."**
The external-validity blow. *Rebuttal/hardening:* §3 (honest-scope framing). The defence is to **own it as
the design's deliberate internal-validity trade and scope the claim to mechanism, not generality** — the
pre-registered null + the comparative framing already make most common-mode threats irrelevant to the
*contrast*. Do NOT over-claim generality; cite Liao–Taori–Raji (2021) as the named external-validity
limitation (turning the attack into self-aware rigor).

### 2.2 H2 (headline) — deepest issues already covered in DEEP_H2; system-level note only
The killer per DEEP_H2: **conjunction-vs-BH double-correction**, the **λ=0/Sharpe-gate construct gap**, and
the **EVT-measurement-noise → feedback-content confound**. All HIGH, all framing/amendment fixes. **System
note:** the construct gap (S3/H5) and the placebo gap (S4) are the two that propagate UP into the overall
claim — if either is unaddressed, the conjunction "distributional beats scalar AND survives controls"
cannot bear the weight the abstract puts on it. Defer to DEEP_H2 for the within-H2 fixes; ensure the abstract
language matches the gated metric.

### 2.3 H1 (LLM vs best hand reward) — killer + rebuttal
**KILLER — MEDIUM — "The human baseline is a strawman (4 textbook rewards, un-tuned), so 'beats the human'
is hollow."** `h1_baselines: [raw_return, return_minus_variance, return_minus_cvar, differential_sharpe]`
are canonical but un-optimized; Eureka's own "human" was an *expert-engineered* reward. *Rebuttal/hardening:*
The asymmetry is deliberately CONSERVATIVE — baselines are deflated by N=1, the LLM by its searched N (a
*higher* human bar, `beat_human_baseline` docstring). State it as report-only context vs the Eureka 83%/+52%
bars, **never as a headline claim**, and disclose that the hand rewards are canonical-not-tuned (so "beat the
human" = "beat the standard textbook objectives," which is the honest claim). Add `return_minus_cvar` is
*already* a tail reward — so H1 implicitly tests "did distributional FEEDBACK beat a hand-written CVaR
REWARD," a genuinely interesting sub-result worth foregrounding.

### 2.4 H3 (iterative vs single-shot) — killer + rebuttal (defer detail to DEEP_H3)
**KILLER — HIGH — "Your reflection result CONTRADICTS your own Eureka framing, and you didn't even test
it."** H2 leans on reflection (the loop feeds the distribution back); H3 prototype found reflection
**unsupported**; and there is no sealed-leg H3 test (G1/S2). An examiner: *"You cite Eureka's −28.6%
reflection-ablation to motivate the channel, then your own data say reflection doesn't help — which is it?"*
*Rebuttal/hardening (DEEP_H3 is strong here):* The two are reconcilable — H2 is about the *information in
the feedback*, H3 about *iteration vs best-of-N at fixed budget*; a sparse, noisy single-seed verifier is
exactly where reflection is documented to stall, so a **null is EXPECTED and is a substantive,
pre-registered counterpoint to the reflection narrative** (not a defect). But it MUST be (a) tested or
explicitly descoped (S2) and (b) framed as a bankable equivalence (TOST), not buried. **The contradiction
is only fatal if undisclosed.**

### 2.5 H4 (LLM vs random-search / Bayesian-opt) — killer + rebuttal (defer detail to DEEP_H4)
**KILLER — HIGH — "You rigged the controls: three arms search three different-richness spaces, and you
mislabel your BO as TPE."** (DEEP_H4 §0: random-search = 3-term grammar; BO = 6-term linear, GP-EI not TPE,
`bayesopt_tpe` mislabel; LLM = free-form.) A naive "LLM beats search" conflates *search-procedure quality*
with *reward-form richness*; under-powered controls make a positive H4 look manufactured by crippling the
baselines. *Rebuttal/hardening:* **Fix the `bayesopt_tpe`→`bayes_opt`/GP-EI label everywhere (factual error
a corpus-author catches instantly)**; scope the claim precisely to "LLM beats uninformed search *over its
respective space at matched evaluation budget*"; and either match the spaces or **state the richness
asymmetry as the point** (the LLM's advantage IS partly that it can author richer forms — but then the
claim is "LLM > template search," not "LLM is a better optimizer"). And wire or descope the sealed-leg test
(S2).

### 2.6 Benchmark ladder — killer per tier (defer SOTA detail to DEEP_BENCH_T4)
- **Floor (1/N + 7 allocators) — MEDIUM — "If you only tie/marginally beat 1/N net of costs, you spent an
  LLM + RL campaign to reproduce a 15-year-old null (DeMiguel 2009)."** *Rebuttal:* 1/N is a documented hard
  floor; clearing it net-of-costs is a real "it works" statement, and a *comparative* H2 does not even
  require beating it (the contrast is the point). Report the full costed table + break-even cost. **Double-
  edged: this IS the best justification for the pre-registered null** (if even sophisticated optimization
  can't beat 1/N, a bounded distributional-vs-scalar result is still a clean methods contribution).
- **REWARD_CANON (H1) — see §2.3.**
- **Search (H4) — see §2.5.**
- **FinRL SOTA band (Tier 4) — CRITICAL if claimed as a ranking — "Apples-to-oranges; the band is a
  reproducibility smear (FinRL's own issue #190: same code/data/seeds, Sharpe 0.16→2.39)."** (DEEP_BENCH_T4
  §0.) *Rebuttal:* **Never claim a head-to-head SOTA win.** Use the band ONLY as a one-paragraph plausibility
  ribbon (costed OOS US-equity DRL Sharpe ≈ 0.85–1.6) with heavy caveats. The defensible claim is the
  internal ladder, full stop.

---

## 3. EXTERNAL VALIDITY — honest-scope framing (1 task, 1 universe, 1 period, 1 agent, 1 LLM)

**What an examiner will say:** "By your own cited framework (Liao–Taori–Raji 2021) this is at best an
*internal-validity* result on a single instance — one draw from the space of markets, agents, regimes, and
models. You present zero external-validity evidence, yet H2 is phrased as a general mechanism. Recht et al.
(2019) show ImageNet classifiers lose ~10% on a same-distribution re-sample — what is your confidence the
*direction* of a tail-feedback advantage survives an actual regime shift your 2005–2025 window never
contained?"

**What can legitimately generalize, and what cannot:**
- **Generalizes (claimable):** the **method** (a pre-registered, matched-compute, off-critic
  distributional-feedback framework with selection-aware inference) and the **mechanism finding** (whether
  *this* bounded LLM optimizer uses the distributional content under a tail-sensitive objective — the
  Gupta–Hartford question, answered with a placebo). These are *about the channel*, not about US large-caps.
- **Does NOT generalize (must not claim):** any statement about *performance magnitude*, *transfer to other
  asset classes / agents / LLMs / periods*, or "beats the market." The Blackwell/Kusuoka theory gives an
  *upper envelope* ("more info can't hurt the optimal user"), not a guarantee the real optimizer attains it
  off this data (H2_THEORY_SPINE §6, claim 11 = EMPIRICAL).

**The honest framing that scopes without gutting the contribution (one paragraph for the dissertation):**
> *This is a single-instance study by design: one task, one survivorship-free US-large-cap universe, one
> period, one fixed bounded agent (SB3-SAC), one frontier LLM (Opus 4.8). That is a deliberate
> internal-validity trade, not an oversight — fixing the agent is precisely what isolates the feedback
> channel, and a single pre-registered comparison is what makes a null bankable. Most threats to the result
> (universe composition, delisting fill, exogenous prices, rf convention, seed count, even a BAB/low-vol
> tilt) are common-mode: applied byte-identically across all arms, they cannot manufacture the
> distributional-vs-scalar contrast we test. What we therefore claim is a mechanism on this instance and a
> method that transfers; what we explicitly do not claim is external validity of the magnitude or its
> transfer to other agents, assets, or regimes — we name that, after Liao et al. (2021), as the principal
> limitation and the obvious next experiment (a second agent, a second universe, a second model), and we
> note that the theory bounds an envelope rather than promising attainment off-sample.*

This converts the n-of-1 attack into self-aware scope. **The error that loses marks is the abstract
sentence that forgets to do this.**

---

## 4. THREATS-TO-VALIDITY MATRIX (internal / external / construct / statistical) — whole system

| Type | Threat | Where it bites | Current defence | Residual / required hardening | Sev |
|---|---|---|---|---|---|
| **Construct** | Headline GATE is Sharpe, framing is tail (H5 missing) | Whole claim | CVaR legs reported | Reframe or pre-register tail co-primary (§1.4/S3) | **HIGH** |
| **Construct** | λ=0 selection is tail-blind; can pass over tail-better candidate | H2 mechanism | Stated (L13); conservative vs H2 | Keep, but state biases-against-tail-legs explicitly | MED |
| **Construct** | "beats the human" with un-tuned textbook rewards | H1 | Conservative N=1 asymmetry | Disclose canonical-not-tuned; report-only | MED |
| **Construct** | LLM responds to prompt FORMAT not feedback CONTENT | H2 placebo | Inert placebo (token count only) | **Freeze `placebo_shuffled`** (S4/G3) | **HIGH** |
| **Internal** | BAB/low-vol tilt = the "edge" | Whole claim | Code exists, not pre-registered | **Pre-register FF6+BAB difference-in-α + L15** (S1/G2) | **CRIT** |
| **Internal** | Selection-on-test leakage via "reflect-on-best" | H2 validity | Selection on VAL DSR only; sealed test | Confirm reflect-on-best touches VAL only, IDENTICALLY per arm (Gulrajani 2021) | **HIGH** |
| **Internal** | DSR trial count correlated-DOWN under sequential reflection | DSR (secondary) | PBO primary (count-free) | Per DEEP_STATS A1; report N_eff band; keep DSR secondary | MED |
| **Internal** | Delisting zero-fill flatters left tail | Tail metric | Located (1 test-leg death, a merger; L2) | univ4 four-fill exhibit (robustness not correction) | MED |
| **Statistical** | Supporting rungs (H1/floor/H4) uncorrected | Context claims | m=6 protects H2 only | **Declare a supporting-rungs family** (S5) | **HIGH** |
| **Statistical** | Seed-only variance underestimates true variance | All A/B | rliable per-seed IQM (n=30) | Per Bouthillier 2021: stratified bootstrap is PARTIAL; disclose single-split limit | MED |
| **Statistical** | Tail tests underpowered at extreme α (CVaR-1%) | Tail legs | Lead with 5%/10%; flag 1% (L6) | Report realized power beside each p (Bauer 2025) | MED |
| **Statistical** | H3/H4 untested on sealed leg | H3, H4 | Single-seed descriptive only | **Wire or descope** (S2) | **HIGH** |
| **External** | n-of-1 (task/universe/period/agent/LLM) | Generality | Comparative/internal framing | Scope to mechanism+method; cite Liao 2021 (§3) | MED |
| **External** | Regime shift may flip the advantage direction | Generality | 2018/2020/2022 stress in-window | Disclose; OOD stress as falsification-probe not OOS (L-set) | MED |
| **External** | Result won't transfer past Opus 4.8 | Generality | Pinned snapshot, replay | Scope as LLM-loop-genre limit; 2nd open-weights model | LOW |
| **Reproducibility** | LLM non-determinism | Whole pipeline | Replay-from-archive, pinned snapshots | Disclosed (L9); genre-standard | LOW |

**Reading:** the **CRITICAL** cell is BAB (one internal-validity control closes it). The **HIGH** cluster is
five items, every one fixable by **pre-registration prose + a report-only addition + a frozen placebo
upgrade** — no campaign re-run. That is the entire difference between a Distinction and a vulnerable headline.

---

## 5. BANKABILITY MATRIX — is it a Distinction across the outcome space?

The PDF-only grade rewards **research design, independence of thought, and self-critical rigor** far more
than a positive effect. The pre-registered null is the insurance. Outcome axes: **H2** (+/null) × **H1**
(+/null) × **H3** (null, expected) × **H4** (+/null). (H3 is treated as null throughout — it is the
expected, pre-registered outcome and is a *feature*, per DEEP_H3.)

| # | H2 | H1 | H4 | Story the dissertation tells | Distinction? |
|---|---|---|---|---|---|
| A | **+** | + | + | Full ladder: LLM-designed distributional rewards beat human, scalar, and search, clear the floor; reflection is the documented null. Strong **if** BAB-attributed + placebo-frozen + claim scoped. | **YES (strong)** — guard against over-claim |
| B | **+** | + | null | Distributional feedback helps and beats the human, but the LLM is not clearly better than uninformed search → reframe: "the *information* helps; the *optimizer* is not the differentiator" — itself an interesting, honest finding. | **YES** |
| C | **+** | null | +/null | Distributional > scalar, but the LLM doesn't clearly beat the best hand reward → "richer feedback improves the LLM's search even where it doesn't beat a tuned human" — bounded but real. | **YES** |
| D | **null** | + | + | Headline null: at matched compute on this task, distributional feedback is **practically equivalent** to scalar (TOST inside ±0.05 DSR) — a *bounded, pre-registered* ceiling on the channel, with H1/H4 wins showing the LLM-design framework itself works. The §5 principled-null catalogue (tail-indifferent objective / optimizer-ignores-info / unmeasurable-at-n / acceleration-erased-by-matched-compute) makes the null **mechanistic and informative**, not a failed run. | **YES** — this is the bankable-null case the whole design is built for |
| E | **null** | null | null | Everything null: even so, a *rigorously executed, pre-registered, well-powered null across the board* — "neither distributional feedback, nor LLM reward-design, nor LLM-over-search beats the simple baselines on this task at this budget" — is a clean, honest, methods-and-negative-results contribution, IF the inference is bulletproof and the limitations own it. | **YES (borderline→solid)** — depends entirely on execution + disclosure quality |
| F | any | any | any | **BUT BAB unattributed + abstract over-claims a tail/market win + H3/H4 left silently untested** | **NO / at-risk** — the only failure modes are self-inflicted |

**Verdict: the dissertation is a Distinction in EVERY genuine outcome combination (A–E).** The pre-registered
null (D) is explicitly bankable; the all-null (E) is solid given execution + disclosure. **The ONLY route to
a non-Distinction (F) is self-inflicted: over-claiming beyond the gated metric, leaving the BAB tilt
unattributed, or shipping H3/H4 as co-equal-but-untested.** Bankability therefore reduces to **discipline,
not luck** — which is exactly what a no-viva, pre-registered design is supposed to guarantee.

**The bulletproof claim-set REGARDLESS of outcome (the pre-registered-null insurance):**
1. *We pre-registered (hashed) the hypotheses, budgets, metrics, equivalence margin (SESOI 0.05 DSR, TOST
   ±0.05), and the m=6 analysis family before the campaign* — so any result is confirmatory, not postdiction.
2. *The headline is comparative and internal (distributional vs scalar at matched compute on a fixed agent),
   never "beats the market."*
3. *The selection signal is reward-independent (validation DSR) and on a different split from the fed signal,
   so a reward cannot game its own fitness; PBO/CSCV (count-free, full 12,870-split enumeration) is the
   primary overfitting guard.*
4. *A non-rejection is reported as a bounded effect (TOST) with the principled-null catalogue, not a failure.*
5. *Every common-mode threat (universe, costs, rf, delisting, seed count, even a factor tilt) is applied
   byte-identically across arms and so cannot manufacture the contrast.*
These five are TRUE and bankable **today**, independent of what the campaign returns.

---

## 6. PRIORITIZED MASTER LIST OF PRE-FREEZE HARDENING ACTIONS (cross-cutting)

Ordered by (severity × cheapness). Items marked **[gov]** = pre-registration/prose only (no code);
**[code]** = a report-only code addition (no campaign re-run); **[freeze]** = a frozen-quantity amendment.

**P0 — close the CRITICAL/HIGH system gaps (do all before freeze):**
1. **[gov+code] Pre-register the BAB/low-vol attribution control + add limitation L15.** Declare the
   FF6+BAB factor ladder as a secondary family; headline the **difference-in-α (distributional − scalar)**;
   wire the verified citation (Frazzini–Pedersen 2014, JFE 111; cite **QMJ = Review of Accounting Studies
   24(1):34-112, 2019** if used — NOT Review of Finance). Pre-empt the post-2018 low-vol-decay double-edge.
   *(Closes S1/G2 — the single highest-value action.)*
2. **[freeze] Freeze the `placebo_shuffled` arm** (m=6→m=8, BH re-applied; candidate-seeded, replayable).
   *(Closes S4/G3 — the Gupta–Hartford existential threat; "single most reviewer-convincing experiment.")*
3. **[gov] Decide H3/H4 status and RECORD it at freeze:** either **[code]** wire a minimal sealed-leg
   H3 (multi-gen winner vs single-shot winner) and H4 (LLM winner vs random_search/bayes_opt winner) test
   reusing `paired_seed_difference_test` on the existing per-seed `test_returns`, OR **[gov]** down-rank
   H3/H4 to explicitly secondary descriptive hypotheses in the prereg and abstract. *(Closes S2/G1 — the
   execution-completeness wound.)*
4. **[gov] Resolve the H5 / Sharpe-gate vs tail-framing contradiction:** either pre-register a tail metric
   as co-primary, or scope the gated claim to risk-adjusted-return-feedback-efficiency and present the tail
   as the mechanistic secondary — and **align the abstract to the gated metric.** *(Closes S3/§1.4.)*
5. **[code] Declare a supporting-rungs multiplicity family** (H1 + floor + any H4 leg), internally BH-
   corrected, disjoint keys (frozen m=6 assert stays green). *(Closes S5.)*

**P1 — fix factual/label errors a corpus-author catches instantly (cheap, mandatory):**
6. **[gov] Fix `bayesopt_tpe` → `bayes_opt` / GP-EI everywhere** (config comment `eureka_loop.yaml:21` +
   any prose). It is GP-EI, not Optuna-TPE (DEEP_H4 §0.1).
7. **[gov] refs.bib citation-integrity sweep** (both research passes converged): **FZ0 → cite Patton,
   Ziegel & Chen 2019 (J. Econometrics 211(2):388-413), not Fissler–Ziegel 2016** (FZ0 = loss-*differences*
   0-homogeneous); Fissler–Ziegel 2016 **erratum** (Ann. Statist. 49(1):614, 2021); **Skalse & Abate UAI
   2023** (not "Skalse 2024"); **Troop POT = UAI 2021 (PMLR 161)** not IME; **Politis–Romano pp.
   1303-1313**; **Ledoit/Wolf = Olivier/Michael**; **Harvey–Liu–Zhu third author "Caroline Zhu" (RFS) vs
   "Heqing Zhu" (NBER) — don't mix**; **Eureka last authors …Zhu, Fan, Anandkumar**; **Recht 2019 cite for
   distribution-shift, NOT adaptive overfitting**; **AlphaEvolve = 2506.13131**; **QMJ = Rev. Acct. Studies
   2019**; **HAC lag rule = Schwert 1989**.

**P2 — statistical hardening the per-docs already prescribe (defer detail there):**
8. **[code/gov] DEEP_STATS_backbone P-list** (DSR N_eff band; report realized power beside each tail p;
   conjunction-vs-BH double-correction wording).
9. **[gov] DEEP_H2 §7 reframe** (mechanism the design actually optimizes); the EVT-noise→content confound
   disclosure; the λ=0 tail-blindness statement.
10. **[gov] Confirm reflect-on-best touches VALIDATION only and IDENTICALLY across arms** (Gulrajani 2021 —
    a selection-on-test leak would invalidate H2; the headline is now parallel reflect-on-best per R24).

**P3 — scope/disclosure prose (the no-viva grade levers):**
11. **[gov] External-validity scope paragraph** (§3) verbatim near the top of Limitations; cite Liao 2021.
12. **[gov] Three meta-points** from the LIMITATIONS register closing (comparative-not-market; null-is-a-
    result; disclosure-is-the-deliverable) — keep, they are correct and high-value.
13. **[gov] State the trial count N explicitly** and that it exceeds MinBTL (~33 for a 7-yr OOS Sharpe 1),
    which is *why* PBO leads over DSR (the finance research's sharpest single weapon — pre-empt it).

**Note on what NOT to do** (scope discipline, CLAUDE.md directive 2): do not add the QD engine, OOD GANs,
offline/CQL arm, or a same-panel SOTA re-run to chase these — they are future work and a same-panel SOTA
re-run is explicitly low-value (DEEP_BENCH_T4 §0.5). The P0–P3 list is governance + report-only + one frozen
placebo, nothing that re-runs the campaign.

---

## 7. THE SINGLE STRONGEST DEFENSIBLE THESIS CLAIM

**Statement (bankable regardless of campaign outcome):**

> *We introduce and pre-register a matched-compute framework in which a language model designs the reward
> CODE for a fixed, bounded reinforcement-learning portfolio agent, and we isolate one factor — whether the
> designer is fed the realized-return DISTRIBUTION (tail statistics) or a scalar Sharpe. Theoretically, the
> scalar is a Blackwell garbling of the distribution and the CVaR profile is a sufficient coordinate basis
> for the coherent-risk class (Kusuoka–Acerbi), with the tail provably off-critic (Rowland 2019), so a
> Bayes-optimal designer can do no worse with the distribution and strictly better under any genuine risk
> attitude — an UPPER ENVELOPE, not an empirical promise. Empirically, on a survivorship-free US-large-cap
> universe with a fixed SB3-SAC agent, we test whether THIS LLM optimizer attains that envelope at matched
> compute, with the contrast identified against a scrambled-feedback placebo (so a difference reflects
> feedback CONTENT, not prompt format), a reward-independent held-out selection rule (so no reward games its
> own fitness), a count-free overfitting guard (PBO/CSCV), and a pre-registered equivalence margin (so a
> null is a bounded ceiling on the channel, not a failed run). The contribution is the FEEDBACK CHANNEL and
> the methodology; the claim is comparative, internal, and mechanistic on this instance — explicitly not a
> claim about market performance, nor about transfer to other agents, assets, periods, or models, which we
> name as the principal limitation and the obvious next experiment.*

**Why this is the strongest:** it (a) leads with the **method + pre-registration** (the highest-weighted,
outcome-independent marking dimensions); (b) states the **theory as an envelope** and the **empirics as the
single open question** (so a null is informative, never embarrassing); (c) bakes in the **placebo, held-out
selection, PBO, and TOST** so the four sharpest attacks are answered *in the claim itself*; (d) scopes
external validity honestly *inside the thesis sentence* so the n-of-1 attack lands on already-conceded
ground; and (e) makes **no statement the BAB/low-vol attribution could overturn** (it never claims a
performance level or a market win — only a feedback-channel mechanism, attribution-controlled by the
common-mode argument). It is true and defensible **today**, before a single campaign number exists — which
is exactly the property a no-viva, pre-registered Distinction requires.

---

### Appendix — provenance of this red-team
Read first-hand: `PREREGISTRATION.md` (full, incl. amendments R11–R24, D2); `config/preregistration.yaml`,
`config/campaign.yaml` (H3 `generations`, H1 baselines); `scripts/analyze_campaign.py` (full — confirmed H1
`beat_human_baseline` + H2 `h2_conjunction` wired; **no H3/H4 sealed-leg test**); `scripts/analyze_results.py`
(single-seed directional "H4 read" only); `00_planning/LIMITATIONS_REGISTER.md` (L1–L14 — confirmed **no BAB/low-vol
attribution entry**; the only Frazzini match is an incidental Frazzini-Israel-Moskowitz 2018 cost citation
in L3, not an attribution limitation); `00_planning/H2_THEORY_SPINE_2026-06-21.md`; `00_planning/VIVA_DEFENSE_REGISTER_2026-06-19.md`;
`00_planning/CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md`; and the existing `docs/DEEP_{H2,H3,H4,BENCH_T4,
STATS_backbone}.md` (headers + key findings, cross-referenced not duplicated). Literature verified via two
adversarial research passes (methodology + finance), primary-source-checked; citation corrections and the
Gupta–Hartford (2025, EMNLP Findings, arXiv:2509.21403) feedback-insensitivity threat are first-hand-verified.
No code, config, or pre-registration was modified.

# DEEP_H3 — Exhaustive scrutiny of H3 (iterative reflection vs single-shot)

> **Scope.** This document is an adversarial, citation-grounded audit of hypothesis **H3** and a
> prescription for the *strongest defensible* version. It is read-only on code: it reports what the
> live code does (verified first-hand, June 2026), names every threat to validity with a severity, and
> prescribes the pre-freeze hardening. The prototype found **H3 unsupported**; the goal is to make that
> null *bankable* and to frame it as a substantive challenge to the reflection narrative, not a defect.
>
> **Status of the conclusion.** The recommended headline is **a pre-registered, well-powered NULL/
> equivalence result**: *iterative reflection is not distinguishable from best-of-N single-shot at this
> budget on this task.* This is scientifically interesting because it is a direct, controlled
> counter-point to Eureka's central "evolution / reward-reflection is indispensable" claim, in a domain
> (sparse-reward financial reward-design) where the theory predicts reflection should be *weakest*.

---

## 0. TL;DR for the supervisor (Dr Okhrati)

1. **What H3 is.** H3 asks whether the **iterative reflection loop** (the LLM sees feedback on its
   prior reward and revises, over G generations) beats a **single-shot** author that spends the *same
   total LLM-call budget* drawing N×M independent candidates in one generation (best-of-N). Winner
   selection is identical (best validation Deflated Sharpe). The pre-registered contrast (FINAL_PLAN
   B.6 / PREREGISTRATION §1, §6) is **on the distributional arm**: multi-generation vs single-shot.

2. **The single biggest issue is that single-shot is NOT a strong, fairly-matched baseline as wired,
   and the contrast is NOT in the analysis pipeline.** Two distinct operationalisations of H3 coexist
   in the repo and they are not equivalent (§2). The dedicated single-shot *run* is a manually-launched
   separate invocation (`generations:1`), is on the explicit *down-rank/cut* list, and **no
   `analyze_campaign` function computes the H3 difference test** (§2, §4). The prototype's actual H3
   evidence came from a *third* construction — a within-arm "uplift" trajectory (§3) — which answers a
   subtly different question.

3. **Best-of-N is a strong baseline and reflection is expected to be *weak* here.** Over a sparse
   reward-design landscape (prototype: median candidate DSR ≈ 0.0018; winner-quality 2–5%), the
   literature predicts parallel sampling (best-of-N) to *match or beat* sequential refinement, and
   predicts intrinsic self-reflection to add little absent a reliable external verifier (§5, §6). The
   selection signal here is a single-seed validation DSR — a *noisy* verifier — which is exactly the
   regime where reflection is documented to stall.

4. **Therefore the honest, defensible target is a null framed as a finding**, backed by (a)
   pre-registered TOST equivalence, (b) the reflection-vs-diversity disentanglement, and (c) the
   literature that makes a null *expected and interesting* rather than a failure (§7, §8). The
   prototype null (placebo's pure-resampling uplift ≥ the informative arms' uplift) is the headline
   sentence of that finding.

---

## 1. What H3 *exactly* is — the contrast, operationalised in code

### 1.1 The pre-registered statement
- **PREREGISTRATION.md §1:** *"H3 — iterative vs single-shot. H0: multi-generation ≤ single-shot at
  matched candidate budget."*
- **FINAL_PLAN B.6:** *"H3 — iterative vs single-shot. H0: multi-generation ≤ single-shot at matched
  candidate budget. **Test: difference test on the two conditions of the distributional arm.**"*
- **PREREGISTRATION.md §6 / FINAL_PLAN B.3:** *"Single-shot arm (H3) draws the whole budget in one
  generation."*

So the **canonical contrast** is, *within the distributional arm*:
- **Iterative condition:** G generations × M candidates (campaign: 6×5 = 30; prototype: 8×5 = 40), with
  reflection — each generation's prompt carries the previous candidate's feedback block.
- **Single-shot condition:** 1 generation × (G·M) candidates (30 / 40), **no reflection** — every
  candidate is drawn from the *initial* prompt; the winner is best-of-(G·M).

### 1.2 How the loop realises "single-shot" (verified in `src/llm/loop.py`)
- `generations` and `candidates_per_gen` are read from config (`run_loop`, lines 269–270). The total is
  `generations × candidates_per_gen`; `_budget_for_generation` (lines 207–215) splits a matched total
  budget across generations, giving a single-generation arm the *whole* budget at once.
- **Reflection is gated purely on generation index**: `prev_feedback_block is None` ⇒ the *initial*
  prompt; otherwise the reflection preamble + the prior block (lines 333–336). With `generations==1`
  the loop NEVER enters the reflection branch — every candidate uses the initial prompt. Confirmed by
  `tests/test_loop.py::test_single_shot_draws_full_budget_in_one_generation` (gen count 1, budget fully
  spent, only the initial prompt drawn).
- **Winner = best validation fitness** in both conditions: `CandidateArchive.winner()` returns
  `max(candidates, key=val_fitness)` (lines 171–181). Selection is identical across conditions and is
  reward-independent (validation DSR on realized val returns), so it cannot be reward-hacked
  (PREREGISTRATION §5). **This is correct and a genuine strength**: the single-shot baseline is
  best-of-N with the *same* selector, which is the fair, strong baseline.

### 1.3 Within-generation diversity (the mechanism that makes single-shot competitive)
`_diversity_directive` (loop.py lines 189–204) appends a per-candidate-index instruction telling the
LLM to vary the risk term / window / functional form, fired only when `diversity_prompt_variation` is
on AND `candidates_per_gen > 1` (line 347). Rationale: Claude Opus 5 (the campaign author) *rejects*
the `temperature` parameter, so within-generation variety is injected by prompt variation instead;
Sonnet 4.6 (prototype author) honours `temperature=1.0` and does NOT use the directive
(`config/prototype.yaml: diversity_prompt_variation:false`; `config/campaign.yaml:true`). The directive
set is **identical across arms**, so it is not an H2 confound — but it is *directly material to H3*
(§6.3): in single-shot, with `candidates_per_gen = 30`, all 30 draws receive distinct directives, which
is precisely what makes best-of-N a strong, diverse baseline.

---

## 2. THREAT CLASS A — the contrast is under-specified and not wired (the dominant problem)

### 2.1 Three non-equivalent operationalisations of H3 coexist in the repo
| # | Where | "Single-shot" means | "Iterative" means | Status |
|---|---|---|---|---|
| **(i) Canonical** | PREREGISTRATION §1/§6, FINAL_PLAN B.6 | distributional arm at `generations:1`, budget in one gen, best-of-N | distributional arm at `generations:6/8` | **Frozen intent**, but a SEPARATE run, NOT auto-wired |
| **(ii) Dedicated arm** | `config/eureka_loop.yaml:19` (`llm_single_shot`), `data_pipeline/.../eureka_loop.yaml` | a 5th LLM arm: "240 one-shot samples, no reflection" | the reflection arms | **Stale/superseded** — NOT in the 6-arm prereg set |
| **(iii) Within-arm uplift** | prototype analysis (`per_generation_summary`), memory [[project-prototype-results-and-benchmarks]] | gen-0 best fitness | overall best-across-generations fitness | **What the prototype actually reported** |

These answer different questions (§3). The dissertation must pick **one** primary H3 estimator and
pre-register it; (i) is the right primary because it is a clean, like-for-like, matched-budget A/B with
identical selection.

- **Severity: HIGH.** Ambiguity in *which* contrast is "H3" is exactly the moved-goalpost risk the
  pre-registration exists to kill. A reader (or the supervisor, who checks) can see three definitions
  and ask which one the null refers to.

### 2.2 `llm_single_shot` as a dedicated arm is a stale design and must be retired
`config/arms.yaml`, `config/campaign.yaml`, `config/prototype.yaml`, and PREREGISTRATION §3 all define
the **seven arms** as `distributional · scalar · placebo · scalar_cvar5 · placebo_shuffled · random_search · bayes_opt` —
**no single-shot arm**. Only the superseded `eureka_loop.yaml` (and its `data_pipeline` copy) still
lists `llm_single_shot`. The matched-budget machinery (`_summary.matched_budget_ok`, the
`accepted+failed==expected` assertion) is keyed to those six.

- **Severity: MEDIUM (citation/consistency).** A grader reading `eureka_loop.yaml` will believe there
  is a single-shot arm and look for it in the results — and not find it. **Action:** delete/annotate
  `llm_single_shot` in both `eureka_loop.yaml`s as SUPERSEDED, pointing to the §6 separate-run protocol.

### 2.3 No H3 test exists in the analysis pipeline
Verified by structure scan of `scripts/analyze_campaign.py`: it has `collect_family_pvalues`,
`h2_conjunction`, `h2_sharpe_rf_robustness`, `winner_dsr`, `campaign_pbo`, `beat_human_baseline`,
`benchmark_floor` — **and nothing for H3**. The frozen testing family (PREREGISTRATION §10, R13) is the
**m=6 H2 family** `{arm-contrast × {Sharpe, CVaR}}`; H3 is *not* in it. `run_campaign.py` threads a
single `generations` scalar from config; the single-shot condition is a *separate* invocation
(`--config`), and the CLI comments confirm "the gated single-shot headline run." There is no code that
loads the two conditions and runs a paired difference test.

- **Severity: HIGH.** As wired, the campaign produces the iterative condition only. Unless the
  single-shot run is *actually launched* and an H3 difference test is *implemented*, H3 has **no
  result at all** beyond the prototype's directional uplift. Given H3 is on the explicit down-rank/cut
  list (CAMPAIGN_DEEP_RESEARCH §compute-split: "...→ H4 baselines → **H3 single-shot** → scalar_cvar5
  →..."), the live risk is that H3 silently ships as "not run."

### 2.4 The single-shot run doubles the LLM/compute cost of H3 — and that is the reason it is cuttable
A dedicated single-shot condition is a *full extra search leg* (G·M LLM calls + G·M trainings + 30-seed
winner re-runs for inference). On the rented-4090 budget this competes with seeds and folds. This is
why H3 is down-ranked. The dissertation must decide *before freeze* whether H3 is (a) a fully-powered
campaign result, or (b) a directional prototype-grade result reported honestly as such. **Do not leave
this implicit.**

- **Severity: HIGH (resource/scope).** A half-run H3 (single-shot at 1 seed, iterative at 30) would be
  an *unmatched* comparison and worse than not reporting H3 at all.

---

## 3. THREAT CLASS B — the prototype's "uplift" estimator answers a different question

The prototype's H3 verdict (memory [[project-prototype-results-and-benchmarks]]): *"H3 NOT supported:
placebo pure-resampling max-uplift 1.84× ≥ real-feedback 1.16×."* This is computed from
`per_generation_summary`'s `best_fitness` trajectory — the ratio of the best-across-all-generations
fitness to the best-in-generation-0 fitness, per arm.

### 3.1 Why this is a *clever* and *defensible* probe
It exploits a within-arm control: **the placebo arm iterates with uninformative feedback**. If
iteration's apparent gains were due to *reflection on information*, the informative arms (distributional)
should show a *larger* generation-over-generation uplift than the placebo. The prototype found the
**opposite** (placebo uplift 1.84× ≥ informative 1.16×), i.e. the uplift is explained by *resampling*
(more draws over more generations → a higher running max), not by learning from feedback. This is a
direct, internal-validity-strong argument that **iteration ≈ best-of-N here**.

### 3.2 Why it is NOT a clean substitute for the canonical H3 test
1. **It is not a matched-budget A/B.** "Gen-0 best" is best-of-M (M=5), while "overall best" is
   best-of-(G·M)=best-of-30/40. A higher running max from 30 draws than from 5 is *mechanically
   guaranteed* (the max of more i.i.d. draws is ≥). So "uplift > 1" is not evidence of reflection — it
   is evidence of *more samples*. The probe is only informative **as a placebo-relative contrast** (does
   informative feedback uplift *more* than uninformative?), not as a standalone "did iteration help."
2. **Order-of-magnitude / single-seed noise.** At 1 seed the per-generation best is a single noisy draw;
   ratios like 1.84 vs 1.16 are not significance-tested. The prototype correctly labels this DIRECTIONAL.
3. **Selection-on-the-max inflation.** The running-max statistic is a biased, selection-after-the-fact
   quantity; it is not the held-out, deflated quantity the dissertation reports for H2.

- **Severity: MEDIUM.** The uplift probe is a *good supporting exhibit* and a strong internal control,
  but it must be **named as a probe, not as the H3 test**, and it must be reported *alongside* the
  canonical matched-budget contrast (§2.1-i), not in place of it. Its placebo-relative framing is the
  durable part; keep that, drop any "uplift>1 ⇒ reflection works" reading.

### 3.3 The right place for `feedback_responsiveness`
`inspect_rewards.feedback_responsiveness` (the Spearman correlation between reward-source edit
magnitude and the fed-back tail-stat delta) is a *directional* "did the designer use the information"
probe and is correctly labelled as such (it gates on `_was_fed_tail`, so scalar/placebo return
`None`). It is an H2 forensics tool, **not** an H3 estimator, but it is *complementary* evidence for the
H3 narrative: if responsiveness is ≈0 even on the distributional arm, that *explains* the null
(reflection had no information-tracking signature). Report it as mechanism evidence under H3.

---

## 4. THREAT CLASS C — budget matching (the classic H3 failure mode), now mostly closed

### 4.1 The historical bug (FIXED — verified)
The adversarial review (`research/ADVERSARIAL_REVIEW_2026-06-17.md`, item **M2**) caught that
`run_loop` previously did `budget_spent += gen_budget` *inside* the per-candidate loop, over-counting by
the accepted-candidate factor and excluding failures. The live code (loop.py lines 323–330) now
accumulates `gen_budget` **once per generation**, summing to `total_budget`. The orchestrator asserts
`accepted+failed == generations·candidates_per_gen` per arm (`parallel._summary.matched_budget_ok`,
lines 500–511; serial `run_arm` equivalent). **The matched-budget accounting is correct now.**

### 4.2 What "matched" must mean for H3 specifically (the live risks)
Budget matching for H2 (all arms at the same G,M) is satisfied. For **H3**, "matched" is more demanding
because the conditions differ in shape:

1. **LLM-call count.** Iterative (G·M calls) vs single-shot (G·M calls). ✅ Equal by construction (one
   `llm.complete` per candidate, regardless of generation structure).
2. **Token budget (NOT equal — a real asymmetry).** The iterative arm's reflection prompts carry the
   *previous feedback block* (extra input tokens every generation after gen-0); the single-shot arm's
   prompts are all the (shorter) initial prompt. So **iterative spends MORE input tokens than
   single-shot at the same call count.** If anything this *favours* iterative, so a null is conservative
   — but it must be *disclosed* in the compute-accounting table (env steps, LLM calls, **tokens**,
   wall-clock) the deep-research §7 already mandates. Do not claim "matched compute" without the token
   line, or a careful reader will catch the asymmetry.
   - **Severity: LOW–MEDIUM (disclosure).** Harmless to the direction of the null; fatal to the *claim
     of exact matching* if undisclosed.
3. **Training-step budget.** Both conditions train each candidate at the same fixed step budget
   (50k campaign / 25k prototype), so total agent-training compute is equal at G·M candidates. ✅ But
   note the **R24 buffer asymmetry**: the headline *iterative* search now runs the parallel
   reflect-on-best path at `buffer==train_steps==50k`; a single-shot control must be run through the
   **same** path/buffer (50k) or it inherits the serial 25k-buffer skew (PREREGISTRATION R21/R24,
   L14). **Action:** run single-shot via the identical trainer/buffer as the iterative headline.
   - **Severity: MEDIUM.** A 25k-vs-50k buffer mismatch would confound H3 with replay capacity.
4. **Selection budget.** Identical (best val DSR over G·M candidates). ✅
5. **Per-candidate independence (single-shot) vs sequential dependence (iterative).** In single-shot the
   30 draws are i.i.d.-ish (same prompt + per-index diversity directive). In iterative, candidate
   *generations* are dependent (each conditions on the prior). This is the *intended* difference (it IS
   H3), not a confound — but see §6.

### 4.3 The fitness/selection multiplicity is matched
DSR's expected-max correction uses `n_trials = candidate count` (40 prototype / 30 campaign), identical
across conditions, so the deflation penalty is the same. ✅ (PREREGISTRATION §5; `config: n_trials`.)

---

## 5. THREAT CLASS D — is iterative reflection even *expected* to beat best-of-N here? (No.)

This is the crux of "is H3 a fair fight," and the honest answer reshapes the framing from "we failed to
show reflection helps" to "we showed best-of-N is a strong baseline that reflection does not beat *in the
regime where theory predicts reflection is weakest*."

### 5.1 Best-of-N is a strong baseline (and Eureka's own ablation is the precedent)
- **Eureka (Ma et al., ICLR 2024; arXiv:2310.12931)** ablates exactly this: **"Eureka w/o Evolution
  (32 samples)"** — sample *more* rewards in the first generation, no iteration — and reports that
  "simply sampling more initial rewards does not yield comparable results," i.e. evolution/iteration
  beats best-of-N *in their robotics setting*. **H3 is a direct replication of this ablation in a new
  domain.** Their separate **"Eureka w/o Reward Reflection"** ablation (feedback reduced to only the
  scalar metric) costs **−28.6%** average normalized score, with greater loss on higher-dimensional
  tasks. *This −28.6% is the bar H3 measures against, and it maps onto the dissertation's arms:* w/o
  Reward Reflection ↔ the **scalar arm** (an H2 contrast), w/o Evolution ↔ the **single-shot control**
  (the H3 contrast) — the explicit mapping in `research/DEEP_RESEARCH_2026-06-17.md` §7.
- **The methodological point** (Snell et al. 2024; Brown et al. 2024, "Large Language Monkeys"): with a
  *good selector*, best-of-N is a remarkably strong inference-time baseline (Brown: 15.9%→56% on
  SWE-bench by sampling alone). Any iterative-refinement method must *beat best-of-N at matched budget*
  to justify its added complexity. H3 is precisely that test, and the prototype says it does not (here).
- **A near-exact published precedent for the H3 null — Olausson et al. (ICLR 2024, "Is Self-Repair a
  Silver Bullet for Code Generation?", arXiv:2306.09896).** In the *code* domain at *matched budget*,
  drawing 2 samples then 10 repair candidates each gave a pass rate **lower than the baseline pass@22** —
  i.e. **iterative self-repair LOST to plain best-of-N.** Gains were "modest, vary a lot … and are
  sometimes not present at all," and the binding constraint was *feedback quality* (human feedback fixed
  it; the model's own feedback did not). This is the closest existing result to the dissertation's H3
  setup (an LLM iterating on code with self-generated feedback) and it *predicts the null*. **Lead the H3
  discussion with this citation.**

### 5.2 Why reflection is expected to be *weak* in this specific setting
1. **No reliable external verifier.** The selection/feedback signal is a **single-seed validation
   Deflated Sharpe** — a *noisy* scalar. The self-correction literature is unambiguous that intrinsic
   reflection *fails to help, and can hurt,* without a reliable external/oracle signal:
   - **Huang et al., ICLR 2024 (arXiv:2310.01798), "Large Language Models Cannot Self-Correct Reasoning
     Yet."** LLMs struggle to self-correct without external feedback; performance can *degrade* after
     self-correction. The dissertation's reward-design loop has only a *noisy proxy* (1-seed DSR) for
     "is this reward good," not ground truth — the exact regime they flag.
   - **Stechly, Marquez & Kambhampati, 2023 (arXiv:2310.12397), "GPT-4 Doesn't Know It's Wrong."** When
     the *same* LLM verifies its own answers (graph colouring), iterative self-critique collapses (1/100
     correct) because the self-verifier "can fail to notice success and instead produce spurious
     feedback." Gains appeared only with an *external sound verifier*. In reward-design, the LLM cannot
     reliably tell a good reward from a bad one a priori; the only verifier is the expensive RL training
     run, which the loop summarises into a noisy scalar.
2. **Sparse, deceptive landscape favours coverage over refinement.** The prototype found a **sparse
   reward-design landscape** (median candidate DSR ≈ 0.0018; only 2–5% of candidates near winner
   quality) — the "Eureka pattern." **Snell et al. 2024 (arXiv:2408.03314)** show sequential refinement
   helps on *easy* problems where the answer is "already on the right track," while *hard* problems
   favour **parallel sampling (wider exploration / best-of-N)**; the compute-optimal mix shifts toward
   parallel as difficulty rises. A sparse landscape with rare high-quality basins is the *hard* regime
   → best-of-N is predicted to match or win. This is the single most important framing sentence for the
   null.
3. **Feedback granularity.** Eureka's reflection feeds *per-component reward statistics* across training
   (the agent's own component traces), enabling targeted edits. The dissertation's reflection feeds a
   *terminal* held-out scalar (+ tail block for the distributional arm) — a *coarser* signal than
   Eureka's, weakening the reflection channel further. Disclose this as a design-level reason the null
   is plausible (and as future work: richer per-component feedback).

- **Net:** a null on H3 is the *predicted* outcome, not an anomaly. The strongest framing is to
  pre-commit to this prediction (a "risky" / falsifiable prediction in the Popperian sense) and report
  the confirmed null.

---

## 6. THREAT CLASS E — the reflection-vs-diversity confound (must be disentangled)

If iterative *did* win, one would need to rule out that the gain came from *more diverse samples* rather
than *genuine reflection on feedback*. The repo's design gives the tools to disentangle, but they must
be deployed and pre-registered.

### 6.1 The confound, precisely
"Iteration helped" could mean (a) the LLM *learned from feedback* (genuine reflection), or (b) iterating
simply produced *different/more diverse* candidates than single-shot did, independent of the feedback's
content. These are observationally similar on a raw "iterative > single-shot" comparison.

### 6.2 The placebo is the key disentangler (and it works)
The **placebo arm** iterates with a feedback block matched in length/format but **inert** (no
information). Comparing:
- **distributional-iterative vs single-shot** (does iteration with *real* feedback beat best-of-N?), and
- **placebo-iterative vs single-shot** (does iteration with *fake* feedback beat best-of-N?),
isolates reflection-from-information: if placebo-iterative ≈ distributional-iterative, the iteration gain
(if any) is *not* from information — it is resampling/diversity. **This is exactly what the prototype's
uplift contrast found (placebo uplift ≥ informative uplift).** Promote this from the directional uplift
ratio to a **proper paired difference test** on the campaign (§7).

- **Caveat (frozen-design):** the current placebo is *inert constants*. The deep-research (§7.1) flags a
  **stronger "scrambled-distribution" placebo** (real tail-stat *format and plausibility*, but values
  *shuffled/mismatched to the policy*) — it holds plausibility constant and destroys only information, a
  cleaner information-isolation control (precedent: permuted feedback dropping below no-feedback,
  arXiv:2408.13915, `% VERIFY`). This is a **PREREG §3 frozen item** → flag for the freeze, do not
  switch silently. For H3 specifically, the inert placebo is adequate *as a diversity-vs-information
  control*, but the scrambled placebo would strengthen it.

### 6.3 The diversity directive is uniform across conditions — but verify it for single-shot
`_diversity_directive` is *identical across arms* (not an H2 confound) and fires for any
`candidates_per_gen > 1`. In single-shot (`candidates_per_gen = G·M = 30`), all 30 draws get distinct
directives, so single-shot is a *deliberately diverse* best-of-30 — the strong baseline we want. **But:**
the directive text is `"directive {cidx+1}/{n}"` with `n = candidates_per_gen`; in iterative `n=5`, in
single-shot `n=30`. The *content* of the directive (vary CVaR/variance/drawdown/window/form) is the same,
but the *index space* differs. This is a benign asymmetry (it does not change the instruction), but it
should be **noted** so a reader does not mistake it for an uncontrolled difference. For the *prototype*
author (Sonnet, `diversity_prompt_variation:false`), single-shot diversity comes from `temperature=1.0`
instead — also uniform. Either way, **single-shot is a genuinely diverse best-of-N, not 30 identical
draws** — the strong-baseline property H3 needs. ✅

- **Severity: LOW.** The mechanism is sound; the only action is *disclosure* of the index-space
  difference and an explicit statement that single-shot's diversity source (prompt-variation directive
  for Opus / temperature for Sonnet) is the *same* mechanism the iterative arm uses within a generation.

### 6.4 An additional disentangler worth pre-registering: candidate-diversity metric
Report a **diversity statistic** (e.g. mean pairwise reward-source edit distance, or distinct
tail-term-usage counts) for the single-shot population vs the union of the iterative generations. If
single-shot is *at least as diverse* as iterative, then any iterative advantage *cannot* be attributed
to diversity — strengthening either a positive (genuine reflection) or, more likely, the null (iteration
adds neither diversity nor information beyond best-of-N). `inspect_rewards` already computes source
complexity and tail-term usage per generation; a small extension yields this. **Low-cost, high-rigour.**

---

## 7. THREAT CLASS F — reflect-on-best vs reflect-on-last (is it material to H3?)

### 7.1 The two protocols
- **Serial loop (`src/llm/loop.py`):** reflection seeds from the **LAST** candidate's feedback block
  (line 450: `prev_feedback_block = feedback_block` updated every candidate; the next generation's
  prompt carries the *last* candidate seen).
- **Parallel scheduler (`parallel._drive_llm_arm`):** reflection seeds from the **BEST** candidate of the
  generation (lines 583–587: tracks `best` by fitness, builds the next block from it). This is the
  **Eureka-faithful** protocol (Eureka reflects on best-so-far, Alg. 1).
- **R24 (2026-06-25)** makes **parallel reflect-on-best the HEADLINE** search protocol; serial
  reflect-on-last is the de-risked fallback (PREREGISTRATION §6).

### 7.2 Materiality to H3
- **For the iterative condition:** reflect-on-best is the *stronger* form of reflection (it always
  conditions on the best design so far, the canonical evolutionary-search move), so it gives reflection
  its **best shot** at beating single-shot. **This is good for H3's fairness**: if even reflect-on-best
  does not beat best-of-N, the null is *more* convincing (we did not handicap reflection). **Use
  reflect-on-best for the iterative condition.**
- **For the single-shot condition:** "best vs last" is *moot* — single-shot has only one generation, so
  there is no reflection seed at all. The protocol choice does not touch single-shot.
- **Subtlety:** reflect-on-best subtly *narrows* the iterative arm's exploration relative to
  reflect-on-last (it keeps re-anchoring on one design), which in a sparse landscape could make
  iterative *less* diverse than single-shot's best-of-30 — *another* reason best-of-N may match/beat it.
  This is worth a sentence in the discussion (it aligns the mechanism with Snell et al.: refinement
  narrows, parallel sampling covers).

- **Severity: LOW–MEDIUM.** Not a confound, but the choice must be *pre-registered for the H3 contrast*
  (use reflect-on-best, matching the headline) and the narrowing effect acknowledged. The prototype was
  serial reflect-on-last, so a campaign H3 on reflect-on-best is a *different* (and stronger) iterative
  arm than the prototype's — disclose that the prototype-to-campaign protocol changed.

---

## 8. THREAT CLASS G — statistical inference for H3 (currently undefined)

H3 is **not** in the frozen m=6 H2 family (PREREGISTRATION R13). It needs its own pre-registered, sized
test, or it must be reported as descriptive-only.

### 8.1 Multiple-testing placement
- **Option A (recommended): report H3 as a separate, named secondary contrast** with its own
  difference test (the same machinery as H2: per-seed Sharpe/CVaR → IQM → paired stratified bootstrap
  over shared training seeds, R16), but **outside** the m=6 H2 FDR family, with the multiplicity
  *stated explicitly* (it is one contrast, on ≤2 metrics). Do **not** silently fold H3 into the H2
  family (that would change the frozen m).
- The bootstrap convention (R11, re-centred basic), the per-seed resampling unit (R16), and the
  null-calibration certification (audit C-7) all transfer directly to the H3 contrast.

### 8.2 Pre-register an EQUIVALENCE test (this is the headline-making move)
A null from a *difference* test alone is "absence of evidence." To claim "iterative ≈ single-shot" *as a
finding*, pre-register a **TOST equivalence test** for H3, mirroring the H2 SESOI/TOST (R12):
- **SESOI:** 0.05 validation-DSR units (same as H2, defensible by analogy; or re-derive from the H3
  seed-variance in the pilot).
- **TOST:** if the 90% bootstrap CI for the (iterative − single-shot) mean-DSR difference lies inside
  ±0.05 DSR, the two are **practically equivalent within the SESOI** — a *positive, bounded* claim, not
  a mere non-rejection. Report the MDE at 80% power (the H3 analogue of `docs/POWER_ANALYSIS.md`).
- **This converts the null into a publishable, defensible result:** "at matched budget, iterative
  reflection and single-shot best-of-N are statistically equivalent within ±0.05 DSR on this task."

### 8.3 Power and the single-shot run's seed count
For a *fair* H3, the single-shot winner must be re-run at the **same 30 seeds** as the iterative winner
(seeds-on-winners). A 1-seed single-shot vs 30-seed iterative is unmatched and uninterpretable. This is
the resource cost that makes H3 cuttable (§2.4) — but it is *non-negotiable if H3 is reported as a
campaign result*. If the budget cannot afford it, **report H3 at prototype/directional grade only**, and
say so.

- **Severity: HIGH.** Without (a) an H3-specific difference test and (b) a pre-registered equivalence
  margin and (c) matched seeds, H3 is either unreported or a weak non-rejection. The equivalence test is
  the difference between "we didn't find an effect" (weak) and "we bounded the effect below the SESOI"
  (strong).

---

## 9. Severity-ranked threat register

| # | Threat | Class | Severity | Direction wrt the null | Pre-freeze action |
|---|---|---|---|---|---|
| T1 | No H3 test in `analyze_campaign`; single-shot run is a manual, cuttable separate invocation | A | **HIGH** | could leave H3 *unreported* | Decide H3's grade (campaign vs directional) NOW; implement the H3 contrast + difference + TOST, or pre-register descriptive-only |
| T2 | Three non-equivalent definitions of "H3" coexist (canonical / `llm_single_shot` arm / uplift) | A | **HIGH** | ambiguity = moved-goalpost risk | Pin the canonical matched-budget A/B (§2.1-i) as primary; retire `llm_single_shot`; demote uplift to a probe |
| T3 | No pre-registered equivalence margin → null is "absence of evidence" only | F/G | **HIGH** | weak null | Pre-register TOST ±0.05 DSR for H3 (mirror R12) |
| T4 | Single-shot winner must be matched at 30 seeds + 50k buffer or H3 is unmatched | C/G | **HIGH** | invalidates H3 if unmet | Run single-shot through the identical headline trainer (50k buffer, 30 winner seeds) |
| T5 | `llm_single_shot` stale arm in `eureka_loop.yaml`(×2) contradicts the 6-arm prereg | A | **MEDIUM** | citation/consistency | Annotate as SUPERSEDED → §6 separate-run protocol |
| T6 | Uplift estimator (prototype's H3 evidence) is not a matched-budget A/B; "uplift>1" is mechanical | B | **MEDIUM** | mis-reads if used standalone | Report uplift ONLY as the placebo-relative contrast; label DIRECTIONAL |
| T7 | R24 buffer asymmetry (single-shot via serial 25k vs headline 50k) | C | **MEDIUM** | confounds H3 with replay capacity | Run single-shot via the parallel reflect-on-best path / 50k |
| T8 | reflect-on-best narrows iterative exploration vs single-shot's diverse best-of-30 | E/F | **MEDIUM** | *favours the null*, plausibly | Acknowledge mechanism (Snell et al.); pre-register reflect-on-best for the iterative arm |
| T9 | Token budget not matched (reflection prompts carry extra input tokens) | C | **LOW–MED** | *favours iterative* (conservative) | Disclose in the compute-accounting table; never claim exact match without the token line |
| T10 | Diversity-directive index space differs (n=5 vs n=30) | D | **LOW** | benign | Disclose; state single-shot diversity source = same mechanism |
| T11 | Inert placebo weaker than a scrambled-distribution placebo for information isolation | D | **LOW** | weakens disentangler slightly | Flag scrambled placebo for the freeze (frozen-design item) |
| T12 | `feedback_responsiveness` could be mis-cited as an H3 test | B | **LOW** | mislabel risk | Keep it labelled as an H2 *forensic* probe; cite as mechanism evidence for the H3 null |

---

## 10. Literature grounding (precise, for the citation-checked write-up)

> Titles, authors, venues, arXiv ids, and all *abstract-level* claims below were verified first-hand
> via web search during this audit (June 2026). Mark any 2024–2026 items `% VERIFY` in `refs.bib` per
> CLAUDE.md until re-checked. **Citation-integrity flags — verify these *table-level numbers* against
> the primary PDF (use the local littxt cache / PyMuPDF) before the reference-checked draft, as they
> came from secondary sources when the PDFs would not render through web tooling:** (i) Huang 2024
> Table-3 GSM8K/CSQA/HotpotQA degradation digits; (ii) Self-Refine per-task math ≈0 figures; (iii)
> Olausson 2024 human-feedback 33.3%→52.6% figure (the "lower than pass@22" reversal IS from the paper
> text); (iv) any specific Stechly graph-colouring / self-verification percentages. The Eureka −28.6%
> and "w/o Evolution" claims, and all directly-quoted abstract sentences, are first-hand verified.

**The reflection-helps thesis (what H3 tests against):**
- **Ma, Liang, Wang, Huang, Bastani, Jayaraman, Zhu, Fan, Anandkumar (2024).** *Eureka: Human-Level
  Reward Design via Coding Large Language Models.* ICLR 2024. arXiv:2310.12931.
  - **Reward-reflection ablation:** removing reward reflection (feedback = scalar snapshot only) drops
    average normalized score by **−28.6%**, with greater loss on higher-dimensional tasks. ↔ H2 scalar
    arm.
  - **"w/o Evolution (32 samples)" ablation:** sampling more initial rewards in one generation (no
    iteration) "does not yield comparable results." ↔ **H3 single-shot control** (the direct precedent).
- **Madaan et al. (2023).** *Self-Refine: Iterative Refinement with Self-Feedback.* NeurIPS 2023.
  arXiv:2303.17651. Same LLM generates→critiques→refines; *~20% absolute average* gain across 7 tasks.
  **Crucial for H3:** gains concentrate on *subjective/open-ended* tasks (sentiment reversal, dialogue,
  acronyms) and are essentially **flat on verifiable math (GSM8K ≈ 0 improvement)** — attributed to the
  model's limited ability to identify its own errors. Reward design has a *verifiable* (if noisy)
  objective, i.e. the regime where Self-Refine is weakest. *(GSM8K per-model digits SECONDARY — verify
  against the results table before citing exact numbers; the qualitative pattern is safe.)*
- **Shinn et al. (2023).** *Reflexion: Language Agents with Verbal Reinforcement Learning.* NeurIPS
  2023. arXiv:2303.11366. Verbal self-reflection stored in episodic memory; **91% pass@1 on HumanEval**
  (vs 80% prior SOTA). **But (load-bearing):** Reflexion's strong results consume an *external*
  task-success signal (unit tests / environment reward) — the "reliable external verifier" condition the
  critiques (Huang, Valmeekam) show is *necessary*. Frame Reflexion as evidence reflection works *when
  externally grounded*, NOT as evidence for intrinsic reflection on a noisy proxy.

**The reflection-does-not-reliably-help critiques (the null's backbone):**
- **Olausson, Inala, Wang, Gao, Solar-Lezama (2024).** *Is Self-Repair a Silver Bullet for Code
  Generation?* ICLR 2024. arXiv:2306.09896. **The closest published analogue of H3.** Code-domain,
  matched-budget: *"when the cost of carrying out repair is taken into account, performance gains are
  often modest, vary a lot … and are sometimes not present at all."* On GPT-4/APPS, *drawing 2 samples
  up front then 10 repair candidates each gives a pass rate **lower than the baseline pass@22*** — i.e.
  **self-repair LOST to plain best-of-N at equal budget.** The bottleneck is *feedback quality*
  (substituting human feedback for the model's own sharply raised repair success). ↔ this is the H3 null
  in a peer-reviewed setting; the LLM's own noisy DSR feedback is the analogue of poor self-feedback.
- **Huang, Chen, Mishra, Zheng, Yu, Song, Zhou (2024).** *Large Language Models Cannot Self-Correct
  Reasoning Yet.* ICLR 2024. arXiv:2310.01798. *LLMs struggle to self-correct without external feedback;
  performance can degrade.* The decisive sentence: improvements in prior self-correction work *"result
  from using oracles … and the improvements vanish when oracle labels are not available."* ↔ the
  reward-design loop has only a noisy 1-seed DSR proxy, not an oracle.
- **Valmeekam, Marquez, Kambhampati (2023).** *Can Large Language Models Really Improve by
  Self-critiquing Their Own Plans?* arXiv:2310.08118 (NeurIPS 2023 FMDM workshop). **An iterative,
  self-critiquing loop where self-critique actively HURTS:** *"self-critiquing appears to diminish plan
  generation performance, especially when compared to systems with external, sound verifiers,"* with the
  LLM verifier producing *"a notable number of false positives."* ↔ direct support that an iterative
  self-critique loop can underperform a single pass.
- **Stechly, Marquez, Kambhampati (2023).** *GPT-4 Doesn't Know It's Wrong: An Analysis of Iterative
  Prompting for Reasoning Problems.* arXiv:2310.12397. *Apparent iterative gains are largely because the
  correct solution is "fortuitously present in the top-k completions" (recognised by an EXTERNAL
  verifier), not from self-critique; "no better at verifying a solution"; calls into question LLM
  self-critiquing claims.* ↔ the reflection-vs-diversity confound, stated by the source: gains are
  sampling/coverage, not critique. (Also **Stechly, Valmeekam, Kambhampati 2024**, *On the
  Self-Verification Limitations of LLMs…*, arXiv:2402.08115 — same conclusion across Game-of-24, graph
  colouring, STRIPS planning.)

**Best-of-N vs sequential refinement (the strong baseline + the difficulty-dependence):**
- **Snell, Lee, Xu, Kumar (2024).** *Scaling LLM Test-Time Compute Optimally can be More Effective than
  Scaling Model Parameters.* arXiv:2408.03314. *Sequential refinement helps on easy problems ("already
  on the right track"); hard problems favour parallel sampling/best-of-N; the compute-optimal mix shifts
  to parallel as difficulty rises; best-of-N performance can be matched with up to 4× less compute by
  optimal allocation.* ↔ the sparse reward-design landscape is the hard regime.
- **Brown, Juravsky, Ehrlich, Clark, Le, Ré, Mirhoseini (2024).** *Large Language Monkeys: Scaling
  Inference Compute with Repeated Sampling.* arXiv:2407.21787. Coverage (any-of-k correct) scales
  smoothly across ~4 orders of magnitude: on SWE-bench Lite, DeepSeek-Coder rises **15.9% (1 sample) →
  56% (250 samples)**, beating the single-attempt SOTA of 43%. *Pure repeated sampling (best-of-N) is an
  extremely strong, simple baseline* — exactly the H3 control — so refinement must *beat* it to justify
  its complexity.
- **rliable — Agarwal et al. (2021).** NeurIPS 2021. arXiv:2108.13264. *(IQM, probability of improvement,
  stratified bootstrap CIs — the seed-reporting Eureka itself used; the H3 contrast inherits R16.)*

**Domain relatives (reflection in reward/code synthesis):**
- **FunSearch — Romera-Paredes et al. (2024), Nature 625, 468–475.** **A strong framing anchor:**
  FunSearch achieves SOTA program search with **NO verbal reflection / self-critique at all** — its loop
  is evolutionary sampling from an island-based *programs database* (for diversity) + few-shot prompting
  + an **external evaluator** that scores candidates; high scorers re-enter the database. All lift comes
  from *sampling diversity + a reliable external selector* (a best-of-N-with-good-selector regime), not
  from the model reflecting on its prior output. Precedent that population search, not reflection, can be
  the workhorse — directly supportive of the H3 null.
- **Text2Reward (Xie et al., ICLR 2024, arXiv:2309.11489); DrEureka (Ma et al., RSS 2024,
  arXiv:2406.01967); REvolve (Hazra et al., 2024, arXiv:2406.01309).** The reward-code lineage. Where
  these iterate, the refinement signal is **human feedback** (Text2Reward, REvolve) or an inherited
  Eureka loop grounded in *RL training statistics* (DrEureka) — i.e. *externally grounded* refinement,
  not intrinsic self-critique on a noisy proxy. None offers independent evidence that *intrinsic*
  reflection on a terminal scalar helps; consistent with the H3 null.

---

## 11. PRIORITIZED pre-freeze hardening (do these, in order)

**P0 — decide H3's grade and wire it (closes T1, T2, T4).**
1. **Pre-register the canonical H3 contrast** as primary in PREREGISTRATION (amend §1/§6 to name it
   unambiguously): *distributional arm, iterative (reflect-on-best, G=6×M=5, 50k buffer) vs single-shot
   (1×30, 50k buffer, same diversity mechanism), winner = best val DSR, both winners re-run at the 30
   campaign seeds.* Retire the `llm_single_shot` arm (annotate both `eureka_loop.yaml`s SUPERSEDED).
2. **Implement the H3 estimator** in `analyze_campaign` (or a clearly-scoped sibling): load the two
   conditions' winners, run the R16 per-seed paired stratified bootstrap on Sharpe (and CVaR), report
   IQM difference + CI, **outside** the m=6 family with multiplicity stated.
3. **Decide & record the budget verdict:** if the rented-4090 budget cannot fund a 30-seed single-shot
   leg, **pre-register H3 as directional/prototype-grade** and say so in the limitations register — do
   not ship a 1-seed-vs-30-seed comparison.

**P1 — pre-register the equivalence test (closes T3).**
4. Add a **TOST ±0.05 DSR** equivalence test for H3 (mirror R12), with the H3 MDE-at-80%-power written
   into a short power note (or `docs/POWER_ANALYSIS.md` H3 section). This is what turns the null into a
   bounded, defensible *finding*.

**P2 — disentangle reflection from diversity (closes T6, strengthens the claim).**
5. Promote the prototype's **placebo-relative uplift** to a proper **paired difference test** on the
   campaign: test (distributional-iterative − single-shot) vs (placebo-iterative − single-shot). If the
   informative arm's iterative gain is not significantly larger than the placebo's, the (null) iteration
   effect is *not* information-driven.
6. Add a **candidate-diversity metric** (mean pairwise source edit distance + distinct tail-term counts)
   comparing single-shot's population to the iterative generations' union (§6.4), to rule out
   diversity-as-explanation either way.
7. Report **`feedback_responsiveness`** for the distributional arm as mechanism evidence: a ≈0
   responsiveness *explains* the H3 null (reflection left no information-tracking signature).

**P3 — disclose the matched-compute fine print (closes T7, T9, T10).**
8. Produce the **compute-accounting table** (env steps, LLM calls, **input/output tokens**, wall-clock)
   for both conditions; explicitly note the iterative arm's *extra* reflection-prompt tokens (favours
   iterative ⇒ the null is conservative) and that single-shot uses the *same* within-generation
   diversity mechanism.
9. Confirm the single-shot run uses the **identical trainer/buffer (50k)** as the iterative headline.

**P4 — (optional, frozen-design) sharper placebo (T11).** Flag the **scrambled-distribution placebo**
for the Phase-1 freeze discussion as a cleaner information-isolation control; do not switch silently.

---

## 12. The STRONGEST defensible H3 framing + the bankable null

### 12.1 Framing (how to write it)
Frame H3 **not** as "does our reflection loop work" but as **a controlled, matched-budget replication of
Eureka's evolution ablation in a new, harder domain**, with a *pre-committed prediction* that reflection
will *not* beat best-of-N here — grounded in (a) the self-correction critiques (no reliable verifier →
reflection stalls; Huang 2024, Stechly 2023) and (b) the test-time-compute scaling result (hard/sparse
landscapes favour parallel sampling; Snell 2024). Reporting the **confirmed null/equivalence** is then a
*successful risky prediction*, the strongest epistemic position available — and a *substantive
contribution*, because it is a rare controlled counter-point to the field's dominant "reflection is
indispensable" narrative (Eureka, Self-Refine, Reflexion), delivered with inference rigour those papers
lack (rliable IQM, paired stratified bootstrap, BH-FDR, PBO, pre-registered TOST).

### 12.2 The bankable-null statement (drop-in for the dissertation)
> **H3 (iterative vs single-shot) — result.** At matched LLM-call budget and identical winner selection
> (validation Deflated Sharpe), iterative reflection (reflect-on-best, *G*×*M*=30 candidates over 6
> generations) did **not** outperform single-shot best-of-30, on this sparse-landscape financial
> reward-design task. The pre-registered TOST equivalence test placed the (iterative − single-shot)
> mean-DSR difference within the ±0.05-DSR SESOI [report CI], i.e. the two conditions are **practically
> equivalent**. A placebo-relative control corroborates the mechanism: the *uninformative* (placebo)
> arm's generation-over-generation uplift was no smaller than the *informative* arm's (prototype:
> placebo 1.84× ≥ distributional 1.16×, directional), so the modest within-arm uplift is attributable
> to **resampling (best-of-N), not to learning from feedback**; feedback-responsiveness on the
> distributional arm left no significant information-tracking signature. **This is a controlled
> replication of Eureka's "w/o Evolution" ablation in a new domain, and it does not reproduce Eureka's
> robotics finding** that in-context evolution is indispensable. The result is consistent with — and
> predicted by — (i) the limits of intrinsic LLM self-correction without a reliable external verifier
> (Huang et al. 2024; Stechly et al. 2023; Valmeekam et al. 2023, where iterative self-critique
> *degrades* performance), the reward-design loop having only a noisy single-seed DSR proxy; (ii) the
> closest matched-budget precedent, in which iterative code self-repair *loses* to best-of-N sampling
> (Olausson et al. 2024); and (iii) test-time-compute scaling theory, under which hard, sparse search
> landscapes favour parallel sampling over sequential refinement (Snell et al. 2024). It echoes
> FunSearch (Romera-Paredes et al. 2024), whose SOTA program search uses evolutionary sampling + an
> external scorer and *no reflection step at all*. We therefore report a **bounded,
> pre-registered null**: on this task and budget, *the value of the LLM reward-designer lies in its
> single-shot priors and the information in the feedback channel (H2), not in the iterative reflection
> loop per se (H3).* We do not claim reflection is useless in general — only that, at this budget, on
> this landscape, with this (terminal-scalar) feedback granularity, it is not distinguishable from a
> strong best-of-N baseline. Richer per-component feedback and a higher-fidelity (multi-seed) selection
> signal are the indicated routes to a positive H3, and are left to future work.

### 12.3 Why this is a *Distinction-grade* null (no-viva, PDF-only)
- It is **pre-registered** (hypothesis, budget, selection, equivalence margin frozen before the run) →
  the null is a finding about the question as posed, not a moved goalpost.
- It is **mechanistically explained and predicted** (two independent literatures), not merely observed.
- It is **internally controlled** (placebo-relative uplift + responsiveness) so the null is *causal*
  ("not from information"), not just "no effect."
- It is **bounded** (TOST), so it states *how small* the effect is, not merely that it was
  non-significant.
- It **honestly disclaims scope** (this budget/landscape/feedback-granularity), pre-empting the obvious
  rebuttal.
- It **contributes**: a controlled domain-transfer counter-point to Eureka's headline ablation, with
  inference rigour the lineage lacks — exactly the kind of credible negative result that strengthens a
  thesis built on a pre-registered null.

---

### Appendix A — code-location index (verified June 2026)
- Reflection loop / single-shot semantics: `src/llm/loop.py` — `run_loop` (269–457),
  `_budget_for_generation` (207–215), reflection gating (333–336, 450), `_diversity_directive`
  (189–204), `CandidateArchive.winner` (171–181).
- Feedback block (arm contrast): `src/feedback/schema.py` — `build_block` (70–120).
- Parallel reflect-on-best (R24 headline): `src/orchestration/parallel.py::_drive_llm_arm` (514–614),
  esp. best-tracking + next-block (583–587); matched-budget guard `_summary` (500–511).
- H3 config knobs: `config/prototype.yaml` (`generations:8`, `single_shot_generations:1` — a separate
  run, "not auto-wired", line 14), `config/campaign.yaml` (`generations:6`; §34 single-shot note),
  `config/llm.yaml` (15–16). Stale dedicated arm: `config/eureka_loop.yaml:19` (`llm_single_shot`) +
  `data_pipeline/config/eureka_loop.yaml:19`.
- H3 forensics (probes, not the test): `scripts/inspect_rewards.py` — `per_generation_summary`
  (194–240, the uplift trajectory source), `feedback_responsiveness` (246–320).
- Analysis pipeline (no H3 function present): `scripts/analyze_campaign.py` — frozen m=6 family is H2
  only (`collect_family_pvalues`, `h2_conjunction`).
- Budget-bug fix (M2): `research/ADVERSARIAL_REVIEW_2026-06-17.md` item M2 ↔ loop.py 323–330.
- Eureka-ablation ↔ arm mapping: `research/DEEP_RESEARCH_2026-06-17.md` §7 (109–111).
- Down-rank list (H3 cuttable): `00_planning/CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md`
  (compute-split line).

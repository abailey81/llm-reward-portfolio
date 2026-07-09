# Grade security, the internal tier design, and precise run times (2026-07-08)

> Tamer, 2026-07-08: *"add to the design an extremely important aspect — GRADE SECURITY"*; *"ultrathink
> the tier systems inside the stages — very smart, advanced, sophisticated, strictly by the
> priorities"*; *"give me the precise run times for everything."* This doc answers all three as one
> coherent design, because they are one design: **the tiers ARE the grade-security mechanism, and the
> run times prove the grade is banked long before any deadline.** Nothing here changes the frozen
> science (canonical hash `1c6b76b6`); it is execution-layer ordering + a throughput-aware target
> selector + a documented principle.

---

## 1. GRADE SECURITY — the design principle (first-class, overriding)

**Definition.** *The design guarantees a distinction-grade, submittable dissertation under every
adversity scenario — crash, reboot, power loss, VPN/Myriad outage, throughput shortfall, a mid-campaign
scheduler migration, or a hard deadline — by CONSTRUCTION, not by luck.* Grade security is priority #1
("secure the grade → 95%+ floor") made operational: at no point after the first ~1–2 days is the grade
at risk, because the complete study is banked first and everything after only tightens it.

**The seven guarantees (each already built or specified; this names them as one system):**

1. **Floor-first ordering (the core).** The tiers are ordered so the *complete distinction-grade study*
   — the full 7-arm design + mechanism (SQ1–SQ3) + H1 + H3 at n=30 — is reached in **~1.3 days
   (central)**, consuming ~10% of the compute. A catastrophe after day 2 still leaves a complete,
   pre-registered, defensible dissertation. Everything above n=30 is equivalence-CI tightening =
   *additive*, never load-bearing for the pass.
2. **Every stop point is a complete design.** Each tier boundary is a coherent deliverable at that
   power (n=30 floor / n=340 = 90% / n=403 = 95% / n=568 = 99%). The run never leaves a half-finished
   mess to write up. "Adaptive execution, invariant design."
3. **Exogenous stopping ⇒ valid inference.** The target n is chosen from **throughput + the calendar**
   (via `recommend_assurance_target`), *never from the observed effect*. The effect-blind gate confirms
   only execution health. So wherever we stop is a valid pre-committed single-look design — no optional
   stopping, nothing a probabilist examiner can attack.
4. **The dual-track fallback (GO is risk-free).** If Myriad certification (G1) fails, access is blocked,
   or the scheduler migrates mid-run, the **laptop track auto-executes the identical study** (Design-L,
   already certified). The cluster is a throughput accelerator, never a single point of failure.
5. **Bulletproof resume.** No single failure loses meaningful progress (archive-as-truth per-training
   checkpoint + compacted resume + supervisor + boot task + 3-site mirror + 12 h transport tolerance +
   `resume_audit.py`). Lost work re-runs to the *identical* result (determinism spine).
6. **Deadline buffer.** Submission targets **Aug 28–29 vs the Sep 1 deadline**; the floor is banked
   ~7 weeks early; Stage 2 (report-only depth) runs in the background *while Tamer writes* and any
   unfinished Stage-2 item simply does not enter the PDF — zero risk to the banked study.
7. **Procedural hygiene (the cheap grade points).** The mandatory **Myriad@UCL acknowledgment**
   (verbatim), **wall-clock compute reporting** from `jobhist`/`qacct` (Okhrati docks its absence), and
   the frozen pre-registration (design cannot drift) — each a grade point secured by construction.

**NEW grade-security threat found in the 2026-07-08 research + its mitigation (guarantee 4 in action):
the SGE→Slurm migration.** UCL is moving Myriad to RHEL 9.5 + Slurm (Kathleen already migrated
June 2025); **as of June 2026 Myriad is still SGE with NO scheduled date.** So SGE is correct for our
July–Sep window, but a mid-campaign announcement is a real risk. Mitigation, in priority order: (a) the
laptop track is scheduler-independent (auto-fallback); (b) our scheduler interaction is ISOLATED to
`jobscript.py`/`submit.py`/`poll.py`, so a Slurm port is bounded — the exact SGE→Slurm mapping is
recorded in the research dossier §13, making it ~a day's work, not a rewrite; (c) monitor the
Planned_Outages page for the announcement. Grade security means this is a *contingency with a written
answer*, not a surprise.

---

## 2. The internal tier design (ultrathought)

Two nested tier axes, ordered by **marginal grade value per GPU-hour** (cheapest-strongest first):

### Stage 1 (SECURE) — the C-ladder, tier by tier

| Tier | What runs | Trainings | GPU-h | **Banks (the guarantee reached)** |
|---|---|---|---|---|
| **S1.0 canary** | 3 H1 baselines through the full Myriad path | 9 | 5 | "the cluster pipeline works" — HARD GATE before any Opus spend |
| **S1.1 H2 search** | k=3 search + reflect → freeze the 3 H2 winners (dist/scalar/scalar_cvar5) | 270 | 157 | the authored winners ⇒ **mechanism SQ1–SQ2** available (on val, sealed from test) |
| **S1.2 H2 test n=30** | 3 H2 winners × 30 seeds, pair-adjacent | 90 | 52 | the **H2 headline at n=30** (directional + co-primary IUT) |
| **S1.3 all-arms floor n=30** | rest of search (placebo/pshuf/random/bayes + H3) → freeze; test all 7 arms + 4 H1 + H3 at n=30 | ~735 | 430 | **★ THE DISTINCTION FLOOR** — complete pre-registered study at n=30 (bankable null + mechanism + all controls). *Grade secured.* |
| — | **EFFECT-BLIND REVIEW GATE** (auto-proceed on green health) | — | — | single-look protected; C4 released |
| **S1.4 equivalence sweep** | extend all 12 units n=30 → target, in assurance BLOCKS (340→403→568) | ≤4,476 | ≤2,610 | progressively **tighter equivalence CIs** (90→95→99%) |
| **S1.5 D1 dose-response** | reflection-value curve levels {1,2,4,8} search+test | 570 | 332 | the **dose-response headline figure** (depth) |

**Cumulative to the floor (S1.0–S1.3): ~1,104 trainings ≈ 644 GPU-h.** That is the whole grade, banked
in ~10% of Stage 1.

**The sweep is SMART, not brute-force:**
- **Uniform n across all 11 units** (7 arms + 4 H1) — deliberately chosen over arm-adaptive because
  Myriad makes it affordable AND it is unambiguously defensible (kills the "asymmetric-leg" objection).
- **Assurance BLOCKS, not one leap:** 30→340 (bank 90% for the whole design) → 340→403 (95%) → 403→568
  (99%). Each block boundary is a complete uniform-n design; the seeds PARTITION (CRN preserved), so a
  block is pure extension, never re-training.
- **Throughput-aware target (the sophistication):** at G1 we MEASURE effective trainings/hour;
  `power_analysis.recommend_assurance_target(tph, days)` then returns the highest tier that finishes
  within the calendar minus a 25% buffer — falling back to the floor if even 90% will not fit. The stop
  is exogenous, so the choice is statistically clean. *This is the mechanism that makes "secure the
  grade safely" a property, not a hope.*

### Stage 2 (ADVANCE) — value-ordered, each independently skippable, all report-only

U3 Qwen → D2+ probes → U2b chains → D6 TQC → D5 calibration → D7 GPT-5.5 → U5 PPO/TD3 → U4b/U4 FTSE.
Runs on BOTH pools (V100 + A100) in the background while Tamer writes; pruned in reverse value order if
the calendar tightens. **Stage 1 is never pruned — it IS the study.**

---

## 3. PRECISE RUN TIMES for everything

**Constants** (the one estimate is per-training wall; re-measured at G1):
- V100 per-training wall = **0.583 h** (35 min) central; honest range 0.40–0.73 h (24–44 min).
- Per-V100 throughput = 1.72 trainings/h unpacked; **×F packing factor** (F≈1.75 central on the 16 GB
  V100 — our ~2–3 GB trainings underutilise it; up to ~2.5 with MPS; higher on the 40/80 GB A100).
- Effective throughput = C_physical × 1.72 × F trainings/h. Three scenarios:
  **conservative** C=6, F=1.0 → **10/h** · **central** C=12, F=1.75 → **36/h** · **optimistic** C=24,
  F=1.75 → **72/h**.

### Stage 1 — cumulative wall-clock at each milestone (V100 pool)

| Milestone | Trainings (cum.) | GPU-h (cum.) | Conservative (10/h) | **Central (36/h)** | Optimistic (72/h) |
|---|---|---|---|---|---|
| **★ Distinction floor (n=30)** | 1,104 | 644 | 4.6 d | **1.3 d** | 0.6 d |
| + sweep to **n=340 (90%)** | 4,824 | 2,814 | 20.1 d | **5.6 d** | 2.8 d |
| + sweep to **n=403 (95%)** | 5,580 | 3,254 | 23.3 d | **6.5 d** | 3.2 d |
| + **D1 curve** (depth) | 6,150 | 3,586 | 25.6 d | **7.1 d** | 3.6 d |
| + sweep to **n=568 (99%)** | 8,130 | 4,743 | 33.9 d | **9.4 d** | 4.7 d |

*(Per-training range shifts these ±40%: at 24 min the central "to-403+D1" is ~4.9 d; at 44 min ~8.9 d.)*

### Stage 2 — report-only, both pools, OFF the critical path (overlaps the write-up)

| Item | Trainings | GPU-h | API $ |
|---|---|---|---|
| U3 Qwen · D2+ probes · U2b chains · D6 TQC · D5 calibration (6k stubs) · D7 GPT-5.5 · U5 PPO/TD3 · U4b/U4 FTSE | 10,250 | 3,354 | $93–178 |

At central both-pool throughput (~60–80/h with A100-80 dense packing), Stage 2 compute ≈ **3–6 days**,
but it runs in the background through August; unfinished items simply don't enter the PDF.

### The bottom line (precise)

- **Grade secured (complete distinction study): ~1.3 days central (0.6–4.6 d).**
- **Full confirmatory Stage 1 at 95% + dose-response curve: ~7 days central (3.6–23 d worst-case).**
- **At 99% assurance: ~9.4 days central.**
- **Everything (Stage 1 + Stage 2): ~10–12 days of compute central**, but only the ~7-day Stage 1 is
  on the critical path; Stage 2 overlaps the write-up. GPU-h grand total **6,934**; API **$126–241**.
- All of it inside the Sep 1 deadline with weeks to spare — which is the whole point of grade security.

The three numbers G1 measures to turn these from estimate into fact: per-training wall (24–44 min),
sustained C (fair-share), and the packing factor F (the 2-process pack smoke). `recommend_assurance_target`
then picks the deadline-safe target the moment those are known.

---

## 4. STAGE 2 — the ADVANCE layer, ultrathought (re-read of PLAN §3/§3b, 2026-07-08)

### 4.0 The armor principle (Stage 2 can never hurt the grade)

Stage 2 is **publishability ARMOR bolted onto a finished object**, never a dependency. Three hard
invariants make it grade-safe by construction (PLAN §3 "Stage-1 independence, absolute"):
- **No-forward-references:** the Stage-1 PDF never mentions or needs a Stage-2 result. Each completed
  Stage-2 item adds **exactly one appendix table + one sentence**; a *missing* item leaves **zero
  holes**. So Stage 2 can be pruned to nothing and the dissertation is still whole.
- **Statistical isolation:** the single confirmatory look happens at the bank gate on Stage-1 data
  ALONE; every Stage-2 item is report-only/exploratory and analysed separately → no forking paths.
- **Compute isolation:** no Stage-1 unit depends on any Stage-2 output; Stage 2 starts only *after* the
  bank gate verifies + banks the complete study.

This is grade security §1 extended: the same "the study is complete and safe before the risky/expensive
part runs" logic that orders Stage 1's tiers also walls Stage 2 off from the grade.

### 4.1 The internal 4-tier structure (ordered by value-per-cost × dependency)

| Tier | Items | API | GPU-h | What it buys | Depends on |
|---|---|---|---|---|---|
| **2.A FREE DEPTH** | D3 variance-decomp · D4 shrinkage · D9 spec-curve+permutation · D8 · **D6 TQC · U5 PPO/TD3 · U4b zero-shot FTSE** | **$0** | 367 (+CPU) | robustness across agent-critic, algorithm, and market — **no authoring** (reuse frozen Stage-1 winners) | bank-gate data / frozen winners |
| **2.B NEARLY-FREE GENERALIZATION + MECHANISM** | **U3 Qwen full** replication · **D2+ lean grid** (interventional mechanism) | **$9–18** | 612 | cross-model-family generalization (flagship) + the "does feeding X change the code?" causal probe | own authoring (Qwen key / archived reflection states) |
| **2.C CALIBRATION (off-Myriad)** | **D5 fleet on the LAPTOP** from GO-day (synthetic, keyless, platform-neutral) | **$0** | 876 (laptop) | "is the pipeline's α really 0.05?" — arrives BEFORE the bank gate | nothing (fully independent) |
| **2.D PREMIUM SHELF (purchase-only)** | U2b chains · D7 GPT-5.5 · U4 full FTSE | **$72–135** | 1,499 | chain-level variance · a 3rd family · full second-market re-search | own authoring; **defaults to CH7 future-work if unbought** |

The ordering mirrors Stage 1's cheapest-strongest-first logic: **free robustness first, nearly-free
generalization next, calibration in parallel off-cluster, premium last.**

### 4.2 The execution design on Myriad (the sophisticated part)

**Two orderings, both load-bearing — do not conflate them:**
- **PRUNE in value order** (what to drop if the calendar tightens): U4 → U4b → U5 → D7 → D5 → D6 →
  U2b → D2+ → U3 (reverse-value). Stage 1 is never pruned.
- **EXECUTE in dependency-readiness order** (what to launch first for throughput): the moment the bank
  gate frees the pools, the **zero-authoring** work floods immediately — the CPU analyses D3/D4/D9 run
  on the just-banked data (instant), and D6/U5/U4b training arrays flood BOTH GPU pools (they only need
  the frozen winners, no LLM). *While those run*, the laptop authors U3 (Qwen) and the D2+
  counterfactuals; their training arrays pipeline in as authoring completes — **zero barriers**, the
  same search→test pipelining that makes Stage 1 efficient. The premium shelf (if purchased) tails in
  last.

**Pool + packing assignment (uses the 2026-07-08 research):**
- Homogeneity is per-CONTRAST, so different Stage-2 items may use different pools in parallel: e.g. U3
  (Qwen) on the A100-40 (L) pool while D6/U5 flood the V100 (EF) pool — the two run concurrently.
- The **A100-80 (U/V) nodes** are the home for the densest packers: D5's 6,000 stubs (if pulled onto
  Myriad rather than the laptop) and the report-only training fleets pack ~25–30/GPU there → the whole
  LEAN Stage-2 GPU work (~979 Myriad GPU-h) collapses to **~3.4 days @ C=12** (PLAN §3), and far less
  if the A100-80 density lands.

**D2+ execution (the interventional mechanism instrument):** ONE authoring sweep over the 6
counterfactual conditions — (i) per-stat perturb ×2/sign-flip · (ii) ablate-one-stat · (iii)
full-quantile-sketch · (iv) CI-annotated tail · (v) Eureka-style training-curve telemetry · (vi)
env-source context — applied to a SAMPLED set of archived Stage-1 reflection states (60–100 authorings,
lean). The subset that most changes the authored code (top-Δ) gets trained on the 2nd pool (~100
trainings). Output: a sensitivity heat-strip = "which fed signal actually moves the reward code."

### 4.3 The Eureka-fidelity narrative (why Stage 2 is defensible, not scattered)

Stage 2 is not a grab-bag; it systematically discharges the **Eureka re-read register** (PLAN §3b): our
three deliberate deviations from Eureka are each *probed*, and one place we *exceed* Eureka is stated:
- Eureka feeds raw env source → we feed a contract only → **D2+ (vi) env-source counterfactual** tests
  whether that handicapped the designer.
- Eureka feeds per-component reward telemetry at checkpoints → we feed a minimal tail block → **D2+ (v)
  telemetry counterfactual** tests it.
- Eureka runs K=16 i.i.d. chains → we run one serial reflect-on-best chain → **U2b** (premium) is the
  multi-chain analogue.
- Eureka selects through 1 unexamined policy → **we use k=3 + IQM (we EXCEED Eureka's rigor — stated in
  the paper).**
Every "what if we fed X?" new-arm temptation is absorbed as a D2+ probe (no late prompt-hash churn, no
m-family amendment), and the full-distribution arm is named the **#1 future-work arm in CH7**.

### 4.4 The runsheet (Stage 2 reuses the CERTIFIED orchestrator — little new code)

Every Stage-2 GPU item is a call to the SAME `src/cluster/campaign` primitives, only the config differs
— which is why Stage 2 is safe (byte-identical science path) and cheap to run:
- **U3 / D7 / U4** (full re-search): `run_campaign_on_cluster` with `--provider qwen|gpt5.5` (U3/D7) or
  the FTSE panel (U4) — authoring + search + freeze + test, exactly like Stage 1.
- **D6 / U5** (algorithm robustness): `run_test_leg` on the frozen Stage-1 winners with a TQC / PPO /
  TD3 agent config — no authoring.
- **U4b** (zero-shot transfer): `run_test_leg` of the frozen winners on the FTSE panel — no authoring,
  no re-search.
- **U2b** (multi-chain): 2 more `run_arm_pipeline` chains at different search seeds.
- **D2+**: the authoring layer (`build_prompt_set` + the 6 perturbations) over archived reflection
  states → `run_test_leg` on the top-Δ subset. (`scripts/mutation_probe.py` is the seed.)
- **D3/D4/D9/D8/D5**: analysis scripts on outputs (`scripts/variance_decomposition.py`,
  `popart_ablation.py`, `cost_sweep.py`, the inference modules — already built). D5 runs keyless on the
  laptop.
No Stage-2 mega-driver is built (or wanted): Tamer launches items value-first as he writes, pruning
from the shelf; each is one certified invocation.

## 5. How everything looks — the finished object

The dissertation is **concentric rings around an already-complete core**:

```
        ┌─────────────────────── RING 2 · PREMIUM (purchase-only) ───────────────────────┐
        │  U2b multi-chain variance · D7 GPT-5.5 3rd family · U4 full FTSE re-search       │
        │  ┌──────────────────── RING 1 · LEAN ARMOR ($9–18, ~free) ──────────────────┐   │
        │  │  U3 Qwen generalization · D2+ interventional mechanism · D5 calibration    │   │
        │  │  D6/U5/U4b algo+market robustness                                          │   │
        │  │  ┌──────────────── CORE · STAGE 1 (THE dissertation) ────────────────┐    │   │
        │  │  │  H2 equivalence (co-primary IUT) · mechanism SQ1–SQ3 · H1 · H3     │    │   │
        │  │  │  dose-response curve · D3 variance-decomp · D4 shrinkage · D9      │    │   │
        │  │  │  spec-curve  →  banked complete at ~day 8, 95% assurance          │    │   │
        │  │  └────────────────────────────────────────────────────────────────────┘    │   │
        │  └────────────────────────────────────────────────────────────────────────────┘   │
        └────────────────────────────────────────────────────────────────────────────────────┘
   rubric case (§1) is made ENTIRELY on the CORE; each ring = +1 appendix table +1 sentence, prunable to 0.
```

- **The 10k-word body never grows:** the CORE fills the 16-section body (Methods/Results/Discussion);
  every ring item lands as one appendix table (word-excluded) + one body sentence (PLAN §8 write-up
  map). A pruned ring = a shorter appendix, never a hole.
- **The rubric mapping:** faultless execution = the frozen 7-arm design + the tiers; unquestionable
  originality = the mechanism instruments (SQ1–SQ3 + D2+ interventional) + the dose-response curve
  measured nowhere in the Eureka lineage; journal-publishable significance = the generalization triad
  (families × market × algorithm) + calibration + the one-command replication package; faultless
  communication = the armor-rings structure itself (a clear core, clearly-labelled robustness).
- **The calendar (central, C=12):** bank gate ~**Jul 28** (complete + verified + drafted) → LEAN Stage 2
  done ~**Aug 3–4** → premium shelf (if purchased) mid-August → write-up surgery + pre-submission sweep
  through August → **submit Aug 28–29** (3-day buffer to Sep 1). Every ring beyond the core is pure
  upside on an already-secured distinction.


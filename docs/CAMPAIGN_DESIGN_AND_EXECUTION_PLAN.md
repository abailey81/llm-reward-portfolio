# Campaign Design & Execution Plan — authoritative determination record

**Date:** 2026-06-29. **Status:** pre-freeze determination complete pending the 3 GPU pilots + 2 no-GPU
fixes. **Scope:** the complete, literature-grounded justification for every campaign parameter (training
steps, seeds, candidates, arms), the power analysis, the compute/time plan, the construct-validity
verification, the framing strategy, and the execution priority. This is the single source of truth for the
methods chapter and the pre-registration freeze.

> **⚠ SPLIT-C / univ5 SUPERSESSION (2026-07-02, ADR-044/051, prereg R73).** The data panel and splits this
> record reasoned over were re-partitioned and extended AFTER it was written (still pre-freeze, never
> results-contingent): the ACTIVE panel is **univ5** (5,406 × 963, 2005-01-03 → 2026-06-30 settled cutoff;
> byte-identical to univ3 on the overlap, 0 changed cells) under **SPLIT C** — train 2005–2016 / val
> 2017–2019 / **test 2020–2026H1** (sealed; purge 60 sessions; executed starts 2017-03-30 / 2020-03-30).
> Wherever the trail below says "test 2018–2025", "10y-3y-8y", "~2,520 train days", or "T≈756", read the
> Split-C values (marked inline); the determination framework, the per-parameter verdicts, and the
> literature grounding are otherwise unchanged. Track-length-dependent numbers (§4 power/K) are to be
> regenerated at the executed Split-C windows (`make power`). Statuses in §2/§11 are as of 2026-06-29 —
> `docs/DESIGN_DETERMINATION.md` (regenerated) is the live status table.

> **Determination principle (read first).** This is a CONTROLLED experiment: the agent is a fixed instrument
> and the *feedback channel* is the only manipulated variable. A system that searched parameters to MAXIMISE
> the headline result would be the garden of forking paths industrialised — it manufactures false positives,
> is unpublishable, and cannot even help a corroborated-NULL headline (a tuned-to-win agent *weakens* an
> equivalence claim). Therefore parameters are **not** optimised for performance. Each is resolved by the
> correct criterion for its class (see §1), and **nothing in this determination touches the sealed test
> split (2018–2025 as written; 2020–2026H1 since Split C, R73)** — the test is opened ONCE, post-freeze,
> for the confirmatory inference only.

---

## 1. The four-class determination framework

Every material parameter belongs to exactly one class, each with a different criterion for "best":

| Class | Criterion for "best" | Optimise for performance? | Examples |
|---|---|---|---|
| **MEASURE** | the value where a diagnostic *plateaus* (adequacy, not performance) | No — optimise for *enough* | training steps B\*, seeds n\*, candidates G\* |
| **CALIBRATE** | controls error at the pre-committed level, set ONCE identically across arms on PRE-TEST data | No — principled procedure | λ (fitness), SESOI, embargo, multiplicity, DSR trial count |
| **FIX** | sensible literature default, held IDENTICAL across arms; tuning would CONFOUND the channel | **Deliberately not** | all SAC/LLM hyperparameters, learning_starts, PopArt |
| **REALISTIC** | credible real-world value, not result-maximising | No — realism | universe, lookback, costs, splits, delisting, cash rate |

Only **three** parameters are "optimised," and only for **adequacy** (MEASURE). Three-quarters of the design
is *correctly not optimised* — that restraint is itself the rigorous choice. This framework is implemented
and audited by `scripts/determine_design.py` (the Design Determination Pipeline, DDP), which emits a
per-parameter status table and a FREEZE-READY verdict (`docs/DESIGN_DETERMINATION.md`).

---

## 2. The committed parameter specification

| Parameter | **Committed value** | Class | Status |
|---|---|---|---|
| `train_steps_per_candidate` (B\*) | **200,000** (band 150k–300k) + plateau figure | MEASURE | confirm via convergence pilot |
| `n_seeds` (winners) | **30** floor → **50** if σ_D > ~0.10 | MEASURE | confirm via σ_D pilot |
| `candidates_per_arm` | **30** (6 generations × 5) | MEASURE | confirm via saturation; opt. 6×8=48 |
| `arms` | **7** (kept; two-tier labelling) | design | settled |
| `lambda` (fitness tail-weight) | **calibrate** on pre-2015 fold (currently `null`) | CALIBRATE | **PENDING** — run calibration |
| `cash_daily_rate` | **risk-free series** (currently `0.0`) | REALISTIC | **FIX_NEEDED** |
| `sesoi` | 0.05 deflated-Sharpe (~0.072 ann-Sharpe) | CALIBRATE | settled |
| `embargo` | ≥ feature lookback (60) — verify effective purge | CALIBRATE | VERIFY |
| SAC hyperparameters | SB3 defaults; `learning_starts=1000`; PopArt on | FIX | settled |
| LLM decoding | Opus 4.8; K=16 internal; max_tokens 4096; held identical | FIX | settled |
| universe / lookback / cost / splits / delisting | 30 assets / 60d / 10 bps / 10y-3y-8y / retain *(splits superseded 2026-07-02 → Split C 12y-3y-6.5y on univ5: 2005-16 / 17-19 / 20-26H1; ADR-044, R73)* | REALISTIC | settled |

---

## 3. Per-parameter justification, grounded in the literature

All citations below were read **first-hand** from the 196-paper corpus (text cache `D:\tmp\littxt`). Three
gaps (not in corpus, to fetch when writing) are flagged in §9.

### 3.1 Training steps — **200,000** (and crucially, *not more*)

> **⚠ UNDER ACTIVE RE-MEASUREMENT (2026-07-13, evidence-ledger claims 8/15).** The "more steps
> OVERFIT" verdict below was inferred from ONE nominal ordering (350k vs 200k, 3 seeds) and is
> contradicted by a first extended-ladder observation: the authored distributional winner at
> **1.6M steps scored val-DSR 0.187 vs 0.041 at 100k on the same CRN seed** (single seed; the
> full 5-budget × 3-seed × 2-winner cluster curve is queued). A pre-committed decision rule
> (EVIDENCE_LEDGER_2026-07-12.md) fires a B\* amendment proposal to Tamer if the ascent confirms.
> The matched-compute identification argument below is UNAFFECTED either way (B\* identical
> across arms); what is in question is the "overfit onset" interpretation, not the design's
> validity. Read this section as the dated 2026-07-02 record, not settled fact.

**The decisive finding: this is a DATA-LIMITED task, so more steps OVERFIT rather than help.** There are only
~2,520 distinct trading days in the train window; off-policy SAC with replay simply re-passes the *same price
path*, so extra steps add overfitting risk, not information. 200k ≈ ~80 passes; 50k ≈ ~20 passes.
*(Split C, 2026-07-02: the executed train window is ~2,961 sessions → 200k ≈ ~68 passes, 50k ≈ ~17 — the
data-limited argument is unchanged.)*

- **Sharpe-Regret-Reward (2502.02619)**, quoted: *"the agent iterates through the same data repeatedly,
  encountering nearly identical trajectories… this significantly increases the risk of overfitting to the
  training dynamics."* This is the data-limited-regime citation.
- **FinRL-DeepSeek (2502.07393)** — the closest analog (daily US-stock RL) — **early-stops at 400–500k**
  despite having a 2M run available. Longer ≠ better.
- **ARM-FM (2510.14176)**: performance *"plateaus early (~300k steps)."*
- **SAC (Haarnoja 1801.01290)**: MuJoCo needs 1M–3M (10M Humanoid) — but that is higher-dimensional dynamics,
  *not* a data-limited daily-allocation task; do **not** anchor to it. Convergence convention: 5 seeds, eval
  rollout every 1,000 steps, mean ± [min,max] band.
- **EIIE (Jiang 1706.10059)**: 2M (crypto, 30-min bars). **News-Driven (2411.11059)**: 20k (undertrained
  outlier). **Sood 2023** (the `PortfolioEnv` template): ~600 passes / 7.5M over 10 parallel envs.

**Verdict:** 50k was undertrained (≈20 passes; corroborated by the observed critic divergence). 200k sits in
the centre of the daily-finance band, below MuJoCo, above the undertrained floor, bracketing ARM-FM's ~300k
plateau. **Going much higher (toward 1M) would overfit the single realized price path — a *worse* result and
an examiner-visible flaw.** The number is secondary to the **plateau-convergence figure** (eval return +
critic loss vs steps, ≥3–5 seeds): pre-register 200k AND the criterion "extend only if the plateau figure
shows the critic still moving." The 2-week budget and the scientific optimum **coincide** here.

### 3.2 Seeds — **30** (paired-CRN), pilot-confirmed, →50 if σ_D high

The headline H2 test is **paired with Common Random Numbers** (amendment R16,
`per_seed_iqm_paired_seed_bootstrap`): arms share the training-seed set, so the common across-seed variance
*cancels*; the sample size is `n_seeds`, reduced by rliable IQM + a paired bootstrap on the per-seed
differences.

- **rliable / Agarwal (2108.13264)**: IQM gives *"reliable interval estimates for as few as N = 10 runs"*;
  *"20 or 30 runs"* is folk wisdom (they push back to 25–100 for **median-difference** claims, but the
  paired-IQM-equivalence regime is the N≈10-reliable one). Small-N caveat: *"with 3 runs, bootstrap CIs
  underestimate"* — CRN buys efficiency, not permission to go below ~10.
- **Henderson (2018, "Deep RL that Matters")**: *"no specific number… power analysis methods can be used"*;
  empirically, **5 seeds of the *same* config differ significantly** (t = −9.09, p = 0.0016) — 5 is dangerous.
- **Common Random Numbers** buys ~`1/(1−ρ)` seed-efficiency on the *difference* estimand (ρ = cross-arm
  correlation; 3–10× at ρ ≈ 0.7–0.9). [CRN methodology not in corpus — cite L'Ecuyer / Glasserman externally.]

**The binding quantity is σ_D** (paired SD of the per-seed difference), measured by a **10-seed pilot**
(Henderson's prescription). TOST power at Δ = 0.05, α = 0.05, 0.8: `n ≈ 2475·σ_D²`:

| σ_D | n needed | At 30 seeds |
|---|---|---|
| 0.03 | ~2 | over-powered |
| 0.06 | ~9 | comfortable |
| 0.10 | ~25 | just adequate |
| 0.12 | ~36 | **insufficient → 50** |
| 0.15 | ~56 | **insufficient → 50+** |

**Verdict:** 30 is the defensible pre-registered floor *for this paired-IQM-TOST equivalence design*,
contingent on σ_D ≤ ~0.10. The 10-seed pilot measures σ_D; upgrade to 50 if it exceeds 0.10. Never below the
N≈10 reliability floor. (Stored prototype σ_seed ≈ 0.36 is *reward-design* dispersion, an upper bound; the
fixed-reward σ_D after pairing is what matters and is far smaller.)

### 3.3 Candidates — **30 (6 generations × 5)**, past the saturation knee

Each arm runs an Eureka-style reflection loop: write reward → train → feedback → revise, over G generations ×
K candidates/generation; matched compute across all arms; H3 single-shot control spends the same 30 in one
generation.

- **Eureka (2310.12931)**: *"5 iterations with K = 16 samples per iteration"* (= 80/run, ×5 restarts = 400).
  K=16 is an **executability** floor (≥1 runnable candidate w.h.p.), not an optimality argument. The **"w.o.
  Evolution (N samples)"** ablation — same budget, single-shot — is beaten by the iterative loop *"after 2
  iterations"*: this **is** your H3 control, and the lineage predicts H3 loses.
- **ICPL (2410.17233)**: ships **K=6 × N=5 = 30** (~49 effective queries) — your published budget twin. Also
  the **monotonicity-as-evidence** argument that blesses the dose-response ladder.
- **CARD (2410.14660)**: iteration ablation — reward quality *"converges"* by iteration 2 (best/comparable on
  7/9 tasks); **more iterations can *hurt*** (reward-drift; performance declines after iter 3 on 2 tasks).
- **REvolve (2406.01309)**: N=7 × K=16, 13 sub-pops — the lineage's upper depth band.
- **FunSearch (Nature 2024) / ELM (2206.08896)**: 10⁶ samples / 1,024-per-iteration — the *pure-code-search*
  regime with cheap fitness; **out of scope** for expensive-fitness (per-candidate SAC training) reward
  design. Cite only to bound scope / pre-empt a "your budget is tiny vs FunSearch" objection.

**Verdict:** 30 (6×5) is in-distribution (ICPL twin) and **6 generations runs *past* the saturation knee
(gen 2–3) with margin** — a fairness feature you can *show* via the per-generation cumulative-best curve. The
one soft spot is width K=5 (vs Eureka's K=16 executability floor); mitigate by **reporting the first-
generation executable rate**. Optional hardening: **6×8 = 48** (matches ICPL's ~49 queries; still fits 2
weeks). Do not go below 4 generations. H3 single-shot = 1×30.

### 3.4 Arms — **7, kept**, two-tier labelling

Arms: (1) distributional, (2) scalar, (3) placebo (inert length/structure-matched block), (4)
placebo_shuffled (distributional's block with tail VALUES deranged), (5) scalar_cvar5 (+ one CVaR line), (6)
random_search, (7) bayes_opt.

- **Eureka (2310.12931)** "No Reward Reflection" ablation (scalar vs full reflection; −28.6% without) is
  *exactly* the H2 contrast — **your H2 is the finance-tail instantiation of Eureka's reflection ablation,
  reframed as an equivalence test.** Primary citation.
- **DrEureka (2406.01967)** holds the reward fixed and varies only the information channel, and runs the
  *identical* control battery: **Uninformative-Prior (=placebo)**, **Random-Sampling (=random_search)**,
  **BayRn/CEM (=bayes_opt)**. Your controls are standard in this exact lineage, not idiosyncratic.
- **`placebo_shuffled` is genuinely NOVEL**: a grep over all 196 papers found **no reward-design study uses a
  structure-matched, content-deranged control.** Every ablation in the field is a *pipeline-component*
  ablation. This isolates *information content* from *prompt structure/length* — a real methodological
  contribution. Anchor by analogy to DrEureka's Uninformative-Prior.
- **ICPL (2410.17233)** monotonicity-as-evidence blesses the **dose-response richness ladder** (scalar →
  scalar_cvar5 → distributional). **Skalse (RewardHacking 2022)** caveat: richer ≠ automatically better →
  frame the ladder *agnostically* ("does monotonically richer tail info monotonically change the code /
  outcome"), not "more must help."
- Foundations: **Singh (WhereRewardsComeFrom 2009)** + **Ng (RewardShaping 1999)** (designed reward ≠ fitness,
  found by search). Search baselines: **Snoek (BayesOpt 2012)**, **Shahriari (2016)**, **OPRO**, **FunSearch**.

**Two-tier labelling (protects the statistics):**
- **H2 information-channel tier** (enters the IUT + multiplicity): scalar, scalar_cvar5, distributional (the
  dose-response ladder) + placebo + placebo_shuffled (construct-validity controls).
- **Search-baseline tier** (context, NOT in the H2 IUT/multiplicity): random_search, bayes_opt.

**Verdict:** keep all 7; none redundant. Optional add (only if compute permits): a pure no-reflection/empty
arm (first-shot, scalar fed back, *no* block) — scalar already approximates it, so skip if tight. If ever
forced to cut, bayes_opt is the most expendable — but don't.

---

## 4. Power analysis (seeds → minimum detectable effect)

Computed with the real simulator (`scripts/power_analysis.simulate_power`, the actual paired one-sided IUT
Monte-Carlo'd). Sharpe→DSR conversion at the validation track length T≈756: **K = 0.6905 DSR per ann-Sharpe**,
so SESOI 0.05 DSR = **0.0724 annualised Sharpe**. *(Split C, 2026-07-02: the executed validation track is
T≈694 sessions — regenerate `make power` at the executed windows before quoting K/MDE in the write-up.)*

| Scenario (σ_seed, ρ) | MDE at n=30 (DSR) | Power @ SESOI, n=30 | Seeds for SESOI |
|---|---|---|---|
| Pessimistic (0.36, 0.0) | 0.077 | **0.58** | **71** |
| **Likely (0.22, 0.4)** | **0.045** | **0.98** | **25** |
| Optimistic (0.15, 0.6) | 0.031 | 1.00 | 11 |

**Reading:** in the likely regime, 30 paired seeds already deliver 0.98 power and MDE *below* the SESOI. Only
the worst case needs 71 (feasible, not hundreds). A non-rejection is reported as **bounded-effect + TOST
equivalence**, never an underpowered shrug. The σ_D pilot picks the scenario.

---

## 5. Construct validity — VERIFIED (the existential check)

First-hand read of the two **frozen, hash-bound** base prompts (`prompts/system.txt`,
`prompts/initial_generation.txt` — `reflection.txt` is an archived/dead illustrative file, R63, not loaded):
they tell every arm only *"Optimize RISK-ADJUSTED performance — the feedback tells you HOW to weigh it; do
not assume."* The words **tail / CVaR / drawdown / downside appear NOWHERE.** Tail-specific information enters
ONLY via the per-arm feedback block (distributional arm). **Construct validity holds** — the channels can
differentiate; the "base primes CVaR to everyone" fear is refuted.

**Precise effect under test:** the base primes *general* risk-awareness, so the manipulation is the
**marginal value of tail-SPECIFICITY over general risk-adjustment** — a deliberately subtle effect. This is a
feature: it makes the null a *predicted* outcome, demands the high-power paired design, and makes the
**mechanism** (does tail-specific feedback change the reward CODE?) the real contribution.

---

## 6. Compute & time plan — full 24/7 two weeks, tiered

**Run-count formula:** `N(C, S) = 8·C + 12·S` trainings, each at B\* steps.
- Search 7C = 210 (7 arms × 30 candidates × 1 seed) + Winners 7S = 210 (7 × 30 seeds) + H1 baselines 4S = 120
  (4 × 30) + H3 single-shot C+S = 60. **Total = 600.**

**Calibration:** ~10.8 ms/step (prototype: ~17.9h / 239 trainings @ 25k). At 200k → 0.6 GPU-h/training. The
convergence pilot replaces this with the laptop's exact value.

**Why NOT pad the primary to fill 2 weeks:** two of three primary knobs have *scientific ceilings* — more
training steps **overfit** (data-limited, §3.1); more candidates **saturate/drift** (§3.3). Only seeds absorb
more, with diminishing returns. Padding the primary makes the result *worse*. Instead, use the full budget in
**tiers** (primary at its optimum, then secondary panels that add evidence without corrupting the headline):

| Tier | Item | Compute | Value |
|---|---|---|---|
| 0 | Pilots (convergence + σ_D) | ~0.5 d | sets B\*, seeds, candidates |
| **1 (locks H2)** | **Primary campaign** 600 @ 200k/30/30 | **7.5 d** | the confirmatory result |
| 2 | Multi-model panel (headline arms, a 2nd open model e.g. Qwen-Coder) | ~2.25 d | **highest** — tests the ceiling-effect, makes "LLMs" plural |
| 3 | Seeds 30→50 (winners) | ~1.75 d | tighter equivalence CI |
| 4 | Robustness grids (cost-bps, λ) — re-*evaluation*, no retraining | ~0.5 d | "null holds across costs/λ" |
| — | Buffer (restart/thermal) | ~1.5 d | resilience |
| | **TOTAL** | **~14 d** | **fully used** |

The 14-day, 2× budget = **1,120 trainings**; the primary is 600. The remaining ~520 buy a second model,
tighter seeds, and robustness — each a real paper paragraph.

**Identifying the best 24/7 run-time — the principle:** run until the marginal value of the next compute-hour
hits zero. MEASURE knobs stop at their pilots' plateaus (steps→eval plateau, candidates→saturation,
seeds→power). Secondary tiers absorb the remainder in value-rank order (multi-model → robustness → seeds →
walk-forward) until the 2 weeks are spent or marginal value drops below threshold. For this design there is
~13–14 days of genuinely value-adding compute — so **run the full 2 weeks**, allocated as above.

**The defensible design space all fits in 2 weeks:** 30/30/200k = 7.5 d; 50 seeds = 10.5 d; 48 candidates =
9.3 d; worst case (50 seed + 48 cand) = 12.3 d.

---

## 7. Framing & publishability strategy (free — writing, not compute)

1. **Dose-response richness ladder** (scalar → scalar_cvar5 → distributional) — frame H2 as a dose-response
   in feedback richness, not binary; a flat ladder is a cleaner, more citable claim (ICPL monotonicity;
   Skalse agnostic-framing caveat).
2. **Bank EQUIVALENCE, not non-rejection** — the single biggest lever. 30 paired-CRN seeds reach the SESOI in
   the likely σ_D regime → report TOST practical equivalence (a *positive* result), not "we found nothing."
3. **Mechanism is the contribution** — the reward-code differential (AST distance: does tail-specific
   feedback change the code?), responsiveness, the prompt-leak fingerprint answer *why*.
4. **Ceiling-effect nuance** — Opus 4.8 may write good risk-aware rewards from the general-risk base alone
   (tail channel redundant). The multi-model secondary panel (weaker model) *tests* this — scientific value
   beyond robustness.
5. **H1 is the validity anchor** — LLM rewards beating naive baselines proves the agent is reward-sensitive,
   which *licenses* interpreting the H2 null (not an agent-washout artifact).
6. **Two-tier arms** — keep random_search/bayes_opt out of the H2 multiplicity (§3.4).

---

## 8. Execution priority (the binding constraint is execution + writing)

The design is sound and the machinery is over-built for an MSc; the grade (PDF-only) is now gated on
execution + writing, not more parameters.

1. **Close the 2 no-GPU blockers** — λ calibration (pre-2015 fold) + `cash_daily_rate` → risk-free.
2. **Run the 3 GPU pilots** (~1.5 d) → DDP flips FREEZE-READY → **freeze**.
3. **Run** the tiered 14-day campaign (§6).
4. **Write** Results + Discussion around §7 (dose-response, equivalence, mechanism, H1-anchor, ceiling-effect,
   self-disclosed limitations).

Compute finishes by ~mid-July; ~7 weeks remain for writing before the **1 Sep 2026** deadline.

---

## 9. Citation gaps to fill when writing (not in the corpus)

- **Colas et al. 2019 (arXiv 1904.06979)** — canonical RL power-analysis / sample-size reference (seeds).
- **CRN efficiency** — L'Ecuyer / Glasserman (simulation-statistics; the `1/(1−ρ)` paired-efficiency claim).
- **SAC-v2 / Applications (Haarnoja 1812.05905)** — the exact SAC convergence budgets.

---

## 10. Repository & reproducibility infrastructure (built this session)

- **Private repo** `github.com/abailey81/llm-reward-portfolio` — pushed, clean (no licensed data / secrets /
  PDFs), all commits authored by the user, **no Claude attribution** (legacy trailers scrubbed).
- **World-class README**, `requirements.lock` (torch==2.6.0+cu124 pinned), `REPRODUCIBILITY.md`,
  `.gitattributes` (LF normalisation), `.editorconfig`.
- **`scripts/determine_design.py`** — the Design Determination Pipeline (§1) + the search-saturation engine
  `recommend_candidates` + the freeze-readiness reporter (`docs/DESIGN_DETERMINATION.md`).
- **`scripts/learning_curve.py`** — `recommend_budget` (knee detector) + `project_campaign` (turnkey
  wall-clock + GO/ADAPT/RECONSIDER verdict).
- Result writes already crash-consistent (temp → fsync → atomic replace); determinism + provenance archive.
- **Advanced-systems research verdict (deep sweep):** the resume/archive design is already SOTA for a frozen
  determinism-first study. **REJECTED** as scope-creep: within-training SAC checkpointing (TB-scale buffers +
  replay-determinism hazard), joblib/diskcache memoization (a weaker pickle-keyed shadow of the archive), and
  Snakemake/Nextflow/DVC/W&B/Hydra (their headline — idempotent input-hashed re-execution — is exactly what
  `--resume` already does; new heavy dep + a competing source of truth). Apptainer only if HPC.
- **One open repo item:** the CI workflow (`.github/workflows/ci.yml`) is staged locally but unpushed — the
  `gh` token lacks the `workflow` scope. Closes with `gh auth refresh -h github.com -s workflow` then a push.

---

## 11. Open items (the DDP freeze-blocker list)

| Item | Status | Action |
|---|---|---|
| `train_steps_per_candidate` (B\*) | PENDING | convergence pilot → confirm 200k |
| `n_seeds` | PENDING | σ_D pilot → confirm 30 (or 50) |
| `candidates_per_arm` | PENDING | saturation check → confirm 30 (or 48) |
| `lambda_frozen` | PENDING | pre-2015 calibration (no GPU) |
| `cash_daily_rate` | FIX_NEEDED | wire risk-free series (no GPU) |

The first two no-GPU items can be closed immediately; the three pilots close the rest and flip the campaign
to FREEZE-READY.

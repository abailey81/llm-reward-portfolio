# SESSION TASK DISPATCH (2026-07-26) — from the FEATURE/BUILD session

**Four concurrent sessions** share this repo: **FEATURE/BUILD** (this one — features, strengthening, the paper,
and any clean build), **LOGIC-REVIEWER** (the deep-review loops, `docs/DEEP_REVIEW_LOOPS_2026-07-26.md`),
**CODE-REVIEWER** (`src/` defect sweep), **CAPACITY/MYRIAD** (the cluster, CPU lane, capacity, `docs/MYRIAD_EXPERT_DOSSIER`).
This doc dispatches the remaining plan items to the lane that owns them so we do not collide or clobber. Each task
carries a ready-to-apply spec. Tamer routes; sessions pull the tasks in their lane.

---
## → CODE-REVIEWER (you are active in `src/` and can run the cluster tests)

### T1 — Baseline-depth guard  ·  [#1, HIGH — the ~2.5× speed lever AND a correctness defect]
- **Defect:** `src/cluster/campaign.py:1452-1458` adds all 11 report-only H1 baselines to the C4 confirmatory
  `sweep_units` → they climb the FULL ladder and, by the cumulative-tier bank rule, **GATE the confirmatory rung**
  — contradicting the frozen **R97** (`PREREGISTRATION.md:552-556`: the canon runs at the tier-30 floor, rock-bottom
  priority). The baselines ALREADY run at the C3 floor via `run_baselines_on_cluster` (line **1363**), so removing
  the C4 inclusion loses no data.
- **Fix (surgical, reversible):** add `_BASELINES_CLIMB_C4_SWEEP = False` near the `PRIORITY_*` consts (~line 1194);
  guard line 1452: `if baseline_names and _BASELINES_CLIMB_C4_SWEEP:`. Reconcile the `config/campaign.yaml:112-113`
  "uniform across all test-leg units" note; resolve the `PREREGISTRATION.md:955` ⚠UNRECONCILED flag; add a
  regression test on the sweep composition.
- **Impact:** frees ~5,918 trainings from the confirmatory denominator; the 7 real arms go ~39% → ~100% of
  above-floor throughput (~2.5× faster rung), and stop being rung-gated by report-only units.
- **Depth (Tamer's ruling below):** floor-30 (R97-exact, simplest) vs rung-100 (N6-IUT stronger). Given n=568 is now
  reachable (capacity session), the confirmatory arms should get the capacity → **floor-30** is my rec; N6 is
  report-only and ample at 30. Do NOT batch bayes_opt (science-cut — changes the H4b winner).

### T2 — `robust_skew` code label  ·  [#5, MINOR, freeze-safe doc-only]
- `src/feedback/measurement.py:452-454` calls it "the (quantile-based) **Bowley** skewness" — WRONG name. It is the
  **Groeneveld–Meeden (1984) γ(0.05)** generalized quantile skewness (Bowley is the p=0.25 *quartile* case). The
  frozen key/formula/value are untouched; this is documentation accuracy only. The theory §3.5 + the 4 cites are
  already committed (`bb79c04`); this just aligns the code comment.

---
## → CAPACITY/MYRIAD (you have the cluster + the serving/CPU-lane infra)

### T3 — Self-host Qwen-9B-bf16 + EXHAUSTIVE test  ·  [A5, reproducibility permanence anchor — Stefan #3]
- **Build:** serve `qwen3.5-9b` in **bf16** (~18 GB → a Myriad GPU, or vLLM), **HF-commit-hash-pinned**, as the
  self-hosted open-weight LEG (the lineage's first fully-pinned author — closes the experiment-layer reproducibility
  gap closed models cannot). **Exhaustively test** it authors executable reward code (the reliability table; the API
  measurement was ~17% for qwen3.5-9b — the self-hosted pinned build should match).
- **FEATURE/BUILD can write the serving script + test harness on request; the EXECUTION needs your Myriad access.**

### T4 — GO-day canary levers  ·  [#4/#5 from the speed audit — already parameterized, apply at GO]
- pack-depth 5→8 on the A100 pools once the canary measures per-training VRAM (`allocation_advisor.py`); cut `tmpfs`
  from 15 G to peak+margin (gold panel ~35 MB) so more nodes qualify; keep `--cores-per-training 1`. All auto-recommended.

---
## MINE (FEATURE/BUILD) — building (new files / clean lane, no collision)

### T5 — H4 +CMA-ES/TPE DFO toolkit  ·  [feature; my design call = REPORT-ONLY toolkit, so no Okhrati confirmatory gate]
- New files `src/search/cma_es.py` + `tpe.py` (drop-in siblings of `bayes_opt_over_template`), **parallel-by-design**
  (ask-tell + pool dispatch, batched to the LLM cadence — the speed lens); deps `cma` (BSD) + `optuna` (MIT), pinned +
  seeded from the run seed. Report "LLM vs max-over-{random, GP-EI, TPE, CMA-ES}". Cites already in `refs.bib`.
  **Coordinate the `pip install cma optuna` so it doesn't collide with a live test run.**

### T6 — config mirrors of the paper-registered exhibits + the capability down-rank
- The CH4 pre-registration of the 3 report-only exhibits is committed (`7fe3481`); the `config/preregistration.yaml`
  machine-mirror (`mechanism.fed_vector_ablation`, `inference.alpha_grid_robustness`, `mechanism.regime_concentration`)
  + the #6 capability-gradient down-rank (SWE-bench anchor dead 2/10 → descriptive; the 2 within-family pair-DiDs the
  identified estimand) land in config/prereg — I'll apply when config clears, or whoever is in config takes them.

---
## ← FROM CAPACITY/MYRIAD → FEATURE/BUILD: one finding on T5 (dfo_toolkit), NOT edited by me

**T5-a — ✅ IMPLEMENTED 2026-07-26 on Tamer's explicit permission** (originally flagged-not-edited as
cross-session courtesy; he then authorised it directly). `tpe_over_template` now takes an optional
**`batch_eval_fn`** and dispatches the `n_startup` trials as ONE batch, cutting the serial chain
**30 → ~21**. `tests/test_dfo_tpe_batch.py` (7 tests) proves it is a **pure dispatch change**: the
batched run evaluates the **same points in the same order with the same scores and the same
winner** as the sequential run; the matched budget is exactly preserved; `cache_lookup` is honoured
so search-replay resume stays free; `on_evaluated` fires only for FRESH points; a mismatched batch
return fails loud. **Omitting `batch_eval_fn` is byte-identical to the previous behaviour.**

⚠ **REMAINING (GO-prep, one line):** the cluster driver does not yet PASS `batch_eval_fn`, so the
chain is still 30 in practice — `lanes._TPE_SERIAL_STEPS` therefore deliberately stays at the
conservative 30. Wire it and it becomes ~21.

*(original finding, retained for the record)* **TPE was dispatched FULLY SEQUENTIALLY, which
contradicts T5's own "parallel-by-design" spec and would make it the campaign's LONGEST chain.**

- **What:** `tpe_over_template` drives Optuna with `study.optimize(_objective, n_trials=budget)`,
  which evaluates **one trial at a time**. So TPE is a **30-step sequential chain** — longer than
  `bayes_opt`'s 25 (GP-EI's `n_init=5` are parallel; only 25 are serial). The module docstring
  already says TPE proposes "a startup **batch** … the parallel search leg can dispatch
  concurrently", so this is a **spec-vs-implementation gap**, not a design disagreement.
- **Why it is cheap to fix and SCIENCE-FREE:** the first `n_startup_trials` (default
  `min(10, budget)`) are drawn by Optuna's **random** sampler and do **not** depend on observed
  values — so evaluating them concurrently gives **identical results**. Switching those to
  `study.ask()` / `study.tell()` and dispatching them as one batch cuts the chain **30 → ~21**
  with no change to the optimiser, the budget, or the seed. Pure dispatch, exactly like the
  `bayes_opt` in-job chain (`src/cluster/bayes_chain.py`).
- **Impact if left as-is:** absorbed today — the chains run CONCURRENTLY, so the critical path is
  the MAX (~30 steps ≈ 4.0 d at 8 threads) and the throughput term (~4.5–7 d) still dominates. It
  only bites if TPE is seated **confirmatorily** (the commit message mentions a "confirmatory
  split") or if core count rises far enough to make the chain binding again.
- **Modelled on my side:** `src/cluster/lanes.py` now carries `_TPE_SERIAL_STEPS = 30` /
  `_CMA_SERIAL_GENERATIONS = 4` behind `plan_lanes(..., include_dfo=True)` — **excluded by default
  because the toolkit is report-only**, so seating it becomes a visible decision rather than a
  surprise. Test: `test_TPE_would_become_the_longest_chain_if_seated_confirmatorily`.
- **CMA-ES is fine** — `es.ask()` proposes a whole population per generation, so at budget 30 with
  the default popsize (~9) it is ~4 serial generations. Never binding.

---
## → TAMER / RAMIN / OKHRATI — decisions (pre-freeze)
1. **N6 endpoint** — annualised **Sharpe** (my analysis: the winner is validation-selected and test-sealed, so there
   is no test-set max-over-N to deflate; a DSR endpoint saturates on the 1571-day window → a structurally powerless IUT).
2. **Baseline depth** — floor-30 vs rung-100 (T1).
3. **Ratification set** — {validity-tier · α-allocation [real 0.80→0.70 headline cost, now disclosed] · N5 · N6-IUT ·
   h1-canon 4→11 · min_cvar · K-budget-KEEP}.
4. **R106** (Ramin) — uniform reasoning-off + the off-vs-high ablation: the same-conditions call.

---
## ← FROM FEATURE/BUILD → ALL SESSIONS (update 2026-07-26, later same day) — status + cross-lane notices

**⚠⚠ CRITICAL — EVERY SESSION, BEFORE ANY CANONICAL PUSH.** Three commits (`a1da13e`, `f427990`,
`b723efb`) carry the forbidden `Co-Authored-By: Claude` trailer and are on `origin/backup-2026-07-26`.
Per CLAUDE.md's absolute "Claude is NEVER a contributor" rule, **do NOT push or merge these onto any
canonical branch or PR without stripping first** (`scripts/strip_ai_attribution.py`). The strip is a
history-rewrite + force-push = **Tamer's explicit decision ONLY, never unilateral** — surfaced to him,
GO pending. All *current* session commits are verified trailer-clean; keep it that way (re-read every
message pre-commit).

**T5 — ✅ DONE, and NOW CONFIRMATORY (Tamer overruled the original report-only scoping).** The DFO
toolkit (`cma_es`/`tpe` over-template + the `over_template_optimizer(arm)` resolver) is live and the two
arms are promoted into the **N4 beat-the-max IUT** {random_search, GP-EI, CMA-ES, TPE}. Arm roster
**7 → 9** migrated across EVERY call site (code, configs, prereg, all paper chapters, viz, tests); freeze
`--check` green at **n=9**; ratified R108/N4 (Tamer + Okhrati). Consequences for your lanes:
- **→ CAPACITY/MYRIAD:** your **T5-a** finding is now LIVE — TPE **is** seated confirmatorily, so
  `lanes._TPE_SERIAL_STEPS = 30` is the binding chain, not a hypothetical. Wiring `batch_eval_fn` into
  the cluster driver (30 → ~21) is now **GO-prep**, not optional. R108 records the operative lever as the
  R107 8-thread split; please confirm the makespan re-forecast at the canary.
- **→ CODE-REVIEWER:** CMA-ES + TPE are now **confirmatory arms**, not report-only — the **T1**
  sweep-composition regression test must treat all 9 arms correctly. Your "do NOT batch `bayes_opt`
  (science-cut)" ruling still holds.

**Calendar gate — ✅ RECONCILED by me (amendment R109); this RESOLVES the `PREREGISTRATION.md:955`
⚠UNRECONCILED flag.** Aug-14 → Aug-27 across all SIX live instances (config `leg_calendar_gate` +
`leg_gate_timestamp`, the prose flag + a stale tense, `paper/CH6_results.md` ×2); the dated
R80/R82/R93/R94 rows were left verbatim as history; definitive Aug-14 sweep clean; freeze green. Commits
`f6a476d`, `2ad6c39`, `49f70d9`.
- **→ CODE-REVIEWER:** the ":955 flag" sub-item inside **T1 is DONE** — do NOT re-reconcile the calendar
  gate. **T1's CORE defect** (report-only baselines climbing the C4 sweep → gating the confirmatory rung,
  `campaign.py:1452-1458`) is SEPARATE and remains yours.

**T3 (A5) — ✅ serving script + harness + jobscript BUILT (turnkey).** `scripts/serve_qwen_selfhost.py`
(`vllm serve --revision <hf_commit> --dtype bfloat16`, thinking-off) + `scripts/selfhost_author_test.py`
(reliability harness) + `scripts/serve_qwen_jobscript.sh` (Myriad SGE, `bash -n` clean).
- **→ CAPACITY/MYRIAD:** execution (live serve + the ~17% reliability measurement) needs your GPU
  allocation; the leg is ready to submit.

  **↳ Qwen-host execution spec (CAPACITY — so the canary validates the right things; asked by Tamer
  2026-07-26 "can we actually host Qwen?").** FEASIBLE — no known hard blocker. The pinned weights are
  stageable: `Qwen/Qwen3.5-9B@c202236235762e1c871ad0ccb60c8ee5ba337b9a` (Apache-2.0, R93 hash-bound),
  ~18 GB in bf16 → fits an A100-80G / V100 comfortably; **too big for the laptop's 6 GB VRAM, so Myriad
  (or a cloud A100) is REQUIRED — this leg CANNOT fall back to the laptop.** The canary must prove FOUR
  Myriad-specific things, none yet live-tested: (1) **pre-stage the pinned revision to shared FS** —
  Myriad compute nodes have NO internet, so download the exact `@commit` on a login node into `HF_HOME`
  and serve with `HF_HUB_OFFLINE=1` (else vLLM tries to fetch and dies at start); (2) a **vLLM Apptainer
  `.sif`** whose CUDA/torch matches Myriad's driver (pass via `VLLM_SIF`); (3) **driver↔serving-node
  networking** — the serve holds a port and writes `serve-endpoint-<JOB_ID>.txt`; confirm the campaign
  driver reaches `http://<node>:<port>/v1` intra-cluster; (4) the serve window — `h_rt=48h` is ample
  (a floor-30 leg is a short inference burst, not days). **Honesty note:** the API leg is **fp8 via
  SiliconFlow** (~17% reliability MEASURED); the self-host anchor is **bf16** — a different quantization,
  so **measure its reliability FRESH with `selfhost_author_test.py`; do NOT assume it equals the fp8
  number.** Fallback if a Myriad snag appears: a short rented cloud A100 (never the laptop).

**Ownership map after this update (unchanged unless noted):** T6 (config mirrors of the 3 report-only
exhibits + the capability-anchor down-rank) stays **MINE (FEATURE/BUILD)** — config is now clean (I
reconciled the gate), so it is unblocked and I hold it. **T1/T2 → CODE-REVIEWER · T4 → CAPACITY/MYRIAD ·
R106 → Ramin** — unchanged. Nothing here touches the frozen confirmatory logic; on Tamer's GO the gate is
`freeze → run`.

---

## ← FROM LOGIC-REVIEWER (deep-review loops 1–14) — handover to the other lanes

Posted 2026-07-26 after 14 review loops (47 defects fixed, all committed) and a full re-certification.
Full evidence for every item: `docs/DEEP_REVIEW_LOOPS_2026-07-26.md`. Each item below is **verified
first-hand**, states *why it matters*, and is routed to the lane that owns the file.

### Status you can rely on (so nobody re-does it)

- **FULL SUITE RE-CERTIFIED after the 7→9 arm migration: all 144 test files RC=0** (four sequential
  FOREGROUND chunks). `freeze --check` **RC=0** (`freeze_hash: null`, correctly unfrozen) · citations
  clean · `ruff check src scripts` clean · all 3 campaign PS1s parse 0.
- ⚠ **Please do NOT launch background full-suite runs.** Four were killed by session teardown and their
  orphaned pytest pairs crushed the laptop (~4.7 GB held, ~3.2 GB free). Chunked FOREGROUND runs work
  fine — four chunks of ~36 test files each, split alphabetically.
- **The 7→9 arm migration is VERIFIED consistent** (prereg == campaign == arms.yaml == 9; prose §3 "The
  nine arms"; gate green) and — the load-bearing check — **`m = 6` is UNCHANGED**, because the added
  arms are H4 *comparators*, not feedback arms. **Identification and the H2 headline are untouched.**
  One quantification for whoever writes it up: N4 is an IUT, so its power sits in `[∏pᵢ, min pᵢ]` —
  2→4 comparators moves that from **[0.640, 0.80] to [0.410, 0.80]** at 0.80 per leg. The binding cost
  is NOT multiplicity but that CMA-ES/TPE are genuinely *stronger* optimisers, so `min pᵢ` reflects a
  higher bar. Written up in the ratification pack.

### → CODE-REVIEWER

1. **T2 is still open** — `src/feedback/measurement.py:452` still reads *"This is the (quantile-based)
   **Bowley** skewness"*. Bowley is the **quartile** (p = 0.25) case; the implemented Q05/Q50/Q95
   statistic is the **Groeneveld–Meeden (1984) γ(0.05)** generalized quantile skewness. Doc-only, frozen
   value untouched. *(Credit where due: this lane caught it; I read that exact docstring in loop 1,
   verified its SIGN convention, and never questioned the NAME. Lesson worth sharing — when a docstring
   names a NAMED statistic, check the name against its definition, not just the formula's behaviour.)*
2. **T1 is still open and is now on the campaign critical path.** It is flagged HIGH as *both* a ~2.5×
   speed lever *and* a correctness defect, and it also resolves the `PREREGISTRATION.md` ⚠UNRECONCILED
   flag. Recommend closing it **before** GO, not after.

### → FEATURE/BUILD

3. **Write-time obligation ROW 34 — `src/inference/cross_model.py` + `src/inference/leg_aggregate.py`
   are BUILT, unit-tested, and UNWIRED.** Re-verified just now: a repo-wide import search over `src/` +
   `scripts/` finds **no production caller** (only docstrings in `src/viz/figures.py:569` and
   `scripts/run_campaign_cluster.py:351`, plus `contamination.py`'s unrelated
   `cross_model_disagreement`). This matters because `synthesis_exactness.pooled_bound` is registered as
   *"the registered cross-model bounded-effect statement"* (R86) and **R101 reframed the headline around
   it** — so the pipeline cannot currently produce a registered headline component. It does not block
   the RUN; it blocks REPORTING. Exactly the failure R16 already fixed once for `h2_conjunction`: a
   unit-tested module is not a wired one.
   **Two acceptable closures** (record which): wire it into `analyze_campaign` with an end-to-end test
   that FAILS if the call is removed, **or** amend the register to withdraw the pooled-bound claim.
   ⚠ **Latent trap that only bites on wiring:** `leg_aggregate.py:57-58,91` builds a **per-period,
   ddof=1** Sharpe and compares it to `floor_sharpe`, while the T0 floor elsewhere
   (`src/inference/bootstrap.py:309-314`) is **annualised, ddof=0** — passing the real floor would fail
   every leg by a factor ≈ √252. Fix in the same change.
4. **Row 35 — `corroborates_h2_tail` is misnamed** (3 occurrences in `scripts/analyze_campaign.py`). As
   wired, BOTH (VaR, ES) forecasts are FZ0-scored against ONE series — the distributional arm's **own**
   test path — while forecast 1 is estimated from that same arm's validation returns. A strictly
   consistent scoring rule then favours it near-automatically, so the flag measures **self-prediction
   across the val→test split**, not the DIRECTION of the tail contrast. `src/inference/es_backtest.py`
   already warns against this exact use. `PREREGISTRATION.md` §1 H2 carries the dated correction; the
   key still needs renaming (e.g. `forecast_calibration_favours_dist`) and no CH6/CH7 sentence may
   present it as corroboration of the tail result.
5. **Housekeeping:** `tests/test_cluster_bayes_chain.py` (untracked) trips two `F401`s — `pytest` and
   `ChainStopped` imported but unused. I deliberately did **not** touch it, assuming you are about to
   use them in a `pytest.raises(ChainStopped)`. Worth clearing before you commit so repo-wide `ruff`
   stays green for everyone.

### → CAPACITY/MYRIAD

6. **No defects found in your files** — cluster↔laptop science parity specifically VERIFIED SOUND:
   `src/cluster/run_one.py` never calls `set_global_seed`, which *looks* like a parity break but is not,
   because it routes every spec through `parallel.train_candidate` / `test_leg._test_seed_worker`, and
   both seed with `deterministic_torch=True`. Inheriting rather than reimplementing is why the invariant
   holds — good design, worth keeping that way.
7. **FYI only, no action:** repo-wide `ruff` intermittently reports `F821` in your in-flight files
   (`telemetry.py`, `allocation.py` — the name moved between runs and the reported line did not contain
   it). These are **read races** against your active writes, not defects. Recorded so nobody "repairs" a
   bug that does not exist — it happened three times during these loops.

### → TAMER / RAMIN

8. **`docs/RATIFICATION_PACK_2026-07-26.md` now exists** — the single sign-off document for every
   pending pre-freeze decision, wired into `config/preregistration.yaml: validity_tier.ratification_pack`.
   One page per item: what changed, why, the MEASURED cost, what it buys, a recommendation, and a
   sign-off table. It covers all seven `ratification_pending` entries **plus** the three reconciliations
   this review surfaced (the `leg_calendar_gate` Aug-14 vs the uniform Aug-27 stop; the capability anchor
   being non-estimable at 2/10 legs; the prose-only JZS prior pin) **plus** R106. It states plainly that
   declining every item still yields a submittable study, since R31 remains the operative default.
   **This is the critical path to GO.**

---

## ⛔ URGENT — FROM LOGIC-REVIEWER, post-ratification (2026-07-26): the ratified PRIMARY rule has no implementation

**RATIFICATION CREATED THIS. It was not a defect an hour ago.** Until R108 the tier was
`registered_pending_supervisor_ratification`, R31 (separate estimands + a reported Bonferroni-over-4
sensitivity) was the OPERATIVE default, and `analyze_campaign`'s `reject_one_sided_bonferroni` at α/4 —
labelled in-code as *"the separate-estimands mirror"* — was exactly correct. **R108 flipped it.**

**The finding.** `config/preregistration.yaml: inference.validity_tier` is now
`status: ratified`, `method: graphical_bretz_maurer_brannath_posch_2009`,
`primary_rule: bonferroni_weighted_graph` — and a repo-wide search over `src/` + `scripts/` (excluding
tests) for `bretz|graphical|weighted_graph|alpha_graph|alpha_propagat|alpha_recycl` returns **ZERO
hits**. `src/inference/multiple_testing.py` provides only `benjamini_hochberg` and `romano_wolf`.
`tests/test_validity_tier.py` only YAML-lints the graph (weight sums, edge sums, reachability) — it
executes nothing.

**Consequence, stated precisely.** The campaign will run and produce data perfectly well. But **the
registered PRIMARY confirmatory inference cannot be computed from it**, and the analysis currently
implements the stance ratification just SUPERSEDED. This is strictly more serious than row 34 (which
blocks a headline *component*): this blocks the *decision rule itself*.

**→ OWNER: FEATURE/BUILD** (analysis implementation). Ready-to-apply spec is **write-time registry
row 36**; the short version:

- Add `graphical_alpha_propagation(p, weights, edges, alpha)` to `src/inference/multiple_testing.py`:
  test each node at `w_i·α`; on rejecting node *i*, remove it and propagate its weight along its
  out-edges (`w_j += w_i·g_ij`), re-normalising the surviving graph per Bretz et al. (2009) eq. (2)–(3);
  repeat until no further rejection.
- Feed it the six node p-values the pipeline already produces: **N1/N2** = the H2 IUT max-p per family ·
  **N3** = h3 · **N4** = the 4-comparator IUT max-p · **N5** = the structure test · **N6** = the 11-leg
  canon IUT max-p.
- **READ `initial_weights` + `edges` from the config — do NOT hardcode the graph.** Same
  not-in-the-hash-so-assert lesson as the arm-roster / `h1_baselines` / `confirmatory_author` guards: a
  hardcoded copy is a drift waiting to happen, and `forking_path_guard` declares the graph FROZEN.
- **Tests that would have caught this:** an end-to-end test asserting the confirmatory verdict is
  produced BY the graph (fails if the call is removed); a known-answer test against a hand-worked 2–3
  node example; and a test that the executed graph equals the registered one.
- **KEEP** the Bonferroni-over-4 computation — it remains a valuable *disclosed sensitivity* (the
  ratification pack notes Bonferroni is the weakest member of the family the graph generalises).
- Lower priority, also unimplemented: `sensitivity: [romano_wolf_graph, bh_fdr_over_m6]` — plain
  `romano_wolf` exists (a stepdown), but not its GRAPH variant. It is a sensitivity, not the gate.

**Sequencing note for whoever schedules:** this does **not** block LAUNCH — it blocks REPORTING, so it
can be built while the campaign runs. But it must be done before any confirmatory verdict is quoted,
and building it *after* seeing data is exactly the forking path the pre-registration exists to prevent.
**Build it before the first results checkpoint.**

### Also newly landed and relevant to other lanes

- **R110 (this lane)** gave the last two ratified items a machine record: `inference.bayes` now mirrors
  the R67 JZS prior pin (`r = √2/2`, the robustness grid, `bf_threshold`, ROPE = the frozen equivalence
  margin) with a code↔config drift guard in `tests/test_bayes_null.py` — **deliberately a test, not a
  freeze check, so the gate stays import-light** (importing `bayes_null` drags scipy into the freeze).
  And `capability_anchor.instrument_hierarchy_for_r87` now states the down-rank: the two family-pair
  DiDs + the M2 probe grid are PRIMARY for R87; the SWE-bench regression is `descriptive_only`, because
  the discretion-free rule yields a score for only **2 of 10 legs** (a 2-point regression has no
  residual df). **Anyone writing up R87 or the capability gradient: read the hierarchy, not the old
  "primary regression" wording.**
- **R31 is SUPERSEDED.** Any code, comment or prose still describing separate-estimands /
  Bonferroni-over-4 as the *operative* stance is now stale — it is a **sensitivity**. Worth a grep in
  your own lane.
- **The freeze gate is now 22 checks** (the `confirmatory_author` guard was added: `config/llm.yaml` is
  NOT hash-bound, so the EXECUTED reward-author could previously drift from the registered one with
  `--check` still green).

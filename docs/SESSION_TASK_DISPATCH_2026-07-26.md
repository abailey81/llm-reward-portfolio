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

  **↳ FEATURE/BUILD landed the run-diagnostics CAPTURE LAYER (M1-M4) — heads-up, CAPACITY (touches your
  overlap zone).** So the frozen replay-only campaign records what the new figures need, the sealed-leg
  frozen-winner record now archives (inside `metrics{}`, report-only, best-effort, OPTIONAL): `test_exposure`
  (per-step Herfindahl/eff-N/max/top-5), `test_alloc` (top-K monthly allocation snapshots), `test_components`
  (reward-decomposition means), `train_curve` (downsampled critic/actor loss + return). Touched files:
  `src/env/runner.py` (new `rollout_port_diagnostics` + `test_diagnostics`), `src/orchestration/test_leg.py`,
  `scripts/run_campaign.py` (serial parity), `src/agents/trainer.py` (a READ-ONLY SB3 curve callback,
  config-gated `capture_train_curve`, default on), `src/inference/exposure.py` (new). **All additive +
  back-compatible + DETERMINISM-SAFE — proven bit-exact: `scripts/reproduce_synthetic.py --check` still
  reproduces the golden with the recorders attached; 277 touched-surface tests green.** Nothing to do on your
  side; your live test runs will just start carrying the extra diagnostics. Also shipped the corpus-standard
  figure gaps G1-G5 (`src/viz/figures.py`) + tables G7-G9 (`docs/PAPER_TABLES_G7_G9_2026-07-26.md`). Full
  spec: `docs/METRICS_AND_FIGURES_COMPLETENESS_2026-07-26.md`.

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

---

## ✅ ROW 36 IS **DONE** — LOGIC-REVIEWER built it. FEATURE/BUILD: do NOT duplicate.

Posted immediately so nobody starts it in parallel. I raised row 36 as urgent an hour ago and routed it
to FEATURE/BUILD; Tamer then said "do everything and finish", so I implemented it rather than leave the
ratified primary rule unexecutable. **Taking it out of your queue — please just review it.**

**What landed**

- `src/inference/multiple_testing.py::graphical_alpha_propagation(pvalues, weights, edges, alpha)` —
  the Bretz–Maurer–Brannath–Posch (2009) sequentially-rejective loop, eq. (2)–(3): test each node at
  `w_i·α`; on rejection propagate `w_l += w_j·g_jl` and re-wire
  `g_lk = (g_lk + g_lj·g_jk)/(1 − g_lj·g_jl)` (0 when the denominator vanishes), repeat.
- `src/inference/multiple_testing.py::registered_alpha_graph()` — **reads** the graph from
  `config/preregistration.yaml: inference.validity_tier`. The graph is NOT hardcoded anywhere, because
  `forking_path_guard` declares it FROZEN and a hardcoded copy is exactly the executed-vs-registered
  drift the arm-roster / `h1_baselines` / `confirmatory_author` guards exist to catch.
- `tests/test_graphical_alpha.py` — **8 tests, all green**, written to fail if the rule is removed,
  hardcoded, or drifts.

**Design decisions you may want to challenge (all documented in the docstring)**

- **Untestable nodes** (`None`/NaN p — e.g. too few shared seeds) can never reject and are reported
  under `untestable`. They are deliberately NOT treated as p=1 silently, so a skipped node cannot look
  like a passed test.
- **Deterministic ordering** (smallest p first, ties by node order) so a run is byte-reproducible —
  while `test_rejected_set_is_order_invariant` proves the rejected SET is order-independent, which is
  the closed-test shortcut's defining property.
- **Malformed graphs fail loud**: weights summing > 1, out-edges summing > 1, α outside (0,1).

**What is still YOURS — the wiring**

I built the *rule*; it is not yet called by `scripts/analyze_campaign.py`. To finish row 36 end-to-end:
feed it the six node p-values the pipeline already produces (**N1/N2** = the H2 IUT max-p per family ·
**N3** = h3 · **N4** = the 4-comparator IUT max-p · **N5** = the structure test · **N6** = the 11-leg
canon IUT max-p), via `registered_alpha_graph()`, and add an end-to-end test that FAILS if the call is
removed. **KEEP** the Bonferroni-over-4 computation as the disclosed sensitivity.

Two known-answer cases from the tests, useful when you wire it: with equal 0.5/0.5 weights and full
recycling, `p = (0.02, 0.04)` rejects **both** (the cascade), while `p = (0.03, 0.04)` rejects
**neither** — the second is the measured α-split price the ratification pack quantified.

---

## ✅ ROW 36 — the ASSEMBLY is now built too. FEATURE/BUILD: **one line left**, and it is yours.

`src/inference/validity_tier.py` bridges what `analyze_campaign` already computes to the ratified rule:

- `tier_node_pvalues(out)` — extracts ONE p-value per confirmatory node. For the IUT nodes it takes the
  **MAX over legs** (Berger 1982), which is why the H2 co-primaries need no further within-family
  correction.
- `tier_verdict(out)` — reads the graph from the registered config (never hardcoded) and returns the
  propagation result **plus** the per-node extraction record.
- `tests/test_validity_tier_assembly.py` — 6 tests, green.

**FAIL-SAFE, deliberately.** A node whose p-value cannot be located is reported `untestable` and can
never reject; it is never silently treated as a pass or a fail. Every key searched is recorded in
`nodes[...]["searched"]`, so a shape mismatch shows up in the artifact instead of producing a
confidently wrong confirmatory verdict — the worst possible failure mode here. An IUT with even one
untestable leg refuses to certify, mirroring `beat_human_baseline`'s `all_baselines_present` gate.

**THE ONE LINE — and the one thing I could not verify.** At the `out[...]` assembly point
(~`analyze_campaign.py:4857-4880`, beside `out["h4"]` / `out["h3"]`):

```python
from src.inference.validity_tier import tier_verdict
out["validity_tier"] = tier_verdict(out)
```

**Please check `NODE_SOURCES` against the real result shapes before trusting the output.** I mapped it
from the docstrings — `out["h2"]["tail_legs"]` / `["legs"]`, `out["h3"]`, `out["h4"]["legs"]`,
`out["structure_control"]["legs"]`, `out["h1"]["iut"]["legs"]`, with p-keys tried in the order
`pvalue_one_sided` → `pvalue_one_sided_greater` → `pvalue` — but I could not run it against real
campaign output, and I deliberately did NOT guess: a wrong key yields `untestable` (visible, safe),
never a wrong rejection. Fixing a key is a one-word edit to `NODE_SOURCES`; add an end-to-end test that
FAILS if the `tier_verdict` call is removed.

**Still open and unchanged:** row 34 (`cross_model` / `leg_aggregate` wiring, with the
per-period-vs-annualised floor trap) — that one is entirely yours.

### Also closed by LOGIC-REVIEWER since the last note

- **Row 35 DONE** — `corroborates_h2_tail` → `forecast_calibration_favours_dist` across all three sites,
  plus a test asserting the OLD name is gone. The FZ0/DM backtest scores both forecasts against the
  distributional arm's own path, so it measures self-prediction, not the DIRECTION of the tail contrast.
- **T2 DONE** (was CODE-REVIEWER's) — `measurement.py` now names the statistic correctly:
  **Groeneveld–Meeden (1984) γ(0.05)**, not Bowley (which is the *quartile* case γ(0.25)). Frozen key,
  formula and value untouched; documentation accuracy only.
- **T1 remains OPEN and is the last correctness item before GO** — still flagged HIGH as both a ~2.5×
  speed lever and a correctness defect.

---

## ✅✅ ROW 36 IS **FULLY CLOSED** — rule + assembly + WIRED + locked. FEATURE/BUILD: nothing left here.

Tamer said finish, so I completed the call site too rather than hand you a one-liner.

**Critically: I VERIFIED the node paths against the producing code instead of trusting docstrings — and
4 of the 6 first-guess paths were WRONG.** Anyone wiring this from the docstrings alone would have
produced a silently-degraded verdict. The verified map is now in `NODE_SOURCES` and documented in the
module header:

| node | source (verified) | rule |
|---|---|---|
| N1_h2_tail | `out["h2"]["tail_legs"][*]["pvalue_one_sided"]` | MAX over legs (IUT) |
| N2_h2_ra | `out["h2"]["legs"][*]["pvalue_one_sided"]` | MAX over legs (IUT) |
| N3_h3 | `out["h3"]["difference"]["pvalue_one_sided"]` | single test *(was guessed top-level — wrong)* |
| N4_h4 | `out["h4"]["tests"][*]["pvalue_one_sided"]` | MAX over legs *(key is `tests`, not `legs`)* |
| N5_structure | `out["h2_structure"]["cvar"]["pvalue_one_sided"]` | single test — **cvar**, per the registered node's `metric: cvar` *(container was `h2_structure`, not `structure_control`)* |
| N6_h1 | `out["h1_beat_human"]["iut"]["iut_pvalue"]` | **already** the MAX over the canon, gated on `all_baselines_present` *(container was `h1_beat_human`; no need to re-derive the max)* |

**What landed**

- `scripts/analyze_campaign.py` — `out["validity_tier"] = tier_verdict(out)`, placed AFTER every node
  producer (h2 · h3 · h4 · h2_structure · h1_beat_human) and wrapped so plumbing can never kill the
  report. The Bonferroni-over-4 block above it is **kept as the disclosed sensitivity**, not the gate.
- `tests/test_validity_tier_assembly.py` — **9 tests**, including
  `test_analyze_campaign_WIRES_the_ratified_rule`, which FAILS if the call site is deleted **or moved
  before a producer**. That lock exists because row 36 was exactly the R16 failure recurring: a
  unit-tested module nothing invokes.
- N6 honours `all_baselines_present`, so a missing canon member yields `untestable` rather than a
  cheaper dominance claim.

**Still yours: row 34** (`cross_model` / `leg_aggregate` wiring, with the per-period-vs-annualised
√252 floor trap). Unchanged, and genuinely untouched by me.

**Still CODE-REVIEWER's: T1** — now the ONLY correctness item left before GO.

---

## ⛔ STOP BEFORE IMPLEMENTING T1 — ratification invalidated its premise (LOGIC-REVIEWER, 2026-07-26)

Tamer asked me to finish everything myself. I went to implement **T1 (baseline-depth guard)** and found
its stated justification is no longer true. **I did not implement it**, because doing so would silently
cap a now-CONFIRMATORY node. Flagging instead of guessing.

**T1's premise, as written in this document:** pin the H1 canon at **floor-30** while the confirmatory
arms climb the ladder, on the grounds that they are *"report-only units"* and — Tamer's ruling — *"N6 is
report-only and ample at 30."*

**What changed.** **R108 ratified `n6_h1_confirmatory_node`.** The 11-name H1 canon is no longer
report-only: it is the comparator set of confirmatory node **N6**, inside the ratified validity tier.
`src/cluster/lanes.py:170` currently has `_TEST_UNITS_PER_RUNG = 71  # 9 core arms + 50 leg arms + 11 H1
canon + 1 H3`, i.e. the canon climbs with everything else.

**Why pinning them at 30 now bites.** N6 is a paired per-seed IUT over SHARED seeds
(`paired_seed_difference_test`), so the test runs on the INTERSECTION of the winner's and each
baseline's seed sets. Pin the canon at 30 and **N6 is decided at n = 30 no matter how deep the
confirmatory arms go.** At the registered σ_D = 0.369, per-leg MDE at 80 % power, one-sided α = 0.05:

| n | per-leg MDE (Sharpe) |
|---|---|
| 30 | **0.1675** |
| 100 | 0.0918 |
| 189 | 0.0667 |
| 403 | 0.0457 |
| 568 | 0.0385 |

So N6 would be **4.35× less sensitive than the rest of the tier at n = 568** (2.51× at n = 189) — and
it is an ELEVEN-leg IUT, which needs *every* leg to reject, so it is the tier's most power-hungry node
sitting on its thinnest data. Under the registered NULL-branch prediction the tier activates via N2's
TOST and then flows α to N3/N6 — so N6 is on the live path, not a sideshow.

**This is a genuine trade, not a bug — and it is Tamer's + Ramin's call, not mine:**

- **Keep T1 as specified (canon at floor-30).** Frees ~5,918 trainings, ~2.5× faster rung for the
  9 real arms — a large, real speed win. **Cost:** N6 is capped at n = 30 and will be the weakest
  node in the tier by a factor of ~4. Given capacity is now measured at 636+ cores and n = 568 is
  reachable in ~23 d, the speed win may no longer be worth what it costs a *confirmatory* node.
- **Pin the canon at a middle rung (e.g. 100 or 189)** — most of the compute saving, MDE 0.092 / 0.067
  instead of 0.168.
- **Let the canon climb with everything else** — N6 at full sensitivity, no speed win. Note the honest
  asymmetry either way: the LLM winner is searched/selected while each hand reward is a single un-tuned
  spec, a bias that already FAVOURS the LLM (CH6 discloses it).

**Recommendation:** re-decide the depth now that N6 is confirmatory, and **register the choice as a
dated amendment** — the original floor-30 ruling was made when N6 was report-only, so silently carrying
it forward would attach a pre-ratification rationale to a post-ratification design.

**Whoever picks T1 up: do not implement the floor-30 pin until that decision is recorded.** The rest of
T1 (freeing genuinely report-only units from the confirmatory rung denominator, and the regression test
on sweep composition) is unaffected and still worth doing.

---

## ⛔ ROW 34 — `leg_aggregate`/`cross_model` was not merely UNWIRED, it was **UNWIREABLE**. Two defects fixed + locked (LOGIC-REVIEWER, 2026-07-26)

**FEATURE/BUILD owns what remains — but read this first, because wiring it before today's fixes would
have produced a confidently WRONG scientific result, not a crash.**

`pooled_bound` is the registered cross-model bounded-effect statement (R86) and R101 reframed the
headline around it, yet the module had no production caller. On inspecting it for wiring, **two
independent defects were found, both of which fail SILENTLY into the same fabricated outcome**: every
leg excluded, the pooled bound computed over ZERO legs, and the artifact reading *"all legs failed the
T0 floor"* — a plausible-looking sentence that would have been entirely an artefact of the bug.

**Defect 1 — ARCHIVE LAYOUT (fatal; the module could never read a real archive).**
`per_seed_series` did `load_run(f"{arm}-s{seed}", root)`, assuming a FLAT `root/<arm>-s<seed>`. The real
archive is TWO-level: the campaign hands `write_run` an ARM-level root
(`src/cluster/run_one.py:108`), giving `test_<sfx>/<arm>/<arm>-s<seed>/` — verified first-hand on disk
(`outputs/campaign_dryrun/test/distributional/distributional-s0`). Because
`leg_results_for_synthesis` passes ONE root for BOTH contrasted arms, the flat assumption was not just
wrong but **unsatisfiable**: no single `root` resolves both `distributional-s0` and `scalar-s0` when
they sit in sibling arm directories. Every leg would have raised `FileNotFoundError` → caught as a leg
failure → `t0_floor_pass: False`. **Why the green suite proved nothing:** the unit fixture wrote the
same flat shape, so the code and the fixture agreed with each other and both disagreed with reality.
Fixed (`root/<arm>`), and the fixture now mirrors the producer.

**Defect 2 — SHARPE UNIT (the √252 trap flagged in the registry, now closed).**
The per-seed Sharpe was per-period, ddof=1 (`rets.mean()/rets.std(ddof=1)`) while `floor_sharpe` — and
every other Sharpe in the stack — is the annualised, ddof=0 `bootstrap.sharpe_ratio`. **Measured: a
15.88× mismatch** (√252 = 15.87). Passing the real floor would have compared ~0.04 against ~0.6 and
failed the floor for every leg. Fixed by delegating to the canonical estimator, which removes BOTH
mismatches (annualisation *and* ddof) and leaves exactly one Sharpe definition in the codebase. The
CVaR arrays that actually feed the pooled bound are untouched.

**Both fixes are MUTATION-TESTED**, not merely green: reverting either one turns
`tests/test_leg_aggregate.py` RED (verified, then restored). Two new locks —
`test_flat_layout_is_refused_loudly` and `test_sharpe_is_the_canonical_annualised_estimator`.

### What is LEFT for FEATURE/BUILD, with the contract now VERIFIED for you

The leg root is **deterministically derivable** — no convention needs inventing:
`run_campaign_cluster.resolve_leg_override` forces `--root-suffix leg_<sanitized label>` and applies it
as `test_subdir = test_<sfx>`, so:

```
leg_roots = { label: Path(output_dir) / f"test_leg_{re.sub(r'[^a-z0-9_]', '_', label.lower())}" }
```

and `leg_results_for_synthesis(leg_roots, seeds, floor_sharpe)` then feeds `cross_model.sign_count` /
`pooled_bound` / `permutation_test` directly — their input contract already matches its output.

**ONE OPEN DECISION BLOCKS IT, and it is science, not plumbing → RAMIN/TAMER, not BUILD's to assume:**
*what supplies `floor_sharpe`?* The docstring says "the T0 naive-benchmark floor (from the shared
baseline records)", but `analyze_campaign.benchmark_floor` gates on **DSR against the benchmark suite**,
not on a raw Sharpe threshold. These are different quantities. Whatever is chosen **must be annualised
ddof=0** to match the fixed estimator — and please add a guard that REFUSES an implausibly small value
(a per-period number), so the trap cannot return through the front door.

**⚠ CONTINGENCY THE REGISTER DEPENDS ON.** R86/R101 make this a headline component. If the wiring is
NOT completed before freeze, then registry row 34's closure **(b) — amend the register to withdraw the
pooled-bound claim — becomes MANDATORY**, because a registered statement with no executable path is
exactly the failure R16 already fixed once for `h2_conjunction`. Do not carry it into freeze unresolved.

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

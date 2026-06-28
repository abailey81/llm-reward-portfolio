# Advancement, Cleanup & Tech-Adoption Plan — senior engineering verdict (2026-06-27)

> Synthesis of a 4-stream first-hand sweep (new tech/packages; domain GitHub repos; Claude Code best-practice
> repos; professional structure + data systems) against the project's hard constraints. **Verdict lens:** does it
> advance the real goal — a ≥90% dissertation (graded on the PDF) + a publication — without breaking the freeze,
> the determinism spine, or the frozen scope? Default answer to "add this": **no**, unless it hardens the spine.

## Meta-verdict (read this first)

1. **The engineering is largely DONE and more sophisticated than it feels.** The "AI slop" feeling is surface
   clutter, not architecture. `src/` is cleanly domain-factored (16 modules); the parallel scheduler is genuinely
   advanced (below). The graded artifact is the **PDF**. So the highest-leverage path is **freeze → run → write**,
   not another build cycle.
2. **A big restructure / tech-injection right before a freeze is high-risk churn for zero grade value.** Your own
   audits concluded the same ("the churn = signal to FREEZE, not re-audit"). Cosmetic polish belongs to the
   *post-campaign code release* (it serves publication, not the mark).
3. **Adopt only what hardens the reproducibility spine without touching the frozen numbers.** That set is small.

---

## Part 1 — Compute maximisation: ALREADY BUILT. Calibrate, don't rewrite.

`src/orchestration/parallel.py` is already a heterogeneous **GPU+CPU** scheduler that pushes this laptop to its
ceiling — exactly the "use all my power" ask:
- `auto_n_gpu()` sizes the worker pool to the **RAM ∧ VRAM ∧ physical-core** ceiling of *this* machine (it already
  learned the hard limit: *"n_gpu=5 hit CPU MemoryError + CUDA-OOM, n_gpu=4 was the max"*).
- `DevicePool(n_gpu, n_cpu)` runs **device-tagged cuda + cpu workers** off a token queue, so the GPU *and* all CPU
  threads stay saturated; threads pinned to 1, TF32 on, `empty_cache()` between tasks, panel cached per worker,
  deadlock-safe pool recycling (`run_recycling`).

**So "parallelise as much as possible" is not a code change — it is a CALIBRATION + a config choice:**
- **Open step (when you're ready to run):** `python scripts/bench_compute.py --steps 4000` → prints the optimal
  `(n_gpu, n_cpu)` and the implied full-campaign hours for *this* machine. Never run on the real config yet.
- **Known safety subtlety:** at 50k steps the *transition wave* (two replay buffers briefly co-resident) spikes
  above steady state, so the measured-safe search concurrency is **n_gpu=2 (proven) / 3 (watchdog-armed)**, not the
  4 that steady-state sizing suggests — the runner already guards this. Do **not** chase "100% utilisation"; the
  repo already proved n_gpu=5 OOMs and corrupts runs.
- **Determinism caveat (the one real catch):** CPU and CUDA results are **not bit-identical**. Use the full
  heterogeneous pool freely on the **SEARCH** leg (it only ranks candidates). For the **TEST** leg (the 30 winner
  seeds = inference data) either keep it **GPU-only** for spotless comparability, or run heterogeneous but **balance
  the CPU/GPU split identically across all 7 arms** and **record device per run** so replay stays exact.
- **Honest ceiling:** fully maxed, this laptop does the campaign in **~1 day**. "Hours" needs many physical GPUs
  (Myriad), not a flag. **No scheduler rewrite — that would churn tested, frozen-adjacent code before a freeze.**

---

## Part 2 — New tech / packages: the short ADOPT list, and the rejects (all versions fetched first-hand)

**ADOPT-NOW (freeze-safe, hardens the spine):**
| Tech (verified ver.) | Adds | Why it earns its place |
|---|---|---|
| **pydantic v2** (2.13.4) | Fail-loud validation of the frozen YAML at load | Extends the mypy/test contract to *config data*; rejects a malformed/edited frozen config before a run. Highest ROI, zero perturbation. |
| **exact version pins** (SB3 + torch + **rliable**) | Lock the determinism stack in the frozen manifest | **SB3 v2.9.0 (2026-06-15) floors torch≥2.8** — a silent numerics hazard. rliable is **archived** (Oct 2025) → pin it. Real reproducibility win. |
| **arch** (8.0.0) SPA / MCS | Multiple-strategy-selection test as **labeled secondary** | "Did the winning arm survive snooping?" — strengthens inference *without* touching the pre-registered IUT. Pre-specify block length. |
| **RestrictedPython** (8.3) | Defense-in-depth over the AST gate | Only determinism-preserving, cross-platform, in-process sandbox; addresses the `from numpy import *` RCE. Layer it, don't trust it as a boundary. |
| **explicit `mp` start = spawn** + order-preserving collection | One-line hardening | Don't inherit the platform default (differs win32 vs Linux). Free determinism insurance. |

**REJECT (scope-creep or determinism foot-guns — all confirmed first-hand):** Hydra/hydra-zen (multirun silently
mutates the frozen design), Ray Tune (ASHA/PBT = pre-registration violation *by design*), Dask (work-stealing →
non-deterministic order), submitit (no SGE), SBX/TorchRL/CleanRL-swap (replace the frozen agent; **SBX is the trap —
same SB3 API, different JAX numerics**), W&B (cloud egress risk for licensed-data metrics), **mlfinlab** (proprietary,
all-rights-reserved — a liability in a public repo; PBO is a *method* you already implement), Sacred (competing
seeding), Pyodide/WASM (different numeric stack → breaks replay), nsjail/gVisor/E2B (Linux-only / cloud / out-of-process).

---

## Part 3 — GitHub repo learnings (adopt as *citation / oracle / convention*, never a code swap)

- **Eureka** `policy_feedback.txt`/`code_feedback.txt`: the per-component max/mean/min trace + 3 improvement
  heuristics is the template your reflect arm should mirror — *if already in the frozen prompt; else it's an
  amendment.*
- **rliable** (archived) IS your canonical IQM/CI oracle — pin version + bootstrap seed/reps.
- **mlfinlab DSR/PSR/MinTRL closed forms** + **purgedcv** (MIT): use as **unit-test oracles** for your deflated
  Sharpe + purge/embargo masks. Do **not** swap estimators (raw-vs-excess kurtosis nuances move frozen numbers).
- **FinRL-DeepSeek** (329★) is the **nearest competitor** — must-distinguish in Related Work (it uses CPPO, injects
  LLM signals into *observations not reward code*, no pre-registration — all differences favour your novelty).
- **Qlib** validates your fixed-env/swappable-reward seam (design citation); adopt with-cost/without-cost columns.
- **RF-Agent** (NeurIPS 2025 Spotlight, MCTS over reward code) — name as *future work*, not a gap.
- **Determinism-ceiling claim for the write-up:** neither CleanRL (10k★) nor SB3 calls
  `torch.use_deterministic_algorithms(True)`. If your byte-identity uses it + `CUBLAS_WORKSPACE_CONFIG`, that's a
  legitimate "we exceed the field-standard reproducibility bar" sentence. (If NOT set → adding it is a re-freeze.)
- **Novelty cell remains empty** (consistent with the 24-agent sweep): no repo writes reward *code* for a frozen
  SB3-SAC with multi-level tail feedback.

---

## Part 4 — Claude Code workflow guardrails (in `.claude/`, freeze-safe; enforces the audit-flagged unenforced freeze)

These touch only `.claude/`, never `src/` — pure dev/QA upgrades, and they make the integrity story *stronger*:
1. **Freeze-file protection (two layers):** a `PreToolUse Edit|Write` hook blocking edits to the 5 frozen files +
   a `Stop` hook `git diff --quiet <frozen paths> || exit 2` (catches Bash-driven changes the edit-matcher misses).
   **This mechanically enforces the freeze your notes say is "computed but never enforced."**
2. **Stop verification gate:** a *fast-subset* `pytest -q -x` ‖ `ruff` ‖ `mypy`, each `|| exit 2` (honor
   `stop_hook_active`). Kills the "reports done before verified" failure mode the audits keep catching.
3. **Deny-first `settings.json`:** deny `Write/Edit(frozen/**)`, `Read(.env*)`, `git push`, `git reset --hard`.
4. **A fresh-context verification subagent** (`audit-campaign`): independently checks freeze hash = prereg, test
   count, and H2 tail metrics = registered values — the discipline your audit history relies on.
5. Trim `CLAUDE.md` < 80 lines + explicit **Do-NOT/FROZEN** block + Key-Decisions table.

---

## Part 5 — Structure & data systems: defer the restructure; Snowflake is a clear NO

- **Freeze hash covers exactly 5 files** (`PREREGISTRATION.md` + `config/{preregistration,inference,environment,data}.yaml`).
  So `src/ tests/ scripts/ docs/` are freeze-irrelevant — but renaming `src/`→`src/<pkg>/` rewrites **95 imports +
  696 tests for zero grade value**, and touching the 4 bound configs is the *only* way to break the freeze.
- **Snowflake / lakeFS / Delta / Iceberg: NO.** A ~40MB licensed single-machine parquet is ~5 orders of magnitude
  below Snowflake's break-even, *and* it's a cloud warehouse — uploading licensed Refinitiv data likely breaches the
  entitlement and breaks single-machine reproducibility. **DuckDB/Polars** = marginal local EDA convenience at most.
  Your existing **provenance.json + .sha256 + synthetic-shadow** pattern is already the correct, lighter answer.
- **Real "slop" = root clutter + 3 overlapping output dirs (`outputs/`, `runs/`, `reports/`) + OS cruft
  (`__MACOSX`, `.DS_Store`).** All freeze-safe, all best fixed **AFTER the campaign** for the code release.

### Freeze-safety & timing
| Change | Breaks freeze? | Breaks imports/tests? | Grade value | DO IT |
|---|---|---|---|---|
| Delete OS cruft (`__MACOSX`, `.DS_Store`) | No | No | None | when ready (user said "don't delete yet") |
| `.claude/` freeze-enforcement guardrails | No | No | Integrity ↑ | **now (on go-ahead)** |
| pydantic config validation + version pins | No | Additive (test it) | Repro ↑ | **now (on go-ahead)** |
| Targeted strict tests (determinism/oracle/freeze-hash) | No | Additive | Repro ↑ | **now (on go-ahead)** |
| Consolidate `outputs/`+`runs/`+`reports/`→`results/` | No | Maybe (scripts write paths) | None | **after campaign** |
| Rename `src/`→`src/<pkg>/` (true src-layout) | No | **YES (95+696)** | None | **after campaign, only if shipping a pip package** |
| Move/rename any bound config or `PREREGISTRATION.md` | **YES** | Yes | Negative | **never** |
| Hydra / Ray / Dask / Snowflake / lakeFS / Polars-swap | varies | varies | None/Neg | **never (this project)** |

---

## Part 6 — Tests: strict and targeted, NOT "enormous and indiscriminate"

An indiscriminate test explosion on a frozen codebase is churn. The high-value additions (additive, freeze-safe):
1. **Property-based determinism tests** (Hypothesis): `seed → byte-identical output` as a property; parallel==serial
   invariance across `(n_gpu, n_cpu)` configs.
2. **Freeze-hash test:** recompute the 5-file SHA-256 and assert it equals the registered value.
3. **Statistical-oracle tests:** deflated Sharpe vs the mlfinlab closed form; CVaR vs the sorted-tail-mean primitive;
   purge/embargo masks vs `purgedcv`.
4. **Reward-contract / sandbox adversarial tests:** the RCE vectors (wildcard import, allocation bomb) stay blocked.

---

## The one-line bottom line
Your repo is more advanced than it feels; the compute-max is built; the grade is in the PDF. **Freeze → run → write.**
Do the small freeze-safe hardening (guardrails, pydantic, version pins, targeted strict tests) now; defer cosmetic
restructuring to the post-campaign code release; reject the over-engineering.

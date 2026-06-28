# Session log — 2026-06-27 → 2026-06-28 (hardening, deep-research, methodology upgrade, coverage)

A complete, auditable record of everything done across this working session, in the order it happened, with
the decisions and their rationale. The authoritative amendment record remains `PREREGISTRATION.md` (R43–R61)
and `docs/RIGOUR_LEDGER.md`; this file is the human-readable narrative + a pointer index. **Nothing was
committed** — all changes are in the working tree; `config/preregistration.yaml` is still `frozen: false`.

## 0. Operating frame (held throughout)
The recurring instruction was "do everything / more advanced / deeper / don't be lazy". The disciplined
response — repeatedly — was to **maximise the GRADE (the submitted PDF), not feature-count**, filtering every
ask through the project's real constraints. A mid-session correction the user forced is load-bearing:
**nothing is *frozen* yet** (`frozen: false`, campaign not run) — so improving the design **now, pre-results,
then freezing** is the correct science, not p-hacking. The only real guardrails are **determinism**
(byte-identical replay), the **LSEG data licence** (no third-party cloud), the **deadline**, and the true
integrity line — *never edit the analysis after the campaign results are in*.

## 1. Research performed (read/verify-only — fed Related Work / Methods / Discussion, no frozen-pipeline change)
- **6-agent sweep** (new-tech / GitHub-repos / Claude-Code-tooling / structure / test-gaps / V1–V19) →
  `docs/RESEARCH_SCAN_2026-06-27.md`. Verdict: **novelty conjunction intact**.
- **Two `deep-research` workflows** (99 + 105 agents, 3-vote adversarial verification):
  (a) novelty/citations (`wf_3e5ea496`) — **NO SCOOP, high confidence**; verified neighbour fences
  (FinRL-DeepSeek, CARD, URDP, Han-Liu-Yu) + the methods citation backbone; (b) examiner red-team
  (`wf_09d241fb`) → `docs/EXAMINER_OBJECTIONS_AND_DEFENCES.md` (top objections + best-practice defences).
- **3 read-only tool/DB sweeps** (~70 tools) → `docs/INFRASTRUCTURE_ASSESSMENT.md`. Verdict: **zero databases
  needed** (parquet+manifest+checksum is correct); all serving/cloud DBs, lakehouse formats, Ray/Dask, cloud
  GPU/sandboxes, experiment-trackers REJECTED on determinism/licence/grade-neutral grounds.
- **3-agent methodology de-risk round** which **overturned an initial GARCH-EVT proposal** (see §3).
- **1 focused package sweep** for the coverage goal (coverage.py `exclude_also`, diff-cover, hypothesis
  stateful; rejected respx/vcrpy/pytest-mock as redundant-with-DI, xdist for nondeterminism).
- **3-agent adversarial verification** of the whole session (security / correctness / consistency — §5).

## 2. Audit discharged (V1–V19 + R43–R60)
First-hand verification confirmed the prior `DEEP_AUDIT_2026-06-26` register was genuinely discharged; the one
real open code-gap (V1) was closed by a **cross-file arm-roster guard** in `scripts/freeze.py`
(`assert_executed_arms_match`: campaign.yaml + arms.yaml rosters must equal the frozen prereg arms) + 7 drift
tests. Most "scary" items were already fixed (V3/V5/V6/V8/V9/V11–V16). Repo confirmed sound; +~160 strict tests
across measurement/env/sandbox/inference/seeding (regression-locking the fixes), no `src` bug.

## 3. Methodology upgrade (WS1–WS7, pre-freeze; PREREGISTRATION R61)
- **WS1 — null reframed Popperian → Mayoian error-statistical severity + garden-of-forking-paths**
  (Rubin 2025; Gelman-Loken 2014), reported via the existing TOST/SESOI equivalence (Lakens 2018;
  Campbell-Gustafson 2018). Pre-registration does NOT improve *Popperian* severity (Rubin); the frozen,
  deviation-free protocol DOES license Mayoian severity. Editorial — the TOST machinery already implemented
  it. Applied across `PREREGISTRATION.md §1a/R45/R61`, `paper/CH1`, `00_FRAMING`, `DEEP_STATS_backbone`,
  `EXAMINER_OBJECTIONS §1c`; `docs/SUPERVISOR_REVIEW_NOTE.md` for Dr Okhrati.
- **WS5 — tail-uncertainty propagation added to `src/feedback/measurement.py`** (ADDITIVE, deterministic, fed
  values byte-identical): `cvar_ci` (stationary-block-bootstrap CVaR confidence intervals), `cvar_bias`
  (bootstrap bias; verdict analytic≈bootstrap), `reliability` tier (Belzile-Davison small-sample),
  `cvar_uncertainty_report`. +strict tests (`tests/test_measurement_uncertainty.py`).
- **GARCH-EVT: investigated and REJECTED** (real grounds, not "frozen"): validated on single-asset not
  aggregated-portfolio returns; adds model-risk at n≈750; `arch` MLE not byte-identical cross-platform ⇒
  breaks determinism. Retained as a Future-Work A/B only.
- **WS2 — citation integrity:** `docs/CITATION_VERIFICATION_TODO.md` (RED: `patton2019dynamic` FZ0-in-prod +
  `khraishi2022offline` supervisor paper; DO-NOT-CITE the hallucinated 2026 arXiv ids — none in refs.bib) +
  7 cited refs added `% VERIFY` (mcneilfrey2000, belziledavison2022, rubin2025, mayo2018, gelman2014,
  lakens2018, campbell2018).
- **WS3/WS6 — consistency + infra docs:** six→seven-arm banners, 210-vs-180 run-count clarity, univ4-heavy-end
  comment; `INFRASTRUCTURE_ASSESSMENT.md`; legibility of the existing advanced backtest stack in
  `ANALYSIS_METHODS_AND_FUTURE_WORK.md`.
- **WS4 — mutation exhibit:** `scripts/mutation_probe.py` → per-module registry; **100% kill on metrics.py and
  measurement.py** after the find→close→kill loop; `make audit` + `make mutation` targets; `docs/TEST_RIGOR.md`.
- **WS7 — re-freeze prep:** freeze hash legitimately recomputed (`4d6a43df…`; still `frozen:false`, USER flips).

## 4. Coverage raised to 90.4% (line+branch) — honestly
From ~79% → **90.38%** via real tests + documented, auditable exclusions (NO gaming): `exclude_also` config;
site-tagged `# pragma: no cover - <reason>` on POSIX-rlimit / spawned-child (`executor.py`) and NVML/rich-UI
(`monitoring.py`) lines; `omit = ["src/orchestration/*"]` (spawned-worker/GPU engine, integration-tested by the
slow `test_test_leg_equivalence` + `test_parallel_recycling`). New tests:
`tests/test_{executor,inference,monitoring}_coverage.py` + the agent-landed `test_{baselines_search,platform}
_coverage.py` (one broken env-wipeout test fixed). Floor raised to **88%** in `pyproject.toml`. Full detail:
`docs/TEST_RIGOR.md §2`.

## 5. Adversarial verification (this session's own work re-broken/re-run)
- **Security: 0 vulnerabilities** (sandbox re-attacked with 25+ fresh RCE/escape payloads — all blocked; env
  read-only hardening holds; WS5 code no resource-exhaustion; API key never logged/archived; deps pinned; no
  path-traversal/shell-injection).
- **Consistency/integrity: CLEAN** (API names match, reframe consistent, GARCH framed as rejected, 7 refs valid
  BibTeX + no DO-NOT-CITE leak + no dangling `\cite`, freeze gate exit 0). Closed one gap (INDEX links).
- **Correctness/determinism: production code CLEAN** + fixed one real test-robustness bug
  (`test_measurement.py` hypothesis-absent collection NameError → no-op shims).

## 6. Explicitly REJECTED (would lower the grade / break a real constraint — never "because frozen")
Databases (Supabase/Cosmos/Postgres/Mongo/Redis/ClickHouse/kdb+/Timescale/Influx) · lakehouse
(Delta/Iceberg/Hudi/lakeFS) · DuckDB/SQLite · Arrow/ORC/Avro/HDF5/Zarr · Ray/Dask/Snakemake/Hydra-multirun
(nondeterminism) · cloud GPU orch + cloud sandboxes (LSEG licence) · gVisor/Firecracker/Pyodide (determinism)
· experiment-trackers (cloud/grade-neutral) · repo restructure · "10× tests" by padding · conditional
GARCH-EVT in the frozen pipeline (§3) · adding rolling-window/MC/UPOT/non-stationary-GPD to the *confirmatory*
analysis (all Future-Work). Rationale per item: `docs/{INFRASTRUCTURE_ASSESSMENT,ANALYSIS_METHODS_AND_FUTURE_WORK}.md`.

## 7. Final state (verified green)
`scripts/freeze.py --check` exit 0 (hash `4d6a43df…`, `frozen:false`) · **1,300+ non-slow tests pass** ·
**coverage 90.38% (line+branch) ≥ 88 floor** · `ruff` clean · `mypy` clean (65 files) · mutation probe **100%**
on metrics.py + measurement.py · sandbox **0 vulnerabilities**.

## 8. Still OPEN — user-only (cannot/should-not be done autonomously)
1. **Flip `frozen: true`** (the freeze act — `make freeze`, user-only).
2. **Run the campaign** (produces results incl. `placebo_shuffled`, the bootstrap-CI/UPOT robustness legs,
   the PopArt σ_max ablation).
3. **Dr Okhrati sign-off** on the Mayoian reframe + the proposal-pivot disclosure (`SUPERVISOR_REVIEW_NOTE.md`).
4. **Pre-submission reference round** — the RED items + the remaining ~40 `% VERIFY` flags
   (`docs/CITATION_VERIFICATION_TODO.md`).
5. **`pip install pip-audit`** to activate `make audit`.

## 9. Key new/changed artifacts (index)
New docs: `RESEARCH_SCAN_2026-06-27`, `EXAMINER_OBJECTIONS_AND_DEFENCES`, `ANALYSIS_METHODS_AND_FUTURE_WORK`,
`TEST_RIGOR`, `INFRASTRUCTURE_ASSESSMENT`, `CITATION_VERIFICATION_TODO`, `SUPERVISOR_REVIEW_NOTE`, `INDEX`, this
log. New code: `scripts/mutation_probe.py`; `measurement.py` uncertainty methods; `freeze.py` arm guard;
`Makefile` audit/mutation targets; `pyproject.toml` coverage config. New tests:
`test_measurement_uncertainty`, `test_{executor,inference,monitoring,baselines_search,platform}_coverage`, +
the round-1/2 `test_*_deep` files. Amendments: `PREREGISTRATION.md` R43–R61; `docs/RIGOUR_LEDGER.md`.

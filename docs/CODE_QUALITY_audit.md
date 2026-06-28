# Code-Quality, Reproducibility & Architecture Audit

**Scope:** `llm-reward-portfolio` (the experimental engine `src/`, the campaign/analysis `scripts/`, the test suite `tests/`).
**Stance:** strict but realistic. The engine is verified-green (ruff clean on the project config, `freeze.py --check` 9/9, full suite green, 611 tests collected) and days from FREEZE. Every recommendation below is **behaviour-preserving** and **LOW-risk**; none changes the science. No "sophistication" rewrite is proposed — for this codebase that would be all downside.
**Method:** read first-hand; ran `mypy src`, `ruff check`, `pytest --collect-only`, and verified each sub-finding against the actual code/prose (several plausible-sounding flags turned out to be false positives — recorded as such so they are not re-raised).

**Auditor verdict (TL;DR):** This is a **clean, reproducible, well-structured research codebase that a top technical examiner will respect.** Provenance and determinism are genuinely publication-grade (atomic+fsync record writes, byte-for-byte sidecar verification, content-hashed env capture, content-hashed frozen pre-registration with a CI drift gate, single-seed-derived RNG across every stack). The new H2/H3/H4/multiplicity analysis layer is rigorous, defensively coded, and well-tested. There are **no HIGH-severity latent bugs.** The improvements below are polish: one genuine robustness asymmetry (MED), the standing mypy noise (all safely fixable), and documentation drift in the README/status counts. Implement the SAFE list, re-run `make test` + `make typecheck` + `make freeze-check`, and the codebase is in excellent shape for submission.

---

## A. PRIORITIZED SAFE IMPROVEMENTS (behaviour-preserving = YES, risk = LOW)

Ordered by grade-value per unit of effort.

### A1. Fix README documentation drift (test counts, dates, stub claims) — **HIGH grade-value, trivial effort**
- **Where:** `README.md` lines 50–53, 74, 78, 92 (and any docs that echo "148 tests").
- **What:** The README states "**153 behaviour tests (148 engine + 5 …)**", "**148 tests pass**", "Status (as of **16 Jun 2026**)", and lists `run_campaign`, `analyze_results`, `inspect_rewards` as "**STUBS (fail loudly; … blueprint T1–T6)**". All three are stale: `pytest --collect-only` now reports **611 tests**, and `scripts/run_campaign.py` is the real **1,400-line** campaign orchestrator (not a stub), as is `analyze_campaign.py` (the analysis entry point the README doesn't even mention). An examiner opening the README first will see numbers that contradict the repo.
- **Fix:** Update the count to the true figure (run `pytest --collect-only -q` and quote it), refresh the status date, and reclassify `run_campaign`/`analyze_campaign` as live. Add a one-line pointer to `docs/CAMPAIGN_RUNBOOK.md` so an examiner can navigate from README → runbook → reproduce.
- **Grade value:** The PDF-only grade leans on "an examiner can navigate + reproduce." A README whose headline metrics are wrong undercuts that on first contact; this is the cheapest credibility win available.

### A2. Use `load_all_safe` (not bare `load_all`) on the two remaining resume paths — **MED grade-value (real robustness), LOW risk**
- **Where:** `scripts/run_campaign.py:1108` (headline-arm test stage) and `:831` (H3 single-shot stage). Compare the baseline stage, which correctly uses `load_all_safe` at `:652` and `:679`.
- **What:** On `--resume`, both lines compute `{r["run_id"] for r in load_all(str(test_root / arm))}`. `load_all` → `load_run` *raises* on a schema-invalid or tampered-sidecar record (it does **not** raise on a truncated/partial write — `write_run` is atomic with fsync+`os.replace`, and `load_all` skips dirs lacking `record.json`; this is proven in `tests/test_results_io.py:111`). So the realistic failure is a hand-edited / schema-drifted prior record crashing the *entire* resume before the per-seed try/except at `:1110` can engage — whereas the baseline and H3-skip paths degrade gracefully via `load_all_safe`. This is a genuine **asymmetry**, not a hypothetical.
- **Fix:** Replace the two bare `load_all(...)` calls in the resume `done`-set construction with `load_all_safe(...)`. The function already exists and is imported in-file. Behaviour for the happy path is byte-identical (both return the same records); only the corrupt-record path changes from "crash" to "degrade".
- **Caveat / honest scoping:** `load_all_safe` (`:702`) currently *also* only guards a missing directory — it does **not** swallow a `load_run` `ValueError` from a corrupt record. So strictly this fix makes the two paths *consistent with the baseline path*, not bulletproof. If you want true resume-robustness, additionally wrap the inner `load_run` in `load_all_safe` (or `load_all`) in a per-dir try/except that logs-and-skips a corrupt dir. That is a slightly larger change; the *consistency* fix is the safe minimum and is what I recommend before freeze.
- **Behaviour-preserving:** YES for all completed/valid records (the only ones that exist after a clean run).

### A3. Clear the standing `mypy src` errors (19 across 4 files) — all SAFE — **MED grade-value, LOW risk**
The brief cited "9 standing errors"; the actual count from `mypy src` (the `make typecheck` target) is **19 errors in 4 files** (note the discrepancy). Every one is a local type-narrowing artifact, not a signature/contract gap (the config is permissive: `ignore_missing_imports = true`, no `strict`). All are SAFE to fix:

1. **`src/sandbox/executor.py:279–281` (3) — Windows false-positives. KEEP behaviour, silence locally.**
   `resource.getrlimit` / `resource.setrlimit` / `resource.RLIM_INFINITY` — the POSIX `resource` module has no Windows stub, so mypy-on-Windows reports "no attribute". The code is already correct (guarded `import resource` in a `try/except ImportError`, attributes reached via `getattr(resource, name, None)`). **Fix:** append `# type: ignore[attr-defined]` to those three lines (or guard the block with `if sys.platform != "win32":`). Do **not** restructure the runtime logic — it is correct as written and the campaign runs on Linux where these resolve.

2. **`src/utils/monitoring.py` (10) — `Optional`-init inference. Annotate, don't restructure.**
   `self._live = None` / `self._progress = None` (`:152–153`) make mypy infer the attribute type as `None`, cascading into every later `Progress(...)`/`Live(...)` assignment and `.add_task`/`.start`/`.update` access (`:174,183–189,206`) plus the `m, cid, arm = ev.get(...)` Optional-key index errors (`:507,515,521,534,535`). **Fix:** declare `self._live: Any = None` and `self._progress: Any = None` (exactly mirroring the existing `self._tasks: dict[str, Any] = {}` on `:154`); for the dispatch-key errors, bind `cid = str(ev.get("cand"))` / `arm = str(ev.get("arm"))` (or annotate locals). Pure annotations — zero runtime change.

3. **`src/agents/trainer.py:175–176` (2) — SB3 stub types `obs_rms` as a dict.**
   `rms.mean` / `rms.var` where `venv.obs_rms` is stubbed `dict[str, RunningMeanStd]` but is a `RunningMeanStd` at runtime for a single-obs env. **Fix:** `rms: Any = venv.obs_rms`. Behaviour-preserving.

4. **`src/orchestration/parallel.py:126, 654` (2) — `str`→`Literal` and `ndarray`→`Sequence`.**
   `:126` passes `str(data.get("on_missing", "liquidate_to_cash"))` where a `Literal['liquidate_to_cash','ffill_then_zero','error']` is expected — drop the redundant `str()` and `cast(...)` to the Literal (the value is already one of the three). `:654` passes a 2-D `np.ndarray` from `family_bounds(...)` to a `Sequence[Sequence[float]]` param — `cast(Sequence[Sequence[float]], …)` (runtime is a no-op: `bayes_opt_over_template` calls `np.asarray` on it). Both are annotation-only.

- **Grade value:** "0 mypy errors" is a clean, examiner-visible signal of type discipline. Doing it via `# type: ignore[...]`/`cast`/local annotations is provably behaviour-preserving; doing it via logic changes would NOT be — so keep strictly to the above.
- **Optional hardening (LOW):** the three `executor.py` ignores could instead be centralised by adding a `[[tool.mypy.overrides]]` block for `src.sandbox.executor` — but per-line `# type: ignore[attr-defined]` is more honest (it documents *why* at the site) and is preferred for an examiner.

### A4. Add a `git_dirty` flag (and optionally the git short-SHA) to the env fingerprint — **LOW grade-value, LOW risk**
- **Where:** `src/utils/provenance.py:75 env_fingerprint()` (records `git_commit` but not working-tree cleanliness); flows into `scripts/capture_env.py:capture_env`.
- **What:** A reproducibility record that pins the commit but not whether the tree was dirty lets a modified-but-uncommitted run *appear* reproducible from its recorded SHA. This is a real (if minor) provenance gap. **Note:** severity is LOW, not HIGH — `capture_env` already records the full `pip_freeze`, `nvidia-smi` driver line, `torch.version.cuda`, cuDNN, the determinism env knobs (`CUBLAS_WORKSPACE_CONFIG`/`PYTHONHASHSEED`/`CUDA_VISIBLE_DEVICES`) and seed, and the campaign is intended to run from a frozen tag — so the practical exposure is small. But it is a one-line, zero-risk addition that a reproducibility-minded examiner specifically looks for.
- **Fix:** add `"git_dirty": <bool>` via `git status --porcelain` (empty output ⇒ clean), guarded with the same `try/except (CalledProcessError, FileNotFoundError)` pattern already used by `git_commit`. Default to `None` when not a work-tree.
- **Behaviour-preserving:** YES (purely additive to the fingerprint dict; `OPTIONAL_FIELDS`/`env.json` already tolerate extra keys, and `sha256_obj` is order-stable so the new key just enriches the hash going forward).

### A5. Resolve the two unimplemented data stubs before freeze (document or delete) — **LOW grade-value, LOW risk**
- **Where:** `scripts/build_gold.py:56` and `scripts/verify_gold.py:54` — both `raise SystemExit("STUB — implement …")` with a `# TODO(FINAL_PLAN …): implement` marker.
- **What:** These are intentional, *documented* stubs (the real gold is built by the self-contained `data_pipeline/` package — `build_gold.py:43–49` says so). They are not on any live path. But a `raise SystemExit("STUB")` entry-point is the kind of thing an examiner greps for and reads as "unfinished." The README already labels them stubs.
- **Fix (choose one):** (a) leave as-is but ensure the README's stub list is accurate after A1; or (b) delete the two thin stubs and replace the README pointer with "gold is built via `data_pipeline/` (`python -m data.cli …`)". Either is fine; (b) removes the dead `SystemExit` entirely.
- **Behaviour-preserving:** YES (neither is invoked by the campaign or tests).

### A6. Two micro-perf nits in the parallel BO path — **NIL grade-value, LOW risk (optional)**
- **Where:** `src/orchestration/parallel.py:~389` (`specs = list(specs)` on an already-list input) and `:~646` (`list(coeffs)` round-trips a numpy array that `params_to_reward` immediately re-`asarray`s).
- **What:** Redundant copies; negligible cost (BO is GPU-bound, not list-bound). Mentioned only for completeness — **not worth touching before freeze** unless you are already editing that block for A3.4.
- **Behaviour-preserving:** YES.

---

## B. REAL ISSUES (severity-rated)

| # | Severity | Issue | Location | Status |
|---|----------|-------|----------|--------|
| B1 | **MED** | Resume `done`-set uses bare `load_all` on the headline-arm and H3 test stages, crashing a `--resume` on a schema-invalid/tampered prior record, while the baseline path degrades via `load_all_safe`. A genuine robustness asymmetry. | `run_campaign.py:1108`, `:831` | **Fix = A2** |
| B2 | **LOW** | `git_dirty` not captured in the provenance fingerprint (modified-uncommitted run looks reproducible from its SHA). Mitigated by full `pip_freeze`/CUDA/env capture + frozen-tag workflow. | `provenance.py:75`, `capture_env.py` | **Fix = A4** |
| B3 | **LOW** | 19 `mypy src` errors stand (brief said "9"). All are local-narrowing artifacts, none a contract gap; all safely silenceable. | executor/monitoring/trainer/parallel | **Fix = A3** |
| B4 | **LOW** | `load_all_safe` name over-promises: it only guards a missing dir, not a corrupt record. Worth a one-line docstring caveat even if you don't extend it. | `run_campaign.py:702` | Doc-only; see A2 caveat |
| B5 | **LOW** | README/status counts and stub list are stale (148/153 tests vs 611; `run_campaign` mislabelled a stub; status date 16 Jun). | `README.md` | **Fix = A1** |

**No HIGH-severity latent bugs found.** In particular, the items most likely to harbour a science-breaking bug were checked first-hand and are sound:
- **Atomic writes / replay integrity** (`io/results.py`): temp-file + `flush` + `os.fsync` + `os.replace` (atomic on Windows & POSIX); `load_run` verifies the `reward.py`, `prompt.txt`, and `env.json` sidecars **byte-for-byte** against the embedded copy and raises on mismatch. Tested incl. the mid-write truncation property (`test_results_io.py:77–130`).
- **Seeding** (`utils/seeding.py`): single run-seed → Python `random`, NumPy legacy + `default_rng`, `PYTHONHASHSEED`, torch/cuDNN, `use_deterministic_algorithms`, `CUBLAS_WORKSPACE_CONFIG`. Residual GPU non-determinism is *documented* (not hidden) and the design reports statistical, not bitwise, reproducibility — the correct stance for a GPU RL study.
- **Frozen-family desync guard** (`analyze_campaign.assert_realized_family_matches_frozen`): tested incl. the raise path (`test_campaign_inference.py:380,393`).
- **H2 conjunction verdict** (`h2_conjunction`): the IUT logic is correct — a conjunction is its own multiplicity correction (Berger 1982; joint size ≤ max leg size = α, no double-correction), the tail IUT is gated at `max(cvar_levels)` so the more-extreme opt-in CVaR-1% can never become the gate, and the BH-over-m=6 set is computed and reported as a *sensitivity*, never the gate. Tested for BH and Romano–Wolf methods, supported/null/missing-arm paths (`test_campaign_inference.py:141–419`).
- **Parallel == serial determinism**: each worker calls `set_global_seed(seed, deterministic_torch=True)` before any heavy import; caches (`_PANEL_CACHE`, `_ENV_CACHE`, `_TEST_PANEL_CACHE`) are process-local and immutable-after-fill; device scheduling is a thread-safe token `queue.Queue` with the token re-`put` in a done-callback that captures a fresh local. Equivalence is separately asserted by `tests/test_test_leg_equivalence.py`.

---

## C. VERIFIED NON-ISSUES (flagged during the sweep, dismissed first-hand — recorded so they are not re-raised)

- **`freeze.py:379` "equivalence-margin regex breaks on bold `**±0.05 DSR**`"** — **FALSE.** Verified by running the actual pattern `(?:±|\+/-|\+-)\s*\*{0,2}([0-9]*\.?[0-9]+)\s*DSR` against the real prose: `\*{0,2}` correctly consumes the leading `**`, and the bold line `PREREGISTRATION.md:312` returns `['0.05']`. The `--check` gate is **sound and non-vacuous** — it matches exactly the intended location with the correct value, and `_require(bool(prose_margin), …)` fails loudly if the prose anchor ever disappears. Same conclusion for the SESOI regex.
- **`provenance.sha256_obj` / `capture_env` `default=str` "could mask non-determinism"** — over-stated. The serialized values are version/platform strings; `sort_keys=True` + `separators=(",",":")` give a canonical, order-stable encoding, and `default=str` is a JSON-safety fallback, not a numeric-coercion path. A "validate-don't-coerce" guard would be belt-and-braces but is not a real reproducibility risk here.
- **`pip_freeze` "discovery order not deterministic"** — handled: `_pip_freeze` returns `dict(sorted(out.items()))` and `write_env_json`/`sha256_obj` sort keys, so the snapshot is order-stable regardless of `metadata.distributions()` iteration order.
- **Signal handlers "not atomic"** — by design and documented (`run_campaign.py:71–78`): cooperative `threading.Event`, checked only at arm/stage boundaries so an in-flight training completes and the science is untouched; a second Ctrl-C hard-exits. Correct trade-off (result integrity over shutdown latency).
- **Frozen-winner hash guard "skips on missing hash"** (`run_campaign.py:477`) — intentional and safe: the guard fires for any real 64-char sha256; baseline records carry a comment-stub source by design, and `freeze_winner` always writes a real hash for LLM winners, so the only records that skip the byte-check are the ones whose source is a deliberate stub. The frozen winner is additionally re-validated against the frozen family hash on the test path. Acceptable as-is.
- **Worker error handling** (`parallel.py`, `test_leg.py`) — no silent-success path: workers catch-and-return explicit `{"ok": False, "error": …}`, CUDA-OOM triggers `empty_cache()`, and a `matched_budget_ok` flag (`(accepted+failed)==expected and accepted>0`) surfaces a failure wave to the caller. The `except Exception: pass` sites are all narrowly-scoped best-effort cleanups (NVML probe, socket-interop init, post-error CUDA cleanup) with `# noqa`/`# pragma: no cover` and rationale.

---

## D. STRENGTHS WORTH STATING (so the write-up can cite them)

These are not findings; they are the things that make this codebase examiner-grade and are worth surfacing in the dissertation's "reproducibility & engineering" section.

- **Single canonical IO boundary** (`io/results.py`): analysis reads results *only* through `load_run`/`load_all`; the schema validates required provenance fields and fails loudly on a missing one. This enforces audit-finding C-1 structurally, not by convention.
- **Replay-not-regenerate is enforced, not asserted**: the `reward.py`/`prompt.txt`/`env.json` sidecars are checked byte-for-byte on every canonical read; a tampered archive cannot pass silently.
- **The freeze is content-addressed and CI-gated**: `freeze.py` hashes the prereg prose **plus** the bound `inference`/`environment`/`data` configs (so "nothing frozen can drift" is true at the config layer too), and `--check` re-derives the hash + verifies prose↔YAML consistency + the Phase-0 marker with no writes. The 9/9 check is a real drift guard, not a rubber stamp.
- **Determinism knobs are recorded with the run** (`capture_env`): `CUBLAS_WORKSPACE_CONFIG`, `PYTHONHASHSEED`, `CUDA_VISIBLE_DEVICES`, `are_deterministic_algorithms_enabled`, the nvidia driver line and torch/CUDA/cuDNN versions — exactly what is needed to *judge* whether a given run could be bit-reproduced.
- **The new analysis layer is unusually well-documented**: every hypothesis function (`h2_conjunction`, `h3_iterative_vs_singleshot`, `h4_search_controls`, `cross_hypothesis_multiplicity`, `evt_consistency_guard`) carries a docstring that names the pre-registration section, the statistical rationale, the disjoint-key discipline that keeps report-only tests out of the frozen m=6 family, and the exact skip/null semantics — and each has supported / not-supported / skipped tests. This is the part most at risk of being a confusing critical path; instead it is the best-commented region of the repo.
- **Test discipline**: 611 collected tests with `pytest-randomly` (order-shuffle + per-test reseed) pinned `<5` as a *hard* dep to catch inter-test state leakage; behaviour/invariance tests (atomicity, no-look-ahead, sidecar integrity, IUT verdicts, parallel≡serial equivalence), not just smoke tests.

---

## E. ACTION CHECKLIST (for the maintainer)

Do these, then re-run `make test && make typecheck && make freeze-check` and confirm all green before freezing:

1. **[A1, ~10 min]** Refresh `README.md`: true test count (611), status date, reclassify `run_campaign`/`analyze_campaign` as live, add a `docs/CAMPAIGN_RUNBOOK.md` pointer.
2. **[A2 / B1, ~5 min]** Swap bare `load_all` → `load_all_safe` at `run_campaign.py:1108` and `:831`. (Optional: extend `load_all_safe` to log-and-skip a corrupt dir + update its docstring per B4.)
3. **[A3 / B3, ~20 min]** Clear `mypy src` to 0 via the exact per-site annotations/`type: ignore`/`cast` listed in A3 — **no logic changes**. Re-run `make typecheck`.
4. **[A4 / B2, ~5 min]** Add `git_dirty` to `provenance.env_fingerprint` (and it flows into `capture_env`).
5. **[A5, optional]** Decide build_gold/verify_gold: keep-and-document, or delete-and-repoint.

None of the above touches an inference path, a seed stream, the env, the reward contract, the sandbox, or the freeze hash inputs — so the verified-green status and the science are preserved. After step 3 the repo should report **0 mypy errors, ruff clean, 9/9 freeze-check, full suite green** — a defensible "clean, reproducible, well-engineered" claim for the dissertation.

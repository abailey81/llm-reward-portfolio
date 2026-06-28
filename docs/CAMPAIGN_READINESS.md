# Campaign-readiness checklist (2026-06-28)

An honest map of what is **done + verified**, what is **scaffold-ready** (code complete, populated by the run),
and what is **yours alone** to do. The campaign has NOT been run (by instruction). `frozen: false`.

## ✅ DONE + VERIFIED (engineering / research / tooling — green)
- **Determinism + design freeze**: `freeze --check` exit 0, canonical hash `4d6a43df…` (unchanged across this
  session's analysis/docs/citation edits), 7-arm roster guard passes. `frozen: false` (yours to flip).
- **Code quality**: ruff clean; mypy clean (65 files); coverage ≥90% (re-confirmed by the P29 gate below).
- **rliable reporting complete**: IQM + probability-of-improvement + stratified-bootstrap CIs + **`performance_profile`**
  (new), all oracle-validated against the `rliable` library; wired into `analyze_results.py` (+test).
- **Mutation exhibit**: `metrics.py`, `measurement.py`, `fitness.py`, `deflated_sharpe.py` all **100% kill**
  (a real test gap was found and closed in `deflated_sharpe`).
- **Benchmark panel**: 9 reward baselines + 10 allocators, catalogued with formulas + primary cites
  (`docs/BENCHMARKS_CATALOG.md`); verdict **no new baseline passes the add-now gate** (panel already meets the
  top-venue bar; BL deferred — needs market caps/views).
- **Novelty**: re-confirmed **EMPTY (high confidence)** by two independent methods (cutting-edge 2024–2026 sweep
  + first-hand read of all 196 corpus PDFs → `docs/LITERATURE_INTEGRATION_MAP.md`). No technique passed the
  determinism/licence/scope gate.
- **Reproducibility artifacts**: `docs/MODEL_CARD.md` (Mitchell), `CITATION.cff`, `docs/REPRODUCIBILITY_CHECKLIST.md`
  (Pineau).
- **Citations (partial)**: dangling chapter cites **104 → 43**; `refs.bib` 61 → 117 (zero dup keys); ORP theory
  spine + Romano-Wolf + Ledoit-Wolf resolved first-hand; 5 alias keys renamed; integrity catches recorded
  (`docs/CITATION_VERIFICATION_TODO.md`, mislabeled Maillard/AI-Feynman/ELfolio files).

## 🟡 SCAFFOLD-READY (code complete; numbers/figures populated BY the run)
- Per-arm rliable IQM/CI + **performance-profile** score-distributions (computed in `analyze_results.py` once
  archives exist).
- Difference tests (Sharpe/CVaR, stationary-bootstrap), interpretability/mechanism gate, PBO/DSR, FZ0/ES.
- P18–P21 robustness reporting (regime / sub-period / crisis / cost-sweep) — analysis code exists; figures need data.

## 📚 REFERENCE ROUND — needs web/library verification (NOT fabricated; tracked in MISSING_CITATIONS_MANIFEST.md)
- **43 dangling keys remain**: 32 NEEDS-WEB-VERIFY (famous papers, just confirm coords) + 9 SUSPICIOUS ≥2025
  (verify existence FIRST — `kvasiuk2026madevolve` highest risk; `deepmind2025alphaevolve`/`yamada2025aiscientist`/
  `zheng2025survey` probably real) + 2 HELD (`harvey1997testing`, `witzany2021bayesian` — confirm the chapter's intent).
- All `% VERIFY`-flagged merged entries (the 39 classics + several fields) need coordinate confirmation.
- Confirm `patton2019dynamic` (FZ0 in production) + `khraishi2022offline` (supervisor paper) — the RED items.

## ✍️ PROSE — the dissertation writing (partly campaign-gated)
- Results chapter (needs the run); Discussion of the realized numbers; folding the new cites/benchmarks into
  Related Work/Methods narrative (P98–P100). Front matter + Intro + Related Work + Theory already drafted.

## 🔒 USER-ONLY (cannot/should not be automated)
1. **Flip `frozen: true`** (`make freeze`) once you accept the improved design.
2. **Run the campaign** (produces all 🟡 numbers; ~600 runs).
3. **Dr Okhrati sign-off** on the Mayoian reframe + proposal-pivot disclosure.
4. **Reference round** (the 📚 section) + `pip install pip-audit`.

## Pre-flight (before `make freeze` → run)
- [ ] Reference round at least for load-bearing cites (FZ0, supervisor paper, the 9 suspicious).
- [ ] `make freeze` → record hash → set `frozen: true`.
- [ ] `freeze --check` exit 0 with the recorded hash.
- [ ] Confirm GPU box repro (device pin, deterministic flags) per `docs/REPRODUCIBILITY_CHECKLIST.md`.

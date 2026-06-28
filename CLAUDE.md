# CLAUDE.md — agent operating brief for `llm-reward-portfolio`

You are building the codebase for an MSc dissertation: **an LLM designs reward-function code
for a risk-sensitive deep-RL portfolio agent, with the reflection loop fed the realized-return
*distribution* (tail statistics) rather than a scalar.** The full design, module specs, configs,
prompts, and phased task list live in **`../00_planning/FINAL_PLAN_FOR_CLAUDE_CODE_DETAILED.md`**
(authoritative) and **`../00_planning/LITERATURE_AND_DEFENSE_COMPANION.md`** (the literature that
justifies every choice). This file is the always-on contract; the FINAL_PLAN is the spec.

> The two `_superseded/` plans (DISSERTATION_MASTER_PLAN, BUILD_SPECIFICATION) predate the audit.
> Where they conflict with FINAL_PLAN, **FINAL_PLAN wins** (e.g. measurement is empirical+EVT, not a
> neural IQN; the headline agent is fixed SB3 SAC with TQC as a *secondary* critic experiment, not
> IQN-SAC; compute is a **rented RTX 4090** + seeds-on-winners — **no UCL Myriad** — see
> `docs/COMPUTE_AND_TRAINING_TIME.md` / ADR-023, not a $50 Colab plan).

## Post-merge context (ADR-022, 2026-06-17) — read before touching the repo
This repo is the **unification of two lines**: A = the audited *experimental engine* (canonical), B = the
*data + acquisition* line. What that means in practice:
- **Live code is A's audited `src/`** (empirical+EVT measurement, SB3 SAC + TQC, full inference incl. FZ/ES
  + DSR/PBO, the Eureka loop). B's **pre-audit** science (IQN-SAC, dropped `crossing_rate`) was **NOT**
  merged — it is preserved in **`archive/pre_merge_repo_B/`** (with a successor map).
- **The REAL data is here:** `data/gold/returns_panel_univ3.parquet` (5,283×953, survivorship-free, PIT;
  Refinitiv/LSEG — **not** CRSP). Load it into the env via **`src/data/loaders.py::load_gold_panel`**
  (anonymised ids; default delisting policy `liquidate_to_cash`, ⚠ provisional — ADR-024).
- **`data_pipeline/`** is B's self-contained Refinitiv→gold acquisition stack (provenance/reproducibility;
  needs live Refinitiv creds to re-run; the gold is already frozen).
- **Two decision logs:** `DECISIONS.md` (root, ADRs 001–024) is **authoritative going forward**;
  `docs/DECISION_LOG.md` (audit/impl/compute entries) is the A-line audit record — append new decisions to
  `DECISIONS.md`. Full merge backup: `~/Downloads/_merge_backup_2026-06-17/`.

## Prime directives (override any task on conflict)
1. **Reconcile, do not assume.** Run the inventory (below) before any task. This repo's stubs are a
   *reference architecture*; where a real file/signature exists, extend it — never duplicate under a
   new name. If a real signature diverges from the spec, follow the real one and note it in
   `docs/DECISION_LOG.md`.
2. **Scope discipline (frozen design).** Add nothing: no multi-agent system, no RAG, no GNNs, no
   transformer agent, no news/sentiment pipeline, no extra asset classes, no options. The urge to
   add scope is the signal to **stop and flag**, not proceed.
3. **Respect the pre-registration.** After Phase 1, `PREREGISTRATION.md` is FROZEN (hypotheses,
   candidate budget, seeds, fitness, the frozen tail-diagnostic set, splits, embargo, benchmark
   suite, analysis plan). Changing any of it requires an explicit amendment entry approved by the
   user — never a silent edit.
4. **No fabrication.** Do not invent repo internals, data, results, or citations. In `paper/refs.bib`
   mark every 2025–2026 sweep-surfaced reference `% VERIFY`; never present an unverified arXiv id as
   confirmed. (The supervisor co-authored two corpus papers — a bad citation gets caught.)
5. **Test, then commit.** Every module gets behaviour-checking unit tests (invariances, bounds,
   calibration), not just smoke tests. One focused commit per task; message names the task id and
   what was verified. Never commit failing tests.
6. **Determinism & provenance.** Seed every stack from the run seed (`src/utils/seeding.py`); archive
   every prompt, generated reward, and feedback block. Results **replay** from the archive — they
   cannot be *regenerated* (LLM calls are non-deterministic).
7. **Stop-and-ask triggers.** A frozen-decision change; a persistent RED smoke test after reasonable
   debugging; a genuinely ambiguous design choice; anything requiring fabricated data or citations.

## The keystone
**Phase 0 is the gate.** Every compute/cost/timeline figure is an estimate until
`scripts/smoke_test.py` trains SB3 SAC **and** sb3-contrib TQC on the online path on the owned RTX 4050
(dev/Phase-0; the rented RTX 4090 is the campaign GPU — ADR-023), proves the loss falls, and reports
minutes-per-run. Do Phase 0 before building anything downstream.

## Run-first inventory (every session)
```bash
ls -R . | sed -n '1,250p'
cat CLAUDE.md PREREGISTRATION.md
for f in config/*.yaml; do echo "=== $f ==="; cat "$f"; done
ls src/ tests/ scripts/ prompts/ 2>/dev/null
git log --oneline -20
pytest -q 2>/dev/null | tail -20
```

## The two distinct "distributional" axes — DO NOT CONFLATE (audit A-1)
- **THE CONTRIBUTION (H2) = the FEEDBACK CHANNEL.** Does feeding the LLM reward-designer
  **multi-level tail-risk feedback** — six left-tail scalars (`cvar_05`/`10`/`25`/`01`,
  `left_tail_mass`, `robust_skew`; a coherent-risk profile of the realized-return *lower tail*, **not**
  the full distribution — R53) beat feeding it a **scalar** performance number? Arms vary **only the
  feedback block**; the **agent is held fixed (SB3 SAC)**. The tail-risk feedback is a
  **critic-agnostic post-hoc estimator** (`src/feedback/measurement.py`): it reads no Q-network and
  fits only on *realized* returns, so it is architecture-independent (works against the SAC mean critic,
  the TQC quantile critic, anything).
  - **Honesty (do not equivocate):** "critic-agnostic" is NOT "agent-independent." The estimator fits
    the **trained policy's OWN realized returns under the candidate reward**, so the fed tail is
    **endogenous** to the agent it steers. H2 thus compares two coupled reward -> policy -> measurement
    loops (scalar-fed vs tail-fed) — the legitimate object of study, not an exogenous risk measurement.
    The train/val split (fed in-sample, scored out-of-sample) mitigates selection-overfitting but does
    NOT break this endogeneity. Never write "works on any agent / agent-independent." (See the
    `measurement.py` module docstring and `README.md` "What is / isn't in the fed vector"; the formal
    distributional-sufficiency argument in the theory spine is unaffected.)
- **A SECONDARY, NAMED experiment = the AGENT'S CRITIC** (SAC mean-critic vs TQC quantile-critic).
  Known in the literature (DSAC, Tail-Safe); **not the novelty**; run only if its Phase-0 smoke is green.

## Conventions
- Python 3.11; one venv; pin versions (`pyproject.toml`). PyTorch + d3rlpy 2.8.1 compatibility is the
  fragile pin — fix it in Phase 0.
- `config/*.yaml` is the single source of truth for parameters; code reads config, never hardcodes.
- Reward code from the LLM is **untrusted**: AST-gate once, then run in-process (`src/sandbox`,
  `src/reward/contract.py`). Anonymised arrays only — no tickers, no dates — ever reach a reward.
- Analysis reads results **only** through `src/io/results.py`; never parse run files ad hoc.

## Build order (bottom-up; see FINAL_PLAN Part G/H)
Phase 0 smoke → env → data pipeline/gold → measurement + fitness (B1/B3) → contract+sandbox,
baselines, regimes, seeding, results-IO → feedback schema + agents + LLM loop → arms + search
baselines → inference (incl. FDR) → orchestration → pilot → campaign → analysis → writing.

**Begin with Phase 0, Task 0.A. Report after each task: what changed, the test result, acceptance status.**

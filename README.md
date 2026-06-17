# llm-reward-portfolio

**Agentic reward engineering with LLMs for risk-sensitive deep-RL portfolio allocation.**
MSc Banking & Digital Finance, UCL Institute of Finance and Technology · supervisor Dr Ramin Okhrati ·
dissertation due **1 Sep 2026** · ICAIF '26 paper target **~2 Aug 2026**.

> **One sentence.** An LLM designs the *reward-function code* for a portfolio-allocation RL agent;
> we test whether feeding its reflection loop the **realized-return distribution** (CVaR at several
> levels, left-tail mass, robust skew) beats feeding it a **scalar** performance number — at matched
> compute, against scalar/placebo/single-CVaR controls.

## Contributions
- **N1 (headline):** first to feed a **return-distribution** signal to an LLM reward designer (H2).
- **N2:** first Eureka-style reward-**code** synthesis for a **trading/portfolio** RL agent.
- **N3:** contamination-aware evaluation (adopted method, not claimed novel).

## ⚠ Start here
1. Read `CLAUDE.md` (operating contract) and `../00_planning/FINAL_PLAN_FOR_CLAUDE_CODE_DETAILED.md`
   (authoritative spec — design, module specs, configs, prompts, phased tasks).
2. **Phase 0 is the gate.** Run the smoke test before building anything downstream:
   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   python scripts/smoke_test.py        # SB3 SAC + TQC on the RTX 4090, online, timed
   ```
   GREEN (both train, loss falls, per-run minutes recorded) → proceed to Phase 1. Persistent RED → stop.

## Layout
```
config/        # single source of truth (10 YAMLs: algos, arms, campaign, data, environment, llm,
               #   preregistration, regimes, eureka_loop, inference)
prompts/       # LLM prompt templates — see prompts/README.md (live prompts are hardcoded in src/llm/loop.py
               #   pending T4; A's system/initial/reflection.txt + B's arm-specific v0 variants kept as reference)
src/
  env/         # the portfolio MDP (reward injected via a callable slot)
  feedback/    # measurement.py (empirical+EVT tail stats, the contribution) + schema.py (the 5 arms' blocks)
  selection/   # fitness.py — held-out Deflated Sharpe (reward-independent)
  reward/      # contract.py — the reward signature/contract
  sandbox/     # executor.py — AST-gate-once + in-process run of untrusted reward code
  baselines/   # hand-designed reward canon + benchmark strategies
  agents/      # SB3 SAC (headline) + TQC (secondary critic)
  llm/         # the Eureka-style loop + pinned-snapshot client (archives every call)
  arms/        # builds the six arms from config
  search/      # H4 baselines: random-search-over-code, BO-over-template
  inference/   # bootstrap, PBO/CSCV, deflated Sharpe, rliable, multiple-testing
  regimes/     # regime labelling (feeds the power analysis)
  io/          # results schema + the ONLY loader analysis may use
  utils/       # seeding, typed config loader, provenance/hashing, structured logging
  data/        # panel type + synthetic generator + pipeline.py (SYNTHETIC) + loaders.py (loads the REAL gold)
scripts/       # entry points — smoke_test, power_analysis, freeze, build_gold, verify_gold, run_campaign,
               #   analyze_results, inspect_rewards are STUBS (fail loudly; GPU/data-gated; blueprint T1–T6).
               #   verify_inventory.py (data audit) is live.
tests/         # 153 behaviour tests (148 engine + 5 real-gold loader) — `make test`
data/          # raw/ clean/ staged/ gold/ synthetic/ + manifest/  — REAL Refinitiv gold panel lives here
               #   (5,283×953 PIT, survivorship-free); licensed & gitignored, manifest/provenance tracked
data_pipeline/ # the Refinitiv→gold acquisition pipeline (relocated from repo B; self-contained; provenance)
archive/       # pre_merge_repo_B/ — B's pre-audit science + root docs, preserved (nothing lost; ADR-022)
outputs/       # runs/ figures/ tables/  — campaign artifacts (gitignored)
runs/          # data-acquisition run logs (from B; gitignored)
reports/       # data EDA, quality scoreboard, session reports (from B)
paper/         # dissertation.tex + chapters, icaif/ (≤8pp), refs.bib
docs/          # engine: DECISION_LOG, POWER_ANALYSIS, COMPUTE_AND_TRAINING_TIME; data: DATASHEET,
               #   DATA_ENTITLEMENTS, environment_spec_v1, distributional_feedback_schema, REFERENCES
CHANGELOG.md   # Keep-a-Changelog (continued from B); DECISIONS.md = ADRs 001–022
PREREGISTRATION.md   # frozen design record (frozen end of Phase 1)
```

> **Unified repository (2026-06-17, ADR-022).** This repo is the merge of two lines: the audited
> *experimental engine* (`src/`, the live code) and the *data + acquisition* line (the real gold panel in
> `data/`, the pipeline in `data_pipeline/`). A's audited science is canonical; B's pre-audit science is
> preserved in `archive/`. Full backups at `~/Downloads/_merge_backup_2026-06-17/`. See `DECISIONS.md`
> ADR-022 and the top `CHANGELOG.md` entry for the complete, staged, no-loss merge record.

## Status (as of 16 Jun 2026)
- ✅ Topic locked; novelty confirmed (8 sweeps + kill-search; N1/N2 hold).
- ✅ Literature corpus: 196 verified PDFs in `../01_literature/` (13 families + logs + `BIBLIOGRAPHY.md`).
- ✅ Plans frozen in `../00_planning/`.
- ✅ **Deterministic core implemented and tested — `148 tests pass`** (`make test`): the full
  statistical-inference stack, the empirical+EVT measurement, the feedback schema, fitness, the
  reward contract + AST sandbox, the baselines (reward canon + HRP / risk-parity / MV-shrinkage), the
  Gymnasium environment (with real no-look-ahead invariance tests), regimes, results IO, the 13-stage
  pipeline (on synthetic data), the arms factory, and both H4 search baselines.
- ✅ Agent-training / LLM paths implemented as real, dependency-injected code (SB3 SAC + TQC via lazy
  import; the Eureka loop tested end-to-end with fakes) — they run once torch/SB3 + an `LLM_API_KEY`
  are available on the GPU box.
- ⬜ **Phase 0 smoke test (the gate)** ← next action: confirm SAC + TQC train on the RTX 4090 and record
  minutes/run. Then design freeze · gold rebuild · campaign · analysis · writing.

### Verify it yourself
```bash
make venv && make test     # 148 passing tests on the light scientific stack (no GPU needed)
```

## Non-negotiables (see `CLAUDE.md`)
Reconcile-don't-assume · no scope creep · respect the freeze · no fabricated citations · test-then-commit ·
replay-not-regenerate · stop-and-ask on frozen-decision changes.

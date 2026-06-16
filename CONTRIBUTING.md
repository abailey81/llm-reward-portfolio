# Contributing / working in this repo

This is a single-author MSc dissertation codebase, but it is built to professional standards so the
results are reproducible and auditable. Read `CLAUDE.md` (the operating contract) and
`../00_planning/FINAL_PLAN_FOR_CLAUDE_CODE_DETAILED.md` (the authoritative spec) first.

## Setup
```bash
make venv          # venv inheriting system scientific libs + gymnasium (deterministic core)
make install-dev   # OR: full install incl. torch/SB3 for the training paths (needs the GPU box)
make test          # run the suite
```
The **deterministic core** (inference, measurement, sandbox, baselines, environment, regimes, IO)
runs and is fully tested on the light stack. The **agent-training / LLM** paths additionally require
torch + Stable-Baselines3 + sb3-contrib and an `LLM_API_KEY`; their tests are marked `slow` / use fakes.

## The rules that matter (from CLAUDE.md)
1. **Reconcile, don't assume** — extend real modules; never duplicate under a new name.
2. **No research-scope creep** — no multi-agent/RAG/GNN/extra-data/options. (Engineering quality is
   *not* scope creep; correctness, tests, and tooling are always welcome.)
3. **Respect the freeze** — after Phase 1, `PREREGISTRATION.md` changes need a dated amendment.
4. **No fabricated citations** — `% VERIFY` every 2025–2026 reference until checked.
5. **Test, then commit** — behaviour tests (invariances, bounds, calibration), not smoke. Never commit
   red tests. One focused commit per task; the message names the task id and what was verified.
6. **Replay, not regenerate** — archive every prompt/reward/feedback; LLM calls are non-deterministic.

## Conventions
- Python 3.11 (project target; the deterministic core also runs on 3.13). Type hints throughout;
  `from __future__ import annotations` at the top of every module.
- `config/*.yaml` is the single source of truth — read it via `src.utils.config`, never hardcode.
- Untrusted LLM reward code is AST-gated once then run in-process (`src.sandbox`, `src.reward.contract`);
  anonymised arrays only — no tickers/dates reach a reward.
- Analysis reads results only through `src.io.results`.
- `ruff` for lint+format, `mypy` for types, `pytest` for tests; `pre-commit install` to enforce.

## Commit message format
```
<area>: <imperative summary>   (e.g. "inference: implement PBO/CSCV + null-calibration test")

Task <id>; verified: <which acceptance criteria / tests pass>.
```

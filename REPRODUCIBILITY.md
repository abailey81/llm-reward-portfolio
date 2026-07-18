# Reproducibility

This study is built to be reproduced. Determinism is load-bearing: results **replay from an on-disk
provenance archive** rather than being regenerated (LLM calls are non-deterministic). This document is the
single map from *what you want to reproduce* to *the exact command*.

## 1. Environment

Python 3.11. The exact, fully-pinned dependency set — including the precise PyTorch + CUDA build, the most
common cause of irreproducible RL numbers — is captured in [`requirements.lock`](requirements.lock).

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.lock                      # exact, reproducible environment (torch==2.6.0+cu124)
pip install -e .                                       # install the package itself
```

For a lightweight, CPU-only verification environment (no torch/SB3), [`requirements-test.txt`](requirements-test.txt)
is the deterministic-core subset used by CI.

## 2. The frozen design

The experimental design — hypotheses, arms, candidate budget, seeds, splits, fitness, the frozen
tail-diagnostic set, and the entire analysis plan — is recorded in [`PREREGISTRATION.md`](PREREGISTRATION.md)
and bound by a **SHA-256 hash** over the prose, the bound configuration, and the loaded prompts. Every change
after Phase 1 is a dated amendment entry, never a silent edit.

```bash
python scripts/freeze.py --check     # verify design integrity (prose <-> config consistency + the hash)
```

## 3. Data (licensed — pipeline, checksums, and synthetic shipped)

The headline results use a licensed Refinitiv/LSEG equity panel that **cannot be redistributed**. The
repository ships everything needed to reproduce the *method* without the raw data:

- [`data_pipeline/`](data_pipeline/) — the Refinitiv → gold acquisition pipeline; an entitled user rebuilds
  the exact panel.
- `data/**/*.sha256`, `data/**/*.provenance.json` — SHA-256 checksums and provenance for byte-exact verification.
- [`data/synthetic/`](data/synthetic/) — a shape-identical synthetic panel; the full pipeline and test suite
  run on it. Most scripts accept a `--synthetic` flag to run end-to-end without the licensed data.

## 4. Reproduce, stage by stage

| Goal | Command |
|---|---|
| Deterministic-core behaviour tests (no GPU) | `make test` |
| Agent-training smoke / Phase-0 gate | `python scripts/smoke_test.py` |
| Training-budget **convergence study** (sets the per-candidate budget at the measured plateau) | `python scripts/learning_curve.py --budgets 50000,100000,200000,400000,800000 --seeds 0,1,2` |
| Freeze the design | `make freeze` |
| Confirmatory campaign (idempotent, resumable) | `python scripts/run_campaign.py --resume` |
| Analysis | `python scripts/analyze_campaign.py` |
| Figures | `python scripts/make_figures.py` |

The campaign is documented end-to-end in [`docs/CAMPAIGN_RUNBOOK.md`](docs/CAMPAIGN_RUNBOOK.md).

## 5. Determinism & provenance guarantees

- **Seeding** — every stack (NumPy, PyTorch, SB3, the env) is seeded from the run seed
  (`src/utils/seeding.py`); `CUBLAS_WORKSPACE_CONFIG` and `PYTHONHASHSEED` are pinned for deterministic cuBLAS.
- **Provenance archive** — every LLM call archives the rendered prompt, the authored reward code, the
  feedback block, the resolved model id, the token usage, and the stop reason.
- **Crash-consistent writes** — each run's result is written atomically (temp file → `flush` + `fsync` →
  atomic rename), so an interrupted campaign resumes from disk with `--resume` and can never bake a
  half-written record into the frozen analysis.
- **Single read path** — analysis reads results **only** through `src/io/results.py`; no ad-hoc parsing.

## 6. Reproducibility checklist

- [x] Code openly available (this repository).
- [x] Exact dependency lockfile, with PyTorch + CUDA pinned (`requirements.lock`).
- [x] Deterministic seeding, documented and tested.
- [x] Pre-registered design with a cryptographic integrity hash (`PREREGISTRATION.md`, `scripts/freeze.py`).
- [x] Data provenance + SHA-256 checksums; a shape-identical synthetic stand-in for the licensed panel.
- [x] Exact commands to reproduce every stage (§4).
- [x] Behaviour test suite (2,000+ tests; `make test`) plus a continuous-integration drift guard.

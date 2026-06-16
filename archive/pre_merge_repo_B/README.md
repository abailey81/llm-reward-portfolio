# `archive/pre_merge_repo_B/` — preserved snapshot of repo "B" (pre-merge)

This folder preserves the parts of the former `~/Downloads/llm-reward-portfolio` repo ("B") that were **not
carried into the live unified repo**, so **nothing is lost** by the unification (ADR-022). Everything else
from B is already live: the real data is in [`../../data/`](../../data/), the acquisition pipeline in
[`../../data_pipeline/`](../../data_pipeline/), and B's provenance docs (`CHANGELOG.md`, `DECISIONS.md`,
`reports/`, `runs/`, `docs/*`) at the repo root.

## Contents
- **`src_flat/`** — B's **pre-audit** science modules (flat layout). These are **superseded** by the audited
  package modules in [`../../src/`](../../src/) and are kept only for provenance. The proof they are
  pre-audit: `smoke_iqn_sac.py` is the IQN-SAC agent the audit **rejected** in favour of SB3 SAC + TQC, and
  `feedback_schema.py` carries a `crossing_rate` reliability diagnostic the preregistration explicitly
  **dropped from the headline**. Successor map:

  | B (pre-audit, here) | live successor in `src/` |
  |---|---|
  | `portfolio_env.py` | `src/env/portfolio_env.py` (audited) |
  | `feedback_schema.py` | `src/feedback/schema.py` + `src/feedback/measurement.py` (EVT `ReturnDistribution`) |
  | `sandbox.py` | `src/sandbox/executor.py` (AST gate + `_safe_import` fix) — *B's resource-limited isolation noted as a candidate future port, own ADR* |
  | `reward_contract.py` | `src/reward/contract.py` (`RewardFn` Protocol) |
  | `rewards_baselines.py`, `reward_family.py` | `src/baselines/rewards.py`, `src/baselines/strategies.py` |
  | `fitness.py` | `src/selection/fitness.py` (held-out, reward-independent) |
  | `stats_inference.py` | `src/inference/*` (bootstrap diff-tests, DSR, PBO, FZ/ES, multiple-testing) |
  | `regimes.py` | `src/regimes/definition.py` |
  | `candidate_archive.py` | `src/llm/loop.py` (`CandidateArchive`) |
  | `config.py`, `features.py` | live in `data_pipeline/src/` (acquisition); engine uses `src/utils/config.py` |
  | `calibrate_lambda.py`, `dry_run_random_search.py`, `pull_pilot.py`, `reconcile.py` | superseded by `src/search/*`, `data_pipeline/`, engine scripts |

- **`root_docs/`** — B's `CLAUDE.md`, `README.md`, `PREREGISTRATION.md`, `Makefile`, `pyproject.toml`,
  `requirements.txt`. The **live canonical** versions are A's at the repo root; these B-versions are retained
  for reconciliation/provenance. (Any B-only requirement, e.g. data deps, is folded into the live config.)

## Full-fidelity backup
A complete `.tgz` of B (including `.git` history and data) is at
`~/Downloads/_merge_backup_2026-06-17/B_downloads_llm-reward-portfolio.tgz`.

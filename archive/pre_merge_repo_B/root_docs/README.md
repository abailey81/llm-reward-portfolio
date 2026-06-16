# llm-reward-portfolio

**LLM-Driven Agentic Reward Engineering for Risk-Sensitive Deep Reinforcement Learning in Portfolio Allocation**

UCL MSc Banking and Digital Finance dissertation (IFTE0008) · Institute of Finance & Technology · Supervisor: Dr Ramin Okhrati (AIRiskLab) · Author: Tamer Atesyakar · Dissertation due **1 September 2026** · Candidate venue: **ACM ICAIF 2026** (paper deadline 2 August 2026, Milan).

---

## 1. What this project is

This repository implements and evaluates an **Eureka-style agentic loop** (Ma et al., ICLR 2024) in which a large language model reads the source code of a portfolio Gymnasium environment, **writes candidate reward functions as executable Python**, has each candidate train deep-RL portfolio agents (SAC / PPO / TD3 / IQN-SAC), ranks candidates on a **held-out validation fitness** (CVaR-penalised Sharpe), and receives a **reward reflection** to improve the next generation.

The original contribution is the **distributional feedback channel**: quantile-function statistics extracted from an Implicit Quantile Network critic (Dabney et al., ICML 2018) — CVaR at 1/5/10/25%, tail skewness, left-tail slope — serialized as structured text in the reflection, and **ablated against scalar-only feedback at matched compute**.

> **Novelty claim (hedged, as it must appear everywhere):** To the best of our knowledge, this is the first work to (i) adapt LLM-based evolutionary reward-function synthesis from robotics to financial portfolio allocation, and (ii) feed distributional-critic statistics back to a meta-level LLM reward designer — in contrast to the scalar reflection of Eureka and the LLM-as-signal-generator paradigm of FinRL-DeepSeek (Benhenda, 2025). Verified by three literature sweeps plus two adversarial re-checks, most recently 10 June 2026 (see `RELATED_WORK_WATCH.md`).

The experimental design is built so that **a rigorous negative result is also a strong result** (supervisor's explicit guidance): matched-compute baselines (random reward search, Bayesian optimisation, single-shot LLM, the canonical differential-Sharpe hand-designed reward) and selection-aware inference (Deflated Sharpe Ratio over the true candidate count; Probability of Backtest Overfitting) mean the headline claim survives its own search either way.

## 2. Architecture (one screen)

```
                          ┌─────────────────────────────────────────────┐
                          │  prompts/  (system · safety · reflection)   │
                          └──────────────────┬──────────────────────────┘
                                             ▼
   env source code ──────►  LLM  ──► K=16 candidate reward fns (Python)
        ▲                                    │ sandboxed exec (src/sandbox.py)
        │                                    ▼
   src/portfolio_env.py  ◄── reward contract: fn(ctx) -> (float, components)
   (PIT data, costs,                         │ trains SAC/PPO/TD3/IQN-SAC
    softmax weights)                         ▼
                              held-out fitness  F = CVaR-penalised Sharpe
                              (src/fitness.py — NEVER the training reward)
                                             │
              ┌──────────────────────────────┴───────────────┐
              ▼                                              ▼
   scalar reflection                          distributional reflection
   (return/Sharpe/DD/turnover                 (IQN quantiles → sorted →
    time series)                               CVaR profile, tail stats;
                                               src/feedback_schema.py)
              └──────────────► next LLM generation ◄─────────┘
                                             │  after N=5 iterations
                                             ▼
                  selection-aware inference: DSR · PBO/CSCV · Ledoit-Wolf
                  bootstrap · BH-FDR  (src/stats_inference.py)
                  regime-stratified evaluation (src/regimes.py, filtered HMM)
```

## 3. Repository layout

| Path | Purpose | Status |
|---|---|---|
| `CLAUDE.md` | Operating manual for Claude Code: hard rules, conventions, playbooks, domain crib sheet | ✅ authoritative |
| `PREREGISTRATION.md` | Frozen experimental design: hypotheses, fitness, budgets, inference rules | 📝 DRAFT v1.0 — freeze by committing 12 Jun |
| `DECISIONS.md` | Architecture Decision Records — every locked choice, dated, with reasoning | ✅ live |
| `RELATED_WORK_WATCH.md` | Monthly novelty re-sweep log | ✅ entry 1 |
| `config/` | Every parameter in the project, YAML, citation-annotated. **No magic numbers in code.** | ✅ |
| `prompts/` | System / safety / mutation / reflection templates (v0) | ✅ drafts |
| `src/` | Library + scripts (see table below) | mixed — see status |
| `tests/` | Pytest suite for everything implementable today | ✅ passing locally in build |
| `docs/` | Specifications, entitlement checklist, paper notes, references bank | ✅ |
| `reports/` | Supervisor brief, vendor-reconciliation report (template) | ✅ / 📝 |
| `data/` | **Immutable once pulled.** CSVs gitignored; SHA-256 manifest tracked | empty by design |

### `src/` module status

| Module | What it does | Status |
|---|---|---|
| `feedback_schema.py` | Distributional feedback: sorted quantiles → CVaR profile, Bowley/moment skew, left-tail slope, crossing rate; JSON + prompt serialization | ✅ implemented + tested |
| `stats_inference.py` | PSR, **Deflated Sharpe Ratio** (expected-max SR with Euler–Mascheroni term), MinTRL, **PBO via CSCV**, TrialLedger | ✅ implemented + tested |
| `fitness.py` | CVaR-penalised Sharpe on a held-out window (fails loudly while λ unfrozen) | ✅ implemented + tested |
| `portfolio_env.py` | Gymnasium env: softmax long-only weights + cash, proportional costs, component-dict reward injection, optional leakage-safe cash-feature block | ✅ implemented + tested (ADR-007) |
| `features.py` | Cash-row features [vol20, vol20/vol60, vix], shift(1)-lagged; truncation/perturbation-invariance tested | ✅ implemented + tested (ADR-007) |
| `reward_contract.py` | The contract every candidate must satisfy + probe battery (single-sourced with the sandbox) | ✅ implemented + tested |
| `rewards_baselines.py` | Full six-reward hand-designed canon + config-enforced registry | ✅ implemented + tested (ADR-009) |
| `reward_family.py` | Parameterised six-term family for the H4 random/BayesOpt arms (vertices = the canon) | ✅ implemented + tested (ADR-010) |
| `calibrate_lambda.py` | PREREG §3 λ-selection machinery (deterministic tie-breaks; never writes config) | ✅ implemented + tested (runs after first training runs) |
| `regimes.py` | 3-state Gaussian HMM: fit-on-train, **filtered** forward recursion over public params, shift(1) | ✅ implemented + tested (ADR-011) |
| `sandbox.py` | AST static gate + isolated subprocess + rlimits + contract validation for untrusted reward code | ✅ hardened + denial-corpus tested (ADR-008) |
| `candidate_archive.py` | Verbatim append-only candidate archive (R6) | ✅ implemented + tested |
| `dry_run_random_search.py` | TrialLedger→DSR/PBO plumbing proof on labelled throwaway candidates | ✅ implemented + tested + executed |
| `data/` (13 modules) | **Medallion data platform**: vault, journaled acquisition, entitlement probes, security master, validation+missing engine, corp-actions+outlier taxonomy, PIT membership, reconciliation, gold panels + PREREG-§6 splits, EDA, quality/datasheet, CLI | ✅ implemented + tested + run on real data (ADR-012) |
| `smoke_iqn_sac.py` | IQN-inside-SAC proof-of-life; **API verified against d3rlpy 2.8.1 source** (ADR-003) | ▶ 4090 only — torch≥2.5 has no Intel-mac wheels (ADR-014) |
| `pull_pilot.py` / `reconcile.py` | Legacy pilot scripts | superseded by `python -m src.data.cli` (kept for reference) |

✅ = implemented and unit-tested in this build · ▶ = runnable script awaiting the GPU box.
**Test suite: 114 tests; data layers carry REAL vendor data only (pulled & checksummed 2026-06-10).**

## 4. Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
make setup          # installs pinned deps; writes requirements.lock
make test           # pytest on the implemented modules (should pass before anything else)
make smoke          # IQN+SAC proof-of-life (GPU box; ~1 min)
cp .env.example .env  # add FRED key; Refinitiv configured via Workspace/eikon config
make pull-pilot     # 5-ticker pulls -> data/ + checksum manifest
make reconcile      # writes reports/vendor_reconciliation_pilot.md tables
```

Open the folder in **VS Code** and start **Claude Code** in the repo root — it reads `CLAUDE.md` automatically and is bound by its rules (frozen pre-registration, scope lock, leakage laws, data immutability).

## 5. Roadmap (anchored to the execution plan)

**This week (10–12 Jun):** entitlement verification → pilot pulls + reconciliation → pre-registration frozen (commit hash into ADR) → smoke test on the 4090 → supervisor one-pager at the first group meeting; raise the **ICAIF 2 Aug** option with Ramin.
**w/c 15 Jun:** environment features (Sood-style [(n+1)×T] state), reward-interface harness, sandbox hardening, first hand-designed-reward training run.
**Late Jun–Jul:** full PIT data build → Eureka loop live (scalar arm) → distributional arm → ablations A1–A5 → ICAIF fork decision (~19 Jun) governs July intensity.
**Aug:** writing month (protected); ICAIF submission 2 Aug if Option A; dissertation 1 Sep.

## 6. Provenance & integrity

Design and documentation were developed with AI assistance (to be acknowledged in the dissertation, as in prior coursework). All third-party formulations carry citations in `docs/REFERENCES.md` and in module docstrings. Data, once pulled, is immutable and checksum-manifested; generated reward functions and every LLM prompt/response are archived verbatim for reproducibility against model drift. The pre-registration, once frozen, may only be amended via a dated ADR plus supervisor notification — that discipline is what makes the Deflated Sharpe Ratio honest and a negative result publishable-strength.

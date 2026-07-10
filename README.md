<div align="center">

# Agentic Reward Engineering for Risk-Sensitive Portfolio RL

**Does feeding an LLM reward-designer a *multi-level tail-risk* signal produce better reward code than a scalar one?**

A pre-registered study in which a large language model authors the **reward-function code** for a fixed deep-RL
portfolio agent, and the *feedback channel* of its reflection loop is the manipulated variable.

[![Python](https://img.shields.io/badge/python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-2000%2B%20passing-2ea44f)](#reproducibility)
[![Compute](https://img.shields.io/badge/compute-UCL%20Myriad%20HPC%20%C2%B7%20SGE-orange)](docs/PLAN_IF_WE_USE_UCL_MYRIAD.md)
[![Pre-registered](https://img.shields.io/badge/design-pre--registered-8957e5)](PREREGISTRATION.md)
[![Determinism](https://img.shields.io/badge/results-replay--from--archive-0072B2)](#design-principles)
[![Lint](https://img.shields.io/badge/lint-ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/license-see%20LICENSE-lightgrey)](LICENSE)

MSc Banking & Digital Finance · UCL Institute of Finance & Technology · Supervisor: Dr Ramin Okhrati

</div>

---

## Abstract

An LLM (Claude Opus 4.8) is used as an **automated reward engineer**: through an Eureka-style reflection
loop it writes the Python reward function that a **fixed** Soft Actor-Critic agent optimizes while allocating
a long-only equity portfolio. The single manipulated variable is the **feedback channel** returned to the
designer between iterations — a **distributional** signal (six coherent left-tail risk statistics: CVaR at
5/10/25/1%, left-tail mass, robust skew) versus a **scalar** performance number — with the agent, data,
search budget, and evaluation held identical across arms. Four pre-registered controls (placebo,
shuffled-placebo, single-CVaR, and code/template search baselines) isolate the *information* in the channel
from its *format* and from search effort alone.

The study is **pre-registered**, **placebo-controlled**, and evaluated on a **survivorship-free,
point-in-time** equity panel with a sealed test period — and the headline is framed as a **corroborated
prediction**: it asks not merely *whether* the richer channel wins, but *why or why not*, supported by a
mechanism analysis (reward-code structural distance, designer responsiveness, and a prompt-leakage
fingerprint). The contribution is the **method and the evidence**, not a trading product.

A **secondary, pre-registered replication** uses an open-weights author (Qwen3-Coder-480B, served via
OpenRouter with the exact snapshot archived) as the study's reproducibility anchor and cross-model
contamination check — it never enters the confirmatory family. The confirmatory campaign runs on the
**UCL Myriad HPC cluster** (SGE batch arrays; device-homogeneous pools), with a laptop track kept in
full parity as the certified fallback.

## Contributions

- **N1 — headline.** First to feed a **multi-level tail-risk** signal — a coherent-risk profile of the
  realized-return *lower tail* — to an LLM reward designer, and to test it against matched scalar and placebo
  channels under a pre-registered equivalence design.
- **N2.** First **Eureka-style reward-*code* synthesis** for a **trading / portfolio** RL agent (prior
  reward-as-code work is robotics/control; the nearest finance work has the LLM emit a *signal*, not author
  the reward).
- **N3.** A contamination-aware, multiplicity-honest evaluation protocol for LLM-authored reward code
  (adopted and adapted, not claimed novel).

> **Construct honesty.** The fed vector is **six left-tail scalars** (`cvar_05/10/25/01`, `left_tail_mass` =
> P(r < −2σ), `robust_skew`) — a theory-grounded summary of the *lower tail*, **not** the full return
> distribution (no mode, no right tail, no full quantile grid). "Multi-level tail-risk feedback" is the
> accurate label; "the return distribution" would overstate what is operationalized.

## Why this is rigorous

| Concern | How it is handled |
|---|---|
| **Garden of forking paths** | Design, hypotheses, arms, budgets, splits, and the entire analysis plan are **frozen** (`PREREGISTRATION.md`) and bound by a cryptographic hash before any confirmatory run; every change is a dated amendment. |
| **Survivorship / look-ahead bias** | A **survivorship-free, point-in-time** Refinitiv panel (delisted names retained); purged-and-embargoed train / validation / sealed-test splits. |
| **"No effect because it didn't train"** | The per-candidate budget is set at a **measured convergence knee** (not a timing guess), with a learning-curve adequacy diagnostic. |
| **Reward hacking / spurious wins** | LLM-authored code is AST-gated and sandboxed; selection is on a tail-blind, reward-independent held-out Deflated Sharpe; the sealed test is never used for selection. |
| **Inference rigor** | rliable IQM with stratified-bootstrap CIs, intersection-union tests, TOST equivalence, Bayes factors, Model Confidence Set, PBO/CSCV, Deflated/Probabilistic Sharpe, FZ0 (VaR, ES) backtests, EVT/GPD tails, factor attribution. |
| **Reproducibility** | Determinism is load-bearing: results **replay from an on-disk provenance archive** rather than being regenerated; every prompt, authored reward, feedback block, and token count is archived. |

## Repository layout

```text
src/
  env/          Portfolio MDP (the reward is injected through a callable slot)
  feedback/     Tail-risk measurement (empirical + EVT) and the per-arm feedback schema
  reward/       The reward contract; sandbox/ AST-gates and runs untrusted reward code
  selection/    Held-out Deflated-Sharpe fitness (reward-independent)
  agents/       SB3 SAC (headline) + TQC (secondary critic); PopArt value-scale normalization
  llm/          The Eureka-style reflection loop + a pinned, fully-archived LLM client
  arms/         Builds the seven experimental arms from config
  search/       Search baselines (random-search-over-code, BO-over-template)
  inference/    Bootstrap, PBO/CSCV, Deflated Sharpe, rliable, Bayes-null, MCS, reward-code distance
  viz/          Publication-grade figure engine (Okabe-Ito, honest-null discipline)
  cluster/      UCL Myriad (SGE) adapter: content-addressed specs, LF-safe jobscripts, batch driver,
                the full campaign orchestrator — every science primitive REUSED (laptop == cluster)
  io/ utils/    Results schema + the sole analysis loader; deterministic seeding, config, provenance
config/         Single source of truth (11 YAMLs) — code reads config, never hardcodes
prompts/        Versioned LLM prompt templates
scripts/        Entry points: smoke_test · learning_curve · power_analysis · freeze · run_campaign · run_campaign_cluster · analyze_campaign · make_figures · monitor
tests/          2,000+ behaviour tests (invariances, bounds, calibration, parallel == serial replay)
data/           Synthetic panel + checksums + provenance (the licensed gold panel is git-ignored — see below)
data_pipeline/  Self-contained Refinitiv -> gold acquisition pipeline (provenance, reproducibility)
paper/          Dissertation + ICAIF manuscript + bibliography
PREREGISTRATION.md   The frozen design record and amendment log
```

## Reproducibility

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.lock && pip install -e .  # exact pinned env (torch==2.6.0+cu124)
make test                  # 2,000+ behaviour tests on the deterministic core (no GPU required)
make freeze                # cryptographically freeze the design, then run the confirmatory campaign
```

For the exact pinned environment and a stage-by-stage reproduction map (tests → convergence study → freeze →
campaign → analysis → figures), see **[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)**. The campaign is
orchestrated by `scripts/run_campaign.py` (idempotent, `--resume`-safe) and analysed by
`scripts/analyze_campaign.py`; see [`docs/CAMPAIGN_RUNBOOK.md`](docs/CAMPAIGN_RUNBOOK.md).

> **Licensed data.** The headline results use a licensed Refinitiv/LSEG equity panel that **cannot be
> redistributed**. This repository therefore ships the **acquisition pipeline, SHA-256 checksums, and a
> shape-identical synthetic panel** — the entire method is verifiable end-to-end on synthetic data, and the
> real panel is reconstructible by an entitled user via `data_pipeline/`. The gold panel itself is
> git-ignored by design.

## Design principles

- **Reconcile, don't assume** — extend the real interfaces; never duplicate under a new name.
- **Respect the freeze** — after Phase 1 the pre-registration is immutable except by dated amendment.
- **Replay, not regenerate** — LLM calls are non-deterministic; results are reproduced from the archive.
- **No fabrication** — no invented data, results, or citations; every recent reference is verified.
- **Test, then commit** — every module carries behaviour tests, not smoke tests.

## Citation

If you reference this work, please cite via [`CITATION.cff`](CITATION.cff). The frozen experimental design is
recorded in [`PREREGISTRATION.md`](PREREGISTRATION.md).

## License

See [`LICENSE`](LICENSE). The licensed market data is **not** covered and is not distributed with this code.

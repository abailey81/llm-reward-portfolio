# Metrics-and-Figures Completeness Plan (2026-07-26) — capture-once, derive-many

> **Why this doc exists (Tamer, 2026-07-26).** The dissertation needs a full, publication-grade figure/table
> suite like the corpus's best papers. The campaign is **frozen + replay-only** (LLM calls are
> non-deterministic; results replay from the archive, never regenerate), so **any metric not logged during the
> run is a figure we can NEVER make without re-running** — which is impossible. Therefore the archive must
> capture **as many metrics as feasibly possible**, so every figure we might ever want is derivable offline.
> **This is PRE-FREEZE-CRITICAL:** the capture layer must land + be tested + pass the golden reproduction
> BEFORE `freeze.py` runs, or the data is lost forever.

## The principle
- **Capture the RAWEST feasible data once; derive every figure offline.** A stored per-step return vector yields
  the equity curve, the drawdown, the QQ/tail plot, and the factor attribution — all without re-running.
- **Determinism-safe capture ONLY.** Every added recorder is **passive**: it reads values the run already
  computed (env `info`, SB3 logger, the LLM response). It **never** draws from a seeded RNG, adds an evaluation,
  or changes float arithmetic. The determinism envelope (CLAUDE.md) is untouched; the golden reproduction must
  stay bit-exact green after every change here.
- **Report-only.** None of this touches the frozen hypotheses, arms, budgets, seeds, fitness, or analysis plan.
  It is additive provenance (OPTIONAL schema fields + sidecars), back-compatible with every existing writer.
- **Size-bounded.** Full per-step matrices only where cheap/high-value (a small declared subset); summary
  time-series everywhere else. Numbers below are order-of-magnitude budgets.

## What the archive ALREADY captures (verified in `src/io/results.py` + `src/llm/loop.py`)
- Per frozen-winner TEST record: `test_returns` (per-step NET), `per_period_pnl`, `test_gross`, `test_turnover`
  (→ cost re-pricing), `reward_source`, `prompt`.
- Per CANDIDATE (all arms, all generations): `reward_source` (+ hash), `feedback_block`, `metrics['val_returns']`
  (per-period validation), `candidate_id`, `generation`, `wall_clock`, `env_fingerprint`.
- ⇒ Already derivable offline: **equity curve, drawdown, per-arm realized return/PnL distribution + QQ/EVT tail,
  factor attribution, cost sweep, performance profile, probability-of-improvement, PBO/CSCV, responsiveness
  (fed→code across candidates), AST-distance.** These figures are NOT blocked — they need renderers, not data.

## METRIC-COLLECTION GAPS — data NOT captured that WOULD block a figure (implement pre-freeze)
| id | Metric to capture | Enables (figure) | Where / how (determinism-safe) | Size budget |
|----|-------------------|------------------|--------------------------------|-------------|
| **M1** | Per-step **exposure summary** on the frozen-winner test path: cash fraction, Herfindahl concentration (HHI), gross/net exposure, effective #positions, turnover — a 1571-step × ~5-scalar series | Allocation/exposure-over-time, concentration, turnover-composition figures | `src/orchestration/test_leg.py`: read `info["weights"]`/`info["turnover"]` already emitted per step; reduce to the 5 summaries; ride in `metrics['test_exposure']`. Pure read. | ~63 KB/record × ~4k = ~250 MB |
| **M1b** | **Full** per-step weight matrix for a SMALL pre-declared subset (per-arm anchor winner at a fixed seed) | Allocation **heatmap** over time (Cartea/Coache/RAMAC archetype) | Same hook, gated to the declared subset (≈11 records) → `metrics['test_weights']` | ~12 MB × 11 = ~130 MB |
| **M2** | **Training curve**: (step, critic_loss, actor_loss, rollout return) downsampled ~every 5k steps (~80 pts) per training | **F9 learning curves** (currently the renderer exists but the DATA is not archived) | `src/agents/trainer.py`: a **read-only** SB3 callback reading the existing logger/`ep_info_buffer` (NO extra eval → no RNG) → `metrics['train_curve']` | ~1.3 KB × 42k = ~55 MB |
| **M3** | Per-step **reward-component** summary on the test path (mean of `info["components"]`) | Reward-decomposition / "what did the reward reward" figure | `test_leg.py`: reduce `info["components"]` → `metrics['test_components']`. Pure read. | tiny |
| **M4** | LLM **reasoning trace** + `reasoning_tokens` per candidate | Specificity ("uses content vs echoes surface") + the R85/R103 reasoning-pin reproducibility evidence | `src/llm/loop.py`: archive the already-received response as a `response.txt` sidecar + `metrics['reasoning_tokens']` | small |

All five are passive reads of already-computed values — **zero determinism-envelope impact**; each ships with a
test + a golden-reproduction re-run.

## FIGURE GAPS vs the corpus's top-band spine (renderers to add; data already/soon available)
Corpus non-negotiables (Agarwal rliable quartet + risk-lens pair + finance staples) mapped to our suite:
| id | Missing figure | Corpus precedent | Data source | Priority |
|----|----------------|------------------|-------------|----------|
| **G1** | **Performance profile** (run-score CDF across arms) | rliable F7/10/12 — the 2nd rliable-quartet member | metric already in `reporting.performance_profile` | HIGH (null-image) |
| **G2** | **Probability-of-improvement** plot (per-arm P(arm>baseline)+CI) | rliable A.28/29 | `reporting.probability_of_improvement` | HIGH (frames the null) |
| **G3** | **Per-arm realized return/PnL distribution + tail** (ECDF/QQ/EVT, left-tail annotated) on the TEST results | Tail-Safe F2-5, Cartea, RAMAC F13, Coache | archived `test_returns` per (arm,seed) | HIGH (the risk story) |
| **G4** | **Equity curve + drawdown** over the sealed test, arms+benchmark overlaid, log-scale | EIIE F5-7, FinRL-DeepSeek, Sood F2 | archived `test_returns` (cumprod) | HIGH (finance staple) |
| **G5** | **Allocation/exposure heatmap** over time | Cartea F3a, Coache F3, RAMAC F4 | needs **M1/M1b** | MED |
| G6 | Fed-vector **ablation curve**; code-evolution **diff** exhibit; quantiles-over-time | CARD F4-6; REvolve F2/CARD F7; Coache F8 | archives | LOW/appendix |

(Existing renderers already cover: system diagram F1, rliable IQM+CI F5, TOST/equivalence F6, controls F7,
reward-AST heatmap F8, responsiveness F8b, learning-curve renderer F9, mechanism chain F10, budget curve F11,
cross-leg forest F12, capability scatter F13, reliability heatmap F14, code exhibit F15, risk-return clouds F-D,
Bayes/MCS evidence-for-null F-E — a strong base.)

## TABLE GAPS vs the corpus
| id | Missing table | Corpus precedent | Priority |
|----|---------------|------------------|----------|
| **G7** | **Hyperparameter / config table** (SAC + training budget + seeds + env knobs) — doubles as a reproducibility artifact fitting the freeze ethos | Text2Reward T2/3, Sood T1, Khraishi-Okhrati T4, RAMAC T6 | HIGH |
| **G8** | **Method-comparison / novelty matrix** (us vs Eureka/Text2Reward/CARD/DLM/GIFT/RD-Agent × the conjunctive-cell dims: authors-CODE · tail-feedback · risk-sensitive-finance · pre-registered · off-critic) | CARD T1, RD-Agent T4 | HIGH (novelty priority) |
| **G9** | **Verbatim frozen-prompt table** (the 2 hash-bound prompts) | CARD T12/13, DLM T4/6 | MED (reproducibility) |
| G10 | Dedicated stylized-facts table; compute+cost table; notation glossary | Qu T1, CARD T10, Tail-Safe T1 | LOW (partly in T1/F3) |

## Flagged defects (from the engine audit) to fix in passing
- `budget_curve_exhibit` (F11) and `mechanism_chain` (F10) have **no unit test** — add.
- `tests/test_viz.py` docstring says "seven arms / eight figures" — **stale**, now 9 arms / 9 figures.
- `pyproject.toml:8` description says "**distributional** tail-risk feedback" — construct-discipline defect → "multi-level".

## Implementation sequence (pre-freeze-gating items FIRST)
1. **PRE-FREEZE (data capture, determinism-safe, tested, golden-repro-verified): M1, M1b, M2, M3, M4.** Nothing
   downstream can be recovered if these are missed. Each: add the passive recorder → OPTIONAL schema field →
   test → re-run `scripts/reproduce_synthetic.py` to confirm bit-exact.
2. Renderers G1-G5 (+ wire F10/F11/F12-F15 into `make_figures.py`; add F10/F11 tests).
3. Tables G7-G9.
4. Update `paper/FIGURE_TABLE_MANIFEST.md` to the complete suite; fix the flagged defects.

## Cross-session note
The capture hooks touch `src/orchestration/test_leg.py`, `src/agents/trainer.py`, `src/llm/loop.py`,
`src/io/results.py` (schema) — the FEATURE/BUILD + CAPACITY overlap zone. Coordinate via the dispatch doc so a
live test run is not disrupted; all changes are additive + back-compatible.

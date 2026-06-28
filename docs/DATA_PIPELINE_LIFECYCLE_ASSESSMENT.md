# Data-pipeline lifecycle — STRICT relevance assessment

The ML-lifecycle checklist is mostly framed for **supervised learning / deployed production ML**. This project
is a **deterministic, pre-registered REINFORCEMENT-LEARNING research experiment** on a fixed survivorship-free
PIT panel, evaluated once and replayed from an archive. So each item is judged: **DONE** (already implemented,
often sophisticated), **ADD** (genuinely relevant + deterministic + worth building now), or **REJECT** (a
supervised/production concept that does not map — implementing it would be cargo-cult noise that *lowers*
credibility). Being strict here is the point.

| # | Lifecycle item | Verdict | Reasoning |
|---|---|---|---|
| 1 | **Define the problem** | ✅ DONE | `PREREGISTRATION.md`: RL reward-*design* ablation (tail feedback vs scalar), not supervised prediction. The data pipeline's job is to produce the gold returns panel. |
| 2 | **Data collection** | ✅ DONE (sophisticated) | Refinitiv RDP (`lseg-data`) + Datastream DSWS; PIT monthly index membership, survivorship-free incl. dead `^RIC`s, market cap, delisting metadata; provenance JSON + manifest + SHA-256 (`data_pipeline/`, `loaders.py`). |
| 3 | **Data validation** | 🟢 **ADD** | Scattered checks exist (checksum, phase/window, NaN policy) but no single **data-contract**. Build `validate_panel()` asserting all invariants in one auditable place + tests. *(implemented this round)* |
| 4 | **Missing values** | ✅ DONE + validate | Dead-RIC / delisting handled (liquidate-to-cash); NaN policy (`error`/fill); **leakage-free VIX fill** (ffill-past, bfill-last-resort only). The contract now also *asserts* the post-policy finiteness invariant. |
| 5 | **Data cleaning** | ✅ DONE | Ince-Porter (2006) screens (min-price, extreme-return-reversal), split-artifact flags, currency handling. |
| 6 | **Data leakage** | ✅ DONE + 🟢 **HARDEN** | THE finance killer, and a core strength: PIT selection-buffer (strictly-prior info), purge/embargo, train/val/test split, anonymised-returns reward, leakage-free VIX fill. **ADD**: explicit leakage **assertions** in the contract (dates strictly increasing, no duplicate sessions, no future selection). *(implemented this round)* |
| 7 | **Feature engineering** | ◑ N/A (frozen state) | RL, not supervised: the "features" are the pre-registered state vector + the tail-stat feedback block (the contribution). No supervised feature-eng applies; the reward-input set is deliberately *minimal + anonymised* (design integrity). |
| 8 | **Class imbalance** | ❌ REJECT | **No classes** — continuous returns / simplex weights (regression/control). SMOTE/reweighting is meaningless here; adding it would be cargo-cult. |
| 9 | **Model training** | ✅ DONE (the campaign) | Fixed SB3 SAC (+ TQC secondary), deterministic seeding; this is the campaign, not a data-pipeline concern. |
| 10 | **Baseline models** | ✅ DONE | 9 reward baselines + 10 allocators (`BENCHMARKS_CATALOG.md`); search baselines (random/Bayes); 1/N severity floor. |
| 11 | **Label errors** | ◑ mostly N/A | **No supervised labels** in RL. Closest analogue = data errors (handled by §5 screens) + the **delisting-reason** mislabel risk (a *known, documented* gate: `DATA_REPULL_DELISTING.md`). Reject the supervised "label-noise" machinery; the analogue is already tracked. |
| 12 | **Model evaluation** | ✅ DONE (sophisticated) | rliable (IQM/POI/CI/profiles), DSR/PBO/CSCV, FZ0/ES backtest, purged walk-forward + CPCV, cost sweep, TOST/severity. Among the strongest parts of the repo. |
| 13 | **Distribution drift** | ◑ REFRAME → 🟢 small ADD | Production input-drift monitoring is N/A. The *research* analogues already exist: **regime-conditional** analysis, the deliberate **temporal train/test split** (the test period IS a distribution shift — that's the test), OOD/contamination analysis. Optional report-only **train-vs-test distribution-distance diagnostic** is a cheap, honest add. |
| 14 | **Model deployment** | ❌ REJECT | This is a research experiment, **not a deployed system**. There is no serving endpoint. The only "deployment" analogue is the **frozen replay-archive** (results replay, never regenerate) — already the design. |
| 15 | **Monitoring & retraining** | ❌ REJECT | **No production model** to monitor or retrain. The analogues — reproducibility/provenance + the **literature novelty re-sweep** (`RELATED_WORK_WATCH.md`) — already exist. A retraining loop would contradict the frozen, pre-registered, single-shot design. |

## Net
**Already sophisticated** on collection / cleaning / leakage / baselines / evaluation. The **only genuinely-relevant
additions** are: (3) a consolidated **data-contract validator**, (6) explicit **leakage assertions** inside it, and
(13) an optional **train-vs-test drift diagnostic** (report-only). **Class imbalance, supervised label-error
machinery, model deployment, and monitoring/retraining are REJECTED** as supervised/production concepts that do
not map to a deterministic pre-registered RL experiment — adding them would be noise, not rigor. This round
implements the data-contract + leakage assertions (`src/data/validation.py`, `validate_panel`).

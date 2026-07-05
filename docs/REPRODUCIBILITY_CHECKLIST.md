# Reproducibility Checklist — `llm-reward-portfolio`

The NeurIPS / ML Reproducibility Checklist (Pineau et al., "Improving Reproducibility in Machine
Learning Research" — % VERIFY), answered against **this** repository. Each item cites the file that
substantiates the answer. **Results-dependent items are marked "TBD — populated after the campaign
run"**, since the campaign has not yet been executed (the pre-registration is not yet frozen:
`config/preregistration.yaml: frozen: false`, `freeze_hash: null`).

---

## 1. Models and algorithms

- **Clear description of the mathematical setting / algorithm.** Yes. Fixed RL agent =
  Stable-Baselines3 **SAC** (`src/agents/factory.py`, `HEADLINE_ALGO = "SAC"`); secondary critic =
  sb3-contrib **TQC**. The portfolio MDP (state / simplex action / proportional-turnover cost /
  walk-forward horizon) is specified in `config/environment.yaml` and `docs/environment_spec_v1.md`.
  The LLM reward-designer + Eureka loop are in `src/llm/loop.py`; the reward contract/sandbox in
  `src/reward/contract.py` + `src/sandbox/executor.py`.
- **Analysis of complexity / compute.** See item 6 below.
- **Link to downloadable source code, incl. dependencies.** Code is in this repository (MIT,
  `pyproject.toml`); release/DOI status in item 7.

## 2. Theoretical claims

- **Statement of the full set of assumptions.** Yes — `PREREGISTRATION.md` (frozen design record)
  states hypotheses H1–H4, the unit of inference (a reward function's OOS risk-adjusted performance),
  the contribution axis (feedback channel; agent fixed), and the pre-registered per-branch predictions.
- **Complete proofs / formal arguments.** The distributional-sufficiency theory spine lives in
  `paper/` (theory chapter); not a coding-reproducibility artifact.

## 3. Datasets

- **The data used.** A single survivorship-free **point-in-time Refinitiv/LSEG** US large-cap equity
  panel, `data/gold/returns_panel_univ5.parquet` (**5,406 × 963**), 2005-01-03 → 2026-06-30 (settled
  cutoff; ADR-051, R73); headline panel **univ5** (zero-fill, no fabricated delisting losses; the R44
  semantics carried forward), selected by the hash-bound `config/data.yaml: gold.suffix: univ5`.
  **univ3** (5,283 × 953, 2005–2025) is the frozen pre-Split-C reference — byte-diff verified: 0
  changed cells on the full overlap, +123 sessions, +10 new-member columns. VIX from FRED VIXCLS
  (refreshed to the cutoff); factors from the Kenneth French data library. See `config/data.yaml`,
  `PREREGISTRATION.md` §7, and the datasheet `docs/DATASHEET_v1.md` (Gebru et al. 2021 — % VERIFY).
- **Train / val / test splits (SPLIT C, ADR-044/R73).** **train 2005–2016** (agent learns + tail
  feedback measured), **val 2017–2019** (winner selection via reward-independent validation Deflated
  Sharpe; executed start 2017-03-30), **test 2020–2026H1** (sealed until final inference; executed
  start 2020-03-30). Inter-split purge = max(embargo 21, lookback 60) = **60 sessions** (López de
  Prado 2018; `config/data.yaml`, R18). Splits are disjoint + embargoed; the resolved integer windows
  are fail-loud asserted against `expected_windows.univ5 = [60,3021]/[3081,3775]/[3835,5406]`
  (`config/inference.yaml`, `run_campaign._assert_expected_windows`).
- **Data availability.** **Licensed and NOT redistributable** (Refinitiv/LSEG; `config/data.yaml:
  licensing: redistribution_prohibited`, `docs/DATA_ENTITLEMENTS`). The repo ships **SHA-256
  checksums + the acquisition pipeline (`data_pipeline/`) + a synthetic panel of identical shape**
  (`src/data/`), so an entitled party can reproduce byte-exact artifacts; others can run the full
  machinery on synthetic data. The 2026 extension is itself reproducible: journaled drivers
  `data_pipeline/scripts/{extend_universe_2026.py` (splice pull with a hard-fail overlap gate +
  enumerated allowlist), `refresh_fred_2026.py`, `build_univ5.py`, `purge_suffix.py}` (guarded vault
  cleanup); the vendor-drift incident + SPLICE rule are documented in `docs/DATASHEET_v1.md`
  §2026-07-02 and ADR-051.
- **Preprocessing.** Medallion pipeline with raw-layer immutability + lineage; Ince–Porter +
  split-artifact integrity screens (flag-only) on the research panel via
  `build_universe(screen=True)` → `univ3s` (byte-identical returns; screening evidence for the
  overlapping span — not re-materialised for univ5); delisting terminals recovered observed-terminal
  for all 333 dead names (`univ5s`, zero surcharges; ADR-051); delisting handling disclosed
  (`docs/DATASHEET_v1.md`). Analysis reads results **only** through `src/io/results.py`.

## 4. Code

- **Code with sufficient instructions to reproduce results.** Yes. Build + smoke gate in `README.md`;
  end-to-end campaign in `docs/CAMPAIGN_RUNBOOK.md` (`scripts/run_campaign.py` →
  `scripts/analyze_campaign.py`). Single source of truth for all parameters is `config/*.yaml` (code
  reads config, never hardcodes — `CLAUDE.md`).
- **Tests.** A behaviour-test suite (invariances / bounds / calibration + parallel≡serial
  byte-identical equivalence) under `tests/` (`make test`; README cites 611 passing on the light
  scientific stack — % VERIFY the live count at run time). Coverage floor `fail_under = 88`
  (`pyproject.toml`), property-based tests with a deterministic Hypothesis profile.

## 5. Experimental results & determinism

- **Specification of all training details (hyperparameters, how chosen).** Yes. Live agent kwargs are
  resolved by `src/agents/trainer.py::resolve_agent_kwargs` (NOT `config/algos.yaml`, which is a
  documentation template): `learning_rate=3e-4`, `batch_size=256`, `gamma=0.99`, `ent_coef="auto"`,
  `learning_starts=1000`, `buffer_size=train_steps_per_candidate` (50k campaign / 25k prototype;
  ADR-025). **Library defaults, identical across feedback arms** (audit A-1; runtime equivalence test
  `src/arms/factory.py`). PopArt value-target scale-norm + train-only `VecNormalize(norm_reward=False)`
  + TF32 applied uniformly across arms.
- **Number of runs / seeds.** **30 winner seeds `[0..29]`** (Amendment D2; Henderson 2018, Colas et
  al. ≥20), one seed per candidate during search (matched budget), winners re-run at 30 seeds —
  `config/campaign.yaml`, `config/preregistration.yaml`.
- **Measure of central tendency + variation.** rliable **IQM** + probability of improvement +
  stratified-bootstrap CIs; per-seed → paired stratified bootstrap over shared training seeds (R16);
  the inference carries the across-seed (training-RNG) variance (`PREREGISTRATION.md` §10).
- **Seed management.** `src/utils/seeding.py::set_global_seed` seeds Python `random`, NumPy,
  `PYTHONHASHSEED`, and (lazily) torch + cuDNN from a single run seed; the seed is recorded in every
  run artifact (`src/io/results.py`).
- **Determinism settings.** With `deterministic_torch=True` (training/campaign path):
  `torch.use_deterministic_algorithms(True, warn_only=True)`, `torch.backends.cudnn.deterministic =
  True`, `cudnn.benchmark = False`, and **`CUBLAS_WORKSPACE_CONFIG=":4096:8"` set before the first
  CUDA op** so deterministic cuBLAS matmul is used (`src/utils/seeding.py`).
  **Honest scope:** determinism is **statistical, not bitwise**, across CPU↔GPU / different-GPU /
  torch-release boundaries (documented in `seeding.py` and METHODS) — hence mean ± error bars over N
  seeds. **LLM calls are non-deterministic and are replayed from the archive, not regenerated**
  (audit C-2; `config/llm.yaml: archive: true`).
- **Frozen config + freeze hash.** The design is pinned by `scripts/freeze.py`, which SHA-256-hashes
  `config/preregistration.yaml`, asserts it agrees with `PREREGISTRATION.md`, and is wired into CI +
  pre-commit (`make freeze-check`). **Status: not yet frozen** (`frozen: false`, `freeze_hash: null`);
  the latest computed pre-freeze canonical hash is `d9204087…` (moved intentionally with the
  Split-C/univ5 rebuild — 3 bound configs + prereg changed; CHANGELOG `[2026-07-02c]`). Freezing is a
  user-gated step (`docs/CAMPAIGN_RUNBOOK.md`).
- **Statistical significance / multiple-comparison handling.** Headline H2 = two co-primary
  intersection–union tests (H2-RA Sharpe IUT + H2-Tail CVaR-5% IUT), each one-sided α=0.05, the
  conjunction being the correction (Berger 1982); PBO/CSCV primary overfitting guard; Deflated Sharpe
  secondary; BH FDR q=0.05 / Romano–Wolf reported as sensitivity over the frozen m=6 union; TOST vs
  SESOI=0.05 for the bankable null (`PREREGISTRATION.md` §10, `config/preregistration.yaml`).
- **Reported quantitative results.** **TBD — populated after the campaign run.** No campaign numbers
  exist; the prototype is directional-only and reports no number.

## 6. Compute

- **Description of compute infrastructure.** Development, Phase-0 gate, **and** the confirmatory campaign all run
  on the owned **RTX 4050** laptop (6 GB; n_gpu 2–3, TF32) — **laptop-only, no rented cloud / UCL Myriad** (**no
  cloud-compute budget**; a WSL2/GPU speed path was probed and rejected — ADR-040), seeds-on-winners, ~2–3 weeks. Validated build: **torch 2.6.0+cu124** (ADR-030/032).
- **Compute budget.** **No GPU-hour cap** (removed 2026-06-28 — it was never enforced by any code, and
  `auto_shutdown_on_complete` is a verified no-op). The GPU-hour figures in
  `docs/COMPUTE_AND_TRAINING_TIME.md` are **informational wall-clock/cost estimates only, not a limit**.
  `resume: true` (idempotent restart). Per-candidate budget **50,000** training steps (fixed, matched;
  `train_steps_per_candidate`). **Wall-clock TBD** until the campaign runs.

## 7. Code release & licensing

- **License.** MIT for the code (`pyproject.toml`, `CITATION.cff`); data licensed Refinitiv/LSEG,
  non-redistributable.
- **Release / archival.** A Zenodo DOI is reserved as a **commented placeholder** in `CITATION.cff`
  (`# doi: "10.5281/zenodo.XXXXXXX"  # TODO: populate after Zenodo archival`); repository URL TODO on
  public release. Citation metadata in `CITATION.cff` (CFF 1.2.0).

## 8. Dependencies & environment

- **Dependency pins.** Pinned in `pyproject.toml`: `numpy>=1.26,<2.0`, `pandas>=2.1,<3.0`,
  `scipy>=1.11`, `scikit-learn>=1.3`, `gymnasium>=0.29`, `stable-baselines3>=2.4,<2.9`,
  `sb3-contrib>=2.4,<2.9`, `torch>=2.6,<2.9` (validated 2.6.0+cu124), `anthropic>=0.69`,
  `tenacity>=8.2`, `statsmodels>=0.14`, `arch>=7.0` (tests-only oracle). Optional extras: `d3rlpy==2.8.1`
  (archived IQN-SAC cross-check), `data` (lseg-data, pyarrow, …), `dev` (pytest, ruff, mypy,
  hypothesis). Python `>=3.11,<3.13`.
- **Exact environment capture.** An env/pip snapshot with sorted, order-stable keys is hashed for
  provenance (`src/utils/` provenance + `docs/CODE_QUALITY_audit.md`); record the exact resolved torch
  build in `docs/DECISION_LOG.md` at campaign time.

---

### Summary status

| Area | Status |
|---|---|
| Code, configs, tests, seeding, determinism settings | Present and substantiated in-repo |
| Data pipeline + checksums + synthetic panel | Present; raw data licensed / not redistributable |
| Frozen pre-registration + freeze hash | Machinery present; **not yet frozen** (user-gated) |
| Quantitative results / wall-clock compute | **TBD — populated after the campaign run** |
| Zenodo DOI / public repo URL | Reserved as commented placeholders (TODO on release) |

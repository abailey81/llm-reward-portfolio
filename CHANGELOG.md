# Changelog

All notable changes to this repository. Format follows Keep a Changelog; this project is pre-versioned
research code, so entries are grouped by session date. Every entry cites its ADR where one exists.

## [2026-06-17] — Repository unification: one folder (engine ⊕ data) — Stage 1 (ADR-022)

### The headline
- **Two divergent repos are being merged into one project folder** under an absolute **no-loss/no-delete**
  rule: the audited *experimental engine* (was `dissertation_papers/llm-reward-portfolio`) is the structural
  base; the *data + hardened core* line (was `~/Downloads/llm-reward-portfolio`, this repo's prior identity)
  is being folded in. Staged + test-verified, never a big-bang (rationale + full plan in **ADR-022**).
- **Safety net first:** full backups of both repos at `~/Downloads/_merge_backup_2026-06-17/`
  (B 416M, A 513M, incl. `.git` + data). The source repo B is **retained untouched** until Stage 4.

### Stage 1 — folded in, non-breaking (DONE)
- **Real data + provenance copied and CHECKSUM-VERIFIED** — canonical panel `returns_panel_univ3.parquet`
  sha256 `f4edc86…` identical at source and destination; `data/{gold(54 parquets),clean,raw,staged,
  manifest}` now live in the unified repo; `data/manifest` carries checksums.txt + manifest.jsonl (874) +
  lineage.jsonl + invalidated.jsonl + journal.
- **Provenance & docs folded in:** `CHANGELOG.md`, `DECISIONS.md`, `RELATED_WORK_WATCH.md`, `reports/`,
  `runs/`, all of B's `docs/*` (DATASHEET, DATA_ENTITLEMENTS, REFERENCES, distributional_feedback_schema,
  environment_spec, …), `scripts/verify_inventory.py`.
- **Configs/prompts:** B-unique `eureka_loop.yaml` + `inference.yaml` added; the 3 clashing configs
  preserved as `config/{data,environment,llm}.B.yaml` (A's never clobbered); all B prompts added alongside
  A's (no filename clash) for Stage-2 reconciliation.
- **Engine integrity confirmed:** **148 tests pass, 0 failed** across 20 test files after the fold-in —
  A's audited science modules were not touched in Stage 1.

### Convergence decision (evidence-based) + interim state
- **B's flat science modules are the PRE-AUDIT line** (verified: B still ships `smoke_iqn_sac.py` — the
  IQN-SAC the audit rejected for SAC+TQC — and a `crossing_rate` neural-IQN diagnostic the preregistration
  dropped). So **A's audited science stays canonical as the live `src/`**; B's pre-audit science is **NOT
  merged** and is **preserved wholesale, not deleted** (Stage 4 folds all of B into `archive/
  pre_merge_repo_B/`). Audit-neutral B engineering gains (resource-limited sandbox isolation) are logged as
  candidate future ports under their own ADR — never blind-merged.
- **B's data-acquisition layer is self-contained** (imports only within `src/data/`), so Stage 3 integrates
  it cleanly into the package and wires a real-gold loader for the audited env.
- Interim only: `config/*.B.yaml` and the dual prompt set are reconciled in Stage 4. PREREGISTRATION stays
  A-canonical and **untouched** — the frozen design is unchanged by the merge.

### Stage 3 — acquisition pipeline relocated + B preserved (DONE; env↔data loader flagged)
- **`data_pipeline/`** created: B's Refinitiv→gold acquisition stack relocated **verbatim** (its dependency
  closure `{config.py, features.py, data/}` + B's `config/*.yaml` + a README). Imports are intact (B's
  `config.py` resolves `CONFIG_DIR` relative to itself) — **smoke-imported clean** in A's venv (which already
  has `lseg-data`, `pandas-market-calendars`). It is decoupled from the live engine: the gold panel is frozen,
  so the pipeline is provenance/reproducibility only (re-running needs live Refinitiv creds).
- **`archive/pre_merge_repo_B/`** created (nothing lost): B's pre-audit flat science modules (`src_flat/`,
  with a successor-map README) + B's root docs (`root_docs/`: CLAUDE/README/PREREGISTRATION/Makefile/
  pyproject/requirements). Full `.tgz` of B (incl. `.git`+data) remains at `~/Downloads/_merge_backup_2026-06-17/`.
- **Flagged for careful follow-up (NOT improvised):** the live env↔real-data **loader** (`returns_panel_univ3`
  → audited `Panel`) must decide **intra-window delisting handling** — e.g. Wachovia `WB.N^A09` is in the
  dev-2005 top-30 and dies in 2009 (NaNs after delisting), while the env's `Panel` requires finite returns.
  That is a preregistration/`environment_spec_v1` design decision, deferred to align with the frozen design.

## [2026-06-12] — Entitlement landed: PIT membership built; universe pulls running

### The headline
- **A1 PIT membership EXISTS and validates** (`data/staged/pit_membership.parquet`): 252 months ×
  499–506 names, union **953 RICs** (2005–2025) incl. **333 dead ^RICs**; Lehman in 2005-01/out 2008-10
  (leaver event 2008-09-17, `LEH.N^I08`), FactSet/Airbnb absent 2005, Tesla out 2019/in 2021.
  Lineage to the three raw event pulls; validation gates recorded in provenance.

### Two silent vendor traps caught by CONTENT validation (shape checks false-passed both)
1. **Membership snapshots return the CURRENT chain** on this route — `TR.IndexConstituentRIC`+SDate,
   the dated chain `0#.SPX(date)`, and field-embedded SDate all silently survivorship-biased (FDS/ODFL/
   ABNB "in 2005"). 98 `rf_members_*` artifacts INVALIDATED (`data/manifest/invalidated.jsonl`, now
   git-tracked); method switched to **reverse event replay** through `TR.IndexJLConstituent*` streams
   (3 requests for 21 years), gated by count-band [495,510] + known-truth checks (**ADR-020**).
2. **`TR.TotalReturn` via get_history returns empty/NaN frames** — 39 `rf_tr_*` artifacts INVALIDATED;
   corrected to **datagrid long form** `Frq=D` (content-verified: Lehman daily series through
   2008-09-12, worst day −44.9%, percent units) and `Frq=M` for market cap; price/bid/ask/volume via
   no-fields `get_history` (TRDPRC_1/BID/ASK/ACVOL_UNS), split per-field for lossless CSV.
- Probes P2/P3 rewritten to content-validated JL queries (assert known dead-RIC leavers), and the
  mnemonic checks of 06-12 morning now read values, not shapes — the trap class is test-closed.

### Added
- `src/data/build_universe.py` + `build-universe` CLI/make target: long→wide assembler
  (percent→decimal, dedup-keep-last, XNYS align, fail-loud on missing pulls) feeding the existing
  `panel.build_gold` with membership+mcap → D2 mcap panel, D3 top-30 per window, PIT D1/D4/D6 (`_univ`).
- Live mnemonic confirmations into config (`TR.CompanyMarketCap`, `TR.BidPrice/AskPrice`, `TR.Volume`,
  TRBC-on-dead-RICs, `.SPXTR`); `.VIX` NOT licensed (CBOE) → FRED VIXCLS stays primary;
  `TR.InstrumentDelistedDate` often null → delist dates derive from ^MYY suffix + last trade.
- Probe evidence serializer fix (Timestamp keys from live frames).

### Pulls (journaled `universe_refinitiv`, resumable)
- Frozen: `rf_chain_current`, `rf_jl_joiners` (523 events), `rf_jl_leavers` (520 events);
  daily-TR chunks streaming (429 total: 39 name-chunks × 11 two-year spans), then 39 monthly-mcap
  chunks, 39 OHLC/bid/ask/volume chunks, delisting/sector metadata, `.SPXTR` benchmark.

### Integrity
- PREREGISTRATION.md + prompts/ untouched; `lambda_frozen` null; invalidations are append-only
  declarations (write-once artifacts remain on disk, nothing consumes them); suite 121 passed + 1 skip.

## [2026-06-10 — data requirements & inventory session]

### Added
- `reports/data_requirements_and_inventory.md` — canonical data bill-of-materials (A1–D6 matrix),
  fully verified physical inventory (39/39 checksums re-hashed PASS, 0 orphans, 0 mutations), D5
  byte-match vs PREREG §6, gap summary with per-item unlock conditions + closing commands, quarantine
  status, and the completeness line ("5 of 14 satisfied; remaining unlock on Refinitiv/LSEG entitlement").
- `config/data.yaml: universe_pull` — A1–A5 acquisition bill-of-materials, citation-annotated, VERIFY
  flags on unconfirmed mnemonics (ADR-019).
- `src/data/pull_universe.py` — header-tolerant parsers (membership / delisting / panel) + journaled-engine
  orchestrator; `pull-universe` CLI subcommand (dry-run default, `--live` when entitled); `make pull-universe`.
- `tests/test_pull_universe.py` — 5 parser/orchestrator tests on synthetic fixtures (no network).
- `DECISIONS.md` ADR-019 (A1–A5 wiring; identification untouched) + ADR-017/018 reserved markers.

### Verified (no change to data)
- Re-probed entitlements: platform session did not open this run (P0 BLOCKED `OpenState.Closed`, vs PASS
  on 10 Jun — short-lived RDP token); data-access conclusion unchanged (no non-empty scope set ever);
  DSWS still `ZLDU178` ClientApi-not-entitled. Report regenerated.
- Write-once integrity: every layer re-hashed, all PASS, no orphan/mutation.

### Unchanged (integrity)
- PREREGISTRATION.md + prompts/ byte-untouched; lambda_frozen null; no data re-pulled; no new dependency;
  no live Refinitiv pull beyond the probe. Test suite 118 passed + 1 platform-skip; ruff clean.

## [2026-06-10 — close-out session] — Pre-Friday plan completion (sections A–E only)

### Added
- `docs/outbox/availability_reply_ramin.md` — copy-paste-ready Thu/Fri availability reply (two bracketed
  slot placeholders, group-format preference, one-pager closing line). DEADLINE: TODAY. Not sent.
- `docs/outbox/escalation_lseg.md` — finalized LSEG escalation (DSWS ClientApi enablement for account
  ZLDU178; RDP data scopes; WRDS/CRSP question; recipient guidance). Verbatim from the entitlement
  report. Not sent.
- `docs/staging/PREREGISTRATION_v1.0_FINAL.md` — freeze candidate: current draft + exactly three folded
  changes (§3 λ tie-break sentence; §4a naming the H4 reward family per config; §10 hash cell re-pointed
  to ADR-005). Diff-verified: 19 lines, all accounted for. Live PREREGISTRATION.md byte-untouched.
- `docs/staging/FREEZE_RUNBOOK.md` — ordered T4 commands + Step-0 decision list: (1) single-shot arm
  count 80 (PREREG §4) vs 240 (config) — recommend "240 = 80 × R=3"; (2) "fixed hyperparameters from
  config/" but no algo-hyperparameter file exists yet — add config/algos.yaml or re-word before freezing.
- `reports/meeting_script.md` — 2-minute spoken version ending on the ICAIF 2-Aug question.
- `reports/session_report_2026-06-10_close.md` — this session's stage-by-stage report incl. 4090 runbook.

### Changed
- `reports/research_brief_v1.md` — live-status block added (5,282×35 panel marked PROVISIONAL pending
  PIT; kurtosis 49.9 / Hill 2.1–3.6 headline; entitlement one-liner; freeze-staged-Friday line).
  427 words — one page.
- `docs/evidence/entitlement_report.md` + probes.json regenerated by a fresh live probe run
  (REFINITIV_APP_KEY present in .env → probe executed per plan): outcomes UNCHANGED — token still
  carries zero scopes (new EDP-API key not yet minted); DSWS still "ClientApi not entitled" for ZLDU178.
  Checklist statuses remain accurate as-is.

### Explicitly NOT done (per session constraints)
- Nothing sent, frozen, or signed; PREREGISTRATION.md, prompts/, scope-lock list untouched
  (byte-verified); lambda_frozen still null; no new dependencies; no week-15 work, no training,
  no new pipeline stages. `make smoke`/`make lock` remain 4090 actions (runbook in the session report).

## [2026-06-10] — Session: W15 build-out + research-grade data platform

### Added — research engine (week-plan W15 items)
- `src/features.py` — leakage-safe cash-row features [vol20, vol20/vol60, vix]: rolling sample std of
  the equal-weight market proxy, shift(1)-lagged, VIX/100 scaling, NaN warm-up; truncation- and
  future-perturbation-invariance tested (ADR-007).
- `src/portfolio_env.py` — optional `cash_features` observation block with fail-loud non-finite guard;
  observation dim +3 when supplied; accounting unchanged (ADR-007).
- `src/rewards_baselines.py` — completed the six-reward canon: `SharpeEpisodic` (expanding-Welford SR
  increment, telescopes to episode Sharpe), `CVaRPenalisedMean` (Rockafellar–Uryasev shortfall),
  `DrawdownPenalised` (running-peak level penalty), `TurnoverPenalised` (extra anti-churn shaping);
  `BASELINE_FACTORIES` registry test-enforced against `config/eureka_loop.yaml` (ADR-009).
- `src/reward_family.py` — six-term parameterised reward family for the H4 random/BayesOpt arms; vertices
  recover the hand-designed canon; seeded uniform sampler over config-frozen ranges; shared
  `params_to_reward` constructor; content-addressed `params_id` (ADR-010).
- `src/calibrate_lambda.py` — PREREG §3 λ-selection machinery: per-λ separation accuracy of known-good vs
  known-degenerate rewards; tie-breaks = across-seed stability, then smallest λ; full table returned for
  the freezing ADR; never writes config (ADR-010).
- `src/candidate_archive.py` — verbatim append-only candidate archive (source + prompt + model snapshot +
  temperature + outcome; content-addressed; collision raises) per R6 (ADR-008).
- `src/dry_run_random_search.py` — TrialLedger end-to-end dry run on labelled THROWAWAY candidates
  (synthetic returns, untrained fixed-logit policies, explicit throwaway λ): 10 candidates → ledger N=10 →
  DSR 0.577 / SR0 +0.069 → PBO 0.094 over 12,870 CSCV splits; sidecar to `runs/dry_run/` (ADR-010).
- `src/reward_contract.py` — `probe_contexts()` extracted as the single source of the synthetic probe
  battery (in-process validator and sandbox share it).

### Added — data platform (`src/data/`, 13 stages; ADR-012)
- `vault.py` — write-once layered storage (raw/staged/clean/gold), SHA-256 manifest (`manifest.jsonl` +
  legacy `checksums.txt`), provenance sidecars, checksum-verified reads (unmanifested reads refused),
  lineage graph (`record_lineage`/`lineage_chain`).
- `acquire.py` — rate governor, exponential backoff with full jitter, per-chunk resumable `PullJournal`,
  ticker/date chunkers, minimal `.env` loader (no new dependency; never logs values), provenance capture
  with library versions, vendor fetchers (Refinitiv platform/desktop, DSWS `DataClient`, yfinance
  OHLCV+actions non-adjusted, FRED, Ken French), `EntitlementError` degradation type,
  `capture_field_definitions` (RI day-count = explicit MANUAL-CONFIRMATION record).
- `probes.py` — automated DATA_ENTITLEMENTS checklist (chain, PIT 2018/2010, DSWS list, GE exit window,
  dead-RIC `LEH.N^I08`, field definitions) → `docs/evidence/entitlement_report.md` + `probes.json`;
  escalation email auto-rendered when the pre-2016 path fails both vendors.
- `security_master.py` — RIC↔ticker symbology with dead-RIC `^`-suffix parsing (month letters A–L),
  yfinance symbol mapping (share-class dashes), curated overrides (GOOG/GOOGL 2014, META/FB 2022),
  `resolve()` that raises on unknown/ambiguous symbols.
- `validate.py` — minimal schema core (dtype/nullability/bounds/monotone-unique tz-naive index), explicit
  coercion (never invents values), XNYS sessions via exchange-calendars with explicit `calendar_start`
  (default ~20y lookback would clip 2005), calendar alignment with off-session reporting, exact-vs-conflict
  duplicate detection, missing-data engine (holiday/pre-IPO/post-delisting/interior taxonomy, full
  conservation counting, ZERO interpolation).
- `integrity.py` — RI internal-consistency flags, unadjusted-split signatures (−50%/−66.7% without vendor
  record), stale-price runs, zero-volume flags, Ince–Porter screens (daily adaptation, documented),
  cross-sectional extreme-day classification with SELF-EXCLUDED peer context (a lone collapse cannot
  certify itself via the EW average), reason-coded quarantine assembly — REAL_TAIL rows are never
  quarantined; no function mutates values.
- `membership.py` — PIT membership normalize/stitch with 2016 overlap cross-validation (Jaccard table),
  joiners/leavers audit, Shumway corrections with per-application audit log and citation (input never
  mutated), `members_asof`/`top30_at` strictly-prior selection (PIT leakage assertions in tests).
- `reconcile_full.py` — two-vendor reconciliation with discrepancy clustering (ex-div / split day /
  index-exit window / unexplained→quarantine), per-field vendor-authority merge (column-wise only;
  cell-wise blending would fabricate an unpublished series).
- `panel.py` — as-of join framework (`AsOfFeature` declares availability lag; the only sanctioned join),
  gold construction (returns panel, cash features via `src/features.py`, EW market proxy, top-30 per
  window when membership+mcap exist), `materialize_splits` = PREREG §6 exact (dev train/val, 8
  walk-forward folds 2018–2025, 21-trading-day embargo at every boundary, CPCV 16 purged blocks) as
  explicit session lists; parquet artifacts with lineage.
- `eda.py` — ADF/KPSS, moments, Hill left-tail estimator, |r|-ACF + ARCH-LM, rolling mean pairwise
  correlation, cross-sectional dispersion, drawdown anatomy, naive reconstitution turnover; every figure
  captioned with the design choice it motivates; headless matplotlib.
- `quality.py` — weighted per-series quality score, coverage matrix, scoreboard, lineage map renderer,
  Gebru et al. datasheet generator (auto-filled from manifests, ⟨TBD⟩ when empty), data-chapter seed
  paragraphs (one per stage, real numbers injected when available).
- `cli.py` — `python -m src.data.cli {probe,pull,build,validate,reconcile,eda,status}`; per-stage run
  sidecars (config hashes, wall-clock, counts); graceful vendor degradation recorded as explicit SKIP.
- Makefile targets: `data-probe data-pull data-build data-validate data-reconcile data-eda data-status`.

### Added — tests (68 → 113; all offline, synthetic fixtures in tmp dirs only)
- `tests/conftest.py` — `data_root` fixture redirects every platform module's ROOT to tmp.
- `tests/test_features.py` — truncation/future-perturbation invariance, lagged VIX, zero-variance ratio,
  env integration (dims, accounting equality, NaN rejection).
- `tests/test_sandbox.py` — 15-case static denial corpus (multi-import bypass, np.load/.lib/DataSource,
  dunders, eval/getattr/open, class/decorator/yield/global, oversized, missing compute_reward, syntax),
  numpy-idiom acceptance incl. real `import numpy as np` execution, malformed-runtime corpus (wrong arity,
  NaN, component-name instability), infinite-loop kill, Linux-gated memory bomb, result-validation bounds.
- `tests/test_rewards_baselines.py`, `test_reward_family.py`, `test_calibrate_lambda.py`,
  `test_regimes.py` (truncation invariance proves filtering-not-smoothing), `test_candidate_archive.py`,
  `test_dry_run.py`.
- `tests/test_data_vault.py` (write-once, tamper detection, lineage chains), `test_data_acquire.py`
  (governor spacing, backoff, journal resume idempotence, env loader), `test_data_validate.py` (schema,
  XNYS MLK-day alignment, conflicts, missing conservation), `test_data_integrity.py` (split recorded-vs-
  suspect, IP screens, REAL_TAIL preservation vs lone-crash quarantine), `test_data_membership.py`
  (splice/overlap, Shumway log + non-mutation, strictly-PIT top-30), `test_data_panel.py` (as-of lag,
  PREREG-§6 embargo-exact splits, gold leakage assertion, golden determinism), `test_data_security_master.py`,
  `test_data_property.py` (hypothesis: softmax/drift distributions, missing-cell conservation, chunk
  partitions, quality bounds), `test_data_cli_and_quality.py` (offline probe report, status, reconciliation
  clustering, authority merge, datasheet honesty).

### Added — configuration
- `config/environment.yaml`: `state.vol_short_window/vol_long_window/vix_scale`; `reward_defaults` for
  cvar_penalised_mean / drawdown_penalised / turnover_penalised (scale-parity comments).
- `config/eureka_loop.yaml`: `reward_family` search space (weight ranges, α choices, window choices).
- `config/data.yaml`: `platform` block (layers, manifests, lineage, journal, quarantine, evidence, runs,
  XNYS calendar + explicit `calendar_start`, chunking, rate limits, outlier taxonomy thresholds,
  vendor-authority rules, quality weights).
- `config/llm.yaml`: PIN_ME resolved — primary `claude-sonnet-4-6` @ $3/$15 per MTok (verified on the
  official models overview 2026-06-10; dateless 4.6-generation ids are documented pinned snapshots);
  open-weights companion `deepseek-ai/DeepSeek-V3-0324` (dated HF checkpoint) (ADR-016).

### Added — governance & docs
- Git repository initialized (the project was previously inside the home-directory repo); two commits:
  `75a697c` scaffold + W15 build-out, `0af2ee9` data platform.
- `DECISIONS.md`: ADR-007 … ADR-016 appended (features, sandbox+archiver, baselines, family+λ-rule,
  filtered HMM, platform architecture, dependencies, build-box environment, entitlement outcome,
  LLM pin).
- `docs/evidence/entitlement_report.md` + `entitlement_probes.json` (live probe evidence).
- `docs/DATASHEET_v1.md`, `reports/eda_v1.md` + `reports/figures/*`, `reports/data_quality_scoreboard.md`,
  `reports/data_chapter_seeds.md`, `docs/evidence/lineage_map.md` — all generated from REAL pulled data.
- `CHANGELOG.md` (this file) and `reports/session_report_2026-06-10.md`.

### Changed
- `src/sandbox.py` — full hardening rewrite (ADR-008): AST static gate replaces the bypassable string
  check; per-resource best-effort rlimits clamped to current hard limits (fixes pre-existing macOS
  `RLIMIT_AS` crash that failed `test_benign_candidate_executes`); minimal subprocess env (no inherited
  secrets, BLAS threads pinned); runtime `__import__` restricted to numpy (previously `None`, which broke
  the mandated `import numpy as np`); parent-side contract validation incl. component-name stability.
- `src/regimes.py` — explicit scaled forward recursion over public fitted parameters replaces private
  hmmlearn APIs; filtering proven causal by truncation invariance (ADR-011).
- `src/feedback_schema.py` — `empirical_cvar` now self-enforces ascending input (R5 made structural);
  `build_feedback` alpha grid defaults from config instead of a duplicated literal.
- `src/data/cli.py` — Ince–Porter price screens fed RAW close instead of adjusted close (the $1 threshold
  is about actual traded microstructure; split-adjustment retroactively drags early AAPL below $1). The
  v1 pilot quarantine (13 rows) was produced under adjusted prices — values were never mutated and
  clean/gold are unaffected; the corrected screens apply from the next build.
- `src/data/acquire.py` — FRED keyless path: date-chunked public fredgraph CSV (full-range requests 504 at
  FRED's gateway; pandas-datareader's combined request times out identically).
- `src/pull_pilot.py`, legacy tests — semicolon statements split; `make lint` now actually passes
  (pre-existing ruff failures fixed forward, no test weakened).
- `Makefile` — data-platform targets appended.
- `requirements.txt` — platform dependencies appended with ADR-013 reference (refinitiv-data, DatastreamPy,
  pyarrow, exchange-calendars, statsmodels, hypothesis, tabulate).
- `README.md`, `docs/environment_spec_v1.md`, `docs/DATA_ENTITLEMENTS.md`, `docs/week_plan_June15.md` —
  status updates to match code as built.
- `.venv` rebuilt on Python 3.12 (3.13 has no torch wheels; d3rlpy 2.8 needs torch≥2.5 which has no
  Intel-mac wheels at all → RL stack remains a 4090 install per ADR-002/ADR-014).

### Live runs (real data only — R4; nothing synthetic enters `data/`)
- Entitlement probes: Refinitiv platform session AUTHENTICATES (credentials recovered, at user direction,
  from `~/Downloads/ifte0005_phase1/.env` into gitignored `.env`; values never displayed) but carries an
  EMPTY RDP scope set — no datagrid, no historical-pricing; Workspace desktop path needs interactive
  login; DSWS connection refused (separate entitlement). Escalation email rendered (ADR-015).
- Pulls frozen to the raw vault: yfinance OHLCV+dividends+splits 2005–2025 (5 field artifacts, 5,282
  sessions × 5 pilot names), FRED {VIXCLS, DGS3MO, DGS10, T10Y2Y} (5,478 rows), Ken French daily factors
  + momentum (5,365 rows each). 8 raw artifacts, 42,618 rows, all SHA-256-manifested with provenance.
- Pipeline: staged (XNYS-aligned, validated, missing-classified) → integrity (13-row quarantine queue:
  6 sub-dollar flags + 7 Citi-2009 extreme-day reviews; tails preserved) → clean 5,282×5 (authority:
  yfinance fallback, decision recorded) → gold (returns panel, cash features, market proxy, PREREG-§6
  splits — dev val 734 post-embargo sessions starting 2015-02-03, 8 walk-forward folds) → EDA (excess kurtosis 5.75–49.9,
  Hill α 2.18–3.48 — the fat-tail evidence behind the CVaR fitness) → quality scoreboard + datasheet +
  lineage map. Every stage left a run sidecar under `runs/data/`.

### Live runs — second wave (universe-scale shadow + screen correction)
- Shadow30 pull: 30 additional real large-caps via yfinance (journaled, 2 chunks of 25; union with the
  pilot = 35 names) — explicitly a PIPELINE-SCALE proof, **not** the research universe (PIT top-30
  selection awaits entitled membership data). 18 raw artifacts total, all checksum-verified (0 failures).
- **Vendor subtlety discovered and fixed at scale**: yfinance `Close` is split-adjusted even with
  `auto_adjust=False` (NVDA's 2005 close reads $0.196 vs ~$23.5 actually traded). Added
  `integrity.reconstruct_unadjusted_close` (close × ∏ future split ratios; unit test pins the exact
  inversion) and routed the Ince–Porter $1 screen through reconstructed traded prices. Effect at scale:
  4,274 phantom sub-dollar flags → **0**; quarantine_v2 holds exactly the 49 genuine extreme-day reviews;
  34 REAL_TAIL classifications preserved.
- v2 build: clean 5,282 × 35; missing engine: 184,870 cells, 177,269 observed, 7,601 pre-IPO masked
  (TSLA/META/ABBV/AVGO… — taxonomy conservation hypothesis-tested), 0 interior gaps; EDA refreshed across
  35 names (Hill α 2.14–3.59 — uniformly fat tails). v1 `_pilot`/`_shadow30` artifacts remain manifested
  (write-once); v2 supersedes for analysis.

### Live runs — third wave (app-free Refinitiv access characterized)
- Added probe **P8 "RDP scope census"** (search/news/pricing families): token carries ZERO scopes for
  EVERY product family → cause narrowed to app-key permissions vs seat licence; BLOCKED status carries the
  app-free fix (web App Key Generator, "EDP API" box, new key in `.env`). Fixed a status-flip bug my P8
  insertion introduced (P7 MANUAL flag had moved onto P8).
- **DSWS upgraded from "unreachable" to "authenticates, service flag missing"**: probe P4 now returns
  `User not entitled to ClientApi service` — credentials are valid Datastream credentials; escalation email
  sharpened to a one-line enablement request (+ RDP scope ask). Checklist row 4 upgraded ❌→🟡.
- No machine-account credentials exist on the laptop (targeted LSEG_*/MACHINE_ID name-scan: zero hits).

### Deliberately NOT done (scope/governance)
- PREREGISTRATION.md, prompts/, and the R2 scope-lock list: UNTOUCHED.
- `lambda_frozen` remains null; the freeze (T4) and supervisor sign-off remain the author's actions.
- No Eureka-loop orchestrator / LLM client yet (post-freeze work; provider now pinned).
- No optuna (BayesOpt arm later, own ADR). No paper-trading, no scope-locked items.

## [2026-06-10] — Initial scaffold (pre-session baseline, commit 75a697c)
- Feedback schema, stats inference (PSR/DSR/MinTRL/PBO/TrialLedger), fitness, env core accounting,
  reward contract, prompts v0, configs, docs, 19-test suite (ADR-001…006).

## [2026-06-12 — completion wave] — Universe data layer COMPLETE (ADR-021)
- A2–A5 pulls finished: journal 653+ chunks frozen / 0 failed; raw vault 788+ artifacts, 5.86M+ rows.
- Third silent-form catch: `TR.TotalReturn` via get_history is empty on this route → datagrid long
  Frq=D (39 junk artifacts invalidated); mnemonic checks now read VALUES.
- Acquisition PARALLELISED on user request: thread-safe launch governor (global requests_per_minute
  respected exactly), 6 workers overlapping response latency; vault/journal lock-serialised; exact
  resume under concurrency (tested).
- `selection_buffer_months`: membership+caps acquired before window.start → dev-2005 top-30 selects on
  strictly-prior Dec-2004 data. Span-stamped artifact versioning fixed a write-once collision.
- **Research panel built (suffix _univ3, canonical):** clean 5,283×953; missing engine 5.03M cells /
  373k pre-IPO / 957k post-delisting / 3,155 interior (0.06%); top-30 at all 9 window starts
  historically exact (dev-2005: GE/XOM/MSFT/C/WMT/PFE/BAC/JNJ; 2019: MSFT>AAPL); two-vendor
  reconciliation median corr 0.99994 (35 names; 390 breaches clustered to ex-div/split);
  dev-30 EDA: excess kurtosis WB 89.4 / AIG 76.8 / C 49.8 — GFC tails inside the search window.
- D1–D6 all satisfied on entitled PIT data. _univ/_univ2 superseded (manifested, write-once).

# DECISIONS.md — Architecture Decision Records (append-only)

Every locked choice gets ~5 lines: date · decision · alternatives · reason · consequences.
Claude Code: read this file at session start; append, never rewrite history.

---

## ADR-001 — Repository structure & config-driven discipline (2026-06-10)
**Decision.** Flat `src/` modules + `config/*.yaml` holding every parameter, citation-annotated; no magic
numbers in code. Strategy docs live in `docs/`, frozen design in `PREREGISTRATION.md`.
**Alternatives.** Python package with setup.py entry points; parameters in code constants.
**Reason.** The dissertation must report every parameter; config-as-single-source makes the methodology
chapter a near-export of `config/` and prevents silent drift between code and prose.
**Consequences.** `src/config.py` is the only sanctioned parameter access path.

## ADR-002 — Dependency policy (2026-06-10)
**Decision.** `requirements.txt` carries deliberate minimum bounds; exact pins captured to
`requirements.lock` on the local machine via `make lock`. New/upgraded dependencies require an ADR.
**Alternatives.** Fully pinned requirements in-repo now.
**Reason.** Build machine ≠ experiment machine (RTX 4090 / Myriad); CUDA wheels must be locked where they run.
**Consequences.** CI-grade reproducibility starts the day `requirements.lock` is committed from the 4090.

## ADR-003 — d3rlpy 2.8.1 IQN-inside-SAC: API VERIFIED against source (2026-06-10)
**Decision.** Pin d3rlpy >=2.8,<3. Use
`SACConfig(q_func_factory=IQNQFunctionFactory(n_quantiles=64, n_greedy_quantiles=32, embed_size=64)).create(device=...)`.
**Evidence (read from the 2.8.1 wheel source, `d3rlpy/models/q_functions.py`):**
`IQNQFunctionFactory` dataclass fields `n_quantiles: int = 64`, `n_greedy_quantiles: int = 32`,
`embed_size: int = 64`; **`create_continuous()` exists** returning `ContinuousIQNQFunction` +
`ContinuousIQNQFunctionForwarder` → IQN works with continuous-control SAC, which is the load-bearing fact
for this project. String alias `"iqn"` registered. `SACConfig` exposes `q_func_factory` plus
{actor,critic,temp}_learning_rate=3e-4, batch_size=256, gamma=0.99, tau=0.005, n_critics=2,
initial_temperature=1.0.
**Consequences.** "Missing piece #1" from the research harvest is closed; `src/smoke_iqn_sac.py` is written
against this exact API and only needs a local GPU run for the proof-of-life log. Fallback if runtime quirks
appear: `QRQFunctionFactory` (same file) — RQ2 needs *a* distributional critic; IQN preferred, not load-bearing by name.

## ADR-004 — Search on a single development split; evaluation on frozen winners (2026-06-10)
**Decision.** The reward search (all arms) runs ONLY on dev = train 2005–2014 / val 2015–2017. Winners are
frozen as code, then evaluated walk-forward 2018–2025 (+ CPCV view). Restarts R=3 (Eureka used 5).
**Alternatives.** Re-running the LLM search inside every walk-forward window.
**Reason.** Per-window search multiplies the trial count ~8×, explodes LLM+GPU budget, and turns the
walk-forward into part of the selection procedure (uncontrollable multiplicity). Dev-split search keeps the
DSR's N honest and the evaluation windows genuinely out-of-sample. GFC-in-dev forces crisis exposure during
search. R=3 bounds compute to the June–August window; the cost is wider restart-variance bands, reported.
**Consequences.** Evaluation-period results are interpretable as deployment of a frozen artefact.

## ADR-005 — Pre-registration freeze (PENDING — complete on 12 June 2026)
**Decision.** Commit `PREREGISTRATION.md` v1.0; paste hash here; inform supervisor.
**Freeze hash.** ⟨run `make freeze-design` after committing and paste output⟩
**λ frozen value.** ⟨after §3 calibration procedure; new ADR⟩

## ADR-006 — Initial build verified (2026-06-10)
**Decision.** Ship the scaffold with the test suite as the commit gate.
**Evidence.** 19/19 pytest green at build time (feedback schema sorting/CVaR monotonicity; DSR reduces to
PSR at N=1; PBO ≈ 0.5 on noise / ≤0.1 with a dominant strategy, C(8,4)=70; fitness fails loudly while λ
unfrozen; env wealth identity to 1e-10 incl. cost monotonicity; sandbox executes benign candidates and
blocks non-numpy imports). All YAML configs parse; all modules byte-compile.
**Consequences.** `make test` green is the definition of "working tree" from day one; smoke test (4090),
pilot pulls (entitlements), and reconciliation are the three local runs that complete the week's plan.

## ADR-007 — Environment cash-row features implemented (2026-06-10)
**Decision.** `src/features.py` builds the Sood cash-row tail [vol20, vol20/vol60, vix]: rolling SAMPLE
std (ddof=1) of the equal-weight universe return (explicit `market_returns` override accepted), ratio
neutral-1.0 under zero variance, VIX scaled 1/100; ALL columns shift(1) so row t holds info ≤ t−1; warm-up
rows NaN and `PortfolioEnv` REJECTS non-finite features on decision rows. Windows/scale in
`config/environment.yaml: state`.
**Alternatives.** Index-series vol (extra data dependency now); z-scored features (full-sample normalisation
violates R3); silent NaN-fill (violates R4 spirit).
**Reason.** Closes the env TODO with leakage proven by truncation- and future-perturbation-invariance tests
(`tests/test_features.py`); EW proxy is deterministic from the env's own returns.
**Consequences.** Spec updated (docs/environment_spec_v1.md); observation appends 3 dims when supplied;
RewardContext/prompt contract UNCHANGED (features are agent state, not reward inputs).

## ADR-008 — Sandbox hardened + candidate archiver (2026-06-10)
**Decision.** `src/sandbox.py`: AST static gate (numpy-only imports incl. multi-import bypass; dunder
names/attrs; exec/eval/open/getattr-class escapes; numpy file/FFI surface np.load/save/fromfile/lib/
DataSource/ctypeslib; no classes/decorators/async/yield/global; compute_reward required; 50KB cap) →
`python -I` in tempdir with MINIMAL env (no inherited secrets; BLAS threads pinned) → per-resource
best-effort rlimits clamped to current hard limits (fixes the macOS RLIMIT_AS crash; Linux/4090 enforces
AS/CPU/NOFILE/FSIZE/NPROC) → whitelisted builtins with `__import__` restricted to numpy (the system prompt
mandates `import numpy as np` — it must WORK) → parent-side `validate_sandbox_results` (finite/bounded,
component-name stability). `src/candidate_archive.py`: verbatim append-only archive (source+prompt+
snapshot+temperature+outcome, content-addressed, FileExistsError on collision) per R6.
**Alternatives.** seccomp/containers (non-portable to the 4090 workflow now); string-based import check
(bypassable: `import numpy as np, os` — test-proven).
**Reason.** Week-plan Tuesday block; R6 requires never exec'ing candidates in-process and archiving all.
**Consequences.** Denial corpus in tests/test_sandbox.py (15 static rejects + runtime paths); memory-bomb
test active on Linux only (Darwin AS limit is best-effort).

## ADR-009 — Baseline reward canon completed (2026-06-10)
**Decision.** `rewards_baselines.py` now implements all six registered names: + SharpeEpisodic
(expanding-Welford SR increment; telescopes to episode Sharpe; Moody et al. 1998 objective),
CVaRPenalisedMean (rolling empirical CVaR shortfall; Rockafellar & Uryasev 2000), DrawdownPenalised
(level penalty on running-peak drawdown), TurnoverPenalised (extra shaping beyond realised cost;
DeMiguel et al. 2009 convention). Parameters in `config/environment.yaml: reward_defaults` (return-scale
parity comments); registry `BASELINE_FACTORIES` ↔ config list is test-enforced.
**Alternatives.** Drawdown-increment penalty (telescopes differently; level form keeps below-high-water
pressure — documented in docstring).
**Reason.** Week-plan Wednesday block; baseline SET unchanged from pre-registration (no R1 trigger).
**Consequences.** All six pass the probe battery; semantic tests pin each definition.

## ADR-010 — H4 parameterised reward family + λ-rule operationalised (2026-06-10)
**Decision.** `src/reward_family.py`: six-term linear family (return, log1p, −turnover, −drawdown,
−CVaR-shortfall, −vol) whose VERTICES recover the hand-designed canon; uniform sampling over ranges frozen
in `config/eureka_loop.yaml: reward_family`; `params_to_reward` is the SHARED constructor for the
random-search and BayesOpt arms (like-for-like H4). `src/calibrate_lambda.py` operationalises PREREG §3:
per-λ separation accuracy of known-good vs known-degenerate rewards, tie-break (1) across-seed stability
(2) SMALLEST λ; returns the full table for the freezing ADR; never writes config.
**Alternatives.** Free-form random reward ASTs (not comparable to LLM arm; unbounded); largest-λ tie-break
(less parsimonious).
**Reason.** H4 is meaningless without a pre-registered family; the λ rule must be deterministic before
freeze. PREREGISTRATION.md left UNTOUCHED per instruction — RECOMMENDATION for the author at freeze (T4):
add a §4a naming this family/config and the §3 tie-break sentence, so both are inside the frozen document.
**Consequences.** BayesOpt arm still requires the optuna dependency later (separate ADR, R8). Dry run
(`src/dry_run_random_search.py`) proves TrialLedger→DSR/PBO end-to-end on labelled THROWAWAY candidates
(synthetic data, untrained policies, explicit λ; lambda_frozen stays null).

## ADR-011 — Filtered HMM forward pass via public parameters (2026-06-10)
**Decision.** `regimes.py` computes FILTERED probabilities by an explicit scaled forward recursion over
fitted public attrs (startprob_/transmat_/means_/covars_), replacing private hmmlearn APIs
(`_do_forward_pass`).
**Alternatives.** predict_proba (SMOOTHED — leaks, R3); keep private APIs (version-fragile).
**Reason.** Filtering must be provably causal: truncation-invariance test (probs at t unchanged when
future data changes) — smoothed implementations fail it.
**Consequences.** hmmlearn needed for EM fit only; tests skip gracefully without it.

## ADR-012 — Data platform: medallion architecture (2026-06-10)
**Decision.** `src/data/` package: raw→staged→clean→gold layers, ALL artifacts SHA-256-manifested
(manifest.jsonl + legacy checksums.txt) with provenance sidecars and a lineage graph (gold traces
byte-exact to API calls). Write-once freeze; CHECKSUM-VERIFIED reads (unmanifested reads refused).
Acquisition: rate governor + exponential backoff w/ full jitter + per-chunk resumable journals +
injectable fetchers (tests are network-free). Stages: probes (entitlement checklist automation),
security_master (dead-RIC ^suffix parsing, GOOG/GOOGL+META curated overrides), validate (schema-core,
XNYS alignment via exchange_calendars w/ explicit `calendar_start` — xcals' default ~20y lookback would
clip 2005, duplicates/conflicts, missing-data taxonomy with FULL counting and ZERO interpolation),
integrity (RI-consistency, unadjusted-split signatures, stale runs, zero-volume, Ince–Porter daily
adaptation, cross-sectional extreme-day classification with SELF-EXCLUDED peer context so lone crashes
can't certify themselves; REAL_TAIL is never quarantined), membership (PIT splice w/ 2016 overlap
validation, logged Shumway corrections, strictly-prior top-30), reconcile_full (discrepancy clustering
ex-div/split/exit-window/unexplained; per-field vendor-authority merge, column-wise only — cell-wise
blending would fabricate a series no vendor published), panel (as-of joins with declared availability
lags as the ONLY join; PREREG-§6-exact embargoed splits materialized to session lists; parquet gold),
eda (ADF/KPSS, moments, Hill, ARCH-LM, rolling corr, dispersion, drawdown anatomy, reconstitution
turnover — captioned to the design choice each motivates), quality (weighted scoreboard, lineage map,
Gebru datasheet, stage seed paragraphs), cli (probe/pull/build/validate/reconcile/eda/status + run
sidecars). FRED keyless path uses date-chunked public fredgraph CSV (full-range 504s at FRED's gateway).
**Alternatives.** Airflow/dagster (operational overkill); pandera (hand-rolled schema core = equivalent
guarantees, zero dependency); single-layer data/ (no lineage, no quarantine discipline).
**Reason.** Data is the binding constraint; R4 requires immutability+verification to be structural.
**Consequences.** 45 platform tests incl. hypothesis properties, golden determinism, leakage assertions.
REAL DATA ONLY in data/ layers: synthetic exists solely in tmp-dir unit tests and the labelled dry run.

## ADR-013 — Dependencies for the data platform (2026-06-10, R8)
**Decision.** Added to requirements.txt: refinitiv-data>=1.6 (vendor SDK), DatastreamPy>=2.0 (DSWS),
pyarrow>=15 (parquet), exchange-calendars>=4.5 (XNYS), statsmodels>=0.14 (ADF/KPSS/ARCH-LM),
hypothesis>=6.100 (property tests), tabulate>=0.9 (pandas to_markdown for EDA/quality reports); plus
setuptools on py3.12 (distutils shim for pandas-datareader 0.10).
**Reason.** Each maps to an explicit platform requirement in the build spec; one-line ADR per R8.
**Consequences.** optuna deliberately NOT added (BayesOpt arm later, own ADR).

## ADR-014 — Build-box environment: py3.12; RL stack stays on the 4090 (2026-06-10)
**Decision.** Local venv rebuilt on Python 3.12 (3.13 lacked torch wheels); d3rlpy 2.8.x requires
torch>=2.5 which has NO Intel-macOS wheels at all → torch/d3rlpy/stable-baselines3 are uninstallable on
this build box. `make smoke` (ADR-003 PASS log) and the canonical `make lock` remain 4090/Linux actions,
exactly the ADR-002 build/experiment split. requirements.txt bounds unchanged (correct for the 4090).
**Consequences.** Full non-RL stack installed and 113-test suite green on the build box.

## ADR-015 — Entitlement probe outcome & degraded-mode build (2026-06-10)
**Decision.** Automated probes (docs/evidence/entitlement_report.md + probes.json): Refinitiv RDP
PLATFORM session AUTHENTICATES with credentials recovered (user-directed) from ifte0005_phase1/.env into
gitignored .env — but the token carries an EMPTY scope set (`Available scopes: {}`): no datagrid (TR.*
fields), no historical-pricing. Workspace DESKTOP path requires interactive login (app running, proxy
port closed, no desktop app key). DSWS rejects connection (product.datastream.com unreachable with these
creds — separate entitlement). Per the pre-declared degradation protocol: the entire pipeline runs on
REAL open-vendor data (yfinance OHLCV+actions 2005–2025, FRED macro, Ken French factors); the Refinitiv/
Datastream span is QUARANTINED pending entitlements; loaders are vendor-agnostic so the gap back-fills
without redesign. Escalation email rendered in the report.
**Consequences.** PIT membership (pre-2016 AND post-2016) remains blocked → top-30 selection and
membership-dependent stages operate the moment entitled pulls land; human actions listed in the session
report (Workspace login; LSEG scope request; library email).

## ADR-016 — LLM snapshot pin for the Eureka loop (2026-06-10; plan F5)
**Decision.** `config/llm.yaml` primary = anthropic `claude-sonnet-4-6` @ $3/MTok input, $15/MTok output
(prompt caching: 5-min cache writes 1.25×, reads ~0.1× — the K=16 shared-context lever). Verified on the
OFFICIAL models overview (platform.claude.com/docs/en/about-claude/models/overview, fetched 2026-06-10),
which states: "Every Claude model ID is a pinned snapshot. Starting with the Claude 4.6 generation, model
IDs use a dateless format that is also a pinned snapshot, not an evergreen pointer." — i.e. the dateless
id IS the immutable snapshot (Eureka's gpt-4-0314 discipline, current naming). Open-weights companion
(FinRL-DeepSeek precedent): DeepSeek-V3 pinned by dated HF checkpoint `deepseek-ai/DeepSeek-V3-0324`
(weights are the reproducibility artifact; API pricing recorded at use time).
**Alternatives.** claude-opus-4-8 ($5/$25 — stronger, ~2× cost; not needed for reward-function codegen);
claude-opus-4-5-20251101 (dated id, but prior generation and legacy track).
**Reason.** Current-generation stability through Jun–Aug 2026, best cost-efficiency for ~240-candidate
arms, 1M context fits env-source caching.
**Consequences.** Anthropic SDK dependency added only when the loop is built (own ADR). Temperature 1.0
retained per Eureka — VERIFY against App. A before first run (docs/notes/eureka.md task stands).

## ADR-017 / ADR-018 — RESERVED
ADR-017 reserved for recording the pre-registration freeze hash (the ADR-005 completion at T4).
ADR-018 reserved for the λ-calibration result + frozen value (after the first dev-split training runs).
Numbers held so the append-only log stays gapless once those two author actions complete.

## ADR-019 — Universe acquisition bill-of-materials A1–A5 wired (config + pipeline only; 2026-06-10)
**Decision.** Encoded the full data bill-of-materials in `config/data.yaml: universe_pull` (A1 PIT monthly
membership: Refinitiv `TR.IndexConstituentRIC` SDate-grid ≥2016 + Datastream `LS&PCOMP{MMYY}` lists
2005–2016 with 2016 overlap; A2 daily total returns incl. dead ^RICs; A3 market cap for the top-30 rule;
A4 delisting metadata — date/exchange/reason/vendor-terminal-return, Shumway −30%/−55% as documented
FALLBACK only; A5 hardening: bid/ask, volume, TRBC/GICS sector as-of, .SPXTR + .VIX two-vendor parity).
Added `src/data/pull_universe.py` (pure header-tolerant PARSERS + a `make pull-universe` orchestrator over
the EXISTING journaled engine), a `pull-universe` CLI subcommand (dry-run by default; `--live` only once
entitled), and parser unit tests on synthetic fixtures. NO live Refinitiv pulls beyond the probe; no data
re-pulled; no new dependency.
**Alternatives.** Hard-code the field strings inside the pull module (violates ADR-001 config-as-truth);
wait for entitlement before writing the wiring (would put the data build on the critical path the day
access lands).
**Reason.** Make "the day entitlement lands, one command acquires A1–A5" literally true and tested now,
while access is pending — and pin every vendor field string in citation-annotated config so the methodology
chapter exports it.
**Consequences (identification untouched, R1/R3).** A1/A2/A3 feed the pre-registered panel + top-30
selection (PREREG §5); A4/A5 serve cost calibration (bid/ask), capacity defence (volume), integrity
(delisting), and EDA attribution (sector) ONLY — none enters the state vector or the reward search.
Mnemonics marked VERIFY in config must be confirmed by the entitled probe before the first live pull; the
parsers locate columns by role, so a header variant does not break them. `lambda_frozen` stays null;
PREREGISTRATION.md untouched (the §5 universe is already pre-registered; this only operationalises it).

## ADR-020 — PIT membership by event replay; snapshot queries invalidated (2026-06-12)
**Decision.** A1 membership is reconstructed by REVERSE EVENT REPLAY: today's chain (0#.SPX) anchored
back through the full joiner/leaver event streams (`TR.IndexJLConstituent{RIC,Name,ChangeDate}` on `.SPX`
with IC=J / IC=L, 2005→today; 3 requests total). Reconstruction is gated by `validate_membership`:
monthly counts must stay in [495, 510] and known truths must hold (Lehman in 2008-H1/out 2008-Q4, Tesla
out 2019/in 2021) — a count drift means a missed/duplicated event and the artifact refuses to ship.
**Evidence.** The snapshot forms SILENTLY FAIL on this route: `get_data("0#.SPX", TR.IndexConstituentRIC,
{SDate})`, the dated chain `0#.SPX(YYYY-MM-DD)`, and field-embedded SDate all return the CURRENT chain
(content check caught FDS/ODFL/ABNB "in 2005"). The 98 rf_members_* v1 artifacts are INVALIDATED in
`data/manifest/invalidated.jsonl` (write-once: they remain on disk, nothing consumes them). The replay
result validates: 252 months × 499–506 names, union 953 RICs, 333 dead ^RICs carried; Lehman leaver
event dated 2008-09-17 with RIC LEH.N^I08.
**Alternatives.** Datastream LS&PCOMP lists (still blocked on DSWS ClientApi — retained as the planned
cross-check); WRDS/CRSP (pending library reply).
**Reason.** Row-count probes false-PASSed the snapshot form; only CONTENT validation against known
index history exposes it. Probes P2/P3 rewritten to content-validated JL queries so the trap cannot
silently pass again.
**Consequences.** PREREG §5's membership-source sentence (Refinitiv ≥2016 + Datastream 2005–2016) is
OPERATIONALISED as Refinitiv event-replay for the full span, with Datastream as cross-check when DSWS
lands — flag this wording at the T4 freeze (runbook Step 0 gains item 3). Single-source caveat for the
pre-2016 segment stands until the cross-check; the validation gates and the 2016 overlap test remain in
force. `pit_membership.parquet` is a STAGED derived artifact with lineage to the three raw event pulls.

## ADR-021 — Universe data layer COMPLETE: corrected forms, buffer, parallel engine (2026-06-12)
**Decision.** (i) A2 daily total returns via datagrid LONG form Frq=D (get_history TR fields return
empty on this route — 39 artifacts invalidated; content gates now check VALUES, never shapes);
(ii) A3 market cap Frq=M; (iii) A5 px/bid/ask/volume via no-fields get_history split per-field;
(iv) `selection_buffer_months` acquires membership+caps BEFORE window.start so the dev-window top-30
(2005-01-03) selects on strictly-prior Dec-2004 information (PIT; using Jan-31 caps would be
look-ahead); artifacts span-stamped so buffered re-pulls version cleanly under write-once;
(v) acquisition parallelised: thread-safe launch governor (global requests_per_minute RESPECTED;
lock-serialised spacing) + worker pool (config rate_limit.workers=6) overlapping response latency;
vault/journal writes lock-serialised; resume exact under concurrency (tested).
**Evidence.** Journal universe_refinitiv: 653+ chunks frozen, 0 failed. Research panel
clean 5,283×953 (5.03M cells; 3.70M observed; 373k pre-IPO masked; 957k post-delisting terminal;
3,155 interior gaps = 0.06%). Top-30 selections historically exact at all 9 window starts —
dev-2005: GE/XOM/MSFT/C/WMT/PFE/BAC/JNJ (GE then the world's largest); 2019: MSFT above AAPL.
Two-vendor reconciliation on 35 common names: median corr 0.99994; 8,437 days>1e-4 with 390
clustered to ex-div/split days (full clustering = EDA material). Dev-30 EDA: excess kurtosis
WB 89.4 / AIG 76.8 / C 49.8 — the GFC tails are inside the search window by design (PREREG §6).
**Consequences.** D1–D6 all satisfied on entitled PIT data (suffix _univ3 = canonical; _univ/_univ2
superseded, manifested). DSWS remains the pre-2016 cross-check want. λ untouched; PREREG untouched.

## ADR-022 — Repository unification: one project folder (engine ⊕ data) (2026-06-17)
**Context.** Two divergent repos existed for the same dissertation: **(A)** `dissertation_papers/
llm-reward-portfolio` — the audited *experimental engine* (clean package layout; SB3 SAC + TQC, NOT the
rejected IQN-SAC; empirical+EVT `ReturnDistribution` measurement; full inference incl. FZ/ES comparative
backtest, stationary-bootstrap Sharpe/CVaR difference tests, Deflated-Sharpe, multiple-testing; the
Eureka LLM loop + client; arms; random/bayes search; io/results; utils; planning docs incl. the advanced-
prototype blueprint, compute and power analyses) — but with **no real data** and a simpler reward/sandbox
contract; **(B)** `~/Downloads/llm-reward-portfolio` — the *data + hardened core* line: the real Refinitiv
PIT panel (5,283×953, survivorship-free, 333 dead RICs, two-vendor reconciled, full provenance), the data-
acquisition layer (`acquire/build_universe/membership/probes/reconcile_full/security_master/validate/vault/
quality/integrity/eda/cli`), a hardened resource-limited sandbox (`run_candidate`/`_limit`/`static_check`/
payload isolation), a richer distributional-feedback module (`DistributionalFeedback`, `empirical_cvar`,
`crossing_rate`, `bowley_skew`, `left_tail_slope`), a fuller baseline family (`make_baseline`,
DifferentialSharpe/CVaRPenalised/Drawdown/Turnover), PBO-CSCV + PSR/DSR/MinTRL + TrialLedger, and the
Keep-a-Changelog + ADR discipline. The two use **incompatible reward contracts** (A: `RewardFn`→float,
in-process; B: `RewardContext`→`RewardOutput`, sandboxed) — so a blind file-union would silently break the
reward/sandbox pipeline the dissertation rests on.

**Decision.** Unify into **one project folder, `dissertation_papers/`** (already holding `00_planning`,
`01_literature`, `02_guidelines_and_examples`), with the single code repo at `dissertation_papers/
llm-reward-portfolio` using **A's package layout as the structural base** and **folding B in** — executed as
a **safe, staged, test-verified merge, never a big-bang**, under an absolute **no-loss/no-delete** rule
(full backups at `~/Downloads/_merge_backup_2026-06-17/`; B retained untouched until the final stage).
- **Stage 1 (DONE, non-breaking):** the real `data/` + `data/manifest` provenance copied in and
  **checksum-verified** (canonical panel sha256 f4edc86… identical); B's `CHANGELOG.md`, `DECISIONS.md`,
  `RELATED_WORK_WATCH.md`, `reports/`, `runs/`, `docs/*`, `scripts/verify_inventory.py`, B-unique configs
  (`eureka_loop.yaml`, `inference.yaml`) and all B prompts folded in; the 3 clashing configs preserved as
  `config/{data,environment,llm}.B.yaml` (never clobbering A's). **A's 148 engine tests remain green.**
- **Stage 2 (REVISED by evidence — convergence decided):** investigation proved **B's flat science
  modules are the PRE-AUDIT line** — B still ships `smoke_iqn_sac.py` (the IQN-SAC the audit *rejected* for
  SB3 SAC+TQC) and a `crossing_rate` reliability diagnostic in `feedback_schema.py` (a neural-IQN artefact
  the preregistration explicitly *dropped from the headline*). Therefore **A's audited science is canonical
  and stays as the live `src/`** (EVT `ReturnDistribution`; SAC/TQC agents; full inference incl. FZ/ES,
  difference tests, DSR, multiple-testing; env; loop; arms; search; the `RewardFn` contract). B's pre-audit
  science is **NOT merged** — it is **preserved wholesale, not deleted** (Stage 4 folds all of B into
  `archive/pre_merge_repo_B/`). Audit-neutral B *engineering* gains (the resource-limited / payload-isolated
  sandbox `run_candidate`/`_limit`/`static_check`) are recorded as **candidate future ports under their own
  ADR** — evaluated deliberately, never blind-merged.
- **Stage 3:** integrate B's **self-contained** data-acquisition layer (verified: imports only within
  `src/data/`, zero dependence on the pre-audit science) into A's `src/data/` package; reconcile the two
  `panel.py` (keep A's `Panel` dataclass used by the env **and** B's `build_gold`/`materialize_splits`/
  `as_of_join`); add the data deps (`lseg-data`, `pandas-market-calendars`); add a **real-gold loader** so
  the audited env consumes `returns_panel_univ3.parquet`, with a test. Single green suite.
- **Stage 4:** fold **all of B** into `archive/pre_merge_repo_B/` (move, not delete — nothing lost), unify
  git (clean history; B's narrative preserved in CHANGELOG/DECISIONS/`lineage.jsonl`), add the adapted
  `.gitignore` (data payloads local, manifest tracked), reconcile root docs (PREREGISTRATION/CLAUDE/README/
  Makefile/pyproject/requirements — currently A-canonical, B-versions retained), update CLAUDE/README.

**Evidence (Stage 1).** `data/gold` = 54 parquet artifacts + sidecar provenance; `data/manifest` =
checksums.txt/manifest.jsonl (874 lines)/lineage.jsonl/invalidated.jsonl/journal. Canonical-panel sha256
match SRC=DST. `pytest`: 148 passed, 0 failed across 20 test files after the fold-in.

**Consequences.** One folder now holds the literature, planning, the audited engine, AND the real data +
provenance. The `.B.yaml`/dual-prompt/duplicate-science-module artifacts are **intentional, documented
interim state** pending Stages 2–4; the end-state is a single clean package. PREREGISTRATION remains
A-canonical and untouched; the frozen design is unchanged by the merge. Nothing has been deleted.

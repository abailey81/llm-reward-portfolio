# DECISIONS.md — Architecture Decision Records (append-only)

Every locked choice gets ~5 lines: date · decision · alternatives · reason · consequences.
Claude Code: read this file at session start; append, never rewrite history.

> **Authoritative decision log (post-merge, ADR-022).** This file (ADRs 001–024) is the single
> authoritative decision record going forward. The engine line's audit/impl/compute history lives in
> `docs/DECISION_LOG.md` (retained, append-only, A-line). Add new decisions HERE.

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
**Freeze hash.** ⟨run `make freeze` after committing and paste output⟩
**Mechanics (Rank 9, IMPL-FREEZE-1).** The frozen-design hash is SHA-256 over the LF-normalized UTF-8 bytes of
`PREREGISTRATION.md` then `config/preregistration.yaml`, joined by a single `\n` (defined only in `scripts/freeze.py`).
The hash is taken **before** `freeze.py` flips `frozen:`/`freeze_hash:`, so those two scalar state-flips are excluded
from the hashed content and `make freeze-check` re-derives the same digest on the frozen repo. The freeze refuses unless
`phase0_smoke_passed_log_id` is set and PROSE↔YAML agree on all six freeze-relevant fields (seeds, testing_family.m,
difference_tests, sesoi, equivalence_margin, cost_sweep.grid_bps). Current pre-freeze gate hash (informational; becomes
the recorded value if no further amendments): `7e6da01f73811e4e92f8b05643b0222170743badcbf7976b1d6879a3193e41d6`. Run
`make freeze` (signed tag `prereg-v1.0`, best-effort `ots stamp`) to complete the freeze and paste the printed hash here.
**λ frozen value.** **λ = 0** (a deliberately tail-blind selector; `config/preregistration.yaml`
`fitness.lambda_cvar: 0.0`) — NOT a calibrated value: a tail-blind selector is the pre-registered design choice,
so any tail effect is attributable to the feedback channel, not the selector. (Supersedes the original
"after §3 calibration procedure" placeholder.)

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
  *(Stage-4 update: these `.B.yaml` were later removed as redundant — the B configs live in
  `data_pipeline/config/` and the backup; A's configs are canonical. See ADR-024.)*
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

## ADR-023 — Compute plan: rented RTX 4090 + seeds-on-winners (no UCL Myriad) (2026-06-17)
**Decision.** Supersede the frozen-plan "RTX 4090 for development + **UCL Myriad** for the campaign"
(PREREGISTRATION §12) with: **prototype/Phase-0 on the owned RTX 4050 laptop**, **campaign on a rented
RTX 4090 (RunPod/Vast) with seeds-on-winners** (≈$13–16, ~1.5 days), free fallback = Kaggle+Lightning+
Colab+laptop stack. **Alternatives rejected:** UCL Myriad (no access); Azure-for-Students / GCP free
(GPU quota blocked/denied). **Reason:** factual access constraints established in `docs/DECISION_LOG.md`
COMPUTE-1 + `docs/COMPUTE_AND_TRAINING_TIME.md` (authoritative). **Consequences:** the matched-compute
design, seeds, and arms are UNCHANGED — only the hardware/venue. PREREGISTRATION §12 carries a footnote
pointing here (it is still pre-freeze draft; this becomes the recorded compute plan at freeze).

## ADR-024 — Gap-closure wave: real-gold loader, delisting policy, provider, dep/doc reconciliation (2026-06-17)
**Decision.** Close the post-merge inconsistencies surfaced by the repo audit:
- **Real-gold loader** `src/data/loaders.py::load_gold_panel` added (+5 tests) so the audited env can train
  on `data/gold/returns_panel_univ3.parquet`. It anonymises identities (integer ids only; RIC map kept
  separately, never to a reward — N3), and enforces finiteness via an explicit **delisting policy**.
- **Delisting policy = `liquidate_to_cash`** (post-delisting/missing return → 0.0; dead names RETAINED, not
  survivorship-dropped). ⚠ **PROVISIONAL** — the env does not yet model intra-window delisting explicitly
  (`environment_spec_v1`); this is a defensible prototype default, NOT a ratified headline choice. **Needs
  preregistration sign-off** before the headline result; alternatives (`ffill_then_zero`, an explicit
  cash-absorbing env slot) parameterised.
- **LLM provider is OPEN:** the live client (`src/llm/client.py`) is OpenAI-backed (so `pyproject` keeps
  `openai`); ADR-016 (B line) pinned a Claude snapshot. To be reconciled before Phase-1 freeze; the repo
  `.env` currently has **no** LLM key (Refinitiv+FRED only) — user must add one to run the loop.
- **Deps declared:** added `[project.optional-dependencies] data` (`lseg-data`, `pandas-market-calendars`,
  `python-dotenv`, `pyarrow`).
- **Docs reconciled:** `data.yaml` source corrected CRSP→Refinitiv (+VIX=FRED VIXCLS); README counts
  (10 YAMLs, scripts marked STUB, 153 tests); CLAUDE.md post-merge section; two decision logs cross-linked
  (this file authoritative); `prompts/README.md` documents the hardcoded-vs-template state; the `.B.yaml`
  removal recorded (ADR-022).
**Reason.** A merge that is "clean, accurate, professional" requires the audit findings closed or explicitly
flagged — no silent inconsistency. **Consequences.** Engine + loader tests green (153). Remaining items are
**build-gated, not inconsistencies** (tracked, not hidden): the GPU/credential entry-point STUBS
(smoke_test, build_gold, run_campaign, freeze, analyze_results, inspect_rewards, power_analysis = blueprint
T1–T6), the concrete SAC trainer, and the LLM key/provider choice.

## ADR-025 — Advanced execution plan adopted; build-reconnaissance findings (2026-06-17)
**Decision.** Adopt `00_planning/MASTER_EXECUTION_PLAN.md` as the authoritative **execution** layer
(build / parallelise / verify / run) over the frozen design (FINAL_PLAN / PREREGISTRATION). It
**supersedes `ADVANCED_PROTOTYPE_BLUEPRINT.md`** (whose critical-path T0 "acquire real data" is CLOSED — the
`_univ3` survivorship-free PIT panel exists and loads). Part I = a user-requested **advanced 40-candidate
prototype** (all **6 arms × 40 candidates × 1 seed**, **8 generations × 5/gen**, dev splits 2005-14 train /
2015-17 val, fixed SB3 SAC); Part II = the full **6 × 30 × 5** campaign.
**Reconnaissance findings (verified on THIS laptop, 2026-06-17):**
- **Runtime not installed** — no `.venv`, no torch/SB3/numpy/pandas (system Py 3.12 only). The "153 tests
  pass" is from a deleted env → it **must be re-earned here** (build task P1). Hardware: i7-13620H 16T /
  15.6 GB RAM / **RTX 4050 6 GB**.
- **⚠ Memory bug** — `make_headline_agent` defaults `buffer_size=1_000_000`; at the 1,893-dim obs that's
  ≈ 15 GB replay RAM → **OOM on the 15.6 GB laptop**. **Fix:** size `buffer_size = train_steps_per_candidate`
  (≈ 1.4 GB at 50k) or `optimize_memory_usage=True`. (The compute doc's "~380 MB" silently assumed a 50k
  buffer.) To be reflected in `config/algos.yaml` + the trainer.
- **Two missing keystones** — `src/agents/trainer.py::train_and_evaluate` (the concrete SAC trainer) and
  `src/env/runner.py` (the `env_builder(reward_fn) -> {train_env, val_returns(policy), train_returns(policy)}`
  glue that `run_loop` injects). Neither exists; only faked in tests.
- **Keyless validation** — because `LLMClient.transport` is injectable and the 2 search arms need no LLM, the
  ENTIRE pipeline (train → measure → fitness → select → archive → inference) is validated end-to-end on real
  GPU+data via a deterministic **`StubDesignerTransport`** (Pass A, keyless), explicitly NOT the experiment;
  the real-LLM headline (Pass B) is one transport swap, gated on provider/key (ADR-016/024).
**Alternatives.** Jump straight to the campaign (rejected — the Phase-0 gate + a prototype de-risk come first
per the frozen design); duplicate the blueprint (rejected — supersede + reconcile instead).
**Reason.** Make the execution machinery real, parallel, and *verified on the actual hardware* before spending
compute; keep every step literature-anchored and recorded.
**Consequences.** Build proceeds **P1→P6** (env → Phase-0 gate → trainer+runner → LLM glue+stub → orchestration
→ run+analyse), each task tested + recorded. Frozen-design open items (budget framing 30/40/240, embargo
10/21, provider, delisting, action projection, λ) routed to the Phase-1 freeze (plan §7.1). The plan is
verified by an independent adversarial review before the build begins.

## ADR-026 — Runtime: pinned Python 3.11; d3rlpy optional; arch/rliable declared; review-driven fixes (2026-06-17)
**Decision.** Build the prototype runtime on the **pinned Python 3.11** (installed 3.11.9 via winget — faithful
to `requires-python >=3.11,<3.12`; the laptop had only 3.12/3.13/3.14, and the test cache shows the suite last
ran under **3.13**, outside the cap). **Move `d3rlpy==2.8.1` from core `dependencies` to
`[optional-dependencies].d3rlpy`** (archived IQN-SAC verification only; it was the *sole* reason for the `<3.12`
cap, so a plain `pip install -e .` no longer drags in the fragile pin). **Declare `arch>=7.0` + `rliable>=1.2`**
(required by the frozen inference plan, PREREG §10, but previously undeclared). Install **torch cu121** for the
RTX 4050. **Adopt the adversarial-review corrections** (`research/ADVERSARIAL_REVIEW_2026-06-17.md`) into the
build: C1 search-arm fitness adapter (`evaluate_reward`), C2 cross-platform sandbox watchdog (SIGALRM is a
Windows no-op), C3 prompt-file rewiring (`loop.py` ignores `prompts/`), M1 explicit DSR `n_trials`, M2
`budget_spent` fix + per-arm budget assertion, M3/M4 prototype-is-directional caveat (**no prototype number
enters the dissertation**), m1 `buffer_size=train_steps` only.
**Alternatives.** Installed 3.12 + relax the cap (rejected — 3.11 is faithful and zero-d3rlpy-risk; winget made
it free); leave deps undeclared / corrections in prose only (rejected — discipline).
**Reason.** A reproducible, frozen-faithful runtime, with the review's integration gaps closed *before* any run.
**Consequences.** Suite re-earned under 3.11 (P1); IQN-SAC cross-check installs via `pip install -e .[d3rlpy]`
when needed. Plan §6.A is the consolidated correction record.

## ADR-027 — Bounded action space for SAC/TQC compatibility (2026-06-17)
**Decision.** Change `PortfolioEnv.action_space` from `Box(-inf, inf)` to **`Box(-bound, bound)`**, `bound=10.0`
(config `action.bound`). SB3 SAC/TQC **assert a finite action space** (they rescale the tanh-squashed action to
the bounds; an infinite bound → inf/NaN). The raw action is pre-softmax logits; `softmax` projects to the
simplex, so `bound` caps concentration — `bound=10` lets softmax reach ~full concentration (one logit=10, rest
=−10 → max weight ≈ 1.0), preserving the frozen design's intent (the env was written unbounded for full
concentration).
**Evidence.** The Phase-0 smoke test (P2) surfaced `AssertionError: Continuous action space must have a finite
lower and upper bound` for BOTH SAC and TQC on the synthetic slice — the integration bug the gate exists to
find (the concrete trainer never existed before, so this path was never exercised). Matches deep-research §2
(Sood 2023; SB3 docs: bounded action space, simplex-project inside the env).
**Alternatives.** `Box(-1,1)` (rejected — caps max weight at ~20% for 30 assets); an internal softmax
temperature (equivalent, less explicit).
**Reason.** Necessary for the fixed agent to run at all; bounded+softmax is the canonical, science-neutral
pattern; `bound` is configurable and frozen at Phase 1 (with the projection choice, audit C-8).
**Consequences.** Re-run env tests + the Phase-0 smoke. `bound` joins the Phase-1 freeze items (plan §7.1).
The obs space stays `Box(-inf,inf)` (SB3 allows unbounded *observations*; the trainer adds a train-only
`VecNormalize`, P3).

## ADR-028 — Cross-platform sandbox validation timeout (Windows SIGALRM no-op) (2026-06-17)
**Decision.** Replace `validate_once`'s `signal.SIGALRM` timeout (Unix-main-thread only) with a **killable
child process** (`multiprocessing` spawn + queue-get timeout + `terminate()`), plus an inline no-timeout
fallback when a child cannot be spawned (so the orchestrator must run candidates in **NON-daemon** workers).
**Evidence.** Adversarial-review finding C2: on Windows `signal` has no `SIGALRM`, so the timeout was silently
skipped — a `while True` reward hung the whole run. Confirmed live: it hung the P1 suite on
`test_infinite_loop_killed_at_validate_once`. The fix makes that test pass (child killed) and protects Pass A/B
on Windows. `test_sandbox.py` 13/13 green; full non-slow suite **153 green**.
**Alternatives.** Thread-based timeout (rejected — a `while True` thread starves the GIL and is unkillable);
WSL-only (rejected — the prototype runs on Windows).
**Reason.** The reward-hacking guardrail (Skalse/Pan) must actually hold on the real execution platform.
**Consequences.** ~one spawn per candidate (negligible vs training). Orchestrator workers must be non-daemon
(P5). The `signal` import and `_Timeout`/`_alarm_handler` were removed.

## ADR-029 — LLM glue + prototype machinery built & verified (C1/C3; P3–P6) (2026-06-18)
**Decision.** Build the world-class prototype machinery (MASTER_EXECUTION_PLAN P3–P6) and verify it
end-to-end, WITHOUT executing the directional run (user directive 2026-06-18: build to the maximum,
coordinate every step with the literature, verify everything, don't run yet). Delivered:
- **P3** — `src/env/runner.py` (the `env_builder` keystone: train/val/measurement windows on one PIT panel +
  deterministic no-look-ahead rollout), `src/agents/trainer.py` (fixed SAC; memory-safe buffer ADR-025;
  **train-only obs-normalization** via a stats-carrying `NormalizedPolicy`, deep-research §2),
  `src/agents/evaluator.py` (the **C1** search-arm adapter — the search arms now consume matched compute
  through the identical train→rollout→select pipeline).
- **P4** — `src/llm/prompts.py` renders `{ENV_INTERFACE}` from the env spec; `loop.py` rewired to send it
  (**C3**, non-breaking — falls back to built-in prompts so tests need no files); `src/llm/stub_designer.py`
  (keyless, deterministic, varied valid reward code spanning the reward family + tail-aware/stateful
  archetypes → the LLM-arm pipeline runs without an API key); `make_anthropic_transport` (provider parity).
- **P5** — `src/baselines/reward_family.py` (the live-contract H4 `params_to_reward` — it existed only as an
  injected name + an *incompatible* archived version), `config/prototype.yaml`, `scripts/run_prototype.py`
  (6 arms; **arm-level parallelism** across non-daemon workers; LLM arms via the loop, search arms via the C1
  evaluator + family; uniform archiving; matched-compute assertion; resumable; dry-runnable).
- **P6** — `scripts/analyze_results.py` (H2/H4 directional reads; Sharpe/CVaR difference tests on the archived
  validation returns; rliable IQM; the interpretability mechanism-gate — does the distributional winner's CODE
  use the tail stats; GREEN/AMBER/RED verdict; compute-accounting). `loop.py` now archives `val_returns`.
**Evidence.** Full non-slow suite **175 green** on this laptop; ruff clean; the orchestrator dry-run ran all
three arm types **in parallel** (matched=True); +22 new tests. The ADR-028 sandbox child-spawn works inside
the pool workers.
**Open (the user's, plan §10):** the LLM provider + key for Pass B; the actual prototype RUN (gated). The
API audit resolved two plan items: `optuna` is NOT used (`bayes_opt` is sklearn-GP) and the archived
reward-family is contract-incompatible (hence the new live one).
**Consequences.** The prototype is one transport-swap (stub→provider) + one command (`run_prototype.py`) from
execution; the analysis regenerates the verdict from the archive.

## ADR-030 — GPU enabled; heterogeneous GPU+CPU candidate scheduler for max throughput (2026-06-18)
**Decision.** Use BOTH the GPU and CPU at maximum via a heterogeneous candidate-level scheduler (user
directive: "use the full computational power… GPU heavily… parallelise to the max").
**Evidence (measured on this laptop; torch 2.6.0+cu124, CUDA-12.5 driver):** the GPU is **~3.3× faster than
CPU** for the fixed SAC — **110 steps/s (7.6 min/50k) on GPU** vs 34 (24.7 min/50k) on CPU; TQC 104 vs 28. The
1,893-dim obs makes the first layer big enough that the GPU wins — this **overturns the earlier "CPU-bound"
assumption** (ADR-027 note / the generic compute-research) and supersedes the CPU-only choice. (The original
pip install had clobbered the GPU torch with a CPU build; cu124 restores it. torch 2.6 < SB3 2.9's *preferred*
2.8, but SAC/TQC train fine on the GPU — verified.)
**Build.** `src/orchestration/parallel.py` — a device-load-balanced `DevicePool` (n_gpu 'cuda' + n_cpu 'cpu'
tokens over a NON-daemon `ProcessPoolExecutor`) fed by arm-driver threads (LLM reflection / search), decoupling
the fast arm logic from the heavy parallel training and removing the slow-CPU-arm bottleneck of arm-level
parallelism. `--parallel` path in `run_prototype.py`; factory/trainer take an explicit `device`.
**Recipe (two deep-research reports):** threads=1/worker (OMP/MKL + torch, BEFORE imports — up to 30× swing),
`batch_size=512` + TF32 (AMP off), `DummyVecEnv`, `empty_cache()` between GPU tasks, ~2-4 GPU + ~10 CPU workers
(CUDA **MPS is unavailable on Windows** → GPU saturates at a few; **thermals** are the real ceiling). SBX
(SB3+JAX, "up to 20× faster") noted as a future lever. `scripts/bench_compute.py` calibrates the exact split.
**Consequences.** Expected ~3-5× the single-GPU rate → the full 240×25k prototype in **~3-6 h** (vs ~1.5-2 days
CPU-only), pending the optimized calibration + the parallel dry-run. The simple arm-level path is retained
(tested). Sources: NVIDIA MPS (Linux/QNX-only); PyTorch multiprocessing best-practices; SB3 RL-tips (SBX/batch);
SB3 issues #350/#2129.

## ADR-031 — Compute calibration: GPU-ONLY is optimal; CPU training workers are useless AND harmful (2026-06-18)
**Decision.** Run the candidate-training pool **GPU-only** (`n_gpu=3, n_cpu=0`), NOT the heterogeneous GPU+CPU
mix ADR-030 anticipated. This **overturns the generic compute-research recommendation** (~10 CPU + 2-3 GPU) —
it was wrong for this workload.
**Evidence (`scripts/bench_compute.py`, this RTX 4050 laptop; threads=1/worker, batch 512, TF32):**
- The GPU **saturates at ~185 steps/s aggregate**: 1 GPU=96, 2=161, 3=183, 4=180, 5=193 — flat beyond 3 (more
  workers merely time-slice: 96→61→45→39 steps/s *each*).
- A 1-thread CPU worker does only **~5 steps/s** (~19× slower than a GPU worker); **10 CPU workers (47 steps/s)
  don't match ONE GPU (96)**.
- CPU workers **starve the GPU**: 3 GPU alone=186, but 3 GPU + 8 CPU=**143** (each GPU worker collapses 62→33) —
  the CPU training threads crowd out the GPU's env-step/feed threads.
**Consequence.** Optimal = **3 GPU workers (safe in 6 GB VRAM) ≈ 183 steps/s → the full 240×25k prototype in
~9.1 h** (~7 h at 20k steps). **ADR-030's "~3-6 h" was wrong** — the GPU is a hard ceiling at ~185 steps/s on
this card; no parallelism beats it. The only sub-3h lever is **SBX (SB3→JAX, ~10×)** — a dependency swap +
agent re-validation, **GATED** (not adopted unprompted). The campaign's rented RTX 4090 will be materially faster.
**Build.** `DevicePool` now accepts `n_cpu=0` (GPU-only) with a CPU-only fallback when no GPU is present;
`config/prototype.yaml` → `n_gpu=3 / n_cpu=0` + `agent.device: cuda`; `run_prototype.py --parallel` exits
cleanly (`os._exit(0)` past the benign Windows CUDA-teardown nonzero code). **Verified:** the GPU dry-run
(2 workers) ran all three arm types — including the nested sandbox validate-once child spawning *inside* a GPU
pool worker — with `matched_budget_ok=true`, a reloadable archive, and exit 0.

## ADR-032 — 20-track audit + P0 remediation + dependency resolution (2026-06-19)
**Context.** A 20-track deep audit (engineering + scientific/methodological) + 6 GitHub-repo research agents, all
recorded in `00_planning/SYSTEM_AUDIT_AND_REMEDIATION_2026-06-19.md`. Verdict: the codebase is **excellent in
design**; the singular gap is that the *executable inference path stops at validation* (test leg / PBO / walk-forward
/ benchmark floor / freeze / power-analysis are specified-but-unwired), plus a few real bugs.
**P0 correctness fixes (DONE, full non-slow suite green).**
- *Numerical (P0-1):* `_sample_moments` (deflated_sharpe) and `sharpe_ratio`/`cvar` (bootstrap) used an exact
  `sd == 0` guard a **near-constant** series evades (residual `sd ~ 2e-19`) → `sr ~ 1e15` → `deflated_sharpe = 1.0`
  for a **flat reward, which would WIN candidate selection**. Fixed with a relative near-zero guard (+`np.ptp`) +
  non-finite stripping + f64. 28 invariant tests added (`tests/test_numerical_guards.py`).
- *Sandbox (P0-2):* `safe_call` (stage-2) was **never wired** into training — the env called `reward_fn` directly,
  so a reward valid on the fixture but failing on a real N-asset obs **crashed the rollout**. Now routed through
  `safe_call`; added `reset_failure_flag()`/`candidate_failed()` accessors; runner resets+logs.
- *Seeding (P0-3):* the GPU parallel worker seeded only the SAC kwarg. Now `set_global_seed(seed,
  deterministic_torch=True)` at worker entry — Python/np-legacy/`PYTHONHASHSEED`/torch/cuDNN + the M4 determinism
  flags (`use_deterministic_algorithms(warn_only)` + `CUBLAS_WORKSPACE_CONFIG`).
**Dependency resolution (P0-5).** SB3 2.9 *requires* torch≥2.8 but the validated GPU build is **torch 2.6.0+cu124**
→ capped `stable-baselines3`/`sb3-contrib` `>=2.4,<2.9` (keeps the validated torch; re-validate on reinstall).
Dropped **rliable** (upstream archived 2025-10; `reporting.py` reimplements its math; figures → matplotlib). Wired
**arch** (`optimal_block_length`). Security re-pins (`python-dotenv>=1.2.2`, `pytest>=9.0.3`, `ruff>=0.15,<0.16`);
added `pytest-randomly`/`pytest-timeout`. Added **anthropic** + **seaborn**. Relaxed `requires-python<3.13` (the cap
was NOT a d3rlpy requirement — d3rlpy is an isolated extra). License audit: all OSI-permissive.
**Cross-check oracles (repo research).** License-clean validation oracles for the custom inference are **arch**
(StationaryBootstrap/StepM-Romano-Wolf) + **statsmodels.multitest** (both already deps) + **pyextremes** (EVT/GPD) +
**jsharpe** (PSR); `mlfinlab` confirmed proprietary, `quantstats` PSR non-canonical (would fail a strict check).
**Consequence.** Remaining remediation (campaign inference-path builds, repro hardening, provider wiring, adopted
tooling, doc reconciliation) proceeds per the register. The real run stays **gated**.

## ADR-033 — LLM provider: Sonnet 4.6 primary + Llama-4 N3 control + DeepSeek-V4 check (2026-06-19)
**Decision.** Pin **Claude Sonnet 4.6** (`claude-sonnet-4-6`) as the PRIMARY reward-author; **Llama-4** (open-weights,
official Aug-2024 cutoff, commit-pinned) as the N3 contamination control; **DeepSeek-V4** (OpenAI-compatible) as an
optional "contaminated" cross-check. (Supersedes the open ADR-016/024 provider reconciliation.)
**Reasoning (two deep-research passes + a from-the-real-prompts costing).** Cost is immaterial (~$7 whole project).
Sonnet 4.6 is **clean** (no finance-code publication — unlike DeepSeek, which FinRL-DeepSeek + AlphaForgeBench expose
on this very universe), honors **`temperature=0`** (Opus 4.7/4.8/Fable reject it), is **novel** (no reward-code paper
uses Claude), and is best at strict-format. The decisive argument: a **null is a valid pre-registered outcome**, and a
null is only defensible if the reward-author was *capable enough to exploit the distributional feedback* — a frontier
instrument makes a null credible; a "mini" invites "your model was too weak." Reproducibility comes from the **archive
(replay)**, not live determinism, so DeepSeek's weaker determinism is moot in its check-arm role. Strongest
"different-cutoff" operationalisation = **two-model replication of the H2 ordering** across different corpora.

## ADR-034 — Pre-registration amendments D2/R11/R12/R13/R15 (2026-06-19; user-approved)
**Decision.** Apply five dated pre-freeze amendments to the (still-draft `frozen: false`) design, each mirrored
machine-readably in `config/preregistration.yaml` so `scripts/freeze.py`'s prose↔YAML assert holds:
- **D2 (user-approved):** per-arm WINNER seed count **5 → 30** (≥20; Henderson 2018, Colas et al.) for the H2 IQM/CI.
  SEARCH budget untouched (1 seed/candidate during search; only winners re-run at 30 — seeds-on-winners, ADR-023), so
  matched compute holds. `config/{preregistration,campaign,inference}.yaml seeds → [0..29]`;
  `docs/COMPUTE_AND_TRAINING_TIME.md` GPU-hour bands recomputed as winners×30 (lean ≈600 runs ≈110 GPU-hr ≈ $32-44 on a
  4090). Hypotheses/arms/fitness/λ/splits unchanged.
- **R13:** the realized multiple-testing family is ENUMERATED + FROZEN = `{arm-contrast × {Sharpe, CVaR-0.05}}` =
  **m = 6** (the three H2-conjunction legs × two metrics), exactly what `analyze_campaign.collect_family_pvalues` /
  `h2_conjunction` produce (corroborated by `tests/test_campaign_inference.py` `n_family==6`). BH q=0.05 PRIMARY; joint
  Romano-Wolf the FWER alternative; Harvey-Liu t>3 scoped to ABSOLUTE-alpha claims only. A `# fail-loud`
  `assert_realized_family_matches_frozen` in `collect_family_pvalues` checks the realized set == the frozen
  `inference.testing_family`. (`cvar_01` is opt-in/EVT, would grow m→9, NOT in the frozen default.)
- **R11 (doc-accuracy):** relabel the Sharpe difference test "studentized (Ledoit-Wolf 2008)" → re-centred basic
  (empirical) stationary block-bootstrap (the SE cancels in the two-sided p-value; size certified by `null_calibration`,
  audit C-7). Numerics unchanged. `difference_tests: [sharpe_recentred_bootstrap, cvar_difference]`.
- **R15 (pre-registered):** cost-robustness sweep — re-price frozen winners over `grid_bps=[0,5,10,25,50]` WITHOUT
  retraining (`net_c = gross − bps·1e-4·turnover`; exact, cost charged after the action), report-only, never
  re-selecting. `cost_sweep:{…}`.
- **R12 (power/viva Q21):** pre-registered **SESOI = 0.05** val-DSR + symmetric **TOST margin ±0.05** DSR for the
  headline H2 (distributional vs scalar); a non-rejection is reported as a bounded effect (the MDE at 80% power /
  Šidák-α, `docs/POWER_ANALYSIS.md`). `inference.{sesoi, equivalence_margin} = 0.05`.
**Alternatives.** Silent edits to the frozen items (rejected — the protocol mandates dated amendment entries); leave the
family implicit (rejected — an un-enumerated family is un-auditable and un-hashable).
**Reason.** Close the four Wave-3 PENDING frozen-doc amendments (IMPL-BOOT-1/COSTSWEEP-1/POWER-1 + the R13 family
enumeration) and the seeds-5-vs-30 record conflict BEFORE the R9 freeze hash, keeping PREREGISTRATION.md ↔
config/preregistration.yaml byte-consistent.
**Consequences.** Full non-slow suite 327 passed / 1 skipped (no regression); ruff clean. Supersedes the "PENDING
frozen-doc amendment" notes in IMPL-BOOT-1 / IMPL-COSTSWEEP-1 / IMPL-POWER-1 (now APPLIED). The freeze (`make freeze`)
remains the user's gated action; `docs/POWER_ANALYSIS.md` SESOI reconciled 0.200→0.05 alongside this.
**Wiring (queued).** `anthropic` added; wire `make_anthropic_transport` as the default, prompt-cache the static system
block + archive the `usage` object, add `tenacity` retry (SDK `max_retries=0`), pin the dated snapshot.
**Security.** The user pasted a live key in chat (2026-06-19) → it is exposed in the transcript and **must be rotated**;
it was never stored/committed (`.env` is gitignored). The fresh key goes in the gitignored `.env` for Pass B.

## ADR-035 — Provider-neutral LLM transport: Gemini 3.5 Flash (prototype) + Claude Opus 4.8 (campaign); + deep audit (2026-06-19; user-directed)
**Decision.** (a) **Reward-author per stage (supersedes ADR-033's Sonnet-4.6 primary):** the PROTOTYPE author is
**Gemini 3.5 Flash** (`$1.50/$9` per MTok, honors `temperature`), the HEADLINE/campaign author is **Claude
Opus 4.8** (frontier #1, `$5/$25`, rejects `temperature`) — user-selected, prioritising grade/capability over
cost+novelty. (b) **Provider-neutral transport:** a `build_transport(provider, model, …)` registry in
`src/llm/client.py` dispatches `anthropic`→native SDK and `openai|gemini|deepseek`→the OpenAI SDK with the
provider `base_url` (Gemini's OpenAI-compatible endpoint) — **no new dependency**. (c) **Each stage owns its
author:** the campaign threads its `llm` block as `run_arm(llm_cfg=…)` so it no longer inherits the prototype's
(the prior shared-config bug). (d) **Diversity is per-provider:** temperature-honoring authors use
`temperature: 1.0`; temperature-rejecting authors use `diversity_prompt_variation` (a per-candidate directive,
uniform across arms — not an H2 confound), applied identically in the serial + parallel paths. (e) **Deep
adversarial audit** (8 dimensions × 3-vote verify, 134 agents): 42 raised → 38 confirmed (3 critical, 9 high,
11 medium, 15 low) → all engineering findings fixed + regression-tested.
**Alternatives.** Keep Sonnet 4.6 everywhere (rejected — user chose the Gemini/Opus split); a Gemini-specific
SDK (rejected — the OpenAI-compatible endpoint needs none); one shared LLM config (rejected — it forced the
prototype and campaign to share a model); silently "fix" the flagged statistical-design items (rejected —
CLAUDE.md §3 requires user/supervisor sign-off for analysis-plan changes).
**Reason.** Provider-neutrality makes a new author one registry entry, not a four-file edit; per-stage configs
let the cheap model de-risk machinery while the frontier model authors the headline; the audit is the
"find/fix everything, verify deeply" mandate. The critical findings were load-bearing: #1 (un-stripped fenced
output) could have silently zeroed every campaign arm; #3 was a verified sandbox RCE; #2 made winner selection
non-reproducible.
**Consequences.** Full non-slow suite **404 passed / 1 skipped, ×3 order-randomized**; `ruff` clean on
src/scripts/tests; `mypy` 0-new; `freeze.py --check` canonical hash `7e6da01f…` **unchanged** (no frozen field
touched — matched-compute/seed/lag fixes are agent/IO plumbing, not pre-registration). The sandbox gate is now
an allowlist (a numeric op omitted from `_ALLOWED_ATTRS` costs a logged-skipped candidate, never a hole). User
must add `GEMINI_API_KEY` to the gitignored `.env` for a Pass-B prototype run. **FLAGGED for user/supervisor
(not changed):** #9/#14 cross-seed return-series averaging in the headline bootstrap (anti-conservative);
#18 the H2 conjunction is implemented+tested but unwired from the analysis entry point; #13 the sealed-test
leg reuses the fixed 2005-cohort universe. See `docs/DECISION_LOG.md` IMPL-AUDIT2-1 + CHANGELOG 2026-06-19.
**Security.** The campaign key (`ANTHROPIC_API_KEY`) + the new `GEMINI_API_KEY` live only in the gitignored
`.env`; the sandbox allowlist additionally denies a reward any reach to `os.environ`, closing the key-exfil
path the denylist left open.

## ADR-036 — Headline H2 inference corrected to per-seed rliable (R16); H2 conjunction wired (R17 test-universe limitation) (2026-06-20; user-directed)
**Decision.** Resolve the three flagged pre-registered-analysis items (user: "do whatever maximises my grade,
work hard"; pre-registration still `frozen: false` -> pre-freeze corrections). (a) **#9/#14 — fix the
anti-conservative headline inference.** The arm-contrast family difference tests AVERAGED the per-seed
frozen-winner TEST return series per arm and fed that single denoised series to a single-strategy stationary
block-bootstrap; averaging N i.i.d. seeds shrinks the tested variance ~N×, so the test over-rejected a true
null (~21% at the 5% level on 30 seeds). REPLACED with the rliable method (Agarwal et al. 2021): per-seed
Sharpe/CVaR scores -> IQM -> **paired stratified bootstrap over the shared training seeds**
(`bootstrap.paired_seed_difference_test`, same re-centred p-convention so `null_calibration` certifies it),
carrying the across-seed variance — null-calibrated to ~5% (correctly sized). `collect_family_pvalues`,
`romano_wolf_joint`, `h2_conjunction` rewired to the per-seed unit; family (m=6), correction, conjunction,
SESOI/TOST unchanged (R16). (b) **#18 — wire the headline test.** `h2_conjunction` (firing the R13
family-equals-frozen assert) is now invoked by `analyze()`/`write_report`/`main`; it had no caller, so the
documented headline result never ran. (c) **#13 — test-universe limitation.** The fixed 30-asset action
space ties SEARCH/SELECT and TEST to ONE universe (the 2005 development-phase PIT top-30), so the 2018-2025
test leg trades the 2005 cohort (11/30 names differ from the 2018 PIT cohort) — documented as a headline
limitation + a loud `run_campaign` caveat; `load_gold_panel(window_start=...)` added so a PIT walk-forward
universe robustness re-evaluation is runnable (R17).
**Alternatives.** Keep the seed-averaged inference (rejected — a measurable anti-conservative ERROR a
stats-savvy supervisor would catch); a hierarchical seed×time bootstrap (sound but heavier + harder to
validate than the rliable per-seed standard, which the design already pre-registered via
`seed_reporting: rliable_iqm`); elevate the PIT universe to the headline (rejected unilaterally — fixed vs
PIT is a methodological design choice with a real consistency/generalization trade-off, flagged for the
supervisor rather than silently changing the frozen experiment).
**Reason.** A correct, conservative, properly-wired headline inference is grade-critical and makes a NULL
result defensible (the pre-registration's whole purpose); the averaging was a genuine error, empirically
demonstrated. The universe is a design choice best served by transparent documentation + a runnable
robustness path.
**Consequences.** Full non-slow suite **410 passed / 1 skipped**; `ruff` clean; `mypy` 0-new;
`freeze.py --check` passes all prose<->yaml consistency; the canonical hash moved
`7e6da01f -> a1f458d5 -> 5aaf1fc4` (intended pre-freeze R16/R17 refinement; `freeze_hash` still null). The
per-seed test + the null-calibration comparison are unit-tested. PREREGISTRATION §10 R16/R17 +
`config/preregistration.yaml: inference.difference_test_unit`. See `docs/DECISION_LOG.md` IMPL-AUDIT3-1 +
CHANGELOG 2026-06-20. **Gated/supervisor:** the PIT-universe robustness re-evaluation (compute) and the
`make freeze`.

## ADR-037 — World-class elevation pass: block decomposition, B11 analytics, B8 baselines, leakage/rigor audit + R18/R19 (2026-06-20; user-directed)
**Decision.** Under the user's "elevate every block to a world-class, publishable, flawless grade-maximiser"
mandate (pre-registration still `frozen: false` -> pre-freeze amendments): (a) **decompose** the system into
14 blocks (`docs/ARCHITECTURE_BLOCKS.md`) with per-block gap ratings + a supervisor gap analysis, under the
governing principle *elevate engineering/analytics/benchmarking/rigor WITHOUT corrupting the frozen H2
contribution*; (b) **B11** — add a `src/backtest/` analytics suite (~30 highly-relevant metrics, regime-
conditional breakdowns, tearsheets) that REUSES the audited inference primitives (no re-derivation); (c)
**B8** — expand the baseline canon (+5 published reward functions, +4 published allocators) and FIX
`risk_parity` (a real defect: NaN divide-by-zero + convergence to a concentrated non-risk-parity solution ->
convex Spinu 2013 log-barrier via L-BFGS-B); (d) run a **50-year-supervisor leakage/rigor audit** (44 agents,
2-vote verification) and fix the confirmed HIGH findings: **R18** the inter-split purge must cover the 60-day
feature lookback (was embargo=21 < lookback=60, leaving 39 contaminated observations — a López de Prado
purge-insufficiency), now `max(embargo, lookback)=60`; **R19** "SPY buy-and-hold" was a mislabelled exact 1/N
duplicate (no index/caps in the anonymized panel) -> de-duped from the gate + suite expanded to 8 distinct
published allocators.
**Alternatives.** (B11) re-implement metrics independently — rejected (DRY violation + risk of diverging
from the audited Sharpe/CVaR/DSR). (risk_parity) guard the division only — rejected (masks the real
non-convergence: the "risk parity" benchmark wasn't risk parity). (SPY) ship the mislabelled duplicate or
silently drop it — rejected (dishonest / loses a documented benchmark); a real cap-weighted/SPX-TR proxy —
**gated** on a non-anonymized data pull (the gold parquet is returns-only; caps live in the Refinitiv
source). (embargo) keep embargo=21 — rejected (a genuine, quantifiable leakage a strict examiner flags).
**Reason.** Each change either fixes a real correctness/leakage defect (risk_parity NaN, the embargo purge,
the SPY duplicate) or adds additive, non-corrupting analytics/benchmark rigor — all grade-critical and all
keeping the frozen H2 arms/env/hypotheses untouched. Honest documentation of the gated items (risk-free
rate, cash interest, real market benchmark — all needing a FRED/Refinitiv pull) is preferred to fabricating
or silently ignoring them (CLAUDE.md #4).
**Consequences.** Full non-slow suite **427 passed / 1 skipped**; `ruff` clean; `mypy` at baseline;
`freeze.py --check` passes. New: `src/backtest/` (+15 tests), `docs/ARCHITECTURE_BLOCKS.md`. Amended:
`baselines.{rewards,strategies}`, `analyze_campaign._BENCHMARK_NAMES` (8 allocators), `run_campaign.
resolve_windows`, `loaders.embargoed_val_start(lookback=)` + 2 callers, `test_embargo_splits`. Recorded:
PREREGISTRATION R18 (§7) + R19 (§9), both config embargo comments, CHANGELOG 2026-06-20.
**Gated / needs user input.** A **FRED API key** (DTB3 3-month T-bill) unblocks the risk-free rate + in-env
cash interest (HIGH/MED findings); a **Refinitiv/SPX pull** unblocks a true market-cap or SPX-TR benchmark.
Remaining MED/LOW audit findings (analyze() val+test subtrees, DSR trial-count config reconcile, VIX
unit-heuristic dev-only, algo-equivalence assertion, Lo-2002 autocorrelation note) tracked for the next pass.

## ADR-038 — Prototype reward-author → Claude Sonnet 4.6; .env actually loaded; Opus temperature guard (2026-06-20; user-directed)
**Decision.** The **PROTOTYPE** reward-author is now **Anthropic Claude Sonnet 4.6** (`claude-sonnet-4-6`),
superseding the ADR-035 Gemini 3.5 Flash pick. The **campaign** author is unchanged — **Claude Opus 4.8**.
Both use the native Anthropic transport (prompt-cache + token-usage archival, ADR-016/033) and the same
gitignored `ANTHROPIC_API_KEY`.
**Rationale.** User-selected. Sonnet 4.6 HONORS `temperature`, so Eureka K-sample diversity comes from
sampling at `temperature: 1.0` (Anthropic max) — no prompt-variation needed (campaign Opus 4.8 instead
REJECTS temperature and uses prompt-variation). Frontier code author with a clean quant-finance contamination
profile comparable to the Opus campaign arm.
**Changes.** (a) `config/prototype.yaml: llm` → provider `anthropic`, `model_snapshot: claude-sonnet-4-6`,
`api_key_env: ANTHROPIC_API_KEY`, `temperature: 1.0`, `diversity_prompt_variation: false`. (b) **`.env` was
never loaded** — nothing in `src/`/`scripts/` called `load_dotenv`, so a Pass-B run would have died with
"ANTHROPIC_API_KEY not found" despite `.env` holding it; added `load_dotenv()` in
`client.build_transport`, the single choke point every path (incl. the Windows-`spawn` parallel workers)
routes through. (c) **Opus temperature guard:** `_TEMPERATURE_REJECTING_MODELS = (opus-4-7, opus-4-8)`;
`make_anthropic_transport` DROPS a stray `temperature` for those so a config mismatch can't silently 400 the
campaign. (d) `anthropic` SDK confirmed installed (0.111.0; already a pyproject dep).
**Validation.** A live Sonnet call returned valid reward code, `temperature=1.0` was accepted, and token
`usage` was archived — the full path (load_dotenv → key → SDK → model → transport → archive) verified
end-to-end. **Scope:** prototype-author change only; the pre-registered campaign design (Opus 4.8, frozen H2
family, seeds, splits) is untouched.

## ADR-039 — Reward-designer: Opus 4.8 primary + a REQUIRED strong-diverse panel; the numeracy-bottleneck reframe; SBX as the panel enabler (2026-07-01; user-directed)
**Decision.** (1) The confirmatory **primary** reward-designer stays **Claude Opus 4.8** — the most capable,
stable, generally-available frontier model, so a null on it is unassailable ("even the best does not exploit the
channel"). (2) A **multi-model PANEL is now REQUIRED** (not optional) to earn the world-class / publishable
generality the strengthened priorities demand; composed of **strong, diverse models ONLY — no weak models**:
**Opus 4.8 + GPT-5.5 + Qwen3-Coder** (open-weights, the reproducibility anchor) [+ optional Gemini 3.1 Pro /
DeepSeek V4]. (3) The mechanism / responsiveness axis is a **reasoning-effort sweep** (GPT-5.5 `none→xhigh`;
DeepSeek think vs non-think) **+ a legible-format ablation** — explicitly **NOT** a weak-model capability ladder.
(4) The **headline reframe is the numeracy bottleneck**.
**Rationale.** (a) *Determinism is dead* for hosted frontier APIs — Opus 4.8 removed `temperature`/`top_p`/`seed`;
the cause is batch-invariance under dynamic server batching (Thinking Machines, 2025) → this **validates the
archive-replay design** as the only reproducibility path, and means only a **self-hosted open model** (Qwen3-Coder)
gives true independent reproducibility. (b) *The numeracy bottleneck* — frontier LLMs cannot reliably
verbalize/compare close small floats (50–70%; arXiv 2602.07812, NUMCoT 2406.02864); our fed CVaR values
(−0.0577 vs −0.0582) sit in the failure regime → a **citable mechanism for the predicted null** + a scaling
hypothesis. (c) *No weak models* (user-directed): a weak model failing is uninformative and invites the "you used
a weak model" dismissal, and is redundant with a bottleneck that predicts even strong models fail; the
**reasoning-effort axis** tests scaling with strong models only — sharper and more novel. (d) *Sonnet 5* (released
2026-06-30; near-Opus at ~40% cost) belongs **in the panel**, not as sole primary (1-day-old → stability risk for
a frozen, months-later-examined run). (e) Licences verified clean: Qwen3 = Apache-2.0, DeepSeek = MIT,
Kimi K2 = Modified-MIT.
**SBX.** The panel multiplies the laptop SEARCH compute (~N×); cloud is LSEG-licence-blocked → an **SBX/JAX SAC
backend (~5–10×) is the only laptop-only enabler** and will be **built (gated)**: developed on synthetic data,
adopted **iff** Phase-0-valid **and** ≥3–5× faster; SBX-SAC need only be a sound SAC used identically across arms
(not byte-match SB3). Fallback if it fails the bar: SB3 + a reduced panel.
**Scope.** Pre-freeze (`frozen: false`) — to be **ratified into `PREREGISTRATION.md` at Phase 4 before `freeze`**
(USER ratifies). Supersedes the single-Claude-family framing in prior notes. The prototype (ADR-038, Sonnet 4.6,
directional-only) is unchanged. Full session context: `docs/SESSION_LOG_2026-06-30_to_07-01.md`.
**↑ SBX clause SUPERSEDED by ADR-040 (2026-07-01) — both software speed levers are infeasible on native Windows;
the panel is achieved via a longer run, not a speedup.**

## ADR-040 — No software speedup on native Windows: drop SBX; achieve the panel via a longer run, not a backend rewrite (2026-07-01; empirical)
**Finding (empirically probed, not assumed).** This is a **native-Windows** laptop (win32, torch 2.6.0+cu124, RTX
4050). BOTH result-neutral speed levers are **blocked here**: (a) **`torch.compile` FAILS** — `Cannot find a
working triton installation` (Triton, the GPU-kernel compiler the inductor backend needs, has no native-Windows
support); (b) **SBX/JAX-GPU is unavailable** — JAX has no native-Windows CUDA, so it would require a **WSL2
platform migration** (move the whole pipeline — env, gold data, sandbox, orchestration — into Linux + re-validate),
**not** a clean spike. So the laptop speed ceiling is essentially **fixed at ~178–235 steps/s** (n_gpu 2–3, TF32 on).
**Decision.** **DROP the SBX spike** (the ADR-039 SBX clause is superseded). The multi-model panel needs *time*,
not a speedup — and the **1 Sep 2026 deadline (~2 months out) supplies it**: at ~200 steps/s a 3-model strong
panel (Opus 4.8 full 7-arm + GPT-5.5 + Qwen3-Coder on the reduced headline contrast / fewer seeds) is **~2–3 weeks
laptop-only**, comfortably inside the deadline. The exact panel-size-vs-time is confirmed by the pilot's wall-clock
projection (`scripts/pilot.py`) at Phase 3.
**Why this is better.** It (i) keeps the world-class 3-model generality + reproducibility-anchor panel; (ii)
**removes the SBX backend-rewrite risk** right before freeze (serves the "minimise risk" priority); (iii) requires
no migration. The model panel from ADR-039 is unchanged (Opus 4.8 primary + GPT-5.5 + Qwen3-Coder; reasoning-effort
axis; numeracy-bottleneck reframe) — only the *enablement* changes (longer run, not SBX).
**WSL2 path — PROBED AND REJECTED (empirical, 2026-07-01).** WSL2 is installed and in principle would unlock
*both* `torch.compile` (~1.6×) and SBX (~5–10×) via Linux (CUDA passthrough verified working). It was actually
attempted, and **the CUDA `torch` wheel failed to install three times** — first "No module named torch" (deps
installed, the torch wheel did not), then truncated CUDA libs (`libcudart.so.12 / libnvrtc.so.12: file too
short`), then the same on a clean reinstall — a systematic large-wheel truncation (most likely the Windows
Defender scan of the WSL vhd). With the deadline already comfortably met by the native run, this was **not worth
further debugging**. **Decision: stay native Windows** (torch 2.6.0+cu124 already validated + reproducible).
Default = laptop-only, native-Windows, longer run, no migration.
**Compute venue (2026-07-01, user-confirmed).** The campaign stays **laptop-only** — the decisive reason is
**cost: there is no budget for rented cloud GPU right now**. (The data-licence cloud-egress question, raised in
older notes, is *not* the blocker — the user confirmed the licensed data is "not an issue"; it is moot given the
cost decision.) Cloud remains a future option if a budget appears, but is not pursued.
**Scope.** Pre-freeze. `frozen: false`. Empirical basis recorded in `docs/SESSION_LOG_2026-06-30_to_07-01.md`.

## ADR-041 — Four pre-freeze amendments RATIFIED; alpha scope-expansion REJECTED (2026-07-01; user-delegated)
**Ratified** (user-delegated authority; `freeze.py --check` GREEN, canonical hash `0f5e99e5`). Four amendments flipped
PROPOSED→RATIFIED in `PREREGISTRATION.md` + mirrored in `config/preregistration.yaml`: (1) **§2a mechanism-headline
reframe** — the foregrounded RQ is the MECHANISM (does showing the LLM the downside change the reward CODE, and does
it propagate?), a 3-link causal chain with SQ1 responsiveness / SQ2 transmission / SQ3 specificity; report-only,
DISJOINT from the frozen m=6; **σ_D-robust** (the headline holds whether H2 lands equivalence or non-rejection).
(2) **§5 λ=0** (tail-blind selector). (3) **§10 rf/cash numeraire** — rf=0 headline + DGS3MO rf-excess robustness +
cash=0; the risk-free term cancels to first order in the arm contrast, so it cannot move the H2 ordering. (4) **§6
serial-headline** — reverts R24 to **serial reflect-on-last** (ADR-040 makes parallel's speed edge moot; the buffer
skew was a prototype-config artefact; the ITEM-3 parallel-cache fix made reproducibility EQUAL across paths → the
prototype-validated serial path's unattended-run reliability decides it); parallel reflect-on-best retained as a
now-resume-safe robustness variant.
**ALPHA scope expansion — REJECTED.** Rejected in both readings: (A) an alpha-*generation* / market-beating
objective would breach the frozen contribution axis (feedback channel, fixed agent), re-introduce the dropped
forecasting scope, weaken the bankable comparative-null + mechanism headline, trade depth for breadth (against
Okhrati's grading function), and be un-implementable cleanly on the anonymised PIT panel (no market index);
(B) reporting factor-alpha as a *headline metric* shifts to an absolute-performance framing the design deliberately
avoids — and the "no hidden factor bet" characterization is ALREADY delivered by the pre-registered six-factor
attribution (CAPM+BAB+QMJ, Newey–West; CH4 §4.7 / R26). The thesis stays: risk-sensitive reward-design, comparative
null, mechanism headline.
**Scope.** Pre-freeze. `frozen: false`. Full record: `CHANGELOG.md` [2026-07-01b] + `memory/session-current-focus.md`.

## ADR-042 — Replay buffer HARD-capped at 50k across ALL legs (convergence-pilot-surfaced OOM; 2026-07-01)
**Decision.** HARD-cap the SB3 replay buffer at **50,000** transitions, **decoupled from `train_steps`**, applied at
EVERY agent-construction site so all campaign legs AND the pilots resolve `buffer_size = min(train_steps, 50k)`.
The cap is config-driven — `config/campaign.yaml` `agent.buffer_size: 50000`, read by the single helper
`src/agents/factory.py::campaign_replay_cap()` (fallback `DEFAULT_REPLAY_CAP = 50000`). Sites:
- `src/agents/trainer.py::resolve_agent_kwargs` (TEST + serial trainer) and `src/agents/factory.py::_policy_kwargs`
  (GPU-parallel workers) — `buffer_size = min(requested_or_train_steps, campaign_replay_cap())`.
- `scripts/run_prototype.py::_agent_cfg` (serial SEARCH worker) — `min(steps, campaign_replay_cap())`, replacing the
  prototype's explicit `buffer_size=25000` read. This ALSO eliminates the **serial-SEARCH-25k vs TEST-50k buffer
  skew**: the winner is now SELECTED under the same replay dynamics it is EVALUATED under (the same matched-compute
  rationale as train_steps matching, run_campaign ~L1065-1096).
- `config/campaign.yaml` — new `agent: { buffer_size: 50000 }` block (TEST leg reads it → the train_steps re-couple
  at run_campaign ~L1095 is skipped, buffer stays 50k even at B*≥200k).
- both pilots (`scripts/learning_curve.py`, `scripts/run_sigma_pilot_train.py`) — `min(budget, campaign cap)`.
**Why.** The convergence pilot (2026-07-01) empirically **OOM'd**: `buffer_size == budget` allocates
`np.zeros((budget, 1, 1893) float32)` ≈ **2.8 GB at 200k / 5 GB at 350k** → `MemoryError` on the 15.6 GB laptop
(n_ok 3→3→1→0 across 50k→100k→200k→350k; critic losses were all FINITE — the failure was purely RAM, NOT
instability). This is the "buffer-cap wiring" pre-freeze fix flagged open in CLAUDE.md CURRENT STATE. It EXTENDS
ADR-025 (`buffer_size = train_steps`, memory-safe only ≤~100k) so B* can rise to 200k+ without OOM; the replay is
a bounded ~0.76 GB 50k sliding window.
**Alternatives.** `optimize_memory_usage=True` (halves RAM but the known SB3 next-obs footgun; rejected);
`buffer_size = train_steps` (ADR-025 — re-OOMs at B*≥200k, which the pilot proved); threading the campaign agent_cfg
through the pickled serial `run_arm` worker (rejected — invasive across the ProcessPool spawn boundary; the one-line
`min(steps, cap)` in `_agent_cfg` reuses the single source of truth).
**Consequences.** NO training path can OOM at any B*; SEARCH/TEST replay dynamics matched. Prototype UNCHANGED
(25k steps → 25k buffer; `min` is a no-op below the cap). VERIFIED (2026-07-01, CPU): every construction site yields
`buffer_size=50000` at `train_steps=200000` and `25000` at `25000`; an explicit oversize buffer is clamped to 50k;
**93 buffer-touching tests green**, ruff clean, **no test changed** (no test encoded the old >50k semantics). The
first (uncapped) convergence ladder's "recommend 200k / still rising" verdict is SUPERSEDED — it rested on 1 surviving
seed at 200k + an unrepresentative full-history buffer; re-run under the cap is in flight.
**Scope.** Pre-freeze. `frozen: false`. Full record: `CHANGELOG.md` + `docs/SESSION_LOG_2026-07-01_phaseBC.md`.

## ADR-043 — Convergence pilot: B* = 200,000 steps; the tool's "350k / NOT CONVERGED" is a plateau-detector artefact (2026-07-01; empirical, RE-RUN PENDING on Split-C)
**Decision.** Set the confirmatory training budget **B\* = 200,000 steps**. **EXECUTION STATUS: DECIDED-pending-execution** —
the pilot that produced this number ran on the **OLD 2005–2014 train window** and **MUST be RE-RUN on the new Split-C window**
(ADR-044) before B\* is finally banked; the value is not yet confirmed on the campaign data.
**Findings (old window).** (a) Held-out eval is **flat-noise ≈ 0** across 50k→350k — no measurable generalization gain from
more training. (b) Critic loss **bottoms ~100k then rises mildly** to 350k — mild overfitting past the knee. (c) The harness's
automated verdict ("recommend 350k / NOT CONVERGED") is a **plateau-detector ARTIFACT**: its plateau rule expects a *monotone*
approach to an asymptote, and flat-noise (no trend) is not that shape → it never fires "converged" even though the curve is
already flat. The number is therefore set by the loss-knee + the buffer-cap memory envelope (ADR-042), not by the tool's verdict.
**Alternatives.** Trust the tool's 350k (rejected — artefact + mild overfit + more RAM under the 50k cap gives no held-out gain);
50k–100k (rejected — below the loss knee; matched-compute headroom favours 200k). 
**Consequences.** B\* = 200k is the working budget for wall-clock projection and the Phase-3 panel-size decision; the Split-C
re-run is the gate that finalizes it. Supersedes the first (uncapped) ladder's "200k / still rising" read (already noted
superseded in ADR-042). `frozen: false`.

## ADR-044 — DATA PLAN: Split-C re-partition (train 2005–2016 / val 2017–2019 / test 2020–2025) + forward-extend to a settled 2026 cutoff; backward-extension / options / synthetic / more-assets REJECTED (2026-07-01; research-grounded)
**Decision. EXECUTION STATUS: DECIDED, pending rebuild** (the gold panel re-partition + the forward pull are not yet executed).
(a) **Split-C re-partition:** **train 2005–2016 / val 2017–2019 / test 2020–2025** (2020–2026 if forward-extended). Rationale:
more training (**12y vs 10y**) AND a **tail event in BOTH halves** — 2008 GFC in train, 2020 COVID + 2022 in test — so the
out-of-sample tail is not a single lucky/unlucky regime. (b) **Forward-extend to a SETTLED 2026 cutoff:** feasible and **FAST**
(Refinitiv pull ~30 min–2 h — NOT the earlier "2 weeks" guess; see ADR-048). Marginal science (H1-2026 was a bull market, no
tail event) but cheap → do it.
**REJECTED (all research-grounded, not convenience):** (1) **2000 backward extension** — the dot-com era is exactly where
survivorship-free reconstruction is HARDEST *and* where validation breaks down (Ince–Porter 2006 "worst-earliest"; yfinance
cannot validate dead names; CRSP is the academic gold standard, not our Refinitiv entitlement). (2) **Options data** — scope
creep + messier quality (OptionMetrics/IvyDB known issues). (3) **Other-markets-as-features / synthetic data / more-assets** —
scope creep + model risk. (4) **More candidates** — raises the Deflated-Sharpe **multiplicity penalty** without fixing data size.
**Reason.** Split-C maximizes training data and puts a tail event on each side of the split (Okhrati "motivate with the data")
while every rejected option either breaks identification, adds unvalidatable data, or worsens the multiplicity correction.
**Consequences.** The `univ3` gold panel is re-partitioned (PREREG §6 splits change — a pre-freeze design edit, `frozen: false`);
B\* (ADR-043) re-runs on this window; the forward pull runs via PowerShell + `.venv-lseg` (ADR-048). Respects prime-directive-2:
no new asset classes, no new state/reward inputs.

## ADR-045 — Three REPORT-ONLY rigor upgrades, all DISJOINT from the frozen confirmatory m=6 (2026-07-01)
**Decision. EXECUTION STATUS: DECIDED, pending implementation.** Three additions that improve realism/attribution/accuracy
WITHOUT touching the frozen arms/env/hypotheses (report-only, disjoint from m=6):
(a) **Bid–ask SQUARE-ROOT market-impact cost model** — replaces the arbitrary flat 10 bps. Spreads are **ALREADY frozen (A5)**
→ **NO new pull**; sweep the impact coefficient **γ ∈ {0.5, 0.75, 1.0}**. (b) **BAB / QMJ factor-attribution completion** —
free AQR / Ken-French factors (extends the existing 6-factor attribution). (c) **Delisting correction via OBSERVED TERMINAL
RETURNS** — the delisting-reason field mnemonic is **absent under this entitlement**, so the terminal-return approach is both
necessary and cleaner; it corrects the univ4 **M&A mis-booking** (the reason `univ3` — not `univ4` — is the headline panel).
**Alternatives.** Keep flat 10 bps (rejected — arbitrary, un-motivated); delisting-reason field (rejected — not entitled);
skip BAB/QMJ (rejected — free rigor for the "no hidden factor bet" claim, CH4 §4.7 / R26).
**Reason.** Each is cost-realism / delisting-accuracy / benchmark-factor construction — legitimate rigor under the ADR-047
identification rule (does NOT feed the agent a new state/reward input). All report-only → cannot move the frozen H2 ordering.
**Consequences.** New report-only analysis code + config knobs (γ sweep, terminal-return delisting policy, BAB/QMJ factors);
disjoint from the freeze hash. `frozen: false`.

## ADR-046 — Second LLM reward-author = Qwen3-Coder; GPT-5.5 REJECTED on cost; weak/mini models REJECTED on principle (2026-07-01)
**Decision. EXECUTION STATUS: DECIDED** (LLM cost is incurred only at campaign-time; no run yet). The panel's second author is
**Qwen3-Coder** — a strong open coding model, **~$1–3 via a cheap hosted API**, giving frontier **cross-vendor diversity
(Anthropic vs Alibaba)** and true **reproducibility via archive-replay** (open weights). This refines the ADR-039 panel
(Opus 4.8 primary + a strong-diverse second author).
**REJECTED.** (1) **GPT-5.5** — cost ($5 / $30 per MTok → ~$20–40 for the panel leg); the diversity/reproducibility value does
not justify ~10× the Qwen cost. (2) **Weak / mini models** — an **uninformative null** (a weak model failing the channel proves
nothing and invites the "you used a weak model" dismissal); this codifies the standing **"no weak models" principle** (ADR-039).
**Reason.** Grade/publishability wants *strong-diverse* generality + a reproducibility anchor at minimum cost; Qwen3-Coder is
the Pareto pick. **Consequences.** Panel = **Opus 4.8 (primary) + Qwen3-Coder (second author)**; reasoning-effort axis and the
numeracy-bottleneck reframe (ADR-039) unchanged; panel enabled by the longer laptop run (ADR-040), not a speedup. `frozen: false`.

## ADR-047 — Multi-market external validity: a LITE FTSE-100 replication of the FROZEN protocol; and the standing IDENTIFICATION rule for all scope calls (2026-07-01)
**Decision. EXECUTION STATUS: DECIDED, pending implementation.** Add a **lite FTSE-100 replication** — single-market is the #1
reviewer weakness, so **report-only** re-run the **FROZEN protocol** on a 2nd survivorship-free panel. It respects identification
because it **reuses the fixed agent** (no state/reward change) — it replicates, it does not modify.
**STANDING IDENTIFICATION RULE (principle, governs every future scope call).** *Only the **reward-feedback block** varies across
arms.* Therefore: **any addition that feeds the agent a NEW STATE or REWARD input** (fundamentals, sentiment, options, extra
features) is **identification-breaking creep — REJECT**. **Legitimate rigor** = **cost realism / delisting accuracy /
benchmark-factor construction / replicating the frozen protocol on another market** — these do not alter the agent's
observation or reward, so they are additive, not confounding. (This rule is the throughline behind ADR-044/045/046 and the
prime-directive-2 scope ban.)
**Alternatives.** Multi-asset-class or feature-rich extensions (rejected by the rule above — they break the single-varying-factor
identification). **Reason.** External validity is the highest-value *rigor* addition that the identification rule permits.
**Consequences.** A second survivorship-free FTSE-100 panel + a report-only replication leg (fixed agent, frozen protocol);
disjoint from the confirmatory freeze. `frozen: false`.

## ADR-048 — Refinitiv access SOLVED (PowerShell + isolated `.venv-lseg`, never the Bash tool); and RL positioning = simulated-ONLINE off-policy, not classic offline RL (2026-07-01; empirical + methodological)
**Refinitiv access — SOLVED (EXECUTION STATUS: DONE, verified).** The LSEG session **opens (`OpenState.Opened`)** via
**PowerShell** + an **ISOLATED `.venv-lseg`** (`refinitiv-data==1.6.2`). **Root cause of the prior failures:** the **Bash /
Git-Bash tool's sandboxed network could not resolve `api.refinitiv.com`**; **native PowerShell resolves it fine.** **STANDING
RULE:** run **ALL Refinitiv ops via PowerShell + `.venv-lseg`, NEVER the Bash tool.** Verified: the pull is **FAST**; 2026 daily
data is clean; **dead-name (survivorship-free) terminal returns are recoverable** (Lehman verified) → this is what makes the
ADR-044 forward-extend fast and the ADR-045 terminal-return delisting correction feasible.
**RL positioning — CLARIFICATION (methodological).** The setup is **simulated-ONLINE off-policy** RL: **SAC interacts with and
explores a historical-replay simulator** (price-taker, exogenous prices) — it is **NOT classic offline RL** (no fixed logged
dataset with no interaction). It is positioned **vs Okhrati's offline-RL** by **his own harm-criterion** + the
**relabelling → CQL bridge** (`docs/offline_online_position.md`), so the examiner-tailoring cite (Khraishi & Okhrati 2022 CQL)
still lands without mislabelling the method. **Consequences.** The prose must say "simulated-online off-policy," not "offline RL";
the Refinitiv runbook (PowerShell + `.venv-lseg`) is the sanctioned path for every future pull. `frozen: false`.

## ADR-049 — 2026-07-02 deep-audit hardening: 8-auditor sweep finds NO critical code defect; lambda reclassified CALIBRATE→FIX; citation/Le-Cam/certification fixes; two new drift guards
**Decision + findings (EXECUTION STATUS: DONE, verified green).** An 8-front READ-ONLY audit (inference/backtests ·
benchmarks/baselines · data/leakage · RL-env/agent/convergence · LLM-loop/sandbox/prompts · theory-CH3 ·
writing/citations/honesty · repro/cross-artifact consistency), each validated against the primary literature by web
research, found **no CRITICAL or HIGH code defect**: the load-bearing statistics (FZ0, DSR/PSR, expected-max-Sharpe,
HLN, stationary bootstrap, PBO/CSCV, MCS, IUT/BH multiplicity, differential-Sharpe recursion, allocator QPs, the
six-scalar tail MEASUREMENT estimator incl. the GPD/POT closed forms) match their sources exactly; the sandbox
default-deny allowlist repels the standard escape battery; the pipeline is leakage-free.
**Fixed on sight (all verified):** (1) CRITICAL — `harvey1997testing` bib entry was fabricated-as-written (a
nonexistent "Harvey & Liu 1997") → replaced with the REAL Harvey–Leybourne–Newbold 1997, IJF 13(2):281–291 (the HLN
DM correction the prose actually cites); Witzany metadata corrected (Risks 9(1):18). (2) HIGH — theory §3.3 Le Cam
deficiency used a silently NON-standard argument order (reads as the vacuous zero under the Le Cam/Torgersen
convention) → switched to the standard order δ(E_scalar, E_vec) with the strictly-positive reading intact.
(3) `null_calibration` certified only the two-sided p while the H2-Tail leg gates on the ONE-SIDED p (R64) → now
certifies both. (4) ES-backtest docstrings called the two-sided equal-accuracy DM test "the Nolde–Ziegel comparative
backtest" (their ONE-SIDED dominance form) → reconciled to the (correct) CH4 §4.7 disclosure. (5) `var_es_estimates`
VaR/ES conventions unified (ES ≤ VaR by construction). (6) `contamination.named_vs_blinded_structural`: unparseable
(empty-AST) pairs scored jaccard=1.0 ("perfectly locked") → excluded + counted (`n_unparseable_pairs`; P7c mirror)
+ regression tests. (7) `parallel.train_candidate` n_trials prototype fallback (40) → fail-loud mandatory key.
(8) **lambda reclassified CALIBRATE→FIX** (`determine_design.py`): λ=0 is a DESIGN identification choice — the
tail-blind selector; tuning it confounds the H2 channel — not a pending calibration, so it no longer blocks freeze;
the legacy `lambda_grid`/`lambda_frozen`/`calibration_fold` DELETED from the hash-bound `inference.yaml`, executing
the prereg §5 note's own instruction. (9) **Two new drift guards:** `freeze.py::assert_h1_baselines_match` (the
PREREG §18 beat-the-human family mirrored machine-readably into `config/preregistration.yaml`; `campaign.yaml`
asserted equal — the roster-guard pattern) and `preflight.py::check_budget_mirror` (campaign vs algos
`train_steps_per_candidate` must agree, so a B* amendment cannot half-land). (10) Paper: CH4 §4.3 replay-buffer-cap
justification added (Zhang–Sutton 2017 + Fedus et al. 2020 — verified first-hand and added to refs.bib; the
fixed-calendar ~20-pass coverage argument; replay-ratio-1; identical-across-arms ⇒ common-mode); CH7 §7.1 explicit
RQ scorecard (responsiveness / transmission / specificity verdict slots); `CAMPAIGN_preflight.md` 6→7 arms,
180→210 re-runs, `--gpu 4`→`--gpu 3` (4 is now refused); stale buffer comments reconciled to the single
`resolve_agent_kwargs` invariant (verified at trainer.py L120); gridach/orra bib venues corrected to arXiv preprints.
**False positives CLEARED (do not re-"fix"):** DSR raw-kurtosis convention (correct as written), differential-Sharpe
minus sign (canonical, verified vs NeurIPS 1998), gneiting DOI (already correct), `return_minus_cvar` estimator
(≡ the ceil(αn) convention — floor((n−1)α)+1 = ceil(nα) at essentially every n), the placebo "inert" intro
(truthful zero-information is the RIGHT design — neutralizing it would create active MISinformation;
`placebo_shuffled` is the tell-free structure control and takes the write-up headline), reward-penalty ddof=0
(a penalty SCALE, not an estimator — now documented at each site).
**Okhrati title verified = "Dr"** (Lecturer/Assistant Professor, UCL IFT; web-verified): the paper front matter was
already correct; CLAUDE.md + memory corrected (the audit's suggested "fix" ran the wrong way and was rejected).
**Verification:** ruff clean (16 touched files); 223/223 targeted tests green (incl. new guard + filter tests);
`freeze.py --check` 12/12 OK with the new h1 guard live; canonical SHA-256 → `843b84c3…` (prereg gained the §18
mirror — expected, pre-freeze). `frozen: false`.

## ADR-050 — 2026-07-02b: the deliverable pipeline exists; run-day ops hardened (3 run-killers closed); two mechanism/EDA instruments delivered; the ULTRAPLAN is the master plan
**Context.** Two NEW audit lenses (neither correctness-focused — the 8-front sweep was clean) found the two
biggest unmitigated risks in the project: (A) the md→PDF DELIVERABLE toolchain did not exist at all (no
pandoc/LaTeX anywhere; the graded artifact was un-producible), and (B) the unattended 2-3-week Windows-laptop
campaign had three run-killers (tenacity absent → EVERY API call single-attempt; Windows Update live-unmitigated
with no reboot re-entry; exit-0 "husk runs" where a winner could freeze from a partial candidate pool).
**Decisions + what now exists (all verified green — 271/271 consolidated tests, ruff repo-wide, freeze 12/12,
PDF 0-warnings; details CHANGELOG [2026-07-02b]).**
1. **PDF pipeline:** pinned PORTABLE pandoc 3.10 + Tectonic 0.16.9 in tools/ (deliberate over a system install:
   reproducible, no elevation, version-pinned), `build_paper.py` (UCL order, fence-aware citation transform with
   a year-key discriminator, Harvard cite-them-right CSL, References, fail-loud), TeX cache on D:. The
   dissertation COMPILES from day one; compile-time surprises are dead as a submission-week risk class.
2. **Word budget is now measured, not guessed:** `word_budget.py` per the UCL exclusion rules — 15.5k vs the
   10k hard limit → the P7 "word surgery IS the depth pass" workstream with per-chapter targets (ULTRAPLAN).
3. **External timestamp:** `make_prereg_bundle.py` packages the exact hash-bound file set for OSF deposit at
   freeze — "the null was predicted in advance" becomes third-party verifiable.
4. **Ops hardening:** tenacity installed+probed (C1); Windows-Update preflight probes + ONSTART re-entry task
   (C2); campaign exit gate + winner-selection floor + llm-error accounting (C3 — the gate instantly exposed
   and fixed a PRE-EXISTING silent dry-run husk: the 600-day synthetic panel never spanned the frozen splits);
   resume threaded through the serial fallback + H3 (M4); watcher follow-campaign/dedupe-reset/post-then-mark +
   deadman ping (M5); thermal governor live on every path (M6); supervisor healthy-runtime reset + always-resume
   (M7); preflight load_env + REAL guarded 1-token probe (M9); minors m10-m12 + the runbook §0b run-day
   checklist. Judgment calls recorded: TEST-leg RunMonitor documented as a limitation (not a clean reuse);
   H3 floor not mirrored (its statuses feed the exit gate).
5. **Instruments:** the reward-program TAXONOMY (CH7's "future work" delivered; prototype-validated — search
   arms collapse to one template-kind each, LLM arms near-fully idiosyncratic, multi-member kinds span arms =
   null-consistent) and the F3 stylised-facts EDA figure from the REAL train window (kurtosis 14.5, −5σ ×~10⁴,
   the CVaR crossover ×0.8→×1.7, co-crash 3.3→20.4% — the motivate-with-data centrepiece). Both report-only,
   DISJOINT from m=6. ⚠ Write-time: skew is POSITIVE (+0.22) — never claim negative; reconcile the manifest's
   "Hill" wording and the old "kurtosis 49.9" note (different aggregate).
6. **Citations:** bauer2025equal verified first-hand + promoted + cited; sun2024card upgraded to the confirmed
   published venue (KBS 326:114065, 2025); the stale discrepancy note replaced.
7. **Planning:** docs/ULTRAPLAN_2026-07-02.md is THE master plan (P0-P8, owners/gates/exit criteria, timeline
   with 1.5-2 weeks of slack to 1 Sep, risk register, the standing document-everything protocol). Gate ① (disk)
   CLOSED — 20.5 GB verified; the next gate is ② rebuild GO + settled-2026 cutoff (user).
`frozen: false`.

## ADR-051 — P1 rebuild execution parameters: cutoff 2026-06-30, suffix univ5(+univ5s), dedicated extension pull (2026-07-02; user GO "execute everything up to the campaign")
**Decision (recorded BEFORE any data is touched — the cutoff is a data-availability choice, never results-contingent).**
* **Cutoff = 2026-06-30** (user delegated; the latest SETTLED month-end: clean quarter boundary, T+1-settled days
  before the pull, no partial-period ambiguity). **Suffixes: `univ5`** = the extended headline panel (univ3
  conventions: zero-fill delisting, no surcharge) and **`univ5s`** = the corrected Shumway band-end (surcharge
  gated by the OBSERVED-terminal-return recovery, DATA_REPULL_DELISTING.md route — the reason mnemonics are
  confirmed non-resolving).
* **Route = a DEDICATED extension pull, NOT a config-span re-run.** Verified first-hand: `chunk_id =
  sha256(vendor, query, params)`, so changing `period.end` re-keys EVERY chunk (a full 21-year re-pull), while
  the journal skips nothing useful. The driver (`data_pipeline/scripts/extend_universe_2026.py`) therefore pulls
  ONLY the extension: A1' chain+joiner/leaver events to today under `_x26` artifact names (the vault is
  write-once; same-name refreezes are not attempted) -> `reconstruct_membership` over the month grid extended to
  2026-06 -> **HARD-FAIL overlap check against the frozen pit_membership on every 2005-2025 month** (vendor
  event-history revisions must stop the rebuild, never silently land) -> freeze the new span-stamped
  `pit_membership_*_202606.parquet` (build_universe consumes the LATEST). A2'/A3'/A5' pull returns/monthly-caps/
  px-bid-ask-vol for the extension window under `rf_trd_x26_*` / `rf_mcapm_x26_*` / A5-x26 names (prefix-collected
  by build_universe automatically); brand-new 2026 joiners (new union minus old union) get FULL-window pulls
  (pre-listing emptiness journals as skipped_empty).
* **Delisting-terminal**: implement the observed-terminal recovery in `build_universe._derive_delisting_map`
  (vendor_terminal_return := the name's last valid in-window return at/near its delist month; flag-gated +
  unit-tested); `apply_shumway_corrections` already PREFERS a present vendor terminal ("vendor_terminal_kept"),
  so univ5s books true terminals and surcharges only genuinely terminal-less names.
* **Acceptance gates (in order, each fail-loud):** (1) pit overlap identical on 2005-2025 months; (2)
  `verify_gold` univ5-vs-univ3 = ZERO changed cells on the (date x RIC) overlap, ~124 appended 2026 sessions,
  added columns only for 2026 joiners; (3) the pipeline validation suite; (4) spot-checks (Lehman rows unchanged;
  last session 2026-06-30; NYSE session count); (5) THEN Split C + expected_windows[univ5] + checksum manifest +
  `gold.suffix` flip + the 12-file punchlist + full test suite + freeze-check. All Refinitiv ops via PowerShell +
  `.venv-lseg` (ADR-048), never Bash. `frozen: false`.

## ADR-051 addendum — the overlap gate FIRED on first live contact: vendor event-history revision (EVHC.N^L16) detected; resolution = the SPLICE rule (2026-07-02)
**Observed (the gate working, first try).** The fresh A1 reverse event replay (2026-07-02) reproduced the frozen
membership EXACTLY except ONE ric: `EVHC.N^L16` appears as a member on 145/254 overlap months (2004-11..2016-11)
where the frozen pit (pulled 2026-06-12) never had it; nothing else differs (-0 everywhere), and all known-truth
checks (Lehman 2008, Tesla 2019/2021, counts 500-507) pass on the fresh replay.
**Root cause (verified externally).** The vendor BACKFILLED the Dec-2016 leaver event in the intervening 3 weeks;
its join counterpart is missing/re-keyed, so reverse replay over-extends the name's membership back to the grid
start. Provably an artifact: old-EVHC (Envision Healthcare Holdings) IPO'd Aug-2013 and merged into AMSURG
2016-12-01 (NYSE delisting 2016-12-13 = the ^L16 suffix; SEC Form 25-NSE) — it cannot have been a member in 2004.
**Materiality: NONE for this design.** Peak cap ~$7B — never remotely a top-30 mega-cap under the strictly-prior
selection rule, so the top-30 book is invariant either way; univ3's 953 columns are unaffected.
**Resolution — the SPLICE rule (now in the driver).** The FROZEN pit is the pre-registered membership record and
stays AUTHORITATIVE through its own last month (2025-12); the fresh replay contributes ONLY the 2026 month-ends
(where replay-from-today's-chain is most reliable). Overlap differences are diagnosed and must fall inside an
ENUMERATED, externally-verified allowlist ({EVHC.N^L16}); anything else still hard-fails. Extension counts and
month-ends are themselves gated (6 months ending 2026-06-30; 495-510 members). This makes frozen history
immune to silent vendor revisions while keeping the gate's teeth — and the incident itself is disclosed in the
data chapter/datasheet as first-hand evidence of vendor-history instability (why the pre-registered frozen
record + hash discipline exists). `frozen: false`.

## ADR-052 — Throughput levers approved (Tamer, 2026-07-06) + Qwen served first-party (R71 routing superseded)

**Context.** Tamer directed: push training wall-clock to the minimum via hardware exploitation and
parallel scheduling ONLY (zero science cuts), and approved "any speed up" under that constraint.

**Decisions.**
1. **L1 — parallel reflect-on-best search as the executed headline mode — APPROVED by Tamer
   (2026-07-06).** ~8.9 d -> ~4.1 d for the 210-search stage. Execution is MECHANICAL-PENDING the
   batched hash move at seed ratification (the frozen prose records `serial_reflect_on_best`; the
   label change + the seed amendment land as ONE dated amendment). Post-S21/S15 the parallel driver
   is hash-verified resume-safe for all 7 arms with as-completed archival.
2. **L2 — H3 single-shot search parallelism — BUILT (run_campaign: `--search-gpu N` now also routes
   the H3 stage's search through `_search_parallel_arm`).** Science-clean by construction:
   generations=1 has no reflection chain, so the 30 candidates are exchangeable independent
   trainings (~1.3 d -> ~0.4 d). The F8 mode guard covers the H3 root too.
3. **E — `--baselines-only` idle-slot backfill — BUILT** (the no-amendment fallback if L1's
   amendment is ever declined; unnecessary when L1 runs).
4. **R71 routing superseded: Qwen3-Coder is served FIRST-PARTY via Alibaba Cloud Model Studio**
   (Tamer provisioned a "dissertation" workspace; key in the gitignored .env as DASHSCOPE_API_KEY +
   DASHSCOPE_BASE_URL; the plaintext source file was deleted after transfer). The MODEL decision is
   unchanged; the pin moves to the OPEN-WEIGHTS snapshot id `qwen3-coder-480b-a35b-instruct` — a
   stronger reproducibility anchor than a router slug (the weights are downloadable forever).
   Verified live 2026-07-06: auth + /models (148 visible) work; completions await workspace
   activation/top-up (smoke_qwen exits 3 with the actionable paywall message until then).

## ADR-053 — Campaign substrate = UCL MYRIAD (Tamer's directive, 2026-07-13); laptop demoted to certified fallback

**Decision (Tamer, verbatim intent): "the whole campaign, we will run it on Myriad to speed up."**
Supersedes the 2026-06-30 LAPTOP-ONLY decision (which itself superseded ADR-023's rented-4090
framing). The confirmatory campaign runs through `scripts/run_campaign_cluster.py` on Myriad SGE
(pack-5, 3.74 trainings/GPU-h measured; V100 EF + A100 L pools under the striped device-blocked
seed design). The laptop (RTX 4050) remains the CERTIFIED FALLBACK — full science parity by
construction (every primitive reused; cross-substrate parity pairs measured). Consequences applied
the same day: CH4 compute prose rewritten to the Myriad facts; CLAUDE.md campaign-compute block
superseded (gitignored-local); the C5 H3-single-shot cluster mode built (`ccbe860`) because a
Myriad-only campaign requires it; the CAMPAIGN_DAY_RUNBOOK (2026-07-13) is the operative launch
document. Launch itself is GATED on Tamer's OFFICIAL approval (his 2026-07-13 instruction) — the
GO package = curve verdict + wording batch + gate green + rehearsal, presented for his explicit GO.

## ADR-054 — Chunked submission as the standing anti-serialization posture (2026-07-13)

**Context (measured, evidence-ledger claim 17):** the scheduler's policy JSV (`snx=1`) holds a
multi-task array's tail in `hqw`, self-releasing ~1 task/~2 h, and has PURGED pending tails
outright twice (the 07-08 rehearsal arrays; the 07-13 `p6ext` tails — qacct shows no trace).
A campaign of big arrays would be policy-throttled regardless of free GPUs (a 180-task tier
array ≈ days; a 6-task search generation ≈ 12 h).
**Decision:** every campaign submission round is split into MANY SMALL ARRAYS
(`submit_batch(chunk_tasks=…)`, launch line `--chunk-tasks 1`; `dc86322`): no pending tail to
hold or purge, every part immediately eligible; drain forensics and the P13 attempt-evidence
attribution follow each part; the adoption matcher is anchored for part names. The 07-13 singles
recovery is the live existence proof of the pattern.

## ADR-055 — Walltime planning floor 25 steps/s for ladder/probe sizing (2026-07-13)

Job 774923 (800k steps) was h_rt-killed at its full 6 h (qacct `failed 37`, wallclock 21,612 s)
⇒ that node sustained **<37 st/s** — the THIRD downward surprise in the sustained-rate series
(clean anchor 102.2 → worst-measured 51 → <37). Co-tenancy has a heavier tail than any point
estimate: report-only ladder/probe h_rt is now sized at a 25 st/s PLANNING FLOOR (h_rt is a
limit, not a reservation; the only cost is backfill placement). The CAMPAIGN's own auto-sizer
already implied ~25.3 st/s per training (×0.5 of the pack-5 aggregate) — consistent, unchanged.

## ADR-056 — Campaign author RE-CONFIRMED: Claude Opus 4.8, on fresh evidence (2026-07-18 sweep)

Tamer commissioned an unbiased, fresh model sweep (2026-07-18; `docs/MODEL_SWEEP_2026-07-18.md`).
**Verdict: `claude-opus-4-8` stays the single campaign author** — the strongest independently
verified coding record available for the role (SWE-bench Verified 88.6% / Pro 69.2%; LMArena
coding leader, July 2026) with ZERO operational confounds: no refusal classifiers (a
mid-campaign refusal would break arm symmetry — a validity threat), no retention precondition,
no preview churn, one stable canonical id, ~$10.50 total authoring. Considered and dispositioned:
**Claude Fable 5** (outright frontier but classifier-interference risk + 30-day retention +
always-on thinking latency/cost → joins the M2 survey roster, where a refusal is DATA);
**GPT-5.6 Sol** (9 days old, no independent benchmarks → M2 roster; NOTE: GPT-5.5 is superseded
— all prose references update to GPT-5.6 or get dated); **DeepSeek V4-Pro** (LiveCodeBench #1 +
MIT weights, but the standing contamination rejection is not worth reopening pre-freeze;
M2 candidate); **Gemini 3.1 Pro** (frontier tier Preview-only = unciteable endpoint);
Grok 4.5 / Kimi K3 (too fresh; K3 weights unreleased). The secondary reproducibility anchor
(Qwen3-Coder, open weights) is unchanged. This ADR supersedes the model-currency aspect of
ADR-039; the panel/robustness design is unchanged.

## ADR-057 — Validation handshake: timeout_s clocks ONLY candidate code (2026-07-18)

**Decision.** `validate_once` spawns its killable child through a stdlib-only boot shim
(`src/sandbox/_child_boot.py`) with a three-phase protocol — `ready` (child spawned, before any
heavy import) → `armed` (numpy + executor imported, fixture unpickled from a bytes blob) →
verdict — and applies the strict `timeout_s` (2.0 s) ONLY to the third phase, the candidate's
own code. Phases 1–2 get environment graces (45 s / 120 s); their exhaustion raises a DISTINCT
"spawn environment starved" `SandboxError`, never a candidate rejection. Success path joins
gracefully before terminating.

**Why.** Forensics (2026-07-18, 15 probes) proved the old single-clock design conflated
environment latency with candidate behaviour: with system commit charge exhausted (an 8-day
ArmouryCrate.UserSessionHelper leak held 7.61 GB; headroom fell to 0.37 GB), a child's numpy/MKL
DLL load stalled ~103 s (py-spy-verified stack; reproduced with plain subprocess — not an mp,
env, CWD, priority, or CPU effect) and perfectly good rewards were rejected as "exceeded the
2.0s validation timeout". The same conflation would reject PAID candidates at authoring under
laptop commit pressure and fail sealed-leg seeds on contended Myriad nodes (the p6ext800 ×0.5
class). Result-neutral by design intent: validation is pass/fail on the candidate's semantics;
excluding environment noise makes the gate MORE faithful to the pre-registered 2 s contract.
Security unchanged: AST gate in-parent, killable child, hard user-code cap. Companion ops
control: `preflight.py check_commit_headroom` (FAIL < 6 GB commit available).

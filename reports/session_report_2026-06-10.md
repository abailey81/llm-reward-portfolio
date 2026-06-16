# Session report — 2026-06-10 — W15 build-out + research-grade data platform

Companion to `CHANGELOG.md` (every change) and `DECISIONS.md` (ADR-007…016). This document is the
stage-by-stage account with evidence paths and numbers. **Real data only**: nothing synthetic entered
`data/`; synthetic fixtures exist solely inside unit tests (tmp dirs) and the labelled throwaway dry run
under `runs/`.

## A. Stage-by-stage status

| # | Stage | Status | Evidence | Numbers |
|---|---|---|---|---|
| 0 | Preflight | 🟢 (2 items 4090-deferred) | commits `75a697c`, `0af2ee9`; ADR-014 | venv py3.12; 113 tests green, ruff clean; smoke+lock blocked here: d3rlpy 2.8 needs torch≥2.5 — no Intel-mac wheels exist |
| 1 | Acquisition | 🟢 open vendors / 🔴 Refinitiv-DSWS (entitlement, not code) | `runs/data/pull_*.json`; journal `data/manifest/journal/` | yfinance 5 field-artifacts 2005–2025 (5,282×5); FRED 5,478×4 (date-chunked fredgraph; full-range 504s); French 2×5,365; pulls 200–481s wall |
| 1a | Entitlement probes (W3) | 🟢 ran live; access BLOCKED with precise evidence | `docs/evidence/entitlement_report.md`, `entitlement_probes.json`; ADR-015 | RDP platform session AUTHENTICATES, scope set EMPTY (`{}`); desktop needs interactive login; DSWS unreachable; escalation email rendered |
| 2 | Raw vault | 🟢 | `data/manifest/manifest.jsonl`, `checksums.txt`; provenance sidecars | 8 raw artifacts, 42,618 rows, SHA-256 + verified reads (tamper test green) |
| 3 | Security master | 🟢 code+tests (population awaits symbology pulls) | `src/data/security_master.py`; tests | dead-RIC `LEH.N^I08`→(LEH.N, 2008-09) parsing; GOOG/GOOGL+META overrides |
| 4 | Structural validation | 🟢 | build sidecar `build_20260610T155818Z.json` | XNYS-aligned 5,282 sessions; 0 schema violations; off-calendar rows reported |
| 5 | Corp-actions integrity | 🟢 | quarantine artifact; tests | split-signature scan vendor-recorded vs suspect; RI-consistency ready for the Refinitiv span |
| 6 | Outlier taxonomy | 🟢 | `data/clean/quarantine_pilot.csv` (13 rows) | 6 sub-dollar flags + 7 Citi-2009 extreme-day reviews; REAL_TAIL days preserved by self-excluded peer context; **fix applied**: $1 screen now uses RAW close (adjusted prices retro-drag AAPL-2005 under $1) |
| 7 | Survivorship/delisting | 🟢 code+tests / 🔴 data (PIT membership needs entitlements) | `src/data/membership.py`; tests | splice + 2016 overlap validation, logged Shumway (−30%/−55%), strictly-prior top-30 — all PIT-leakage-tested |
| 8 | Missing-data engine | 🟢 | build sidecar `missing` block | taxonomy counts conserved (hypothesis-tested); zero interpolation |
| 9 | Reconciliation | 🟡 single-vendor (by entitlement) | `reconcile` CLI returns explicit SKIP; authority decision recorded in clean provenance | clustering (ex-div/split/exit/unexplained) test-proven; activates when the second vendor lands |
| 10 | Gold construction | 🟢 | `data/gold/*_pilot.parquet`; lineage map | returns 5,282×5; cash features [vol20, ratio, vix] shift(1); splits: dev train 2,517 sessions, val 734 post-embargo (starts 2015-02-03 = boundary+21td), 8 WF folds (each embargoed), CPCV 16 blocks purge 21; leakage ASSERTED by tests |
| 11 | EDA | 🟢 | `reports/eda_v1.md` + `reports/figures/` | excess kurtosis: AAPL 5.75, C **49.9**, GE 8.90, MSFT 9.94, XOM 9.93; Hill α: C **2.18** … AAPL 3.48; ADF/KPSS, ARCH-LM, rolling-corr, dispersion, drawdown anatomy — each captioned to the design choice it motivates |
| 12 | Quality/lineage/datasheet | 🟢 | `reports/data_quality_scoreboard.md`, `docs/evidence/lineage_map.md`, `docs/DATASHEET_v1.md`, `reports/data_chapter_seeds.md` | per-series score 0.70 (recon term honestly 0 until vendor #2); coverage 100% live-span |
| 13 | Tests & tooling | 🟢 | `make test` / `make lint`; CLI `python -m src.data.cli` | **113 passed + 1 platform-skip (114), 8.0s**; hypothesis properties; golden determinism; no network in tests; deep-verification battery: configs parse (no PIN_ME), λ null, PREREG+prompts byte-untouched vs `75a697c`, 18/18 raw checksums clean |
| — | W15 research engine | 🟢 | CHANGELOG "research engine" section; ADR-007…011 | features, sandbox hardening, 6/6 baselines, H4 family, λ-machinery, filtered HMM, ledger dry run (DSR 0.577, PBO 0.094, N=10) |
| — | F5 LLM pin | 🟢 | `config/llm.yaml`; ADR-016 | `claude-sonnet-4-6` $3/$15 MTok (official page 2026-06-10; dateless 4.6 ids ARE pinned snapshots); companion `DeepSeek-V3-0324` |
| — | Scale wave (shadow30 + v2) | 🟢 | CHANGELOG "second wave"; `build_20260610T160743Z.json` | union 35 names; 18 raw artifacts checksum-clean; **yfinance split-adjustment subtlety found & fixed** (reconstructed traded prices; 4,274 phantom flags → 0; 49 genuine reviews; 34 real tails kept); missing engine 184,870 cells / 7,601 pre-IPO masked / 0 interior |

## B. ADRs added this session
Full texts in `DECISIONS.md`: **ADR-007** env cash-row features · **ADR-008** sandbox hardening +
candidate archiver · **ADR-009** baseline canon completed · **ADR-010** H4 reward family + λ-rule
operationalised (incl. freeze-time recommendation to the author) · **ADR-011** filtered HMM via public
parameters · **ADR-012** medallion data platform · **ADR-013** dependencies (R8) · **ADR-014** build-box
py3.12 / RL stack on the 4090 · **ADR-015** entitlement outcome + degraded-mode build · **ADR-016** LLM
snapshot pin.

## C. Data-quality scoreboard (35-name shadow universe, single-vendor era)
| name | coverage (live span) | recon | integrity flag rate | freshness | score |
|---|---|---|---|---|---|
| all 35 names | 1.00 | 0.00¹ | ~0.00 | 1.00 | **0.70** |

Full per-name table: `reports/data_quality_scoreboard.md`. Later-IPO names (TSLA, META, ABBV, AVGO, V, MA,
CRM…) show 100% coverage on their live span with pre-IPO cells MASKED by the missing engine, not imputed.

¹ The reconciliation term is honestly zero until the second vendor lands — the scoreboard is designed to
rise to ~1.0 exactly when entitled Refinitiv data arrives and agrees.

## D. Human-only list (in priority order)
1. **Refinitiv/LSEG access — app-free paths first** (ADR-015; scope census P8):
   (i) **2-minute attempt, browser only**: mint a NEW app key at the WEB App Key Generator
   (apps.cp.thomsonreuters.com/apps/AppkeyGenerator) with the **"EDP API" permission box ticked**, put it
   in `.env` as `REFINITIV_APP_KEY`, run `make data-probe` — if the empty-scope problem was key-side,
   everything flows with credentials alone (platform session already authenticates app-free).
   (ii) **DSWS enablement — strongest lead**: your credentials AUTHENTICATE against the Datastream Web
   Service; the account is merely "not entitled to ClientApi service". Send the rendered escalation email
   (docs/evidence/entitlement_report.md) asking for that one service flag — it unblocks the critical
   pre-2016 membership lists + RI datatype, fully app-free.
   (iii) Fallback only if (i)+(ii) are refused: interactive Workspace login (seat-licence desktop path)
   with a desktop app key in `.env` as `EIKON_APP_KEY`.
2. **PREREGISTRATION freeze (T4, Friday 12 Jun)** — yours alone. Recommended pre-freeze additions (ADR-010,
   file deliberately untouched by this session): a §4a naming the H4 reward family
   (`config/eureka_loop.yaml: reward_family`, `src/reward_family.py`) and the §3 λ tie-break sentence
   ("smallest λ among maximal-separation values; across-seed stability first tie-break"). Then commit with
   `T4: freeze pre-registration v1.0`, run `make freeze-design`, paste the hash into ADR-005, inform Ramin.
3. **4090 box**: `make setup && make test && make smoke` (paste PASS log into ADR-003) and `make lock`
   (canonical requirements.lock per ADR-002/014).
4. **Reading**: Khraishi & Okhrati 2022 in full (W4 → `docs/notes/khraishi_okhrati.md`), Sood 2023
   verification items (T5), Eureka App. A verbatim prompts + temperature check before the first LLM call
   (F5 residue; `docs/notes/eureka.md`).
5. **λ calibration**: stays PENDING until hand-designed training runs exist on the dev split
   (machinery ready: `src/calibrate_lambda.py`).
6. **Citi 2009 quarantine review** (5 min): 7 extreme-day rows are real moves on a ~$1–4 stock —
   expected resolution is "real, keep" once the $1-screen interplay is inspected at raw prices; the queue
   preserves values either way.

## E. Integrity confirmations
- **PREREGISTRATION.md: untouched** (byte-identical to the scaffold commit). **prompts/: untouched.**
  **R2 scope-lock list: untouched** — nothing on the forbidden list was implemented or scaffolded.
- `inference.fitness.lambda_frozen` remains **null**; no search was run; the TrialLedger dry run is
  labelled throwaway, synthetic, and outside `data/`.
- `data/` payloads are exclusively real vendor pulls, write-once, SHA-256-manifested, checksum-verified
  on read; corrections (Shumway, screens) are flag/log-only — no return value was ever mutated.
- Secrets: credentials recovered at your direction from `ifte0005_phase1/.env` into the project's
  gitignored `.env` (chmod 600); values never printed, logged, or committed.

## F. Judgment calls beyond the spec (one line each)
1. Probe battery single-sourced (`reward_contract.probe_contexts`) so sandbox and in-process validation
   can never drift.
2. Sandbox runtime `__import__` allows numpy (system prompt mandates `import numpy as np`; previously a
   hidden contradiction).
3. Extreme-day market context SELF-EXCLUDES the name (a lone collapse must not certify itself through a
   5-name EW average).
4. Authority merge is column-wise only — cell-wise vendor blending would fabricate a series no vendor
   published (R4).
5. Ince–Porter $1 screen moved to RAW close after the pilot run exposed the adjusted-price artefact.
6. exchange-calendars constructed with explicit `calendar_start` (its ~20y default would silently clip
   2005 from 2026 onward).
7. FRED keyless path date-chunks the public fredgraph CSV (their gateway 504s full-range requests).
8. `claude-sonnet-4-6` over Opus: 2× cheaper per token at reward-codegen quality, and officially a pinned
   snapshot despite the dateless id (URL + quote in ADR-016).
9. Family rewards don't pass through the sandbox (repo code, not LLM output — R6 governs untrusted text);
   they satisfy the same contract + probe battery.
10. PREREG tightenings (§3 tie-break, §4a family) delivered as ADR-010 recommendations instead of edits —
    your instruction made the file untouchable; the freeze commit is the right vehicle.
11. Pilot legacy scripts (`pull_pilot.py`/`reconcile.py`) kept working but superseded by the platform CLI
    (lint-fixed, not deleted — week-plan references them).
12. Quarantine never deletes: full original rows ride along with reason codes; REAL_TAIL classifications
    are evidence, not exclusions (the project is ABOUT tails).
13. Shadow30 universe pull (30 extra real large-caps) added as a PIPELINE-SCALE proof, explicitly labelled
    non-research-universe — it stress-tested chunked journaling and exposed the yfinance split-adjustment
    subtlety, now fixed via `reconstruct_unadjusted_close` (unit-tested inversion; 4,274 phantom flags → 0).

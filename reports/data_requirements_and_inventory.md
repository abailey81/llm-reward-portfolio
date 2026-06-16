# Data Requirements & Inventory — canonical report

**Generated 2026-06-10** by re-verifying every manifest checksum and walking all four medallion layers.
Authority: `CLAUDE.md` (R1–R8), `PREREGISTRATION.md` §5–6, `config/data.yaml`, `data/manifest/`.
This is the project's single source of truth for *what data the dissertation needs · what exists on disk,
verified · what is missing and its unlock condition.*

> **RED-ALERT CHECKSUM LINE:** none. **39 / 39 artifacts re-hashed → PASS.** No mutated artifact vs
> manifest; no orphan file on disk outside the manifest. Write-once integrity (R4) intact.

---

## 1. Canonical requirements matrix (the data bill of materials)

**Status legend:** HAVE = on disk, verified · PARTIAL = present but provisional/shadow · MISSING-ENT =
blocked on a Refinitiv/LSEG entitlement · MISSING-OTHER = not yet built (no entitlement blocker).

### Block A — entitled vendor inputs (Refinitiv / Datastream)

| # | Requirement | Vendor / field | Config reference | Role in design | Status |
|---|---|---|---|---|---|
| A1 | PIT S&P 500 **monthly membership** 2005–2025 | Refinitiv **event replay** (`TR.IndexJLConstituent*` J/L streams + current chain; ADR-020 — snapshot forms are survivorship traps on this route); Datastream `LS&PCOMP{MMYY}` = pending cross-check | `universe_pull.membership` | Survivorship-free universe; the spine of PREREG §5 | **HAVE (2026-06-12)** — `pit_membership.parquet`, 252mo × 499–506, union 953 RICs, 333 dead ^RICs, validation-gated |
| A2 | Daily **total returns**, full membership union incl. dead ^RICs + leavers | Refinitiv datagrid long form `TR.TotalReturn` `Frq=D` (ADR-020 correction; get_history form returns empty) | `universe_pull.total_return` | The return panel itself (identification) | **HAVE (2026-06-12)** — 429/429 chunks; panel 5,283×953 incl. 333 dead ^RICs; content-verified |
| A3 | **Market-cap** history for the top-30 selection | Refinitiv `TR.CompanyMarketCap` `Frq=M` (CONFIRMED) | `universe_pull.market_cap` | Pre-registered top-30-by-cap rule (PREREG §5) | **HAVE (2026-06-12)** — monthly caps incl. pre-window buffer (PIT-clean dev selection) |
| A4 | **Delisting-event metadata** (date, exchange, reason, terminal return) | `TR.ExchangeName` + TRBC on dead RICs (CONFIRMED); date via ^MYY suffix + last trade (`TR.InstrumentDelistedDate` often null); Shumway = documented FALLBACK only | `universe_pull.delisting` | Integrity: correct terminal returns, no silent disappearance (R4) | **HAVE (2026-06-12)** — rf_meta_* (exchange/TRBC incl. dead RICs); dates via ^suffix + last trade |
| A5 | **Hardening pulls** (NOT identification) | bid/ask/volume/price via no-fields `get_history` (BID/ASK/ACVOL_UNS/TRDPRC_1, CONFIRMED); TRBC sector; `.SPXTR` (CONFIRMED); `.VIX` **NOT LICENSED** → FRED VIXCLS primary | `universe_pull.hardening` | Cost calibration · capacity defence · EDA attribution · index parity | **HAVE (2026-06-12)** — px/bid/ask/vol per chunk + .SPXTR; .VIX not licensed → FRED |

### Block B–C — open-vendor inputs (no entitlement needed)

| # | Requirement | Vendor / field | Config reference | Role in design | Status |
|---|---|---|---|---|---|
| B1 | yfinance OHLCV + dividends + splits, pilot-5 + shadow-30, 2005–2025 | yfinance (non-adjusted + actions) | `pilot.tickers`; `vendors.yfinance` | Cross-validation vendor; the **provisional** panel until Block A lands | **HAVE** |
| C1 | FRED macro: VIXCLS, DGS3MO, DGS10, T10Y2Y | FRED (keyed or fredgraph) | `macro_fred` | VIX → cash-row feature; rates → context | **HAVE** |
| C2 | Ken French daily factors + momentum | Ken French data library | `factors_french` | Attribution only (never identification) | **HAVE** |

### Block D — derived (gold) artifacts — **PROVISIONAL on the shadow universe**

All Block-D rows are built and verified, but on the 35-name yfinance **shadow** universe.
**Rebuild trigger for every D-row: Block A landing** (PIT membership + market cap), which replaces the
shadow tickers with the pre-registered top-30-by-cap union and re-runs `make data-build`.

| # | Requirement | Source artifact (verified) | Config / spec | Role in design | Status |
|---|---|---|---|---|---|
| D1 | Clean return panel | `clean_returns_univ3.parquet` (5,283×953, Refinitiv authority) | stage 9 authority merge | The panel the env consumes | **HAVE (PIT, 2026-06-12)** |
| D2 | Market-cap panel | `staged_mcap_refinitiv_univ3.parquet` (monthly, buffered) | `universe_pull.market_cap` | Drives top-30 selection | **HAVE (2026-06-12)** |
| D3 | Top-30 selections per window | `top30_selection_univ3.parquet` — dev-2005 + 8 WF starts, historically exact | `membership.top30_at`; PREREG §5 | The pre-registered universe per window start | **HAVE (2026-06-12)** |
| D4 | Features vol20 / vol20-vol60 / VIX | `cash_features_v2.parquet` (5,282×3) | `features.py`; ADR-007 | Leakage-safe cash-row state | **HAVE (PIT, 2026-06-12)** — `cash_features_univ3` |
| D5 | PREREG §6 splits, 21-day embargo | `splits_v2.parquet` | `panel.materialize_splits` | Dev/eval split + CPCV | **HAVE — split logic is universe-independent; byte-matches §6 (see §2)** |
| D6 | HMM input series | `market_proxy_univ3.parquet` (PIT universe EW) | `regimes.py`; ADR-011 | 3-state filtered regime detector input | **HAVE (PIT, 2026-06-12)** |

---

## 2. Physical inventory, verified

**Totals:** 39 manifested artifacts · 179,056 manifest rows · **checksum pass rate 39/39 (100%)** ·
every artifact carries a `.provenance.json` sidecar · 0 orphans on disk · 0 mutations vs manifest.
Date span where applicable: **2005-01-03 → 2025-12-30/31** (XNYS sessions / FRED calendar).

### Raw (18 artifacts) — three pull generations, all PASS
| File | Rows×Cols | Tickers / series | Satisfies |
|---|---|---|---|
| `yf_{adjclose,close,volume,dividends,splits}_34c45d1f.csv` | 5282×5 | AAPL,C,GE,MSFT,XOM (pilot-5) | B1 |
| `yf_{…}_6e4cc12d.csv` | 5282×25 | shadow-30 chunk A (ABBV,AMD,AMZN,AVGO,BAC,BRK-B,…) | B1 |
| `yf_{…}_493311e7.csv` | 5282×5 | shadow-30 chunk B | B1 |
| `fred_macro.csv` | 5478×4 | VIXCLS,DGS3MO,DGS10,T10Y2Y | C1 |
| `french_F-F_Research_Data_Factors_daily.csv` | 5365×4 | MKT-RF,SMB,HML,RF | C2 |
| `french_F-F_Momentum_Factor_daily.csv` | 5365×1 | MOM | C2 |

### Staged (3) · Clean (6) · Gold (12) — all PASS, all sidecar'd
- staged: `staged_returns_yfinance_{pilot(5),shadow30(35),v2(35)}.parquet`
- clean: `clean_returns_{pilot,shadow30,v2}.parquet` + `quarantine_{pilot(13),shadow30(4323),v2(49)}.csv`
- gold: `{returns_panel,cash_features,market_proxy,splits}_{pilot,shadow30,v2}.parquet`
  (v2 is the current analysis set: 35 names, corrected price screens → 49-row quarantine)

### D5 split boundaries — byte-match against PREREGISTRATION §6 ✓
| Field | splits_v2 (on disk) | PREREG §6 | Match |
|---|---|---|---|
| Embargo | 21 trading days | 21 | ✓ |
| Dev train | 2005-01-03 → 2014-12-31 | 2005-01-01 → 2014-12-31 (first XNYS session = Jan 3) | ✓ |
| Dev validation (post-embargo) | **2015-02-03** → 2017-12-29 | 2015-01-01 → 2017-12-31, **+21-session embargo** | ✓ (starts exactly boundary+21) |
| Walk-forward test years | 2018,2019,…,2025 (8) | 2018 → 2025, 1y step | ✓ |
| CPCV | 16 blocks, purge 21 | S=16, purged | ✓ |

---

## 3. Pipeline extension (config + wiring only — no pulls)

Added this session so that **the day entitlement lands, one command acquires A1–A5** (ADR-019):
- `config/data.yaml: universe_pull` — every A1–A5 vendor field string, citation-annotated; mnemonics that
  need confirmation on the entitled feed are marked **VERIFY**.
- `src/data/pull_universe.py` — header-tolerant PARSERS (membership, delisting, panel fields) + an
  orchestrator over the existing journaled engine (rate-governed, chunked, resumable, manifested).
- `make pull-universe` (dry-run default; `make pull-universe LIVE=1` once entitled) /
  `python -m src.data.cli pull-universe [--live]`.
- `tests/test_pull_universe.py` — parser fixtures + a dry-run plan assertion (no network).
- **Identification untouched:** A1/A2/A3 feed the panel + top-30 rule (PREREG §5); A4/A5 are cost/capacity/
  integrity/EDA only — none enters the state vector or the reward search.

Dry-run plan (verified): **252 monthly membership requests** (21y × 12m) + A2/A3/A4/A5 field pulls.

---

## 4. Entitlement status (re-probed 2026-06-10)

Evidence: `docs/evidence/entitlement_report.md` (+ `entitlement_probes.json`), regenerated by
`make data-probe` this session. Outcome vs the 10-Jun run: the platform session did **not** open this run
(P0 BLOCKED, `OpenState.Closed`) where it had authenticated before — RDP platform tokens are short-lived
and sign-on may be transiently rejected; **the data-access conclusion is unchanged either way** — no probe
ever returned a non-empty scope set. DSWS still authenticates the user but `ZLDU178` is "not entitled to
ClientApi service".

---

## 5. Gap summary

### (a) Missing items — each with its single unlock condition + the command that closes it
| Item(s) | Unlock condition (verbatim) | Command that closes it |
|---|---|---|
| A1, A2, A3, A4, A5 (RDP path) | **EDP-API app-key permission**: mint a key at the web App Key Generator (`apps.cp.thomsonreuters.com/apps/AppkeyGenerator`) with the **"EDP API" box ticked**, set it in `.env` as `REFINITIV_APP_KEY` | `make data-probe` → (if scopes present) `make pull-universe LIVE=1` |
| A1 pre-2016 + A2 dead-RIC backbone (Datastream path) | **DSWS ClientApi enablement for account ZLDU178** (UCL Library / LSEG) — see `docs/outbox/escalation_lseg.md` | send the escalation email → `make data-probe` → `make pull-universe LIVE=1` |
| D2, D3 | Block A landing (A1 + A3) | `make data-build` (re-runs with PIT membership + market cap) |
| D1, D4, D6 (replace shadow with PIT top-30) | Block A landing | `make data-build` |

### (b) Quarantine status — author sign-off pending
49 extreme-day rows (all `ERROR_SUSPECT`, the v2 corrected-price-screen result) await author review:
**`data/clean/quarantine_v2.csv`**. Full original values preserved; 34 REAL_TAIL crisis days were
classified as real and kept in the panel. Expected verdict on most: real moves on low-priced names through
the GFC — but the call is yours; nothing is excluded from the panel by this queue until you sign off.

### (c) Completeness statement
**UPDATE 2026-06-12 — the entitlement condition LANDED.** A1 is satisfied and validation-gated
(`pit_membership.parquet`); A2–A5 are streaming through the journaled pull; D2/D3 and the PIT rebuild of
D1/D4/D6 execute via `make build-universe` the moment the pull completes. Remaining external wants:
DSWS ClientApi (cross-check of the pre-2016 membership segment, single-source caveat until then) and the
`.VIX` CBOE licence (FRED VIXCLS covers it).

*(Superseded 2026-06-10 statement: 5 of 14 satisfied; all 9 remaining items unlock on Refinitiv/LSEG
entitlement — that condition has now been met.)*

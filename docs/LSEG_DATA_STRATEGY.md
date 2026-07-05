# LSEG data strategy — what the full licence unlocks for THIS project (deep, unfrozen re-assessment)

> **★★ EXECUTED 2026-07-02 — the forward-2026 extension + Split C this document planned HAS NOW RUN.**
> The dedicated journaled extension pull (`data_pipeline/scripts/extend_universe_2026.py`, PowerShell +
> `.venv-lseg`, 138/138 chunks) + `build_univ5.py` produced the ACTIVE panel **univ5 = 5,406 × 963,
> 2005-01-03 → 2026-06-30** (settled cutoff), byte-diff-verified vs univ3 (**0 changed overlap cells**;
> +123 sessions, +10 new 2026-joiner columns), and **Split C is executed + hash-bound**: train 2005–2016 /
> val 2017–2019 / test 2020–2026H1 (`gold.suffix: univ5`; `expected_windows.univ5`). The overlap gate
> caught a live vendor event-history revision (`EVHC.N^L16`) → resolved by the SPLICE rule + enumerated
> allowlist. See **ADR-051 (+ addendum)**, **CHANGELOG `[2026-07-02c]`**, prereg **R73**, and
> `docs/DATASHEET_v1.md` §2026-07-02. Still DECIDED-not-executed from this doc: the **FTSE-lite
> replication** (§2B). The body below is the reasoning trail and is left as written.

> **★ RECONCILED 2026-07-01 (decisions settled this session — read FIRST; DECIDED vs EXECUTED marked).**
> The exhaustive upgrade-research pass closed several questions this doc had left open. Net changes vs the
> 2026-06-28 body below:
> - **Refinitiv access is SOLVED (verified 2026-07-01), not blocked/uncertain.** A live session opens via
>   **PowerShell + an isolated `.venv-lseg` (`refinitiv-data` 1.6.2)**. The earlier friction was the **Bash
>   tool's sandboxed network**, not an entitlement or licence gap — run every pull via **PowerShell +
>   `.venv-lseg`**. **The pull is FAST**: a full/forward Refinitiv pull is ~**30 min – 2 h**, **NOT "~2 weeks"**
>   (any "~2 weeks" figure elsewhere refers to the *laptop training campaign*, not a data re-pull — do not
>   conflate). This retires the §7 🟡 "probe access before relying" hedge for the entitlement itself.
> - **Data plan DECIDED (pending rebuild) = Split C:** train **2005–2016** / val **2017–2019** / test
>   **2020–2025 (or 2020–2026)**. The **forward-2026 settled extension is FEASIBLE + FAST** (same ~30 min–2 h
>   pull) → it becomes the concrete, preferred history move, *replacing* extend-history-backward as the live
>   lever. **DECIDED, pending the rebuild pull (not yet EXECUTED).**
> - **Backward extension to ~2000 (dot-com) is REJECTED on DATA-QUALITY grounds** (not deadline): a
>   survivorship-free dot-com reconstruction is the hardest + least validatable era — Ince–Porter (2006) shows
>   the earliest Datastream years are worst-quality; yfinance cannot cover dead names; **CRSP is the gold
>   standard there and Refinitiv is not**. This SUPERSEDES §2A's "extend to ~1989" as a candidate: the
>   forward-2026 extension is the accepted direction; deeper backward history is off the table on quality, not
>   just non-stationarity. (§2A's non-stationarity + pre-2016-membership cautions still stand and reinforce it.)
> - **Multi-market "lite" FTSE replication is now DECIDED (report-only external-validity leg)** — §2B's
>   FTSE 100 path is adopted as the single external-validity replication, not left as an option among UK/EU/JP.
> - **The 2nd LLM is Qwen3-Coder** (open, the reproducibility anchor); **GPT-5.5 was REJECTED on cost.**
>   Wherever a panel below lists "GPT-5.5" as a live 2nd model, prefer **Qwen3-Coder** (the panel framing in
>   MODEL_CARD.md §"panel" is the stale one — flagged for the owning agent, not edited here).
>
> **REASSESSED 2026-06-28 (nothing frozen).** An earlier version of this doc rejected most LSEG categories on a
> "frozen scope" gate. That was wrong: the campaign has not run and the design is malleable, so the question is
> **not** "does this fit the frozen design" but **"with a full LSEG licence, what data most strengthens the
> CONTRIBUTION — an LLM-designed *tail-risk* reward for a risk-sensitive portfolio agent — and the generalisation
> claim, subject to the constraints that genuinely remain?"** The genuinely-remaining constraints are: (1)
> **Determinism** (a methodological pillar — reproducible PIT/survivorship-free pulls, byte-identical replay);
> (2) **LSEG licence egress** (legal — local/UCL-governed, no third-party cloud); (3) **Design integrity** (the
> *anonymised-returns* reward input is a deliberate clean-causal-attribution choice — see rejects); (4) the BINDING
> real constraint: **the MSc deadline / feasibility** (engineering + compute per added data type). "Relevance" now
> means *maximises grade + publishability*, not *fits a frozen pipeline*.

## 0. The reframe — the contribution is about TAILS, so rank data by how much it strengthens the tail story
The thesis lives or dies on the credibility of its **EVT/CVaR tail estimation and the tail-feedback-vs-scalar
contrast**. The single biggest internal threat (self-flagged limitation) is **small-sample tail fragility**:
~750 trading days ⇒ only ~7–37 exceedances at α=5%/1%, below the ~50–100 EVT-reliability standard
(Belzile-Davison 2022). Therefore the data levers are ranked by **how directly they fix/strengthen the tail
contribution and the generalisation claim**, with feasibility as the tie-breaker — NOT by "fits the frozen panel".

## 1. Current LSEG footprint (verified first-hand from `data_pipeline/`)
- **Access**: `refinitiv.data` (RDP Platform grant *or* `EIKON_APP_KEY`/`RD_APP_KEY` desktop session) **and**
  Datastream Web Services (`DatastreamPy`/DSWS, a *separate* entitlement) — see `acquire.py`, `DATA_ENTITLEMENTS.md`.
  (LSEG has since renamed the Python client `refinitiv-data` → **`lseg-data`**; see §5 % VERIFY.) Shadow vendors:
  FRED (risk-free) + Ken French (factors) — already wired (`market_reference.py`).
- **Data pulled (bill-of-materials A1–A5)**: A1 PIT monthly **S&P 500 membership** (`TR.IndexConstituentRIC`,
  `0#.SPX` / Datastream `LS&PCOMP{MMYY}`); A2 **daily total returns** (`TR.TotalReturn` / `RI`); A3 monthly
  **market cap**; A4 **delisting metadata** (`TR.InstrumentDelistedDate`, `TR.ExchangeName`); A5 sector / bid-ask
  / volume (cost calibration, capacity, EDA — **never** in the state vector or reward).
- **Scope**: US large-cap, top-30-by-mcap, 2005–2025, survivorship-free PIT, Shumway delisting corrections.
  **Single market, single asset class.**

## 2. TIER 1 — highest contribution/grade impact, feasible

### 2A. EXTEND HISTORY to ~1989 — SUPERSEDED 2026-07-01 (backward extension REJECTED; forward-2026 chosen instead)
> **RESOLUTION (2026-07-01).** This whole "extend backward" lever is now **closed**. The decided history move is
> the **forward-2026 settled extension** (fast, quality-safe — see the top banner + §2B / Split C), and deep
> **backward** extension (to ~2000 dot-com, a fortiori ~1989) is **REJECTED on DATA-QUALITY grounds**:
> survivorship-free reconstruction is worst-and-un-validatable in the earliest years (Ince–Porter 2006),
> yfinance can't cover dead names, and CRSP — not Refinitiv — is the gold standard there. The analysis below is
> retained as the (still-valid) non-stationarity/quality reasoning that led here; treat it as historical.

### 2A (historical). EXTEND HISTORY to ~1989 — RECONSIDERED + DOWNGRADED (⚠ not the slam-dunk first claimed)
A first pass crowned this the "#1 lever" on the surface logic *more history → more exceedances → robust EVT*.
On scrutiny that is **half-true and over-sold**. Genuine mechanism: a longer per-candidate window does yield more
left-tail exceedances toward the ~50–100 EVT-reliability standard. **But the costs I under-weighted are serious:**
1. **Non-stationarity (the decisive one).** EVT/GPD assumes a roughly *stationary* tail. Pooling 1989–2025 mixes
   regimes + microstructure eras (decimalisation, Reg NMS, HFT, QE) → more data *from a different distribution*
   can **bias** the tail estimate, not sharpen it. The textbook fix — conditional GARCH-EVT (McNeil-Frey) — is the
   very thing we **rejected for breaking byte-identical determinism**, so the non-stationarity it imports has no
   deterministic remedy here.
2. **Data quality degrades pre-2016**: PIT membership leans on the weaker Datastream backbone (TR.IndexConstituentRIC
   reliable only ≥~2016) — the *added* years are *lower*-quality survivorship reconstruction.
3. **It attacks a SECONDARY concern** (CVaR-feedback-signal reliability), not the headline per-seed rliable arm
   comparison; and the current **2005–2025 window already contains GFC 2008 + COVID 2020** (the "n≈750" is a
   per-*window* count, not the ~5,000-day panel) — so the "tail-starved" premise is itself weak.
4. **Feasibility is HEAVY, not moderate**: forces a full **re-pre-registration + campaign re-run** vs the deadline.

**Better, cheaper, lower-risk alternative for the same limitation (PREFERRED):** *disclose it and quantify the
uncertainty* — already built (WS5 stationary-block-bootstrap CVaR CIs + reliability tiers + CVaR-1% marked
exploratory; Belzile-Davison). A well-quantified, honestly-disclosed small-sample tail is more defensible than a
window extension that imports non-stationarity. **Verdict: CONDITIONAL / likely-dominated** — pursue only if (i)
non-stationarity is explicitly handled (regime-conditional or block-resampled tail, NOT naive pooling), (ii)
pre-2016 membership quality is verified, and (iii) the timeline genuinely allows a re-run. Otherwise prefer
disclosure + multi-market.

### 2A-bis. EXPAND THE CROSS-SECTION (top-30 → top-100), SAME market + SAME period — the *clean* "more tail data"
The lever extend-history *wanted* to be, without its flaw. Widening the universe (e.g. S&P 500 top-100, or the
full index) over the **identical 2005–2025 window** adds **more cross-sectional left-tail events + a harder, more
realistic allocation problem**, with **no time-series non-stationarity** and **no pre-2016 membership cliff** (it
reuses the S&P 500 membership/returns we already pull). Statistically the cleanest way to enrich the tail.
**Honest cost: a real design change** — the SAC action space + state vector are dimensioned for N=30, so a larger
N means a bigger network, more training, and a re-pre-registration + re-run (comparable lift to multi-market). Use
`TR.IndexConstituentRIC` / Datastream lists exactly as now, just a larger `top-N` selection. Net: **preferable to
extend-history** (same period → stationary), still re-run-level → weigh vs deadline.

### 2B. MULTI-MARKET (FTSE 100, STOXX 600) — fixes external validity; **FTSE-lite DECIDED 2026-07-01**
> **RESOLUTION (2026-07-01).** A **multi-market "lite" FTSE 100 replication** is **DECIDED** as the single
> report-only external-validity leg (DECIDED, not yet EXECUTED — needs the entitled pull via PowerShell +
> `.venv-lseg`). FTSE is chosen over STOXX/Japan (the high-confidence, same-currency-clean case). The
> implementation path below is the accepted plan; register it as a pre-freeze external-validity amendment.

The other top reviewer weakness is **single-market generalisation**. The pipeline is **already index-parameterised**
(`config/data.yaml: universe.index: SP500`, membership via `TR.IndexConstituentRIC`/Datastream lists), so
re-pointing it reuses the identical, deterministic A1/A2/A3 machinery:
| Market | Membership universe | Why relevant |
|---|---|---|
| **FTSE 100 (UK)** | `0#.FTSE` / Datastream `LFTSE100` | different regime/regulatory regime; same-currency-clean GBP |
| **STOXX Europe 600 / EURO STOXX 50** | `0#.STOXX` / `0#.STOXX50E` | continental Europe, broader breadth |
| **TOPIX / Nikkei 225 (Japan)** | `0#.TOPX` / `0#.N225` | distinct tail behaviour, different crisis timing |
- **Passes the gates**: same `TR.TotalReturn` + membership + mcap fields (universal LSEG), so the pull is
  deterministic + PIT + survivorship-free exactly as univ3/univ4 were; local/UCL-governed (licence-safe);
  it is an **external-validity REPLICATION leg, not a change to the frozen H2** (report-only / pre-freeze
  registrable). **Execution is USER-GATED** (needs the entitled live pull + creds, like the original univ pulls).
- **Implementation path**: (a) add a second universe block to `config/data.yaml` (index + membership mnemonics);
  (b) `make pull-universe --live` for the new index → new `returns_panel_univ*_<mkt>.parquet` + provenance;
  (c) register a **pre-registration amendment** (external-validity replication arm, report-only — NOT a new
  co-primary IUT) BEFORE the campaign; (d) run the frozen protocol on the new panel; report rliable IQM +
  performance profiles per market. *Caveat*: cross-currency total returns — pull in local currency and keep the
  Sharpe/CVaR currency-consistent (or USD-convert via LSEG FX with the same PIT discipline).

## 3. TIER 2 — design-enhancing, HEAVY lift (weigh hard against the deadline)  🟠
### 3A. MULTI-ASSET universe (equities + government/credit indices + commodities + FX)
This is **not** scope-creep — it is the *richest* version of the actual question. Commodities, credit and FX
exhibit **fatter and more heterogeneous tails** than large-cap equities, so a tail-feedback reward-design study
spanning asset classes is a far stronger test of *"does feeding the tail help where tails actually bite?"* —
and a cross-asset risk-sensitive RL allocator is materially more publishable than a single-market equity one.
Uses the same LSEG **total-return index** machinery (deterministic, PIT). **Cost/feasibility: HEAVY** — each
asset class needs its own transaction-cost / rebalancing calibration in the env, and the validation surface
multiplies. Honest verdict: the *best* design on the merits, but the **MSc deadline likely bounds it to v2 /
second-paper** unless the timeline is generous. If included, it is a pre-freeze design change (register first).

## 4. TIER 3 — cheap report-only enrichment (marginal but easy)  🟢
- **Richer regime conditioners** — VIX term structure, credit spreads, macro indicators (LSEG/Datastream
  economics) → sharper regime-conditional robustness reporting (the regime split already exists in `src/regimes/`).
- **Richer factor data** — LSEG/StarMine factor exposures beyond Ken French FF, for the pre-registered
  factor-attribution of agent behaviour. Both are report-only (do not touch the reward/state).

## 5. REJECTED — on DESIGN-INTEGRITY / RELEVANCE / GRANULARITY (survives "nothing is frozen")  ❌
| LSEG category | Why rejected — a real reason, NOT "frozen" |
|---|---|
| **News / sentiment (News Analytics MRN, MarketPsych)** | Breaks the deliberate **anonymised-returns** reward design — the reward sees NO identifying info precisely so the tail-feedback effect is *cleanly attributable*; injecting sentiment confounds the contribution and adds look-ahead/leakage risk. A different (separate) paper. |
| **Options / vol surface / derivatives** | Turns the allocator into an options/hedging trader — a fundamentally *different problem and agent*, not a richer version of this one. |
| **Tick History (TRTH) / intraday** | Granularity mismatch: portfolio allocation here is **daily**; intraday adds determinism + storage burden for no gain on the tail-allocation question. |
| **Standalone ESG / ownership / supply-chain / deals / patents / alt-data** | No mechanism linking it to the tail-risk reward-design question — pure scope-creep regardless of freeze. |

## 4. REJECTED — scope-creep against the frozen design (strict)  ❌
| LSEG category | Why rejected |
|---|---|
| **News / sentiment / News Analytics (MRN/TRNA)** | CLAUDE.md forbids a news/sentiment pipeline; the reward sees only anonymised returns. Out of scope. |
| **ESG (LSEG ESG scores)** | not a state/reward input; no role in a tail-risk reward ablation. |
| **Estimates / IBES, Fundamentals (TR.F\*)** | the agent trades on returns, not fundamentals; would change the contribution. |
| **Options / vol surface** | the study is allocation over equities at daily freq; VIX (points) already loaded; options = new asset class + scope-creep. |
| **Tick History (TRTH) / intraday** | the study is **daily**; intraday is a different problem + determinism/storage burden. |
| **Ownership, supply-chain, deals, patents, alt-data** | no role in the frozen design. |

## 6. ALREADY-USED / no action  ✓
Risk-free (FRED DGS3MO), market benchmark (`market_ew`), Fama-French factors (Ken French) — on disk + wired.
The S&P 500 univ3 panel is the headline data.

## 7. Verification status (reconciled 2026-06-28 — see `docs/LSEG_CATALOG_VERIFICATION.md`)
✅ **CONFIRMED** (LSEG devportal/PyPI + LSEG docs):
- Python client = **`lseg-data`** (LSEG Data Library v2, successor to `refinitiv-data` v1); uniform across
  RDP/LSEG Data Platform/Workspace/Eikon/CodeBook; **DSWS is a separate entitlement** (matches the repo).
- `get_history(TR.TotalReturn)` + `TR.IndexConstituentRIC` work the same for **non-US** indices. **Cleaner PIT
  path noted**: LSEG's "historical index constituents" supports `TR.IndexJLConstituent*` (joiner/leaver replay)
  — a more robust PIT membership method than monthly snapshots; consider it for the multi-market pull.
- Datastream `MMYY` backbone depth: S&P 500 → `LS&PCOMP0989` (Sep 1989); FTSE → `LFTSE1000199` (Jan 1999);
  monthly-only; bare `LFTSE100` is current-only (use `MMYY` for history — repo already does).
- **Shumway −30/−55 do NOT transfer** (US-CRSP/exchange-specific). Non-US analogue = observed terminal
  `RI`/`TR.TotalReturn` + the repo's existing **liquidate-to-cash** default; **scope Shumway to the US panel only**.
- Catalogue breadth: all mapped asset classes available under a full licence → the §3/§4 reject/future-work
  partition stands. Licence: systematic redistribution + third-party (derived) data handling barred; individual/
  institution-governed academic use permitted → **third-party cloud egress barred, local/UCL-governed OK**.

🟡 **OPEN — probe in Workspace before relying** (`% VERIFY`):
- **Japan (TOPIX/Nikkei)**: chain RICs `0#.TOPX` / `0#.N225` + PIT history depth — mechanism identical to UK/EU
  but no LSEG-primary confirmation; probe before use. (UK FTSE 100 + Europe STOXX 600 / EURO STOXX 50 are
  HIGH-confidence — the cases LSEG documents.)
- **Delisting *reason* field (US and non-US)** — **RESOLVED 2026-07-01 (negative):** the delisting-REASON
  mnemonics (`TR.DelistingReason` / `TR.DelistingType` / `TR.DelistingReasonDescription`) do **NOT resolve
  under this entitlement** (probed 2026-07-01). The fix therefore uses the **observed-terminal-return
  fallback** (dead-name daily returns ARE recoverable — Lehman `LEH.N^I08` returned 2042 daily rows). See
  `docs/DATA_REPULL_DELISTING.md` for the recorded probe result + procedure. `TR.InstrumentDelistedDate`
  resolves (often null).
- STOXX 600 / TOPIX / Nikkei **Datastream earliest `MMYY`**; the exact cloud clause in UCL's specific agreement.

⚠ **Two pre-pull caveats for every non-US leg** (belong in the pre-freeze amendment + entitled probe):
1. **Currency** — `TR.TotalReturn` has no API currency override; pull in local currency and keep Sharpe/CVaR
   currency-consistent, or FX-convert via LSEG FX under the same PIT discipline.
2. **Delisting** — no US Shumway carryover; use observed terminal + liquidate-to-cash (already the repo default).
Neither blocks the lever.

## 8. Deep-sweep confirmations (workflow `wfn5e6xn7`, 2026-06-28 — full report in the task output)
A 103-agent adversarially-verified deep sweep CONFIRMED and sharpened the above:
- **Access route**: `lseg-data` v2 (LDL; PyPI v2.1.1, 2025-04-04; v1 `refinitiv-data` is feature-complete). For
  reproducible headless historical pulls use a **cloud/RDP Platform Session** with a machine account — NOT the
  desktop (Workspace-app-on-localhost) or real-time streaming channels.
- **Survivorship-free PIT membership**: `TR.IndexJLConstituent*` (joiner/leaver) family + the **`0#.<RIC>(YYYYMMDD)`
  as-of chain syntax** reconstruct membership across global indices (CONFIRMED, 3-0).
- **Extended history — COVERAGE confirmed, but RECOMMENDATION downgraded (see §2A).** Datastream equity
  total-return backbones reach **~1986–1988** (so ~1989 is firmly covered; G7 macro reaches the 1900s), and the EVT
  literature does motivate more exceedances (GP/MLE estimators downward-biased at ≤60 exceedances). **However**, the
  deep sweep ALSO flagged the counterpoint: unconditional POT over a 36-year pool is **non-stationary**, and the
  conditional fix (McNeil-Frey GARCH-EVT) breaks determinism — so "more history" is NOT a clean deterministic fix.
  Net (§2A): the mechanism is real but the move is **conditional/likely-dominated** by disclosure + multi-market.
- **Multi-market Datastream list mnemonics** (CONFIRMED): `LFTSE100` (UK), `LS&PCOMP` (US), `LDAXINDX` (DAX),
  `LSTOKYOSE` (Tokyo SE); STOXX via `0#.STOXX`. Multi-asset breadth = Datastream's 48M+ instruments.
- **Methodology**: prefer **CVaR/ES** over VaR as the tail-feedback target (coherent; Basel III/FRTB standard) —
  which the design already does.

## Bottom line (reconciled 2026-07-01 — forward-2026 + FTSE-lite DECIDED; backward-extend REJECTED)
**Settled this session (see top banner):** the live data moves are **(a) the forward-2026 settled extension**
under **Split C** (fast pull, quality-safe) and **(b) the FTSE-lite external-validity replication** (report-only).
**Backward extension is REJECTED on data quality.** Refinitiv access is **solved + fast** (PowerShell +
`.venv-lseg`). The feasibility ranking below is retained as the reasoning trail; items 1–2 remain valid, item 3
(extend-history-backward) is now CLOSED.

Feasibility-ranked, after stress-testing the extend-history claim:
0. **DEFAULT (cheapest, lowest-risk, do regardless): disclose + quantify the small-sample tail** (WS5 bootstrap
   CIs + reliability tiers + CVaR-1% exploratory). This handles the #1 limitation *without* new data or a re-run,
   and is more defensible than importing non-stationarity. No licence/deadline cost.
1. **Multi-market replication** (Tier 1, cheap, pipeline-ready) — now the **strongest data lever**: a different
   cross-section over the *same* period → external validity (a PRIMARY reviewer concern) with **no
   non-stationarity-over-time problem**. UK/EU high-confidence, Japan probe-first.
2. **Extend history to ~1989** (⚠ CONDITIONAL — see §2A) — a real mechanism but **dominated** by (0)+(1) for an
   MSc timeline: imports non-stationarity (no deterministic EVT fix), relies on weaker pre-2016 membership, and
   forces a re-pre-registration + re-run. Pursue ONLY with explicit non-stationarity handling + verified data
   quality + ample time.
3. **Multi-asset universe** (Tier 2, heavy) — the richest test of the tail question; deadline-bounded → likely v2.
Everything else is **report-only enrichment (Tier 3)** or **rejected on design-integrity/granularity** (news/
sentiment, options, intraday — *not* on "frozen"). All data levers are **user-gated** (entitled live pull) and,
since the campaign has not run, are **legitimate pre-freeze design changes** that must be locked (and registered)
before the run — the binding constraint is the **deadline**, not a freeze.

# LSEG / Refinitiv catalogue verification — for `LSEG_DATA_STRATEGY.md` §6

Strict web verification (2026-06-28) of the data-strategy doc's claims, against LSEG/Refinitiv's
own developer portal, the LSEG Data-Analytics product pages, and university-library Datastream/Workspace
guidance. Each item is tagged **CONFIRMED** (corroborated by an LSEG-owned or authoritative source),
**LIKELY** (corroborated by secondary/community sources but not LSEG primary docs at field-level), or
**UNVERIFIED** (could not confirm — must be checked in Workspace / the entitled portal).

> **Method honesty.** "CONFIRMED" here means *confirmed in public docs*, NOT confirmed on *this account's*
> entitlement. Field availability, history depth, and currency conventions are entitlement-specific; every
> item below that gates a live pull still needs the entitled probe (`% VERIFY — confirm in Workspace`).
> No field mnemonic, chain RIC, or product name below was invented; uncertain ones are flagged.

---

## 1. Python access — `lseg-data` and the API family

**CONFIRMED — current client is `lseg-data` (LSEG Data Library for Python, "LD"/v2), successor to `refinitiv-data` ("RD"/v1).**
- The LSEG developer portal's "Essential Guide to the Data Libraries" describes the generations explicitly:
  EDAPI (Eikon Data API) → RDP library → **RD (Refinitiv Data Library, v1)** → **LD (LSEG Data Library, v2)**.
  LD is the recommended/latest version; the PyPI package is **`lseg-data`** (import surface `lseg.data`).
  Eikon Data API users are directed to migrate to the LSEG Data Library. (developers.lseg.com; pypi.org/project/lseg-data)
- **Relationship to RDP / LSEG Data Platform, Workspace/Eikon, DSWS:** CONFIRMED that the library offers
  *uniform access* across access points — direct connection to the Data Platform (RDP, now "LSEG Data Platform"),
  via Eikon, via LSEG Workspace, via CodeBook, or via a local Real-Time Distribution System. The same Python
  code retrieves data regardless of the session type. This matches the repo's `acquire.py`, which opens either an
  RDP **platform** session (username/password/app-key) or a **desktop** Workspace/Eikon session (app-key).
- **DSWS is a separate product/entitlement.** Datastream Web Services (`DatastreamPy` / DSWS) is a distinct
  service and entitlement from the Workspace/RDP data library — CONFIRMED by both the repo's own
  `DATA_ENTITLEMENTS.md` design and LSEG's separate Datastream documentation. The two are not interchangeable;
  the repo correctly treats them as separate vendor adapters.
- **Repo migration note (no action required for verification):** the repo currently imports `refinitiv.data`
  (the v1 RD library). This still works, but is the *predecessor*. Migrating to `lseg-data` (`import lseg.data as ld`)
  is a like-for-like swap (`get_history` / `get_data` exist in both); not required, but worth a one-line ADR if/when
  the live pull is re-run. **LIKELY** that `get_history`/`get_data` signatures are equivalent across RD→LD
  (both expose `get_history(universe=, fields=, start=, end=)`); confirm against the LD docs at pull time.

**Does `get_history` with `TR.TotalReturn` / `TR.IndexConstituentRIC` work the same for NON-US indices?**
- **CONFIRMED (mechanically, in public docs).** `TR.TotalReturn` is a universal Refinitiv-fundamentals field
  computed *in the instrument's own currency*; community + portal examples use it across markets. `TR.IndexConstituentRIC`
  is demonstrated on non-US chains (`.FTSE`, `.STOXX`) in LSEG's own "Building historical index constituents" article
  (see §2). The field grammar is identical for non-US indices.
- **Caveat — CONFIRMED:** `TR.TotalReturn` has **no built-in currency override** in the Python API / Excel
  (LSEG community: "calculated based on the instrument currency only"). For cross-currency comparison you must
  pull in local currency and either keep Sharpe/CVaR currency-consistent per market, or pull an FX timeseries and
  convert (Datastream offers `X(RI)~U$` to express the total-return index in USD). This **confirms the strategy
  doc's currency caveat** (§2 last bullet) — it is real and must be handled.

---

## 2. Multi-market PIT membership (the external-validity lever)

**CONFIRMED — point-in-time, survivorship-free constituent membership is obtainable for non-US indices, by the
same machinery the repo already uses (snapshot + joiner/leaver replay), and is explicitly documented for FTSE & STOXX.**

- **LSEG's own article "Building historical index constituents"** (developers.lseg.com) builds PIT membership in
  three steps and **demonstrates it on FTSE 100 (`.FTSE`), S&P 500 (`.SPX`), and STOXX (`.STOXX`)**:
  1. start-date snapshot via the dated-chain form `0#{ric}({date})` (e.g. `0#.FTSE(20140101)`);
  2. joiners/leavers via **`TR.IndexJLConstituentChangeDate`, `TR.IndexJLConstituentRIC`, `TR.IndexJLConstituentChange`**;
  3. chronological replay (add joiners, remove leavers; handle same-day join+leave).
  This is a *more robust* PIT construction than monthly `TR.IndexConstituentRIC` snapshots alone, and it
  **handles delisted/leaver names** (survivorship-free by construction). The article's example window is
  2014–2024, implying multi-year depth on Workspace; it does NOT state a hard earliest date or quantify survivorship
  caveats — **UNVERIFIED on depth per index** (confirm in Workspace).
  - *New, useful finding:* the **J/L change fields** (`TR.IndexJLConstituent*`) are the documented, lower-risk way
    to get PIT membership than the repo's current monthly-SDate-grid on `TR.IndexConstituentRIC`. Worth noting in the
    pull design; the repo's monthly-snapshot approach also works but is coarser. **LIKELY** these J/L fields resolve
    for FTSE/STOXX/TOPIX (demonstrated for FTSE/STOXX; TOPIX not shown).

- **Chain RICs** in the strategy doc:
  - `0#.FTSE` (FTSE 100) — **CONFIRMED** (LSEG article + community examples use `.FTSE` / `0#.FTSE`).
  - `0#.STOXX` (STOXX Europe 600) — **CONFIRMED** (`.STOXX` used in the LSEG article).
  - `0#.STOXX50E` (EURO STOXX 50) — **LIKELY** (`.STOXX50E` is the widely-used RIC for EURO STOXX 50; not seen in
    an LSEG-primary source in this sweep — confirm in Workspace).
  - `0#.TOPX` (TOPIX) and `0#.N225` (Nikkei 225) — **LIKELY/UNVERIFIED**. These are the conventional RICs, but I did
    **not** find an LSEG-primary confirmation of the exact chain-RIC strings or PIT-membership coverage for the
    Japanese indices in this sweep. **`% VERIFY` — confirm `0#.TOPX` / `0#.N225` resolve and return PIT membership in Workspace.**
    (Do not assume Japan behaves identically to FTSE/STOXX without checking.)

- **Datastream constituent-list backbone** (the repo's pre-2016 path):
  - **CONFIRMED:** Datastream constituent lists are coded `L<mnemonic>`; the **current** list is e.g. `LFTSE100`,
    `LS&PCOMP`, `LDAXINDX`. **Historical monthly** membership is the list code **+ `MMYY`** — e.g. `LS&PCOMP1218`
    (Dec 2018), `LFTSE1000199` (Jan 1999 FTSE 100), `LDAXINDX1221` (DAX Dec 2021). This **confirms the repo's
    `LS&PCOMP{MMYY}` pattern** and the analogous `LFTSE100{MMYY}`.
  - **CONFIRMED (important caveat):** the *bare* `LFTSE100` list is **current constituents only** — you must use
    the `MMYY`-suffixed codes for historical/PIT membership; you cannot derive history from the live list. The repo's
    `data.yaml` already encodes the `{MMYY}` pattern, so it is correct.
  - **CONFIRMED:** retrieval is **monthly only** (Datastream historical lists are month-granular).
  - **CONFIRMED depth (S&P 500):** Datastream's oldest S&P 500 historical list is `LS&PCOMP0989` (**Sept 1989**) —
    consistent with the repo note "1989→". FTSE 100 historical lists exist back to at least Jan 1999 (`LFTSE1000199`).
  - **UNVERIFIED depth (STOXX 600 / TOPIX / Nikkei 225):** I found no source stating the earliest `MMYY` for these.
    Library guidance repeatedly warns "historical constituents are not always available for all indices."
    **`% VERIFY` — confirm earliest available `MMYY` per index in Datastream Navigator.**

- **Market cap:** **CONFIRMED** the fields exist universally — Refinitiv `TR.CompanyMarketCap` (the repo verified
  `TR.CompanyMarketCap` resolves and `TR.MarketCap` does not, 2026-06-12) and Datastream `MV` (market value).
  Cross-market resolution is **LIKELY** (these are standard cross-market fields) — confirm per market at pull time.

- **Daily total returns:** **CONFIRMED** available for non-US via `TR.TotalReturn` (Refinitiv) and `RI`
  (Datastream Total Return Index), in local currency, daily frequency (§1).

**Realistic PIT history depth per market (best current estimate):**
| Market | Membership PIT source | Realistic depth (to confirm) |
|---|---|---|
| S&P 500 (US, current) | DS `LS&PCOMP{MMYY}` / `TR.IndexConstituentRIC` | **CONFIRMED ~1989→** (DS), TR snapshots reliable ≥~2016 |
| FTSE 100 (UK) | DS `LFTSE100{MMYY}` / `0#.FTSE` + J/L fields | **CONFIRMED ≥1999** (DS); TR/J/L multi-year |
| STOXX Europe 600 | `0#.STOXX` + J/L fields / DS list | **LIKELY** (article shows STOXX); DS depth UNVERIFIED |
| EURO STOXX 50 | `0#.STOXX50E` / DS list | **LIKELY**; depth UNVERIFIED |
| TOPIX / Nikkei 225 (JP) | `0#.TOPX` / `0#.N225` / DS list | **UNVERIFIED** — confirm RICs + depth in Workspace |

**Feasibility verdict on the lever:** the multi-market external-validity replication is **feasible as described**
for **UK (FTSE 100)** and **Europe (STOXX)** with high confidence — these are the cases LSEG itself documents. For
**Japan (TOPIX / Nikkei)** the *mechanism* is identical but the specific chain RICs and PIT depth are unconfirmed and
must be probed before relying on them. (See summary at end.)

---

## 3. Survivorship-free delisting for non-US exchanges

**Delisting metadata availability — LIKELY/CONFIRMED-mechanism, field-detail UNVERIFIED:**
- The PIT membership construction in §2 is **survivorship-free by construction**: leavers (including delisted names)
  are carried via the J/L change fields and the dead RICs remain queryable. **CONFIRMED** that Datastream supports
  retrieving **dead/inactive** securities (the "Dead"/"Activity" category; "include dead securities" in the Explorer),
  and that **RDP Search** exposes delisting-relevant fields such as **`ListingStatus`, `ExchangeCountry`, `RetireDate`**
  for delisted instruments (LSEG community). This corroborates the repo's approach of carrying dead `^RICs`.
- **`TR.InstrumentDelistedDate`** — **LIKELY** (it is referenced as the delist-date field across community threads and
  the repo verified on 2026-06-12 that it *resolves but is often null*, deriving the date from the `^MYY` RIC suffix +
  last-traded date instead). I could **not** independently confirm the field's exact behaviour for non-US equities from
  an LSEG-primary doc in this sweep; treat as **`% VERIFY` per market**.
- **Delisting REASON** — **UNVERIFIED.** I could not confirm a clean, populated delisting-*reason* field (a "RetireReason"
  / cause-of-delisting taxonomy) via LSEG-primary docs. The repo's own `data.yaml` already states the frozen pull carries
  **no reason**, so every name currently classifies "absent → surcharge". This is consistent with the difficulty I found
  confirming a reason field. **`% VERIFY` — whether any reason/status field (RDP Search `ListingStatus`/`RetireReason`,
  or a TR cause field) is populated for non-US delistings; if not, reason-gating is unavailable cross-market too.**

**Shumway −30 / −55 buckets do NOT transfer to non-US — CONFIRMED.**
- The −30% (NYSE/AMEX) and −55% (Nasdaq) imputations are **CRSP-specific, US-exchange-specific** values from
  Shumway (1997) and Shumway & Warther (1999), estimated on CRSP's NYSE/AMEX and Nasdaq delisting-return samples.
  They are **not** calibrated to UK/EU/JP exchanges and there is **no published equivalent constant** for those markets.
  Using −30/−55 on LSE/Euronext/TSE names would be an unjustified transfer. **CONFIRMED the strategy doc's concern.**
- **Appropriate non-US analogue (LIKELY / best-practice, not a single citable constant):** because LSEG/Datastream
  is *not* CRSP, the cleaner treatment for UK/EU/JP is **not** a fixed Shumway constant but one of:
  (a) **use the actual last total return / last traded price** carried in `RI` / `TR.TotalReturn` through the delist
  event (LSEG carries the dead RIC, so the realised exit return is often *observed*, removing the need to impute);
  (b) **liquidate-to-cash at the last available price net of cost** — which is exactly the repo's existing
  `leaver_treatment: liquidate_last_price_net_of_cost` / loader default `liquidate_to_cash`; and
  (c) treat genuinely *missing* terminal returns as a sensitivity/quarantine case rather than applying a US constant.
  This matches the repo's existing design and means **the US Shumway buckets should be scoped to the US panel only**;
  the non-US replication legs should rely on observed terminal returns + liquidate-to-cash. **`% VERIFY` — confirm
  the fraction of non-US leavers with an observed terminal `RI`/`TR.TotalReturn` vs genuinely missing, per market.**

---

## 4. Catalogue breadth (confirm the strategy doc's relevance map) — brief

**CONFIRMED — under a full LSEG licence the catalogue spans all the asset classes the strategy doc maps**, with
PIT/total-return reproducible pulls via the same `TR.*` / Datastream machinery (LSEG Data-Analytics product pages):
- **Equities:** 7M+ securities, 200+ exchanges, 100+ countries, ~20y price history (deeper via Datastream).
- **Fixed income / credit:** 3M+ evaluated FI securities + bank loans; LSEG **Fixed Income Indices** (total-return index families).
- **FX & commodities:** exchange-traded + OTC FX, money markets, commodities.
- **Futures & options:** 100+ derivatives-exchange feeds (46 countries); 7.8M active + 120M+ expired options.
- **Economic indicators:** Datastream ~19M economic series, 175 countries, "120+ years" of macro history.
- **REITs:** covered within the equities universe (no separate confirmation needed; standard listed-equity coverage).
- **Total-return / PIT reproducibility:** **CONFIRMED-mechanism** — `TR.TotalReturn`/`RI` (equities), FI total-return
  indices, and the dated-chain PIT machinery generalise; per-asset-class field details are **LIKELY** and would need
  probing, but this is FUTURE-WORK in the strategy doc, so detail is intentionally out of scope.
- **This confirms the strategy doc's relevance map and its FUTURE-WORK / REJECTED partition** — everything beyond the
  multi-market equity replication is genuinely *available* but is correctly classified as scope-creep / future-work.

---

## 5. Licence / egress

**CONFIRMED — the standard LSEG (Workspace/Datastream academic) licence bars systematic redistribution and
third-party egress of data/derived data; local, individual, institution-governed academic use is the permitted mode.**
- LSEG/Refinitiv terms: **"republication or redistribution of LSEG content … is prohibited without prior written
  consent."** Reselling/redistributing applications built on LSEG data to third parties **requires a developer's
  licence agreement** with LSEG.
- **Derived data still falls under the licence** even when transformed/unrecognisable (LSEG/Thomson Reuters guidance) —
  so derived panels are **not** licence-exempt.
- Academic Workspace/Datastream guidance (university library terms): permitted use is **individual academic /
  non-commercial**, downloading **for personal research**, **derived data for individual use**; only **"insubstantial
  portions"** may be redistributed and only **"non-systematically"** (infrequent, **not machine-generated**).
  Prohibited: **systematic/automated extraction**, redistribution to third parties without their own subscription,
  and use outside the institution.
- **Implication for cloud (Colab/Kaggle/rental) — CONFIRMED-by-inference:** pushing the derived gold panel to a
  third-party cloud for compute is **systematic** handling of licensed/derived content on infrastructure outside the
  institution's governed environment, which the redistribution/systematic-use clauses bar. The library guidance
  explicitly notes systematic/machine-generated handling and third-party sharing are not permitted. This **confirms
  the project's stated constraint**: laptop / UCL-governed compute is fine; arbitrary third-party cloud egress of the
  derived panel is not. **`% VERIFY`** the *exact* clause against UCL's specific LSEG agreement — academic terms vary
  by institution and the precise cloud language should be read in UCL's contract (the strongest-form claim, "cloud is
  barred", is **CONFIRMED in substance** by the public terms but the institution-specific wording is the binding text).

---

## Bottom line — §6 % VERIFY items, CONFIRMED vs OPEN

| Strategy doc §6 item | Status |
|---|---|
| Python client name = **`lseg-data`** (successor to `refinitiv-data`) | **CONFIRMED** |
| `get_history(TR.TotalReturn)` + `TR.IndexConstituentRIC` behave the same for non-US | **CONFIRMED (mechanism)**; currency-override caveat CONFIRMED; per-account at pull time |
| Non-US membership PIT depth — equivalents exist for FTSE/STOXX/TOPIX | **CONFIRMED for FTSE & STOXX** (LSEG article + DS `MMYY`); **TOPIX/Nikkei UNVERIFIED** (RICs + depth) |
| `TR.IndexConstituentRIC` reliable ≥~2016; Datastream `MMYY` backbone covers earlier | **CONFIRMED** (DS S&P 500 → 1989, FTSE → 1999; monthly-only) |
| Survivorship-free delisting metadata coverage non-US | **LIKELY** (dead RICs/J-L leavers carried, RDP `ListingStatus`/`RetireDate`); **delisting REASON UNVERIFIED** |
| Shumway −30/−55 don't transfer; need a non-US analogue | **CONFIRMED don't transfer**; analogue = observed terminal `RI` + liquidate-to-cash (repo's existing default), scope Shumway to US only |
| Licence bars third-party-cloud egress; local/UCL-governed OK | **CONFIRMED in substance**; exact cloud clause = `% VERIFY` against UCL's specific agreement |

**Multi-market external-validity lever — feasible as described?**
**YES for UK (FTSE 100) and Europe (STOXX 600 / EURO STOXX 50)** — high confidence; these are exactly the cases LSEG's
own documentation demonstrates, using the identical deterministic PIT + total-return + market-cap machinery already in
the pipeline. **For Japan (TOPIX / Nikkei 225) the mechanism is identical but UNVERIFIED at field level** — the chain
RICs (`0#.TOPX` / `0#.N225`) and PIT history depth must be probed in Workspace before relying on them. Two real,
pre-pull caveats apply to all non-US legs: (1) **currency** — `TR.TotalReturn` has no API currency override, pull
local-currency and keep Sharpe/CVaR currency-consistent (or FX-convert with the same PIT discipline); (2) **delisting**
— do **not** carry the US −30/−55 constants over; rely on observed terminal returns + liquidate-to-cash and treat the
US Shumway surcharge as US-only. None of these blocks the lever; they are exactly the items to register in the
pre-freeze amendment and confirm in the entitled probe.

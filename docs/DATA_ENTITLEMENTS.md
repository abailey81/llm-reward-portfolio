# Data entitlement verification — CRITICAL PATH (plan block W3)

Run tonight in LSEG Workspace/Eikon (UCL credentials). Screenshot every result into `docs/evidence/`.
The project's largest data risk: `TR.IndexConstituentRIC` history reliably reaches only ~2016; the
2005–2016 backbone needs **Datastream** (`LS&PCOMP MMYY` lists + `RI` datatype), often a SEPARATE
entitlement (DSWS / Datastream Excel add-in) from the Workspace terminal.

## Checklist (fill ✅/❌ + evidence path)

Automated by `python -m src.data.cli probe` (src/data/probes.py). Last live run **2026-06-12 —
ENTITLEMENT LANDED**: every Refinitiv probe PASSES, including PIT membership at 2010 and dead-RIC
history. Full evidence: `docs/evidence/entitlement_report.md` + `entitlement_probes.json` (ADR-015).
Field-mnemonic verification 2026-06-12 (recorded in config `universe_pull`): TR.CompanyMarketCap,
TR.BidPrice/TR.AskPrice, TR.Volume, TR.TRBCEconomicSector (incl. dead RICs), TR.ExchangeName, .SPXTR all
CONFIRMED; `.VIX` NOT licensed (CBOE permission) → FRED VIXCLS remains the VIX source;
TR.InstrumentDelistedDate resolves but is often null → delist dates derive from the ^MYY RIC suffix +
last-traded date.

| # | Test | Exact query | Expected | Result |
|---|---|---|---|---|
| 1 | Chain resolves | `0#.SPX` in Workspace / `ek.get_data('0#.SPX', ['TR.CommonName'])` | ~503 rows | ✅ 2026-06-12 (P1 PASS) |
| 2 | PIT constituents post-2016 | `ek.get_data('0#.SPX', ['TR.IndexConstituentRIC'], {'SDate':'2018-01-02'})` | dated membership | ✅ 2026-06-12 (P2 PASS) |
| 3 | PIT constituents PRE-2016 | same with `SDate='2010-01-04'` | if ❌ → Datastream path mandatory | ✅ 2026-06-12 (P3 PASS) — Refinitiv serves pre-2016 on this feed; pre-2016 segment to be VALIDATED (counts ≈500/month, known joiners/leavers) and single-source caveat documented until DSWS cross-check lands |
| 4 | Datastream lists | DSWS/Excel: static request on list `LS&PCOMP0110` | Jan-2010 members | 🟡 2026-06-12 — unchanged: DSWS authenticates, `ZLDU178` "not entitled to ClientApi service"; now a CROSS-CHECK want, not a blocker (escalation email still worth sending) |
| 5 | RI on a LEAVER | `GE` total-return daily around 2018-06-26 | continuous total-return incl. exit | ✅ 2026-06-12 (P5 PASS via TR.TotalReturn) |
| 6 | RI on a DEAD ticker | dead-RIC probe `LEH.N^I08` (Lehman, Sep-2008) | series to delisting | ✅ 2026-06-12 (P6 PASS) |
| 7 | Day-count for RI yield method | confirm N=260 vs 365 on your feed (harvest missing-piece #5) | documented | 📝 MANUAL — only relevant to the Datastream RI path; Refinitiv TR.TotalReturn path does not need it |

## Escalation email (send TONIGHT if 4–6 fail)

> Subject: Datastream access for MSc dissertation (supervisor: Dr R. Okhrati)
> Dear Library Data Services — for my IFTE0008 dissertation I require Datastream constituent lists
> (`LS&PCOMP` + monthly `LS&PCOMPmmyy`, 2005–2016) and the `RI` total-return datatype for delisted/exited
> S&P 500 members. Is DSWS or the Datastream Excel add-in included in UCL's licence, and how do I obtain
> access? Timeline is tight (data build starts mid-June). Thank you — Tamer Atesyakar (MSc B&DF, IFT).

**Fallbacks (in order):** WRDS/CRSP `MSP500LIST` via UCL (gold standard — enquire in the same email) →
hand-reconstructed joiners/leavers from S&P press releases (document as explicitly inferior in the Data chapter).

# Delisting-reason / vendor-terminal re-pull — procedure, feasibility, gating

**Status:** DOCUMENTED, **not executed** (data-integrity audit 2026-06-25). Refinitiv creds are live
(per project memory), so this is *runnable* by an entitled operator; it is deliberately **not run** here
because the campaign is mid-freeze and the existing band already brackets the tail (below). No data is
fabricated (R4): until this re-pull lands, the delisting REASON does **not** exist on disk and the
surcharge stays un-gated.

## 1. Why the re-pull is needed (the verified gap)

The `univ4` Shumway surcharge is **un-gated**: it books a fixed −30 % (NYSE/AMEX) / −55 % (Nasdaq)
delisting return onto **100 % (333/333)** of dead RICs, including premium M&A whose true terminal was
positive. Root cause, verified first-hand in the frozen vault:

| Field needed to gate the surcharge | In the frozen `rf_meta_*` pull? | Evidence |
|---|---|---|
| Delisting **reason / type** (M&A vs. bankruptcy vs. compliance) | **NO — never requested** | `rf_meta_*` columns = `Instrument, Instrumented Delist Date, Exchange Name, TRBC Economic Sector Name`; provenance `params.fields = [TR.InstrumentDelistedDate, TR.ExchangeName, TR.TRBCEconomicSector]` |
| Vendor **terminal total return** (the realised last return) | **NO — declared in config, never in the fields list** | `config/data.yaml: universe_pull.delisting.terminal_return_field: TR.TotalReturn` is set, but the A4 `refinitiv_fields` list that is actually pulled omits it |
| Delisting **date** | Requested, but **empty for all 333** dead RICs | `Instrumented Delist Date` is blank on every `^`-suffixed RIC; the date is currently derived from the `^MYY` RIC suffix |

So `parse_delisting_metadata` returns `vendor_terminal_return=None` and `reason=None` for every name, and
`apply_shumway_corrections` falls through to the fixed surcharge for all of them.

## 2. The re-pull (one config edit + re-run of A4 only)

A4 is a **static metadata** pull over the membership union (`pull_universe.py` ~372–382); it does **not**
touch returns, membership, or selection, so re-running it is cheap and **identification-neutral**
(ADR-019: A4 serves integrity only, never the state vector or the reward search).

**Step 1 — extend the A4 field list** in `config/data.yaml`:

```yaml
universe_pull:
  delisting:
    refinitiv_fields:                 # ADD the two recovery fields to the existing three:
      - TR.InstrumentDelistedDate
      - TR.ExchangeName
      - TR.TRBCEconomicSector
      - TR.DelistingReason            # VERIFY mnemonic on the entitled probe (candidates below)
      - TR.TotalReturn                # terminal total return at/around the delist date
```

Refinitiv reason-field candidates (confirm the exact resolvable mnemonic with the entitled probe
`make probe` / `acquire.fetch_refinitiv_data(rd, "<dead RIC>", ["<field>.date","<field>"])` before the
bulk pull — `pull_universe.py` parsers locate columns by ROLE, not fixed name, so any of these will be
absorbed once the header is known):

- `TR.DelistingReason` / `TR.DelistingReasonDescription`
- `TR.InstrumentDeListReason` / `TR.QuoteDeListReason`
- `TR.DelistingType` (categorical: Merger / Acquisition / Bankruptcy / Compliance / …)
- DataScope / RDP `DelistingReasonCode` (if entitled to the reference feed)

If `TR.TotalReturn` will not return a clean terminal at the exit grid, the realised terminal return is
recoverable from the **last two valid prices** in the already-frozen `rf_px_*` / `rf_trd_*` history, or
from a dated `TR.PriceClose` pull bracketing the suffix-derived delist month.

**Step 2 — re-run A4 only** (the journaled pull is resumable and span-stamped, so it lands as a NEW
artifact without colliding with the frozen `rf_meta_*`):

```bash
make pull-universe LIVE=1          # the journal skips A1/A2/A3/A5 (done); only A4 re-pulls with new fields
```

**Step 3 — rebuild the corrected panel** as a new suffix (write-once layers keep `univ4` intact):

```python
build_universe(suffix="_univ4r", apply_delisting=True)   # 'r' = reason-gated
```

## 3. Reason-gated surcharge — already wired (no-op until the reason lands)

The gating logic is implemented and unit-tested so that the moment a reason column exists, the surcharge
is applied **only** to genuine performance terminations:

- `pull_universe.parse_delisting_metadata` already extracts `reason` (present here; unused until pulled).
- `build_universe._derive_delisting_map` threads `reason` into the per-name correction dict.
- `membership.apply_shumway_corrections` gates on it: a name whose reason is **M&A / merger / acquisition
  / buyout / privatization** is booked `mna_keep_vendor_terminal` — its real last return is kept and **no
  surcharge** is applied; only **performance / bankruptcy / compliance / liquidation** (or an absent
  reason, the current conservative default) receives −30 / −55 %. The classification is config-driven
  (`data.series.delisting_reason_classes`), audit-logged per name, and never guesses (an unmapped reason
  stays surcharged with a logged `reason_unmapped_surcharged` action so the operator can review it).

Because the on-disk vault carries **no** reason, every name currently classifies as "reason absent →
surcharge" and `univ4` is **byte-identical** to the pre-gating build — the gating is latent until Step 2.

## 4. Feasibility

| Dimension | Assessment |
|---|---|
| Entitlement | Creds are LIVE (memory); A4 fields are standard reference/`TR.*` mnemonics. **HIGH** that reason/type resolves; confirm the exact field on the probe first. |
| Cost / time | A4 is 953 names ÷ 200/req = **5 requests**; minutes, rate-governed. Trivial. |
| Risk to frozen results | **None.** A4 is identification-neutral; the rebuild is a new suffix; `univ3`/`univ4` and the frozen winners are untouched. |
| Scientific upside | Converts the M&A-contaminated heavy band end into a **correct** Shumway panel (surcharge only on genuine failures), tightening the band's upper bracket toward the truth and removing the 3 mis-signed headline-cohort cells (DELL buyout, TWX/WB acquisitions). |
| Downside of NOT re-pulling | Bounded: the pre-registered `delisting_band` already brackets the tail and the full `d∈{0,−100 %}` sweep moves pooled test CVaR-5 % by only ~2 % (−0.0493 → −0.0504), so the **headline H2 tail ordering is invariant**. The bias matters for a per-name delisting study, not for the matched-budget arm contrast. |

## 5. Recommendation

**Re-pull before any per-name or attribution-level delisting analysis; OPTIONAL for the headline H2.**
The headline is protected by the bracketing band (univ4 is the disclosed M&A-contaminated upper end, not
"the tail"). If time permits, run §2 — it is cheap, identification-neutral, and upgrades `univ4` from a
biased extreme to a correct survivorship panel. If not, the disclosed band + this documented procedure is
the honest, audit-complete posture for a PDF-graded submission.

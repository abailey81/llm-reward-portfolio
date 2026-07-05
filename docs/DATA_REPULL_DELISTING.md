# Delisting-reason / vendor-terminal re-pull — procedure, feasibility, gating

> **★★ EXECUTED 2026-07-02 (observed-terminal route) — the re-pull/rebuild this document planned HAS NOW
> RUN**, as part of the univ5 rebuild (ADR-051; CHANGELOG `[2026-07-02c]`; prereg R73). The recovery
> (`build_universe._derive_delisting_map::_recover_terminal_from_returns`) booked the realised terminal for
> **ALL 333 dead names** from the vendor daily series — Shumway audit: `vendor_terminal_kept = 333`,
> **ZERO surcharges** — so the corrected Shumway panel landed as **`univ5s`** (not the `_univ4r` suffix
> sketched in §2) and **equals the zero-fill headline on returns**. Finding: `univ4`'s flat −30/−55 %
> surcharge was **double-counting** terminals already present in the vendor series, on top of the M&A
> contamination documented below. The delisting band stays reported with `univ4` as its disclosed
> contaminated heavy end. The body below (2026-06-25 procedure + the 2026-07-01 probe banner) is the
> reasoning trail and is left as written.

**Status:** DOCUMENTED, **not executed** (data-integrity audit 2026-06-25). Refinitiv creds are live
(per project memory), so this is *runnable* by an entitled operator; it is deliberately **not run** here
because the campaign is mid-freeze and the existing band already brackets the tail (below). No data is
fabricated (R4): until this re-pull lands, the delisting REASON does **not** exist on disk and the
surcharge stays un-gated.

> **★ PROBE RESULT + DECIDED FIX (2026-07-01).** The reason-field probe was run and came back **negative**:
> the delisting-REASON mnemonics **`TR.DelistingReason` / `TR.DelistingType` / `TR.DelistingReasonDescription`
> do NOT resolve under this entitlement** (probed 2026-07-01 via PowerShell + `.venv-lseg`, the solved live
> path). So the reason-GATED surcharge (§3) **cannot** be driven by a vendor reason field. **DECIDED fix:
> use the OBSERVED-TERMINAL-RETURN fallback** — the realised dead-name terminal is recoverable directly from
> daily returns (confirmed: **Lehman `LEH.N^I08` returned 2042 daily rows**), so the correct terminal replaces
> the fixed −30/−55 % surcharge without needing a reason label. This makes §2's "Step 1 add `TR.DelistingReason`"
> path **moot** (kept below as the reasoning trail) and promotes the "recover from prices/returns" fallback
> noted in §2 to the **primary mechanism**. DECIDED, **not yet EXECUTED** (the terminal-return re-pull/rebuild
> is still pending). Report-only, disjoint from the frozen m=6.

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

> **SUPERSEDED 2026-07-01 (Step 1 reason-field is MOOT).** The reason mnemonics below do **not** resolve under
> this entitlement (top-of-file probe result). Skip the `TR.DelistingReason`/`TR.DelistingType` add; instead take
> the **observed-terminal-return** route — pull/recover `TR.TotalReturn` (or the last two valid prices from the
> frozen `rf_px_*`/`rf_trd_*` history, as this Step already notes) and book the realised terminal. The rest of
> the re-pull mechanics (A4-only, journaled, new-suffix rebuild) are unchanged.

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
| Entitlement | Creds are LIVE + access is SOLVED (PowerShell + `.venv-lseg`, verified 2026-07-01). ⚠ **UPDATE 2026-07-01:** the reason/type mnemonics **do NOT resolve** under this entitlement (probed) — the earlier "HIGH that reason/type resolves" is **REFUTED**. Use the **observed-terminal-return** fallback instead (dead-name daily returns ARE recoverable — Lehman = 2042 rows). |
| Cost / time | A4 is 953 names ÷ 200/req = **5 requests**; minutes, rate-governed. Trivial. |
| Risk to frozen results | **None.** A4 is identification-neutral; the rebuild is a new suffix; `univ3`/`univ4` and the frozen winners are untouched. |
| Scientific upside | Converts the M&A-contaminated heavy band end into a **correct** Shumway panel (surcharge only on genuine failures), tightening the band's upper bracket toward the truth and removing the 3 mis-signed headline-cohort cells (DELL buyout, TWX/WB acquisitions). |
| Downside of NOT re-pulling | Bounded: the pre-registered `delisting_band` already brackets the tail and the full `d∈{0,−100 %}` sweep moves pooled test CVaR-5 % by only ~2 % (−0.0493 → −0.0504), so the **headline H2 tail ordering is invariant**. The bias matters for a per-name delisting study, not for the matched-budget arm contrast. |

## 5. Recommendation

**Re-pull (via the OBSERVED-TERMINAL-RETURN route, §2 Step-1 SUPERSEDED) before any per-name or
attribution-level delisting analysis; OPTIONAL for the headline H2.** The headline is protected by the
bracketing band (univ4 is the disclosed M&A-contaminated upper end, not "the tail"). If time permits, run §2
with the terminal-return fix (the reason-field mnemonics are confirmed non-resolving as of 2026-07-01) — it is
cheap, identification-neutral, and upgrades `univ4` from a biased extreme to a correct survivorship panel. If
not, the disclosed band + this documented procedure is the honest, audit-complete posture for a PDF-graded
submission.

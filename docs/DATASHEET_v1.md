# Datasheet v1 — generated 2026-06-10 (Gebru et al., CACM 2021; auto-filled from data/manifest)

## Motivation
Created to answer the pre-registered research question (PREREGISTRATION §1): LLM-evolved rewards under distributional feedback vs hand-designed rewards on a **953-name survivorship-free point-in-time Refinitiv/LSEG universe (top-30 selected per window)**, 2005–2025. Funded/required by the UCL MSc IFTE0008 dissertation; no commercial purpose.

## Composition
> ⚠ **STALE (note added 2026-06-25).** The artifact/row counts below are an auto-fill from an early
> *pilot* manifest and **predate the univ3 freeze**. They do **not** describe the frozen campaign gold,
> which is `data/gold/returns_panel_univ3.parquet` at **5,283 × 953** (survivorship-free, point-in-time;
> Refinitiv/LSEG). Kept verbatim for provenance only — see CLAUDE.md "Post-merge context" and
> `01_literature/DATASETS.md`.
**Frozen campaign gold (univ3, the real panel):** `data/gold/returns_panel_univ3.parquet` —
**5,283 trading days × 953 RICs**, survivorship-free point-in-time (Refinitiv/LSEG), with **333
delisting cells** and a fixed **30-name development cohort** (the 2005 cohort).

## Collection process
Pulled via src/data/acquire.py (journaled, rate-governed, provenance-sidecar'd) from vendors: Refinitiv/LSEG, derived, fred, kenfrench, merged, yfinance. Entitlement evidence: docs/evidence/entitlement_report.md.

## Preprocessing / cleaning / labeling
Medallion pipeline (src/data): structural validation, corporate-action integrity, Ince–Porter screens (flag-only), Shumway delisting corrections (logged), missing-data taxonomy with zero interpolation (R4). Raw layer is immutable; every transform is lineage-recorded.

> **Integrity-screen scope correction (data-integrity audit 2026-06-25).** The Ince–Porter + split-artifact screens above are run by **two** code paths, and their coverage of the *research* panel was overstated before this correction. `cli.cmd_build` (the **yfinance pilot/shadow** path) runs them on `rets_yf`. The **Refinitiv research builder** `build_universe.py` (which produces the headline `univ3`/`univ4` gold) **did not call `integrity.*` at all** — so the claim above was true of the pilot path but **not** of the research panel. It is now true of both: `build_universe(screen=True)` runs `integrity.ince_porter_flags` + `split_artifact_flags` + the new `forward_split_artifact_flags` (positive +100/+200/+300 % total-return analogue) over the research returns and freezes the **flag report** `integrity_report_<suffix>.parquet` (CLEAN layer). Screened research panel materialised as **`univ3s`** (`returns_panel_univ3s.parquet`, **byte-identical returns** to `univ3` — screens are FLAG-ONLY, R4 — plus the evidence log). On the real panel the screens flag **24 cells**: 22 unadjusted price-side −50/−66.7 % split signatures + 2 forward-split (+200 % `JCI.N^I16` 3:1 Oct-2007; +98 % `CAR.OQ`). The `min_prior_price_usd` $1 screen needs an **unadjusted** price; the frozen `rf_px_` (TRDPRC_1) panel is **split-adjusted** (NVDA reads $0.197 in 2005), so it is NOT fed to that screen on the research path (it would false-flag every later-split high-flyer) — the $1 screen requires a gated unadjusted-price re-pull (`docs/DATA_REPULL_DELISTING.md`). Known residual artifacts the panel still carries (flagged, not mutated — they ARE the tail signal vs. an error is the data-chapter's adjudication): `FTR.OQ^D20` +278.9 % (2020 reverse-split, below the +300 % Ince–Porter reversal threshold and partner-free, so it does NOT trip that screen) and the +200 % `JCI.N^I16`.

> **Delisting-return M&A bias — disclosed limitation (data-integrity audit 2026-06-25).** The Shumway delisting corrections behind the `univ4` panel are **un-gated**: Refinitiv's frozen `rf_meta_*` metadata pull contains only `TR.InstrumentDelistedDate` (verified **empty for all 333** dead RICs), `TR.ExchangeName`, `TR.TRBCEconomicSector` — **no delisting REASON and no terminal `TR.TotalReturn`** were ever pulled. Consequently `apply_shumway_corrections` finds `vendor_terminal_return=None` for **100 % (333/333)** of delistings and books the fixed **−30 %/−55 %** surcharge **unconditionally**, including on premium **M&A/mergers** whose true terminal was positive/neutral. Verified test-window (2018–2025) examples booked at a fabricated loss: `ABMD→J&J` (−54.97 %), `ALTR→Intel` (−54.97 %), `AGN→AbbVie` (−29.99 %), `CELG→BMS`, `RHT→IBM`, `TWX→AT&T`, `ATVI→Microsoft`, `XLNX→AMD`, `ALXN→AstraZeneca`. **3 of the 30 headline (2005-cohort) names** are affected: `DELL.OQ^J13` (2013 buyout: univ3 +0.29 % → univ4 −54.87 %), `TWX.N^F18` (+0.84 % → −29.41 %), `WB.N^A09` (crisis acquisition, −3.32 % → −32.32 %). **Mitigation, not a fix:** the surcharge cannot be reason-gated from the on-disk vault (the reason was never pulled; fabricating one is barred, R4), so `univ4` is **NOT** reported as the true tail — it is the **M&A-contaminated heavy END of a pre-registered delisting-return sensitivity band** `d∈{0, −30, −55, −100 %}` (`analyze_campaign.delisting_band`); `univ3` (zero-fill) is the **too-light 0 % end**; the truth lies **inside** the band. Empirically the entire sweep moves the pooled test CVaR-5 % only ~**2 %** (−0.0493 → −0.0504), so the **headline tail ordering is invariant** to the assumption even though the bias would badly distort a per-name delisting study. The reason-gated surcharge re-pull is documented (`docs/DATA_REPULL_DELISTING.md`), not executed.

## Uses
Training/evaluating deep-RL portfolio policies inside this dissertation only; vendor licence terms prohibit redistribution of raw data — the repo ships manifests, not payloads.

## Distribution
NOT distributed. SHA-256 manifests + pull provenance allow an entitled party to reproduce byte-exact artifacts.

## Maintenance
Maintained by the author until dissertation submission (2026-09-01); manifest + ADR log document every change.

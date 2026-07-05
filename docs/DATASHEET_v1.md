# Datasheet v1 — generated 2026-06-10 (Gebru et al., CACM 2021; auto-filled from data/manifest)

## Motivation
Created to answer the pre-registered research question (PREREGISTRATION §1): LLM-evolved rewards under distributional feedback vs hand-designed rewards on a **963-name survivorship-free point-in-time Refinitiv/LSEG universe (top-30 selected per window)**, 2005–2026 (settled 2026-06-30 cutoff; 953 names / 2005–2025 before the 2026-07-02 extension recorded below). Funded/required by the UCL MSc IFTE0008 dissertation; no commercial purpose.

## Composition
> ⚠ **STALE (note added 2026-06-25).** The artifact/row counts below are an auto-fill from an early
> *pilot* manifest and **predate the univ3 freeze**. They do **not** describe the frozen campaign gold,
> which is `data/gold/returns_panel_univ3.parquet` at **5,283 × 953** (survivorship-free, point-in-time;
> Refinitiv/LSEG). Kept verbatim for provenance only — see CLAUDE.md "Post-merge context" and
> `01_literature/DATASETS.md`. *(Since 2026-07-02 the ACTIVE gold is **univ5** — see the dated
> extension section below; univ3 is now the frozen pre-Split-C reference.)*
**Active campaign gold (univ5, the real panel — since 2026-07-02):**
`data/gold/returns_panel_univ5.parquet` — **5,406 trading days × 963 RICs**, 2005-01-03 → 2026-06-30
(settled cutoff), survivorship-free point-in-time (Refinitiv/LSEG), selected by the hash-bound
`config/data.yaml: gold.suffix: univ5`, with **333 delisting cells** (each dead name's realised
terminal return verified present in the vendor daily series — see the 2026-07-02 section) and a fixed
**30-name development cohort** (the 2005 cohort). **univ3** (`returns_panel_univ3.parquet`,
**5,283 × 953**, 2005–2025) is retained as the **frozen pre-Split-C reference**; univ5 reproduces it
byte-exactly on the full overlap (0 changed cells, verified).

## Collection process
Pulled via src/data/acquire.py (journaled, rate-governed, provenance-sidecar'd) from vendors: Refinitiv/LSEG, derived, fred, kenfrench, merged, yfinance. Entitlement evidence: docs/evidence/entitlement_report.md.

## Preprocessing / cleaning / labeling
Medallion pipeline (src/data): structural validation, corporate-action integrity, Ince–Porter screens (flag-only), Shumway delisting corrections (logged), missing-data taxonomy with zero interpolation (R4). Raw layer is immutable; every transform is lineage-recorded.

> **Integrity-screen scope correction (data-integrity audit 2026-06-25).** The Ince–Porter + split-artifact screens above are run by **two** code paths, and their coverage of the *research* panel was overstated before this correction. `cli.cmd_build` (the **yfinance pilot/shadow** path) runs them on `rets_yf`. The **Refinitiv research builder** `build_universe.py` (which produces the headline `univ3`/`univ4` gold) **did not call `integrity.*` at all** — so the claim above was true of the pilot path but **not** of the research panel. It is now true of both: `build_universe(screen=True)` runs `integrity.ince_porter_flags` + `split_artifact_flags` + the new `forward_split_artifact_flags` (positive +100/+200/+300 % total-return analogue) over the research returns and freezes the **flag report** `integrity_report_<suffix>.parquet` (CLEAN layer). Screened research panel materialised as **`univ3s`** (`returns_panel_univ3s.parquet`, **byte-identical returns** to `univ3` — screens are FLAG-ONLY, R4 — plus the evidence log). On the real panel the screens flag **24 cells**: 22 unadjusted price-side −50/−66.7 % split signatures + 2 forward-split (+200 % `JCI.N^I16` 3:1 Oct-2007; +98 % `CAR.OQ`). The `min_prior_price_usd` $1 screen needs an **unadjusted** price; the frozen `rf_px_` (TRDPRC_1) panel is **split-adjusted** (NVDA reads $0.197 in 2005), so it is NOT fed to that screen on the research path (it would false-flag every later-split high-flyer) — the $1 screen requires a gated unadjusted-price re-pull (`docs/DATA_REPULL_DELISTING.md`). Known residual artifacts the panel still carries (flagged, not mutated — they ARE the tail signal vs. an error is the data-chapter's adjudication): `FTR.OQ^D20` +278.9 % (2020 reverse-split, below the +300 % Ince–Porter reversal threshold and partner-free, so it does NOT trip that screen) and the +200 % `JCI.N^I16`.

> **Delisting-return M&A bias — disclosed limitation (data-integrity audit 2026-06-25).** The Shumway delisting corrections behind the `univ4` panel are **un-gated**: Refinitiv's frozen `rf_meta_*` metadata pull contains only `TR.InstrumentDelistedDate` (verified **empty for all 333** dead RICs), `TR.ExchangeName`, `TR.TRBCEconomicSector` — **no delisting REASON and no terminal `TR.TotalReturn`** were ever pulled. Consequently `apply_shumway_corrections` finds `vendor_terminal_return=None` for **100 % (333/333)** of delistings and books the fixed **−30 %/−55 %** surcharge **unconditionally**, including on premium **M&A/mergers** whose true terminal was positive/neutral. Verified test-window (2018–2025) examples booked at a fabricated loss: `ABMD→J&J` (−54.97 %), `ALTR→Intel` (−54.97 %), `AGN→AbbVie` (−29.99 %), `CELG→BMS`, `RHT→IBM`, `TWX→AT&T`, `ATVI→Microsoft`, `XLNX→AMD`, `ALXN→AstraZeneca`. **3 of the 30 headline (2005-cohort) names** are affected: `DELL.OQ^J13` (2013 buyout: univ3 +0.29 % → univ4 −54.87 %), `TWX.N^F18` (+0.84 % → −29.41 %), `WB.N^A09` (crisis acquisition, −3.32 % → −32.32 %). **Mitigation, not a fix:** the surcharge cannot be reason-gated from the on-disk vault (the reason was never pulled; fabricating one is barred, R4), so `univ4` is **NOT** reported as the true tail — it is the **M&A-contaminated heavy END of a pre-registered delisting-return sensitivity band** `d∈{0, −30, −55, −100 %}` (`analyze_campaign.delisting_band`); `univ3` (zero-fill) is the **too-light 0 % end**; the truth lies **inside** the band. Empirically the entire sweep moves the pooled test CVaR-5 % only ~**2 %** (−0.0493 → −0.0504), so the **headline tail ordering is invariant** to the assumption even though the bias would badly distort a per-name delisting study. The reason-gated surcharge re-pull is documented (`docs/DATA_REPULL_DELISTING.md`), not executed. **[Supersession 2026-07-02: the re-pull HAS now executed via the observed-terminal route — see the "2026-07-02 extension + rebuild (univ5)" section below. The finding sharpens this note: the −30/−55 % surcharge was not merely mis-gated, it DOUBLE-COUNTED terminals already present in the vendor daily series.]**

## 2026-07-02 extension + rebuild (univ5)
Records the one coordinated data event executed between the 2026-06-12 frozen pull and the campaign
(ADR-044 ratified the plan; ADR-051 + addendum recorded the execution parameters and the incident;
prereg amendment R73; CHANGELOG `[2026-07-02c]`). All decisions were recorded **before** any data was
touched; nothing here is results-contingent (the campaign has not run).

**Settled-cutoff extension + Split C.** The panel was extended to **2026-06-30** — the latest *settled*
month-end (clean quarter boundary, T+1-settled days before the pull, no partial-period ambiguity) —
via a **dedicated, journaled extension pull** (`data_pipeline/scripts/extend_universe_2026.py`;
PowerShell + `.venv-lseg`; 138/138 chunks frozen, 0 failed), NOT a config-span re-run (chunk ids are
parameter-hashed, so changing `period.end` would have re-keyed and re-pulled all 21 years). The pull
covered A1′ joiner/leaver membership events, A2′ returns, A3′ monthly caps, A4′ metadata, A5′
price/bid-ask/volume, and SPXTR for the extension window; `refresh_fred_2026.py` refreshed the FRED
series (VIX/rf/term) keylessly to the cutoff; `build_univ5.py` built the panels. A first build was
poisoned by a pipeline-config window clip (no 2026 sessions) and was surgically removed with the new
guarded `purge_suffix.py` (36 files + 53 ledger lines, all verified never-consumed; the tool refuses
protected/active suffixes) before the correct rebuild; the vault-root junction
`data_pipeline/data → data` repaired the ADR-022 merge split. Splits moved to **SPLIT C**: train
2005-01-01→2016-12-31 · val 2017-01-01→2019-12-31 · test 2020-01-01→2026-06-30 (sealed; spans the
2020 COVID stress, the 2022 hiking cycle, the 2023–25 rally, and settled H1-2026). With the
inter-split purge max(embargo 21, lookback 60) = 60 sessions, the executed val start is
**2017-03-30** and the executed test start **2020-03-30**; the resolved integer windows are recorded
and fail-loud-asserted as `expected_windows.univ5 = [60,3021] / [3081,3775] / [3835,5406]`
(`config/inference.yaml`). The panel identity is hash-bound via `config/data.yaml: gold.suffix: univ5`.

**Byte-diff referee (extension ≠ revision).** `verify_gold` univ5-vs-univ3: **0 changed cells**
(max |Δ| = 0.000e+00) over the full 5,283 × 953 overlap; the extension contributes **+123 sessions**
(2026-H1) and **+10 new-member columns** only. The overlap identity was re-verified first-hand for
this datasheet update (0 changed cells).

**Vendor-drift incident (EVHC.N^L16) + the SPLICE rule.** Exactly the class of provenance event a
datasheet exists to record: between the frozen pull (2026-06-12) and the extension pull (2026-07-02),
Refinitiv **backfilled the Dec-2016 leaver event** for `EVHC.N^L16`; with its join counterpart
missing/re-keyed, the fresh reverse event-replay claimed S&P 500 membership for the name back to 2004
(145/254 overlap months). This is provably an artifact — old-EVHC (Envision Healthcare Holdings)
IPO'd Aug-2013, merged into AMSURG 2016-12-01, NYSE delisting 2016-12-13 (the `^L16` suffix; SEC Form
25-NSE) — and provably immaterial here (~$7 B peak cap, never remotely top-30, so the top-30 book is
invariant either way). The extension driver's **hard-fail overlap gate caught it on first live
contact**. Resolution = the **SPLICE rule**, now in the driver: the frozen membership record stays
**authoritative through its own last month (2025-12)**; the fresh replay contributes **only the 2026
month-ends**; overlap differences must fall inside an **enumerated, externally-verified allowlist**
({`EVHC.N^L16`}) or the rebuild hard-fails, and the extension's month-ends and member counts are
themselves gated (6 months ending 2026-06-30; 495–510 members). Frozen history is thereby immune to
silent vendor event-history revision — first-hand evidence for why the pre-registered frozen record +
hash discipline exists.

**Delisting finding — zero surcharges; the univ4 surcharge double-counted.** The OBSERVED-terminal
recovery (`build_universe._derive_delisting_map::_recover_terminal_from_returns`, ADR-051; the route
`docs/DATA_REPULL_DELISTING.md` planned after the reason mnemonics proved non-resolving) recovered the
realised terminal return for **ALL 333 dead names** directly from the vendor daily series (Shumway
audit: `vendor_terminal_kept = 333`, **zero surcharges booked**). Consequence: the corrected Shumway
panel **univ5s equals the zero-fill headline on returns** — and `univ4`'s unconditional −30/−55 %
surcharge is now known to have **double-counted terminals already present in the vendor daily
series**, on top of its M&A contamination documented in the 2026-06-25 note above. The pre-registered
delisting-return band d ∈ {0, −30, −55, −100 %} is still reported, with `univ4` as its **disclosed
contaminated heavy end**; what the band brackets now is residual post-delisting (off-exchange) value
loss, not a missing terminal. Naming caveat: the `s` suffix is overloaded — `univ3s` = the
integrity-SCREENED univ3 (flag-only screens), while `univ5s` = the SHUMWAY-corrected univ5. The
flag-only integrity screens were **not** re-materialised as a univ5-suffixed screened panel;
`integrity_report_univ3s` remains the screening evidence for the overlapping span.

**The 10 new members (2026-H1 joiners; new union minus old union):** `CASY.OQ`, `COHR.N`, `ECHO.OQ`,
`FDXF.N` (the 2026 FedEx-Freight spinoff), `FLEX.OQ`, `HONA.OQ` (the 2026 Honeywell-Aerospace
spinoff), `LITE.OQ`, `MRVL.OQ`, `VEEV.N`, `VRT.N`. Brand-new joiners received full-window pulls
(pre-listing emptiness journals as `skipped_empty`); none affects the fixed 2005-cohort development
top-30.

## Uses
Training/evaluating deep-RL portfolio policies inside this dissertation only; vendor licence terms prohibit redistribution of raw data — the repo ships manifests, not payloads.

## Distribution
NOT distributed. SHA-256 manifests + pull provenance allow an entitled party to reproduce byte-exact artifacts.

## Maintenance
Maintained by the author until dissertation submission (2026-09-01); manifest + ADR log document every change.

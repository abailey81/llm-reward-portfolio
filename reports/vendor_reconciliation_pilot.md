# Vendor reconciliation — pilot report  (template; populated by `make reconcile`)
Tickers: AAPL, MSFT, XOM, C, GE · Window: 2005-01-01 → 2025-12-31 · Vendors: Refinitiv/Datastream vs yfinance.
Why it matters: Ince & Porter (2006) show naïve vendor use inflated equal-weighted returns ~72% vs CRSP;
two vendors disagreeing is INFORMATION about where data risk lives. Tolerance: |Δ daily return| > 1e-4 flagged.

<!-- BEGIN AUTO (reconcile.py overwrites between markers; do not hand-edit) -->
| Ticker | corr(daily ret) | max \|Δ\| | days >tol | dividend mismatches | notes |
|---|---|---|---|---|---|
| ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ | ⟨TBD⟩ |
GE index-exit continuity (2018-06-26 ± 5d): ⟨TBD⟩
<!-- END AUTO -->

**Interpretation (≈200 words, hand-written after numbers exist).** ⟨Where do discrepancies cluster —
ex-dividend days? splits? the GE exit? What does that imply for which vendor anchors the build and what the
reconciliation tolerance should be in `config/data.yaml`? This paragraph seeds the EDA-that-motivates-method
section Ramin asked for.⟩

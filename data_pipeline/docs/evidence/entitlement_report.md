# Entitlement probe report (automated — plan W3)
Generated 2026-06-19T13:15:05.720051+00:00 by `python -m src.data.cli probe`.
Checklist source: docs/DATA_ENTITLEMENTS.md. Secrets are never recorded here.

| # | Probe | Status | Latency | Evidence / error |
|---|---|---|---|---|
| P0 | Refinitiv session (platform/desktop) | ✅ PASS | 1.03s | `{"env_file": true, "env_keys_loaded": ["ANTHROPIC_API_KEY", "REFINITIV_APP_KEY", "REFINITIV_PASSWORD", "REFINITIV_USERNAME"], "session": "open (platform grant or desktop proxy)"}` |
| P1 | 0#.SPX chain resolves (~503 rows) | ✅ PASS | 2.17s | `{"rows": 503, "cols": 2, "sample": {"Instrument": {"0": "WEC.N", "1": "TROW.OQ", "2": "HST.OQ"}, "Company Common Name": {"0": "WEC Energy Group Inc", "1": "T Rowe Price Group Inc", "2": "Host Hotels and Resorts, Inc"}}, "index_range": ["0", "502"]}` |
| P2 | PIT membership events 2018 (content-validated) | ✅ PASS | 1.48s | `{"rows": 28, "cols": 4, "sample": {"Instrument": {"0": ".SPX", "1": ".SPX", "2": ".SPX"}, "Constituent RIC": {"0": "BCR.N^L17", "1": "SNI.OQ^C18", "2": "CHK.N^F20"}, "Constituent Name": {"0": "CR Bard", "1": "Scripps Networks", "2": "Expand Energy"}}, "index_range": ["0", "27"], "known_truth": "GGP*` |
| P3 | PIT membership events PRE-2016 (content: Lehman leaver 2008) | ✅ PASS | 1.0s | `{"rows": 35, "cols": 4, "sample": {"Instrument": {"0": ".SPX", "1": ".SPX", "2": ".SPX"}, "Constituent RIC": {"0": "SNV.N^A26", "1": "HET.N^A08", "2": "CC.N^K08"}, "Constituent Name": {"0": "Synovus Fin", "1": "HARRAH S", "2": "Circuit City"}}, "index_range": ["0", "34"], "known_truth": "LEH* leaver` |
| P4 | Datastream list LS&PCOMP0110 (DSWS) | 🚫 BLOCKED | 0.0s | `DatastreamPy not installed` |
| P5 | GE total-return continuity around 2018-06-26 | ✅ PASS | 0.25s | `{"rows": 1, "cols": 1, "sample": {"TR.TOTALRETURN": {"2018-07-13 00:00:00": "<NA>"}}, "index_range": ["2018-07-13 00:00:00", "2018-07-13 00:00:00"]}` |
| P6 | Dead RIC LEH.N^I08 history (delisted coverage) | ✅ PASS | 0.47s | `{"rows": 177, "cols": 1, "sample": {"Price Close": {"2008-01-02 00:00:00": "62.19", "2008-01-03 00:00:00": "61.0", "2008-01-04 00:00:00": "58.35"}}, "index_range": ["2008-01-02 00:00:00", "2008-09-12 00:00:00"]}` |
| P7 | Field definitions: RI day-count & currency | 📝 MANUAL | 0.14s | `{"RI_day_count": {"status": "REQUIRES_MANUAL_CONFIRMATION", "note": "Datastream Navigator > RI definition on the entitled feed; harvest missing-piece #5 (docs/DATA_ENTITLEMENTS.md test 7)"}, "currency_check": {"status": "OK", "sample": [{"Instrument": "AAPL.O", "Currency": "USD"}]}}` |
| P8 | RDP scope census (search/news/pricing) | ✅ PASS | 4.38s | `{"search": "IN SCOPE", "news": "ScopeError: Error code -1 | Insufficient scope for key=/data/news/v1/headlines, method=GET.\nRequired scopes: {'trapi.data.news.read'", "pricing_snapshot": "IN SCOPE"}` |

## Interpretation

Pre-2016 membership path verified — proceed with the full PIT build.

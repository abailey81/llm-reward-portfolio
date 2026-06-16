# Entitlement probe report (automated — plan W3)
Generated 2026-06-12T13:19:04.769622+00:00 by `python -m src.data.cli probe`.
Checklist source: docs/DATA_ENTITLEMENTS.md. Secrets are never recorded here.

| # | Probe | Status | Latency | Evidence / error |
|---|---|---|---|---|
| P0 | Refinitiv session (platform/desktop) | ✅ PASS | 1.01s | `{"env_file": true, "env_keys_loaded": ["REFINITIV_APP_KEY", "REFINITIV_PASSWORD", "REFINITIV_USERNAME"], "session": "open (platform grant or desktop proxy)"}` |
| P1 | 0#.SPX chain resolves (~503 rows) | ✅ PASS | 2.44s | `{"rows": 503, "cols": 2, "sample": {"Instrument": {"0": "PG.N", "1": "FDS.N", "2": "ODFL.OQ"}, "Company Common Name": {"0": "Procter & Gamble Co", "1": "Factset Research Systems Inc", "2": "Old Dominion Freight Line Inc"}}, "index_range": ["0", "502"]}` |
| P2 | TR.IndexConstituentRIC @ 2018-01-02 | ✅ PASS | 1.49s | `{"rows": 503, "cols": 2, "sample": {"Instrument": {"0": "PG.N", "1": "FDS.N", "2": "ODFL.OQ"}, "Constituent RIC": {"0": "<NA>", "1": "<NA>", "2": "<NA>"}}, "index_range": ["0", "502"]}` |
| P3 | TR.IndexConstituentRIC @ 2010-01-04 | ✅ PASS | 1.47s | `{"rows": 503, "cols": 2, "sample": {"Instrument": {"0": "PG.N", "1": "FDS.N", "2": "ODFL.OQ"}, "Constituent RIC": {"0": "<NA>", "1": "<NA>", "2": "<NA>"}}, "index_range": ["0", "502"]}` |
| P4 | Datastream list LS&PCOMP0110 (DSWS) | 🚫 BLOCKED | 0.43s | `DSWS login failed: DSUserObjectFault: User 'ZLDU178' not entitled to ClientApi service.` |
| P5 | GE total-return continuity around 2018-06-26 | ✅ PASS | 0.31s | `{"rows": 1, "cols": 1, "sample": {"TR.TOTALRETURN": {"2018-07-13 00:00:00": "<NA>"}}, "index_range": ["2018-07-13 00:00:00", "2018-07-13 00:00:00"]}` |
| P6 | Dead RIC LEH.N^I08 history (delisted coverage) | ✅ PASS | 0.48s | `{"rows": 177, "cols": 1, "sample": {"Price Close": {"2008-01-02 00:00:00": "62.19", "2008-01-03 00:00:00": "61.0", "2008-01-04 00:00:00": "58.35"}}, "index_range": ["2008-01-02 00:00:00", "2008-09-12 00:00:00"]}` |
| P7 | Field definitions: RI day-count & currency | 📝 MANUAL | 0.16s | `{"RI_day_count": {"status": "REQUIRES_MANUAL_CONFIRMATION", "note": "Datastream Navigator > RI definition on the entitled feed; harvest missing-piece #5 (docs/DATA_ENTITLEMENTS.md test 7)"}, "currency_check": {"status": "OK", "sample": [{"Instrument": "AAPL.O", "Currency": "USD"}]}}` |
| P8 | RDP scope census (search/news/pricing) | ✅ PASS | 3.18s | `{"search": "IN SCOPE", "news": "ScopeError: Error code -1 | Insufficient scope for key=/data/news/v1/headlines, method=GET.\nRequired scopes: {'trapi.data.news.read'", "pricing_snapshot": "IN SCOPE"}` |

## Interpretation

Pre-2016 membership path verified — proceed with the full PIT build.

# Datasheet v1 — generated 2026-06-10 (Gebru et al., CACM 2021; auto-filled from data/manifest)

## Motivation
Created to answer the pre-registered research question (PREREGISTRATION §1): LLM-evolved rewards under distributional feedback vs hand-designed rewards on a survivorship-bias-free 30-stock US large-cap universe, 2005–2025. Funded/required by the UCL MSc IFTE0008 dissertation; no commercial purpose.

## Composition
- **raw**: 18 artifacts, 95,438 rows (e.g. yf_adjclose_34c45d1f.csv)
- **staged**: 3 artifacts, 15,846 rows (e.g. staged_returns_yfinance_pilot.parquet)
- **clean**: 6 artifacts, 20,231 rows (e.g. quarantine_pilot.csv)
- **gold**: 12 artifacts, 47,541 rows (e.g. returns_panel_pilot.parquet)

## Collection process
Pulled via src/data/acquire.py (journaled, rate-governed, provenance-sidecar'd) from vendors: derived, fred, kenfrench, merged, yfinance. Entitlement evidence: docs/evidence/entitlement_report.md.

## Preprocessing / cleaning / labeling
Medallion pipeline (src/data): structural validation, corporate-action integrity, Ince–Porter screens (flag-only), Shumway delisting corrections (logged), missing-data taxonomy with zero interpolation (R4). Raw layer is immutable; every transform is lineage-recorded.

## Uses
Training/evaluating deep-RL portfolio policies inside this dissertation only; vendor licence terms prohibit redistribution of raw data — the repo ships manifests, not payloads.

## Distribution
NOT distributed. SHA-256 manifests + pull provenance allow an entitled party to reproduce byte-exact artifacts.

## Maintenance
Maintained by the author until dissertation submission (2026-09-01); manifest + ADR log document every change.

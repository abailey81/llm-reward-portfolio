# Data-chapter seed paragraphs (one per pipeline stage)

**Acquisition.** Data were acquired through a journaled, rate-governed pipeline with request-level provenance (⟨TBD: chunk/row counts⟩); every artifact is SHA-256-manifested at the moment of receipt.

**Raw vault.** The raw layer is write-once and checksum-verified on every read (⟨TBD: artifact count⟩), making fabrication or silent revision detectable by construction (R4).

**Security master.** All joins key on a security master that resolves renames, share-class splits and dead-RIC suffixes (⟨TBD: n securities⟩), eliminating ticker-reuse contamination.

**Validation.** Structural validation enforced schema, XNYS calendar alignment and duplicate detection (⟨TBD: violation counts⟩).

**Corporate actions.** Total-return internal consistency and unadjusted-split signatures were screened (⟨TBD: flag counts⟩); flags never mutate values.

**Outliers.** Ince–Porter screens plus cross-sectional context classification preserved genuine crisis tails while quarantining suspect prints (⟨TBD⟩).

**Survivorship.** Point-in-time membership with a spliced 2016 overlap validation (⟨TBD: jaccard⟩) and logged Shumway corrections removes the 0.9–1.4%/yr survivorship inflation documented by Elton–Gruber–Blake.

**Missing data.** Every missing cell is classified and counted (⟨TBD: taxonomy counts⟩); returns are never interpolated.

**Reconciliation.** Two-vendor reconciliation across the universe (⟨TBD: corr/discrepancy stats⟩) clusters discrepancies on ex-dividend and split days, deciding per-field vendor authority.

**Gold construction.** Model-ready panels are built exclusively through availability-lagged as-of joins with embargoed splits materialized to explicit session lists (⟨TBD: split session counts⟩), and leakage is asserted by tests.

**EDA.** Profiling confirmed fat tails, volatility clustering and correlation-regime dynamics (median excess kurtosis 11.5), motivating the CVaR-penalised fitness, the 60-day lookback and the 3-state filtered HMM.

**Quality.** A per-series scoreboard (⟨TBD: median score⟩) and a raw→gold lineage map close the loop from API call to model input.

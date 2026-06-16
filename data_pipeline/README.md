# `data_pipeline/` — Refinitiv → gold data-acquisition pipeline

This is the **self-contained, first-class reproduction pipeline** that built the frozen, survivorship-free,
point-in-time research panel in [`../data/gold/`](../data/gold/). It was developed as repo "B" (see
`DECISIONS.md` ADR-019…021) and relocated here **verbatim** during the repository unification (ADR-022) —
all internal imports are intact and it runs in its own right.

It is intentionally **decoupled from the live engine** in [`../src/`](../src/): the gold panel is already
built and frozen (checksummed in [`../data/manifest/`](../data/manifest/)), so this pipeline is **not** part
of the training loop. It exists for **reproducibility and provenance** — re-running it requires live
Refinitiv (LSEG) credentials and will re-pull from the vendor.

## Layout
```
data_pipeline/
├── config/                 # the data-layer YAML config the pipeline reads (vendor mnemonics, universe, dates)
└── src/
    ├── config.py           # YAML loader; get("data.universe…"); CONFIG_DIR = data_pipeline/config
    ├── features.py         # build_cash_features, rolling_vol_shifted
    └── data/               # the acquisition layer
        ├── acquire.py          # Refinitiv RDP pulls (get_history / datagrid long-form)
        ├── membership.py       # PIT index membership by reverse event replay (ADR-020)
        ├── build_universe.py   # long→wide assembler → panel.build_gold
        ├── panel.py            # build_gold / materialize_splits / as_of_join  (gold builder)
        ├── reconcile_full.py   # two-vendor reconciliation
        ├── security_master.py  # RIC↔ticker mapping
        ├── vault.py            # write-once frozen-artifact vault + lineage/manifest
        ├── validate.py, quality.py, integrity.py, probes.py, eda.py, pull_universe.py, cli.py
```

## How the frozen gold was produced (summary; full record in `../DECISIONS.md`, `../CHANGELOG.md`)
- **Survivorship-free, point-in-time** S&P-500-scale universe, 2005–2025: union **953 RICs incl. 333 dead**;
  PIT membership via reverse event replay through `TR.IndexJLConstituent*` (snapshot queries were found to
  silently return the *current* chain → 98 artefacts invalidated; ADR-020).
- Daily total returns via **datagrid long-form `Frq=D`** (the `get_history` TR route returned empty frames →
  39 artefacts invalidated), monthly market cap `Frq=M`, OHLC/bid/ask/volume via `get_history`.
- `selection_buffer_months` acquires membership+caps *before* each window start so top-30 selection uses
  strictly-prior information (no look-ahead).
- Two-vendor reconciliation (median corr 0.99994), write-once vault with full lineage/manifest.
- `.VIX` is **not** licensed (CBOE) → the VIX feature uses **FRED VIXCLS** (see the engine's data config).

## Re-running (requires Refinitiv credentials in `../.env`: `REFINITIV_USERNAME/PASSWORD/APP_KEY`)
```bash
cd data_pipeline
python -m src.data.cli --help        # entry points for the acquisition stages
```
The canonical research panel is `returns_panel_univ3.parquet` (5,283 × 953); `_univ`/`_univ2` are superseded
(manifested, write-once). **Do not re-run unless you intend to re-pull from the vendor** — the frozen panel
is the immutable input to the experiment.

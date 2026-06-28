# Infrastructure assessment — databases, storage, and tooling adopt/reject matrix

**Purpose.** A strict, opinionated adopt/reject decision for every storage engine, data format, and
orchestration/tracking tool a reviewer might ask "why didn't you use X?". It is grounded in the **actual**
stack, not a greenfield design, and complements `DATASHEET_v1.md` (what the data *is*) and
`DATA_ENTITLEMENTS.md` (what the LSEG/Refinitiv licence *permits*).

## The actual stack (what is already true)

- **Data at rest = Parquet.** `data/gold/*.parquet` (returns / cash-features / market-proxy / top-30
  selection, per universe suffix). Read once into the engine's `Panel` by `src/data/loaders.py::load_gold_panel`.
- **Provenance is per-file and explicit.** Every gold artifact has a sibling `*.provenance.json`; the build
  lineage lives in `data/manifest/` (`manifest.jsonl`, `lineage.jsonl`, `checksums.txt`, `invalidated.jsonl`).
- **Integrity is a checksum gate.** `loaders.py` computes a SHA-256 over each parquet (`_file_sha256`) and
  verifies it against the frozen manifest (`_verify_checksum`, `config/data.yaml: freeze.checksum: sha256`)
  before the bytes reach the env.
- **Access pattern = one-time, whole-panel, in-process pandas load**, then slice in NumPy. There is no
  concurrent writer, no online ingestion, no multi-tenant query workload, no row-level update — the panel is
  **frozen** at campaign start.

## HEADLINE VERDICT

**ZERO databases needed.** Parquet + per-file provenance JSON + SHA-256 checksum gate + a single one-time
pandas load is the **correct** design for this project: it is **license-clean** (the data never leaves the
governed disk, no third-party service touches LSEG-derived returns), **reproducible** (byte-identical replay
from the frozen, checksummed files — CLAUDE.md PD-6), and **minimal** (no daemon, no schema migration, no
network dependency in the run path). Adding a database would add operational surface, a determinism risk, and
— for any hosted engine — a data-licence exposure, while buying **nothing** for a read-only frozen panel of
this size. The bar for adopting anything below is therefore: *does it improve license-cleanliness,
reproducibility, or grade, net of the risk it adds?* Almost nothing clears it pre-freeze.

---

## REJECT — databases (no query/concurrency/update workload to justify any of them)

| Tool | One-line reason to reject |
|---|---|
| **Supabase** | Hosted Postgres ⇒ LSEG-derived returns leave the governed disk; license exposure + a network dep in the run path, for a read-only frozen panel. |
| **Azure Cosmos DB** | Cloud, multi-model, pay-per-RU — same license exposure; document/graph semantics irrelevant to a dense return matrix. |
| **PostgreSQL** | A relational server for a single frozen matrix is pure overhead: schema, daemon, connection pool — zero queries to serve. |
| **MongoDB** | Document store for tabular numeric panel = wrong shape; no semi-structured/schema-flex need; adds a daemon. |
| **Redis** | In-memory KV cache; nothing to cache — the panel already lives in RAM for the whole run. |
| **ClickHouse** | OLAP column store for analytical queries we never issue; the analysis reads a results matrix, not SQL. |
| **kdb+/q** | Tick-database for high-frequency time-series queries; daily aggregated returns + proprietary licence + cost = unjustified. |
| **TimescaleDB** | Postgres time-series extension; no continuous ingestion or time-range query workload exists. |
| **InfluxDB** | Metrics/IoT time-series DB; same — no streaming writes, no retention policies needed. |

## REJECT — table/lakehouse formats (no mutation, no concurrent writers, no time-travel need)

| Tool | One-line reason to reject |
|---|---|
| **Delta Lake** | ACID/time-travel over a *frozen* single-writer panel buys nothing; the freeze manifest already pins the exact bytes. |
| **Apache Iceberg** | Large-table schema-evolution/partition-evolution for a static ~5k×~950 matrix is over-engineering. |
| **Apache Hudi** | Upsert/incremental-ingestion engine; there are no upserts and no incremental ingestion. |
| **lakeFS** | Git-for-data branching; our versioning is the provenance JSON + checksummed freeze manifest + git on the build code. |

## REJECT — embedded/single-file engines (the load is whole-panel, not query-shaped)

| Tool | One-line reason to reject |
|---|---|
| **DuckDB** | Excellent embedded OLAP, but we read the *entire* panel once into pandas — there is no selective SQL to push down; adds a dependency for no win. |
| **SQLite** | Row-store for transactional/relational access we don't have; Parquet is the better at-rest format for a numeric matrix. |

## REJECT — alternative at-rest formats (Parquet is already the right one)

| Tool | One-line reason to reject |
|---|---|
| **Arrow (IPC/Feather)** | In-memory/interchange format; pandas already uses Arrow under the hood on read — no at-rest benefit over Parquet, weaker ecosystem for archival. |
| **ORC** | Hive-ecosystem column format; Parquet has the better Python/pandas support and is already in place. |
| **Avro** | Row-oriented serialization for streaming/schemas; wrong access pattern for a dense analytical matrix. |
| **HDF5** | Historically brittle concurrency + version/portability issues; works against byte-identical reproducibility. |
| **Zarr** | Chunked N-d arrays for out-of-core/cloud tensors; the panel fits in RAM, so chunked lazy access is unnecessary. |

## REJECT — experiment trackers (cloud-license exposure and/or grade-neutral)

| Tool | One-line reason to reject |
|---|---|
| **Weights & Biases** | Hosted ⇒ uploads run artifacts derived from licensed data; grade-neutral vs the existing archive/results-IO; adds a network dep. |
| **MLflow** | Even self-hosted it duplicates what `src/io/results.py` + the prompt/reward/feedback archive already record deterministically. |
| **Neptune / Comet / TensorBoard-as-tracker** | Same: a tracking layer is grade-neutral here, and any hosted variant carries the license exposure. |

> Provenance and run-tracking are **already solved** by the deterministic archive (every prompt, generated
> reward, and feedback block) + `src/io/results.py`, which is the *only* read path for analysis. A tracker
> would add surface without changing the result.

## REJECT — parallel/distributed compute (nondeterminism vs the replay guarantee)

| Tool | One-line reason to reject |
|---|---|
| **Ray** | Distributed scheduling introduces nondeterministic task ordering/placement ⇒ breaks byte-identical replay; the campaign already parallelises the test leg deterministically on one box. |
| **Dask** | Same nondeterminism risk for a workload that fits a single GPU box; no out-of-core need (panel fits in RAM). |

## REJECT — cloud orchestration & hosted sandboxes (LSEG licence)

| Tool | One-line reason to reject |
|---|---|
| **Cloud GPU orchestration** (SkyPilot/Kubernetes/managed clusters) | Moving the gold panel to a third-party cluster is a derived-data licence exposure; the run fits a single rented/owned GPU. |
| **Cloud code sandboxes** (E2B / Modal / hosted execution of LLM-generated reward code) | Untrusted reward code is already AST-gated and run **in-process** on the governed box; shipping it (and the data) to a hosted sandbox adds licence exposure for no safety gain. |

## REJECT (pre-freeze) — containerisation

| Tool | Disposition |
|---|---|
| **Docker** | Grade-neutral **pre-freeze** — determinism is already secured by exact version pins + the freeze manifest + torch deterministic flags. A pinned repro image is genuinely useful for third-party bit-reproduction, so it is recorded as **Future Work** (see `ANALYSIS_METHODS_AND_FUTURE_WORK.md` §3), not adopted now. |

---

## ADOPT — NOW (cheap, license-clean, strengthens reproducibility/integrity)

| Action | Why |
|---|---|
| **`pip-audit`** | A supply-chain vulnerability scan over the pinned dependency set — cheap integrity evidence, no design change. |
| **Exact version pins** | Keep `pyproject.toml` pins exact (the fragile PyTorch ↔ d3rlpy pin especially); pins are the determinism backbone. |
| **`uv.lock` on the GPU box** | Materialise a fully-resolved lockfile on the actual campaign machine so the environment is bit-reproducible, not just constraint-compatible. |
| **Confirm torch deterministic flags present** | Verify the seeding/determinism flags (`torch.use_deterministic_algorithms`, cuDNN settings) are set on the run path, so replay holds on the GPU box. |

## ADOPT — IF TIME (nice-to-have, not load-bearing)

| Action | Why |
|---|---|
| **Lightweight Pandera / pydantic data-contract** | A small declarative schema/range contract on the loaded `Panel` (dtypes, shapes, finiteness, id ranges) — *complements* the checksum gate by catching *semantic* drift the SHA cannot. Keep it lightweight. |
| **NOT Great Expectations** | Rejected even in the "if time" tier: heavyweight, redundant with the SHA-256 checksum gate + a small Pandera contract; not worth the dependency and config surface. |

---

**Bottom line.** The infrastructure is already at the right altitude: a frozen, checksummed, provenance-
stamped Parquet panel loaded once into memory. The adopt list is small and integrity-focused
(`pip-audit`, exact pins, `uv.lock`, confirmed determinism flags); everything heavier is rejected because it
adds operational surface, nondeterminism, or LSEG-licence exposure without improving the grade or the result.

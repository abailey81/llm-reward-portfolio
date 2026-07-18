# Publication release & reproducibility checklist (2026-07-18, pre-launch audit)

> Commissioned by Tamer ("since we plan to publish — Docker and all the other stuff").
> The organizing principle: **run-time-capturable items must exist BEFORE/DURING the campaign
> or they are unreconstructable; release-time artifacts are deliberately deferred** and built
> from what the run captures. Status: every run-time item is CAPTURED; every release item is
> inventoried with its recipe. TMLR → ICAIF release path (memory: publication plan).

## A. Run-time-captured (must exist during the campaign — ALL ✓ as of 2026-07-18)

| Item | Status | Evidence |
|---|---|---|
| Per-record environment snapshot (python/platform/packages/pip-freeze/CUDA/driver/determinism flags/gold manifest shas) | ✓ automatic | `capture_env` → `env.json` + content-sha in every record |
| **Code identity in every record** | ✓ **FIXED TODAY** | cluster deploys via `git archive` (not a work-tree) → `git_commit` was None; now a `GIT_COMMIT` marker is written at sync and `provenance.git_commit()` falls back to it as `deployed-archive:<sha>` (tested; marker live on ~/llmrp = `b4862e99…`) |
| Container identity | ✓ recorded | Apptainer `python311.sif` sha256 `bacd34a0a6f519e0…` (2026-07-18) + `scripts/myriad/build_env.sh` in-repo |
| LLM call provenance (prompt/completion/usage/model id per call) | ✓ automatic | the provenance archive; replay-from-archive is the results contract (generation is NOT the reproducible object — B.6.1) |
| Seeds / CRN / device assignment | ✓ automatic | records + env fingerprints + the CRN-pair device census |
| Design identity | ✓ | freeze hash binds the 8 design files; verify-or-refuse on every driver start; prereg bundle zip rebuilt at freeze (`make_prereg_bundle` asserts hash match) |
| Archive integrity | ✓ | content-addressed manifest root (`archive_integrity`) + bank-gate write→verify |
| Wall-clock/compute accounting | ✓ automatic | per-record wall_clock (M4 fix) + epilogue ledgers + qacct forensics |

## B. At-freeze actions (minutes; part of the GO sequence)

1. `git tag prereg-freeze-ce5db62c` at the freeze commit (local; pushing = Tamer's act).
2. Rebuild + sha256 the prereg bundle (`prereg_bundle_ce5db62c.zip`); record the sha in
   CHANGELOG (dated). Optional external anchoring (Tamer's choice, strengthens but not
   required): OSF registration or an OpenTimestamps stamp of the bundle.

## C. Release-time artifacts (post-campaign; recipes ready, nothing blocked)

| Item | Recipe |
|---|---|
| **Dockerfile** | `FROM python:3.11-slim` + `requirements.lock` + repo + entrypoints for `analyze_campaign`/`make_figures`; smoke = the suite headless (CPU) + a synthetic-panel mini-run. The Apptainer path stays documented for HPC users (`build_env.sh`); note the sif sha. |
| Zenodo/OSF DOI deposit | code (tagged release) + prereg bundle + AGGREGATE results + figures; CITATION.cff already present |
| **⚠ Licensed-derivatives decision (the one open LEGAL question)** | `val_returns`/`test_returns` series are DERIVED from licensed LSEG prices — whether raw derived return series may be published needs a licence check before the data deposit. Fallbacks (either fully acceptable for TMLR): publish aggregate statistics + inference outputs only, or ship the synthetic-panel replication configs so the pipeline is end-to-end runnable without the licence. THE DISSERTATION IS UNAFFECTED (examiners get the PDF; UCL may receive the archive privately). |
| MODEL_CARD refresh | campaign facts + the GPT-5.5→5.6 currency touch (noted 07-18) |
| Repro checklist mapping | the 06-28 checklist mapped onto the TMLR reproducibility-statement format + the ICAIF variant |
| Public CI (nicety) | GitHub Actions: lint + the CPU suite on the Dockerfile image |
| REPRODUCIBILITY.md refresh | the stage map updated to the executed campaign (Myriad substrate, supervisor, chunked submission) |

## D. Why Docker is NOT a launch blocker (the reasoning, recorded)

The results contract is **replay-from-archive**: trainings are bitwise-deterministic per device
class (grade-A certified) and archived; LLM generations are non-deterministic BY NATURE and
archived per-call; analysis is a pure function of the archive + pinned deps. A Dockerfile
written at release from the SAME `requirements.lock` reproduces the analysis bit-for-bit.
What cannot be reconstructed later is exactly the run-time column above — which is why the
git-identity gap found today mattered and the container itself does not. The campaign already
runs IN a container (Apptainer) whose identity is now hash-recorded.

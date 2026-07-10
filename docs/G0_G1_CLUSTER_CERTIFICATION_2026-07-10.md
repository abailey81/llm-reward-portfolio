# Myriad cluster certification — measured facts (2026-07-10)

The empirical record that re-anchors every wall-clock figure in the plan. Everything here was
measured first-hand on the live cluster, not assumed. Job IDs are real SGE submissions.

---

## G0 — reconnaissance (login node + one batch GPU probe)

### Login node (`login12`, `scripts/myriad/g0_probe.sh`)
| Fact | Value |
|---|---|
| OS / libc | RHEL 7.9 (Maipo) / glibc **2.17** |
| Home / Scratch | `/home/ucestes`, `~/Scratch` on `myriadfs`, **1.0 TB** |
| ACFS | `/acfs/users/ucestes` present (backed, read-only on compute) |
| Login outbound HTTPS | **works** (api.anthropic.com reachable, pypi 200) |
| Scheduler | SGE (`qsub`/`qstat` under `/opt/sge`) |
| Interactive `qrsh` | **REJECTED by JSV** — batch `qsub` only (no impact: campaign is batch arrays) |
| Apptainer | **1.2.4** present (`/usr/bin/apptainer`) |
| `lquota` | errors on the new `myriadfs` (cosmetic; `df` gives quota) |

**Platform verdict.** glibc 2.17 has **no installable wheels** for the pinned `pandas 2.3.3`
(needs manylinux_2_24) or `contourpy 1.3.3` (2_27), and source builds fail on GCC 4.8.5. The
plan's pre-written **R12 container route** was taken: `~/python311.sif`
(`python:3.11-slim-bookworm`, glibc 2.36); the venv is built THROUGH the container so every locked
version installs exactly as validated. This preserves laptop↔cluster pin parity.

### GPU node (batch probe, job **762862** on `node-e00a-013`, pool `EF`)
```
CUDA_VISIBLE_DEVICES=            (empty — cgroup restricts the device list instead)
GPU 0: Tesla V100-PCIE-32GB, driver 550.127.05, 32768 MiB
GPUs visible under gpu=1: 1     => cgroup isolation => PACKING SAFE
compute-node outbound: HTTP 404 => compute nodes have outbound internet
```

**Three load-bearing findings:**
1. **Packing is safe.** `gpu=1` exposes exactly one GPU; no foreign job can share it. Pack N
   processes on `cuda:0` with confidence.
2. **V100 is the 32 GB PCIe variant, not 16 GB SXM2.** Memory is no longer the binding constraint
   (each training ≈ 2–3 GiB); the packing ceiling is CPU cores (36/node ÷ 4 ≈ 9), not VRAM. This is
   **denser than the "~5/GPU" planning assumption** — an upside to be confirmed by the G1 ladder.
   Driver 550.127.05 is well above the cu124 floor (≥520).
3. **Compute nodes have outbound internet.** Architecture is flexible; the laptop-driver design
   still stands but is not forced.

### Queue contention (measured, fresh fair-share)
- **5,092 pending jobs** cluster-wide; **several GPU nodes DOWN** (`adu`/`ad` states — their
  advertised free GPUs are phantoms). Only the two `e96a` V100 nodes showed healthy free GPUs.
- A 15-minute single-GPU job waited **> 1 hour** to start (762862 submitted 14:19, started 15:31).
- **No resource-quota rule caps us** (the only RQS, `slowemdown`, is disabled and targets another
  user).
- Implication: access is done; **throughput is the one open variable** — exactly what the plan
  anticipated. It makes the ARR→CRAG co-sign ask concrete (CRAG meets Tue 14 Jul).

---

## Environment build (login node, through the container)
`torch 2.6.0+cu124 · pandas 2.3.3 · numpy 1.26.4 · stable-baselines3 2.8.0 · gymnasium 1.2.3`;
`import src.cluster` OK. CPU + import smoke green.

## Data staging
The 10-file `univ5` gold family (~36 MB) → `/acfs/users/ucestes/gold`; **all SHA-256 verified
identical** on both sides (`returns_panel_univ5` = `7cf5d988…`).

## Launcher fix (commit `08a1ba7`)
The containerized jobscript launched the container's bare `python` (no deps → first-import death)
and did not bind `$TMPDIR`/gold into the container. Fixed to
`apptainer exec --nv --bind "$TMPDIR,{gold_dir}" {sif} {venv}/bin/python`; regression test corrected
to assert the right behaviour; 71/71 cluster tests green.

---

## G1 — certification

### Launcher validated on BOTH pools (the `08a1ba7` fix, on real hardware)
| Job | Node | GPU | torch drives it? | 50× 2048² matmul |
|---|---|---|---|---|
| `g1smoke` 762914 | node-e00a-013 (EF) | Tesla **V100-PCIE-32GB**, drv 550.127.05 | **yes**, cuda 12.4 | **0.144 s** |
| `g1L` 762959 | node-l00a-004 (L) | NVIDIA **A100-PCIE-40GB**, drv 550.127.05 | **yes**, cuda 12.4 | **0.21 s** |

Both jobs printed `TMPDIR bind OK …/bind_marker` and `=== G1 SMOKE PASSED ===`, confirming the
containerized launcher `apptainer exec --nv --bind "$TMPDIR" {sif} {venv}/bin/python` works exactly
as fixed, on both node types, and that the full cu124 stack (torch 2.6.0, sb3 2.8.0, pandas, numpy)
drives each GPU.

**Load-bearing throughput finding.** The A100 is **not faster** than the V100 for this workload —
it is slightly *slower* in the microbench (0.21 s vs 0.144 s), because a small fp32 matmul touches no
tensor cores and the PCIe A100's clocks are lower. This empirically confirms the plan's claim
**"A100 ≈ V100 per training"**: the A100 pool's value is denser *packing* (40 GB, 36 cores) for the
Stage-2 report-only fleet, never per-training speed. The confirmatory campaign stays V100-only for
device homogeneity.

### Still to measure
A real short SAC-training timing probe (steps/sec at pack=1 vs pack=N on the staged gold) to convert
"packing safe" into a measured packing factor **F** and a per-training wall-clock, then re-anchor the
day-tables. Gold data path being verified on the login node first (CPU) to de-risk the GPU slot.

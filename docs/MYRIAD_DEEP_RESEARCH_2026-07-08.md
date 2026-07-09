# UCL Myriad — deep research dossier (2026-07-08)

> **Purpose.** A first-hand, verbatim-sourced reference for how Myriad actually works and how to run
> our campaign on it natively. Every fact below was read directly from the UCL Research Computing docs
> (`rc.ucl.ac.uk/docs`, the `UCL-ARC/mkdocs-rc-docs` source), a real production config (nf-core), or a
> real UCL paper that used Myriad. Sources are listed per section and collected at the end. This
> dossier **supersedes-as-evidence** the R1–R14 rules register in `PLAN_IF_WE_USE_UCL_MYRIAD.md §4`
> and the §14 native-maximisation claims: where they agree it is now first-hand-confirmed; where this
> dossier is more precise, THIS wins. §12 is the reconciliation (what's confirmed / corrected / new).

---

## 0. The five findings that change or lock our plan

1. **GPU PACKING IS VALIDATED (was our single biggest open risk).** UCL GPU nodes run **device
   cgroups since 10 Aug 2022**: a job "only ha[s] access to the number of GPUs they requested," and
   nodes are shared per-GPU across jobs. So a `-l gpu=1` job owns that GPU exclusively (no other job
   can land on it and OOM us), and we can safely run **N training processes on our one cgroup-isolated
   GPU** — the §15 pack lever (×2–2.5) is sound, not a hope. Verbatim source: the Young GPU-nodes page
   (same UCL-RC SGE + admin as Myriad; the Myriad GPU page's support for `gpu=1..4` on 2- and 4-GPU
   nodes implies the same isolation). G0 now *confirms* (`nvidia-smi -L` + `$CUDA_VISIBLE_DEVICES`
   inside a Myriad `gpu=1` job) rather than *discovers* — the timeline risk drops from "could double"
   to "very likely fine, G0 ticks the box."
2. **74 GPUs, exact node inventory CONFIRMED.** E/F = 19 nodes × 2 V100-16G = **38 V100**; L = 6 × 4
   A100-40G = **24**; U/V = 3 nodes × 4 A100-80G = **12**. Total **74 GPUs** across ~393 nodes. Plus
   T-type (6× AMD EPYC 64-core, 768 GB, no GPU — irrelevant to us). Our two-pool plan (V100
   confirmatory / A100 report-only) maps exactly onto this.
3. **Storage model CONFIRMED:** on Myriad **home == Scratch, 1 TB combined, NOT backed up**; **ACFS is
   the daily-backed-up, read-only-on-compute** filesystem → gold input data lives on ACFS (immutable
   input), outputs live on Scratch and MUST be mirrored off-cluster (our 3-site mirror). Local node
   disk `$TMPDIR` is **1.5 TB** on the V100 nodes and is wiped on job end/failure (never leave results
   there).
4. **Throughput knobs CONFIRMED from a production config.** nf-core's live Myriad profile sets
   `executor=sge`, **`queueSize=100`**, **`submitRateLimit='10/1s'`**, `penv='smp'` — exactly the
   courtesy throttle our driver already targets (`-tc` + rate-limited submits). The real ceiling is
   fair-share; more sustained throughput comes from the **ARR → CRAG** (monthly, 2nd Tuesday,
   `rc-support@ucl.ac.uk`, co-signed with the PI).
5. **Two integration gotchas to encode now:** (a) **Apptainer must build on the LOCAL filesystem
   (`$TMPDIR`), not home/Scratch**; (b) do **not** copy jobscript syntax from the UCL *CS-department*
   cluster tutorials — they use `tmem` / `gpu=true` / `/share/apps`, whereas **Myriad uses `mem` /
   `gpu=1` / `module load`**. Getting these wrong is a day-1 failure.

---

## 1. Hardware (verbatim from the Myriad cluster page)

| Type | Nodes | Cores | RAM | GPUs | tmpfs (local disk) | CPU |
|---|---|---|---|---|---|---|
| D (standard) | 342 | 36 | 192 GB | — | 1500 GB | Xeon Gold 6240 @2.6 GHz |
| I,B (high-mem) | 17 | 36 | 1.5 TB | — | 1500 GB | Xeon Gold 6140/6240 |
| **E,F (V100)** | **19** | 36 | 192 GB | **2 × V100-16G** | 1500 GB | Xeon Gold 6140/6240 |
| **L (A100-40)** | **6** | 36 | 192 GB | **4 × A100-40G** | 1500 GB | Xeon Gold 6240 |
| **U,V (A100-80)** | **3** | 48 | 256 GB | **4 × A100-80G** | 1700–1800 GB | Xeon Gold 6336Y/6342 |
| T (AMD) | 6 | 64 | 768 GB | — | 420 GB | AMD EPYC 9554P @3.1 GHz |

**GPU totals: 38 V100 (CC 7.0) + 24 A100-40 (CC 8.0) + 12 A100-80 (CC 8.0) = 74.** ~393 nodes total.
**Design intent (verbatim):** Myriad is "designed for high I/O, high throughput jobs that will run
within a single node rather than multi-node parallel jobs" — i.e. exactly our workload (thousands of
independent single-GPU trainings). This sentence is worth quoting in the paper's compute section.

## 2. Access & login

- `ssh <UCLusername>@myriad.rc.ucl.ac.uk` (round-robins to `login12`/`login13.myriad.rc.ucl.ac.uk`).
  UCL username + password. **Off the UCL network → UCL VPN required.**
- **Login-node policy:** "Very short (< 15 mins) and non-resource-intensive software tests can be run
  on the login nodes, but anything more should be submitted as a job." → our driver runs on the
  **laptop over the VPN**, never resident on a login node (R2). ssh calls (`qsub`/`qstat`/`tar`) are
  short and fine.
- **Open OnDemand** (`https://ood.myriad.rc.ucl.ac.uk/`, limited pilot, Microsoft-365 login,
  UCL-network/VPN only): browser file manager (≤10 GiB), **Active Jobs (a `qstat` queue view)**, Job
  Composer, in-browser SSH terminal, interactive desktops, and **Jupyter servers on compute nodes**.
  → Tamer's human queue-monitor + a Jupyter to eyeball the synced archive, complementing the laptop
  sentinel. Request pilot access from `rc-support@ucl.ac.uk`.

## 3. Scheduler — Grid Engine (SGE), verbatim directives

Submit `qsub`, monitor `qstat`, delete `qdel`, interactive `qrsh`, accounting `qacct`. Jobscript
starts `#!/bin/bash -l` (login shell — loads the module system). Directives:

| Directive | Meaning |
|---|---|
| `#$ -l h_rt=48:00:00` | wallclock (HH:MM:SS) |
| `#$ -l mem=4G` | RAM **per core** |
| `#$ -l tmpfs=15G` | local `$TMPDIR` disk (default 10 GB) |
| `#$ -l gpu=1` | number of GPUs (1–4 on Myriad) |
| `#$ -pe smp 4` | N cores, shared-memory (threaded) |
| `#$ -ac allow=EF` / `=L` | restrict to V100 (EF) / A100-40 (L) nodes |
| `#$ -ac exclusive` | reserve the WHOLE node (no other jobs on it) |
| `#$ -t 1-N` + `#$ -tc K` | **array of N tasks, at most K running at once** |
| `#$ -hold_jid <id/name>` | don't start until the named job(s) finish (dependency chains) |
| `#$ -wd /path` | working dir (use a Scratch path) |
| `#$ -N name` | job name (what `qstat -r` matches — plain `qstat` truncates it) |

**Walltime limits (confirmed):** 1 core → **72 h**; 2–36 cores (and 2–48 on U/V, 2–64 on T) → **48 h**.
Our trainings request **3 h** = ≥16× margin. **Arrays**: the docs' own example is `#$ -t 1-10000`
(large arrays are normal); `-tc` throttles concurrency; one array = one `qsub` (never loop qsub —
respect the 10/s submit limit). `$SGE_TASK_ID` indexes the task. **Automatic rerun** `#$ -r y` lets
SGE requeue a task after a node failure (we also requeue from the driver).

## 4. GPU specifics (verbatim from the GPU-nodes / Young-GPU pages)

- Request a **type** with `-ac allow=EF` (V100) or `-ac allow=L` (A100-40); up to 4 GPUs + 36 cores in
  one node; MPI-with-GPU only within a single node.
- **Device cgroups (10 Aug 2022, verbatim):** *"At the start of the pilot, jobs did not share nodes
  and users always had access to all GPUs on each node. This has since been altered and device cgroups
  are implemented (as of 10 Aug 2022) so jobs can share nodes on the GPU nodes and each only have
  access to the number of GPUs they requested."* Example: many single-GPU jobs share a node, each
  isolated. **`-ac exclusive`** = *"Exclusive use of node: no other jobs are allowed to run on the rest
  of this node."*
- **`CUDA_VISIBLE_DEVICES`** is set for the job; the allocated GPU(s) are **renamed 0,1,…** inside the
  job (location IDs unchanged) → our code using `cuda:0` correctly targets our allocated GPU. **No MPS
  needed** — for packing we launch N processes ourselves on the one visible GPU (they time-slice it;
  our ~2–3 GiB/training fits 4–5 in a 16 GB V100).
- **CUDA modules are old** (`cuda/7.5.18` … `cuda/11.3.1`); bundled TF/PyTorch modules are old
  (`pytorch/1.11.0/gpu`). → We **bring our own** `torch 2.6.0+cu124` (the wheel bundles its CUDA
  runtime; only the host NVIDIA *driver* matters), via a venv or an Apptainer `.sif`. Confirmed
  necessary.

## 5. Storage & data (verbatim from Data_Storage + Myriad pages)

- **Home = Scratch on Myriad**, *"all of your home space should be considered scratch"*, **1 TB**,
  **NOT backed up** ("should not be relied on for secure long-term storage; back up regularly"). Check
  with `lquota` (also `gquota` on the Myriad page — verify at G0). There is also a **file-count
  (inode) quota** — conda/venv trees burn inodes fast (a real HPC gotcha); prefer a lean venv or a
  single `.sif`.
- **ACFS** (`/home/<user>/ACFS` or `/acfs/users/<user>`): *"backed-up location for data which you wish
  to keep"*, **backed up daily**, **read-only on compute nodes**. → **gold input panel + frozen bundle
  live here** (immutable, backed-up input); outputs go to Scratch.
- **`$TMPDIR`**: fast local disk, **only exists during the job, wiped at end**, unrecoverable on
  failure/timeout. Use for the transient staged gold + working files; **archive every record to
  Scratch** (then mirror off-cluster).
- **Retention / expiry (staged):** at quota expiry, day-of → quota reset (new files blocked); +1 month
  → data moved aside; +3 months → deleted. Reminders at 1 mo / 2 wk / 1 wk / day / +1 mo. Shared
  spaces reapply every 12 months. Irrelevant at our ~8-week horizon but wired into the evacuation
  checklist.

## 6. Software environment & containers (verbatim from the Apptainer page)

- **Modules:** `module load ...`; for a GPU job unload the default compilers/mpi first, then load
  `cuda`. Our approach is a self-contained venv (or `.sif`), so we lean on the module system only for
  `apptainer` (and optionally a recent Python).
- **Apptainer** (`module load apptainer`; `singularity` is a symlink to it):
  - **Build directly on login/compute nodes** — *"as long as they use a LOCAL filesystem and not home
    or Scratch"* → **build in `$TMPDIR`, then move the `.sif` to Scratch.** Use `--fakeroot` (no root
    on HPC): `apptainer build --fakeroot img.sif def.def`.
  - **No Dockerfile support** → write a `.def`, OR convert a Docker image:
    `apptainer pull img.sif docker://pytorch/pytorch:...`.
  - **GPU:** run with **`--nv`** (exposes the NVIDIA devices + CUDA libs into the container).
  - **Bind mounts:** `$HOME` is auto-bound; **on Myriad Scratch is NOT separately auto-bound** — but
    since Scratch ⊂ `$HOME` on Myriad, the home bind covers it. Bind ACFS explicitly if a container
    must read gold (`--bind /acfs/users/<user>`). Cache: `export
    APPTAINER_CACHEDIR=$HOME/Scratch/.apptainer`.
  - Our Plan-B Dockerfile → convert to a `.def` or `apptainer pull` the base image. Apptainer is the
    hard fallback if the venv path hits a driver mismatch.

## 7. Throughput, fair-share & policy

- **Fair-share is the real limiter, not permission.** Free use is governed by fair-share priority that
  decays as you consume → a front-loaded burst then a decaying sustained rate. Our two-stage doctrine
  is queue-optimal (Stage 1 on fresh priority; Stage 2 rides the tail).
- **Production courtesy throttle (nf-core, live):** `queueSize=100` concurrent submitted jobs,
  `submitRateLimit=10/1s`. Our driver respects both: bulk work as throttled arrays (`-tc`), submits
  rate-limited, one array per batch.
- **ARR → CRAG (the throughput lever):** for "higher throughput than possible with fair-share," submit
  the **Additional Resource Request** form (with the PI) to **`rc-support@ucl.ac.uk`**; the **CRAG
  (Computing Resource Allocation Group) meets monthly, 2nd Tuesday**; approval is likely when "the
  impact on other users is not significant or of long duration" — our 1-GPU/3-h backfill jobs are
  exactly that low-impact shape. Extended-wallclock projects exist (e.g. `crag5day`) — we don't need
  them (3-h jobs). Paid **Gold**/node-purchase exists as a last resort (almost certainly unnecessary).
- **Acknowledgment (MANDATORY, verbatim, R9):** *"The authors acknowledge the use of the UCL Myriad
  High Performance Computing Facility (Myriad@UCL), and associated support services, in the completion
  of this work."* → verbatim into the dissertation Acknowledgements **and** the paper. Include the
  `Myriad@UCL` label so UCL can track the output.

## 8. How others actually use Myriad (real precedent)

- **nf-core (bioinformatics, production):** a maintained institutional Nextflow profile — `executor
  sge`, `queueSize 100`, `submitRateLimit 10/1s`, `penv smp`, mem-per-CPU, Apptainer with
  `autoMounts`, cache in `$HOME/Scratch/.apptainer/pull`. Proof that sustained, high-job-count,
  container-based pipelines are a first-class Myriad use pattern (exactly our shape).
- **De Moor et al., UCL — GPU-accelerated value iteration in JAX for perishable inventory control
  (arXiv:2303.10672):** the *closest analog to us* — a UCL group solving a large **MDP by value
  iteration/simulation** (dynamic-programming cousin of RL) that acknowledges **Myriad@UCL** verbatim.
  They **develop on a consumer GPU (RTX 3060) and scale on Myriad A100-40G (1/2/4)**, use **batching**
  of states and **`pmap` multi-device** mapping; a run went **11,496 s → 4,838 s (RTX 3060 → single
  A100, ≈2.4×)**. This validates (a) our develop-on-laptop / confirm-on-Myriad pattern and (b) our
  ~1.75× laptop→V100 planning constant (V100 is modestly slower than A100, so 2.4× consumer→A100 is
  consistent). It is a citable, in-domain precedent that the facility fits MDP/RL compute.
- **Breadth:** Myriad acknowledgments appear across chemistry (MOF free energies), quantum computing,
  wireless-comms simulation (MATLAB Parallel Server), and astrophysics — a general single-node
  high-throughput workhorse, not a niche system. Our usage is squarely within its intended envelope.
- **Caveat learned:** several "UCL HPC" ML tutorials online are for the **CS-department cluster**
  (`tmem`, `gpu=true`, `/share/apps`, `conda`) — **NOT Myriad** (`mem`, `gpu=1`, `module load`). The
  generic array pattern (`-t 1:N -tc K`, read config by `$SGE_TASK_ID`) transfers; the resource syntax
  does not. The **inode-quota** warning (venv/conda burn the file-count limit) does transfer.

## 9. The canonical Myriad jobscript for us (assembled from the confirmed facts)

```bash
#!/bin/bash -l
#$ -N llmrp_search_g0            # qstat -r matches this; -hold_jid can reference it
#$ -l h_rt=3:0:0                 # 3 h (>=16x margin under the 48 h multi-core cap)
#$ -pe smp 4                     # 4 cores
#$ -l mem=4G                     # per core -> 16 GB
#$ -l gpu=1                      # one cgroup-isolated GPU (packing runs N procs on it)
#$ -ac allow=EF                  # pin to the V100 pool (device homogeneity)
#$ -l tmpfs=15G                  # local scratch for the staged gold + working files
#$ -t 1-30 -tc 12                # array of 30 tasks, <=12 concurrent (fair-share-friendly)
#$ -wd /home/<user>/Scratch/llmrp
# --- environment (own runtime; system CUDA/torch are too old) ---
export PYTHONPATH=/home/<user>/llmrp:$PYTHONPATH
source /home/<user>/llmrp/venv/bin/activate      # OR: apptainer exec --nv img.sif ...
# --- stage immutable gold from ACFS to fast local disk (optional) ---
cp /acfs/users/<user>/llmrp-inputs/gold.parquet "$TMPDIR/" && export LLM_RP_GOLD_STAGED_DIR="$TMPDIR"
# --- run one task; write the atomic record to Scratch (mirrored off-cluster) ---
python -m src.cluster.run_one --spec "$SGE_TASK_SPEC_FOR_$SGE_TASK_ID"
```
This matches what `src/cluster/jobscript.py` renders; §12 lists the few facts to double-check against
the current renderer.

## 10. Zero-problem checklist deltas (feed into PLAN §6)

- **G0 (first login, ≤30 min):** in a `-l gpu=1 -ac allow=EF` interactive job run `nvidia-smi -L` and
  `echo $CUDA_VISIBLE_DEVICES` → confirm **exactly one** GPU visible as index 0 (Myriad-specific
  confirmation of the cgroup isolation documented cluster-wide). Also `lquota`/`gquota`, `module avail
  apptainer`, and a 2-process pack smoke on the one GPU.
- **G1 (cert):** the fps micro-benchmark on EF **and** a `-tc` scale test that MEASURES achieved
  sustained concurrency + queue waits over 24–48 h → the freeze-time timeline uses the MEASURED C, and
  the pack ×N factor uses the MEASURED 2-process throughput.

## 11. Sources (all read first-hand, 2026-07-08)

- Myriad cluster page — https://www.rc.ucl.ac.uk/docs/Clusters/Myriad/
- GPU nodes — https://www.rc.ucl.ac.uk/docs/Supplementary/GPU_Nodes/ (+ raw md in `UCL-ARC/mkdocs-rc-docs`)
- Young GPU nodes (device-cgroup verbatim) — https://www.rc.ucl.ac.uk/docs/Supplementary/Young_GPU_Nodes/
- Example jobscripts — https://www.rc.ucl.ac.uk/docs/Example_Jobscripts/
- Experienced-users quick ref — https://www.rc.ucl.ac.uk/docs/Experienced_Users/
- Data storage — https://www.rc.ucl.ac.uk/docs/Background/Data_Storage/
- Apptainer/Singularity — https://www.rc.ucl.ac.uk/docs/Software_Guides/Singularity/
- Additional Resource Requests / CRAG — https://www.rc.ucl.ac.uk/docs/Additional_Resource_Requests/
- Acknowledging RC systems — https://www.rc.ucl.ac.uk/docs/Clusters/Acknowledging_RC_Systems/
- Open OnDemand — https://www.rc.ucl.ac.uk/docs/Supplementary/OnDemand/
- nf-core Myriad production config — https://nf-co.re/configs/ucl_myriad/
- UCL Myriad precedent paper (JAX value iteration, MDP) — arXiv:2303.10672
- Generic SGE array/dependency pattern (UCL CDT tutorial; CS-cluster syntax caveat) — github.com/andre-vauvelle/hpc-tutorial

## 12. Reconciliation with our plan (actionable)

**CONFIRMED (now first-hand):** 74 GPUs / node inventory; SGE + `qsub/qstat/qdel/qacct`; directives
`-l h_rt/mem/tmpfs/gpu`, `-pe smp`, `-ac allow=EF|L`, `-t/-tc`, `-hold_jid`, `-r y`; walltime 72 h/48 h;
home=Scratch 1 TB not-backed-up + ACFS backed-up read-only-on-compute; ARR→CRAG (2nd-Tue, rc-support);
the Myriad@UCL acknowledgment text.

**VALIDATED (was flagged as the top risk):** GPU **device cgroups (10 Aug 2022)** ⇒ the §15 packing
lever is sound. Downgrade the "cgroup-exclusivity UNCONFIRMED → timeline could double" risk to "G0
confirms on Myriad" in PLAN §5/§6/§15 and the CHANGELOG.

**CORRECTED / SHARPENED:** home==Scratch (1 TB combined, not a separate Scratch); local `$TMPDIR`
1.5 TB on V100 nodes; CUDA modules top out at 11.3.1 (own torch required — confirmed); Apptainer
**builds on local fs only** (`$TMPDIR`, not home/Scratch) + no Dockerfiles (use `.def`/`pull`); the
`queueSize=100` / `10-per-s` figures are the nf-core production throttle (source them); `lquota` is the
storage-page command (Myriad page says `gquota` — verify at G0); watch the **inode quota**.

**NEW to exploit:** Open OnDemand browser monitor (`ood.myriad.rc.ucl.ac.uk`, pilot via rc-support) as
the human queue view alongside the sentinel; `-ac exclusive` to grab a whole node if ever useful;
`CUDA_VISIBLE_DEVICES` renumbering ⇒ `cuda:0` is correct.

**RESIDUAL G0 items (Myriad-specific confirmations):** one GPU visible under `gpu=1` (cgroup);
`lquota` vs `gquota`; apptainer module present; 2-process pack throughput. All in `scripts/myriad/g0_probe.sh`.

---

## 13. Round-2 research (2026-07-08) — capabilities we can USE + one migration risk

**(a) GPU MPS + packing density — a real Stage-2 throughput lever.** Our SAC trainings launch small
kernels on ~2–3 GB → they *underutilise* the GPU (a single process ~20% SM utilisation), which is
exactly why packing pays. Two ways to pack our OWN cgroup-exclusive GPU (no admin needed): **(i)
time-slicing** (just launch N processes — the default; safe, full process isolation, net ~×1.75–2 from
filling the idle gaps); **(ii) CUDA MPS** (`nvidia-cuda-mps-control -d` inside our jobscript → the N
processes share one GPU context and run concurrently on different SMs → higher utilisation, potentially
×2.5–3). MPS trades isolation for throughput (a shared context couples failures), so the DEFAULT stays
time-slicing (grade-security: robustness first) and MPS is a **G1-tested optional boost**. **Density by
VRAM:** V100-16G packs ~4–5 of our trainings; **A100-40G ~12–15; A100-80G ~25–30** → the report-only
Stage-2 fleet (esp. D5's 6,000 stubs) runs dramatically faster on the A100-80 (U/V) nodes. Confirm the
per-process throughput at G1 (`ruse`/`nvidia-smi dmon` during a 2- and 4-process pack).

**(b) Compute accounting for the PAPER (Okhrati docks missing wall-clock compute).** UCL ships
`userscripts`: **`jobhist [--hours=N]`** (finished jobs with start/end times, host, exit status) →
run it across the campaign for the exact per-training timeline ⇒ total wall-clock + GPU-hours for the
methods section; **`qacct -j <job>`** (full resource usage; `-m -j` says if a job was killed for
time/memory); **`nodesforjob <jobid>`** (live load/mem/swap — verify a packed node isn't swapping);
**`qexplain <jobid>`** (untruncated error for a failed job — better forensics than qacct);
**`scriptfor`/`envfor <jobid>`** (recover a past jobscript/env). `ruse` (`module load ruse/2.0`) and
`/usr/bin/time --verbose` profile peak memory (informs pack density). Source: UCL-ARC/go-clustertools
+ rcps-cluster-scripts on GitHub.

**(c) `qstat` job states → a monitoring upgrade.** States: `qw` (queued), `hqw` (held), `r` (running),
**`Eqw` (jobscript error — will NEVER run)**, `t` (transferring), `dr` (deleting). Our driver already
recovers an `Eqw` task via the no-record → requeue → exhaust path, but the sentinel's queue panel
should surface `Eqw` explicitly (a stuck-in-error job is a silent stall). *Flagged as a G1 monitoring
improvement* (needs the driver's `batch_jobs_in_queue` to parse the state column, not just names).

**(d) Fair-share & priority (sharpens the sustained-C estimate).** Regular use is fair-share; priority
decays as you consume (front-loaded burst → decaying tail — our two-stage doctrine is queue-optimal).
Paid **Gold** jobs "greatly increase the likelihood of being next to run" (non-Gold rarely reaches
"priority 3"); purchased nodes convert to a **quarterly priority-cycle** allocation usable
cluster-wide. We plan free fair-share + the ARR; Gold is the last-resort lever if the deadline ever
tightens.

**(e) T-type nodes (6× AMD EPYC 64-core, 768 GB, no GPU) for the CPU analysis.** Our post-campaign
analysis (variance decomposition over k=3, bootstrap CIs, specification-curve, permutation panels) is
embarrassingly-parallel CPU work → a single `-pe smp 64` job on a T-node runs it fast, off the GPU
pools. Minor but free efficiency for the bank-gate analysis + `notebooks/` regeneration. OOD Jupyter
(§2) can drive it interactively.

**(f) ⚠ THE MIGRATION RISK — SGE → Slurm (grade-security contingency).** UCL is moving Myriad to
**RHEL 9.5 + Slurm** (Kathleen migrated June 2025; new Myriad GPFS filesystem live since April 2025).
**As of June 2026 Myriad is STILL SGE, operational, with NO scheduled migration date** ("await official
announcement"). So SGE is correct for our July–Sep window, but a mid-campaign switch would break every
SGE jobscript. Because our scheduler interaction is isolated to `jobscript.py`/`submit.py`/`poll.py`,
the port is bounded — the mapping (to pre-write a Slurm renderer if the announcement lands):

| SGE (`#$`) | Slurm (`#SBATCH`) |
|---|---|
| `-N name` | `--job-name=name` |
| `-l h_rt=H:M:S` | `--time=H:M:S` |
| `-l mem=XG` (per core) | `--mem-per-cpu=XG` |
| `-pe smp N` | `--cpus-per-task=N` (or `--ntasks=N`) |
| `-l gpu=N` | `--gres=gpu:N` |
| `-l tmpfs=XG` | `--gres=…,tmpfs:XG` |
| `-ac allow=EF` | `--partition=…`/`--constraint=…` (Myriad V100 partition TBD at migration) |
| `-t 1-N` + `-tc K` | `--array=1-N%K` |
| `-hold_jid JID` | `--dependency=afterok:JID` |
| `qsub`/`qstat`/`qdel`/`qacct` | `sbatch`/`squeue --me`/`scancel`/`sacct` |

Slurm requires all `#SBATCH` lines together at the top; `--export=ALL` copies the login env. Reference:
the UCL Slurm doc page + `kathleen-ng.rc.ucl.ac.uk` (already RHEL9/Slurm) for a live template.

**Round-2 sources:** Job_Results / howto (jobhist/qacct/nodesforjob/qexplain/qstat-states/ruse);
Paid-For_Resources (Gold/priority-cycles); Supplementary/Slurm (SGE→Slurm mapping); Status_page +
search (migration timeline: Kathleen done 06/2025, Myriad unscheduled as of 06/2026); NVIDIA MPS
concept (abhik.ai / SchedMD). The A100-80 pack density is an arithmetic bound from 80 GB ÷ ~2.5 GB.

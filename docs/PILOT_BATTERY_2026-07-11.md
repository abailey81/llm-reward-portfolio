# Pre-freeze pilot battery (2026-07-11) — every remaining unknown, one decision-ruled pilot each

> Tamer, 2026-07-11: *"can we make a lot of advanced and sophisticated and extremely accurate and
> precise pilots and run them on Myriad to identify everything?"* Answer: not *a lot* — a **targeted
> battery**. Precision here means each pilot names ONE unknown, carries a **pre-stated decision
> rule**, touches **train/val only** (the sealed test leg is read by nothing), and uses CRN pairing
> where applicable. Most unknowns are already closed by the pilots that ran (σ_D, convergence B\*,
> G0/G1, crash rehearsals); this battery closes the enumerated remainder. Total ≈ **33 GPU-h ≈ 1.2%
> of the campaign floor**, elapsed 1–3 queue-bound days that fully overlap the communication build
> (the write-up work loses nothing).

## 0. Why the battery exists — the incident that proves the method

The 2026-07-11 rehearsal's three arrays **vanished from the queue without running** (no `qacct`
record). First-hand diagnosis: the rendered jobscript carried **literal `~` paths** — SGE `#$ -wd`
directives expand neither `~` nor `$HOME` (→ the array Eqw-dies at dispatch; UCL cleanup deletes it
traceless), quoted bash strings keep `~` literal (the spec push even created a literal `~` directory
under `$HOME`, since removed), and `PYTHONPATH` never expands `~`. **This was a guaranteed
campaign-day-1 breaker.** Fixed 2026-07-11 (tilde-free render contract + fail-loud validation at the
render choke point + `remote_home`/`expand_remote` resolution in the entry point + regression
tests; cluster suite green). The lesson is the battery's charter: *only a live execution on the real
scheduler surfaces this class of defect* — dry-runs and unit tests all passed while the bug shipped.

## 1. The battery

| # | Pilot | Unknown it closes | Design | Decision rule (pre-stated) | Cost |
|---|---|---|---|---|---|
| **P0** | **Rehearsal relaunch** (fixed code) | the Apptainer-on-node campaign path — the ONE untested piece | 3 arms × 2 gen × 4 cand × 1 seed × 10k steps, Qwen `--pass-mode B`, `--synthetic`, spend-capped | a node-produced training record lands in the archive → **path CERTIFIED**; any node error → fix, repeat until green | ~0.5 GPU-h + ~¢ Qwen |
| **P1** | **Packing factor F** | trainings/GPU (multiplies all wall-clock math) | pack ∈ {1, 2, 3, 5} × 3 trainings × 50k steps, `--cores-per-training 1–2` | F = argmax aggregate steps/s s.t. per-training slowdown ≤ 15%; feeds `recommend_assurance_target` | ~3 GPU-h |
| **P2** | **Sustained concurrency C** | fair-share placement rate (the honest days-formula input) | ~~standalone probe~~ **DROPPED as redundant** — the live arrays' epilogue ledgers + `qacct` timestamps ARE the placement experiment | C_central for the wall-clock model, derived from the fleet | $0 |
| **P3** | **Full-length anchor** | h_rt sizing, memory/thermal stability at B\* (32.6 min is an 8-min extrapolation) | ONE real-gold 200k training (H1 baseline reward, seed 0, train/val windows) on a V100 | campaign array h_rt = 1.5 × measured wall; memory high-water < 8 GB | ~0.6 GPU-h |
| **P4** | **Cross-node determinism** | does the determinism spine (seeded stacks + CUBLAS workspace) hold ACROSS V100 nodes? | the SAME spec + seed run on two different EF nodes | identical final eval metrics → replay-from-archive claim holds on the cluster; any drift → documented and folded into the seed-variance framing (never silently) | ~1–2 GPU-h |
| **P5** | **Resume-under-fire** | driver death mid-batch on the REAL cluster (the campaign's scariest failure) | kill the driver after first completions during P0/P1; restart `--resume`; run `resume_audit.py` | zero lost + zero duplicated trainings (resume_audit exit 0) | ~0 (piggybacks) |
| **P6** | **B\*-on-authored-rewards ladder** ⚠ needs Tamer's go | the R74 blind spot: the 25k→350k flatness was measured on ONE hand-written reward (`differential_sharpe`); authored-reward curve shape is unmeasured | 2 archived prototype winner rewards (distributional + scalar; Sonnet-authored code replayed from the archive) × 3 CRN seeds × {100k, 200k, 400k} = 18 trainings, train/val only | if eval-IQM(400k) − eval-IQM(200k) > 2×seed-SE for EITHER reward → propose a B\* amendment BEFORE freeze; else **B\* = 200k stands with the authored-reward blind spot closed** (and the examiner answer becomes "measured to 2×B\* on authored code") | ~20 GPU-h, $0 API |
| **P7** | **D5 calibration early-start** (laptop, parallel) | pipeline's realized α = 0.05 (already Stage-2.C; starting early is free) | keyless synthetic fleet on the laptop | as specified in Stage-2.C | $0; gated on clearing C: (14 GB < 20 GB floor) |

**Sequencing.** P0 first (it certifies the path everything else uses) → P1–P4 submitted together
(independent arrays) → P5 fired during P1 → P6 after P0 (needs real gold staged + 3 h h_rt). P7 on
the laptop in parallel. Every pilot is queue-bound waiting, so **the communication build (the
highest-EV grade work) proceeds in the foreground throughout.**

## 2. Explicitly NOT piloted (each rejected with its reason — resist the volume urge)

- **σ_D re-estimation at larger n** — the E1 assurance ladder already powers the SESOI at the χ²
  UPPER confidence bound on σ_D (uncertainty absorbed by design), and rung 100 tightens σ in-campaign;
  re-opening supervisor-approved tiers is churn with no decision it could change.
- **Intraday data** — settled analysis (2026-07-11): attacks marginal estimator noise, which is not
  the binding object (paired-on-common-path differences are well-determined); cannot see overnight
  gaps; explodes episode length ×7–390 and breaks the γ-horizon, licensing, PIT auditability, and the
  cost model.
- **Prompt / construct experiments on the frozen prompts** — hash-bound; construct validity verified
  (tail-neutral base prompts, R38); any change re-opens the manipulated variable.
- **More candidates / arms / SESOI variants** — settled rejections (multiplicity; identification).
- **Anything that reads the sealed 2020–2026H1 test leg** — never, under any pilot.

## 2b. MAX-THROUGHPUT CAMPAIGN RUNBOOK (2026-07-11, Tamer: "push absolutely everything to the
## maximum — hardware only, no science reduction")

The throughput identity: `trainings/hour = C (GPUs held) × F (pack) × 1/wall − overheads`.
Every lever below is hardware/scheduling-side ONLY — B\*, arms, seeds, splits, prompts untouched.

> **CRAG reservation = REJECTED by Tamer (2026-07-11: "we won't use CRAG — we can finish
> without").** The campaign runs on **fair-share alone**; the draft application was deleted. The
> design already absorbs fair-share variability BY CONSTRUCTION: the distinction floor banks first
> (C0–C3, ~644 GPU-h), and the E1 assurance ladder's stopping tier is chosen EXOGENOUSLY from
> measured throughput vs the deadline — a slow queue costs only the marginal rung, never the study.
> The levers below are the complete fair-share-side speed budget.

**Levers, in EV order:**
1. **Packing (the F lever — now the dominant controllable).** P1 ladder in flight (pack 2/3/5 = jobs 772152–4, pack 8 = 772286;
   cores = pack × 1). Campaign policy: `--pack F*` at the measured optimum, `--cores-per-training 1`.
   If scaling is sublinear from SM contention, per-job **NVIDIA MPS** (`nvidia-cuda-mps-control`,
   user-space, legal on a cgroup-owned GPU) is the P1-conditional follow-up.
2. **Device-stratified seed blocks (the C multiplier — RATIFIED 2026-07-11).** Tamer granted
   full delegated permission ("solve all other issues yourself") in the max-speed directive after
   this lever was put to him; ratified as a dated pre-freeze EXECUTION note (CHANGELOG
   [2026-07-11c]): whole SEED BLOCKS may be assigned to different GPU pools (e.g. seeds → V100/EF
   and A100/L blocks). Validity: the inference is PAIRED per seed (CRN) — every contrast
   D_s = X_a,s − X_b,s compares arms trained on the SAME device at the same seed, so each pair
   stays device-homogeneous and the device cancels in the difference (a randomized-block design);
   the only conceivable threat (a device×arm interaction) is directly reported as a per-device D̄
   diagnostic table (env_fp records the GPU per record, S6). Adds ~24–30 A100s to C (≈ +60–80%
   throughput). Implemented FLAG-OFF (`--seed-pool-blocks "EF:0-283,L:284-567"`); the default
   single-pool path is byte-identical to the certified one.
3. **Backfill-tight walltime (the placement lever).** BUILT: `--h-rt` threads
   entry→campaign→driver→jobscript. Campaign value = measured wall × 1.5 (e.g. `0:50:0` at
   pack=1/B\*; `1:15:0` at pack=5 waves) instead of the 3 h default (a 5.5× over-request that
   disqualifies tasks from backfill gaps). P3/P6 measure the exact wall.
4. **Launch timing + fair-share hygiene.** Launch C0–C3 Friday evening / weekend (measured: the
   queue drains overnight); keep pre-campaign usage tiny (pilots ≈ 60 GPU-h — negligible share
   burn); the C-ladder's `-p` self-deprioritization already orders our own jobs correctly.
5. **Poll cadence.** Driver `--poll-secs 180` during search phases (generation turnaround), 600
   during the long test flood. Marker-hold chains already pre-submit test arrays at zero latency.
6. **Node-local staging, containerised env, ≤2 fast-fail requeues, `-r y`, 3-site mirror** — all
   already built; no per-task pip/network on nodes.
7. **⚠ MEASURED CLUSTER POLICY (2026-07-11 ~21:00): array-tail serialization under contention.**
   The Myriad policy JSV (`account: policyjsv`, injected `snx=1`) moved tasks 2..N of EVERY pending
   array to `hqw`, leaving task 1 schedulable — arrays serialize internally during high contention
   (not a user hold; `qrls` no-ops). Two consequences, both encoded here: (a) **fleet shape
   matters**: many SMALL arrays ≫ one giant array under this policy (16 arrays → up to 16
   concurrent eligible tasks even fully serialized) — if the policy is active at campaign time,
   submit the C4 sweep as CHUNKED arrays (per-arm × seed-chunk) rather than monoliths; the driver
   already batches per-arm/per-generation, and `--seed-pool-blocks` chunking doubles as this
   mitigation. (b) **Watch the cascade**: if task 2 flips `hqw→qw` when task 1 completes, the
   policy is self-releasing (serialized but automatic); if not, rc-support is the escalation path.
   The fleet monitor observes exactly this transition.

**Rejected, with reasons (so no one re-litigates under time pressure):**
- **torch.compile on the cluster** (Triton works on Linux): ~10–30% per-training gain, but it
  changes numerics → breaks laptop↔cluster parity + the determinism spine, and compile warmup eats
  much of the gain on 33-min jobs. Speed is bought with packing instead.
- **Larger batch / smaller nets / fewer steps:** science reduction — out by definition.
- **Kathleen / CS cluster:** no GPUs / separate access regime.
- **`-ac exclusive` node grabs:** wastes 3 of 4 GPUs per node unless pack ≥ 9 per card lands.

## 3. Standing decisions this battery feeds

- **The stopping tier** (E1): P1's F + P2's C → `recommend_assurance_target(tph, days)` picks the
  deadline-safe rung exogenously at the C3→C4 gate.
- **The freeze**: P6 is the only pilot that could still move a frozen number (B\*), which is exactly
  why it runs pre-freeze. P0–P5 are execution-layer and gate the CAMPAIGN, not the freeze.
- **Pending Tamer (unchanged):** freeze (his act), force-push, Anthropic top-up ~$70, UCL password
  rotation, C: disk cleanup; plus the two open design calls — **P6 go/no-go** and the **A5
  rational-insensitivity fingerprint amendment** (option 1: surgical pre-freeze amendment, hash
  moves; option 2: Stage-2-doc-only registration).

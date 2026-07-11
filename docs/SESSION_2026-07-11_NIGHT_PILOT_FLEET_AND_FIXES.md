# Session record — 2026-07-11 evening → night: the pilot fleet, three campaign-breaking bugs, and the measured throughput model

> **Purpose.** Complete, self-contained record of everything done in the 2026-07-11 evening/night
> session (continuation of `SESSION_2026-07-11_GRADE_STRATEGY_AND_HANDOFF.md`). Every claim below
> was verified first-hand in-session; job ids are real SGE submissions; commits are on
> `myriad-cluster-and-tier-system`. Companion operative doc: `PILOT_BATTERY_2026-07-11.md`
> (the battery + the max-throughput runbook). CHANGELOG entries: `[2026-07-11b]`, `[2026-07-11c]`,
> `[2026-07-11d]`.

---

## 0. TL;DR

- **The campaign execution path is now CERTIFIED live on Myriad** (Apptainer → containerized venv
  → `run_one` → `train_candidate` on real ACFS gold → archived records with real `val_fitness`).
- **Three campaign-day-1 breakers were found and fixed tonight**, each only findable by live
  execution: (1) literal-`~` paths (arrays Eqw-died traceless), (2) the wrong-provider string +
  the TEMP-Qwen-config dependency, (3) cross-campaign batch-name collision in the driver's
  double-submit guard (silent infinite wait).
- **The throughput model is now measured, not estimated**: 102.2 steps/s solo; 66.4 steps/s each
  at pack-2; ~860 s fixed per-task overhead (amortizes at B\*); → 1.28 (unpacked) / 1.86 (pack-2)
  trainings per GPU-hour at B\*=200k.
- **Campaign wall-clock (measured constants, C = fair-share GPUs held):** floor 1,104 trainings =
  4.1/2.1/1.0 days at C=6/12/24; the 95% target (5,580) = 20.8/10.4/5.2 days; ceiling n=568
  (8,130) = 30.3/15.2/7.6 days. Every stop is a valid design (E1 exogenous ladder).
- **Amendment R76 landed pre-freeze, pre-data** (A5 rational-insensitivity account + the fed-delta
  SNR/attenuation exhibit); canonical hash `79a6db44` → **`e3a8c880`**, gate 21/21 GREEN.
- **Tamer's decisions tonight:** no CRAG (fair-share only) · device-stratified seed blocks
  RATIFIED (delegated) · Myriad-picks-up ⇒ laptop-stops dedup rule · B\* ladder extended to 1.6M ·
  the full prototype moved to Myriad · C:\ disk resolved (Windows.old removed → 30.5 GB free).

---

## 1. Chronology (evening → night)

1. **Full-context re-read** (Tamer: "deep full understanding") — all operative docs + the
   pre-registration + the IFTE0008 rubric re-read first-hand; freeze gate re-run GREEN.
2. **Live-state verification** found the previous rehearsal's 3 arrays VANISHED (no qacct trace)
   and C: at 14 GB (< the 20 GB floor).
3. **Design Q&A** (intraday? B\*=200k global? episodes?) — answered with fresh measurements
   (see §4); surfaced the fed-delta noise-floor insight → later became Amendment R76.
4. **Root-caused the vanished arrays**: literal `~` in SGE directives/quoted-bash/PYTHONPATH →
   Eqw at dispatch → admin cleanup deletes traceless. Fixed + committed (`387a0f7`); the literal
   `~` junk dir on the cluster verified (44 K, ours only) and removed.
5. **Pilot battery planned** (`PILOT_BATTERY_2026-07-11.md`) and, on full permission, LAUNCHED:
   P0 rehearsal relaunch, P6 authored-winner B\* ladder (18 tasks), P1 packing 2/3/5(/8),
   P4 determinism pair, P8 full prototype-on-Myriad; P2 dropped as redundant; P3 subsumed by P6.
6. **Amendment R76** (A5 + instrument (h)) committed (`db52495`); hash → `e3a8c880`.
7. **Throughput levers built** (`02cf8c3`): `--h-rt` backfill threading, pack-8 probe; CRAG draft
   (later DELETED on Tamer's rejection, `bbd2c5d`); device-stratified seed blocks ratified under
   delegated permission and wired flag-off (`--seed-pool-blocks`, same commit).
8. **C: disk resolved**: `C:\Windows.old` (19.8 GB, the 07-10 repair rollback — rollback
   undesirable) removed via Disk Cleanup `sagerun` → **30.5 GB free**.
9. **Myriad policy event (~21:00)**: every pending array's tasks 2..N moved to `hqw` (task 1
   schedulable) — array-tail serialization under contention (`policyjsv`, injected `snx=1`);
   documented + chunked-array mitigation encoded (`e4ab4f3`).
10. **Laptop pivot** (Tamer): GPU clock lock re-applied; both P6 ladders launched as 2 concurrent
    processes (~10–11 h); laptop + cluster ultramonitors armed. Then the dedup rule: first Myriad
    P6 record ⇒ kill the laptop ladders.
11. **First placements & the certification**: `p1pack2` ran and completed on `node-e00a-005`
    (`ok: 2`, 2 records, real `val_fitness` 0.0519) — **the Apptainer-on-node path is certified**;
    `p4det` leg-1 completed on `node-e00a-007`; `p1pack5` started; `p1pack2c4` (the CPU-vs-GPU
    discriminator, `26d9acb`) submitted after the F confound was recognized.
12. **The batch-name collision bug** (§3.3) found because Tamer asked "did the prototype run?" —
    fixed (`83b06ee`), the prototype's 5 orphaned arrays qdel'd, the driver relaunched namespaced
    (`--batch-tag pm`).

## 2. Commits (all on `myriad-cluster-and-tier-system`; freeze hash `e3a8c880` untouched by all
   except the R76 amendment itself, which moved it deliberately)

| Commit | What |
|---|---|
| `387a0f7` | Tilde-free jobscript contract (the Eqw root cause) + `PILOT_BATTERY` doc |
| `db52495` | **Amendment R76**: A5 account + fed-delta SNR/attenuation exhibit (hash → `e3a8c880`) |
| `efe60de` | `learning_curve --reward-source` (authored-source ladders, sandbox-parity compile) |
| `ed742b2` | `p6_authored_ladder.py` — P6 as a Myriad array on campaign parity rails |
| `85d3c7a` | `myriad_probes.py` — P1 packing + P4 determinism probes |
| `b5e3d39` | P6 extended to 800k + 1.6M (`--budgets`/`--batch-name`, auto h_rt) |
| `02cf8c3` | `--h-rt` backfill threading + pack-8 + runbook (CRAG draft — superseded) |
| `e4ab4f3` | Runbook: the measured array-tail serialization policy + chunking mitigation |
| `bbd2c5d` | CRAG REJECTED (draft deleted) + device-stratified seed blocks RATIFIED + wired |
| `26d9acb` | Probes `--cores-total`/`--name-suffix` (the F confound discriminator) |
| `83b06ee` | **`batch_tag`** per-run namespacing (the cross-campaign collision bug) |

## 3. The three campaign-day-1 breakers (all found by LIVE execution — the battery's charter)

### 3.1 Literal `~` paths (fixed `387a0f7`)
SGE `#$ -wd/-o` expand neither `~` nor `$HOME` → arrays **Eqw at dispatch** → UCL cleanup deletes
them with **no qacct record** (deleted-before-start jobs write no accounting). Quoted bash keeps
`~` literal (the spec push created a literal `~` directory under `$HOME`); `PYTHONPATH` never
expands `~`. Two unit tests had regression-locked the broken form. Fix: fail-loud tilde validation
at the render choke point; absolute `remote_root` required; `$HOME/…` shell-only defaults;
`remote_home()`/`expand_remote()` resolution in the entry point.

### 3.2 Provider string + config dependency (operational)
`--provider qwen` is not a provider (`openrouter` is; Qwen3-Coder rides through it), and the
model id comes from `config/prototype.yaml`'s `llm` block → the documented TEMP-Qwen edit is
REQUIRED for Qwen smokes (banner-marked, never committed; **revert to
anthropic/claude-sonnet-4-6 after the rehearsal**).

### 3.3 Cross-campaign batch-name collision (fixed `83b06ee`)
`driver.batch_jobs_in_queue` matches queued jobs **by name across the user's whole queue**. The
prototype's `distributional_g0`/`scalar_g0` matched the rehearsal's still-queued arrays of the
same name → the double-submit guard suppressed submission → the arm threads polled
`proto_myriad`'s archive, which those jobs never write to → **silent infinite wait** ("0/5 done,
5 pending, round 0" forever; no local batch dirs even written). Fix: `batch_tag` prefixes every
batch at the `run_batch` choke point (markers + local dirs inherit; same-run resume adoption
unaffected). **Rule: any two concurrent runs use distinct `--batch-tag`.**

## 4. Measurements (the throughput model is now empirical)

| Quantity | Value | Source |
|---|---|---|
| Solo training rate (V100, campaign dims) | **102.2 steps/s** | G1 anchor 764154 |
| Pack-2 per-training rate | **66.4 steps/s** | p1pack2 (1,612 s task) − overhead |
| Fixed per-task overhead (container+init+gold+eval+archive) | **≈ 860 s** | p4det-t1: 1,348 s for one 50k (489 s training) |
| Trainings per GPU-hour at B\*=200k | **1.28 unpacked · 1.86 pack-2** | arithmetic from the above |
| F(2) effective at B\* | **≈ 1.45** (early estimate 0.7 was an overhead artifact on 50k probes) | same |
| Pack-5 / pack-8 / pack-2@4-cores | in flight (772154 running · 772286 · 772474) | P1 ladder |
| Determinism (cross-node) | leg-1 done; verdict when leg-2 runs (byte-equal `val_returns`) | p4det |
| Queue reality (evening peak) | 369 GPU-pending vs ~74 GPUs; ~2 free V100s; 2 of ours ran concurrently | qstat/qhost |

**Design lesson encoded:** fewer/longer tasks ≫ many short ones (860 s overhead = 60% of a 50k
probe, 5% of a B\* task). The F confound (cores scaled with pack → CPU starvation vs GPU
time-slicing indistinguishable) is resolved by `p1pack2c4`: recovery ⇒ campaign packs with
`cores = 2×pack`; no recovery ⇒ MPS is the lever.

## 5. The Myriad serialization policy (measured ~21:00)

`policyjsv` (visible in `qstat -j` accounting; injected `snx=1`) moved tasks 2..N of EVERY pending
array to `hqw`, task 1 left schedulable. Not a user hold (`qrls` no-ops). **Cascade diagnostic:**
p4det task 2 did NOT release immediately when task 1 completed — grace of ~1 policy cycle, then
the escalation path is rc-support (evidence: completed task, rc=0, sibling still held).
**Mitigation encoded:** fleet-of-many-small-arrays ≫ one monolith (16 arrays → up to 16 eligible
tasks even fully serialized); the campaign's C4 sweep must be chunked (per-arm × seed-chunk;
`--seed-pool-blocks` chunking doubles as this).

## 6. Decisions made tonight (all Tamer's, executed)

1. **No CRAG** — fair-share only; draft deleted. Safe by construction (floor-first + exogenous
   ladder).
2. **Device-stratified seed blocks RATIFIED** (delegated full permission): CRN pairing is per-seed
   → whole seed blocks on different pools keep every pair device-homogeneous (randomized-block;
   per-device D̄ diagnostic via `env_fp`). Adds the A100 pools to confirmatory C (≈ +60–80%).
   Wired flag-off: `--seed-pool-blocks "EF:0-283,L:284-567"`.
3. **Laptop↔Myriad dedup rule**: whatever Myriad picks up, the laptop stops on it — armed as:
   first Myriad P6 record ⇒ kill the laptop ladders; if the cluster stalls mid-array, relaunch
   the laptop for missing rungs only.
4. **B\* ladder to 1.6M** (800k/1.6M arrays queued): the object is the held-out eval plateau, NOT
   the critic-loss minimum (Goodhart — the critic fits its replay buffer while eval degrades;
   350k < 200k measured). Any CI-separated ascent = a pre-freeze amendment PROPOSAL, never an
   auto-change.
5. **The full prototype on Myriad** (7 arms + 4 H1 baselines, real gold, 25k steps, 30 cand ×
   6 gens, seeds 0–2, Qwen, directional-only).

## 7. Live fleet at time of writing (~23:30)

| Family | Jobs | State |
|---|---|---|
| P0 rehearsal | 771926 / 771951 / 771952 | task-1 `qw`, tails `hqw` |
| P6 ladder + ext | 771972 (18) · 772246 (800k) · 772247 (1.6M) | task-1 `qw`, tails `hqw` |
| P1 packing | 772152 ✅ done · 772153 `qw` · **772154 RUNNING** · 772286 `qw` · 772474 `qw` (c4) | 2 records banked |
| P4 determinism | 772155: t1 ✅ done · t2 `hqw` (cascade watch) | 1 record banked |
| P8 prototype | relaunching namespaced (`pm_*`), driver `bho6a1l0j` | authoring/submitting |
| Laptop | 2 × P6 ladders (dist/scalar), ~10–11 h | healthy (48%+ GPU, 50 °C, 2550 MHz locked) |

**Monitors:** cluster fleet `b1vhgvyfy` (sorted-diff change detection: states, per-root record
counts, Eqw alarm) · laptop `bm05e3hzl` (ladder liveness, thermal ≥88 °C, GPU-idle anomaly,
per-ladder completion) · P0 driver `b6oq519ta` · prototype driver `bho6a1l0j`.

**Known-minor (queued fix):** cluster-path records carry `wall_clock: 0.0` (the laptop path
stamps it; `run_one` doesn't) — timing comes from the epilogue ledger meanwhile; fix before the
campaign for compute-accounting completeness.

## 8. The campaign wall-clock (measured constants; C = sustained GPUs held)

Throughput/GPU at B\*=200k: 1.28 unpacked, **1.86 pack-2** (pack-5/8 pending). Days = trainings ÷
(1.86 × C × 24):

| Milestone (trainings) | C=6 | **C=12** | C=24 | C=38 |
|---|---|---|---|---|
| ★ Floor (1,104) | 4.1 | **2.1** | 1.0 | 0.7 |
| n=403 / 95% (5,580) | 20.8 | **10.4** | 5.2 | 3.3 |
| +D1 (6,150) | 22.9 | **11.5** | 5.7 | 3.6 |
| n=568 / 99% (8,130) | 30.3 | **15.2** | 7.6 | 4.8 |

Every stop is a complete pre-registered design (E1 exogenous ladder). Even the worst column fits
1 Sep with weeks of slack. Overnight C + F(5)/F(8) + the c4 discriminator tighten this to a
single central number.

## 9. Standing next actions (decision rules already written)

- **On the ladder JSONs (laptop ~08:00 or Myriad P6):** eval(400k) − eval(200k) > 2×seed-SE on
  either winner ⇒ B\* amendment proposal to Tamer; else **B\* = 200k stands, blind spot closed**.
- **On p4det leg-2:** byte-equal `val_returns` ⇒ determinism certified on the cluster; any drift
  ⇒ documented, never silent.
- **On the cascade:** t2 still `hqw` after ~1 policy cycle ⇒ draft the rc-support escalation.
- **On first Myriad P6 record:** kill the laptop ladders (Tamer's dedup rule).
- **Pending Tamer (his acts alone):** freeze (stamps `e3a8c880`) · force-push · ~$70 top-up ·
  UCL password rotation. The TEMP Qwen edit in `prototype.yaml` reverts after the rehearsal.

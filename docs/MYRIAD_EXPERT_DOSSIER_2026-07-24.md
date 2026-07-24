# MYRIAD EXPERT DOSSIER (2026-07-24) — the scheduling ground truth, live-probed + doc-verified

> Purpose: everything that actually determines how fast our jobs run on UCL Myriad, verified
> against the LIVE scheduler configuration (`qconf -ssconf`, probed 2026-07-24), the official RC
> docs, and the SGE reference manuals — so the campaign's speed decisions rest on the scheduler's
> real arithmetic, never folklore. Standing order: NEVER lower our job priority (CLAUDE.md ★).

## 1. THE PRIORITY FORMULA (decoded from the live config — this IS Myriad)

```
prior = 4.0 * norm(POSIX -p)  +  1.5 * norm(tickets)  +  1.0 * norm(waiting_time)   [urgency 0]
```

- **POSIX term (weight 4.0)**: users can only LOWER -p (forbidden for us, ever). Everyone sane
  sits at 0 → the term cancels among competitors. Ignore.
- **Tickets (weight 1.5), policy O>S>F with functional DOMINANT**:
  `weight_tickets_functional = 5e8` vs `weight_tickets_share = 1e4` → the share-tree (usage
  history) is **negligible: 50,000× smaller**. Myriad priority is effectively usage-history-FREE.
  - **Functional = equal share per USER** (122 users pending at probe time → our slice ≈ 1/122),
    and `share_functional_shares = TRUE` → **our slice is SPLIT ACROSS OUR PENDING JOBS**
    (SGE sched_conf: "shares … shared among all the jobs associated with the object").
    → **THE LEVER: fewer simultaneously-pending jobs = more tickets per job = higher prior.**
  - Myriad overrides the array-consideration defaults (`max_functional_jobs_to_schedule 5000`,
    **`max_pending_tasks_per_job 1`**) — see §3b: big arrays concentrate tickets but ramp at
    1 task/cycle from cold, so chunking is TWO-REGIME, not one-sided.
- **Waiting time (weight 1.0)**: eligible (`qw`) jobs accrue priority while they wait.
  **`hqw` entries show prior 0.000** (live-verified) — these are BOTH genuine dependency holds
  AND each array's throttled tail beyond its one considered task (§3b). Only the eligible front
  tasks age; pipelined-rungs earns concurrency, not waiting-time credit.
- `halftime 604800` (7d) applies to the (negligible) share component. Pilot usage does NOT
  handicap us; the campaign does NOT degrade its own standing as it runs.
- `max_reservation 20` cluster-wide; our jobs carry `reserve: y` (anti-starvation, keep it).

**Live calibration (2026-07-24 04–05 UTC+5):** our eligible jobs prior 2.39–3.19 vs cluster top
3.50 → near the FRONT of the pending band; ~2,990 qw / ~700 hqw cluster-wide; 122 users.

## 2. THE HARDWARE (free-tier GPU pools)

| Pool | Nodes | GPUs | VRAM | Notes |
|---|---|---|---|---|
| **EF** (E-type) | ~19 | 2× V100 each (~38) | 16/32G (verify via the jobscript's archived `nvidia-smi` at canary) | Bigger pool, less contended — our default |
| **L** | 6 | 4× A100-40G each (24) | 40G | ~1.7–2.2× faster/training; more contended |
| U / V | 1 + 2 | 4× A100-80G each (12) | 80G | LIVE EXPERIMENT (2026-07-24): the JSV **accepted** `-ac allow=U`/`allow=V` submissions — probes 10293/10294 queued (EF control 10295). A probe RUNNING = usable (+12 A100-80G); pending >48h vs the control = effectively restricted (then qdel the probes). Runbook §10 best-hardware protocol has the branch. |

CPU nodes (D/I/B/T) irrelevant to training. tmpfs per node is large (hundreds of GB) but our
REQUEST size gates node eligibility (see lever 3). GPU job wallclock cap: 48h (2–36 cores).

## 3. THE LEVERS (all legitimate; priority never touched)

1. **TICKET CONCENTRATION — read WITH §3b's two-regime doctrine.** Fewer pending jobs = more
   tickets each (~50× between the 1,200-singleton and dozens-of-arrays extremes), but cold-start
   ramp runs at 1 task/job/cycle — so chunk BIG only under contention; under quiet skies the
   many-array flood ramps faster and tickets barely bind. GO-day congestion read decides
   (`--chunk-tasks`); always < 1000 pending jobs (max_u_jobs).
2. **Pool selection at GO** (`--pool` → `-ac allow=`): read live free-GPU headroom per pool
   (`qhost -F gpu | grep -B1 'gpu=[1-9]'`) and pin for (availability × speed), CRN-homogeneous
   per comparison unit. Default EF; L for the latency-critical core if it has headroom.
3. **tmpfs right-sizing**: we request 15G; the gold panel is 35 MB. Nodes with a free GPU but
   <15G free tmpfs EXCLUDE us. Measure the true high-water at canary → cut to peak+margin.
4. **Per-VRAM pack calibration**: pack-5 was sized conservatively; A100-40/80G can host more
   concurrent envs per GPU. Measure VRAM headroom at canary (`nvidia-smi` is already archived) →
   raise pack per pool if headroom is 2×. More effective GPUs per granted slot.
5. **Submit early / morning launch / summer window**: eligible waiting-time accrues (weight 1.0);
   late-July–August is the UK academic low season; maintenance = 2nd Tuesday (Aug 11).
6. Already optimal: pack bursts (fewer queue entries), auto-sized short h_rt (backfill-friendly),
   `reserve: y`, 12 concurrent lines, striped pools.

## 3b. THE DISPATCH MECHANICS (probed 2026-07-24 — corrects the naive ticket doctrine)

- `schedule_interval 0:10:0` + `flush_submit_sec/flush_finish_sec 1`: full cycles every 10 min;
  MICRO-CYCLES fire within 1s of any submit/finish -> dispatch is event-driven at churn,
  10-min-granular from COLD (launch, post-maintenance).
- **`max_pending_tasks_per_job 1`** (vanilla default 50): each array job exposes exactly ONE
  pending task per cycle. (This is why qstat shows each array as one qw entry at real priority +
  one hqw bundle at 0.000 — the tail tasks are throttled, not merely dependency-held.)
- `max_functional_jobs_to_schedule 5000`; RQS: one rule, DISABLED, other-user-scoped ->
  **no hidden per-user GPU caps** (the fair-share grant IS the ceiling).
- **THE CHUNKING DOCTRINE (two regimes — replaces one-sided ticket concentration):**
  - CONTENDED (grants scarce): per-job PRIORITY dominates -> chunk BIG (few heavy arrays).
  - QUIET (slots plentiful): RAMP dominates (1 task/job/cycle from cold) -> MORE arrays ramp
    faster in parallel; a monolithic 568-task array would need days just to spin up.
  - STEADY STATE (hundreds running, finishes every few seconds): flush micro-cycles make
    dispatch continuous -> chunking barely matters; the constraint bites at cold-start only.
  - GO-day rule: read live contention (`qstat -u '*' | grep -c ' qw '`); heavy -> raise
    chunk-tasks toward job-count ~dozens; quiet -> keep the mode-D flood (its many arrays are a
    RAMP FEATURE under quiet skies). Never exceed max_u_jobs=1000 pending jobs either way.

## 4. DEAD ENDS (verified — stop revisiting)

- **Self-elevation**: impossible (fair-share allows only self-LOWERING; forbidden for us anyway).
- **Usage-history worry**: a myth on Myriad (share weight 1e4 ≪ functional 5e8).
- **Idle departmental nodes**: owned/paid pools, invisible to free allocation.
- **`qsub -w v` pre-validation**: false-negatives on gpu/allow complexes; don't trust it.
- **RC fast-track**: admin-only; Tamer's standing "no RC request"; surfaced, never actioned.
- **Advance reservations (qrsub)**: `max_advance_reservations 0` + explicit ACL denial
  ("must be manager or in userset arusers") — definitively unavailable (probed 2026-07-24).
- **Hidden per-user quotas**: none (the single RQS is disabled + other-user-scoped).

## 5. THE COMMAND TOOLKIT

```
qstat -u '*' | awk '{print $5}' | sort | uniq -c    # cluster pressure at a glance
qstat -j <jid>                                      # why pending + exact resource request
qhost -F gpu | grep -B1 'gpu=[1-9]'                 # nodes with free GPUs right now
qconf -ssconf                                       # the scheduler policy (this dossier's source)
qquota                                              # resource-quota limits on us
qdel <jid>                                          # remove (never on reserved queued jobs
                                                    #   — kill+resubmit forfeits reservation+age)
```

*Sources: live `qconf -ssconf`/`qstat`/`qhost` probes (2026-07-24); UCL RC docs (Myriad cluster
page; GPU nodes; Experienced Users); SGE sched_conf(5)/sge_priority(5) manuals. UCL is migrating
SGE→Slurm at some future date — this dossier is SGE-era.*

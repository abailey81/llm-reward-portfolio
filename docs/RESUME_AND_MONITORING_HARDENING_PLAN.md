# Resume + monitoring deep-hardening plan (2026-07-05, queued after the flawlessness review)

**Goal (Tamer).** The unattended ~23-day laptop campaign must (a) NEVER lose meaningful progress on any
crash/reboot/power-loss, with an extremely advanced + sophisticated resume system, and (b) very closely
monitor and detect ANYTHING — stalls, drift, errors, resource exhaustion, integrity breaks, silent
shortfalls — as early as possible.

**Foundational design decision (do NOT violate).** The reproducibility contract is *results REPLAY from
the archive; they cannot be regenerated* (LLM calls are non-deterministic; training is seeded-deterministic).
Therefore the resume UNIT is one completed training (~85 min, ≤3 concurrent ⇒ a crash loses ≤ ~4 GPU-h of
in-flight work), and those lost trainings re-run to the **identical** result. Finer-grained mid-training
SB3 checkpointing is REJECTED: bit-exact resume across a torch save/load boundary is not guaranteed under
CUDA, so it would trade the determinism/replay guarantee (the study's credibility spine) for crash
granularity — a bad trade. "Advanced" = bulletproof the per-training boundary, not sub-divide it.

---

## PART A — RESUME / NO-PROGRESS-LOSS (what to build)

### A0. What already exists (verified this session — do NOT rebuild)
- LLM arms: search-replay cache (resume replays candidates + failures, no Opus re-bill; byte-faithful).
- **Search arms (NEW 2026-07-05): per-candidate checkpoint + hash-verified resume cache** — byte-identity
  certified (test_search ×2); a crash re-draws the same sequence and skips archived candidates.
- TEST leg: per-seed atomic record writes (sidecars-first fsync, write-once), resume skips completed seeds.
- Supervisor: auto-relaunch with backoff, always `--resume`; ONSTART task re-enters after reboot +
  re-applies the GPU clock lock.
- Sub-experiment (NEW): resume skips complete (condition, seed) cells.
- Archive mirror to a 2nd physical disk; freeze verify-or-refuse; enforce_freeze.

### A1. As-completed streaming archival (THE remaining real gap — HIGH)
`src/orchestration/parallel.py::run_recycling` collects futures in SUBMISSION order (`for f in futs:
out.append(f.result())`), so a driver-process crash mid-batch can orphan up to `recycle_every-1` (~12)
COMPLETED-but-uncollected trainings (~17 h re-paid). **Fix:** collect via `concurrent.futures.as_completed`
and invoke `on_result` (the streaming archival hook) the MOMENT each future completes, so every finished
training is durably archived before the next starts. Preserve determinism: the archive is keyed by
run_id, not order, so as-completed collection changes nothing about WHAT is written. + a test that a
simulated mid-batch crash loses zero completed trainings.

### A2. A precise per-run PROGRESS/HEARTBEAT ledger (HIGH)
Add one append-only `outputs/campaign/run_journal.jsonl` — every state transition (arm_started,
candidate_started/done, seed_started/done, checkpoint_written, arm_done, stage_done) with a UTC timestamp,
run_id, and elapsed. Purpose: (a) on resume the EXACT completed set is known from the journal, not inferred
from a directory walk; (b) the sentinel computes real progress-RATE + ETA + stall detection from it;
(c) a full post-hoc timeline for the write-up's compute-reporting. Append-only + fsync so it survives a
crash mid-write (a torn last line is tolerated on read).

### A3. Resume coverage for EVERY stage (MEDIUM)
Verify + (where missing) add skip-completed resume to: the H1 baseline stage (does it skip already-tested
baselines on `--resume`? — confirm/add), the H3 single-shot stage, the report-only sub-experiments. Every
stage must be idempotent: re-running with `--resume` re-does only un-done units.

### A4. Atomicity + corruption quarantine (MEDIUM)
Confirm every write is tmp→fsync→atomic-rename (records + sidecars + journal + summary). A record that
fails to parse on load is QUARANTINED (moved aside + logged) and its slot re-run on resume — never trusted
as complete, never silently dropped. (The write path is mostly there; audit for any non-atomic write.)

### A5. Continuous verified mirror (MEDIUM)
Register the 6-hourly mirror task; after each mirror pass, run the archive-integrity `verify` against the
mirror so a silently-corrupted backup is caught. The archive-integrity seal (built 2026-07-05) is the tool.

### A6. An automated crash-resume self-test (MEDIUM)
Promote the crash-injection rehearsal to a test: on the synthetic config, run N units, kill, resume,
assert the final archive == the uninterrupted baseline (byte-identical) AND the journal shows no
double-work. Run it in the pre-freeze gauntlet so resume is CERTIFIED end-to-end, not just unit-tested.

---

## PART B — MONITORING / DETECT-EVERYTHING (what to build)

### B0. What already exists (verified this session)
- Dashboard `scripts/monitor.py` (multi-level progress, GPU/RAM telemetry, anomaly tracker, token/cost,
  silent-hang detector, ntfy on done/error/stall + the NEW disk_low/anomaly_surge; survives exit-3 passes).
- **The SENTINEL `scripts/sentinel.py` (NEW)** — 12 invariant checks + a **CUSUM change-point drift
  detector** on the streaming gate-failure / NaN rates; `--watch`; severity-tagged transitions →
  `events.jsonl`; exits non-zero on CRITICAL.
- **Archive-integrity seal (NEW)** — tamper-evident result-archive root; verify-before-trust in analyze().

### B1. Multi-granularity STALL detection (HIGH)
Beyond progress.json mtime, detect a stall at three levels from the journal (A2): (i) a TRAINING running
> (median + k·MAD) of measured per-training times (~85 min) = a wedged CUDA/hung candidate; (ii) no new
CANDIDATE completed in > the expected inter-candidate interval; (iii) an ARM not advancing across a
threshold. Each is a distinct sentinel check with its own severity. This catches the "one training wedged
but the process alive" hang that a process-liveness check misses.

### B2. Statistical anomaly detection on TRAINING metrics (HIGH)
Reuse the CUSUM/EWMA infra on the streamed training telemetry: critic-loss trending UP (predict divergence
BEFORE the explosion), entropy collapse (policy degeneracy), fps degradation (thermal throttle / swap).
Early-warn on the TREND, not just the breach. Report-only; never touches the frozen result.

### B3. PREDICTIVE resource exhaustion (MEDIUM)
Not just "disk < floor" but "disk will hit the floor in N hours at the current fill rate" (linear
extrapolation over the recent samples) → a WARN with lead time. Same for RAM growth (a leak) and the
mirror drive.

### B4. Completeness / coverage ledger + ETA (HIGH)
A live expected-vs-done table (arms × seeds × candidates, per stage) computed from the frozen design + the
journal, so you always know EXACTLY how much remains + a data-driven ETA, and any silent SHORTFALL (a unit
that should exist but doesn't) is flagged CRITICAL. This is the anti-husk guarantee at the monitor level.

### B5. Error aggregation + taxonomy (MEDIUM)
Cluster every error/anomaly by type (critic_explosion, OOM, sandbox-reject, API-error/refusal,
failure_wave) with rate + first/last timestamp + affected arm, surfaced in one panel. The sentinel's
divergence + API-error checks are the seed; extend to a full taxonomy.

### B6. External DEADMAN + heartbeat (MEDIUM)
The run emits a heartbeat (a full health snapshot) every N minutes; an EXTERNAL watcher (phone ntfy / a
cheap cloud cron hitting a healthcheck URL) alarms on the ABSENCE of a heartbeat — the only way to detect
HOST DEATH (power loss, kernel panic) that no on-host monitor can report. Partly there (deadman ping);
make it a full-snapshot heartbeat + a documented external check.

### B7. One unified live view (LOW)
The dashboard + sentinel + journal feed one `--watch` view: progress + health + drift + coverage + errors
+ ETA on one screen, refreshed every tick, with the severity-graded event log tailing beneath.

---

## Execution order (after the flawlessness review's fixes land)
1. A1 as-completed streaming archival (biggest real progress-loss gap) + test.
2. A2 the run_journal ledger (unblocks B1/B4/B5 precision).
3. B4 completeness/coverage + ETA; B1 multi-granularity stall.
4. B2 training-metric CUSUM/EWMA early-warning; B5 error taxonomy.
5. A3/A4/A5/A6 stage-resume coverage + atomicity + verified mirror + the automated crash self-test.
6. B3 predictive exhaustion; B6 heartbeat/deadman; B7 unified view.
7. Full battery + runbook update + document.

Every item is report-only / infra: it NEVER changes the frozen design, a result, or the determinism
contract; a monitor/resume failure must always fail-safe (degrade to the existing behaviour, never block
or corrupt the run).

# DEFERRED FIXES — written now, applied at the next natural restart

Three defects found during RUN 4's launch night are deliberately NOT applied while the run is live:
every one touches a file inside the `src scripts config prompts` pathspec, and editing those mid-run
would break the §23.9 drift invariant (`git diff <running-sha> HEAD -- src scripts config prompts`
must stay empty) — the RUN 3 condition.

They are written out in full here so the work is done and reviewed, not improvised later under time
pressure. **Apply in this order, re-certify, then re-deploy.**

---

## 1. D13 — a provider reply with no `choices` must be RETRYABLE, not a `TypeError`

**File:** `src/llm/client.py` ~line 346
**Seen:** twice on `nemotron-3-super`, 2026-07-29, killing 5 arm pipelines.

**Now:**
```python
choice = response.choices[0]
```

**Becomes:**
```python
# 2026-07-29 (D13): a provider can return HTTP 200 with a body carrying no choices at all --
# OpenRouter did exactly that on nemotron-3-super, and `response.choices[0]` then raised
# `TypeError: 'NoneType' object is not subscriptable`. The retry classifier is duck-typed on HTTP
# STATUS, so a TypeError is not transient to it: the exception escaped the transport, propagated
# through `_complete_with_outage_tolerance`, and crashed the whole arm pipeline. A malformed body
# is a TRANSPORT fault and must be retried like one, with a named error rather than an
# AttributeError-shaped accident.
_choices = getattr(response, "choices", None)
if not _choices:
    raise EmptyCompletionError(
        f"{self.model}: provider returned a response with no choices "
        f"(id={getattr(response, 'id', None)!r}); treating as a transient transport fault"
    )
choice = _choices[0]
```

plus, beside the other transport exceptions:

```python
class EmptyCompletionError(RuntimeError):
    """A provider returned a well-formed HTTP 200 whose body carries no completion.

    Distinct from a refusal or a truncation, both of which DO carry a choice with a
    ``finish_reason``. This is the provider failing to answer at all, which is transient by
    nature -- so it must reach the retry layer, not the arm pipeline.
    """
```

and it must be added to whatever set the tenacity predicate treats as retryable.

**Test (must FAIL first):** a fake transport whose `response.choices` is `None` raises
`EmptyCompletionError` (not `TypeError`), and the retry predicate returns True for it.

---

## 2. D12 — a gate stop must not look like success

**File:** `scripts/run_campaign_cluster.py` ~line 1403, and `scripts/mode_d_supervisor.ps1`
**Seen:** six legs reported `LINE COMPLETE` having produced nothing, 2026-07-29.

**Now:** the C3 review-gate stop does `return 0`, so the supervisor's `if ($rc -eq 0)` treats
"stopped awaiting human review" as "finished successfully" and exits the line.

**Becomes:** return a distinct code, and teach the supervisor the difference.

```python
# 2026-07-29 (D12): a gate stop is NOT a success. Returning 0 made the supervisor log
# "LINE COMPLETE" and exit for six legs that had produced nothing at all -- only the watchdog's
# 300 s revive loop kept them alive. Success and awaiting-review must be distinguishable to the
# process that decides whether to relaunch.
return 3   # EXIT_AWAITING_REVIEW
```

```powershell
if ($rc -eq 0) { Log "driver exited 0 - LINE COMPLETE."; break }
if ($rc -eq 3) {
    # A gate stop: real work is done and a HUMAN must look. Do not relaunch in a tight loop, and
    # do not pretend the line finished.
    Log "driver exited 3 - STOPPED AT THE REVIEW GATE, awaiting approval. Not relaunching."
    break
}
```

**Test (must FAIL first):** the tiered path with `awaiting_review=True` returns 3, not 0; and a
`test_mode_d.py` assertion that the supervisor script branches on 3 distinctly from 0.

> ⚠ Check every other consumer of this exit code before applying — the watchdog decides "dead line"
> by process absence, not exit code, so it is unaffected, but that must be VERIFIED not assumed.

---

## 3. Preflight — a key can be valid and out of budget

**File:** `scripts/preflight.py`
**Seen:** the OpenRouter key smoke-tested green while its $10 per-key cap was already spent.

Add `check_provider_headroom`: for each configured provider, query the key's remaining budget
(OpenRouter: `GET /api/v1/key` → `limit`, `usage`, `limit_remaining`) and **FAIL** when the
remaining headroom is below the registered projection ($18.72 Anthropic / $5.28 OpenRouter).
An absent headroom field must **WARN**, never silently pass — same fail-loud principle as the rest
of the gate.

**Test:** a fake key endpoint reporting `limit_remaining` below the projection makes preflight FAIL;
one above it passes; a response with no limit field WARNs.

---

## 4. D14 — a PARTIAL arm failure must not be silent (found live, 2026-07-29)

**Files:** `src/cluster/campaign.py` (`run_campaign_tiered`) and `scripts/campaign_guards.py`
**Seen:** `nemotron-3-super` (leg7) ran **8 h 29 m with 3 of its 5 arms**, having lost `scalar` and
`placebo_shuffled` to D13. Full narrative + evidence in `CAMPAIGN_EXECUTION_RECORD.md` §25.

**The asymmetry.** When EVERY arm crashes, the line exits, the supervisor logs `LINE COMPLETE` and
the watchdog revives it 300 s later — six lines did exactly that 10× each on launch night and all
recovered. When only SOME arms crash, the survivors keep the process alive, `run_campaign_tiered`
never returns, no supervisor exit fires, no watchdog revive triggers, and the dead arms are stranded
for the life of the process. **The louder failure is the safe one.**

`_arm_core`'s `except` is deliberate ("one unit must not sink the ladder") and is right for
throughput. What is missing is any reconciliation afterwards.

### 4a. Detection (do this one regardless — it is pure monitoring)

Add an `arm_coverage` guard to `campaign_guards.py`: per `(line, arm)`, assert every leg line has
submitted ≥1 batch for all five LLM arms, reading the **`batches/` registry** — NOT the archive
directory listing, which is misleading: leg7's dead arms had populated `search_.../<arm>/`
directories because the authoring succeeded and was billed, and only the submission died. Must know
`h3ss` is single-arm by design and `c1`'s LLM arms are canary-gated. Effect-blind (counts only).

**A working, falsified implementation is committed at `docs/ops/arm_coverage.py`** — port it into
`campaign_guards.py` at the restart. It lives under `docs/` deliberately: `scripts/` is inside the
drift pathspec and the run is live, whereas `docs/` is not, so the detector could be armed
immediately without breaking the invariant. It was proven to FAIL on the live bad state
(`leg7 MISSING ['placebo_shuffled','scalar']`, exit 2) and then to PASS once leg7 recovered
(`ALL LINES FULL`, exit 0) — falsified in both directions before being trusted.

Run it beside the repo guards until it is ported:
`python docs/ops/arm_coverage.py outputs/campaign_cluster_run4`

### 4b. Repair (the durable fix)

Either retry a crashed arm inside the tiered pass, or make a pass that ends with any `ok: False`
arm exit **non-zero** so the supervisor relaunches the line — recovery must not depend on a human
noticing. ⚠ This interacts with D12 above: `core_ok` is already computed and currently does not
influence the exit code. Decide the two together, and check every consumer of the exit code.

**Test (must FAIL first):** a tiered run where one arm raises and the others succeed returns
non-zero / re-attempts the failed arm; and the guard exits 2 on a registry missing one leg-arm.

---

## 5. D15 — the watchdog must carry `-ExcludeHosts` (found 2026-07-30, worked around live)

**File:** `scripts/mode_d_watchdog.ps1`
**Seen:** the substrate fence (`node-d00b-024`, record §28) was applied to all 12 supervisors, and the
watchdog would have **silently undone it** on the next revival.

**The defect.** The watchdog's param block carries only `IntervalSecs`, `OutDir`, `RemoteRoot`. It
revives a dead line with `Start-Process … mode_d_supervisor.ps1 -Line … -OutDir … -RemoteRoot …` and
**never passes `ExcludeHosts`**, so the revived line falls back to the supervisor's default fence
(`node-d00a-230` alone) and loses the substrate fence.

This is **exactly the D4 shape, one parameter later** — and the file's own comment already warns about
it for the other two: *"Before this parameter existed the watchdog restarted every dead line with the
supervisor's DEFAULTS."* **An automatic restarter is a second launcher and must take every parameter
the thing that started the line took.**

**Becomes:**
```powershell
    # The substrate/host fence. MUST be passed through on revival: a revived line that silently
    # reverts to the default fence re-opens the very inhomogeneity the fence was added to close
    # (record s.28). Same reasoning as OutDir/RemoteRoot above.
    [string]$ExcludeHosts = "node-d00a-230",
```
and in the revival call:
```powershell
                "-Line", $d, "-StaggerSecs", "0",
                "-ExcludeHosts", $ExcludeHosts,
                "-OutDir", $OutDir, "-RemoteRoot", $RemoteRoot
```

**Test (must FAIL first):** a `test_mode_d.py` assertion that the watchdog's revival argument vector
contains `-ExcludeHosts`, and that its value is threaded from the parameter rather than defaulted.

**Live workaround in force NOW:** `docs/ops/watchdog_fenced.ps1` — a faithful copy that carries the
parameter, running in place of the repo watchdog (which is retired for the duration). It sits under
`docs/` because `scripts/` is inside the drift pathspec. **Retire the workaround and restore the repo
watchdog the moment this fix lands.**

⚠ Audit the OTHER launchers for the same omission when applying: `mode_d_launch.ps1` and
`campaign_backup.ps1` were fixed for roots in D4, but were not checked for the fence.

---

## 6. D16 — the C3 gate's `health_ok` does NOT see a SUBSTRATE mix (found 2026-07-30)

**File:** `src/cluster/integrity.py` ~line 360 (`write_integrity_report`)
**Found while checking whether D15's four 6140 records would stall C4 at the review gate.**

**The defect.** The gate's stop message says it fires on *"a REAL execution defect (a short/incomplete
unit or **device inhomogeneity**)"*, and the gate reads exactly one field:

```python
"health_ok": bool(all_complete and crn_consistent and not mixed_winner_units),
```

`crn_consistent` is computed from `seed_devices`, i.e. the **device label** (`cpu` / `cuda`) only. And
`device_homogeneous_everywhere` — the nearest thing to a substrate check — is explicitly annotated
*"informational under seed-pool blocks"* and is **not** a gate input.

**So the one inhomogeneity that ACTUALLY occurred in RUN 4 — a Xeon Gold 6140 mixed into a unit whose
other 26 records ran on 6240s — passes the gate silently.** `check_substrate_fields` already exists in
`campaign_health.py` and rates exactly this CRITICAL, but it is wired into the SENTINEL, not into the
gate. The gate therefore promises a check it does not perform.

Two mitigating facts, so the exposure is stated honestly: this is why C4 will **not** stall on D15
(good for the timeline), and the sentinel does catch it (which is how D15 was found at all). The
defect is that the *blocking* control is blind to it while an *advisory* one is not.

**Becomes:** fold the substrate census into the gate verdict, so the blocking control checks the same
thing the advisory one does.

```python
# 2026-07-30 (D16): `crn_consistent` keys on the DEVICE label only, so an Intel/AMD or
# Skylake/Cascade-Lake mix — the exact thing that happened in RUN 4 — passed a gate whose own stop
# message claims to catch "device inhomogeneity". The substrate census is what makes the promise true.
from src.cluster.integrity import substrate_field_census
_sub = substrate_field_census(...)           # same census check_substrate_fields consumes
substrate_homogeneous = len({k for k, v in _sub.items() if v > 0}) <= 1
report["verdict"]["substrate_homogeneous"] = substrate_homogeneous
report["verdict"]["health_ok"] = bool(
    all_complete and crn_consistent and not mixed_winner_units and substrate_homogeneous
)
```

**Test (must FAIL first):** an integrity report built over a unit holding two distinct CPU-model
signatures returns `health_ok = False`; one holding a single signature returns True; and a device-only
mix still fails as before (no regression).

⚠ **Consequence to weigh before applying:** with this in place, a single stray record on an odd node
STOPS the line at the gate until a human clears it. That is the correct default for a validity failure,
but it turns a silent pass into a hard stop — so it must land together with the host-fencing mechanism
(`--exclude-hosts`, already used for `node-d00b-024`) so the stop is rare rather than routine.


## 7. D17 — the safe-default must not clear the reward's state (found 2026-07-30)

**Severity: MEDIUM for the science, HIGH for the instrument.** It does not touch any confirmatory
result — R115 excludes every affected record, effect-blind, and no breach sits on line `c1` — but it
biases the per-model authoring-reliability measurement, which is a *reported* result, and it makes a
recoverable authoring defect unrecoverable.

**The defect.** `safe_call` (`src/sandbox/executor.py:779`) substitutes
`(SAFE_DEFAULT, {}, None)` on failure. The third element is the reward's own `reward_state`, so every
failure also *erases the reward's memory*. A stateful reward with a cold-start branch is then pinned in
a limit cycle — cold-start call succeeds, main-path call raises, state cleared, repeat — for the whole
400,000-step budget. Full mechanism, evidence and archive-wide exposure: execution record §37;
disclosed as limitation B.8.7; probe `docs/ops/probe_safe_default_cycle.py`.

Measured: 2 of the 9 breaching records are rewards whose main path is *sound* and whose only defect is
a one-step warm-up boundary. With state preserved they fail on 1.0–1.75 % of calls; as shipped they
fail on 50 %.

**The fix.** On failure, hand the reward back the state it had going in, rather than `None`:

```python
# in safe_call, at the except site
except Exception:
    _LAST_CALL_FAILED = True
    _SAFE_DEFAULT_COUNT += 1
    prior = args[4].get("reward_state") if len(args) > 4 and isinstance(args[4], dict) else None
    return (SAFE_DEFAULT, {}, prior)
```

**Why the prior state and not `None`.** A failed call produced *no* new state, so the last valid state
is the one that went in — returning it is the semantically accurate choice, and it lets a reward whose
defect was transient recover on the next call. `None` asserts something stronger and false: that the
reward has no usable history.

**The counter-argument, and why it does not win.** Preserving state could propagate a corrupt state
forever, so a reward that poisons its own state would fail on every subsequent call instead of
alternating. That is the *correct* outcome: it reports 100 % rather than 50 %, which is the honest
severity, and R115 excludes it either way. The shipped behaviour does not avoid that failure — it
merely disguises it as a 50 % figure that reads like partial success.

**Do NOT apply live.** `src/` is drift-fenced for the duration of the confirmatory run and
`safe_call`'s substitution semantics sit inside the frozen determinism envelope. Changing a
reward-evaluation semantic mid-campaign would invalidate every record written before the change.

**Tests to write with the fix** (each must be shown to FAIL against the pre-fix code):

1. A reward that raises only on its second call, given a cold-start branch, reaches its third call
   under the fix and does not under it — asserting the failure count is 1, not `n_steps / 2`.
2. A reward that poisons its own state reports ~100 % defaults under the fix, not ~50 % — the
   severity-honesty property.
3. `reward_state` identity: after a failure the object handed to the next call `is` the object handed
   to the failed call.

**Also fix at the same time — the validation blind spot.** `validate_once` runs the reward exactly
once, from a cold-start state, i.e. precisely the call that succeeds in this cycle. It cannot see the
defect *by construction*. Extend it to call the reward at least three times, threading the returned
state, so a state-transition failure surfaces at validation rather than after an 8-hour training. This
is the cheaper half of the fix and catches the whole class.

---

## 8. THE MEMORY REQUEST IS 19.5x THE MEASURED PEAK, AND IT IS WHAT KEEPS US QUEUED (found 2026-07-30, worked around live)

**File:** `src/cluster/jobscript.py` (`mem_per_core: str = "4G"`, rendered into `#$ -l mem={mem_per_core}`)
plus `scripts/run_campaign_cluster.py` (no CLI override exists).
**Evidence:** record §38 — a six-job canary in which the ONLY field that decided placement was the
memory request (`smp 8 / h_rt 15h / mem 4G` stayed queued; the same job at `mem 2G` and `mem 1G` ran at
the next scheduling pass), plus `maxvmem` p50 1.57 GB / max **1.64 GB** over n=55 completed 8-slot
RUN-4 jobs against a **32 GB** per-job request.

**Now:** every job on both lanes asks `4G` per slot. The 8-slot search lane therefore asks 32 GB, on a
pool whose nodes carry 5.2 GB per core; 54 of the 106 pool-d hosts with free slots have under 32 GB of
`memory` consumable left, stranding 660 free slots.

**Becomes:** a lane-aware default sized from the measured footprint, plus an explicit override so an
operator never has to edit source to re-size it:

```python
# 2026-07-30 (record §38, §43): size the memory request from the MEASURED footprint, not a round
# number. Measured on RUN 4's own tasks, per LANE:
#   search lane, pack 1 on 8 slots : maxvmem p50 1.57 GB, max 1.64 GB   (n=55)
#   test lane,   pack 4 on 4 slots : maxvmem 5.86-6.16 GB               (exit-0 c1_baselines_pNN)
# i.e. ~1.55-1.64 GB per CONCURRENT TRAINING, and the job's need scales with the PACK, not the slot
# count. The old flat "4G per slot" asked 32 GB for a search job that peaks at 1.64 GB (19.5x); on
# Myriad memory - not slots - is the scarce consumable, so the over-ask was the binding placement
# constraint, AND at C4 it makes the 1,000-job cap unreachable (1,000 x 16 GB = 16 TB against 11.7-12.1 TB
# of free pool-d memory).
#
# ⚠ AN EARLIER DRAFT OF THIS FIX USED A 4x HEADROOM. That is wrong in the direction that matters: for
# the pack-4 test lane it computes 6.8G per slot, i.e. LARGER than the 4G it replaces, which would
# have made placement worse while appearing to fix it. Caught by measuring the pack-4 peak instead of
# inferring it. The rule below is 1.3x on the MEASURED per-lane peak, which lands on 2G per slot for
# both lanes: 8 GB per search job (4.9x its 1.64 GB) and 8 GB per test job (1.29x its 6.2 GB).
_MEASURED_PEAK_GB_PER_TRAINING = 1.64
if mem_per_core is None:
    concurrent = max(1, int(pack))                 # packed trainings share the job's memory
    need_gb = _MEASURED_PEAK_GB_PER_TRAINING * concurrent * 1.3     # 1.3x on the measured peak
    per_slot = max(1.0, need_gb / max(1, int(cores)))
    mem_per_core = f"{max(1, round(per_slot)):d}G"
```

**Sanity table for the two live lanes (this is what the rule must produce):**

| lane | pack | cores | measured peak | rule output | request | headroom |
|---|---|---|---|---|---|---|
| search | 1 | 8 | 1.64 GB | `1G`/slot | 8 GB | 4.9x |
| test (C4) | 4 | 4 | 6.2 GB | `2G`/slot | 8 GB | 1.29x |

At `2G` the C4 reservation for 1,000 concurrent jobs is **8 TB against 11.7-12.1 TB of free pool-d
memory** — feasible; at the current `4G` it is **16 TB**, which is not. **This fix is therefore the
precondition for the 4,000-core target, not merely a queue-time improvement** (record §43.3).

and in `scripts/run_campaign_cluster.py`:

```python
p.add_argument("--mem-per-core", default=None, metavar="NG",
               help="SGE per-slot memory request (default: sized from the measured per-training "
                    "peak, >=4x headroom). Raise it only with a maxvmem measurement in hand.")
```

**Falsifiable test** (must FAIL against the current code first):

```python
def test_memory_request_is_sized_from_the_measured_peak_not_a_flat_4g():
    """An 8-slot single-training search job must not ask 32 GB when it peaks at 1.64 GB.

    Regression for record §38: the flat `4G` per slot made the job need a 32 GB window on a pool
    whose nodes carry 5.2 GB/core, which is what held 119 of our 190 jobs in `qw` while 3,400 slots
    sat free. The bound below keeps >=4x headroom over the measured peak and stays well under the
    per-node ratio.
    """
    js = render_jobscript("t", 1, "/r", "/g", device="cpu", pack=1, cores=8)
    mem = re.search(r"^#\$ -l mem=(\d+)G", js, re.M).group(1)
    assert 1 <= int(mem) <= 2, f"per-slot memory {mem}G: sized from a round number, not the measurement"
    # and the packed test lane must still cover its 4 concurrent trainings
    js4 = render_jobscript("t", 1, "/r", "/g", device="cpu", pack=4, cores=4)
    mem4 = int(re.search(r"^#\$ -l mem=(\d+)G", js4, re.M).group(1))
    assert mem4 * 4 >= 4 * 1.7 * 2, "packed lane must keep >=2x headroom over 4 x 1.7 GB"
```

**⚠⚠ STATUS CHANGED 2026-07-30 16:05 — THIS FIX WAS APPLIED, NOT DEFERRED, and the "live workaround"
below is DEAD.** `jsv_allowed_mod = ac,h,i,e,o,j,M,N,p,w` has no `l`, so `qalter -l` is rejected
site-wide and a queued job's memory request is immutable (record §45). The renderer change is therefore
the ONLY delivery mechanism; it is implemented in `src/cluster/jobscript.py`, its test was falsified
against the pre-fix code, and it ships via the driver relaunch. Everything below is the specification
it was built from.

~~**Live workaround, already in place:** `docs/ops/mem_relax.sh` — `qalter`s the memory term of~~
already-queued jobs to 2G/slot, reading each job's own `hard resource_list` back from `qstat -j` so the
`snx` / `tmpfs` / `batch` / `h_rt` terms and the D15 host fence are carried across verbatim. It is
dry-run by default and must be re-run as new batches are submitted, because the renderer keeps
producing 4G. **It is an operator action** (the harness classifier blocks agent-side `qalter`, as it
does `qdel`).

**⚠ Do NOT confuse this with the walltime.** `h_rt=15h` against a measured 12.20 h maximum training is
1.23x headroom and is NOT slack; cutting it would SIGKILL long trainings. Record §38.4.

---

## 9. `CPU_THREAD_SPEEDUP[8]` IS A BENCH NUMBER; PRODUCTION SAYS 1.92x (found 2026-07-30)

**File:** `src/cluster/lanes.py` (`CPU_THREAD_SPEEDUP = {1: 1.00, 2: 1.57, 4: 2.23, 8: 2.72, 16: 2.11}`)
**Evidence:** record §39 - 60 packed 1-thread baseline tasks (p50 8.33 h) against 680 8-thread search
records (p50 4.34 h) on the SAME 400,000-step training: **1.92x by median, 1.75x by mean**, versus the
modelled 2.72x taken from an isolated steps/s bench.

**Now:** the ladder model's `critical_chain` term is computed with 2.72, making the floor 3.27 d.

**Becomes:** the field value, with the bench value preserved as a comment naming the conditions under
which it held.

```python
#: 2026-07-30 (record §39): the 2.72x came from an ISOLATED bench (8-core box, 21.5 -> 60.0 steps/s).
#: In production, across 740 timed trainings on shared 36-core nodes, 8 threads is **1.92x by median /
#: 1.75x by mean** - co-tenants take memory bandwidth an idle bench never loses. The packed lane's own
#: four-way sharing biases the 1-thread figure UP, so 1.92 is an upper bound. Bench values kept for
#: provenance: {1: 1.00, 2: 1.57, 4: 2.23, 8: 2.72, 16: 2.11}.
CPU_THREAD_SPEEDUP = {1: 1.00, 2: 1.45, 4: 1.75, 8: 1.92, 16: 1.55}   # field-measured at 8; others scaled
```

**Falsifiable test** (must FAIL against the current code first):

```python
def test_chain_thread_speedup_is_the_field_value_not_the_bench_value():
    """The ladder model must use the production speedup, not the idle-node bench.

    Regression for record §39: at 2.72x the critical-chain floor reports 3.27 d; the measured 1.92x
    puts it at 4.64 d. Quoting the optimistic floor understates the front of the ladder by ~1.4 days.
    """
    assert 1.8 <= lanes.CPU_THREAD_SPEEDUP[8] <= 2.0
    p = lanes.plan_lanes(rung=30, cpu_cores=100_000, chain_threads=8)
    floor = float(p["makespan_days"] if isinstance(p, dict) else p.makespan_days)
    assert 4.3 <= floor <= 5.0, f"critical-chain floor {floor:.2f} d looks like the bench number"
```

**⚠ SCOPE:** this is a MODEL INPUT, not a behaviour change - nothing the campaign computes moves, only
what we PREDICT about it. No rung-568 ETA changes (rungs 100+ are throughput-bound); the correction
costs ~1.36 d at rung 30 and at the early rungs when cores are plentiful. Any prose quoting "2.72x" or
a "3.27 d critical-chain floor" must be corrected before it reaches the PDF.

---

## 10. D18 — one record at two paths, and ~20 recursive consumers count it twice (found 2026-07-30)

**Files:** `src/cluster/poll.py` (the transfer's destination join) and every consumer that discovers
records with `rglob("record.json")` — `scripts/sentinel.py` (8 sites), `src/cluster/integrity.py` (2,
one of which feeds the C3 gate's completeness table), `src/cluster/telemetry.py`, `src/cluster/poll.py`,
`scripts/provisional_bank.py`, `scripts/resume_audit.py`, `scripts/first_seed_sanity.py`.

**Evidence:** record §44.6. `search_leg_haiku_4_5/scalar/scalar-g1-c3/record.json` and
`…/scalar-g1-c3/scalar-g1-c3/record.json` carry an identical `reward_source_hash`, an identical
metrics dict and an **identical mtime** — one write landing at two paths, not a second training. It is
the only such pair in 1,025 records.

**Impact, bounded:** the confirmatory analysis is safe twice over — `analyze_campaign.py` dedupes by
`run_id` and its walker is depth-limited to `<root>/<leg>/<arm>/<candidate>/record.json` — but every
recursive consumer counts the candidate twice. Today that is +1 on a count of 1,025; a systematic
version would inflate the completeness checks the C3 gate reads.

**Becomes:** (a) fix the destination join so a path already ending in `<run_id>` is not extended by it
again; (b) make the recursive consumers dedupe:

```python
# 2026-07-30 (D18): the archive can contain the SAME record at two paths (a destination computed as
# <dest>/<run_id> where <dest> already ended in <run_id>). Discovery must be by run_id, not by file,
# or every count silently gains a phantom record.
seen: dict[str, Path] = {}
for rec_path in root.rglob("record.json"):
    try:
        rid = json.loads(rec_path.read_text(encoding="utf-8")).get("run_id")
    except Exception:
        continue
    if rid and rid not in seen:
        seen[rid] = rec_path
```

**Falsifiable test (must FAIL first):** build a temp archive containing one record written at both
`<arm>/<rid>/record.json` and `<arm>/<rid>/<rid>/record.json`; assert the discovery helper returns
**one** record and that the integrity report's `present` count is 1, not 2.

**⚠ DO NOT delete the duplicate file** (trap 18): the archive is a mirror and `pull_archive` restores
it. The fix is in the discovery and the join, not in the filesystem.

---

## 11. C4 LAUNCH FLAG — `--pack 8` (decided 2026-07-31, record §50)

**Not a code fix: a LAUNCH FLAG for the C4-boundary restart.** The twelve supervisors currently pass
`--pack 4 --cores-per-training 1`. At the boundary they take `--pack 8 --cores-per-training 1`.

**Why:** pack 8 reaches the 4,000-core saturation point with **500** concurrent jobs where pack 4
needs **1,000** — and 1,000 is a cap we have never approached (peak observed: 204). Across every job
count we have actually seen, pack 8 halves the rung-568 makespan. It is insurance against the
exogenous 2026-08-27 stop truncating the top rung, which is the rung the power analysis was built on.

**Why it is safe:** pack is OUTSIDE the determinism envelope. Pack-mates run in separate spawned
processes via `DevicePool`'s `ProcessPoolExecutor`, each initialised with the same thread/alloc/preload
contract, so pack size cannot reach any training's arithmetic — verified structurally and empirically
(330 packed CPU baselines in this run, all `device='cpu'`, all `OMP_NUM_THREADS=1`).

**Conditions:** validate on the FIRST line to reach C4 before the other eleven follow; fall back to
pack 4 and record it if that line misbehaves.

**Also fix at the same time:** `_task_device`'s docstring in `src/cluster/run_one.py` claims *"the CPU
lane has only ever been exercised at pack=1"* — falsified by this run's 330 packed CPU baselines.

---

## 12. D19 — the search lane's 15 h wall is only 1.12x its p99 (found 2026-07-31, record §55)

**File:** `src/cluster/jobscript.py` (the `h_rt` sizing), CPU **search** lane only.
**Evidence:** `qacct` over 1,508 finished jobs — **12 SEARCH jobs killed by `failed 37 : qmaster
enforced h_rt`**, every one at 15.00–15.01 h against the 15.00 h request, spanning nine lines and
including the confirmatory core and `h3ss`. Search-lane distribution: p50 3.94 h, p90 6.61 h,
**p99 13.44 h**, max 15.01 h (censored). Test/packed lane: p99 **9.85 h** — comfortable.

**Why the archive never showed this:** a training killed at `h_rt` writes NO record, so `wall_clock`
over the archive is **censored at the wall** and structurally cannot contain the failure mode. §38.4's
"longest observed 12.20 h" was measured that way and is unbiased only for jobs that survived.

**Impact is compute, not science:** all 12 are retried or currently retrying and **0 candidates are
lost** (verified against the live queue, not inferred from `qacct`, which only sees FINISHED jobs).
Cost ≈ 120 core-hours per kill before it dies, plus the retry.

**NOT applied now, deliberately** (§55.4): 0.85 % loss, all recovered; a longer walltime is HARDER to
backfill and placement is the binding constraint; it costs another relaunch; and **the problem is
self-limiting — the tight lane is SEARCH, which ends in 1–2 days, while C4 is the TEST lane at 1.52x
headroom.**

**At the restart, since the renderer is being touched anyway:** size the search lane's `h_rt` from the
MEASURED p99 with an explicit margin rather than a round 15 h, and add a falsifiable test asserting
the search-lane request exceeds the measured p99 by a stated factor. **Re-open sooner** if the search
p99 climbs toward 14 h, or if a kill lands on a `c1` candidate that does not recover.

---

## Applying, at the next restart

> ⚠ **THE COUNT: eleven items are documented here, but only TEN are still to apply.** Item **8 (the
> §38 memory sizing) WAS APPLIED LIVE on 2026-07-30** and shipped by the driver relaunch (record §46) —
> its own status block says so, but this checklist still listed it, and step 1 below demands each fix be
> applied "with its falsifiable test proven to FAIL against the current code first". **Item 8's test
> cannot fail any more, because the fix is in.** Corrected 2026-07-31 after re-deriving the renderer's
> output first-hand: `pack=1,cores=8 → 1G/slot`, `pack=4,cores=4 → 2G/slot`, and `pack=8,cores=8 →
> 2G/slot = 16 GB/job` — which is exactly the sanity table above and exactly the 7.8 TB-at-500-jobs
> figure §50.4's pack-8 feasibility argument rests on. Leave item 8 in place as the specification it
> was built from; do NOT re-apply it, and do NOT expect its test to fail.

1. apply the TEN outstanding fixes above (D13, D12, preflight headroom, D14, D15, D16, D17, the §39 speedup constant, D18 and the §50 pack flag — item 8 is ALREADY LIVE, see the note above), each with its falsifiable test proven to FAIL against the current code first;
2. full suite, `PYTEST_RC` read from the log, source-tree hash identical both ends;
3. `ruff`; `freeze --check` (none of these files is hash-bound, so the hash MUST NOT move);
4. commit, push, re-deploy the cluster (§23.12's delta method), re-verify `DIFFER=0 MISSING=0`;
5. only then restart the affected lines.

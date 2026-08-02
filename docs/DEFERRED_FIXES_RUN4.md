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

**── RE-VERIFIED INDEPENDENTLY 2026-07-31 (RUN 8, record §65.4) at a 41 % LARGER ARCHIVE. ──**
Re-measured from scratch over **1,449 records / 1,124 distinct `(root, arm, candidate_id)` keys** —
not by re-reading §44.6, but by rebuilding the duplicate detection from the archive:

* **still exactly ONE duplicated record**, the same `search_leg_haiku_4_5/scalar/scalar-g1-c3` nested
  pair. The defect has **not** become systematic as the archive grew, which was the stated worry
  ("a systematic version would inflate the completeness checks the C3 gate reads").
* both copies **byte-identical** — `sha256 803af2e302e9feb612e87cf8fa9cdc4585191110b156a6a272bca7b18a5e280b`
  on each. Stronger than §44.6's "identical hash/metrics/mtime": the *files* are identical, so no
  consumer's answer can depend on which path it happens to read.
* **ZERO duplicates on the confirmatory core line (`search/`)** — the "confirmatory path SAFE" claim is
  now VERIFIED first-hand, not carried on trust.
* it sits on a **report-only leg (R80)**, so it cannot touch a confirmatory quantity even before
  `analyze_campaign.py`'s two independent protections (`run_id` dedupe + depth-limited walker).

**Verdict: the fix stays DEFERRED and the priority stays LOW** — impact is +1 on a count of 1,449
(0.07 %), bounded, non-growing, and off the confirmatory path. **The falsifiable test and both fix
halves above remain the correct work at the C4 boundary**; nothing about them changes.

⚠ **A trap for whoever re-measures this.** Do NOT key candidate identity on
`(root, arm, candidate_id)` alone: the `test/` lane runs each baseline at **30 seeds**, all sharing one
`candidate_id`, so that key reports **12 phantom "duplicates" at 30 paths each and 12 "divergent
copies"** — a 349-path over-count that reads as a serious integrity failure and is purely an artefact
of the missing `seed` field. That false alarm was generated and caught during this very
re-verification (**P34**, record §65.5). **Key on `run_id`** — which is exactly what the fix above
already prescribes.

---

## 11. C4 LAUNCH FLAG — `--pack 8` — ✅ **APPLIED 2026-07-31, record §58** (decided §50)

> **CLOSED.** Applied ahead of the C4 boundary via a rolling watchdog-driven SUPERVISOR restart
> (not a driver relaunch — PowerShell binds the supervisor's argument array at supervisor start).
> Canaried on `qwen3.5-9b`, then rolled to all twelve lines; the watchdog revived every line
> within 40 s with the D15 host fence intact. Verified: **24 driver processes, all `--pack 8`**,
> zero at pack 4. INERT until C4 (`--search-pack` is still 1). RUNNING_SHA re-based to `f5014ce`,
> drift and working tree both clean. **Do NOT re-apply at the restart.**


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

## CONSIDERED AND DECLINED — pool widening `d` → `d,b` (measured 2026-07-31, record §57)

Raised again because placement became the binding constraint (§54). **Measured on the live cluster,
counting only USABLE queue instances (excluding `d`/`a`/`u`/`E` states):**

| pool | usable hosts | free slots | 8-slot jobs placeable | cores |
|---|---|---|---|---|
| **d** | 272 | 2,472 | 239 | **1,912** |
| **b** | 12 | 112 | 10 | **80** |

**Widening adds 80 cores = +4 %.** §46.2 established pool b is microarchitecture-IDENTICAL (both
`Intel Xeon Gold 6240 @ 2.60GHz`), so there is no CRN hazard in principle — but D15 is the standing
reminder that **one** heterogeneous host cost four archived records and an open bit-comparison
experiment, and 12 hosts is a thin sample to bet a substrate claim on for a 4 % gain.

**DECLINED.** Re-open only if pool d's own capacity becomes the binding constraint — it is not; our
constraint was priority (§54) and is now queue position. Recorded so the option is not re-litigated
from first principles a third time.

---

## 13. D20 - the driver lock must test pid IDENTITY, not pid EXISTENCE (found live 2026-07-31, record 59)

**File:** `src/cluster/driver.py` (`_acquire_driver_lock`, ~line 224-254).
**Seen:** the `h3` line stranded indefinitely - 0 drivers, supervisor retrying into the same wall,
every guard green - because Windows recycled a dead driver's pid onto `OpenConsole.exe` and
`psutil.pid_exists(pid)` returned True, so the lock was never broken.

**The defect:** `pid_exists` tests EXISTENCE, not IDENTITY. The lock is deliberately self-healing
("a DEAD owner's lock is broken automatically") and that design is right - it just heals on a
predicate that pid reuse defeats.

**Becomes:** store the owner's process CREATE-TIME beside the pid, and treat the lock as stale unless
BOTH match. A reused pid necessarily has a later create-time than the recorded one.

```python
proc = psutil.Process(os.getpid())
json.dump({"pid": os.getpid(), "create_time": proc.create_time(), "ts": time.time()}, fh)
...
# on collision:
same = False
if pid > 0 and psutil.pid_exists(pid):
    try:
        same = abs(psutil.Process(pid).create_time() - recorded_create_time) < 1.0
    except psutil.Error:
        same = False
if not same:
    lock_path.unlink(missing_ok=True)   # stale: dead owner, OR the pid was reused
```

**Test (must FAIL first):** a lock whose recorded pid is alive but whose recorded create_time does not
match the live process is BROKEN and re-acquired; one where both match still raises the
refuse-to-double-drive error.

**Live detector already armed (outside the fence):** `docs/ops/cycle.py` raises RED when any
`batches/*.driver.lock` has a live owner that is not a python process running
`run_campaign_cluster`. Falsified on three cases including a pid reused onto a DIFFERENT python
program. That closes the detection gap now; this item closes the mechanism at the restart.

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

---

## 14. `transport_guard`'s `timeout_events` COUNTER IS STRUCTURALLY ZERO (found 2026-07-31, record 79.5)

**File:** `scripts/campaign_guards.py`, `transport_guard()` (the `if "timed out after" in line:` branch).

**The defect.** The guard counts transport timeouts by searching driver logs for the literal string
`"timed out after"`. **Nothing in the codebase emits that string.** `grep -rn "timed out" src/` returns
exactly ONE hit, and it is a **retry-classification KEYWORD LIST** at `src/cluster/campaign.py:515`,
not a log message. So `timeout_events=N` can never be non-zero however many timeouts occur.

**This is the SECOND instance of the identical bug.** The same string, with the same
always-zero consequence, was found on Tamer's status page and fixed there (record 76.2). Both were
written from the same wrong assumption about the log vocabulary.

**Impact, bounded and measured — the VERDICT is NOT affected.** `transport_guard`'s return code is
driven solely by `worst_consecutive`, which parses `r"\((\d+) consecutive"` — a string the driver logs
genuinely DO emit. Verified by falsification on a real driver log: baseline
`timeout_events=0 worst_consecutive=2` -> ok; planting one `(12 consecutive` line gives
`worst_consecutive=12` -> **rc=2 CRITICAL**. The `ssh_timeout_diagnostic` counter is also correct (it
uses the right string and feeds the D9 evidence block). **So only the REPORTED `timeout_events` figure
is false; the guard's decision is sound.**

**Becomes:** count what a transport timeout actually produces, exactly as the status page now does —

```python
    if "ssh_timeout_diagnostic" in line or "TimeoutExpired" in line:
        timeouts += 1
```

**Falsifiable test (must FAIL first):** append a line containing `ssh_timeout_diagnostic` to a synthetic
driver log and assert `timeout_events` rises from 0 to 1; against the pre-fix code it stays 0.

⚠ **WHY IT IS DEFERRED RATHER THAN FIXED NOW.** `scripts/` is inside the **drift watch** (record 3):
editing it — committed or not — makes the drift check permanently non-zero and turns the monitoring
cycle into a standing alarm for code the drivers never import. The change is safe in itself (it alters
a REPORTED number, not a computed one, so it does not touch the deterministic-replay argument of 75.1)
and should go in with the **core-line C4 relaunch** alongside items 1-7, 9, 10, 12, 13.

---

## 15. WRITE-UP TOOLING THAT LANDS INSIDE THE DRIFT FENCE — queued on behalf of the write-up lane (2026-07-31, RUN 9)

**Not defects.** These are four planned additions from `docs/GRADE_95_MASTER_PLAN.md` whose target
files sit inside the `src scripts config prompts` pathspec, so they cannot be written while RUN 4 is
live. They are recorded here because **`docs/DEFERRED_FIXES_RUN4.md` is ops-owned** and
`docs/LANE_COORDINATION_2026-07-31.md` §2 assigns the queuing to the ops lane explicitly:

> *"`presentation_lint.py`, the `WHY_REGISTER` generator, the `ASSEMBLY` edit and the seed-trajectory
> figure function should be added to `docs/DEFERRED_FIXES_RUN4.md` **by the ops lane** so they ship with
> the next restart. The write-up lane must not add them unilaterally — that file is ops-owned."*

**Verified first-hand before queuing** (the P42 rule — do not assert something about an artefact
without opening it): all four action IDs exist in the master plan at the lines cited below.

| id | action | target file (FENCED) | plan line |
|---|---|---|---|
| **15a** | **C4-1** Phase 1 restructure — the **`ASSEMBLY` tuple edit** to the 16-section order (Theory → Appendix C, Prototype → Appendix D, new §10 Data, CH7 split into §13 Discussion + §14 Conclusions, and the four orphan `paper/sections/` files wired in) | `scripts/build_paper.py` | `GRADE_95_MASTER_PLAN.md:195` |
| **15b** | **C4-3** `presentation_lint.py` — machine-gate the presentation checklist; exit non-zero on any failure | `scripts/presentation_lint.py` (new) | `:197`, `:314` |
| **15c** | **X-6** the `docs/WHY_REGISTER.md` **generator** — one row per quantity (observation · mechanism · uncertainty · counterfactual), generated from the 35 `out[...]` keys of `scripts/analyze_campaign.py` rather than hand-listed | `scripts/` (new) | `:220` |
| **15d** | **X-7** the seed-trajectory panel function (Okhrati D2) — small multiples over every seeded unit plus the per-seed-block heterogeneity variant | `src/viz/figures.py` | `:221`, `:1001` |

**★ ONLY THE FILE LOCATION IS FENCED, NOT THE WORK.** `LANE_COORDINATION §2` splits C4-1 correctly:
the *content* half — creating the appendix files, the Data section, the Discussion/Conclusions split,
and the four orphan sections — is **entirely inside `paper/` and is UNFENCED**. Only the one-line
`ASSEMBLY` tuple edit waits. The same applies to 15b/15c/15d: **author and validate them in the
scratchpad, land them at the re-base.** That is the rule R96's harness already lives under (§40.3).

**GATING CONDITION — different from items 1-14.** Items 1-14 wait for the **core-line C4 boundary**
because they protect a confirmatory quantity. These four wait only because of the **drift invariant**:
none of them is imported by a driver, none changes what a training computes, and none touches the
determinism envelope. They are the **cheapest** things in this file to land and carry **zero** science
risk — they simply cannot be committed while `git status --porcelain -- src scripts config prompts`
must stay empty.

**Consequence for sequencing:** when the core line reaches C4 and the relaunch happens, **land 15a-15d
in the same change as items 1-7, 9, 10, 12, 13, 14.** A second restart purely for write-up tooling
would be a needless disturbance of a live ladder.

⚠ **15d TOUCHES `src/`.** `src/viz/figures.py` is not imported by the training path, but it IS inside
the pathspec and inside the repository the drivers were launched from. Treat it exactly like the
others: no edit before the re-base.

---

# ★★★ RUN 10 DISPOSITION — 2026-08-01. EVERY ITEM WORKED TO A VERDICT.

Tamer, 2026-08-01: *"apply everything that was supposed to be applied **if you think that would
benefit the campaign**… Don't be fucking lazy"* and *"0 issue tolerance, 0 defects tolerance."*
Both halves are load-bearing: he asked for JUDGEMENT, not a checklist. Applying all of them
uncritically would have shipped D17 — which breaks deterministic replay mid-campaign — so every
item below carries its verdict AND its reason. **Nothing is left unstated; a silent skip is the
defect this block exists to prevent.**

| item | verdict | why |
|---|---|---|
| **1 · D13** empty completion | ✅ **APPLIED** | a live crash path that had already killed 5 arm pipelines. **Two defects in the SPEC itself** — see below. |
| **2 · D12** gate-stop exit code | ✅ applied by RUN 9 (§97) | — |
| **3 · preflight headroom** | ⏸ **DEFERRED, stated** | `preflight.py` runs only BEFORE a campaign. It cannot affect anything live, and it is the single item with zero semantic risk — but it also buys the live run nothing, and every line I touch in a fenced file is risk. It ships at the next natural restart. |
| **4 · D14** silent partial arm failure | ✅ **APPLIED (the protective half)** | the *early stop* is in. See the scope note below — the detection half was already live. |
| **5 · D15** watchdog host fence | ✅ **APPLIED — and it was WORSE than described** | see below. |
| **6 · D16** substrate in the gate | ✅ applied by RUN 9 (§97) | — |
| **7 · D17** safe-default clears state | ⛔ **NEVER APPLY WHILE LIVE** | it changes reward-evaluation SEMANTICS on the training path. Every record written before the change would replay differently — a direct hit on reproducibility layer 1. RUN 9's refusal is upheld. Limitation B.8.7. |
| **8 · memory sizing** | ✅ applied 2026-07-30 | do not re-apply; its test cannot fail. |
| **9 · `CPU_THREAD_SPEEDUP[8]`** | ✅ **APPLIED** | 2.72x was an idle bench; production says **1.92x** across 740 timed trainings. Model input only. |
| **10 · D18** one record at two paths | ⏸ **DEFERRED, and this is a DELIBERATE assessment, not an oversight** | 1 duplicate in 1,591 records (0.06 %), byte-identical, on a report-only leg, **zero on the confirmatory path**, and NOT growing (re-verified at a 41 % larger archive, §65.4). The fix touches ~20 discovery sites across 8 files. **A 20-site diff on a live confirmatory run is a larger risk than the defect it removes.** Re-open if a second duplicate ever appears — that would make it systematic, which is the condition the original entry named. |
| **11 · `--pack 8`** | ✅ applied 2026-07-31 (§58), re-verified optimal (§96.5) | — |
| **12 · D19** search-lane `h_rt` | ⏸ **DEFERRED, on the original reasoning, re-checked** | 12 kills, 0 candidates lost, and the tight lane is SEARCH — which ends in 1-2 days — while C4 is the TEST lane at 1.52x headroom. A longer walltime is HARDER to backfill, so it trades a self-limiting problem for a permanent placement penalty. **Re-open if the search p99 climbs toward 14 h.** |
| **13 · D20** lock identity | ✅ **APPLIED — and it FIRED FOR REAL first** | see below. |
| **14 · `timeout_events`** | ✅ **APPLIED** | the counter searched for a string nothing emits. Structurally zero. |
| **15a-d · write-up tooling** | 🔄 **RE-SCOPED at the write-up lane's request** | see below. |

### 1 · D13 — ★ THE SPECIFICATION ABOVE CONTAINED TWO DEFECTS OF ITS OWN

1. **The fix as specified would have retried NOTHING.** Item 1 places the `EmptyCompletionError`
   check at the extraction site — i.e. AFTER `self._retrying(_call)` has already returned, outside
   tenacity's scope. The named error would have propagated on the first malformed body and retried
   **zero** times. Caught by writing a test that asserted *recovery* rather than *classification*;
   `test_the_named_fault_is_classified_transient` passes against the broken placement. **The
   validation now lives INSIDE the retried callable, on both transports.**
2. **The spec covered only the OpenAI path — and the identical defect is on the ANTHROPIC
   transport, which is what the CONFIRMATORY core line runs on.** `blocks = list(message.content)`
   fails as `TypeError: 'NoneType' object is not iterable`. Found by grepping every
   response-extraction site rather than fixing only the one that had already bitten us.

**The line the fix must not cross, now pinned by three tests:** a response that is well-formed but
says nothing — a truncation, a refusal, a completion carrying only `thinking` blocks — is a
LEGITIMATE authoring outcome and must reach the archive as an authoring failure. That is the
capability signal the per-model reliability result is measured from. Retrying it would silently
change which candidates exist. **The predicate is "the container is missing", never "the text is
empty".**

11 tests; falsified against HEAD in all four failure modes (`TypeError`/`IndexError`,
`transient=False` for each).

### 4 · D14 — SCOPE, STATED EXACTLY

**Applied: 4b, the protective half.** A core arm that RAISED now stops the pass **before** the H2
pair test, writes a line-qualified `ARM_CRASH_<line>.json` marker, and exits non-zero so the
supervisor relaunches and `--resume` re-runs only that arm.

**The reason this is the important half, and it is not the one the register emphasised.** The
register framed D14 as wasted compute. It is worse: the statement immediately after the arm drain
builds the H2 pair test from `winners`, as ONE `interleave=True` CRN-paired array. **A crashed arm
has no winner, so it would be SILENTLY ABSENT from that array** — every seed paired against a
comparator set that is not the registered one. Stopping is what prevents that.

**Deliberately NARROW, with a control test.** Only an arm carrying an `error` key stops anything.
A `no_winner`, an R115 ineligibility, or a canary-gated arm is a RESULT of the experiment, not a
fault; stopping on those would relaunch the line forever on an ordinary scientific outcome.

**NOT applied: 4a, porting `arm_coverage` into `campaign_guards.py`.** The detector is ALREADY
ARMED and running every ~42 s from `docs/ops/arm_coverage.py`, and has been since 2026-07-29.
Porting it would duplicate live logic into a second location during a live run and change nothing
operationally. **Signal over noise: it is tidiness, not safety.** The marker above is wired into
`docs/ops/cycle.py` and positive-controlled.

### 5 · D15 — ★ THE REGISTER SUSPECTED `mode_d_launch.ps1`. IT WAS RIGHT, AND IT IS THE WORSE HALF.

The entry closes with *"Audit the OTHER launchers for the same omission when applying:
`mode_d_launch.ps1` and `campaign_backup.ps1` were fixed for roots in D4, but were not checked for
the fence."* **Checked 2026-08-01: `mode_d_launch.ps1` passed NO `-ExcludeHosts` at all.** So the
substrate fence protecting this run existed ONLY because the twelve live supervisors happened to be
started with it BY HAND. A clean relaunch from the ratified launch script would have dropped it —
for **all twelve lines at once**, not one revived line.

Both launchers now take the parameter, thread it, and the watchdog LOGS the fence it will revive
with (a fence nobody prints can be wrong for days). 8 tests, 7 falsified against HEAD; the 8th is a
**discovery-based completeness test** — it enumerates every `.ps1` that actually EXECUTES
`mode_d_supervisor.ps1` (comment-stripped, so prose cannot masquerade as a call site) and fails if
one is not fence-tested. A hard-coded launcher list inside the test would be the same failure
waiting to happen.

### 13 · D20 — IT STRANDED A C4 LINE FOR ~14 HOURS BEFORE IT WAS APPLIED

See `CAMPAIGN_EXECUTION_RECORD.md` §100. `leg4` (`qwen3.5-9b`) was hard-down from a pid recycled
onto `backgroundTaskHost.exe`. Fixed live at 01:05:46Z, then twice over: the monitoring cycle now
**reaps** such a lock (commit `2368b5e`), and the lock itself now records the owner's process
**create-time**, so a recycled pid is decisively distinguishable.

**The design point worth carrying forward:** the two possible errors are NOT symmetric. Breaking a
LIVE owner's lock permits two drivers on one batch — double requeues, corrupted retry accounting,
unrecoverable. Failing to break a dead owner's lock stalls a line — recoverable, and now
auto-reaped. **So every ambiguity resolves to "owned"**, and that direction is pinned by its own
tests (`test_ambiguity_resolves_to_owned`, `test_empty_cmdline_resolves_to_owned`). The legacy
fallback matters during the deploy itself: locks already on disk carry no create-time.

### 15 · WRITE-UP TOOLING — RE-SCOPED EXACTLY AS THE WRITE-UP LANE ASKED

`docs/LANE_COORDINATION_2026-07-31.md` §4c-REVISED raised four corrections. **All four are
accepted, and this register is the ops-owned place they land:**

| id | scope | state |
|---|---|---|
| **15a-i** | wire the **13** existing `paper/` artefacts into `ASSEMBLY`/`APPENDICES` (the lane's tuple, which is authoritative — `ls paper/tables/` is the source of truth for the count, not any prose figure) | **READY, mechanical — blocked ONLY on the lane confirming its SHIP-FORM pass** |
| **15a-ii** | the 16-section restructure (Appendix C/D, §10 Data, the CH7 split) | ⛔ blocked on `paper/` content that does not exist yet. **Not attempted.** |
| **15b** | `scripts/presentation_lint.py` | queued |
| **15c** | the `docs/WHY_REGISTER.md` generator | queued |
| **15d** | the seed-trajectory panel in `src/viz/figures.py` | queued |
| **15e** | ★ **widen `check_citations.py` beyond `paper/*.md` top-level** | **ADDED, as requested, with the lane's constraint: it MUST land in the same commit as 15a-i.** The lane is right that this is the dangerous half — wiring the artefacts while the gate still globs only the top level would import unchecked citations, including dangling keys, straight into the compiled PDF, and the integrity check would report clean. |

**And the four `paper/sections/` files are NOT to be wired** — they are inserts into body chapters,
and wiring them as standalone `ASSEMBLY` entries would move ~1,100 words of counted prose outside
`word_budget.py`'s `BODY_CHAPTERS`. That is word-count evasion, not the appendix escape hatch.

---

## 16. ★ D21 — THERE IS NO REBOOT RECOVERY AT ALL (found 2026-08-01, RUN 10)

**Verified, not assumed:** `Get-ScheduledTask | Where-Object { … -like '*llm-reward-portfolio*' }`
returns **nothing**. The ONSTART task `scripts/install_onstart_task.ps1` exists but **was never
registered for this run**.

**Exposure.** A Windows Update reboot — over a 26-day run, not a remote possibility — kills all 12
supervisors, all 24 drivers, the watchdog, the cycle loop, the publisher and the backup, and
**none of them come back.** The Myriad arrays keep running and finishing with nobody polling,
pulling or submitting the next generation.

**And the installer as written would not fix it.** Its `-Myriad` branch does not start the mode-D
fleet at all: it launches `scripts/supervisor.py` driving ONE `run_campaign_cluster.py` with
hard-coded args carrying `--batch-tag c1` (the CORE LINE ONLY — the other eleven would stay down),
`--pack 4` (the live fleet runs `--pack 8`, §58) and `--exclude-hosts node-d00a-230` (**missing
`node-d00b-024` — the substrate fence, i.e. the D15 defect on the reboot path**).

**The fix is not to correct those three literals — it is to delete them.** A reboot must re-enter
the fleet through `mode_d_launch.ps1` + the watchdog, which are the single source of truth for how
this campaign starts; duplicating the argument vector is what produced all three drifts. Queued as
the next change after the D13/D14/D15/D20 deploy.

---

## 17. D22 — `src/utils/provenance.py:77` reads a subprocess with the box's locale codec (found 2026-08-01, RUN 11)

**The class.** `subprocess.run(args, capture_output=True, text=True)` with no `encoding=` decodes the
child's output with the LOCALE codec — cp1251 on this box. Reproduced by execution this session
(`tests/test_build_paper_diagnostics.py`, the positive control): the reader thread dies on the first
non-decodable byte and **`subprocess.run` still returns rc=0 with the channel gone**. In
`scripts/build_paper.py` this exact idiom hid seventeen dropped characters in the deliverable for
nineteen days, so the class is not theoretical.

**Why this instance is DEFERRED and not fixed with the other two.** `src/utils/provenance.py` **IS
inside the driver import closure** — proven, not assumed:
`python docs/ops/import_closure.py src/utils/provenance.py` reports REACHED. Editing it live would
require a full 12-line relaunch, and the fix does not earn one.

**Why it is nearly harmless today, stated so the priority is honest.** The call is
`git rev-parse --short HEAD`, whose output is a hex SHA — ASCII by construction, so there is no byte
that can fail to decode. The residual exposure is the `except` clause: it catches only
`CalledProcessError` and `FileNotFoundError`, so a decode error would PROPAGATE out of a provenance
helper rather than fall through to the `GIT_COMMIT` marker path.

**The fix, for the next relaunch or post-campaign window:** add `encoding="utf-8",
errors="replace"`, and widen the `except` to include `UnicodeDecodeError` (or `OSError`/`ValueError`)
so the deployed-archive fallback is reachable from every failure mode rather than two of them.

**Already fixed, same class, both proven OUTSIDE the closure and landed live:**
`scripts/build_paper.py` (severe — the false-green) and `scripts/resume_brief.py` (cosmetic — the
session brief would silently lose a section).

## 18. D23 — THE C4 SUBMISSION WILL EXCEED `max_u_jobs`, AND THE REJECTION PATH IS UNPROVEN (found 2026-08-01, RUN 11)

**The arithmetic, from the executed tier sizes `[30,70,89,90,61,63,165]`** (C4 blocks = the last six
= 538 seeds) **and `--pack 8`:**

```
core line   20 units x 538 seeds = 10,760 trainings -> 1,345 tasks
each leg     5 units x 538 seeds =  2,690 trainings ->   337 tasks
fleet total                                          -> 5,052 tasks
```

**At `--chunk-tasks 1` every task is its own array job, so that is 5,052 array jobs against
`max_u_jobs = 1000`. The CORE LINE ALONE (1,345) exceeds the cap.**

> ### ⚠⚠ UPDATE 2026-08-02 — IT HAS NOW HAPPENED, AND THE REJECTION STRING IS NO LONGER A GUESS
>
> With two of eleven lines in C4 the job count reached **exactly 1000**, and a submission was refused.
> The literal message, captured live, is:
>
> ```
> Unable to run job: job rejected: only 1000 jobs are allowed per user (current job count: 1000)
> ```
>
> `max_u_jobs = 1000` is also confirmed first-hand from **both** `qconf -sconf` and `qconf -ssconf`,
> rather than from documentation. **The fix must match that exact string**, which was previously
> unmeasured — this entry could only say "the rejection path is UNPROVEN".
>
> **Where it surfaces:** `submit.qsub` is three lines —
> `return parse_job_id(runner(["qsub", jobscript_remote_path]))` — so the refusal arrives either as a
> `CalledProcessError` from the runner or as `parse_job_id`'s "could not parse a job id" `RuntimeError`.
> **A correct fix must handle BOTH**, back off, and retry rather than raise.
>
> **Realised cost so far: ZERO.** At the moment of writing no driver has crashed on it (0 rejections in
> the driver logs, 0 pipeline crashes in two hours) because the drivers submit per block as blocks
> drain, and it was MY probe submission that met the cap first. But nine more lines are still to enter
> C4, and the fleet demand is 5,052 jobs against 1,000.
>
> **AND SIX OF THE THOUSAND ARE JUNK.** The six `sshorig` interactive jobs pinned to an unavailable
> host have been unschedulable since 2026-08-01 16:07 (`qalter -w p`: *"verification: no suitable
> queues"*). 994 campaign jobs + 6 junk = the cap exactly. **`qdel 66103 66104 66105 66106 66107
> 66108` buys back the whole margin** — and `qdel` is blocked for the agent, so it is one command for
> Tamer.

**⚠ THE FIX IS NOT CHUNKING.** `mode_d_supervisor.ps1:119` records the site policy: *"arrays are
SERIALISED by policy (tasks 2..n sit in hqw) and pending tails have twice been PURGED outright."*
Chunking to 25 would park 24 of every 25 tasks in hold. `--chunk-tasks 1` stays.

**WHY THIS IS PROBABLY FINE, AND WHY THAT IS NOT GOOD ENOUGH.** The cap is very likely not the
binding constraint: 1,000 jobs x 8 packed trainings = **8,000 slots**, far above the **3,366 free in
pool D**. So we should saturate on free capacity long before we saturate on job count, and the
expected behaviour is that `qsub` rejects the excess per-call, the driver re-derives pending on its
next cycle and retries — self-pacing by construction.

**WHAT IS NOT PROVEN, AND IT IS CHECKABLE STATICALLY:** whether a run of `qsub` rejections can trip
the driver's CONSECUTIVE-FAILURE bound and take a line down. `driver.py` has a documented
"consecutive-failure streak is fatal only once it persists past BOTH bounds' first trip" for
TRANSPORT failures; a submission rejection at the job cap is a different class and may or may not be
accounted the same way. **If it is counted as a transport-class failure, the fleet could start losing
lines at exactly the moment C4 opens — the worst possible timing.**

**ACTION:** read the submission-failure accounting in `src/cluster/driver.py` and, if a rejection
streak is fatal, either classify `max_u_jobs` rejections as a benign back-pressure signal (retry
without incrementing the streak) or add an explicit outstanding-job budget at the submit layer. This
needs no relaunch — the driver re-reads nothing, but the change lands on the next natural restart.

### D23 — RESOLVED THE SAME DAY, BY READING THE FAILURE ACCOUNTING. NOT A HAZARD.

Checked immediately rather than left queued, because it would have bitten at the worst moment.
**The rejection path is graceful, for three independent reasons:**

1. **A `qsub` rejection is CAUGHT, not fatal.** `_TRANSPORT_ERRORS = (ConnectionError, TimeoutError,
   OSError, subprocess.SubprocessError, RuntimeError)` — broad enough to cover every way an ssh
   `qsub` failure surfaces. The submit sits inside that `except`, which increments `ops_failures`
   and retries. **`pending_submit` is cleared ONLY on success** (`# consumed ONLY on success -> a
   failed submit re-tries`), so nothing is dropped.
2. **The streak resets on ANY successful cycle** (`ops_failures = 0` on the success path). Fatality
   needs 72 CONSECUTIVE failures (3.6 h at `--poll-secs 180`) or a 12 h continuous outage. As our
   own jobs complete, the job count falls and submits succeed again, resetting the counter.
3. **AND THE CAP ALMOST CERTAINLY NEVER BINDS.** Free capacity in pool D is ~3,366 slots = **~420
   jobs at pack 8** — well under `max_u_jobs = 1000`. We saturate on FREE SLOTS long before job
   count, so the 1,345/5,052 arithmetic above describes DEMAND, not what SGE will ever let us hold.

**Downgraded from hazard to analysed-and-benign. Overstating a risk is as inaccurate as
understating one, and leaving a phantom in this file costs the next reader real attention.**
The residual, and it is small: nobody has OBSERVED a `max_u_jobs` rejection in this campaign, so
point 1 is a reading of the code paths rather than a measurement. If C4 ever does hit the cap, the
log line to look for is a `queue op failed (N consecutive, …)` warning naming the batch.

## 19. D24 — `_outage_is_fatal` IS AN **OR** WHILE ITS DOCSTRING SAYS **BOTH**, SO THE DRIVER DIES AT 3.6 h, NOT 12 h (found by COORD 2026-08-01, M223)

**Found by the coord lane, statically, and it is the reassuring-comment tell in its purest form: the
same function documents itself both ways and the safe-sounding version is the wrong one.**

`run_batch`'s docstring (`driver.py:369-371`) says a failure streak *"is fatal only once it persists
past **BOTH** bounds' first trip"*. **The code is an OR** — `_outage_is_fatal` (`:434-440`) returns
True as soon as `n_failures >= max_consecutive_errors`, regardless of elapsed time. Its own INNER
docstring correctly says *"EITHER bound"*.

**WHY IT HAS NEVER MATTERED, AND WHY THAT IS ABOUT TO CHANGE.** The two bounds coincide exactly at
the DEFAULT poll interval — `72 × 600 s = 43,200 s = 12.0 h = max_transport_outage_secs` — which is
plainly deliberate, and while `poll_secs = 600` the OR-vs-AND distinction is invisible. **But the
live supervisors pass `--poll-secs 180`** (`mode_d_supervisor.ps1:146`, `campaign_supervisor.ps1:44`):

```
poll 600 s (default) -> 12.0 h      poll 180 s (LIVE) -> 3.6 h
poll 120 s           ->  2.4 h      poll  45 s        -> 0.9 h
```

**So today the count bound trips 3.3× sooner than the docstring promises, and any poll shortening
done to chase throughput shortens it proportionally.**

**THE PATCH (coord's, and it restores the design's own intent):**
```python
effective_max_errors = max(max_consecutive_errors, max_transport_outage_secs / poll_secs)
```
so the count bound can never be tighter than the time bound — making the 600 s coincidence
poll-rate-INVARIANT instead of an accident of the default. **And fix the `:370` docstring to say
EITHER**, because a reader who trusts it today believes they have 12 h and has 3.6.

**⚠ WHY IT IS NOT APPLIED IN RUN 11.** `src/cluster/driver.py` **IS in the driver import closure** —
`docs/ops/import_closure.py` reports `REACHED: src.cluster.driver (via src.cluster.campaign)` — so
landing it requires relaunching all twelve lines. Committing it WITHOUT a relaunch would make
`RUNNING_SHA` assert that the executing code matches the committed code when it does not, which is
the one thing the drift invariant exists to prevent. **Apply it at the next natural relaunch**; the
procedure is proven in record §100.50 and takes ~5 min per line via the watchdog.

**AND A MITIGATION COORD DID NOT ACCOUNT FOR, WHICH DOWNGRADES THE SEVERITY — verified in the
supervisor source.** A fatal raise does **not** end the line: `mode_d_supervisor.ps1` wraps the
driver in `while ($attempt -lt $maxAttempts)` with **`$maxAttempts = 1000`** and
**`$backoffSecs = 600`**, and the fenced watchdog independently revives any line whose supervisor
dies (≤300 s). **So the realised cost of hitting this bound is roughly ten minutes and a log line,
not a lost line.** Combined with D23 — the slot ceiling (3,366 free in pool D) binds long before the
1,000-job ceiling, so submissions should thin rather than fail outright — this is a real defect worth
fixing on its own merits, and not an emergency.

> **⚠ CORRECTED 2026-08-01 (RUN 12, ops). THE FINAL CLAUSE ABOVE IS WRONG, AND IT IS THE LOAD-BEARING
> ONE.** *"The slot ceiling binds long before the 1,000-job ceiling, so submissions should thin rather
> than fail outright"* assumes the submitter throttles to AVAILABLE SLOTS. **It does not.**
> `submit_batch` (`src/cluster/driver.py:150-161`) `qsub`s **every** part unconditionally, and SGE
> counts **QUEUED** jobs toward `max_u_jobs`. So we can hold ~341 running (2,729 free ÷ 8) while
> submitting thousands more into `qw` — **the JOB ceiling binds FIRST, not the slot ceiling.** See
> **D25**. The rest of D24 stands.

---

### D25 — **`max_u_jobs = 1000` IS THE REAL C4 FENCE, AND IT WILL BE BREACHED.** Not a hazard to fix while live; a behaviour to EXPECT.

**MEASURED 2026-08-01 (RUN 12).** `qconf -sconf` ⇒ `max_u_jobs 1000` (live). The pipelined C4 path
(`src/cluster/campaign.py:1997`) submits **all six assurance blocks at once** via a
`ThreadPoolExecutor` over `tiers[1:]`. Block increments are 70/89/90/61/63/165 seeds × 5 units ÷ 8
per pack ⇒ **~340 jobs PER LINE in one go**, on top of the ~104 steady-state.

| lines in C4 | jobs in system | verdict |
|---|---|---|
| 1 | 444 | ✔ |
| 2 | 784 | ✔ |
| **3** | **1,124** | ✘ **cap breached** |

Only ~341 of our jobs can RUN against the 2,729 free slots in d00a+d00b; **the remainder queue, and
queued jobs count toward the cap.** With 11 lines converging on C4 the breach is near-certain.

**THE FAILURE MODE, TRACED FIRST-HAND (this is the part that matters operationally).**
`src/cluster/submit.py:198` `parse_job_id` **raises `RuntimeError`** on any output it cannot parse, so
a cap rejection fails **LOUD**: `qsub` → `submit_batch` → `run_test_leg` → the C4 `ex.map` → **the
driver crashes** → `mode_d_supervisor.ps1` relaunches it with `--resume`. **No records are lost**,
already-submitted jobs keep running, and `--resume` skips completed seeds rather than re-training
them. **So the outcome is survivable and self-healing — but the mechanism is a CRASH-LOOP, not a
clean backoff.** D23/M223 called this path "graceful"; the verdict is right and the mechanism
description is not.

> **★ THE STANDING INSTRUCTION THAT MATTERS: when C4 opens, drivers crash-looping around `qsub` is
> EXPECTED BEHAVIOUR, not a new defect.** A session that sees it, diagnoses a bug and "fixes" it
> mid-ladder will do real damage. Confirm the cause by checking `qstat -u ucestes | wc -l` against
> 1000 BEFORE acting.

**THE OBVIOUS MITIGATION IS FORBIDDEN.** `src/cluster/allocation.py:284` advises *"chunk the rung
blocks up if the pending count approaches the cap"*, and `:256` already anticipated the breach
(*"chunk-1 with pipelined rungs can enqueue ~1,200 arrays, where a cap hit classes as a transport
error"*). **But RUN 11 established that Myriad SERIALISES array tasks — tasks 2..n sit in `hqw`** —
so `--chunk-tasks 25` would park ~96 % of C4 in hold. **These two pieces of in-repo guidance are in
direct conflict; the brief's side (`chunk-1`) is correct and must win.**

### D26 — ~~`--pack 9` strictly dominates pack 8~~ **★ REFUTED BY MY OWN MEASUREMENT, 2026-08-01 (RUN 12). DO NOT ACT ON IT.**

> **★★★ THE FINDING BELOW IS WRONG, AND THE REASON IS THE MOST USEFUL PART OF IT.**
> **I computed the free-slot histogram over ALL d00a/d00b nodes. 89 nodes on Myriad belong to PAID
> DEPARTMENTAL ALLOCATIONS (`@PAID_BLIC`, `@PAID_Economics`, `@PAID_hpc.10/11`, `@PAID_MathsStatSci`,
> `@PAID_MEDPHYS`), and queue `Bran` gates each via a per-hostgroup `user_lists` override. Of those,
> 47 are d00a and 7 are d00b — nodes I counted as ours.**
>
> **THE DECISIVE NUMBER: of the 49 completely-empty (36-free) nodes the pack-9 case rested on,
> ALL 49 ARE PAID NODES. On the set we can actually reach there are ZERO empty nodes** — so the
> `36 mod 8 = 4` stranded-core argument, which requires a fully-empty 36-core node, **does not apply
> to any node we can use.** Recomputed over reachable nodes only, the table INVERTS:
>
> | pack | usable (reachable only) | % of free |
> |---|---|---|
> | **8 (current)** | **248** | 37.7 % |
> | **9** | **225** | 34.2 % |
> | 4 | 448 | 68.1 % |
> | 1 | 658 | 100 % |
>
> **Pack 9 is WORSE than pack 8 on the nodes we can actually use.** The deferral in the original
> entry happened to be the right call, but for the wrong reason — and had we relaunched for it we
> would have made throughput worse while believing we improved it.
>
> **THAT PAID NODES ARE UNUSABLE BY US IS MEASURED, NOT ASSUMED — 83 observations, zero
> counterexamples:** all 83 hosts our jobs occupied at 18:05 UTC are non-paid; the 3 d00a probe
> nodes that placed are non-paid; `node-d00a-126` (a real completed campaign job, from `qacct`) is
> non-paid; and 22 probes pinned to d97 (100 % `@PAID_Economics`) sat in `qw` indefinitely while
> identical probes on non-paid d00a placed in ~5 minutes.
>
> **THE STANDING LESSON, and it generalises past this row:** *a capacity number computed over nodes
> you are not entitled to is not a capacity number.* Coord's M237 warned that the empty-node count
> was a load-bearing SNAPSHOT worth a second sample before acting. The second sample did not just
> move the number — **it reversed the conclusion.** Any future pack/throughput analysis MUST filter
> `@PAID_*` hostgroups first.

**(Original entry retained below for the audit trail — its numbers are superseded.)**

### D26 (SUPERSEDED) — `--pack 8` strands 4 of every 36 cores; `--pack 9` appeared to dominate.

**THE STRUCTURAL FACT, MEASURED 2026-08-01 (RUN 12).** Pool-d nodes are uniformly **36 slots**
(d00a 8,712/242 = 36.0; d00b 612/17 = 36.0), and `smp-D` has **`allocation_rule $pe_slots`**
(verified `qconf -sp smp-D`) — so **every slot of a job must be on ONE node**. Therefore
**36 mod 8 = 4: on every fully-empty node, pack 8 fits 4 jobs = 32 slots and STRANDS 4 CORES
(11.1 %).** This is structural, not a property of any snapshot. Pack sizes dividing 36 (6, 9, 12, 18)
strand nothing.

**MEASURED FREE-CAPACITY DISTRIBUTION (`qhost -q`, d00a+d00b, 2,802 free over 259 nodes):**
**62 nodes completely empty (36 free) = 2,232 slots = 80 % of all free capacity**; 69 nodes with 0
free; 128 nodes fragmented at 1–17 free (570 slots).

| pack | 36 mod k | usable slots | % of free | jobs/line @C4 | lines before the 1000-cap |
|---|---|---|---|---|---|
| **8 (current)** | **4** | 2,184 | 77.9 % | 337 | 2 |
| **9** | **0** | **2,421 (+237)** | **86.4 %** | **299 (−11 %)** | 2 |
| 12 | 0 | 2,328 | 83.1 % | 225 | 3 |
| 18 | 0 | 2,232 | 79.7 % | 150 | 5 |

**Pack 9 beats pack 8 on EVERY axis simultaneously** — more usable capacity, fewer concurrent jobs
(269 vs 273), and less `max_u_jobs` pressure. C4 makespan 6.7 d → **6.0 d**.

**WHY THIS WAS MISSED, AND IT IS NOT A CRITICISM OF §50.** Record **§50** ("C4 RUNS AT `--pack 8`, AND
THE REASON IS RISK, NOT SPEED", 2026-07-31) chose 8 deliberately, after Tamer challenged the earlier
"pack 8 buys nothing" — but the comparison was **pack 4 vs pack 8 ONLY**. The divisibility loss
appears nowhere in the record, because **`recommend_pack` (`allocation.py:211`) is purely VRAM-based**
(`floor(VRAM*0.9/per-training)`, "pack-5 everywhere") — **a GPU-era function with no concept of CPU
core counts.** P17's own lesson was *"evaluate across the range you will actually operate in, not at
the boundary"*; the range simply never included the divisors of 36.

**FEASIBILITY, ALL CHECKED.** Memory: `jobscript.py:291` computes `1.55 GB × pack × 1.3` = **18.1 GB
at pack 9**, four jobs/node = 72 GB of 188 GB — fine. Arithmetic: **pack is NEUTRAL** — `_task_device`
/ `_task_threads` (`run_one.py:240`) read device and threads from the SPECS and **fail loud on a
mix**, and all **591 live pack-8 test records** carry `omp=1, torch_threads=1, cuda_available=False`,
one CPU model. Pack changes only how many single-core trainings share one placement.

> **★ THE DECISION: NOT APPLIED IN RUN 12, AND THE REASON IS EVIDENCE, NOT EFFORT.**
> The gain is **~0.7 days** on a budget with **~19 days of slack** (26 available, ~7 needed). Against
> that: **the pack>1 path on the CPU lane is NEW code as of 2026-07-31** — `run_one.py:250` states
> plainly *"the CPU lane has only ever been exercised at pack=1"*, and that path once silently forced
> `device="cuda"` on every packed CPU spec. **Pack 8 now has 591 production records of proven
> behaviour; pack 9 would have ZERO — and we would be adopting it at the exact moment C4 begins the
> irreplaceable bulk of the campaign.** On an irreplaceable run, *proven-at-scale beats 11 %
> theoretical.* Deferring is the higher-quality choice, not the lazier one.
>
> **APPLY AT THE NEXT NATURAL RELAUNCH**, alongside D22/D24/D25 — the rolling watchdog restart is
> proven (§100.50, ~5 min/line) and pack 9 rides along for free. **If the cluster becomes contended
> and free capacity concentrates into fragments, this finding gets MORE valuable, not less** (empty
> nodes are taken first, so the stranded-core penalty grows). Re-measure the histogram before
> deciding.

**ALSO CHECKED AND CLEAR (so nobody re-runs these):** `reserve: y` **IS** live on our jobs (verified
on job 61646 — CLAUDE.md's anti-starvation claim is CORRECT; the jobscript's `#$ -r y` is
*rerunnable*, a different flag, and I nearly mis-reported the doc as wrong by reading the template
instead of measuring the job). PE `smp-D` slot ceiling 10,476 — not binding. The six `sshorig` jobs
stuck in `qw` are **interactive** jobs (`interactive=true`) pinned to `hostname=node-d00b-007`, which
is why they never schedule — 1 slot each, harmless, not ours to fix.

---

**THE REAL FIX, WHEN A RELAUNCH IS NATURAL:** bound in-flight submissions — have `submit_batch`
detect the cap-rejection string and back off/retry rather than raise, or have the C4 path submit
blocks against a live `qstat` count instead of all six at once. **NOT applied in RUN 12:** both
`submit.py` and `campaign.py` are in the driver import closure, so landing either requires relaunching
all twelve lines, and the self-healing path above makes the realised cost churn rather than lost work.
**Apply at the next natural relaunch.**

---

## 20. ★★★★★ D27 — CMA-ES's POPULATION IS EVALUATED **SERIALLY**, SO THE CAMPAIGN'S LONGEST CHAIN IS 30 STEPS, NOT 4 (found 2026-08-02, RUN 13)

**This is the largest single throughput defect found in RUN 4, and it is the answer to "we are at a
very low amount of cores".** It is not a capacity problem. Measured the same night: 70 jobs running /
560 slots, **6 jobs queued** (all six the known unschedulable `sshorig` interactive jobs), and **864
entitled slots free** with 387 of our jobs placeable immediately. The scheduler was giving us
everything we asked for. We were not asking.

**Files:** `src/search/dfo_toolkit.py` ~line 121 · `src/cluster/campaign.py` ~line 1174 ·
`src/cluster/lanes.py` ~line 204-208. All three are inside the driver import closure.

### What the code does

`cma_es_over_template` proposes a whole generation and then evaluates it one member at a time:

```python
xs = [np.clip(np.asarray(x, dtype=float), lo, hi) for x in es.ask()]
remaining = budget - evaluated
if len(xs) <= remaining:
    scores = [_evaluate(x, "cma") for x in xs]      # <-- SERIAL list comprehension
    es.tell(xs, [-s for s in scores])
```

On the cluster path `_evaluate` is `campaign.template_eval`, and every call is a **blocking
`run.run_batch(...)`** — one array-of-1 job, queued and trained to completion before the next member
is proposed to the queue. A population of 9 is therefore 9 sequential cluster round-trips.

### What the code SAYS it does — and this is why nobody caught it

`src/cluster/campaign.py`, in the block that decides which arms get `batch_eval_fn`:

> `# random_search is already one array; CMA-ES already dispatches a whole population per`
> `# generation; neither accepts the kwarg.`

**That comment is false.** CMA-ES *proposes* a whole population per generation; it *dispatches* them
one at a time. The false comment is exactly why `batch_eval_fn` — already written, already wired for
`tpe` and `bayes_opt`, already identity-proven in `tests/test_dfo_tpe_batch.py` — was never extended
to `cma_es`. This is CLAUDE.md's own tell ④ in its purest form: *when a comment and the code
disagree, the COMMENT is the more dangerous artefact.*

`src/cluster/lanes.py` then encodes the same false belief as a planning constant:

> `#: * **CMA-ES ~ 4 serial generations.** ``es.ask()`` proposes a whole population per generation`
> `#:   (parallel within a generation), so at budget 30 with the default popsize ~9 it is ~4 steps —`
> `#:   never the binding chain.`
> `_CMA_SERIAL_GENERATIONS = 4`

### The three consequences, all measured

1. **PLANNING.** `lanes._critical_chain_days` prices the CMA chain at `4 x cpu_h`. The truth is
   `30 x cpu_h`. The makespan model understates this chain by **7.5x**, and `lanes.py:201`'s
   "this restores `bayes_opt` (25) as the longest DFO chain" is wrong — cma_es at 30 is longer.
2. **MONITORING — the chain has NO stall detector.** `sentinel.py:1295` builds `chain_progress` from
   `lanes.SERIAL_CHAIN_STEPS`, and `campaign_health.check_chain_progress` classifies an arm as done
   when `completed >= total`. Live output on 2026-08-02: **`chain_progress ... (bayes_opt 19/25,
   tpe 18/20, cma_es 9/4)` — reported OK with cma_es counted COMPLETE at 9 of a real 30.** The
   campaign's longest serial chain is the one arm the stall detector cannot see. That check exists,
   in its own docstring, because "a stalled chain is the campaign's worst silent failure".
3. **REALITY.** Measured from the archive (`docs/ops/family_arm_cadence.py`):
   `cma_es` **9/30 done**, median cadence **8.57 h/candidate**, mean 9.33 h.
   **21 candidates remain => ~180 h ~ 7.5 DAYS of pure serial chain** before the core line's C1
   barrier (`campaign.py`'s `as_completed` over EVERY arm, not just the five LLM arms) can release
   into C2, the C3 gate and C4. Nothing about core count changes that number.

### The numbers that decide it

Template dimension `d = 6` (`baselines.reward_family.family_bounds`), so pycma's default
`popsize = 4 + floor(3*ln 6) = 9`, and budget 30 = **generations of 9 + 9 + 9 and a partial 3**.
Nine candidates archived (`cma_es-c0 .. c8`) is **exactly generation 1 complete**, leaving **three
dispatch steps**.

| | remaining chain | wall-clock |
|---|---|---|
| **serial (today)** | 21 blocking round-trips | 21 x 8.57 h = **180 h ~ 7.5 d** |
| **batched (this fix)** | 3 array dispatches | 3 x ~5 h = **~15 h ~ 0.6 d** |

**Saving on the campaign's critical path: 80-160 h, i.e. 3.3-6.6 DAYS.** ⚠ The table above prices a batched generation at a TYPICAL training and the serial chain at its worst observed cadence; both are corrected in the "TWO CORRECTIONS" section at the end of this item, which is the figure of record.

### Why the fix cannot change any result

Identical in form to the TPE change already shipped and proven. `es.ask()` returns the whole
population **before any member is evaluated**, and `es.tell(xs, scores)` consumes all of them at
once, so no member's proposal depends on any other member's fitness. Dispatching the population as
ONE array therefore changes only *when* each training starts:

* same points (`es.ask()` untouched, same seed, same popsize),
* same candidate ids — `template_eval_batch` assigns from the shared `state["i"]` in `xs` order,
  which is the order the serial comprehension used,
* same fitnesses (each training is independent and seeded from its candidate id),
* same `es.tell(xs, scores)` => same subsequent generations.

**Resume is preserved for the same reason:** on `--resume` both eval paths replay an archived
candidate by id without retraining, so generation 1's nine fitnesses replay identically and
generation 2's `ask()` is unchanged.

### The change

1. `dfo_toolkit.cma_es_over_template`: accept `batch_eval_fn` and use it for a FULL generation —
   `scores = list(batch_eval_fn(xs)) if batch_eval_fn is not None else [_evaluate(x, "cma") for x in xs]`
   — keeping the partial-tail branch exactly as it is (it deliberately does not `tell`).
2. `campaign.run_family_search_arm`: change `if arm in ("tpe", "bayes_opt")` to include `"cma_es"`,
   and **delete the false comment** rather than leaving it to mislead a third time.
3. `lanes.py`: `_CMA_SERIAL_GENERATIONS` becomes the honest number for whichever variant is running —
   4 once batched, 30 while serial — and the note above it is corrected. This is what re-arms the
   sentinel's stall detector on this arm.
4. A test in the shape of `tests/test_dfo_tpe_batch.py` asserting the batched and serial paths
   produce the **same points, same order, same scores and same winner**. Without it this is an
   argument, not a proof, and the argument is exactly the one the false comment already made once.

### ⚠ NOT APPLIED TONIGHT, AND THE REASON IS ON THE RECORD

All three files are in the driver import closure, so landing this requires **relaunching the CORE
line — the confirmatory line — mid-search**. The prize is 3.3-6.6 days; the risk is a CMA state-replay
divergence on a confirmatory H4 arm of an irreplaceable campaign, executed while nobody is awake to
read the result. The correct sequencing is: land the change with its identity test green, then do a
controlled single-line relaunch and verify the first batched generation dispatches **9 concurrent
`c1_cma_es_c*` jobs** instead of one. **This is TAMER'S CALL and it is the highest-value decision
open on the campaign.** Every hour it waits is an hour of a 180 h chain.

**Cheap partial mitigation available immediately, no relaunch:** nothing. The chain is the chain.
The only thing that shortens it is dispatching the population.

**⚠ ONE IMPLEMENTATION HAZARD, verified by reading `template_eval_batch` rather than assuming it.**
Id assignment is confirmed safe — `cids = [f"{arm}-c{idx0 + j}" for j in range(len(coeffs_list))]`
allocates contiguously from the shared `state["i"]` in `xs` order, exactly as the serial
comprehension would. But the batch is submitted under the **fixed** name `f"{arm}_startup"`, which is
correct for TPE and GP-EI because each of them batches exactly ONCE (their startup/init phase).
CMA-ES would call it **once per generation**, so three generations would all submit as
`cma_es_startup` and collide on the same batch directory, the same `.driver.lock` and the same
`.permanent.jsonl`. A stale lock from that collision is not hypothetical — it cost this campaign
4.5 h on `cma_es-c5` on 2026-08-01. **The fix must pass a per-call batch name** (e.g.
`f"{arm}_gen{idx0}"`), and the identity test must cover two consecutive generations, not one.

### D27 — THE SAFETY ARGUMENT IS NOW PROVEN, NOT ARGUED (added 2026-08-02, same session)

`docs/ops/d27_identity_proof.py` runs the **real** `cma_es_over_template` twice at the campaign's own
shape (budget 30, dim 6, so popsize 9) with a deterministic evaluator — once in production's
one-at-a-time order, once with each generation scored as a single batch — and compares the full
sequence of proposed points **in order**, every score, the winner, the winner's score, and the
evaluation count.

```
budget 30, dim 6
serial : 30 evaluations, best -1.612888329269
batched: 30 evaluations, best -1.612888329269

IDENTICAL: same points in the same order, same scores, same winner, same eval count.
matched budget honoured exactly: 30 evaluations
mutation control: perturbing ONE score in the batched path IS detected.
```

The **order** check is not decoration: candidate ids are assigned in proposal order, and `--resume`
replays archived candidates BY ID, so a reordering would silently corrupt the replay on a confirmatory
arm. It is identical.

The **mutation control** is why the pass means anything. Perturbing a single score by `1e-6` inside the
batched path makes the comparison FAIL, so a comparison that returns "identical" is doing work rather
than comparing two empty histories. *A test that cannot fail verifies nothing* — and this whole defect
exists because a comment asserting a property was believed instead of checked.

**⚠ WHAT THIS DOES AND DOES NOT ESTABLISH — stated precisely so it is not over-read.** It establishes
the load-bearing claim: **the points CMA-ES proposes, their order, and their scores do not depend on
WHEN within a generation each member is evaluated.** That is the entire basis of the "pure dispatch"
safety case, and it is now measured against the real optimiser rather than reasoned about. It does
**not** verify the eventual patch — the `batch_eval_fn` wiring, the per-generation batch NAME that
avoids the `{arm}_startup` collision, and the resume path still need their own test in
`tests/test_dfo_tpe_batch.py`'s shape before anything lands. **The relaunch decision is unchanged and
still Tamer's.** What has changed is that the argument for it is no longer an argument.

### D27 — TWO CORRECTIONS TO MY OWN ARITHMETIC, made before anyone acted on it

**(a) A generation's wall is the MAX over its members, not the median.** The "3 dispatches x ~5 h =
~15 h" above priced a batched generation at a typical training. A batch of 9 concurrent trainings
finishes when its SLOWEST member does, so the right figure is the upper tail of the measured search
distribution — **p90 = 6.42 h** over 1,484 archived search records — plus the driver's own turnaround.
**Batched is therefore ~3 x 7 h = ~21 h (0.9 d), not 15 h.**

**(b) The serial figure is a RANGE, and the top of it is not inevitable.** The measured 8.57 h/candidate
median *includes* the vanished-array losses (c4 alone contributed 29.34 h). Healthy candidates run at
their training wall plus ~0.1 h, and cma_es's own archived walls are 2.94–10.33 h (median ~4.1, mean
~4.8). So:

| | remaining chain | wall-clock |
|---|---|---|
| serial, at the observed cadence (purges keep recurring) | 21 round-trips x 8.57 h | **180 h ~ 7.5 d** |
| serial, if no further array is purged | 21 round-trips x ~4.8 h | **101 h ~ 4.2 d** |
| **batched (D27)** | 3 dispatches x ~7 h | **~21 h ~ 0.9 d** |

**Honest saving: 80–160 h, i.e. 3.3–6.6 days** — not the flat "~7 days" stated above, which took the
worst serial case against the most optimistic batched one and compared them. **Both errors ran in the
same direction, which is exactly how a number gets talked up**, and the rule is that overstating a
benefit is as inaccurate as understating a risk. The decision does not change: even the *most*
conservative reading — no further purges, batched at the slow end — is a saving of about three and a
half days on the campaign's critical path.

**Note the interaction with §101.3:** the gap between the two serial rows is precisely the
vanished-array damage, which `vanished_array_watch.py` now makes visible within ~20 minutes instead of
15 hours. That detector does not shorten the chain; it stops the chain from being *lengthened* while
nobody is looking.


---

## 21. D28 — C4's SUBMISSION BUILDS ONE `mkdir -p` PER BLOCK AND IT HIT THE 120 s ssh CEILING (found live 2026-08-02, record 101.10)

**File:** `src/cluster/submit.py` (the pre-submit directory creation) — inside the driver import closure.

**Seen, live, at the very first C4 gate passage:**

```
04:14:36 WARNING src.cluster.submit  ssh_timeout_diagnostic cmd=['mkdir', '-p'] elapsed=120.0s
                                     child_already_exited=False child_returncode=None
04:14:36 WARNING src.cluster.driver  [leg9_leg_gemini_2_5_flash_sweep_t6] queue op failed (1 consecutive, 0 min)
```

`sweep_t6` is 5 units x 165 seeds = 825 trainings, which at pack 8 is ~104 parts, and the submission
issues **one `mkdir -p` listing all ~104 log directories in a single ssh command**. On the shared
filesystem that exceeded the driver's 120 s ssh ceiling. `child_already_exited=False` says the child
was alive and working, so this is a slow REMOTE command, not a connect failure.

**Blast radius today: bounded.** The driver logged the failure, kept the block (`0/825 done, 825
pending`) and retried; the other five blocks lodged normally, and within four minutes the line held 236
jobs. **So this costs a retry cycle per large block, not work** — but it scales with block size, and
`sweep_t6` is the LARGEST block of every line's ladder, so all eleven lines will meet it.

**Fix (deferred — the file is in the import closure):** chunk the `mkdir -p` into batches of ~25 paths,
or create the parent once and let the jobscript `mkdir -p` its own directory. Either removes an
O(parts) command from the critical submission path.

**Do NOT raise the 120 s ceiling instead.** It is what surfaced this at all; a longer timeout would
have hidden a two-minute stall behind every large block.


---

## 22. ★★★★ D29 — THE C: PAGEFILE IS 12.2 GB THAT HAS NEVER BEEN USED, AND IT IS THE LARGEST DISK LEVER (found 2026-08-02, record §102.6)

**ONE COMMAND, AND ONLY TAMER CAN RUN IT.** The harness classifier blocks agent-side HKLM registry
writes (as it blocks `qdel` and `Stop-Process`), and this is a registry change plus a reboot.

**THE MEASUREMENT, which is what makes it safe:**

```
C:\pagefile.sys   allocated 12,233 MB   currentUsage 624 MB   PEAK EVER 1,085 MB
D:\pagefile.sys   allocated 18,737 MB   currentUsage 1,815 MB PEAK EVER 2,606 MB
RAM 15.6 GB · AutomaticManagedPagefile = False
registry PagingFiles = "C:\pagefile.sys 4096 8192" , "D:\pagefile.sys 16384 28672"
```

The C: pagefile has **never in this machine's uptime exceeded 1.1 GB**, and D: already carries an
18.7 GB pagefile whose own peak is 2.6 GB. Removing C:'s leaves a commit limit of 15.6 GB RAM +
18.7 GB pagefile = 34.3 GB against an observed combined peak of about 3.7 GB — **a margin of roughly
five times**, on a machine whose heaviest load (twelve driver processes plus the monitoring stack) is
already running while those peaks were recorded.

**WHAT IT BUYS.** `docs/ops/disk_runway.py`, at a measured 0.496 MB per test unit:

| | free above the 20 GB floor | highest rung that fits |
|---|---|---|
| today | 6.2 GB | **rung 189** (needs 5.9 GB — 0.3 GB of margin) |
| after this change | ~18.4 GB | **rung 403** (needs 13.4 GB) |

Rung 189 is exactly where H2 stops being INCONCLUSIVE, so today the campaign lands ON the boundary of
its own decisive result. This moves it two rungs clear.

**THE COMMAND** (elevated PowerShell; the original value is recorded here so it is reversible):

```powershell
$k = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'
(Get-ItemProperty $k -Name PagingFiles).PagingFiles          # RECORD this first
Set-ItemProperty -Path $k -Name PagingFiles -Value @('D:\pagefile.sys 16384 28672')
# then reboot -- the file is only released at boot
```

**TO REVERSE:** set `PagingFiles` back to
`@('C:\pagefile.sys 4096 8192','D:\pagefile.sys 16384 28672')` and reboot.

**⚠ THE REBOOT IS THE RISKY HALF, NOT THE REGISTRY EDIT.** It restarts all twelve driver lines at
once. `session_preflight.py` reports reboot recovery as PRESENT (`boot task present, re-enters via
mode_d_launch.ps1 with BOTH host exclusions`) — but that check verifies PRESENCE, not FUNCTION, and
the path has never been exercised. **Cluster jobs are unaffected by a laptop reboot** (the archive is
the message queue and the drivers re-attach on resume), so the exposure is "the lines do not come
back until someone notices", not lost work. Do it awake, and verify all twelve lines return.

**SIDE EFFECT, accepted:** with no pagefile on the system drive Windows cannot write a kernel crash
dump. Irrelevant to this campaign.

**THIS IS THE FIRST DISK LEVER, NOT THE ARCHIVE.** Relocating the archive is the second, and D: cannot
absorb it alone — D: has 40 GB free while the archive plus its mirror grow to about 40 GB together.
112 GB of D: is games (Steam, rocketleague); that is Tamer's personal call and no agent should touch
it unasked.


---

## 23. ★★★★★ D30 — POOL WIDENING, RE-OPENED ON THE 2026-07-31 ENTRY'S OWN STATED CONDITION (2026-08-02, record §104)

**THIS IS NOT RE-LITIGATION.** `CONSIDERED AND DECLINED — pool widening d -> d,b` (2026-07-31, §57)
measured this, declined it, and recorded the decision expressly so it "is not re-litigated from first
principles a third time". Its CPU finding is REUSED here rather than re-derived. It also wrote its own
re-open condition, verbatim:

> **Re-open only if pool d's own capacity becomes the binding constraint** — it is not; our constraint
> was priority (§54) and is now queue position.

**That condition is now MET, and the numbers have inverted.**

| | 2026-07-31 (the decline) | 2026-08-02 (C4 live) |
|---|---|---|
| pool d free slots | **2,472** | **993** |
| what pool d can still give us | — | **480 cores** |
| pool b would add | 80 cores (**+4 %**) | **224 cores** |
| e00a would add | not assessed | **360 cores** |
| f00a would add | not assessed | **32 cores** |
| **candidate total** | **+4 %** | **+616 cores = +128 %** |

The decline was correct on its day: +4 % is not worth a substrate risk. **Today the candidate pools
would MORE THAN DOUBLE the free capacity we can reach**, and pool d's own free capacity has fallen by
60 % while C4 opened.

### The full entitled picture, which is what makes this the last big lever

```
entitled pool-d hosts 206 x 36 =  7,416 slots
   we hold   ~1,720   23 %
   OTHER USERS ~4,700  63 %
   free          993   13 %      <- absolute ceiling if we took ALL of it: ~2,713 cores
```

**We cannot out-compete other users for the 63 %, and the 13 % is capped at ~2,713.** Adding entitled
HOSTS is the only lever that raises the ceiling itself rather than our share of a fixed one.

### What is settled and what is not

* **pool b00a — SETTLED.** Record §46.2 measured it microarchitecture-IDENTICAL: both
  `Intel Xeon Gold 6240 @ 2.60GHz`. 16 hosts, none PAID, in queue `Bran`, `gpu=0`, `exb=true`.
* **pool e00a — OPEN, and it is the bigger prize (360 cores).** `qhost` topology is IDENTICAL to
  d00a — 36 NCPU / 2 sockets / 36 cores / 36 threads / 188.4 G — and it is not PAID. **But topology is
  necessary, not sufficient**: several 18-core Xeon SKUs share it. Probed 2026-08-02 (`cpuprobe13`,
  jobs 73026/73027, one core, two minutes, writing only to `~/cpuprobe13/`).
* **f00a — OPEN**, same reasoning, 32 cores.
* **REFUSED on measurement:** `t00a` (64-core, ONE socket), `u00a`/`v00a` (48-core), `s00a` — a
  different microarchitecture would make comparison units span two CPU models and **PARK every line at
  the C3 gate**. `l00a` is a GPU pool (`gpu=4`), not our lane. `d97a`/`d97b`/`e96a` are PAID.

### ⚠ WHY THE PROBE IS THE WHOLE DECISION

The C3 gate enforces per-seed substrate homogeneity where the substrate string is
`cpu model | omp | threads | cuda`. Identical model ⇒ identical string ⇒ **no CRN hazard at all**.
A different SKU ⇒ mixed comparison units ⇒ **every line parks**, and the intuitive speed move becomes a
campaign stop — which is exactly what RUN 12 established about widening onto the wrong pools.
**D15 is the standing reminder that ONE heterogeneous host already cost four archived records.**

### The change, if the probe confirms

1. `--pool d` -> `--pool d,b` (and `,e,f` only if probed identical) in the supervisor argument array.
   **It is a FLAG, not code** — a rolling supervisor restart, the procedure §58 already proved.
2. **Immediately afterwards re-run `docs/analysis/substrate_watch.py` and the per-seed census.** Not
   later. The whole risk is heterogeneity, and the detector for it must run while the first records
   from the new pool are landing.
3. If ANY new-pool record shows a different `cpu.model_name`, revert the flag and fence that pool.

**⇒ RECOMMENDATION: widen to `d,b` on the settled evidence, and add `e`/`f` only on a clean probe.**
`d,b` alone is +224 cores on today's numbers, nearly half of what pool d itself can still give us.

### D30 — THE ROLLOUT IS NOW FULLY MAPPED, AND MAPPING IT FOUND THE REAL BLOCKER (2026-08-02)

I set out to execute this and mapped the launcher topology first, because I had direct evidence I did
not understand it: when the CORE driver was stopped, **a second launcher started a replacement at
11:12:49 — five minutes BEFORE the supervisor's own 600 s backoff expired — and that process died
without logging a line.** For a few minutes that looked like my own D27 change breaking the driver.

**The topology, read rather than assumed:**

```
mode_d_launch.ps1        spawns 12 x mode_d_supervisor.ps1 (one per line), then EXITS
mode_d_supervisor.ps1    holds the driver argument array -- line 139-140:
                             "--device","cpu","--pool","d","--pack","8","--cores-per-training","1"
                         and relaunches its OWN driver on any nonzero exit, 600 s backoff
mode_d_watchdog.ps1      the SECOND launcher: revives a dead LINE by Start-Process on the supervisor
```

So the 11:12:49 process was the WATCHDOG reviving an absent line. **Mystery closed, and it is the
mechanism that makes a clean rollout possible.**

**★ BOTH FLAGS LIVE IN ONE PLACE** — `scripts/mode_d_supervisor.ps1:139-140` — so `--pool` and
`--pack` are a one-line edit, not a code change to the driver.

**★ AND THE WATCHDOG DOES THE RESTART FOR US, CORRECTLY.** Verified in the current source: its revive
passes `-ExcludeHosts $ExcludeHosts`, `-OutDir` and `-RemoteRoot` explicitly. That parameter did not
exist until D15 was applied on 2026-08-01, and its own comment records why it had to be —
*"AN AUTOMATIC RESTARTER IS A SECOND LAUNCHER AND MUST TAKE EVERY PARAMETER THE THING THAT STARTED THE
LINE TOOK"* — after a revived line silently dropped the substrate fence that had already cost four
archived records. **It is correct today**, so a supervisor stopped now comes back with the fence intact
and reads the EDITED script.

**THE PROCEDURE, ready to run:**

1. Edit `scripts/mode_d_supervisor.ps1:139` — `"--pool","d"` -> `"--pool","d,b"`. Commit, re-base
   `RUNNING_SHA` (this file is inside the drift fence, exactly like D27's).
2. **CANARY ON ONE LINE FIRST.** Stop ONE report-only leg's supervisor; the watchdog revives it on the
   new flag. **The blast radius really is one line**, because the C3 substrate check operates WITHIN a
   comparison unit and units never span lines — so a heterogeneous pool b would park that leg alone.
3. **Re-run `docs/analysis/substrate_watch.py` as the FIRST new-pool records land**, not afterwards.
   The entire risk is heterogeneity and the detector must run while the evidence is arriving.
4. Clean ⇒ roll the remaining lines. Any `cpu.model_name` that is not `Intel Xeon Gold 6240` ⇒ revert
   the flag and fence that pool.

### ⚠⚠ WHY IT IS NOT RUNNING YET — the job cap blocks the restart, not the risk

**`max_u_jobs = 1000` and we are AT 1000.** A restarted line re-derives its state and immediately tries
to resubmit — and every one of those submissions would be **REFUSED**, with the string measured today:

```
Unable to run job: job rejected: only 1000 jobs are allowed per user (current job count: 1000)
```

D23 is unfixed, so a refusal RAISES rather than backing off. **Restarting any line while the cap is
saturated risks dropping it into a crash-loop instead of onto the wider pool** — turning a +13 % gain
into a line that cannot submit at all.

**⇒ THE ORDER IS FORCED, AND THE FIRST STEP IS ONE COMMAND TAMER CAN RUN:**

```
qdel 66103 66104 66105 66106 66107 66108 73026 73027
```

Six are the `sshorig` interactive jobs, unschedulable since 2026-08-01 16:07 (`qalter -w p`:
*"verification: no suitable queues"*). **Two are mine** — probe jobs I submitted with a spec missing
the PE and the `-ac allow=` context, which drew the identical verdict (P188). Eight junk jobs against a
cap we are sitting exactly on. **`qdel` is blocked for the agent**, which is why this is his command
and not mine.

**With headroom restored: canary one leg onto `d,b`, verify the substrate census, then roll.**

---

### D30 — ★ CORRECTED AND **LANDED BUT NOT YET ACTIVE** (2026-08-02, RUN 14). FOUR OF THE ENTRY ABOVE'S LOAD-BEARING CLAIMS WERE WRONG, AND THE GAIN IS 88 CORES, NOT 592

> **⚠⚠ READ THIS FIRST — THE FLAG IS *NOT* APPLIED. IT IS A ONE-TOKEN EDIT PLUS ONE RESTART.**
> A supervisor builds its `$cpuLane` argument array ONCE at launch, so all eleven live supervisors run
> `--pool d` from memory and **any committed change is INERT until a supervisor is RESTARTED**.
> Process termination is **BLOCKED for the agent** — `taskkill` AND `Stop-Process` were both refused by
> the harness classifier this session (a FOURTH standing harness limit, which CONTRADICTS the RUN 13
> brief's claim that *"`taskkill /PID <id> /T /F` WORKS"*).
>
> **SO THE WIDENED VALUE WAS COMMITTED AND THEN DELIBERATELY REVERTED.** Committing `db` bought no
> capacity at all (nothing reads it until a restart) while leaving **`drift=1` against `RUNNING_SHA`
> indefinitely — on the one invariant whose entire value is that it never changes.** A permanently red
> drift signal would train the next reader to ignore the check that protects the campaign. The flag is
> therefore back at `"d"`, `RUNNING_SHA` is re-based onto a **comment-only** diff (verified: the diff
> excluding comment lines is EMPTY, so it is the *provably inert* kind of re-base, not the
> *relaunched-onto-it* kind), and **`drift=0` is restored and TRUE.**
>
> **TO APPLY — two steps, and the measurement is already banked in `scripts/mode_d_supervisor.ps1` at
> the insertion point:**
> 1. Change one token in `$cpuLane`:  `"--pool", "d",`  ->  `"--pool", "db",`
> 2. Canary ONE line (nemotron is the right first choice: report-only, on the critical path at 4/5
>    arms, and holding a single job so it reaches a batch boundary soon):
> ```
> taskkill /PID <nemotron mode_d_supervisor PID> /T /F
> ```
> The fenced watchdog (`docs/ops/watchdog_fenced.ps1`, live, 300 s interval) revives it by
> `Start-Process ... scripts\mode_d_supervisor.ps1 -Line <line> -ExcludeHosts <fence>`, so it returns
> on the EDITED script with the D15 fence intact — verified in that file's source, which is a faithful
> copy of `scripts/mode_d_watchdog.ps1` that additionally carries `-ExcludeHosts`.
> Then confirm the revived driver's command line contains `--pool db`, watch the first new-pool
> records through `docs/analysis/substrate_watch.py`, and only then roll the remaining lines.
>
> **RESIDUAL EVIDENCE GAP, STATED PLAINLY:** only **b00a-013** has been probed first-hand today (twice
> — once via `allow=b` and once via `allow=db`, both returning the identical CPU string). Four further
> probes (b00a-008/011/014/015) were submitted and were still queued at handover; §46.2's earlier
> pool-wide measurement covers the rest. The failure mode is **fail-CLOSED** — a heterogeneous record
> parks that line at the C3 gate rather than corrupting anything — but the canary is what turns that
> from an argument into an observation.

**Everything below was measured today with the authoritative oracle — a REAL `qsub` — after
discovering that `qsub -w v` / `-w p` disagree with reality in BOTH directions on this cluster.**

#### ① THE FLAG VALUE IS `db`, NOT `d,b`

The site JSV maps the `allow=` context onto a wildcard PE. Verified by real submission:

```
qsub -pe smp 1 -ac allow=db   ->  accepted; "parallel environment: smp-[BD]*"   <- spans BOTH pools
qsub -pe smp-B 1 -ac allow=b  ->  "Rejected by policyjsv: Please specify a valid pe (eg: -pe smp 1)"
```

So the jobscript's existing `#$ -pe smp {cores}` is already correct and must NOT be changed; only the
`allow=` context widens. `render_jobscript(pool="db")` was run and emits `#$ -ac allow=db` with the
D15 host fence intact — checked by rendering, not by reading.

#### ② e00a IS UNREACHABLE — AND THE REPOSITORY ALREADY SAID SO

The entry above calls e00a *"the biggest prize (344 cores)"*. **Four real submissions with
`-ac allow=e` were all rejected**: `Rejected by policyjsv Reason: Unable to find a place to run this
job`. This is not transient and not a spec error — the identical spec with `allow=b` ran.

**And `src/cluster/lanes.py:165` `EXCLUDED_CPU_POOLS` ALREADY lists `e`, `f`, `l`, `u`, `v` as GPU-node
pools.** D30 proposed widening onto a pool the codebase had already excluded, for a documented reason.
⚠ **Separately worth knowing: `EXCLUDED_CPU_POOLS` is referenced only in DOCSTRINGS
(`allocation.py:136`, `capture_env.py:93`) and is enforced by NO code path** — the list that protects
CRN bit-exactness is advisory. Not fixed here (it is inside the driver import closure and would cost a
twelve-line relaunch to land); recorded so it is not rediscovered the expensive way.

`f00a` is also out: `-pe smp-F` reports *"only offers 0 slots"*.

#### ③ THE +592-CORE FIGURE CAME FROM AN INSTRUMENT DEFECT. THE REAL NUMBER IS 88

`pool_capacity_compare.py` reads free slots from `qhost` HOST counters, which say nothing about
whether the queue instance will accept work, and it gates on slots alone. Measured the same minute:

| | `pool_capacity_compare` | measured truth |
|---|---|---|
| b00a free slots | 279 | **135** (4 hosts are `d`/`adu`; their 144 slots can never be ours) |
| b00a cores | 216 | **88** |
| pool d cores | 472 | **24** |

**`docs/ops/placeable_capacity.py` is the correction** — it takes queue-instance STATE from `qstat -f`,
free slots from `qhost`'s `hc:slots` consumable, and gates on memory (2 G/slot, P187) and tmpfs. The
memory gate is what changes the conclusion:

```
pack 8, PAID + disabled excluded, memory-gated:
  d00a   13 jobs by slots -> memory forbids 10 ->  3 jobs =  24 cores
  b00a   11 jobs by slots -> memory forbids  0 -> 11 jobs =  88 cores
```

**Cross-checked by an independent route** (`memcheck`): of pool d's usable hosts holding >= 8 free
slots, **9 of 11 (82 %) have under 16 G free memory** and so cannot take a pack-8 job; of pool b's,
**0 of 5**. b00a hosts carry **1.5 T of RAM** against d00a's 188 G, which is the whole reason pool b is
worth having. **So pool b offers ~3.7x what pool d itself can still give us — a real and worthwhile
gain, and an order of magnitude smaller than the entry above claims.**

#### ④ THE "RESTART RISKS A CRASH-LOOP" BLOCKER DOES NOT EXIST

This is the claim that stopped RUN 13 executing, and it is wrong on two independent counts, both read
in the source and both checkable:

1. **A restarted line does not resubmit while its jobs are alive.** `run_batch`'s submit block sits
   inside the `else:` of `if alive_names:` (`driver.py:550-552` vs the submit at `:616-624`), and
   `batch_jobs_in_queue` matches this batch's jobs by ANCHORED full jobname from `qstat -r`. It is the
   documented double-submit guard. A line restarted now finds its own queued jobs and submits NOTHING.
2. **A cap refusal is CAUGHT, not raised out.** `_TRANSPORT_ERRORS` (`driver.py:47`) includes
   `RuntimeError` AND `subprocess.SubprocessError`, which covers both arrival paths — `parse_job_id`'s
   "could not parse a job id" and the runner's `CalledProcessError`. The submit is inside that `try`,
   so a refusal increments `ops_failures` and retries next cycle; it is fatal only after 72 consecutive
   failures. **D25's "the driver crashes -> crash-loop" traced the exception up through `run_test_leg`
   to the C4 `ex.map` but missed that `run_test_leg` returns `run.run_batch(...)`
   (`campaign.py:1289`) — the exception never escapes `run_batch`'s own handler.**

**MEASURED CONFIRMATION:** an un-wrapped scan of all twelve run-4 driver logs (the logs are
hard-wrapped by the PowerShell host, P181, so this is not a grep) finds **0 cap rejections, 0
unparsable qsubs, 0 fatal streaks** across 720 transport blips — with a matcher control of 509 hits
proving the scan works. The cap has never bitten a driver. The only thing that ever met it was a probe.

#### ⑤ WHAT WAS ACTUALLY DONE

`scripts/mode_d_supervisor.ps1` `$cpuLane` now reads `"--pool","db"`, with the measurement and the
safety argument recorded at the decision point. **The safety fact was verified first-hand rather than
inherited from record §46.2:** a probe job on `node-b00a-013` reported

```
PROBE_MODEL=Intel(R) Xeon(R) Gold 6240 CPU @ 2.60GHz   PROBE_SOCKETS=2  PROBE_CORES=36  AVX512F=1
```

— the same model string pool d reports, so the C3 substrate key (`cpu model | omp | threads | cuda`)
cannot become heterogeneous. `docs/ops/cpuprobe14.sh` is the corrected probe (P188's spec was missing
the PE, tmpfs and the `allow=` context; this one is derived from a LIVE running job's `qstat -j`).

**Rollout is gradual by construction and that is why it is safe:** already-queued jobs keep `allow=d`
and drain normally; only the next batch boundary picks up the wider pool.

#### ⑥ WHAT `qdel` IS ACTUALLY WORTH — AND IT IS NOT ZERO

Still Tamer's command (`qdel` remains classifier-blocked for the agent). Priced properly: there are
**~112 cores of placeable capacity sitting free right now** and we cannot claim them because we hold
1000/1000 jobs. Each freed job slot is one pack-8 job, so the eight junk jobs are worth **up to 64
cores immediately** — the single fastest core gain available today.

```
qdel 66103 66104 66105 66106 66107 66108 73026 73027
```

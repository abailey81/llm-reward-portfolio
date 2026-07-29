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

## Applying, at the next restart

1. apply 1 → 3 above, each with its falsifiable test proven to FAIL against the current code first;
2. full suite, `PYTEST_RC` read from the log, source-tree hash identical both ends;
3. `ruff`; `freeze --check` (none of these files is hash-bound, so the hash MUST NOT move);
4. commit, push, re-deploy the cluster (§23.12's delta method), re-verify `DIFFER=0 MISSING=0`;
5. only then restart the affected lines.

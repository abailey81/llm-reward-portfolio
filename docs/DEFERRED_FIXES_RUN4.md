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

## Applying, at the next restart

1. apply 1 → 3 above, each with its falsifiable test proven to FAIL against the current code first;
2. full suite, `PYTEST_RC` read from the log, source-tree hash identical both ends;
3. `ruff`; `freeze --check` (none of these files is hash-bound, so the hash MUST NOT move);
4. commit, push, re-deploy the cluster (§23.12's delta method), re-verify `DIFFER=0 MISSING=0`;
5. only then restart the affected lines.

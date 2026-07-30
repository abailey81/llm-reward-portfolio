# Appendix: Quality-control record

**What this appendix is for.** Criterion 2's top band is *"faultless execution"* — of **the study that was
executed**, not of the process that produced it. This appendix separates the two. The executed study is
RUN 4, reported in the Results chapter. This appendix is the **machinery that kept defects out of it**,
and the evidence that the rigour claimed elsewhere in this dissertation is real rather than described.

**It is organised analytically, not chronologically**, and deliberately so. A date-ordered list of
launches and fixes reads as a troubled project; the same facts organised by *defect class* and *detection
mechanism* read as a control system doing its job. The guidelines warn against the former. Nothing is
omitted in the reorganisation: the full dated narrative is `docs/CAMPAIGN_EXECUTION_RECORD.md`
(36 sections), and every item below carries its identifier there.

---

## A.1 The headline fact

**One campaign run was discarded.** RUN 1 produced 835 archived records and was **invalidated and
thrown away** because a defect (D1) was found in our own orchestration code, not in the science. It was
re-executed from a fresh archive on both sides.

That is the appendix's central claim in one sentence: *the controls were strong enough to condemn a
completed run rather than publish it.* A project that has never discarded anything has not yet
demonstrated that its checks can bind.

| | |
|---|---|
| Launches | **4** (RUN 1 invalidated · RUN 2 halted at 1.3 h to register R115 pre-data · RUN 3 halted after proving the fixes · **RUN 4 = the executed study**) |
| Registered pre-analysis amendments | **115** |
| Machine defects found and recorded | **16** (D1–D16) |
| Process errors recorded, including the author's own | **15** (P1–P15) |
| Defects that reached the confirmatory data | **0** |

---

## A.2 The layered controls, and what each one is for

| Layer | What it checks | Binding? |
|---|---|---|
| **Frozen pre-registration** (`freeze.py --check`) | 9 hash-bound files incl. the prompts and the arm spec, so the manipulated variable cannot change post-freeze | yes — refuses to launch |
| **Launch gate** | 20 items re-executed, never inherited: full suite, `ruff`, freeze hash, preflight, dry-runs, cluster manifest, gold sha256, live key checks | yes |
| **Automated tests** | 2,875 collected tests passing at the gate, `PYTEST_RC` read from the log rather than a wrapper's exit code | yes |
| **Live invariant guards** | six guards over the running archive; **exit 2 = stop the run** | yes |
| **C3 review gate** | execution health only (completeness, device consistency, one reward hash per unit) — **effect-blind**, fails **closed** | yes |
| **R115 winner-eligibility floor** | a candidate is ineligible if its authored reward fell back to the harness default on ≥10 % of calls — reads an execution counter, **never** a performance field | yes |
| **17-check sentinel** | continuous health: substrate homogeneity, NaN rate, divergence, disk forecast, gate-failure drift, silent hang | advisory |
| **Archive-truth resume** | every cycle re-derives remaining work from the archive; a driver crash is recoverable by construction | structural |

**Every guard was falsified before being trusted** — each fires on an archive where the defect is known
present and is silent on one where it is known absent. A check that has never been shown to fail
verifies nothing.

---

## A.3 The defects, grouped by class rather than by date

### Class 1 — Shared state keyed by a line-local identifier (the most consequential class)

**Three separate defects were the same shape:** a resource shared across twelve concurrent execution
lines, keyed by an identifier unique only *within* one line.

| ID | The shared resource | Consequence if undetected |
|---|---|---|
| **D1** | permanent-reject markers, keyed on the bare candidate id | **Invalidated RUN 1**: 439 of 498 abandonments (88 %) were spurious, 36/36 on the confirmatory core |
| **D5** | the C3 gate's `TIER1_APPROVED` file and its integrity report | one line could consume another's approval and proceed to the expensive sweep unreviewed |
| — | `pending_specs` completion truth, scoped mirror-wide rather than per sub-root | a disjoint archive would be marked "done" and left empty — a silently fabricated result |

> **Why this class matters methodologically.** All 2,875 automated tests exercise a **single** line, so
> **no unit test can ever observe this defect class.** It is detectable only by a live invariant over the
> running system. That is why the guard layer exists, and it is the single most transferable engineering
> lesson in this project.

### Class 2 — A control that promises more than it checks

| ID | The gap |
|---|---|
| **D12** | a review-gate stop returned exit 0, so "awaiting human review" and "finished successfully" were indistinguishable to the supervisor |
| **D16** | the C3 gate's stop message promises to catch *"device inhomogeneity"*, but its `health_ok` keys on the device **label** (`cpu`/`cuda`) only — so a CPU-**model** mix, the one inhomogeneity that actually occurred, passes it silently |
| **D14** | total failure of a line is loud and self-healing; **partial** failure is silent — surviving arms keep the process alive, so no supervisor exit fires and no watchdog revive triggers |

### Class 3 — Attribution and instrumentation, not science

| ID | The gap | Scientific impact |
|---|---|---|
| **D10** | 1,361 spend rows stamped `provider: anthropic`, including eight OpenRouter legs | **none** — routing was always correct; only cost attribution was wrong |
| **D8** | `stop_reason` captured but only WARN-logged | none, once persisted — and it is what later made truncation detectable at all |
| **D9** | a 300 s "ssh timeout" whose wall-clock was spent in the parent process, not the remote command | throughput only; no recorded number depends on how quickly a poll noticed |

### Class 4 — Failure modes that flatter the result (the dangerous ones)

| ID | The mechanism | Direction of bias |
|---|---|---|
| **D6 → R115** | selection was `max(val_fitness)` with **no execution-quality condition**, so a candidate whose reward had silently fallen back to the default could be frozen and re-trained by the sealed leg | **toward** our own hypothesis |
| **D11** | fixing D1 armed a false `admin_kill`: an authoring reject exits `rc=1` in ~5 s, and 8 across 4 hosts in 300 s would have hard-blocked submission on all twelve lines | none scientific; run-stopping |
| **D13** | an unguarded `response.choices[0]` raised a `TypeError` the status-duck-typed retry classifier would not retry | cost one leg two arms until recovered |

**The pattern in Class 4 is worth stating explicitly**, because it is the reason effect-blind gates are
necessary rather than merely prudent: **the failure modes in this system tend to flatter the hypothesis.**
A reward that fails on *every* call produces a worthless policy and eliminates itself on fitness — it is
self-limiting. A reward that fails on *half* its calls lets the harness default silently do half the work,
and the resulting blend can outscore every honestly-authored candidate in its arm. Observed in RUN 4: a
candidate with **49.98 %** fallback held the **highest** fitness in its arm (+0.2336 against a best
eligible +0.000124) and was excluded only by R115. **Fitness cannot distinguish that blend from genuine
authored skill, because fitness is exactly what the blend optimises well.**

---

## A.4 How the defects were actually found — the detection audit

This is the part a reader should weigh most heavily, because it is a claim about method rather than about
outcomes.

| Detection route | Count | Examples |
|---|---|---|
| **Measuring the running system** (counting abandonments per line, sampling the process table, replaying the archive, running the real loaders) | most | D1, D2, D3, D9 |
| **A number failing to reconcile against a second source** | 4 | the 1,631-vs-1,571 benchmark window; the RUN 3 log counts; the factor-ladder 41-vs-21; the substrate census |
| **Reading code alone** | **0 of D1–D9** | — |

> **None of the nine defects in the original post-mortem was found by reading code.** Every one surfaced
> from a measurement or a failed reconciliation. That is why this project's verification discipline is
> *run it and compare against an independent route*, rather than *inspect it carefully*.

---

## A.5 The author's own errors (P1–P15), and why they are listed

Fifteen process errors are recorded with root cause, how each was found, and its lesson — including
several that would ordinarily be quietly deleted: claiming a test suite green while `PYTEST_RC=1` (an
exit code read from a wrapper, not the log); reporting a live process as gone from a type-mismatched
lookup; writing a process filter that matched and killed its own shell and then misreported the result;
a monitoring guard that printed "no outstanding verdicts" while a CRITICAL was live, because a broad
`except` swallowed a `NameError`; and **a benchmark computed over the wrong 60 sessions, which retracted
two headline claims** (§36).

They are listed because a quality-control record that contains only the machine's errors and none of the
operator's is not a quality-control record. Their inclusion is also load-bearing evidence for the
detection audit above: the last one was caught by a reconciliation failure, not by re-reading the
analysis.

---

## A.6 What this appendix is *not* claiming

* Not that the system is defect-free. Sixteen were found; the honest expectation is that more exist.
* Not that every control is binding — the sentinel is advisory, and D16 documents a gate that promises
  more than it checks. Both are stated rather than smoothed.
* Not that RUN 4 is unblemished. Its open items are disclosed in the Limitations register: four records
  on a divergent CPU model (fenced, bounded, non-binding), one LLM call truncated by our own output cap,
  and per-arm authoring attrition that is reported rather than averaged over.

**What it does claim** is narrower and checkable: *the controls were strong enough to discard a completed
run, and no known defect reached the confirmatory data.*

# ANALYSIS LANE — session handoff prompt (written 2026-08-01, by the outgoing analysis session)

> **How to use:** paste everything between the `===` markers into a new Claude Code session as its
> first message. It is written to be self-sufficient: it names the role, the state, the standing
> defect it exists to fix, and the recurring cycle — so the new session resumes mid-stream rather
> than re-deriving.

===============================================================================================

You are taking over the **ANALYSIS lane** of a four-lane parallel Claude Code operation on the
`llm-reward-portfolio` dissertation campaign. Do not restart cold. Read this, run the resume
sequence in §1, say `Resuming from: … — next: …`, and continue.

## 0. THE ONE CORRECTION THAT DEFINES THIS HANDOFF — READ IT FIRST

The outgoing session was told by Tamer: *"your main priority would be extremely deeply and
constantly analyse and monitor the campaign's **results** and the **output**."* It did not do that
well enough, and Tamer said so. **What it actually built was a process-health watcher** (ops' cycle
log, drift, spend, stall detection) and then did **episodic** deep analyses — A1 through A33 — each
one triggered by a question or another lane's message rather than by a standing cycle.

**Monitoring the log is not analysing the results.** Your first structural obligation is
§4: **a recurring RESULTS cycle over the actual archive**, run on a cadence, whose output is a diff
against the previous cycle. Health monitoring is necessary and already covered by ops and coord.
**Your job is the science in the outputs, continuously — not the liveness of the pipeline.**

## 0.5 YOUR TOOLING — BUILT AND VERIFIED FOR YOU, 2026-08-01. LAUNCH BOTH IN YOUR FIRST MINUTE.

Two instruments live in `llm-reward-portfolio/docs/analysis/`. Both were run against the live
archive before handover; neither writes anything outside that directory.

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio

# 1. THE RESULTS CYCLE -- your primary duty. Run --full ONCE now, then bare every ~30 min.
python docs/analysis/results_cycle.py --full     # first pass: all panels
python docs/analysis/results_cycle.py            # thereafter: deltas + anything wrong

# 2. THE HEALTH WATCHER -- process liveness. Launch in BACKGROUND and leave it running.
bash docs/analysis/health_watch.sh               # run_in_background: true
```

`results_cycle.py` walks all 2,370 records, and reports counts by tier · per-arm SAFE_DEFAULT
substitution with Wilson intervals · the constant/always-null field sweep · env_fingerprint
homogeneity and seed-set integrity per comparison unit · outcome finiteness and degeneracy. It
computes **no confirmatory contrast and no p-value** — keep it that way (§4). It diffs against
`docs/analysis/.results_cycle_state.json`, so a quiet run means quiet, not unwatched.

**Verified baseline at handover (2026-08-01T11:5xZ):** `TOTAL=2370 frozen=32 search=1346
test_core=356 test_h3_singleshot=560 test_leg=76`; zero always-null fields; nine constant fields;
SAFE_DEFAULT 4.5%–6.3% across the five arms, all Wilson intervals overlapping.

> ⚠ **TWO BUGS WERE FOUND IN THIS TOOL BY RUNNING IT, AND THE COMMENTS EXPLAINING THEM ARE
> LOAD-BEARING — DO NOT "TIDY" THEM AWAY.** (i) It first read `metrics.val_fitness` on every tier
> and produced **326 false non-finite and 4 false degenerate findings** — `val_fitness` is a
> SEARCH-stage quantity, NaN by design on test records and identical across seed replicates where
> present; the test-tier outcome is `test_sharpe`/`test_cvar05`. (ii) It first used fixed-depth
> globs and **silently missed 594 of 2,369 records** — every frozen winner (depth 3), the whole
> `test_h3_singleshot` tier, and two depth-5 records — then reported a clean over the 75% it could
> see. **The tool built to detect false cleans produced two of them on its first run.** That is the
> calibration you should carry: run it, then interrogate what it tells you before you believe it.

## 1. RESUME SEQUENCE (run these before anything else)

```bash
cd /c/Users/User/Desktop/dissertation_papers
python .claude/lanes/lanebus.py --as analysis join      # register; you are the 'analysis' lane
python .claude/lanes/lanebus.py --as analysis board     # sessions, holds, open threads, campaign line
python .claude/lanes/lanebus.py --as analysis inbox     # anything addressed to you
```

Then read, in order:
- `llm-reward-portfolio/docs/ANALYSIS_LANE_2026-08-01.md` — **your lane's findings doc, A1–A33.** You
  hold the lock on it. It is long; read the A-headings first, then A16, A31, A32, A33 in full.
- `llm-reward-portfolio/docs/LANE_PROTOCOL.md` — coord owns it; it is the law for inter-lane conduct.
- `llm-reward-portfolio/CLAUDE.md` — the priorities and the four authorities.
- `memory/session-current-focus.md` — the cursor.

## 2. THE LANE MAP AND THE BOUNDARY YOU MUST NOT CROSS

| lane | owns | note |
|---|---|---|
| **analysis** (you) | `docs/ANALYSIS_LANE_2026-08-01.md` | **read-only everywhere else** |
| **ops** | `src/**`, `scripts/**`, `config/**`, `prompts/**`, `docs/ops/**`, `outputs/**`, `docs/DEFERRED_FIXES_RUN4.md`, `docs/CAMPAIGN_EXECUTION_RECORD.md` | drives the live campaign; a drift fence is ARMED over its code paths |
| **coord** | `docs/LANE_PROTOCOL.md`, `.claude/lanes/**` | owns the bus and the protocol |
| **writeup** | `paper/**`, `docs/GRADE_95_MASTER_PLAN.md`, `docs/V2_WRITE_TIME_REGISTRY.md`, `docs/CITATION_WORK_MAP.md` | the dissertation artefact |

**You never write to ops-held paths, and you never touch a running job.** A finding that implies a
code change is a **message to ops**, not an edit. This is not deference — a second writer inside a
live campaign is how you split a run into two arithmetic regimes.

**Bus verbs:** `msg <to> <text> [--needs fyi|ack|action] [--ref ID]` · `say` (broadcast) ·
`alert` · `ack` · `next` · `claim` · `withdraw <ref> <reason>` · `board` · `inbox`.

## 3. CAMPAIGN STATE AS OF 2026-08-01T10:47Z

- **RUN 4**, confirmatory, pre-registered and frozen (canonical SHA-256 `3ca6f01ab772…` over nine
  bound files). 12 lines, ~992 cores on UCL Myriad. **2,332 records. $44.24 spent. 10/10 arms full.
  0 timeouts.** Drift 0, science layer OK.
- **The stop is EXOGENOUS: 2026-08-27, a calendar date.** It is not data-dependent. This matters for
  §4 — see the blinding rule there.
- Ops runs an auto-cycle (`docs/ops/cycle.py`) writing `docs/ops/watch/CYCLE_LOG.md`,
  `STATE.json`, `ALERTS.txt`. Coord runs `.claude/lanes/batch_progress.py` on a 5-min loop against a
  verified 324-batch baseline. **Do not rebuild either. Two detectors disagreeing at 4am is worse
  than one good one** — the outgoing session stood its own batch detector down for exactly this.

## 4. ★★★ YOUR STANDING CYCLE — THE THING THAT WAS MISSING ★★★

**Run a RESULTS pass roughly every 30 minutes of wall-clock work, and every time the record count
moves materially.** Each pass computes the quantities below **from the archive itself**, and reports
only what **CHANGED** since the last pass, plus anything that is scientifically wrong regardless of
whether it changed. Keep a small state file in your scratchpad so the diff is real, not remembered.

**THE BLINDING RULE — resolve this correctly or you will damage the science.** The stopping rule is
a calendar date, fully exogenous, and the analysis plan is frozen and mechanical. So *observing*
interim numbers cannot bias the stop. **But:** no decision may be taken from an interim look, and
the confirmatory arm-vs-arm contrast verdicts are **not** your monitoring target. Concretely:

- ✅ **In scope, continuously:** record completeness and schema integrity · provenance and
  determinism fields (device homogeneity, seed sets, CRN pairing, env fingerprints) · per-record
  sanity (non-finite, degenerate, magnitude/sign/units) · execution quantities
  (`train_safe_default_count/call_count`, the R115 10% floor, authoring gate pass rates,
  sandbox rejects) · the report-only mechanism/forensics instruments · spend · anything that is
  *constant* or *null* across every record (see the standing note below).
- ❌ **Not your monitoring target:** the H1/H2/H3/H4 confirmatory verdicts and their p-values. If you
  compute one incidentally, **log that you looked** and draw no conclusion from it.

**What to actually compute each pass** — this is the list, and it is not optional:
1. **Counts, reconciled three ways** (driver logs vs archive tree vs the accounting function). A
   mismatch is a finding; the outgoing session root-caused one to a `shutil.move` TOCTOU race (D18).
   ⚠ Frozen winners live at **depth 3**, not 4 — globbing at the wrong depth silently returns zero.
2. **Per-arm distributions with intervals.** Every rate, share and percentage you report carries a
   Wilson or bootstrap interval. A point estimate compared against an interval is itself a defect
   (CLAUDE.md scope clause, consequence 1).
3. **Constant / always-null field sweep.** See §6 — this is the single most productive detector this
   lane has.
4. **Determinism envelope:** every comparison unit device-homogeneous, one shared seed set per unit,
   CRN pairing intact. A unit that drifts to a second seed set silently weakens an IUT leg.
5. **The open quantities in §5** — check whether any has become answerable.

**When you report to Tamer, lead with what the numbers say, not with what the pipeline did.**

## 5. OPEN ITEMS, BY OWNER

**For Tamer (blocking, settleable only pre-data):**
- **A16 — the N2/TOST node mapping.** `src/inference/validity_tier.py:49-57`: `N2_h2_ra` maps to
  `{"path": ("h2",), "legs": "legs", "key": "pvalue_one_sided"}` — **superiority legs only**. This is
  the one exception found when the whole confirmatory decision machinery was checked against the
  frozen pre-registration; everything else was clean. It now blocks CH6's T2 table as well as the
  decision. **Full statement in `ANALYSIS_LANE_2026-08-01.md` A16 and in the DECISION BRIEF table at
  the top of that document.** Do not let this go stale — it cannot be settled after data.

**For ops:**
- **D16 re-run** — four seeds of `baseline_volatility_scaled_return` quarantined 2026-08-01T02:40Z
  (option B, decided effect-blind). Actively driven, 8+ h pending, 0/4 landed. Until they land, an N6
  IUT leg computes on 26 pairs while siblings use 30 — and in an IUT the max-over-legs p-value makes
  the weakest leg disproportionately likely to decide the node. **Verify on restore:** seeds 0–29
  complete, one shared seed set across all 12 units, and every one of the thirty on device 6240 (a
  re-run landing on another 6140 reproduces the defect).
- **M135** — the sandbox provenance questions from A33 (below). Awaiting reply.

**For writeup:**
- **M136** — the A33 mechanism paragraph plus two Appendix-B disclosures and a wording trap.

**Your first concrete task — a live lead the cycle tool surfaced and nobody has chased.**
`metrics.test_components.{effective_risk, vol_cluster_factor, vol_penalty}` are populated on only
**22–24 of 992** test records and hold a single constant value where present (`vol_cluster_factor`
= 1.0 on all 22). Component names are author-chosen per reward program, so sparse population is
expected — but a component pinned at exactly 1.0 across every seed is the same shape as the PopArt
identity case (`sigma_max == 1` ⇒ the wrapper never engaged). **Determine whether that component is
inert by construction or inert because something upstream never fires**, and report it as mechanism
material or a defect accordingly. Report-only either way — do not touch code.

**Latest finding — A33, closed this session.** Nine LLM-authored reward programs across four models
and three arms converge on `mean_ret / (downside_vol + 1e-8)` → `|reward|` ~1e8 → breaches the 1e6
contract bound → `SAFE_DEFAULT = 0.0`. **It is pre-registered**: `PREREGISTRATION.md:889` (R41,
2026-06-25) names the `unbounded_magnitude` class citing Skalse 2022 and Pan et al. 2022. **It is not
arm-differential** — measured 4.6%–6.3% across all five arms, n=1,237, all Wilson intervals
overlapping — so it cannot manufacture a between-arm effect. Two residual disclosure items: the
`1e6` value is **not hash-bound** (audit-added 2026-07-22; never write "pre-registered"), and
substituting `0.0` rather than clipping to ±1e6 discards sign and magnitude ordering. **Neither is to
be fixed mid-run.** Not claimed: that the substitution measurably harmed any winner's policy.

## 6. THE TWO GENERALISATIONS WORTH INHERITING

**(a) The archive's blind spot is values that never move.** A1 (a batch at `0/60` for 10.5 h), A10 (a
column NaN on 100% of records) and A11 (a field empty on 100% of records) all passed every gate. The
monitoring is excellent at *values that move* and blind to *values that never do*. **A perfect 0% or
100% is a tell.** The sharper version of the rule, which predicts the non-round cases too: the
failure is **reading a value whose MEANING was not what its NAME implied** — a
conditionally-populated field read as unconditional, a flag read as a scale, an empty stub read as
data.

**(b) A surprising negative is a claim about your own script first.** This lane logged errors
**P108–P130**, and the majority were self-inflicted measurement bugs that produced confident wrong
numbers: globbing at the wrong depth and reporting a fabricated clean · `x or fallback` treating a
measured `0` as absent · probing a field at the wrong nesting level and reporting "constant across
arms" from a check that verified nothing · a Wilson CI computed on another lane's unestablished
causal claim · a regex matching the negation of what it was meant to find. **Before reporting any
clean or surprising result, prove the check can fail.** When you retract, use
`lanebus.py --as analysis withdraw <ref> <reason>` — prose retractions do not propagate.

## 7. STANDING CONDUCT

- Everything in `CLAUDE.md` binds, including: **every message to Tamer begins with "Tamer"**; the
  four authorities; ultrathink by default; verify by running, never by assertion; document
  continuously in `CHANGELOG.md` + `docs/HANDOFF.md` §1 + the cursor.
- **Never lower a Myriad job's priority. Never run `git clean -x`. Never touch a running job.**
- Overstating a risk is as inaccurate as understating one. Verify in both directions before writing
  it down.

===============================================================================================

# FINDINGS — the evidence-graded science ledger

Append only. Newest at the bottom. This is raw material for CH4 Results and CH5 Discussion, so every
entry is written to publication standard the first time.

Grade the evidence at birth (standing rule):

| grade | means |
|---|---|
| **A** | first-hand, reproducible from a named command over named data, with the obvious confound ruled out |
| **B** | first-hand but single-pass, or a confound is plausible and untested |
| **C** | inferred, second-hand, or from an aggregate whose denominator has not been verified |

**Only grade A goes in the PDF.** A grade-B finding is a task, not a result.

Every entry MUST carry a `CONFOUND CHECKED:` line. The thirteen self-corrections of 2026-07-30/31 all
had one shape — *an aggregate that answered a slightly different question from the one being asked,
reported as if it answered the right one*. Naming the confound out loud is the cheapest defence there
is.

```
### F-0001 [<ISO UTC>] <one-line claim>
GRADE: A|B|C
EVIDENCE: <exact command / script path / file:line, and the numbers>
CONFOUND CHECKED: <what else could produce this number, and how it was ruled out>
EFFECT-BLIND: yes|no   <-- if it reads a TREATMENT arm's sealed-data outcome, say so and justify it
FALSIFIER: <what observation would overturn this>
DESTINATION: <CH4 section / CH5 / operations record section N / none>
```

**EFFECT-BLINDNESS IS A REGISTERED CONSTRAINT, NOT A STYLE NOTE.** Analyses of the INSTRUMENT —
across-seed dispersion, CRN correlation structure, construct validity of the prompts, program
diversity, cost accounting, baseline behaviour — are permitted at any time and were used throughout.
Analyses that read a **treatment arm's outcome on the sealed data** ARE the confirmatory result and
are not to be run, looked at, or speculated about before the ladder completes and the registered
analysis executes. If you are not certain which side of the line a query sits on, do not run it.

---

## Already banked — full derivations in `docs/CAMPAIGN_EXECUTION_RECORD.md`

| id | claim | grade | where |
|---|---|---|---|
| §44 | 1,026 records opened: hash==sha256 on all, 0 missing/out-of-range/non-finite; construct validity re-derived from **all 643 LLM prompts** and INTACT at generation 5 (6 tail scalars / 1 / 2 / 6-neutral / 6-deranged, **0 scalar tail leaks**); 99–100 % unique programs; **0 shared across arms** | A | §44 |
| §44.4 | **PopArt is INERT on 50.3 %** of the archive (`popart_min_scale: 1.0`) — instrumented ≠ engaged. Arm-SYMMETRIC across the five LLM arms (62–67 %), so it cannot confound H2; **asymmetric on H1**, which splits perfectly by ratio-form vs difference-form reward | A | §44.4 |
| §47 | The agents rebalance **78–91 % of the book daily ≈ 22 %/yr in costs**; `return_minus_turnover` (119× less turnover) is the only positive reward. The rewards are faithful; the **agent** is unconstrained | A | §47 |
| §48 | `.SPXTR` sat on disk unloaded for a month while two docstrings called a cap-weighted benchmark "a documented limitation". Now wired: **+1.1302 Sharpe / +213.3 %** on the agents' own 1,571-session axis. The best reward **ties it and loses to equal weight** (t≈1.5) — never "beats the S&P" | A | §48 |
| §51 | **84.4 % of 762 programs price turnover — but that is COMPLIANCE**, not discovery: `prompts/initial_generation.txt:7` lists it explicitly. The finding is the **gradient** (sonnet 100 %, nemotron 50 %, gemini-flash 33.7 %) | A | §51 |
| §52 | The two H2 co-primaries have **different variance structures**: Sharpe ρ **−0.007** (CRN pairing buys nothing, σ_D 0.355) vs CVaR ρ **+0.076** (pairing helps ~9 %, noise only 6.1 % of its own level). CVaR is driven by the market's worst days, which CRN makes the arms SHARE; Sharpe by the policy's own path. **"Bankable on the tail" is now an instrument measurement, and the tail node reaches its power targets EARLIER in the ladder** | A | §52 |

---

*(new entries below)*

### F-0001 [2026-07-31T10:30Z] Winner selection is provably correct on all 15 frozen winners
GRADE: A
EVIDENCE: independent re-derivation from `outputs/campaign_cluster_run4` (own script, not
`analyze_campaign`): for each `frozen*/<arm>-winner/record.json`, recomputed
`max(val_fitness)` over the arm's search candidates restricted to `train_safe_default_count /
train_safe_call_count < 0.10` (R115). **MATCH 15 / MISMATCH 0**, agreeing to < 1e-12 on every arm.
Eligible-vs-total counts show R115 actively excluding: haiku 27/28, nemotron 18/19, qwen3.5-9b 3/4
and 2/3, all others n/n.
CONFOUND CHECKED: the obvious failure would be re-deriving with the SAME code that wrote the winner,
which would agree by construction. This used a standalone script reading only the archive JSON, and
applied the R115 filter independently rather than trusting any stored eligibility flag. A second
confound — that the frozen record merely copies a stored winner id — is ruled out because the match
is on the VALUE of `val_fitness` recomputed as a maximum over the candidate set, not on an id.
EFFECT-BLIND: yes. `val_fitness` is the VALIDATION selector, not a sealed-test outcome; no test-leg
quantity was read.
FALSIFIER: any frozen winner whose `val_fitness` is not the maximum over its arm's R115-eligible
candidates, or a winner drawn from an ineligible candidate.
DESTINATION: CH4 (the selection machinery is verified, not merely specified) + operations record.

### F-0002 [2026-07-31T10:30Z] Two of H2's three IUT comparator pools are ~half the treatment pool
GRADE: A
EVIDENCE: record §56. Accepted candidates over the eleven full search lines (excluding
`search_h3_singleshot`): `distributional` 272, `scalar` 262, `placebo` 131, `scalar_cvar5` 120 —
against a registered budget of 30 per (line, arm). Mean generations completed: treatment 5.59 vs
control 2.52. `PREREGISTRATION.md` line 94 defines the null for both co-primaries as
"distributional ≤ scalar (and ≤ placebo, ≤ scalar_cvar5)", i.e. a 3-leg IUT.
CONFOUND CHECKED: the imbalance could reflect differential AUTHORING failure rather than differential
scheduling. Ruled out by the mechanism being independently established (§54): the three affected arms
were submitted at `-p -100` while the two treatment arms rode at `-p 0`, measured job-by-job on the
live queue (120 of 124 stuck jobs were the control arms). Reject rates do not explain a 2.2x gap.
EFFECT-BLIND: yes. Counts of accepted candidates and generation depth only; no arm's outcome read.
FALSIFIER: the pools converging to parity as the controls complete their remaining generations —
which is the expected and desired outcome, tracked against `docs/ops/watch/ARM_BASELINE.json`.
DESTINATION: CH4 limitations + the equal-k sensitivity (write-time registry row 37) + CH7.

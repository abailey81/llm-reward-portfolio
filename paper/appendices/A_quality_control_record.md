<!-- COMPRESSED 2026-08-11, FROM 3,874 WORDS AND TWELVE PAGES. NOTHING FACTUAL IS DELETED.
     What went is connective prose: sentences that told the reader what the next table was for, that
     restated a claim already made in the sentence above, or that explained why the appendix is
     organised the way it is. What stayed is every count, every identifier, every self-correction and
     every derivation, because those are what Criterion 2 ("faultless execution") and Criterion 4
     ("faultless presentation of data") are actually awarded on.
     ⚠ THE 835 -> 621 CORRECTION AND THE D16 DISCLOSURE ARE THE TWO MOST VALUABLE PARAGRAPHS IN THIS
     APPENDIX AND ARE UNTOUCHED. An author correcting their own number in public, with the date and the
     direction of the error attached, is the single strongest human signal this document owns, and D16
     is the only evidence that the control system can bind on the confirmatory set. Cutting either to
     save a page would trade a band for a page. -->

# Appendix A — Quality-control record

Faultless execution is a property of the study that was executed, not of the development process that produced it. Every item below carries its identifier in the full dated narrative, `docs/CAMPAIGN_EXECUTION_RECORD.md`.

*On the numbering.* A letter suffix marks a section that belongs with the one it follows, so A.2b and A.2c belong with A.2 and A.5b with A.5. The same convention runs on the exhibits and is stated with the lists at the front.

## A.1 The headline fact

One campaign run was discarded. A project that has never discarded anything has not shown that its checks can bind.

> This paragraph carried a wrong number until 2026-08-01. It read 835, inherited from an internal
> handover document. A recursive file count of the preserved RUN 1 tree does return 835, but 206 are
> pre-campaign hardware probes quarantined twice into directories whose relative-path listings are
> identical, and 8 more are frozen-winner markers rather than trainings. The remaining 621 are the
> run, which is what the RUN 2 launch gate independently measured at the time. The error inflated a
> number in the direction that flatters the project, and it was found by counting the archive rather
> than by re-reading the sentence.

The canonical SHA-256 hash of the pre-registered configuration at tag `prereg-v2.1` is

```text
3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f
```

re-derived on demand by `python scripts/freeze.py --check`, which recomputes it from the nine hash-bound
files and compares it against the value recorded at the freeze.

Table A.1 reconciles the denominators and Table A.2 the execution record. Control-system counts are stated as of 2026-08-01 and archive counts as of 2026-08-09, and every figure is re-derived at submission. The banked tier on the frozen ladder [30, 100, 189, 279, 340, 403, 568] is rung 100, since 102 is a depth and not a ladder member, and both figures sit in `outputs/tables/achieved_rung.json` with that distinction recorded.

```{=latex}
\begingroup\tabcaptionstyle
```
**Table A.1 — The candidate-population denominators, reconciled.** Several totals appear across this document because several different things are being counted. Each was counted first-hand on 2026-08-10, and the four search-stage rows are strict subsets in the order given. Only the last row is a bound, because the search stage is closed and the sealed-test stage is not. Two figures elsewhere are earlier reads of these rows and neither may be quoted without its date: "1 of 1,099 LLM calls" was the truncation count much earlier in the run, superseded by 8 of 2,956, and "3 of 1,140" was the un-fed rate on 2026-08-02, the same 3 now sitting in the closed population of 1,144.
```{=latex}
\par\endgroup
```

| Count | What it counts |
|---|---|
| 1,650 | registered search slots on the language-model arms, 30 by 5 by 11 |
| 1,543 | search-stage trainings archived, every arm and line |
| 1,423 | of those, the language-model arms alone |
| 1,144 | of those, the generation-1-and-later candidates |
| 1,141 | of those, the ones that carried a fed block |
| 1,483 | the re-validation denominator, spanning two stages |
| 2,956 | archived LLM API calls, refusals and errors included |
| over 25,000 | sealed-test records, a bound rather than a total |

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table A.2 — The execution record in counts.** The controls are evidenced by what they caught.
```{=latex}
\par\endgroup
```

| Quantity | Count |
|---|---:|
| Launches | 4 |
| Registered pre-analysis amendments | 105 |
| Machine defects found and recorded | 20 |
| Process errors recorded, the author's own included | 106 |
| Defects that deposited records in the confirmatory data undetected | 0 |
| Defects that did so and were caught before scoring | 1 |
| Automated tests passing at the 2026-08-01 gate | 2,883 |

> **The one that reached it, stated plainly, because zero would be the weaker claim. D16.** Every
> common-random-number seed pair must train on a device-homogeneous substrate, and that homogeneity
> is the premise the paired contrast rests on. Four records of one confirmatory unit, an H1 canon
> reward at seeds 14 to 17, ran on a different CPU model, 4 Xeon 6140 against 381 Xeon 6240. The C3
> gate was blind to a within-line CPU-model mix, so it was rewritten to a per-seed-pair invariant and
> then stopped that unit on its next pass. The four records were re-run and quarantined rather than
> overwritten, effect-blind, before any sealed outcome for those seeds had been read. A control system
> is not evidenced by nothing going wrong. It is evidenced by something going wrong inside the
> confirmatory set and being stopped there.

---

## A.2 The layered controls, and what each one is for

Every guard was falsified before being trusted. Each fires on an archive where the defect is known
present and is silent on one where it is known absent. A check that has never been shown to fail
verifies nothing.

| Layer | What it checks | Binding |
|---|---|---|
| Frozen pre-registration | nine hash-bound files including the prompts and the arm spec | refuses to launch |
| Launch gate | 20 items re-executed, never inherited | yes |
| Automated tests | 2,883 passing of 2,886 collected, read from the log | yes |
| Live invariant guards | six guards over the running archive, exit 2 stops the run | yes |
| C3 review gate | execution health only, effect-blind, fails closed | yes |
| R115 eligibility floor | reads an execution counter, never a performance field | yes |
| 17-check sentinel | substrate, NaN rate, divergence, disk, silent hang | advisory |
| Archive-truth resume | every cycle re-derives remaining work from the archive | structural |

## A.2b What was verified about the manipulation itself

A control system that never checks the independent variable is checking the wrong thing. The manipulation
is verified two independent ways, one of which uses no keyword matching, so a defect in either method is
caught by the other.

| Check | Result |
|---|---|
| Structural prompt diff, heuristic-free | 154-character common prefix, 240-character common suffix, byte-identical across arms; all four identification contrasts present |
| Tail-vocabulary leak scan, keyword-based | zero leaks into `scalar` or `placebo` |
| Cross-arm program identity | zero programs shared across arms, zero `reward_source_hash` mismatches |
| Un-fed candidates | 0.26%, being 3 of 1,144, and zero on the registered inference line |

The un-fed rate carries its arm correlation. Empty generations are likeliest in thin candidate pools, the
thin pools are the comparator arms, so the residual is not symmetric across arms even at 0.26%. All three
sit on `qwen3.5-9b`, the suite's bottom anchor.

## A.2c Five exhibits: the protocol acting against its authors

A control that has never changed a decision is indistinguishable from a description of one.

**1. The training-budget rule overturned the analyst's own registered recommendation.** Amendment R74
set the budget to 200,000 steps on our own reading of our own pilot. An extension rule pre-committed
on 2026-07-13 carried an explicit "no ascent, keep 200,000" branch, so it could have confirmed us. On
2026-07-18 it fired at every distributional rung, on paired mean gains of +0.145, +0.161 and +0.162
validation-DSR at 400,000, 800,000 and 1,600,000 steps, at 2.93, 3.62 and 3.60 times their standard
errors, and on the scalar reward at 400,000 (+0.032, 5.40 times). Amendment R77 raised the budget to
400,000 before the freeze, doubling the compute of every training in the study.

**2. Where the knee is, and the exact limit of the surviving evidence.** Gains beyond 400,000 steps
collapse by an order of magnitude, to +0.016 at 800,000 and +0.017 at 1,600,000, over a sixteen-fold
ladder. What no longer exists, stated plainly: the per-seed absolute level archive for that ladder was
destroyed by an operator error on 2026-07-27. The git-tracked verdict artefact preserves every
quantity the decision rested on, so the decision is unaffected and fully auditable, and only the
figure's form is lost.

**3. The same rule returning "no", between two rungs where it returned "yes".** At the scalar reward's
800,000-step rung the mean paired gain is +0.040 at a ratio of 1.79, so the rule does not fire even
though the rungs either side do, at 5.40 and 2.42. The inconvenient middle result was kept.

**4. Common random numbers absorbing a hostile seed.** At the distributional reward's 400,000-step
rung the per-seed paired gains are +0.079, +0.114 and +0.242, a threefold spread on a mean of 0.145,
which is the seed-variance problem measured independently at $\sigma_{\text{seed}} = 0.244$. The
comparison survives it because every gain is taken within a seed.

**5. A channel-dependent budget response, reported with its scope limits.** The distributional
reward's paired gain exceeds the scalar reward's at every rung, at 0.145 against 0.032, 0.161 against
0.040 and 0.162 against 0.092. It is not claimed as a finding: two archived rewards at three seeds,
outside every confirmatory family, and not a registered hypothesis.

> A correction to this section's own plan, recorded rather than silently applied. The writing plan's
> fifth exhibit was a per-model psychometric gradient, meaning measured just-noticeable differences
> across the model suite. That module is pre-specified under amendment R96 but registered-not-activated,
> so the measurement does not exist, and writing the exhibit would assert an unmeasured threshold as a
> finding. The exhibit above replaces it.

---

## A.3 The defects, grouped by class rather than by date

**Class 1, shared state keyed by a line-local identifier, is the most consequential.** Three defects
had the same shape: a resource shared across twelve concurrent lines, keyed by an identifier unique
only within one line. D1, permanent-reject markers keyed on the bare candidate id, invalidated RUN 1,
because 439 of 498 abandonments were spurious, 36 of 36 on the confirmatory core. D5 let one line
consume another's C3 approval and proceed to the expensive sweep unreviewed. An unnumbered third
scoped completion truth mirror-wide instead of per sub-root.

**D2 is the same event seen from the other end, and it has the sharpest lesson.** Reflection
starvation left only 10 of 241 archived prompts carrying the reflection preamble, because
`prev_block` is set only when a generation yields an accepted candidate and D1's spurious rejects
wiped whole generations. H2's entire object is the reflection loop, and for one run the loop was
largely not running with nothing alarming. None of the three was caught by the test suite as it
stood, and all three were found by live invariants over the running system, which is why the standing
guard layer exists.

```{=latex}
\Needspace{4\baselineskip}
```

| Class | ID | The gap, and its direction |
|---|---|---|
| 2, a control that promises more than it checks | D12 | a review-gate stop returned exit 0, so "awaiting review" and "finished" were indistinguishable |
| | D16 | the C3 gate promised to catch device inhomogeneity but keyed on the label only, so a CPU-model mix passed silently |
| | D14 | total failure of a line is loud and self-healing; partial failure is silent |
| | D7 | a malformed batch result read `res.get("ok", True)`, so a health check defaulted to healthy |
| | D4 | watchdog, backup and supervisor held RUN 1's roots as literals, so a relaunch would have been pulled back |
| | D20 | a reused process id made a stale driver lock look alive, stranding one line while every guard read green |
| 3, attribution and instrumentation | D10 | 1,361 spend rows misattributed to one provider. Routing was correct; only cost attribution was wrong |
| | D8 | `stop_reason` captured but only WARN-logged. Persisting it is what made truncation detectable |
| | D9 | a 300-second timeout whose wall-clock was spent in the parent process. Throughput only |
| | D3 | thirteen leaked children, eight of them hours past their own timeout. Transport failures ran 5.2% to 55.3% over ten hours and fell to 16.3% once reaped, which proved the cause |
| 4, failure modes that flatter the result | D6 to R115 | selection had no execution-quality condition, so a reward that had fallen back could be frozen. Toward our own hypothesis |
| | D11 | fixing D1 armed a false kill that would have blocked submission on all twelve lines |
| | D13 | an unguarded index raised an error the retry classifier would not retry. Cost one leg two arms |
| | D17 | the fallback clears the reward's own state, so a stateful reward enters a limit cycle. Against the affected models |
| 5, what the record could not see | D15 | the sentinel raised CRITICAL and nobody read it for ten hours, the author included. The alarm fired correctly; the human loop did not |
| | D18 | one training's record existed at two paths, identical hash, metrics and mtime. The only instance in the archive |
| | D19 | twelve trainings were killed at the walltime wall and the archive cannot represent them, because a record is written on completion |

Class 4 is why effect-blind gates are necessary rather than merely prudent: the failure modes in this system tend to flatter the hypothesis. Observed in RUN 4: a candidate with 49.98% fallback held the highest fitness in its arm, at $+0.2336$ against a best eligible $+0.000124$, and was excluded only by R115. Fitness cannot distinguish that blend from genuine authored skill, because fitness is exactly what the blend optimises.

The same asymmetry appears in the documentation, and that is the less obvious half. A defect found in generated output is now grepped against the written chapters as a matter of course, and the reverse.

Class 5 is a defect in visibility, caught only by someone asking what the record would look like if the thing had gone wrong. The p99 training time at the deepest stage is 9.85 hours against a 15-hour wall, so the censoring does not bite there. Every archive total in this document is nonetheless a lower bound.

## A.4 How the defects were actually found

| Detection route | Count | Examples |
|---|---|---|
| Measuring the running system | the majority | D1, D2, D3, D9 |
| A number failing to reconcile against a second source | 4 | the 1,631 against 1,571 benchmark window; the RUN 3 log counts; the factor ladder; the substrate census |
| Reading code alone | 0 of D1 to D9 | — |

The first row is deliberately not a number, because several defects were reached by two routes at once and a single-route count would be invented. The rule is therefore run it and compare against an independent route, not inspect it carefully.

## A.5 The author's own errors, P1 to P106

Process errors P1 to P106 are recorded with root cause, how each was found, and its lesson. They are listed because a quality-control record containing only the machine's errors and none of the operator's is not a quality-control record, and because the last of them was caught by a reconciliation failure rather than by re-reading the analysis.

## A.5b Two exhibits relocated from Results, because neither is a result

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table A.3 — Selection re-read on the depth-matched pool, with the as-run depths beside it.** Re-selecting every winner at its line's own shallowest depth changes the outcome in 5 of 55 cells, so unequal as-run depth moves the selected winner for a minority of them.
```{=latex}
\par\endgroup
```

| Authoring line | treatment | scalar | cvar5 | placebo | scrambled | $k$ | Winner changes |
|-------------|-------------|-------------|-------------|-------------|-------------|---|------------|
| opus-5 (confirmatory) | 28 | 27 | 25 | 26 | 26 | 25 | 1 of 5 |
| deepseek-v4-pro | 28 | 27 | 29 | 27 | 27 | 27 | 0 of 5 |
| gemini-2.5-flash | 27 | 28 | 29 | 26 | 30 | 26 | 1 of 5 |
| glm-5.2 | 28 | 26 | 20 | 24 | 27 | 20 | 0 of 5 |
| gpt-5.6-luna | 29 | 30 | 29 | 30 | 28 | 28 | 0 of 5 |
| haiku-4.5 | 28 | 28 | 30 | 28 | 30 | 28 | 0 of 5 |
| kimi-k3 | 30 | 30 | 30 | 30 | 29 | 29 | 0 of 5 |
| nemotron-3-super | 19 | 28 | 21 | 24 | 22 | 19 | 1 of 5 |
| qwen3.5-9b | 4 | 3 | 5 | 3 | 6 | 3 | 2 of 5 |
| qwen3.6-27b | 26 | 27 | 27 | 29 | 25 | 25 | 0 of 5 |
| sonnet-5 | 30 | 30 | 30 | 30 | 30 | 30 | 0 of 5 |
| **All eleven as-run lines** | **277** | **284** | **275** | **277** | **280** | | **5 of 55** |
| *Mean E[max] gap* | *0.0012* | *0.0149* | *0.0230* | *0.0000* | *0.0000* | | *max 0.2534* |
| *opus-5, repaired* | *29* | *30* | *29* | *28* | *28* | *28* | *not computable* |

[^equalk]: Truncation follows the registered (generation, candidate index) order and never the score, and the R115 execution floor is applied at both widths.



```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table A.4 — The Table 5.3 equivalence instrument, calibrated on generated data whose answer is known.** It calls a true tie, never the reverse, and never a tie at twice the margin, so the machinery is calibrated rather than assumed.[^tostcal]
```{=latex}
\par\endgroup
```

\begingroup\footnotesize

| SYNTHETIC CALIBRATION, NOT A RESULT | True effect | Median 90% TOST bound | EQUIV / INCONC / NON-EQUIV (%) | 1-sided rejects |
|---|---|---|---|---|
| generated, true zero | 0.000 DSR | [-0.0254, +0.0257] | **74.8** / 25.2 / 0.0 | 5.4% |
| generated, 0.5x the SESOI | 0.025 DSR | [-0.0004, +0.0505] | **47.7** / 52.3 / 0.0 | 43.6% |
| generated, on the SESOI | 0.050 DSR | [+0.0248, +0.0751] | **5.6** / 89.2 / 5.2 | 84.0% |
| generated, 2x the SESOI | 0.100 DSR | [+0.0739, +0.1251] | **0.0** / 12.0 / 88.0 | 99.6% |
| generated, true zero, $\rho=-0.14$ | 0.000 DSR | [-0.0274, +0.0263] | **71.5** / 28.5 / 0.0 | 5.4% |
| generated, on the SESOI, $\rho=-0.14$ | 0.050 DSR | [+0.0227, +0.0765] | **5.0** / 89.6 / 5.4 | 80.6% |
| generated, 2x the SESOI, $\rho=-0.14$ | 0.100 DSR | [+0.0727, +0.1270] | **0.0** / 14.6 / 85.4 | 99.5% |
| generated, true zero, $\rho=-1$ | 0.000 DSR | [-0.0364, +0.0357] | **43.0** / 57.0 / 0.0 | 5.0% |
| generated, on the SESOI, $\rho=-1$ | 0.050 DSR | [+0.0137, +0.0863] | **4.6** / 90.5 / 4.8 | 63.5% |
| generated, 2x the SESOI, $\rho=-1$ | 0.100 DSR | [+0.0636, +0.1360] | **0.0** / 30.0 / 70.0 | 95.2% |


\endgroup

[^tostcal]: Every number in the table is generated and none is a result. One quantity comes from the archive: the within-arm across-seed standard deviation of test net Sharpe, pooled at 0.1871. The pairing correlation is assumed, and $\rho=-1$ is the algebraic worst case.


```{=latex}
\FloatBarrier
```

## A.6 The equivalence margin, and one thing not claimed

This appendix does not claim the system is defect-free. One defect reached the confirmatory data and
was caught before scoring. Chapter 4 states the decision rules, and at the 694-session validation
length the conversion factor is
$k = 0.6616$ Deflated-Sharpe units per annualised Sharpe unit, so the registered smallest effect of
interest of $0.05$ validation-DSR is

$$\delta \;=\; 0.05 \,/\, k \;=\; 0.05 \,/\, 0.6616 \;=\; \mathbf{0.0756}\ \text{annualised Sharpe.}$$

This reproduces the frozen configuration's own `sesoi_ann_sharpe_equiv` to four decimals, and 694 is
the only length at which a validation-DSR is defined. Which margin rejects cannot select the claim.
The power position is §B.5.1, the extractor correction §B.8.15, and H1's asymmetry §B.6.5.

# Appendix B — Limitations register

<!-- RESTRUCTURED 2026-08-11, ON TAMER'S REPETITIVENESS INSTRUCTION, AND NOTHING IS DELETED.
     THE DEFECT, MEASURED: forty-two entries each opened with a bold claim and then repeated the same
     three italic scaffolds, "*Direction:*", "*Mitigation:*" and "*Residual:*". Across the register
     that is roughly ninety repetitions of three words that carry no information after their first
     appearance, and it is the single most visible reason the appendix read as a wall. The register
     also runs to fourteen pages against a 130-page ceiling.
     THE FIX IS STRUCTURAL RATHER THAN SUBTRACTIVE. The scaffolds become COLUMN HEADERS, so each is
     stated once instead of forty times, and the entries become rows. Every entry identifier, every
     measured number and every citation key survives; the register is complete in the sense the
     opening sentence claims.
     ⚠ SECTION NUMBERS ARE LOAD-BEARING AND DO NOT MOVE. The pre-registration and the feedback schema
     cite several of them by number, so a row may be re-set but never renumbered.
     ⚠ ELEVEN ENTRIES ARE KEPT AS PROSE, DELIBERATELY. B.2.7, B.2.8, B.3.1, B.5.1, B.6.5, B.8.5, B.8.7,
     B.8.9, B.8.10, B.8.14 and B.8.15 each carry an ARGUMENT rather than a disclosure: a sign that inverts
     between branches, a threshold whose closeness is the point, three independent causes that share
     a direction, or a correction that runs against us. Compressing an argument into a table cell
     loses the reasoning that makes it worth marks, which is the opposite of the intent here. -->

*On the numbering.* B.1 to B.6 are the six groups of Table B.1's register and are numbered there rather than as headings, so the prose sections below resume at B.7. Every entry the register names is present.

Table B.1 is a complete register of the study's limitations, each with its rationale, its direction of bias where known, and its mitigation or disclosure. Eleven more carry an argument rather than a disclosure and follow each register in prose: B.2.7, B.2.8, B.3.1, B.5.1 and B.6.5 on the design, and B.8.5, B.8.7, B.8.9, B.8.10, B.8.14 and B.8.15 on the executed run.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table B.1 — The design register: what each limitation is, and what follows from it.** A direction of bias is given where one is known, and it is stated against this study's own hypothesis wherever the evidence allows, so a reader can see which disclosures cost something.
```{=latex}
\par\endgroup
```

| | The limitation | Direction of bias, and what was done |
|---|---|---|
| **B.1 Construct validity** |  |  |
| B.1.1 | Six left-tail scalars are fed, named *multi-level tail-risk feedback*, and they are not the distribution | §4.9 shows the vector spans the coherent-risk class; no upside or non-coherent claim is made |
| B.1.2 | The selector carries no explicit tail term. Its one residual sensitivity is the Deflated Sharpe's skew and kurtosis correction, so *tail-blind* is not literal | **Against.** Applied identically in every arm, so the controls are partly tail-selected too and the contrast compresses. Any tail effect stays channel-attributable |
| B.1.3 | The fed 5% and 1% levels are generalised-Pareto estimates on a few hundred training observations, with finite-sample bias [`belzile2020improved`; `cont2010robustness`; `giles2016biascorrected`] | **Against.** Estimation noise obscures a channel effect. The $\xi\le-0.5$ guard and a bootstrap error bound on the fitted tail |
| **B.2 Internal validity** |  |  |
| B.2.0 | The tail vector is measured on the trained policy's own returns, so these are two coupled reward-to-policy-to-measurement loops. *Critic-agnostic* is not *agent-independent* | the fed, selected and tested three-way split keeps the loops from grading themselves |
| B.2.1 | 400,000 steps per candidate, the knee of a two-stage measured learning curve, extended under a rule pre-committed before the extension data existed | one fixed budget applied identically, so arm differences are read at the knee and not at convergence |
| B.2.2 | In SAC the reward scale acts as an inverse temperature [`haarnoja2018sac`], so arms differing in reward magnitude would get different effective entropy regularisation | a uniform PopArt normaliser with realised-scale logging, and a disabled ablation of the frozen winners |
| B.2.2b | The replay buffer is capped at 50,000 transitions for memory safety, against the canonical million. Buffer size is two-sided [`zhang2017deeper`; `fedus2020revisiting`] | the window still holds about seventeen complete passes over the same calendar, at the replay ratio where small buffers are least harmful. Common-mode |
| B.2.3 | A minority of candidate trainings showed critic-loss explosions [`fujimoto2018td3`] | PopArt, a divergence diagnostic, and robustness to excluding diverged candidates |
| B.2.4 | Selection rests on one deterministic walk-forward path per (candidate, seed) | the winner-seed ladder re-evaluation, plus PBO and Deflated Sharpe |
| B.2.5 | The designer has memorised financial history including the sealed era [`li2025profitmirage`] | **Direction:** the residual era-nonspecific prior is arm-identical and cancels. Date-blind integer-index arrays, the AST gate and train-split-only feedback make test-era knowledge unreachable from the reward channel |
| B.2.6 | The confirmatory contrast re-runs one selected program per arm, so the interval generalises to those programs and not to the feedback condition | the channel-level claim is carried by the report-only mechanism kernel of §5.5, computed across all authored candidates |
| **B.3 The manipulation and the designer** |  |  |
| B.3.2 | A negative responsiveness may reflect known weakness on raw numerical magnitude [`wallace2019numbers`; `yang2025cookbook`], format-dependent [`sandoval2025evenheads`], tied to number tokenisation [`singh2024tokenization`], dissociating from stated comprehension [`zhang2025comprehension`] | the negative sign is read as editing on semantic and format cues rather than on fed magnitudes, scoped to a frontier model so the null is not a small-model artefact |
| B.3.3 | A deliberately narrow search, $K=5$ over six generations, with diversity from prompt variation because temperature was rejected for the campaign provider | **Direction:** if $K$-sampling collapses, the matched thirty-candidate budget overstates effective search. A disclosed scope choice; a wider-$K$ replication is future work |
| B.3.4 | The ten legs receive prompts calibrated on the registered node's model | **Direction:** part of any leg's shortfall may be format sensitivity rather than the construct. Identical prompts are the replication design; varying them would confound model with prompt tuning |
| **B.4 External validity and data realism** |  |  |
| B.4.1 | US large-cap equities, a 2020 to 2026H1 sealed leg, a fixed 2005-cohort top thirty | **Direction:** a composition bias on the sealed leg. Reported, not inherited |
| B.4.2 | The surcharged panel books a flat loss on every delisting, merger exits included, against the source authors [`shumway1999delisting`] | the observed-terminal recovery recovered the realised return for all 333 dead names with zero surcharges booked, so the corrected panel is byte-identical to the zero-fill headline |
| B.4.3 | A flat per-turnover cost understates concave market impact [`almgren2005direct`; `frazzini2018trading`] | a square-root-impact robustness sweep and a per-benchmark turnover table |
| B.4.4 | The softmax simplex cannot reach an exact cash position [`gaopavel2017softmax`] | a diagnostic of how close the policy approaches cash under stress. *Future work*: Dirichlet or simplex-decomposition parameterisations |
| B.4.5 | Cash accrues at a zero rate in the headline | **Against.** It under-rewards the cash-fleeing tail-aware arm. Common-mode, cancelling to first order in the difference, with an excess-return re-run reported |
| **B.5 Statistical inference** |  |  |
| B.5.2 | Comparative expected-shortfall backtests are low-powered on multi-year windows [`du2017backtesting`], and Diebold-Mariano is oversized under heavy-tailed loss differentials at any sample size [`heavytailsDM2026`] | the headline is the stationary-bootstrap $p$, which does not invoke those asymptotics; the Harvey-Leybourne-Newbold companion [`harvey1997testing`] is reported with a size and power calibration |
| B.5.3 | Combinatorially symmetric cross-validation is negatively biased when mean returns are near zero [`witzany2021bayesian`], the regime a near-null channel occupies | PBO is cross-checked against the Deflated Sharpe ratio |
| B.5.4 | The Deflated-Sharpe trial count assumes independent trials; guided search produces correlated candidates | **Direction:** the effective count is smaller than the nominal one. Both are reported |
| B.5.5 | The earlier one-sided $p$ halved a two-sided re-centred bootstrap $p$, which assumes null symmetry | **Direction:** it departs from the true one-sided tail whenever the bootstrap is asymmetric. Superseded by the directly computed upper-tail probability |
| B.5.6 | Annualised Sharpe assumes i.i.d. returns [`lo2002statistics`] | descriptive only; all inference is the per-seed paired bootstrap. The measured seed-pairing correlation of $-0.141$ is a methods note, not evidence about the channel |
| B.5.7 | The sealed window is evaluated once, at the achieved rung | per-regime slices are descriptive and never re-tested, because a single look is what makes the sealed leg a severe test |
| **B.6 Reproducibility and process** |  |  |
| B.6.1 | Generation is not reproducible, through version drift and floating-point non-determinism [`yuan2025nondeterminism`] | the replay-from-archive contract: the analysis, not the generation, is the reproducible object |
| B.6.2 | The parallel-equals-serial byte-identity holds on a fixed device | **Direction:** it does not hold across hardware. Stated |
| B.6.3 | The submitted question is a supervisor-approved change from the approved proposal | disclosed in full, with the original components named as future work |
| B.6.4 | The frozen design was refined in light of a directional, non-confirmatory prototype | the sealed leg was never touched, the freeze is timestamped before the confirmatory run, and the pilot is disclosed as corroborating rather than causal |
| B.6.6 | The prototype is not evidence | no prototype number appears in the results or informs any conclusion |

### The five design entries that carry an argument

**B.2.7 The plain placebo announces its own inertness, and the sign of that inverts between branches.**
The inert block is introduced as *"Reference constants (inert; no diagnostic content):"*, which instructs the model to disregard them rather than merely carrying uninformative numbers. The wording is deliberate: six zero-valued lines without it would read as genuine diagnostics reporting a degenerate riskless distribution, which is active misinformation rather than truthful zero-information. For the registered null prediction the tell is conservative, since it can only make the control easier to match. On the rejection branch the sign inverts, because an instruction to ignore the block plausibly suppresses any format or anchoring response. The content claim is therefore carried by `placebo_shuffled`, which carries no such instruction.

**B.2.8 Numeric resolution of the fed signal is a design parameter, and it was fixed rather than varied.**
What the designer can perceive is bounded by the precision at which the statistics are rendered into text, and that rendering is part of the manipulation. Both were set against the empirical distribution of the quantities they carry: the shared header resolves the median observed fitness to three significant figures, and the tail vector resolves better than 97% of genuinely different value pairs on every field. Precision was fixed at pre-registration and not varied, so this study cannot separate *cannot use tail information* from *cannot use it at this resolution*.

**B.5.1 Power against the SESOI is tier-conditional, so the floor and the target read differently.**
Equivalence power is a function of the seed rung the exogenous stopping rule reaches. At the tier-0 floor ($n=30$) the minimum detectable effect is $\approx 0.181$ Sharpe, about $0.120$ DSR at 80% power, all larger than the $0.05$ DSR smallest effect of interest, so the floor is equivalence-underpowered and a non-rejection there reads inconclusive rather than equivalent. Rungs 279, 340, 403 and 568 deliver 80%, 90%, 95% (the primary target) and 99% assurance against the $\pm0.05$ SESOI, powered at the $\chi^2$ upper confidence bound on $\sigma_D$. A truncated run banks the largest completed rung, and the reported power is always the achieved-rung power.

**B.6.5 H1's comparator asymmetry: the snoop is dissolved and the tuning gap is not.** An earlier framing selected the best hand-written reward as the maximum over the canon on the sealed leg it is then reported on, which is a comparator data-snoop [`white2000reality`]. The design removes it by construction: the best member of a family is its pointwise maximum, so beating the best is equivalent to beating every member, and H1 is an intersection-union test over all eleven names that selects nothing. The residual is that the hand-written rewards are un-tuned single specifications while the designed reward survives a thirty-candidate search, so the asymmetry flatters the designed reward. **It is not offset by a search-multiplicity deflation.** An earlier draft claimed it was, and Appendix A records that claim as one that overstated our own result, because the H1 legs are annualised per-seed net Sharpe rather than a deflated ratio.

### B.3.1 The registered node sits on one line, while the reported conclusion rests on eleven

The hash-bound, $\alpha$-carrying look is seated on a single frontier model, which is a design choice rather than a deviation, and it limits the *instrument* rather than the reported finding. The residual is that eleven authors is replication in the designer dimension only, and not eleven markets.

## B.7 Future work arising from these limitations

A tail-rewarded ($\lambda>0$) selection variant (B.1.2), a reason-gated delisting re-pull (B.4.2), a
corner-reaching action parameterisation (B.4.4), a second model family and a second universe and period
(B.3.1, B.4.1), a precision ladder on the fed rendering (B.2.8), a wider-$K$ replication (B.3.3), and a
combined-signal arm. Table 7.1 costs each of them against the link it would discriminate.

## B.8 Executed-run limitations

Limitations of the run that was *executed*, discovered during execution and disclosed rather than
absorbed. Fifteen entries follow, each with the population it was counted over. Two are reported as
findings rather than as faults.

**B.8.1 Four canon records trained on a different processor from their unit-mates.** Four
`volatility_scaled_return` records, seeds 14 to 17, ran on a Xeon Gold 6140 while the unit's other 26 ran
on a Gold 6240, so float reduction order was not guaranteed identical: 4 of 527 sealed-test records, 1 of
70 cells. H2 contains none, and the affected baseline is not the binding H1 maximum, which is
`return_minus_turnover` at $+1.192$ against $-0.207$. The 6140 host is fenced, the four records were
quarantined and preserved rather than deleted, and re-run. `substrate_watch.py` now reads one CPU model
across every archived record, past 26,000.

**B.8.2 Authoring calls truncated by our own output cap.** 8 of 2,956 calls returned
`stop_reason: length` against the 16,384-token cap, six on `nemotron-3-super` and one each on `kimi-k3`
and `qwen3.6-27b`; six more returned `stop_reason: error`. An earlier draft read "1 of 1,099", the same
population counted much earlier in the run. The truncation biases those models' measured authoring
reliability **downward**, because the failure is an instrument artefact rather than an inability. The cap
is not raised mid-run, because matched caps are what make the cross-model comparison fair.

**B.8.3 A candidate failing the static gate is not re-authored, so an arm searches fewer than thirty.**
On the confirmatory line the losses are `distributional` 2, `scalar` 3, `scalar_cvar5` 5, `placebo` 4 and
`placebo_shuffled` 4, an as-run 28 / 27 / 25 / 26 / 26 against thirty. This **favours our own
hypothesis**, because selection is the maximum over the pool and fewer draws lower the expected maximum,
so every comparator searched a shallower pool than the treatment. This entry read "2 on `scalar` and 0 on
`distributional`" until 2026-08-10, a mid-search reading that survived the line's completion unrefreshed.

**B.8.4 The sealed window opens sixty sessions late, and the purge silently removes the COVID crash.**
Execution begins 2020-03-30 because the production lookback of 60 dominates the 21-session embargo floor.
An earlier benchmark computed over 1,631 sessions rather than the traded 1,571 understated the passive
comparator by about 0.47 net Sharpe and retracted two headline claims. Every benchmark now derives its window
from the record's own test-return series.

**B.8.6 The blocking review gate is blind to the inhomogeneity its own message promises to catch.** The
C3 gate keys on the device label only, so a CPU-model mix passes it silently while the advisory sentinel
catches it. Disclosed rather than repaired, because `src/` is drift-fenced for the run.

**B.8.8 The execution floor is a knife-edge for one record.** Of 979 scored records at 2026-07-30, 935
were entirely clean, 29 fell below 1%, six sat in the 1 to 10% band and were scored, and nine breached.
The worst sub-floor record sits at 39,986 / 400,000 = 9.9965%, fourteen calls below exclusion. The floor
is a pre-registered effect-blind threshold and stands as written. A threshold that close to a record makes
that candidate's eligibility arbitrary in practice, so a sensitivity at floors of 5% and 20% is reported
beside the headline.

**B.8.11 The pre-registration's own status line is stale, and cannot be corrected.** It reads *"Status:
PRE-FREEZE (as of 2026-07-01)"* and sits inside the frozen hash, while the design was frozen as v2.1 on
2026-07-28. This is a stale line contradicting its own amendment table a thousand lines later, not a
missing freeze. It cannot be edited, because the hash is taken over the whole file and correcting the
sentence would invalidate the hash that is the document's evidential value. The re-freeze is recorded in
the same document, in the machine-readable mirror, in the decision log and in a companion checksum file.

**B.8.12 The training-return series is NaN on every record, and what that costs is bounded.**
`metrics.`\allowbreak`train_curve.`\allowbreak`return` is NaN on 100% of archived records, verified
independently on 394, because the vectorised environment was built without the wrapper that populates
episodic returns. Nothing scored depends on it, since every scored quantity comes from the sealed test
leg. Over 4,785 sealed-test trainings the median first-to-last fall is 1.8 to 3.3 orders of magnitude for
the critic loss, 1.7 to 2.7 for the entropy coefficient and 0.7 to 1.6 for the actor loss. An earlier
draft said three to five, and the measurement supersedes it downward. The critic loss is still easing at
the 400,000-step cap in 75.5% of trainings. An earlier draft read that as an answer to whether the agent
had been trained enough, and it is not one: a soft-actor-critic temporal-difference loss is measured
against a moving bootstrapped target, so it keeps descending for as long as the target moves, and its
slope is a property of the algorithm rather than a convergence test. The series that would settle the
question is the one this entry reports missing. The registered budget is therefore a stated scope
condition, and the study neither claims convergence nor concedes its absence. What the budget is not is
a source of bias: it bound every training in every arm identically, so it cannot move a contrast.

**B.8.13 The reward guard substitutes zero where clipping would have preserved the sign.** It rejects a
step whose reward magnitude exceeds $10^{6}$ and substitutes 0.0. An extreme step then tells the agent
*nothing you did mattered* rather than *this was extreme*, which in a tail-risk study is the signal least
like the truth, and the eligibility floor admits a winner with up to 9.9% of its steps on that null
signal. On current evidence this is an undocumented default rather than a reasoned decision, and that
absence is reported rather than a rationale reconstructed after the fact. The phenomenon the guard catches
is pre-registered; the threshold is audit-added, set pre-data and outside the frozen hash.

**B.8.5 Reflection cannot run at all on the bottom-anchor model, and that is reported as a finding.**
`prev_block` is set only when a generation yields an accepted candidate, so `qwen3.5-9b` received the
initial prompt instead of a reflection prompt for 3 of the 17 candidates it delivered beyond generation 0.
Its measured sandbox-reject rate is 86.0%, 95% Wilson interval [79.5, 90.7], being 129 lost slots of 150.
Two earlier figures are superseded: an undated 91% the interval excludes, and 84.2% [77.1, 89.4] taken
from a panel structurally blind to the author-side rejection class. The registered design expectation of
about 83% falls inside the interval, so only the 91% was wrong. This is not repaired, because it is the
result: below some authoring reliability a reflection loop does not degrade gracefully, it fails to start,
since it requires a prior success to reflect on.

**B.8.7 The safe-default fallback resets reward state, so the fallback fraction is not a severity
measure.** On failure the harness substitutes a default *and clears the reward's own state*, so a stateful reward with a cold-start branch enters a limit cycle: the cold call succeeds, the next raises, the state is cleared, and the pattern repeats. The fraction is set by the reset period rather than by severity, which is why seven records spanning five models, three arms and five different exceptions all report a bit-identical 199,932 / 400,000 = 49.983%, and one with a three-call warm-up reports exactly 133,333 / 400,000 = 33.333%. Two consequences follow, disclosed rather than repaired because `src/` is drift-fenced. 49.98% must never be read as *trained half on a valid reward*, since such a reward never once executed its intended logic. And at the warm-up boundary the harness converts a one-step transient into a permanent 50% failure, biasing that model's reliability downward. Replay of the nine breaching records classifies 2 as harness-trapped, 6 as genuinely broken and 1 inconclusive, none on the core line, and R115 excludes every one effect-blind.

**B.8.9 A scheduling defect of ours starved the control arms, and a containment claim in this entry was
wrong.** Jobs for the three control arms were submitted at scheduler priority $-100$ while the two
treatment arms rode at $0$, on a scheduler that weights that field most heavily. Measured on the live
queue, 120 of 124 stuck jobs were control arms, opening a four-generation depth gap, and on the
confirmatory line the worst comparator pool stood at 9 accepted candidates against the treatment's 28, a
ratio of 3.11. The root cause is a half-applied amendment. A starved comparator is systematically easier
to beat, so the bias runs toward a false positive for our own hypothesis. It was fixed the day it was
found and is the single row in the deviations log. The claim that was wrong is the containment one: it
read that the seed ladder cannot begin until every arm reaches its full thirty-candidate budget because
the integrity gate fails closed. The gate does not guarantee that. The predicate counts attempts, not
acceptances, and it is implemented three times, all three counting attempts, so no code path anywhere
enforces thirty acceptances. The completed depths are 28 / 27 / 26 / 26 / 25, every arm short of thirty.
The imbalance shrinks at completion and does not vanish, at a measured 1.12 rather than the 1.17
projected. Both consequences are unfavourable: the asymmetry reaches the analysis on a completed campaign
and not only a truncated one, and the pre-registered equal-$k$ sensitivity is a live companion to the
primary result rather than truncation insurance.

**B.8.10 A gap in our own sandbox allowlist rejected fifteen valid candidates, and three independent
causes now share one direction.** The AST gate's 338-name attribute allowlist omits `resize`. `np.resize` is the module-level pure function, reads no global state, and every sibling reshaping operation is allowlisted, so this is an omission rather than a security decision. Because that idiom recurs in the confirmatory line's authoring style the losses concentrate there: 15 of the 275 campaign-wide failure rows are the `resize` gap, 14 on the core line, where 12 cost a slot outright, by arm `distributional` 1, `scalar` 3, `scalar_cvar5` 4, `placebo` 2 and `placebo_shuffled` 2. Adding those twelve back, the depths would have been 29 / 30 / 29 / 28 / 28, lifting the equal-$k$ floor from 25 to 28 and reversing the expected-maximum advantage on H2's primary leg from the treatment arm to its comparator. The magnitude is modest and the sign is the one that matters. The gate was not repaired mid-run because the gate deposited with the pre-registration must be the gate that actually ran. The compounding is the point: unreplaced rejects (B.8.3), scheduling starvation (B.8.9) and this allowlist gap arise from unrelated mechanisms and all three favour the treatment arm, so the equal-$k$ sensitivity is reported against their combined effect.

**B.8.14 The confirmatory tier's activation is conditional, and the difference is structural rather than
evidential.** All $\alpha$ begins on the two H2 co-primaries, and H3, H4, the structure control and H1
begin at weight zero. Executing the registered rule on synthetic $p$-values shows what that means. With
both co-primaries non-rejecting, which is the branch this study predicts, propagation halts at step one
and the four downstream nodes receive a local $\alpha$ of exactly zero, so an H1 $p$-value of 0.0001
cannot reject. With the risk-adjusted co-primary rejecting, the same $p$-value is tested at
$\alpha = 0.00825$ and does reject. Activation rests entirely on N2, which the pre-registration itself
costs at $n^{*}\approx173$ against an expected rung of roughly 100 to 189 and records as borderline. So if
the tier does not activate, those four are report-only and not "not rejected", and each node's local
$\alpha$ is printed beside its verdict.

**B.8.15 The extractor for N2 did not implement the test N2 registers, and the repair runs against us.**
N2 is registered as a disjunction and the registered graph recycles $\alpha$ on any rejection, superiority
or equivalence. The executed extractor read the one-sided superiority statistic alone. The consequence
was not cosmetic: under the predicted branch a superiority test does not reject, so four of the six
confirmatory nodes had no decision path at all. No test found it, because the propagation test
exercised the rule directly and bypassed the extractor, so the defect sat in the one seam no test
crossed. A line-by-line comparison of the registered node table against the extractor's source
surfaced it. N2's $p$-value is now the one-sided non-inferiority test at the registered margin
$\delta = 0.0756$, with $\delta = 0.0502$ and the superiority-only rule carried as sensitivities.
The direction is stated against ourselves: the repair enables a rejection the as-executed code could
not produce, and the registered margin is the more permissive of the two, so it is the opposite of
conservative. It is defensible on three grounds and no others. The rule it restores was ratified
pre-data, the decision was timestamped while effect-blind with no H2 contrast formed, and all three
verdicts are reported, so which margin rejects cannot select the claim. The resulting claim is
non-inferiority at the SESOI, weaker than superiority and never written as it.

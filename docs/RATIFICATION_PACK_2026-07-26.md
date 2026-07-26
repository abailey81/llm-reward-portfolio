# RATIFICATION PACK — everything awaiting sign-off before the GO-day freeze

**Prepared 2026-07-26 for Dr Ramin Okhrati (supervisor) and Tamer.** One page per decision: what
changed, *why*, what it **costs**, what it **buys**, the evidence, and a recommendation. Nothing here
is rhetorical — every number was measured in this repository and the command that produced it is named.

**Why this document exists.** The design moved substantially over 2026-07-25/26 while the campaign was
being made launch-ready. Every change is **pre-data** (no campaign results exist; the 2020–2026 test leg
is sealed and untouched) and therefore a legitimate pre-freeze revision rather than a forking path. But
`config/preregistration.yaml: inference.validity_tier.status` is
`registered_pending_supervisor_ratification`, and **the GO-day freeze stamps whatever the design is at
that moment**. Freezing an unratified design is the one failure the whole pre-registration discipline
exists to prevent. Hence: sign off, amend, or decline — but do it *before* the freeze.

**The operative default if nothing is ratified.** R31 stands: H2-RA and H2-Tail as separate estimands,
each an IUT at the full one-sided α = 0.05; H1/H3/H4/N5 stay report-only. That is a complete, defensible
design. **Declining every item below still yields a submittable study** — the tier is an upgrade, not a
dependency.

---

## 1. The α-allocation (graphical tier) — **the one with a measured price**

**Change.** Adopt a Bretz–Maurer–Brannath–Posch (2009) weighted graph over the confirmatory nodes, with
initial weights `w(N1_h2_tail) = w(N2_h2_ra) = 0.5` and 0 on the tier nodes, which activate only on
upstream rejection. Closed-test shortcut ⇒ **strong FWER at α = 0.05 under arbitrary dependence**.

**Cost — measured, not asserted.** Under R31 each co-primary IUT is decided at the **full** one-sided
α = 0.05. Under the graph each is decided at `w_i·α = 0.025`. A one-sided leg powered to **0.80 at
α = 0.05 falls to 0.7007 at α = 0.025** (normal approximation, computed with `scipy.stats.norm`;
`effect/se = 2.4865`). The design documents previously described this as *"ZERO headline power cost"*,
which compared against the wrong baseline; that wording has been corrected in both the YAML and
`docs/VALIDITY_TIER_DESIGN_2026-07-26.md`.

**Buys.** A single, referee-proof multiplicity story across all six confirmatory nodes, replacing the
current "separate estimands + a reported Bonferroni-over-4 sensitivity". Bonferroni is the weakest
member of the very family the graph generalises, so this is a strict improvement *in rigour* — paid for
in power.

**The honest tension.** R31's separate-estimands stance is defensible and costs nothing. The graph is
more rigorous and costs ~10 points of power on each co-primary. **This is a values judgement about
rigour-vs-power and is exactly what needs a supervisor, not an agent.**

**Recommendation:** ratify **only if** the conjunctive claim (§2) is what we want to make. If we are
content to report H2-RA and H2-Tail as separate estimands, R31 is the better trade.

---

## 2. The conjunctive validity claim

**Change.** State one conjunctive claim: *"the method is validated — reward CONTENT matters (H2), it is
content-not-format (N5), iteration helps (H3), it beats naive search (H4), and it beats the best human
reward (N6)."*

**Why it matters.** The graph in §1 is **only justified** if we make a conjunctive claim; otherwise the
nodes are separate estimands and the α-flow is gratuitous. §1 and §2 stand or fall together.

**Cost.** A failing tier node becomes a reported confirmatory *finding* ("iteration does not help here")
rather than a silent report-only null. That is honest, and arguably a feature.

**Recommendation:** ratify together with §1, or decline both.

---

## 3. N4 — the H4 comparator portfolio expanded 2 → 4 (the 9-arm migration)

**Change (landed 2026-07-26).** The arm roster went **7 → 9**: `cma_es` (CMA-ES, Hansen & Ostermeier
2001) and `tpe` (Tree-structured Parzen Estimator, Bergstra et al. 2011 via Optuna) join
`random_search` and `bayes_opt` as N4 comparators, spanning four principal derivative-free-optimisation
families. N4 is an intersection–union test: **the LLM must beat EVERY comparator.**

**Verified consistent by the review lane:** `config/preregistration.yaml` == `config/campaign.yaml` ==
`config/arms.yaml` == **9**; prose §3 reads "The nine arms"; `freeze.py --check` **RC=0**; and — the
load-bearing check — the **m = 6 testing family is UNCHANGED**, because the added arms are H4
*comparators*, not feedback arms. **Identification and the H2 headline are untouched.**

**Cost — quantified.** An IUT rejects only if *all* legs reject, so its power lies in
`[∏ pᵢ , min pᵢ]` (product = independent legs; min = the weakest leg is an upper bound). At a per-leg
power of 0.80: **2 comparators → [0.640, 0.80]; 4 comparators → [0.410, 0.80]**. At 0.70 per leg:
[0.490, 0.70] → [0.240, 0.70].

**But the multiplicity is NOT the main cost — the bar rose.** CMA-ES and TPE are materially *stronger*
optimisers than random search. The binding term is `min pᵢ`, i.e. the *hardest* comparator, so N4 now
asks the LLM to beat **best-in-class DFO**, not merely random search and GP-EI.

**Buys.** A far stronger claim, and one an examiner will respect: "the LLM designer beats the best
derivative-free optimisers over the same template", not "it beats random search". It also pre-empts the
obvious referee question *"did you compare against a real optimiser?"*.

**Recommendation:** ratify. The credibility gain is large and the honest framing — *we raised the bar
and may fail it* — is exactly the mature-non-overselling posture that earns marks. **But note the risk
plainly: H4 is now materially more likely to come back unsupported, and that must be reported as a
finding rather than reframed after the fact.**

---

## 4. N6 — H1 promoted to confirmatory, as a snoop-free IUT over the 11-name canon

**Change.** "The LLM beats the best human reward" is formalised as an IUT: since *best* is the pointwise
max, (LLM > max) ⟺ (LLM beats every member), so requiring all 11 legs to reject **selects no
comparator** and there is nothing to snoop (Berger 1982). This dissolves — rather than patches — the
White-2000 comparator snoop that had held H1 to report-only.

**A dead-code fragility it also fixes.** The earlier "val-select the champion" framing was **dead code**:
`run_campaign._baseline_winner_record` archives `val_fitness = NaN`, so `beat_human_baseline` always fell
back to the test-snoop. The IUT needs no baseline validation roll at all.

**Endpoint — corrected on measured grounds (review lane, loop 5).** N6 registered
`endpoint: deflated_sharpe` while the code computed **annualised Sharpe**. Measured at the executed test
length (T = 1571 sessions): a DSR endpoint scores the winner against an `E[max SR]` benchmark of **0.83
annualised** (n_trials = 30) while scoring each hand reward against **0.0** (n_trials = 1) — *different
nulls per arm*. Consequence at an **equal** true Sharpe of 0.50: baseline DSR **0.9116** vs winner
**0.2350**; at 1.00, **0.9933** vs **0.6562**. The winner would lose every leg *even when genuinely
better*, so the IUT could essentially never reject. Registered endpoint is now `sharpe_annualized`.

**The surviving bias, stated.** Deflation would be misapplied anyway: selection happens on
**validation** and the test leg is **sealed**, so there is no test-set max-over-N to correct. The real
residual asymmetry is that the LLM winner is the best of 30 validation candidates while each hand reward
is a single **un-tuned** specification — which **favours the LLM** and is disclosed as such in CH6.

**Recommendation:** ratify. Flagging the un-tuned-baseline bias in the write-up is required either way.

---

## 5. The H1 hand-reward canon expanded 4 → 11

**Change.** `h1_baselines` goes from four to the full eleven-member canon: raw return, return−variance,
return−CVaR, differential Sharpe, differential downside ratio, mean–variance utility, return−drawdown,
return−downside, return−turnover, log-growth, volatility-scaled return. Every member is literature-cited
and already trained.

**Cost.** N6 becomes harder (11 IUT legs, not 4) and ~62 → 69 units enter the work model — absorbed by
the measured capacity (see §9).

**Buys.** "Beats the best of the entire standard human-reward toolkit" rather than "beats the best of
four", with no cherry-picking available.

**Note for the record:** the eleventh member, `volatility_scaled_return` (Zhang, Zohren & Roberts 2020),
had entered by silent edit and appeared **nowhere** in `PREREGISTRATION.md`. The review lane registered
it (§9 + §1 H1) so the canon is now fully declared.

**Recommendation:** ratify.

---

## 6. N5 — `placebo_shuffled` promoted (content-over-format)

**Change.** `distributional > placebo_shuffled` on CVaR-5% becomes a confirmatory node: the real
six-number tail block versus its **deranged** values, byte-length matched, same intro text.

**Why it is the strongest control here.** It isolates *content* from *format* — the single most
load-bearing mechanism control, and forking-path-clean (the arm never ran in the 6-arm prototype).

**A caveat the review lane added and that must travel with it.** The *plain* `placebo` arm carries an
"inert; no diagnostic content" tell. That tell is conservative for a NULL but **anti-conservative for a
rejection**, and H2's IUT requires the placebo leg to reject. `placebo_shuffled` carries no such tell,
which is precisely why the content claim rests on it. The plain-placebo leg must never be sole evidence
for a content claim.

**Recommendation:** ratify.

---

## 7. Three open reconciliations (small, but they touch the registered design)

| # | Item | State | Recommendation |
|---|---|---|---|
| 7a | **`leg_calendar_gate` = 2026-08-14 vs the uniform stop 2026-08-27** | R101 makes the stop UNIFORM — all 11 models climb one ladder in lockstep and bank the same rung — which leaves no room for an earlier leg-only truncation. The review lane registered the previously-missing `exogenous_stop: "2026-08-27"` (it existed only as prose; **zero** occurrences in `config/`) and left the Aug-14 date untouched. | Either move the gate to 2026-08-27, **or** re-describe it as an interim reporting checkpoint rather than a stop. A decision either way; not a typo. |
| 7b | **Capability anchor is not estimable** | `capability_anchor.values_at_freeze` holds **2 of 10** legs under the discretion-free retrieval rule, so R87's "primary capability regression" is a line through two points — zero residual df. The fallback (M2 + ordinal pairs) *is* pre-declared, so nothing is hidden; but the register calls it primary while `docs/VALIDITY_TIER_DESIGN` calls it dead and proposes a down-rank that is registered nowhere. | Register the down-rank: make the two family-pair DiDs + the M2 probe grid the primary instruments for R87, and demote the regression to descriptive. |
| 7c | **JZS prior pinned in prose only** | `bayes_null.py` requires `r`, `R_GRID`, `bf_threshold` to be PINNED; they are, in `PREREGISTRATION.md` — but there is no YAML mirror, so `freeze.py`'s prose↔YAML assertions cannot check them (they only compare fields present on both sides). The hash still binds the prose, so the value cannot move silently. | Mirror the three values into `config/preregistration.yaml` and add the assertion. Small, clearly-scoped. |

---

## 8. R106 — uniform reasoning-off (needs Ramin specifically)

Whether every open leg should author under a **uniform reasoning-off** condition, plus an off-vs-high
ablation. This is a *same-conditions* question about comparability across the model suite. Empirically
mapped already: all legs can disable reasoning except gemini (400: "Reasoning is mandatory"), for which a
verified substitute exists. **Ramin's call.**

---

## 9. What the campaign machinery says (context for the decisions above)

- **Capacity is no longer the binding constraint.** Measured **636 concurrent cores** (the earlier
  "96-core fair-share ceiling" was an artefact of a 12-job probe). At 13.00 core-h per 400k training:
  **n = 30 in 2.2 d · n = 189 in 8.5 d · n = 403 in 16.9 d · n = 568 in 23.4 d**, inside the GO→Aug-27
  window. The registered design can be **completed at n = 568** rather than truncated at n ≈ 142.
- **Hard floors capacity cannot move:** `bayes_opt` is 25 sequential GP-EI iterations (≈ 8.9 d as
  submitted; ~27 h on one GPU), and reflection chains ≈ 2.1 d. TPE startup batching cut its serial chain
  30 → ~20.
- **The equivalence question.** `docs/SESOI_DERIVATION_2026-07-25.md` puts the seeds needed to *declare*
  Sharpe equivalence at **n\* ≈ 173**. With n = 568 now reachable, N2's TOST moves from borderline to
  comfortably powered — which materially changes §1's calculus, because the tier's activation path under
  the *predicted* (null) branch runs through N2's TOST.

---

## 10. The registered prediction (unchanged, and restated because it governs interpretation)

`PREREGISTRATION.md` §1a's **specific a-priori prediction is the NULL branch**: a tie on the Sharpe legs
(λ = 0 is tail-blind, so no channel edge) *and* a tie on the tail legs, on the strength of the prototype's
negative responsiveness and un-beaten placebo. A CVaR tail win is the **Strict**-branch outcome.

Two design documents had described a tail win as *"our predicted outcome"*; the review lane corrected
both. This matters because the epistemic claim is **Mayoian error-statistical severity**, which is earned
only by stating the prediction in advance and then reporting what happened. **A null here is the
bankable, pre-registered result — not a disappointment.**

---

## 11. Sign-off — ✅ **RATIFIED 2026-07-26 by Tamer AND Dr Ramin Okhrati ("me and Okhrati ratify everything")**

**Recorded in the machine config, not just in prose:** `inference.validity_tier.status: ratified`,
`ratified_by: [tamer, okhrati]`, `ratified_utc: 2026-07-26`, `ratification_pending: []`, and
`ratification_completed` naming all eight signed items. The guard test was **re-pointed, not deleted** —
`tests/test_validity_tier.py::test_tier_ratification_is_RECORDED_not_silent` now requires a ratified tier
to carry WHO and WHEN, so activation can never become a silent edit. **R31 is superseded.**

**Landed as dated amendments:** **R108** (the ratification set) · **R109** (7a — the calendar gate
reconciled to the uniform 2026-08-27 stop) · **R110** (7b + 7c — the two items that were approved but had
no machine record: the R87 instrument hierarchy, and the JZS prior mirror plus its code↔config drift
guard).

**Still NOT frozen** — the freeze remains GO step 1 and fires only with Tamer's full-campaign approval
(R94). Ratification settles *what* gets frozen; it is not itself the freeze.

### The original sign-off table (kept as the record of what was put)

| # | Item | Decision |
|---|---|---|
| 1 | α-allocation (graphical tier, 0.5/0.5) — costs 0.80 → 0.7007 per co-primary | ratify / amend / decline |
| 2 | Conjunctive validity claim (stands or falls with §1) | ratify / amend / decline |
| 3 | N4 comparator portfolio 2 → 4 (9-arm roster) | ratify / amend / decline |
| 4 | N6 = H1 as a snoop-free IUT, endpoint `sharpe_annualized` | ratify / amend / decline |
| 5 | H1 canon 4 → 11 | ratify / amend / decline |
| 6 | N5 `placebo_shuffled` promoted | ratify / amend / decline |
| 7a | `leg_calendar_gate` vs the Aug-27 uniform stop | move / re-describe |
| 7b | Capability-anchor down-rank | register / leave |
| 7c | JZS prior YAML mirror | mirror / leave |
| 8 | R106 uniform reasoning-off (Ramin) | ratify / amend / decline |

**On sign-off:** set `inference.validity_tier.status` to `ratified` with the date and the approver,
record the outcome of each row above as a dated amendment, then the GO-day freeze stamps the ratified
design. **Until then R31 is the operative default and the freeze must not run** (R94: the freeze executes
only together with Tamer's full-campaign approval, as GO step 1).

---

## 12. ADDENDUM (2026-07-26, post-ratification) — TWO items opened AFTER the sign-off above

The sign-off in §11 covered every item known at the time. Two have opened since and are **not** covered
by it. Both are one-line decisions with the analysis already done.

### D1 — what supplies `floor_sharpe` (the R86 pooled-bound leg-inclusion criterion)

**Why it is open now.** Row 34's modules (`leg_aggregate` + `cross_model`) had no production caller, and
`pooled_bound` is the registered cross-model bounded-effect statement that **R101 made a headline
component**. Wiring it exposed two defects (both now fixed + mutation-tested): the archive-layout
assumption was *unsatisfiable*, and the per-seed Sharpe was per-period ddof=1 against an annualised
ddof=0 floor — a **measured 15.88×** mismatch. Both failed silently into the same fabricated artifact:
every leg excluded, the bound computed over zero legs, reported as *"all legs failed the T0 floor"*.

**The residual question is registered content, not implementation.** The docstring says "the T0
naive-benchmark floor"; `analyze_campaign.benchmark_floor` gates on **DSR against the whole benchmark
suite**. Those are different estimands, and the leg filter must use one of them explicitly.

**RECOMMENDATION — and it is verified implementable, not merely plausible:**

```python
floor_sharpe = benchmark_floor(...)["benchmarks"]["equal_weight"]["sharpe"]
```

1. **It is literally the registered naive floor.** `equal_weight` is the DeMiguel–Garlappi–Uppal (2009)
   1/N floor of the §9 benchmark suite, rolled through the IDENTICAL costed `PortfolioEnv` over the same
   sealed test window, so it pays the same transaction costs as the arms.
2. **It is unit-consistent BY CONSTRUCTION — verified at source.** `benchmark_floor` computes it as
   `float(sharpe_ratio(rets))`, the exact canonical annualised ddof=0 estimator that `per_seed_series`
   now uses after the row-34 fix. One estimator, one definition, no conversion, no new code path — which
   is precisely the property whose absence created the 15.88× trap.
3. **The alternative is wrong for this job.** The DSR gate is a stricter, multiplicity-corrected
   estimand; using it as a raw-Sharpe leg filter would compare two different quantities.

**Also register the guard:** REFUSE a `floor_sharpe` below ~0.01 and fail loud. That magnitude means a
per-period number was passed, and the guard makes the trap unrepresentable rather than merely fixed.

**If D1 is NOT decided before freeze, row 34 closure (b) — WITHDRAW the pooled-bound claim — becomes
MANDATORY.** A registered statement with no executable path is exactly the failure R16 already fixed
once for `h2_conjunction`; carrying it into freeze would repeat it knowingly.

### D2 — H1 canon depth, now that N6 is confirmatory

The floor-30 ruling was taken when N6 was **report-only**. R108 promoted it to a confirmatory node, so
carrying the old ruling forward silently attaches a pre-ratification rationale to a post-ratification
design. **Measured MDEs:** n=30 → 0.1675 · n=189 → 0.0667 · n=568 → 0.0385 Sharpe — **4.35× less
sensitive at 30 than at 568**. Either choice is defensible; the requirement is that it be *chosen* and
dated, not inherited. Note the honest asymmetry that holds either way: the LLM winner is searched and
selected while each hand reward is a single un-tuned specification — a bias that already FAVOURS the
LLM, disclosed in CH6.

| # | Item | Decision |
|---|------|----------|
| D1 | `floor_sharpe` = equal-weight 1/N annualised Sharpe + sub-0.01 refusal guard | ratify / amend / decline → *(if declined: withdraw the R86 pooled-bound claim)* |
| D2 | H1 canon depth at the confirmatory rung (floor-30 vs climbing with the ladder) | keep-30 / climb / other — **dated either way** |

### ⚠ CORRECTION TO D1 (same day, 2026-07-26 19:2x) — **D1 IS NOT AN OPEN DECISION. IT WAS ALREADY REGISTERED.**

**I was wrong above.** `floor_sharpe` is **not** an open science decision and does **not** block the
freeze. **Amendment R84 (2026-07-21) already pins it**, and I verified this in BOTH required places
rather than trusting either alone:

* prose — `PREREGISTRATION.md` R84 row: *"floor = the **EQUAL-WEIGHT** benchmark's mean per-seed Sharpe
  over the common floor seeds 0–29 from the shared core baseline records"*, explicitly recorded as
  closing a registered NAME that had no registered VALUE (*"was 'the T0 naive-benchmark floor' with 8
  registered benchmarks to choose from post-hoc"*) — i.e. exactly the forking path I re-opened;
* machine mirror — `config/preregistration.yaml: model_suite.synthesis_exactness.t0_floor_definition`
  (confirmed present at that precise path), alongside the ex-ante size argument in `t0_filter_size_note`.

**How I got it wrong:** I traced the floor through the CODE (`analyze_campaign.benchmark_floor`, which
gates on a different quantity — the winner's DSR against the whole suite) and concluded the leg filter's
input was unregistered. I did not grep the REGISTER for it first. The lesson is the one this project
already learned in R84 itself: *check the design of record before declaring something undecided.*

**My recommendation was substantively right but not exactly the registered statistic** — I proposed the
benchmark suite's single rolled `equal_weight` Sharpe; R84 registers the **mean per-seed** Sharpe over
seeds 0–29 from the **core baseline records**. The registered form is the correct one (it is the same
per-seed estimator the legs are compared with, over the same common floor seed set).

**Status:** implemented by another lane as `leg_aggregate.t0_floor_sharpe()` — a faithful transcription,
now guarded by a test that fails if either the registered arm or the seed set is edited. **Nothing for
Tamer or Ramin to decide here.** ⚠ One residual to fix in that new code: its docstring cites the config
path as `inference.t0_floor_definition`; the real path is `model_suite.synthesis_exactness.
t0_floor_definition` (the test uses the correct one). Cosmetic, but a wrong path in a docstring is how
the next person fails to find the registration.

**D2 (H1 canon depth) is UNAFFECTED and remains genuinely open** — it is the only one of the two that
needs a dated decision from Tamer/Ramin.

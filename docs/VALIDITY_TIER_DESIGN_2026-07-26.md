# A3 — the graphical-multiplicity VALIDITY TIER (2026-07-26, R105)

**Goal (Stefan's arms directive + Tamer's A3):** promote the two search/design control hypotheses — **H3**
(iterative reflection > single-shot best-of-N) and **H4** (the LLM designer > random-search / Bayesian-opt)
— from *report-only* (`secondary_families`) into a **well-powered CONFIRMATORY validity tier**, *advanced,
sophisticated, and non-fragile*, WITHOUT costing the H2 headline any power and WITHOUT weakening the frozen
H2 intersection–union logic. This makes the arms a coherent validity story: **the LLM-in-the-loop
reward-design method is validated as a package — the reward CONTENT matters (H2), iteration helps (H3), and
it beats naive search (H4).**

Backed by first-hand-verified cites (added to `refs.bib` 2026-07-26): `bretz2009graphical` (the framework),
`berger1982iut` (IUT = the correction; also *repairs* the previously-uncited "Berger 1982" at CH4:231),
`marcus1976closed` (closure ⇒ strong FWER), `bergerhsu1996equivalence` (TOST *is* an IUT — lets equivalence
and superiority share one graph), `benjamini1995fdr` + `romanowolf2005stepwise` (the retained sensitivity).

## The construction (a single weighted directed graph ABOVE the existing structure)
A Bretz–Maurer–Brannath–Posch (2009) graph governs only **cross-hypothesis α-flow**; it does **not** touch
any node's internals — each H2 co-primary stays an IUT whose size ≤ α by Berger (1982). Because a graphical
procedure is a shortcut for a closed test (Marcus–Peritz–Gabriel 1976), the whole family enjoys **strong
FWER control at α = 0.05 under arbitrary dependence**.

**Nodes** (each supplies exactly ONE valid level-α p-value — the only requirement, which is what lets test
types mix):
- **N1 = H2-Tail** — the CVaR-5% IUT (max of its three one-sided leg p-values). The scientific headline.
- **N2 = H2-RA** — the Sharpe IUT *and* the ±0.05-DSR TOST equivalence. TOST is itself an IUT
  (`bergerhsu1996equivalence`), so its p-value is a valid node p-value and mixes into the same graph with
  no error inflation — critical, because our predicted result is a **tail win + a Sharpe equivalence**.
- **N3 = H3** — iterative > single-shot best-of-N (one-sided superiority).
- **N4 = H4** — LLM designer > {random-search, Bayesian-opt}; itself an IUT over the two comparators, so it
  stays one valid p-value.
- **N5 = structure control** — `distributional > placebo_shuffled` on CVaR-5% (content over format).
- **N6 = H1** — the LLM reward DOMINATES the 11-name hand-reward canon; itself an IUT over the canon
  (Berger 1982), so it too supplies exactly one valid p-value.

> **⚠ RECONCILED 2026-07-26 by the deep review.** This block previously described a **4-node** graph
> (N1–N4) with edges `N1→{N2:0.5, N4:0.5}`, `N2→{N1:0.5, N3:0.5}`, `N3↔N4`, while
> `config/preregistration.yaml: inference.validity_tier` — the machine mirror that
> `tests/test_validity_tier.py` binds and that `forking_path_guard` declares FROZEN — carried a
> **6-node** graph including N5 and N6, added the same day. Since this document is cited by the YAML
> as both `source:` and `per_node_strength:`, the ratifiers would have been signing off on a topology
> that was not the registered one. The YAML is authoritative; the node list, allocation and edges
> below are now transcribed from it verbatim.

**Initial α-allocation (pre-specified):** `w(N1)=0.5, w(N2)=0.5, w(N3)=w(N4)=w(N5)=w(N6)=0` (sums to 1).
ALL α starts on the two headline co-primaries; the validity tier (N3–N6) is **activated only by upstream
success** — the defining feature of a confirmatory tier. Rationale for 0.5/0.5: co-primary symmetry
(neither H2 leg is privileged); rationale for 0 on the tier: the headline must earn the right to spend α
downstream.

> **⚠ "Zero power cost" corrected 2026-07-26 (same review).** Promoting N3–N6 costs the headline nothing
> *relative to a graph that had given them initial weight* — that much is true and is the point of the
> activate-on-success design. But the OPERATIVE baseline is **R31**: H2-RA and H2-Tail as SEPARATE
> ESTIMANDS, each an IUT decided at the FULL one-sided α = 0.05 (`PREREGISTRATION.md` §1 H2, the
> "two-tier verdict"). Under this graph each co-primary is instead tested at `w_i·α = 0.025`. That IS a
> headline power cost: a one-sided leg powered to **0.80 at α = 0.05 falls to 0.7007 at α = 0.025**
> (verified numerically, normal approximation). It is the honest price of STRONG FWER across all six
> nodes and may well be worth paying — but it is not zero, and it is exactly what
> `ratification_pending: alpha_allocation` asks the supervisors to accept.

**Edges (recycle α on ANY rejection — superiority or equivalence alike; each node's out-edges sum to ≤ 1):**
- `N1 → {N2: 0.34, N4: 0.33, N5: 0.33}` — a confirmed tail headline frees α to the RA co-primary, to
  "beats naive search", and to the content-over-format structure control.
- `N2 → {N1: 0.34, N3: 0.33, N6: 0.33}` — a confirmed RA-equivalence (or RA-superiority) frees α to the
  tail co-primary, to "iteration helps", and to "beats the best human".
- `N3 → {N4: 0.5, N6: 0.5}` · `N4 → {N3: 0.34, N5: 0.33, N6: 0.33}` · `N5 → {N3: 0.5, N4: 0.5}` ·
  `N6 → {N3: 0.5, N4: 0.5}` — the tier nodes recycle exhausted α among themselves.

**The predicted-null path is a first-class α source (non-obvious, load-bearing).** α flows on *rejection*,
and a **TOST rejection = "equivalence proven."** So the tier can activate even when every superiority test
ties; we are **not** stranded when the Sharpe superiority is, as predicted, a tie. This is why
`bergerhsu1996equivalence` is load-bearing.

> **⚠ PREDICTION CORRECTED 2026-07-26 (deep review, loop 8).** This paragraph previously called
> *"a CVaR-5% tail win (N1 rejects) + a Sharpe equivalence"* **"our predicted outcome"**. That
> **contradicts the registered prediction.** `PREREGISTRATION.md` §1a is a conditional table
> (Strict → tail rejects · Weak → inconclusive · Null → both tie), and its *specific a-priori
> prediction* is the **NULL branch**: "its negative responsiveness (≈ −0.05) and un-beaten placebo
> **predict the NULL branch** — a clean, bankable result". A tail win is the **STRICT-branch** outcome,
> not the predicted one. Getting this right is not cosmetic: the whole epistemic claim is Mayoian
> severity, which is only earned by stating the prediction in advance and then reporting what happened —
> a design document that quietly upgrades the registered prediction to the more favourable branch is
> exactly the forking-path move the severity argument is meant to exclude.
>
> **What this means for the tier, stated honestly.** Under the *predicted* (null) branch, N1 does NOT
> reject, so the tier's activation rests entirely on **N2 rejecting via TOST** — i.e. on *proving*
> Sharpe equivalence. That is a genuine, pre-registered α source, but it is **power-limited**:
> `docs/SESOI_DERIVATION_2026-07-25.md` puts the seeds needed to declare equivalence against the
> SESOI at **n\* ≈ 173**, while R101's expected achieved common rung is **~100–189**. So on the
> design's own prediction the tier is *borderline* to activate, and it is honest to say so up front
> rather than discover it at analysis time. The tier remains worth having — it costs the headline only
> the α-split already disclosed above, and it pays off on the Strict branch and on any rung above
> n\* — but it must not be presented as certain to be evaluated.

**Primary rule = the Bonferroni-weighted graph** (valid under any dependence; referee-proof). **Sensitivity
= a Romano–Wolf / resampling graph** (recovers the correlation-induced power our shared-seed design earns);
plus **BH-FDR over the m=6 union** as the disclosed cross-metric sensitivity. This is a strict Pareto
improvement over the current "Bonferroni-over-4" sensitivity (CH4:275,301) — Bonferroni is the weakest member
of the very family the graph generalises.

## Scope + interaction with R101 (must stay consistent)
The tier governs the **single confirmatory look on the Opus arm** at the Aug-27 achieved rung (H2/H3/H4 are
properties of the confirmatory reward-design process, not per-leg). The 10 replication legs remain
**report-only** (R101); the pooled cross-model bounded-effect + per-leg BH-FDR are unchanged. The tier does
NOT alter the m=6 fed-vector family or the identification principle.

## Fragility guards (a statistician / Okhrati will probe these — pre-answered)
1. **FORKING-PATH on promotion — the #1 guard.** The prototype hinted at outcomes (H3 unsupported, H4 clean),
   so choosing to promote H3/H4 and the graph topology *after* seeing that would be a forking path. GUARD:
   the ENTIRE graph — nodes, initial weights, edge weights, each node's test definition, one-sided
   directions, and the single endpoint per node — is **FROZEN in the pre-registration BEFORE the sealed
   leg**. No prototype number enters the dissertation, and the topology is **principled and symmetric**
   (headline-first; H3↔H4 symmetric), NOT engineered around any expected outcome. Disclosed as such.
2. **"Separate estimands vs one family."** The graph is justified iff we make the **conjunctive validity
   claim** ("the method is validated: reward-content matters AND iteration helps AND it beats search"). We
   make exactly that claim (Stefan's arms directive); stated explicitly so the graph is necessary, not
   gratuitous. A failing tier node (e.g. H3 not confirmed) is an honest confirmatory FINDING ("iteration
   does not help here — a boundary of the method"), not a design failure.
3. **IUT/TOST conservativeness → power.** IUTs and TOST have size ≤ α but are conservative away from the
   least-favourable boundary. GUARD: each node's power/MDE is reported separately; H3/H4 are single
   one-sided tests (less conservative than the H2 IUTs), so the tier is not the power-limiting element.
4. **Edge semantics must be scientifically coherent across test types.** Each edge is justified in words;
   comparator sets kept straight (H2 = within-LLM channel vs scalar/placebo; H4 = LLM vs external search) so
   "equivalence to scalar" and "superiority over search" never read as contradictory.
5. **Hidden endpoint-multiplicity inside H3/H4.** Each tier node pre-specifies ONE endpoint (or is an
   explicit IUT over its endpoints) — no silent Sharpe-and-CVaR double test.
6. **Consonance / Simes.** Bonferroni-based weights are consonant by construction and keep the closed-test
   equivalence; the parametric/Romano-Wolf upgrade is a disclosed sensitivity only.
7. **α-allocation is a free parameter** — justified above (headline-priority + co-primary symmetry), argued
   not asserted (Stefan criterion 4).

## Judgment calls surfaced for Tamer / Ramin / Okhrati ratification (pre-freeze, reversible)
- **The conjunctive-validity framing** (chosen; makes the graph necessary) — confirm it is the intended claim.
- **Whether the graphical-FWER tier is the PRIMARY rule** (this design) **or Okhrati prefers the current
  BH-FDR primary with the graph as a sensitivity** — flagged; either is a one-line switch here.
- **The α-allocation** 0.5/0.5-headline / 0-tier — confirm.
These are registered as the design of record but explicitly marked for supervisor ratification before the
GO-day freeze (the freeze executes with the campaign-run approval, R94).

## Report-only / descriptive-only elements — the systematic UPGRADE ANALYSIS (Tamer, 2026-07-26)
Directive: ultrathink on the priorities and, *where the priorities genuinely allow*, upgrade report-only /
descriptive-only elements — but never at the cost of identification, the frozen H2 logic, forking-path
discipline, or Okhrati's depth-over-breadth. Each element below is judged against that bar.

**UPGRADE — promoted into the confirmatory tier (priorities allow):**
- **H3 (iteration > single-shot)** → node **N3**. Done above.
- **H4 (LLM designer > search)** → node **N4**. Done above.
- **Structure control / `placebo_shuffled` (content-over-format)** → **NEW node N5** (this amendment). The
  strongest additional upgrade: it is a *mechanism* claim (the tail effect comes from the fed CONTENT, not
  merely from the presence of a six-number block), so promoting it **DEEPENS the originality headline**
  (Okhrati: depth + originality) and is exactly the "control that isolates the effect" Stefan named. It is
  already a frozen arm (no re-authoring), it is **forking-path-clean** (the 6-arm prototype never ran
  `placebo_shuffled`, so no prototype signal informs it), and it enters DOWNSTREAM of the H2 headline
  (activate-on-upstream), so it costs the headline zero power. N5 makes the conjunctive claim strictly
  stronger: *reward-content matters (H2) AND it is the content not the format (N5) AND iteration helps (H3)
  AND it beats naive search (H4).*

**CANDIDATE — H1 promoted via a SNOOP-FREE reformulation (registered, ratification-pending):**
- **H1 (beat-the-human)** is descriptive-only *solely* because "the best hand-reward" is named by the MAX over
  the same sealed leg the LLM is scored on (a comparator test-snoop → no valid p-value; White 2000). The
  SMART, non-fragile fix (Tamer 2026-07-26, "make it smart + sound") needs no new data and no baseline
  validation-roll: **beating the best hand-reward is logically identical to beating EVERY member of the
  canon** — the best is the pointwise max, so beat-max ⟺ beat-all. Requiring the LLM to beat all 11, each
  one-sided at α, is an **intersection-union test** (Berger 1982) that selects NO comparator, so there is
  nothing to snoop; the IUT p-value is the MAX over the per-baseline one-sided leg p's, and the LLM
  "DOMINATES the canon" iff every member is beaten. This adds a node **N6 = "the LLM reward DOMINATES the
  hand-reward canon (== beats the best human, made precise)"**, reported with the honest per-baseline
  dominance profile (dominates / ahead-n.s. / behind). It SUPERSEDES the earlier val-select framing, which
  was DEAD CODE (the campaign archives `val_fitness=NaN`, so `beat_human_baseline` already fell back to the
  test-snoop) AND needed a fragile new baseline val-roll — the IUT **dissolves** the fragility instead of
  patching it, and is consistent with the H2 co-primary IUTs (one shared inference tool). Registered as a
  CANDIDATE (it changes H1's inferential definition → supervisor ratification); implemented + unit-tested in
  `beat_human_baseline` (the `iut` block; `tests/test_analyze_campaign.py::test_iut_*`).

**KEEP report-only — upgrading would VIOLATE the priorities or is infeasible (stated, not defaulted):**
- **`factor_attribution` (BAB/low-vol pre-empt)** — a robustness DEFENCE ("your edge is just a known
  factor"), not a hypothesis; a confirmatory version would be gratuitous breadth.
- **`delisting_band`, `cost_sweep`, `dsr_effective_n`** — DATA/parameter sensitivities (no policy re-run);
  they answer "is the result robust to X", not "is there an effect". Report-only is correct.
- **`capability_gradient`** — the primary SWE-bench anchor is DEAD (2/10 legs); it cannot be upgraded, and
  the honest move is to DOWN-RANK it to the two within-family pair-DiDs (Qwen-9B↔27B, Haiku↔Opus) — a
  separate fix, not a promotion.
- **The M2 psychometric module (R96)** — a registered-but-not-activated P2-paper extension; activation is
  Tamer's write-time decision, not a confirmatory-tier node.
- **The mechanism sub-experiments (named-vs-blinded, legible-vs-raw; SQ1–SQ3)** — these ARE the depth
  headline and are best served as RICH descriptive/mediation analyses (Okhrati rewards the insight, not a
  p-value); the one plausibly-confirmatory piece, SQ1 responsiveness, already carries a positive control and
  is kept descriptive by design so the mechanism story stays a detective story, not a test battery.
- **The per-model H2 contrasts (R101 BH-FDR secondary)** — R101 (Okhrati's seed-parity) already set
  pooled-primary + per-model-FDR-secondary; promoting per-model to primary is the "11 independent
  confirmatory tests" alternative that R101 flagged as *Okhrati's* call, not a unilateral upgrade.

**Net:** two upgrades already in the tier (H3, H4) + one strong new one (N5 structure/content-over-format,
implemented) + one ratification-pending candidate (N6 H1, snoop-free IUT). Everything else stays report-only
for a stated priority reason. This is "upgrade where it deepens the confirmatory validity story at zero
headline cost; keep report-only where it is a sensitivity, a defence, a dead anchor, or a depth-analysis."

## The H1 comparator — "why best of 4 only?" (Tamer, 2026-07-26)
Tamer asked why H1 compares against only FOUR hand-designed rewards. **State of the design when the
question was asked (now superseded — see the resolution at the end of this section):** it froze a 4-name
CORE — `raw_return`, `return_minus_variance`, `return_minus_cvar`, `differential_sharpe` (the pre-registered
§1-H1 family) — while a broader 10-name `REWARD_CANON` (adding the differential-downside ratio, Markowitz
utility, drawdown-penalty, Sortino downside, turnover-penalty, Kelly log-growth) ran as a report-only
secondary panel. The analysis + upgrade:

1. **There is no good reason to cap the CONFIRMATORY comparator at 4.** The human champion (the strongest
   hand-reward on THIS heavy-tailed panel) could lie OUTSIDE the core 4 — e.g. Kelly log-growth or the
   differential-downside ratio may dominate differential-Sharpe under fat tails. "Beat the best of 4" is
   weaker and invites the "you cherry-picked four weak baselines" critique; **"beat the best of the full
   standard human-reward toolkit"** is the strong, non-fragile, Stefan-aligned claim.
2. **The upgrade is FREE and STRICTLY MORE CONSERVATIVE.** The 10 canon rewards are ALREADY trained (the
   secondary panel), so selecting the champion from all 10 costs NO extra compute. A larger champion pool =
   a STRONGER human bar = a MORE impressive LLM win. ⚠ **Corrected 2026-07-26 (deep review, loop 5):**
   this paragraph previously claimed a *deflation asymmetry* favouring the humans (LLM winner
   DSR-deflated over its candidate count, each hand-reward at N=1). That is not what happens. N6's
   endpoint is annualised per-seed **Sharpe**, not DSR, so nothing is deflated in the test; and
   deflation would be misapplied regardless, because selection is on **VALIDATION**
   (`run_campaign` selects on `val_fitness`; `held_out_fitness` refuses a non-val split) and the test
   leg is **SEALED** — there is no test-set max-over-N to correct for. The real residual asymmetry runs
   the OTHER way: the LLM winner is the best of 30 validation candidates while each hand reward is one
   fixed, un-tuned specification, which **FAVOURS the LLM** and is disclosed as such in CH6. Raising the
   human bar to the full canon therefore strengthens the claim on its own merits, not via a deflation
   that does not occur. Selection bias from the max-over-N is **DISSOLVED** by the IUT
   reformulation: N6 selects no champion at all (it requires beating EVERY member — beat-all ⟺ beat-max),
   so there is no order statistic to snoop (superseding the earlier val-select fix, which was dead code).
3. **N6's comparator is therefore the FULL canon, not the 4** (registered in the N6 spec, this amendment).
4. **Beyond 10 — RESOLVED the same day; the section above is the pre-resolution reasoning.** The canon
   was expanded **4 → 11**: the research returned exactly ONE principled addition,
   `volatility_scaled_return` (the volatility-TARGETED deep-RL-for-trading reward of Zhang, Zohren &
   Roberts 2020 — the RL-trading-provenance member the panel lacked). `REWARD_CANON` ==
   `config/preregistration.yaml: h1_baselines` == `config/campaign.yaml: h1_baselines` ==
   `config/eureka_loop.yaml: baseline_rewards` == the SAME 11 names;
   `freeze.py::assert_h1_baselines_match` verifies n=11 and `tests/test_baselines.py` binds the config
   list to `REWARD_CANON` in both directions. The open question below is what was considered *before*
   that resolution, and is retained as the reasoning trail:
   Whether to expand the canon to the
   comprehensive literature toolkit (Calmar, Sterling, Omega, prospect-theory / CPT utility, risk-parity,
   …) so "the human toolkit" is complete and every member is literature-cited. Each added member costs one
   trained baseline + one verified citation; the research returns the principled comprehensive set + the
   BibTeX, after which `REWARD_CANON` + `h1_baselines` are expanded to the full toolkit in one amendment,
   `freeze.py::assert_h1_baselines_match` re-verified. **This turns H1 from "beats 4 core rewards" into
   "beats the best of the entire standard risk-sensitive-reward toolkit" — a materially stronger result.**

## Per-node STRENGTH, EVIDENCE, and NON-FRAGILITY (Tamer, 2026-07-26: additions must be *very strong*)
Each confirmatory node is a rigorous, evidence-backed, VALID level-α test under strong FWER; the graph is
robust to any node being a null (it reports only what is confirmed); and the whole graph is frozen BEFORE
the sealed leg (the forking-path guard). We keep EVERY legitimate node regardless of expected outcome —
cherry-picking the confirmatory set on prototype hints would itself be a forking path.

- **N1 / N2 (H2 — the headline).** Two co-primary IUTs (`berger1982iut`); the mechanism the whole thesis
  rests on. Powered to the derived SESOI (R104: 0.05 DSR = 0.0756 ann-Sharpe, inside the economic band).
  Grade-A, first-hand-measured. Non-fragile: the conjunction IS the correction.
- **N3 (H3 — iteration > single-shot).** A CORE Eureka-lineage claim — does the reflection loop help?
  (`ma2024eureka` shows it does). A single one-sided superiority test (LESS conservative than an IUT).
  Honest-null posture: the directional prototype was inconclusive, so we test rigorously and report either
  way — a null is the finding "iteration does not help HERE, a boundary", never a design flaw.
- **N4 (H4 — LLM designer > naive search).** The LLM winner vs random-search + Bayesian-opt over the SAME
  six-primitive reward family — an IUT over the two procedural comparators. Isolates the LLM's contribution
  from mere search. Strong (the prototype was directionally clean); each comparator a valid node p-value.
- **N5 (structure control — CONTENT over FORMAT).** `distributional > placebo_shuffled` on CVaR-5%: the real
  six-number tail block vs its DERANGED values. Rules out the format confound — the single most load-bearing
  MECHANISM control (Stefan: the control that isolates the effect). Frozen arm (R32); forking-path-clean
  (never ran in the 6-arm prototype). A single one-sided test.
- **N6 (H1 — LLM beats the best HUMAN reward, over the full 11-canon).** The STRONGEST-possible human bar:
  the pointwise max over EVERY accepted family of hand-designed portfolio objective — risk-neutral return,
  mean-variance + online Sharpe (`markowitz1952portfolio`; `moody2001directrl`; `sharpe1966mutualfund`),
  coherent tail (`rockafellar2000cvar` CVaR; `sortino1991downside`; Moody-Saffell DDR), drawdown
  (`chekhlov2005drawdown`), growth-optimal (`kelly1956information`), transaction cost (`garleanu2013dynamic`),
  volatility targeting (`zhang2020drltrading`) — each literature-cited and first-hand-verified. Beating THIS
  is beating the accumulated wisdom of the field at its standard specifications — a strong bar, though not
  a TUNED one (see the honest caveat below). ⚠ **Corrected 2026-07-26 (deep review, loop 5):** the earlier
  text claimed TWO conservative features, the first being that "every hand-reward is un-searched /
  DSR-deflated at N=1 while the LLM winner still pays its full search-multiplicity penalty". That feature
  does not exist — N6's endpoint is annualised Sharpe (no deflation), and deflation would be misapplied
  anyway since selection is on validation and the test leg is sealed. The surviving asymmetry is the
  opposite one and must be stated plainly: **the baselines are UN-TUNED**, so the comparison favours the
  LLM (CH6 already discloses this). What genuinely remains conservative is the second feature — the IUT
  reformulation (beat EVERY canon member —
  NO champion is selected) removes the max-over-N selection bias ENTIRELY: there is no order statistic to snoop
  (beat-all ⟺ beat-max, `berger1982iut`), so the conservative human bar is also a snoop-free one, and H1 needs
  no fragile baseline validation-roll. NOVELTY: the lineage (Eureka / Text2Reward /
  REvolve) benchmarks against a SINGLE incumbent reward; a **canon-as-champion is, to our knowledge, a first**
  in the LLM-reward-design lineage — itself a contribution (framing for CH2/CH7).

**Non-fragility summary.** No node is a weak link: each is a valid level-α test (Berger / TOST / one-sided);
the tier costs the H2 headline ZERO power (activate-on-upstream); the graph enjoys strong FWER (closed test,
`marcus1976closed`); the forking-path guard freezes the graph before the sealed leg; and a failing node is
an honest, reportable boundary, never a collapse. The additions STRENGTHEN the conjunctive validity story
precisely *because* each is hard, conservative, and evidence-backed.

## Reproduce / verify
`config/preregistration.yaml: inference.validity_tier` (the machine-readable graph) + `PREREGISTRATION.md`
R105 + `tests/test_validity_tier.py` (graph well-formed: node p-value validity, per-node out-edge weights
sum ≤ 1, initial weights sum to α-allocation, and — corrected 2026-07-26, this line previously said
"H1 excluded" — that **H1 IS present as node N6**, promoted the same day, with
`endpoint: sharpe_annualized` (corrected 2026-07-26, deep review loop 5: the code builds the IUT legs from
annualised per-seed Sharpe, not DSR — a DSR endpoint would deflate the winner by n=30 vs each hand reward by
n=1, i.e. different nulls per arm, so the winner would lose every leg even at an equal true Sharpe). The analysis
implementation reuses
`src/inference/multiple_testing.py` (`benjamini_hochberg`, `romano_wolf`) as node/sensitivity procedures.
